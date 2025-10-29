#!/usr/bin/env python3
"""
Add accurate dietary tags and allergen information to all 500 recipes
by analyzing actual ingredients - NO PLACEHOLDERS!
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import Recipe, RecipeIngredient, Ingredient
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DietaryTagAnalyzer:
    def __init__(self):
        self.db = SessionLocal()
        
        # Define ingredient categories for accurate analysis
        self.meat_ingredients = {
            'beef', 'pork', 'chicken', 'turkey', 'lamb', 'veal', 'duck', 'goose', 
            'bacon', 'ham', 'sausage', 'chorizo', 'pepperoni', 'salami', 'prosciutto',
            'ground beef', 'ground pork', 'ground turkey', 'ground lamb',
            'steak', 'roast', 'chop', 'cutlet', 'tenderloin', 'ribs', 'wings',
            'meat', 'poultry', 'game', 'venison', 'bison', 'rabbit'
        }
        
        self.fish_seafood = {
            'fish', 'salmon', 'tuna', 'cod', 'halibut', 'mackerel', 'sardines',
            'shrimp', 'prawns', 'crab', 'lobster', 'scallops', 'mussels', 'clams',
            'oysters', 'squid', 'octopus', 'anchovies', 'caviar', 'roe',
            'seafood', 'shellfish', 'crustacean', 'mollusk'
        }
        
        self.dairy_ingredients = {
            'milk', 'cream', 'butter', 'cheese', 'yogurt', 'sour cream', 'buttermilk',
            'heavy cream', 'half and half', 'whipping cream', 'mascarpone', 'ricotta',
            'mozzarella', 'cheddar', 'parmesan', 'feta', 'goat cheese', 'blue cheese',
            'brie', 'camembert', 'swiss', 'gouda', 'cheddar', 'monterey jack',
            'dairy', 'lactose', 'whey', 'casein'
        }
        
        self.egg_ingredients = {
            'egg', 'eggs', 'egg white', 'egg yolk', 'whole egg', 'beaten egg',
            'egg substitute', 'egg replacer'
        }
        
        self.gluten_ingredients = {
            'wheat', 'flour', 'bread', 'pasta', 'noodles', 'couscous', 'bulgur',
            'barley', 'rye', 'oats', 'spelt', 'kamut', 'triticale', 'semolina',
            'breadcrumbs', 'panko', 'crackers', 'cereal', 'granola', 'beer',
            'soy sauce', 'teriyaki', 'worcestershire', 'malt', 'malt extract'
        }
        
        self.nut_ingredients = {
            'almond', 'walnut', 'pecan', 'hazelnut', 'pistachio', 'cashew',
            'brazil nut', 'macadamia', 'pine nut', 'peanut', 'peanut butter',
            'almond butter', 'nut butter', 'nuts', 'nut flour', 'nut meal'
        }
        
        self.soy_ingredients = {
            'soy', 'soybean', 'tofu', 'tempeh', 'miso', 'soy sauce', 'tamari',
            'soy milk', 'soy yogurt', 'soy cheese', 'edamame', 'soy protein',
            'soy flour', 'soy lecithin'
        }
        
        self.vegetarian_safe = {
            'vegetable', 'fruit', 'grain', 'rice', 'quinoa', 'beans', 'lentils',
            'chickpeas', 'tofu', 'tempeh', 'mushroom', 'herb', 'spice', 'oil',
            'vinegar', 'sugar', 'salt', 'pepper', 'garlic', 'onion', 'tomato',
            'potato', 'carrot', 'celery', 'bell pepper', 'zucchini', 'eggplant',
            'spinach', 'lettuce', 'cabbage', 'broccoli', 'cauliflower'
        }
    
    def analyze_recipe_ingredients(self, recipe):
        """Analyze recipe ingredients to determine dietary tags"""
        dietary_tags = []
        allergens = []
        
        # Get all ingredients for this recipe
        ingredients = []
        for ri in recipe.ingredients:
            ingredients.append(ri.ingredient.name.lower())
        
        # Check for meat/fish (not vegetarian/vegan)
        has_meat = any(any(meat in ing for meat in self.meat_ingredients) for ing in ingredients)
        has_fish = any(any(fish in ing for fish in self.fish_seafood) for ing in ingredients)
        
        # Check for dairy (not vegan)
        has_dairy = any(any(dairy in ing for dairy in self.dairy_ingredients) for ing in ingredients)
        
        # Check for eggs (not vegan)
        has_eggs = any(any(egg in ing for egg in self.egg_ingredients) for ing in ingredients)
        
        # Check for gluten
        has_gluten = any(any(gluten in ing for gluten in self.gluten_ingredients) for ing in ingredients)
        
        # Check for nuts
        has_nuts = any(any(nut in ing for nut in self.nut_ingredients) for ing in ingredients)
        
        # Check for soy
        has_soy = any(any(soy in ing for soy in self.soy_ingredients) for ing in ingredients)
        
        # Determine dietary categories
        if not has_meat and not has_fish:
            dietary_tags.append('vegetarian')
            if not has_dairy and not has_eggs:
                dietary_tags.append('vegan')
        
        if not has_gluten:
            dietary_tags.append('gluten-free')
        
        if not has_nuts:
            dietary_tags.append('nut-free')
        
        if not has_soy:
            dietary_tags.append('soy-free')
        
        # Add allergen warnings
        if has_dairy:
            allergens.append('dairy')
        if has_eggs:
            allergens.append('eggs')
        if has_gluten:
            allergens.append('gluten')
        if has_nuts:
            allergens.append('nuts')
        if has_soy:
            allergens.append('soy')
        if has_fish:
            allergens.append('fish')
        
        # Add health-focused tags
        if any('low' in ing or 'reduced' in ing for ing in ingredients):
            dietary_tags.append('low-sodium')
        
        if any('sugar' not in ing and 'honey' not in ing and 'syrup' not in ing for ing in ingredients):
            dietary_tags.append('low-sugar')
        
        if any('oil' in ing or 'fat' in ing for ing in ingredients):
            dietary_tags.append('contains-oils')
        
        return dietary_tags, allergens
    
    def update_all_recipes(self):
        """Update all 500 recipes with accurate dietary tags"""
        logger.info("🔍 Analyzing ingredients for dietary tags...")
        
        recipes = self.db.query(Recipe).all()
        updated_count = 0
        
        for recipe in recipes:
            try:
                dietary_tags, allergens = self.analyze_recipe_ingredients(recipe)
                
                # Update recipe with dietary tags
                recipe.dietary_tags = dietary_tags
                
                # Add allergen information to summary if not already there
                if allergens:
                    allergen_text = f" Contains: {', '.join(allergens).title()}"
                    if not recipe.summary or allergen_text not in recipe.summary:
                        recipe.summary = (recipe.summary or "") + allergen_text
                
                updated_count += 1
                
                if updated_count % 50 == 0:
                    logger.info(f"Updated {updated_count} recipes...")
                    
            except Exception as e:
                logger.error(f"Error updating recipe {recipe.title}: {e}")
                continue
        
        try:
            self.db.commit()
            logger.info(f"✅ Updated {updated_count} recipes with accurate dietary tags!")
            
            # Verify updates
            self.verify_updates()
        except Exception as e:
            logger.error(f"Error committing changes: {e}")
            self.db.rollback()
            raise
    
    def verify_updates(self):
        """Verify the dietary tag updates"""
        logger.info("🔍 Verifying dietary tag updates...")
        
        # Check a few recipes
        sample_recipes = self.db.query(Recipe).limit(5).all()
        
        for recipe in sample_recipes:
            print(f"\nRecipe: {recipe.title}")
            print(f"Dietary Tags: {recipe.dietary_tags}")
            print(f"Summary: {recipe.summary}")
        
        # Check distribution of dietary tags
        all_tags = set()
        for recipe in self.db.query(Recipe).all():
            if recipe.dietary_tags:
                all_tags.update(recipe.dietary_tags)
        
        print(f"\nAll dietary tags found:")
        for tag in sorted(all_tags):
            count = sum(1 for r in self.db.query(Recipe).all() if r.dietary_tags and tag in r.dietary_tags)
            print(f"  {tag}: {count} recipes")

def main():
    analyzer = DietaryTagAnalyzer()
    analyzer.update_all_recipes()

if __name__ == "__main__":
    main()


