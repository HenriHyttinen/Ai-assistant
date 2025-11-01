"""
Enhanced Personalization Service for AI Meal Planning

This service provides advanced personalization features including:
- Behavioral pattern analysis
- Preference learning from user interactions
- Contextual meal planning
- Seasonal and cultural adaptations
- Health goal optimization
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, date, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)

class PersonalizationContext(Enum):
    """Types of personalization context"""
    HEALTH_GOALS = "health_goals"
    LIFESTYLE = "lifestyle"
    CULTURAL = "cultural"
    SEASONAL = "seasonal"
    BEHAVIORAL = "behavioral"
    NUTRITIONAL = "nutritional"

@dataclass
class UserBehaviorPattern:
    """Represents a user's behavioral pattern"""
    pattern_type: str
    confidence_score: float
    data_points: int
    last_updated: datetime
    pattern_data: Dict[str, Any]

class EnhancedPersonalizationService:
    """Enhanced service for AI meal planning personalization"""
    
    def __init__(self):
        self.seasonal_ingredients = self._initialize_seasonal_ingredients()
        self.cultural_meal_patterns = self._initialize_cultural_meal_patterns()
        self.health_goal_optimizations = self._initialize_health_goal_optimizations()
        self.lifestyle_adaptations = self._initialize_lifestyle_adaptations()
        
    def _initialize_seasonal_ingredients(self) -> Dict[str, List[str]]:
        """Initialize seasonal ingredient preferences"""
        return {
            "spring": [
                "asparagus", "artichokes", "peas", "radishes", "spinach", "lettuce",
                "strawberries", "rhubarb", "mint", "dill", "chives"
            ],
            "summer": [
                "tomatoes", "cucumbers", "zucchini", "corn", "peppers", "eggplant",
                "berries", "stone_fruits", "herbs", "basil", "cilantro"
            ],
            "fall": [
                "pumpkin", "squash", "apples", "pears", "cranberries", "sweet_potatoes",
                "mushrooms", "cabbage", "brussels_sprouts", "sage", "thyme"
            ],
            "winter": [
                "citrus", "root_vegetables", "winter_squash", "kale", "cabbage",
                "pomegranates", "persimmons", "rosemary", "oregano", "bay_leaves"
            ]
        }
    
    def _initialize_cultural_meal_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize cultural meal patterns and preferences"""
        return {
            "mediterranean": {
                "breakfast": ["olive_oil", "tomatoes", "feta", "olives", "herbs"],
                "lunch": ["fish", "vegetables", "legumes", "whole_grains"],
                "dinner": ["grilled_meat", "vegetables", "wine"],
                "cooking_methods": ["grilling", "roasting", "sautéing"],
                "meal_timing": {"breakfast": "7-9am", "lunch": "1-3pm", "dinner": "8-10pm"}
            },
            "asian": {
                "breakfast": ["rice", "miso_soup", "pickled_vegetables", "fish"],
                "lunch": ["stir_fry", "rice", "vegetables", "soup"],
                "dinner": ["family_style", "multiple_dishes", "rice", "tea"],
                "cooking_methods": ["stir_frying", "steaming", "braising"],
                "meal_timing": {"breakfast": "6-8am", "lunch": "12-2pm", "dinner": "6-8pm"}
            },
            "indian": {
                "breakfast": ["spiced_tea", "flatbread", "yogurt", "fruits"],
                "lunch": ["rice", "curry", "vegetables", "dal"],
                "dinner": ["family_meal", "multiple_curries", "bread", "dessert"],
                "cooking_methods": ["currying", "tandoori", "steaming"],
                "meal_timing": {"breakfast": "7-9am", "lunch": "1-3pm", "dinner": "8-10pm"}
            },
            "mexican": {
                "breakfast": ["eggs", "beans", "tortillas", "salsa"],
                "lunch": ["tacos", "burritos", "rice", "beans"],
                "dinner": ["family_meal", "multiple_dishes", "dessert"],
                "cooking_methods": ["grilling", "braising", "frying"],
                "meal_timing": {"breakfast": "7-9am", "lunch": "1-3pm", "dinner": "7-9pm"}
            },
            "middle_eastern": {
                "breakfast": ["bread", "olives", "cheese", "tea"],
                "lunch": ["rice", "meat", "vegetables", "yogurt"],
                "dinner": ["family_meal", "multiple_dishes", "dessert"],
                "cooking_methods": ["grilling", "roasting", "braising"],
                "meal_timing": {"breakfast": "7-9am", "lunch": "1-3pm", "dinner": "8-10pm"}
            }
        }
    
    def _initialize_health_goal_optimizations(self) -> Dict[str, Dict[str, Any]]:
        """Initialize health goal specific optimizations"""
        return {
            "weight_loss": {
                "calorie_distribution": {"breakfast": 0.25, "lunch": 0.35, "dinner": 0.30, "snacks": 0.10},
                "nutrient_priorities": ["protein", "fiber", "water"],
                "meal_timing": {"breakfast": "within_1_hour_waking", "dinner": "3_hours_before_bed"},
                "cooking_methods": ["grilling", "steaming", "baking"],
                "avoid": ["fried_foods", "processed_foods", "sugary_drinks"]
            },
            "muscle_gain": {
                "calorie_distribution": {"breakfast": 0.30, "lunch": 0.30, "dinner": 0.30, "snacks": 0.10},
                "nutrient_priorities": ["protein", "carbohydrates", "healthy_fats"],
                "meal_timing": {"pre_workout": "1-2_hours_before", "post_workout": "within_30_minutes"},
                "cooking_methods": ["grilling", "baking", "sautéing"],
                "focus": ["lean_proteins", "complex_carbs", "recovery_nutrients"]
            },
            "heart_health": {
                "calorie_distribution": {"breakfast": 0.25, "lunch": 0.35, "dinner": 0.30, "snacks": 0.10},
                "nutrient_priorities": ["omega_3", "fiber", "antioxidants"],
                "meal_timing": {"regular_intervals": True, "no_late_night_eating": True},
                "cooking_methods": ["grilling", "steaming", "baking"],
                "focus": ["fish", "vegetables", "whole_grains", "healthy_fats"]
            },
            "diabetes_management": {
                "calorie_distribution": {"breakfast": 0.25, "lunch": 0.35, "dinner": 0.30, "snacks": 0.10},
                "nutrient_priorities": ["fiber", "protein", "low_gi_carbs"],
                "meal_timing": {"consistent_timing": True, "small_frequent_meals": True},
                "cooking_methods": ["steaming", "baking", "grilling"],
                "focus": ["low_gi_foods", "portion_control", "blood_sugar_stability"]
            },
            "athletic_performance": {
                "calorie_distribution": {"breakfast": 0.25, "lunch": 0.30, "dinner": 0.30, "snacks": 0.15},
                "nutrient_priorities": ["carbohydrates", "protein", "hydration"],
                "meal_timing": {"pre_workout": "2-3_hours_before", "post_workout": "within_1_hour"},
                "cooking_methods": ["grilling", "baking", "steaming"],
                "focus": ["performance_nutrition", "recovery", "hydration"]
            }
        }
    
    def _initialize_lifestyle_adaptations(self) -> Dict[str, Dict[str, Any]]:
        """Initialize lifestyle-based adaptations"""
        return {
            "busy_professional": {
                "meal_prep_friendly": True,
                "quick_cooking_methods": ["one_pot", "sheet_pan", "slow_cooker"],
                "portable_meals": True,
                "meal_timing": {"flexible": True, "grab_and_go": True}
            },
            "family_with_children": {
                "kid_friendly": True,
                "batch_cooking": True,
                "variety_important": True,
                "meal_timing": {"consistent": True, "family_meals": True}
            },
            "elderly": {
                "easy_to_chew": True,
                "nutrient_dense": True,
                "small_portions": True,
                "meal_timing": {"regular": True, "frequent_small_meals": True}
            },
            "student": {
                "budget_friendly": True,
                "simple_recipes": True,
                "meal_prep": True,
                "meal_timing": {"flexible": True, "irregular": True}
            },
            "athlete": {
                "performance_focused": True,
                "recovery_nutrition": True,
                "timing_critical": True,
                "meal_timing": {"pre_post_workout": True, "consistent": True}
            }
        }
    
    def analyze_user_behavior_patterns(self, user_id: str, meal_history: List[Dict[str, Any]], 
                                     rating_history: List[Dict[str, Any]]) -> List[UserBehaviorPattern]:
        """
        Analyze user behavior patterns from meal and rating history
        
        Args:
            user_id: User ID
            meal_history: List of past meal choices
            rating_history: List of recipe ratings
            
        Returns:
            List of identified behavior patterns
        """
        patterns = []
        
        # Analyze cuisine preferences
        cuisine_preferences = self._analyze_cuisine_preferences(meal_history, rating_history)
        if cuisine_preferences:
            patterns.append(UserBehaviorPattern(
                pattern_type="cuisine_preferences",
                confidence_score=cuisine_preferences["confidence"],
                data_points=cuisine_preferences["data_points"],
                last_updated=datetime.now(),
                pattern_data=cuisine_preferences
            ))
        
        # Analyze meal timing patterns
        timing_patterns = self._analyze_meal_timing(meal_history)
        if timing_patterns:
            patterns.append(UserBehaviorPattern(
                pattern_type="meal_timing",
                confidence_score=timing_patterns["confidence"],
                data_points=timing_patterns["data_points"],
                last_updated=datetime.now(),
                pattern_data=timing_patterns
            ))
        
        # Analyze ingredient preferences
        ingredient_preferences = self._analyze_ingredient_preferences(meal_history, rating_history)
        if ingredient_preferences:
            patterns.append(UserBehaviorPattern(
                pattern_type="ingredient_preferences",
                confidence_score=ingredient_preferences["confidence"],
                data_points=ingredient_preferences["data_points"],
                last_updated=datetime.now(),
                pattern_data=ingredient_preferences
            ))
        
        # Analyze cooking method preferences
        cooking_preferences = self._analyze_cooking_preferences(meal_history, rating_history)
        if cooking_preferences:
            patterns.append(UserBehaviorPattern(
                pattern_type="cooking_preferences",
                confidence_score=cooking_preferences["confidence"],
                data_points=cooking_preferences["data_points"],
                last_updated=datetime.now(),
                pattern_data=cooking_preferences
            ))
        
        return patterns
    
    def _analyze_cuisine_preferences(self, meal_history: List[Dict[str, Any]], 
                                   rating_history: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Analyze user's cuisine preferences"""
        if not meal_history:
            return None
        
        cuisine_counts = {}
        cuisine_ratings = {}
        
        for meal in meal_history:
            cuisine = meal.get("cuisine", "unknown")
            cuisine_counts[cuisine] = cuisine_counts.get(cuisine, 0) + 1
        
        for rating in rating_history:
            cuisine = rating.get("cuisine", "unknown")
            rating_value = rating.get("rating", 0)
            if cuisine not in cuisine_ratings:
                cuisine_ratings[cuisine] = []
            cuisine_ratings[cuisine].append(rating_value)
        
        # Calculate preference scores
        preference_scores = {}
        for cuisine in cuisine_counts:
            count = cuisine_counts[cuisine]
            avg_rating = sum(cuisine_ratings.get(cuisine, [0])) / len(cuisine_ratings.get(cuisine, [1]))
            preference_scores[cuisine] = count * avg_rating
        
        if not preference_scores:
            return None
        
        # Sort by preference score
        sorted_cuisines = sorted(preference_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "preferred_cuisines": [cuisine for cuisine, score in sorted_cuisines[:3]],
            "preference_scores": dict(sorted_cuisines),
            "confidence": min(0.9, len(meal_history) / 20),  # More data = higher confidence
            "data_points": len(meal_history)
        }
    
    def _analyze_meal_timing(self, meal_history: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Analyze user's meal timing patterns"""
        if not meal_history:
            return None
        
        meal_times = []
        for meal in meal_history:
            if "timestamp" in meal:
                try:
                    meal_time = datetime.fromisoformat(meal["timestamp"])
                    meal_times.append(meal_time.hour)
                except:
                    continue
        
        if not meal_times:
            return None
        
        # Analyze timing patterns
        breakfast_times = [t for t in meal_times if 6 <= t <= 10]
        lunch_times = [t for t in meal_times if 11 <= t <= 14]
        dinner_times = [t for t in meal_times if 17 <= t <= 21]
        
        patterns = {
            "breakfast_time": sum(breakfast_times) / len(breakfast_times) if breakfast_times else None,
            "lunch_time": sum(lunch_times) / len(lunch_times) if lunch_times else None,
            "dinner_time": sum(dinner_times) / len(dinner_times) if dinner_times else None,
            "meal_frequency": len(meal_times),
            "timing_consistency": self._calculate_timing_consistency(meal_times)
        }
        
        return {
            "patterns": patterns,
            "confidence": min(0.9, len(meal_times) / 30),
            "data_points": len(meal_times)
        }
    
    def _analyze_ingredient_preferences(self, meal_history: List[Dict[str, Any]], 
                                      rating_history: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Analyze user's ingredient preferences"""
        if not meal_history:
            return None
        
        ingredient_counts = {}
        ingredient_ratings = {}
        
        for meal in meal_history:
            ingredients = meal.get("ingredients", [])
            for ingredient in ingredients:
                ingredient_counts[ingredient] = ingredient_counts.get(ingredient, 0) + 1
        
        for rating in rating_history:
            ingredients = rating.get("ingredients", [])
            rating_value = rating.get("rating", 0)
            for ingredient in ingredients:
                if ingredient not in ingredient_ratings:
                    ingredient_ratings[ingredient] = []
                ingredient_ratings[ingredient].append(rating_value)
        
        # Calculate preference scores
        preference_scores = {}
        for ingredient in ingredient_counts:
            count = ingredient_counts[ingredient]
            avg_rating = sum(ingredient_ratings.get(ingredient, [0])) / len(ingredient_ratings.get(ingredient, [1]))
            preference_scores[ingredient] = count * avg_rating
        
        if not preference_scores:
            return None
        
        # Sort by preference score
        sorted_ingredients = sorted(preference_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "preferred_ingredients": [ingredient for ingredient, score in sorted_ingredients[:10]],
            "disliked_ingredients": [ingredient for ingredient, score in sorted_ingredients[-5:] if score < 0],
            "preference_scores": dict(sorted_ingredients),
            "confidence": min(0.9, len(meal_history) / 25),
            "data_points": len(meal_history)
        }
    
    def _analyze_cooking_preferences(self, meal_history: List[Dict[str, Any]], 
                                   rating_history: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Analyze user's cooking method preferences"""
        if not meal_history:
            return None
        
        cooking_methods = {}
        method_ratings = {}
        
        for meal in meal_history:
            method = meal.get("cooking_method", "unknown")
            cooking_methods[method] = cooking_methods.get(method, 0) + 1
        
        for rating in rating_history:
            method = rating.get("cooking_method", "unknown")
            rating_value = rating.get("rating", 0)
            if method not in method_ratings:
                method_ratings[method] = []
            method_ratings[method].append(rating_value)
        
        # Calculate preference scores
        preference_scores = {}
        for method in cooking_methods:
            count = cooking_methods[method]
            avg_rating = sum(method_ratings.get(method, [0])) / len(method_ratings.get(method, [1]))
            preference_scores[method] = count * avg_rating
        
        if not preference_scores:
            return None
        
        # Sort by preference score
        sorted_methods = sorted(preference_scores.items(), key=lambda x: x[1], reverse=True)
        
        return {
            "preferred_methods": [method for method, score in sorted_methods[:5]],
            "preference_scores": dict(sorted_methods),
            "confidence": min(0.9, len(meal_history) / 20),
            "data_points": len(meal_history)
        }
    
    def _calculate_timing_consistency(self, meal_times: List[int]) -> float:
        """Calculate how consistent meal timing is (0-1 scale)"""
        if len(meal_times) < 2:
            return 0.0
        
        # Group by meal type and calculate variance
        breakfast_times = [t for t in meal_times if 6 <= t <= 10]
        lunch_times = [t for t in meal_times if 11 <= t <= 14]
        dinner_times = [t for t in meal_times if 17 <= t <= 21]
        
        consistency_scores = []
        
        for times in [breakfast_times, lunch_times, dinner_times]:
            if len(times) > 1:
                variance = sum((t - sum(times)/len(times))**2 for t in times) / len(times)
                consistency_scores.append(max(0, 1 - variance / 4))  # Normalize to 0-1
        
        return sum(consistency_scores) / len(consistency_scores) if consistency_scores else 0.0
    
    def generate_personalized_meal_plan_context(self, user_profile: Dict[str, Any], 
                                              behavior_patterns: List[UserBehaviorPattern],
                                              current_date: date = None) -> Dict[str, Any]:
        """
        Generate personalized context for meal planning
        
        Args:
            user_profile: User's profile information
            behavior_patterns: Identified behavior patterns
            current_date: Current date for seasonal considerations
            
        Returns:
            Personalized meal planning context
        """
        if current_date is None:
            current_date = date.today()
        
        context = {
            "seasonal_ingredients": self._get_seasonal_ingredients(current_date),
            "cultural_adaptations": self._get_cultural_adaptations(user_profile),
            "health_goal_optimizations": self._get_health_goal_optimizations(user_profile),
            "lifestyle_adaptations": self._get_lifestyle_adaptations(user_profile),
            "behavioral_insights": self._extract_behavioral_insights(behavior_patterns),
            "personalization_score": self._calculate_personalization_score(user_profile, behavior_patterns)
        }
        
        return context
    
    def _get_seasonal_ingredients(self, current_date: date) -> List[str]:
        """Get seasonal ingredients for current date"""
        month = current_date.month
        
        if month in [3, 4, 5]:  # Spring
            season = "spring"
        elif month in [6, 7, 8]:  # Summer
            season = "summer"
        elif month in [9, 10, 11]:  # Fall
            season = "fall"
        else:  # Winter
            season = "winter"
        
        return self.seasonal_ingredients.get(season, [])
    
    def _get_cultural_adaptations(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get cultural adaptations based on user profile"""
        cultural_background = user_profile.get("cultural_background", "western")
        
        if cultural_background in self.cultural_meal_patterns:
            return self.cultural_meal_patterns[cultural_background]
        
        return self.cultural_meal_patterns.get("mediterranean", {})  # Default
    
    def _get_health_goal_optimizations(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get health goal optimizations based on user profile"""
        fitness_goal = user_profile.get("fitness_goal", "general_fitness")
        
        if fitness_goal in self.health_goal_optimizations:
            return self.health_goal_optimizations[fitness_goal]
        
        return self.health_goal_optimizations.get("weight_loss", {})  # Default
    
    def _get_lifestyle_adaptations(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get lifestyle adaptations based on user profile"""
        lifestyle = user_profile.get("lifestyle", "general")
        
        if lifestyle in self.lifestyle_adaptations:
            return self.lifestyle_adaptations[lifestyle]
        
        return self.lifestyle_adaptations.get("busy_professional", {})  # Default
    
    def _extract_behavioral_insights(self, behavior_patterns: List[UserBehaviorPattern]) -> Dict[str, Any]:
        """Extract insights from behavior patterns"""
        insights = {
            "cuisine_preferences": [],
            "meal_timing_preferences": {},
            "ingredient_preferences": [],
            "cooking_preferences": [],
            "confidence_levels": {}
        }
        
        for pattern in behavior_patterns:
            if pattern.pattern_type == "cuisine_preferences":
                insights["cuisine_preferences"] = pattern.pattern_data.get("preferred_cuisines", [])
                insights["confidence_levels"]["cuisine"] = pattern.confidence_score
            
            elif pattern.pattern_type == "meal_timing":
                insights["meal_timing_preferences"] = pattern.pattern_data.get("patterns", {})
                insights["confidence_levels"]["timing"] = pattern.confidence_score
            
            elif pattern.pattern_type == "ingredient_preferences":
                insights["ingredient_preferences"] = pattern.pattern_data.get("preferred_ingredients", [])
                insights["confidence_levels"]["ingredients"] = pattern.confidence_score
            
            elif pattern.pattern_type == "cooking_preferences":
                insights["cooking_preferences"] = pattern.pattern_data.get("preferred_methods", [])
                insights["confidence_levels"]["cooking"] = pattern.confidence_score
        
        return insights
    
    def _calculate_personalization_score(self, user_profile: Dict[str, Any], 
                                       behavior_patterns: List[UserBehaviorPattern]) -> float:
        """Calculate overall personalization score (0-100)"""
        score = 0
        
        # Base score from profile completeness
        profile_fields = ["age", "gender", "activity_level", "fitness_goal", "dietary_restrictions"]
        profile_completeness = sum(1 for field in profile_fields if field in user_profile and user_profile[field])
        score += (profile_completeness / len(profile_fields)) * 30
        
        # Score from behavior patterns
        if behavior_patterns:
            avg_confidence = sum(p.confidence_score for p in behavior_patterns) / len(behavior_patterns)
            score += avg_confidence * 40
        
        # Score from dietary restrictions complexity
        dietary_restrictions = user_profile.get("dietary_restrictions", [])
        if dietary_restrictions:
            score += min(len(dietary_restrictions) * 5, 30)
        
        return min(score, 100)







