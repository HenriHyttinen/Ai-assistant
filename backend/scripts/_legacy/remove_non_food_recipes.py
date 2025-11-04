#!/usr/bin/env python3
"""
Remove Non-Food Recipes

This script:
1. Identifies and removes non-food items (drinks, dips, sauces, spreads, etc.)
2. Replaces them with proper food recipes from SQLite
"""

import sys
import os
import sqlite3
import re
import random
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import Recipe, RecipeIngredient, Ingredient, RecipeInstruction
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NonFoodRecipeRemover:
    def __init__(self):
        self.db = SessionLocal()
        
        # Find SQLite database
        sqlite_paths = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'recipes.sqlite3'),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'recipes.sqlite3'),
            '../recipes.sqlite3',
            '../../recipes.sqlite3',
            'recipes.sqlite3'
        ]
        
        self.sqlite_conn = None
        for path in sqlite_paths:
            if os.path.exists(path):
                try:
                    self.sqlite_conn = sqlite3.connect(path)
                    logger.info(f"✅ Connected to SQLite: {path}")
                    break
                except Exception:
                    continue
        
        if not self.sqlite_conn:
            raise FileNotFoundError("Could not find recipes.sqlite3")
        
        self.sqlite_cursor = self.sqlite_conn.cursor()
        self.deleted_count = 0
        self.imported_count = 0
        self.ingredient_cache = {}
    
    def is_non_food_recipe(self, recipe):
        """Check if recipe is actually a non-food item"""
        title_lower = recipe.title.lower()
        
        # Drinks (standalone beverages)
        if re.search(r'\b(drink|beverage|cocktail|punch|smoothie|toddy)\b', title_lower):
            if not re.search(r'\b(with|in|and)\b', title_lower):
                return 'drink'
        
        # Dips (standalone dips)
        if re.search(r'\bdip\b', title_lower) and 'with' not in title_lower:
            return 'dip'
        
        # Sauces/Relishes/Dressings (standalone)
        if re.search(r'\b(sauce|relish|dressing|mayo|aioli|chutney)\b', title_lower):
            if 'with' not in title_lower and 'and' not in title_lower:
                return 'sauce'
        
        # Spreads
        if re.search(r'\bspread\b', title_lower) and 'with' not in title_lower:
            return 'spread'
        
        # Jams/Preserves
        if re.search(r'\b(jam|jelly|preserve)\b', title_lower) and 'with' not in title_lower:
            return 'jam'
        
        # Marinades/Brines
        if re.search(r'\b(marinade|brine)\b', title_lower) and 'with' not in title_lower:
            return 'marinade'
        
        # Syrups (standalone)
        if re.search(r'\bsyrup\b', title_lower) and not re.search(r'\b(with|in|and)\b', title_lower):
            return 'syrup'
        
        return None
    
    def find_non_food_recipes(self):
        """Find all non-food recipes"""
        all_recipes = self.db.query(Recipe).all()
        non_food_recipes = []
        
        for recipe in all_recipes:
            category = self.is_non_food_recipe(recipe)
            if category:
                non_food_recipes.append({
                    'recipe': recipe,
                    'category': category
                })
        
        logger.info(f"🔍 Found {len(non_food_recipes)} non-food recipes")
        
        return non_food_recipes
    
    def normalize_title(self, title):
        """Normalize title for matching"""
        if not title:
            return ""
        title = re.sub(r'\s+', ' ', title.strip().lower())
        title = re.sub(r'[^\w\s]', '', title)
        return title
    
    def get_existing_titles(self):
        """Get all existing recipe titles"""
        existing = self.db.query(Recipe.title).all()
        return {self.normalize_title(title[0]) for title in existing}
    
    def get_replacement_recipes(self, count, existing_titles):
        """Get replacement recipes from SQLite (food recipes only)"""
        self.sqlite_cursor.execute("""
            SELECT id, title, ingredients, directions, categories, calories, protein, fat, sodium, "desc", rating, image
            FROM recipes
            WHERE calories IS NOT NULL 
            AND calories >= 100
            AND calories <= 2000
            AND protein IS NOT NULL
            AND fat IS NOT NULL
            AND ingredients IS NOT NULL 
            AND directions IS NOT NULL
            AND ingredients != ''
            AND directions != ''
            AND title NOT LIKE '%drink%'
            AND title NOT LIKE '%beverage%'
            AND title NOT LIKE '%cocktail%'
            AND title NOT LIKE '%punch%'
            AND title NOT LIKE '%smoothie%'
            AND title NOT LIKE '%dip%'
            AND title NOT LIKE '%sauce%'
            AND title NOT LIKE '%dressing%'
            AND title NOT LIKE '%mayo%'
            AND title NOT LIKE '%jam%'
            AND title NOT LIKE '%jelly%'
            AND title NOT LIKE '%preserve%'
            AND title NOT LIKE '%spread%'
            AND title NOT LIKE '%syrup%'
            AND title NOT LIKE '%marinade%'
            AND title NOT LIKE '%brine%'
        """)
        
        all_candidates = self.sqlite_cursor.fetchall()
        logger.info(f"Found {len(all_candidates)} potential replacement recipes")
        
        # Filter out duplicates
        filtered = []
        for candidate in all_candidates:
            title = candidate[1]
            if self.normalize_title(title) not in existing_titles:
                filtered.append(candidate)
        
        logger.info(f"After filtering duplicates: {len(filtered)} candidates")
        
        # Shuffle and take count
        random.shuffle(filtered)
        return filtered[:count]
    
    def delete_recipe(self, recipe):
        """Delete a recipe and all related data"""
        try:
            # Delete instructions
            from models.recipe import RecipeInstruction
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
        except Exception as e:
            logger.error(f"Error deleting recipe {recipe.id}: {e}")
            self.db.rollback()
            raise
    
    def get_or_create_ingredient(self, name):
        """Get existing ingredient or use placeholder"""
        name = name.strip()
        if not name or len(name) < 2:
            return None
        
        # Check cache
        if name in self.ingredient_cache:
            return self.ingredient_cache[name]
        
        # Try to find existing
        ingredient = self.db.query(Ingredient).filter(
            Ingredient.name.ilike(f"%{name}%")
        ).first()
        
        if not ingredient:
            # Use placeholder
            placeholder = self.db.query(Ingredient).filter(
                Ingredient.name.ilike('unknown%')
            ).first()
            
            if not placeholder:
                placeholder = self.db.query(Ingredient).filter(
                    Ingredient.calories == 0
                ).first()
            
            if placeholder:
                ingredient = placeholder
            else:
                return None
        
        self.ingredient_cache[name] = ingredient
        return ingredient
    
    def parse_ingredients(self, ingredients_text):
        """Parse ingredients from text"""
        if not ingredients_text:
            return []
        
        lines = ingredients_text.split('\n')
        ingredients = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Try to extract quantity, unit, and name
            parts = line.split(',', 1)
            first_part = parts[0].strip()
            
            qty_match = re.match(r'^([\d\s/]+)\s*(cup|cups|tbsp|tablespoon|tablespoons|tsp|teaspoon|teaspoons|oz|ounce|ounces|lb|pound|pounds|g|gram|grams|kg|kilogram|kg|ml|milliliter|milliliters)?\s+(.+)', first_part, re.IGNORECASE)
            
            if qty_match:
                qty_str = qty_match.group(1).strip()
                unit = (qty_match.group(2) or 'g').lower()
                name = qty_match.group(3).strip()
                
                try:
                    if '/' in qty_str:
                        parts = qty_str.split()
                        qty = 0
                        for part in parts:
                            if '/' in part:
                                num, den = part.split('/')
                                qty += float(num) / float(den)
                            else:
                                qty += float(part)
                    else:
                        qty = float(qty_str)
                    
                    # Convert to grams
                    if unit in ['cup', 'cups']:
                        qty = qty * 240
                    elif unit in ['tbsp', 'tablespoon', 'tablespoons']:
                        qty = qty * 15
                    elif unit in ['tsp', 'teaspoon', 'teaspoons']:
                        qty = qty * 5
                    elif unit in ['oz', 'ounce', 'ounces']:
                        qty = qty * 28.35
                    elif unit in ['lb', 'pound', 'pounds']:
                        qty = qty * 453.6
                    
                    if qty > 0:
                        ingredients.append({
                            'name': name,
                            'quantity': qty,
                            'unit': 'g'
                        })
                except (ValueError, ZeroDivisionError):
                    ingredients.append({
                        'name': line,
                        'quantity': 100.0,
                        'unit': 'g'
                    })
            else:
                ingredients.append({
                    'name': line,
                    'quantity': 100.0,
                    'unit': 'g'
                })
        
        return ingredients
    
    def parse_instructions(self, directions_text):
        """Parse instructions from text"""
        if not directions_text:
            return []
        
        steps = re.split(r'\n+|\d+\.\s*|•\s*', directions_text)
        instructions = []
        
        for i, step in enumerate(steps, 1):
            step = step.strip()
            if step and len(step) > 10:
                instructions.append({
                    'step_number': i,
                    'step_title': f'Step {i}',
                    'description': step
                })
        
        return instructions if instructions else [{
            'step_number': 1,
            'step_title': 'Step 1',
            'description': directions_text[:1000]
        }]
    
    def import_recipe(self, recipe_data, recipe_number):
        """Import a replacement recipe"""
        sqlite_id, title, ingredients_text, directions_text, categories, calories, protein, fat, sodium, desc, rating, image = recipe_data
        
        try:
            # Calculate carbs
            carbs = max(0, (calories - protein * 4 - fat * 9) / 4)
            
            # Determine servings
            servings = 4
            if desc:
                servings_match = re.search(r'(\d+)\s*(serving|portion)', desc.lower())
                if servings_match:
                    servings = int(servings_match.group(1))
            
            # Calculate totals
            total_calories = calories * servings
            total_protein = protein * servings
            total_fat = fat * servings
            total_carbs = carbs * servings
            total_sodium = sodium * servings if sodium else 0
            
            # Create recipe
            recipe = Recipe(
                id=f'recipe_{recipe_number}',
                title=title[:200],
                summary=desc[:500] if desc else None,
                cuisine=categories.split(',')[0].strip()[:50] if categories else 'unknown',
                meal_type='main_course',
                servings=servings,
                prep_time=0,
                cook_time=0,
                difficulty_level='medium',
                per_serving_calories=round(calories, 1),
                per_serving_protein=round(protein, 1),
                per_serving_carbs=round(carbs, 1),
                per_serving_fat=round(fat, 1),
                per_serving_sodium=round(sodium, 1) if sodium else 0,
                total_calories=round(total_calories, 1),
                total_protein=round(total_protein, 1),
                total_carbs=round(total_carbs, 1),
                total_fat=round(total_fat, 1),
                total_sodium=round(total_sodium, 1) if sodium else 0
            )
            
            self.db.add(recipe)
            self.db.flush()
            
            # Add ingredients
            parsed_ingredients = self.parse_ingredients(ingredients_text)
            for ing_data in parsed_ingredients:
                ingredient = self.get_or_create_ingredient(ing_data['name'])
                if ingredient:
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
            import traceback
            traceback.print_exc()
            self.db.rollback()
            raise
    
    def find_invalid_nutrition_recipes(self):
        """Find recipes with invalid nutrition values"""
        all_recipes = self.db.query(Recipe).all()
        invalid_recipes = []
        
        for recipe in all_recipes:
            calories = recipe.per_serving_calories or 0
            
            # Check for invalid calories
            if calories > 0 and (calories < 50 or calories > 2000):
                invalid_recipes.append({
                    'recipe': recipe,
                    'reason': 'invalid_calories',
                    'calories': calories
                })
            # Check for missing nutrition
            elif calories == 0 or not recipe.per_serving_protein:
                invalid_recipes.append({
                    'recipe': recipe,
                    'reason': 'missing_nutrition',
                    'calories': calories
                })
        
        return invalid_recipes
    
    def remove_and_replace(self):
        """Main removal and replacement process"""
        # Find non-food recipes
        non_food_recipes = self.find_non_food_recipes()
        
        # Find recipes with invalid nutrition
        invalid_nutrition_recipes = self.find_invalid_nutrition_recipes()
        
        # Combine lists
        all_problematic = non_food_recipes + invalid_nutrition_recipes
        
        if not all_problematic:
            logger.info("✅ No problematic recipes found!")
            return
        
        logger.info(f"🔍 Found {len(non_food_recipes)} non-food recipes")
        logger.info(f"🔍 Found {len(invalid_nutrition_recipes)} recipes with invalid nutrition")
        
        # Group by category
        by_category = defaultdict(list)
        for item in non_food_recipes:
            by_category[item['category']].append(item)
        
        logger.info("\n📋 Non-food recipes by category:")
        for category, items in sorted(by_category.items()):
            logger.info(f"   {category}: {len(items)} recipes")
            for item in items[:5]:
                logger.info(f"      • {item['recipe'].title}")
            if len(items) > 5:
                logger.info(f"      ... and {len(items) - 5} more")
        
        if invalid_nutrition_recipes:
            logger.info("\n📋 Recipes with invalid nutrition:")
            for item in invalid_nutrition_recipes[:10]:
                r = item['recipe']
                logger.info(f"   • {r.title}: {item['calories']} cal/serving ({item['reason']})")
            if len(invalid_nutrition_recipes) > 10:
                logger.info(f"   ... and {len(invalid_nutrition_recipes) - 10} more")
        
        # Get existing titles
        existing_titles = self.get_existing_titles()
        
        # Get replacement recipes
        replacements = self.get_replacement_recipes(len(all_problematic), existing_titles)
        
        if len(replacements) < len(all_problematic):
            logger.warning(f"⚠️  Only found {len(replacements)} replacements for {len(all_problematic)} deletions")
            all_problematic = all_problematic[:len(replacements)]
        
        # Delete problematic recipes
        logger.info("\n🗑️  Deleting problematic recipes...")
        for item in all_problematic:
            recipe = item['recipe'] if 'recipe' in item else item
            self.delete_recipe(recipe)
        
        self.db.flush()
        logger.info(f"✅ Deleted {self.deleted_count} recipes")
        
        # Import replacement recipes
        logger.info("\n📥 Importing replacement recipes...")
        # Get next recipe number
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
                logger.info(f"Progress: {i + 1}/{len(replacements)} imported...")
                self.db.commit()
        
        self.db.commit()
        
        logger.info(f"\n🎉 Successfully replaced {self.deleted_count} non-food recipes with {self.imported_count} food recipes!")
        logger.info("\n🔄 Next step: Run optimize_and_calculate_micronutrients.py to recalculate nutrition")

if __name__ == "__main__":
    remover = NonFoodRecipeRemover()
    try:
        remover.remove_and_replace()
    except Exception as e:
        logger.error(f"❌ Removal failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

