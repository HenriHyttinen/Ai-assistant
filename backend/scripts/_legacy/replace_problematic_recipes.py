#!/usr/bin/env python3
"""
Replace Problematic Recipes

This script:
1. Identifies recipes with critical issues (missing data, very low calories)
2. Replaces them with good recipes from SQLite that have proper nutrition
3. Prioritizes replacing recipes that can't be fixed
"""

import sys
import os
import json
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

class ProblematicRecipeReplacer:
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
    
    def load_validation_report(self):
        """Load recipe validation report"""
        try:
            with open('recipe_validation_report.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error("❌ Validation report not found. Run comprehensive_recipe_validator.py first.")
            return None
    
    def identify_problematic_recipes(self, report):
        """Identify recipes that should be replaced"""
        to_replace = []
        
        # Check critical recipes
        for recipe_info in report.get('critical_recipes', []):
            recipe_id = recipe_info.get('recipe_id') or recipe_info.get('id')
            title = recipe_info.get('title')
            if recipe_id and title:
                to_replace.append({'id': recipe_id, 'title': title, 'reason': 'critical'})
        
        # Check warning recipes for very low calories
        for recipe_info in report.get('warning_recipes', []):
            recipe_id = recipe_info.get('recipe_id') or recipe_info.get('id')
            title = recipe_info.get('title')
            issue = recipe_info.get('issue', '')
            
            if recipe_id and title and 'Very Low Calories' in issue:
                to_replace.append({'id': recipe_id, 'title': title, 'reason': 'very_low_calories'})
        
        # Also check recipes directly in database for issues
        recipes_very_low = self.db.query(Recipe).filter(
            Recipe.per_serving_calories > 0,
            Recipe.per_serving_calories < 50
        ).all()
        
        recipes_zero = self.db.query(Recipe).filter(
            (Recipe.per_serving_calories == 0) | 
            (Recipe.per_serving_calories.is_(None))
        ).all()
        
        recipes_too_high = self.db.query(Recipe).filter(
            Recipe.per_serving_calories > 3000
        ).all()
        
        for recipe in recipes_very_low:
            # Check if already in to_replace
            if not any(r['id'] == recipe.id for r in to_replace):
                to_replace.append({'id': recipe.id, 'title': recipe.title, 'reason': 'very_low_calories_db'})
        
        for recipe in recipes_zero:
            if not any(r['id'] == recipe.id for r in to_replace):
                to_replace.append({'id': recipe.id, 'title': recipe.title, 'reason': 'zero_calories'})
        
        for recipe in recipes_too_high:
            if not any(r['id'] == recipe.id for r in to_replace):
                to_replace.append({'id': recipe.id, 'title': recipe.title, 'reason': 'too_high_calories'})
        
        # Remove duplicates (same recipe might be flagged multiple times)
        seen_ids = set()
        unique_to_replace = []
        for r in to_replace:
            if r['id'] not in seen_ids:
                seen_ids.add(r['id'])
                unique_to_replace.append(r)
        
        logger.info(f"🔍 Found {len(unique_to_replace)} recipes to replace")
        for r in unique_to_replace[:10]:
            logger.info(f"   • {r['title']} ({r['reason']})")
        if len(unique_to_replace) > 10:
            logger.info(f"   ... and {len(unique_to_replace) - 10} more")
        
        return unique_to_replace
    
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
        """Get replacement recipes from SQLite"""
        self.sqlite_cursor.execute("""
            SELECT id, title, ingredients, directions, categories, calories, protein, fat, sodium, "desc", rating, image
            FROM recipes
            WHERE calories IS NOT NULL 
            AND calories >= 100
            AND calories <= 2000
            AND protein IS NOT NULL
            AND fat IS NOT NULL
            AND sodium IS NOT NULL
            AND ingredients IS NOT NULL 
            AND directions IS NOT NULL
            AND ingredients != ''
            AND directions != ''
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
        """Get existing ingredient or create placeholder"""
        # Clean name
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
            # Use a generic placeholder ingredient instead of creating new ones
            # This avoids ingredient ID issues - we'll use "Unknown" as a fallback
            placeholder = self.db.query(Ingredient).filter(
                Ingredient.name.ilike('unknown%')
            ).first()
            
            if not placeholder:
                # Try to find any ingredient with 0 calories as a placeholder
                placeholder = self.db.query(Ingredient).filter(
                    Ingredient.calories == 0
                ).first()
            
            if placeholder:
                ingredient = placeholder
            else:
                # Last resort: skip this ingredient
                logger.warning(f"⚠️  Skipping ingredient '{name}' - no placeholder available")
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
            # Common patterns: "1 cup flour", "2 tbsp butter", etc.
            parts = line.split(',', 1)
            first_part = parts[0].strip()
            
            # Try to parse quantity and unit
            qty_match = re.match(r'^([\d\s/]+)\s*(cup|cups|tbsp|tablespoon|tablespoons|tsp|teaspoon|teaspoons|oz|ounce|ounces|lb|pound|pounds|g|gram|grams|kg|kilogram|kg|ml|milliliter|milliliters)?\s+(.+)', first_part, re.IGNORECASE)
            
            if qty_match:
                qty_str = qty_match.group(1).strip()
                unit = (qty_match.group(2) or 'g').lower()
                name = qty_match.group(3).strip()
                
                # Convert quantity to number
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
                    
                    # Convert to grams (simplified)
                    if unit in ['cup', 'cups']:
                        qty = qty * 240  # ml to g approximation
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
                    # If parsing fails, just use the whole line as name
                    ingredients.append({
                        'name': line,
                        'quantity': 100.0,  # Default
                        'unit': 'g'
                    })
            else:
                # No quantity found, use whole line as name
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
        
        # Split by common delimiters
        steps = re.split(r'\n+|\d+\.\s*|•\s*', directions_text)
        instructions = []
        
        for i, step in enumerate(steps, 1):
            step = step.strip()
            if step and len(step) > 10:  # Skip very short steps
                instructions.append({
                    'step_number': i,
                    'step_title': f'Step {i}',  # Required field, can't be None
                    'description': step
                })
        
        return instructions if instructions else [{
            'step_number': 1,
            'step_title': 'Step 1',  # Required field
            'description': directions_text[:1000]  # Truncate if too long
        }]
    
    def import_recipe(self, recipe_data, recipe_number):
        """Import a replacement recipe"""
        sqlite_id, title, ingredients_text, directions_text, categories, calories, protein, fat, sodium, desc, rating, image = recipe_data
        
        try:
            # Calculate carbs from calories
            carbs = max(0, (calories - protein * 4 - fat * 9) / 4)
            
            # Determine servings (default to 4, but can parse from description)
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
                title=title[:200],  # Limit title length
                summary=desc[:500] if desc else None,
                cuisine=categories.split(',')[0].strip()[:50] if categories else 'unknown',
                meal_type='main_course',  # Default
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
    
    def replace_problematic_recipes(self):
        """Main replacement process"""
        # Load validation report
        report = self.load_validation_report()
        if not report:
            return
        
        # Identify problematic recipes
        to_replace = self.identify_problematic_recipes(report)
        
        if not to_replace:
            logger.info("✅ No problematic recipes found to replace!")
            return
        
        logger.info(f"\n🔍 Recipes to replace: {len(to_replace)}")
        for r in to_replace[:10]:
            logger.info(f"   • {r['title']} ({r['reason']})")
        
        # Get existing titles
        existing_titles = self.get_existing_titles()
        
        # Get replacement recipes
        replacements = self.get_replacement_recipes(len(to_replace), existing_titles)
        
        if len(replacements) < len(to_replace):
            logger.warning(f"⚠️  Only found {len(replacements)} replacements for {len(to_replace)} deletions")
            to_replace = to_replace[:len(replacements)]
        
        # Delete problematic recipes
        logger.info("\n🗑️  Deleting problematic recipes...")
        for recipe_info in to_replace:
            recipe = self.db.query(Recipe).filter(Recipe.id == recipe_info['id']).first()
            if recipe:
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
        
        logger.info(f"\n🎉 Successfully replaced {self.deleted_count} recipes with {self.imported_count} new recipes!")
        logger.info("\n🔄 Next step: Run optimize_and_calculate_micronutrients.py to recalculate nutrition")

if __name__ == "__main__":
    replacer = ProblematicRecipeReplacer()
    try:
        replacer.replace_problematic_recipes()
    except Exception as e:
        logger.error(f"❌ Replacement failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

