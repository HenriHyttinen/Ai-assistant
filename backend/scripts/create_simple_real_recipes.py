#!/usr/bin/env python3
"""
Create a few REAL recipes to test the system.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine
from models.recipe import Recipe, Ingredient, RecipeIngredient, RecipeInstruction
from models.base import Base
from sqlalchemy import text
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clear_all_recipes():
    """Clear all existing recipes"""
    db = SessionLocal()
    try:
        # Delete all existing recipes, ingredients, and instructions
        db.execute(text("DELETE FROM recipe_instructions"))
        db.execute(text("DELETE FROM recipe_ingredients")) 
        db.execute(text("DELETE FROM recipes"))
        db.execute(text("DELETE FROM ingredients"))
        db.commit()
        logger.info("✅ Cleared all existing recipes")
    except Exception as e:
        logger.error(f"❌ Error clearing recipes: {e}")
        db.rollback()
    finally:
        db.close()

def create_basic_ingredients():
    """Create basic ingredients"""
    db = SessionLocal()
    try:
        ingredients = [
            {"id": "chicken_breast", "name": "Chicken Breast", "category": "protein", "unit": "g", "calories": 165, "protein": 31, "carbs": 0, "fats": 3.6},
            {"id": "onion", "name": "Onion", "category": "vegetable", "unit": "g", "calories": 40, "protein": 1.1, "carbs": 9.3, "fats": 0.1},
            {"id": "garlic", "name": "Garlic", "category": "vegetable", "unit": "clove", "calories": 4, "protein": 0.2, "carbs": 1, "fats": 0},
            {"id": "tomato", "name": "Tomato", "category": "vegetable", "unit": "g", "calories": 18, "protein": 0.9, "carbs": 3.9, "fats": 0.2},
            {"id": "olive_oil", "name": "Olive Oil", "category": "oil", "unit": "ml", "calories": 884, "protein": 0, "carbs": 0, "fats": 100},
            {"id": "salt", "name": "Salt", "category": "spice", "unit": "g", "calories": 0, "protein": 0, "carbs": 0, "fats": 0},
            {"id": "black_pepper", "name": "Black Pepper", "category": "spice", "unit": "g", "calories": 251, "protein": 10, "carbs": 64, "fats": 3.3},
            {"id": "oregano", "name": "Oregano", "category": "herb", "unit": "g", "calories": 265, "protein": 9, "carbs": 69, "fats": 4.3},
            {"id": "basil", "name": "Basil", "category": "herb", "unit": "g", "calories": 22, "protein": 3.2, "carbs": 2.6, "fats": 0.6},
            {"id": "cheese", "name": "Cheese", "category": "dairy", "unit": "g", "calories": 113, "protein": 7, "carbs": 0.4, "fats": 9},
        ]
        
        for ing_data in ingredients:
            ingredient = Ingredient(
                id=ing_data["id"],
                name=ing_data["name"],
                category=ing_data["category"],
                unit=ing_data["unit"],
                default_quantity=100.0,
                calories=ing_data["calories"],
                protein=ing_data["protein"],
                carbs=ing_data["carbs"],
                fats=ing_data["fats"]
            )
            db.add(ingredient)
        
        db.commit()
        logger.info(f"✅ Created {len(ingredients)} basic ingredients")
        
    except Exception as e:
        logger.error(f"❌ Error creating ingredients: {e}")
        db.rollback()
    finally:
        db.close()

def create_simple_recipes():
    """Create simple real recipes"""
    db = SessionLocal()
    try:
        recipes = [
            {
                "id": "simple_chicken",
                "title": "Simple Grilled Chicken",
                "cuisine": "American",
                "meal_type": "dinner",
                "servings": 4,
                "summary": "Basic grilled chicken breast with herbs",
                "prep_time": 10,
                "cook_time": 15,
                "ingredients": [
                    {"ingredient_id": "chicken_breast", "quantity": 500, "unit": "g"},
                    {"ingredient_id": "olive_oil", "quantity": 30, "unit": "ml"},
                    {"ingredient_id": "salt", "quantity": 5, "unit": "g"},
                    {"ingredient_id": "black_pepper", "quantity": 2, "unit": "g"},
                    {"ingredient_id": "oregano", "quantity": 3, "unit": "g"},
                ],
                "instructions": [
                    "Preheat grill to medium-high heat.",
                    "Season chicken breasts with salt, pepper, and oregano.",
                    "Brush chicken with olive oil.",
                    "Grill chicken for 6-7 minutes per side until internal temperature reaches 75°C.",
                    "Let rest for 5 minutes before serving."
                ]
            },
            {
                "id": "tomato_sauce",
                "title": "Basic Tomato Sauce",
                "cuisine": "Italian",
                "meal_type": "dinner",
                "servings": 4,
                "summary": "Simple homemade tomato sauce",
                "prep_time": 10,
                "cook_time": 30,
                "ingredients": [
                    {"ingredient_id": "tomato", "quantity": 800, "unit": "g"},
                    {"ingredient_id": "onion", "quantity": 100, "unit": "g"},
                    {"ingredient_id": "garlic", "quantity": 3, "unit": "clove"},
                    {"ingredient_id": "olive_oil", "quantity": 30, "unit": "ml"},
                    {"ingredient_id": "basil", "quantity": 5, "unit": "g"},
                    {"ingredient_id": "salt", "quantity": 3, "unit": "g"},
                    {"ingredient_id": "black_pepper", "quantity": 1, "unit": "g"},
                ],
                "instructions": [
                    "Heat olive oil in a large saucepan over medium heat.",
                    "Add diced onions and cook until translucent, about 5 minutes.",
                    "Add minced garlic and cook for 1 minute until fragrant.",
                    "Add tomatoes and break them down with a spoon.",
                    "Season with salt and pepper. Simmer for 20-25 minutes.",
                    "Add fresh basil and stir. Serve hot."
                ]
            }
        ]
        
        for recipe_data in recipes:
            # Create recipe
            recipe = Recipe(
                id=recipe_data["id"],
                title=recipe_data["title"],
                cuisine=recipe_data["cuisine"],
                meal_type=recipe_data["meal_type"],
                servings=recipe_data["servings"],
                summary=recipe_data["summary"],
                prep_time=recipe_data["prep_time"],
                cook_time=recipe_data["cook_time"],
                difficulty_level="easy"
            )
            db.add(recipe)
            db.flush()
            
            # Add ingredients
            for ing_data in recipe_data["ingredients"]:
                recipe_ingredient = RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=ing_data["ingredient_id"],
                    quantity=ing_data["quantity"],
                    unit=ing_data["unit"]
                )
                db.add(recipe_ingredient)
            
            # Add instructions
            for i, instruction in enumerate(recipe_data["instructions"], 1):
                recipe_instruction = RecipeInstruction(
                    recipe_id=recipe.id,
                    step_number=i,
                    step_title=f"Step {i}",
                    description=instruction
                )
                db.add(recipe_instruction)
        
        db.commit()
        logger.info(f"✅ Created {len(recipes)} simple real recipes")
        
    except Exception as e:
        logger.error(f"❌ Error creating recipes: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main function"""
    logger.info("🍳 Creating simple real recipes...")
    
    # Clear existing data
    clear_all_recipes()
    
    # Create basic ingredients
    create_basic_ingredients()
    
    # Create simple recipes
    create_simple_recipes()
    
    logger.info("✅ Simple real recipes created successfully!")
    logger.info("📚 Now you have actual cooking recipes with real ingredients and instructions!")

if __name__ == "__main__":
    main()










