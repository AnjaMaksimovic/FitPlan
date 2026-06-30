"""
FitPlan DSL — HTML Generator
Generates styled HTML page with recipe cards and weekly plan.
"""

import os
from datetime import datetime
from os.path import dirname, join

import click
from jinja2 import Environment, FileSystemLoader
from textx import generator

from ..main import parse_model
from ..nutrition_calc import calc_nutrition_for_recipe, calc_nutrition_for_day
from ..plan_generator import generate_weekly_plan, get_workouts_for_day, DAYS

THIS_FOLDER = dirname(dirname(__file__))


@generator('fitplan', 'html')
def html_generator(metamodel, model, output_path, overwrite, debug, **kwargs):
    """Generates HTML page from .fitplan file."""
    input_file = model._tx_filename
    base_dir = output_path if output_path else os.path.dirname(input_file)
    base_name, _ = os.path.splitext(os.path.basename(input_file))
    output_file = os.path.abspath(join(base_dir, f"{base_name}.html"))

    if not overwrite and os.path.exists(output_file):
        click.echo(f'-- Skipping: {output_file}')
        return

    click.echo(f'-> Generating HTML: {output_file}')

    fitplan_model, warnings = parse_model(input_file)
    if fitplan_model is None:
        return

    declarations = fitplan_model.declarations
    custom_ingredients = [d for d in declarations if d.__class__.__name__ == 'Ingredient']
    recipes = [d for d in declarations if d.__class__.__name__ == 'Recipe']
    workouts = [d for d in declarations if d.__class__.__name__ == 'Workout']
    plans = [d for d in declarations if d.__class__.__name__ == 'Plan']

    # Calculate nutrition for each recipe (per serving)
    recipe_data = []
    for r in recipes:
        nutrition = calc_nutrition_for_recipe(r, custom_ingredients, servings=1)
        recipe_data.append((r, nutrition))

    # Generate weekly plans
    plan_data = []
    for plan in plans:
        weekly = generate_weekly_plan(plan, recipes)
        day_details = []
        for day in DAYS:
            day_plan = weekly.get(day, {})
            day_nutrition = calc_nutrition_for_day(day_plan, custom_ingredients)
            day_workouts = get_workouts_for_day(workouts, day)
            workout_burns = sum(w.burns if w.burns else 0 for w in day_workouts)
            net_kcal = day_nutrition['calories'] - workout_burns
            day_details.append((day, day_plan, day_nutrition, day_workouts, workout_burns, net_kcal))
        plan_data.append((plan, day_details))

    # Render Jinja2 template
    jinja_env = Environment(
        loader=FileSystemLoader(join(THIS_FOLDER, 'templates')),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = jinja_env.get_template('fitplan.html')
    html = template.render(
        recipes=recipe_data,
        plans=plan_data,
        workouts=workouts,
        generated_at=datetime.now().strftime('%d.%m.%Y %H:%M'),
    )

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)

    click.echo(f'OK HTML generated: {output_file}')