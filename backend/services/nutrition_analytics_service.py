"""
Advanced Nutrition Analytics Service
Provides comprehensive nutrition analytics, trends, and insights
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc, extract
from models.nutrition import NutritionalLog, MealPlan, MealPlanMeal
from models.user import User
from models.recipe import Recipe
import pandas as pd
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

class NutritionAnalyticsService:
    def __init__(self):
        self.logger = logger

    def get_nutrition_trends(self, db: Session, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get nutrition trends over specified days"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get nutritional logs for the period
            logs = db.query(NutritionalLog).filter(
                and_(
                    NutritionalLog.user_id == user_id,
                    NutritionalLog.date >= start_date,
                    NutritionalLog.date <= end_date
                )
            ).order_by(NutritionalLog.date).all()
            
            if not logs:
                return self._empty_trends_response(days)
            
            # Convert to DataFrame for easier analysis
            data = []
            for log in logs:
                data.append({
                    'date': log.date,
                    'calories': log.calories or 0,
                    'protein': log.protein or 0,
                    'carbs': log.carbs or 0,
                    'fat': log.fat or 0,
                    'fiber': log.fiber or 0,
                    'sugar': log.sugar or 0,
                    'sodium': log.sodium or 0,
                    'vitamin_c': log.vitamin_c or 0,
                    'vitamin_a': log.vitamin_a or 0,
                    'calcium': log.calcium or 0,
                    'iron': log.iron or 0
                })
            
            df = pd.DataFrame(data)
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')
            
            # Calculate daily totals
            daily_totals = df.resample('D').sum()
            
            # Calculate trends
            trends = {}
            for nutrient in ['calories', 'protein', 'carbs', 'fat', 'fiber', 'sugar', 'sodium']:
                if nutrient in daily_totals.columns:
                    values = daily_totals[nutrient].values
                    if len(values) > 1:
                        # Calculate trend direction and strength
                        trend_slope = np.polyfit(range(len(values)), values, 1)[0]
                        trend_direction = 'increasing' if trend_slope > 0 else 'decreasing' if trend_slope < 0 else 'stable'
                        trend_strength = abs(trend_slope)
                        
                        trends[nutrient] = {
                            'direction': trend_direction,
                            'strength': trend_strength,
                            'current_avg': float(np.mean(values[-7:]) if len(values) >= 7 else np.mean(values)),
                            'previous_avg': float(np.mean(values[:-7]) if len(values) >= 14 else np.mean(values)),
                            'change_percent': self._calculate_change_percent(values),
                            'daily_values': values.tolist(),
                            'dates': daily_totals.index.strftime('%Y-%m-%d').tolist()
                        }
            
            return {
                'period_days': days,
                'total_days_logged': len(daily_totals),
                'trends': trends,
                'summary': self._calculate_summary_stats(daily_totals)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting nutrition trends: {str(e)}")
            raise

    def get_nutrition_insights(self, db: Session, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get AI-powered nutrition insights and recommendations"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get nutritional logs
            logs = db.query(NutritionalLog).filter(
                and_(
                    NutritionalLog.user_id == user_id,
                    NutritionalLog.date >= start_date,
                    NutritionalLog.date <= end_date
                )
            ).all()
            
            if not logs:
                return self._empty_insights_response()
            
            # Calculate averages
            total_days = len(set(log.date.date() for log in logs))
            avg_calories = sum(log.calories or 0 for log in logs) / total_days
            avg_protein = sum(log.protein or 0 for log in logs) / total_days
            avg_carbs = sum(log.carbs or 0 for log in logs) / total_days
            avg_fat = sum(log.fat or 0 for log in logs) / total_days
            avg_fiber = sum(log.fiber or 0 for log in logs) / total_days
            avg_sodium = sum(log.sodium or 0 for log in logs) / total_days
            
            insights = []
            recommendations = []
            
            # Calorie analysis
            if avg_calories < 1200:
                insights.append({
                    'type': 'warning',
                    'title': 'Low Calorie Intake',
                    'message': f'Your average daily calorie intake ({avg_calories:.0f}) is quite low. Consider increasing portion sizes or adding healthy snacks.',
                    'priority': 'high'
                })
                recommendations.append('Add nutrient-dense snacks like nuts, fruits, or yogurt to increase calorie intake.')
            elif avg_calories > 3000:
                insights.append({
                    'type': 'warning',
                    'title': 'High Calorie Intake',
                    'message': f'Your average daily calorie intake ({avg_calories:.0f}) is quite high. Consider reducing portion sizes or choosing lower-calorie options.',
                    'priority': 'high'
                })
                recommendations.append('Focus on portion control and choose more vegetables and lean proteins.')
            
            # Protein analysis
            protein_ratio = avg_protein / avg_calories * 100 if avg_calories > 0 else 0
            if protein_ratio < 10:
                insights.append({
                    'type': 'info',
                    'title': 'Low Protein Intake',
                    'message': f'Your protein intake is {protein_ratio:.1f}% of total calories. Aim for 15-25% for optimal health.',
                    'priority': 'medium'
                })
                recommendations.append('Include more lean meats, fish, eggs, beans, or dairy products in your meals.')
            elif protein_ratio > 35:
                insights.append({
                    'type': 'info',
                    'title': 'High Protein Intake',
                    'message': f'Your protein intake is {protein_ratio:.1f}% of total calories. This is quite high - ensure you\'re getting enough carbs and fats.',
                    'priority': 'low'
                })
            
            # Fiber analysis
            if avg_fiber < 25:
                insights.append({
                    'type': 'info',
                    'title': 'Low Fiber Intake',
                    'message': f'Your daily fiber intake ({avg_fiber:.1f}g) is below the recommended 25-35g. Add more whole grains, fruits, and vegetables.',
                    'priority': 'medium'
                })
                recommendations.append('Include more whole grains, fruits, vegetables, and legumes in your diet.')
            
            # Sodium analysis
            if avg_sodium > 2300:
                insights.append({
                    'type': 'warning',
                    'title': 'High Sodium Intake',
                    'message': f'Your daily sodium intake ({avg_sodium:.0f}mg) exceeds the recommended 2300mg limit.',
                    'priority': 'high'
                })
                recommendations.append('Reduce processed foods, canned goods, and added salt. Choose fresh ingredients when possible.')
            
            # Consistency analysis
            calorie_variance = self._calculate_variance([log.calories or 0 for log in logs])
            if calorie_variance > 500:
                insights.append({
                    'type': 'info',
                    'title': 'Inconsistent Eating Patterns',
                    'message': 'Your calorie intake varies significantly day to day. Try to maintain more consistent eating patterns.',
                    'priority': 'medium'
                })
                recommendations.append('Plan your meals in advance and try to eat at regular times.')
            
            # Positive insights
            if avg_fiber >= 25:
                insights.append({
                    'type': 'success',
                    'title': 'Great Fiber Intake',
                    'message': f'Excellent! Your daily fiber intake ({avg_fiber:.1f}g) meets the recommended guidelines.',
                    'priority': 'low'
                })
            
            if 15 <= protein_ratio <= 25:
                insights.append({
                    'type': 'success',
                    'title': 'Balanced Protein Intake',
                    'message': f'Your protein intake ({protein_ratio:.1f}% of calories) is well-balanced.',
                    'priority': 'low'
                })
            
            return {
                'insights': insights,
                'recommendations': recommendations,
                'summary': {
                    'avg_calories': round(avg_calories, 1),
                    'avg_protein': round(avg_protein, 1),
                    'avg_carbs': round(avg_carbs, 1),
                    'avg_fat': round(avg_fat, 1),
                    'avg_fiber': round(avg_fiber, 1),
                    'avg_sodium': round(avg_sodium, 1),
                    'total_days': total_days
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error getting nutrition insights: {str(e)}")
            raise

    def get_meal_pattern_analysis(self, db: Session, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Analyze meal patterns and timing"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Get meal plan meals
            meals = db.query(MealPlanMeal).join(MealPlan).filter(
                and_(
                    MealPlan.user_id == user_id,
                    MealPlanMeal.created_at >= start_date,
                    MealPlanMeal.created_at <= end_date
                )
            ).all()
            
            if not meals:
                return self._empty_meal_pattern_response()
            
            # Analyze meal timing
            meal_times = []
            meal_types = defaultdict(int)
            calories_by_meal = defaultdict(list)
            
            for meal in meals:
                if meal.created_at:
                    hour = meal.created_at.hour
                    meal_times.append(hour)
                    meal_types[meal.meal_type] += 1
                    calories_by_meal[meal.meal_type].append(meal.calories or 0)
            
            # Calculate patterns
            avg_breakfast_time = self._calculate_avg_meal_time(meal_times, 5, 11)  # 5 AM - 11 AM
            avg_lunch_time = self._calculate_avg_meal_time(meal_times, 11, 16)    # 11 AM - 4 PM
            avg_dinner_time = self._calculate_avg_meal_time(meal_times, 16, 22)   # 4 PM - 10 PM
            
            # Calculate calorie distribution
            calorie_distribution = {}
            for meal_type, calories_list in calories_by_meal.items():
                if calories_list:
                    calorie_distribution[meal_type] = {
                        'avg_calories': round(np.mean(calories_list), 1),
                        'total_meals': len(calories_list),
                        'percentage': round(len(calories_list) / len(meals) * 100, 1)
                    }
            
            # Meal consistency analysis
            total_meals = len(meals)
            breakfast_consistency = meal_types.get('breakfast', 0) / days * 100
            lunch_consistency = meal_types.get('lunch', 0) / days * 100
            dinner_consistency = meal_types.get('dinner', 0) / days * 100
            
            return {
                'total_meals_logged': total_meals,
                'avg_meals_per_day': round(total_meals / days, 1),
                'meal_timing': {
                    'breakfast_avg_time': avg_breakfast_time,
                    'lunch_avg_time': avg_lunch_time,
                    'dinner_avg_time': avg_dinner_time
                },
                'meal_consistency': {
                    'breakfast': round(breakfast_consistency, 1),
                    'lunch': round(lunch_consistency, 1),
                    'dinner': round(dinner_consistency, 1)
                },
                'calorie_distribution': calorie_distribution,
                'meal_type_frequency': dict(meal_types)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting meal pattern analysis: {str(e)}")
            raise

    def get_nutrition_goals_progress(self, db: Session, user_id: str, days: int = 30) -> Dict[str, Any]:
        """Get progress toward nutrition goals"""
        try:
            # This would integrate with user goals/preferences
            # For now, we'll use general recommendations
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            logs = db.query(NutritionalLog).filter(
                and_(
                    NutritionalLog.user_id == user_id,
                    NutritionalLog.date >= start_date,
                    NutritionalLog.date <= end_date
                )
            ).all()
            
            if not logs:
                return self._empty_goals_response()
            
            # Calculate averages
            total_days = len(set(log.date.date() for log in logs))
            avg_calories = sum(log.calories or 0 for log in logs) / total_days
            avg_protein = sum(log.protein or 0 for log in logs) / total_days
            avg_fiber = sum(log.fiber or 0 for log in logs) / total_days
            avg_sodium = sum(log.sodium or 0 for log in logs) / total_days
            
            # Define goals (these would come from user preferences)
            goals = {
                'calories': {'target': 2000, 'min': 1500, 'max': 2500},
                'protein': {'target': 150, 'min': 100, 'max': 200},
                'fiber': {'target': 30, 'min': 25, 'max': 35},
                'sodium': {'target': 2000, 'min': 1000, 'max': 2300}
            }
            
            progress = {}
            for nutrient, goal in goals.items():
                current = locals()[f'avg_{nutrient}']
                target = goal['target']
                min_val = goal['min']
                max_val = goal['max']
                
                if min_val <= current <= max_val:
                    status = 'on_track'
                    progress_percent = 100
                elif current < min_val:
                    status = 'below_target'
                    progress_percent = max(0, (current / min_val) * 100)
                else:
                    status = 'above_target'
                    progress_percent = min(100, (max_val / current) * 100)
                
                progress[nutrient] = {
                    'current': round(current, 1),
                    'target': target,
                    'min': min_val,
                    'max': max_val,
                    'status': status,
                    'progress_percent': round(progress_percent, 1)
                }
            
            return {
                'goals': goals,
                'progress': progress,
                'overall_status': self._calculate_overall_status(progress),
                'days_tracked': total_days
            }
            
        except Exception as e:
            self.logger.error(f"Error getting nutrition goals progress: {str(e)}")
            raise

    def _empty_trends_response(self, days: int) -> Dict[str, Any]:
        """Return empty response for trends when no data"""
        return {
            'period_days': days,
            'total_days_logged': 0,
            'trends': {},
            'summary': {
                'avg_calories': 0,
                'avg_protein': 0,
                'avg_carbs': 0,
                'avg_fat': 0,
                'avg_fiber': 0,
                'avg_sodium': 0
            }
        }

    def _empty_insights_response(self) -> Dict[str, Any]:
        """Return empty response for insights when no data"""
        return {
            'insights': [],
            'recommendations': [],
            'summary': {
                'avg_calories': 0,
                'avg_protein': 0,
                'avg_carbs': 0,
                'avg_fat': 0,
                'avg_fiber': 0,
                'avg_sodium': 0,
                'total_days': 0
            }
        }

    def _empty_meal_pattern_response(self) -> Dict[str, Any]:
        """Return empty response for meal patterns when no data"""
        return {
            'total_meals_logged': 0,
            'avg_meals_per_day': 0,
            'meal_timing': {},
            'meal_consistency': {},
            'calorie_distribution': {},
            'meal_type_frequency': {}
        }

    def _empty_goals_response(self) -> Dict[str, Any]:
        """Return empty response for goals when no data"""
        return {
            'goals': {},
            'progress': {},
            'overall_status': 'no_data',
            'days_tracked': 0
        }

    def _calculate_change_percent(self, values: List[float]) -> float:
        """Calculate percentage change in values"""
        if len(values) < 2:
            return 0.0
        
        recent_avg = np.mean(values[-7:]) if len(values) >= 7 else values[-1]
        previous_avg = np.mean(values[:-7]) if len(values) >= 14 else values[0]
        
        if previous_avg == 0:
            return 0.0
        
        return round(((recent_avg - previous_avg) / previous_avg) * 100, 1)

    def _calculate_summary_stats(self, daily_totals: pd.DataFrame) -> Dict[str, float]:
        """Calculate summary statistics"""
        return {
            'avg_calories': round(daily_totals['calories'].mean(), 1) if 'calories' in daily_totals.columns else 0,
            'avg_protein': round(daily_totals['protein'].mean(), 1) if 'protein' in daily_totals.columns else 0,
            'avg_carbs': round(daily_totals['carbs'].mean(), 1) if 'carbs' in daily_totals.columns else 0,
            'avg_fat': round(daily_totals['fat'].mean(), 1) if 'fat' in daily_totals.columns else 0,
            'avg_fiber': round(daily_totals['fiber'].mean(), 1) if 'fiber' in daily_totals.columns else 0,
            'avg_sodium': round(daily_totals['sodium'].mean(), 1) if 'sodium' in daily_totals.columns else 0
        }

    def _calculate_variance(self, values: List[float]) -> float:
        """Calculate variance in values"""
        if len(values) < 2:
            return 0.0
        return float(np.var(values))

    def _calculate_avg_meal_time(self, meal_times: List[int], start_hour: int, end_hour: int) -> Optional[str]:
        """Calculate average meal time for a given period"""
        filtered_times = [t for t in meal_times if start_hour <= t < end_hour]
        if not filtered_times:
            return None
        
        avg_hour = np.mean(filtered_times)
        hour = int(avg_hour)
        minute = int((avg_hour - hour) * 60)
        return f"{hour:02d}:{minute:02d}"

    def _calculate_overall_status(self, progress: Dict[str, Any]) -> str:
        """Calculate overall goal status"""
        if not progress:
            return 'no_data'
        
        on_track_count = sum(1 for p in progress.values() if p['status'] == 'on_track')
        total_count = len(progress)
        
        if on_track_count == total_count:
            return 'excellent'
        elif on_track_count >= total_count * 0.75:
            return 'good'
        elif on_track_count >= total_count * 0.5:
            return 'fair'
        else:
            return 'needs_improvement'







