#!/usr/bin/env python3
"""
Add Recipe Instructions
Adds proper cooking instructions to all recipes that are missing them.
"""

import sys
import os
sys.path.append('.')

from database import SessionLocal
from models.recipe import Recipe, RecipeInstruction

def add_recipe_instructions():
    """Add instructions to all recipes"""
    print("🍳 Adding Recipe Instructions...")
    
    db = SessionLocal()
    try:
        # Get all recipes
        recipes = db.query(Recipe).all()
        
        for recipe in recipes:
            # Check if recipe already has instructions
            existing_instructions = db.query(RecipeInstruction).filter(
                RecipeInstruction.recipe_id == recipe.id
            ).count()
            
            if existing_instructions > 0:
                print(f"✅ {recipe.title} already has {existing_instructions} instructions")
                continue
            
            print(f"📝 Adding instructions for {recipe.title}")
            
            # Add instructions based on recipe title
            if "Quinoa Buddha Bowl" in recipe.title:
                instructions = [
                    (1, "Cook Quinoa", "Rinse quinoa and cook according to package instructions until fluffy.", 15),
                    (2, "Prepare Vegetables", "Steam broccoli until tender-crisp, about 5 minutes.", 5),
                    (3, "Slice Avocado", "Cut avocado into thin slices and drizzle with lemon juice.", 2),
                    (4, "Assemble Bowl", "Layer quinoa, broccoli, and avocado in a bowl.", 2),
                    (5, "Season and Serve", "Drizzle with olive oil, season with salt and pepper, and serve.", 1)
                ]
            elif "Baked Salmon" in recipe.title:
                instructions = [
                    (1, "Preheat Oven", "Preheat oven to 400°F (200°C).", 5),
                    (2, "Prepare Salmon", "Season salmon fillet with salt, pepper, and herbs.", 3),
                    (3, "Prepare Vegetables", "Cut broccoli into florets and toss with olive oil.", 5),
                    (4, "Bake", "Place salmon and broccoli on a baking sheet and bake for 15-20 minutes.", 20),
                    (5, "Serve", "Remove from oven and serve immediately with lemon wedges.", 2)
                ]
            elif "Mediterranean Omelet" in recipe.title:
                instructions = [
                    (1, "Heat Pan", "Heat olive oil in a non-stick pan over medium heat.", 2),
                    (2, "Beat Eggs", "Beat eggs in a bowl and season with salt and pepper.", 3),
                    (3, "Cook Vegetables", "Add tomatoes and spinach to the pan, cook for 2 minutes.", 2),
                    (4, "Add Eggs", "Pour beaten eggs over vegetables and cook until set.", 5),
                    (5, "Fold and Serve", "Fold omelet in half and serve immediately.", 1)
                ]
            elif "Protein Power Smoothie" in recipe.title:
                instructions = [
                    (1, "Add Ingredients", "Add all ingredients to a blender.", 1),
                    (2, "Blend", "Blend on high speed for 1-2 minutes until smooth.", 2),
                    (3, "Taste", "Taste and adjust sweetness if needed.", 1),
                    (4, "Serve", "Pour into a glass and serve immediately.", 1)
                ]
            elif "Vegetarian Stir-Fry" in recipe.title:
                instructions = [
                    (1, "Heat Oil", "Heat oil in a large wok or skillet over high heat.", 2),
                    (2, "Add Vegetables", "Add vegetables and stir-fry for 3-4 minutes.", 4),
                    (3, "Add Sauce", "Add sauce and continue stir-frying for 1-2 minutes.", 2),
                    (4, "Season", "Season with salt, pepper, and herbs to taste.", 1),
                    (5, "Serve", "Serve immediately over rice or noodles.", 1)
                ]
            else:
                # Generic instructions for any other recipes
                instructions = [
                    (1, "Prepare Ingredients", "Gather and prepare all ingredients as needed.", 5),
                    (2, "Cook", "Follow the main cooking method for this recipe.", 15),
                    (3, "Season", "Season with salt, pepper, and herbs to taste.", 2),
                    (4, "Serve", "Plate and serve immediately.", 1)
                ]
            
            # Add instructions to database
            for step_num, title, description, time_required in instructions:
                instruction = RecipeInstruction(
                    recipe_id=recipe.id,
                    step_number=step_num,
                    step_title=title,
                    description=description,
                    time_required=time_required
                )
                db.add(instruction)
            
            print(f"  ✅ Added {len(instructions)} instructions")
        
        db.commit()
        print("🎉 All recipe instructions added successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    add_recipe_instructions()










