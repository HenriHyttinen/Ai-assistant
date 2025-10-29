from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel

from database import get_db
from auth.supabase_auth import get_current_user_supabase as get_current_user
from models.nutrition import NutritionalLog
from models.recipe import Recipe
from services.nutrition_service import NutritionService

router = APIRouter()

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
        
        # Prepare entries data
        entries_data = []
        for log in logs:
            entry_data = {
                "food_name": f"Meal ({log.meal_type})",  # Default name
                "quantity": 1,
                "unit": "serving",
                "meal_type": log.meal_type,
                "calories": log.calories,
                "protein": log.protein,
                "carbs": log.carbs,
                "fats": log.fats
            }
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
        user_id = current_user.id
        
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
        ).delete()
        
        # Create nutritional logs from meal plan
        logged_meals = 0
        for meal in meals:
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
                    calories_per_serving = meal.calories / servings if servings > 0 else meal.calories
                    protein_per_serving = meal.protein / servings if servings > 0 else meal.protein
                    carbs_per_serving = meal.carbs / servings if servings > 0 else meal.carbs
                    fats_per_serving = meal.fats / servings if servings > 0 else meal.fats
                    
                    # Create nutritional log entry
                    log_entry = NutritionalLog(
                        user_id=user_id,
                        log_date=log_date,
                        meal_type=meal.meal_type,
                        calories=calories_per_serving,
                        protein=protein_per_serving,
                        carbs=carbs_per_serving,
                        fats=fats_per_serving
                    )
                    db.add(log_entry)
                    logged_meals += 1
            else:
                # No recipe, use meal data directly
                log_entry = NutritionalLog(
                    user_id=user_id,
                    log_date=log_date,
                    meal_type=meal.meal_type,
                    calories=meal.calories,
                    protein=meal.protein,
                    carbs=meal.carbs,
                    fats=meal.fats
                )
                db.add(log_entry)
                logged_meals += 1
        
        db.commit()
        
        return {
            "message": f"Successfully logged {logged_meals} meals from meal plan to daily intake",
            "logged_meals": logged_meals,
            "log_date": log_date
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to log from meal plan: {str(e)}")
