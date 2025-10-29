"""
Service for regenerating individual meals or meal plans while preserving preferences
"""

from sqlalchemy.orm import Session
from models.nutrition import MealPlan, MealPlanMeal
from ai.nutrition_ai import NutritionAI
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class MealRegenerationService:
    """Service for regenerating meals while preserving preferences and other meals"""
    
    def __init__(self):
        self.nutrition_ai = NutritionAI()
    
    def regenerate_individual_meal(self, db: Session, meal_plan_id: str, meal_id: str, 
                                 user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Regenerate a single meal while preserving other meals and user preferences
        """
        try:
            # Get the existing meal
            existing_meal = db.query(MealPlanMeal).filter(
                MealPlanMeal.id == meal_id,
                MealPlanMeal.meal_plan_id == meal_plan_id
            ).first()
            
            if not existing_meal:
                raise ValueError(f"Meal {meal_id} not found in meal plan {meal_plan_id}")
            
            # Get the meal plan to understand context
            meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()
            if not meal_plan:
                raise ValueError(f"Meal plan {meal_plan_id} not found")
            
            # Extract requirements from existing meal
            target_calories = existing_meal.calories or 500
            target_meal_type = existing_meal.meal_type
            target_cuisine = existing_meal.cuisine or "International"
            
            # Generate new meal with same requirements but different content
            new_meal_data = self._generate_single_meal(
                meal_type=target_meal_type,
                target_calories=target_calories,
                target_cuisine=target_cuisine,
                user_preferences=user_preferences,
                exclude_existing=existing_meal.meal_name
            )
            
            # Update the existing meal with new data
            existing_meal.meal_name = new_meal_data.get('meal_name', existing_meal.meal_name)
            existing_meal.calories = new_meal_data.get('recipe', {}).get('nutrition', {}).get('calories', target_calories)
            existing_meal.protein = new_meal_data.get('recipe', {}).get('nutrition', {}).get('protein', 0)
            existing_meal.carbs = new_meal_data.get('recipe', {}).get('nutrition', {}).get('carbs', 0)
            existing_meal.fats = new_meal_data.get('recipe', {}).get('nutrition', {}).get('fats', 0)
            existing_meal.cuisine = new_meal_data.get('recipe', {}).get('cuisine', target_cuisine)
            existing_meal.recipe_details = new_meal_data.get('recipe', {})
            
            db.commit()
            db.refresh(existing_meal)
            
            return {
                "message": "Meal regenerated successfully",
                "meal_id": existing_meal.id,
                "new_meal": {
                    "id": existing_meal.id,
                    "meal_name": existing_meal.meal_name,
                    "meal_type": existing_meal.meal_type,
                    "calories": existing_meal.calories,
                    "protein": existing_meal.protein,
                    "carbs": existing_meal.carbs,
                    "fats": existing_meal.fats,
                    "cuisine": existing_meal.cuisine,
                    "recipe_details": existing_meal.recipe_details
                }
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error regenerating individual meal: {str(e)}")
            raise
    
    def regenerate_meal_type(self, db: Session, meal_plan_id: str, meal_type: str, 
                           user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Regenerate all meals of a specific type (e.g., all breakfasts) while preserving others
        """
        try:
            # Get all meals of the specified type
            meals_to_regenerate = db.query(MealPlanMeal).filter(
                MealPlanMeal.meal_plan_id == meal_plan_id,
                MealPlanMeal.meal_type == meal_type
            ).all()
            
            if not meals_to_regenerate:
                return {"message": f"No {meal_type} meals found to regenerate"}
            
            regenerated_meals = []
            
            for meal in meals_to_regenerate:
                # Generate new meal data
                new_meal_data = self._generate_single_meal(
                    meal_type=meal_type,
                    target_calories=meal.calories or 500,
                    target_cuisine=meal.cuisine or "International",
                    user_preferences=user_preferences,
                    exclude_existing=meal.meal_name
                )
                
                # Update the meal
                meal.meal_name = new_meal_data.get('meal_name', meal.meal_name)
                meal.calories = new_meal_data.get('recipe', {}).get('nutrition', {}).get('calories', meal.calories)
                meal.protein = new_meal_data.get('recipe', {}).get('nutrition', {}).get('protein', meal.protein)
                meal.carbs = new_meal_data.get('recipe', {}).get('nutrition', {}).get('carbs', meal.carbs)
                meal.fats = new_meal_data.get('recipe', {}).get('nutrition', {}).get('fats', meal.fats)
                meal.cuisine = new_meal_data.get('recipe', {}).get('cuisine', meal.cuisine)
                meal.recipe_details = new_meal_data.get('recipe', {})
                
                regenerated_meals.append({
                    "id": meal.id,
                    "meal_name": meal.meal_name,
                    "meal_type": meal.meal_type,
                    "calories": meal.calories,
                    "protein": meal.protein,
                    "carbs": meal.carbs,
                    "fats": meal.fats,
                    "cuisine": meal.cuisine
                })
            
            db.commit()
            
            return {
                "message": f"Regenerated {len(regenerated_meals)} {meal_type} meals",
                "regenerated_meals": regenerated_meals
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error regenerating meal type: {str(e)}")
            raise
    
    def regenerate_entire_meal_plan(self, db: Session, meal_plan_id: str, 
                                  user_preferences: Dict[str, Any], 
                                  preserve_structure: bool = True) -> Dict[str, Any]:
        """
        Regenerate entire meal plan while preserving user preferences and optionally meal structure
        """
        try:
            # Get the existing meal plan
            meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()
            if not meal_plan:
                raise ValueError(f"Meal plan {meal_plan_id} not found")
            
            # Get existing meals
            existing_meals = db.query(MealPlanMeal).filter(
                MealPlanMeal.meal_plan_id == meal_plan_id
            ).all()
            
            if preserve_structure:
                # Regenerate each meal individually while preserving meal types and timing
                regenerated_meals = []
                
                for meal in existing_meals:
                    new_meal_data = self._generate_single_meal(
                        meal_type=meal.meal_type,
                        target_calories=meal.calories or 500,
                        target_cuisine=meal.cuisine or "International",
                        user_preferences=user_preferences,
                        exclude_existing=meal.meal_name
                    )
                    
                    # Update the meal
                    meal.meal_name = new_meal_data.get('meal_name', meal.meal_name)
                    meal.calories = new_meal_data.get('recipe', {}).get('nutrition', {}).get('calories', meal.calories)
                    meal.protein = new_meal_data.get('recipe', {}).get('nutrition', {}).get('protein', meal.protein)
                    meal.carbs = new_meal_data.get('recipe', {}).get('nutrition', {}).get('carbs', meal.carbs)
                    meal.fats = new_meal_data.get('recipe', {}).get('nutrition', {}).get('fats', meal.fats)
                    meal.cuisine = new_meal_data.get('recipe', {}).get('cuisine', meal.cuisine)
                    meal.recipe_details = new_meal_data.get('recipe', {})
                    
                    regenerated_meals.append({
                        "id": meal.id,
                        "meal_name": meal.meal_name,
                        "meal_type": meal.meal_type,
                        "calories": meal.calories,
                        "protein": meal.protein,
                        "carbs": meal.carbs,
                        "fats": meal.fats,
                        "cuisine": meal.cuisine
                    })
                
                db.commit()
                
                return {
                    "message": f"Regenerated {len(regenerated_meals)} meals while preserving structure",
                    "regenerated_meals": regenerated_meals
                }
            else:
                # Complete regeneration - delete existing meals and generate new ones
                # This would require more complex logic to maintain meal plan integrity
                # For now, we'll use the existing meal plan generation
                return {"message": "Complete regeneration not yet implemented"}
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error regenerating entire meal plan: {str(e)}")
            raise
    
    def _generate_single_meal(self, meal_type: str, target_calories: int, 
                            target_cuisine: str, user_preferences: Dict[str, Any],
                            exclude_existing: Optional[str] = None) -> Dict[str, Any]:
        """Generate a single meal with specific requirements"""
        
        # Create a focused prompt for single meal generation
        prompt = f"""
        Generate a single {meal_type} meal with these exact requirements:
        
        MEAL REQUIREMENTS:
        - Meal Type: {meal_type}
        - Target Calories: {target_calories} (±50)
        - Cuisine: {target_cuisine}
        - Dietary Preferences: {user_preferences.get('dietary_preferences', [])}
        - Allergies: {user_preferences.get('allergies', [])}
        - Disliked Ingredients: {user_preferences.get('disliked_ingredients', [])}
        - Cuisine Preferences: {user_preferences.get('cuisine_preferences', [])}
        
        VARIETY REQUIREMENTS:
        - Make this meal different and appealing
        - Use {target_cuisine} cuisine style
        - Include unique ingredients or cooking methods
        - Ensure it's nutritious and balanced
        """
        
        if exclude_existing:
            prompt += f"\n- AVOID creating anything similar to: {exclude_existing}"
        
        prompt += """
        
        Respond with ONLY valid JSON in this exact format:
        {
            "meal_type": "breakfast|lunch|dinner|snack",
            "meal_name": "descriptive_name",
            "recipe": {
                "title": "recipe_title",
                "cuisine": "cuisine_name",
                "prep_time": number,
                "cook_time": number,
                "servings": 1,
                "difficulty": "easy|medium|hard",
                "summary": "brief_description",
                "ingredients": [{"name": "string", "quantity": number, "unit": "string"}],
                "instructions": [{"step": number, "description": "string"}],
                "dietary_tags": ["string"],
                "nutrition": {"calories": number, "protein": number, "carbs": number, "fats": number}
            }
        }
        """
        
        if self.nutrition_ai.openai_client:
            try:
                response = self.nutrition_ai._call_openai(prompt, 0.8)  # Higher temperature for variety
                return self.nutrition_ai._parse_json_response(response, "meal")
            except Exception as e:
                logger.warning(f"AI generation failed, using fallback: {str(e)}")
                return self._generate_fallback_meal(meal_type, target_calories, target_cuisine)
        else:
            return self._generate_fallback_meal(meal_type, target_calories, target_cuisine)
    
    def _generate_fallback_meal(self, meal_type: str, target_calories: int, 
                              target_cuisine: str) -> Dict[str, Any]:
        """Generate a fallback meal when AI is not available"""
        
        # Fallback meal templates
        fallback_templates = {
            "breakfast": [
                {"name": f"{target_cuisine} Omelet", "calories": target_calories},
                {"name": f"{target_cuisine} Pancakes", "calories": target_calories},
                {"name": f"{target_cuisine} Breakfast Bowl", "calories": target_calories}
            ],
            "lunch": [
                {"name": f"{target_cuisine} Salad", "calories": target_calories},
                {"name": f"{target_cuisine} Wrap", "calories": target_calories},
                {"name": f"{target_cuisine} Soup", "calories": target_calories}
            ],
            "dinner": [
                {"name": f"{target_cuisine} Pasta", "calories": target_calories},
                {"name": f"{target_cuisine} Stir-fry", "calories": target_calories},
                {"name": f"{target_cuisine} Curry", "calories": target_calories}
            ],
            "snack": [
                {"name": f"{target_cuisine} Smoothie", "calories": 200},
                {"name": f"{target_cuisine} Trail Mix", "calories": 200},
                {"name": f"{target_cuisine} Yogurt Bowl", "calories": 200}
            ]
        }
        
        import random
        templates = fallback_templates.get(meal_type, fallback_templates["lunch"])
        selected_template = random.choice(templates)
        
        return {
            "meal_type": meal_type,
            "meal_name": selected_template["name"],
            "recipe": {
                "title": selected_template["name"],
                "cuisine": target_cuisine,
                "prep_time": 15,
                "cook_time": 20,
                "servings": 1,
                "difficulty": "easy",
                "summary": f"A delicious {target_cuisine.lower()} {meal_type} option",
                "ingredients": [
                    {"name": "main_ingredient", "quantity": 150, "unit": "g"},
                    {"name": "seasoning", "quantity": 5, "unit": "g"}
                ],
                "instructions": [
                    {"step": 1, "description": "Prepare ingredients"},
                    {"step": 2, "description": f"Cook according to {target_cuisine.lower()} style"},
                    {"step": 3, "description": "Serve hot"}
                ],
                "dietary_tags": ["balanced"],
                "nutrition": {
                    "calories": selected_template["calories"],
                    "protein": int(selected_template["calories"] * 0.25 / 4),
                    "carbs": int(selected_template["calories"] * 0.45 / 4),
                    "fats": int(selected_template["calories"] * 0.30 / 9)
                }
            }
        }



