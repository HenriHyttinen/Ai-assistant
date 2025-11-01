"""
AI Nutritional Analysis Service
Provides comprehensive AI-driven nutritional summaries with achievements, concerns, and balance analysis
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import date, timedelta
from sqlalchemy.orm import Session

from models.nutrition import NutritionalLog, UserNutritionPreferences
from models.health_profile import HealthProfile
from ai.nutrition_ai import NutritionAI

logger = logging.getLogger(__name__)

class AINutritionalAnalysisService:
    """Service for AI-driven nutritional analysis and summaries"""
    
    def __init__(self):
        self.nutrition_ai = NutritionAI()
    
    def generate_comprehensive_analysis(self, db: Session, user_id: int, 
                                      start_date: date, end_date: date, 
                                      analysis_type: str = "daily") -> Dict[str, Any]:
        """
        Generate comprehensive AI nutritional analysis with achievements, concerns, and balance analysis
        """
        try:
            # Get nutritional data
            nutritional_data = self._get_nutritional_data(db, user_id, start_date, end_date)
            
            # Get user preferences and health profile
            user_preferences = self._get_user_preferences(db, user_id)
            health_profile = self._get_health_profile(db, user_id)
            
            # Generate AI insights
            ai_insights = self._generate_ai_insights(nutritional_data, user_preferences, health_profile, analysis_type)
            
            # Generate balance analysis
            balance_analysis = self._generate_balance_analysis(nutritional_data, user_preferences)
            
            # Generate achievements
            achievements = self._generate_achievements(nutritional_data, user_preferences, health_profile)
            
            # Generate concerns
            concerns = self._generate_concerns(nutritional_data, user_preferences, health_profile)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(nutritional_data, user_preferences, health_profile)
            
            return {
                "analysis_type": analysis_type,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days_analyzed": (end_date - start_date).days + 1
                },
                "nutritional_summary": nutritional_data,
                "achievements": achievements,
                "concerns": concerns,
                "balance_analysis": balance_analysis,
                "ai_insights": ai_insights,
                "recommendations": recommendations,
                "user_context": {
                    "fitness_goal": health_profile.fitness_goal if health_profile else None,
                    "activity_level": health_profile.activity_level if health_profile else None,
                    "dietary_preferences": user_preferences.get("dietary_preferences", []),
                    "allergies": user_preferences.get("allergies", [])
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating comprehensive nutritional analysis: {str(e)}")
            return self._generate_fallback_analysis()
    
    def _get_nutritional_data(self, db: Session, user_id: int, start_date: date, end_date: date) -> Dict[str, Any]:
        """Get nutritional data for the period"""
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
        total_fiber = sum(log.fiber for log in logs)
        total_sugar = sum(log.sugar for log in logs)
        total_sodium = sum(log.sodium for log in logs)
        
        # Calculate daily averages
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
        
        # Get meal distribution
        meal_distribution = self._analyze_meal_distribution(logs)
        
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
            "meal_distribution": meal_distribution,
            "data_completeness": {
                "logged_days": len(set(log.log_date for log in logs)),
                "total_days": days_in_period,
                "completion_rate": (len(set(log.log_date for log in logs)) / days_in_period) * 100 if days_in_period > 0 else 0
            }
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
    
    def _analyze_meal_distribution(self, logs: List[NutritionalLog]) -> Dict[str, Any]:
        """Analyze meal distribution patterns"""
        meal_totals = {}
        meal_counts = {}
        
        for log in logs:
            meal_type = log.meal_type
            if meal_type not in meal_totals:
                meal_totals[meal_type] = {
                    "calories": 0,
                    "protein": 0,
                    "carbs": 0,
                    "fats": 0
                }
                meal_counts[meal_type] = 0
            
            meal_totals[meal_type]["calories"] += log.calories
            meal_totals[meal_type]["protein"] += log.protein
            meal_totals[meal_type]["carbs"] += log.carbs
            meal_totals[meal_type]["fats"] += log.fats
            meal_counts[meal_type] += 1
        
        # Calculate averages
        meal_averages = {}
        for meal_type, totals in meal_totals.items():
            count = meal_counts[meal_type]
            meal_averages[meal_type] = {
                "calories": totals["calories"] / count if count > 0 else 0,
                "protein": totals["protein"] / count if count > 0 else 0,
                "carbs": totals["carbs"] / count if count > 0 else 0,
                "fats": totals["fats"] / count if count > 0 else 0,
                "frequency": count
            }
        
        return meal_averages
    
    def _generate_ai_insights(self, nutritional_data: Dict[str, Any], 
                            user_preferences: Dict[str, Any], 
                            health_profile: Optional[HealthProfile],
                            analysis_type: str) -> Dict[str, Any]:
        """Generate AI-powered insights using OpenAI"""
        try:
            # Prepare data for AI analysis
            ai_data = {
                "nutritional_data": nutritional_data,
                "user_preferences": user_preferences,
                "health_profile": {
                    "fitness_goal": health_profile.fitness_goal if health_profile else None,
                    "activity_level": health_profile.activity_level if health_profile else None,
                    "weight": health_profile.weight if health_profile else None,
                    "height": health_profile.height if health_profile else None
                },
                "analysis_type": analysis_type
            }
            
            # Use the existing nutrition AI to generate insights
            insights = self.nutrition_ai.generate_nutritional_insights(
                nutritional_data["daily_averages"], 
                user_preferences
            )
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating AI insights: {str(e)}")
            return {
                "achievements": ["Data analysis completed successfully"],
                "concerns": ["Unable to generate AI insights at this time"],
                "suggestions": ["Continue tracking your nutrition for better insights"]
            }
    
    def _generate_balance_analysis(self, nutritional_data: Dict[str, Any], 
                                 user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Generate macronutrient balance analysis"""
        daily_avg = nutritional_data["daily_averages"]
        targets = {
            "calories": user_preferences["daily_calorie_target"],
            "protein": user_preferences["protein_target"],
            "carbs": user_preferences["carbs_target"],
            "fats": user_preferences["fats_target"]
        }
        
        # Calculate percentages
        percentages = {}
        for nutrient in ["calories", "protein", "carbs", "fats"]:
            target = targets[nutrient]
            actual = daily_avg[nutrient]
            percentages[nutrient] = (actual / target) * 100 if target > 0 else 0
        
        # Calculate macronutrient distribution
        protein_calories = daily_avg["protein"] * 4
        carbs_calories = daily_avg["carbs"] * 4
        fats_calories = daily_avg["fats"] * 9
        total_macro_calories = protein_calories + carbs_calories + fats_calories
        
        if total_macro_calories > 0:
            macro_distribution = {
                "protein": (protein_calories / total_macro_calories) * 100,
                "carbs": (carbs_calories / total_macro_calories) * 100,
                "fats": (fats_calories / total_macro_calories) * 100
            }
        else:
            macro_distribution = {"protein": 0, "carbs": 0, "fats": 0}
        
        # Ideal distribution (based on general recommendations)
        ideal_distribution = {
            "protein": 20,  # 20-25%
            "carbs": 50,    # 45-65%
            "fats": 30      # 20-35%
        }
        
        # Calculate balance score
        balance_score = self._calculate_balance_score(macro_distribution, ideal_distribution)
        
        return {
            "target_percentages": percentages,
            "macro_distribution": macro_distribution,
            "ideal_distribution": ideal_distribution,
            "balance_score": balance_score,
            "balance_assessment": self._assess_balance(macro_distribution, ideal_distribution)
        }
    
    def _calculate_balance_score(self, actual: Dict[str, float], ideal: Dict[str, float]) -> float:
        """Calculate overall balance score (0-100)"""
        total_deviation = 0
        for nutrient in ["protein", "carbs", "fats"]:
            deviation = abs(actual[nutrient] - ideal[nutrient])
            total_deviation += deviation
        
        # Convert to score (lower deviation = higher score)
        max_possible_deviation = 200  # Maximum possible deviation
        score = max(0, 100 - (total_deviation / max_possible_deviation) * 100)
        return round(score, 1)
    
    def _assess_balance(self, actual: Dict[str, float], ideal: Dict[str, float]) -> str:
        """Assess macronutrient balance"""
        balance_score = self._calculate_balance_score(actual, ideal)
        
        if balance_score >= 80:
            return "Excellent balance"
        elif balance_score >= 60:
            return "Good balance with minor adjustments needed"
        elif balance_score >= 40:
            return "Moderate imbalance - consider adjustments"
        else:
            return "Significant imbalance - major adjustments recommended"
    
    def _generate_achievements(self, nutritional_data: Dict[str, Any], 
                             user_preferences: Dict[str, Any], 
                             health_profile: Optional[HealthProfile]) -> List[Dict[str, Any]]:
        """Generate achievement highlights"""
        achievements = []
        daily_avg = nutritional_data["daily_averages"]
        targets = {
            "calories": user_preferences["daily_calorie_target"],
            "protein": user_preferences["protein_target"],
            "carbs": user_preferences["carbs_target"],
            "fats": user_preferences["fats_target"]
        }
        
        # Calorie target achievement
        calorie_percentage = (daily_avg["calories"] / targets["calories"]) * 100 if targets["calories"] > 0 else 0
        if 95 <= calorie_percentage <= 105:
            achievements.append({
                "title": "Perfect Calorie Target",
                "description": f"Hit your daily calorie target of {targets['calories']} calories",
                "icon": "target",
                "category": "calories"
            })
        
        # Protein achievement
        protein_percentage = (daily_avg["protein"] / targets["protein"]) * 100 if targets["protein"] > 0 else 0
        if protein_percentage >= 90:
            achievements.append({
                "title": "Protein Power",
                "description": f"Met {protein_percentage:.0f}% of your protein target",
                "icon": "muscle",
                "category": "protein"
            })
        
        # Fiber achievement
        if daily_avg["fiber"] >= 25:
            achievements.append({
                "title": "Fiber Champion",
                "description": f"Consumed {daily_avg['fiber']:.1f}g of fiber (recommended: 25g+)",
                "icon": "leaf",
                "category": "fiber"
            })
        
        # Consistency achievement
        completion_rate = nutritional_data["data_completeness"]["completion_rate"]
        if completion_rate >= 90:
            achievements.append({
                "title": "Consistent Tracker",
                "description": f"Logged nutrition {completion_rate:.0f}% of the time",
                "icon": "calendar",
                "category": "consistency"
            })
        
        # Meal variety achievement
        meal_distribution = nutritional_data["meal_distribution"]
        if len(meal_distribution) >= 3:
            achievements.append({
                "title": "Meal Variety",
                "description": f"Consumed {len(meal_distribution)} different meal types",
                "icon": "variety",
                "category": "variety"
            })
        
        return achievements
    
    def _generate_concerns(self, nutritional_data: Dict[str, Any], 
                          user_preferences: Dict[str, Any], 
                          health_profile: Optional[HealthProfile]) -> List[Dict[str, Any]]:
        """Generate concern highlights"""
        concerns = []
        daily_avg = nutritional_data["daily_averages"]
        targets = {
            "calories": user_preferences["daily_calorie_target"],
            "protein": user_preferences["protein_target"],
            "carbs": user_preferences["carbs_target"],
            "fats": user_preferences["fats_target"]
        }
        
        # Calorie concerns
        calorie_percentage = (daily_avg["calories"] / targets["calories"]) * 100 if targets["calories"] > 0 else 0
        if calorie_percentage < 70:
            concerns.append({
                "title": "Low Calorie Intake",
                "description": f"Only {calorie_percentage:.0f}% of calorie target - consider increasing portions",
                "severity": "high",
                "category": "calories"
            })
        elif calorie_percentage > 130:
            concerns.append({
                "title": "High Calorie Intake",
                "description": f"{calorie_percentage:.0f}% of calorie target - consider reducing portions",
                "severity": "medium",
                "category": "calories"
            })
        
        # Protein concerns
        protein_percentage = (daily_avg["protein"] / targets["protein"]) * 100 if targets["protein"] > 0 else 0
        if protein_percentage < 70:
            concerns.append({
                "title": "Low Protein Intake",
                "description": f"Only {protein_percentage:.0f}% of protein target - add lean proteins",
                "severity": "medium",
                "category": "protein"
            })
        
        # Fiber concerns
        if daily_avg["fiber"] < 15:
            concerns.append({
                "title": "Low Fiber Intake",
                "description": f"Only {daily_avg['fiber']:.1f}g fiber - add more fruits, vegetables, and whole grains",
                "severity": "medium",
                "category": "fiber"
            })
        
        # Sodium concerns
        if daily_avg["sodium"] > 2300:
            concerns.append({
                "title": "High Sodium Intake",
                "description": f"{daily_avg['sodium']:.0f}mg sodium - consider reducing processed foods",
                "severity": "medium",
                "category": "sodium"
            })
        
        # Sugar concerns
        if daily_avg["sugar"] > 50:
            concerns.append({
                "title": "High Sugar Intake",
                "description": f"{daily_avg['sugar']:.1f}g sugar - consider reducing added sugars",
                "severity": "low",
                "category": "sugar"
            })
        
        return concerns
    
    def _generate_recommendations(self, nutritional_data: Dict[str, Any], 
                                user_preferences: Dict[str, Any], 
                                health_profile: Optional[HealthProfile]) -> List[Dict[str, Any]]:
        """Generate personalized recommendations"""
        recommendations = []
        daily_avg = nutritional_data["daily_averages"]
        targets = {
            "calories": user_preferences["daily_calorie_target"],
            "protein": user_preferences["protein_target"],
            "carbs": user_preferences["carbs_target"],
            "fats": user_preferences["fats_target"]
        }
        
        # Calorie recommendations
        calorie_percentage = (daily_avg["calories"] / targets["calories"]) * 100 if targets["calories"] > 0 else 0
        if calorie_percentage < 80:
            recommendations.append({
                "title": "Increase Calorie Intake",
                "description": "Add healthy snacks between meals or increase portion sizes",
                "priority": "high",
                "category": "calories"
            })
        elif calorie_percentage > 120:
            recommendations.append({
                "title": "Optimize Calorie Intake",
                "description": "Focus on nutrient-dense, lower-calorie foods",
                "priority": "medium",
                "category": "calories"
            })
        
        # Protein recommendations
        protein_percentage = (daily_avg["protein"] / targets["protein"]) * 100 if targets["protein"] > 0 else 0
        if protein_percentage < 80:
            recommendations.append({
                "title": "Boost Protein Intake",
                "description": "Include lean proteins like chicken, fish, legumes, or Greek yogurt",
                "priority": "high",
                "category": "protein"
            })
        
        # Fiber recommendations
        if daily_avg["fiber"] < 20:
            recommendations.append({
                "title": "Increase Fiber Intake",
                "description": "Add more fruits, vegetables, whole grains, and legumes",
                "priority": "medium",
                "category": "fiber"
            })
        
        # Meal timing recommendations
        meal_distribution = nutritional_data["meal_distribution"]
        if "breakfast" not in meal_distribution:
            recommendations.append({
                "title": "Add Breakfast",
                "description": "Start your day with a balanced breakfast for better energy",
                "priority": "medium",
                "category": "meal_timing"
            })
        
        # Hydration recommendation
        recommendations.append({
            "title": "Stay Hydrated",
            "description": "Aim for 8-10 glasses of water daily for optimal health",
            "priority": "low",
            "category": "hydration"
        })
        
        return recommendations
    
    def _generate_fallback_analysis(self) -> Dict[str, Any]:
        """Generate fallback analysis when AI is unavailable"""
        return {
            "analysis_type": "fallback",
            "achievements": [
                {
                    "title": "Data Collection",
                    "description": "Successfully collected nutritional data",
                    "icon": "data",
                    "category": "system"
                }
            ],
            "concerns": [
                {
                    "title": "Limited Analysis",
                    "description": "AI analysis unavailable - basic tracking only",
                    "severity": "low",
                    "category": "system"
                }
            ],
            "balance_analysis": {
                "balance_score": 0,
                "balance_assessment": "Analysis unavailable"
            },
            "ai_insights": {
                "achievements": ["Data tracking active"],
                "concerns": ["AI analysis temporarily unavailable"],
                "suggestions": ["Continue logging meals for better insights"]
            },
            "recommendations": [
                {
                    "title": "Continue Tracking",
                    "description": "Keep logging your meals for comprehensive analysis",
                    "priority": "medium",
                    "category": "tracking"
                }
            ]
        }








