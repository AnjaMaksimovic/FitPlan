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


if __name__ == "__main__":
    server.start_io()