"""
Function calling implementation for AI assistant.
Defines functions that the AI can call to access user data.
"""
from typing import Dict, Any, List, Callable, Optional
from datetime import date, datetime, timedelta
import logging
import re

logger = logging.getLogger(__name__)


class FunctionRegistry:
    """Registry for function calling."""
    
    def __init__(self):
        """Initialize function registry."""
        self.functions: Dict[str, Dict[str, Any]] = {}
        self.handlers: Dict[str, Callable] = {}
    
    def register(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        handler: Callable
    ):
        """
        Register a function for AI calling.
        
        Args:
            name: Function name
            description: Function description
            parameters: Function parameters schema
            handler: Function handler
        """
        self.functions[name] = {
            "name": name,
            "description": description,
            "parameters": parameters
        }
        self.handlers[name] = handler
        logger.info(f"Registered function: {name}")
    
    def get_function_definitions(self) -> List[Dict[str, Any]]:
        """Get all function definitions for OpenAI."""
        return list(self.functions.values())
    
    async def call_function(self, name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a registered function.
        
        Args:
            name: Function name
            arguments: Function arguments
        
        Returns:
            Function result
        
        Raises:
            ValueError: If function not found or invalid arguments
        """
        if name not in self.handlers:
            raise ValueError(f"Function {name} not found")
        
        handler = self.handlers[name]
        try:
            result = await handler(**arguments)
            return result
        except Exception as e:
            logger.error(f"Error calling function {name}: {str(e)}")
            raise ValueError(f"Error calling function {name}: {str(e)}")


# Global function registry instance
function_registry = FunctionRegistry()


def get_health_metrics_schema() -> Dict[str, Any]:
    """Get schema for get_health_metrics function."""
    return {
        "type": "object",
        "properties": {
            "metric_type": {
                "type": "string",
                "enum": ["bmi", "weight", "wellness_score", "all"],
                "description": "The specific metric to retrieve. Use 'all' to get all metrics."
            },
            "time_period": {
                "type": "string",
                "enum": ["current", "weekly", "monthly"],
                "description": "Time period for the metrics. 'current' returns latest value, 'weekly' returns week trend, 'monthly' returns month trend."
            }
        },
        "required": ["metric_type"]
    }


def get_meal_plan_schema() -> Dict[str, Any]:
    """Get schema for get_meal_plan function."""
    return {
        "type": "object",
        "properties": {
            "date": {
                "type": "string",
                "description": "Date in YYYY-MM-DD format. If not provided, defaults to today. Use 'today', 'tomorrow', or specific date."
            },
            "meal_type": {
                "type": "string",
                "enum": ["breakfast", "lunch", "dinner", "snack", None],
                "description": "Optional filter for specific meal type. If not provided, returns all meals for the date."
            }
        },
        "required": []
    }


def get_nutritional_analysis_schema() -> Dict[str, Any]:
    """Get schema for get_nutritional_analysis function."""
    return {
        "type": "object",
        "properties": {
            "start_date": {
                "type": "string",
                "description": "Start date. Can use 'today', 'yesterday', '7 days ago', '30 days ago', or YYYY-MM-DD format. For 'this week', use '7 days ago'. For 'this month', use '30 days ago'. The system will automatically calculate the correct date."
            },
            "end_date": {
                "type": "string",
                "description": "End date in YYYY-MM-DD format. Can use 'today', 'yesterday', or specific date. For weekly/monthly queries, typically use 'today'."
            },
            "analysis_type": {
                "type": "string",
                "enum": ["daily", "weekly", "monthly"],
                "description": "Type of analysis: 'daily' for single day, 'weekly' for week summary (7 days), 'monthly' for month summary (30 days). When user asks for 'this week' or 'weekly' data, use 'weekly'. When user asks for 'this month' or 'monthly' data, use 'monthly'."
            }
        },
        "required": ["start_date", "end_date"]
    }


def get_recipe_details_schema() -> Dict[str, Any]:
    """Get schema for get_recipe_details function."""
    return {
        "type": "object",
        "properties": {
            "recipe_id": {
                "type": "string",
                "description": "Recipe ID to retrieve details for. Use this if you have the exact recipe ID."
            },
            "recipe_name": {
                "type": "string",
                "description": "Recipe name to search for. Use this when the user asks about a recipe by name (e.g., 'Mediterranean Morning Bowl'). The function will search for the recipe and return details."
        },
            "meal_name": {
                "type": "string",
                "description": "Meal name from meal plan (e.g., 'tonight's dinner', 'today's breakfast'). Use this when the user asks about a meal from their meal plan. The function will find the meal in the meal plan and return complete recipe details including ingredients and instructions."
            },
            "meal_date": {
                "type": "string",
                "description": "Date for the meal (e.g., 'today', 'tomorrow', 'YYYY-MM-DD'). Use this with meal_name to find the meal in the meal plan. Defaults to 'today' if not provided."
            }
        },
        "required": []
    }


def get_goals_schema() -> Dict[str, Any]:
    """Get schema for get_goals function."""
    return {
        "type": "object",
        "properties": {},
        "required": []
    }


def get_progress_schema() -> Dict[str, Any]:
    """Get schema for get_progress function."""
    return {
        "type": "object",
        "properties": {
            "metric_type": {
                "type": "string",
                "enum": ["weight", "bmi", "wellness_score", "nutrition", "all"],
                "description": "Type of progress to track."
            },
            "time_period": {
                "type": "string",
                "enum": ["week", "month", "quarter", "year"],
                "description": "Time period for progress tracking."
            }
        },
        "required": ["metric_type", "time_period"]
    }


def get_generate_chart_schema() -> Dict[str, Any]:
    """Get schema for generate_chart function."""
    return {
        "type": "object",
        "properties": {
            "chart_type": {
                "type": "string",
                "enum": ["line", "bar", "pie"],
                "description": "Type of chart to generate: line (for trends over time), bar (for comparisons), pie (for distributions)."
            },
            "data_type": {
                "type": "string",
                "enum": ["health", "nutrition", "progress"],
                "description": "Type of data to visualize: health (BMI, weight, wellness), nutrition (calories, macros), progress (goal tracking)."
            },
            "time_period": {
                "type": "string",
                "enum": ["week", "month", "year"],
                "description": "Time period for the data. Optional, defaults to week for health/nutrition, month for progress."
            },
            "metric": {
                "type": "string",
                "description": "Specific metric to chart (e.g., 'weight', 'calories', 'protein', 'bmi'). Optional, defaults to all relevant metrics."
            }
        },
        "required": ["chart_type", "data_type"]
    }


def normalize_date(date_str: str) -> date:
    """
    Normalize date string to date object.
    Handles 'today', 'tomorrow', 'yesterday', relative dates like '7 days ago', '30 days ago',
    and YYYY-MM-DD format.
    
    Args:
        date_str: Date string
    
    Returns:
        Date object
    """
    today = date.today()
    date_str_lower = date_str.lower().strip()
    
    if date_str_lower == "today":
        return today
    elif date_str_lower == "tomorrow":
        return today + timedelta(days=1)
    elif date_str_lower == "yesterday":
        return today - timedelta(days=1)
    elif "days ago" in date_str_lower or "day ago" in date_str_lower:
        # Handle relative dates like "7 days ago", "30 days ago", "1 day ago"
        match = re.search(r'(\d+)\s*(?:day|days)\s*ago', date_str_lower)
        if match:
            days = int(match.group(1))
            return today - timedelta(days=days)
        else:
            logger.warning(f"Could not parse relative date: {date_str}, defaulting to today")
            return today
    elif "weeks ago" in date_str_lower or "week ago" in date_str_lower:
        # Handle relative dates like "1 week ago", "2 weeks ago"
        match = re.search(r'(\d+)\s*(?:week|weeks)\s*ago', date_str_lower)
        if match:
            weeks = int(match.group(1))
            return today - timedelta(days=weeks * 7)
        else:
            logger.warning(f"Could not parse relative date: {date_str}, defaulting to today")
            return today
    elif "months ago" in date_str_lower or "month ago" in date_str_lower:
        # Handle relative dates like "1 month ago" (approximate as 30 days)
        match = re.search(r'(\d+)\s*(?:month|months)\s*ago', date_str_lower)
        if match:
            months = int(match.group(1))
            return today - timedelta(days=months * 30)
        else:
            logger.warning(f"Could not parse relative date: {date_str}, defaulting to today")
            return today
    else:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            # If parsing fails, default to today
            logger.warning(f"Invalid date format: {date_str}, defaulting to today")
            return today


def initialize_functions(data_access_service) -> FunctionRegistry:
    """
    Initialize function registry with all functions.
    
    Args:
        data_access_service: Data access service instance
    
    Returns:
        Initialized function registry
    """
    from ai.function_handlers import FunctionHandlers
    
    handlers = FunctionHandlers(data_access_service)
    
    # Register all functions
    function_registry.register(
        name="get_health_metrics",
        description="Retrieves user's current health metrics including BMI, weight, and wellness score. Can get current values or trends over time periods.",
        parameters=get_health_metrics_schema(),
        handler=handlers.get_health_metrics
    )
    
    function_registry.register(
        name="get_meal_plan",
        description="Retrieves user's meal plan for a specific date. Can filter by meal type (breakfast, lunch, dinner, snack).",
        parameters=get_meal_plan_schema(),
        handler=handlers.get_meal_plan
    )
    
    function_registry.register(
        name="get_nutritional_analysis",
        description="Retrieves nutritional analysis including calories, protein, carbs, fats compared to targets. Can analyze daily, weekly, or monthly periods. For 'this week', use start_date '7 days ago', end_date 'today', and analysis_type 'weekly'. For 'this month', use start_date '30 days ago', end_date 'today', and analysis_type 'monthly'. The system automatically handles relative date strings like '7 days ago'.",
        parameters=get_nutritional_analysis_schema(),
        handler=handlers.get_nutritional_analysis
    )
    
    function_registry.register(
        name="get_recipe_details",
        description="Retrieves complete recipe information including ingredients, instructions, nutrition, and preparation steps. Can search by recipe name (e.g., 'Mediterranean Morning Bowl'), use recipe_id if available, or get recipe from meal plan using meal_name (e.g., 'tonight's dinner', 'today's breakfast'). When user asks 'How do I prepare tonight's dinner?', use meal_name='dinner' and meal_date='today' to get complete recipe details from their meal plan.",
        parameters=get_recipe_details_schema(),
        handler=handlers.get_recipe_details
    )
    
    function_registry.register(
        name="get_goals",
        description="Retrieves user's health and nutrition goals including fitness goals, target weight, and nutrition targets.",
        parameters=get_goals_schema(),
        handler=handlers.get_goals
    )
    
    function_registry.register(
        name="get_progress",
        description="Tracks progress toward goals over time periods. Can track weight, BMI, wellness score, or nutrition progress.",
        parameters=get_progress_schema(),
        handler=handlers.get_progress
    )
    
    function_registry.register(
        name="generate_chart",
        description="Generates chart visualizations for health and nutrition data. Supports line charts (trends), bar charts (comparisons), and pie charts (distributions). Use this when the user asks to see data in a chart, graph, or visualization.",
        parameters=get_generate_chart_schema(),
        handler=handlers.generate_chart
    )
    
    return function_registry

