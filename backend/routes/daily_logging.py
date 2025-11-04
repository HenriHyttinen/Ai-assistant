from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel
import logging
import traceback

from database import get_db
from auth.supabase_auth import get_current_user_supabase as get_current_user
from models.nutrition import NutritionalLog
from models.recipe import Recipe
from services.nutrition_service import NutritionService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/test")
async def test_endpoint():
    """Test endpoint to check if the router is working"""
    return {"message": "Daily logging router is working"}

class FoodLogEntry(BaseModel):
    recipe_id: Optional[str] = None
    food_name: str
    quantity: float
    unit: str
    meal_type: str  # breakfast, lunch, dinner, snack
    calories: float
    protein: float
    carbs: float
    fats: float

class DailyLogRequest(BaseModel):
    log_date: date
    entries: List[FoodLogEntry]

class DailyLogResponse(BaseModel):
    log_date: date
    total_calories: float
    total_protein: float
    total_carbs: float
    total_fats: float
    meal_count: int
    entries: List[dict]

@router.post("/log-daily-intake", response_model=DailyLogResponse)
async def log_daily_intake(
    request: DailyLogRequest,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log daily food intake"""
    try:
        user_id = current_user.id
        
        # Delete existing logs for this date
        db.query(NutritionalLog).filter(
            NutritionalLog.user_id == user_id,
            NutritionalLog.log_date == request.log_date
        ).delete()
        
        # Create new logs
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fats = 0
        
        entries_data = []
        
        for entry in request.entries:
            # Create nutritional log entry
            log_entry = NutritionalLog(
                user_id=user_id,
                log_date=request.log_date,
                meal_type=entry.meal_type,
                food_name=entry.food_name,
                calories=entry.calories,
                protein=entry.protein,
                carbs=entry.carbs,
                fats=entry.fats
            )
            db.add(log_entry)
            
            # Accumulate totals
            total_calories += entry.calories
            total_protein += entry.protein
            total_carbs += entry.carbs
            total_fats += entry.fats
            
            # Prepare entry data for response
            entry_data = {
                "food_name": entry.food_name,
                "quantity": entry.quantity,
                "unit": entry.unit,
                "meal_type": entry.meal_type,
                "calories": entry.calories,
                "protein": entry.protein,
                "carbs": entry.carbs,
                "fats": entry.fats
            }
            
            if entry.recipe_id:
                entry_data["recipe_id"] = entry.recipe_id
                
            entries_data.append(entry_data)
        
        db.commit()
        
        return DailyLogResponse(
            log_date=request.log_date,
            total_calories=total_calories,
            total_protein=total_protein,
            total_carbs=total_carbs,
            total_fats=total_fats,
            meal_count=len(request.entries),
            entries=entries_data
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to log daily intake: {str(e)}")

@router.get("/daily-log/{log_date}", response_model=DailyLogResponse)
async def get_daily_log(
    log_date: date,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily food log for a specific date"""
    try:
        print(f"Getting daily log for date: {log_date}")
        user_id = current_user.id
        print(f"User ID: {user_id}")
        
        # Get logs for the date
        logs = db.query(NutritionalLog).filter(
            NutritionalLog.user_id == user_id,
            NutritionalLog.log_date == log_date
        ).all()
        
        if not logs:
            return DailyLogResponse(
                log_date=log_date,
                total_calories=0,
                total_protein=0,
                total_carbs=0,
                total_fats=0,
                meal_count=0,
                entries=[]
            )
        
        # Calculate totals
        total_calories = sum(log.calories for log in logs)
        total_protein = sum(log.protein for log in logs)
        total_carbs = sum(log.carbs for log in logs)
        total_fats = sum(log.fats for log in logs)
        
        # Prepare entries data - include database ID for deletion
        entries_data = []
        for log in logs:
            entry_data = {
                "id": str(log.id),  # Include database ID for individual deletion
                "food_name": log.food_name or f"Meal ({log.meal_type})",  # Use saved name or default
                "quantity": 1,
                "unit": "serving",
                "meal_type": log.meal_type,
                "calories": log.calories,
                "protein": log.protein,
                "carbs": log.carbs,
                "fats": log.fats
            }
            # Include recipe_id if meal_id exists and we can look it up
            if log.meal_id:
                from models.nutrition import MealPlanRecipe
                meal_recipe = db.query(MealPlanRecipe).filter(
                    MealPlanRecipe.meal_id == log.meal_id
                ).first()
                if meal_recipe:
                    entry_data["recipe_id"] = meal_recipe.recipe_id
            entries_data.append(entry_data)
        
        return DailyLogResponse(
            log_date=log_date,
            total_calories=total_calories,
            total_protein=total_protein,
            total_carbs=total_carbs,
            total_fats=total_fats,
            meal_count=len(logs),
            entries=entries_data
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get daily log: {str(e)}")

@router.get("/recent-logs", response_model=List[DailyLogResponse])
async def get_recent_logs(
    days: int = 7,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent daily logs"""
    try:
        user_id = current_user.id
        end_date = date.today()
        start_date = date.today() - datetime.timedelta(days=days-1)
        
        # Get logs for the period
        logs = db.query(NutritionalLog).filter(
            NutritionalLog.user_id == user_id,
            NutritionalLog.log_date >= start_date,
            NutritionalLog.log_date <= end_date
        ).order_by(NutritionalLog.log_date.desc()).all()
        
        # Group by date
        logs_by_date = {}
        for log in logs:
            if log.log_date not in logs_by_date:
                logs_by_date[log.log_date] = []
            logs_by_date[log.log_date].append(log)
        
        # Create response for each date
        response_data = []
        for log_date in sorted(logs_by_date.keys(), reverse=True):
            date_logs = logs_by_date[log_date]
            
            total_calories = sum(log.calories for log in date_logs)
            total_protein = sum(log.protein for log in date_logs)
            total_carbs = sum(log.carbs for log in date_logs)
            total_fats = sum(log.fats for log in date_logs)
            
            entries_data = []
            for log in date_logs:
                entry_data = {
                    "food_name": f"Meal ({log.meal_type})",
                    "quantity": 1,
                    "unit": "serving",
                    "meal_type": log.meal_type,
                    "calories": log.calories,
                    "protein": log.protein,
                    "carbs": log.carbs,
                    "fats": log.fats
                }
                entries_data.append(entry_data)
            
            response_data.append(DailyLogResponse(
                log_date=log_date,
                total_calories=total_calories,
                total_protein=total_protein,
                total_carbs=total_carbs,
                total_fats=total_fats,
                meal_count=len(date_logs),
                entries=entries_data
            ))
        
        return response_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recent logs: {str(e)}")

@router.delete("/daily-log-entry/{log_id}")
async def delete_daily_log_entry(
    log_id: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a single nutritional log entry by ID"""
    try:
        user_id = current_user.id
        
        # Find the log entry
        log_entry = db.query(NutritionalLog).filter(
            NutritionalLog.id == log_id,
            NutritionalLog.user_id == user_id
        ).first()
        
        if not log_entry:
            raise HTTPException(status_code=404, detail="Log entry not found")
        
        # Delete the single entry
        db.delete(log_entry)
        db.commit()
        
        return {"message": f"Deleted log entry {log_id}"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete log entry: {str(e)}")

@router.delete("/daily-log/{log_date}")
async def delete_daily_log(
    log_date: date,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete daily food log for a specific date"""
    try:
        user_id = current_user.id
        
        # Delete logs for the date
        deleted_count = db.query(NutritionalLog).filter(
            NutritionalLog.user_id == user_id,
            NutritionalLog.log_date == log_date
        ).delete()
        
        db.commit()
        
        return {"message": f"Deleted {deleted_count} log entries for {log_date}"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete daily log: {str(e)}")

@router.post("/log-from-meal-plan")
async def log_from_meal_plan(
    log_date: date,
    meal_plan_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Automatically log meals from a meal plan to daily intake"""
    try:
        if not current_user:
            raise HTTPException(status_code=401, detail="User not authenticated")
        
        user_id = current_user.id
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid user ID")
        
        logger.info(f"Logging meals from meal plan {meal_plan_id} for user {user_id} on date {log_date}")
        
        # Get meal plan with meals and recipes
        from models.nutrition import MealPlan, MealPlanMeal, MealPlanRecipe
        
        meal_plan = db.query(MealPlan).filter(
            MealPlan.id == meal_plan_id,
            MealPlan.user_id == user_id
        ).first()
        
        if not meal_plan:
            raise HTTPException(status_code=404, detail="Meal plan not found")
        
        # Get meals for the specific date
        meals = db.query(MealPlanMeal).filter(
            MealPlanMeal.meal_plan_id == meal_plan_id,
            MealPlanMeal.meal_date == log_date
        ).all()
        
        if not meals:
            return {"message": f"No meals found for {log_date} in this meal plan"}
        
        # Delete existing logs for this date (to avoid duplicates)
        db.query(NutritionalLog).filter(
            NutritionalLog.user_id == user_id,
            NutritionalLog.log_date == log_date
        ).delete(synchronize_session=False)
        
        # Helper function to normalize meal_type to valid values
        def normalize_meal_type(meal_type: str) -> str:
            """Normalize meal_type to breakfast, lunch, dinner, or snack"""
            if not meal_type:
                return 'snack'
            meal_type_lower = meal_type.lower().strip()
            if meal_type_lower in ['breakfast', 'lunch', 'dinner']:
                return meal_type_lower
            # Any snack variant (morning snack, afternoon snack, evening snack) -> snack
            if 'snack' in meal_type_lower:
                return 'snack'
            # Default to snack if unknown
            return 'snack'
        
        # Create nutritional logs from meal plan
        logged_meals = 0
        for meal in meals:
            try:
                # Normalize meal_type to valid value
                normalized_meal_type = normalize_meal_type(meal.meal_type)
                
                # Get recipe details if available
                meal_recipe = db.query(MealPlanRecipe).filter(
                    MealPlanRecipe.meal_id == meal.id
                ).first()
                
                if meal_recipe:
                    # Get recipe details
                    recipe = db.query(Recipe).filter(Recipe.id == meal_recipe.recipe_id).first()
                    if recipe:
                        # Calculate nutrition per serving
                        servings = meal_recipe.servings or 1
                        if servings <= 0:
                            servings = 1
                        
                        calories_per_serving = (meal.calories or 0) / servings if servings > 0 else (meal.calories or 0)
                        protein_per_serving = (meal.protein or 0) / servings if servings > 0 else (meal.protein or 0)
                        carbs_per_serving = (meal.carbs or 0) / servings if servings > 0 else (meal.carbs or 0)
                        fats_per_serving = (meal.fats or 0) / servings if servings > 0 else (meal.fats or 0)
                        
                        # Extract fiber, sugar, sodium from recipe if available, or use 0
                        fiber_value = 0.0
                        sugar_value = 0.0
                        sodium_value = 0.0
                        
                        # Try to get from recipe per-serving values (divide by servings again since meal_recipe.servings is the portion size)
                        # Note: recipe.per_serving_* is already per serving, but meal_recipe.servings might be > 1
                        if hasattr(recipe, 'per_serving_fiber') and recipe.per_serving_fiber is not None:
                            fiber_value = float(recipe.per_serving_fiber)
                        elif hasattr(recipe, 'total_fiber') and recipe.total_fiber is not None:
                            # Calculate from total if per_serving not available
                            recipe_servings = recipe.servings or 1
                            fiber_value = float(recipe.total_fiber / recipe_servings) if recipe_servings > 0 else 0.0
                        
                        # Recipe model doesn't have sugar fields, use 0.0 (sugar is typically tracked separately)
                        sugar_value = 0.0
                        
                        if hasattr(recipe, 'per_serving_sodium') and recipe.per_serving_sodium is not None:
                            sodium_value = float(recipe.per_serving_sodium)
                        elif hasattr(recipe, 'total_sodium') and recipe.total_sodium is not None:
                            recipe_servings = recipe.servings or 1
                            sodium_value = float(recipe.total_sodium / recipe_servings) if recipe_servings > 0 else 0.0
                        
                        # Create nutritional log entry
                        log_entry = NutritionalLog(
                            user_id=int(user_id),  # Ensure integer
                            log_date=log_date,
                            meal_type=normalized_meal_type,
                            food_name=meal.meal_name or recipe.title if meal.meal_name else recipe.title,
                            meal_id=meal.id,
                            calories=float(calories_per_serving or 0.0),
                            protein=float(protein_per_serving or 0.0),
                            carbs=float(carbs_per_serving or 0.0),
                            fats=float(fats_per_serving or 0.0),
                            fiber=fiber_value,
                            sugar=sugar_value,
                            sodium=sodium_value
                        )
                        db.add(log_entry)
                        logged_meals += 1
                else:
                    # No recipe, use meal data directly (fiber, sugar, sodium may not be on meal)
                    # Try to get from recipe_details JSON if available
                    fiber_value = 0.0
                    sugar_value = 0.0
                    sodium_value = 0.0
                    
                    if meal.recipe_details and isinstance(meal.recipe_details, dict):
                        nutrition = meal.recipe_details.get('nutrition', {})
                        if nutrition:
                            fiber_value = float(nutrition.get('fiber', 0) or 0)
                            sugar_value = float(nutrition.get('sugar', 0) or 0)
                            sodium_value = float(nutrition.get('sodium', 0) or 0)
                    
                    log_entry = NutritionalLog(
                        user_id=int(user_id),  # Ensure integer
                        log_date=log_date,
                        meal_type=normalized_meal_type,
                        food_name=meal.meal_name or f"Meal ({normalized_meal_type})",
                        meal_id=meal.id,
                        calories=float(meal.calories or 0.0),
                        protein=float(meal.protein or 0.0),
                        carbs=float(meal.carbs or 0.0),
                        fats=float(meal.fats or 0.0),
                        fiber=fiber_value,
                        sugar=sugar_value,
                        sodium=sodium_value
                    )
                    db.add(log_entry)
                    logged_meals += 1
            except Exception as meal_error:
                logger.error(f"Error processing meal {meal.id}: {type(meal_error).__name__}: {str(meal_error)}", exc_info=True)
                continue  # Skip this meal and continue with others
        
        db.commit()
        
        # Automatically update goal progress from the logged nutrition data
        try:
            from services.nutrition_goals_service import NutritionGoalsService
            # NutritionalLog is already imported at the top of the file (line 12)
            from models.nutrition_goals import NutritionGoal, GoalType
            from sqlalchemy import func
            # or_ is already imported at the top
            from datetime import datetime as dt
            
            goals_service = NutritionGoalsService()
            
            # Aggregate nutrition totals for this date
            logs = db.query(NutritionalLog).filter(
                NutritionalLog.user_id == user_id,
                NutritionalLog.log_date == log_date
            ).all()
            
            if logs:
                # Calculate totals
                total_calories = sum(log.calories or 0 for log in logs)
                total_protein = sum(log.protein or 0 for log in logs)
                total_carbs = sum(log.carbs or 0 for log in logs)
                total_fats = sum(log.fats or 0 for log in logs)
                total_fiber = sum(log.fiber or 0 for log in logs)
                total_sodium = sum(log.sodium or 0 for log in logs)
                
                # Get active goals that match the logged nutrient types
                log_datetime = dt.combine(log_date, dt.min.time())
                goal_query = db.query(NutritionGoal).filter(
                    NutritionGoal.user_id == user_id,
                    NutritionGoal.status == 'active',
                    NutritionGoal.start_date <= log_datetime
                )
                
                # Filter by target_date if it exists
                goal_query = goal_query.filter(
                    or_(
                        NutritionGoal.target_date == None,
                        NutritionGoal.target_date >= log_datetime
                    )
                )
                
                active_goals = goal_query.all()
                
                # Map nutrient types to goal types
                nutrient_to_goal_type = {
                    'calories': GoalType.CALORIES,
                    'protein': GoalType.PROTEIN,
                    'carbs': GoalType.CARBS,
                    'fat': GoalType.FAT,
                    'fiber': GoalType.FIBER,
                    'sodium': GoalType.SODIUM,
                }
                
                # Update progress for matching goals
                for goal in active_goals:
                    goal_type_value = goal.goal_type.value if hasattr(goal.goal_type, 'value') else goal.goal_type
                    
                    # Get achieved value based on goal type
                    achieved_value = 0.0
                    if goal_type_value == 'calories':
                        achieved_value = total_calories
                    elif goal_type_value == 'protein':
                        achieved_value = total_protein
                    elif goal_type_value == 'carbs':
                        achieved_value = total_carbs
                    elif goal_type_value == 'fat':
                        achieved_value = total_fats
                    elif goal_type_value == 'fiber':
                        achieved_value = total_fiber
                    elif goal_type_value == 'sodium':
                        achieved_value = total_sodium
                    else:
                        continue  # Skip goals that don't match logged nutrients
                    
                    # Create or update goal progress log
                    from schemas.nutrition_goals import GoalProgressLogCreate
                    progress_data = GoalProgressLogCreate(
                        goal_id=goal.id,
                        date=log_datetime,
                        achieved_value=achieved_value
                    )
                    
                    try:
                        goals_service.log_progress(db, user_id, progress_data)
                    except Exception as e:
                        # Use module-level logger (already defined at top of file)
                        logger.warning(f"Failed to update goal {goal.id} progress: {str(e)}")
                        continue
        except Exception as goal_error:
            # Use module-level logger (already defined at top of file)
            logger.error(f"Error updating goals after logging meal plan: {str(goal_error)}")
            # Don't fail the entire request if goal update fails
        
        return {
            "message": f"Successfully logged {logged_meals} meals from meal plan to daily intake",
            "logged_meals": logged_meals,
            "log_date": log_date
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        error_type = type(e).__name__
        error_message = str(e)
        error_traceback = traceback.format_exc()
        
        logger.error(f"Error logging from meal plan: {error_type}: {error_message}", exc_info=True)
        logger.error(f"Full traceback:\n{error_traceback}")
        
        # Return more detailed error for debugging
        detail_message = f"Failed to log from meal plan: {error_type}: {error_message}"
        if "UnboundLocalError" in error_type:
            detail_message += " (This is a code bug - please check server logs)"
        
        raise HTTPException(
            status_code=500,
            detail=detail_message
        )
