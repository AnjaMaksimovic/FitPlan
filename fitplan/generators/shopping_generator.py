"""
FitPlan DSL — Shopping List Generator (v2)
Aggregates ingredients from auto-generated weekly plan.
"""

import os
from datetime import datetime
from os.path import join

import click
from textx import generator

from ..main import parse_model
from ..nutrition_calc import calc_shopping_list, format_grams
from ..plan_generator import generate_weekly_plan, DAYS

CATEGORY_NAMES = {
    'meat':      '🥩 Meat & Poultry',
    'fish':      '🐟 Fish & Seafood',
    'dairy':     '🥛 Dairy',
    'vegetable': '🥦 Vegetables',
    'fruit':     '🍎 Fruit',
    'grain':     '🌾 Grains',
    'legume':    '🫘 Legumes',
    'fat':       '🫒 Oils & Fats',
    'sweetener': '🍯 Sweeteners',
    'other':     '🛒 Other',
}


@generator('fitplan', 'shopping')
def shopping_generator(metamodel, model, output_path, overwrite, debug, **kwargs):
    """Generates shopping list from .fitplan file."""
    input_file = model._tx_filename
    base_dir = output_path if output_path else os.path.dirname(input_file)
    base_name, _ = os.path.splitext(os.path.basename(input_file))
    output_file = os.path.abspath(join(base_dir, f"{base_name}_shopping.html"))

    if not overwrite and os.path.exists(output_file):
        click.echo(f'-- Skipping: {output_file}')
        return

    click.echo(f'-> Generating shopping list: {output_file}')

    fitplan_model, warnings = parse_model(input_file)
    if fitplan_model is None:
        return

    declarations = fitplan_model.declarations
    custom_ingredients = [d for d in declarations if d.__class__.__name__ == 'Ingredient']
    recipes = [d for d in declarations if d.__class__.__name__ == 'Recipe']
    plans = [d for d in declarations if d.__class__.__name__ == 'Plan']

    if not plans:
        click.echo('No plans found.')
        return

    plan = plans[0]
    weekly = generate_weekly_plan(plan, recipes)
    shopping = calc_shopping_list(weekly, custom_ingredients)

    # Group by category
    by_category = {}
    for name, data in shopping.items():
        cat = data['data'].get('category', 'other') if data['data'] else 'other'
        if cat not in by_category:
            by_category[cat] = []
        allergens = data['data'].get('allergens', []) if data['data'] else []
        by_category[cat].append({
            'name': name,
            'amount': format_grams(data['amount_g']),
            'allergens': allergens,
        })

    ordered_categories = [c for c in CATEGORY_NAMES if c in by_category]
    total_items = len(shopping)

    categories_html = ''
    for cat in ordered_categories:
        items = by_category[cat]
        cat_label = CATEGORY_NAMES.get(cat, cat)
        items_html = ''
        for item in sorted(items, key=lambda x: x['name']):
            allergen_html = f'<span class="allergen">⚠️ {", ".join(item["allergens"])}</span>' if item['allergens'] else ''
            items_html += f"""
            <li class="shopping-item">
                <label>
                    <input type="checkbox" onchange="this.parentElement.parentElement.classList.toggle('checked',this.checked)">
                    <span class="item-name">{item['name']}</span>
                    <span class="item-amount">{item['amount']}</span>
                </label>{allergen_html}
            </li>"""
        categories_html += f"""
        <div class="category-section">
            <h3 class="category-title">{cat_label}</h3>
            <ul class="shopping-list">{items_html}</ul>
        </div>"""

    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Shopping List — {plan.name}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}body{{font-family:'Segoe UI',sans-serif;background:#f0f4f8;color:#2d3748;padding:1.5rem;max-width:700px;margin:0 auto}}
header{{background:linear-gradient(135deg,#38a169,#276749);color:white;padding:1.5rem;border-radius:12px;margin-bottom:1.5rem}}
header h1{{font-size:1.5rem;margin-bottom:.3rem}}header p{{opacity:.85;font-size:.9rem}}
.stats{{display:flex;gap:1rem;margin-bottom:1.5rem}}.stat-box{{flex:1;background:white;border-radius:10px;padding:.8rem 1rem;text-align:center;box-shadow:0 2px 6px rgba(0,0,0,.06)}}
.stat-value{{font-size:1.4rem;font-weight:700;color:#276749}}.stat-label{{font-size:.78rem;color:#718096;text-transform:uppercase}}
.category-section{{background:white;border-radius:12px;margin-bottom:1rem;box-shadow:0 2px 6px rgba(0,0,0,.06);overflow:hidden}}
.category-title{{background:#f0fff4;padding:.7rem 1.2rem;font-size:1rem;color:#276749;border-bottom:1px solid #c6f6d5}}
.shopping-list{{list-style:none;padding:.5rem 0}}.shopping-item{{padding:.5rem 1.2rem;border-bottom:1px solid #f7fafc}}
.shopping-item.checked{{opacity:.45;text-decoration:line-through}}
.shopping-item label{{display:flex;align-items:center;gap:.8rem;cursor:pointer}}
input[type=checkbox]{{width:18px;height:18px;accent-color:#38a169;cursor:pointer}}
.item-name{{flex:1;font-size:.95rem}}.item-amount{{font-weight:600;color:#38a169;font-size:.9rem;min-width:80px;text-align:right}}
.allergen{{display:block;font-size:.75rem;color:#c05621;padding-left:2.4rem;margin-top:.1rem}}
.print-btn{{display:block;width:100%;padding:.9rem;background:#38a169;color:white;border:none;border-radius:10px;font-size:1rem;cursor:pointer;margin-top:1.5rem}}
.print-btn:hover{{background:#276749}}footer{{text-align:center;color:#a0aec0;font-size:.8rem;margin-top:2rem}}
@media print{{.print-btn{{display:none}}body{{background:white;padding:0}}}}
</style></head><body>
<header><h1>🛒 Shopping List</h1><p>Plan: <strong>{plan.name}</strong> · 7 days · {total_items} items</p>
<p>Generated: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p></header>
<div class="stats">
<div class="stat-box"><div class="stat-value">{total_items}</div><div class="stat-label">Items</div></div>
<div class="stat-box"><div class="stat-value">{len(ordered_categories)}</div><div class="stat-label">Categories</div></div>
<div class="stat-box"><div class="stat-value">7</div><div class="stat-label">Days</div></div>
</div>
{categories_html}
<button class="print-btn" onclick="window.print()">🖨️ Print List</button>
<footer>FitPlan DSL · {datetime.now().strftime('%Y')}</footer>
</body></html>"""

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    click.echo(f'OK Shopping list: {output_file}')
    click.echo(f'  Total items: {total_items} in {len(ordered_categories)} categories')
