"""
Meal Plan Versioning Service

Manages versioning of meal plans, allowing users to:
- Create new versions when meal plans are modified
- View version history
- Restore previous versions
- Compare versions
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, date
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from models.nutrition import MealPlan, MealPlanMeal
from models.user import User
import uuid

logger = logging.getLogger(__name__)

class MealPlanVersioningService:
    """Service for managing meal plan versions"""
    
    def __init__(self):
        self.max_versions_per_plan = 10  # Keep last 10 versions
        self.auto_version_actions = [
            "regenerate_meal",
            "regenerate_plan", 
            "reorder_meals",
            "add_custom_meal",
            "adjust_portions"
        ]
    
    def create_meal_plan_version(self, db: Session, user_id: int, meal_plan_id: str, 
                                action: str, description: str = None) -> Optional[str]:
        """
        Create a new version of a meal plan
        
        Args:
            db: Database session
            user_id: User ID
            meal_plan_id: Original meal plan ID
            action: Action that triggered versioning
            description: Optional description of changes
            
        Returns:
            New meal plan ID if versioning was successful, None otherwise
        """
        try:
            # Get the original meal plan
            original_plan = db.query(MealPlan).filter(
                and_(MealPlan.id == meal_plan_id, MealPlan.user_id == user_id)
            ).first()
            
            if not original_plan:
                logger.error(f"Meal plan {meal_plan_id} not found for user {user_id}")
                return None
            
            # Check if we should create a version for this action
            if action not in self.auto_version_actions:
                logger.info(f"Action '{action}' does not require versioning")
                return None
            
            # Create new meal plan with incremented version
            new_version = self._increment_version(original_plan.version)
            new_plan_id = f"mp_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Create new meal plan record
            new_meal_plan = MealPlan(
                id=new_plan_id,
                user_id=user_id,
                plan_type=original_plan.plan_type,
                start_date=original_plan.start_date,
                end_date=original_plan.end_date,
                version=new_version,
                is_active=True,
                generation_strategy=original_plan.generation_strategy,
                ai_model_used=original_plan.ai_model_used,
                generation_parameters=original_plan.generation_parameters
            )
            
            # Add versioning metadata
            version_metadata = {
                "parent_plan_id": meal_plan_id,
                "action": action,
                "description": description or f"Version created by {action}",
                "created_at": datetime.utcnow().isoformat(),
                "version_number": new_version
            }
            new_meal_plan.generation_parameters = {
                **(original_plan.generation_parameters or {}),
                "versioning": version_metadata
            }
            
            db.add(new_meal_plan)
            db.flush()
            
            # Copy all meals from original plan
            original_meals = db.query(MealPlanMeal).filter(
                MealPlanMeal.meal_plan_id == meal_plan_id
            ).all()
            
            for original_meal in original_meals:
                new_meal = MealPlanMeal(
                    meal_plan_id=new_plan_id,
                    meal_date=original_meal.meal_date,
                    meal_type=original_meal.meal_type,
                    meal_time=original_meal.meal_time,
                    meal_name=original_meal.meal_name,
                    calories=original_meal.calories,
                    protein=original_meal.protein,
                    carbs=original_meal.carbs,
                    fats=original_meal.fats,
                    recipe_details=original_meal.recipe_details,
                    cuisine=original_meal.cuisine
                )
                db.add(new_meal)
            
            # Deactivate the original plan
            original_plan.is_active = False
            
            # Clean up old versions if we exceed the limit
            self._cleanup_old_versions(db, user_id, meal_plan_id)
            
            db.commit()
            
            logger.info(f"Created new version {new_version} for meal plan {meal_plan_id}")
            return new_plan_id
            
        except Exception as e:
            logger.error(f"Error creating meal plan version: {str(e)}")
            db.rollback()
            return None
    
    def get_meal_plan_versions(self, db: Session, user_id: int, base_plan_id: str) -> List[Dict[str, Any]]:
        """
        Get all versions of a meal plan
        
        Args:
            db: Database session
            user_id: User ID
            base_plan_id: Base meal plan ID
            
        Returns:
            List of version information
        """
        try:
            # Find all versions related to this plan
            versions = []
            
            # Get the original plan and all its versions
            original_plan = db.query(MealPlan).filter(
                and_(MealPlan.id == base_plan_id, MealPlan.user_id == user_id)
            ).first()
            
            if not original_plan:
                return versions
            
            # Get all plans with the same start_date and user_id (versions)
            all_plans = db.query(MealPlan).filter(
                and_(
                    MealPlan.user_id == user_id,
                    MealPlan.start_date == original_plan.start_date,
                    MealPlan.plan_type == original_plan.plan_type
                )
            ).order_by(desc(MealPlan.created_at)).all()
            
            for plan in all_plans:
                version_info = {
                    "id": plan.id,
                    "version": plan.version,
                    "is_active": plan.is_active,
                    "created_at": plan.created_at.isoformat() if plan.created_at else None,
                    "updated_at": plan.updated_at.isoformat() if plan.updated_at else None,
                    "action": None,
                    "description": None,
                    "meal_count": len(plan.meals),
                    "total_calories": sum(meal.calories for meal in plan.meals)
                }
                
                # Extract versioning metadata
                if plan.generation_parameters and "versioning" in plan.generation_parameters:
                    versioning = plan.generation_parameters["versioning"]
                    version_info["action"] = versioning.get("action")
                    version_info["description"] = versioning.get("description")
                
                versions.append(version_info)
            
            return versions
            
        except Exception as e:
            logger.error(f"Error getting meal plan versions: {str(e)}")
            return []
    
    def restore_meal_plan_version(self, db: Session, user_id: int, version_id: str) -> Optional[str]:
        """
        Restore a specific version of a meal plan
        
        Args:
            db: Database session
            user_id: User ID
            version_id: Version ID to restore
            
        Returns:
            New active meal plan ID if successful, None otherwise
        """
        try:
            # Get the version to restore
            version_plan = db.query(MealPlan).filter(
                and_(MealPlan.id == version_id, MealPlan.user_id == user_id)
            ).first()
            
            if not version_plan:
                logger.error(f"Version {version_id} not found for user {user_id}")
                return None
            
            # Create a new active version based on the restored version
            new_version = self._increment_version(version_plan.version)
            new_plan_id = f"mp_{user_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
            
            # Create new meal plan record
            new_meal_plan = MealPlan(
                id=new_plan_id,
                user_id=user_id,
                plan_type=version_plan.plan_type,
                start_date=version_plan.start_date,
                end_date=version_plan.end_date,
                version=new_version,
                is_active=True,
                generation_strategy=version_plan.generation_strategy,
                ai_model_used=version_plan.ai_model_used,
                generation_parameters=version_plan.generation_parameters
            )
            
            # Add restoration metadata
            restoration_metadata = {
                "restored_from": version_id,
                "action": "restore_version",
                "description": f"Restored from version {version_plan.version}",
                "created_at": datetime.utcnow().isoformat(),
                "version_number": new_version
            }
            new_meal_plan.generation_parameters = {
                **(version_plan.generation_parameters or {}),
                "versioning": restoration_metadata
            }
            
            db.add(new_meal_plan)
            db.flush()
            
            # Copy all meals from the restored version
            version_meals = db.query(MealPlanMeal).filter(
                MealPlanMeal.meal_plan_id == version_id
            ).all()
            
            for version_meal in version_meals:
                new_meal = MealPlanMeal(
                    meal_plan_id=new_plan_id,
                    meal_date=version_meal.meal_date,
                    meal_type=version_meal.meal_type,
                    meal_time=version_meal.meal_time,
                    meal_name=version_meal.meal_name,
                    calories=version_meal.calories,
                    protein=version_meal.protein,
                    carbs=version_meal.carbs,
                    fats=version_meal.fats,
                    recipe_details=version_meal.recipe_details,
                    cuisine=version_meal.cuisine
                )
                db.add(new_meal)
            
            # Deactivate all other versions for this date
            self._deactivate_other_versions(db, user_id, version_plan.start_date, version_plan.plan_type)
            
            db.commit()
            
            logger.info(f"Restored version {version_plan.version} as new active plan {new_plan_id}")
            return new_plan_id
            
        except Exception as e:
            logger.error(f"Error restoring meal plan version: {str(e)}")
            db.rollback()
            return None
    
    def compare_meal_plan_versions(self, db: Session, user_id: int, 
                                 version1_id: str, version2_id: str) -> Dict[str, Any]:
        """
        Compare two versions of a meal plan
        
        Args:
            db: Database session
            user_id: User ID
            version1_id: First version ID
            version2_id: Second version ID
            
        Returns:
            Comparison data
        """
        try:
            # Get both versions
            version1 = db.query(MealPlan).filter(
                and_(MealPlan.id == version1_id, MealPlan.user_id == user_id)
            ).first()
            
            version2 = db.query(MealPlan).filter(
                and_(MealPlan.id == version2_id, MealPlan.user_id == user_id)
            ).first()
            
            if not version1 or not version2:
                return {"error": "One or both versions not found"}
            
            # Get meals for both versions
            meals1 = db.query(MealPlanMeal).filter(MealPlanMeal.meal_plan_id == version1_id).all()
            meals2 = db.query(MealPlanMeal).filter(MealPlanMeal.meal_plan_id == version2_id).all()
            
            # Calculate nutritional differences
            total_calories1 = sum(meal.calories for meal in meals1)
            total_calories2 = sum(meal.calories for meal in meals2)
            total_protein1 = sum(meal.protein for meal in meals1)
            total_protein2 = sum(meal.protein for meal in meals2)
            
            comparison = {
                "version1": {
                    "id": version1.id,
                    "version": version1.version,
                    "created_at": version1.created_at.isoformat() if version1.created_at else None,
                    "meal_count": len(meals1),
                    "total_calories": total_calories1,
                    "total_protein": total_protein1
                },
                "version2": {
                    "id": version2.id,
                    "version": version2.version,
                    "created_at": version2.created_at.isoformat() if version2.created_at else None,
                    "meal_count": len(meals2),
                    "total_calories": total_calories2,
                    "total_protein": total_protein2
                },
                "differences": {
                    "calorie_difference": total_calories2 - total_calories1,
                    "protein_difference": total_protein2 - total_protein1,
                    "meal_count_difference": len(meals2) - len(meals1)
                }
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing meal plan versions: {str(e)}")
            return {"error": str(e)}
    
    def _increment_version(self, current_version: str) -> str:
        """Increment version number"""
        try:
            # Parse version (e.g., "1.0" -> 1.0)
            version_parts = current_version.split(".")
            major = int(version_parts[0])
            minor = int(version_parts[1]) if len(version_parts) > 1 else 0
            
            # Increment minor version
            minor += 1
            
            return f"{major}.{minor}"
        except:
            # If parsing fails, start from 1.1
            return "1.1"
    
    def _cleanup_old_versions(self, db: Session, user_id: int, base_plan_id: str):
        """Clean up old versions to stay within the limit"""
        try:
            # Get the base plan to find related versions
            base_plan = db.query(MealPlan).filter(
                and_(MealPlan.id == base_plan_id, MealPlan.user_id == user_id)
            ).first()
            
            if not base_plan:
                return
            
            # Get all versions for this date and plan type
            all_versions = db.query(MealPlan).filter(
                and_(
                    MealPlan.user_id == user_id,
                    MealPlan.start_date == base_plan.start_date,
                    MealPlan.plan_type == base_plan.plan_type
                )
            ).order_by(desc(MealPlan.created_at)).all()
            
            # Keep only the most recent versions
            if len(all_versions) > self.max_versions_per_plan:
                versions_to_delete = all_versions[self.max_versions_per_plan:]
                
                for version in versions_to_delete:
                    # Delete associated meals first
                    db.query(MealPlanMeal).filter(
                        MealPlanMeal.meal_plan_id == version.id
                    ).delete()
                    
                    # Delete the meal plan
                    db.delete(version)
                
                logger.info(f"Cleaned up {len(versions_to_delete)} old meal plan versions")
                
        except Exception as e:
            logger.error(f"Error cleaning up old versions: {str(e)}")
    
    def _deactivate_other_versions(self, db: Session, user_id: int, start_date: date, plan_type: str):
        """Deactivate all other versions for the same date and plan type"""
        try:
            db.query(MealPlan).filter(
                and_(
                    MealPlan.user_id == user_id,
                    MealPlan.start_date == start_date,
                    MealPlan.plan_type == plan_type,
                    MealPlan.is_active == True
                )
            ).update({"is_active": False})
            
        except Exception as e:
            logger.error(f"Error deactivating other versions: {str(e)}")

# Global instance
meal_plan_versioning_service = MealPlanVersioningService()



