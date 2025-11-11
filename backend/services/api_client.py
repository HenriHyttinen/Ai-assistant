"""
API client service for calling existing health and nutrition platform APIs.
This service acts as the Data Access Layer, making HTTP requests to existing endpoints.
"""
import httpx
from typing import Optional, Dict, Any, List
from datetime import date, datetime
from config import get_settings
import logging

logger = logging.getLogger(__name__)


class APIClient:
    """Client for calling existing platform APIs."""
    
    def __init__(self, auth_token: str):
        """
        Initialize API client with authentication token.
        
        Args:
            auth_token: Bearer token for authentication
        """
        self.auth_token = auth_token
        settings = get_settings()
        self.headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        self.health_base_url = settings.health_api_url
        self.nutrition_base_url = settings.nutrition_api_url
    
    async def _make_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict] = None,
        json_data: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to API endpoint.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL to endpoint
            params: Query parameters
            json_data: JSON body for POST/PUT requests
        
        Returns:
            Response data as dictionary
        
        Raises:
            Exception: If request fails
        """
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    params=params,
                    json=json_data
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"API request failed: {e.response.status_code} - {e.response.text}")
            raise Exception(f"API request failed: {e.response.status_code}")
        except Exception as e:
            logger.error(f"API request error: {str(e)}")
            raise
    
    # Health Profile Endpoints
    
    async def get_health_profile(self) -> Dict[str, Any]:
        """Get current user's health profile."""
        url = f"{self.health_base_url}/profiles/me"
        return await self._make_request("GET", url)
    
    async def get_health_metrics(
        self,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """Get health metrics history."""
        url = f"{self.health_base_url}/profiles/me/metrics"
        params = {"days": days}
        return await self._make_request("GET", url, params=params)
    
    async def get_health_analytics(self) -> Dict[str, Any]:
        """Get comprehensive health analytics."""
        url = f"{self.health_base_url}/profiles/me/analytics"
        return await self._make_request("GET", url)
    
    async def get_health_goals(self) -> Dict[str, Any]:
        """Get user's health goals."""
        # Note: This endpoint may need to be verified
        url = f"{self.health_base_url}/goals"
        try:
            return await self._make_request("GET", url)
        except Exception:
            # If goals endpoint doesn't exist, return empty
            return {"goals": []}
    
    # Nutrition Endpoints
    
    async def get_meal_plans(
        self,
        date: Optional[str] = None,
        plan_type: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get user's meal plans."""
        url = f"{self.nutrition_base_url}/meal-plans"
        params = {}
        if date:
            params["date"] = date
        if plan_type:
            params["plan_type"] = plan_type
        params["limit"] = limit
        return await self._make_request("GET", url, params=params)
    
    async def get_meal_plan(self, meal_plan_id: str) -> Dict[str, Any]:
        """Get specific meal plan by ID."""
        url = f"{self.nutrition_base_url}/meal-plans/{meal_plan_id}"
        return await self._make_request("GET", url)
    
    async def get_nutritional_analysis(
        self,
        start_date: date,
        end_date: date,
        analysis_type: str = "daily"
    ) -> Dict[str, Any]:
        """Get nutritional analysis."""
        url = f"{self.nutrition_base_url}/nutritional-analysis"
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "analysis_type": analysis_type
        }
        return await self._make_request("GET", url, params=params)
    
    async def search_recipes(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search recipes by name or query."""
        url = f"{self.nutrition_base_url}/recipes/search"
        search_data = {
            "query": query,
            "limit": limit
        }
        result = await self._make_request("POST", url, json_data=search_data)
        # Extract recipes from search results
        if isinstance(result, dict) and "recipes" in result:
            return result.get("recipes", [])
        elif isinstance(result, list):
            return result
        return []
    
    async def get_recipe(self, recipe_id: str) -> Dict[str, Any]:
        """Get recipe details by ID using search endpoint."""
        # Note: There's no direct GET endpoint for recipes, so we use search
        url = f"{self.nutrition_base_url}/recipes/search"
        search_data = {
            "recipe_id": recipe_id,
            "limit": 1
        }
        result = await self._make_request("POST", url, json_data=search_data)
        # Extract recipe from search results
        if isinstance(result, dict) and "recipes" in result:
            recipes = result.get("recipes", [])
            if recipes:
                return recipes[0]
        elif isinstance(result, list) and len(result) > 0:
            return result[0]
        raise Exception(f"Recipe {recipe_id} not found")
    
    async def get_nutrition_preferences(self) -> Dict[str, Any]:
        """Get user's nutrition preferences."""
        url = f"{self.nutrition_base_url}/preferences"
        return await self._make_request("GET", url)

