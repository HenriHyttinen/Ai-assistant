"""
Meal Plan Versioning API

Provides endpoints for managing meal plan versions:
- View version history
- Restore previous versions
- Compare versions
- Manage version lifecycle
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from database import get_db
from auth.supabase_auth import get_current_user_supabase as get_current_user
from models.user import User
from services.meal_plan_versioning_service import meal_plan_versioning_service
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/meal-plans", tags=["Meal Plan Versioning"])

@router.get("/{meal_plan_id}/versions")
def get_meal_plan_versions(
    meal_plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get all versions of a meal plan"""
    try:
        versions = meal_plan_versioning_service.get_meal_plan_versions(
            db, current_user.id, meal_plan_id
        )
        
        return versions
        
    except Exception as e:
        logger.error(f"Error getting meal plan versions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting meal plan versions: {str(e)}"
        )

@router.post("/{meal_plan_id}/versions/{version_id}/restore")
def restore_meal_plan_version(
    meal_plan_id: str,
    version_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Restore a specific version of a meal plan"""
    try:
        new_plan_id = meal_plan_versioning_service.restore_meal_plan_version(
            db, current_user.id, version_id
        )
        
        if not new_plan_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Version not found or could not be restored"
            )
        
        return {
            "message": "Meal plan version restored successfully",
            "new_meal_plan_id": new_plan_id,
            "restored_from_version": version_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error restoring meal plan version: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error restoring meal plan version: {str(e)}"
        )

@router.get("/{meal_plan_id}/versions/compare")
def compare_meal_plan_versions(
    meal_plan_id: str,
    version1_id: str = Query(..., description="First version ID to compare"),
    version2_id: str = Query(..., description="Second version ID to compare"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Compare two versions of a meal plan"""
    try:
        comparison = meal_plan_versioning_service.compare_meal_plan_versions(
            db, current_user.id, version1_id, version2_id
        )
        
        if "error" in comparison:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=comparison["error"]
            )
        
        return comparison
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing meal plan versions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error comparing meal plan versions: {str(e)}"
        )

@router.get("/{meal_plan_id}/versions/{version_id}")
def get_meal_plan_version_details(
    meal_plan_id: str,
    version_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get detailed information about a specific meal plan version"""
    try:
        from models.nutrition import MealPlan, MealPlanMeal
        from sqlalchemy import and_
        
        # Get the version
        version_plan = db.query(MealPlan).filter(
            and_(MealPlan.id == version_id, MealPlan.user_id == current_user.id)
        ).first()
        
        if not version_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Version not found"
            )
        
        # Get meals for this version
        meals = db.query(MealPlanMeal).filter(
            MealPlanMeal.meal_plan_id == version_id
        ).all()
        
        # Calculate totals
        total_calories = sum(meal.calories for meal in meals)
        total_protein = sum(meal.protein for meal in meals)
        total_carbs = sum(meal.carbs for meal in meals)
        total_fats = sum(meal.fats for meal in meals)
        
        # Extract versioning metadata
        versioning_info = {}
        if version_plan.generation_parameters and "versioning" in version_plan.generation_parameters:
            versioning_info = version_plan.generation_parameters["versioning"]
        
        return {
            "id": version_plan.id,
            "version": version_plan.version,
            "is_active": version_plan.is_active,
            "created_at": version_plan.created_at.isoformat() if version_plan.created_at else None,
            "updated_at": version_plan.updated_at.isoformat() if version_plan.updated_at else None,
            "plan_type": version_plan.plan_type,
            "start_date": version_plan.start_date.isoformat() if version_plan.start_date else None,
            "end_date": version_plan.end_date.isoformat() if version_plan.end_date else None,
            "meals": [
                {
                    "id": meal.id,
                    "meal_type": meal.meal_type,
                    "meal_name": meal.meal_name,
                    "meal_date": meal.meal_date.isoformat() if meal.meal_date else None,
                    "calories": meal.calories,
                    "protein": meal.protein,
                    "carbs": meal.carbs,
                    "fats": meal.fats,
                    "cuisine": meal.cuisine,
                    "recipe_details": meal.recipe_details
                }
                for meal in meals
            ],
            "totals": {
                "calories": total_calories,
                "protein": total_protein,
                "carbs": total_carbs,
                "fats": total_fats
            },
            "versioning": versioning_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting meal plan version details: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting meal plan version details: {str(e)}"
        )

@router.delete("/{meal_plan_id}/versions/{version_id}")
def delete_meal_plan_version(
    meal_plan_id: str,
    version_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Delete a specific meal plan version (cannot delete active version)"""
    try:
        from models.nutrition import MealPlan, MealPlanMeal
        from sqlalchemy import and_
        
        # Get the version
        version_plan = db.query(MealPlan).filter(
            and_(MealPlan.id == version_id, MealPlan.user_id == current_user.id)
        ).first()
        
        if not version_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Version not found"
            )
        
        # Cannot delete active version
        if version_plan.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete active meal plan version"
            )
        
        # Delete associated meals first
        db.query(MealPlanMeal).filter(
            MealPlanMeal.meal_plan_id == version_id
        ).delete()
        
        # Delete the meal plan
        db.delete(version_plan)
        db.commit()
        
        return {
            "message": "Meal plan version deleted successfully",
            "deleted_version_id": version_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting meal plan version: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting meal plan version: {str(e)}"
        )

@router.get("/{meal_plan_id}/active")
def get_active_meal_plan(
    meal_plan_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get the currently active version of a meal plan"""
    try:
        from models.nutrition import MealPlan, MealPlanMeal
        from sqlalchemy import and_
        
        # Get the base plan to find the active version
        base_plan = db.query(MealPlan).filter(
            and_(MealPlan.id == meal_plan_id, MealPlan.user_id == current_user.id)
        ).first()
        
        if not base_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal plan not found"
            )
        
        # Find the active version for this date and plan type
        active_plan = db.query(MealPlan).filter(
            and_(
                MealPlan.user_id == current_user.id,
                MealPlan.start_date == base_plan.start_date,
                MealPlan.plan_type == base_plan.plan_type,
                MealPlan.is_active == True
            )
        ).first()
        
        if not active_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active version found"
            )
        
        # Get meals for the active version
        meals = db.query(MealPlanMeal).filter(
            MealPlanMeal.meal_plan_id == active_plan.id
        ).all()
        
        # Calculate totals
        total_calories = sum(meal.calories for meal in meals)
        total_protein = sum(meal.protein for meal in meals)
        total_carbs = sum(meal.carbs for meal in meals)
        total_fats = sum(meal.fats for meal in meals)
        
        return {
            "id": active_plan.id,
            "version": active_plan.version,
            "is_active": active_plan.is_active,
            "created_at": active_plan.created_at.isoformat() if active_plan.created_at else None,
            "updated_at": active_plan.updated_at.isoformat() if active_plan.updated_at else None,
            "plan_type": active_plan.plan_type,
            "start_date": active_plan.start_date.isoformat() if active_plan.start_date else None,
            "end_date": active_plan.end_date.isoformat() if active_plan.end_date else None,
            "meals": [
                {
                    "id": meal.id,
                    "meal_type": meal.meal_type,
                    "meal_name": meal.meal_name,
                    "meal_date": meal.meal_date.isoformat() if meal.meal_date else None,
                    "calories": meal.calories,
                    "protein": meal.protein,
                    "carbs": meal.carbs,
                    "fats": meal.fats,
                    "cuisine": meal.cuisine,
                    "recipe_details": meal.recipe_details
                }
                for meal in meals
            ],
            "totals": {
                "calories": total_calories,
                "protein": total_protein,
                "carbs": total_carbs,
                "fats": total_fats
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting active meal plan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting active meal plan: {str(e)}"
        )
