"""
AI-Powered Ingredient Substitution Service
Allows users to substitute ingredients in recipes with AI-generated alternatives
based on dietary restrictions, allergies, or availability.
"""

from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from ai.nutrition_ai import NutritionAI
from models.recipe import Recipe, Ingredient
from services.measurement_standardization_service import MeasurementStandardizationService
import logging

logger = logging.getLogger(__name__)

class IngredientSubstitutionService:
    """Service for AI-powered ingredient substitution"""
    
    def __init__(self):
        self.nutrition_ai = NutritionAI()
        self.measurement_service = MeasurementStandardizationService()
    
    def suggest_substitutions(
        self,
        recipe: Dict[str, Any],
        ingredient_to_replace: str,
        reason: str = "dietary_preference",
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Suggest AI-generated ingredient substitutions
        
        Args:
            recipe: Recipe dictionary containing ingredients
            ingredient_to_replace: Name of ingredient to replace
            reason: Reason for substitution (dietary_preference, allergy, availability, etc.)
            user_preferences: User preferences (allergies, dietary restrictions, etc.)
        
        Returns:
            List of substitution suggestions with nutritional information
        """
        try:
            # Find the ingredient in the recipe
            ingredient = self._find_ingredient_in_recipe(recipe, ingredient_to_replace)
            if not ingredient:
                return []
            
            # Get AI-generated substitution suggestions
            suggestions = self._generate_substitution_suggestions(
                ingredient,
                recipe,
                reason,
                user_preferences or {}
            )
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error suggesting ingredient substitutions: {e}")
            return []
    
    def _find_ingredient_in_recipe(self, recipe: Dict[str, Any], ingredient_name: str) -> Optional[Dict[str, Any]]:
        """Find ingredient in recipe by name"""
        ingredients = recipe.get('ingredients', []) or recipe.get('ingredients_list', [])
        
        ingredient_lower = ingredient_name.lower().strip()
        for ing in ingredients:
            if isinstance(ing, dict):
                name = str(ing.get('name', '')).lower()
                if ingredient_lower in name or name in ingredient_lower:
                    return ing
            elif isinstance(ing, str):
                if ingredient_lower in ing.lower():
                    return {'name': ing, 'quantity': 0, 'unit': 'g'}
        
        return None
    
    def _generate_substitution_suggestions(
        self,
        original_ingredient: Dict[str, Any],
        recipe: Dict[str, Any],
        reason: str,
        user_preferences: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate AI-powered substitution suggestions"""
        try:
            prompt = self._create_substitution_prompt(
                original_ingredient,
                recipe,
                reason,
                user_preferences
            )
            
            response = self.nutrition_ai._call_openai(prompt, temperature=0.7)
            substitutions = self._parse_substitution_response(response)
            
            # Validate and enrich substitutions
            validated_substitutions = []
            for sub in substitutions:
                validated = self._validate_substitution(
                    original_ingredient,
                    sub,
                    recipe,
                    user_preferences
                )
                if validated:
                    validated_substitutions.append(validated)
            
            return validated_substitutions[:5]  # Return top 5 suggestions
            
        except Exception as e:
            logger.error(f"Error generating substitution suggestions: {e}")
            return self._get_fallback_substitutions(original_ingredient, reason)
    
    def _create_substitution_prompt(
        self,
        original_ingredient: Dict[str, Any],
        recipe: Dict[str, Any],
        reason: str,
        user_preferences: Dict[str, Any]
    ) -> str:
        """Create AI prompt for ingredient substitution"""
        ingredient_name = original_ingredient.get('name', '')
        quantity = original_ingredient.get('quantity', 0)
        unit = original_ingredient.get('unit', 'g')
        recipe_name = recipe.get('title', recipe.get('meal_name', 'Unknown Recipe'))
        
        allergies = user_preferences.get('allergies', [])
        dietary_prefs = user_preferences.get('dietary_preferences', [])
        disliked = user_preferences.get('disliked_ingredients', [])
        
        prompt = f"""
        Suggest ingredient substitutions for a recipe ingredient.
        
        ORIGINAL INGREDIENT:
        - Name: {ingredient_name}
        - Quantity: {quantity} {unit}
        - Recipe: {recipe_name}
        - Reason for substitution: {reason}
        
        USER PREFERENCES:
        - Allergies: {', '.join(allergies) if allergies else 'None'}
        - Dietary preferences: {', '.join(dietary_prefs) if dietary_prefs else 'None'}
        - Disliked ingredients: {', '.join(disliked) if disliked else 'None'}
        
        REQUIREMENTS:
        1. Suggest 3-5 alternative ingredients that can replace "{ingredient_name}"
        2. Consider dietary restrictions, allergies, and user preferences
        3. Provide equivalent quantities (same measurement unit: {unit})
        4. Ensure nutritional compatibility (similar calories, protein, carbs, fats where possible)
        5. Maintain recipe functionality (similar texture, flavor profile where applicable)
        
        Respond with ONLY valid JSON in this format:
        {{
            "substitutions": [
                {{
                    "name": "substitute_ingredient_name",
                    "quantity": {quantity},
                    "unit": "{unit}",
                    "reason": "why this substitution works",
                    "nutrition_adjustment": {{
                        "calories_change": 0,
                        "protein_change": 0,
                        "carbs_change": 0,
                        "fats_change": 0
                    }},
                    "cooking_adjustment": "any changes needed in cooking method",
                    "flavor_impact": "how this affects the flavor"
                }}
            ]
        }}
        """
        return prompt
    
    def _parse_substitution_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse AI response into substitution suggestions"""
        try:
            import json
            # Extract JSON from response
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                response = response[json_start:json_end].strip()
            elif '```' in response:
                json_start = response.find('```') + 3
                json_end = response.find('```', json_start)
                response = response[json_start:json_end].strip()
            
            data = json.loads(response)
            return data.get('substitutions', [])
            
        except Exception as e:
            logger.error(f"Error parsing substitution response: {e}")
            return []
    
    def _validate_substitution(
        self,
        original: Dict[str, Any],
        substitution: Dict[str, Any],
        recipe: Dict[str, Any],
        user_preferences: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Validate substitution suggestion"""
        try:
            # Standardize measurement
            standardized = self.measurement_service.standardize_ingredient_measurement(
                substitution.get('name', ''),
                float(substitution.get('quantity', 0)),
                substitution.get('unit', 'g')
            )
            
            return {
                'name': substitution.get('name', ''),
                'original_name': original.get('name', ''),
                'quantity': standardized['standardized_quantity'],
                'unit': standardized['standardized_unit'],
                'original_quantity': original.get('quantity', 0),
                'original_unit': original.get('unit', 'g'),
                'reason': substitution.get('reason', ''),
                'nutrition_adjustment': substitution.get('nutrition_adjustment', {}),
                'cooking_adjustment': substitution.get('cooking_adjustment', ''),
                'flavor_impact': substitution.get('flavor_impact', ''),
                'measurement_type': standardized.get('measurement_type', 'weight')
            }
            
        except Exception as e:
            logger.error(f"Error validating substitution: {e}")
            return None
    
    def _get_fallback_substitutions(self, ingredient: Dict[str, Any], reason: str) -> List[Dict[str, Any]]:
        """Get fallback substitution suggestions when AI fails"""
        name = str(ingredient.get('name', '')).lower()
        quantity = float(ingredient.get('quantity', 0))
        unit = ingredient.get('unit', 'g')
        
        fallback_map = {
            'milk': ['almond milk', 'oat milk', 'coconut milk', 'soy milk'],
            'butter': ['olive oil', 'coconut oil', 'avocado', 'margarine'],
            'flour': ['almond flour', 'rice flour', 'coconut flour', 'quinoa flour'],
            'sugar': ['honey', 'maple syrup', 'stevia', 'erythritol'],
            'egg': ['flax egg', 'chia egg', 'applesauce', 'banana'],
            'cheese': ['nutritional yeast', 'cashew cream', 'tofu', 'almond cheese'],
            'chicken': ['tofu', 'tempeh', 'mushrooms', 'beans'],
            'beef': ['lentils', 'mushrooms', 'beans', 'tofu']
        }
        
        suggestions = []
        for key, alternatives in fallback_map.items():
            if key in name:
                for alt in alternatives[:3]:
                    suggestions.append({
                        'name': alt,
                        'original_name': ingredient.get('name', ''),
                        'quantity': quantity,
                        'unit': unit,
                        'original_quantity': quantity,
                        'original_unit': unit,
                        'reason': f'Common {reason} substitution',
                        'nutrition_adjustment': {},
                        'cooking_adjustment': 'May require slight cooking adjustments',
                        'flavor_impact': 'Similar flavor profile'
                    })
                break
        
        return suggestions
    
    def apply_substitution(
        self,
        recipe: Dict[str, Any],
        original_ingredient_name: str,
        substitution: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply a substitution to a recipe
        
        Args:
            recipe: Recipe dictionary
            original_ingredient_name: Name of ingredient to replace
            substitution: Substitution dictionary
        
        Returns:
            Updated recipe with substitution applied
        """
        try:
            updated_recipe = recipe.copy()
            ingredients = updated_recipe.get('ingredients', [])
            
            # Find and replace ingredient
            ingredient_lower = original_ingredient_name.lower().strip()
            for i, ing in enumerate(ingredients):
                if isinstance(ing, dict):
                    name = str(ing.get('name', '')).lower()
                    if ingredient_lower in name or name in ingredient_lower:
                        # Replace ingredient
                        ingredients[i] = {
                            'name': substitution['name'],
                            'quantity': substitution['quantity'],
                            'unit': substitution['unit'],
                            'original_name': ing.get('name', ''),
                            'substitution_note': substitution.get('reason', '')
                        }
                        break
                elif isinstance(ing, str):
                    if ingredient_lower in ing.lower():
                        ingredients[i] = {
                            'name': substitution['name'],
                            'quantity': substitution['quantity'],
                            'unit': substitution['unit']
                        }
                        break
            
            updated_recipe['ingredients'] = ingredients
            
            # Recalculate nutrition if possible
            # This would typically be done by calling a nutrition recalculation service
            # For now, we'll add a flag indicating nutrition needs recalculation
            updated_recipe['nutrition_needs_recalculation'] = True
            
            return updated_recipe
            
        except Exception as e:
            logger.error(f"Error applying substitution: {e}")
            return recipe
