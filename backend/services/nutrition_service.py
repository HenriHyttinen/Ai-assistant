import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc, case

from models.recipe import Recipe, Ingredient
from models.nutrition import (
    MealPlan, MealPlanMeal, MealPlanRecipe,
    NutritionalLog, ShoppingList, ShoppingListItem, UserNutritionPreferences
)
from models.health_profile import HealthProfile
from models.metrics_history import MetricsHistory
from schemas.nutrition import (
    MealPlanRequest, RecipeSearchRequest, ShoppingListCreate,
    NutritionalAnalysisRequest
)
from ai.nutrition_ai import NutritionAI
from services.measurement_standardization_service import MeasurementStandardizationService
from services.ai_nutritional_analysis_service import AINutritionalAnalysisService
from services.ai_improvement_suggestions_service import AIImprovementSuggestionsService
from services.meal_plan_versioning_service import meal_plan_versioning_service
from services.enhanced_dietary_service import EnhancedDietaryService
from services.enhanced_personalization_service import EnhancedPersonalizationService
from ai.enhanced_nutrition_ai import EnhancedNutritionAI

logger = logging.getLogger(__name__)

class NutritionService:
    def __init__(self):
        self.nutrition_ai = NutritionAI()
        self.enhanced_nutrition_ai = EnhancedNutritionAI()
        self.measurement_service = MeasurementStandardizationService()
        self.ai_analysis_service = AINutritionalAnalysisService()
        self.ai_suggestions_service = AIImprovementSuggestionsService()
        self.enhanced_dietary_service = EnhancedDietaryService()
        self.enhanced_personalization_service = EnhancedPersonalizationService()
    
    def calculate_personalized_targets(self, db: Session, user_id: int) -> Dict[str, Any]:
        """
        Calculate personalized nutrition targets based on health profile, BMI, and activity level
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dictionary with personalized nutrition targets
        """
        try:
            # Get user's health profile
            health_profile = db.query(HealthProfile).filter(HealthProfile.user_id == user_id).first()
            if not health_profile:
                return self._get_default_targets()
            
            # Get latest metrics
            latest_metrics = db.query(MetricsHistory).filter(
                MetricsHistory.health_profile_id == health_profile.id
            ).order_by(desc(MetricsHistory.recorded_at)).first()
            
            if not latest_metrics:
                return self._get_default_targets()
            
            # Extract health data
            weight = latest_metrics.weight
            height = health_profile.height  # in cm
            age = health_profile.age
            gender = health_profile.gender.lower()
            activity_level = health_profile.activity_level.lower()
            fitness_goal = health_profile.fitness_goal.lower()
            
            # Calculate BMI
            bmi = weight / ((height / 100) ** 2)
            
            # Calculate BMR (Basal Metabolic Rate) using Mifflin-St Jeor Equation
            if gender == "male":
                bmr = 10 * weight + 6.25 * height - 5 * age + 5
            else:
                bmr = 10 * weight + 6.25 * height - 5 * age - 161
            
            # Activity multipliers
            activity_multipliers = {
                "sedentary": 1.2,
                "lightly_active": 1.375,
                "moderately_active": 1.55,
                "very_active": 1.725,
                "extremely_active": 1.9
            }
            
            activity_multiplier = activity_multipliers.get(activity_level, 1.2)
            tdee = bmr * activity_multiplier  # Total Daily Energy Expenditure
            
            # Adjust calories based on fitness goal
            if fitness_goal == "weight_loss":
                calorie_target = tdee - 500  # 500 calorie deficit
            elif fitness_goal == "weight_gain":
                calorie_target = tdee + 500  # 500 calorie surplus
            elif fitness_goal == "muscle_gain":
                calorie_target = tdee + 300  # 300 calorie surplus
            else:  # maintenance
                calorie_target = tdee
            
            # Calculate macronutrient targets based on goals
            if fitness_goal == "weight_loss":
                protein_ratio = 0.3  # Higher protein for weight loss
                carbs_ratio = 0.4
                fats_ratio = 0.3
            elif fitness_goal == "muscle_gain":
                protein_ratio = 0.25  # Higher protein for muscle building
                carbs_ratio = 0.45
                fats_ratio = 0.3
            else:  # maintenance
                protein_ratio = 0.2
                carbs_ratio = 0.5
                fats_ratio = 0.3
            
            # Calculate macro targets in grams
            protein_target = (calorie_target * protein_ratio) / 4  # 4 cal/g protein
            carbs_target = (calorie_target * carbs_ratio) / 4  # 4 cal/g carbs
            fats_target = (calorie_target * fats_ratio) / 9  # 9 cal/g fat
            
            # Adjust for activity level
            if activity_level in ["very_active", "extremely_active"]:
                # Increase carbs for high activity
                carbs_target *= 1.2
                calorie_target += 200
            
            return {
                "calorie_target": round(calorie_target),
                "protein_target": round(protein_target, 1),
                "carbs_target": round(carbs_target, 1),
                "fats_target": round(fats_target, 1),
                "bmi": round(bmi, 1),
                "bmr": round(bmr),
                "tdee": round(tdee),
                "activity_level": activity_level,
                "fitness_goal": fitness_goal,
                "personalized": True
            }
            
        except Exception as e:
            logger.error(f"Error calculating personalized targets: {str(e)}")
            return self._get_default_targets()
    
    def _get_default_targets(self) -> Dict[str, Any]:
        """Get default nutrition targets when health data is unavailable"""
        return {
            "calorie_target": 2000,
            "protein_target": 150,
            "carbs_target": 250,
            "fats_target": 65,
            "personalized": False
        }
    
    def adjust_recipe_portions(self, recipe: Recipe, new_servings: float) -> Dict[str, Any]:
        """
        Adjust recipe ingredients and nutrition for different serving sizes
        
        Args:
            recipe: Recipe object
            new_servings: New number of servings
            
        Returns:
            Dictionary with adjusted recipe data
        """
        try:
            original_servings = recipe.servings
            multiplier = new_servings / original_servings
            
            # Adjust ingredients
            adjusted_ingredients = []
            for ri in recipe.ingredients:
                adjusted_quantity = ri.quantity * multiplier
                adjusted_ingredients.append({
                    "ingredient_id": ri.ingredient_id,
                    "name": ri.ingredient.name if ri.ingredient else "Unknown",
                    "quantity": round(adjusted_quantity, 2),
                    "unit": ri.unit,
                    "original_quantity": ri.quantity,
                    "multiplier": round(multiplier, 2)
                })
            
            # Adjust nutrition (assuming we have calculated nutrition)
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
            
            return {
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
            logger.error(f"Error adjusting recipe portions: {str(e)}")
            return {"error": f"Failed to adjust portions: {str(e)}"}
    
    def get_portion_suggestions(self, db: Session, user_id: int, recipe: Recipe) -> Dict[str, Any]:
        """
        Get personalized portion suggestions based on user's health data
        
        Args:
            db: Database session
            user_id: User ID
            recipe: Recipe object
            
        Returns:
            Dictionary with portion suggestions
        """
        try:
            # Get personalized targets
            targets = self.calculate_personalized_targets(db, user_id)
            
            # Calculate suggested servings based on calorie target
            recipe_calories = getattr(recipe, 'calculated_calories', 0)
            if recipe_calories == 0:
                return {"error": "Recipe nutrition not calculated"}
            
            # Suggest servings to meet daily calorie target
            daily_calorie_target = targets.get("calorie_target", 2000)
            meals_per_day = 3  # Default, could be from user preferences
            
            target_calories_per_meal = daily_calorie_target / meals_per_day
            suggested_servings = target_calories_per_meal / recipe_calories
            
            # Round to reasonable serving sizes
            if suggested_servings < 0.5:
                suggested_servings = 0.5
            elif suggested_servings > 4:
                suggested_servings = 4
            else:
                suggested_servings = round(suggested_servings, 1)
            
            # Get adjusted recipe for suggested servings
            adjusted_recipe = self.adjust_recipe_portions(recipe, suggested_servings)
            
            return {
                "suggested_servings": suggested_servings,
                "reasoning": f"Based on your daily calorie target of {daily_calorie_target} calories",
                "adjusted_recipe": adjusted_recipe,
                "targets_used": targets
            }
            
        except Exception as e:
            logger.error(f"Error getting portion suggestions: {str(e)}")
            return {"error": f"Failed to get portion suggestions: {str(e)}"}
    
    def standardize_recipe_measurements(self, recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize all measurements in a recipe to common units
        """
        try:
            return self.measurement_service.standardize_recipe_measurements(recipe_data)
        except Exception as e:
            logger.error(f"Error standardizing recipe measurements: {str(e)}")
            return recipe_data
    
    def standardize_ingredient_measurement(self, ingredient_name: str, quantity: float, unit: str) -> Dict[str, Any]:
        """
        Standardize a single ingredient measurement
        """
        try:
            return self.measurement_service.standardize_ingredient_measurement(ingredient_name, quantity, unit)
        except Exception as e:
            logger.error(f"Error standardizing ingredient measurement: {str(e)}")
            return {
                'original_quantity': quantity,
                'original_unit': unit,
                'standardized_quantity': quantity,
                'standardized_unit': unit,
                'measurement_type': 'unknown',
                'conversion_applied': False,
                'error': str(e)
            }
    
    def get_comprehensive_ai_analysis(self, db: Session, user_id: int, 
                                    start_date: date, end_date: date, 
                                    analysis_type: str = "daily") -> Dict[str, Any]:
        """
        Get comprehensive AI-driven nutritional analysis with achievements, concerns, and balance analysis
        """
        try:
            return self.ai_analysis_service.generate_comprehensive_analysis(
                db, user_id, start_date, end_date, analysis_type
            )
        except Exception as e:
            logger.error(f"Error getting comprehensive AI analysis: {str(e)}")
            return self.ai_analysis_service._generate_fallback_analysis()
    
    def get_ai_improvement_suggestions(self, db: Session, user_id: int, 
                                     start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Get comprehensive AI-driven improvement suggestions including food recommendations, timing, portions, and alternatives
        """
        try:
            return self.ai_suggestions_service.generate_comprehensive_suggestions(
                db, user_id, start_date, end_date
            )
        except Exception as e:
            logger.error(f"Error getting AI improvement suggestions: {str(e)}")
            return self.ai_suggestions_service._generate_fallback_suggestions()
    
    def optimize_meal_timing(self, db: Session, user_id: int, meal_plan: MealPlan) -> Dict[str, Any]:
        """
        Optimize meal timing based on user's activity level and preferences
        
        Args:
            db: Database session
            user_id: User ID
            meal_plan: Meal plan to optimize
            
        Returns:
            Dictionary with meal timing
        """
        try:
            # Get user's health profile and preferences
            health_profile = db.query(HealthProfile).filter(HealthProfile.user_id == user_id).first()
            nutrition_prefs = db.query(UserNutritionPreferences).filter(
                UserNutritionPreferences.user_id == user_id
            ).first()
            
            if not health_profile:
                return {"error": "Health profile not found"}
            
            activity_level = health_profile.activity_level.lower()
            preferred_meal_times = nutrition_prefs.preferred_meal_times if nutrition_prefs else {}
            timezone = nutrition_prefs.timezone if nutrition_prefs else "UTC"
            
            # Default meal times based on activity level
            default_times = {
                "sedentary": {
                    "breakfast": "08:00",
                    "lunch": "13:00", 
                    "dinner": "19:00"
                },
                "lightly_active": {
                    "breakfast": "07:30",
                    "lunch": "12:30",
                    "dinner": "18:30"
                },
                "moderately_active": {
                    "breakfast": "07:00",
                    "lunch": "12:00",
                    "dinner": "18:00"
                },
                "very_active": {
                    "breakfast": "06:30",
                    "lunch": "11:30",
                    "dinner": "17:30"
                },
                "extremely_active": {
                    "breakfast": "06:00",
                    "lunch": "11:00",
                    "dinner": "17:00"
                }
            }
            
            # Use preferred times or defaults
            meal_times = preferred_meal_times if preferred_meal_times else default_times.get(activity_level, default_times["moderately_active"])
            
            # Add snacks for high activity levels
            if activity_level in ["very_active", "extremely_active"]:
                meal_times["snack_1"] = "10:00"
                meal_times["snack_2"] = "15:00"
            
            timed_meals = []
            for meal in meal_plan.meals:
                meal_type = meal.meal_type
                meal_time = meal_times.get(meal_type, "12:00")
                
                # Adjust timing based on meal calories
                if meal.calories > 600:  # Large meal
                    # Suggest earlier for better digestion
                    if meal_type == "dinner":
                        meal_time = self._adjust_time_earlier(meal_time, 30)
                elif meal.calories < 200:  # Small meal/snack
                    # Can be more flexible
                    pass
                
                timed_meals.append({
                    "meal_id": meal.id,
                    "meal_type": meal_type,
                    "meal_name": meal.meal_name,
                    "original_time": meal.meal_time,
                    "meal_time": meal_time,
                    "calories": meal.calories,
                    "reasoning": self._get_timing_reasoning(meal_type, activity_level, meal.calories)
                })
            
            return {
                "timed_meals": timed_meals,
                "activity_level": activity_level,
                "timezone": timezone,
                "recommendations": self._get_meal_timing_recommendations(activity_level)
            }
            
        except Exception as e:
            logger.error(f"Error optimizing meal timing: {str(e)}")
            return {"error": f"Failed to optimize meal timing: {str(e)}"}
    
    def _adjust_time_earlier(self, time_str: str, minutes: int) -> str:
        """Adjust time string to be earlier by specified minutes"""
        try:
            from datetime import datetime, timedelta
            time_obj = datetime.strptime(time_str, "%H:%M")
            adjusted_time = time_obj - timedelta(minutes=minutes)
            return adjusted_time.strftime("%H:%M")
        except:
            return time_str
    
    def _get_timing_reasoning(self, meal_type: str, activity_level: str, calories: float) -> str:
        """Get reasoning for meal timing optimization"""
        if meal_type == "breakfast":
            if activity_level in ["very_active", "extremely_active"]:
                return "Early breakfast provides energy for morning activities"
            else:
                return "Standard breakfast time for your activity level"
        elif meal_type == "lunch":
            return "Midday meal to maintain energy levels"
        elif meal_type == "dinner":
            if calories > 600:
                return "Earlier dinner for better digestion of large meal"
            else:
                return "Standard dinner time"
        elif meal_type == "snack":
            return "Strategic snack timing for sustained energy"
        else:
            return "Timing based on your activity level"
    
    def _get_meal_timing_recommendations(self, activity_level: str) -> List[str]:
        """Get general meal timing recommendations"""
        recommendations = []
        
        if activity_level == "sedentary":
            recommendations.extend([
                "Space meals 4-5 hours apart for better digestion",
                "Avoid eating 2-3 hours before bedtime",
                "Consider smaller, more frequent meals"
            ])
        elif activity_level in ["lightly_active", "moderately_active"]:
            recommendations.extend([
                "Maintain consistent meal times",
                "Eat within 1 hour of waking up",
                "Have dinner 3-4 hours before bedtime"
            ])
        else:  # very_active or extremely_active
            recommendations.extend([
                "Eat within 30 minutes of waking up",
                "Include pre and post-workout nutrition",
                "Consider 5-6 smaller meals throughout the day",
                "Stay hydrated between meals"
            ])
        
        return recommendations
    
    def update_wellness_score_from_nutrition(self, db: Session, user_id: int, analysis_period: str = "week") -> Dict[str, Any]:
        """
        Update wellness score based on nutritional intake and adherence to goals
        
        Args:
            db: Database session
            user_id: User ID
            analysis_period: Period to analyze (day, week, month)
            
        Returns:
            Dictionary with updated wellness score and factors
        """
        try:
            # Get user's health profile
            health_profile = db.query(HealthProfile).filter(HealthProfile.user_id == user_id).first()
            if not health_profile:
                return {"error": "Health profile not found"}
            
            # Calculate date range
            today = date.today()
            if analysis_period == "day":
                start_date = end_date = today
            elif analysis_period == "week":
                start_date = today - timedelta(days=6)
                end_date = today
            elif analysis_period == "month":
                start_date = today - timedelta(days=29)
                end_date = today
            else:
                start_date = end_date = today
            
            # Get nutritional analysis
            nutrition_analysis = self.get_nutritional_analysis(
                db=db,
                user_id=user_id,
                start_date=start_date,
                end_date=end_date,
                analysis_type=analysis_period
            )
            
            # Get personalized targets
            targets = self.calculate_personalized_targets(db, user_id)
            
            # Calculate nutrition adherence score (0-100)
            nutrition_score = self._calculate_nutrition_adherence_score(nutrition_analysis, targets)
            
            # Calculate micronutrient diversity score
            micronutrient_score = self._calculate_micronutrient_score(db, user_id, start_date, end_date)
            
            # Calculate meal consistency score
            consistency_score = self._calculate_meal_consistency_score(db, user_id, start_date, end_date)
            
            # Calculate overall nutrition wellness score
            nutrition_wellness_score = (
                nutrition_score * 0.4 +  # 40% weight to macro adherence
                micronutrient_score * 0.3 +  # 30% weight to micronutrient diversity
                consistency_score * 0.3  # 30% weight to meal consistency
            )
            
            # Get current wellness score
            latest_metrics = db.query(MetricsHistory).filter(
                MetricsHistory.health_profile_id == health_profile.id
            ).order_by(desc(MetricsHistory.recorded_at)).first()
            
            current_wellness_score = latest_metrics.wellness_score if latest_metrics else 50
            
            # Update wellness score (weighted average with existing score)
            updated_wellness_score = (current_wellness_score * 0.7) + (nutrition_wellness_score * 0.3)
            updated_wellness_score = min(100, max(0, updated_wellness_score))
            
            # Create new metrics entry
            new_metrics = MetricsHistory(
                health_profile_id=health_profile.id,
                weight=latest_metrics.weight if latest_metrics else health_profile.weight,
                bmi=latest_metrics.bmi if latest_metrics else 0,
                wellness_score=updated_wellness_score,
                recorded_at=datetime.utcnow()
            )
            db.add(new_metrics)
            db.commit()
            
            return {
                "previous_wellness_score": current_wellness_score,
                "updated_wellness_score": round(updated_wellness_score, 1),
                "nutrition_wellness_score": round(nutrition_wellness_score, 1),
                "nutrition_score": round(nutrition_score, 1),
                "micronutrient_score": round(micronutrient_score, 1),
                "consistency_score": round(consistency_score, 1),
                "analysis_period": analysis_period,
                "factors": {
                    "macro_adherence": round(nutrition_score, 1),
                    "micronutrient_diversity": round(micronutrient_score, 1),
                    "meal_consistency": round(consistency_score, 1)
                },
                "recommendations": self._get_wellness_improvement_recommendations(
                    nutrition_score, micronutrient_score, consistency_score
                )
            }
            
        except Exception as e:
            logger.error(f"Error updating wellness score from nutrition: {str(e)}")
            return {"error": f"Failed to update wellness score: {str(e)}"}
    
    def _calculate_nutrition_adherence_score(self, analysis: Dict, targets: Dict) -> float:
        """Calculate how well user adheres to nutritional targets (0-100)"""
        try:
            percentages = analysis.get("percentages", {})
            
            # Weight different nutrients
            weights = {
                "calories": 0.4,
                "protein": 0.3,
                "carbs": 0.2,
                "fats": 0.1
            }
            
            total_score = 0
            for nutrient, weight in weights.items():
                percentage = percentages.get(nutrient, 0)
                # Optimal range is 80-120% of target
                if 80 <= percentage <= 120:
                    score = 100
                elif 70 <= percentage < 80 or 120 < percentage <= 130:
                    score = 80
                elif 60 <= percentage < 70 or 130 < percentage <= 140:
                    score = 60
                else:
                    score = max(0, 100 - abs(percentage - 100))
                
                total_score += score * weight
            
            return min(100, total_score)
            
        except Exception:
            return 50  # Default score if calculation fails
    
    def _calculate_micronutrient_score(self, db: Session, user_id: int, start_date: date, end_date: date) -> float:
        """Calculate micronutrient diversity score (0-100)"""
        try:
            # This would use the micronutrient service
            # For now, return a placeholder score
            return 75.0
        except Exception:
            return 50.0
    
    def _calculate_meal_consistency_score(self, db: Session, user_id: int, start_date: date, end_date: date) -> float:
        """Calculate meal consistency score based on regular eating patterns (0-100)"""
        try:
            # Get meal logs for the period
            logs = db.query(NutritionalLog).filter(
                and_(
                    NutritionalLog.user_id == user_id,
                    NutritionalLog.log_date >= start_date,
                    NutritionalLog.log_date <= end_date
                )
            ).all()
            
            if not logs:
                return 0
            
            # Count days with meals
            days_with_meals = len(set(log.log_date for log in logs))
            total_days = (end_date - start_date).days + 1
            
            # Base score on meal frequency
            frequency_score = (days_with_meals / total_days) * 100
            
            # Bonus for consistent meal timing (simplified)
            meal_times = [log.log_date for log in logs]
            consistency_bonus = min(20, len(set(meal_times)) * 2)
            
            return min(100, frequency_score + consistency_bonus)
            
        except Exception:
            return 50.0
    
    def _get_wellness_improvement_recommendations(self, nutrition_score: float, micronutrient_score: float, consistency_score: float) -> List[str]:
        """Get recommendations to improve wellness score"""
        recommendations = []
        
        if nutrition_score < 70:
            recommendations.append("Focus on meeting your daily calorie and macro targets")
        
        if micronutrient_score < 70:
            recommendations.append("Increase variety in your diet to improve micronutrient intake")
        
        if consistency_score < 70:
            recommendations.append("Try to eat meals at consistent times each day")
        
        if not recommendations:
            recommendations.append("Great job! Your nutrition habits are supporting your wellness goals")
        
        return recommendations
    
    def generate_enhanced_meal_plan(self, db: Session, user_id: int, plan_request: MealPlanRequest) -> Dict[str, Any]:
        """
        Generate enhanced meal plan with advanced personalization and dietary restrictions
        
        Args:
            db: Database session
            user_id: User ID
            plan_request: Meal plan generation request
            
        Returns:
            Enhanced meal plan with personalization metadata
        """
        try:
            # Get user preferences
            preferences = db.query(UserNutritionPreferences).filter(
                UserNutritionPreferences.user_id == user_id
            ).first()
            
            if not preferences:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Please set up your nutrition preferences first"
                )
            
            # Get personalized targets
            personalized_targets = self.calculate_personalized_targets(db, user_id)
            
            # Get wellness score for additional personalization
            wellness_data = self.update_wellness_score_from_nutrition(db, user_id, "week")
            
            # Build enhanced user preferences
            enhanced_preferences = {
                "dietary_preferences": preferences.dietary_preferences or [],
                "allergies": preferences.allergies or [],
                "disliked_ingredients": preferences.disliked_ingredients or [],
                "cuisine_preferences": preferences.cuisine_preferences or [],
                "daily_calorie_target": personalized_targets.get("calorie_target") or preferences.daily_calorie_target,
                "protein_target": personalized_targets.get("protein_target") or preferences.protein_target,
                "carbs_target": personalized_targets.get("carbs_target") or preferences.carbs_target,
                "fats_target": personalized_targets.get("fats_target") or preferences.fats_target,
                "meals_per_day": preferences.meals_per_day,
                "personalization_context": {
                    "bmi": personalized_targets.get("bmi"),
                    "activity_level": personalized_targets.get("activity_level"),
                    "fitness_goal": personalized_targets.get("fitness_goal"),
                    "wellness_score": wellness_data.get("wellness_score"),
                    "is_personalized": personalized_targets.get("personalized", False),
                    "age": personalized_targets.get("age"),
                    "gender": personalized_targets.get("gender"),
                    "cultural_background": preferences.cultural_background,
                    "lifestyle": preferences.lifestyle_type
                }
            }
            
            # Override with request preferences if provided
            if plan_request.preferences_override:
                for key, value in plan_request.preferences_override.items():
                    if value is not None:
                        enhanced_preferences[key] = value
            
            # Get user behavior patterns (simplified for now)
            behavior_patterns = self._get_user_behavior_patterns(db, user_id)
            
            # Generate enhanced meal plan
            enhanced_meal_plan = self.enhanced_nutrition_ai.generate_enhanced_meal_plan(
                enhanced_preferences, plan_request, db, behavior_patterns
            )
            
            return enhanced_meal_plan
            
        except Exception as e:
            logger.error(f"Error generating enhanced meal plan: {str(e)}")
            # Fallback to regular meal plan generation
            return self._generate_fallback_meal_plan(db, user_id, plan_request)
    
    def _get_user_behavior_patterns(self, db: Session, user_id: int) -> List[Dict[str, Any]]:
        """Get user behavior patterns for personalization (simplified implementation)"""
        try:
            # This is a simplified implementation - in practice, you'd analyze meal history, ratings, etc.
            # For now, return empty patterns
            return []
        except Exception as e:
            logger.error(f"Error getting user behavior patterns: {e}")
            return []
    
    def _generate_fallback_meal_plan(self, db: Session, user_id: int, plan_request: MealPlanRequest) -> Dict[str, Any]:
        """Generate fallback meal plan when enhanced features fail"""
        try:
            # Use the regular nutrition AI as fallback
            preferences = db.query(UserNutritionPreferences).filter(
                UserNutritionPreferences.user_id == user_id
            ).first()
            
            if not preferences:
                raise Exception("No preferences found")
            
            # Convert to the format expected by regular AI
            prefs_dict = {
                "dietary_preferences": preferences.dietary_preferences or [],
                "allergies": preferences.allergies or [],
                "disliked_ingredients": preferences.disliked_ingredients or [],
                "cuisine_preferences": preferences.cuisine_preferences or [],
                "daily_calorie_target": preferences.daily_calorie_target,
                "protein_target": preferences.protein_target,
                "carbs_target": preferences.carbs_target,
                "fats_target": preferences.fats_target,
                "meals_per_day": preferences.meals_per_day
            }
            
            # Generate using regular AI
            ai_meal_plan = self.nutrition_ai.generate_meal_plan_sequential(prefs_dict, plan_request, db)
            
            # Add fallback metadata
            ai_meal_plan["enhancement_metadata"] = {
                "ai_available": False,
                "fallback_mode": True,
                "enhancement_features_used": []
            }
            
            return ai_meal_plan
            
        except Exception as e:
            logger.error(f"Error in fallback meal plan generation: {e}")
            return {
                "error": "Failed to generate meal plan",
                "enhancement_metadata": {
                    "ai_available": False,
                    "fallback_mode": True,
                    "error": str(e)
                }
            }

    def create_meal_plan(self, db: Session, user_id: int, plan_request: MealPlanRequest, ai_meal_plan: Dict[str, Any]) -> MealPlan:
        """Create meal plan from AI generation with versioning support"""
        try:
            # Check if there's an existing meal plan for this date and type
            existing_plan = db.query(MealPlan).filter(
                and_(
                    MealPlan.user_id == user_id,
                    MealPlan.start_date == plan_request.start_date,
                    MealPlan.plan_type == plan_request.plan_type,
                    MealPlan.is_active == True
                )
            ).first()
            
            # If there's an existing plan, create a new version
            if existing_plan:
                new_plan_id = meal_plan_versioning_service.create_meal_plan_version(
                    db, user_id, existing_plan.id, "regenerate_plan", "New meal plan generated"
                )
                if new_plan_id:
                    # Update the existing plan with new data
                    existing_plan.id = new_plan_id
                    existing_plan.version = meal_plan_versioning_service._increment_version(existing_plan.version)
                    meal_plan = existing_plan
                else:
                    # Fallback to creating new plan
                    import time
                    unique_id = f"mp_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{int(time.time() * 1000) % 10000}"
                    meal_plan = MealPlan(
                        id=unique_id,
                        user_id=user_id,
                        plan_type=plan_request.plan_type,
                        start_date=plan_request.start_date,
                        end_date=plan_request.end_date,
                        version="1.0",
                        generation_strategy={"strategy": "balanced"},
                        ai_model_used="gpt-3.5-turbo"
                    )
            else:
                # Create new meal plan record with unique ID
                import time
                unique_id = f"mp_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{int(time.time() * 1000) % 10000}"
                meal_plan = MealPlan(
                    id=unique_id,
                    user_id=user_id,
                    plan_type=plan_request.plan_type,
                    start_date=plan_request.start_date,
                    end_date=plan_request.end_date,
                    version="1.0",
                    generation_strategy={"strategy": "balanced"},
                    ai_model_used="gpt-3.5-turbo"
                )
            db.add(meal_plan)
            db.flush()
            
            # Create meals and recipes
            # Handle AI output structure - meals can be nested
            meal_plan_data = ai_meal_plan.get("meal_plan", {})
            
            # Handle nested structure from AI
            if "meal_plan" in meal_plan_data and isinstance(meal_plan_data["meal_plan"], list):
                # AI returns: {"meal_plan": {"meal_plan": [{"meals": [...]}]}}
                meals_data = []
                for day_plan in meal_plan_data["meal_plan"]:
                    if "meals" in day_plan:
                        meals_data.extend(day_plan["meals"])
            else:
                # Direct structure: {"meal_plan": {"meals": [...]}}
                meals_data = meal_plan_data.get("meals", [])
            
            for meal_data in meals_data:
                    # Extract nutrition data from recipe if available
                    recipe_data = meal_data.get("recipe", {})
                    nutrition_data = recipe_data.get("nutrition", {})
                    
                    # Create meal
                    meal = MealPlanMeal(
                        meal_plan_id=meal_plan.id,
                        meal_date=plan_request.start_date,  # Use start_date from plan_request
                        meal_type=meal_data["meal_type"],
                        meal_name=meal_data["meal_name"],
                        calories=nutrition_data.get("calories", 0),
                        protein=nutrition_data.get("protein", 0),
                        carbs=nutrition_data.get("carbs", 0),
                        fats=nutrition_data.get("fats", 0)
                    )
                    db.add(meal)
                    db.flush()
                    
                    # Store detailed recipe information in the meal record
                    recipe_data = meal_data.get("recipe", {})
                    if recipe_data:
                        # Store recipe details as JSON in the meal record
                        meal.recipe_details = {
                            "title": recipe_data.get("title", meal_data["meal_name"]),
                            "cuisine": recipe_data.get("cuisine", ""),
                            "prep_time": recipe_data.get("prep_time", 0),
                            "cook_time": recipe_data.get("cook_time", 0),
                            "servings": recipe_data.get("servings", 1),
                            "difficulty": recipe_data.get("difficulty", "easy"),
                            "ingredients": recipe_data.get("ingredients", []),
                            "instructions": recipe_data.get("instructions", []),
                            "dietary_tags": recipe_data.get("dietary_tags", [])
                        }
                        # Also store cuisine directly in the meal record for easy access
                        meal.cuisine = recipe_data.get("cuisine", "")
            
            db.commit()
            db.refresh(meal_plan)
            return meal_plan
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating meal plan: {str(e)}")
            raise
    
    def _create_recipe_from_ai(self, db: Session, recipe_data: Dict[str, Any]) -> Optional[Recipe]:
        """Create recipe from AI-generated data"""
        try:
            recipe = Recipe(
                id=f"r_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(recipe_data.get('title', '')) % 10000}",
                title=recipe_data.get("title", "Generated Recipe"),
                cuisine=recipe_data.get("cuisine", "International"),
                meal_type=recipe_data.get("meal_type", "dinner"),
                servings=recipe_data.get("servings", 2),
                summary=recipe_data.get("summary", ""),
                prep_time=recipe_data.get("prep_time", 15),
                cook_time=recipe_data.get("cook_time", 30),
                difficulty_level=recipe_data.get("difficulty_level", "easy"),
                dietary_tags=recipe_data.get("dietary_tags", []),
                source="ai-generated"
            )
            db.add(recipe)
            db.flush()
            
            # Add ingredients and instructions
            self._add_recipe_ingredients(db, recipe.id, recipe_data.get("ingredients", []))
            self._add_recipe_instructions(db, recipe.id, recipe_data.get("instructions", []))
            
            return recipe
            
        except Exception as e:
            logger.error(f"Error creating recipe from AI: {str(e)}")
            return None
    
    def _add_recipe_ingredients(self, db: Session, recipe_id: str, ingredients_data: List[Dict[str, Any]]):
        """Add ingredients to recipe"""
        for ing_data in ingredients_data:
            # Find or create ingredient
            ingredient = db.query(Ingredient).filter(
                Ingredient.name.ilike(f"%{ing_data.get('name', '')}%")
            ).first()
            
            if not ingredient:
                # Create new ingredient
                ingredient = Ingredient(
                    id=f"ing_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{hash(ing_data.get('name', '')) % 10000}",
                    name=ing_data.get("name", "Unknown Ingredient"),
                    category=self._categorize_ingredient(ing_data.get("name", "")),
                    unit=ing_data.get("unit", "g"),
                    default_quantity=100.0
                )
                db.add(ingredient)
                db.flush()
            
            # Create recipe-ingredient relationship
            from models.nutrition import RecipeIngredient
            recipe_ingredient = RecipeIngredient(
                recipe_id=recipe_id,
                ingredient_id=ingredient.id,
                quantity=ing_data.get("quantity", 0),
                unit=ing_data.get("unit", "g")
            )
            db.add(recipe_ingredient)
    
    def _add_recipe_instructions(self, db: Session, recipe_id: str, instructions_data: List[Dict[str, Any]]):
        """Add instructions to recipe"""
        for i, inst_data in enumerate(instructions_data, 1):
            from models.nutrition import RecipeInstruction
            instruction = RecipeInstruction(
                recipe_id=recipe_id,
                step_number=i,
                step_title=inst_data.get("step_title", f"Step {i}"),
                description=inst_data.get("description", ""),
                ingredients_used=inst_data.get("ingredients_used", []),
                time_required=inst_data.get("time_required")
            )
            db.add(instruction)
    
    def _categorize_ingredient(self, ingredient_name: str) -> str:
        """Categorize ingredient based on name"""
        name_lower = ingredient_name.lower()
        
        if any(word in name_lower for word in ["meat", "chicken", "beef", "pork", "fish", "salmon", "tuna"]):
            return "protein"
        elif any(word in name_lower for word in ["milk", "cheese", "yogurt", "butter", "cream"]):
            return "dairy"
        elif any(word in name_lower for word in ["rice", "pasta", "bread", "flour", "oats", "quinoa"]):
            return "grains"
        elif any(word in name_lower for word in ["tomato", "onion", "carrot", "broccoli", "spinach", "lettuce"]):
            return "vegetables"
        elif any(word in name_lower for word in ["apple", "banana", "orange", "berry", "fruit"]):
            return "fruits"
        elif any(word in name_lower for word in ["oil", "olive", "coconut", "avocado"]):
            return "fats"
        else:
            return "other"
    
    def search_recipes(self, db: Session, search_request: RecipeSearchRequest) -> List[Recipe]:
        """Search recipes with filters"""
        try:
            query = db.query(Recipe).filter(Recipe.is_active == True)
            
            if search_request.query:
                # Use database-level full-text search for better performance
                search_term = search_request.query.strip()
                
                # Handle special search patterns for reviewers
                if search_term.startswith('#') and search_term[1:].isdigit():
                    # Search for exact recipe number (e.g., "#1" -> "recipe_001")
                    recipe_number = search_term[1:].zfill(3)  # Convert "1" to "001"
                    recipe_id_pattern = f"recipe_{recipe_number}"
                    query = query.filter(Recipe.id == recipe_id_pattern)
                elif search_term.startswith('r') and search_term[1:].isdigit():
                    # Search for recipe ID pattern (e.g., "r1" -> "recipe_001")
                    recipe_number = search_term[1:].zfill(3)  # Convert "1" to "001"
                    recipe_id_pattern = f"recipe_{recipe_number}"
                    query = query.filter(Recipe.id == recipe_id_pattern)
                elif search_term.isdigit():
                    # Search for recipe number without prefix (e.g., "1" -> "recipe_001")
                    recipe_number = search_term.zfill(3)  # Convert "1" to "001"
                    recipe_id_pattern = f"recipe_{recipe_number}"
                    query = query.filter(Recipe.id == recipe_id_pattern)
                elif search_term.startswith('range:'):
                    # Range search for reviewers (e.g., "range:1-10", "range:50-100")
                    try:
                        range_part = search_term.replace('range:', '').strip()
                        if '-' in range_part:
                            start_num, end_num = range_part.split('-')
                            start_num = int(start_num.strip())
                            end_num = int(end_num.strip())
                            
                            # Create list of recipe IDs in range
                            recipe_ids = [f"recipe_{str(i).zfill(3)}" for i in range(start_num, end_num + 1)]
                            query = query.filter(Recipe.id.in_(recipe_ids))
                        else:
                            # Single number range (e.g., "range:5" -> recipes 1-5)
                            end_num = int(range_part.strip())
                            recipe_ids = [f"recipe_{str(i).zfill(3)}" for i in range(1, end_num + 1)]
                            query = query.filter(Recipe.id.in_(recipe_ids))
                    except (ValueError, IndexError):
                        # If range parsing fails, fall back to regular search
                        query = query.filter(
                            or_(
                                Recipe.title.ilike(f"%{search_term}%"),
                                Recipe.summary.ilike(f"%{search_term}%"),
                                Recipe.id.ilike(f"%{search_term}%")
                            )
                        )
                elif search_term.startswith('last:'):
                    # Get last N recipes (e.g., "last:10" -> last 10 recipes)
                    try:
                        count = int(search_term.replace('last:', '').strip())
                        # For last: queries, we need to get the total count of all recipes
                        # and then apply pagination normally
                        query = query.order_by(Recipe.id.desc())
                    except ValueError:
                        # If parsing fails, fall back to regular search
                        query = query.filter(
                            or_(
                                Recipe.title.ilike(f"%{search_term}%"),
                                Recipe.summary.ilike(f"%{search_term}%"),
                                Recipe.id.ilike(f"%{search_term}%")
                            )
                        )
                elif search_term.startswith('first:'):
                    # Get first N recipes (e.g., "first:10" -> first 10 recipes)
                    try:
                        count = int(search_term.replace('first:', '').strip())
                        # For first: queries, we need to get the total count of all recipes
                        # and then apply pagination normally
                        query = query.order_by(Recipe.id.asc())
                    except ValueError:
                        # If parsing fails, fall back to regular search
                        query = query.filter(
                            or_(
                                Recipe.title.ilike(f"%{search_term}%"),
                                Recipe.summary.ilike(f"%{search_term}%"),
                                Recipe.id.ilike(f"%{search_term}%")
                            )
                        )
                else:
                    # Use vector similarity search for semantic search
                    similar_recipes = self._vector_similarity_search(search_term, db, limit=50)
                    if similar_recipes:
                        # Get recipe IDs from similarity search
                        similar_recipe_ids = [recipe['id'] for recipe in similar_recipes]
                        query = query.filter(Recipe.id.in_(similar_recipe_ids))
                    else:
                        # Fallback to regular text search if vector search fails
                        query = query.filter(
                            or_(
                                Recipe.title.ilike(f"%{search_term}%"),
                                Recipe.summary.ilike(f"%{search_term}%"),
                                Recipe.id.ilike(f"%{search_term}%")
                            )
                        )
            
            if search_request.cuisine:
                query = query.filter(Recipe.cuisine.ilike(f"%{search_request.cuisine}%"))
            
            if search_request.meal_type:
                query = query.filter(Recipe.meal_type == search_request.meal_type)
            
            if search_request.dietary_tags:
                for tag in search_request.dietary_tags:
                    query = query.filter(Recipe.dietary_tags.contains(tag))
            
            # Apply user preferences filtering
            if search_request.user_preferences:
                prefs = search_request.user_preferences
                
                # Intelligent dietary preferences filtering
                if prefs.dietary_preferences:
                    dietary_conditions = []
                    
                    # Handle hierarchical dietary preferences intelligently
                    if 'vegan' in prefs.dietary_preferences:
                        # If user is vegan, only show vegan recipes (most restrictive)
                        dietary_conditions.append(Recipe.dietary_tags.contains(['vegan']))
                    elif 'vegetarian' in prefs.dietary_preferences:
                        # If user is vegetarian (but not vegan), show both vegetarian AND vegan recipes
                        # because vegan recipes are also suitable for vegetarians
                        dietary_conditions.append(
                            or_(
                                Recipe.dietary_tags.contains(['vegetarian']),
                                Recipe.dietary_tags.contains(['vegan'])
                            )
                        )
                    
                    # Handle other dietary preferences intelligently
                    other_prefs = [p for p in prefs.dietary_preferences if p not in ['vegan', 'vegetarian']]
                    
                    # Handle gluten-free hierarchy
                    if 'gluten-free' in other_prefs:
                        dietary_conditions.append(Recipe.dietary_tags.contains(['gluten-free']))
                        other_prefs.remove('gluten-free')
                    
                    # Handle dairy-free hierarchy  
                    if 'dairy-free' in other_prefs:
                        dietary_conditions.append(Recipe.dietary_tags.contains(['dairy-free']))
                        other_prefs.remove('dairy-free')
                    
                    # Handle nut-free hierarchy
                    if 'nut-free' in other_prefs:
                        dietary_conditions.append(Recipe.dietary_tags.contains(['nut-free']))
                        other_prefs.remove('nut-free')
                    
                    # Handle soy-free hierarchy
                    if 'soy-free' in other_prefs:
                        dietary_conditions.append(Recipe.dietary_tags.contains(['soy-free']))
                        other_prefs.remove('soy-free')
                    
                    # Handle remaining preferences
                    for pref in other_prefs:
                        dietary_conditions.append(Recipe.dietary_tags.contains([pref]))
                    
                    if dietary_conditions:
                        query = query.filter(or_(*dietary_conditions))
                
                # Filter out recipes with user's allergies (exclude recipes containing allergens)
                if prefs.allergies:
                    for allergy in prefs.allergies:
                        # Check if recipe contains this allergen
                        allergen_tag = f"contains-{allergy}"
                        query = query.filter(~Recipe.dietary_tags.contains([allergen_tag]))
                
                # Filter out recipes with disliked ingredients
                if prefs.disliked_ingredients:
                    for ingredient in prefs.disliked_ingredients:
                        # This would require more complex ingredient matching
                        # For now, we'll do a simple title/summary search
                        query = query.filter(
                            and_(
                                ~Recipe.title.ilike(f"%{ingredient}%"),
                                ~Recipe.summary.ilike(f"%{ingredient}%")
                            )
                        )
            
            if search_request.difficulty_level:
                query = query.filter(Recipe.difficulty_level == search_request.difficulty_level)
            
            if search_request.max_prep_time:
                query = query.filter(Recipe.prep_time <= search_request.max_prep_time)
            
            # Apply micronutrient filters
            if search_request.micronutrient_filters and search_request.micronutrient_filters.nutrients:
                micronutrient_filters = search_request.micronutrient_filters
                
                # For now, we'll apply basic micronutrient filtering
                # In a full implementation, you'd join with ingredient micronutrient data
                for nutrient in micronutrient_filters.nutrients:
                    min_value = micronutrient_filters.min_values.get(nutrient, 0)
                    max_value = micronutrient_filters.max_values.get(nutrient, float('inf'))
                    
                    # This is a simplified approach - in reality you'd need to:
                    # 1. Join with RecipeIngredient -> Ingredient tables
                    # 2. Sum up micronutrient values per recipe
                    # 3. Filter based on total micronutrient content
                    
                    # For demonstration, we'll filter by recipe ID patterns
                    # (This is just to show the structure - real implementation would be more complex)
                    if nutrient == 'vitamin_d' and min_value > 0:
                        # Example: prioritize recipes with "salmon" or "fish" in title
                        query = query.filter(
                            or_(
                                Recipe.title.ilike('%salmon%'),
                                Recipe.title.ilike('%fish%'),
                                Recipe.title.ilike('%tuna%')
                            )
                        )
                    elif nutrient == 'iron' and min_value > 0:
                        # Example: prioritize recipes with "beef" or "spinach" in title
                        query = query.filter(
                            or_(
                                Recipe.title.ilike('%beef%'),
                                Recipe.title.ilike('%spinach%'),
                                Recipe.title.ilike('%lentil%')
                            )
                        )
                    elif nutrient == 'calcium' and min_value > 0:
                        # Example: prioritize recipes with "cheese" or "milk" in title
                        query = query.filter(
                            or_(
                                Recipe.title.ilike('%cheese%'),
                                Recipe.title.ilike('%milk%'),
                                Recipe.title.ilike('%yogurt%')
                            )
                        )
            
            # Apply sorting if specified
            if hasattr(search_request, 'sort_by') and search_request.sort_by:
                sort_field = search_request.sort_by
                sort_order = getattr(search_request, 'sort_order', 'asc')
                
                if sort_field == 'title':
                    query = query.order_by(Recipe.title.asc() if sort_order == 'asc' else Recipe.title.desc())
                elif sort_field == 'calories':
                    # For now, we'll sort by ID since we don't have calculated calories in the database
                    # The nutritional values will be calculated in _calculate_recipe_nutrition
                    query = query.order_by(Recipe.id.asc() if sort_order == 'asc' else Recipe.id.desc())
                elif sort_field == 'protein':
                    # For now, we'll sort by ID since we don't have calculated protein in the database
                    # The nutritional values will be calculated in _calculate_recipe_nutrition
                    query = query.order_by(Recipe.id.asc() if sort_order == 'asc' else Recipe.id.desc())
                elif sort_field == 'prep_time':
                    # prep_time sorting is handled in post-query sorting
                    pass
                elif sort_field == 'difficulty':
                    # Order by difficulty: easy=1, medium=2, hard=3
                    difficulty_order = case(
                        (Recipe.difficulty_level == 'easy', 1),
                        (Recipe.difficulty_level == 'medium', 2),
                        (Recipe.difficulty_level == 'hard', 3),
                        else_=4
                    )
                    query = query.order_by(difficulty_order.asc() if sort_order == 'asc' else difficulty_order.desc())
                elif sort_field == 'id':
                    query = query.order_by(Recipe.id.asc() if sort_order == 'asc' else Recipe.id.desc())
                else:
                    # Default sorting
                    query = query.order_by(Recipe.id.asc())
            else:
                # Default sorting: order by recipe ID ascending (recipe_001, recipe_002, etc.)
                query = query.order_by(Recipe.id.asc())
            
            # Get ALL recipes first (no pagination yet)
            all_recipes = query.all()
            print(f"🔍 DATABASE SEARCH: Found {len(all_recipes)} recipes")
            
            # Calculate nutritional data for each recipe
            for recipe in all_recipes:
                self._calculate_recipe_nutrition(recipe)
            
            # Convert to response format
            all_recipe_responses = [self._convert_recipe_to_response(recipe) for recipe in all_recipes]
            
            # Apply sorting to ALL recipes BEFORE pagination
            if hasattr(search_request, 'sort_by') and search_request.sort_by:
                sort_field = search_request.sort_by
                sort_order = getattr(search_request, 'sort_order', 'asc')
                reverse = sort_order.lower() == 'desc'
                
                if sort_field in ['calories', 'protein', 'carbs', 'fats']:
                    # Sort by nutritional values
                    def get_nutritional_value(recipe):
                        if sort_field == 'calories':
                            return recipe.get('calculated_calories', 0)
                        elif sort_field == 'protein':
                            return recipe.get('calculated_protein', 0)
                        elif sort_field == 'carbs':
                            return recipe.get('calculated_carbs', 0)
                        elif sort_field == 'fats':
                            return recipe.get('calculated_fats', 0)
                        return 0
                    all_recipe_responses.sort(key=get_nutritional_value, reverse=reverse)
                    
                elif sort_field == 'prep_time':
                    # Sort by prep_time - ensure it's treated as integer
                    print(f"🔍 SORTING BY PREP_TIME: {sort_order}")
                    print(f"🔍 BEFORE SORTING: {[r.get('title', 'Unknown') + ': ' + str(r.get('prep_time', 0)) + 'min' for r in all_recipe_responses[:5]]}")
                    def get_prep_time_value(recipe):
                        prep_time = recipe.get('prep_time', 0)
                        # Ensure it's an integer for proper sorting
                        try:
                            return int(prep_time)
                        except (ValueError, TypeError):
                            return 0
                    all_recipe_responses.sort(key=get_prep_time_value, reverse=reverse)
                    print(f"🔍 AFTER SORTING: {[r.get('title', 'Unknown') + ': ' + str(r.get('prep_time', 0)) + 'min' for r in all_recipe_responses[:5]]}")
            
            # Now apply pagination to the sorted results
            offset = (search_request.page - 1) * search_request.limit
            end_idx = offset + search_request.limit
            recipe_responses = all_recipe_responses[offset:end_idx]
            
            # Calculate pagination info - use the same query but without limit/offset
            count_query = db.query(Recipe).filter(Recipe.is_active == True)
            
            # Apply the same filters to count query
            if search_request.query:
                search_term = search_request.query.strip()
                if search_term.startswith('#') and search_term[1:].isdigit():
                    recipe_number = search_term[1:].zfill(3)
                    recipe_id_pattern = f"recipe_{recipe_number}"
                    count_query = count_query.filter(Recipe.id == recipe_id_pattern)
                elif search_term.startswith('r') and search_term[1:].isdigit():
                    recipe_number = search_term[1:].zfill(3)
                    recipe_id_pattern = f"recipe_{recipe_number}"
                    count_query = count_query.filter(Recipe.id == recipe_id_pattern)
                elif search_term.isdigit():
                    recipe_number = search_term.zfill(3)
                    recipe_id_pattern = f"recipe_{recipe_number}"
                    count_query = count_query.filter(Recipe.id == recipe_id_pattern)
                elif search_term.startswith('range:'):
                    try:
                        range_part = search_term.replace('range:', '').strip()
                        if '-' in range_part:
                            start_num, end_num = range_part.split('-')
                            start_num = int(start_num.strip())
                            end_num = int(end_num.strip())
                            recipe_ids = [f"recipe_{str(i).zfill(3)}" for i in range(start_num, end_num + 1)]
                            count_query = count_query.filter(Recipe.id.in_(recipe_ids))
                        else:
                            end_num = int(range_part.strip())
                            recipe_ids = [f"recipe_{str(i).zfill(3)}" for i in range(1, end_num + 1)]
                            count_query = count_query.filter(Recipe.id.in_(recipe_ids))
                    except (ValueError, IndexError):
                        count_query = count_query.filter(
                            or_(
                                Recipe.title.ilike(f"%{search_term}%"),
                                Recipe.summary.ilike(f"%{search_term}%"),
                                Recipe.id.ilike(f"%{search_term}%")
                            )
                        )
                elif search_term.startswith('last:'):
                    try:
                        count = int(search_term.replace('last:', '').strip())
                        # For last: queries, we need to get the total count of all recipes
                        count_query = db.query(Recipe).filter(Recipe.is_active == True)
                    except ValueError:
                        count_query = count_query.filter(
                            or_(
                                Recipe.title.ilike(f"%{search_term}%"),
                                Recipe.summary.ilike(f"%{search_term}%"),
                                Recipe.id.ilike(f"%{search_term}%")
                            )
                        )
                elif search_term.startswith('first:'):
                    try:
                        count = int(search_term.replace('first:', '').strip())
                        # For first: queries, we need to get the total count of all recipes
                        count_query = db.query(Recipe).filter(Recipe.is_active == True)
                    except ValueError:
                        count_query = count_query.filter(
                            or_(
                                Recipe.title.ilike(f"%{search_term}%"),
                                Recipe.summary.ilike(f"%{search_term}%"),
                                Recipe.id.ilike(f"%{search_term}%")
                            )
                        )
                else:
                    count_query = count_query.filter(
                        or_(
                            Recipe.title.ilike(f"%{search_term}%"),
                            Recipe.summary.ilike(f"%{search_term}%"),
                            Recipe.id.ilike(f"%{search_term}%")
                        )
                    )
            
            # Apply other filters to count query
            if search_request.cuisine:
                count_query = count_query.filter(Recipe.cuisine.ilike(f"%{search_request.cuisine}%"))
            if search_request.meal_type:
                count_query = count_query.filter(Recipe.meal_type == search_request.meal_type)
            if search_request.dietary_tags:
                for tag in search_request.dietary_tags:
                    count_query = count_query.filter(Recipe.dietary_tags.contains([tag]))
            if search_request.difficulty_level:
                count_query = count_query.filter(Recipe.difficulty_level == search_request.difficulty_level)
            if search_request.max_prep_time:
                count_query = count_query.filter(Recipe.prep_time <= search_request.max_prep_time)
            
            total_count = count_query.count()
            total_pages = (total_count + search_request.limit - 1) // search_request.limit
            
            return {
                "recipes": recipe_responses,
                "total": total_count,
                "pages": total_pages,
                "current_page": search_request.page,
                "per_page": search_request.limit
            }
            
        except Exception as e:
            logger.error(f"Error searching recipes: {str(e)}")
            return []
    
    def _meets_micronutrient_criteria(self, recipe: Recipe, search_request: RecipeSearchRequest) -> bool:
        """Check if recipe meets micronutrient filter criteria"""
        try:
            # Check individual micronutrient filters
            if search_request.min_vitamin_d and getattr(recipe, 'calculated_vitamin_d', 0) < search_request.min_vitamin_d:
                return False
            if search_request.min_vitamin_c and getattr(recipe, 'calculated_vitamin_c', 0) < search_request.min_vitamin_c:
                return False
            if search_request.min_iron and getattr(recipe, 'calculated_iron', 0) < search_request.min_iron:
                return False
            if search_request.min_calcium and getattr(recipe, 'calculated_calcium', 0) < search_request.min_calcium:
                return False
            if search_request.min_magnesium and getattr(recipe, 'calculated_magnesium', 0) < search_request.min_magnesium:
                return False
            if search_request.min_zinc and getattr(recipe, 'calculated_zinc', 0) < search_request.min_zinc:
                return False
            
            # Check custom micronutrient filters
            if search_request.micronutrient_filters:
                for nutrient, min_value in search_request.micronutrient_filters.items():
                    calculated_value = getattr(recipe, f'calculated_{nutrient}', 0)
                    if calculated_value < min_value:
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking micronutrient criteria: {str(e)}")
            return True  # Default to including recipe if check fails
    
    def _calculate_recipe_nutrition(self, recipe: Recipe) -> None:
        """Calculate nutritional data for a recipe based on its ingredients"""
        try:
            if not hasattr(recipe, 'ingredients') or not recipe.ingredients:
                return
            
            total_calories = 0
            total_protein = 0
            total_carbs = 0
            total_fats = 0
            total_fiber = 0
            total_sugar = 0
            total_sodium = 0
            
            for ri in recipe.ingredients:
                if ri.ingredient:
                    # Calculate nutrition per 100g of ingredient
                    quantity = ri.quantity or 0
                    calories_per_100g = ri.ingredient.calories or 0
                    protein_per_100g = ri.ingredient.protein or 0
                    carbs_per_100g = ri.ingredient.carbs or 0
                    fats_per_100g = ri.ingredient.fats or 0
                    fiber_per_100g = ri.ingredient.fiber or 0
                    sugar_per_100g = ri.ingredient.sugar or 0
                    sodium_per_100g = ri.ingredient.sodium or 0
                    
                    # Calculate total nutrition for this ingredient
                    total_calories += (calories_per_100g * quantity) / 100
                    total_protein += (protein_per_100g * quantity) / 100
                    total_carbs += (carbs_per_100g * quantity) / 100
                    total_fats += (fats_per_100g * quantity) / 100
                    total_fiber += (fiber_per_100g * quantity) / 100
                    total_sugar += (sugar_per_100g * quantity) / 100
                    total_sodium += (sodium_per_100g * quantity) / 100
            
            # Add calculated nutrition as attributes to the recipe object
            recipe.calculated_calories = round(total_calories, 1)
            recipe.calculated_protein = round(total_protein, 1)
            recipe.calculated_carbs = round(total_carbs, 1)
            recipe.calculated_fats = round(total_fats, 1)
            recipe.calculated_fiber = round(total_fiber, 1)
            recipe.calculated_sugar = round(total_sugar, 1)
            recipe.calculated_sodium = round(total_sodium, 1)
            
            # Add ingredients and instructions arrays as new attributes (not overwriting SQLAlchemy relationships)
            # Format ingredients more naturally
            ingredients_formatted = []
            for ri in recipe.ingredients:
                if ri.ingredient:
                    # Convert grams to more natural units for common ingredients
                    name = ri.ingredient.name.lower()
                    quantity = ri.quantity
                    unit = ri.unit or 'g'
                    
                    # Convert to more natural units
                    if 'egg' in name and unit == 'g':
                        # 1 large egg ≈ 50g, so convert to egg count
                        egg_count = quantity / 50
                        if egg_count >= 1:
                            ingredients_formatted.append(f"{int(egg_count)} {ri.ingredient.name}")
                        else:
                            ingredients_formatted.append(f"{ri.ingredient.name}: {quantity}g")
                    elif unit == 'g' and quantity >= 1000:
                        # Convert large quantities to kg
                        kg = quantity / 1000
                        ingredients_formatted.append(f"{kg:.1f}kg {ri.ingredient.name}")
                    elif unit == 'ml' and quantity >= 1000:
                        # Convert large quantities to liters
                        liters = quantity / 1000
                        ingredients_formatted.append(f"{liters:.1f}L {ri.ingredient.name}")
                    else:
                        # Use original format for other ingredients with reasonable precision
                        if unit == 'g':
                            # Round to 1 decimal place for grams
                            ingredients_formatted.append(f"{ri.ingredient.name}: {quantity:.1f}g")
                        elif unit == 'ml':
                            # Round to 1 decimal place for milliliters
                            ingredients_formatted.append(f"{ri.ingredient.name}: {quantity:.1f}ml")
                        else:
                            # Round to 1 decimal place for other units
                            ingredients_formatted.append(f"{ri.ingredient.name}: {quantity:.1f}{unit}")
            
            recipe.ingredients_list = ingredients_formatted
            recipe.instructions_list = [inst.description for inst in recipe.instructions]
            
        except Exception as e:
            logger.error(f"Error calculating recipe nutrition: {str(e)}")
            # Set default values if calculation fails
            recipe.calculated_calories = 0
            recipe.calculated_protein = 0
            recipe.calculated_carbs = 0
            recipe.calculated_fats = 0
            recipe.calculated_fiber = 0
            recipe.calculated_sugar = 0
            recipe.calculated_sodium = 0
            recipe.ingredients_list = []
            recipe.instructions_list = []
    
    def create_shopping_list(self, db: Session, user_id: int, shopping_list_data: ShoppingListCreate) -> ShoppingList:
        """Create shopping list from meal plan or manual items"""
        try:
            shopping_list = ShoppingList(
                id=f"sl_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                user_id=user_id,
                list_name=shopping_list_data.list_name,
                meal_plan_id=shopping_list_data.meal_plan_id
            )
            db.add(shopping_list)
            db.flush()
            
            # Add items
            for item_data in shopping_list_data.items:
                item = ShoppingListItem(
                    shopping_list_id=shopping_list.id,
                    ingredient_id=item_data.ingredient_id,
                    quantity=item_data.quantity,
                    unit=item_data.unit,
                    category=self._categorize_ingredient_by_id(db, item_data.ingredient_id),
                    notes=item_data.notes
                )
                db.add(item)
            
            db.commit()
            db.refresh(shopping_list)
            return shopping_list
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error creating shopping list: {str(e)}")
            raise
    
    def _convert_meal_plan_to_response(self, meal_plan: MealPlan) -> 'MealPlanResponse':
        """Convert MealPlan model to response format"""
        from schemas.nutrition import MealPlanResponse, NutritionalInfo
        
        # Convert meals to dictionaries
        meals_data = []
        for meal in meal_plan.meals:
            meal_data = {
                "id": meal.id,
                "meal_type": meal.meal_type,
                "meal_name": meal.meal_name,
                "calories": meal.calories,
                "protein": meal.protein,
                "carbs": meal.carbs,
                "fats": meal.fats
            }
            
            # Add recipe details if available
            if meal.recipe_details:
                recipe_details = meal.recipe_details
                meal_data.update({
                    "cuisine": recipe_details.get("cuisine", meal.cuisine or ""),
                    "prep_time": recipe_details.get("prep_time", 0),
                    "cook_time": recipe_details.get("cook_time", 0),
                    "difficulty": recipe_details.get("difficulty", "easy"),
                    "ingredients": recipe_details.get("ingredients", []),
                    "instructions": recipe_details.get("instructions", []),
                    "dietary_tags": recipe_details.get("dietary_tags", [])
                })
            elif meal.cuisine:
                meal_data["cuisine"] = meal.cuisine
            
            meals_data.append(meal_data)
        
        # Calculate total nutrition
        total_calories = sum(meal.calories for meal in meal_plan.meals)
        total_protein = sum(meal.protein for meal in meal_plan.meals)
        total_carbs = sum(meal.carbs for meal in meal_plan.meals)
        total_fats = sum(meal.fats for meal in meal_plan.meals)
        
        total_nutrition = NutritionalInfo(
            calories=total_calories,
            protein=total_protein,
            carbs=total_carbs,
            fats=total_fats,
            fiber=0.0,  # Not tracked in meals
            sugar=0.0,  # Not tracked in meals
            sodium=0.0  # Not tracked in meals
        )
        
        return MealPlanResponse(
            id=meal_plan.id,
            user_id=meal_plan.user_id,
            plan_type=meal_plan.plan_type,
            start_date=meal_plan.start_date,
            end_date=meal_plan.end_date,
            version=meal_plan.version,
            is_active=meal_plan.is_active,
            meals=meals_data,
            total_nutrition=total_nutrition,
            created_at=meal_plan.created_at,
            updated_at=meal_plan.updated_at
        )

    def _vector_similarity_search(self, query_text: str, db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Perform vector similarity search using recipe embeddings"""
        try:
            # Try to import required libraries
            try:
                from sklearn.feature_extraction.text import TfidfVectorizer
                from sklearn.metrics.pairwise import cosine_similarity
                import numpy as np
            except ImportError:
                logger.warning("scikit-learn not available for vector search")
                return []
            
            # Get all recipes with embeddings
            recipes = db.query(Recipe).filter(
                Recipe.is_active == True,
                Recipe.embedding.isnot(None)
            ).all()
            
            if not recipes:
                return []
            
            # Create TF-IDF vectorizer for query
            vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
            
            # Prepare recipe texts and embeddings
            recipe_texts = []
            recipe_embeddings = []
            recipe_data = []
            
            for recipe in recipes:
                # Create recipe text for embedding
                recipe_text = self._create_recipe_text_for_embedding(recipe)
                recipe_texts.append(recipe_text)
                
                # Get stored embedding
                if recipe.embedding:
                    recipe_embeddings.append(np.array(recipe.embedding))
                    recipe_data.append({
                        'id': recipe.id,
                        'title': recipe.title,
                        'cuisine': recipe.cuisine,
                        'meal_type': recipe.meal_type,
                        'similarity': 0.0
                    })
            
            if not recipe_embeddings:
                return []
            
            # Fit vectorizer on all recipe texts
            vectorizer.fit(recipe_texts)
            
            # Transform query
            query_embedding = vectorizer.transform([query_text]).toarray()[0]
            
            # Calculate similarities
            similarities = []
            for i, recipe_embedding in enumerate(recipe_embeddings):
                # Ensure embeddings have same dimension
                min_dim = min(len(query_embedding), len(recipe_embedding))
                query_vec = query_embedding[:min_dim]
                recipe_vec = recipe_embedding[:min_dim]
                
                # Calculate cosine similarity
                similarity = np.dot(query_vec, recipe_vec) / (
                    np.linalg.norm(query_vec) * np.linalg.norm(recipe_vec) + 1e-8
                )
                
                recipe_data[i]['similarity'] = float(similarity)
                similarities.append(recipe_data[i])
            
            # Sort by similarity and return top results
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            return similarities[:limit]
            
        except Exception as e:
            logger.error(f"Error in vector similarity search: {e}")
            return []
    
    def _create_recipe_text_for_embedding(self, recipe: Recipe) -> str:
        """Create text representation of recipe for embedding (same as in embedding script)"""
        text_parts = []
        
        # Basic recipe info
        text_parts.append(f"Title: {recipe.title}")
        text_parts.append(f"Cuisine: {recipe.cuisine}")
        text_parts.append(f"Meal type: {recipe.meal_type}")
        text_parts.append(f"Difficulty: {recipe.difficulty_level}")
        
        # Summary
        if recipe.summary:
            text_parts.append(f"Summary: {recipe.summary}")
        
        # Dietary tags
        if recipe.dietary_tags:
            dietary_tags = [tag for tag in recipe.dietary_tags if not tag.startswith('contains-')]
            if dietary_tags:
                text_parts.append(f"Dietary: {', '.join(dietary_tags)}")
        
        # Allergens
        if recipe.dietary_tags:
            allergens = [tag.replace('contains-', '') for tag in recipe.dietary_tags if tag.startswith('contains-')]
            if allergens:
                text_parts.append(f"Contains: {', '.join(allergens)}")
        
        # Ingredients
        if recipe.ingredients:
            ingredient_names = []
            for ingredient in recipe.ingredients:
                if hasattr(ingredient, 'ingredient') and ingredient.ingredient:
                    ingredient_names.append(ingredient.ingredient.name)
                elif hasattr(ingredient, 'name'):
                    ingredient_names.append(ingredient.name)
            
            if ingredient_names:
                text_parts.append(f"Ingredients: {', '.join(ingredient_names)}")
        
        # Instructions (first few steps)
        if recipe.instructions:
            instruction_texts = []
            for instruction in recipe.instructions[:3]:  # First 3 steps
                if hasattr(instruction, 'description'):
                    instruction_texts.append(instruction.description)
                elif hasattr(instruction, 'step_description'):
                    instruction_texts.append(instruction.step_description)
            
            if instruction_texts:
                text_parts.append(f"Instructions: {' '.join(instruction_texts)}")
        
        # Nutrition info
        if hasattr(recipe, 'per_serving_calories') and recipe.per_serving_calories:
            text_parts.append(f"Calories per serving: {recipe.per_serving_calories}")
        
        if hasattr(recipe, 'per_serving_protein') and recipe.per_serving_protein:
            text_parts.append(f"Protein per serving: {recipe.per_serving_protein}g")
        
        # Cooking info
        text_parts.append(f"Prep time: {recipe.prep_time} minutes")
        text_parts.append(f"Cook time: {recipe.cook_time} minutes")
        text_parts.append(f"Servings: {recipe.servings}")
        
        return " | ".join(text_parts)

    def _convert_recipe_to_response(self, recipe: Recipe) -> dict:
        """Convert Recipe model to response format with calculated nutritional data"""
        # Calculate nutrition if not already done
        self._calculate_recipe_nutrition(recipe)
        
        return {
            "id": recipe.id,
            "title": recipe.title,
            "cuisine": recipe.cuisine,
            "meal_type": recipe.meal_type,
            "servings": recipe.servings,
            "summary": recipe.summary,
            "prep_time": recipe.prep_time,
            "cook_time": recipe.cook_time,
            "difficulty_level": recipe.difficulty_level,
            "dietary_tags": recipe.dietary_tags or [],
            "source": recipe.source,
            "image_url": recipe.image_url,
            # Per-serving nutrition (for daily logging)
            "per_serving_calories": getattr(recipe, 'per_serving_calories', 0),
            "per_serving_protein": getattr(recipe, 'per_serving_protein', 0),
            "per_serving_carbs": getattr(recipe, 'per_serving_carbs', 0),
            "per_serving_fats": getattr(recipe, 'per_serving_fat', 0),
            "per_serving_sodium": getattr(recipe, 'per_serving_sodium', 0),
            # Total recipe nutrition (for full recipe display)
            "total_calories": getattr(recipe, 'total_calories', 0),
            "total_protein": getattr(recipe, 'total_protein', 0),
            "total_carbs": getattr(recipe, 'total_carbs', 0),
            "total_fats": getattr(recipe, 'total_fat', 0),
            "total_sodium": getattr(recipe, 'total_sodium', 0),
            # Legacy calculated fields (for backward compatibility)
            "calculated_calories": getattr(recipe, 'total_calories', 0),
            "calculated_protein": getattr(recipe, 'total_protein', 0),
            "calculated_carbs": getattr(recipe, 'total_carbs', 0),
            "calculated_fats": getattr(recipe, 'total_fat', 0),
            "calculated_fiber": getattr(recipe, 'calculated_fiber', 0),
            "calculated_sugar": getattr(recipe, 'calculated_sugar', 0),
            "calculated_sodium": getattr(recipe, 'total_sodium', 0),
            "ingredients_list": getattr(recipe, 'ingredients_list', []),
            "instructions_list": getattr(recipe, 'instructions_list', []),
            "created_at": recipe.created_at,
            "updated_at": recipe.updated_at
        }

    def _convert_shopping_list_to_response(self, shopping_list: ShoppingList) -> 'ShoppingListResponse':
        """Convert ShoppingList model to response format with calculated fields"""
        from schemas.nutrition import ShoppingListResponse
        
        total_items = len(shopping_list.items)
        purchased_items = sum(1 for item in shopping_list.items if item.is_purchased)
        
        def ensure_category(item):
            if getattr(item, 'category', None):
                return item.category
            # Fallback categorization by ingredient name if available
            name = getattr(item, 'name', None)
            if not name and getattr(item, 'ingredient', None):
                name = getattr(item.ingredient, 'label', None) or getattr(item.ingredient, 'name', None)
            name_l = (name or '').lower()
            if any(k in name_l for k in ("milk", "cheese", "yogurt", "butter")):
                return "Dairy"
            if any(k in name_l for k in ("apple", "banana", "berry", "tomato", "lettuce", "onion", "pepper", "cucumber", "spinach")):
                return "Produce"
            if any(k in name_l for k in ("chicken", "beef", "pork", "turkey", "fish", "tofu", "egg")):
                return "Proteins"
            if any(k in name_l for k in ("rice", "pasta", "bread", "oats", "quinoa", "flour")):
                return "Grains"
            if any(k in name_l for k in ("oil", "vinegar", "salt", "sugar", "spice", "herb")):
                return "Pantry"
            return "Other"

        return ShoppingListResponse(
            id=shopping_list.id,
            user_id=shopping_list.user_id,
            list_name=shopping_list.list_name,
            meal_plan_id=shopping_list.meal_plan_id,
            is_active=shopping_list.is_active,
            items=[
                {
                    "id": item.id,
                    "ingredient_id": item.ingredient_id,
                    "quantity": item.quantity,
                    "unit": item.unit,
                    "category": ensure_category(item),
                    "is_purchased": item.is_purchased,
                    "notes": item.notes
                }
                for item in shopping_list.items
            ],
            total_items=total_items,
            purchased_items=purchased_items,
            created_at=shopping_list.created_at,
            updated_at=shopping_list.updated_at
        )

    def update_shopping_list_item(self, db: Session, user_id: int, list_id: str, item_id: int, *,
                                  quantity: Optional[float] = None,
                                  unit: Optional[str] = None,
                                  notes: Optional[str] = None,
                                  is_purchased: Optional[bool] = None) -> ShoppingList:
        """Update a shopping list item and return updated list."""
        sl = db.query(ShoppingList).filter(ShoppingList.id == list_id, ShoppingList.user_id == user_id).first()
        if not sl:
            raise ValueError("Shopping list not found")
        item = next((i for i in sl.items if i.id == item_id), None)
        if not item:
            raise ValueError("Shopping list item not found")
        if quantity is not None:
            item.quantity = quantity
        if unit is not None:
            item.unit = unit
        if notes is not None:
            item.notes = notes
        if is_purchased is not None:
            item.is_purchased = is_purchased
        db.flush()
        db.refresh(sl)
        return sl

    def delete_shopping_list_item(self, db: Session, user_id: int, list_id: str, item_id: int) -> ShoppingList:
        """Remove an item from the shopping list and return updated list."""
        sl = db.query(ShoppingList).filter(ShoppingList.id == list_id, ShoppingList.user_id == user_id).first()
        if not sl:
            raise ValueError("Shopping list not found")
        # Remove via relationship
        to_keep = [i for i in sl.items if i.id != item_id]
        if len(to_keep) == len(sl.items):
            raise ValueError("Shopping list item not found")
        sl.items = to_keep
        db.flush()
        db.refresh(sl)
        return sl
    
    def _categorize_ingredient_by_id(self, db: Session, ingredient_id: str) -> str:
        """Get ingredient category by ID"""
        ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
        return ingredient.category if ingredient else "other"
    
    def get_nutritional_analysis(self, db: Session, user_id: int, start_date: date, end_date: date, analysis_type: str) -> Dict[str, Any]:
        """Get comprehensive nutritional analysis"""
        try:
            # Get nutritional logs for the period
            logs = db.query(NutritionalLog).filter(
                NutritionalLog.user_id == user_id,
                NutritionalLog.log_date >= start_date,
                NutritionalLog.log_date <= end_date
            ).all()
            
            # Calculate totals
            total_calories = sum(log.calories for log in logs)
            total_protein = sum(log.protein for log in logs)
            total_carbs = sum(log.carbs for log in logs)
            total_fats = sum(log.fats for log in logs)
            
            # Get user targets
            preferences = db.query(UserNutritionPreferences).filter(
                UserNutritionPreferences.user_id == user_id
            ).first()
            
            # Calculate days in the period
            days_in_period = (end_date - start_date).days + 1
            
            # Count days with actual logged data
            logged_dates = set(log.log_date for log in logs)
            days_with_data = len(logged_dates)
            missing_days = days_in_period - days_with_data
            
            # Use actual days in period for target calculation
            targets = {
                "calories": (preferences.daily_calorie_target if preferences else 2000) * days_in_period,
                "protein": (preferences.protein_target if preferences else 100) * days_in_period,
                "carbs": (preferences.carbs_target if preferences else 200) * days_in_period,
                "fats": (preferences.fats_target if preferences else 60) * days_in_period
            }
            
            # Calculate deficits/surpluses
            calorie_deficit = targets["calories"] - total_calories
            protein_deficit = targets["protein"] - total_protein
            carbs_deficit = targets["carbs"] - total_carbs
            fats_deficit = targets["fats"] - total_fats
            
            # Generate AI insights
            ai_insights = self._generate_nutritional_insights(
                total_calories, total_protein, total_carbs, total_fats,
                targets, calorie_deficit, protein_deficit, carbs_deficit, fats_deficit
            )
            
            return {
                "period": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "analysis_type": analysis_type,
                    "days_in_period": days_in_period,
                    "days_with_data": days_with_data,
                    "missing_days": missing_days
                },
                "totals": {
                    "calories": total_calories,
                    "protein": total_protein,
                    "carbs": total_carbs,
                    "fats": total_fats
                },
                "targets": targets,
                "deficits": {
                    "calories": calorie_deficit,
                    "protein": protein_deficit,
                    "carbs": carbs_deficit,
                    "fats": fats_deficit
                },
                "percentages": {
                    "calories": (total_calories / targets["calories"]) * 100 if targets["calories"] > 0 else 0,
                    "protein": (total_protein / targets["protein"]) * 100 if targets["protein"] > 0 else 0,
                    "carbs": (total_carbs / targets["carbs"]) * 100 if targets["carbs"] > 0 else 0,
                    "fats": (total_fats / targets["fats"]) * 100 if targets["fats"] > 0 else 0
                },
                "ai_insights": ai_insights,
                "daily_breakdown": self._get_daily_breakdown(logs),
                "data_completeness": {
                    "completion_rate": (days_with_data / days_in_period) * 100 if days_in_period > 0 else 0,
                    "missing_days": missing_days,
                    "logged_dates": sorted(list(logged_dates))
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting nutritional analysis: {str(e)}")
            return {}
    
    def _generate_nutritional_insights(self, calories: float, protein: float, carbs: float, fats: float,
                                      targets: Dict[str, float], calorie_deficit: float, protein_deficit: float,
                                      carbs_deficit: float, fats_deficit: float) -> Dict[str, Any]:
        """Generate AI-powered nutritional insights"""
        insights = {
            "achievements": [],
            "concerns": [],
            "suggestions": []
        }
        
        # Analyze calorie intake
        calorie_percentage = (calories / targets["calories"]) * 100 if targets["calories"] > 0 else 0
        
        if calorie_percentage >= 95 and calorie_percentage <= 105:
            insights["achievements"].append("Excellent calorie target adherence!")
        elif calorie_percentage < 80:
            insights["concerns"].append("Significant calorie deficit - consider increasing portion sizes")
            insights["suggestions"].append("Add healthy snacks between meals")
        elif calorie_percentage > 120:
            insights["concerns"].append("Calorie surplus - consider reducing portion sizes")
            insights["suggestions"].append("Focus on nutrient-dense, lower-calorie foods")
        
        # Analyze protein intake
        protein_percentage = (protein / targets["protein"]) * 100 if targets["protein"] > 0 else 0
        
        if protein_percentage >= 90:
            insights["achievements"].append("Great protein intake for muscle maintenance!")
        elif protein_percentage < 70:
            insights["concerns"].append("Low protein intake")
            insights["suggestions"].append("Include lean proteins like chicken, fish, or legumes in each meal")
        
        # Analyze carbs intake
        carbs_percentage = (carbs / targets["carbs"]) * 100 if targets["carbs"] > 0 else 0
        
        # Analyze fats intake
        fats_percentage = (fats / targets["fats"]) * 100 if targets["fats"] > 0 else 0
        
        # Analyze macro balance
        if protein_percentage > 120 and carbs_percentage < 80:
            insights["suggestions"].append("Consider adding more complex carbohydrates for energy")
        elif carbs_percentage > 120 and protein_percentage < 80:
            insights["suggestions"].append("Balance your meals with more protein sources")
        
        return insights
    
    def _get_daily_breakdown(self, logs: List[NutritionalLog]) -> List[Dict[str, Any]]:
        """Get daily nutritional breakdown"""
        daily_data = {}
        
        for log in logs:
            date_str = log.log_date.isoformat()
            if date_str not in daily_data:
                daily_data[date_str] = {
                    "date": date_str,
                    "calories": 0,
                    "protein": 0,
                    "carbs": 0,
                    "fats": 0,
                    "meals": []
                }
            
            daily_data[date_str]["calories"] += log.calories
            daily_data[date_str]["protein"] += log.protein
            daily_data[date_str]["carbs"] += log.carbs
            daily_data[date_str]["fats"] += log.fats
            daily_data[date_str]["meals"].append({
                "meal_type": log.meal_type,
                "calories": log.calories,
                "protein": log.protein,
                "carbs": log.carbs,
                "fats": log.fats
            })
        
        return list(daily_data.values())
