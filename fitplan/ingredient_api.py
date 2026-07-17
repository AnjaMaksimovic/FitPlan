"""
FitPlan DSL — Ingredient API Client
Uses OpenFoodFacts API v2 to fetch nutritional data.
Results are cached locally to avoid repeated API calls.
"""

import json
import os
import requests
from os.path import dirname, join

CACHE_DIR = join(dirname(__file__), ".ingredient_cache")
API_URL = "https://world.openfoodfacts.org/api/v2/search"
HEADERS = {"User-Agent": "FitPlanDSL/1.0 (fitplan@example.com)"}


def _ensure_cache_dir():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR, exist_ok=True)


def _cache_path(name):
    safe_name = name.lower().replace(" ", "_")
    return join(CACHE_DIR, f"{safe_name}.json")


def _load_from_cache(name):
    path = _cache_path(name)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None


def _save_to_cache(name, data):
    _ensure_cache_dir()
    path = _cache_path(name)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def clear_cache():
    """Clears all cached API results."""
    import shutil
    if os.path.exists(CACHE_DIR):
        shutil.rmtree(CACHE_DIR)
        print("Ingredient cache cleared.")


def list_cached_ingredients():
    """Lists all cached ingredient names."""
    if not os.path.exists(CACHE_DIR):
        return []
    return [f.replace(".json", "") for f in os.listdir(CACHE_DIR) if f.endswith(".json")]


def fetch_ingredient_from_api(name):
    """
    Searches OpenFoodFacts for an ingredient using API v2.
    Returns dict with nutritional values per 100g, or None if not found.
    """
    cached = _load_from_cache(name)
    if cached is not None:
        return cached

    try:
        params = {
            "search_terms": name.replace("_", " "),
            "fields": "product_name,nutriments",
            "page_size": 5,
        }
        r = requests.get(API_URL, headers=HEADERS, params=params, timeout=5)
        if r.status_code != 200:
            return None

        products = r.json().get("products", [])
        if not products:
            return None

        for product in products:
            nutriments = product.get("nutriments", {})
            calories = nutriments.get("energy-kcal_100g")
            protein = nutriments.get("proteins_100g")

            if calories is not None and protein is not None:
                result = {
                    "calories": round(float(calories), 1),
                    "protein": round(float(protein or 0), 1),
                    "carbs": round(float(nutriments.get("carbohydrates_100g", 0)), 1),
                    "fat": round(float(nutriments.get("fat_100g", 0)), 1),
                    "fiber": round(float(nutriments.get("fiber_100g", 0)), 1),
                    "category": "other",
                    "source": "OpenFoodFacts",
                    "product_name": product.get("product_name", name),
                }
                _save_to_cache(name, result)
                return result

        return None

    except Exception as e:
        print(f"  [API] Could not fetch data for {name}: {e}")
        return None


def search_ingredient(name, custom_ingredients, builtin_db):
    """
    Searches for an ingredient: custom -> built-in DB -> OpenFoodFacts API.
    Returns (data_dict, source_string) or (None, None)
    """
    for ing in custom_ingredients:
        if ing.name == name:
            data = {
                "calories": ing.calories,
                "protein": ing.protein,
                "carbs": ing.carbs,
                "fat": ing.fat,
                "fiber": getattr(ing, "fiber", 0) or 0,
                "category": getattr(ing, "category", "other") or "other",
            }
            return data, "custom"

    if name in builtin_db:
        return builtin_db[name].copy(), "builtin"

    api_data = fetch_ingredient_from_api(name)
    if api_data:
        return api_data, "api"

    return None, None
