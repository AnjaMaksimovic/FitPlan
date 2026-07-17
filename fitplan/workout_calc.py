"""
FitPlan DSL — Workout Calorie Calculator
Estimates calories burned using MET (Metabolic Equivalent of Task) values.

Formula: Calories = MET x weight_kg x duration_hours

MET values sourced from:
- Compendium of Physical Activities (Ainsworth et al.)
"""

# MET values by workout type and intensity
MET_TABLE = {
    'running':        {'low': 7.0,  'medium': 9.8,  'high': 12.8},
    'cycling':        {'low': 4.0,  'medium': 6.8,  'high': 10.0},
    'swimming':       {'low': 5.8,  'medium': 7.0,  'high': 9.8},
    'weightlifting':  {'low': 3.5,  'medium': 5.0,  'high': 6.0},
    'yoga':           {'low': 2.5,  'medium': 3.0,  'high': 4.0},
    'pilates':        {'low': 3.0,  'medium': 4.0,  'high': 5.0},
    'hiit':           {'low': 6.0,  'medium': 8.0,  'high': 12.0},
    'walking':        {'low': 2.5,  'medium': 3.5,  'high': 5.0},
    'rowing':         {'low': 4.8,  'medium': 7.0,  'high': 8.5},
    'elliptical':     {'low': 4.6,  'medium': 5.0,  'high': 6.3},
    'hiking':         {'low': 5.3,  'medium': 6.0,  'high': 7.8},
    'other':          {'low': 3.5,  'medium': 5.0,  'high': 7.0},
}

# Default body weight assumption (kg)
DEFAULT_WEIGHT_KG = 70

# Activities for burn-off suggestions
BURN_SUGGESTIONS = {
    'walking':  {'met': 3.5,  'description': 'brisk walking'},
    'running':  {'met': 9.8,  'description': 'moderate running'},
    'cycling':  {'met': 6.8,  'description': 'moderate cycling'},
    'yoga':     {'met': 3.0,  'description': 'yoga session'},
    'swimming': {'met': 7.0,  'description': 'moderate swimming'},
}


def estimate_calories_burned(workout_type, duration_min, intensity, weight_kg=None):
    """
    Estimates calories burned for a workout.

    Args:
        workout_type: str — type of workout (running, cycling, etc.)
        duration_min: int — duration in minutes
        intensity: str — 'low', 'medium', or 'high'
        weight_kg: float — body weight in kg (default: 70)

    Returns:
        int — estimated calories burned
    """
    if weight_kg is None:
        weight_kg = DEFAULT_WEIGHT_KG

    met_values = MET_TABLE.get(workout_type, MET_TABLE['other'])
    met = met_values.get(intensity, met_values['medium'])

    duration_hours = duration_min / 60.0
    calories = met * weight_kg * duration_hours

    return round(calories)


def get_workout_calories(workout, weight_kg=None):
    """
    Returns calories for a workout.
    Uses manually specified 'burns' if available, otherwise auto-calculates.
    """
    if hasattr(workout, 'burns') and workout.burns:
        return workout.burns
    return estimate_calories_burned(
        workout.type, workout.duration, workout.intensity, weight_kg
    )


def suggest_activity_for_excess(excess_kcal, weight_kg=None):
    """
    Suggests activities to burn off excess calories.

    Args:
        excess_kcal: int — calories to burn
        weight_kg: float — body weight

    Returns:
        list of dicts: [{'activity': str, 'duration_min': int, 'description': str}]
    """
    if weight_kg is None:
        weight_kg = DEFAULT_WEIGHT_KG

    suggestions = []

    for activity, data in BURN_SUGGESTIONS.items():
        met = data['met']
        hours_needed = excess_kcal / (met * weight_kg)
        minutes_needed = round(hours_needed * 60)

        if minutes_needed > 0:
            suggestions.append({
                'activity': activity,
                'duration_min': minutes_needed,
                'description': data['description'],
            })

    suggestions.sort(key=lambda x: x['duration_min'])
    return suggestions