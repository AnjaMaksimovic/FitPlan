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


def run_all_validations(model):
    """Runs all validations on the model. Returns list of warnings."""
    warnings = []

    for decl in model.declarations:
        cls = decl.__class__.__name__

        if cls == 'Ingredient':
            validate_ingredient_values(decl)

        elif cls == 'Recipe':
            validate_recipe_serves(decl)
            validate_recipe_time(decl)
            validate_recipe_has_ingredients(decl)
            validate_recipe_has_steps(decl)

        elif cls == 'MealOptions':
            validate_options_not_empty(decl)

        elif cls == 'Workout':
            validate_workout_days(decl)
            validate_workout_burns(decl)

    return warnings