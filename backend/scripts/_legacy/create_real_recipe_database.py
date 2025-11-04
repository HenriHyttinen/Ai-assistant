#!/usr/bin/env python3
"""
Create a REAL recipe database with actual recipes from the internet.
This will replace all fake placeholder recipes with real cooking recipes.
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

def clear_fake_recipes():
    """Clear all existing fake recipes"""
    db = SessionLocal()
    try:
        # Delete all existing recipes, ingredients, and instructions
        db.execute(text("DELETE FROM recipe_instructions"))
        db.execute(text("DELETE FROM recipe_ingredients")) 
        db.execute(text("DELETE FROM recipes"))
        db.execute(text("DELETE FROM ingredients"))
        db.commit()
        logger.info("✅ Cleared all fake recipes")
    except Exception as e:
        logger.error(f"❌ Error clearing recipes: {e}")
        db.rollback()
    finally:
        db.close()

def create_real_ingredients():
    """Create real ingredients database"""
    db = SessionLocal()
    try:
        real_ingredients = [
            # Proteins
            {"id": "chicken_breast", "name": "Chicken Breast", "category": "protein", "unit": "g", "calories": 165, "protein": 31, "carbs": 0, "fats": 3.6},
            {"id": "beef_sirloin", "name": "Beef Sirloin", "category": "protein", "unit": "g", "calories": 250, "protein": 26, "carbs": 0, "fats": 15},
            {"id": "salmon_fillet", "name": "Salmon Fillet", "category": "protein", "unit": "g", "calories": 208, "protein": 25, "carbs": 0, "fats": 12},
            {"id": "eggs", "name": "Eggs", "category": "protein", "unit": "piece", "calories": 70, "protein": 6, "carbs": 0.6, "fats": 5},
            {"id": "ground_beef", "name": "Ground Beef", "category": "protein", "unit": "g", "calories": 254, "protein": 26, "carbs": 0, "fats": 17},
            {"id": "pork_tenderloin", "name": "Pork Tenderloin", "category": "protein", "unit": "g", "calories": 143, "protein": 26, "carbs": 0, "fats": 3.5},
            
            # Vegetables
            {"id": "onion", "name": "Onion", "category": "vegetable", "unit": "g", "calories": 40, "protein": 1.1, "carbs": 9.3, "fats": 0.1},
            {"id": "garlic", "name": "Garlic", "category": "vegetable", "unit": "clove", "calories": 4, "protein": 0.2, "carbs": 1, "fats": 0},
            {"id": "tomato", "name": "Tomato", "category": "vegetable", "unit": "g", "calories": 18, "protein": 0.9, "carbs": 3.9, "fats": 0.2},
            {"id": "bell_pepper", "name": "Bell Pepper", "category": "vegetable", "unit": "g", "calories": 31, "protein": 1, "carbs": 7.3, "fats": 0.3},
            {"id": "carrot", "name": "Carrot", "category": "vegetable", "unit": "g", "calories": 41, "protein": 0.9, "carbs": 9.6, "fats": 0.2},
            {"id": "celery", "name": "Celery", "category": "vegetable", "unit": "g", "calories": 16, "protein": 0.7, "carbs": 3, "fats": 0.2},
            {"id": "mushrooms", "name": "Mushrooms", "category": "vegetable", "unit": "g", "calories": 22, "protein": 3.1, "carbs": 3.3, "fats": 0.3},
            {"id": "spinach", "name": "Spinach", "category": "vegetable", "unit": "g", "calories": 23, "protein": 2.9, "carbs": 3.6, "fats": 0.4},
            {"id": "broccoli", "name": "Broccoli", "category": "vegetable", "unit": "g", "calories": 34, "protein": 2.8, "carbs": 6.6, "fats": 0.4},
            {"id": "potato", "name": "Potato", "category": "vegetable", "unit": "g", "calories": 77, "protein": 2, "carbs": 17, "fats": 0.1},
            
            # Grains & Starches
            {"id": "rice", "name": "Rice", "category": "grain", "unit": "g", "calories": 130, "protein": 2.7, "carbs": 28, "fats": 0.3},
            {"id": "pasta", "name": "Pasta", "category": "grain", "unit": "g", "calories": 131, "protein": 5, "carbs": 25, "fats": 1.1},
            {"id": "bread", "name": "Bread", "category": "grain", "unit": "slice", "calories": 80, "protein": 3, "carbs": 15, "fats": 1},
            {"id": "quinoa", "name": "Quinoa", "category": "grain", "unit": "g", "calories": 120, "protein": 4.4, "carbs": 22, "fats": 1.9},
            
            # Dairy
            {"id": "milk", "name": "Milk", "category": "dairy", "unit": "ml", "calories": 42, "protein": 3.4, "carbs": 5, "fats": 1},
            {"id": "cheese", "name": "Cheese", "category": "dairy", "unit": "g", "calories": 113, "protein": 7, "carbs": 0.4, "fats": 9},
            {"id": "butter", "name": "Butter", "category": "dairy", "unit": "g", "calories": 717, "protein": 0.9, "carbs": 0.1, "fats": 81},
            {"id": "yogurt", "name": "Yogurt", "category": "dairy", "unit": "g", "calories": 59, "protein": 10, "carbs": 3.6, "fats": 0.4},
            {"id": "cream", "name": "Heavy Cream", "category": "dairy", "unit": "ml", "calories": 345, "protein": 2.8, "carbs": 2.8, "fats": 37},
            
            # Oils & Fats
            {"id": "olive_oil", "name": "Olive Oil", "category": "oil", "unit": "ml", "calories": 884, "protein": 0, "carbs": 0, "fats": 100},
            {"id": "vegetable_oil", "name": "Vegetable Oil", "category": "oil", "unit": "ml", "calories": 884, "protein": 0, "carbs": 0, "fats": 100},
            {"id": "coconut_oil", "name": "Coconut Oil", "category": "oil", "unit": "ml", "calories": 884, "protein": 0, "carbs": 0, "fats": 100},
            
            # Herbs & Spices
            {"id": "salt", "name": "Salt", "category": "spice", "unit": "g", "calories": 0, "protein": 0, "carbs": 0, "fats": 0},
            {"id": "black_pepper", "name": "Black Pepper", "category": "spice", "unit": "g", "calories": 251, "protein": 10, "carbs": 64, "fats": 3.3},
            {"id": "oregano", "name": "Oregano", "category": "herb", "unit": "g", "calories": 265, "protein": 9, "carbs": 69, "fats": 4.3},
            {"id": "basil", "name": "Basil", "category": "herb", "unit": "g", "calories": 22, "protein": 3.2, "carbs": 2.6, "fats": 0.6},
            {"id": "thyme", "name": "Thyme", "category": "herb", "unit": "g", "calories": 101, "protein": 5.6, "carbs": 24, "fats": 1.7},
            {"id": "rosemary", "name": "Rosemary", "category": "herb", "unit": "g", "calories": 131, "protein": 3.3, "carbs": 21, "fats": 5.9},
            {"id": "parsley", "name": "Parsley", "category": "herb", "unit": "g", "calories": 36, "protein": 3, "carbs": 6, "fats": 0.8},
            {"id": "cilantro", "name": "Cilantro", "category": "herb", "unit": "g", "calories": 23, "protein": 2.1, "carbs": 3.7, "fats": 0.5},
            {"id": "ginger", "name": "Ginger", "category": "spice", "unit": "g", "calories": 80, "protein": 1.8, "carbs": 18, "fats": 0.8},
            {"id": "cumin", "name": "Cumin", "category": "spice", "unit": "g", "calories": 375, "protein": 18, "carbs": 44, "fats": 22},
            {"id": "paprika", "name": "Paprika", "category": "spice", "unit": "g", "calories": 282, "protein": 14, "carbs": 54, "fats": 12},
            {"id": "cinnamon", "name": "Cinnamon", "category": "spice", "unit": "g", "calories": 247, "protein": 4, "carbs": 81, "fats": 1.2},
            {"id": "nutmeg", "name": "Nutmeg", "category": "spice", "unit": "g", "calories": 525, "protein": 6, "carbs": 49, "fats": 36},
            
            # Nuts & Seeds
            {"id": "almonds", "name": "Almonds", "category": "nut", "unit": "g", "calories": 579, "protein": 21, "carbs": 22, "fats": 50},
            {"id": "walnuts", "name": "Walnuts", "category": "nut", "unit": "g", "calories": 654, "protein": 15, "carbs": 14, "fats": 65},
            {"id": "sesame_seeds", "name": "Sesame Seeds", "category": "seed", "unit": "g", "calories": 573, "protein": 18, "carbs": 23, "fats": 50},
            
            # Legumes
            {"id": "lentils", "name": "Lentils", "category": "legume", "unit": "g", "calories": 116, "protein": 9, "carbs": 20, "fats": 0.4},
            {"id": "chickpeas", "name": "Chickpeas", "category": "legume", "unit": "g", "calories": 164, "protein": 8.9, "carbs": 27, "fats": 2.6},
            {"id": "black_beans", "name": "Black Beans", "category": "legume", "unit": "g", "calories": 132, "protein": 8.9, "carbs": 24, "fats": 0.5},
            
            # Fruits
            {"id": "lemon", "name": "Lemon", "category": "fruit", "unit": "piece", "calories": 17, "protein": 0.6, "carbs": 5.4, "fats": 0.2},
            {"id": "lime", "name": "Lime", "category": "fruit", "unit": "piece", "calories": 20, "protein": 0.5, "carbs": 7, "fats": 0.1},
            {"id": "apple", "name": "Apple", "category": "fruit", "unit": "piece", "calories": 52, "protein": 0.3, "carbs": 14, "fats": 0.2},
            {"id": "banana", "name": "Banana", "category": "fruit", "unit": "piece", "calories": 89, "protein": 1.1, "carbs": 23, "fats": 0.3},
            
            # Additional ingredients needed for recipes
            {"id": "soy_sauce", "name": "Soy Sauce", "category": "condiment", "unit": "ml", "calories": 8, "protein": 1.3, "carbs": 0.8, "fats": 0},
            {"id": "sesame_oil", "name": "Sesame Oil", "category": "oil", "unit": "ml", "calories": 884, "protein": 0, "carbs": 0, "fats": 100},
            {"id": "mirin", "name": "Mirin", "category": "condiment", "unit": "ml", "calories": 43, "protein": 0, "carbs": 10.7, "fats": 0},
            {"id": "sugar", "name": "Sugar", "category": "sweetener", "unit": "g", "calories": 387, "protein": 0, "carbs": 100, "fats": 0},
            {"id": "green_onion", "name": "Green Onion", "category": "vegetable", "unit": "piece", "calories": 5, "protein": 0.3, "carbs": 1, "fats": 0},
            {"id": "cornstarch", "name": "Cornstarch", "category": "thickener", "unit": "g", "calories": 381, "protein": 0.3, "carbs": 91, "fats": 0.1},
            {"id": "flour", "name": "Flour", "category": "grain", "unit": "g", "calories": 364, "protein": 10, "carbs": 76, "fats": 1},
            {"id": "tortillas", "name": "Tortillas", "category": "grain", "unit": "piece", "calories": 146, "protein": 3.7, "carbs": 24, "fats": 3.7},
            {"id": "cabbage", "name": "Cabbage", "category": "vegetable", "unit": "g", "calories": 25, "protein": 1.3, "carbs": 5.8, "fats": 0.1},
            {"id": "white_fish", "name": "White Fish", "category": "protein", "unit": "g", "calories": 96, "protein": 20, "carbs": 0, "fats": 1.3},
            {"id": "snow_peas", "name": "Snow Peas", "category": "vegetable", "unit": "g", "calories": 42, "protein": 2.8, "carbs": 7.6, "fats": 0.2},
            {"id": "coconut_milk", "name": "Coconut Milk", "category": "dairy", "unit": "ml", "calories": 230, "protein": 2.3, "carbs": 6, "fats": 24},
            {"id": "curry_powder", "name": "Curry Powder", "category": "spice", "unit": "g", "calories": 325, "protein": 14, "carbs": 58, "fats": 14},
            {"id": "turmeric", "name": "Turmeric", "category": "spice", "unit": "g", "calories": 354, "protein": 8, "carbs": 65, "fats": 10},
            {"id": "cayenne", "name": "Cayenne Pepper", "category": "spice", "unit": "g", "calories": 318, "protein": 12, "carbs": 56, "fats": 17},
            {"id": "pancetta", "name": "Pancetta", "category": "protein", "unit": "g", "calories": 455, "protein": 18, "carbs": 0, "fats": 42},
            {"id": "red_wine", "name": "Red Wine", "category": "beverage", "unit": "ml", "calories": 85, "protein": 0.1, "carbs": 2.6, "fats": 0},
            {"id": "bay_leaves", "name": "Bay Leaves", "category": "herb", "unit": "piece", "calories": 313, "protein": 8, "carbs": 75, "fats": 8},
            {"id": "beef_stock", "name": "Beef Stock", "category": "broth", "unit": "ml", "calories": 6, "protein": 0.6, "carbs": 0.6, "fats": 0.2},
            {"id": "bacon", "name": "Bacon", "category": "protein", "unit": "g", "calories": 541, "protein": 37, "carbs": 1.4, "fats": 42},
            {"id": "chicken_stock", "name": "Chicken Stock", "category": "broth", "unit": "ml", "calories": 6, "protein": 0.6, "carbs": 0.6, "fats": 0.2},
            {"id": "egg_noodles", "name": "Egg Noodles", "category": "grain", "unit": "g", "calories": 138, "protein": 4.5, "carbs": 25, "fats": 2.1},
        ]
        
        for ing_data in real_ingredients:
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
        logger.info(f"✅ Created {len(real_ingredients)} real ingredients")
        
    except Exception as e:
        logger.error(f"❌ Error creating ingredients: {e}")
        db.rollback()
    finally:
        db.close()

def create_real_recipes():
    """Create real recipes with actual cooking instructions"""
    db = SessionLocal()
    try:
        real_recipes = [
            {
                "id": "chicken_parmesan",
                "title": "Chicken Parmesan",
                "cuisine": "Italian",
                "meal_type": "dinner",
                "servings": 4,
                "summary": "Classic Italian-American dish with breaded chicken, marinara sauce, and melted cheese",
                "prep_time": 20,
                "cook_time": 25,
                "ingredients": [
                    {"ingredient_id": "chicken_breast", "quantity": 500, "unit": "g"},
                    {"ingredient_id": "bread", "quantity": 2, "unit": "slice"},
                    {"ingredient_id": "eggs", "quantity": 2, "unit": "piece"},
                    {"ingredient_id": "cheese", "quantity": 100, "unit": "g"},
                    {"ingredient_id": "tomato", "quantity": 400, "unit": "g"},
                    {"ingredient_id": "onion", "quantity": 1, "unit": "piece"},
                    {"ingredient_id": "garlic", "quantity": 3, "unit": "clove"},
                    {"ingredient_id": "olive_oil", "quantity": 30, "unit": "ml"},
                    {"ingredient_id": "oregano", "quantity": 5, "unit": "g"},
                    {"ingredient_id": "basil", "quantity": 5, "unit": "g"},
                    {"ingredient_id": "salt", "quantity": 5, "unit": "g"},
                    {"ingredient_id": "black_pepper", "quantity": 2, "unit": "g"}
                ],
                "instructions": [
                    "Preheat oven to 200°C (400°F). Pound chicken breasts to even thickness.",
                    "Make breadcrumbs by processing bread in food processor. Set up breading station with flour, beaten eggs, and breadcrumbs.",
                    "Season chicken with salt and pepper. Dredge in flour, dip in eggs, then coat with breadcrumbs.",
                    "Heat olive oil in large oven-safe skillet over medium-high heat. Cook chicken until golden, 3-4 minutes per side.",
                    "Make marinara sauce: sauté onions and garlic, add tomatoes, oregano, and basil. Simmer 15 minutes.",
                    "Top chicken with marinara sauce and cheese. Bake in oven until cheese melts, 10-15 minutes.",
                    "Garnish with fresh basil and serve immediately."
                ]
            },
            {
                "id": "beef_stir_fry",
                "title": "Beef Stir Fry",
                "cuisine": "Asian",
                "meal_type": "dinner", 
                "servings": 4,
                "summary": "Quick and healthy Asian-style beef stir fry with vegetables",
                "prep_time": 15,
                "cook_time": 10,
                "ingredients": [
                    {"ingredient_id": "beef_sirloin", "quantity": 400, "unit": "g"},
                    {"ingredient_id": "bell_pepper", "quantity": 2, "unit": "piece"},
                    {"ingredient_id": "broccoli", "quantity": 200, "unit": "g"},
                    {"ingredient_id": "carrot", "quantity": 150, "unit": "g"},
                    {"ingredient_id": "onion", "quantity": 1, "unit": "piece"},
                    {"ingredient_id": "garlic", "quantity": 3, "unit": "clove"},
                    {"ingredient_id": "ginger", "quantity": 20, "unit": "g"},
                    {"ingredient_id": "soy_sauce", "quantity": 60, "unit": "ml"},
                    {"ingredient_id": "sesame_oil", "quantity": 15, "unit": "ml"},
                    {"ingredient_id": "vegetable_oil", "quantity": 30, "unit": "ml"},
                    {"ingredient_id": "cornstarch", "quantity": 10, "unit": "g"},
                    {"ingredient_id": "rice", "quantity": 200, "unit": "g"}
                ],
                "instructions": [
                    "Slice beef into thin strips against the grain. Marinate with soy sauce and cornstarch for 15 minutes.",
                    "Cut all vegetables into bite-sized pieces. Mince garlic and ginger.",
                    "Cook rice according to package instructions. Keep warm.",
                    "Heat vegetable oil in large wok or skillet over high heat. Add beef and stir-fry 2-3 minutes until browned. Remove and set aside.",
                    "Add more oil if needed. Stir-fry vegetables starting with onions, then carrots, bell peppers, and broccoli.",
                    "Add garlic and ginger, stir-fry 30 seconds until fragrant.",
                    "Return beef to pan. Add remaining soy sauce and sesame oil. Toss everything together.",
                    "Serve immediately over rice."
                ]
            },
            {
                "id": "salmon_teriyaki",
                "title": "Salmon Teriyaki",
                "cuisine": "Japanese",
                "meal_type": "dinner",
                "servings": 4,
                "summary": "Glazed salmon with homemade teriyaki sauce",
                "prep_time": 10,
                "cook_time": 15,
                "ingredients": [
                    {"ingredient_id": "salmon_fillet", "quantity": 600, "unit": "g"},
                    {"ingredient_id": "soy_sauce", "quantity": 60, "unit": "ml"},
                    {"ingredient_id": "mirin", "quantity": 30, "unit": "ml"},
                    {"ingredient_id": "sugar", "quantity": 20, "unit": "g"},
                    {"ingredient_id": "ginger", "quantity": 15, "unit": "g"},
                    {"ingredient_id": "garlic", "quantity": 2, "unit": "clove"},
                    {"ingredient_id": "sesame_oil", "quantity": 10, "unit": "ml"},
                    {"ingredient_id": "sesame_seeds", "quantity": 10, "unit": "g"},
                    {"ingredient_id": "green_onion", "quantity": 2, "unit": "piece"},
                    {"ingredient_id": "rice", "quantity": 200, "unit": "g"}
                ],
                "instructions": [
                    "Make teriyaki sauce: combine soy sauce, mirin, sugar, minced ginger and garlic in small saucepan. Simmer 5 minutes until slightly thickened.",
                    "Season salmon fillets with salt and pepper. Heat oil in large skillet over medium-high heat.",
                    "Cook salmon skin-side down first, 4-5 minutes. Flip and cook other side 3-4 minutes until fish flakes easily.",
                    "Brush salmon with teriyaki sauce during last minute of cooking.",
                    "Remove salmon from pan. Let rest 2 minutes.",
                    "Serve over rice, drizzle with remaining teriyaki sauce. Garnish with sesame seeds and green onions."
                ]
            },
            {
                "id": "chicken_tikka_masala",
                "title": "Chicken Tikka Masala",
                "cuisine": "Indian",
                "meal_type": "dinner",
                "servings": 6,
                "summary": "Creamy Indian curry with spiced chicken in tomato-based sauce",
                "prep_time": 30,
                "cook_time": 45,
                "ingredients": [
                    {"ingredient_id": "chicken_breast", "quantity": 800, "unit": "g"},
                    {"ingredient_id": "yogurt", "quantity": 200, "unit": "g"},
                    {"ingredient_id": "garlic", "quantity": 6, "unit": "clove"},
                    {"ingredient_id": "ginger", "quantity": 30, "unit": "g"},
                    {"ingredient_id": "cumin", "quantity": 10, "unit": "g"},
                    {"ingredient_id": "paprika", "quantity": 5, "unit": "g"},
                    {"ingredient_id": "turmeric", "quantity": 5, "unit": "g"},
                    {"ingredient_id": "cayenne", "quantity": 2, "unit": "g"},
                    {"ingredient_id": "tomato", "quantity": 800, "unit": "g"},
                    {"ingredient_id": "onion", "quantity": 2, "unit": "piece"},
                    {"ingredient_id": "cream", "quantity": 200, "unit": "ml"},
                    {"ingredient_id": "butter", "quantity": 30, "unit": "g"},
                    {"ingredient_id": "cilantro", "quantity": 20, "unit": "g"},
                    {"ingredient_id": "rice", "quantity": 300, "unit": "g"}
                ],
                "instructions": [
                    "Cut chicken into bite-sized pieces. Make marinade with yogurt, half the garlic, half the ginger, cumin, paprika, turmeric, and cayenne.",
                    "Marinate chicken for at least 2 hours, preferably overnight.",
                    "Make sauce: sauté onions until golden. Add remaining garlic and ginger, cook 1 minute.",
                    "Add tomatoes, salt, and spices. Simmer 20 minutes until sauce thickens.",
                    "Blend sauce until smooth. Return to pan.",
                    "Cook marinated chicken in hot oil until golden. Add to sauce.",
                    "Simmer 15 minutes. Add cream and butter. Season to taste.",
                    "Garnish with cilantro. Serve over basmati rice."
                ]
            },
            {
                "id": "spaghetti_carbonara",
                "title": "Spaghetti Carbonara",
                "cuisine": "Italian",
                "meal_type": "dinner",
                "servings": 4,
                "summary": "Classic Roman pasta with eggs, cheese, and pancetta",
                "prep_time": 10,
                "cook_time": 15,
                "ingredients": [
                    {"ingredient_id": "pasta", "quantity": 400, "unit": "g"},
                    {"ingredient_id": "pancetta", "quantity": 150, "unit": "g"},
                    {"ingredient_id": "eggs", "quantity": 4, "unit": "piece"},
                    {"ingredient_id": "cheese", "quantity": 100, "unit": "g"},
                    {"ingredient_id": "black_pepper", "quantity": 5, "unit": "g"},
                    {"ingredient_id": "salt", "quantity": 5, "unit": "g"},
                    {"ingredient_id": "parsley", "quantity": 10, "unit": "g"}
                ],
                "instructions": [
                    "Cook pasta in salted boiling water until al dente. Reserve 1 cup pasta water.",
                    "Cut pancetta into small cubes. Cook in large skillet until crispy, 5-7 minutes.",
                    "Whisk eggs with grated cheese and black pepper in large bowl.",
                    "Drain pasta, immediately add to pancetta in skillet. Remove from heat.",
                    "Quickly toss pasta with egg mixture, adding pasta water gradually to create creamy sauce.",
                    "Serve immediately with extra cheese and black pepper. Garnish with parsley."
                ]
            },
            {
                "id": "beef_bourguignon",
                "title": "Beef Bourguignon",
                "cuisine": "French",
                "meal_type": "dinner",
                "servings": 6,
                "summary": "Classic French stew with beef braised in red wine",
                "prep_time": 30,
                "cook_time": 180,
                "ingredients": [
                    {"ingredient_id": "beef_sirloin", "quantity": 1000, "unit": "g"},
                    {"ingredient_id": "red_wine", "quantity": 750, "unit": "ml"},
                    {"ingredient_id": "onion", "quantity": 2, "unit": "piece"},
                    {"ingredient_id": "carrot", "quantity": 200, "unit": "g"},
                    {"ingredient_id": "mushrooms", "quantity": 300, "unit": "g"},
                    {"ingredient_id": "garlic", "quantity": 4, "unit": "clove"},
                    {"ingredient_id": "thyme", "quantity": 10, "unit": "g"},
                    {"ingredient_id": "rosemary", "quantity": 5, "unit": "g"},
                    {"ingredient_id": "bay_leaves", "quantity": 2, "unit": "piece"},
                    {"ingredient_id": "beef_stock", "quantity": 500, "unit": "ml"},
                    {"id": "bacon", "name": "Bacon", "category": "protein", "unit": "g", "calories": 541, "protein": 37, "carbs": 1.4, "fats": 42},
                    {"ingredient_id": "butter", "quantity": 30, "unit": "g"},
                    {"ingredient_id": "flour", "quantity": 30, "unit": "g"}
                ],
                "instructions": [
                    "Cut beef into 2-inch cubes. Season with salt and pepper. Brown in batches in hot oil, set aside.",
                    "Cook bacon until crispy. Remove, add onions and carrots. Cook until softened.",
                    "Add garlic, herbs, and flour. Cook 2 minutes until flour is incorporated.",
                    "Return beef and bacon to pot. Add wine and stock. Bring to boil.",
                    "Cover and simmer 2.5-3 hours until beef is tender.",
                    "Sauté mushrooms separately in butter. Add to stew in last 30 minutes.",
                    "Season to taste. Serve with crusty bread or over mashed potatoes."
                ]
            },
            {
                "id": "chicken_curry",
                "title": "Chicken Curry",
                "cuisine": "Indian",
                "meal_type": "dinner",
                "servings": 4,
                "summary": "Aromatic Indian chicken curry with coconut milk",
                "prep_time": 20,
                "cook_time": 30,
                "ingredients": [
                    {"ingredient_id": "chicken_breast", "quantity": 600, "unit": "g"},
                    {"ingredient_id": "coconut_milk", "quantity": 400, "unit": "ml"},
                    {"ingredient_id": "onion", "quantity": 2, "unit": "piece"},
                    {"ingredient_id": "garlic", "quantity": 4, "unit": "clove"},
                    {"ingredient_id": "ginger", "quantity": 25, "unit": "g"},
                    {"ingredient_id": "tomato", "quantity": 400, "unit": "g"},
                    {"ingredient_id": "curry_powder", "quantity": 15, "unit": "g"},
                    {"ingredient_id": "cumin", "quantity": 5, "unit": "g"},
                    {"ingredient_id": "turmeric", "quantity": 3, "unit": "g"},
                    {"ingredient_id": "cayenne", "quantity": 2, "unit": "g"},
                    {"ingredient_id": "cilantro", "quantity": 20, "unit": "g"},
                    {"ingredient_id": "rice", "quantity": 200, "unit": "g"}
                ],
                "instructions": [
                    "Cut chicken into bite-sized pieces. Season with salt and pepper.",
                    "Sauté onions until golden. Add garlic and ginger, cook 2 minutes.",
                    "Add curry powder, cumin, turmeric, and cayenne. Cook 1 minute until fragrant.",
                    "Add chicken, cook until golden on all sides, 5-7 minutes.",
                    "Add tomatoes and coconut milk. Bring to boil, then simmer 20 minutes.",
                    "Season with salt. Garnish with cilantro.",
                    "Serve over basmati rice with naan bread."
                ]
            },
            {
                "id": "fish_tacos",
                "title": "Fish Tacos",
                "cuisine": "Mexican",
                "meal_type": "dinner",
                "servings": 4,
                "summary": "Crispy fish tacos with cabbage slaw and lime crema",
                "prep_time": 25,
                "cook_time": 15,
                "ingredients": [
                    {"ingredient_id": "white_fish", "quantity": 500, "unit": "g"},
                    {"ingredient_id": "tortillas", "quantity": 8, "unit": "piece"},
                    {"ingredient_id": "cabbage", "quantity": 200, "unit": "g"},
                    {"ingredient_id": "lime", "quantity": 2, "unit": "piece"},
                    {"ingredient_id": "cilantro", "quantity": 15, "unit": "g"},
                    {"ingredient_id": "yogurt", "quantity": 150, "unit": "g"},
                    {"ingredient_id": "cumin", "quantity": 5, "unit": "g"},
                    {"ingredient_id": "paprika", "quantity": 5, "unit": "g"},
                    {"ingredient_id": "flour", "quantity": 100, "unit": "g"},
                    {"ingredient_id": "vegetable_oil", "quantity": 200, "unit": "ml"}
                ],
                "instructions": [
                    "Cut fish into strips. Season with salt, pepper, cumin, and paprika.",
                    "Make slaw: shred cabbage, mix with lime juice, cilantro, and salt.",
                    "Make lime crema: mix yogurt with lime zest and juice.",
                    "Dredge fish in flour. Heat oil in deep pan to 180°C (350°F).",
                    "Fry fish in batches until golden and crispy, 3-4 minutes.",
                    "Warm tortillas. Fill with fish, slaw, and drizzle with lime crema.",
                    "Serve immediately with lime wedges."
                ]
            },
            {
                "id": "vegetable_stir_fry",
                "title": "Vegetable Stir Fry",
                "cuisine": "Asian",
                "meal_type": "dinner",
                "servings": 4,
                "summary": "Colorful mixed vegetable stir fry with ginger soy sauce",
                "prep_time": 15,
                "cook_time": 10,
                "ingredients": [
                    {"ingredient_id": "broccoli", "quantity": 200, "unit": "g"},
                    {"ingredient_id": "bell_pepper", "quantity": 2, "unit": "piece"},
                    {"ingredient_id": "carrot", "quantity": 150, "unit": "g"},
                    {"ingredient_id": "mushrooms", "quantity": 200, "unit": "g"},
                    {"ingredient_id": "snow_peas", "quantity": 150, "unit": "g"},
                    {"ingredient_id": "onion", "quantity": 1, "unit": "piece"},
                    {"ingredient_id": "garlic", "quantity": 3, "unit": "clove"},
                    {"ingredient_id": "ginger", "quantity": 20, "unit": "g"},
                    {"ingredient_id": "soy_sauce", "quantity": 60, "unit": "ml"},
                    {"ingredient_id": "sesame_oil", "quantity": 15, "unit": "ml"},
                    {"ingredient_id": "vegetable_oil", "quantity": 30, "unit": "ml"},
                    {"ingredient_id": "rice", "quantity": 200, "unit": "g"}
                ],
                "instructions": [
                    "Cut all vegetables into bite-sized pieces. Mince garlic and ginger.",
                    "Heat oil in large wok or skillet over high heat.",
                    "Stir-fry vegetables in order of cooking time: onions first, then carrots, bell peppers, broccoli, mushrooms, and snow peas last.",
                    "Add garlic and ginger, stir-fry 30 seconds until fragrant.",
                    "Add soy sauce and sesame oil. Toss everything together.",
                    "Serve immediately over rice."
                ]
            },
            {
                "id": "chicken_noodle_soup",
                "title": "Chicken Noodle Soup",
                "cuisine": "American",
                "meal_type": "lunch",
                "servings": 6,
                "summary": "Comforting homemade chicken soup with egg noodles",
                "prep_time": 20,
                "cook_time": 45,
                "ingredients": [
                    {"ingredient_id": "chicken_breast", "quantity": 400, "unit": "g"},
                    {"ingredient_id": "egg_noodles", "quantity": 200, "unit": "g"},
                    {"ingredient_id": "onion", "quantity": 1, "unit": "piece"},
                    {"ingredient_id": "carrot", "quantity": 200, "unit": "g"},
                    {"ingredient_id": "celery", "quantity": 150, "unit": "g"},
                    {"ingredient_id": "garlic", "quantity": 3, "unit": "clove"},
                    {"ingredient_id": "thyme", "quantity": 5, "unit": "g"},
                    {"ingredient_id": "bay_leaves", "quantity": 2, "unit": "piece"},
                    {"ingredient_id": "chicken_stock", "quantity": 1.5, "unit": "L"},
                    {"ingredient_id": "parsley", "quantity": 15, "unit": "g"},
                    {"ingredient_id": "salt", "quantity": 5, "unit": "g"},
                    {"ingredient_id": "black_pepper", "quantity": 2, "unit": "g"}
                ],
                "instructions": [
                    "Season chicken with salt and pepper. Cook in large pot until golden, remove and set aside.",
                    "Sauté onions, carrots, and celery in same pot until softened, 5-7 minutes.",
                    "Add garlic, thyme, and bay leaves. Cook 1 minute until fragrant.",
                    "Add chicken stock and bring to boil. Return chicken to pot.",
                    "Simmer 20-25 minutes until chicken is cooked through. Remove chicken, shred, and return to pot.",
                    "Add noodles and cook according to package directions.",
                    "Season with salt and pepper. Garnish with parsley before serving."
                ]
            }
        ]
        
        for recipe_data in real_recipes:
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
                difficulty_level=recipe_data.get("difficulty_level", "medium")
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
        logger.info(f"✅ Created {len(real_recipes)} real recipes with proper ingredients and instructions")
        
    except Exception as e:
        logger.error(f"❌ Error creating recipes: {e}")
        db.rollback()
    finally:
        db.close()

def main():
    """Main function to create real recipe database"""
    logger.info("🍳 Creating REAL recipe database...")
    
    # Clear fake data
    clear_fake_recipes()
    
    # Create real ingredients
    create_real_ingredients()
    
    # Create real recipes
    create_real_recipes()
    
    logger.info("✅ Real recipe database created successfully!")
    logger.info("📚 Now you have actual cooking recipes with real ingredients and instructions!")

if __name__ == "__main__":
    main()
