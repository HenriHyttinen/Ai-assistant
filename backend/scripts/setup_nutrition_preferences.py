#!/usr/bin/env python3
"""
Script to set up default nutrition preferences for a user
"""

import sys
import os
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine
from sqlalchemy import text

def setup_nutrition_preferences():
    """Set up default nutrition preferences for the user"""
    db = SessionLocal()
    try:
        # Get the user ID
        result = db.execute(text("SELECT id FROM users WHERE email = 'henri_hyttinen@hotmail.com'"))
        user_row = result.fetchone()
        
        if not user_row:
            print("❌ User not found in database")
            return False
        
        user_id = user_row[0]
        print(f"✅ User found: ID {user_id}")
        
        # Check if user already has nutrition preferences
        result = db.execute(text("SELECT id FROM user_nutrition_preferences WHERE user_id = :user_id"), {"user_id": user_id})
        existing_prefs = result.fetchone()
        
        if existing_prefs:
            print("✅ User already has nutrition preferences")
            return True
        
        # Create default nutrition preferences
        now = datetime.now()
        insert_sql = text("""
            INSERT INTO user_nutrition_preferences (
                user_id, dietary_preferences, allergies, disliked_ingredients,
                cuisine_preferences, daily_calorie_target, protein_target,
                carbs_target, fats_target, meals_per_day, preferred_meal_times,
                timezone, created_at, updated_at
            ) VALUES (
                :user_id, :dietary_preferences, :allergies, :disliked_ingredients,
                :cuisine_preferences, :daily_calorie_target, :protein_target,
                :carbs_target, :fats_target, :meals_per_day, :preferred_meal_times,
                :timezone, :created_at, :updated_at
            )
        """)
        
        db.execute(insert_sql, {
            "user_id": user_id,
            "dietary_preferences": "[]",
            "allergies": "[]", 
            "disliked_ingredients": "[]",
            "cuisine_preferences": '["International"]',
            "daily_calorie_target": 2000,
            "protein_target": 150,
            "carbs_target": 250,
            "fats_target": 65,
            "meals_per_day": 3,
            "preferred_meal_times": '{"breakfast": "08:00", "lunch": "13:00", "dinner": "19:00"}',
            "timezone": "UTC",
            "created_at": now,
            "updated_at": now
        })
        
        db.commit()
        print("✅ Default nutrition preferences created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up nutrition preferences: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    setup_nutrition_preferences()





