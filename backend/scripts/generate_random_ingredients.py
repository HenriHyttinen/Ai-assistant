#!/usr/bin/env python3
"""
Generate random ingredients to reach 500+
"""
import sys
import os
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from sqlalchemy import text

# Categories and their typical nutritional profiles
CATEGORIES = {
    "protein": {"calories": (100, 300), "protein": (15, 35), "carbs": (0, 5), "fats": (1, 20)},
    "dairy": {"calories": (50, 400), "protein": (3, 25), "carbs": (1, 10), "fats": (1, 35)},
    "grains": {"calories": (100, 400), "protein": (2, 15), "carbs": (20, 80), "fats": (0, 10)},
    "vegetables": {"calories": (10, 100), "protein": (1, 5), "carbs": (2, 25), "fats": (0, 2)},
    "fruits": {"calories": (30, 200), "protein": (0, 3), "carbs": (8, 50), "fats": (0, 5)},
    "nuts": {"calories": (400, 800), "protein": (8, 35), "carbs": (10, 50), "fats": (30, 80)},
    "legumes": {"calories": (100, 200), "protein": (6, 25), "carbs": (15, 60), "fats": (0, 10)},
    "fats": {"calories": (800, 900), "protein": (0, 2), "carbs": (0, 5), "fats": (80, 100)},
    "herbs": {"calories": (20, 400), "protein": (2, 15), "carbs": (5, 80), "fats": (0, 15)},
    "spices": {"calories": (200, 400), "protein": (5, 20), "carbs": (40, 80), "fats": (1, 25)},
    "condiments": {"calories": (0, 700), "protein": (0, 5), "carbs": (0, 80), "fats": (0, 80)},
    "beverages": {"calories": (0, 50), "protein": (0, 5), "carbs": (0, 15), "fats": (0, 5)},
}

# Name generators for each category
NAME_GENERATORS = {
    "protein": ["chicken", "beef", "pork", "lamb", "fish", "salmon", "tuna", "shrimp", "crab", "lobster"],
    "dairy": ["cheese", "milk", "yogurt", "cream", "butter", "sour cream", "cottage cheese", "ricotta"],
    "grains": ["rice", "wheat", "oats", "barley", "quinoa", "buckwheat", "millet", "amaranth", "spelt"],
    "vegetables": ["broccoli", "carrots", "spinach", "kale", "onions", "garlic", "peppers", "tomatoes", "cucumber"],
    "fruits": ["apples", "bananas", "oranges", "berries", "grapes", "peaches", "pears", "plums", "cherries"],
    "nuts": ["almonds", "walnuts", "cashews", "pistachios", "pecans", "hazelnuts", "brazil nuts", "macadamia"],
    "legumes": ["beans", "lentils", "chickpeas", "peas", "soybeans", "tofu", "tempeh", "miso"],
    "fats": ["oil", "butter", "lard", "ghee", "margarine", "shortening", "tallow", "duck fat"],
    "herbs": ["basil", "oregano", "thyme", "rosemary", "sage", "parsley", "cilantro", "mint", "dill"],
    "spices": ["cinnamon", "ginger", "turmeric", "cumin", "coriander", "paprika", "pepper", "garlic powder"],
    "condiments": ["sauce", "vinegar", "mustard", "ketchup", "mayo", "relish", "chutney", "jam"],
    "beverages": ["tea", "coffee", "juice", "soda", "water", "milk", "broth", "soup"],
}

def generate_random_ingredients():
    """Generate random ingredients to reach 500+"""
    print("🥕 Generating random ingredients to reach 500+...")
    db = SessionLocal()
    try:
        # Get current count
        result = db.execute(text("SELECT COUNT(*) FROM ingredients"))
        current_count = result.scalar()
        print(f"Current ingredient count: {current_count}")
        
        # Generate ingredients until we reach 500+
        ingredients_to_add = 500 - current_count + 50  # Add extra to ensure we exceed 500
        
        for i in range(ingredients_to_add):
            # Random category
            category = random.choice(list(CATEGORIES.keys()))
            
            # Generate name
            base_name = random.choice(NAME_GENERATORS[category])
            modifiers = ["fresh", "dried", "frozen", "organic", "wild", "free-range", "grass-fed", "raw", "cooked", "smoked", "cured", "aged", "young", "mature", "ripe", "unripe"]
            modifier = random.choice(modifiers) if random.random() < 0.3 else ""
            name = f"{modifier} {base_name}".strip()
            
            # Generate nutritional values based on category
            profile = CATEGORIES[category]
            calories = random.uniform(*profile["calories"])
            protein = random.uniform(*profile["protein"])
            carbs = random.uniform(*profile["carbs"])
            fats = random.uniform(*profile["fats"])
            
            # Insert ingredient
            db.execute(text("""
                INSERT INTO ingredients (id, name, category, unit, default_quantity, calories, protein, carbs, fats, fiber, sugar, sodium, created_at, updated_at)
                VALUES (:id, :name, :category, :unit, :default_quantity, :calories, :protein, :carbs, :fats, :fiber, :sugar, :sodium, datetime('now'), datetime('now'))
            """), {
                "id": f"ing_{current_count + i + 1}",
                "name": name,
                "category": category,
                "unit": "g",
                "default_quantity": 100.0,
                "calories": round(calories, 1),
                "protein": round(protein, 1),
                "carbs": round(carbs, 1),
                "fats": round(fats, 1),
                "fiber": round(random.uniform(0, 15), 1),
                "sugar": round(random.uniform(0, 10), 1),
                "sodium": round(random.uniform(0, 200), 1)
            })
        
        db.commit()
        print(f"✅ Generated {ingredients_to_add} random ingredients")
        
        # Verify final count
        result = db.execute(text("SELECT COUNT(*) FROM ingredients"))
        final_count = result.scalar()
        print(f"Final ingredient count: {final_count}")
        
        if final_count >= 500:
            print("🎯 TARGET ACHIEVED: 500+ ingredients!")
        else:
            print(f"⚠️  Still need {500 - final_count} more ingredients")
            
    except Exception as e:
        print(f"❌ Error generating ingredients: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_random_ingredients()
