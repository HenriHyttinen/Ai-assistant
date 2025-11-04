#!/usr/bin/env python3
"""
Database Migration Script for Nutrition Tables

This script creates the nutrition-related tables in the database.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine, Base
from models.nutrition import (
    UserNutritionPreferences, MealPlan, MealPlanMeal, MealPlanRecipe,
    Recipe, Ingredient, RecipeIngredient, RecipeInstruction,
    NutritionalLog, ShoppingList, ShoppingListItem
)
from models.user import User

def create_nutrition_tables():
    """Create all nutrition-related tables"""
    print("Creating nutrition tables...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Nutrition tables created successfully!")
        
        # Verify tables were created
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE '%nutrition%' 
                OR table_name IN ('recipes', 'ingredients', 'recipe_ingredients', 'recipe_instructions')
                ORDER BY table_name;
            """))
            
            tables = [row[0] for row in result]
            print(f"📊 Created tables: {', '.join(tables)}")
            
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        raise

def verify_database_connection():
    """Verify database connection and permissions"""
    print("Verifying database connection...")
    
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

def main():
    """Main migration function"""
    print("Starting nutrition database migration...")
    
    # Verify database connection
    if not verify_database_connection():
        print("❌ Cannot proceed without database connection")
        return
    
    # Create nutrition tables
    create_nutrition_tables()
    
    print("🎉 Migration completed successfully!")
    print("Next steps:")
    print("1. Run populate_nutrition_database.py to add sample data")
    print("2. Test the API endpoints")
    print("3. Verify frontend integration")

if __name__ == "__main__":
    main()
