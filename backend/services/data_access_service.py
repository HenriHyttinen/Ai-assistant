"""
Data Access Service - Formats data from API client for AI consumption.
This is part of the Data Access Layer that processes and formats data.
"""
from typing import Dict, Any, List, Optional
from datetime import date, datetime, timedelta
from services.api_client import APIClient
import logging
import re

logger = logging.getLogger(__name__)


class DataAccessService:
    """Service for accessing and formatting data for AI assistant."""
    
    def __init__(self, api_client: APIClient):
        """
        Initialize data access service.
        
        Args:
            api_client: API client instance
        """
        self.api_client = api_client
    
    async def get_health_metrics(
        self,
        metric_type: str = "all",
        time_period: str = "current"
    ) -> Dict[str, Any]:
        """
        Get health metrics formatted for AI consumption.
        
        Args:
            metric_type: Type of metric (bmi, weight, wellness_score, all)
            time_period: Time period (current, weekly, monthly)
        
        Returns:
            Formatted health metrics data
        """
        try:
            # Get health profile
            profile = await self.api_client.get_health_profile()
            
            # Get metrics history based on time period
            days = 1 if time_period == "current" else (7 if time_period == "weekly" else 30)
            metrics_history = await self.api_client.get_health_metrics(days=days)
            
            # Format data based on metric_type
            result = {
                "user_name": profile.get("name", "User"),
                "metrics": {}
            }
            
            # Get current weight and height from profile
            current_weight = profile.get("weight")
            current_height = profile.get("height")
            
            # Calculate expected BMI from current profile
            calculated_bmi = None
            if current_weight is not None and current_height is not None:
                height_m = current_height / 100
                calculated_bmi = current_weight / (height_m * height_m)
            
            # Check if metrics history exists and is up-to-date
            metrics_outdated = False
            if metrics_history and len(metrics_history) > 0:
                latest = metrics_history[0]  # Most recent
                # Check if weight in profile matches weight in latest metrics
                if current_weight is not None and latest.get("weight") is not None:
                    # Allow small difference due to rounding (0.1 kg)
                    weight_diff = abs(float(current_weight) - float(latest.get("weight")))
                    if weight_diff > 0.1:
                        metrics_outdated = True
                        logger.warning(f"Metrics history outdated: profile weight={current_weight}kg, metrics weight={latest.get('weight')}kg, difference={weight_diff:.2f}kg")
                
                # Also check if BMI in metrics matches calculated BMI from profile
                if not metrics_outdated and calculated_bmi is not None and latest.get("bmi") is not None:
                    bmi_diff = abs(float(calculated_bmi) - float(latest.get("bmi")))
                    if bmi_diff > 0.1:  # Allow 0.1 difference for rounding
                        metrics_outdated = True
                        logger.warning(f"Metrics history BMI outdated: calculated BMI={calculated_bmi:.2f}, metrics BMI={latest.get('bmi')}, difference={bmi_diff:.2f}")
                elif current_weight is not None:
                    # Profile has weight but metrics don't - use profile
                    metrics_outdated = True
                    logger.warning(f"Metrics history missing weight: profile weight={current_weight}kg, will calculate from profile")
            else:
                metrics_outdated = True
                logger.warning("No metrics history found, will calculate from profile")
            
            # Calculate BMI from current profile if metrics are outdated or missing
            if metrics_outdated and calculated_bmi is not None:
                logger.info(f"Calculating BMI from profile: weight={current_weight}kg, height={current_height}cm, BMI={calculated_bmi:.2f}")
                
                if metric_type in ["bmi", "all"]:
                    result["metrics"]["bmi"] = {
                        "value": round(calculated_bmi, 1),
                        "category": self._get_bmi_category(calculated_bmi),
                        "recorded_at": datetime.now().isoformat(),
                        "calculated_from_profile": True
                    }
                
                if metric_type in ["weight", "all"]:
                    result["metrics"]["weight"] = {
                        "value": current_weight,  # in kg
                        "unit": "kg",
                        "recorded_at": datetime.now().isoformat(),
                        "from_profile": True
                    }
            elif metrics_history:
                # Use metrics history if it's up-to-date
                latest = metrics_history[0]  # Most recent
                
                if metric_type in ["bmi", "all"]:
                    result["metrics"]["bmi"] = {
                        "value": latest.get("bmi"),
                        "category": self._get_bmi_category(latest.get("bmi")),
                        "recorded_at": latest.get("recorded_at")
                    }
                
                if metric_type in ["weight", "all"]:
                    result["metrics"]["weight"] = {
                        "value": latest.get("weight"),  # in kg
                        "unit": "kg",
                        "recorded_at": latest.get("recorded_at")
                    }
                    
                    # Add trend if we have historical data
                    if len(metrics_history) > 1:
                        previous = metrics_history[-1]
                        weight_change = latest.get("weight") - previous.get("weight")
                        result["metrics"]["weight"]["change"] = weight_change
                        result["metrics"]["weight"]["change_period"] = time_period
                
                if metric_type in ["wellness_score", "all"]:
                    result["metrics"]["wellness_score"] = {
                        "value": latest.get("wellness_score"),
                        "recorded_at": latest.get("recorded_at")
                    }
            
            # Add profile data
            result["profile"] = {
                "height": profile.get("height"),  # in cm
                "activity_level": profile.get("activity_level"),
                "fitness_goal": profile.get("fitness_goal")
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting health metrics: {str(e)}")
            return {
                "error": f"Unable to retrieve health metrics: {str(e)}",
                "metrics": {}
            }
    
    async def get_meal_plan(
        self,
        date_str: Optional[str] = None,
        meal_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get meal plan formatted for AI consumption.
        
        Args:
            date_str: Date in YYYY-MM-DD format (defaults to today)
            meal_type: Type of meal (breakfast, lunch, dinner, snack) - optional filter
        
        Returns:
            Formatted meal plan data
        """
        try:
            if not date_str:
                date_str = datetime.now().strftime("%Y-%m-%d")
            
            logger.info(f"Getting meal plan for date: {date_str}, meal_type: {meal_type}")
            
            # Try to get meal plans for the date (both daily and weekly)
            # First try without plan_type to get any plan (daily or weekly) for this date
            meal_plans = await self.api_client.get_meal_plans(date=date_str, limit=10)
            
            logger.info(f"Found {len(meal_plans)} meal plan(s) for date {date_str}")
            
            if not meal_plans:
                # If no plans found, try getting the most recent active plan
                logger.info("No meal plans found for specific date, trying to get most recent active plan")
                meal_plans = await self.api_client.get_meal_plans(limit=5)
                
                if meal_plans:
                    logger.info(f"Found {len(meal_plans)} recent meal plan(s), using most recent")
                    # Use the most recent plan
                    meal_plan = meal_plans[0]
                else:
                    logger.warning(f"No meal plans found at all for user")
                return {
                    "date": date_str,
                    "meals": [],
                    "message": "No meal plan found for this date"
                }
            else:
                meal_plan = meal_plans[0]
            
            meals = meal_plan.get("meals", [])
            
            # For weekly plans, filter meals by the specific date
            plan_type = meal_plan.get("plan_type", "daily")
            if plan_type == "weekly" and date_str:
                # Parse the target date
                try:
                    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    # Filter meals to only include those for the target date
                    filtered_meals = []
                    for m in meals:
                        meal_date_str = m.get("meal_date")
                        if meal_date_str:
                            try:
                                # Handle different date formats
                                if isinstance(meal_date_str, str):
                                    # Try ISO format first
                                    if 'T' in meal_date_str:
                                        meal_date = datetime.fromisoformat(meal_date_str.replace('Z', '+00:00')).date()
                                    else:
                                        meal_date = datetime.strptime(meal_date_str, "%Y-%m-%d").date()
                                else:
                                    # If it's already a date object
                                    meal_date = meal_date_str if hasattr(meal_date_str, 'date') else meal_date_str
                                
                                if meal_date == target_date:
                                    filtered_meals.append(m)
                            except (ValueError, AttributeError) as e:
                                logger.warning(f"Could not parse meal_date {meal_date_str}: {str(e)}")
                                # Include meal if we can't parse date (better to show than hide)
                                filtered_meals.append(m)
                        else:
                            # If no meal_date, include it (might be a daily plan meal)
                            filtered_meals.append(m)
                    
                    meals = filtered_meals
                    logger.info(f"Filtered weekly plan meals to {len(meals)} meals for date {date_str}")
                except ValueError as e:
                    logger.error(f"Could not parse target date {date_str}: {str(e)}")
                    # Continue with all meals if date parsing fails
            
            # Filter by meal_type if specified
            if meal_type:
                meals = [m for m in meals if m.get("meal_type", "").lower() == meal_type.lower()]
            
            # Format meals - include recipe_details if available (for complete recipe info)
            formatted_meals = []
            for meal in meals:
                # Get recipe_details from meal (contains full recipe info including ingredients/instructions)
                recipe_details = meal.get("recipe_details") or {}
                
                formatted_meal = {
                    "id": meal.get("id"),
                    "name": meal.get("meal_name") or meal.get("name"),
                    "type": meal.get("meal_type") or meal.get("type"),
                    "calories": meal.get("calories") or meal.get("per_serving_calories", 0),
                    "protein": meal.get("protein") or meal.get("per_serving_protein", 0),
                    "carbs": meal.get("carbs") or meal.get("per_serving_carbs", 0),
                    "fats": meal.get("fats") or meal.get("per_serving_fats", 0),
                    "recipe_id": meal.get("recipe_id"),
                    # Include recipe_details for complete recipe information
                    "recipe_details": recipe_details if recipe_details else None
                }
                formatted_meals.append(formatted_meal)
            
            return {
                "date": date_str,
                "meals": formatted_meals,
                "total_calories": sum(m.get("calories", 0) for m in formatted_meals),
                "total_protein": sum(m.get("protein", 0) for m in formatted_meals),
                "total_carbs": sum(m.get("carbs", 0) for m in formatted_meals),
                "total_fats": sum(m.get("fats", 0) for m in formatted_meals)
            }
            
        except Exception as e:
            logger.error(f"Error getting meal plan: {str(e)}")
            return {
                "error": f"Unable to retrieve meal plan: {str(e)}",
                "meals": []
            }
    
    async def get_nutritional_analysis(
        self,
        start_date: date,
        end_date: date,
        analysis_type: str = "daily"
    ) -> Dict[str, Any]:
        """
        Get nutritional analysis formatted for AI consumption.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            analysis_type: Type of analysis (daily, weekly, monthly)
        
        Returns:
            Formatted nutritional analysis data
        """
        try:
            logger.info(f"Getting nutritional analysis: start_date={start_date}, end_date={end_date}, analysis_type={analysis_type}")
            
            analysis = await self.api_client.get_nutritional_analysis(
                start_date=start_date,
                end_date=end_date,
                analysis_type=analysis_type
            )
            
            logger.info(f"Nutritional analysis response: totals={analysis.get('totals', {})}")
            
            # Get preferences for daily targets
            preferences = await self.api_client.get_nutrition_preferences()
            
            totals = analysis.get("totals", {})
            logger.info(f"Extracted totals: calories={totals.get('calories', 0)}, protein={totals.get('protein', 0)}, carbs={totals.get('carbs', 0)}, fats={totals.get('fats', 0)}")
            
            # Calculate number of days in the period
            period_days = (end_date - start_date).days + 1
            logger.info(f"Period days: {period_days}")
            
            # Daily targets from preferences
            daily_targets = {
                "calories": preferences.get("daily_calorie_target", 2000),
                "protein": preferences.get("protein_target", 100),
                "carbs": preferences.get("carbs_target", 200),
                "fats": preferences.get("fats_target", 60)
            }
            
            # Scale daily targets to period targets (for comparison with period totals)
            period_targets = {
                "calories": daily_targets["calories"] * period_days,
                "protein": daily_targets["protein"] * period_days,
                "carbs": daily_targets["carbs"] * period_days,
                "fats": daily_targets["fats"] * period_days
            }
            
            logger.info(f"Daily targets: {daily_targets}")
            logger.info(f"Period targets (for {period_days} days): {period_targets}")
            
            # Get daily breakdown from API response (for charts)
            days_list = analysis.get("days", [])
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "analysis_type": analysis_type,
                    "days": period_days
                },
                "totals": {
                    "calories": totals.get("calories", 0),
                    "protein": totals.get("protein", 0),  # in grams
                    "carbs": totals.get("carbs", 0),  # in grams
                    "fats": totals.get("fats", 0)  # in grams
                },
                "daily_breakdown": days_list,  # Daily data for charts (alias for days)
                "days": days_list,  # Also include as days for compatibility
                "daily_targets": daily_targets,  # Keep daily targets for reference
                "period_targets": period_targets,  # Period targets for comparison
                "comparison": {
                    "calories": {
                        "current": totals.get("calories", 0),
                        "target": period_targets["calories"],
                        "daily_target": daily_targets["calories"],
                        "percentage": (totals.get("calories", 0) / period_targets["calories"] * 100) if period_targets["calories"] > 0 else 0
                    },
                    "protein": {
                        "current": totals.get("protein", 0),
                        "target": period_targets["protein"],
                        "daily_target": daily_targets["protein"],
                        "percentage": (totals.get("protein", 0) / period_targets["protein"] * 100) if period_targets["protein"] > 0 else 0
                    },
                    "carbs": {
                        "current": totals.get("carbs", 0),
                        "target": period_targets["carbs"],
                        "daily_target": daily_targets["carbs"],
                        "percentage": (totals.get("carbs", 0) / period_targets["carbs"] * 100) if period_targets["carbs"] > 0 else 0
                    },
                    "fats": {
                        "current": totals.get("fats", 0),
                        "target": period_targets["fats"],
                        "daily_target": daily_targets["fats"],
                        "percentage": (totals.get("fats", 0) / period_targets["fats"] * 100) if period_targets["fats"] > 0 else 0
                    }
                },
                "ai_insights": analysis.get("ai_insights")
            }
            
        except Exception as e:
            logger.error(f"Error getting nutritional analysis: {str(e)}")
            return {
                "error": f"Unable to retrieve nutritional analysis: {str(e)}",
                "totals": {},
                "targets": {}
            }
    
    async def get_recipe_details(self, recipe_id: str = None, recipe_name: str = None, meal_name: str = None, meal_date: str = None) -> Dict[str, Any]:
        """
        Get recipe details formatted for AI consumption.
        
        Args:
            recipe_id: Recipe ID (optional if recipe_name or meal_name is provided)
            recipe_name: Recipe name to search for (optional if recipe_id or meal_name is provided)
            meal_name: Meal name from meal plan (e.g., "dinner", "breakfast") - optional
            meal_date: Date for the meal (e.g., "today", "YYYY-MM-DD") - optional, defaults to "today"
        
        Returns:
            Formatted recipe data
        """
        try:
            # If meal_name is provided, try to get recipe from meal plan first
            # This ensures we get complete ingredients/instructions even if recipe table is incomplete
            if meal_name:
                logger.info(f"Getting recipe details from meal plan for meal '{meal_name}' on {meal_date or 'today'}")
                try:
                    # Normalize date
                    if not meal_date or meal_date.lower() == "today":
                        date_str = datetime.now().strftime("%Y-%m-%d")
                    elif meal_date.lower() == "tomorrow":
                        from datetime import timedelta
                        date_str = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
                    else:
                        date_str = meal_date
                    
                    meal_plan = await self.get_meal_plan(date_str)
                    meals = meal_plan.get("meals", [])
                    
                    # Find meal by type (e.g., "dinner", "breakfast") or name
                    matching_meal = None
                    meal_name_lower = meal_name.lower()
                    
                    # First try to match by meal type
                    for meal in meals:
                        meal_type = (meal.get("type") or "").lower()
                        meal_name_from_plan = (meal.get("name") or "").lower()
                        
                        # Match by type (e.g., "dinner", "breakfast")
                        if meal_name_lower in meal_type or meal_type in meal_name_lower:
                            matching_meal = meal
                            break
                        # Match by name
                        if meal_name_lower in meal_name_from_plan or meal_name_from_plan in meal_name_lower:
                            matching_meal = meal
                            break
                    
                    if matching_meal:
                        recipe_details = matching_meal.get("recipe_details")
                        if recipe_details:
                            logger.info(f"Found recipe details in meal plan for meal '{meal_name}'")
                            # Extract and format ingredients/instructions from recipe_details
                            ingredients_from_meal = recipe_details.get("ingredients", [])
                            instructions_from_meal = recipe_details.get("instructions", [])
                            
                            # Format ingredients
                            ingredients_list = []
                            for ing in ingredients_from_meal:
                                if isinstance(ing, dict):
                                    name = ing.get("name", "")
                                    quantity = ing.get("quantity", 0)
                                    unit = ing.get("unit", "")
                                    if name:
                                        if quantity and unit:
                                            ingredients_list.append(f"{quantity} {unit} {name}")
                                        else:
                                            ingredients_list.append(name)
                                else:
                                    ingredients_list.append(str(ing))
                            
                            # Format instructions
                            instructions_list = []
                            for inst in instructions_from_meal:
                                if isinstance(inst, dict):
                                    step = inst.get("step") or inst.get("step_number")
                                    description = inst.get("description") or inst.get("instruction") or inst.get("text", "")
                                    if description:
                                        if step:
                                            instructions_list.append(f"{step}. {description}")
                                        else:
                                            instructions_list.append(description)
                                else:
                                    instructions_list.append(str(inst))
                            
                            # If we found ingredients/instructions in meal plan, use them
                            if ingredients_list or instructions_list:
                                logger.info(f"Using recipe details from meal plan: {len(ingredients_list)} ingredients, {len(instructions_list)} instructions")
                                return {
                                    "id": recipe_details.get("id") or recipe_id,
                                    "title": recipe_details.get("title") or matching_meal.get("name"),
                                    "description": recipe_details.get("summary") or recipe_details.get("description"),
                                    "ingredients": ingredients_list,
                                    "instructions": instructions_list,
                                    "nutrition": recipe_details.get("nutrition", {}),
                                    "servings": recipe_details.get("servings", 1),
                                    "prep_time": recipe_details.get("prep_time"),
                                    "cook_time": recipe_details.get("cook_time"),
                                    "cuisine": recipe_details.get("cuisine"),
                                    "dietary_tags": recipe_details.get("dietary_tags", [])
                                }
                except Exception as e:
                    logger.warning(f"Could not get recipe details from meal plan for meal '{meal_name}': {str(e)}")
            
            # If recipe_name is provided, search for it first
            if recipe_name and not recipe_id:
                logger.info(f"Searching for recipe by name: {recipe_name}")
                
                # Try multiple search variations to handle typos
                search_variations = [recipe_name]
                # Common typo fixes
                if "bow" in recipe_name.lower() and "bowl" not in recipe_name.lower():
                    search_variations.append(recipe_name.replace("bow", "bowl").replace("Bow", "Bowl"))
                if "bowl" in recipe_name.lower() and "bow" not in recipe_name.lower():
                    search_variations.append(recipe_name.replace("bowl", "bow").replace("Bowl", "Bow"))
                
                # Also try searching with just key words (e.g., "Mediterranean Morning" if full name fails)
                words = recipe_name.split()
                if len(words) > 2:
                    # Try without last word, then without first word
                    search_variations.append(" ".join(words[:-1]))  # "Mediterranean Morning"
                    search_variations.append(" ".join(words[1:]))  # "Morning Bowl"
                
                recipes = []
                for search_term in search_variations:
                    try:
                        recipes = await self.api_client.search_recipes(search_term, limit=5)
                        if recipes:
                            logger.info(f"Found {len(recipes)} recipe(s) using search term: '{search_term}'")
                            # Log first recipe title for debugging
                            if recipes[0].get("title"):
                                logger.info(f"First match: '{recipes[0].get('title')}'")
                            break
                    except Exception as e:
                        logger.warning(f"Error searching with term '{search_term}': {str(e)}")
                        continue
                
                if not recipes:
                    # Fallback: Search meal plans for this recipe name
                    logger.info(f"Recipe '{recipe_name}' not found in Recipe table, searching meal plans")
                    try:
                        meal_plans = await self.api_client.get_meal_plans(limit=20)
                        
                        logger.info(f"Searching {len(meal_plans)} meal plans for recipe '{recipe_name}'")
                        
                        # Search through all meal plans for meals with this recipe
                        for plan in meal_plans:
                            meals = plan.get("meals", [])
                            for meal in meals:
                                meal_name = meal.get("name") or meal.get("meal_name") or ""
                                meal_recipe_title = None
                                if meal.get("recipe"):
                                    meal_recipe_title = meal.get("recipe", {}).get("title") or meal.get("recipe", {}).get("name")
                                if meal.get("recipe_details"):
                                    meal_recipe_title = meal.get("recipe_details", {}).get("title") or meal.get("recipe_details", {}).get("name") or meal_recipe_title
                                
                                # Get recipe details (check multiple possible locations)
                                recipe_details = meal.get("recipe_details") or meal.get("recipe") or {}
                                
                                # Normalize strings for comparison (remove extra spaces, lowercase)
                                def normalize(s):
                                    return " ".join(s.lower().split()) if s else ""
                                
                                meal_name_norm = normalize(meal_name)
                                recipe_title_norm = normalize(meal_recipe_title) if meal_recipe_title else ""
                                recipe_name_norm = normalize(recipe_name)
                                
                                # Check if recipe name matches (case-insensitive, partial match, try variations)
                                search_terms = [recipe_name_norm] + [normalize(v) for v in search_variations[1:]]
                                
                                # Extract key words from recipe name (e.g., "Mediterranean Morning Bowl" -> ["mediterranean", "morning", "bowl"])
                                recipe_keywords = set([w for w in recipe_name_norm.split() if len(w) > 3])
                                
                                # Check if recipe name matches meal name or recipe title
                                matched = False
                                for search_term in search_terms:
                                    # Full match or significant partial match
                                    if (search_term in meal_name_norm or meal_name_norm in search_term or
                                        search_term in recipe_title_norm or recipe_title_norm in search_term):
                                        matched = True
                                        break
                                    
                                    # Keyword-based matching (at least 2 keywords match)
                                    if recipe_keywords:
                                        meal_keywords = set([w for w in meal_name_norm.split() if len(w) > 3])
                                        title_keywords = set([w for w in recipe_title_norm.split() if len(w) > 3]) if recipe_title_norm else set()
                                        matching_keywords = recipe_keywords & (meal_keywords | title_keywords)
                                        if len(matching_keywords) >= min(2, len(recipe_keywords)):
                                            matched = True
                                            break
                                
                                if matched and recipe_details:
                                    # Verify recipe_details has actual data (not just empty dict)
                                    has_data = (
                                        recipe_details.get("title") or 
                                        recipe_details.get("ingredients") or 
                                        recipe_details.get("instructions") or
                                        meal_name
                                    )
                                    if has_data:
                                        logger.info(f"Found recipe '{recipe_name}' in meal plan as '{meal_name}' (title: '{meal_recipe_title}')")
                                        return self._format_recipe_from_meal_plan(recipe_details, meal)
                        
                        logger.warning(f"⚠️ Could not find recipe '{recipe_name}' in any meal plans")
                    except Exception as e:
                        logger.warning(f"Could not search meal plans for recipe '{recipe_name}': {str(e)}")
                    
                    return {
                        "error": f"Recipe '{recipe_name}' not found",
                        "id": None
                    }
                # Use the first matching recipe
                recipe = recipes[0]
                logger.info(f"Found recipe: {recipe.get('title')} (ID: {recipe.get('id')})")
            elif recipe_id:
                recipe = await self.api_client.get_recipe(recipe_id)
            else:
                return {
                    "error": "Either recipe_id, recipe_name, or meal_name must be provided",
                    "id": None
                }
            
            # Handle different recipe response formats
            ingredients = recipe.get("ingredients", [])
            ingredients_list = []
            if isinstance(ingredients, list) and len(ingredients) > 0:
                # If ingredients is a list of strings, use as-is
                if isinstance(ingredients[0], str):
                    ingredients_list = ingredients
                else:
                    # If ingredients is a list of objects, format them nicely
                    for ing in ingredients:
                        if isinstance(ing, dict):
                            name = ing.get("name") or ing.get("ingredient_name") or "Unknown ingredient"
                            quantity = ing.get("quantity")
                            unit = ing.get("unit") or ""
                            if quantity is not None:
                                ingredients_list.append(f"{quantity} {unit} {name}".strip())
                            else:
                                ingredients_list.append(name)
                        else:
                            # Handle non-dict ingredients (strings, etc.)
                            ingredients_list.append(str(ing))
            # If ingredients is empty or not a list, ingredients_list remains empty
            
            instructions = recipe.get("instructions", [])
            instructions_list = []
            if isinstance(instructions, list) and len(instructions) > 0:
                # If instructions is a list of strings, use as-is
                if isinstance(instructions[0], str):
                    instructions_list = instructions
                else:
                    # If instructions is a list of objects, format them nicely
                    for inst in instructions:
                        if isinstance(inst, dict):
                            # Handle different instruction formats
                            step_num = inst.get("step") or inst.get("step_number")
                            description = inst.get("description") or inst.get("instruction") or inst.get("step_title") or ""
                            
                            if step_num is not None and description:
                                instructions_list.append(f"{step_num}. {description}")
                            elif description:
                                instructions_list.append(description)
                            elif step_num is not None:
                                instructions_list.append(f"Step {step_num}")
                            else:
                                instructions_list.append(str(inst))
                        elif isinstance(inst, (int, float)):
                            # Handle case where instructions might be just numbers
                            instructions_list.append(f"Step {inst}")
                        else:
                            instructions_list.append(str(inst))
            
            # CRITICAL FALLBACK: If recipe table has no ingredients/instructions, 
            # search meal plans for this recipe to get complete recipe_details
            recipe_id_from_table = recipe.get("id")
            recipe_name_from_table = recipe.get("title") or recipe.get("name")
            
            logger.debug(f"Fallback check: recipe_id={recipe_id_from_table}, ingredients_list length={len(ingredients_list)}, instructions_list length={len(instructions_list)}")
            
            if (not ingredients_list or not instructions_list) and recipe_id_from_table:
                logger.info(f"Recipe {recipe_id_from_table} has incomplete data, searching meal plans for complete recipe_details")
                try:
                    # Search recent meal plans (last 30 days) for this recipe
                    from datetime import timedelta
                    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
                    end_date = datetime.now().strftime("%Y-%m-%d")
                    
                    meal_plans = await self.api_client.get_meal_plans(limit=20)
                    logger.info(f"Searching {len(meal_plans)} meal plans for recipe {recipe_id_from_table} or '{recipe_name_from_table}'")
                    
                    # Search through all meal plans for meals with this recipe
                    for plan_idx, plan in enumerate(meal_plans):
                        meals = plan.get("meals", [])
                        logger.debug(f"Checking meal plan {plan_idx+1}: {len(meals)} meals")
                        for meal_idx, meal in enumerate(meals):
                            recipe_details = meal.get("recipe_details")
                            if recipe_details:
                                # Check if this meal's recipe matches our recipe
                                meal_recipe_id = recipe_details.get("id")
                                meal_recipe_title = recipe_details.get("title") or meal.get("meal_name") or meal.get("name")
                                
                                logger.debug(f"  Meal {meal_idx+1}: recipe_id={meal_recipe_id}, title='{meal_recipe_title}'")
                                
                                # Match by ID or name (fuzzy match for name)
                                name_match = False
                                if recipe_name_from_table and meal_recipe_title:
                                    # Normalize names for comparison (remove "Gourmet", extra spaces, etc.)
                                    normalized_search = recipe_name_from_table.lower().replace("gourmet", "").strip()
                                    normalized_meal = meal_recipe_title.lower().replace("gourmet", "").strip()
                                    name_match = normalized_search in normalized_meal or normalized_meal in normalized_search
                                
                                id_match = meal_recipe_id == recipe_id_from_table
                                
                                if id_match or name_match:
                                    logger.info(f"✅ MATCH FOUND! Meal plan {plan_idx+1}, meal {meal_idx+1}: recipe_id={meal_recipe_id}, title='{meal_recipe_title}'")
                                    
                                    # Extract ingredients/instructions from meal plan
                                    ingredients_from_meal = recipe_details.get("ingredients", [])
                                    instructions_from_meal = recipe_details.get("instructions", [])
                                    
                                    logger.info(f"  Found {len(ingredients_from_meal)} ingredients and {len(instructions_from_meal)} instructions in meal plan")
                                    
                                    # Use meal plan data if we don't have it from recipe table
                                    if not ingredients_list and ingredients_from_meal:
                                        ingredients_list = []
                                        for ing in ingredients_from_meal:
                                            if isinstance(ing, dict):
                                                name = ing.get("name", "")
                                                quantity = ing.get("quantity", 0)
                                                unit = ing.get("unit", "")
                                                if name:
                                                    if quantity and unit:
                                                        ingredients_list.append(f"{quantity} {unit} {name}")
                                                    else:
                                                        ingredients_list.append(name)
                                            else:
                                                ingredients_list.append(str(ing))
                                        logger.info(f"  Extracted {len(ingredients_list)} ingredients from meal plan")
                                    
                                    if not instructions_list and instructions_from_meal:
                                        instructions_list = []
                                        for inst in instructions_from_meal:
                                            if isinstance(inst, dict):
                                                step = inst.get("step") or inst.get("step_number")
                                                description = inst.get("description") or inst.get("instruction") or inst.get("text", "")
                                                if description:
                                                    if step:
                                                        instructions_list.append(f"{step}. {description}")
                                                    else:
                                                        instructions_list.append(description)
                                            else:
                                                instructions_list.append(str(inst))
                                        logger.info(f"  Extracted {len(instructions_list)} instructions from meal plan")
                                    
                                    # If we found complete data, break out of loops
                                    if ingredients_list and instructions_list:
                                        logger.info(f"✅ Retrieved complete recipe from meal plan: {len(ingredients_list)} ingredients, {len(instructions_list)} instructions")
                                        break
                        
                        # Break outer loop if we found complete data
                        if ingredients_list and instructions_list:
                            break
                    
                    if not ingredients_list and not instructions_list:
                        logger.warning(f"⚠️ Could not find recipe {recipe_id_from_table} ('{recipe_name_from_table}') in any meal plans")
                            
                except Exception as e:
                    logger.warning(f"Could not search meal plans for recipe {recipe_id_from_table}: {str(e)}")
            
            # If ingredients/instructions are empty but we have a summary, try to extract from summary
            # This handles cases where AI-generated recipes might have data in summary text
            summary = recipe.get("description") or recipe.get("summary") or ""
            logger.debug(f"Recipe {recipe.get('id')} summary length: {len(summary)} characters")
            
            if not ingredients_list and summary:
                logger.info(f"Recipe {recipe.get('id')} has no ingredients in relationships, checking summary for extraction")
                # Try to extract ingredients from summary (basic pattern matching)
                # Look for common patterns like "Ingredients:", "You'll need:", etc.
                ingredients_match = re.search(r'(?:ingredients?|you\'ll need|what you need)[:\-]?\s*(.+?)(?:\n\n|\ninstructions?|\nsteps?|$)', summary, re.IGNORECASE | re.DOTALL)
                if ingredients_match:
                    ingredients_text = ingredients_match.group(1)
                    # Split by lines and clean up
                    potential_ingredients = [line.strip() for line in ingredients_text.split('\n') if line.strip() and not line.strip().startswith('#')]
                    if potential_ingredients:
                        ingredients_list = potential_ingredients[:10]  # Limit to first 10
                        logger.info(f"Extracted {len(ingredients_list)} potential ingredients from summary")
                else:
                    logger.debug(f"No ingredients pattern found in summary. Summary preview: {summary[:200]}")
            
            if not instructions_list and summary:
                logger.info(f"Recipe {recipe.get('id')} has no instructions in relationships, checking summary for extraction")
                # Try to extract instructions from summary
                instructions_match = re.search(r'(?:instructions?|directions?|method|how to|steps?)[:\-]?\s*(.+?)(?:\n\n|$)', summary, re.IGNORECASE | re.DOTALL)
                if instructions_match:
                    instructions_text = instructions_match.group(1)
                    # Split by numbered steps or lines
                    potential_instructions = []
                    # Try to find numbered steps (1., 2., Step 1, etc.)
                    step_pattern = r'(?:^|\n)\s*(?:\d+\.|step\s+\d+[:\-]?)\s*(.+?)(?=\n\s*(?:\d+\.|step\s+\d+)|$)'
                    steps = re.findall(step_pattern, instructions_text, re.IGNORECASE | re.MULTILINE)
                    if steps:
                        potential_instructions = [step.strip() for step in steps if step.strip()]
                    else:
                        # Fallback: split by lines
                        potential_instructions = [line.strip() for line in instructions_text.split('\n') if line.strip() and not line.strip().startswith('#')]
                    
                    if potential_instructions:
                        instructions_list = potential_instructions[:15]  # Limit to first 15 steps
                        logger.info(f"Extracted {len(instructions_list)} potential instructions from summary")
                else:
                    logger.debug(f"No instructions pattern found in summary. Summary preview: {summary[:200]}")
            
            return {
                "id": recipe.get("id"),
                "title": recipe.get("title") or recipe.get("name"),
                "description": recipe.get("description") or recipe.get("summary"),
                "ingredients": ingredients_list,
                "instructions": instructions_list,
                "nutrition": {
                    "calories": recipe.get("calculated_calories") or recipe.get("per_serving_calories", 0),
                    "protein": recipe.get("calculated_protein") or recipe.get("per_serving_protein", 0),
                    "carbs": recipe.get("calculated_carbs") or recipe.get("per_serving_carbs", 0),
                    "fats": recipe.get("calculated_fats") or recipe.get("per_serving_fat", 0)
                },
                "servings": recipe.get("servings", 1),
                "prep_time": recipe.get("prep_time"),
                "cook_time": recipe.get("cook_time"),
                "cuisine": recipe.get("cuisine"),
                "dietary_tags": recipe.get("dietary_tags", [])
            }
            
        except Exception as e:
            logger.error(f"Error getting recipe details: {str(e)}")
            return {
                "error": f"Unable to retrieve recipe: {str(e)}",
                "id": recipe_id
            }
    
    def _format_recipe_from_meal_plan(self, recipe_details: Dict[str, Any], meal: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format recipe details from meal plan for AI consumption.
        
        Args:
            recipe_details: Recipe details from meal plan
            meal: Meal data from meal plan
        
        Returns:
            Formatted recipe data
        """
        # Extract ingredients
        ingredients_list = []
        ingredients_from_meal = recipe_details.get("ingredients", [])
        for ing in ingredients_from_meal:
            if isinstance(ing, dict):
                name = ing.get("name", "")
                quantity = ing.get("quantity", 0)
                unit = ing.get("unit", "")
                if name:
                    if quantity and unit:
                        ingredients_list.append(f"{quantity} {unit} {name}")
                    else:
                        ingredients_list.append(name)
            else:
                ingredients_list.append(str(ing))
        
        # Extract instructions
        instructions_list = []
        instructions_from_meal = recipe_details.get("instructions", [])
        for inst in instructions_from_meal:
            if isinstance(inst, dict):
                step = inst.get("step") or inst.get("step_number")
                # Try multiple possible keys for instruction text
                description = (inst.get("description") or inst.get("instruction") or 
                             inst.get("text") or inst.get("step_title") or "")
                if description:
                    if step:
                        instructions_list.append(f"{step}. {description}")
                    else:
                        instructions_list.append(description)
            else:
                instructions_list.append(str(inst))
        
        # Extract nutrition
        nutrition = recipe_details.get("nutrition", {})
        if meal.get("calories"):
            nutrition["calories"] = meal.get("calories")
        if meal.get("protein"):
            nutrition["protein"] = meal.get("protein")
        if meal.get("carbs"):
            nutrition["carbs"] = meal.get("carbs")
        if meal.get("fats"):
            nutrition["fats"] = meal.get("fats")
        
        return {
            "id": recipe_details.get("id") or meal.get("recipe_id"),
            "title": recipe_details.get("title") or meal.get("name"),
            "description": recipe_details.get("summary") or recipe_details.get("description") or meal.get("description"),
            "ingredients": ingredients_list,
            "instructions": instructions_list,
            "nutrition": nutrition,
            "servings": recipe_details.get("servings", meal.get("servings", 1)),
            "prep_time": recipe_details.get("prep_time"),
            "cook_time": recipe_details.get("cook_time"),
            "cuisine": recipe_details.get("cuisine"),
            "dietary_tags": recipe_details.get("dietary_tags", [])
        }
    
    def _get_bmi_category(self, bmi: Optional[float]) -> str:
        """Get BMI category from BMI value."""
        if not bmi:
            return "unknown"
        if bmi < 18.5:
            return "underweight"
        elif bmi < 25:
            return "normal"
        elif bmi < 30:
            return "overweight"
        else:
            return "obese"

