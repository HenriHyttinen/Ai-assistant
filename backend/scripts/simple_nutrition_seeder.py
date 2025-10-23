#!/usr/bin/env python3
"""
Simple Nutrition Database Seeder

This script creates basic nutrition data without heavy ML dependencies.
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal, engine
from models.recipe import Recipe, Ingredient, RecipeIngredient, RecipeInstruction
from models.nutrition import (
    UserNutritionPreferences, MealPlan, MealPlanMeal, MealPlanRecipe,
    NutritionalLog, ShoppingList, ShoppingListItem
)
from models.base import Base
from models.user import User

# Simple ingredients data
SIMPLE_INGREDIENTS = [
    {"name": "chicken breast", "category": "protein", "calories": 165, "protein": 31, "carbs": 0, "fats": 3.6},
    {"name": "salmon fillet", "category": "protein", "calories": 208, "protein": 25, "carbs": 0, "fats": 12},
    {"name": "eggs", "category": "protein", "calories": 155, "protein": 13, "carbs": 1.1, "fats": 11},
    {"name": "brown rice", "category": "grains", "calories": 111, "protein": 2.6, "carbs": 23, "fats": 0.9},
    {"name": "quinoa", "category": "grains", "calories": 120, "protein": 4.4, "carbs": 22, "fats": 1.9},
    {"name": "oats", "category": "grains", "calories": 68, "protein": 2.4, "carbs": 12, "fats": 1.4},
    {"name": "broccoli", "category": "vegetables", "calories": 34, "protein": 2.8, "carbs": 7, "fats": 0.4},
    {"name": "spinach", "category": "vegetables", "calories": 23, "protein": 2.9, "carbs": 3.6, "fats": 0.4},
    {"name": "tomatoes", "category": "vegetables", "calories": 18, "protein": 0.9, "carbs": 3.9, "fats": 0.2},
    {"name": "olive oil", "category": "fats", "calories": 884, "protein": 0, "carbs": 0, "fats": 100},
    {"name": "avocados", "category": "fruits", "calories": 160, "protein": 2, "carbs": 9, "fats": 15},
    {"name": "bananas", "category": "fruits", "calories": 89, "protein": 1.1, "carbs": 23, "fats": 0.3},
    {"name": "greek yogurt", "category": "dairy", "calories": 59, "protein": 10, "carbs": 3.6, "fats": 0.4},
    {"name": "cheese", "category": "dairy", "calories": 113, "protein": 7, "carbs": 1, "fats": 9},
    {"name": "almonds", "category": "fats", "calories": 579, "protein": 21, "carbs": 22, "fats": 50},
]

# Simple recipe templates
SIMPLE_RECIPES = [
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
            "Heat olive oil in a non-stick pan over medium heat.",
            "Beat eggs in a bowl and season with salt and pepper.",
            "Add tomatoes and spinach to the pan, cook for 2 minutes.",
            "Pour beaten eggs over vegetables and cook until set.",
            "Sprinkle cheese on top and fold omelet in half."
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
            {"name": "oats", "quantity": 30, "unit": "g"},
            {"name": "almonds", "quantity": 20, "unit": "g"}
        ],
        "instructions": [
            "Add all ingredients to a blender.",
            "Blend on high speed for 1-2 minutes until smooth.",
            "Taste and adjust sweetness if needed.",
            "Pour into a glass and serve immediately."
        ]
    },
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
            {"name": "broccoli", "quantity": 150, "unit": "g"},
            {"name": "avocados", "quantity": 100, "unit": "g"},
            {"name": "olive oil", "quantity": 15, "unit": "ml"}
        ],
        "instructions": [
            "Cook quinoa according to package instructions.",
            "Steam broccoli until tender.",
            "Slice avocado and prepare vegetables.",
            "Arrange all ingredients in a bowl.",
            "Drizzle with olive oil and season to taste."
        ]
    },
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
            {"name": "olive oil", "quantity": 20, "unit": "ml"}
        ],
        "instructions": [
            "Preheat oven to 400°F (200°C).",
            "Season salmon with salt, pepper, and olive oil.",
            "Toss broccoli with olive oil and seasonings.",
            "Place salmon and vegetables on a baking sheet.",
            "Bake for 20-25 minutes until salmon is flaky."
        ]
    }
]

def create_ingredients(db):
    """Create ingredient records"""
    print("Creating ingredients...")
    
    for ingredient_data in SIMPLE_INGREDIENTS:
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
        db.add(ingredient)
    
    db.commit()
    print(f"✅ Created {len(SIMPLE_INGREDIENTS)} ingredients")

def create_recipes(db):
    """Create recipe records"""
    print("Creating recipes...")
    
    # Get all ingredients for reference
    ingredients = {ing.name: ing for ing in db.query(Ingredient).all()}
    
    recipes_created = 0
    
    # Create base recipes
    for template in SIMPLE_RECIPES:
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
        for i, instruction_text in enumerate(template["instructions"], 1):
            instruction = RecipeInstruction(
                recipe_id=recipe.id,
                step_number=i,
                step_title=f"Step {i}",
                description=instruction_text,
                time_required=random.randint(2, 10)
            )
            db.add(instruction)
        
        recipes_created += 1
    
    # Generate additional recipes to reach 50+ (simpler than 500+)
    while recipes_created < 50:
        base_template = random.choice(SIMPLE_RECIPES)
        
        variation_title = f"{base_template['title']} Variation {recipes_created + 1}"
        recipe = Recipe(
            id=f"r_{hash(variation_title) % 100000}",
            title=variation_title,
            cuisine=random.choice(["Italian", "Mexican", "Asian", "Mediterranean", "American"]),
            meal_type=base_template["meal_type"],
            servings=random.randint(1, 4),
            summary=f"A delicious variation of {base_template['title'].lower()}",
            prep_time=base_template["prep_time"] + random.randint(-5, 10),
            cook_time=base_template["cook_time"] + random.randint(-5, 15),
            difficulty_level=random.choice(["easy", "medium", "hard"]),
            dietary_tags=random.sample(["vegetarian", "vegan", "gluten-free", "high-protein", "low-carb"], random.randint(1, 3)),
            source="ai-generated"
        )
        
        db.add(recipe)
        db.flush()
        
        # Add random ingredients
        selected_ingredients = random.sample(list(ingredients.values()), random.randint(3, 6))
        for ingredient in selected_ingredients:
            recipe_ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient.id,
                quantity=random.randint(50, 200),
                unit="g"
            )
            db.add(recipe_ingredient)
        
        # Add basic instructions
        for i in range(1, random.randint(3, 5)):
            instruction = RecipeInstruction(
                recipe_id=recipe.id,
                step_number=i,
                step_title=f"Step {i}",
                description=f"Follow step {i} of the cooking process",
                time_required=random.randint(2, 10)
            )
            db.add(instruction)
        
        recipes_created += 1
    
    db.commit()
    print(f"✅ Created {recipes_created} recipes")

def create_sample_data(db):
    """Create sample user preferences and meal plans"""
    print("Creating sample data...")
    
    # Get a sample user (assuming user ID 1 exists)
    user = db.query(User).first()
    
    if not user:
        print("⚠️  No users found. Creating sample user...")
        # Create a sample user for testing
        user = User(
            email="test@example.com",
            hashed_password="hashed_password",
            is_active=True,
            is_verified=True
        )
        db.add(user)
        db.flush()
    
    # Create sample nutrition preferences
    preferences = UserNutritionPreferences(
        user_id=user.id,
        dietary_preferences=["vegetarian", "gluten-free"],
        allergies=["nuts"],
        disliked_ingredients=["mushrooms"],
        cuisine_preferences=["Mediterranean", "Italian"],
        daily_calorie_target=2000,
        protein_target=100,
        carbs_target=200,
        fats_target=60,
        meals_per_day=3,
        preferred_meal_times={
            "breakfast": "08:00",
            "lunch": "12:30",
            "dinner": "19:00"
        },
        timezone="UTC"
    )
    db.add(preferences)
    
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
    print("✅ Created sample user data")

def main():
    """Main function to populate the database"""
    print("🚀 Starting simple nutrition database population...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create ingredients
        create_ingredients(db)
        
        # Create recipes
        create_recipes(db)
        
        # Create sample data
        create_sample_data(db)
        
        print("🎉 Database population completed successfully!")
        print("📊 Summary:")
        print(f"   - {len(SIMPLE_INGREDIENTS)} ingredients created")
        print(f"   - 50+ recipes created")
        print(f"   - Sample user preferences created")
        print(f"   - Sample meal plan created")
        print("\n🔗 Next steps:")
        print("   1. Test the API endpoints")
        print("   2. Verify frontend integration")
        print("   3. Add more recipes as needed")
        
    except Exception as e:
        print(f"❌ Error populating database: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()
