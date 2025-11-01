"""
AI Improvement Suggestions Service
Provides comprehensive AI-driven improvement suggestions including food recommendations, timing, portions, and alternatives
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session

from models.nutrition import NutritionalLog, UserNutritionPreferences, MealPlan, MealPlanMeal
from models.health_profile import HealthProfile
from models.recipe import Recipe, Ingredient
from ai.nutrition_ai import NutritionAI

logger = logging.getLogger(__name__)

class AIImprovementSuggestionsService:
    """Service for AI-driven improvement suggestions"""
    
    def __init__(self):
        self.nutrition_ai = NutritionAI()
    
    def generate_comprehensive_suggestions(self, db: Session, user_id: int, 
                                         start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Generate comprehensive improvement suggestions including food recommendations, timing, portions, and alternatives
        """
        try:
            # Get user data
            nutritional_data = self._get_nutritional_data(db, user_id, start_date, end_date)
            user_preferences = self._get_user_preferences(db, user_id)
            health_profile = self._get_health_profile(db, user_id)
            recent_meals = self._get_recent_meals(db, user_id, end_date)
            
            # Generate different types of suggestions
            food_recommendations = self._generate_food_recommendations(
                nutritional_data, user_preferences, health_profile
            )
            
            timing_suggestions = self._generate_timing_suggestions(
                nutritional_data, user_preferences, health_profile
            )
            
            portion_suggestions = self._generate_portion_suggestions(
                nutritional_data, user_preferences, health_profile
            )
            
            meal_alternatives = self._generate_meal_alternatives(
                recent_meals, user_preferences, health_profile
            )
            
            optimization_suggestions = self._generate_optimization_suggestions(
                nutritional_data, user_preferences, health_profile
            )
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days_analyzed": (end_date - start_date).days + 1
                },
                "food_recommendations": food_recommendations,
                "timing_suggestions": timing_suggestions,
                "portion_suggestions": portion_suggestions,
                "meal_alternatives": meal_alternatives,
                "optimization_suggestions": optimization_suggestions,
                "user_context": {
                    "fitness_goal": health_profile.fitness_goal if health_profile else None,
                    "activity_level": health_profile.activity_level if health_profile else None,
                    "dietary_preferences": user_preferences.get("dietary_preferences", []),
                    "allergies": user_preferences.get("allergies", [])
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating comprehensive suggestions: {str(e)}")
            return self._generate_fallback_suggestions()
    
    def _get_nutritional_data(self, db: Session, user_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get nutritional data for the period"""
        logs = db.query(NutritionalLog).filter(
            NutritionalLog.user_id == user_id,
            NutritionalLog.log_date >= start_date,
            NutritionalLog.log_date <= end_date
        ).all()
        
        # Calculate totals and averages
        total_calories = sum(log.calories for log in logs)
        total_protein = sum(log.protein for log in logs)
        total_carbs = sum(log.carbs for log in logs)
        total_fats = sum(log.fats for log in logs)
        total_fiber = sum(log.fiber for log in logs)
        total_sugar = sum(log.sugar for log in logs)
        total_sodium = sum(log.sodium for log in logs)
        
        days_in_period = (end_date - start_date).days + 1
        daily_averages = {
            "calories": total_calories / days_in_period if days_in_period > 0 else 0,
            "protein": total_protein / days_in_period if days_in_period > 0 else 0,
            "carbs": total_carbs / days_in_period if days_in_period > 0 else 0,
            "fats": total_fats / days_in_period if days_in_period > 0 else 0,
            "fiber": total_fiber / days_in_period if days_in_period > 0 else 0,
            "sugar": total_sugar / days_in_period if days_in_period > 0 else 0,
            "sodium": total_sodium / days_in_period if days_in_period > 0 else 0
        }
        
        return {
            "totals": {
                "calories": total_calories,
                "protein": total_protein,
                "carbs": total_carbs,
                "fats": total_fats,
                "fiber": total_fiber,
                "sugar": total_sugar,
                "sodium": total_sodium
            },
            "daily_averages": daily_averages,
            "logged_days": len(set(log.log_date for log in logs))
        }
    
    def _get_user_preferences(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Get user nutrition preferences"""
        preferences = db.query(UserNutritionPreferences).filter(
            UserNutritionPreferences.user_id == user_id
        ).first()
        
        if preferences:
            return {
                "daily_calorie_target": preferences.daily_calorie_target,
                "protein_target": preferences.protein_target,
                "carbs_target": preferences.carbs_target,
                "fats_target": preferences.fats_target,
                "dietary_preferences": preferences.dietary_preferences or [],
                "allergies": preferences.allergies or [],
                "disliked_ingredients": preferences.disliked_ingredients or [],
                "cuisine_preferences": preferences.cuisine_preferences or []
            }
        
        return {
            "daily_calorie_target": 2000,
            "protein_target": 100,
            "carbs_target": 200,
            "fats_target": 60,
            "dietary_preferences": [],
            "allergies": [],
            "disliked_ingredients": [],
            "cuisine_preferences": []
        }
    
    def _get_health_profile(self, db: Session, user_id: int) -> Optional[HealthProfile]:
        """Get user health profile"""
        return db.query(HealthProfile).filter(HealthProfile.user_id == user_id).first()
    
    def _get_recent_meals(self, db: Session, user_id: int, end_date: date) -> List[Dict[str, Any]]:
        """Get recent meals for alternative suggestions"""
        recent_meals = db.query(MealPlanMeal).join(MealPlan).filter(
            MealPlan.user_id == user_id,
            MealPlan.created_at >= end_date - timedelta(days=7)
        ).limit(10).all()
        
        return [
            {
                "id": meal.id,
                "meal_name": meal.meal_name,
                "meal_type": meal.meal_type,
                "calories": meal.calories,
                "protein": meal.protein,
                "carbs": meal.carbs,
                "fats": meal.fats,
                "cuisine": meal.cuisine
            }
            for meal in recent_meals
        ]
    
    def _generate_food_recommendations(self, nutritional_data: Dict[str, Any], 
                                     user_preferences: Dict[str, Any], 
                                     health_profile: Optional[HealthProfile]) -> List[Dict[str, Any]]:
        """Generate specific food recommendations based on nutritional gaps"""
        recommendations = []
        daily_avg = nutritional_data["daily_averages"]
        targets = {
            "calories": user_preferences["daily_calorie_target"],
            "protein": user_preferences["protein_target"],
            "carbs": user_preferences["carbs_target"],
            "fats": user_preferences["fats_target"]
        }
        
        # Protein recommendations
        protein_percentage = (daily_avg["protein"] / targets["protein"]) * 100 if targets["protein"] > 0 else 0
        if protein_percentage < 80:
            protein_foods = self._get_protein_rich_foods(user_preferences)
            recommendations.append({
                "category": "protein",
                "title": "Increase Protein Intake",
                "description": f"Current: {daily_avg['protein']:.1f}g, Target: {targets['protein']}g",
                "priority": "high",
                "foods": protein_foods,
                "reasoning": "Protein is essential for muscle maintenance and satiety"
            })
        
        # Fiber recommendations
        if daily_avg["fiber"] < 20:
            fiber_foods = self._get_fiber_rich_foods(user_preferences)
            recommendations.append({
                "category": "fiber",
                "title": "Boost Fiber Intake",
                "description": f"Current: {daily_avg['fiber']:.1f}g, Recommended: 25g+",
                "priority": "medium",
                "foods": fiber_foods,
                "reasoning": "Fiber supports digestive health and helps with satiety"
            })
        
        # Healthy fats recommendations
        fats_percentage = (daily_avg["fats"] / targets["fats"]) * 100 if targets["fats"] > 0 else 0
        if fats_percentage < 70:
            healthy_fats = self._get_healthy_fat_foods(user_preferences)
            recommendations.append({
                "category": "fats",
                "title": "Add Healthy Fats",
                "description": f"Current: {daily_avg['fats']:.1f}g, Target: {targets['fats']}g",
                "priority": "medium",
                "foods": healthy_fats,
                "reasoning": "Healthy fats support brain function and nutrient absorption"
            })
        
        # Micronutrient recommendations
        micronutrient_foods = self._get_micronutrient_rich_foods(user_preferences)
        recommendations.append({
            "category": "micronutrients",
            "title": "Enhance Micronutrient Intake",
            "description": "Add nutrient-dense foods for optimal health",
            "priority": "low",
            "foods": micronutrient_foods,
            "reasoning": "Micronutrients support overall health and immune function"
        })
        
        return recommendations
    
    def _generate_timing_suggestions(self, nutritional_data: Dict[str, Any], 
                                   user_preferences: Dict[str, Any], 
                                   health_profile: Optional[HealthProfile]) -> List[Dict[str, Any]]:
        """Generate meal timing optimization suggestions"""
        suggestions = []
        
        # General timing recommendations
        suggestions.append({
            "category": "meal_frequency",
            "title": "Optimize Meal Frequency",
            "description": "Consider eating 3-4 balanced meals with 1-2 healthy snacks",
            "priority": "medium",
            "timing": "Throughout the day",
            "reasoning": "Regular meal timing helps maintain stable blood sugar and energy levels"
        })
        
        # Pre-workout nutrition
        if health_profile and health_profile.activity_level in ['moderate', 'active', 'very_active']:
            suggestions.append({
                "category": "pre_workout",
                "title": "Pre-Workout Nutrition",
                "description": "Eat a light meal 1-2 hours before exercise",
                "priority": "medium",
                "timing": "1-2 hours before exercise",
                "reasoning": "Proper pre-workout nutrition provides energy and improves performance"
            })
        
        # Post-workout nutrition
        if health_profile and health_profile.activity_level in ['moderate', 'active', 'very_active']:
            suggestions.append({
                "category": "post_workout",
                "title": "Post-Workout Recovery",
                "description": "Consume protein and carbs within 30-60 minutes after exercise",
                "priority": "high",
                "timing": "30-60 minutes after exercise",
                "reasoning": "Post-workout nutrition supports muscle recovery and glycogen replenishment"
            })
        
        # Breakfast timing
        suggestions.append({
            "category": "breakfast",
            "title": "Morning Fuel",
            "description": "Eat breakfast within 1-2 hours of waking up",
            "priority": "medium",
            "timing": "Within 1-2 hours of waking",
            "reasoning": "Early breakfast kickstarts metabolism and provides energy for the day"
        })
        
        # Evening meal timing
        suggestions.append({
            "category": "evening",
            "title": "Evening Meal Timing",
            "description": "Finish dinner 2-3 hours before bedtime",
            "priority": "low",
            "timing": "2-3 hours before bedtime",
            "reasoning": "Allows for proper digestion and better sleep quality"
        })
        
        return suggestions
    
    def _generate_portion_suggestions(self, nutritional_data: Dict[str, Any], 
                                    user_preferences: Dict[str, Any], 
                                    health_profile: Optional[HealthProfile]) -> List[Dict[str, Any]]:
        """Generate portion size optimization suggestions"""
        suggestions = []
        daily_avg = nutritional_data["daily_averages"]
        targets = {
            "calories": user_preferences["daily_calorie_target"],
            "protein": user_preferences["protein_target"],
            "carbs": user_preferences["carbs_target"],
            "fats": user_preferences["fats_target"]
        }
        
        # Calorie portion suggestions
        calorie_percentage = (daily_avg["calories"] / targets["calories"]) * 100 if targets["calories"] > 0 else 0
        if calorie_percentage < 80:
            suggestions.append({
                "category": "calories",
                "title": "Increase Portion Sizes",
                "description": f"Current: {calorie_percentage:.0f}% of calorie target",
                "priority": "high",
                "adjustment": "Increase by 20-30%",
                "reasoning": "Larger portions will help meet your daily calorie needs"
            })
        elif calorie_percentage > 120:
            suggestions.append({
                "category": "calories",
                "title": "Reduce Portion Sizes",
                "description": f"Current: {calorie_percentage:.0f}% of calorie target",
                "priority": "medium",
                "adjustment": "Reduce by 15-20%",
                "reasoning": "Smaller portions will help maintain your calorie target"
            })
        
        # Protein portion suggestions
        protein_percentage = (daily_avg["protein"] / targets["protein"]) * 100 if targets["protein"] > 0 else 0
        if protein_percentage < 80:
            suggestions.append({
                "category": "protein",
                "title": "Increase Protein Portions",
                "description": f"Current: {daily_avg['protein']:.1f}g, Target: {targets['protein']}g",
                "priority": "high",
                "adjustment": "Add 20-30g protein per meal",
                "reasoning": "Higher protein portions support muscle maintenance and satiety"
            })
        
        # Vegetable portion suggestions
        suggestions.append({
            "category": "vegetables",
            "title": "Increase Vegetable Portions",
            "description": "Aim for 2-3 cups of vegetables per day",
            "priority": "medium",
            "adjustment": "Fill half your plate with vegetables",
            "reasoning": "Vegetables provide essential vitamins, minerals, and fiber"
        })
        
        # Hydration portion suggestions
        suggestions.append({
            "category": "hydration",
            "title": "Optimize Hydration",
            "description": "Drink 8-10 glasses of water daily",
            "priority": "low",
            "adjustment": "Drink 1 glass with each meal and snack",
            "reasoning": "Proper hydration supports metabolism and overall health"
        })
        
        return suggestions
    
    def _generate_meal_alternatives(self, recent_meals: List[Dict[str, Any]], 
                                  user_preferences: Dict[str, Any], 
                                  health_profile: Optional[HealthProfile]) -> List[Dict[str, Any]]:
        """Generate alternative meal suggestions"""
        alternatives = []
        
        # Analyze recent meals for variety
        meal_types = [meal["meal_type"] for meal in recent_meals]
        cuisines = [meal["cuisine"] for meal in recent_meals if meal.get("cuisine")]
        
        # Suggest variety improvements
        if len(set(meal_types)) < 3:
            alternatives.append({
                "category": "variety",
                "title": "Increase Meal Variety",
                "description": "Try different meal types throughout the day",
                "priority": "medium",
                "suggestions": [
                    "Add smoothie bowls for breakfast",
                    "Try grain bowls for lunch",
                    "Experiment with sheet pan dinners"
                ],
                "reasoning": "Variety ensures you get different nutrients and keeps meals interesting"
            })
        
        # Suggest cuisine variety
        if len(set(cuisines)) < 3:
            alternatives.append({
                "category": "cuisine",
                "title": "Explore New Cuisines",
                "description": "Try different cultural cuisines for variety",
                "priority": "low",
                "suggestions": [
                    "Mediterranean: Greek salads, hummus, grilled fish",
                    "Asian: Stir-fries, sushi, miso soup",
                    "Mexican: Tacos with fresh vegetables, black beans",
                    "Indian: Curry dishes, dal, vegetable biryani"
                ],
                "reasoning": "Different cuisines offer unique flavors and nutritional benefits"
            })
        
        # Suggest cooking method alternatives
        alternatives.append({
            "category": "cooking_methods",
            "title": "Try New Cooking Methods",
            "description": "Experiment with different cooking techniques",
            "priority": "low",
            "suggestions": [
                "Grilling: Adds flavor without extra calories",
                "Steaming: Preserves nutrients and natural flavors",
                "Roasting: Enhances natural sweetness of vegetables",
                "Sautéing: Quick cooking with minimal oil"
            ],
            "reasoning": "Different cooking methods can enhance flavors and nutritional value"
        })
        
        return alternatives
    
    def _generate_optimization_suggestions(self, nutritional_data: Dict[str, Any], 
                                         user_preferences: Dict[str, Any], 
                                         health_profile: Optional[HealthProfile]) -> List[Dict[str, Any]]:
        """Generate general optimization suggestions"""
        suggestions = []
        
        # Meal prep suggestions
        suggestions.append({
            "category": "meal_prep",
            "title": "Meal Preparation",
            "description": "Prepare meals in advance for consistency",
            "priority": "medium",
            "suggestions": [
                "Prep vegetables and proteins on weekends",
                "Cook grains in batches",
                "Prepare healthy snacks in portion-controlled containers",
                "Plan meals for the week ahead"
            ],
            "reasoning": "Meal prep helps maintain consistent nutrition and saves time"
        })
        
        # Hydration optimization
        suggestions.append({
            "category": "hydration",
            "title": "Hydration Strategy",
            "description": "Optimize your hydration throughout the day",
            "priority": "low",
            "suggestions": [
                "Start the day with a glass of water",
                "Drink water before each meal",
                "Keep a water bottle nearby",
                "Add lemon or cucumber for flavor"
            ],
            "reasoning": "Proper hydration supports metabolism and overall health"
        })
        
        # Mindful eating suggestions
        suggestions.append({
            "category": "mindful_eating",
            "title": "Mindful Eating Practices",
            "description": "Develop healthy eating habits",
            "priority": "low",
            "suggestions": [
                "Eat without distractions (no TV, phone)",
                "Chew food slowly and thoroughly",
                "Listen to hunger and fullness cues",
                "Take time to enjoy your meals"
            ],
            "reasoning": "Mindful eating helps with portion control and digestion"
        })
        
        return suggestions
    
    def _get_protein_rich_foods(self, user_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get protein-rich food recommendations based on dietary preferences"""
        foods = []
        
        # Check dietary preferences
        dietary_prefs = [pref.lower() for pref in user_preferences.get("dietary_preferences", [])]
        allergies = [allergy.lower() for allergy in user_preferences.get("allergies", [])]
        
        if "vegetarian" in dietary_prefs or "vegan" in dietary_prefs:
            foods.extend([
                {"name": "Lentils", "protein": "18g per cup", "benefits": "High in fiber and iron"},
                {"name": "Chickpeas", "protein": "15g per cup", "benefits": "Versatile and filling"},
                {"name": "Quinoa", "protein": "8g per cup", "benefits": "Complete protein with all amino acids"},
                {"name": "Greek Yogurt", "protein": "20g per cup", "benefits": "Probiotics and calcium"},
                {"name": "Tofu", "protein": "10g per 100g", "benefits": "Absorbs flavors well"}
            ])
        else:
            foods.extend([
                {"name": "Chicken Breast", "protein": "31g per 100g", "benefits": "Lean and versatile"},
                {"name": "Salmon", "protein": "25g per 100g", "benefits": "Rich in omega-3 fatty acids"},
                {"name": "Eggs", "protein": "6g per egg", "benefits": "Complete protein with vitamins"},
                {"name": "Greek Yogurt", "protein": "20g per cup", "benefits": "Probiotics and calcium"},
                {"name": "Lean Beef", "protein": "26g per 100g", "benefits": "High in iron and B vitamins"}
            ])
        
        # Filter out foods with allergies
        filtered_foods = []
        for food in foods:
            if not any(allergy in food["name"].lower() for allergy in allergies):
                filtered_foods.append(food)
        
        return filtered_foods
    
    def _get_fiber_rich_foods(self, user_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get fiber-rich food recommendations"""
        return [
            {"name": "Black Beans", "fiber": "15g per cup", "benefits": "High in protein and iron"},
            {"name": "Avocado", "fiber": "10g per fruit", "benefits": "Healthy fats and potassium"},
            {"name": "Raspberries", "fiber": "8g per cup", "benefits": "Antioxidants and vitamin C"},
            {"name": "Oatmeal", "fiber": "4g per cup", "benefits": "Soluble fiber for heart health"},
            {"name": "Broccoli", "fiber": "5g per cup", "benefits": "Vitamin C and folate"},
            {"name": "Sweet Potato", "fiber": "4g per medium", "benefits": "Beta-carotene and potassium"}
        ]
    
    def _get_healthy_fat_foods(self, user_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get healthy fat food recommendations"""
        return [
            {"name": "Avocado", "fats": "21g per fruit", "benefits": "Monounsaturated fats and fiber"},
            {"name": "Nuts (Almonds)", "fats": "14g per ounce", "benefits": "Vitamin E and magnesium"},
            {"name": "Olive Oil", "fats": "14g per tablespoon", "benefits": "Monounsaturated fats"},
            {"name": "Salmon", "fats": "12g per 100g", "benefits": "Omega-3 fatty acids"},
            {"name": "Chia Seeds", "fats": "9g per ounce", "benefits": "Omega-3 and fiber"},
            {"name": "Dark Chocolate", "fats": "12g per ounce", "benefits": "Antioxidants and flavonoids"}
        ]
    
    def _get_micronutrient_rich_foods(self, user_preferences: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get micronutrient-rich food recommendations"""
        return [
            {"name": "Spinach", "nutrients": "Iron, folate, vitamin K", "benefits": "Supports blood health"},
            {"name": "Bell Peppers", "nutrients": "Vitamin C, vitamin A", "benefits": "Immune system support"},
            {"name": "Berries", "nutrients": "Antioxidants, vitamin C", "benefits": "Anti-inflammatory properties"},
            {"name": "Nuts", "nutrients": "Magnesium, zinc, vitamin E", "benefits": "Heart and brain health"},
            {"name": "Citrus Fruits", "nutrients": "Vitamin C, folate", "benefits": "Immune system and collagen"},
            {"name": "Leafy Greens", "nutrients": "Vitamin K, folate, iron", "benefits": "Bone and blood health"}
        ]
    
    def _generate_fallback_suggestions(self) -> Dict[str, Any]:
        """Generate fallback suggestions when AI is unavailable"""
        return {
            "period": {"start_date": "", "end_date": "", "days_analyzed": 0},
            "food_recommendations": [
                {
                    "category": "general",
                    "title": "Balanced Nutrition",
                    "description": "Focus on whole, unprocessed foods",
                    "priority": "medium",
                    "foods": [
                        {"name": "Vegetables", "benefits": "Vitamins, minerals, and fiber"},
                        {"name": "Fruits", "benefits": "Antioxidants and natural sugars"},
                        {"name": "Whole Grains", "benefits": "Fiber and B vitamins"},
                        {"name": "Lean Proteins", "benefits": "Essential amino acids"}
                    ],
                    "reasoning": "Whole foods provide comprehensive nutrition"
                }
            ],
            "timing_suggestions": [
                {
                    "category": "general",
                    "title": "Regular Meal Times",
                    "description": "Eat at consistent times each day",
                    "priority": "medium",
                    "timing": "Every 3-4 hours",
                    "reasoning": "Consistent timing supports metabolism"
                }
            ],
            "portion_suggestions": [
                {
                    "category": "general",
                    "title": "Balanced Portions",
                    "description": "Use the plate method for portion control",
                    "priority": "medium",
                    "adjustment": "Half plate vegetables, quarter protein, quarter carbs",
                    "reasoning": "Balanced portions ensure adequate nutrition"
                }
            ],
            "meal_alternatives": [
                {
                    "category": "variety",
                    "title": "Meal Variety",
                    "description": "Try different foods and cooking methods",
                    "priority": "low",
                    "suggestions": ["Experiment with new recipes", "Try different cuisines"],
                    "reasoning": "Variety ensures comprehensive nutrition"
                }
            ],
            "optimization_suggestions": [
                {
                    "category": "general",
                    "title": "Healthy Habits",
                    "description": "Develop consistent healthy eating habits",
                    "priority": "medium",
                    "suggestions": ["Plan meals ahead", "Stay hydrated", "Eat mindfully"],
                    "reasoning": "Consistent habits support long-term health"
                }
            ]
        }








