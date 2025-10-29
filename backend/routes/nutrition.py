from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Any, Dict
from datetime import datetime, date, timedelta

from database import get_db
from auth.supabase_auth import get_current_user_supabase as get_current_user
from models.user import User
from models.recipe import Recipe, Ingredient
from models.nutrition import (
    UserNutritionPreferences, MealPlan, NutritionalLog, 
    ShoppingList
)
from schemas.nutrition import (
    UserNutritionPreferencesCreate, UserNutritionPreferencesUpdate,
    UserNutritionPreferencesResponse, MealPlanRequest, MealPlanResponse,
    MealPlanGenerationRequest, NutritionalLogCreate, NutritionalLogResponse, 
    RecipeSearchRequest, RecipeResponse, ShoppingListCreate, ShoppingListResponse,
    NutritionalAnalysisRequest
)
from ai.nutrition_ai import NutritionAI
from services.nutrition_service import NutritionService
from services.shopping_list_service import ShoppingListService
from services.integration_service import IntegrationService
from services.meal_alternatives_service import MealAlternativesService
from services.meal_regeneration_service import MealRegenerationService
from services.shopping_list_service import ShoppingListService
from services.portion_adjustment_service import PortionAdjustmentService
from services.measurement_standardization_service import MeasurementStandardizationService
from services.nutrition_analytics import NutritionAnalyticsService
from services.recipe_recommendation_service import RecipeRecommendationService
from services.meal_plan_versioning_service import meal_plan_versioning_service

router = APIRouter()

@router.get("/test")
async def test_endpoint():
    """Test endpoint to check if the router is working"""
    return {"message": "Nutrition router is working"}

@router.get("/test-sorting")
async def test_sorting(db: Session = Depends(get_db)):
    """Test endpoint to check if sorting is working"""
    try:
        # Test prep_time sorting
        recipes_asc = db.query(Recipe).filter(Recipe.is_active == True).order_by(Recipe.prep_time.asc()).limit(5).all()
        recipes_desc = db.query(Recipe).filter(Recipe.is_active == True).order_by(Recipe.prep_time.desc()).limit(5).all()
        
        return {
            "message": "Sorting test",
            "ascending": [{"title": r.title, "prep_time": r.prep_time} for r in recipes_asc],
            "descending": [{"title": r.title, "prep_time": r.prep_time} for r in recipes_desc]
        }
    except Exception as e:
        return {"error": str(e)}

@router.post("/test-search-simple")
async def test_search_simple(
    search_request: RecipeSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Simple test endpoint to check search and sorting"""
    try:
        # Get recipes without any complex logic
        recipes = db.query(Recipe).filter(Recipe.is_active == True).limit(10).all()
        
        # Convert to simple format
        simple_recipes = []
        for recipe in recipes:
            simple_recipes.append({
                "id": recipe.id,
                "title": recipe.title,
                "prep_time": recipe.prep_time,
                "calories": getattr(recipe, 'calculated_calories', 0),
                "protein": getattr(recipe, 'calculated_protein', 0)
            })
        
        # Apply sorting if requested
        if search_request.sort_by == 'prep_time':
            if search_request.sort_order == 'asc':
                simple_recipes.sort(key=lambda x: x['prep_time'])
            else:
                simple_recipes.sort(key=lambda x: x['prep_time'], reverse=True)
        
        return {
            "message": "Simple search test",
            "sort_by": search_request.sort_by,
            "sort_order": search_request.sort_order,
            "recipes": simple_recipes
        }
    except Exception as e:
        return {"error": str(e)}

# Initialize services
nutrition_ai = NutritionAI()
nutrition_service = NutritionService()

def _sort_recipes(recipes: List[dict], sort_by: str, sort_order: str = "asc") -> List[dict]:
    """Sort recipes based on the specified criteria"""
    if not recipes:
        return recipes
    
    # Define sort key functions
    def get_sort_key(recipe):
        if sort_by == "title":
            return recipe.get("title", "").lower()
        elif sort_by == "calories":
            return recipe.get("calories", 0)
        elif sort_by == "protein":
            return recipe.get("protein", 0)
        elif sort_by == "carbs":
            return recipe.get("carbs", 0)
        elif sort_by == "fats":
            return recipe.get("fats", 0)
        elif sort_by == "prep_time":
            return recipe.get("prep_time", 0)
        elif sort_by == "difficulty":
            # Map difficulty levels to numeric values for sorting
            difficulty_map = {"easy": 1, "medium": 2, "hard": 3}
            return difficulty_map.get(recipe.get("difficulty_level", "easy"), 1)
        elif sort_by == "rating":
            return recipe.get("rating", 0)
        elif sort_by == "id":
            return recipe.get("id", "")
        else:
            return recipe.get("title", "").lower()
    
    # Sort recipes
    reverse = sort_order.lower() == "desc"
    sorted_recipes = sorted(recipes, key=get_sort_key, reverse=reverse)
    
    print(f"Sorted {len(sorted_recipes)} recipes by {sort_by} ({sort_order})")
    return sorted_recipes

@router.get("/meal-plans/{meal_plan_id}/versions")
def get_meal_plan_versions(
    meal_plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all versions of a meal plan (by same date/type)."""
    try:
        versions = meal_plan_versioning_service.get_meal_plan_versions(db, current_user.id, meal_plan_id)
        return {"versions": versions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/meal-plans/{meal_plan_id}/versions")
def create_meal_plan_version(
    meal_plan_id: str,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new meal plan version due to an action (e.g., regenerate_plan)."""
    action = payload.get("action", "regenerate_plan")
    description = payload.get("description")
    new_plan_id = meal_plan_versioning_service.create_meal_plan_version(db, current_user.id, meal_plan_id, action, description)
    if not new_plan_id:
        raise HTTPException(status_code=400, detail="Failed to create version")
    return {"new_plan_id": new_plan_id}

@router.post("/meal-plans/restore/{version_id}")
def restore_meal_plan_version(
    version_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Restore a meal plan version and make it the active plan (returns new plan id)."""
    new_plan_id = meal_plan_versioning_service.restore_meal_plan_version(db, current_user.id, version_id)
    if not new_plan_id:
        raise HTTPException(status_code=400, detail="Failed to restore version")
    return {"new_plan_id": new_plan_id}

@router.get("/preferences", response_model=UserNutritionPreferencesResponse)
def get_nutrition_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user nutrition preferences"""
    try:
        preferences = db.query(UserNutritionPreferences).filter(
            UserNutritionPreferences.user_id == current_user.id
        ).first()
        
        if not preferences:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nutrition preferences not found. Please set up your preferences first."
            )
        
        return preferences
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving nutrition preferences: {str(e)}"
        )

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


@router.get("/preferences/integrated")
def get_integrated_nutrition_preferences(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get nutrition preferences with data pre-filled from health profile"""
    try:
        integration_service = IntegrationService()
        integrated_data = integration_service.get_integrated_nutrition_preferences(db, current_user.id)
        return integrated_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting integrated preferences: {str(e)}"
        )

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

@router.post("/meal-plans/generate-enhanced", response_model=Dict[str, Any])
def generate_enhanced_meal_plan(
    plan_request: MealPlanGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate enhanced AI-powered meal plan with advanced personalization and dietary restrictions"""
    try:
        enhanced_meal_plan = nutrition_service.generate_enhanced_meal_plan(
            db, current_user.id, plan_request
        )
        return enhanced_meal_plan
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating enhanced meal plan: {str(e)}"
        )

@router.post("/meal-plans/generate", response_model=MealPlanResponse)
def generate_meal_plan(
    plan_request: MealPlanGenerationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate AI-powered meal plan with personalized targets"""
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
        
        # Get personalized targets based on health profile, BMI, and activity level
        personalized_targets = nutrition_service.calculate_personalized_targets(db, current_user.id)
        
        # Get wellness score for additional personalization
        wellness_data = nutrition_service.update_wellness_score_from_nutrition(db, current_user.id, "week")
        
        # Convert preferences to dict for AI, prioritizing personalized targets
        prefs_dict = {
            "dietary_preferences": preferences.dietary_preferences or [],
            "allergies": preferences.allergies or [],
            "disliked_ingredients": preferences.disliked_ingredients or [],
            "cuisine_preferences": preferences.cuisine_preferences or [],
            # Use personalized targets if available, otherwise fall back to user preferences
            "daily_calorie_target": personalized_targets.get("calorie_target") or preferences.daily_calorie_target,
            "protein_target": personalized_targets.get("protein_target") or preferences.protein_target,
            "carbs_target": personalized_targets.get("carbs_target") or preferences.carbs_target,
            "fats_target": personalized_targets.get("fats_target") or preferences.fats_target,
            "meals_per_day": preferences.meals_per_day,
            # Add personalization context for AI
            "personalization_context": {
                "bmi": personalized_targets.get("bmi"),
                "activity_level": personalized_targets.get("activity_level"),
                "fitness_goal": personalized_targets.get("fitness_goal"),
                "wellness_score": wellness_data.get("wellness_score"),
                "is_personalized": personalized_targets.get("personalized", False)
            }
        }
        
        # Override with request preferences if provided
        if plan_request.preferences_override:
            print(f"Overriding preferences with: {plan_request.preferences_override}")
            for key, value in plan_request.preferences_override.items():
                if value is not None:
                    prefs_dict[key] = value
        
        print(f"Final preferences (with personalization): {prefs_dict}")
        
        # Generate meal plan using AI with personalized context and RAG
        ai_meal_plan = nutrition_ai.generate_meal_plan_sequential(prefs_dict, plan_request, db)
        
        # Save meal plan to database
        meal_plan = nutrition_service.create_meal_plan(
            db=db,
            user_id=current_user.id,
            plan_request=plan_request,
            ai_meal_plan=ai_meal_plan
        )
        
        # Convert to response format
        return nutrition_service._convert_meal_plan_to_response(meal_plan)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating meal plan: {str(e)}"
        )

@router.get("/meal-plans/{meal_plan_id}/alternatives/{meal_type}")
def get_meal_alternatives(
    meal_plan_id: str,
    meal_type: str,
    count: int = Query(3, ge=1, le=5),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get alternative meal options for a specific meal type"""
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
        
        # Convert preferences to dict
        prefs_dict = {
            "dietary_preferences": preferences.dietary_preferences or [],
            "allergies": preferences.allergies or [],
            "disliked_ingredients": preferences.disliked_ingredients or [],
            "cuisine_preferences": preferences.cuisine_preferences or [],
            "daily_calorie_target": preferences.daily_calorie_target,
            "protein_target": preferences.protein_target,
            "meals_per_day": preferences.meals_per_day,
            "snacks_per_day": preferences.snacks_per_day
        }
        
        # Generate alternatives
        alternatives_service = MealAlternativesService()
        alternatives = alternatives_service.generate_meal_alternatives(
            db, meal_plan_id, meal_type, prefs_dict, count
        )
        
        return {
            "meal_plan_id": meal_plan_id,
            "meal_type": meal_type,
            "alternatives": alternatives,
            "count": len(alternatives)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating meal alternatives: {str(e)}"
        )

@router.put("/meal-plans/{meal_plan_id}/reorder")
def reorder_meals(
    meal_plan_id: str,
    meal_order: List[str],  # List of meal IDs in new order
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Reorder meals within a meal plan"""
    try:
        # Verify meal plan belongs to user
        meal_plan = db.query(MealPlan).filter(
            MealPlan.id == meal_plan_id,
            MealPlan.user_id == current_user.id
        ).first()
        
        if not meal_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal plan not found"
            )
        
        # Get all meals for this meal plan
        meals = db.query(MealPlanMeal).filter(
            MealPlanMeal.meal_plan_id == meal_plan_id
        ).all()
        
        # Create a mapping of meal ID to meal object
        meal_map = {meal.id: meal for meal in meals}
        
        # Update meal order (we'll use a simple approach with a display_order field)
        # For now, we'll just update the meal_time to reflect the order
        for index, meal_id in enumerate(meal_order):
            if meal_id in meal_map:
                meal = meal_map[meal_id]
                # Use meal_time to store order (this is a simple approach)
                # In a production system, you'd want a dedicated order field
                from datetime import datetime, time
                meal.meal_time = datetime.combine(meal.meal_date, time(index, 0, 0))
        
        db.commit()
        
        return {"message": "Meal order updated successfully", "new_order": meal_order}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error reordering meals: {str(e)}"
        )

@router.post("/meal-plans/{meal_plan_id}/custom-meal")
def add_custom_meal(
    meal_plan_id: str,
    custom_meal_data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a custom meal to an existing meal plan"""
    try:
        # Verify meal plan belongs to user
        meal_plan = db.query(MealPlan).filter(
            MealPlan.id == meal_plan_id,
            MealPlan.user_id == current_user.id
        ).first()
        
        if not meal_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal plan not found"
            )
        
        # Create new meal entry
        from datetime import date
        new_meal = MealPlanMeal(
            meal_plan_id=meal_plan_id,
            meal_date=date.today(),  # Use current date or allow specification
            meal_type=custom_meal_data.get('meal_type', 'breakfast'),
            meal_name=custom_meal_data.get('meal_name', 'Custom Meal'),
            calories=custom_meal_data.get('nutrition', {}).get('calories', 0),
            protein=custom_meal_data.get('nutrition', {}).get('protein', 0),
            carbs=custom_meal_data.get('nutrition', {}).get('carbs', 0),
            fats=custom_meal_data.get('nutrition', {}).get('fats', 0),
            recipe_details=custom_meal_data,  # Store full custom meal data
            cuisine=custom_meal_data.get('cuisine', 'Custom')
        )
        
        db.add(new_meal)
        db.commit()
        db.refresh(new_meal)
        
        return {
            "message": "Custom meal added successfully",
            "meal_id": new_meal.id,
            "meal": {
                "id": new_meal.id,
                "meal_name": new_meal.meal_name,
                "meal_type": new_meal.meal_type,
                "calories": new_meal.calories,
                "protein": new_meal.protein,
                "carbs": new_meal.carbs,
                "fats": new_meal.fats,
                "cuisine": new_meal.cuisine
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding custom meal: {str(e)}"
        )

@router.get("/meal-plans", response_model=List[MealPlanResponse])
def get_meal_plans(
    date: Optional[str] = Query(None, description="Filter by date (YYYY-MM-DD)"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's meal plans"""
    query = db.query(MealPlan).filter(MealPlan.user_id == current_user.id)
    
    if date:
        from datetime import datetime
        filter_date = datetime.strptime(date, "%Y-%m-%d").date()
        query = query.filter(MealPlan.start_date == filter_date)
    
    meal_plans = query.order_by(MealPlan.created_at.desc()).offset(offset).limit(limit).all()
    
    # Convert to proper response format
    return [nutrition_service._convert_meal_plan_to_response(meal_plan) for meal_plan in meal_plans]

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
    
    return nutrition_service._convert_meal_plan_to_response(meal_plan)

@router.post("/recipes/search")
def search_recipes(
    search_request: RecipeSearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search recipes with filters - Use database (500 recipes) not SimpleNutritionAI (10 recipes)"""
    try:
        print(f"🔍 SEARCH REQUEST RECEIVED: {search_request}")
        # Use the original nutrition service that queries the DATABASE (500 recipes)
        result = nutrition_service.search_recipes(db, search_request)
        print(f"🔍 SEARCH RESULT: {type(result)}, length: {len(result) if isinstance(result, (list, dict)) else 'unknown'}")
        
        # The nutrition_service returns a dictionary with pagination info
        if isinstance(result, dict):
            return result
        else:
            # Fallback if it returns a list
            return {
                "recipes": result,
                "total": len(result),
                "pages": 1,
                "current_page": 1,
                "per_page": len(result)
            }
        
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
        
        # Generate recipe using AI with RAG (Retrieval-Augmented Generation)
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
        # Convert to response format with calculated fields
        return nutrition_service._convert_shopping_list_to_response(shopping_list_obj)
        
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
    
    # Convert each shopping list to response format
    return [nutrition_service._convert_shopping_list_to_response(sl) for sl in shopping_lists]

@router.patch("/shopping-lists/{list_id}/items/{item_id}")
def update_shopping_list_item(
    list_id: str,
    item_id: int,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update quantity/unit/notes/is_purchased for a shopping list item."""
    try:
        nutrition_service = NutritionService()
        updated = nutrition_service.update_shopping_list_item(
            db,
            current_user.id,
            list_id,
            item_id,
            quantity=payload.get("quantity"),
            unit=payload.get("unit"),
            notes=payload.get("notes"),
            is_purchased=payload.get("is_purchased"),
        )
        return nutrition_service._convert_shopping_list_to_response(updated)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating item: {str(e)}")

@router.delete("/shopping-lists/{list_id}/items/{item_id}")
def delete_shopping_list_item(
    list_id: str,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove an item from a shopping list (soft behavior: delete item record)."""
    try:
        nutrition_service = NutritionService()
        updated = nutrition_service.delete_shopping_list_item(db, current_user.id, list_id, item_id)
        return nutrition_service._convert_shopping_list_to_response(updated)
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting item: {str(e)}")

@router.get("/personalized-targets")
def get_personalized_targets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get personalized nutrition targets based on health data"""
    try:
        targets = nutrition_service.calculate_personalized_targets(db, current_user.id)
        return targets
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating personalized targets: {str(e)}"
        )

@router.post("/recipes/{recipe_id}/adjust-portions")
def adjust_recipe_portions(
    recipe_id: str,
    new_servings: float = Query(..., description="New number of servings"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Adjust recipe portions and recalculate nutrition"""
    try:
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found"
            )
        
        adjusted_recipe = nutrition_service.adjust_recipe_portions(recipe, new_servings)
        return adjusted_recipe
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adjusting recipe portions: {str(e)}"
        )

@router.get("/recipes/{recipe_id}/portion-suggestions")
def get_portion_suggestions(
    recipe_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get personalized portion suggestions for a recipe"""
    try:
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Recipe not found"
            )
        
        suggestions = nutrition_service.get_portion_suggestions(db, current_user.id, recipe)
        return suggestions
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting portion suggestions: {str(e)}"
        )

@router.post("/meal-plans/{meal_plan_id}/optimize-timing")
def optimize_meal_timing(
    meal_plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Optimize meal timing based on user's activity level"""
    try:
        meal_plan = db.query(MealPlan).filter(
            MealPlan.id == meal_plan_id,
            MealPlan.user_id == current_user.id
        ).first()
        
        if not meal_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal plan not found"
            )
        
        optimization = nutrition_service.optimize_meal_timing(db, current_user.id, meal_plan)
        return optimization
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error optimizing meal timing: {str(e)}"
        )

@router.post("/wellness-score/update")
def update_wellness_score(
    analysis_period: str = Query("week", description="Analysis period: day, week, month"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update wellness score based on nutritional intake"""
    try:
        result = nutrition_service.update_wellness_score_from_nutrition(
            db, current_user.id, analysis_period
        )
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating wellness score: {str(e)}"
        )

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
        # Get nutritional analysis with AI-powered insights
        analysis = nutrition_service.get_nutritional_analysis(
            db=db,
            user_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            analysis_type=analysis_type
        )
        
        # Add AI-powered insights if we have nutritional data
        if analysis.get('totals', {}).get('calories', 0) > 0:
            # Get user preferences for AI insights
            preferences = db.query(UserNutritionPreferences).filter(
                UserNutritionPreferences.user_id == current_user.id
            ).first()
            
            if preferences:
                prefs_dict = {
                    "dietary_preferences": preferences.dietary_preferences or [],
                    "allergies": preferences.allergies or [],
                    "daily_calorie_target": preferences.daily_calorie_target or 2000,
                    "protein_target": preferences.protein_target or 100,
                    "carbs_target": preferences.carbs_target or 200,
                    "fats_target": preferences.fats_target or 60
                }
                
                # Generate AI insights
                ai_insights = nutrition_ai.generate_nutritional_insights(
                    analysis['totals'], 
                    prefs_dict
                )
                analysis['ai_insights'] = ai_insights
        
        return analysis
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting nutritional analysis: {str(e)}"
        )

@router.post("/meal-plans/{meal_plan_id}/regenerate-meal/{meal_id}")
async def regenerate_individual_meal(
    meal_plan_id: str,
    meal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Regenerate a single meal while preserving other meals and preferences"""
    try:
        # Get user's nutrition preferences
        integration_service = IntegrationService()
        user_preferences = integration_service.get_integrated_nutrition_preferences(db, current_user.id)
        
        # Regenerate the meal
        regeneration_service = MealRegenerationService()
        result = regeneration_service.regenerate_individual_meal(
            db, meal_plan_id, meal_id, user_preferences
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error regenerating meal: {str(e)}")

@router.post("/meal-plans/{meal_plan_id}/regenerate-meal-type/{meal_type}")
async def regenerate_meal_type(
    meal_plan_id: str,
    meal_type: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Regenerate all meals of a specific type (e.g., all breakfasts)"""
    try:
        # Validate meal type
        valid_meal_types = ["breakfast", "lunch", "dinner", "snack"]
        if meal_type not in valid_meal_types:
            raise HTTPException(status_code=400, detail=f"Invalid meal type. Must be one of: {valid_meal_types}")
        
        # Get user's nutrition preferences
        integration_service = IntegrationService()
        user_preferences = integration_service.get_integrated_nutrition_preferences(db, current_user.id)
        
        # Regenerate meals of this type
        regeneration_service = MealRegenerationService()
        result = regeneration_service.regenerate_meal_type(
            db, meal_plan_id, meal_type, user_preferences
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error regenerating meal type: {str(e)}")

@router.post("/meal-plans/{meal_plan_id}/regenerate-entire")
async def regenerate_entire_meal_plan(
    meal_plan_id: str,
    preserve_structure: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Regenerate entire meal plan while preserving preferences"""
    try:
        # Get user's nutrition preferences
        integration_service = IntegrationService()
        user_preferences = integration_service.get_integrated_nutrition_preferences(db, current_user.id)
        
        # Regenerate the entire meal plan
        regeneration_service = MealRegenerationService()
        result = regeneration_service.regenerate_entire_meal_plan(
            db, meal_plan_id, user_preferences, preserve_structure
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error regenerating meal plan: {str(e)}")

@router.post("/meal-plans/{meal_plan_id}/generate-shopping-list")
async def generate_shopping_list_from_meal_plan(
    meal_plan_id: str,
    list_name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a shopping list from all meals in a meal plan"""
    try:
        shopping_list_service = ShoppingListService()
        shopping_list = shopping_list_service.generate_shopping_list_from_meal_plan(
            db, current_user.id, meal_plan_id, list_name
        )
        
        # Convert to response format
        from services.nutrition_service import NutritionService
        nutrition_service = NutritionService()
        return nutrition_service._convert_shopping_list_to_response(shopping_list)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating shopping list: {str(e)}")

@router.post("/meals/{meal_id}/generate-shopping-list")
async def generate_shopping_list_from_meal(
    meal_id: str,
    list_name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a shopping list from a single meal"""
    try:
        shopping_list_service = ShoppingListService()
        shopping_list = shopping_list_service.generate_shopping_list_from_meal(
            db, current_user.id, meal_id, list_name
        )
        
        # Convert to response format
        from services.nutrition_service import NutritionService
        nutrition_service = NutritionService()
        return nutrition_service._convert_shopping_list_to_response(shopping_list)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating shopping list: {str(e)}")

@router.post("/meal-plans/{meal_plan_id}/generate-shopping-list-by-types")
async def generate_shopping_list_from_meal_types(
    meal_plan_id: str,
    meal_types: List[str],
    list_name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a shopping list from specific meal types in a meal plan"""
    try:
        # Validate meal types
        valid_meal_types = ["breakfast", "lunch", "dinner", "snack"]
        invalid_types = [mt for mt in meal_types if mt not in valid_meal_types]
        if invalid_types:
            raise HTTPException(status_code=400, detail=f"Invalid meal types: {invalid_types}. Must be one of: {valid_meal_types}")
        
        shopping_list_service = ShoppingListService()
        shopping_list = shopping_list_service.generate_shopping_list_from_meal_types(
            db, current_user.id, meal_plan_id, meal_types, list_name
        )
        
        # Convert to response format
        from services.nutrition_service import NutritionService
        nutrition_service = NutritionService()
        return nutrition_service._convert_shopping_list_to_response(shopping_list)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating shopping list: {str(e)}")

@router.get("/shopping-lists/{shopping_list_id}/summary")
async def get_shopping_list_summary(
    shopping_list_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a detailed summary of a shopping list with categorized items"""
    try:
        # Verify shopping list belongs to user
        shopping_list = db.query(ShoppingList).filter(
            ShoppingList.id == shopping_list_id,
            ShoppingList.user_id == current_user.id
        ).first()
        
        if not shopping_list:
            raise HTTPException(status_code=404, detail="Shopping list not found")
        
        shopping_list_service = ShoppingListService()
        return shopping_list_service.get_shopping_list_summary(db, shopping_list_id)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting shopping list summary: {str(e)}")

@router.put("/shopping-lists/items/{item_id}/quantity")
async def update_shopping_list_item_quantity(
    item_id: int,
    new_quantity: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the quantity of a shopping list item"""
    try:
        if new_quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
        
        shopping_list_service = ShoppingListService()
        result = shopping_list_service.update_shopping_list_item_quantity(
            db, current_user.id, item_id, new_quantity
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating item quantity: {str(e)}")

@router.delete("/shopping-lists/items/{item_id}")
async def remove_shopping_list_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove an item from a shopping list"""
    try:
        shopping_list_service = ShoppingListService()
        result = shopping_list_service.remove_shopping_list_item(
            db, current_user.id, item_id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing item: {str(e)}")

@router.put("/shopping-lists/items/{item_id}/purchased")
async def toggle_item_purchased_status(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle the purchased status of a shopping list item"""
    try:
        shopping_list_service = ShoppingListService()
        result = shopping_list_service.toggle_item_purchased_status(
            db, current_user.id, item_id
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating purchased status: {str(e)}")

@router.post("/shopping-lists/{shopping_list_id}/custom-item")
async def add_custom_item_to_shopping_list(
    shopping_list_id: str,
    item_name: str,
    quantity: float,
    unit: str,
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a custom item to an existing shopping list"""
    try:
        if quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
        
        shopping_list_service = ShoppingListService()
        result = shopping_list_service.add_custom_item_to_shopping_list(
            db, current_user.id, shopping_list_id, item_name, quantity, unit, category
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding custom item: {str(e)}")

@router.put("/shopping-lists/items/{item_id}/notes")
async def update_item_notes(
    item_id: int,
    notes: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update the notes for a shopping list item"""
    try:
        shopping_list_service = ShoppingListService()
        result = shopping_list_service.update_item_notes(
            db, current_user.id, item_id, notes
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating item notes: {str(e)}")

@router.put("/meals/{meal_id}/adjust-portions")
async def adjust_meal_portion(
    meal_id: str,
    new_servings: float,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Adjust the portion size of a meal and recalculate ingredient quantities"""
    try:
        if new_servings <= 0:
            raise HTTPException(status_code=400, detail="Servings must be greater than 0")
        
        # Verify meal belongs to user
        meal = db.query(MealPlanMeal).join(MealPlan).filter(
            MealPlanMeal.id == meal_id,
            MealPlan.user_id == current_user.id
        ).first()
        
        if not meal:
            raise HTTPException(status_code=404, detail="Meal not found or doesn't belong to user")
        
        portion_service = PortionAdjustmentService()
        result = portion_service.adjust_meal_portion(db, meal_id, new_servings)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adjusting meal portion: {str(e)}")

@router.get("/meals/{meal_id}/portion-suggestions")
async def get_meal_portion_suggestions(
    meal_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized portion suggestions for a meal"""
    try:
        # Verify meal belongs to user
        meal = db.query(MealPlanMeal).join(MealPlan).filter(
            MealPlanMeal.id == meal_id,
            MealPlan.user_id == current_user.id
        ).first()
        
        if not meal:
            raise HTTPException(status_code=404, detail="Meal not found or doesn't belong to user")
        
        portion_service = PortionAdjustmentService()
        result = portion_service.get_portion_suggestions_for_meal(db, current_user.id, meal_id)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting portion suggestions: {str(e)}")

@router.put("/meal-plans/{meal_plan_id}/batch-adjust-portions")
async def batch_adjust_meal_plan_portions(
    meal_plan_id: str,
    portion_adjustments: Dict[str, float],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Adjust portions for multiple meals in a meal plan"""
    try:
        # Verify meal plan belongs to user
        meal_plan = db.query(MealPlan).filter(
            MealPlan.id == meal_plan_id,
            MealPlan.user_id == current_user.id
        ).first()
        
        if not meal_plan:
            raise HTTPException(status_code=404, detail="Meal plan not found or doesn't belong to user")
        
        # Validate all servings are positive
        for meal_id, servings in portion_adjustments.items():
            if servings <= 0:
                raise HTTPException(status_code=400, detail=f"Servings for meal {meal_id} must be greater than 0")
        
        portion_service = PortionAdjustmentService()
        result = portion_service.batch_adjust_meal_plan_portions(db, meal_plan_id, portion_adjustments)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error batch adjusting portions: {str(e)}")

@router.post("/standardize-measurements")
async def standardize_measurements(
    measurement_data: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Standardize measurements to common units"""
    try:
        measurement_service = MeasurementStandardizationService()
        
        if 'ingredient_name' in measurement_data and 'quantity' in measurement_data and 'unit' in measurement_data:
            # Standardize single ingredient measurement
            result = measurement_service.standardize_ingredient_measurement(
                measurement_data['ingredient_name'],
                float(measurement_data['quantity']),
                measurement_data['unit']
            )
        elif 'recipe_data' in measurement_data:
            # Standardize entire recipe
            result = measurement_service.standardize_recipe_measurements(measurement_data['recipe_data'])
        else:
            raise HTTPException(status_code=400, detail="Invalid measurement data format")
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error standardizing measurements: {str(e)}")

@router.get("/standard-units")
async def get_standard_units():
    """Get the standard units used in the system"""
    try:
        measurement_service = MeasurementStandardizationService()
        return {
            "standard_units": measurement_service.get_standard_units(),
            "conversion_factors": measurement_service.get_conversion_factors()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting standard units: {str(e)}")

@router.post("/validate-measurement")
async def validate_measurement(
    quantity: float,
    unit: str,
    measurement_type: str,
    current_user: User = Depends(get_current_user)
):
    """Validate that a measurement is in the correct format"""
    try:
        measurement_service = MeasurementStandardizationService()
        is_valid = measurement_service.validate_measurement(quantity, unit, measurement_type)
        
        return {
            "is_valid": is_valid,
            "quantity": quantity,
            "unit": unit,
            "measurement_type": measurement_type
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error validating measurement: {str(e)}")

@router.get("/comprehensive-ai-analysis")
async def get_comprehensive_ai_analysis(
    start_date: date = Query(...),
    end_date: date = Query(...),
    analysis_type: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive AI-driven nutritional analysis with achievements, concerns, and balance analysis"""
    try:
        nutrition_service = NutritionService()
        result = nutrition_service.get_comprehensive_ai_analysis(
            db, current_user.id, start_date, end_date, analysis_type
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting comprehensive AI analysis: {str(e)}")

@router.get("/ai-improvement-suggestions")
async def get_ai_improvement_suggestions(
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive AI-driven improvement suggestions including food recommendations, timing, portions, and alternatives"""
    try:
        nutrition_service = NutritionService()
        result = nutrition_service.get_ai_improvement_suggestions(
            db, current_user.id, start_date, end_date
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting AI improvement suggestions: {str(e)}")

@router.get("/advanced-analytics")
async def get_advanced_analytics(
    start_date: date = Query(...),
    end_date: date = Query(...),
    analysis_type: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get advanced nutritional analytics with comprehensive insights"""
    try:
        analytics_service = NutritionAnalyticsService()
        
        # Convert dates to datetime objects
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        result = analytics_service.get_comprehensive_analysis(
            current_user.id, start_datetime, end_datetime, db
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting advanced analytics: {str(e)}")

@router.get("/weekly-analytics")
async def get_weekly_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get weekly nutritional analytics"""
    try:
        analytics_service = NutritionAnalyticsService()
        result = analytics_service.get_weekly_analysis(current_user.id, db)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting weekly analytics: {str(e)}")

@router.get("/monthly-analytics")
async def get_monthly_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly nutritional analytics"""
    try:
        analytics_service = NutritionAnalyticsService()
        result = analytics_service.get_monthly_analysis(current_user.id, db)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting monthly analytics: {str(e)}")

@router.get("/recommendations")
async def get_recipe_recommendations(
    recommendation_type: str = Query("mixed", regex="^(nutritional|similar|trending|diverse|mixed)$"),
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized recipe recommendations"""
    try:
        recommendation_service = RecipeRecommendationService()
        recommendations = recommendation_service.get_personalized_recommendations(
            current_user.id, db, limit, recommendation_type
        )
        
        return {
            "recommendations": recommendations,
            "total": len(recommendations),
            "recommendation_type": recommendation_type,
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting recommendations: {str(e)}")

@router.get("/recommendations/contextual")
async def get_contextual_recommendations(
    context: str = Query(..., description="Context for recommendations (e.g., 'breakfast', 'high protein', 'quick meal')"),
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get contextual recipe recommendations based on specific context"""
    try:
        recommendation_service = RecipeRecommendationService()
        recommendations = recommendation_service.get_contextual_recommendations(
            context, current_user.id, db, limit
        )
        
        return {
            "recommendations": recommendations,
            "total": len(recommendations),
            "context": context,
            "user_id": current_user.id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting contextual recommendations: {str(e)}")

@router.get("/recommendations/meal/{meal_type}")
async def get_meal_specific_recommendations(
    meal_type: str,
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recommendations for specific meal types"""
    try:
        # Validate meal_type
        valid_meal_types = ["breakfast", "lunch", "dinner", "snacks"]
        if meal_type not in valid_meal_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid meal_type. Must be one of: {', '.join(valid_meal_types)}"
            )
        
        recommendation_service = RecipeRecommendationService()
        recommendations = recommendation_service.get_meal_specific_recommendations(
            meal_type, current_user.id, db, limit
        )
        
        return {
            "recommendations": recommendations,
            "total": len(recommendations),
            "meal_type": meal_type,
            "user_id": current_user.id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting meal-specific recommendations: {str(e)}")

@router.get("/shopping-lists/{shopping_list_id}/export")
async def export_shopping_list(
    shopping_list_id: str,
    format: str = Query("json", regex="^(json|csv|txt)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export shopping list in various formats"""
    try:
        # Verify shopping list belongs to user
        shopping_list = db.query(ShoppingList).filter(
            ShoppingList.id == shopping_list_id,
            ShoppingList.user_id == current_user.id
        ).first()
        
        if not shopping_list:
            raise HTTPException(status_code=404, detail="Shopping list not found")
        
        shopping_list_service = ShoppingListService()
        summary = shopping_list_service.get_shopping_list_summary(db, shopping_list_id)
        
        if format == "json":
            return summary
        elif format == "csv":
            # Convert to CSV format
            csv_data = "Category,Item,Quantity,Unit,Purchased,Notes\n"
            for category, items in summary['categories'].items():
                for item in items:
                    csv_data += f"{category},{item['ingredient_id']},{item['quantity']},{item['unit']},{item['is_purchased']},{item.get('notes', '')}\n"
            
            return {
                "content": csv_data,
                "filename": f"{summary['list_name']}.csv",
                "content_type": "text/csv"
            }
        elif format == "txt":
            # Convert to plain text format
            txt_data = f"Shopping List: {summary['list_name']}\n"
            txt_data += f"Generated: {summary['created_at']}\n"
            txt_data += f"Progress: {summary['purchased_items']}/{summary['total_items']} items ({summary['completion_percentage']:.1f}%)\n\n"
            
            for category, items in summary['categories'].items():
                txt_data += f"{category.upper()}:\n"
                for item in items:
                    status = "✓" if item['is_purchased'] else "○"
                    txt_data += f"  {status} {item['quantity']} {item['unit']} {item['ingredient_id']}"
                    if item.get('notes'):
                        txt_data += f" ({item['notes']})"
                    txt_data += "\n"
                txt_data += "\n"
            
            return {
                "content": txt_data,
                "filename": f"{summary['list_name']}.txt",
                "content_type": "text/plain"
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting shopping list: {str(e)}")

@router.post("/shopping-lists/{shopping_list_id}/duplicate")
async def duplicate_shopping_list(
    shopping_list_id: str,
    new_name: str = Query(..., description="Name for the duplicated shopping list"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Duplicate an existing shopping list"""
    try:
        # Verify original shopping list belongs to user
        original_list = db.query(ShoppingList).filter(
            ShoppingList.id == shopping_list_id,
            ShoppingList.user_id == current_user.id
        ).first()
        
        if not original_list:
            raise HTTPException(status_code=404, detail="Shopping list not found")
        
        # Create new shopping list
        new_list = ShoppingList(
            id=f"sl_{current_user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            user_id=current_user.id,
            meal_plan_id=original_list.meal_plan_id,
            list_name=new_name,
            is_active=True
        )
        
        db.add(new_list)
        db.flush()
        
        # Copy all items
        for item in original_list.items:
            new_item = ShoppingListItem(
                shopping_list_id=new_list.id,
                ingredient_id=item.ingredient_id,
                quantity=item.quantity,
                unit=item.unit,
                category=item.category,
                notes=item.notes,
                is_purchased=False  # Reset purchased status
            )
            db.add(new_item)
        
        db.commit()
        db.refresh(new_list)
        
        return nutrition_service._convert_shopping_list_to_response(new_list)
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error duplicating shopping list: {str(e)}")

@router.delete("/shopping-lists/{shopping_list_id}")
async def delete_shopping_list(
    shopping_list_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a shopping list (soft delete by setting is_active to False)"""
    try:
        shopping_list = db.query(ShoppingList).filter(
            ShoppingList.id == shopping_list_id,
            ShoppingList.user_id == current_user.id
        ).first()
        
        if not shopping_list:
            raise HTTPException(status_code=404, detail="Shopping list not found")
        
        shopping_list.is_active = False
        db.commit()
        
        return {"message": "Shopping list deleted successfully"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting shopping list: {str(e)}")
