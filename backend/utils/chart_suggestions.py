"""
Chart suggestion utilities for AI assistant.
Provides proactive suggestions for visualizations based on conversation context.
"""
from typing import Dict, Any, List, Optional
import re
import logging

logger = logging.getLogger(__name__)


class ChartSuggestionEngine:
    """Engine for suggesting charts based on conversation context."""
    
    def __init__(self):
        """Initialize chart suggestion engine."""
        # Keywords that suggest different chart types
        self.chart_keywords = {
            "line": ["trend", "over time", "progress", "change", "history", "track", "evolution"],
            "bar": ["compare", "comparison", "versus", "vs", "difference", "better", "worse"],
            "pie": ["distribution", "breakdown", "split", "percentage", "proportion", "share"]
        }
        
        # Keywords that suggest different data types
        self.data_type_keywords = {
            "health": ["weight", "bmi", "wellness", "health", "fitness", "activity"],
            "nutrition": ["calories", "protein", "carbs", "fats", "nutrition", "macros", "meal"],
            "progress": ["progress", "goal", "target", "improvement", "achievement"]
        }
        
        # Keywords that suggest time periods
        self.time_period_keywords = {
            "week": ["week", "weekly", "7 days", "last week"],
            "month": ["month", "monthly", "30 days", "last month"],
            "year": ["year", "yearly", "annual", "12 months"]
        }
    
    def suggest_charts(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        function_results: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Suggest charts based on conversation context.
        
        Args:
            message: Current user message
            conversation_history: Previous conversation messages
            function_results: Results from function calls in this conversation
        
        Returns:
            List of suggested chart configurations
        """
        suggestions = []
        
        # Analyze current message
        message_lower = message.lower()
        
        # Check if user is asking about data that could be visualized
        if self._should_suggest_chart(message_lower, conversation_history):
            # Detect chart type
            chart_type = self._detect_chart_type(message_lower)
            
            # Detect data type
            data_type = self._detect_data_type(message_lower, conversation_history)
            
            # Detect time period
            time_period = self._detect_time_period(message_lower)
            
            # Detect metric
            metric = self._detect_metric(message_lower, data_type)
            
            if chart_type and data_type:
                suggestions.append({
                    "chart_type": chart_type,
                    "data_type": data_type,
                    "time_period": time_period,
                    "metric": metric,
                    "reason": self._generate_suggestion_reason(chart_type, data_type, metric)
                })
        
        # Suggest additional relevant charts based on function results
        if function_results:
            additional = self._suggest_from_function_results(function_results)
            suggestions.extend(additional)
        
        return suggestions
    
    def _should_suggest_chart(
        self,
        message: str,
        conversation_history: List[Dict[str, str]]
    ) -> bool:
        """Determine if a chart should be suggested."""
        # Check for visualization keywords
        visualization_keywords = [
            "show", "display", "visualize", "graph", "chart", "plot",
            "see", "view", "illustrate", "depict"
        ]
        
        # Check for data-related keywords
        data_keywords = [
            "data", "metrics", "stats", "numbers", "values",
            "trend", "progress", "comparison", "breakdown"
        ]
        
        has_visualization = any(keyword in message for keyword in visualization_keywords)
        has_data = any(keyword in message for keyword in data_keywords)
        
        # Also check if recent function calls returned data that could be visualized
        recent_data = False
        if conversation_history:
            recent_messages = conversation_history[-3:]  # Last 3 messages
            for msg in recent_messages:
                if msg.get("role") == "assistant":
                    content = msg.get("content", "").lower()
                    if any(keyword in content for keyword in data_keywords):
                        recent_data = True
                        break
        
        return has_visualization or (has_data and recent_data)
    
    def _detect_chart_type(self, message: str) -> Optional[str]:
        """Detect chart type from message."""
        scores = {
            "line": 0,
            "bar": 0,
            "pie": 0
        }
        
        for chart_type, keywords in self.chart_keywords.items():
            for keyword in keywords:
                if keyword in message:
                    scores[chart_type] += 1
        
        # Return chart type with highest score, or default to line
        max_score = max(scores.values())
        if max_score > 0:
            return max(scores, key=scores.get)
        
        # Default to line for trends, bar for comparisons
        if any(word in message for word in ["compare", "versus", "vs", "difference"]):
            return "bar"
        elif any(word in message for word in ["distribution", "breakdown", "percentage"]):
            return "pie"
        else:
            return "line"  # Default for trends
    
    def _detect_data_type(
        self,
        message: str,
        conversation_history: List[Dict[str, str]]
    ) -> Optional[str]:
        """Detect data type from message and context."""
        scores = {
            "health": 0,
            "nutrition": 0,
            "progress": 0
        }
        
        # Check current message
        for data_type, keywords in self.data_type_keywords.items():
            for keyword in keywords:
                if keyword in message:
                    scores[data_type] += 1
        
        # Check conversation history
        if conversation_history:
            recent_messages = conversation_history[-5:]  # Last 5 messages
            for msg in recent_messages:
                content = msg.get("content", "").lower()
                for data_type, keywords in self.data_type_keywords.items():
                    for keyword in keywords:
                        if keyword in content:
                            scores[data_type] += 0.5  # Lower weight for history
        
        # Return data type with highest score
        max_score = max(scores.values())
        if max_score > 0:
            return max(scores, key=scores.get)
        
        return None
    
    def _detect_time_period(self, message: str) -> Optional[str]:
        """Detect time period from message."""
        for period, keywords in self.time_period_keywords.items():
            for keyword in keywords:
                if keyword in message:
                    return period
        
        return None  # Default will be handled by chart service
    
    def _detect_metric(self, message: str, data_type: Optional[str]) -> Optional[str]:
        """Detect specific metric from message."""
        # Common metrics
        metrics = {
            "weight": ["weight", "kg", "pounds", "lbs"],
            "bmi": ["bmi", "body mass"],
            "calories": ["calories", "cal", "energy"],
            "protein": ["protein"],
            "carbs": ["carbs", "carbohydrates"],
            "fats": ["fats", "fat"],
            "wellness_score": ["wellness", "score", "health score"]
        }
        
        message_lower = message.lower()
        for metric, keywords in metrics.items():
            for keyword in keywords:
                if keyword in message_lower:
                    return metric
        
        return None
    
    def _generate_suggestion_reason(
        self,
        chart_type: str,
        data_type: str,
        metric: Optional[str]
    ) -> str:
        """Generate human-readable reason for suggestion."""
        reason_parts = []
        
        if metric:
            reason_parts.append(f"showing {metric}")
        else:
            reason_parts.append(f"showing {data_type} data")
        
        if chart_type == "line":
            reason_parts.append("as a trend over time")
        elif chart_type == "bar":
            reason_parts.append("as a comparison")
        elif chart_type == "pie":
            reason_parts.append("as a distribution")
        
        return " ".join(reason_parts)
    
    def _suggest_from_function_results(
        self,
        function_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Suggest charts based on function call results."""
        suggestions = []
        
        for result in function_results:
            function_name = result.get("name", "")
            result_data = result.get("result", {})
            
            # Suggest charts based on function results
            if function_name == "get_health_metrics":
                if "metrics" in result_data:
                    suggestions.append({
                        "chart_type": "line",
                        "data_type": "health",
                        "time_period": "month",
                        "metric": None,
                        "reason": "visualize health metrics over time"
                    })
            
            elif function_name == "get_nutritional_analysis":
                if "comparison" in result_data:
                    suggestions.append({
                        "chart_type": "bar",
                        "data_type": "nutrition",
                        "time_period": "week",
                        "metric": None,
                        "reason": "compare nutrition targets vs actual"
                    })
                    suggestions.append({
                        "chart_type": "pie",
                        "data_type": "nutrition",
                        "time_period": None,
                        "metric": None,
                        "reason": "show macronutrient distribution"
                    })
            
            elif function_name == "get_progress":
                suggestions.append({
                    "chart_type": "line",
                    "data_type": "progress",
                    "time_period": "month",
                    "metric": None,
                    "reason": "track progress over time"
                })
        
        return suggestions

