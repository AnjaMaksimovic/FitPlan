"""
FitPlan DSL — Nutrition Report Generator (v2)
"""

import os
from datetime import datetime
from os.path import dirname, join

import click
from textx import generator

from ..main import parse_model
from ..nutrition_calc import calc_nutrition_for_day, calc_nutrition_for_recipe
from ..plan_generator import generate_weekly_plan, get_workouts_for_day, DAYS

THIS_FOLDER = dirname(dirname(__file__))


def _status_icon(actual, target, tolerance=0.1):
    ratio = actual / target if target > 0 else 0
    if abs(ratio - 1.0) <= tolerance:
        return '✅'
    elif ratio < 1.0 - tolerance:
        return '⬇️'
    else:
        return '⬆️'


def _macro_grams(total_kcal, pct, kcal_per_gram):
    return (total_kcal * pct / 100) / kcal_per_gram


@generator('fitplan', 'nutrition')
def nutrition_generator(metamodel, model, output_path, overwrite, debug, **kwargs):
    """Generates nutrition report from .fitplan file."""
    input_file = model._tx_filename
    base_dir = output_path if output_path else os.path.dirname(input_file)
    base_name, _ = os.path.splitext(os.path.basename(input_file))
    output_file = os.path.abspath(join(base_dir, f"{base_name}_nutrition.html"))

    if not overwrite and os.path.exists(output_file):
        click.echo(f'-- Skipping: {output_file}')
        return

    click.echo(f'-> Generating nutrition report: {output_file}')

    fitplan_model, warnings = parse_model(input_file)
    if fitplan_model is None:
        return

    declarations = fitplan_model.declarations
    custom_ingredients = [d for d in declarations if d.__class__.__name__ == 'Ingredient']
    recipes = [d for d in declarations if d.__class__.__name__ == 'Recipe']
    workouts = [d for d in declarations if d.__class__.__name__ == 'Workout']
    plans = [d for d in declarations if d.__class__.__name__ == 'Plan']

    if not plans:
        click.echo('No plans found.')
        return

    plan = plans[0]
    weekly = generate_weekly_plan(plan, recipes)

    target_kcal = plan.target_calories
    target_protein_g = _macro_grams(target_kcal, plan.protein_pct, 4)
    target_carbs_g = _macro_grams(target_kcal, plan.carbs_pct, 4)
    target_fat_g = _macro_grams(target_kcal, plan.fat_pct, 9)

    week_total = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0}
    rows_html = ''

    for day in DAYS:
        day_plan = weekly.get(day, {})
        dn = calc_nutrition_for_day(day_plan, custom_ingredients)

        for k in week_total:
            week_total[k] += dn[k]

        diff = dn['calories'] - target_kcal
        diff_str = f"+{diff:.0f}" if diff > 0 else f"{diff:.0f}"
        diff_color = '#e53e3e' if diff > 200 else ('#38a169' if diff < -50 else '#d69e2e')

        day_workouts = get_workouts_for_day(workouts, day)
        workout_burns = sum(w.burns for w in day_workouts if w.burns)
        net_kcal = dn['calories'] - workout_burns

        workout_str = ', '.join(f"{w.type} ({w.burns} kcal)" for w in day_workouts) if day_workouts else '—'

        rows_html += f"""
        <tr>
            <td class="day-col"><strong>{day}</strong></td>
            <td>{dn['calories']:.0f} {_status_icon(dn['calories'], target_kcal)}</td>
            <td style="color:{diff_color}; font-weight:600">{diff_str}</td>
            <td>{net_kcal:.0f}</td>
            <td>{dn['protein']:.1f}g {_status_icon(dn['protein'], target_protein_g)}</td>
            <td>{dn['carbs']:.1f}g {_status_icon(dn['carbs'], target_carbs_g)}</td>
            <td>{dn['fat']:.1f}g {_status_icon(dn['fat'], target_fat_g)}</td>
            <td>{dn['fiber']:.1f}g</td>
            <td>{workout_str}</td>
        </tr>"""

    num_days = len(DAYS)
    avg = {k: v / num_days for k, v in week_total.items()}

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8">
<title>Nutrition Report — {plan.name}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',sans-serif;background:#f0f4f8;color:#2d3748;padding:2rem}}
h1{{color:#276749;margin-bottom:.3rem}}
.subtitle{{color:#718096;margin-bottom:2rem;font-size:.95rem}}
.goal-badge{{display:inline-block;background:#c6f6d5;color:#276749;padding:.3rem 1rem;border-radius:20px;font-weight:600;margin-bottom:1.5rem}}
.targets-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem;margin-bottom:2rem}}
.target-box{{background:white;border-radius:10px;padding:1rem;text-align:center;box-shadow:0 2px 6px rgba(0,0,0,.06);border-top:4px solid #38a169}}
.target-box.protein{{border-color:#fc8181}}.target-box.carbs{{border-color:#f6ad55}}.target-box.fat{{border-color:#68d391}}
.target-value{{font-size:1.6rem;font-weight:700;color:#276749}}
.target-label{{font-size:.8rem;color:#718096;text-transform:uppercase}}
.target-sub{{font-size:.85rem;color:#4a5568;margin-top:.3rem}}
table{{width:100%;border-collapse:collapse;background:white;border-radius:12px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.07);margin-bottom:2rem}}
th{{background:#276749;color:white;padding:.8rem 1rem;text-align:left;font-size:.85rem}}
td{{padding:.75rem 1rem;border-bottom:1px solid #e2e8f0;font-size:.9rem}}
tr:hover td{{background:#f0fff4}}.day-col{{font-weight:600;color:#276749}}
.avg-row td{{background:#f0fff4;font-weight:600;border-top:2px solid #38a169}}
.legend{{background:white;border-radius:10px;padding:1rem 1.5rem;box-shadow:0 2px 6px rgba(0,0,0,.06);font-size:.85rem;color:#4a5568}}
.legend span{{margin-right:1.5rem}}
.footer{{margin-top:2rem;color:#a0aec0;font-size:.8rem;text-align:center}}
</style></head><body>
<h1>📊 Nutrition Report</h1>
<p class="subtitle">Plan: <strong>{plan.name}</strong> · Generated: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
<div class="goal-badge">Goal: {plan.goal}</div>
<div class="targets-grid">
<div class="target-box"><div class="target-value">{target_kcal}</div><div class="target-label">Target Calories</div><div class="target-sub">kcal / day</div></div>
<div class="target-box protein"><div class="target-value">{target_protein_g:.0f}g</div><div class="target-label">Protein ({plan.protein_pct}%)</div></div>
<div class="target-box carbs"><div class="target-value">{target_carbs_g:.0f}g</div><div class="target-label">Carbs ({plan.carbs_pct}%)</div></div>
<div class="target-box fat"><div class="target-value">{target_fat_g:.0f}g</div><div class="target-label">Fat ({plan.fat_pct}%)</div></div>
</div>
<table><thead><tr><th>Day</th><th>Calories</th><th>Diff</th><th>Net (after workout)</th><th>Protein</th><th>Carbs</th><th>Fat</th><th>Fiber</th><th>Workout</th></tr></thead>
<tbody>{rows_html}
<tr class="avg-row"><td>Average/day</td><td>{avg['calories']:.0f} kcal</td><td>—</td><td>—</td><td>{avg['protein']:.1f}g</td><td>{avg['carbs']:.1f}g</td><td>{avg['fat']:.1f}g</td><td>{avg['fiber']:.1f}g</td><td>—</td></tr>
</tbody></table>
<div class="legend"><span>✅ On target (±10%)</span><span>⬇️ Below target</span><span>⬆️ Above target</span></div>
<p class="footer">FitPlan DSL · {datetime.now().strftime('%Y')}</p>
</body></html>"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    click.echo(f'OK Nutrition report: {output_file}')
