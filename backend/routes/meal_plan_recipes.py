from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.user import User
from auth.supabase_auth import get_current_user_supabase as get_current_user
from services.meal_plan_recipe_service import MealPlanRecipeService
from schemas.nutrition import MealPlanMealResponse
from pydantic import BaseModel
from datetime import date, datetime

router = APIRouter(prefix="/meal-plan-recipes", tags=["Meal Plan Recipes"])

class AddRecipeToMealPlanRequest(BaseModel):
    recipe_id: str
    meal_date: date
    meal_type: str
    servings: float = 1.0
    meal_time: Optional[datetime] = None
    custom_meal_name: Optional[str] = None

class UpdateRecipeServingsRequest(BaseModel):
    recipe_id: str
    new_servings: float

class ServingAdjustmentSuggestion(BaseModel):
    recipe_id: str
    recipe_title: str
    current_servings: float
    adjustments: dict

@router.post("/{meal_plan_id}/add-recipe", response_model=MealPlanMealResponse, status_code=status.HTTP_201_CREATED)
def add_recipe_to_meal_plan(
    meal_plan_id: str,
    request: AddRecipeToMealPlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a recipe to a meal plan with serving size adjustments"""
    service = MealPlanRecipeService()
    try:
        meal = service.add_recipe_to_meal_plan(
            db=db,
            meal_plan_id=meal_plan_id,
            recipe_id=request.recipe_id,
            meal_date=request.meal_date,
            meal_type=request.meal_type,
            servings=request.servings,
            meal_time=request.meal_time,
            custom_meal_name=request.custom_meal_name
        )
        return meal
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/{meal_plan_id}/meals/{meal_id}/update-servings", response_model=MealPlanMealResponse)
def update_recipe_servings(
    meal_plan_id: str,
    meal_id: int,
    request: UpdateRecipeServingsRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update the serving size of a recipe in a meal plan"""
    service = MealPlanRecipeService()
    try:
        meal = service.update_recipe_servings(
            db=db,
            meal_plan_id=meal_plan_id,
            meal_id=meal_id,
            recipe_id=request.recipe_id,
            new_servings=request.new_servings
        )
        return meal
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/{meal_plan_id}/meals/{meal_id}/remove-recipe")
def remove_recipe_from_meal_plan(
    meal_plan_id: str,
    meal_id: int,
    recipe_id: str = Query(..., description="ID of the recipe to remove"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove a recipe from a meal plan"""
    service = MealPlanRecipeService()
    try:
        success = service.remove_recipe_from_meal_plan(
            db=db,
            meal_plan_id=meal_plan_id,
            meal_id=meal_id,
            recipe_id=recipe_id
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found in meal plan")
        return {"message": "Recipe removed successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{meal_plan_id}/recipes", response_model=List[dict])
def get_meal_plan_recipes(
    meal_plan_id: str,
    meal_date: Optional[date] = Query(None, description="Filter by specific meal date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all recipes in a meal plan with their details"""
    service = MealPlanRecipeService()
    try:
        recipes = service.get_meal_plan_recipes(
            db=db,
            meal_plan_id=meal_plan_id,
            meal_date=meal_date
        )
        return recipes
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{meal_plan_id}/serving-suggestions", response_model=List[ServingAdjustmentSuggestion])
def get_serving_suggestions(
    meal_plan_id: str,
    target_calories: Optional[float] = Query(None, description="Target calories for the meal plan"),
    target_protein: Optional[float] = Query(None, description="Target protein for the meal plan"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get serving size adjustment suggestions to meet nutritional targets"""
    service = MealPlanRecipeService()
    try:
        suggestions = service.suggest_serving_adjustments(
            db=db,
            meal_plan_id=meal_plan_id,
            target_calories=target_calories,
            target_protein=target_protein
        )
        return suggestions
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/{meal_plan_id}/bulk-add-recipes", response_model=List[MealPlanMealResponse], status_code=status.HTTP_201_CREATED)
def bulk_add_recipes_to_meal_plan(
    meal_plan_id: str,
    requests: List[AddRecipeToMealPlanRequest],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add multiple recipes to a meal plan at once"""
    service = MealPlanRecipeService()
    results = []
    errors = []
    
    for request in requests:
        try:
            meal = service.add_recipe_to_meal_plan(
                db=db,
                meal_plan_id=meal_plan_id,
                recipe_id=request.recipe_id,
                meal_date=request.meal_date,
                meal_type=request.meal_type,
                servings=request.servings,
                meal_time=request.meal_time,
                custom_meal_name=request.custom_meal_name
            )
            results.append(meal)
        except Exception as e:
            errors.append({
                "recipe_id": request.recipe_id,
                "error": str(e)
            })
    
    if errors:
        # Return partial success with errors
        return {
            "meals": results,
            "errors": errors,
            "message": f"Successfully added {len(results)} recipes, {len(errors)} failed"
        }
    
    return results

@router.get("/{meal_plan_id}/nutrition-summary")
def get_meal_plan_nutrition_summary(
    meal_plan_id: str,
    meal_date: Optional[date] = Query(None, description="Get summary for specific date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get nutritional summary for a meal plan"""
    service = MealPlanRecipeService()
    try:
        recipes = service.get_meal_plan_recipes(
            db=db,
            meal_plan_id=meal_plan_id,
            meal_date=meal_date
        )
        
        # Calculate totals
        total_calories = sum(recipe["recipe"]["calories"] or 0 for recipe in recipes)
        total_protein = sum(recipe["recipe"]["protein"] or 0 for recipe in recipes)
        total_carbs = sum(recipe["recipe"]["carbs"] or 0 for recipe in recipes)
        total_fat = sum(recipe["recipe"]["fat"] or 0 for recipe in recipes)
        total_sodium = sum(recipe["recipe"]["sodium"] or 0 for recipe in recipes)
        
        # Group by meal type
        meal_type_totals = {}
        for recipe in recipes:
            # Get meal type from the meal (would need to join with MealPlanMeal)
            # For now, we'll use the recipe's meal_type
            meal_type = recipe["recipe"]["meal_type"]
            if meal_type not in meal_type_totals:
                meal_type_totals[meal_type] = {
                    "calories": 0,
                    "protein": 0,
                    "carbs": 0,
                    "fat": 0,
                    "sodium": 0,
                    "recipe_count": 0
                }
            
            meal_type_totals[meal_type]["calories"] += recipe["recipe"]["calories"] or 0
            meal_type_totals[meal_type]["protein"] += recipe["recipe"]["protein"] or 0
            meal_type_totals[meal_type]["carbs"] += recipe["recipe"]["carbs"] or 0
            meal_type_totals[meal_type]["fat"] += recipe["recipe"]["fat"] or 0
            meal_type_totals[meal_type]["sodium"] += recipe["recipe"]["sodium"] or 0
            meal_type_totals[meal_type]["recipe_count"] += 1
        
        return {
            "total_nutrition": {
                "calories": total_calories,
                "protein": total_protein,
                "carbs": total_carbs,
                "fat": total_fat,
                "sodium": total_sodium
            },
            "meal_type_breakdown": meal_type_totals,
            "recipe_count": len(recipes),
            "date": meal_date
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/{meal_plan_id}/shopping-list")
def generate_shopping_list(
    meal_plan_id: str,
    meal_date: Optional[date] = Query(None, description="Generate list for specific date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a shopping list from meal plan recipes"""
    service = MealPlanRecipeService()
    try:
        recipes = service.get_meal_plan_recipes(
            db=db,
            meal_plan_id=meal_plan_id,
            meal_date=meal_date
        )
        
        # Aggregate ingredients
        ingredient_totals = {}
        for recipe in recipes:
            servings = recipe["servings"]
            recipe_details = recipe["recipe"]
            
            # This would need to be expanded to include actual ingredients
            # For now, return a placeholder structure
            if "ingredients" in recipe_details:
                for ingredient in recipe_details["ingredients"]:
                    key = f"{ingredient['name']}_{ingredient['unit']}"
                    if key not in ingredient_totals:
                        ingredient_totals[key] = {
                            "name": ingredient["name"],
                            "unit": ingredient["unit"],
                            "total_quantity": 0,
                            "recipes": []
                        }
                    
                    ingredient_totals[key]["total_quantity"] += ingredient["quantity"]
                    ingredient_totals[key]["recipes"].append({
                        "recipe_title": recipe_details["title"],
                        "quantity": ingredient["quantity"],
                        "servings": servings
                    })
        
        return {
            "ingredients": list(ingredient_totals.values()),
            "recipe_count": len(recipes),
            "date": meal_date
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
