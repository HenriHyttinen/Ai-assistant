"""
Service to integrate data between Health Profile and Nutrition Preferences
to avoid duplicate input and provide seamless user experience.
"""

from sqlalchemy.orm import Session
from models.health_profile import HealthProfile
from models.nutrition import UserNutritionPreferences
from typing import Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

class IntegrationService:
    """Service to handle data integration between different user profile sections"""
    
    def get_integrated_nutrition_preferences(self, db: Session, user_id: int) -> Dict[str, Any]:
        """
        Get nutrition preferences with data pre-filled from health profile
        to avoid duplicate input.
        """
        try:
            # Get health profile data
            health_profile = db.query(HealthProfile).filter(
                HealthProfile.user_id == user_id
            ).first()
            
            # Get existing nutrition preferences
            nutrition_prefs = db.query(UserNutritionPreferences).filter(
                UserNutritionPreferences.user_id == user_id
            ).first()
            
            # Start with default values
            integrated_data = {
                "dietary_preferences": [],
                "allergies": [],
                "disliked_ingredients": [],
                "cuisine_preferences": [],
                "daily_calorie_target": 2000,
                "protein_target": 100,
                "carbs_target": 200,
                "fats_target": 65,
                "meals_per_day": 3,
                "snacks_per_day": 2,
                "preferred_meal_times": {
                    "breakfast": "08:00",
                    "lunch": "13:00",
                    "dinner": "19:00"
                },
                "timezone": "UTC"
            }
            
            # Pre-fill from health profile if available
            if health_profile:
                # Dietary preferences from health profile
                if health_profile.dietary_preferences:
                    try:
                        health_dietary = json.loads(health_profile.dietary_preferences)
                        if isinstance(health_dietary, list):
                            integrated_data["dietary_preferences"] = health_dietary
                        elif isinstance(health_dietary, str):
                            # Convert string to list if needed
                            integrated_data["dietary_preferences"] = [health_dietary]
                    except (json.JSONDecodeError, TypeError):
                        # If it's a simple string, convert to list
                        integrated_data["dietary_preferences"] = [health_profile.dietary_preferences]
                
                # Dietary restrictions from health profile
                if health_profile.dietary_restrictions:
                    try:
                        health_restrictions = json.loads(health_profile.dietary_restrictions)
                        if isinstance(health_restrictions, list):
                            integrated_data["allergies"] = health_restrictions
                        elif isinstance(health_restrictions, str):
                            integrated_data["allergies"] = [health_restrictions]
                    except (json.JSONDecodeError, TypeError):
                        integrated_data["allergies"] = [health_profile.dietary_restrictions]
                
                # Meal preferences from health profile
                if health_profile.meal_preferences:
                    try:
                        meal_prefs = json.loads(health_profile.meal_preferences)
                        if isinstance(meal_prefs, dict):
                            integrated_data["preferred_meal_times"] = meal_prefs
                    except (json.JSONDecodeError, TypeError):
                        pass
                
                # Calculate calorie targets based on health profile
                if health_profile.weight and health_profile.height and health_profile.activity_level:
                    calorie_target = self._calculate_calorie_target(
                        health_profile.weight,
                        health_profile.height,
                        health_profile.age,
                        health_profile.gender,
                        health_profile.activity_level,
                        health_profile.fitness_goal
                    )
                    integrated_data["daily_calorie_target"] = calorie_target
                
                # Calculate protein target based on weight and goals
                if health_profile.weight:
                    protein_target = self._calculate_protein_target(
                        health_profile.weight,
                        health_profile.fitness_goal
                    )
                    integrated_data["protein_target"] = protein_target
            
            # Override with existing nutrition preferences if they exist
            if nutrition_prefs:
                integrated_data.update({
                    "dietary_preferences": nutrition_prefs.dietary_preferences or integrated_data["dietary_preferences"],
                    "allergies": nutrition_prefs.allergies or integrated_data["allergies"],
                    "disliked_ingredients": nutrition_prefs.disliked_ingredients or integrated_data["disliked_ingredients"],
                    "cuisine_preferences": nutrition_prefs.cuisine_preferences or integrated_data["cuisine_preferences"],
                    "daily_calorie_target": nutrition_prefs.daily_calorie_target or integrated_data["daily_calorie_target"],
                    "protein_target": nutrition_prefs.protein_target or integrated_data["protein_target"],
                    "carbs_target": nutrition_prefs.carbs_target or integrated_data["carbs_target"],
                    "fats_target": nutrition_prefs.fats_target or integrated_data["fats_target"],
                    "meals_per_day": nutrition_prefs.meals_per_day or integrated_data["meals_per_day"],
                    "snacks_per_day": nutrition_prefs.snacks_per_day or integrated_data["snacks_per_day"],
                    "preferred_meal_times": nutrition_prefs.preferred_meal_times or integrated_data["preferred_meal_times"],
                    "timezone": nutrition_prefs.timezone or integrated_data["timezone"]
                })
            
            return integrated_data
            
        except Exception as e:
            logger.error(f"Error getting integrated nutrition preferences: {str(e)}")
            # Return default values if integration fails
            return {
                "dietary_preferences": [],
                "allergies": [],
                "disliked_ingredients": [],
                "cuisine_preferences": [],
                "daily_calorie_target": 2000,
                "protein_target": 100,
                "carbs_target": 200,
                "fats_target": 65,
                "meals_per_day": 3,
                "snacks_per_day": 2,
                "preferred_meal_times": {
                    "breakfast": "08:00",
                    "lunch": "13:00",
                    "dinner": "19:00"
                },
                "timezone": "UTC"
            }
    
    def _calculate_calorie_target(self, weight: float, height: float, age: Optional[int], 
                                gender: Optional[str], activity_level: str, fitness_goal: Optional[str]) -> int:
        """Calculate daily calorie target based on health profile data"""
        try:
            # Calculate BMR using Mifflin-St Jeor Equation
            if gender and age:
                if gender.lower() in ['male', 'm']:
                    bmr = 10 * weight + 6.25 * height - 5 * age + 5
                else:
                    bmr = 10 * weight + 6.25 * height - 5 * age - 161
            else:
                # Default to male calculation if gender/age not available
                bmr = 10 * weight + 6.25 * height - 5 * 30 + 5
            
            # Activity multipliers
            activity_multipliers = {
                'sedentary': 1.2,
                'light': 1.375,
                'moderate': 1.55,
                'active': 1.725,
                'very_active': 1.9
            }
            
            activity_multiplier = activity_multipliers.get(activity_level.lower(), 1.55)
            tdee = bmr * activity_multiplier
            
            # Adjust based on fitness goal
            if fitness_goal:
                if 'weight loss' in fitness_goal.lower():
                    tdee *= 0.8  # 20% deficit
                elif 'weight gain' in fitness_goal.lower() or 'muscle' in fitness_goal.lower():
                    tdee *= 1.1  # 10% surplus
            
            return int(tdee)
            
        except Exception as e:
            logger.error(f"Error calculating calorie target: {str(e)}")
            return 2000  # Default fallback
    
    def _calculate_protein_target(self, weight: float, fitness_goal: Optional[str]) -> float:
        """Calculate protein target based on weight and fitness goals"""
        try:
            # Base protein requirement (g per kg body weight)
            if fitness_goal:
                if 'muscle' in fitness_goal.lower() or 'strength' in fitness_goal.lower():
                    protein_per_kg = 2.0  # Higher for muscle building
                elif 'weight loss' in fitness_goal.lower():
                    protein_per_kg = 1.8  # Higher for weight loss to preserve muscle
                else:
                    protein_per_kg = 1.6  # Moderate for general fitness
            else:
                protein_per_kg = 1.6  # Default moderate level
            
            return round(weight * protein_per_kg, 1)
            
        except Exception as e:
            logger.error(f"Error calculating protein target: {str(e)}")
            return 100.0  # Default fallback
    
    def sync_health_profile_to_nutrition(self, db: Session, user_id: int) -> bool:
        """
        Sync relevant data from health profile to nutrition preferences
        when health profile is updated.
        """
        try:
            health_profile = db.query(HealthProfile).filter(
                HealthProfile.user_id == user_id
            ).first()
            
            if not health_profile:
                return False
            
            # Get or create nutrition preferences
            nutrition_prefs = db.query(UserNutritionPreferences).filter(
                UserNutritionPreferences.user_id == user_id
            ).first()
            
            if not nutrition_prefs:
                nutrition_prefs = UserNutritionPreferences(user_id=user_id)
                db.add(nutrition_prefs)
            
            # Update nutrition preferences with health profile data
            if health_profile.dietary_preferences:
                try:
                    health_dietary = json.loads(health_profile.dietary_preferences)
                    nutrition_prefs.dietary_preferences = health_dietary if isinstance(health_dietary, list) else [health_dietary]
                except (json.JSONDecodeError, TypeError):
                    nutrition_prefs.dietary_preferences = [health_profile.dietary_preferences]
            
            if health_profile.dietary_restrictions:
                try:
                    health_restrictions = json.loads(health_profile.dietary_restrictions)
                    nutrition_prefs.allergies = health_restrictions if isinstance(health_restrictions, list) else [health_restrictions]
                except (json.JSONDecodeError, TypeError):
                    nutrition_prefs.allergies = [health_profile.dietary_restrictions]
            
            # Recalculate targets based on updated health profile
            if health_profile.weight and health_profile.height and health_profile.activity_level:
                nutrition_prefs.daily_calorie_target = self._calculate_calorie_target(
                    health_profile.weight,
                    health_profile.height,
                    health_profile.age,
                    health_profile.gender,
                    health_profile.activity_level,
                    health_profile.fitness_goal
                )
                
                nutrition_prefs.protein_target = self._calculate_protein_target(
                    health_profile.weight,
                    health_profile.fitness_goal
                )
            
            db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error syncing health profile to nutrition: {str(e)}")
            db.rollback()
            return False
