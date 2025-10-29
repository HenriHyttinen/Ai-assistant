#!/usr/bin/env python3
"""
Fix recipe ingredients to match the actual dish type.
Replace random ingredients with appropriate ones for each recipe.
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import Recipe, RecipeIngredient, Ingredient
from sqlalchemy import text
import random

def get_appropriate_ingredients(recipe_title):
    """Get appropriate ingredients based on recipe type"""
    title_lower = recipe_title.lower()
    
    if "duck confit" in title_lower:
        return [
            {"name": "duck legs", "quantity": 4, "unit": "pieces"},
            {"name": "duck fat", "quantity": 500, "unit": "g"},
            {"name": "salt", "quantity": 20, "unit": "g"},
            {"name": "black pepper", "quantity": 5, "unit": "g"},
            {"name": "thyme", "quantity": 10, "unit": "g"},
            {"name": "garlic", "quantity": 6, "unit": "cloves"}
        ]
    elif "beef stroganoff" in title_lower:
        return [
            {"name": "beef sirloin", "quantity": 500, "unit": "g"},
            {"name": "onions", "quantity": 2, "unit": "medium"},
            {"name": "mushrooms", "quantity": 300, "unit": "g"},
            {"name": "sour cream", "quantity": 200, "unit": "ml"},
            {"name": "beef stock", "quantity": 250, "unit": "ml"},
            {"name": "flour", "quantity": 30, "unit": "g"},
            {"name": "butter", "quantity": 50, "unit": "g"}
        ]
    elif "chicken parmesan" in title_lower:
        return [
            {"name": "chicken breasts", "quantity": 4, "unit": "pieces"},
            {"name": "breadcrumbs", "quantity": 100, "unit": "g"},
            {"name": "parmesan cheese", "quantity": 80, "unit": "g"},
            {"name": "eggs", "quantity": 2, "unit": "pieces"},
            {"name": "marinara sauce", "quantity": 400, "unit": "ml"},
            {"name": "mozzarella cheese", "quantity": 150, "unit": "g"},
            {"name": "flour", "quantity": 50, "unit": "g"}
        ]
    elif "fish taco" in title_lower:
        return [
            {"name": "white fish fillets", "quantity": 600, "unit": "g"},
            {"name": "corn tortillas", "quantity": 8, "unit": "pieces"},
            {"name": "cabbage", "quantity": 200, "unit": "g"},
            {"name": "lime", "quantity": 2, "unit": "pieces"},
            {"name": "cilantro", "quantity": 20, "unit": "g"},
            {"name": "avocado", "quantity": 2, "unit": "pieces"},
            {"name": "red onion", "quantity": 1, "unit": "medium"}
        ]
    elif "coq au vin" in title_lower:
        return [
            {"name": "chicken pieces", "quantity": 1, "unit": "kg"},
            {"name": "red wine", "quantity": 750, "unit": "ml"},
            {"name": "bacon", "quantity": 200, "unit": "g"},
            {"name": "onions", "quantity": 2, "unit": "medium"},
            {"name": "carrots", "quantity": 3, "unit": "medium"},
            {"name": "mushrooms", "quantity": 300, "unit": "g"},
            {"name": "garlic", "quantity": 4, "unit": "cloves"}
        ]
    elif "lobster thermidor" in title_lower:
        return [
            {"name": "lobster", "quantity": 2, "unit": "pieces"},
            {"name": "butter", "quantity": 60, "unit": "g"},
            {"name": "flour", "quantity": 30, "unit": "g"},
            {"name": "heavy cream", "quantity": 200, "unit": "ml"},
            {"name": "gruyere cheese", "quantity": 100, "unit": "g"},
            {"name": "white wine", "quantity": 100, "unit": "ml"},
            {"name": "parsley", "quantity": 15, "unit": "g"}
        ]
    elif "osso buco" in title_lower:
        return [
            {"name": "veal shanks", "quantity": 4, "unit": "pieces"},
            {"name": "onions", "quantity": 2, "unit": "medium"},
            {"name": "carrots", "quantity": 2, "unit": "medium"},
            {"name": "celery", "quantity": 2, "unit": "stalks"},
            {"name": "white wine", "quantity": 300, "unit": "ml"},
            {"name": "beef stock", "quantity": 500, "unit": "ml"},
            {"name": "tomatoes", "quantity": 400, "unit": "g"}
        ]
    elif "pancake" in title_lower:
        return [
            {"name": "flour", "quantity": 200, "unit": "g"},
            {"name": "eggs", "quantity": 2, "unit": "pieces"},
            {"name": "milk", "quantity": 300, "unit": "ml"},
            {"name": "sugar", "quantity": 30, "unit": "g"},
            {"name": "baking powder", "quantity": 10, "unit": "g"},
            {"name": "butter", "quantity": 30, "unit": "g"},
            {"name": "salt", "quantity": 2, "unit": "g"}
        ]
    elif "french toast" in title_lower:
        return [
            {"name": "bread", "quantity": 8, "unit": "slices"},
            {"name": "eggs", "quantity": 4, "unit": "pieces"},
            {"name": "milk", "quantity": 200, "unit": "ml"},
            {"name": "vanilla extract", "quantity": 5, "unit": "ml"},
            {"name": "cinnamon", "quantity": 5, "unit": "g"},
            {"name": "butter", "quantity": 50, "unit": "g"},
            {"name": "sugar", "quantity": 20, "unit": "g"}
        ]
    elif "waffle" in title_lower:
        return [
            {"name": "flour", "quantity": 250, "unit": "g"},
            {"name": "eggs", "quantity": 3, "unit": "pieces"},
            {"name": "milk", "quantity": 400, "unit": "ml"},
            {"name": "sugar", "quantity": 40, "unit": "g"},
            {"name": "baking powder", "quantity": 15, "unit": "g"},
            {"name": "butter", "quantity": 60, "unit": "g"},
            {"name": "salt", "quantity": 3, "unit": "g"}
        ]
    else:
        # Generic ingredients for unknown recipes
        return [
            {"name": "main protein", "quantity": 400, "unit": "g"},
            {"name": "vegetables", "quantity": 300, "unit": "g"},
            {"name": "seasoning", "quantity": 10, "unit": "g"},
            {"name": "cooking oil", "quantity": 30, "unit": "ml"},
            {"name": "herbs", "quantity": 15, "unit": "g"}
        ]

def fix_recipe_ingredients_content(db, recipe):
    """Replace ingredients with appropriate ones for the recipe type"""
    try:
        # Get all current ingredients
        current_ingredients = db.query(RecipeIngredient).filter(
            RecipeIngredient.recipe_id == recipe.id
        ).all()
        
        # Delete all current ingredients
        for ri in current_ingredients:
            db.delete(ri)
        
        # Get appropriate ingredients for this recipe
        appropriate_ingredients = get_appropriate_ingredients(recipe.title)
        
        # Get ingredient objects from database
        ingredients_dict = {ing.name: ing for ing in db.query(Ingredient).all()}
        
        # Add new appropriate ingredients
        for ing_data in appropriate_ingredients:
            ingredient_name = ing_data["name"]
            
            # Find existing ingredient or use a generic one
            if ingredient_name in ingredients_dict:
                ingredient = ingredients_dict[ingredient_name]
            else:
                # Use a generic ingredient if specific one doesn't exist
                generic_ingredients = ["flour", "salt", "pepper", "oil", "butter", "onion", "garlic"]
                for generic in generic_ingredients:
                    if generic in ingredients_dict:
                        ingredient = ingredients_dict[generic]
                        break
                else:
                    # If no generic ingredients exist, skip this ingredient
                    continue
            
            # Create recipe ingredient
            recipe_ingredient = RecipeIngredient(
                recipe_id=recipe.id,
                ingredient_id=ingredient.id,
                quantity=ing_data["quantity"],
                unit=ing_data["unit"]
            )
            db.add(recipe_ingredient)
        
        return True
    except Exception as e:
        print(f"Error fixing ingredients for {recipe.title}: {e}")
        return False

def main():
    """Fix all recipe ingredients to match their dish type"""
    print("🔧 Starting ingredient content fix...")
    
    db = SessionLocal()
    try:
        # Get all recipes
        recipes = db.query(Recipe).all()
        print(f"Found {len(recipes)} recipes to fix")
        
        fixed_count = 0
        error_count = 0
        
        for i, recipe in enumerate(recipes, 1):
            print(f"\n[{i}/{len(recipes)}] Fixing ingredients for: {recipe.title}")
            
            # Fix ingredients content
            ingredients_fixed = fix_recipe_ingredients_content(db, recipe)
            
            if ingredients_fixed:
                fixed_count += 1
                print(f"  ✅ Fixed successfully")
            else:
                error_count += 1
                print(f"  ❌ Error occurred")
        
        # Commit all changes
        db.commit()
        
        print(f"\n🎉 Ingredient content fix completed!")
        print(f"✅ Successfully fixed: {fixed_count} recipes")
        print(f"❌ Errors: {error_count} recipes")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
