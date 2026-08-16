"""
FitPlan DSL - Language Server Protocol (LSP) Server
Provides code completion, hover documentation and real-time diagnostics
for .fitplan files in VS Code.
"""

import logging
import tempfile
import os
from typing import Optional

from pygls.lsp.server import LanguageServer
from lsprotocol.types import (
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_HOVER,
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CHANGE,
    CompletionItem,
    CompletionItemKind,
    CompletionList,
    CompletionParams,
    Diagnostic,
    DiagnosticSeverity,
    DidChangeTextDocumentParams,
    DidOpenTextDocumentParams,
    Hover,
    HoverParams,
    MarkupContent,
    MarkupKind,
    Position,
    Range,
)

logging.basicConfig(level=logging.INFO)
server = LanguageServer("fitplan-lsp", "v0.1")

# =====================================================================
# COMPLETION ITEMS
# =====================================================================

TOP_LEVEL_KEYWORDS = [
    "ingredient", "recipe", "options", "workout", "plan"
]

RECIPE_KEYWORDS = [
    "serves", "time", "difficulty", "ingredients", "steps", "tags"
]

PLAN_KEYWORDS = [
    "goal", "target_calories", "target_macros", "meals", "filters"
]

WORKOUT_KEYWORDS = [
    "type", "duration", "intensity", "days", "burns"
]

INGREDIENT_KEYWORDS = [
    "per", "calories", "protein", "carbs", "fat", "fiber",
    "allergens", "category"
]

DIFFICULTY_VALUES = ["easy", "medium", "hard"]

GOAL_VALUES = ["weightLoss", "muscleGain", "maintenance", "endurance"]

WORKOUT_TYPES = [
    "running", "cycling", "swimming", "weightlifting",
    "yoga", "pilates", "hiit", "walking", "rowing",
    "elliptical", "hiking", "other"
]

INTENSITY_VALUES = ["low", "medium", "high"]

DAYS_VALUES = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday"
]

MEAL_TYPES = ["breakfast", "lunch", "dinner", "snack"]

FILTER_VALUES = ["no_repeat_same_day", "max_per_week"]

CATEGORIES = [
    "meat", "fish", "dairy", "vegetable", "fruit",
    "grain", "legume", "fat", "sweetener", "other"
]

BUILTIN_INGREDIENTS = [
    "ChickenBreast", "ChickenThigh", "Turkey", "GroundBeef", "LeanBeef", "Pork",
    "Salmon", "Tuna", "Shrimp", "CodFish",
    "Egg", "Milk", "GreekYogurt", "Cheese", "CottageCheese", "AlmondMilk",
    "Broccoli", "Spinach", "Tomato", "Cucumber", "SweetPotato", "Carrot",
    "BellPepper", "Onion", "Garlic", "Mushroom", "Zucchini", "Leek",
    "Banana", "Apple", "Blueberry", "Strawberry", "Avocado", "Orange",
    "Oats", "BrownRice", "WhiteRice", "Quinoa", "Pasta", "Bread",
    "Lentils", "Chickpeas", "BlackBeans", "Tofu", "Tempeh", "Edamame",
    "OliveOil", "CoconutOil", "Butter", "Almonds", "Walnuts", "PeanutButter",
    "Hummus", "Tahini", "Honey", "ProteinPowder",
]

UNITS = ["g", "kg", "ml", "l", "tbsp", "tsp", "piece", "pieces"]


def make_completion_items(words, kind=CompletionItemKind.Keyword):
    return [CompletionItem(label=w, kind=kind) for w in words]


def get_bracket_context(text: str, position: Position) -> str:
    """
    Analyzes the text to determine what block the cursor is in.
    Returns the name of the outermost unclosed block.
    """
    lines = text.split("\n")
    flat = "\n".join(lines[:position.line + 1])

    depth = 0
    current_block = None
    block_stack = []

    i = 0
    tokens = flat.replace("{", " { ").replace("}", " } ").split()

    for idx, token in enumerate(tokens):
        if token == "{":
            depth += 1
            if idx > 0:
                block_stack.append(tokens[idx - 1])
        elif token == "}":
            depth -= 1
            if block_stack:
                block_stack.pop()

    if block_stack:
        return block_stack[-1]
    return "toplevel"


@server.feature(TEXT_DOCUMENT_COMPLETION)
def completions(params: CompletionParams):
    doc = server.workspace.text_documents.get(params.text_document.uri)
    if not doc:
        return CompletionList(is_incomplete=False, items=[])

    text = doc.source
    position = params.position
    context = get_bracket_context(text, position)

    items = []

    if context == "toplevel":
        items = make_completion_items(TOP_LEVEL_KEYWORDS)
    elif context in ("recipe",):
        items = make_completion_items(RECIPE_KEYWORDS)
    elif context in ("ingredients",):
        items = make_completion_items(BUILTIN_INGREDIENTS, CompletionItemKind.Value)
        items += make_completion_items(UNITS, CompletionItemKind.Unit)
    elif context in ("steps",):
        items = [CompletionItem(label='step "description"', kind=CompletionItemKind.Snippet)]
    elif context in ("workout",):
        items = make_completion_items(WORKOUT_KEYWORDS)
    elif context in ("type",):
        items = make_completion_items(WORKOUT_TYPES, CompletionItemKind.EnumMember)
    elif context in ("intensity",):
        items = make_completion_items(INTENSITY_VALUES, CompletionItemKind.EnumMember)
    elif context in ("days",):
        items = make_completion_items(DAYS_VALUES, CompletionItemKind.EnumMember)
    elif context in ("plan",):
        items = make_completion_items(PLAN_KEYWORDS)
    elif context in ("goal",):
        items = make_completion_items(GOAL_VALUES, CompletionItemKind.EnumMember)
    elif context in ("meals",):
        items = make_completion_items(MEAL_TYPES)
    elif context in ("filters",):
        items = make_completion_items(FILTER_VALUES)
    elif context in ("ingredient",):
        items = make_completion_items(INGREDIENT_KEYWORDS)
    elif context in ("category",):
        items = make_completion_items(CATEGORIES, CompletionItemKind.EnumMember)
    elif context in ("difficulty",):
        items = make_completion_items(DIFFICULTY_VALUES, CompletionItemKind.EnumMember)
    else:
        items = make_completion_items(TOP_LEVEL_KEYWORDS)

    return CompletionList(is_incomplete=False, items=items)

# =====================================================================
# HOVER DOCUMENTATION
# =====================================================================

HOVER_DOCS = {
    "recipe": "**recipe** — Defines a recipe with ingredients and preparation steps.\n\nUsage:\n```\nrecipe RecipeName {\n    serves 2\n    time 30 min\n    difficulty easy\n    ingredients { ... }\n    steps { ... }\n}\n```",
    "ingredient": "**ingredient** — Optional custom food item. Most common ingredients are already in the built-in database.\n\nUsage:\n```\ningredient MyIngredient {\n    per 100g\n    calories 200 kcal\n    protein 10 g\n    carbs 20 g\n    fat 5 g\n}\n```",
    "options": "**options** — Defines meal variations for a meal type. The plan generator automatically distributes these across 7 days.\n\nUsage:\n```\noptions lunch_options {\n    ChickenWithBroccoli\n    SalmonWithQuinoa servings 1\n}\n```",
    "workout": "**workout** — Defines a training session assigned to specific days. Calories burned are auto-calculated using MET values.\n\nUsage:\n```\nworkout StrengthTraining {\n    type weightlifting\n    duration 60 min\n    intensity high\n    days [Monday, Wednesday, Friday]\n}\n```",
    "plan": "**plan** — Defines a weekly nutrition and training plan. The system automatically generates a 7-day schedule.\n\nUsage:\n```\nplan MyPlan {\n    goal weightLoss\n    target_calories 1800 kcal\n    target_macros { protein 40 % carbs 30 % fat 30 % }\n    meals { breakfast from breakfast_options }\n}\n```",
    "weightLoss": "**weightLoss** — Goal for losing weight. Recommended calorie target: 1200–2000 kcal/day.",
    "muscleGain": "**muscleGain** — Goal for building muscle mass. Recommended calorie target: 2200–3500 kcal/day.",
    "maintenance": "**maintenance** — Goal for maintaining current weight. Recommended calorie target: 1800–2500 kcal/day.",
    "endurance": "**endurance** — Goal for improving cardiovascular endurance. Recommended calorie target: 2000–3000 kcal/day.",
    "running": "**running** — MET values: low=7.0, medium=9.8, high=12.8\n\nExample (70kg, 30min, medium): **343 kcal**",
    "weightlifting": "**weightlifting** — MET values: low=3.5, medium=5.0, high=6.0\n\nExample (70kg, 60min, high): **420 kcal**",
    "yoga": "**yoga** — MET values: low=2.5, medium=3.0, high=4.0\n\nExample (70kg, 45min, low): **131 kcal**",
    "cycling": "**cycling** — MET values: low=4.0, medium=6.8, high=10.0\n\nExample (70kg, 45min, medium): **357 kcal**",
    "hiit": "**hiit** — MET values: low=6.0, medium=8.0, high=12.0\n\nExample (70kg, 30min, high): **420 kcal**",
    "no_repeat_same_day": "**no_repeat_same_day** — Filter that prevents using the same protein source for lunch and dinner on the same day.\n\nExample: if lunch has ChickenWithBroccoli (meat), dinner will not be another meat dish.",
    "max_per_week": "**max_per_week** — Filter that limits how many times a recipe appears in the weekly plan.\n\nUsage: `max_per_week RecipeName 3`",
    "ChickenBreast": "**ChickenBreast** (built-in) — 165 kcal | 31g protein | 0g carbs | 3.6g fat per 100g\n\nCategory: meat",
    "Salmon": "**Salmon** (built-in) — 208 kcal | 20g protein | 0g carbs | 13g fat per 100g\n\nCategory: fish | Allergens: fish",
    "Oats": "**Oats** (built-in) — 389 kcal | 17g protein | 66g carbs | 7g fat per 100g\n\nCategory: grain",
    "Quinoa": "**Quinoa** (built-in) — 368 kcal | 14g protein | 64g carbs | 6g fat per 100g\n\nCategory: grain",
    "Avocado": "**Avocado** (built-in) — 160 kcal | 2g protein | 9g carbs | 15g fat per 100g\n\nCategory: fruit",
}


@server.feature(TEXT_DOCUMENT_HOVER)
def hover(params: HoverParams):
    doc = server.workspace.text_documents.get(params.text_document.uri)
    if not doc:
        return None

    position = params.position
    lines = doc.source.split("\n")
    if position.line >= len(lines):
        return None

    line = lines[position.line]
    char = position.character

    # Find word under cursor
    start = char
    end = char
    while start > 0 and (line[start-1].isalnum() or line[start-1] == "_"):
        start -= 1
    while end < len(line) and (line[end].isalnum() or line[end] == "_"):
        end += 1

    word = line[start:end].strip()

    if word in HOVER_DOCS:
        return Hover(
            contents=MarkupContent(
                kind=MarkupKind.Markdown,
                value=HOVER_DOCS[word]
            ),
            range=Range(
                start=Position(line=position.line, character=start),
                end=Position(line=position.line, character=end)
            )
        )

    return None

if __name__ == "__main__":
    server.start_io()