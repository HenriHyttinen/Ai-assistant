"""
Advanced Nutrition Analytics Service
Provides comprehensive nutritional analysis, trends, and insights
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from models.nutrition import NutritionalLog
from models.user import User
from models.recipe import Recipe
import statistics

logger = logging.getLogger(__name__)

class NutritionAnalyticsService:
    def __init__(self):
        self.logger = logger

    def get_comprehensive_analysis(
        self, 
        user_id: str, 
        start_date: datetime, 
        end_date: datetime,
        db: Session
    ) -> Dict[str, Any]:
        """
        Get comprehensive nutritional analysis for a user over a date range
        """
        try:
            # Get nutritional logs for the period
            logs = db.query(NutritionalLog).filter(
                and_(
                    NutritionalLog.user_id == user_id,
                    NutritionalLog.log_date >= start_date.date(),
                    NutritionalLog.log_date <= end_date.date()
                )
            ).order_by(NutritionalLog.log_date).all()

            if not logs:
                return self._get_empty_analysis()

            # Calculate totals
            totals = self._calculate_totals(logs)
            
            # Get user targets
            user = db.query(User).filter(User.id == user_id).first()
            targets = self._get_user_targets(user)
            
            # Calculate progress
            progress = self._calculate_progress(totals, targets)
            
            # Calculate daily breakdown
            daily_breakdown = self._calculate_daily_breakdown(logs)
            
            # Calculate meal distribution
            meal_distribution = self._calculate_meal_distribution(logs)
            
            # Calculate trends
            trends = self._calculate_trends(daily_breakdown)
            
            # Generate AI insights
            ai_insights = self._generate_ai_insights(totals, targets, progress, trends, daily_breakdown)
            
            # Calculate nutrition score
            nutrition_score = self._calculate_nutrition_score(progress)
            
            return {
                "totals": totals,
                "targets": targets,
                "progress": progress,
                "daily_breakdown": daily_breakdown,
                "meal_distribution": meal_distribution,
                "trends": trends,
                "ai_insights": ai_insights,
                "nutrition_score": nutrition_score,
                "period_days": (end_date - start_date).days + 1,
                "logged_days": len(set(log.log_date for log in logs))
            }
            
        except Exception as e:
            self.logger.error(f"Error in comprehensive analysis: {e}")
            return self._get_empty_analysis()

    def get_weekly_analysis(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Get weekly nutritional analysis"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=6)
        return self.get_comprehensive_analysis(user_id, start_date, end_date, db)

    def get_monthly_analysis(self, user_id: str, db: Session) -> Dict[str, Any]:
        """Get monthly nutritional analysis"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=29)
        return self.get_comprehensive_analysis(user_id, start_date, end_date, db)

    def get_daily_analysis(self, user_id: str, date: datetime, db: Session) -> Dict[str, Any]:
        """Get daily nutritional analysis"""
        return self.get_comprehensive_analysis(user_id, date, date, db)

    def _calculate_totals(self, logs: List[NutritionalLog]) -> Dict[str, float]:
        """Calculate total nutrition from logs"""
        totals = {
            "calories": 0.0,
            "protein": 0.0,
            "carbs": 0.0,
            "fats": 0.0,
            "fiber": 0.0,
            "sugar": 0.0,
            "sodium": 0.0
        }
        
        for log in logs:
            totals["calories"] += log.calories or 0
            totals["protein"] += log.protein or 0
            totals["carbs"] += log.carbs or 0
            totals["fats"] += log.fats or 0
            totals["fiber"] += log.fiber or 0
            totals["sugar"] += log.sugar or 0
            totals["sodium"] += log.sodium or 0
            
        return totals

    def _get_user_targets(self, user: Optional[User]) -> Dict[str, float]:
        """Get user nutrition targets"""
        if not user or not user.nutrition_preferences:
            # Default targets
            return {
                "calories": 2000.0,
                "protein": 150.0,
                "carbs": 250.0,
                "fats": 65.0,
                "fiber": 25.0,
                "sugar": 50.0,
                "sodium": 2300.0
            }
        
        prefs = user.nutrition_preferences
        return {
            "calories": prefs.get("daily_calories", 2000.0),
            "protein": prefs.get("daily_protein", 150.0),
            "carbs": prefs.get("daily_carbs", 250.0),
            "fats": prefs.get("daily_fats", 65.0),
            "fiber": prefs.get("daily_fiber", 25.0),
            "sugar": prefs.get("daily_sugar", 50.0),
            "sodium": prefs.get("daily_sodium", 2300.0)
        }

    def _calculate_progress(self, totals: Dict[str, float], targets: Dict[str, float]) -> Dict[str, Any]:
        """Calculate progress towards targets"""
        progress = {}
        deficits = {}
        percentages = {}
        
        for nutrient in ["calories", "protein", "carbs", "fats", "fiber", "sugar", "sodium"]:
            current = totals.get(nutrient, 0)
            target = targets.get(nutrient, 0)
            
            if target > 0:
                percentage = (current / target) * 100
                deficit = target - current
            else:
                percentage = 0
                deficit = 0
                
            progress[nutrient] = {
                "current": current,
                "target": target,
                "percentage": percentage,
                "deficit": deficit,
                "surplus": max(0, current - target)
            }
            
            deficits[nutrient] = deficit
            percentages[nutrient] = percentage
            
        return {
            "progress": progress,
            "deficits": deficits,
            "percentages": percentages
        }

    def _calculate_daily_breakdown(self, logs: List[NutritionalLog]) -> List[Dict[str, Any]]:
        """Calculate daily nutrition breakdown"""
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
                    "fiber": 0,
                    "sugar": 0,
                    "sodium": 0,
                    "meals": []
                }
            
            daily_data[date_str]["calories"] += log.calories or 0
            daily_data[date_str]["protein"] += log.protein or 0
            daily_data[date_str]["carbs"] += log.carbs or 0
            daily_data[date_str]["fats"] += log.fats or 0
            daily_data[date_str]["fiber"] += log.fiber or 0
            daily_data[date_str]["sugar"] += log.sugar or 0
            daily_data[date_str]["sodium"] += log.sodium or 0
            
            # Add meal info
            daily_data[date_str]["meals"].append({
                "meal_type": log.meal_type or "unknown",
                "calories": log.calories or 0,
                "protein": log.protein or 0,
                "carbs": log.carbs or 0,
                "fats": log.fats or 0,
                "time": log.created_at.strftime("%H:%M") if log.created_at else "unknown"
            })
        
        return list(daily_data.values())

    def _calculate_meal_distribution(self, logs: List[NutritionalLog]) -> Dict[str, float]:
        """Calculate meal distribution percentages"""
        meal_totals = {
            "breakfast": 0,
            "lunch": 0,
            "dinner": 0,
            "snacks": 0
        }
        
        total_calories = 0
        
        for log in logs:
            calories = log.calories or 0
            meal_type = (log.meal_type or "snacks").lower()
            
            if meal_type in meal_totals:
                meal_totals[meal_type] += calories
            else:
                meal_totals["snacks"] += calories
                
            total_calories += calories
        
        if total_calories > 0:
            return {
                "breakfast": (meal_totals["breakfast"] / total_calories) * 100,
                "lunch": (meal_totals["lunch"] / total_calories) * 100,
                "dinner": (meal_totals["dinner"] / total_calories) * 100,
                "snacks": (meal_totals["snacks"] / total_calories) * 100
            }
        
        return meal_totals

    def _calculate_trends(self, daily_breakdown: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate nutritional trends"""
        if len(daily_breakdown) < 2:
            return {"trend": "insufficient_data", "direction": "stable"}
        
        # Calculate trends for each nutrient
        trends = {}
        for nutrient in ["calories", "protein", "carbs", "fats"]:
            values = [day[nutrient] for day in daily_breakdown]
            if len(values) >= 2:
                # Simple linear trend calculation
                first_half = values[:len(values)//2]
                second_half = values[len(values)//2:]
                
                first_avg = statistics.mean(first_half)
                second_avg = statistics.mean(second_half)
                
                if second_avg > first_avg * 1.05:
                    trends[nutrient] = "increasing"
                elif second_avg < first_avg * 0.95:
                    trends[nutrient] = "decreasing"
                else:
                    trends[nutrient] = "stable"
            else:
                trends[nutrient] = "stable"
        
        # Overall trend
        calorie_trend = trends.get("calories", "stable")
        return {
            "trends": trends,
            "overall_trend": calorie_trend,
            "consistency": self._calculate_consistency(daily_breakdown)
        }

    def _calculate_consistency(self, daily_breakdown: List[Dict[str, Any]]) -> float:
        """Calculate consistency score (0-100)"""
        if len(daily_breakdown) < 2:
            return 0
        
        calories = [day["calories"] for day in daily_breakdown]
        if not calories:
            return 0
            
        mean_calories = statistics.mean(calories)
        if mean_calories == 0:
            return 0
            
        # Calculate coefficient of variation (lower is more consistent)
        std_dev = statistics.stdev(calories)
        cv = (std_dev / mean_calories) * 100
        
        # Convert to consistency score (0-100)
        consistency = max(0, 100 - cv)
        return min(100, consistency)

    def _generate_ai_insights(
        self, 
        totals: Dict[str, float], 
        targets: Dict[str, float], 
        progress: Dict[str, Any],
        trends: Dict[str, Any],
        daily_breakdown: List[Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Generate AI-powered nutritional insights"""
        insights = {
            "achievements": [],
            "concerns": [],
            "suggestions": [],
            "trends": []
        }
        
        # Analyze achievements
        for nutrient, data in progress["progress"].items():
            if data["percentage"] >= 90:
                insights["achievements"].append(
                    f"Great job meeting your {nutrient} target! ({data['percentage']:.1f}%)"
                )
        
        # Analyze concerns
        for nutrient, data in progress["progress"].items():
            if data["percentage"] < 50:
                insights["concerns"].append(
                    f"Low {nutrient} intake - only {data['percentage']:.1f}% of target"
                )
            elif data["percentage"] > 150:
                insights["concerns"].append(
                    f"High {nutrient} intake - {data['percentage']:.1f}% of target"
                )
        
        # Generate suggestions
        if progress["percentages"]["protein"] < 80:
            insights["suggestions"].append("Consider adding more protein-rich foods like lean meats, beans, or Greek yogurt")
        
        if progress["percentages"]["fiber"] < 70:
            insights["suggestions"].append("Increase fiber intake with more vegetables, fruits, and whole grains")
        
        if progress["percentages"]["sodium"] > 120:
            insights["suggestions"].append("Consider reducing sodium intake by choosing fresh foods over processed ones")
        
        # Analyze trends
        for nutrient, trend in trends["trends"].items():
            if trend == "increasing":
                insights["trends"].append(f"{nutrient.capitalize()} intake is trending upward")
            elif trend == "decreasing":
                insights["trends"].append(f"{nutrient.capitalize()} intake is trending downward")
        
        # Consistency insights
        consistency = trends.get("consistency", 0)
        if consistency > 80:
            insights["achievements"].append("Excellent consistency in your eating patterns!")
        elif consistency < 50:
            insights["concerns"].append("Inconsistent eating patterns - try to maintain regular meal times")
        
        return insights

    def _calculate_nutrition_score(self, progress: Dict[str, Any]) -> int:
        """Calculate overall nutrition score (0-100)"""
        percentages = progress["percentages"]
        
        # Weight different nutrients
        weights = {
            "calories": 0.3,
            "protein": 0.25,
            "carbs": 0.2,
            "fats": 0.15,
            "fiber": 0.1
        }
        
        weighted_score = 0
        total_weight = 0
        
        for nutrient, weight in weights.items():
            if nutrient in percentages:
                # Score based on how close to 100% (optimal)
                percentage = percentages[nutrient]
                if percentage <= 100:
                    score = percentage
                else:
                    # Penalty for exceeding target
                    score = max(0, 100 - (percentage - 100) * 0.5)
                
                weighted_score += score * weight
                total_weight += weight
        
        if total_weight > 0:
            final_score = weighted_score / total_weight
            return min(100, max(0, int(final_score)))
        
        return 0

    def _get_empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis structure"""
        return {
            "totals": {
                "calories": 0,
                "protein": 0,
                "carbs": 0,
                "fats": 0,
                "fiber": 0,
                "sugar": 0,
                "sodium": 0
            },
            "targets": {
                "calories": 2000,
                "protein": 150,
                "carbs": 250,
                "fats": 65,
                "fiber": 25,
                "sugar": 50,
                "sodium": 2300
            },
            "progress": {
                "progress": {},
                "deficits": {},
                "percentages": {}
            },
            "daily_breakdown": [],
            "meal_distribution": {
                "breakfast": 0,
                "lunch": 0,
                "dinner": 0,
                "snacks": 0
            },
            "trends": {
                "trends": {},
                "overall_trend": "stable",
                "consistency": 0
            },
            "ai_insights": {
                "achievements": ["No data available yet"],
                "concerns": ["Please log some meals to see analysis"],
                "suggestions": ["Start by logging your daily meals"],
                "trends": []
            },
            "nutrition_score": 0,
            "period_days": 0,
            "logged_days": 0
        }


