"""
Chart generation service for AI assistant.
Handles creation of line, bar, and pie charts from health and nutrition data.
"""
from typing import Dict, Any, List, Optional
from datetime import date, datetime, timedelta
from services.data_access_service import DataAccessService
import logging

logger = logging.getLogger(__name__)


class ChartService:
    """Service for generating chart data from health and nutrition data."""
    
    def __init__(self, data_access: DataAccessService):
        """
        Initialize chart service.
        
        Args:
            data_access: Data access service instance
        """
        self.data_access = data_access
    
    async def generate_chart(
        self,
        chart_type: str,
        data_type: str,
        time_period: Optional[str] = None,
        metric: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate chart data based on type and parameters.
        
        Args:
            chart_type: Type of chart ('line', 'bar', 'pie')
            data_type: Type of data ('health', 'nutrition', 'progress')
            time_period: Time period for data ('week', 'month', 'year')
            metric: Specific metric to chart ('weight', 'calories', 'protein', etc.)
        
        Returns:
            Chart configuration dictionary
        """
        try:
            if data_type == "health":
                return await self._generate_health_chart(chart_type, time_period, metric)
            elif data_type == "nutrition":
                return await self._generate_nutrition_chart(chart_type, time_period, metric)
            elif data_type == "progress":
                return await self._generate_progress_chart(chart_type, time_period, metric)
            else:
                raise ValueError(f"Unknown data type: {data_type}")
        except Exception as e:
            logger.error(f"Error generating chart: {str(e)}")
            raise
    
    async def _generate_health_chart(
        self,
        chart_type: str,
        time_period: Optional[str],
        metric: Optional[str]
    ) -> Dict[str, Any]:
        """Generate health metrics chart."""
        # Get health metrics data
        metrics_data = await self.data_access.get_health_metrics(
            metric_type=metric or "all",
            time_period=time_period or "weekly"
        )
        
        # Convert metrics_data to list format for chart creation
        # metrics_data is a dict with "metrics" key, need to extract list
        chart_data = []
        if isinstance(metrics_data, dict) and "metrics" in metrics_data:
            metrics = metrics_data["metrics"]
            for metric_name, metric_value in metrics.items():
                if isinstance(metric_value, dict):
                    chart_data.append({
                        "date": metric_value.get("recorded_at", ""),
                        "metric": metric_name,
                        "value": metric_value.get("value", 0)
                    })
        elif isinstance(metrics_data, list):
            chart_data = metrics_data
        else:
            # Fallback: create empty chart
            chart_data = []
        
        if chart_type == "line":
            return self._create_line_chart(
                data=chart_data,
                x_key="date",
                y_key=metric or "value",
                title=f"{metric or 'Health Metrics'} Over Time"
            )
        elif chart_type == "bar":
            return self._create_bar_chart(
                data=chart_data,
                x_key="date",
                y_key=metric or "value",
                title=f"{metric or 'Health Metrics'} Comparison"
            )
        elif chart_type == "pie":
            return self._create_pie_chart(
                data=chart_data,
                name_key="metric",
                value_key="value",
                title="Health Metrics Distribution"
            )
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")
    
    async def _generate_nutrition_chart(
        self,
        chart_type: str,
        time_period: Optional[str],
        metric: Optional[str]
    ) -> Dict[str, Any]:
        """Generate nutrition chart."""
        # Determine date range
        end_date = date.today()
        if time_period == "week":
            start_date = end_date - timedelta(days=7)
        elif time_period == "month":
            start_date = end_date - timedelta(days=30)
        else:
            start_date = end_date - timedelta(days=7)
        
        # Get nutrition data (pass date objects, not strings)
        nutrition_data = await self.data_access.get_nutritional_analysis(
            start_date=start_date,
            end_date=end_date,
            analysis_type="daily"
        )
        
        if chart_type == "line":
            return self._create_line_chart(
                data=nutrition_data.get("daily_breakdown", []),
                x_key="date",
                y_key=metric or "calories",
                title=f"{metric or 'Calories'} Over Time"
            )
        elif chart_type == "bar":
            # Bar chart for macronutrients
            return self._create_macro_bar_chart(
                data=nutrition_data,
                title="Macronutrient Comparison"
            )
        elif chart_type == "pie":
            # Pie chart for macronutrient distribution
            return self._create_macro_pie_chart(
                data=nutrition_data,
                title="Macronutrient Distribution"
            )
        else:
            raise ValueError(f"Unsupported chart type: {chart_type}")
    
    async def _generate_progress_chart(
        self,
        chart_type: str,
        time_period: Optional[str],
        metric: Optional[str]
    ) -> Dict[str, Any]:
        """Generate progress tracking chart."""
        # Get progress data
        progress_data = await self.data_access.get_progress(
            metric_type=metric or "all",
            time_period=time_period or "month"
        )
        
        if chart_type == "line":
            return self._create_line_chart(
                data=progress_data.get("history", []),
                x_key="date",
                y_key=metric or "value",
                title=f"{metric or 'Progress'} Over Time"
            )
        elif chart_type == "bar":
            return self._create_bar_chart(
                data=progress_data.get("history", []),
                x_key="date",
                y_key=metric or "value",
                title=f"{metric or 'Progress'} Comparison"
            )
        else:
            raise ValueError(f"Unsupported chart type for progress: {chart_type}")
    
    def _create_line_chart(
        self,
        data: List[Dict[str, Any]],
        x_key: str,
        y_key: str,
        title: str
    ) -> Dict[str, Any]:
        """Create line chart configuration."""
        chart_data = []
        for item in data:
            x_value = item.get(x_key, "")
            # Format date if it's a date string
            if x_key == "date" and x_value:
                # If date is in YYYY-MM-DD format, format it nicely
                if isinstance(x_value, str) and len(x_value) >= 10:
                    try:
                        from datetime import datetime
                        date_obj = datetime.strptime(x_value[:10], "%Y-%m-%d")
                        # Format as "MMM DD" (e.g., "Nov 04")
                        x_value = date_obj.strftime("%b %d")
                    except (ValueError, TypeError):
                        pass  # Keep original value if parsing fails
            
            y_value = item.get(y_key, 0)
            # Ensure y_value is a number
            try:
                y_value = float(y_value) if y_value else 0
            except (ValueError, TypeError):
                y_value = 0
            
            chart_data.append({
                "x": x_value,
                "y": y_value
            })
        
        return {
            "type": "line",
            "title": title,
            "data": chart_data,
            "xAxis": {"label": x_key.replace("_", " ").title()},
            "yAxis": {"label": y_key.replace("_", " ").title()},
            "config": {
                "strokeWidth": 2,
                "dot": True,
                "grid": True
            }
        }
    
    def _create_bar_chart(
        self,
        data: List[Dict[str, Any]],
        x_key: str,
        y_key: str,
        title: str
    ) -> Dict[str, Any]:
        """Create bar chart configuration."""
        chart_data = []
        for item in data:
            chart_data.append({
                "x": item.get(x_key, ""),
                "y": item.get(y_key, 0)
            })
        
        return {
            "type": "bar",
            "title": title,
            "data": chart_data,
            "xAxis": {"label": x_key.replace("_", " ").title()},
            "yAxis": {"label": y_key.replace("_", " ").title()},
            "config": {
                "barRadius": 4,
                "grid": True
            }
        }
    
    def _create_pie_chart(
        self,
        data: List[Dict[str, Any]],
        name_key: str,
        value_key: str,
        title: str
    ) -> Dict[str, Any]:
        """Create pie chart configuration."""
        chart_data = []
        for item in data:
            chart_data.append({
                "name": item.get(name_key, ""),
                "value": item.get(value_key, 0)
            })
        
        return {
            "type": "pie",
            "title": title,
            "data": chart_data,
            "config": {
                "innerRadius": 0,
                "outerRadius": "80%",
                "label": True
            }
        }
    
    def _create_macro_bar_chart(
        self,
        data: Dict[str, Any],
        title: str
    ) -> Dict[str, Any]:
        """Create bar chart for macronutrients."""
        comparison = data.get("comparison", {})
        
        chart_data = []
        macros = ["calories", "protein", "carbs", "fats"]
        
        for macro in macros:
            if macro in comparison:
                macro_data = comparison[macro]
                chart_data.append({
                    "x": macro.title(),
                    "current": macro_data.get("current", 0),
                    "target": macro_data.get("target", 0)
                })
        
        return {
            "type": "bar",
            "title": title,
            "data": chart_data,
            "xAxis": {"label": "Macronutrient"},
            "yAxis": {"label": "Amount"},
            "config": {
                "barRadius": 4,
                "grid": True,
                "stacked": False,
                "showTarget": True
            }
        }
    
    def _create_macro_pie_chart(
        self,
        data: Dict[str, Any],
        title: str
    ) -> Dict[str, Any]:
        """Create pie chart for macronutrient distribution."""
        comparison = data.get("comparison", {})
        
        chart_data = []
        macros = [
            {"key": "protein", "name": "Protein", "color": "#3182ce"},
            {"key": "carbs", "name": "Carbs", "color": "#38a169"},
            {"key": "fats", "name": "Fats", "color": "#d69e2e"}
        ]
        
        for macro in macros:
            if macro["key"] in comparison:
                macro_data = comparison[macro["key"]]
                chart_data.append({
                    "name": macro["name"],
                    "value": macro_data.get("current", 0),
                    "color": macro["color"]
                })
        
        return {
            "type": "pie",
            "title": title,
            "data": chart_data,
            "config": {
                "innerRadius": 0,
                "outerRadius": "80%",
                "label": True
            }
        }

