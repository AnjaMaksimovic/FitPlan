"""
FitPlan DSL — Plan Generator
Automatically distributes meals across 7 days based on options.
"""

from .ingredient_db import BUILTIN_INGREDIENTS

DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


def get_recipe_protein_category(recipe):
    """
    Determines the main protein category of a recipe
    by checking which ingredient contributes the most protein.
    """
    max_protein = 0
    main_category = None

    for item in recipe.items:
        ing_data = BUILTIN_INGREDIENTS.get(item.ingredient)
        if ing_data and ing_data['protein'] > max_protein:
            max_protein = ing_data['protein']
            main_category = ing_data.get('category')

    return main_category


def generate_weekly_plan(plan, all_recipes):
    """
    Generates a 7-day meal plan based on meal options.
    Rotates through options for variety.
    Returns: { 'Monday': { 'breakfast': {'recipe': ..., 'servings': ...}, ... }, ... }
    """
    # Build options dict: { 'breakfast': [{'recipe': ..., 'servings': ...}], ... }
    options = {}
    for assignment in plan.assignments:
        recipes = []
        for ref in assignment.options.recipes:
            recipes.append({
                'recipe': ref.recipe,
                'servings': ref.servings if ref.servings else 1
            })
        options[assignment.type] = recipes

    # Generate plan for each day
    weekly_plan = {}

    for day in DAYS:
        day_plan = {}

        for meal_type in ['breakfast', 'lunch', 'dinner', 'snack']:
            if meal_type not in options:
                continue

            available = options[meal_type]

            # Rotate through options based on day index
            day_index = DAYS.index(day)
            pick_index = day_index % len(available)
            chosen = available[pick_index]

            day_plan[meal_type] = chosen

        weekly_plan[day] = day_plan

    return weekly_plan


def get_workouts_for_day(workouts, day_name):
    """Returns all workouts scheduled for a given day."""
    return [w for w in workouts if day_name in w.days]
