#!/usr/bin/env python3
"""
Analyze and Fix Recipe Servings Based on Ingredient Quantities

This script analyzes actual ingredient quantities and recipe structure
to determine realistic serving counts for each recipe, then updates
totals accordingly.

Analysis approach:
1. Look at key ingredient quantities (meat, flour, vegetables, etc.)
2. Check recipe type/structure (soup, casserole, individual items, etc.)
3. Use standard serving sizes to estimate
4. Update servings and recalculate totals from per-serving values
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

class RecipeServingAnalyzer:
    def __init__(self):
        self.db = SessionLocal()
        self.updated_count = 0
        self.analysis_summary = {}
        
    def analyze_and_fix_all_recipes(self):
        """Analyze and fix servings for all recipes"""
        logger.info("🔍 Starting recipe serving analysis...")
        
        recipes = self.db.query(Recipe).filter(Recipe.is_active == True).all()
        total_recipes = len(recipes)
        logger.info(f"📊 Found {total_recipes} active recipes to analyze")
        
        for recipe in recipes:
            try:
                estimated_servings = self.analyze_recipe_servings(recipe)
                if estimated_servings and estimated_servings > 0:
                    self.update_recipe_servings(recipe, estimated_servings)
            except Exception as e:
                logger.error(f"❌ Error processing recipe {recipe.id} ({recipe.title}): {str(e)}")
                continue
        
        self.db.commit()
        
        logger.info(f"\n✅ Analysis complete!")
        logger.info(f"   Updated: {self.updated_count} recipes")
        logger.info(f"   Total: {total_recipes} recipes")
        
        # Print summary
        logger.info(f"\n📊 Servings Distribution:")
        for servings_count, recipe_count in sorted(self.analysis_summary.items()):
            logger.info(f"   {servings_count} servings: {recipe_count} recipes")
    
    def analyze_recipe_servings(self, recipe):
        """Analyze recipe to determine realistic serving count"""
        # Strategy 1: Check for explicit serving mentions in summary/title
        explicit_servings = self.extract_explicit_servings(recipe)
        if explicit_servings:
            return explicit_servings
        
        # Strategy 2: Analyze ingredient quantities
        ingredient_based = self.analyze_ingredient_quantities(recipe)
        if ingredient_based:
            return ingredient_based
        
        # Strategy 3: Analyze recipe type/structure
        type_based = self.analyze_recipe_type(recipe)
        if type_based:
            return type_based
        
        # Strategy 4: Use existing servings if reasonable (1-12)
        if recipe.servings and 1 <= recipe.servings <= 12:
            return recipe.servings
        
        # Default: estimate based on common patterns
        return self.default_serving_estimate(recipe)
    
    def extract_explicit_servings(self, recipe):
        """Extract serving count from recipe summary or title"""
        text = (recipe.title + " " + (recipe.summary or "")).lower()
        
        # Look for patterns like "serves 4", "4 servings", "for 4 people"
        patterns = [
            r'serves?\s+(\d+)',
            r'(\d+)\s+servings?',
            r'for\s+(\d+)\s+(?:people|persons|servings?)',
            r'makes?\s+(\d+)',
            r'(\d+)\s+(?:people|persons|portions)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                servings = int(match.group(1))
                if 1 <= servings <= 24:  # Reasonable range
                    logger.debug(f"Found explicit servings {servings} in {recipe.id}")
                    return servings
        
        return None
    
    def analyze_ingredient_quantities(self, recipe):
        """Analyze ingredient quantities to estimate servings"""
        # Get all ingredients for this recipe
        recipe_ingredients = self.db.query(RecipeIngredient).filter(
            RecipeIngredient.recipe_id == recipe.id
        ).all()
        
        if not recipe_ingredients:
            return None
        
        serving_indicators = []
        
        for ri in recipe_ingredients:
            ingredient = ri.ingredient
            quantity = ri.quantity
            unit = ri.unit.lower() if ri.unit else ''
            ingredient_name = (ingredient.name or "").lower() if ingredient else ""
            
            # Analyze based on ingredient type and quantity
            estimated = self.estimate_servings_from_ingredient(
                ingredient_name, quantity, unit
            )
            
            if estimated:
                serving_indicators.append(estimated)
        
        if not serving_indicators:
            return None
        
        # Use median of all estimates (more robust than average)
        serving_indicators.sort()
        median_index = len(serving_indicators) // 2
        median_servings = serving_indicators[median_index]
        
        # If we have multiple indicators, use the median
        logger.debug(f"Recipe {recipe.id}: ingredient analysis suggests {median_servings} servings")
        return median_servings
    
    def estimate_servings_from_ingredient(self, ingredient_name, quantity, unit):
        """Estimate servings based on a single ingredient"""
        # Meat-based serving estimation
        meat_keywords = ['beef', 'chicken', 'pork', 'lamb', 'turkey', 'fish', 'salmon', 'tuna', 'meat', 'steak', 'breast', 'thigh']
        if any(kw in ingredient_name for kw in meat_keywords):
            if unit in ['lb', 'pound', 'pounds', 'kg', 'kilogram']:
                # 1 lb meat ≈ 4 servings (4 oz per serving)
                if unit in ['lb', 'pound', 'pounds']:
                    servings_per_lb = 4
                    return max(2, min(12, int(quantity * servings_per_lb)))
                elif unit in ['kg', 'kilogram']:
                    servings_per_kg = 8
                    return max(2, min(24, int(quantity * servings_per_kg)))
            elif unit in ['g', 'gram', 'grams']:
                # 113g ≈ 4 oz ≈ 1 serving
                servings = max(1, min(12, int(quantity / 113)))
                if servings > 0:
                    return servings
        
        # Pasta/noodles serving estimation
        pasta_keywords = ['pasta', 'noodle', 'spaghetti', 'penne', 'macaroni', 'fettuccine', 'linguine']
        if any(kw in ingredient_name for kw in pasta_keywords):
            if unit in ['lb', 'pound', 'pounds']:
                # 1 lb pasta ≈ 8 servings
                return max(4, min(12, int(quantity * 8)))
            elif unit in ['g', 'gram', 'grams']:
                # 60g dry pasta ≈ 1 serving
                servings = max(2, min(12, int(quantity / 60)))
                if servings > 0:
                    return servings
        
        # Rice serving estimation
        if 'rice' in ingredient_name:
            if unit in ['cup', 'cups']:
                # 1 cup uncooked rice ≈ 3 servings
                return max(2, min(12, int(quantity * 3)))
            elif unit in ['g', 'gram', 'grams']:
                # 65g uncooked rice ≈ 1 serving
                servings = max(2, min(12, int(quantity / 65)))
                if servings > 0:
                    return servings
        
        # Flour-based items (bread, baked goods)
        if 'flour' in ingredient_name:
            if unit in ['cup', 'cups']:
                # Rough estimate: 2-3 cups flour ≈ 1 loaf bread ≈ 8-12 slices ≈ 4-6 servings
                # More conservative: 1 cup flour ≈ 2 servings for baked goods
                return max(2, min(12, int(quantity * 2)))
            elif unit in ['g', 'gram', 'grams']:
                # 125g flour ≈ 1 cup ≈ 2 servings
                servings = max(1, min(12, int(quantity / 125 * 2)))
                if servings > 0:
                    return servings
        
        # Eggs
        if 'egg' in ingredient_name:
            # 2 eggs ≈ 1-2 servings depending on recipe type
            # For baked goods: 2 eggs ≈ 4-6 servings
            # For main dishes: 2 eggs ≈ 2 servings
            if quantity >= 4:
                return min(8, max(2, int(quantity / 2)))
            else:
                return max(1, min(4, int(quantity)))
        
        # Vegetables - harder to estimate, but large quantities indicate more servings
        veg_keywords = ['potato', 'onion', 'tomato', 'bell pepper', 'carrot', 'broccoli', 'cauliflower']
        if any(kw in ingredient_name for kw in veg_keywords):
            if unit in ['lb', 'pound', 'pounds']:
                # 1 lb vegetables ≈ 3-4 servings
                return max(2, min(12, int(quantity * 3.5)))
            elif unit in ['cup', 'cups']:
                # 1 cup vegetables ≈ 1 serving (as side)
                return max(2, min(12, int(quantity)))
        
        # Cheese
        if 'cheese' in ingredient_name:
            if unit in ['cup', 'cups']:
                # 1 cup shredded cheese ≈ 2-3 servings worth
                return max(2, min(8, int(quantity * 2.5)))
            elif unit in ['lb', 'pound', 'pounds']:
                # 1 lb cheese ≈ 6-8 servings
                return max(4, min(12, int(quantity * 7)))
        
        # Stock/broth - common for soups/stews
        if 'stock' in ingredient_name or 'broth' in ingredient_name:
            if unit in ['cup', 'cups']:
                # Rough estimate: 1 cup stock ≈ 1 serving for soup
                return max(2, min(12, int(quantity)))
            elif unit in ['g', 'gram', 'grams']:
                # 250ml ≈ 1 cup ≈ 1 serving
                servings = max(2, min(12, int(quantity / 250)))
                if servings > 0:
                    return servings
        
        return None
    
    def analyze_recipe_type(self, recipe):
        """Analyze recipe type to estimate servings"""
        title_lower = recipe.title.lower()
        summary_lower = (recipe.summary or "").lower()
        text = title_lower + " " + summary_lower
        
        # Soups and stews typically serve more
        if any(kw in text for kw in ['soup', 'stew', 'chili', 'gumbo', 'curry']):
            return 6  # Common soup serving size
        
        # Dips and sauces
        if any(kw in text for kw in ['dip', 'sauce', 'spread']):
            return 8  # Party-sized
        
        # Casseroles
        if 'casserole' in text:
            return 8
        
        # Individual items (sandwiches, burgers, etc.)
        if any(kw in text for kw in ['sandwich', 'burger', 'wrap', 'taco', 'burrito', 'pizza']):
            # Count based on typical batch sizes
            if 'party' in text or 'family' in text:
                return 8
            else:
                return 4  # Typical batch
        
        # Baked goods
        if any(kw in text for kw in ['muffin', 'cookie', 'biscuit', 'roll', 'bun']):
            # These are typically made in batches of 12-24
            return 12
        
        # Bread/loaf
        if 'bread' in text or 'loaf' in text:
            return 8  # Typical loaf
        
        return None
    
    def default_serving_estimate(self, recipe):
        """Default serving estimate when other methods fail"""
        # Conservative default
        return 4
    
    def update_recipe_servings(self, recipe, new_servings):
        """Update recipe servings and recalculate totals from per-serving values"""
        if new_servings <= 0:
            logger.warning(f"⚠️  Recipe {recipe.id} has invalid servings {new_servings}, skipping")
            return
        
        old_servings = recipe.servings or 1
        
        # Only update if servings changed
        if old_servings == new_servings:
            # Still recalculate totals to ensure consistency
            self.recalculate_totals(recipe, new_servings)
            return
        
        recipe.servings = new_servings
        
        # Recalculate totals from per-serving values (matching import_500_correct_recipes.py pattern)
        # Pattern: total = per_serving * servings
        self.recalculate_totals(recipe, new_servings)
        
        # Track distribution
        self.analysis_summary[new_servings] = self.analysis_summary.get(new_servings, 0) + 1
        
        logger.info(f"✅ Updated {recipe.id} ({recipe.title[:50]}): {old_servings} → {new_servings} servings")
        self.updated_count += 1
        self.db.flush()
    
    def recalculate_totals(self, recipe, servings):
        """Recalculate total recipe nutrition from per-serving values"""
        # Pattern from import_500_correct_recipes.py: total = per_serving * servings
        if recipe.per_serving_calories:
            recipe.total_calories = recipe.per_serving_calories * servings
        
        if recipe.per_serving_protein:
            recipe.total_protein = recipe.per_serving_protein * servings
        
        if recipe.per_serving_carbs:
            recipe.total_carbs = recipe.per_serving_carbs * servings
        
        # Handle both per_serving_fat and per_serving_fats
        per_serving_fat = recipe.per_serving_fat or recipe.per_serving_fats
        if per_serving_fat:
            recipe.total_fat = per_serving_fat * servings
        
        if recipe.per_serving_sodium:
            recipe.total_sodium = recipe.per_serving_sodium * servings

if __name__ == "__main__":
    analyzer = RecipeServingAnalyzer()
    analyzer.analyze_and_fix_all_recipes()

