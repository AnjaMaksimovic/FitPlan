"""
FitPlan DSL — Metamodel loader and model parser.
"""

from os.path import dirname, join
from textx import metamodel_from_file, language
from textx.exceptions import TextXSemanticError, TextXSyntaxError

THIS_FOLDER = dirname(__file__)


def get_mm():
    """Creates and returns the FitPlan metamodel."""
    return metamodel_from_file(join(THIS_FOLDER, 'grammars', 'fitplan.tx'))


def parse_model(model_filename):
    """
    Parses a .fitplan file and returns the model.
    Returns (model, warnings) or (None, None) on error.
    """
    mm = get_mm()
    try:
        model = mm.model_from_file(model_filename)
    except TextXSyntaxError as e:
        print(f"Syntax error in '{model_filename}': {e}")
        return None, None
    except TextXSemanticError as e:
        print(f"Semantic error in '{model_filename}': {e}")
        return None, None
    return model, []


@language('fitplan', '*.fitplan')
def fitplan_language():
    """FitPlan DSL — language for nutrition and training planning."""
    return get_mm()
