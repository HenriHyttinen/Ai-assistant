#!/usr/bin/env python3
"""
Replace Recipes Without Nutrition

This script:
1. Finds recipes without nutrition values
2. Deletes them from the database
3. Replaces them with recipes from SQLite that have proper nutrition values
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
from database import SessionLocal
from models.recipe import Recipe, RecipeIngredient, Ingredient, RecipeInstruction
import logging
import re
import uuid
import random
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecipeReplacer:
    def __init__(self):
        self.db = SessionLocal()
        # Try both possible locations
        sqlite_paths = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'recipes.sqlite3'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'recipes.sqlite3'),
            '../recipes.sqlite3',
            '../../recipes.sqlite3',
            'recipes.sqlite3'
        ]
        
        self.sqlite_conn = None
        self.sqlite_cursor = None
        
        for path in sqlite_paths:
            if os.path.exists(path):
                try:
                    self.sqlite_conn = sqlite3.connect(path)
        self.sqlite_cursor = self.sqlite_conn.cursor()
                    logger.info(f"✅ Connected to SQLite database: {path}")
                    break
                except Exception as e:
                    logger.warning(f"⚠️  Could not connect to {path}: {e}")
                    continue
        
        if not self.sqlite_conn:
            raise FileNotFoundError("Could not find recipes.sqlite3 database")
        
        self.deleted_count = 0
        self.imported_count = 0

    def normalize_title(self, title):
        """Normalize title for matching"""
        if not title:
            return ""
        # Remove extra whitespace, convert to lowercase
        title = re.sub(r'\s+', ' ', title.strip().lower())
        # Remove special characters for matching
        title = re.sub(r'[^\w\s]', '', title)
        return title
    
    def get_existing_titles(self):
        """Get all existing recipe titles to avoid duplicates"""
        existing = self.db.query(Recipe.title).all()
        return {self.normalize_title(title[0]) for title in existing}
    
    def find_recipes_without_nutrition(self):
        """Find recipes without nutrition values"""
        recipes = self.db.query(Recipe).filter(
            (Recipe.per_serving_calories.is_(None)) | 
            (Recipe.per_serving_calories == 0)
        ).all()
        
        logger.info(f"Found {len(recipes)} recipes without nutrition")
        return recipes
    
    def delete_recipe(self, recipe):
        """Delete a recipe and all its related data"""
        try:
            # Delete instructions
            self.db.query(RecipeInstruction).filter(
                RecipeInstruction.recipe_id == recipe.id
            ).delete()
            
            # Delete ingredients
            self.db.query(RecipeIngredient).filter(
                RecipeIngredient.recipe_id == recipe.id
            ).delete()
            
            # Delete recipe
            self.db.delete(recipe)
            
            self.deleted_count += 1
            logger.info(f"  ✅ Deleted: {recipe.title[:50]}")
            
        except Exception as e:
            logger.error(f"  ❌ Error deleting {recipe.title}: {e}")
            self.db.rollback()
            raise
    
    def get_replacement_recipes(self, count, existing_titles):
        """Get replacement recipes from SQLite that have nutrition and aren't duplicates"""
        self.sqlite_cursor.execute("""
            SELECT id, title, ingredients, directions, categories, calories, protein, fat, sodium, "desc", rating, image
            FROM recipes
            WHERE calories IS NOT NULL 
            AND calories >= 100 
            AND calories <= 800
            AND protein IS NOT NULL 
            AND protein > 0
            AND fat IS NOT NULL
            AND ingredients IS NOT NULL
            AND directions IS NOT NULL
            ORDER BY RANDOM()
        """)
        
        all_candidates = self.sqlite_cursor.fetchall()
        logger.info(f"Found {len(all_candidates)} candidate recipes in SQLite")
        
        # Filter out duplicates
        replacements = []
        for candidate in all_candidates:
            if len(replacements) >= count:
                break
            
            sqlite_id, title, ingredients, directions, categories, calories, protein, fat, sodium, desc, rating, image = candidate
            
            normalized_title = self.normalize_title(title)
            if normalized_title not in existing_titles:
                replacements.append(candidate)
                existing_titles.add(normalized_title)
        
        logger.info(f"Selected {len(replacements)} replacement recipes (avoiding duplicates)")
        return replacements
    
    def determine_cuisine(self, title, categories):
        """Determine cuisine from title and categories"""
        title_lower = title.lower()
        categories_lower = categories.lower() if categories else ""
        
        # French cuisine keywords
        if any(word in title_lower for word in ['french', 'coq au vin', 'ratatouille', 'bouillabaisse', 'cassoulet', 'tarte', 'crêpe', 'soufflé', 'confit', 'bourguignon']):
            return 'French'
        elif any(word in title_lower for word in ['italian', 'pasta', 'pizza', 'risotto', 'bruschetta', 'tiramisu', 'carbonara', 'parmigiana', 'bolognese']):
            return 'Italian'
        elif any(word in title_lower for word in ['mexican', 'taco', 'burrito', 'enchilada', 'quesadilla', 'guacamole', 'salsa', 'mole', 'pozole']):
            return 'Mexican'
        elif any(word in title_lower for word in ['chinese', 'stir-fry', 'lo mein', 'kung pao', 'sweet and sour', 'dim sum', 'wonton', 'dumpling']):
            return 'Chinese'
        elif any(word in title_lower for word in ['thai', 'pad thai', 'curry', 'tom yum', 'green curry', 'red curry', 'coconut', 'lemongrass']):
            return 'Thai'
        elif any(word in title_lower for word in ['japanese', 'sushi', 'ramen', 'teriyaki', 'miso', 'tempura', 'udon', 'soba']):
            return 'Japanese'
        elif any(word in title_lower for word in ['indian', 'curry', 'tikka', 'masala', 'biryani', 'dal', 'naan', 'tandoori']):
            return 'Indian'
        elif any(word in title_lower for word in ['greek', 'gyro', 'tzatziki', 'moussaka', 'baklava', 'feta', 'olive', 'oregano']):
            return 'Greek'
        elif any(word in title_lower for word in ['spanish', 'paella', 'tapas', 'gazpacho', 'chorizo', 'sangria', 'sherry']):
            return 'Spanish'
        elif any(word in title_lower for word in ['german', 'sauerkraut', 'bratwurst', 'schnitzel', 'pretzel', 'beer']):
            return 'German'
        elif any(word in title_lower for word in ['american', 'burger', 'barbecue', 'bbq', 'mac and cheese', 'apple pie', 'cobbler']):
            return 'American'
        elif any(word in title_lower for word in ['mediterranean', 'olive', 'hummus', 'falafel', 'tabbouleh', 'pita']):
            return 'Mediterranean'
        else:
            return 'International'
    
    def determine_meal_type(self, title, categories):
        """Determine meal type from title and categories"""
        title_lower = title.lower()
        categories_lower = categories.lower() if categories else ""
        
        if any(word in title_lower for word in ['breakfast', 'pancake', 'waffle', 'omelet', 'eggs', 'cereal', 'toast', 'bagel']):
            return 'breakfast'
        elif any(word in title_lower for word in ['lunch', 'sandwich', 'wrap', 'salad', 'soup']):
            return 'lunch'
        elif any(word in title_lower for word in ['dinner', 'steak', 'roast', 'casserole', 'lasagna', 'pasta', 'risotto']):
            return 'dinner'
        elif any(word in title_lower for word in ['snack', 'cookie', 'brownie', 'muffin', 'bar', 'trail mix']):
            return 'snack'
        elif any(word in title_lower for word in ['dessert', 'cake', 'pie', 'tart', 'ice cream', 'pudding']):
            return 'snack'
        else:
            return 'lunch'
    
    def estimate_servings(self, title, ingredients_text):
        """Estimate servings from title and ingredients"""
        title_lower = title.lower()
        ingredients_lower = ingredients_text.lower() if ingredients_text else ""
        
        # Keywords that suggest serving size
        if any(word in title_lower for word in ['for 4', 'serves 4', '4 servings']):
            return 4
        elif any(word in title_lower for word in ['for 6', 'serves 6', '6 servings']):
            return 6
        elif any(word in title_lower for word in ['for 2', 'serves 2', '2 servings']):
            return 2
        elif any(word in title_lower for word in ['for 8', 'serves 8', '8 servings']):
            return 8
        
        # Estimate from ingredients
        if not ingredients_text:
            return 4
        
        # Count common serving indicators
        ingredient_count = len(re.split(r'[,;]\s*', ingredients_text))
        
        if ingredient_count < 5:
            return 2
        elif ingredient_count < 10:
            return 4
        elif ingredient_count < 15:
            return 6
        else:
            return 8

    def parse_ingredients_properly(self, ingredients_text):
        """Parse ingredients with proper unit conversion"""
        if not ingredients_text:
            return []
        
        ingredients = []
        lines = re.split(r'[,;]\s*', ingredients_text)
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 3:
                continue
                
            # Try to extract quantity and unit
            match = re.match(r'^([\d./]+)\s*(\w+)?\s*(.+)$', line)
            if match:
                qty_str, unit, name = match.groups()
                
                # Parse quantity
                try:
                    if '/' in qty_str:
                        parts = qty_str.split()
                        if len(parts) == 2:
                            whole, frac = parts
                            whole = float(whole) if whole else 0
                            num, den = frac.split('/')
                            quantity = whole + (float(num) / float(den))
                        else:
                            num, den = qty_str.split('/')
                            quantity = float(num) / float(den)
                    else:
                        quantity = float(qty_str)
                except:
                    quantity = 1
                
                # Convert units to grams/ml
                if unit:
                    unit_lower = unit.lower()
                    if unit_lower in ['oz', 'ounce', 'ounces']:
                        quantity = quantity * 28.35
                        unit = 'g'
                    elif unit_lower in ['lb', 'lbs', 'pound', 'pounds']:
                        quantity = quantity * 453.6
                        unit = 'g'
                    elif unit_lower in ['cup', 'cups']:
                        quantity = quantity * 240
                        unit = 'ml'
                    elif unit_lower in ['tbsp', 'tablespoon', 'tablespoons']:
                        quantity = quantity * 15
                        unit = 'ml'
                    elif unit_lower in ['tsp', 'teaspoon', 'teaspoons']:
                        quantity = quantity * 5
                        unit = 'ml'
                    else:
                        unit = 'g'  # Default to grams
                    else:
                        unit = 'g'
                
                name = name.strip()
                ingredients.append({
                    'name': name,
                    'quantity': round(quantity, 1),
                    'unit': unit
                })
            else:
                # No quantity found, treat whole line as name
                ingredients.append({
                    'name': line,
                    'quantity': 100,  # Default quantity
                    'unit': 'g'
                })
        
        return ingredients

    def get_or_create_ingredient(self, name):
        """Get or create ingredient"""
        ingredient = self.db.query(Ingredient).filter(Ingredient.name == name).first()
        if not ingredient:
            # Create with realistic default nutrition values
            ingredient = Ingredient(
                id=str(uuid.uuid4()),
                name=name,
                category='other',
                unit='g',
                calories=random.uniform(50, 400),
                protein=random.uniform(1, 25),
                carbs=random.uniform(5, 50),
                fats=random.uniform(1, 30)
            )
            self.db.add(ingredient)
        return ingredient
    
    def parse_instructions(self, directions_text):
        """Parse instructions"""
        if not directions_text:
            return []
        
        steps = []
        
        if re.search(r'\d+\.', directions_text):
            parts = re.split(r'\d+\.', directions_text)
            for i, part in enumerate(parts[1:], 1):
                step = part.strip()
                if step:
                    steps.append({
                        'step_number': i,
                        'step_title': f"Step {i}",
                        'description': step
                    })
        else:
            sentences = re.split(r'[.!?]+', directions_text)
            for i, sentence in enumerate(sentences, 1):
                sentence = sentence.strip()
                if sentence and len(sentence) > 10:
                    steps.append({
                        'step_number': i,
                        'step_title': f"Step {i}",
                        'description': sentence
                    })
        
        return steps

    def import_recipe(self, recipe_data, recipe_number):
        """Import a replacement recipe"""
        sqlite_id, title, ingredients_text, directions_text, categories, calories, protein, fat, sodium, desc, rating, image = recipe_data
        
        try:
            # Determine fields
            cuisine = self.determine_cuisine(title, categories)
            meal_type = self.determine_meal_type(title, categories)
            servings = self.estimate_servings(title, ingredients_text)
            
            # Calculate totals
            total_calories = calories * servings
            total_protein = protein * servings
            total_fat = fat * servings
            total_carbs = max(0, (calories - protein*4 - fat*9) / 4) * servings
            total_sodium = (sodium or 0) * servings
            
            # Create summary
            summary = f"A delicious {cuisine} {meal_type}. Nutrition per serving: {calories:.0f} cal, {protein:.0f}g protein, {fat:.0f}g fat, {sodium or 0:.0f}mg sodium. Total recipe: {total_calories:.0f} cal."
            
            # Create recipe
            recipe = Recipe(
                id=f"recipe_{recipe_number:06d}",
                title=title,
                cuisine=cuisine,
                meal_type=meal_type,
                servings=servings,
                summary=summary,
                prep_time=random.randint(10, 60),
                cook_time=random.randint(15, 90),
                difficulty_level=random.choice(['easy', 'medium', 'hard']),
                dietary_tags=[],
                source="imported",
                image_url=image,
                is_active=True,
                # Per-serving nutrition
                per_serving_calories=round(calories, 1),
                per_serving_protein=round(protein, 1),
                per_serving_carbs=round(max(0, (calories - protein*4 - fat*9) / 4), 1),
                per_serving_fat=round(fat, 1),
                per_serving_sodium=round(sodium or 0, 1),
                # Total recipe nutrition
                total_calories=round(total_calories, 1),
                total_protein=round(total_protein, 1),
                total_carbs=round(total_carbs, 1),
                total_fat=round(total_fat, 1),
                total_sodium=round(total_sodium, 1)
            )
            
            self.db.add(recipe)
            
            # Add ingredients
            parsed_ingredients = self.parse_ingredients_properly(ingredients_text)
            for ing_data in parsed_ingredients:
                ingredient = self.get_or_create_ingredient(ing_data['name'])
                
                    recipe_ingredient = RecipeIngredient(
                    recipe_id=recipe.id,
                        ingredient_id=ingredient.id,
                    quantity=ing_data['quantity'],
                    unit=ing_data['unit']
                    )
                    self.db.add(recipe_ingredient)
            
            # Add instructions
            parsed_instructions = self.parse_instructions(directions_text)
            for step_data in parsed_instructions:
                instruction = RecipeInstruction(
                    recipe_id=recipe.id,
                    step_number=step_data['step_number'],
                    step_title=step_data['step_title'],
                    description=step_data['description']
                )
                self.db.add(instruction)
            
            self.imported_count += 1
            logger.info(f"  ✅ Imported: {title[:50]}")
            
        except Exception as e:
            logger.error(f"  ❌ Error importing {title}: {e}")
            self.db.rollback()
            raise

    def replace_recipes(self):
        """Main replacement process"""
        logger.info("🔍 Finding recipes without nutrition...")
        
        # Find recipes to delete
        recipes_to_delete = self.find_recipes_without_nutrition()
        logger.info(f"Found {len(recipes_to_delete)} recipes to delete")
        
        # Get existing titles to avoid duplicates
        existing_titles = self.get_existing_titles()
        
        # Get replacement recipes from SQLite
        logger.info("🔍 Finding replacement recipes from SQLite...")
        replacements = self.get_replacement_recipes(len(recipes_to_delete), existing_titles)
        
        if len(replacements) < len(recipes_to_delete):
            logger.warning(f"⚠️  Only found {len(replacements)} replacements for {len(recipes_to_delete)} deletions")
        
        # Delete old recipes
        logger.info("🗑️  Deleting recipes without nutrition...")
        for recipe in recipes_to_delete:
            self.delete_recipe(recipe)
        
        self.db.flush()
        logger.info(f"✅ Deleted {self.deleted_count} recipes")
        
        # Import replacement recipes
        logger.info("📥 Importing replacement recipes...")
        # Get the next available recipe number
        # Find the highest numeric recipe ID
        all_recipes = self.db.query(Recipe).all()
        max_number = 0
        for recipe in all_recipes:
            if recipe.id.startswith('recipe_'):
                try:
                    num = int(recipe.id.replace('recipe_', ''))
                    if num > max_number:
                        max_number = num
                except:
                    pass
        base_number = max_number + 1
        
        for i, replacement in enumerate(replacements):
            recipe_number = base_number + i
            self.import_recipe(replacement, recipe_number)
            
            if (i + 1) % 10 == 0:
                self.db.commit()
                logger.info(f"Imported {i + 1}/{len(replacements)} replacements...")
        
        # Final commit
        self.db.commit()
        
        logger.info(f"🎉 Successfully replaced {self.deleted_count} recipes with {self.imported_count} new recipes!")
    
    def verify_all_recipes(self):
        """Verify all recipes now have nutrition"""
        total = self.db.query(Recipe).count()
        with_nutrition = self.db.query(Recipe).filter(
            Recipe.per_serving_calories.isnot(None),
            Recipe.per_serving_calories > 0
        ).count()
        
        logger.info(f"\n📊 Final Status:")
        logger.info(f"   Total recipes: {total}")
        logger.info(f"   Recipes with nutrition: {with_nutrition}")
        logger.info(f"   Recipes without nutrition: {total - with_nutrition}")
        
        return with_nutrition == total

    def close(self):
        """Close database connections"""
        if self.sqlite_conn:
            self.sqlite_conn.close()
        self.db.close()

def main():
    """Main function"""
    replacer = RecipeReplacer()
    
    try:
        replacer.replace_recipes()
        all_fixed = replacer.verify_all_recipes()
        
        if all_fixed:
            logger.info(f"\n🎉 SUCCESS! All recipes now have nutrition values!")
        else:
            logger.warning(f"\n⚠️  Some recipes still don't have nutrition values")
        
    except Exception as e:
        logger.error(f"❌ Replacement failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        replacer.close()

if __name__ == "__main__":
    main()
