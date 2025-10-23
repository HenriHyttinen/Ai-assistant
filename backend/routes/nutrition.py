from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Any
from datetime import datetime, date, timedelta

from database import get_db
from auth.supabase_auth import get_current_user_supabase as get_current_user
from models.user import User
from models.nutrition import (
    UserNutritionPreferences, MealPlan, NutritionalLog, 
    Recipe, Ingredient, ShoppingList
)
from schemas.nutrition import (
    UserNutritionPreferencesCreate, UserNutritionPreferencesUpdate,
    UserNutritionPreferencesResponse, MealPlanRequest, MealPlanResponse,
    NutritionalLogCreate, NutritionalLogResponse, RecipeSearchRequest,
    RecipeResponse, ShoppingListCreate, ShoppingListResponse,
    NutritionalAnalysisRequest
)
from ai.nutrition_ai import NutritionAI
from services.nutrition_service import NutritionService

router = APIRouter()

# Initialize services
nutrition_ai = NutritionAI()
nutrition_service = NutritionService()

@router.post("/preferences", response_model=UserNutritionPreferencesResponse)
def create_nutrition_preferences(
    preferences: UserNutritionPreferencesCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update user nutrition preferences"""
    try:
        # Check if user already has preferences
        existing_prefs = db.query(UserNutritionPreferences).filter(
            UserNutritionPreferences.user_id == current_user.id
        ).first()
        
        if existing_prefs:
            # Update existing preferences
            for field, value in preferences.dict(exclude_unset=True).items():
                setattr(existing_prefs, field, value)
            existing_prefs.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_prefs)
            return existing_prefs
        else:
            # Create new preferences
            db_preferences = UserNutritionPreferences(
                user_id=current_user.id,
                **preferences.dict()
            )
            db.add(db_preferences)
            db.commit()
            db.refresh(db_preferences)
            return db_preferences
            
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating nutrition preferences: {str(e)}"
        )

@router.get("/preferences", response_model=UserNutritionPreferencesResponse)
def get_nutrition_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user nutrition preferences"""
    preferences = db.query(UserNutritionPreferences).filter(
        UserNutritionPreferences.user_id == current_user.id
    ).first()
    
    if not preferences:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nutrition preferences not found"
        )
    
    return preferences

@router.put("/preferences", response_model=UserNutritionPreferencesResponse)
def update_nutrition_preferences(
    preferences: UserNutritionPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user nutrition preferences"""
    try:
        db_preferences = db.query(UserNutritionPreferences).filter(
            UserNutritionPreferences.user_id == current_user.id
        ).first()
        
        if not db_preferences:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nutrition preferences not found"
            )
        
        # Update only provided fields
        for field, value in preferences.dict(exclude_unset=True).items():
            setattr(db_preferences, field, value)
        
        db_preferences.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_preferences)
        return db_preferences
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating nutrition preferences: {str(e)}"
        )

@router.post("/meal-plans/generate", response_model=MealPlanResponse)
def generate_meal_plan(
    plan_request: MealPlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate AI-powered meal plan"""
    try:
        # Get user preferences
        preferences = db.query(UserNutritionPreferences).filter(
            UserNutritionPreferences.user_id == current_user.id
        ).first()
        
        if not preferences:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please set up your nutrition preferences first"
            )
        
        # Convert preferences to dict for AI
        prefs_dict = {
            "dietary_preferences": preferences.dietary_preferences or [],
            "allergies": preferences.allergies or [],
            "disliked_ingredients": preferences.disliked_ingredients or [],
            "cuisine_preferences": preferences.cuisine_preferences or [],
            "daily_calorie_target": preferences.daily_calorie_target,
            "protein_target": preferences.protein_target,
            "carbs_target": preferences.carbs_target,
            "fats_target": preferences.fats_target,
            "meals_per_day": preferences.meals_per_day
        }
        
        # Generate meal plan using AI
        ai_meal_plan = nutrition_ai.generate_meal_plan_sequential(prefs_dict, plan_request)
        
        # Save meal plan to database
        meal_plan = nutrition_service.create_meal_plan(
            db=db,
            user_id=current_user.id,
            plan_request=plan_request,
            ai_meal_plan=ai_meal_plan
        )
        
        return meal_plan
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating meal plan: {str(e)}"
        )

@router.get("/meal-plans", response_model=List[MealPlanResponse])
def get_meal_plans(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's meal plans"""
    meal_plans = db.query(MealPlan).filter(
        MealPlan.user_id == current_user.id
    ).order_by(MealPlan.created_at.desc()).offset(offset).limit(limit).all()
    
    return meal_plans

@router.get("/meal-plans/{meal_plan_id}", response_model=MealPlanResponse)
def get_meal_plan(
    meal_plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get specific meal plan"""
    meal_plan = db.query(MealPlan).filter(
        MealPlan.id == meal_plan_id,
        MealPlan.user_id == current_user.id
    ).first()
    
    if not meal_plan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Meal plan not found"
        )
    
    return meal_plan

@router.post("/recipes/search", response_model=List[RecipeResponse])
def search_recipes(
    search_request: RecipeSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search recipes with filters"""
    try:
        recipes = nutrition_service.search_recipes(db, search_request)
        return recipes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching recipes: {str(e)}"
        )

@router.post("/recipes/generate")
def generate_recipe(
    query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate AI recipe using RAG"""
    try:
        # Get user preferences
        preferences = db.query(UserNutritionPreferences).filter(
            UserNutritionPreferences.user_id == current_user.id
        ).first()
        
        prefs_dict = {}
        if preferences:
            prefs_dict = {
                "dietary_preferences": preferences.dietary_preferences or [],
                "allergies": preferences.allergies or [],
                "disliked_ingredients": preferences.disliked_ingredients or [],
                "cuisine_preferences": preferences.cuisine_preferences or []
            }
        
        # Generate recipe using RAG
        recipe = nutrition_ai.generate_recipe_with_rag(query, prefs_dict, db)
        return recipe
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating recipe: {str(e)}"
        )

@router.post("/nutritional-logs", response_model=NutritionalLogResponse)
def log_nutrition(
    log_data: NutritionalLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Log nutritional intake"""
    try:
        nutritional_log = NutritionalLog(
            user_id=current_user.id,
            **log_data.dict()
        )
        db.add(nutritional_log)
        db.commit()
        db.refresh(nutritional_log)
        return nutritional_log
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging nutrition: {str(e)}"
        )

@router.get("/nutritional-logs", response_model=List[NutritionalLogResponse])
def get_nutritional_logs(
    start_date: date = Query(...),
    end_date: date = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get nutritional logs for date range"""
    logs = db.query(NutritionalLog).filter(
        NutritionalLog.user_id == current_user.id,
        NutritionalLog.log_date >= start_date,
        NutritionalLog.log_date <= end_date
    ).order_by(NutritionalLog.log_date.desc()).all()
    
    return logs

@router.post("/shopping-lists", response_model=ShoppingListResponse)
def create_shopping_list(
    shopping_list: ShoppingListCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create shopping list from meal plan"""
    try:
        shopping_list_obj = nutrition_service.create_shopping_list(
            db=db,
            user_id=current_user.id,
            shopping_list_data=shopping_list
        )
        return shopping_list_obj
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating shopping list: {str(e)}"
        )

@router.get("/shopping-lists", response_model=List[ShoppingListResponse])
def get_shopping_lists(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's shopping lists"""
    shopping_lists = db.query(ShoppingList).filter(
        ShoppingList.user_id == current_user.id,
        ShoppingList.is_active == True
    ).order_by(ShoppingList.created_at.desc()).all()
    
    return shopping_lists

@router.get("/nutritional-analysis")
def get_nutritional_analysis(
    start_date: date = Query(...),
    end_date: date = Query(...),
    analysis_type: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get nutritional analysis and insights"""
    try:
        analysis = nutrition_service.get_nutritional_analysis(
            db=db,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            analysis_type=analysis_type
        )
        return analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting nutritional analysis: {str(e)}"
        )
