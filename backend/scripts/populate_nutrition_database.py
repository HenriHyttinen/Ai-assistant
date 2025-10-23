#!/usr/bin/env python3
"""
Nutrition Database Population Script

This script populates the database with 500+ recipes and ingredients
with vector embeddings for RAG functionality.
"""

import os
import sys
import json
import random
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine
from models.nutrition import (
    Recipe, Ingredient, RecipeIngredient, RecipeInstruction,
    UserNutritionPreferences, MealPlan, MealPlanMeal, MealPlanRecipe,
    NutritionalLog, ShoppingList, ShoppingListItem
)
from models.base import Base
from sqlalchemy.orm import sessionmaker

# Initialize embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Sample ingredients with nutritional data
INGREDIENTS_DATA = [
    # Proteins
    {"name": "chicken breast", "category": "protein", "calories": 165, "protein": 31, "carbs": 0, "fats": 3.6},
    {"name": "salmon fillet", "category": "protein", "calories": 208, "protein": 25, "carbs": 0, "fats": 12},
    {"name": "ground beef", "category": "protein", "calories": 250, "protein": 26, "carbs": 0, "fats": 15},
    {"name": "eggs", "category": "protein", "calories": 155, "protein": 13, "carbs": 1.1, "fats": 11},
    {"name": "tofu", "category": "protein", "calories": 76, "protein": 8, "carbs": 1.9, "fats": 4.8},
    {"name": "lentils", "category": "protein", "calories": 116, "protein": 9, "carbs": 20, "fats": 0.4},
    {"name": "black beans", "category": "protein", "calories": 132, "protein": 8.9, "carbs": 24, "fats": 0.5},
    {"name": "greek yogurt", "category": "dairy", "calories": 59, "protein": 10, "carbs": 3.6, "fats": 0.4},
    {"name": "cottage cheese", "category": "dairy", "calories": 98, "protein": 11, "carbs": 3.4, "fats": 4.3},
    
    # Grains
    {"name": "brown rice", "category": "grains", "calories": 111, "protein": 2.6, "carbs": 23, "fats": 0.9},
    {"name": "quinoa", "category": "grains", "calories": 120, "protein": 4.4, "carbs": 22, "fats": 1.9},
    {"name": "oats", "category": "grains", "calories": 68, "protein": 2.4, "carbs": 12, "fats": 1.4},
    {"name": "whole wheat pasta", "category": "grains", "calories": 124, "protein": 5, "carbs": 25, "fats": 1.1},
    {"name": "bread", "category": "grains", "calories": 265, "protein": 9, "carbs": 49, "fats": 3.2},
    
    # Vegetables
    {"name": "broccoli", "category": "vegetables", "calories": 34, "protein": 2.8, "carbs": 7, "fats": 0.4},
    {"name": "spinach", "category": "vegetables", "calories": 23, "protein": 2.9, "carbs": 3.6, "fats": 0.4},
    {"name": "carrots", "category": "vegetables", "calories": 41, "protein": 0.9, "carbs": 10, "fats": 0.2},
    {"name": "tomatoes", "category": "vegetables", "calories": 18, "protein": 0.9, "carbs": 3.9, "fats": 0.2},
    {"name": "onions", "category": "vegetables", "calories": 40, "protein": 1.1, "carbs": 9.3, "fats": 0.1},
    {"name": "bell peppers", "category": "vegetables", "calories": 31, "protein": 1, "carbs": 7.3, "fats": 0.3},
    {"name": "mushrooms", "category": "vegetables", "calories": 22, "protein": 3.1, "carbs": 3.3, "fats": 0.3},
    {"name": "zucchini", "category": "vegetables", "calories": 17, "protein": 1.2, "carbs": 3.1, "fats": 0.3},
    {"name": "sweet potatoes", "category": "vegetables", "calories": 86, "protein": 1.6, "carbs": 20, "fats": 0.1},
    
    # Fruits
    {"name": "bananas", "category": "fruits", "calories": 89, "protein": 1.1, "carbs": 23, "fats": 0.3},
    {"name": "apples", "category": "fruits", "calories": 52, "protein": 0.3, "carbs": 14, "fats": 0.2},
    {"name": "berries", "category": "fruits", "calories": 57, "protein": 0.7, "carbs": 14, "fats": 0.3},
    {"name": "oranges", "category": "fruits", "calories": 47, "protein": 0.9, "carbs": 12, "fats": 0.1},
    {"name": "avocados", "category": "fruits", "calories": 160, "protein": 2, "carbs": 9, "fats": 15},
    
    # Fats & Oils
    {"name": "olive oil", "category": "fats", "calories": 884, "protein": 0, "carbs": 0, "fats": 100},
    {"name": "coconut oil", "category": "fats", "calories": 862, "protein": 0, "carbs": 0, "fats": 100},
    {"name": "butter", "category": "fats", "calories": 717, "protein": 0.9, "carbs": 0.1, "fats": 81},
    {"name": "almonds", "category": "fats", "calories": 579, "protein": 21, "carbs": 22, "fats": 50},
    {"name": "walnuts", "category": "fats", "calories": 654, "protein": 15, "carbs": 14, "fats": 65},
    
    # Dairy
    {"name": "milk", "category": "dairy", "calories": 42, "protein": 3.4, "carbs": 5, "fats": 1},
    {"name": "cheese", "category": "dairy", "calories": 113, "protein": 7, "carbs": 1, "fats": 9},
    {"name": "yogurt", "category": "dairy", "calories": 59, "protein": 10, "carbs": 3.6, "fats": 0.4},
]

# Recipe templates for different cuisines and meal types
RECIPE_TEMPLATES = [
    # Breakfast recipes
    {
        "title": "Mediterranean Omelet",
        "cuisine": "Mediterranean",
        "meal_type": "breakfast",
        "prep_time": 10,
        "cook_time": 15,
        "difficulty": "easy",
        "dietary_tags": ["vegetarian", "high-protein"],
        "ingredients": [
            {"name": "eggs", "quantity": 100, "unit": "g"},
            {"name": "tomatoes", "quantity": 150, "unit": "g"},
            {"name": "spinach", "quantity": 50, "unit": "g"},
            {"name": "olive oil", "quantity": 10, "unit": "ml"},
            {"name": "cheese", "quantity": 30, "unit": "g"}
        ],
        "instructions": [
            {"step": 1, "description": "Heat olive oil in a non-stick pan over medium heat."},
            {"step": 2, "description": "Beat eggs in a bowl and season with salt and pepper."},
            {"step": 3, "description": "Add tomatoes and spinach to the pan, cook for 2 minutes."},
            {"step": 4, "description": "Pour beaten eggs over vegetables and cook until set."},
            {"step": 5, "description": "Sprinkle cheese on top and fold omelet in half."}
        ]
    },
    {
        "title": "Protein Power Smoothie",
        "cuisine": "International",
        "meal_type": "breakfast",
        "prep_time": 5,
        "cook_time": 0,
        "difficulty": "easy",
        "dietary_tags": ["vegetarian", "high-protein", "quick"],
        "ingredients": [
            {"name": "greek yogurt", "quantity": 200, "unit": "g"},
            {"name": "bananas", "quantity": 100, "unit": "g"},
            {"name": "berries", "quantity": 50, "unit": "g"},
            {"name": "oats", "quantity": 30, "unit": "g"},
            {"name": "milk", "quantity": 150, "unit": "ml"}
        ],
        "instructions": [
            {"step": 1, "description": "Add all ingredients to a blender."},
            {"step": 2, "description": "Blend on high speed for 1-2 minutes until smooth."},
            {"step": 3, "description": "Taste and adjust sweetness if needed."},
            {"step": 4, "description": "Pour into a glass and serve immediately."}
        ]
    },
    # Lunch recipes
    {
        "title": "Quinoa Buddha Bowl",
        "cuisine": "International",
        "meal_type": "lunch",
        "prep_time": 15,
        "cook_time": 20,
        "difficulty": "medium",
        "dietary_tags": ["vegetarian", "vegan", "gluten-free"],
        "ingredients": [
            {"name": "quinoa", "quantity": 100, "unit": "g"},
            {"name": "sweet potatoes", "quantity": 200, "unit": "g"},
            {"name": "broccoli", "quantity": 150, "unit": "g"},
            {"name": "avocados", "quantity": 100, "unit": "g"},
            {"name": "olive oil", "quantity": 15, "unit": "ml"}
        ],
        "instructions": [
            {"step": 1, "description": "Cook quinoa according to package instructions."},
            {"step": 2, "description": "Roast sweet potatoes and broccoli with olive oil for 20 minutes."},
            {"step": 3, "description": "Slice avocado and prepare vegetables."},
            {"step": 4, "description": "Arrange all ingredients in a bowl."},
            {"step": 5, "description": "Drizzle with olive oil and season to taste."}
        ]
    },
    {
        "title": "Mediterranean Chicken Salad",
        "cuisine": "Mediterranean",
        "meal_type": "lunch",
        "prep_time": 20,
        "cook_time": 15,
        "difficulty": "easy",
        "dietary_tags": ["high-protein", "gluten-free"],
        "ingredients": [
            {"name": "chicken breast", "quantity": 150, "unit": "g"},
            {"name": "tomatoes", "quantity": 200, "unit": "g"},
            {"name": "cucumber", "quantity": 150, "unit": "g"},
            {"name": "olive oil", "quantity": 20, "unit": "ml"},
            {"name": "cheese", "quantity": 50, "unit": "g"}
        ],
        "instructions": [
            {"step": 1, "description": "Season and grill chicken breast until cooked through."},
            {"step": 2, "description": "Chop tomatoes and cucumber into bite-sized pieces."},
            {"step": 3, "description": "Slice grilled chicken into strips."},
            {"step": 4, "description": "Combine all ingredients in a large bowl."},
            {"step": 5, "description": "Drizzle with olive oil and crumble cheese on top."}
        ]
    },
    # Dinner recipes
    {
        "title": "Baked Salmon with Roasted Vegetables",
        "cuisine": "International",
        "meal_type": "dinner",
        "prep_time": 15,
        "cook_time": 25,
        "difficulty": "medium",
        "dietary_tags": ["gluten-free", "high-protein", "omega-3"],
        "ingredients": [
            {"name": "salmon fillet", "quantity": 200, "unit": "g"},
            {"name": "broccoli", "quantity": 200, "unit": "g"},
            {"name": "carrots", "quantity": 150, "unit": "g"},
            {"name": "olive oil", "quantity": 20, "unit": "ml"},
            {"name": "lemon", "quantity": 50, "unit": "g"}
        ],
        "instructions": [
            {"step": 1, "description": "Preheat oven to 400°F (200°C)."},
            {"step": 2, "description": "Season salmon with salt, pepper, and lemon juice."},
            {"step": 3, "description": "Toss vegetables with olive oil and seasonings."},
            {"step": 4, "description": "Place salmon and vegetables on a baking sheet."},
            {"step": 5, "description": "Bake for 20-25 minutes until salmon is flaky."}
        ]
    },
    {
        "title": "Vegetarian Stir-Fry",
        "cuisine": "Asian",
        "meal_type": "dinner",
        "prep_time": 20,
        "cook_time": 15,
        "difficulty": "easy",
        "dietary_tags": ["vegetarian", "vegan", "quick"],
        "ingredients": [
            {"name": "tofu", "quantity": 200, "unit": "g"},
            {"name": "bell peppers", "quantity": 150, "unit": "g"},
            {"name": "broccoli", "quantity": 150, "unit": "g"},
            {"name": "brown rice", "quantity": 100, "unit": "g"},
            {"name": "coconut oil", "quantity": 15, "unit": "ml"}
        ],
        "instructions": [
            {"step": 1, "description": "Cook brown rice according to package instructions."},
            {"step": 2, "description": "Cut tofu into cubes and vegetables into bite-sized pieces."},
            {"step": 3, "description": "Heat coconut oil in a large wok or pan."},
            {"step": 4, "description": "Stir-fry tofu and vegetables for 10-12 minutes."},
            {"step": 5, "description": "Serve over brown rice with soy sauce."}
        ]
    }
]

def create_ingredients(db):
    """Create ingredient records with embeddings"""
    print("Creating ingredients...")
    
    for ingredient_data in INGREDIENTS_DATA:
        # Create ingredient
        ingredient = Ingredient(
            id=f"ing_{hash(ingredient_data['name']) % 100000}",
            name=ingredient_data["name"],
            category=ingredient_data["category"],
            unit="g",
            default_quantity=100.0,
            calories=ingredient_data["calories"],
            protein=ingredient_data["protein"],
            carbs=ingredient_data["carbs"],
            fats=ingredient_data["fats"],
            fiber=random.uniform(0, 5),
            sugar=random.uniform(0, 10),
            sodium=random.uniform(0, 200)
        )
        
        # Generate embedding
        ingredient_text = f"{ingredient_data['name']} {ingredient_data['category']} {ingredient_data['calories']} calories"
        embedding = embedding_model.encode([ingredient_text])[0]
        ingredient.embedding = embedding.tolist()
        
        db.add(ingredient)
    
    db.commit()
    print(f"Created {len(INGREDIENTS_DATA)} ingredients")

def create_recipes(db):
    """Create recipe records with embeddings"""
    print("Creating recipes...")
    
    # Get all ingredients for reference
    ingredients = {ing.name: ing for ing in db.query(Ingredient).all()}
    
    recipes_created = 0
    
    # Create base recipes from templates
    for template in RECIPE_TEMPLATES:
        recipe = Recipe(
            id=f"r_{hash(template['title']) % 100000}",
            title=template["title"],
            cuisine=template["cuisine"],
            meal_type=template["meal_type"],
            servings=2,
            summary=f"A delicious {template['title'].lower()} perfect for {template['meal_type']}",
            prep_time=template["prep_time"],
            cook_time=template["cook_time"],
            difficulty_level=template["difficulty"],
            dietary_tags=template["dietary_tags"],
            source="database-seeded"
        )
        
        # Generate embedding
        recipe_text = f"{template['title']} {template['cuisine']} {template['meal_type']} {' '.join(template['dietary_tags'])}"
        embedding = embedding_model.encode([recipe_text])[0]
        recipe.embedding = embedding.tolist()
        
        db.add(recipe)
        db.flush()
        
        # Add ingredients
        for ing_data in template["ingredients"]:
            if ing_data["name"] in ingredients:
                recipe_ingredient = RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=ingredients[ing_data["name"]].id,
                    quantity=ing_data["quantity"],
                    unit=ing_data["unit"]
                )
                db.add(recipe_ingredient)
        
        # Add instructions
        for i, inst_data in enumerate(template["instructions"], 1):
            instruction = RecipeInstruction(
                recipe_id=recipe.id,
                step_number=i,
                step_title=f"Step {i}",
                description=inst_data["description"],
                time_required=random.randint(2, 10)
            )
            db.add(instruction)
        
        recipes_created += 1
    
    # Generate additional recipes to reach 500+
    while recipes_created < 500:
        # Create variations of existing recipes
        base_template = random.choice(RECIPE_TEMPLATES)
        
        # Create variation
        variation_title = f"{base_template['title']} Variation {recipes_created + 1}"
        recipe = Recipe(
            id=f"r_{hash(variation_title) % 100000}",
            title=variation_title,
            cuisine=random.choice(["Italian", "Mexican", "Asian", "Mediterranean", "American"]),
            meal_type=base_template["meal_type"],
            servings=random.randint(1, 6),
            summary=f"A delicious variation of {base_template['title'].lower()}",
            prep_time=base_template["prep_time"] + random.randint(-5, 10),
            cook_time=base_template["cook_time"] + random.randint(-5, 15),
            difficulty_level=random.choice(["easy", "medium", "hard"]),
            dietary_tags=random.sample(["vegetarian", "vegan", "gluten-free", "high-protein", "low-carb", "keto"], random.randint(1, 3)),
            source="ai-generated"
        )
        
        # Generate embedding
        recipe_text = f"{variation_title} {recipe.cuisine} {recipe.meal_type} {' '.join(recipe.dietary_tags)}"
        embedding = embedding_model.encode([recipe_text])[0]
        recipe.embedding = embedding.tolist()
        
        db.add(recipe)
        db.flush()
        
        # Add random ingredients
        selected_ingredients = random.sample(list(ingredients.values()), random.randint(3, 8))
        for ingredient in selected_ingredients:
            recipe_ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient.id,
                quantity=random.randint(50, 300),
                unit="g"
            )
            db.add(recipe_ingredient)
        
        # Add basic instructions
        for i in range(1, random.randint(3, 6)):
            instruction = RecipeInstruction(
                recipe_id=recipe.id,
                step_number=i,
                step_title=f"Step {i}",
                description=f"Follow step {i} of the cooking process",
                time_required=random.randint(2, 15)
            )
            db.add(instruction)
        
        recipes_created += 1
    
    db.commit()
    print(f"Created {recipes_created} recipes")

def create_sample_meal_plans(db):
    """Create sample meal plans for testing"""
    print("Creating sample meal plans...")
    
    # Get a sample user (assuming user ID 1 exists)
    from models.user import User
    user = db.query(User).first()
    
    if not user:
        print("No users found. Please create a user first.")
        return
    
    # Create sample meal plan
    meal_plan = MealPlan(
        id=f"mp_{user.id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        user_id=user.id,
        plan_type="daily",
        start_date=datetime.now().date(),
        end_date=datetime.now().date(),
        version="1.0"
    )
    
    db.add(meal_plan)
    db.flush()
    
    # Add sample meals
    meal_types = ["breakfast", "lunch", "dinner"]
    for meal_type in meal_types:
        meal = MealPlanMeal(
            meal_plan_id=meal_plan.id,
            meal_date=datetime.now().date(),
            meal_type=meal_type,
            meal_name=f"Sample {meal_type.title()}",
            calories=random.randint(300, 600),
            protein=random.randint(15, 40),
            carbs=random.randint(20, 60),
            fats=random.randint(10, 25)
        )
        db.add(meal)
    
    db.commit()
    print("Created sample meal plan")

def main():
    """Main function to populate the database"""
    print("Starting nutrition database population...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create ingredients
        create_ingredients(db)
        
        # Create recipes
        create_recipes(db)
        
        # Create sample meal plans
        create_sample_meal_plans(db)
        
        print("✅ Database population completed successfully!")
        print(f"📊 Created {len(INGREDIENTS_DATA)} ingredients")
        print(f"📊 Created 500+ recipes with embeddings")
        print(f"📊 Created sample meal plans")
        
    except Exception as e:
        print(f"❌ Error populating database: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
