"""
Centralized function-calling registry for AI nutritional calculations.

- calculate_nutrition: Summarize nutrition for an ingredient list and servings (uses ingredient database)
- scale_recipe: Scale a recipe's ingredients and recompute nutrition
- get_ingredient_suggestions: Get ingredient combinations that naturally fit calorie targets
- suggest_lower_calorie_alternatives: Get lower-calorie ingredient swaps

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


def _convert_to_grams(quantity: float, unit: str, ingredient_name: str = "") -> float:
    """Convert quantity to grams, with special handling for pieces/items"""
    unit = unit.strip().lower()
    ingredient_lower = ingredient_name.strip().lower()
    
    # Special handling for items sold by piece (eggs, fruits, etc.)
    if not unit or unit in ("piece", "pieces", "item", "items", ""):
        # Check if this is a known per-piece ingredient
        if any(word in ingredient_lower for word in ["egg", "banana", "apple", "orange", "tomato"]):
            # Estimate weight per piece for nutrition calculation
            if "egg" in ingredient_lower:
                return quantity * 50.0  # 1 large egg ≈ 50g
            elif any(fruit in ingredient_lower for fruit in ["banana", "apple", "orange"]):
                return quantity * 150.0  # Average fruit ≈ 150g
            elif "tomato" in ingredient_lower:
                return quantity * 100.0  # Average tomato ≈ 100g
            else:
                # Generic piece - estimate 100g per piece
                return quantity * 100.0
    
    if unit in ("g", "gram", "grams"):
        return quantity
    if unit in ("kg", "kilogram", "kilograms"):
        return quantity * 1000.0
    if unit in ("oz", "ounce", "ounces"):
        return quantity * 28.35
    if unit in ("lb", "pound", "pounds"):
        return quantity * 453.59
    if unit in ("ml", "milliliter", "milliliters", "l", "liter", "liters"):
        # For liquids, assume 1ml ≈ 1g (water density)
        if unit.startswith("l") and not unit.startswith("ml"):
            return quantity * 1000.0
        return quantity
    # Unknown unit - assume grams
    return quantity

def _estimate_nutrition_for_ingredient(name: str, quantity: float, unit: str) -> Tuple[float, float, float, float]:
    """Return (cal, protein_g, carbs_g, fats_g) for provided quantity.
    FALLBACK: Used only if database lookup fails.
    All calculations assume quantity is already in g/ml aligned to data density.
    """
    n = name.lower()
    # crude defaults per 100g (or per piece for special items)
    
    # Special handling for eggs (per piece, not per 100g)
    if "egg" in n and quantity < 200:  # If quantity is small (<200), likely means pieces
        # 1 large egg ≈ 72 calories, 6g protein, 0.6g carbs, 5g fats
        eggs_count = quantity / 50.0  # Assuming quantity is already converted to grams (1 egg = 50g)
        return (72.0 * eggs_count, 6.0 * eggs_count, 0.6 * eggs_count, 5.0 * eggs_count)
    
    # Per 100g defaults
    if any(k in n for k in ("chicken", "beef", "turkey", "pork", "tofu")):
        base = (165.0, 31.0, 0.0, 4.0)
    elif any(k in n for k in ("rice", "pasta", "quinoa", "oat")):
        base = (130.0, 2.8, 28.0, 1.1)
    elif any(k in n for k in ("olive oil", "butter", "oil")):
        base = (884.0, 0.0, 0.0, 100.0)
    elif any(k in n for k in ("tomato", "cucumber", "lettuce", "vegetable", "carrot", "pepper")):
        base = (20.0, 1.0, 4.0, 0.1)
    elif any(k in n for k in ("cheese", "feta", "cheddar", "mozzarella")):
        base = (300.0, 20.0, 2.0, 25.0)  # Cheese is calorie-dense
    else:
        base = (50.0, 5.0, 10.0, 2.0)

    factor = quantity / 100.0
    return (base[0] * factor, base[1] * factor, base[2] * factor, base[3] * factor)


class NutritionFunctionRegistry:
    """Simple registry with explicit function definitions and execution."""
    
    def __init__(self, db_session: Optional[Any] = None):
        """Initialize registry with optional database session for ingredient lookups"""
        self.db = db_session
    
    def _find_ingredient_in_database(self, ingredient_name: str) -> Optional[Any]:
        """Find ingredient in database by name (fuzzy match)"""
        if not self.db:
            return None
        
        try:
            from models.recipe import Ingredient
            from difflib import SequenceMatcher
            
            ingredient_name_lower = ingredient_name.strip().lower()
            
            # Try exact match first (case-insensitive)
            exact_match = self.db.query(Ingredient).filter(
                Ingredient.name.ilike(ingredient_name_lower)
            ).first()
            if exact_match:
                logger.debug(f"✅ Exact match found: {exact_match.name} (unit: {exact_match.unit}, calories: {exact_match.calories})")
                return exact_match
            
            # For specific ingredients, try specific matches first (e.g., "cheddar cheese" should match "cheddar" not "cheese")
            # Priority: specific > generic
            if "cheddar" in ingredient_name_lower or "cheddar cheese" in ingredient_name_lower:
                # Prefer entries with higher calories (more accurate, e.g., 403 vs 113 cal/100g)
                cheddar_matches = self.db.query(Ingredient).filter(
                    Ingredient.name.ilike("%cheddar%")
                ).all()
                if cheddar_matches:
                    # Prefer "grated cheddar" or entries with unit="g" and calories > 200 (more accurate)
                    best_cheddar = None
                    best_score = 0
                    for m in cheddar_matches:
                        score = 0
                        if "grated" in m.name.lower() or "grated cheddar" in m.name.lower():
                            score += 10
                        if m.unit and m.unit.lower() == "g" and m.calories and m.calories > 200:
                            score += 5
                        if m.calories and m.calories > 300:
                            score += 3
                        if score > best_score:
                            best_score = score
                            best_cheddar = m
                    if best_cheddar:
                        logger.debug(f"✅ Specific match (cheddar): {best_cheddar.name} (unit: {best_cheddar.unit}, calories: {best_cheddar.calories})")
                        return best_cheddar
            
            if "egg" in ingredient_name_lower or "eggs" in ingredient_name_lower:
                # Prefer entries with unit="piece" or unit="large" (correct for eggs)
                egg_matches = self.db.query(Ingredient).filter(
                    Ingredient.name.ilike("%egg%")
                ).all()
                if egg_matches:
                    # Filter out egg noodles and eggplant
                    valid_eggs = [e for e in egg_matches if "noodle" not in e.name.lower() and "plant" not in e.name.lower()]
                    if valid_eggs:
                        # Prefer entries with unit="piece" or unit="large"
                        best_egg = None
                        best_score = 0
                        for e in valid_eggs:
                            score = 0
                            # Exact match "eggs" or "egg" is better than "eggs, separated"
                            if e.name.lower().strip() in ("eggs", "egg"):
                                score += 10
                            # Prefer "piece" or "large" unit
                            if e.unit and e.unit.lower() in ("piece", "pieces", "large"):
                                score += 10
                            # Prefer entries with calories around 70-155 (realistic for eggs)
                            if e.calories and 70 <= e.calories <= 155:
                                score += 5
                            if score > best_score:
                                best_score = score
                                best_egg = e
                        if best_egg:
                            logger.debug(f"✅ Specific match (egg): {best_egg.name} (unit: {best_egg.unit}, calories: {best_egg.calories})")
                            return best_egg
                        # Fallback to first valid egg
                        if valid_eggs:
                            logger.debug(f"✅ Fallback match (egg): {valid_eggs[0].name} (unit: {valid_eggs[0].unit}, calories: {valid_eggs[0].calories})")
                            return valid_eggs[0]
            
            # Try contains match
            contains_match = self.db.query(Ingredient).filter(
                Ingredient.name.ilike(f"%{ingredient_name_lower}%")
            ).all()
            
            if contains_match:
                # Find best match by similarity, preferring exact word matches
                best_match = None
                best_similarity = 0
                
                for ing in contains_match:
                    # Prefer matches where ingredient name contains the search term as a whole word
                    ing_name_lower = ing.name.lower()
                    if ingredient_name_lower in ing_name_lower.split() or ingredient_name_lower == ing_name_lower:
                        similarity = 1.0
                    else:
                        similarity = SequenceMatcher(None, ing_name_lower, ingredient_name_lower).ratio()
                    
                    if similarity > best_similarity:
                        best_similarity = similarity
                        best_match = ing
                
                if best_match and best_similarity > 0.6:  # 60% similarity threshold
                    logger.debug(f"✅ Contains match found: {best_match.name} (similarity: {best_similarity:.2f}, unit: {best_match.unit}, calories: {best_match.calories})")
                    return best_match
            
            # Try reverse contains (e.g., ingredient_name "chicken breast" matches "chicken")
            words = ingredient_name_lower.split()
            for word in words:
                if len(word) > 3:  # Only match words longer than 3 chars
                    word_match = self.db.query(Ingredient).filter(
                        Ingredient.name.ilike(f"%{word}%")
                    ).first()
                    if word_match:
                        logger.debug(f"✅ Word match found: {word_match.name} (from word: {word}, unit: {word_match.unit}, calories: {word_match.calories})")
                        return word_match
                        
            logger.debug(f"⚠️ No match found for ingredient: {ingredient_name}")
            return None
        except Exception as e:
            logger.warning(f"Error finding ingredient in database: {e}")
            return None
    
    def _get_nutrition_from_database(self, ingredient_name: str, quantity: float, unit: str) -> Tuple[float, float, float, float]:
        """Get nutrition from database or fallback to estimate"""
        db_ingredient = self._find_ingredient_in_database(ingredient_name)
        
        if db_ingredient and db_ingredient.calories and db_ingredient.calories > 0:
            # Check if database stores ingredient as "per piece" vs "per 100g"
            db_unit = db_ingredient.unit.lower() if db_ingredient.unit else "g"
            recipe_unit = unit.lower().strip() if unit else ""
            
            # CRITICAL FIX: Detect if ingredient is likely pieces even if unit is empty
            # For eggs: "eggs - 2" with empty unit should be treated as 2 pieces, not 2g
            ingredient_name_lower = ingredient_name.lower()
            is_piece_item = any(word in ingredient_name_lower for word in ["egg", "banana", "apple", "orange", "tomato"])
            
            # If database has "piece" OR "large" (for eggs), use quantity directly
            if db_unit in ("piece", "pieces", "item", "items", "large"):
                # Use quantity directly (it's already in pieces)
                # For eggs: database has 155 cal per "large", recipe has "2 eggs" → 155 × 2 = 310 cal
                multiplier = quantity
                logger.debug(f"📦 Using piece-based calculation: {quantity} {db_unit} × {db_ingredient.calories} cal/{db_unit}")
            elif is_piece_item and not recipe_unit:
                # Ingredient is piece-item (eggs, banana) with empty unit, but DB stores as grams
                # Convert pieces to grams first, then calculate per 100g
                # For eggs: "eggs - 2" → 2 pieces × 50g/piece = 100g → 155 cal/100g × 1 = 155 cal
                # BUT: if DB has eggs stored as "large" or "piece", we should have caught it above
                # So this means DB has eggs as "g" with cal/100g, but recipe has pieces
                # Estimate: 1 large egg ≈ 50g, so 2 eggs ≈ 100g
                quantity_g = _convert_to_grams(quantity, unit, ingredient_name)
                multiplier = quantity_g / 100.0
                logger.debug(f"⚖️ Using piece-to-gram conversion: {quantity} pieces → {quantity_g}g ÷ 100g × {db_ingredient.calories} cal/100g")
            else:
                # Database stores as "per 100g" - convert recipe quantity to grams
                quantity_g = _convert_to_grams(quantity, unit, ingredient_name)
                multiplier = quantity_g / 100.0
                logger.debug(f"⚖️ Using gram-based calculation: {quantity_g}g ÷ 100g × {db_ingredient.calories} cal/100g")
            
            cal = (db_ingredient.calories or 0) * multiplier
            pro = (db_ingredient.protein or 0) * multiplier
            carb = (db_ingredient.carbs or 0) * multiplier
            fat = (db_ingredient.fats or 0) * multiplier
            
            # Log what we actually found for debugging
            logger.info(f"✅ Found {ingredient_name} in database: {cal:.1f} cal for {quantity} {unit or db_unit} (DB: {db_ingredient.name}, unit: {db_ingredient.unit}, cal: {db_ingredient.calories}/{db_unit}, multiplier: {multiplier:.2f})")
            return (cal, pro, carb, fat)
        else:
            # Fallback to estimate
            logger.warning(f"⚠️ Using fallback estimate for {ingredient_name} (not found in database)")
            quantity_g = _convert_to_grams(quantity, unit, ingredient_name)
            return _estimate_nutrition_for_ingredient(ingredient_name, quantity_g, "g")

    def definitions(self) -> List[Dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": "calculate_nutrition",
                    "description": "Calculates nutrition totals for an ingredient list and servings using ingredient database. Returns accurate nutrition values based on actual ingredient data.",
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
            },
            {
                "type": "function",
                "function": {
                    "name": "get_ingredient_suggestions",
                    "description": "Get ingredient combinations from database that naturally fit a calorie target for a meal type. Returns suggestions with quantities that create realistic portions.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "target_calories": {"type": "number", "minimum": 100, "maximum": 1000},
                            "meal_type": {"type": "string", "enum": ["breakfast", "lunch", "dinner", "snack"]},
                            "dietary_preferences": {"type": "array", "items": {"type": "string"}, "default": []},
                            "max_ingredients": {"type": "number", "minimum": 2, "maximum": 8, "default": 6}
                        },
                        "required": ["target_calories", "meal_type"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "suggest_lower_calorie_alternatives",
                    "description": "Suggest lower-calorie ingredient alternatives from database. Returns swaps that reduce calories while maintaining similar function (e.g., butter -> olive oil, cream -> milk).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "ingredient_name": {"type": "string"},
                            "current_quantity": {"type": "number"},
                            "unit": {"type": "string"}
                        },
                        "required": ["ingredient_name"]
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
            if name == "get_ingredient_suggestions":
                return self._get_ingredient_suggestions(arguments)
            if name == "suggest_lower_calorie_alternatives":
                return self._suggest_lower_calorie_alternatives(arguments)
            raise FunctionCallError("UNKNOWN_FUNCTION", f"Unknown function: {name}")
        except FunctionCallError as e:
            logger.warning(f"Function call error [{e.code}]: {e.message}")
            return {"error": {"code": e.code, "message": e.message}}
        except Exception as e:
            logger.exception("Unhandled function execution error")
            return {"error": {"code": "EXECUTION_ERROR", "message": str(e)}}

    def _calculate_nutrition(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate nutrition using ingredient database (not estimates)"""
        ingredients = args.get("ingredients")
        servings = _coerce_positive_number(args.get("servings"), "servings")
        if not isinstance(ingredients, list) or len(ingredients) == 0:
            raise FunctionCallError("INVALID_PARAM", "ingredients must be a non-empty array")

        if not self.db:
            logger.warning(f"⚠️ Database session not available - using estimates for all ingredients (accuracy reduced)")

        total_cal = total_pro = total_carb = total_fat = 0.0
        db_used_count = 0
        
        for ing in ingredients:
            if not isinstance(ing, dict):
                raise FunctionCallError("INVALID_PARAM", "ingredient must be an object")
            name = str(ing.get("name", "")).strip()
            if not name:
                raise FunctionCallError("INVALID_PARAM", "ingredient.name is required")
            qty = _coerce_positive_number(ing.get("quantity", 0), "ingredient.quantity")
            unit = _normalize_unit(ing.get("unit"))
            
            # ROOT CAUSE FIX: Use database lookup instead of estimates
            cal, pro, carb, fat = self._get_nutrition_from_database(name, qty, unit)
            total_cal += cal
            total_pro += pro
            total_carb += carb
            total_fat += fat
            
            # Track if we used database (check if estimate was used)
            db_ing = self._find_ingredient_in_database(name)
            if db_ing and db_ing.calories and db_ing.calories > 0:
                db_used_count += 1

        per_serving = {
            "calories": round(total_cal / servings, 1),
            "protein": round(total_pro / servings, 1),
            "carbs": round(total_carb / servings, 1),
            "fats": round(total_fat / servings, 1),
        }
        
        result = {
            "totals": {
                "calories": round(total_cal, 1),
                "protein": round(total_pro, 1),
                "carbs": round(total_carb, 1),
                "fats": round(total_fat, 1),
                "servings": servings,
            },
            "per_serving": per_serving,
            "database_used": db_used_count,
            "total_ingredients": len(ingredients)
        }
        
        logger.info(f"✅ Calculated nutrition: {per_serving['calories']} cal (used DB for {db_used_count}/{len(ingredients)} ingredients)")
        if db_used_count < len(ingredients):
            missing = len(ingredients) - db_used_count
            logger.warning(f"⚠️ {missing} ingredient(s) not found in database - using estimates (accuracy may be reduced)")
        return result

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
    
    def _get_ingredient_suggestions(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get ingredient combinations from database that naturally fit calorie target"""
        if not self.db:
            return {"error": {"code": "DATABASE_UNAVAILABLE", "message": "Database session not available"}}
        
        try:
            target_calories = _coerce_positive_number(args.get("target_calories"), "target_calories")
            meal_type = str(args.get("meal_type", "")).lower()
            max_ingredients = int(args.get("max_ingredients", 6))
            dietary_prefs = args.get("dietary_preferences", []) or []
            
            if meal_type not in ["breakfast", "lunch", "dinner", "snack"]:
                raise FunctionCallError("INVALID_PARAM", "meal_type must be breakfast, lunch, dinner, or snack")
            
            from models.recipe import Ingredient
            
            # Define meal type categories and calorie distribution
            meal_guidelines = {
                "breakfast": {
                    "categories": ["protein", "grains", "dairy", "fruits"],
                    "distributions": {"protein": 0.30, "grains": 0.30, "dairy": 0.20, "vegetables": 0.10, "fruits": 0.10}
                },
                "lunch": {
                    "categories": ["protein", "grains", "vegetables"],
                    "distributions": {"protein": 0.35, "grains": 0.30, "vegetables": 0.25, "fats": 0.10}
                },
                "dinner": {
                    "categories": ["protein", "vegetables", "grains"],
                    "distributions": {"protein": 0.40, "vegetables": 0.30, "grains": 0.20, "fats": 0.10}
                },
                "snack": {
                    "categories": ["fruits", "nuts", "dairy"],
                    "distributions": {"fruits": 0.40, "nuts": 0.30, "dairy": 0.30}
                }
            }
            
            guidelines = meal_guidelines.get(meal_type, meal_guidelines["lunch"])
            
            # Build query
            query = self.db.query(Ingredient).filter(
                Ingredient.calories > 0,
                Ingredient.calories.isnot(None)
            )
            
            # Filter by dietary preferences
            is_vegetarian = "vegetarian" in [p.lower() for p in dietary_prefs]
            is_vegan = "vegan" in [p.lower() for p in dietary_prefs]
            
            if is_vegan:
                query = query.filter(~Ingredient.category.in_(["protein", "dairy"]))
            elif is_vegetarian:
                query = query.filter(~Ingredient.category.in_(["protein"]))
            
            # Get ingredients by category
            suggestions = []
            total_cal = 0
            
            for category, calorie_share in guidelines["distributions"].items():
                category_cal = target_calories * calorie_share
                
                # Get ingredients in this category with appropriate calorie density
                cat_query = query.filter(Ingredient.category == category)
                
                # For protein, get moderate-calorie options (150-200 cal/100g)
                # For vegetables, get low-calorie options (<50 cal/100g)
                # For grains, get moderate options (100-150 cal/100g)
                
                category_ingredients = cat_query.order_by(Ingredient.id).limit(10).all()
                
                if category_ingredients:
                    # Pick ingredient that fits calorie budget with reasonable portion
                    for ing in category_ingredients:
                        cal_per_100g = ing.calories or 0
                        if cal_per_100g > 0:
                            # Calculate reasonable quantity to hit calorie target for this category
                            quantity_g = (category_cal / cal_per_100g) * 100
                            
                            # Ensure reasonable portions (50g-300g for most, 10g-50g for high-calorie)
                            if cal_per_100g > 500:  # High-calorie (oils, nuts)
                                quantity_g = min(max(quantity_g, 10), 50)
                            elif cal_per_100g > 200:  # Medium-high (cheese, some proteins)
                                quantity_g = min(max(quantity_g, 30), 150)
                            else:  # Low-medium calorie
                                quantity_g = min(max(quantity_g, 50), 300)
                            
                            actual_cal = (cal_per_100g * quantity_g) / 100.0
                            
                            suggestions.append({
                                "name": ing.name,
                                "quantity": round(quantity_g, 1),
                                "unit": "g",
                                "category": category,
                                "calories": round(actual_cal, 1),
                                "protein": round((ing.protein or 0) * quantity_g / 100, 1),
                                "carbs": round((ing.carbs or 0) * quantity_g / 100, 1),
                                "fats": round((ing.fats or 0) * quantity_g / 100, 1)
                            })
                            total_cal += actual_cal
                            
                            if len(suggestions) >= max_ingredients:
                                break
                            break  # One ingredient per category for now
            
            return {
                "suggestions": suggestions[:max_ingredients],
                "total_calories": round(total_cal, 1),
                "target_calories": target_calories,
                "difference": round(abs(total_cal - target_calories), 1),
                "meal_type": meal_type
            }
            
        except FunctionCallError:
            raise
        except Exception as e:
            logger.error(f"Error getting ingredient suggestions: {e}")
            return {"error": {"code": "EXECUTION_ERROR", "message": str(e)}}
    
    def _suggest_lower_calorie_alternatives(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest lower-calorie ingredient alternatives from database"""
        if not self.db:
            return {"error": {"code": "DATABASE_UNAVAILABLE", "message": "Database session not available"}}
        
        try:
            ingredient_name = str(args.get("ingredient_name", "")).strip()
            if not ingredient_name:
                raise FunctionCallError("INVALID_PARAM", "ingredient_name is required")
            
            current_quantity = args.get("current_quantity")
            unit = str(args.get("unit", "g")).strip()
            
            # Find current ingredient
            current_ing = self._find_ingredient_in_database(ingredient_name)
            if not current_ing:
                return {"alternatives": [], "message": f"Ingredient '{ingredient_name}' not found in database"}
            
            current_cal_per_100g = current_ing.calories or 0
            if current_cal_per_100g <= 0:
                return {"alternatives": [], "message": "Current ingredient has no calorie data"}
            
            from models.recipe import Ingredient
            
            # Find lower-calorie alternatives in same category
            category = current_ing.category
            alternatives = []
            
            # Query same category with lower calories
            query = self.db.query(Ingredient).filter(
                Ingredient.category == category,
                Ingredient.calories < current_cal_per_100g,
                Ingredient.calories > 0,
                Ingredient.id != current_ing.id
            ).order_by(Ingredient.calories.asc()).limit(5)
            
            for alt_ing in query.all():
                cal_per_100g = alt_ing.calories or 0
                calorie_reduction = current_cal_per_100g - cal_per_100g
                reduction_percent = (calorie_reduction / current_cal_per_100g) * 100
                
                # Calculate equivalent quantity for similar calories
                if current_quantity:
                    current_quantity_g = _convert_to_grams(float(current_quantity), unit, ingredient_name)
                    equivalent_cal = (current_cal_per_100g * current_quantity_g) / 100.0
                    equivalent_quantity_g = (equivalent_cal / cal_per_100g) * 100.0 if cal_per_100g > 0 else 0
                    equivalent_quantity_g = min(max(equivalent_quantity_g, 10), 500)  # Reasonable range
                else:
                    equivalent_quantity_g = 100
                
                alternatives.append({
                    "name": alt_ing.name,
                    "quantity": round(equivalent_quantity_g, 1),
                    "unit": "g",
                    "calories_per_100g": round(cal_per_100g, 1),
                    "current_calories_per_100g": round(current_cal_per_100g, 1),
                    "calorie_reduction_percent": round(reduction_percent, 1),
                    "reason": f"{reduction_percent:.0f}% fewer calories"
                })
            
            # Also check similar categories (e.g., butter -> olive oil)
            category_swaps = {
                "fats": ["oils"],
                "dairy": ["alternatives"],
                "protein": ["lean protein"]
            }
            
            swap_categories = category_swaps.get(category, [])
            for swap_cat in swap_categories:
                swap_query = self.db.query(Ingredient).filter(
                    Ingredient.category == swap_cat,
                    Ingredient.calories < current_cal_per_100g,
                    Ingredient.calories > 0
                ).order_by(Ingredient.calories.asc()).limit(3)
                
                for alt_ing in swap_query.all():
                    cal_per_100g = alt_ing.calories or 0
                    calorie_reduction = current_cal_per_100g - cal_per_100g
                    reduction_percent = (calorie_reduction / current_cal_per_100g) * 100 if current_cal_per_100g > 0 else 0
                    
                    if reduction_percent > 10:  # Only suggest if meaningful reduction
                        alternatives.append({
                            "name": alt_ing.name,
                            "quantity": 100,
                            "unit": "g",
                            "calories_per_100g": round(cal_per_100g, 1),
                            "current_calories_per_100g": round(current_cal_per_100g, 1),
                            "calorie_reduction_percent": round(reduction_percent, 1),
                            "reason": f"Category swap: {reduction_percent:.0f}% fewer calories"
                        })
            
            return {
                "current_ingredient": ingredient_name,
                "alternatives": alternatives[:5],  # Return top 5
                "message": f"Found {len(alternatives)} lower-calorie alternatives"
            }
            
        except FunctionCallError:
            raise
        except Exception as e:
            logger.error(f"Error suggesting alternatives: {e}")
            return {"error": {"code": "EXECUTION_ERROR", "message": str(e)}}


# Global registry instance (will be initialized with db session when needed)
registry = NutritionFunctionRegistry()








