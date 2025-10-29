#!/usr/bin/env python3
"""
Simple script to check database content without relationship issues
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal
from sqlalchemy import text

def check_database():
    """Check database content"""
    db = SessionLocal()
    try:
        # Check recipes
        result = db.execute(text("SELECT COUNT(*) FROM recipes"))
        recipe_count = result.scalar()
        print(f"📊 Recipes in database: {recipe_count}")
        
        # Check ingredients
        result = db.execute(text("SELECT COUNT(*) FROM ingredients"))
        ingredient_count = result.scalar()
        print(f"📊 Ingredients in database: {ingredient_count}")
        
        # Check nutrition preferences
        result = db.execute(text("SELECT COUNT(*) FROM user_nutrition_preferences"))
        pref_count = result.scalar()
        print(f"📊 Nutrition preferences: {pref_count}")
        
        # Check meal plans
        result = db.execute(text("SELECT COUNT(*) FROM meal_plans"))
        meal_plan_count = result.scalar()
        print(f"📊 Meal plans: {meal_plan_count}")
        
        # Show sample recipes
        result = db.execute(text("SELECT title, cuisine, meal_type FROM recipes LIMIT 5"))
        recipes = result.fetchall()
        print(f"\n🍽️ Sample recipes:")
        for recipe in recipes:
            print(f"  - {recipe[0]} ({recipe[1]}, {recipe[2]})")
            
        # Show sample ingredients
        result = db.execute(text("SELECT name, category FROM ingredients LIMIT 5"))
        ingredients = result.fetchall()
        print(f"\n🥕 Sample ingredients:")
        for ingredient in ingredients:
            print(f"  - {ingredient[0]} ({ingredient[1]})")
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_database()
