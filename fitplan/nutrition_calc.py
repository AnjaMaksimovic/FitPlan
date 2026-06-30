"""
FitPlan DSL — Nutritional calculation engine.
Handles unit conversion, per-serving scaling, and daily/weekly aggregation.
"""

from .ingredient_db import BUILTIN_INGREDIENTS

# Unit to grams conversion table
UNIT_TO_GRAMS = {
    'g': 1.0,
    'kg': 1000.0,
    'ml': 1.0,
    'l': 1000.0,
    'tbsp': 15.0,
    'tsp': 5.0,
    'piece': 100.0,
    'pieces': 100.0,
}


def amount_in_grams(amount, unit):
    """Converts an amount to grams using the conversion table."""
    return amount * UNIT_TO_GRAMS.get(unit, 1.0)


def resolve_ingredient(name, custom_ingredients):
    """
    Resolves an ingredient by name.
    Search order: custom definitions -> built-in database.
    Returns dict with nutritional values or None.
    """
    # Check custom ingredients first
    for ing in custom_ingredients:
        if ing.name == name:
            return {
                "calories": ing.calories,
                "protein": ing.protein,
                "carbs": ing.carbs,
                "fat": ing.fat,
                "fiber": getattr(ing, "fiber", 0) or 0,
                "category": getattr(ing, "category", "other") or "other",
            }

    # Fall back to built-in database
    if name in BUILTIN_INGREDIENTS:
        return BUILTIN_INGREDIENTS[name].copy()

    return None


def calc_nutrition_for_recipe(recipe, custom_ingredients, servings=1):
    """
    Calculates total nutritional values for a recipe.
    Scales from per-100g reference to actual amount used,
    then divides by serving count and multiplies by requested servings.
    """
    total = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0}

    for item in recipe.items:
        ing_data = resolve_ingredient(item.ingredient, custom_ingredients)
        if not ing_data:
            continue

        # Convert to grams and scale from per-100g
        factor = amount_in_grams(item.amount, item.unit) / 100.0

        for key in total:
            total[key] += ing_data.get(key, 0) * factor

    # Scale by servings
    per_serving_factor = servings / recipe.serves
    return {k: v * per_serving_factor for k, v in total.items()}


def calc_nutrition_for_day(day_plan, custom_ingredients):
    """
    Calculates total nutrition for a day's meal plan.
    day_plan: { 'breakfast': {'recipe': ..., 'servings': ...}, ... }
    """
    total = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'fiber': 0}

    for meal_type, meal_data in day_plan.items():
        recipe = meal_data['recipe']
        servings = meal_data.get('servings', 1)
        n = calc_nutrition_for_recipe(recipe, custom_ingredients, servings)
        for key in total:
            total[key] += n[key]

    return total


def calc_shopping_list(weekly_plan, custom_ingredients):
    """
    Aggregates all ingredients from the generated weekly plan.
    Returns: { ingredient_name: { 'amount_g': float, 'data': dict } }
    """
    shopping = {}

    for day, day_plan in weekly_plan.items():
        for meal_type, meal_data in day_plan.items():
            recipe = meal_data['recipe']
            factor = meal_data.get('servings', 1) / recipe.serves

            for item in recipe.items:
                name = item.ingredient
                amount_g = amount_in_grams(item.amount, item.unit) * factor
                ing_data = resolve_ingredient(name, custom_ingredients)

                if name in shopping:
                    shopping[name]['amount_g'] += amount_g
                else:
                    shopping[name] = {
                        'amount_g': amount_g,
                        'data': ing_data or {},
                    }

    return shopping


def format_grams(grams):
    """Formats grams into a readable string."""
    if grams >= 1000:
        return f"{grams / 1000:.2f} kg"
    return f"{grams:.0f} g"
