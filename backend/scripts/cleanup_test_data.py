#!/usr/bin/env python3
"""
Clean up test data from the database to start fresh.
This will remove all existing users and related data.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.user import User
from models.user_settings import UserSettings
from models.health_profile import HealthProfile
from models.goal import Goal
from models.achievement import Achievement, UserAchievement
from models.activity_log import ActivityLog
from models.metrics_history import MetricsHistory
from models.consent import DataConsent
from models.recipe import Recipe, Ingredient, RecipeIngredient, RecipeInstruction
from models.nutrition import (
    UserNutritionPreferences, MealPlan, MealPlanMeal, MealPlanRecipe,
    NutritionalLog, ShoppingList, ShoppingListItem
)

def cleanup_database():
    """Clean up all test data from the database."""
    db = SessionLocal()
    try:
        print("🧹 Cleaning up test data...")
        
        # Delete in reverse order of dependencies
        print("Deleting nutrition data...")
        db.query(ShoppingListItem).delete()
        db.query(ShoppingList).delete()
        db.query(NutritionalLog).delete()
        db.query(MealPlanRecipe).delete()
        db.query(MealPlanMeal).delete()
        db.query(MealPlan).delete()
        db.query(UserNutritionPreferences).delete()
        
        print("Deleting recipe data...")
        db.query(RecipeInstruction).delete()
        db.query(RecipeIngredient).delete()
        db.query(Recipe).delete()
        db.query(Ingredient).delete()
        
        print("Deleting user-related data...")
        db.query(UserAchievement).delete()
        db.query(ActivityLog).delete()
        db.query(MetricsHistory).delete()
        db.query(DataConsent).delete()
        db.query(Goal).delete()
        db.query(HealthProfile).delete()
        db.query(UserSettings).delete()
        
        print("Deleting users...")
        db.query(User).delete()
        
        # Commit all changes
        db.commit()
        print("✅ Database cleaned up successfully!")
        
        # Verify cleanup
        user_count = db.query(User).count()
        settings_count = db.query(UserSettings).count()
        print(f"Remaining users: {user_count}")
        print(f"Remaining settings: {settings_count}")
        
    except Exception as e:
        print(f"❌ Error cleaning up database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_database()





