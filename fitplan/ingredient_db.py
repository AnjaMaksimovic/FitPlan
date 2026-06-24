"""
FitPlan DSL — Built-in Ingredient Database
Contains nutritional values for common ingredients per 100g/100ml.
Users can reference these by name without defining values manually.
Custom ingredients can still be defined in .fitplan files to override or extend.
"""

# Format: name -> {calories, protein, carbs, fat, fiber, category}
# All values per 100g unless noted otherwise

BUILTIN_INGREDIENTS = {
    # === MEAT & POULTRY ===
    "ChickenBreast":    {"calories": 165, "protein": 31.0, "carbs": 0.0,  "fat": 3.6,  "fiber": 0, "category": "meat"},
    "ChickenThigh":     {"calories": 209, "protein": 26.0, "carbs": 0.0,  "fat": 10.9, "fiber": 0, "category": "meat"},
    "Turkey":           {"calories": 135, "protein": 30.0, "carbs": 0.0,  "fat": 1.0,  "fiber": 0, "category": "meat"},
    "GroundBeef":       {"calories": 250, "protein": 26.0, "carbs": 0.0,  "fat": 17.0, "fiber": 0, "category": "meat"},
    "LeanBeef":         {"calories": 192, "protein": 28.0, "carbs": 0.0,  "fat": 9.0,  "fiber": 0, "category": "meat"},
    "Pork":             {"calories": 242, "protein": 27.0, "carbs": 0.0,  "fat": 14.0, "fiber": 0, "category": "meat"},

    # === FISH & SEAFOOD ===
    "Salmon":           {"calories": 208, "protein": 20.0, "carbs": 0.0,  "fat": 13.0, "fiber": 0, "category": "fish", "allergens": ["fish"]},
    "Tuna":             {"calories": 130, "protein": 29.0, "carbs": 0.0,  "fat": 1.0,  "fiber": 0, "category": "fish", "allergens": ["fish"]},
    "Shrimp":           {"calories": 85,  "protein": 20.0, "carbs": 0.0,  "fat": 0.5,  "fiber": 0, "category": "fish", "allergens": ["shellfish"]},
    "CodFish":          {"calories": 82,  "protein": 18.0, "carbs": 0.0,  "fat": 0.7,  "fiber": 0, "category": "fish", "allergens": ["fish"]},

    # === DAIRY ===
    "Egg":              {"calories": 155, "protein": 13.0, "carbs": 1.1,  "fat": 11.0, "fiber": 0, "category": "dairy"},
    "Milk":             {"calories": 61,  "protein": 3.2,  "carbs": 4.8,  "fat": 3.3,  "fiber": 0, "category": "dairy", "allergens": ["lactose"]},
    "GreekYogurt":      {"calories": 97,  "protein": 9.0,  "carbs": 3.6,  "fat": 5.0,  "fiber": 0, "category": "dairy", "allergens": ["lactose"]},
    "Cheese":           {"calories": 402, "protein": 25.0, "carbs": 1.3,  "fat": 33.0, "fiber": 0, "category": "dairy", "allergens": ["lactose"]},
    "CottageCheese":    {"calories": 98,  "protein": 11.0, "carbs": 3.4,  "fat": 4.3,  "fiber": 0, "category": "dairy", "allergens": ["lactose"]},
    "AlmondMilk":       {"calories": 17,  "protein": 0.6,  "carbs": 0.3,  "fat": 1.4,  "fiber": 0, "category": "dairy", "allergens": ["nuts"]},

    # === VEGETABLES ===
    "Broccoli":         {"calories": 34,  "protein": 2.8,  "carbs": 6.6,  "fat": 0.4,  "fiber": 2.6, "category": "vegetable"},
    "Spinach":          {"calories": 23,  "protein": 2.9,  "carbs": 3.6,  "fat": 0.4,  "fiber": 2.2, "category": "vegetable"},
    "Tomato":           {"calories": 18,  "protein": 0.9,  "carbs": 3.9,  "fat": 0.2,  "fiber": 1.2, "category": "vegetable"},
    "Cucumber":         {"calories": 15,  "protein": 0.7,  "carbs": 3.6,  "fat": 0.1,  "fiber": 0.5, "category": "vegetable"},
    "SweetPotato":      {"calories": 86,  "protein": 1.6,  "carbs": 20.0, "fat": 0.1,  "fiber": 3.0, "category": "vegetable"},
    "Carrot":           {"calories": 41,  "protein": 0.9,  "carbs": 10.0, "fat": 0.2,  "fiber": 2.8, "category": "vegetable"},
    "BellPepper":       {"calories": 31,  "protein": 1.0,  "carbs": 6.0,  "fat": 0.3,  "fiber": 2.1, "category": "vegetable"},
    "Onion":            {"calories": 40,  "protein": 1.1,  "carbs": 9.3,  "fat": 0.1,  "fiber": 1.7, "category": "vegetable"},
    "Garlic":           {"calories": 149, "protein": 6.4,  "carbs": 33.0, "fat": 0.5,  "fiber": 2.1, "category": "vegetable"},
    "Mushroom":         {"calories": 22,  "protein": 3.1,  "carbs": 3.3,  "fat": 0.3,  "fiber": 1.0, "category": "vegetable"},
    "Zucchini":         {"calories": 17,  "protein": 1.2,  "carbs": 3.1,  "fat": 0.3,  "fiber": 1.0, "category": "vegetable"},
    "Leek":             {"calories": 61,  "protein": 1.5,  "carbs": 14.0, "fat": 0.3,  "fiber": 1.8, "category": "vegetable"},

    # === FRUIT ===
    "Banana":           {"calories": 89,  "protein": 1.1,  "carbs": 23.0, "fat": 0.3,  "fiber": 2.6, "category": "fruit"},
    "Apple":            {"calories": 52,  "protein": 0.3,  "carbs": 14.0, "fat": 0.2,  "fiber": 2.4, "category": "fruit"},
    "Blueberry":        {"calories": 57,  "protein": 0.7,  "carbs": 14.0, "fat": 0.3,  "fiber": 2.4, "category": "fruit"},
    "Strawberry":       {"calories": 32,  "protein": 0.7,  "carbs": 7.7,  "fat": 0.3,  "fiber": 2.0, "category": "fruit"},
    "Avocado":          {"calories": 160, "protein": 2.0,  "carbs": 9.0,  "fat": 15.0, "fiber": 7.0, "category": "fruit"},
    "Orange":           {"calories": 47,  "protein": 0.9,  "carbs": 12.0, "fat": 0.1,  "fiber": 2.4, "category": "fruit"},

    # === GRAINS ===
    "Oats":             {"calories": 389, "protein": 17.0, "carbs": 66.0, "fat": 7.0,  "fiber": 10.0, "category": "grain"},
    "BrownRice":        {"calories": 370, "protein": 7.9,  "carbs": 77.0, "fat": 2.9,  "fiber": 3.5,  "category": "grain"},
    "WhiteRice":        {"calories": 365, "protein": 7.1,  "carbs": 80.0, "fat": 0.7,  "fiber": 1.3,  "category": "grain"},
    "Quinoa":           {"calories": 368, "protein": 14.0, "carbs": 64.0, "fat": 6.0,  "fiber": 7.0,  "category": "grain"},
    "Pasta":            {"calories": 371, "protein": 13.0, "carbs": 75.0, "fat": 1.5,  "fiber": 3.2,  "category": "grain", "allergens": ["gluten"]},
    "Bread":            {"calories": 265, "protein": 9.0,  "carbs": 49.0, "fat": 3.2,  "fiber": 2.7,  "category": "grain", "allergens": ["gluten"]},

    # === LEGUMES ===
    "Lentils":          {"calories": 352, "protein": 25.0, "carbs": 60.0, "fat": 1.1,  "fiber": 31.0, "category": "legume"},
    "Chickpeas":        {"calories": 364, "protein": 19.0, "carbs": 61.0, "fat": 6.0,  "fiber": 17.0, "category": "legume"},
    "BlackBeans":       {"calories": 341, "protein": 21.0, "carbs": 63.0, "fat": 0.9,  "fiber": 16.0, "category": "legume"},
    "Tofu":             {"calories": 76,  "protein": 8.0,  "carbs": 1.9,  "fat": 4.8,  "fiber": 0.3,  "category": "legume"},

    # === FATS & OILS ===
    "OliveOil":         {"calories": 884, "protein": 0.0,  "carbs": 0.0,  "fat": 100.0, "fiber": 0, "category": "fat"},
    "CoconutOil":       {"calories": 862, "protein": 0.0,  "carbs": 0.0,  "fat": 100.0, "fiber": 0, "category": "fat"},
    "Butter":           {"calories": 717, "protein": 0.9,  "carbs": 0.1,  "fat": 81.0,  "fiber": 0, "category": "fat", "allergens": ["lactose"]},
    "Almonds":          {"calories": 579, "protein": 21.0, "carbs": 22.0, "fat": 50.0,  "fiber": 12.0, "category": "fat", "allergens": ["nuts"]},
    "Walnuts":          {"calories": 654, "protein": 15.0, "carbs": 14.0, "fat": 65.0,  "fiber": 6.7,  "category": "fat", "allergens": ["nuts"]},
    "PeanutButter":     {"calories": 588, "protein": 25.0, "carbs": 20.0, "fat": 50.0,  "fiber": 6.0,  "category": "fat", "allergens": ["nuts"]},

    # === OTHER ===
    "Honey":            {"calories": 304, "protein": 0.3,  "carbs": 82.0, "fat": 0.0,  "fiber": 0, "category": "sweetener"},
    "ProteinPowder":    {"calories": 375, "protein": 75.0, "carbs": 10.0, "fat": 3.0,  "fiber": 0, "category": "other"},
}


def get_ingredient(name):
    """
    Returns ingredient data by name from built-in database.
    Returns None if not found.
    """
    return BUILTIN_INGREDIENTS.get(name)


def get_all_ingredients():
    """Returns all built-in ingredient names."""
    return list(BUILTIN_INGREDIENTS.keys())


def get_ingredients_by_category(category):
    """Returns all ingredient names in a given category."""
    return [
        name for name, data in BUILTIN_INGREDIENTS.items()
        if data.get("category") == category
    ]
