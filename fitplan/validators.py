from .ingredient_db import BUILTIN_INGREDIENTS
def validate_ingredient_values(ingredient):
    """Nutritional values cannot be negative."""
    for field in ['calories', 'protein', 'carbs', 'fat']:
        if getattr(ingredient, field) < 0:
            raise ValueError(
                f"Ingredient '{ingredient.name}': '{field}' cannot be negative"
            )


def validate_recipe_serves(recipe):
    """Serves must be positive."""
    if recipe.serves <= 0:
        raise ValueError(f"Recipe '{recipe.name}': serves must be positive")


def validate_recipe_time(recipe):
    """Time must be positive."""
    if recipe.time <= 0:
        raise ValueError(f"Recipe '{recipe.name}': time must be positive")


def validate_recipe_has_ingredients(recipe):
    """Recipe must have at least one ingredient."""
    if not recipe.items:
        raise ValueError(f"Recipe '{recipe.name}': must have at least one ingredient")


def validate_recipe_has_steps(recipe):
    """Recipe must have at least one step."""
    if not recipe.steps:
        raise ValueError(f"Recipe '{recipe.name}': must have at least one step")


def validate_options_not_empty(meal_options):
    """Options block must contain at least one recipe."""
    if not meal_options.recipes:
        raise ValueError(f"Options '{meal_options.name}': must contain at least one recipe")


def validate_workout_days(workout):
    """Workout must have at least one day assigned."""
    if not workout.days:
        raise ValueError(f"Workout '{workout.name}': must have at least one day assigned")


def validate_workout_burns(workout):
    """Burns cannot be negative (0 means auto-calculate)."""
    if hasattr(workout, 'burns') and workout.burns is not None and workout.burns < 0:
        raise ValueError(f"Workout '{workout.name}': burns cannot be negative")

def validate_macros_sum(plan):
    """Macronutrient percentages must sum to exactly 100%."""
    total = plan.protein_pct + plan.carbs_pct + plan.fat_pct
    if total != 100:
        raise ValueError(
            f"Plan '{plan.name}': macronutrient percentages must sum to 100%, "
            f"currently {total}%"
        )


def validate_target_calories(plan):
    """Target calories must be at least 1000 kcal."""
    if plan.target_calories < 1000:
        raise ValueError(
            f"Plan '{plan.name}': target_calories must be at least 1000 kcal, "
            f"currently {plan.target_calories}"
        )


def validate_plan_has_meals(plan):
    """Plan must have at least one meal assignment."""
    if not plan.assignments:
        raise ValueError(f"Plan '{plan.name}': must have at least one meal assignment")


def validate_goal_calories(plan):
    """Warning if goal is inconsistent with target calories."""
    warnings = []
    if plan.goal == 'weightLoss' and plan.target_calories > 2500:
        warnings.append(
            f"Warning: Plan '{plan.name}': goal is weightLoss but "
            f"target_calories ({plan.target_calories}) is high"
        )
    if plan.goal == 'muscleGain' and plan.target_calories < 1800:
        warnings.append(
            f"Warning: Plan '{plan.name}': goal is muscleGain but "
            f"target_calories ({plan.target_calories}) is low"
        )
    if plan.goal == 'endurance' and plan.target_calories < 2000:
        warnings.append(
            f"Warning: Plan '{plan.name}': goal is endurance but "
            f"target_calories ({plan.target_calories}) may be low for endurance training."
        )
    return warnings
def validate_recipe_ingredients_exist(recipe, custom_ingredients):
    """Checks that all ingredients exist in built-in DB, custom definitions, or API."""
    from .ingredient_api import fetch_ingredient_from_api
    custom_names = [ing.name for ing in custom_ingredients]
    for item in recipe.items:
        name = item.ingredient
        if name not in BUILTIN_INGREDIENTS and name not in custom_names:
            # Try API as last resort
            api_data = fetch_ingredient_from_api(name)
            if api_data:
                print(f"  [API] Found '{name}' via OpenFoodFacts")
            else:
                raise ValueError(
                    f"Recipe '{recipe.name}': ingredient '{name}' not found "
                    f"in built-in database or OpenFoodFacts API. "
                    f"Define it as a custom ingredient."
                )
def run_all_validations(model):
    """Runs all validations on the model. Returns list of warnings."""
    warnings = []
    custom_ingredients = [
        d for d in model.declarations
        if d.__class__.__name__ == 'Ingredient'
    ]
    for decl in model.declarations:
        cls = decl.__class__.__name__

        if cls == 'Ingredient':
            validate_ingredient_values(decl)

        elif cls == 'Recipe':
            validate_recipe_serves(decl)
            validate_recipe_time(decl)
            validate_recipe_has_ingredients(decl)
            validate_recipe_has_steps(decl)
            validate_recipe_ingredients_exist(decl, custom_ingredients)

        elif cls == 'MealOptions':
            validate_options_not_empty(decl)

        elif cls == 'Workout':
            validate_workout_days(decl)
            validate_workout_burns(decl)

        elif cls == 'Plan':
            validate_macros_sum(decl)
            validate_target_calories(decl)
            validate_plan_has_meals(decl)
            warnings.extend(validate_goal_calories(decl))

    return warnings
