#!/usr/bin/env python3
"""
Fix Ingredient Quantities from Names

This script fixes ingredients where the quantity is embedded in the ingredient name
(e.g., "5-ounce fish fillet" should have quantity 141.75g, not 6g).

It extracts ounce values from ingredient names like:
- "5-ounce fish fillet"
- "6 oz package"
- "(8-oz) can"
- "10 ounces of flour"

And converts them to proper grams in the quantity field.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from database import SessionLocal
from models.recipe import Recipe, RecipeIngredient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IngredientQuantityFixer:
    def __init__(self):
        self.db = SessionLocal()
        self.fixed_count = 0
        self.issues_found = []
        
    def extract_ounce_from_name(self, ingredient_name):
        """Extract ounce value from ingredient name"""
        if not ingredient_name:
            return None
        
        # Patterns to match:
        # "5-ounce" -> 5
        # "5 ounce" -> 5
        # "(6-oz)" -> 6
        # "10 ounces" -> 10
        # "14 1/2-ounce" -> 14.5
        # "13.5- to 14-ounce" -> 14 (use the larger value)
        
        patterns = [
            r'\((\d+(?:\.\d+)?)\s*-\s*oz\)',  # (6-oz)
            r'\((\d+(?:\.\d+)?)\s*oz\)',      # (6 oz)
            r'(\d+(?:\.\d+)?)\s*-\s*to\s*(\d+(?:\.\d+)?)\s*-\s*ounce',  # 13.5- to 14-ounce -> use 14
            r'(\d+(?:\s+\d+/\d+)?)\s*-\s*ounce',  # 5-ounce, 14 1/2-ounce
            r'(\d+(?:\.\d+)?)\s*-\s*oz\b',    # 5-oz
            r'(\d+(?:\s+\d+/\d+)?)\s+ounces?',  # 10 ounces, 10 ounce
            r'(\d+(?:\.\d+)?)\s*oz\b',        # 10 oz
            r'about\s+(\d+(?:\.\d+)?)\s+ounces?',  # about 10 ounces
        ]
        
        for pattern in patterns:
            match = re.search(pattern, ingredient_name, re.IGNORECASE)
            if match:
                # Handle range (e.g., "13.5- to 14-ounce")
                if len(match.groups()) == 2:
                    value1 = float(match.group(1))
                    value2 = float(match.group(2))
                    return max(value1, value2)
                
                # Handle fractions (e.g., "14 1/2-ounce")
                quantity_str = match.group(1)
                if ' ' in quantity_str and '/' in quantity_str:
                    # Handle "14 1/2" -> 14.5
                    parts = quantity_str.split()
                    whole = float(parts[0])
                    frac = parts[1]
                    num, denom = map(float, frac.split('/'))
                    return whole + (num / denom)
                
                return float(match.group(1))
        
        return None
    
    def should_fix_ingredient(self, ingredient, ounce_value):
        """Check if ingredient needs fixing"""
        expected_grams = ounce_value * 28.35
        
        # Current quantity is way too low (less than 50% of expected)
        if ingredient.unit == 'g' and ingredient.quantity < expected_grams * 0.5:
            return True
        
        # Current quantity is 1-10g but should be much more
        if ingredient.unit == 'g' and ingredient.quantity <= 10 and expected_grams > 50:
            return True
        
        return False
    
    def fix_ingredient(self, ingredient, ounce_value):
        """Fix ingredient quantity"""
        expected_grams = ounce_value * 28.35
        
        old_quantity = ingredient.quantity
        old_unit = ingredient.unit
        
        ingredient.quantity = round(expected_grams, 1)
        ingredient.unit = 'g'
        
        ingredient_name = ingredient.ingredient.name if ingredient.ingredient else "Unknown"
        recipe_title = ingredient.recipe.title if ingredient.recipe else "Unknown"
        
        logger.info(f"✅ Fixed: {recipe_title[:50]}")
        logger.info(f"   {ingredient_name[:60]}")
        logger.info(f"   {old_quantity} {old_unit} → {ingredient.quantity}g (from {ounce_value} oz)")
        
        self.fixed_count += 1
        return True
    
    def fix_all_ingredients(self):
        """Find and fix all ingredients with quantity in name"""
        logger.info("🔍 Searching for ingredients with ounce values in names...")
        
        recipes = self.db.query(Recipe).all()
        issues_found = []
        
        for recipe in recipes:
            for ingredient in recipe.ingredients:
                ingredient_name = ingredient.ingredient.name if ingredient.ingredient else ""
                
                # Extract ounce value from name
                ounce_value = self.extract_ounce_from_name(ingredient_name)
                
                if ounce_value:
                    # Check if it needs fixing
                    if self.should_fix_ingredient(ingredient, ounce_value):
                        issues_found.append({
                            'recipe': recipe.title,
                            'ingredient': ingredient_name,
                            'stored': f"{ingredient.quantity} {ingredient.unit}",
                            'expected': f"{ounce_value * 28.35:.1f}g",
                            'ounce_value': ounce_value,
                            'ingredient_obj': ingredient
                        })
        
        logger.info(f"Found {len(issues_found)} ingredients that need fixing")
        
        # Fix ingredients
        for issue in issues_found:
            self.fix_ingredient(issue['ingredient_obj'], issue['ounce_value'])
        
        # Commit changes
        self.db.commit()
        
        logger.info(f"🎉 Fixed {self.fixed_count} ingredients")
        
        return self.fixed_count, len(issues_found)
    
    def verify_fixes(self):
        """Verify the fixes were successful"""
        logger.info("🔍 Verifying fixes...")
        
        recipes = self.db.query(Recipe).all()
        remaining_issues = []
        
        for recipe in recipes:
            for ingredient in recipe.ingredients:
                ingredient_name = ingredient.ingredient.name if ingredient.ingredient else ""
                ounce_value = self.extract_ounce_from_name(ingredient_name)
                
                if ounce_value:
                    expected_grams = ounce_value * 28.35
                    if ingredient.unit == 'g' and abs(ingredient.quantity - expected_grams) > expected_grams * 0.2:
                        remaining_issues.append({
                            'recipe': recipe.title,
                            'ingredient': ingredient_name,
                            'stored': f"{ingredient.quantity}g",
                            'expected': f"{expected_grams:.1f}g"
                        })
        
        if remaining_issues:
            logger.warning(f"⚠️  Found {len(remaining_issues)} ingredients that may still need fixing:")
            for issue in remaining_issues[:5]:
                logger.warning(f"   {issue['recipe'][:50]}: {issue['ingredient'][:50]}")
                logger.warning(f"      Stored: {issue['stored']}, Expected: {issue['expected']}")
        else:
            logger.info("✅ All ounce values in names have been properly converted")
    
    def close(self):
        """Close database connection"""
        self.db.close()

def main():
    """Main function to fix ingredient quantities"""
    fixer = IngredientQuantityFixer()
    
    try:
        fixed_count, issues_found = fixer.fix_all_ingredients()
        fixer.verify_fixes()
        
        logger.info(f"🎉 SUCCESS!")
        logger.info(f"   Fixed {fixed_count} out of {issues_found} problematic ingredients")
        
    except Exception as e:
        logger.error(f"❌ Fix failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        fixer.close()

if __name__ == "__main__":
    main()

