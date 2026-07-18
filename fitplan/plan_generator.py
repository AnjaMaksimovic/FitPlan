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
    Generates a 7-day meal plan based on meal options and filters.

    Filters:
    - no_repeat_same_day: don't use same protein source for lunch and dinner
    - max_per_week: limit how many times a recipe appears per week
    """
    # Parse filters
    no_repeat_same_day = False
    max_per_week = {}

    if hasattr(plan, 'filters') and plan.filters:
        for f in plan.filters:
            if hasattr(f, 'recipe') and f.recipe:
                max_per_week[f.recipe.name] = f.count
            else:
                no_repeat_same_day = True

    # Build options dict
    options = {}
    for assignment in plan.assignments:
        recipes = []
        for ref in assignment.options.recipes:
            recipes.append({
                'recipe': ref.recipe,
                'servings': ref.servings if ref.servings else 1
            })
        options[assignment.type] = recipes

    # Track weekly usage
    weekly_usage = {}

    # Generate plan for each day
    weekly_plan = {}

    for day in DAYS:
        day_plan = {}
        day_proteins = []

        for meal_type in ['breakfast', 'lunch', 'dinner', 'snack']:
            if meal_type not in options:
                continue

            available = options[meal_type]
            candidates = []

            for opt in available:
                recipe_name = opt['recipe'].name

                # Check max_per_week filter
                if recipe_name in max_per_week:
                    if weekly_usage.get(recipe_name, 0) >= max_per_week[recipe_name]:
                        continue

                # Check no_repeat_same_day filter
                if no_repeat_same_day and meal_type in ('lunch', 'dinner'):
                    protein_cat = get_recipe_protein_category(opt['recipe'])
                    if protein_cat and protein_cat in day_proteins:
                        continue

                candidates.append(opt)

            if not candidates:
                candidates = available

            day_index = DAYS.index(day)
            pick_index = day_index % len(candidates)
            chosen = candidates[pick_index]

            day_plan[meal_type] = chosen

            # Track usage
            weekly_usage[chosen['recipe'].name] = weekly_usage.get(chosen['recipe'].name, 0) + 1

            protein_cat = get_recipe_protein_category(chosen['recipe'])
            if protein_cat:
                day_proteins.append(protein_cat)

        weekly_plan[day] = day_plan

    return weekly_plan


def get_workouts_for_day(workouts, day_name):
    """Returns all workouts scheduled for a given day."""
    return [w for w in workouts if day_name in w.days]
