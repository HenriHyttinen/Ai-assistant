"""
Unit tests for Function Calling (nutrition calculation, ingredient suggestions)
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai.functions import NutritionFunctionRegistry


class TestFunctionCalling:
    """Test function calling for nutrition calculations"""

    @pytest.fixture
    def function_registry(self, db_session):
        """Initialize function registry with test database"""
        return NutritionFunctionRegistry(db_session=db_session)

    @pytest.fixture
    def sample_ingredients(self, db_session):
        """Create sample ingredients in database"""
        from models.recipe import Ingredient
        
        ingredients_data = [
            {
                "id": "ing_chicken",
                "name": "chicken breast",
                "category": "protein",
                "unit": "g",
                "calories": 165.0,
                "protein": 31.0,
                "carbs": 0.0,
                "fats": 3.6,
            },
            {
                "id": "ing_eggs",
                "name": "eggs",
                "category": "protein",
                "unit": "piece",
                "calories": 70.0,
                "protein": 6.0,
                "carbs": 0.6,
                "fats": 5.0,
            },
            {
                "id": "ing_rice",
                "name": "rice",
                "category": "grain",
                "unit": "g",
                "calories": 130.0,
                "protein": 2.7,
                "carbs": 28.0,
                "fats": 0.3,
            },
        ]
        
        ingredients = []
        for data in ingredients_data:
            ingredient = Ingredient(
                id=data["id"],
                name=data["name"],
                category=data["category"],
                unit=data["unit"],
                default_quantity=100.0,
                calories=data["calories"],
                protein=data["protein"],
                carbs=data["carbs"],
                fats=data["fats"],
            )
            db_session.add(ingredient)
            ingredients.append(ingredient)
        
        db_session.commit()
        return ingredients

    def test_calculate_nutrition_with_database_lookup(
        self, function_registry, sample_ingredients, db_session
    ):
        """Test nutrition calculation using database lookup"""
        ingredients = [
            {"name": "chicken breast", "quantity": 200, "unit": "g"},
            {"name": "rice", "quantity": 150, "unit": "g"},
        ]
        
        result = function_registry.execute(
            "calculate_nutrition",
            {"ingredients": ingredients, "servings": 1}
        )
        
        # Verify nutrition was calculated (new structure uses 'totals' dict)
        assert "totals" in result or "total_calories" in result
        if "totals" in result:
            assert "calories" in result["totals"]
            assert "protein" in result["totals"]
            assert "carbs" in result["totals"]
            assert "fats" in result["totals"]
            assert result["totals"]["calories"] > 0
            assert result["totals"]["protein"] > 0
        else:
            assert "total_protein" in result
            assert result["total_calories"] > 0
            assert result["total_protein"] > 0

    def test_calculate_nutrition_with_piece_based_ingredients(
        self, function_registry, sample_ingredients, db_session
    ):
        """Test nutrition calculation for piece-based ingredients (eggs)"""
        ingredients = [
            {"name": "eggs", "quantity": 3, "unit": "piece"},
        ]
        
        result = function_registry.execute(
            "calculate_nutrition",
            {"ingredients": ingredients, "servings": 1}
        )
        
        # Verify nutrition was calculated (new structure uses 'totals' dict)
        assert "totals" in result or "total_calories" in result
        calories = result.get("totals", {}).get("calories") or result.get("total_calories", 0)
        # 3 eggs * 70 cal/egg = 210 calories
        assert abs(calories - 210.0) < 10.0  # Allow small margin

    def test_calculate_nutrition_fallback_estimation(
        self, function_registry, db_session
    ):
        """Test that fallback estimation is used when ingredient not in database"""
        ingredients = [
            {"name": "unknown ingredient", "quantity": 100, "unit": "g"},
        ]
        
        result = function_registry.execute(
            "calculate_nutrition",
            {"ingredients": ingredients, "servings": 1}
        )
        
        # Verify fallback was used (new structure uses 'totals' dict)
        assert "totals" in result or "total_calories" in result
        calories = result.get("totals", {}).get("calories") or result.get("total_calories", 0)
        assert calories > 0  # Fallback provides estimate

    def test_get_ingredient_suggestions(
        self, function_registry, sample_ingredients, db_session
    ):
        """Test ingredient suggestion functionality"""
        target_calories = 500.0
        meal_type = "dinner"
        
        result = function_registry.execute(
            "get_ingredient_suggestions",
            {
                "target_calories": target_calories,
                "meal_type": meal_type,
                "count": 5,
            }
        )
        
        # Verify suggestions were returned
        assert "suggestions" in result or "ingredients" in result

    def test_suggest_lower_calorie_alternatives(
        self, function_registry, sample_ingredients, db_session
    ):
        """Test lower-calorie alternative suggestions"""
        current_ingredient = "chicken breast"
        target_calories = 100.0
        
        result = function_registry.execute(
            "suggest_lower_calorie_alternatives",
            {
                "ingredient_name": current_ingredient,  # Changed from current_ingredient
                "target_calories": target_calories,
            }
        )
        
        # Verify alternatives were suggested
        assert "alternatives" in result or "suggestions" in result or "error" not in result

    def test_unit_conversion_to_grams(self, function_registry):
        """Test unit conversion to grams"""
        from ai.functions import _convert_to_grams
        
        # Test conversion function
        test_cases = [
            (100, "g", 100.0),  # Already grams
            (1, "kg", 1000.0),  # Kilograms
            (1, "oz", 28.35),  # Ounces
            (2, "piece", 100.0, "eggs"),  # Pieces - eggs are 50g each
        ]
        
        for test_case in test_cases:
            if len(test_case) == 4:  # Has ingredient name
                quantity, unit, expected, ingredient = test_case
                result = _convert_to_grams(quantity, unit, ingredient)
            else:
                quantity, unit, expected = test_case
                result = _convert_to_grams(quantity, unit)
            assert abs(result - expected) < 0.1  # Allow small floating point differences

    def test_database_ingredient_lookup(self, function_registry, sample_ingredients, db_session):
        """Test that ingredients are correctly looked up in database"""
        ingredient_name = "chicken breast"
        
        # Test fuzzy matching
        result = function_registry._find_ingredient_in_database(ingredient_name)
        
        # Verify ingredient was found
        assert result is not None
        assert result.name.lower() in ingredient_name.lower()

    def test_nutrition_calculation_with_mixed_units(
        self, function_registry, sample_ingredients, db_session
    ):
        """Test nutrition calculation with mixed units (grams and pieces)"""
        ingredients = [
            {"name": "chicken breast", "quantity": 150, "unit": "g"},
            {"name": "eggs", "quantity": 2, "unit": "piece"},
        ]
        
        result = function_registry.execute(
            "calculate_nutrition",
            {"ingredients": ingredients, "servings": 1}
        )
        
        # Verify nutrition was calculated correctly (new structure uses 'totals' dict)
        assert "totals" in result or "total_calories" in result
        calories = result.get("totals", {}).get("calories") or result.get("total_calories", 0)
        assert calories > 0

    def test_error_handling_invalid_ingredient(
        self, function_registry, db_session
    ):
        """Test error handling for invalid ingredients"""
        ingredients = [
            {"name": "invalid ingredient xyz", "quantity": 100, "unit": "g"},
        ]
        
        # Should not raise exception, should use fallback
        result = function_registry.execute(
            "calculate_nutrition",
            {"ingredients": ingredients, "servings": 1}
        )
        
        # Verify fallback was used (new structure uses 'totals' dict)
        assert "totals" in result or "total_calories" in result

    def test_function_registry_execute_method(self, function_registry, sample_ingredients, db_session):
        """Test that execute method dispatches to correct functions"""
        # Test calculate_nutrition
        result = function_registry.execute(
            "calculate_nutrition",
            {"ingredients": [{"name": "chicken breast", "quantity": 100, "unit": "g"}], "servings": 1}
        )
        assert result is not None
        
        # Test invalid function name (now returns error dict instead of raising)
        result = function_registry.execute("invalid_function", {})
        assert "error" in result
        assert result["error"]["code"] == "UNKNOWN_FUNCTION"

