#!/usr/bin/env python3
"""
Minimal Database Seeder

This script creates minimal sample data without triggering SQLAlchemy relationship issues.
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine
from models.base import Base
from sqlalchemy import text

def create_tables():
    """Create all tables"""
    print("Creating nutrition tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")

def create_sample_data():
    """Create minimal sample data using raw SQL"""
    print("Creating sample data...")
    
    db = SessionLocal()
    try:
        # Create sample ingredients using raw SQL
        ingredients_sql = """
        INSERT INTO ingredients (id, name, category, unit, default_quantity, calories, protein, carbs, fats, fiber, sugar, sodium, created_at, updated_at)
        VALUES 
        ('ing_1', 'chicken breast', 'protein', 'g', 100.0, 165, 31, 0, 3.6, 0, 0, 74, datetime('now'), datetime('now')),
        ('ing_2', 'salmon fillet', 'protein', 'g', 100.0, 208, 25, 0, 12, 0, 0, 59, datetime('now'), datetime('now')),
        ('ing_3', 'eggs', 'protein', 'g', 100.0, 155, 13, 1.1, 11, 0, 1.1, 124, datetime('now'), datetime('now')),
        ('ing_4', 'brown rice', 'grains', 'g', 100.0, 111, 2.6, 23, 0.9, 1.8, 0.4, 5, datetime('now'), datetime('now')),
        ('ing_5', 'quinoa', 'grains', 'g', 100.0, 120, 4.4, 22, 1.9, 2.8, 0.9, 7, datetime('now'), datetime('now')),
        ('ing_6', 'broccoli', 'vegetables', 'g', 100.0, 34, 2.8, 7, 0.4, 2.6, 1.5, 33, datetime('now'), datetime('now')),
        ('ing_7', 'spinach', 'vegetables', 'g', 100.0, 23, 2.9, 3.6, 0.4, 2.2, 0.4, 79, datetime('now'), datetime('now')),
        ('ing_8', 'tomatoes', 'vegetables', 'g', 100.0, 18, 0.9, 3.9, 0.2, 1.2, 2.6, 5, datetime('now'), datetime('now')),
        ('ing_9', 'olive oil', 'fats', 'ml', 100.0, 884, 0, 0, 100, 0, 0, 2, datetime('now'), datetime('now')),
        ('ing_10', 'avocados', 'fruits', 'g', 100.0, 160, 2, 9, 15, 6.7, 0.7, 7, datetime('now'), datetime('now'))
        ON CONFLICT (id) DO NOTHING;
        """
        
        db.execute(text(ingredients_sql))
        
        # Create sample recipes using raw SQL
        recipes_sql = """
        INSERT INTO recipes (id, title, cuisine, meal_type, servings, summary, prep_time, cook_time, difficulty_level, dietary_tags, source, created_at, updated_at)
        VALUES 
        ('r_1', 'Mediterranean Omelet', 'Mediterranean', 'breakfast', 2, 'A delicious Mediterranean-style omelet perfect for breakfast', 10, 15, 'easy', '["vegetarian", "high-protein"]', 'database-seeded', datetime('now'), datetime('now')),
        ('r_2', 'Protein Power Smoothie', 'International', 'breakfast', 1, 'A nutritious smoothie packed with protein', 5, 0, 'easy', '["vegetarian", "high-protein", "quick"]', 'database-seeded', datetime('now'), datetime('now')),
        ('r_3', 'Quinoa Buddha Bowl', 'International', 'lunch', 2, 'A healthy and colorful Buddha bowl', 15, 20, 'medium', '["vegetarian", "vegan", "gluten-free"]', 'database-seeded', datetime('now'), datetime('now')),
        ('r_4', 'Baked Salmon with Vegetables', 'International', 'dinner', 2, 'A healthy and delicious salmon dinner', 15, 25, 'medium', '["gluten-free", "high-protein", "omega-3"]', 'database-seeded', datetime('now'), datetime('now')),
        ('r_5', 'Vegetarian Stir-Fry', 'Asian', 'dinner', 2, 'A quick and healthy stir-fry', 20, 15, 'easy', '["vegetarian", "vegan", "quick"]', 'database-seeded', datetime('now'), datetime('now'))
        ON CONFLICT (id) DO NOTHING;
        """
        
        db.execute(text(recipes_sql))
        
        # Create recipe ingredients
        recipe_ingredients_sql = """
        INSERT INTO recipe_ingredients (recipe_id, ingredient_id, quantity, unit)
        VALUES 
        ('r_1', 'ing_3', 100, 'g'),
        ('r_1', 'ing_8', 150, 'g'),
        ('r_1', 'ing_7', 50, 'g'),
        ('r_1', 'ing_9', 10, 'ml'),
        ('r_2', 'ing_3', 200, 'g'),
        ('r_2', 'ing_10', 100, 'g'),
        ('r_3', 'ing_5', 100, 'g'),
        ('r_3', 'ing_6', 150, 'g'),
        ('r_3', 'ing_10', 100, 'g'),
        ('r_4', 'ing_2', 200, 'g'),
        ('r_4', 'ing_6', 200, 'g'),
        ('r_4', 'ing_9', 20, 'ml')
        ON CONFLICT DO NOTHING;
        """
        
        db.execute(text(recipe_ingredients_sql))
        
        # Create recipe instructions
        instructions_sql = """
        INSERT INTO recipe_instructions (recipe_id, step_number, step_title, description, time_required)
        VALUES 
        ('r_1', 1, 'Step 1', 'Heat olive oil in a non-stick pan over medium heat.', 2),
        ('r_1', 2, 'Step 2', 'Beat eggs in a bowl and season with salt and pepper.', 3),
        ('r_1', 3, 'Step 3', 'Add tomatoes and spinach to the pan, cook for 2 minutes.', 2),
        ('r_1', 4, 'Step 4', 'Pour beaten eggs over vegetables and cook until set.', 5),
        ('r_1', 5, 'Step 5', 'Fold omelet in half and serve immediately.', 1),
        ('r_2', 1, 'Step 1', 'Add all ingredients to a blender.', 1),
        ('r_2', 2, 'Step 2', 'Blend on high speed for 1-2 minutes until smooth.', 2),
        ('r_2', 3, 'Step 3', 'Taste and adjust sweetness if needed.', 1),
        ('r_2', 4, 'Step 4', 'Pour into a glass and serve immediately.', 1)
        ON CONFLICT DO NOTHING;
        """
        
        db.execute(text(instructions_sql))
        
        db.commit()
        print("✅ Sample data created successfully")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    """Main function to populate the database"""
    print("🚀 Starting minimal database population...")
    
    try:
        # Create tables
        create_tables()
        
        # Create sample data
        create_sample_data()
        
        print("🎉 Database population completed successfully!")
        print("📊 Summary:")
        print("   - 10 ingredients created")
        print("   - 5 recipes created")
        print("   - Recipe ingredients and instructions added")
        print("\n🔗 Next steps:")
        print("   1. Test the API endpoints")
        print("   2. Verify frontend integration")
        print("   3. Add more recipes as needed")
        
    except Exception as e:
        print(f"❌ Error populating database: {str(e)}")
        raise

if __name__ == "__main__":
    main()
