"""
FitPlan DSL — Progress Tracker Generator
Generates an interactive HTML page where users can:
- Track completed workouts with checkboxes
- Log calorie intake per meal
- See daily calorie balance (consumed vs target vs burned)
- Get activity suggestions if they exceed their calorie target
- Log extra meals and see the impact

Usage:
    textx generate plan.fitplan --target progress --overwrite
"""

import os
import json
from datetime import datetime
from os.path import dirname, join

import click
from textx import generator

from ..main import parse_model
from ..nutrition_calc import calc_nutrition_for_recipe, calc_nutrition_for_day
from ..plan_generator import generate_weekly_plan, get_workouts_for_day, DAYS
from ..workout_calc import get_workout_calories, estimate_calories_burned, suggest_activity_for_excess

THIS_FOLDER = dirname(dirname(__file__))


@generator('fitplan', 'progress')
def progress_generator(metamodel, model, output_path, overwrite, debug, **kwargs):
    """Generates interactive progress tracker from .fitplan file."""
    input_file = model._tx_filename
    base_dir = output_path if output_path else os.path.dirname(input_file)
    base_name, _ = os.path.splitext(os.path.basename(input_file))
    output_file = os.path.abspath(join(base_dir, f"{base_name}_progress.html"))

    if not overwrite and os.path.exists(output_file):
        click.echo(f'-- Skipping: {output_file}')
        return

    click.echo(f'-> Generating progress tracker: {output_file}')

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

    # Build data for each day
    days_json = []
    for day in DAYS:
        day_plan = weekly.get(day, {})
        day_workouts = get_workouts_for_day(workouts, day)

        meals = []
        for meal_type in ['breakfast', 'lunch', 'dinner', 'snack']:
            if meal_type in day_plan:
                recipe = day_plan[meal_type]['recipe']
                servings = day_plan[meal_type].get('servings', 1)
                kcal = calc_nutrition_for_recipe(recipe, custom_ingredients, servings)['calories']
                meals.append({
                    'type': meal_type,
                    'name': recipe.name,
                    'kcal': round(kcal),
                })

        workout_list = []
        for w in day_workouts:
            burns = get_workout_calories(w)
            workout_list.append({
                'name': w.name,
                'type': w.type,
                'duration': w.duration,
                'intensity': w.intensity,
                'burns': burns,
            })

        days_json.append({
            'name': day,
            'meals': meals,
            'workouts': workout_list,
        })

    # Suggestion data
    suggestions = suggest_activity_for_excess(200)  # Base for 200 kcal excess
    suggestions_json = json.dumps(suggestions[:3])

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>FitPlan Progress Tracker — {plan.name}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',sans-serif;background:#f0f4f8;color:#2d3748;padding:1.5rem;max-width:900px;margin:0 auto}}
header{{background:linear-gradient(135deg,#38a169,#276749);color:white;padding:1.5rem;border-radius:12px;margin-bottom:1.5rem;text-align:center}}
header h1{{font-size:1.8rem;margin-bottom:.3rem}}header p{{opacity:.85}}
.day-card{{background:white;border-radius:12px;margin-bottom:1.5rem;box-shadow:0 2px 8px rgba(0,0,0,.08);overflow:hidden}}
.day-header{{background:#f0fff4;padding:.8rem 1.2rem;font-weight:700;color:#276749;font-size:1.1rem;border-bottom:1px solid #c6f6d5;display:flex;justify-content:space-between;align-items:center}}
.day-status{{font-size:.85rem;font-weight:400}}
.day-body{{padding:1rem 1.2rem}}
.section-label{{font-size:.8rem;text-transform:uppercase;color:#718096;font-weight:600;margin:.8rem 0 .4rem}}
.meal-row{{display:flex;align-items:center;gap:.8rem;padding:.4rem 0;border-bottom:1px solid #f7fafc}}
.meal-row input[type=checkbox]{{width:18px;height:18px;accent-color:#38a169}}
.meal-row.done{{opacity:.5;text-decoration:line-through}}
.meal-name{{flex:1;font-size:.9rem}}.meal-kcal{{font-weight:600;color:#38a169;font-size:.85rem}}
.workout-row{{display:flex;align-items:center;gap:.8rem;padding:.4rem 0;border-bottom:1px solid #f7fafc}}
.workout-row input[type=checkbox]{{width:18px;height:18px;accent-color:#2b6cb0}}
.workout-row.done{{opacity:.5;text-decoration:line-through}}
.workout-name{{flex:1;font-size:.9rem;color:#2b6cb0}}.workout-burns{{font-weight:600;color:#e53e3e;font-size:.85rem}}
.extra-meal{{margin-top:.5rem;display:flex;gap:.5rem}}
.extra-meal input{{flex:1;padding:.4rem .6rem;border:1px solid #e2e8f0;border-radius:6px;font-size:.85rem}}
.extra-meal button{{padding:.4rem .8rem;background:#38a169;color:white;border:none;border-radius:6px;cursor:pointer;font-size:.85rem}}
.balance-bar{{margin-top:1rem;background:#e2e8f0;border-radius:8px;height:24px;overflow:hidden;position:relative}}
.balance-fill{{height:100%;border-radius:8px;transition:width .3s}}
.balance-fill.under{{background:linear-gradient(90deg,#68d391,#38a169)}}
.balance-fill.over{{background:linear-gradient(90deg,#fc8181,#e53e3e)}}
.balance-text{{font-size:.82rem;color:#4a5568;margin-top:.3rem;text-align:right}}
.suggestion{{margin-top:.8rem;background:#ebf8ff;border-radius:8px;padding:.6rem 1rem;font-size:.85rem;color:#2b6cb0;display:none}}
.suggestion.visible{{display:block}}
.summary{{background:white;border-radius:12px;padding:1.5rem;box-shadow:0 2px 8px rgba(0,0,0,.08);margin-bottom:1.5rem}}
.summary h2{{color:#276749;margin-bottom:1rem;font-size:1.2rem}}
.summary-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:1rem}}
.summary-box{{text-align:center;padding:.8rem;background:#f0fff4;border-radius:8px}}
.summary-value{{font-size:1.4rem;font-weight:700;color:#276749}}
.summary-label{{font-size:.75rem;color:#718096;text-transform:uppercase}}
footer{{text-align:center;color:#a0aec0;font-size:.8rem;margin-top:2rem}}
</style>
</head>
<body>
<header>
<h1>📊 Progress Tracker</h1>
<p>{plan.name} · Target: {target_kcal} kcal/day · Goal: {plan.goal}</p>
</header>

<div class="summary">
<h2>📈 Weekly Overview</h2>
<div class="summary-grid">
<div class="summary-box"><div class="summary-value" id="totalMeals">0</div><div class="summary-label">Meals Logged</div></div>
<div class="summary-box"><div class="summary-value" id="totalWorkouts">0</div><div class="summary-label">Workouts Done</div></div>
<div class="summary-box"><div class="summary-value" id="avgCalories">0</div><div class="summary-label">Avg kcal/day</div></div>
<div class="summary-box"><div class="summary-value" id="weeklyBurn">0</div><div class="summary-label">Total Burned</div></div>
</div>
</div>

<div id="daysContainer"></div>

<footer>FitPlan DSL Progress Tracker · {datetime.now().strftime('%Y')}</footer>

<script>
const TARGET = {target_kcal};
const DAYS_DATA = {json.dumps(days_json)};
const SUGGESTIONS_BASE = {suggestions_json};

function renderDays() {{
    const container = document.getElementById('daysContainer');
    container.innerHTML = '';

    DAYS_DATA.forEach((day, dayIdx) => {{
        const card = document.createElement('div');
        card.className = 'day-card';

        let mealsHtml = '';
        day.meals.forEach((m, mIdx) => {{
            mealsHtml += `
            <div class="meal-row" id="meal-${{dayIdx}}-${{mIdx}}">
                <input type="checkbox" onchange="toggleMeal(${{dayIdx}},${{mIdx}},this.checked)">
                <span class="meal-name">${{m.type.charAt(0).toUpperCase() + m.type.slice(1)}}: ${{m.name}}</span>
                <span class="meal-kcal">${{m.kcal}} kcal</span>
            </div>`;
        }});

        let workoutsHtml = '';
        day.workouts.forEach((w, wIdx) => {{
            workoutsHtml += `
            <div class="workout-row" id="workout-${{dayIdx}}-${{wIdx}}">
                <input type="checkbox" onchange="toggleWorkout(${{dayIdx}},${{wIdx}},this.checked)">
                <span class="workout-name">🏋️ ${{w.name}} · ${{w.duration}} min</span>
                <span class="workout-burns">-${{w.burns}} kcal</span>
            </div>`;
        }});

        card.innerHTML = `
        <div class="day-header">
            <span>${{day.name}}</span>
            <span class="day-status" id="status-${{dayIdx}}">—</span>
        </div>
        <div class="day-body">
            <div class="section-label">🍽 Meals</div>
            ${{mealsHtml}}
            <div class="extra-meal">
                <input type="text" placeholder="Extra meal name" id="extraName-${{dayIdx}}">
                <input type="number" placeholder="kcal" id="extraKcal-${{dayIdx}}" style="width:80px">
                <button onclick="addExtra(${{dayIdx}})">+</button>
            </div>
            ${{day.workouts.length ? '<div class="section-label">🏋️ Workouts</div>' + workoutsHtml : ''}}
            <div class="balance-bar"><div class="balance-fill" id="bar-${{dayIdx}}"></div></div>
            <div class="balance-text" id="balanceText-${{dayIdx}}"></div>
            <div class="suggestion" id="suggestion-${{dayIdx}}"></div>
        </div>`;
        container.appendChild(card);
    }});
    updateAll();
}}

// State tracking
const state = DAYS_DATA.map(day => ({{
    mealsChecked: day.meals.map(() => false),
    workoutsChecked: day.workouts.map(() => false),
    extraMeals: [],
}}));

function toggleMeal(dayIdx, mealIdx, checked) {{
    state[dayIdx].mealsChecked[mealIdx] = checked;
    document.getElementById(`meal-${{dayIdx}}-${{mealIdx}}`).classList.toggle('done', checked);
    updateDay(dayIdx);
    updateSummary();
}}

function toggleWorkout(dayIdx, wIdx, checked) {{
    state[dayIdx].workoutsChecked[wIdx] = checked;
    document.getElementById(`workout-${{dayIdx}}-${{wIdx}}`).classList.toggle('done', checked);
    updateDay(dayIdx);
    updateSummary();
}}

function addExtra(dayIdx) {{
    const nameEl = document.getElementById(`extraName-${{dayIdx}}`);
    const kcalEl = document.getElementById(`extraKcal-${{dayIdx}}`);
    const name = nameEl.value.trim();
    const kcal = parseInt(kcalEl.value);
    if (!name || !kcal) return;
    state[dayIdx].extraMeals.push({{ name, kcal }});
    nameEl.value = ''; kcalEl.value = '';
    renderDays();
}}

function updateDay(dayIdx) {{
    const day = DAYS_DATA[dayIdx];
    const s = state[dayIdx];

    let consumed = 0;
    day.meals.forEach((m, i) => {{ if (s.mealsChecked[i]) consumed += m.kcal; }});
    s.extraMeals.forEach(e => consumed += e.kcal);

    let burned = 0;
    day.workouts.forEach((w, i) => {{ if (s.workoutsChecked[i]) burned += w.burns; }});

    const net = consumed - burned;
    const diff = net - TARGET;
    const pct = Math.min((net / TARGET) * 100, 150);

    const bar = document.getElementById(`bar-${{dayIdx}}`);
    bar.style.width = pct + '%';
    bar.className = 'balance-fill ' + (diff > 0 ? 'over' : 'under');

    const diffStr = diff > 0 ? `+${{diff}}` : `${{diff}}`;
    document.getElementById(`balanceText-${{dayIdx}}`).textContent =
        consumed > 0 ? `${{consumed}} eaten - ${{burned}} burned = ${{net}} net (${{diffStr}} from target)` : 'No meals logged yet';

    document.getElementById(`status-${{dayIdx}}`).textContent =
        consumed > 0 ? `${{net}} / ${{TARGET}} kcal` : '—';

    // Show suggestion if over target
    const suggEl = document.getElementById(`suggestion-${{dayIdx}}`);
    if (diff > 50) {{
        const mins = Math.round(diff / (7 * 70 / 60)); // rough walking estimate
        const suggestions = SUGGESTIONS_BASE.map(s => {{
            const adjMins = Math.round(s.duration_min * (diff / 200));
            return `${{adjMins}} min ${{s.description}}`;
        }});
        suggEl.innerHTML = `💡 Over target by ${{diff}} kcal. Try: ${{suggestions.join(' or ')}} to compensate.`;
        suggEl.classList.add('visible');
    }} else {{
        suggEl.classList.remove('visible');
    }}
}}

function updateSummary() {{
    let totalMeals = 0, totalWorkouts = 0, totalConsumed = 0, totalBurned = 0, daysWithData = 0;
    DAYS_DATA.forEach((day, i) => {{
        const s = state[i];
        let dayConsumed = 0;
        s.mealsChecked.forEach((checked, j) => {{ if (checked) {{ totalMeals++; dayConsumed += day.meals[j].kcal; }} }});
        s.extraMeals.forEach(e => dayConsumed += e.kcal);
        s.workoutsChecked.forEach((checked, j) => {{ if (checked) {{ totalWorkouts++; totalBurned += day.workouts[j].burns; }} }});
        totalConsumed += dayConsumed;
        if (dayConsumed > 0) daysWithData++;
    }});
    document.getElementById('totalMeals').textContent = totalMeals;
    document.getElementById('totalWorkouts').textContent = totalWorkouts;
    document.getElementById('avgCalories').textContent = daysWithData > 0 ? Math.round(totalConsumed / daysWithData) : 0;
    document.getElementById('weeklyBurn').textContent = totalBurned;
}}

function updateAll() {{ DAYS_DATA.forEach((_, i) => updateDay(i)); updateSummary(); }}
renderDays();
</script>
</body></html>"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    click.echo(f'OK Progress tracker: {output_file}')
