"""
Function handlers for AI assistant function calling.
These functions are called by the AI when it needs to access user data.
"""
from typing import Dict, Any, Optional
from datetime import date, timedelta
from services.data_access_service import DataAccessService
from services.chart_service import ChartService
from ai.function_calling import normalize_date
import logging

logger = logging.getLogger(__name__)


class FunctionHandlers:
    """Handlers for function calls."""
    
    def __init__(self, data_access_service: DataAccessService):
        """
        Initialize function handlers.
        
        Args:
            data_access_service: Data access service instance
        """
        self.data_access = data_access_service
        self.chart_service = ChartService(data_access_service)
    
    async def get_health_metrics(
        self,
        metric_type: str = "all",
        time_period: str = "current"
    ) -> Dict[str, Any]:
        """
        Get health metrics handler.
        
        Args:
            metric_type: Type of metric (bmi, weight, wellness_score, all)
            time_period: Time period (current, weekly, monthly)
        
        Returns:
            Health metrics data
        """
        # Validate parameters
        if metric_type not in ["bmi", "weight", "wellness_score", "all"]:
            raise ValueError(f"Invalid metric_type: {metric_type}. Must be one of: bmi, weight, wellness_score, all")
        
        if time_period not in ["current", "weekly", "monthly"]:
            raise ValueError(f"Invalid time_period: {time_period}. Must be one of: current, weekly, monthly")
        
        return await self.data_access.get_health_metrics(metric_type, time_period)
    
    async def get_meal_plan(
        self,
        date: Optional[str] = None,
        meal_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get meal plan handler.
        
        Args:
            date: Date string (today, tomorrow, YYYY-MM-DD)
            meal_type: Optional meal type filter (breakfast, lunch, dinner, snack)
        
        Returns:
            Meal plan data
        """
        # Validate meal_type if provided
        if meal_type and meal_type not in ["breakfast", "lunch", "dinner", "snack"]:
            raise ValueError(f"Invalid meal_type: {meal_type}. Must be one of: breakfast, lunch, dinner, snack")
        
        # Normalize date
        if date:
            date_obj = normalize_date(date)
            date_str = date_obj.isoformat()
        else:
            date_str = None
        
        return await self.data_access.get_meal_plan(date_str, meal_type)
    
    async def get_nutritional_analysis(
        self,
        start_date: str,
        end_date: str,
        analysis_type: str = "daily"
    ) -> Dict[str, Any]:
        """
        Get nutritional analysis handler.
        
        Args:
            start_date: Start date string (today, yesterday, YYYY-MM-DD)
            end_date: End date string (today, yesterday, YYYY-MM-DD)
            analysis_type: Type of analysis (daily, weekly, monthly)
        
        Returns:
            Nutritional analysis data
        """
        # Validate analysis_type
        if analysis_type not in ["daily", "weekly", "monthly"]:
            raise ValueError(f"Invalid analysis_type: {analysis_type}. Must be one of: daily, weekly, monthly")
        
        # Normalize dates
        start = normalize_date(start_date)
        end = normalize_date(end_date)
        
        # Validate date range
        if start > end:
            raise ValueError(f"start_date ({start}) must be before or equal to end_date ({end})")
        
        return await self.data_access.get_nutritional_analysis(start, end, analysis_type)
    
    async def get_recipe_details(self, recipe_id: str = None, recipe_name: str = None, meal_name: str = None, meal_date: str = None) -> Dict[str, Any]:
        """
        Get recipe details handler.
        
        Args:
            recipe_id: Recipe ID (optional if recipe_name or meal_name is provided)
            recipe_name: Recipe name to search for (optional if recipe_id or meal_name is provided)
            meal_name: Meal name from meal plan (e.g., "tonight's dinner") - optional
            meal_date: Date for the meal (e.g., "today", "YYYY-MM-DD") - optional, defaults to "today"
        
        Returns:
            Recipe details
        """
        if not recipe_id and not recipe_name and not meal_name:
            raise ValueError("Either recipe_id, recipe_name, or meal_name must be provided")
        
        # Default meal_date to "today" if meal_name is provided
        if meal_name and not meal_date:
            meal_date = "today"
        
        return await self.data_access.get_recipe_details(
            recipe_id=recipe_id,
            recipe_name=recipe_name,
            meal_name=meal_name,
            meal_date=meal_date
        )
    
    async def get_goals(self) -> Dict[str, Any]:
        """
        Get user goals handler.
        
        Returns:
            User goals data
        """
        try:
            # Get health profile for goals
            profile = await self.data_access.api_client.get_health_profile()
            
            # Get nutrition preferences for nutrition goals
            preferences = await self.data_access.api_client.get_nutrition_preferences()
            
            return {
                "health_goals": {
                    "fitness_goal": profile.get("fitness_goal"),
                    "target_weight": profile.get("target_weight"),
                    "activity_level": profile.get("activity_level")
                },
                "nutrition_goals": {
                    "daily_calorie_target": preferences.get("daily_calorie_target", 2000),
                    "protein_target": preferences.get("protein_target", 100),
                    "carbs_target": preferences.get("carbs_target", 200),
                    "fats_target": preferences.get("fats_target", 60)
                }
            }
        except Exception as e:
            logger.error(f"Error getting goals: {str(e)}")
            return {
                "error": f"Unable to retrieve goals: {str(e)}",
                "health_goals": {},
                "nutrition_goals": {}
            }
    
    async def get_progress(
        self,
        metric_type: str,
        time_period: str
    ) -> Dict[str, Any]:
        """
        Get progress tracking handler.
        
        Args:
            metric_type: Type of progress (weight, bmi, wellness_score, nutrition, all)
            time_period: Time period (week, month, quarter, year)
        
        Returns:
            Progress data
        """
        # Validate parameters
        if metric_type not in ["weight", "bmi", "wellness_score", "nutrition", "all"]:
            raise ValueError(f"Invalid metric_type: {metric_type}")
        
        if time_period not in ["week", "month", "quarter", "year"]:
            raise ValueError(f"Invalid time_period: {time_period}")
        
        # Calculate date range based on time_period
        today = date.today()
        if time_period == "week":
            start = today - timedelta(days=7)
        elif time_period == "month":
            start = today - timedelta(days=30)
        elif time_period == "quarter":
            start = today - timedelta(days=90)
        else:  # year
            start = today - timedelta(days=365)
        
        result = {}
        
        # Get health metrics progress
        if metric_type in ["weight", "bmi", "wellness_score", "all"]:
            time_period_map = {
                "week": "weekly",
                "month": "monthly",
                "quarter": "monthly",
                "year": "monthly"
            }
            health_metrics = await self.data_access.get_health_metrics(
                metric_type if metric_type != "all" else "all",
                time_period_map.get(time_period, "monthly")
            )
            result["health_metrics"] = health_metrics
        
        # Get nutrition progress
        if metric_type in ["nutrition", "all"]:
            nutrition = await self.data_access.get_nutritional_analysis(
                start, today, "daily" if time_period == "week" else "weekly"
            )
            result["nutrition"] = nutrition
        
        return result
    
    async def generate_chart(
        self,
        chart_type: str,
        data_type: str,
        time_period: Optional[str] = None,
        metric: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate chart handler.
        
        Args:
            chart_type: Type of chart (line, bar, pie)
            data_type: Type of data (health, nutrition, progress)
            time_period: Time period for data (week, month, year)
            metric: Specific metric to chart (weight, calories, protein, etc.)
        
        Returns:
            Chart configuration dictionary
        """
        # Validate chart_type
        if chart_type not in ["line", "bar", "pie"]:
            raise ValueError(f"Invalid chart_type: {chart_type}. Must be one of: line, bar, pie")
        
        # Validate data_type
        if data_type not in ["health", "nutrition", "progress"]:
            raise ValueError(f"Invalid data_type: {data_type}. Must be one of: health, nutrition, progress")
        
        # Validate time_period if provided
        if time_period and time_period not in ["week", "month", "year"]:
            raise ValueError(f"Invalid time_period: {time_period}. Must be one of: week, month, year")
        
        return await self.chart_service.generate_chart(chart_type, data_type, time_period, metric)

