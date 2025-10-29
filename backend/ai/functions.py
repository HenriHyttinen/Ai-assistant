"""
Centralized function-calling registry for AI nutritional calculations.

- calculate_nutrition: Summarize nutrition for an ingredient list and servings
- scale_recipe: Scale a recipe's ingredients and recompute nutrition

All functions must:
  - validate input against expected schema
  - raise structured errors with clear codes
  - return JSON-serializable dicts
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import math
import logging

logger = logging.getLogger(__name__)


class FunctionCallError(Exception):
    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
        self.message = message


def _coerce_positive_number(value: Any, field: str) -> float:
    try:
        num = float(value)
        if not math.isfinite(num) or num < 0:
            raise ValueError
        return num
    except Exception:
        raise FunctionCallError("INVALID_PARAM", f"{field} must be a non-negative number")


def _normalize_unit(unit: Optional[str]) -> str:
    if not unit:
        return "g"
    u = unit.strip().lower()
    # standardize to grams for solids, ml for liquids; defaults to grams
    if u in ("g", "gram", "grams"):
        return "g"
    if u in ("ml", "milliliter", "milliliters"):
        return "ml"
    # Fallback: treat unknown as grams to keep invariants
    return "g"


def _estimate_nutrition_for_ingredient(name: str, quantity: float, unit: str) -> Tuple[float, float, float, float]:
    """Return (cal, protein_g, carbs_g, fats_g) for provided quantity.
    Placeholder logic; callers should replace with DB-backed lookup when available.
    All calculations assume quantity is already in g/ml aligned to data density.
    """
    n = name.lower()
    # crude defaults per 100g
    if any(k in n for k in ("chicken", "beef", "turkey", "pork", "tofu")):
        base = (165.0, 31.0, 0.0, 4.0)
    elif any(k in n for k in ("rice", "pasta", "quinoa", "oat")):
        base = (130.0, 2.8, 28.0, 1.1)
    elif any(k in n for k in ("olive oil", "butter", "oil")):
        base = (884.0, 0.0, 0.0, 100.0)
    elif any(k in n for k in ("tomato", "cucumber", "lettuce", "vegetable", "carrot", "pepper")):
        base = (20.0, 1.0, 4.0, 0.1)
    else:
        base = (50.0, 5.0, 10.0, 2.0)

    factor = quantity / 100.0
    return (base[0] * factor, base[1] * factor, base[2] * factor, base[3] * factor)


class NutritionFunctionRegistry:
    """Simple registry with explicit function definitions and execution."""

    def definitions(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "calculate_nutrition",
                    "description": "Calculates nutrition totals for an ingredient list and servings.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ingredients": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "quantity": {"type": "number"},
                                        "unit": {"type": "string"}
                                    },
                                    "required": ["name", "quantity"]
                                }
                            },
                            "servings": {"type": "number", "minimum": 1}
                        },
                        "required": ["ingredients", "servings"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "scale_recipe",
                    "description": "Scale ingredients to target servings and return scaled list.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ingredients": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                        "quantity": {"type": "number"},
                                        "unit": {"type": "string"}
                                    },
                                    "required": ["name", "quantity"]
                                }
                            },
                            "current_servings": {"type": "number", "minimum": 1},
                            "target_servings": {"type": "number", "minimum": 1}
                        },
                        "required": ["ingredients", "current_servings", "target_servings"]
                    }
                }
            }
        ]

    def execute(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if name == "calculate_nutrition":
                return self._calculate_nutrition(arguments)
            if name == "scale_recipe":
                return self._scale_recipe(arguments)
            raise FunctionCallError("UNKNOWN_FUNCTION", f"Unknown function: {name}")
        except FunctionCallError as e:
            logger.warning(f"Function call error [{e.code}]: {e.message}")
            return {"error": {"code": e.code, "message": e.message}}
        except Exception as e:
            logger.exception("Unhandled function execution error")
            return {"error": {"code": "EXECUTION_ERROR", "message": str(e)}}

    def _calculate_nutrition(self, args: Dict[str, Any]) -> Dict[str, Any]:
        ingredients = args.get("ingredients")
        servings = _coerce_positive_number(args.get("servings"), "servings")
        if not isinstance(ingredients, list) or len(ingredients) == 0:
            raise FunctionCallError("INVALID_PARAM", "ingredients must be a non-empty array")

        total_cal = total_pro = total_carb = total_fat = 0.0
        for ing in ingredients:
            if not isinstance(ing, dict):
                raise FunctionCallError("INVALID_PARAM", "ingredient must be an object")
            name = str(ing.get("name", "")).strip()
            if not name:
                raise FunctionCallError("INVALID_PARAM", "ingredient.name is required")
            qty = _coerce_positive_number(ing.get("quantity", 0), "ingredient.quantity")
            unit = _normalize_unit(ing.get("unit"))
            cal, pro, carb, fat = _estimate_nutrition_for_ingredient(name, qty, unit)
            total_cal += cal
            total_pro += pro
            total_carb += carb
            total_fat += fat

        per_serving = {
            "calories": round(total_cal / servings, 1),
            "protein": round(total_pro / servings, 1),
            "carbs": round(total_carb / servings, 1),
            "fats": round(total_fat / servings, 1),
        }
        return {
            "totals": {
                "calories": round(total_cal, 1),
                "protein": round(total_pro, 1),
                "carbs": round(total_carb, 1),
                "fats": round(total_fat, 1),
                "servings": servings,
            },
            "per_serving": per_serving,
        }

    def _scale_recipe(self, args: Dict[str, Any]) -> Dict[str, Any]:
        ingredients = args.get("ingredients")
        current_servings = _coerce_positive_number(args.get("current_servings"), "current_servings")
        target_servings = _coerce_positive_number(args.get("target_servings"), "target_servings")
        if current_servings <= 0:
            raise FunctionCallError("INVALID_PARAM", "current_servings must be > 0")
        if not isinstance(ingredients, list) or len(ingredients) == 0:
            raise FunctionCallError("INVALID_PARAM", "ingredients must be a non-empty array")

        factor = target_servings / current_servings
        scaled = []
        for ing in ingredients:
            name = str(ing.get("name", "")).strip()
            if not name:
                raise FunctionCallError("INVALID_PARAM", "ingredient.name is required")
            qty = _coerce_positive_number(ing.get("quantity", 0), "ingredient.quantity")
            unit = _normalize_unit(ing.get("unit"))
            scaled.append({
                "name": name,
                "quantity": round(qty * factor, 2),
                "unit": unit,
            })

        return {
            "ingredients": scaled,
            "factor": round(factor, 4),
            "current_servings": current_servings,
            "target_servings": target_servings,
        }


registry = NutritionFunctionRegistry()


