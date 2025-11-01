"""
Service for generating and managing alternative meal options
"""

from sqlalchemy.orm import Session
from models.nutrition import MealPlan, MealPlanMeal
from models.recipe import Recipe
from ai.nutrition_ai import NutritionAI
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class MealAlternativesService:
    """Service for generating alternative meal options"""
    
    def __init__(self):
        self.nutrition_ai = NutritionAI()
    
    def generate_meal_alternatives(self, db: Session, meal_plan_id: str, meal_type: str, 
                                 user_preferences: Dict[str, Any], count: int = 3) -> List[Dict[str, Any]]:
        """
        Generate alternative meal options for a specific meal type
        """
        try:
            # Get the original meal plan to understand the context
            meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()
            if not meal_plan:
                raise ValueError(f"Meal plan {meal_plan_id} not found")
            
            # Get the original meal to understand requirements
            original_meal = db.query(MealPlanMeal).filter(
                MealPlanMeal.meal_plan_id == meal_plan_id,
                MealPlanMeal.meal_type == meal_type
            ).first()
            
            if not original_meal:
                raise ValueError(f"Meal of type {meal_type} not found in meal plan")
            
            # Extract requirements from original meal
            target_calories = self._extract_calories_from_meal(original_meal)
            target_cuisine = original_meal.cuisine or "International"
            
            # Generate alternatives using AI
            alternatives = []
            for i in range(count):
                try:
                    alternative = self._generate_single_alternative(
                        meal_type, target_calories, target_cuisine, user_preferences, i, db
                    )
                    alternatives.append(alternative)
                except Exception as e:
                    logger.warning(f"Failed to generate alternative {i+1}: {str(e)}")
                    continue
            
            # If AI fails, provide fallback alternatives
            if not alternatives:
                alternatives = self._generate_fallback_alternatives(
                    meal_type, target_calories, user_preferences
                )
            
            return alternatives
            
        except Exception as e:
            logger.error(f"Error generating meal alternatives: {str(e)}")
            return self._generate_fallback_alternatives(meal_type, 500, user_preferences)
    
    def _generate_single_alternative(self, meal_type: str, target_calories: int, 
                                   target_cuisine: str, user_preferences: Dict[str, Any], 
                                   variation_index: int, db: Session = None) -> Dict[str, Any]:
        """Generate a single alternative meal option"""
        
        # Create variation in cuisine and style
        cuisine_variations = {
            0: target_cuisine,
            1: self._get_alternative_cuisine(target_cuisine),
            2: self._get_alternative_cuisine(target_cuisine, exclude=[target_cuisine])
        }
        
        selected_cuisine = cuisine_variations.get(variation_index, target_cuisine)
        
        # Create a focused prompt for this specific alternative
        prompt = f"""
        Generate a single {meal_type} alternative with these exact requirements:
        
        MEAL REQUIREMENTS:
        - Meal Type: {meal_type}
        - Target Calories: {target_calories} (±50)
        - Cuisine: {selected_cuisine}
        - Dietary Preferences: {user_preferences.get('dietary_preferences', [])}
        - Allergies: {user_preferences.get('allergies', [])}
        - Disliked Ingredients: {user_preferences.get('disliked_ingredients', [])}
        
        VARIATION REQUIREMENTS:
        - This is alternative #{variation_index + 1} - make it different from typical {meal_type} options
        - Use {selected_cuisine} cuisine style
        - Include unique ingredients or cooking methods
        - Ensure it's appealing and nutritious
        
        Respond with ONLY valid JSON in this exact format:
        {{
            "meal_type": "{meal_type}",
            "meal_name": "descriptive_name",
            "recipe": {{
                "title": "recipe_title",
                "cuisine": "{selected_cuisine}",
                "prep_time": number,
                "cook_time": number,
                "servings": 1,
                "difficulty": "easy|medium|hard",
                "summary": "brief_description",
                "ingredients": [{{"name": "string", "quantity": number, "unit": "string"}}],
                "instructions": [{{"step": number, "description": "string"}}],
                "dietary_tags": ["string"],
                "nutrition": {{"calories": number, "protein": number, "carbs": number, "fats": number}}
            }}
        }}
        """
        
        if self.nutrition_ai.openai_client:
            response = self.nutrition_ai._call_openai(prompt, 0.8)  # Higher temperature for variety
            alternative = self.nutrition_ai._parse_json_response(response, "meal_alternative")
            
            # ROOT CAUSE FIX: Calculate actual nutrition from ingredients (like meal generation)
            # Don't trust AI's placeholder nutrition values - calculate from ingredients
            if alternative and alternative.get('recipe', {}).get('ingredients'):
                try:
                    calculated_nutrition = self.nutrition_ai._calculate_recipe_nutrition(
                        alternative['recipe']['ingredients'], db
                    )
                    if calculated_nutrition and calculated_nutrition.get('calories', 0) > 0:
                        # Use calculated nutrition (more accurate than AI placeholder values)
                        # _calculate_recipe_nutrition returns flat dict: {calories, protein, carbs, fats}
                        alternative['recipe']['nutrition'] = {
                            "calories": calculated_nutrition.get('calories', target_calories),
                            "protein": calculated_nutrition.get('protein', int(target_calories * 0.25 / 4)),
                            "carbs": calculated_nutrition.get('carbs', int(target_calories * 0.45 / 4)),
                            "fats": calculated_nutrition.get('fats', int(target_calories * 0.30 / 9))
                        }
                        alternative['calories'] = calculated_nutrition.get('calories', target_calories)
                        alternative['per_serving_calories'] = calculated_nutrition.get('calories', target_calories)
                        logger.info(f"✅ Calculated nutrition for alternative: {calculated_nutrition.get('calories', 0)} cal")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to calculate nutrition from ingredients: {e}")
            
            return alternative
        else:
            return self._generate_fallback_alternative(meal_type, target_calories, selected_cuisine)
    
    def _get_alternative_cuisine(self, original_cuisine: str, exclude: List[str] = None) -> str:
        """Get an alternative cuisine that's different from the original"""
        cuisine_options = [
            "Italian", "Mexican", "Asian", "Mediterranean", "Indian", 
            "Thai", "French", "American", "Japanese", "Chinese", "Middle Eastern"
        ]
        
        if exclude is None:
            exclude = []
        
        # Remove original and excluded cuisines
        available = [c for c in cuisine_options if c.lower() != original_cuisine.lower() and c not in exclude]
        
        if available:
            import random
            return random.choice(available)
        else:
            return "International"
    
    def _extract_calories_from_meal(self, meal: MealPlanMeal) -> int:
        """Extract target calories from meal data"""
        try:
            if meal.recipe_details and 'nutrition' in meal.recipe_details:
                cal = meal.recipe_details['nutrition'].get('calories')
                if cal and cal > 0:
                    return int(cal)
            # Fallback: use meal.calories if available
            if meal.calories and meal.calories > 0:
                return int(meal.calories)
            # Final fallback: estimate from meal type
            default_cal_by_type = {'breakfast': 400, 'lunch': 500, 'dinner': 600, 'snack': 200}
            return default_cal_by_type.get(meal.meal_type, 500)
        except:
            # On error, estimate from meal type
            default_cal_by_type = {'breakfast': 400, 'lunch': 500, 'dinner': 600, 'snack': 200}
            return default_cal_by_type.get(meal.meal_type, 500)
    
    def _generate_fallback_alternatives(self, meal_type: str, target_calories: int, 
                                      user_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate fallback alternatives when AI is not available"""
        alternatives = []
        
        # Different fallback options for each meal type
        fallback_options = {
            "breakfast": [
                {"name": "Protein Pancakes", "cuisine": "American", "calories": target_calories},
                {"name": "Mediterranean Toast", "cuisine": "Mediterranean", "calories": target_calories},
                {"name": "Asian Rice Bowl", "cuisine": "Asian", "calories": target_calories}
            ],
            "lunch": [
                {"name": "Grilled Chicken Wrap", "cuisine": "American", "calories": target_calories},
                {"name": "Mediterranean Salad", "cuisine": "Mediterranean", "calories": target_calories},
                {"name": "Thai Curry Bowl", "cuisine": "Thai", "calories": target_calories}
            ],
            "dinner": [
                {"name": "Baked Salmon", "cuisine": "Mediterranean", "calories": target_calories},
                {"name": "Italian Pasta", "cuisine": "Italian", "calories": target_calories},
                {"name": "Indian Curry", "cuisine": "Indian", "calories": target_calories}
            ],
            "snack": [
                {"name": "Greek Yogurt Parfait", "cuisine": "Mediterranean", "calories": 200},
                {"name": "Mixed Nuts", "cuisine": "International", "calories": 200},
                {"name": "Fruit Smoothie", "cuisine": "International", "calories": 200}
            ]
        }
        
        options = fallback_options.get(meal_type, fallback_options["lunch"])
        
        for option in options[:3]:  # Limit to 3 alternatives
            alternative = self._generate_fallback_alternative(
                meal_type, option["calories"], option["cuisine"]
            )
            alternative["meal_name"] = option["name"]
            alternative["recipe"]["title"] = option["name"]
            alternative["recipe"]["cuisine"] = option["cuisine"]
            alternatives.append(alternative)
        
        return alternatives
    
    def _generate_fallback_alternative(self, meal_type: str, target_calories: int, 
                                     cuisine: str) -> Dict[str, Any]:
        """Generate a single fallback alternative"""
        return {
            "meal_type": meal_type,
            "meal_name": f"{cuisine} {meal_type.title()}",
            "recipe": {
                "title": f"{cuisine} {meal_type.title()}",
                "cuisine": cuisine,
                "prep_time": 15,
                "cook_time": 20,
                "servings": 1,
                "difficulty": "easy",
                "summary": f"A delicious {cuisine.lower()} {meal_type} option",
                "ingredients": [
                    {"name": "main_ingredient", "quantity": 150, "unit": "g"},
                    {"name": "seasoning", "quantity": 5, "unit": "g"}
                ],
                "instructions": [
                    {"step": 1, "description": "Prepare ingredients"},
                    {"step": 2, "description": "Cook according to {cuisine.lower()} style"},
                    {"step": 3, "description": "Serve hot"}
                ],
                "dietary_tags": ["balanced"],
                "nutrition": {
                    "calories": target_calories,
                    "protein": int(target_calories * 0.25 / 4),  # 25% protein
                    "carbs": int(target_calories * 0.45 / 4),   # 45% carbs
                    "fats": int(target_calories * 0.30 / 9)     # 30% fats
                }
            }
        }
    
    def get_meal_alternatives_from_database(self, db: Session, meal_type: str, 
                                          user_preferences: Dict[str, Any], 
                                          limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get alternative meal options from existing recipes in the database
        """
        try:
            # Query recipes that match the meal type and dietary preferences
            query = db.query(Recipe).filter(Recipe.meal_type == meal_type)
            
            # Filter by dietary preferences
            dietary_prefs = user_preferences.get('dietary_preferences', [])
            if dietary_prefs:
                for pref in dietary_prefs:
                    query = query.filter(Recipe.dietary_tags.contains(pref))
            
            # Filter out allergies - recipes should NOT contain allergens
            allergies = user_preferences.get('allergies', [])
            if allergies:
                for allergy in allergies:
                    # Check for contains-{allergy} tag (e.g., contains-fish, contains-peanuts)
                    allergen_tag = f"contains-{allergy}"
                    query = query.filter(~Recipe.dietary_tags.contains([allergen_tag]))
            
            # Get random selection
            recipes = query.order_by(Recipe.id).limit(limit).all()
            
            alternatives = []
            for recipe in recipes:
                alternative = {
                    "meal_type": meal_type,
                    "meal_name": recipe.title,
                    "recipe": {
                        "title": recipe.title,
                        "cuisine": recipe.cuisine or "International",
                        "prep_time": recipe.prep_time or 15,
                        "cook_time": recipe.cook_time or 20,
                        "servings": recipe.servings or 1,
                        "difficulty": recipe.difficulty_level or "medium",
                        "summary": recipe.summary or f"A delicious {recipe.title}",
                        "ingredients": [
                            {"name": ing.ingredient.name, "quantity": ing.quantity, "unit": ing.unit}
                            for ing in recipe.ingredients
                        ],
                        "instructions": [
                            {"step": inst.step_number, "description": inst.description}
                            for inst in recipe.instructions
                        ],
                        "dietary_tags": recipe.dietary_tags or [],
                        "nutrition": {
                            "calories": recipe.per_serving_calories or recipe.calories or 400,
                            "protein": recipe.per_serving_protein or recipe.protein or 20,
                            "carbs": recipe.per_serving_carbs or recipe.carbs or 40,
                            "fats": recipe.per_serving_fat or recipe.per_serving_fats or recipe.fats or 15
                        },
                        "per_serving_calories": recipe.per_serving_calories or recipe.calories or 400,
                        "per_serving_protein": recipe.per_serving_protein or recipe.protein or 20,
                        "per_serving_carbs": recipe.per_serving_carbs or recipe.carbs or 40,
                        "per_serving_fats": recipe.per_serving_fat or recipe.per_serving_fats or recipe.fats or 15
                    }
                }
                alternatives.append(alternative)
            
            return alternatives
            
        except Exception as e:
            logger.error(f"Error getting alternatives from database: {str(e)}")
            return []








