"""
Service for adjusting portion sizes and recalculating ingredient quantities
"""

from sqlalchemy.orm import Session
from models.nutrition import MealPlan, MealPlanMeal
from models.recipe import Recipe, RecipeIngredient
from typing import Dict, List, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)

class PortionAdjustmentService:
    """Service for adjusting portion sizes and recalculating ingredient quantities"""
    
    def __init__(self):
        from services.measurement_standardization_service import MeasurementStandardizationService
        self.measurement_service = MeasurementStandardizationService()
    
    def adjust_meal_portion(self, db: Session, meal_id: str, new_servings: float) -> Dict[str, Any]:
        """
        Adjust the portion size of a meal and recalculate all ingredient quantities
        """
        try:
            # Get the meal
            meal = db.query(MealPlanMeal).filter(MealPlanMeal.id == meal_id).first()
            
            if not meal:
                raise ValueError(f"Meal {meal_id} not found")
            
            if new_servings <= 0:
                raise ValueError("Servings must be greater than 0")
            
            # Get original servings from recipe details
            original_servings = 1.0  # Default
            if meal.recipe_details and isinstance(meal.recipe_details, dict):
                original_servings = meal.recipe_details.get('servings', 1.0)
            
            # Calculate multiplier
            multiplier = new_servings / original_servings
            
            # Adjust ingredients if recipe details exist
            # Automatically recalculate quantities using standardized measurements
            adjusted_ingredients = []
            if meal.recipe_details and isinstance(meal.recipe_details, dict):
                ingredients = meal.recipe_details.get('ingredients', [])
                
                logger.info(f"📊 Adjusting {len(ingredients)} ingredients by {multiplier:.2f}x (servings: {original_servings} → {new_servings})")
                
                for ingredient in ingredients:
                    if not isinstance(ingredient, dict):
                        # Skip invalid ingredients
                        adjusted_ingredients.append(ingredient)
                        continue
                    
                    # Get original quantity and unit
                    original_quantity = float(ingredient.get('quantity', 0))
                    original_unit = ingredient.get('unit', 'g')
                    ingredient_name = ingredient.get('name', '')
                    
                    if original_quantity <= 0:
                        # Skip ingredients with invalid quantities
                        adjusted_ingredients.append(ingredient)
                        continue
                    
                    # Calculate adjusted quantity
                    adjusted_quantity = original_quantity * multiplier
                    
                    # Standardize measurement (ensures grams/ml/piece)
                    try:
                        standardized = self.measurement_service.standardize_ingredient_measurement(
                            ingredient_name,
                            adjusted_quantity,
                            original_unit
                        )
                        
                        # Create adjusted ingredient with updated quantities
                        # Preserve all original fields but update quantity and unit
                        adjusted_ingredient = {
                            **ingredient,  # Preserve all original fields (name, notes, etc.)
                            'quantity': round(standardized['standardized_quantity'], 2),
                            'unit': standardized['standardized_unit'],  # Standardized unit
                        }
                        
                        logger.debug(f"  {ingredient_name}: {original_quantity}{original_unit} → {adjusted_ingredient['quantity']}{adjusted_ingredient['unit']} ({multiplier:.2f}x)")
                        
                    except Exception as e:
                        logger.warning(f"Failed to standardize {ingredient_name}: {e}. Using proportional scaling.")
                        # Fallback: simple proportional scaling
                        adjusted_ingredient = {
                            **ingredient,
                            'quantity': round(adjusted_quantity, 2),
                            'unit': original_unit
                        }
                    
                    adjusted_ingredients.append(adjusted_ingredient)
                
                logger.info(f"✅ Adjusted {len(adjusted_ingredients)} ingredients")
            
            # CRITICAL: Recalculate nutrition from scaled ingredients for accuracy
            # This ensures nutrition matches actual ingredient quantities (like in meal generation)
            from services.hybrid_meal_generator import HybridMealGenerator
            hybrid_gen = HybridMealGenerator()
            
            # Prepare ingredients for nutrition calculation (extract quantity, unit, name)
            # Only if we have adjusted ingredients (recipe details exist)
            ingredients_for_calc = []
            if adjusted_ingredients:
                for ing in adjusted_ingredients:
                    if isinstance(ing, dict) and 'name' in ing:
                        ingredients_for_calc.append({
                            'name': ing.get('name', ''),
                            'quantity': ing.get('quantity', 0),
                            'unit': ing.get('unit', 'g')
                        })
            
            # Calculate nutrition from scaled ingredients (more accurate than proportional scaling)
            # Only if we have ingredient data
            recalculated_nutrition = None
            if ingredients_for_calc and len(ingredients_for_calc) > 0:
                try:
                    logger.info(f"🔬 Recalculating nutrition from {len(ingredients_for_calc)} scaled ingredients...")
                    recalculated_nutrition = hybrid_gen.nutrition_ai._calculate_recipe_nutrition(
                        ingredients_for_calc, db
                    )
                    if recalculated_nutrition and recalculated_nutrition.get('calories', 0) > 0:
                        logger.info(f"✅ Nutrition recalculated: {recalculated_nutrition.get('calories', 0)} cal")
                    else:
                        logger.warning(f"⚠️ Nutrition recalculation returned 0 calories")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to recalculate nutrition from ingredients: {e}")
            
            # Use recalculated values if available, otherwise fall back to proportional scaling
            if recalculated_nutrition and recalculated_nutrition.get('calories', 0) > 0:
                adjusted_nutrition = {
                    'calories': int(recalculated_nutrition.get('calories', 0)),
                    'protein': int(recalculated_nutrition.get('protein', 0)),
                    'carbs': int(recalculated_nutrition.get('carbs', 0)),
                    'fats': int(recalculated_nutrition.get('fats', 0)),
                    'per_serving_calories': int(recalculated_nutrition.get('calories', 0)),
                    'per_serving_protein': int(recalculated_nutrition.get('protein', 0)),
                    'per_serving_carbs': int(recalculated_nutrition.get('carbs', 0)),
                    'per_serving_fats': int(recalculated_nutrition.get('fats', 0))
                }
                logger.info(f"✅ Recalculated nutrition from scaled ingredients: {adjusted_nutrition['calories']} cal")
            else:
                # Fallback: proportional scaling if recalculation fails
                nutrition_multiplier = multiplier
                adjusted_nutrition = {
                    'calories': int(round((meal.calories or 0) * nutrition_multiplier)),
                    'protein': int(round((meal.protein or 0) * nutrition_multiplier)),
                    'carbs': int(round((meal.carbs or 0) * nutrition_multiplier)),
                    'fats': int(round((meal.fats or 0) * nutrition_multiplier)),
                    'per_serving_calories': int(round((meal.calories or 0) * nutrition_multiplier)),
                    'per_serving_protein': int(round((meal.protein or 0) * nutrition_multiplier)),
                    'per_serving_carbs': int(round((meal.carbs or 0) * nutrition_multiplier)),
                    'per_serving_fats': int(round((meal.fats or 0) * nutrition_multiplier))
                }
                logger.warning(f"⚠️ Using proportional scaling (recalculation failed): {adjusted_nutrition['calories']} cal")
            
            # Update the meal in the database
            meal.calories = adjusted_nutrition['calories']
            meal.protein = adjusted_nutrition['protein']
            meal.carbs = adjusted_nutrition['carbs']
            meal.fats = adjusted_nutrition['fats']
            
            # Update recipe details with adjusted ingredients and nutrition
            if meal.recipe_details and isinstance(meal.recipe_details, dict):
                updated_recipe_details = meal.recipe_details.copy()
                updated_recipe_details['servings'] = new_servings
                updated_recipe_details['ingredients'] = adjusted_ingredients
                
                # Update nutrition in recipe_details
                if 'nutrition' not in updated_recipe_details:
                    updated_recipe_details['nutrition'] = {}
                updated_recipe_details['nutrition'].update(adjusted_nutrition)
                
                meal.recipe_details = updated_recipe_details
            
            db.commit()
            db.refresh(meal)
            
            logger.info(f"✅ Adjusted meal {meal_id} from {original_servings} to {new_servings} servings")
            logger.info(f"   Calories: {(meal.calories or 0) / multiplier:.1f} → {meal.calories} cal ({multiplier:.2f}x)")
            logger.info(f"   Ingredients: {len(adjusted_ingredients)} scaled")
            
            return {
                "message": "Meal portion adjusted successfully",
                "meal_id": meal.id,
                "meal_name": meal.meal_name,
                "original_servings": original_servings,
                "new_servings": new_servings,
                "multiplier": round(multiplier, 2),
                "adjusted_ingredients": adjusted_ingredients,  # All ingredients with updated quantities
                "adjusted_nutrition": adjusted_nutrition,
                "recipe_details": meal.recipe_details,  # Include full recipe_details with adjusted ingredients
                "updated_meal": {
                    "id": meal.id,
                    "meal_name": meal.meal_name,
                    "calories": meal.calories,
                    "protein": meal.protein,
                    "carbs": meal.carbs,
                    "fats": meal.fats,
                    "servings": new_servings,
                    "recipe": meal.recipe_details  # Full recipe with adjusted ingredients
                }
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error adjusting meal portion: {str(e)}")
            raise
    
    def adjust_recipe_portion(self, db: Session, recipe_id: str, new_servings: float) -> Dict[str, Any]:
        """
        Adjust the portion size of a database recipe and recalculate all ingredient quantities
        """
        try:
            # Get the recipe
            recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
            
            if not recipe:
                raise ValueError(f"Recipe {recipe_id} not found")
            
            if new_servings <= 0:
                raise ValueError("Servings must be greater than 0")
            
            # Calculate multiplier
            original_servings = recipe.servings or 1.0
            multiplier = new_servings / original_servings
            
            # Adjust ingredients with automatic standardization
            adjusted_ingredients = []
            for ri in recipe.ingredients:
                original_qty = ri.quantity
                original_unit = ri.unit or 'g'
                
                # Calculate adjusted quantity
                adjusted_quantity = original_qty * multiplier
                
                # Standardize measurement (ensures grams/ml/piece)
                standardized = self.measurement_service.standardize_ingredient_measurement(
                    ri.ingredient.name if ri.ingredient else "Unknown",
                    adjusted_quantity,
                    original_unit
                )
                
                adjusted_ingredients.append({
                    "ingredient_id": ri.ingredient_id,
                    "name": ri.ingredient.name if ri.ingredient else "Unknown",
                    "quantity": round(standardized['standardized_quantity'], 2),
                    "unit": standardized['standardized_unit'],  # Standardized unit
                    "original_quantity": original_qty,
                    "original_unit": original_unit,
                    "multiplier": round(multiplier, 2),
                    "measurement_type": standardized.get('measurement_type', 'weight')
                })
            
            # Adjust nutrition (if calculated)
            nutrition_multiplier = multiplier
            adjusted_nutrition = {
                "calories": round(getattr(recipe, 'calculated_calories', 0) * nutrition_multiplier, 1),
                "protein": round(getattr(recipe, 'calculated_protein', 0) * nutrition_multiplier, 1),
                "carbs": round(getattr(recipe, 'calculated_carbs', 0) * nutrition_multiplier, 1),
                "fats": round(getattr(recipe, 'calculated_fats', 0) * nutrition_multiplier, 1),
                "fiber": round(getattr(recipe, 'calculated_fiber', 0) * nutrition_multiplier, 1),
                "sugar": round(getattr(recipe, 'calculated_sugar', 0) * nutrition_multiplier, 1),
                "sodium": round(getattr(recipe, 'calculated_sodium', 0) * nutrition_multiplier, 1)
            }
            
            logger.info(f"Adjusted recipe {recipe_id} from {original_servings} to {new_servings} servings")
            
            return {
                "message": "Recipe portion adjusted successfully",
                "recipe_id": recipe.id,
                "title": recipe.title,
                "original_servings": original_servings,
                "new_servings": new_servings,
                "multiplier": round(multiplier, 2),
                "adjusted_ingredients": adjusted_ingredients,
                "adjusted_nutrition": adjusted_nutrition,
                "prep_time": recipe.prep_time,
                "cook_time": recipe.cook_time,
                "total_time": recipe.prep_time + recipe.cook_time
            }
            
        except Exception as e:
            logger.error(f"Error adjusting recipe portion: {str(e)}")
            raise
    
    def get_portion_suggestions_for_meal(self, db: Session, user_id: int, meal_id: str) -> Dict[str, Any]:
        """
        Get personalized portion suggestions for a meal based on user's health data
        """
        try:
            # Get the meal
            meal = db.query(MealPlanMeal).filter(MealPlanMeal.id == meal_id).first()
            
            if not meal:
                raise ValueError(f"Meal {meal_id} not found")
            
            # Get user's health profile for personalized suggestions
            from models.health_profile import HealthProfile
            health_profile = db.query(HealthProfile).filter(HealthProfile.user_id == user_id).first()
            
            # Get user's nutrition preferences
            from models.nutrition import UserNutritionPreferences
            nutrition_prefs = db.query(UserNutritionPreferences).filter(
                UserNutritionPreferences.user_id == user_id
            ).first()
            
            # Calculate base suggestions
            suggestions = []
            
            # Current serving size
            current_servings = 1.0
            if meal.recipe_details and isinstance(meal.recipe_details, dict):
                current_servings = meal.recipe_details.get('servings', 1.0)
            
            # Small portion (0.5x)
            small_servings = max(0.5, current_servings * 0.5)
            small_adjustment = self.adjust_meal_portion(db, meal_id, small_servings)
            suggestions.append({
                "serving_size": small_servings,
                "label": "Small Portion",
                "description": "Light meal or snack",
                "calories": small_adjustment["adjusted_nutrition"]["calories"],
                "reasoning": "Good for light meals or when you're not very hungry"
            })
            
            # Reset to original
            self.adjust_meal_portion(db, meal_id, current_servings)
            
            # Regular portion (1x)
            regular_servings = current_servings
            suggestions.append({
                "serving_size": regular_servings,
                "label": "Regular Portion",
                "description": "Standard serving size",
                "calories": meal.calories or 0,
                "reasoning": "Balanced portion for most people"
            })
            
            # Large portion (1.5x)
            large_servings = current_servings * 1.5
            large_adjustment = self.adjust_meal_portion(db, meal_id, large_servings)
            suggestions.append({
                "serving_size": large_servings,
                "label": "Large Portion",
                "description": "Hearty meal",
                "calories": large_adjustment["adjusted_nutrition"]["calories"],
                "reasoning": "Good for active individuals or when you're very hungry"
            })
            
            # Reset to original
            self.adjust_meal_portion(db, meal_id, current_servings)
            
            # Personalized suggestion based on user data
            if health_profile and nutrition_prefs:
                daily_calorie_target = nutrition_prefs.daily_calorie_target or 2000
                meals_per_day = nutrition_prefs.meals_per_day or 3
                target_calories_per_meal = daily_calorie_target / meals_per_day
                
                # Get personalized targets for better portion suggestions
                from services.nutrition_service import NutritionService
                nutrition_service = NutritionService()
                personalized_targets = nutrition_service.calculate_personalized_targets(db, user_id)
                
                # Use personalized calorie target if available
                if personalized_targets.get('personalized') and personalized_targets.get('calorie_target'):
                    daily_calorie_target = personalized_targets['calorie_target']
                    target_calories_per_meal = daily_calorie_target / meals_per_day
                
                # Calculate suggested servings to meet calorie target
                if meal.calories and meal.calories > 0:
                    suggested_servings = target_calories_per_meal / meal.calories
                    suggested_servings = max(0.5, min(3.0, suggested_servings))  # Reasonable range
                    
                    personalized_adjustment = self.adjust_meal_portion(db, meal_id, suggested_servings)
                    
                    # Create personalized reasoning based on user context
                    reasoning_parts = [f"Based on your daily calorie target of {daily_calorie_target} kcal"]
                    
                    if personalized_targets.get('activity_level'):
                        activity = personalized_targets['activity_level'].replace('_', ' ').title()
                        reasoning_parts.append(f"and {activity} lifestyle")
                    
                    if personalized_targets.get('fitness_goal'):
                        goal = personalized_targets['fitness_goal'].replace('_', ' ').title()
                        reasoning_parts.append(f"for {goal}")
                    
                    reasoning = f"{', '.join(reasoning_parts)}, this portion helps you stay on track."
                    
                    suggestions.append({
                        "serving_size": suggested_servings,
                        "label": "Personalized Suggestion",
                        "description": "Optimized for your health profile and goals",
                        "calories": personalized_adjustment["adjusted_nutrition"]["calories"],
                        "reasoning": reasoning
                    })
                    
                    # Reset to original
                    self.adjust_meal_portion(db, meal_id, current_servings)
            
            return {
                "meal_id": meal_id,
                "meal_name": meal.meal_name,
                "current_servings": current_servings,
                "suggestions": suggestions,
                "user_context": {
                    "has_health_profile": health_profile is not None,
                    "has_nutrition_prefs": nutrition_prefs is not None,
                    "daily_calorie_target": nutrition_prefs.daily_calorie_target if nutrition_prefs else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting portion suggestions for meal: {str(e)}")
            raise
    
    def batch_adjust_meal_plan_portions(self, db: Session, meal_plan_id: str, 
                                      portion_adjustments: Dict[str, float]) -> Dict[str, Any]:
        """
        Adjust portions for multiple meals in a meal plan
        """
        try:
            # Get the meal plan
            meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()
            
            if not meal_plan:
                raise ValueError(f"Meal plan {meal_plan_id} not found")
            
            # Get all meals in the meal plan
            meals = db.query(MealPlanMeal).filter(MealPlanMeal.meal_plan_id == meal_plan_id).all()
            
            adjusted_meals = []
            total_adjusted_nutrition = {
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fats': 0
            }
            
            for meal in meals:
                if meal.id in portion_adjustments:
                    new_servings = portion_adjustments[meal.id]
                    adjustment_result = self.adjust_meal_portion(db, meal.id, new_servings)
                    adjusted_meals.append(adjustment_result)
                    
                    # Add to total nutrition
                    nutrition = adjustment_result["adjusted_nutrition"]
                    total_adjusted_nutrition['calories'] += nutrition['calories']
                    total_adjusted_nutrition['protein'] += nutrition['protein']
                    total_adjusted_nutrition['carbs'] += nutrition['carbs']
                    total_adjusted_nutrition['fats'] += nutrition['fats']
            
            logger.info(f"Batch adjusted {len(adjusted_meals)} meals in meal plan {meal_plan_id}")
            
            return {
                "message": f"Successfully adjusted {len(adjusted_meals)} meals",
                "meal_plan_id": meal_plan_id,
                "adjusted_meals": adjusted_meals,
                "total_adjusted_nutrition": total_adjusted_nutrition,
                "adjustments_made": len(adjusted_meals)
            }
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error batch adjusting meal plan portions: {str(e)}")
            raise
