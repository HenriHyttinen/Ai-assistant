#!/usr/bin/env python3
"""
Comprehensive Ingredient Quantity Fix

This script performs a comprehensive audit and fix of all ingredient quantities:
1. Converts any remaining imperial units in unit field to grams
2. Extracts and fixes quantities from ingredient names (e.g., "5-ounce", "1lb 2oz")
3. Fixes suspiciously low quantities that don't match ingredient names
4. Handles complex cases like "14 1/2-ounce", "13.5- to 14-ounce", etc.
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

class ComprehensiveIngredientFixer:
    def __init__(self):
        self.db = SessionLocal()
        self.fixed_count = 0
        self.converted_units = 0
        self.fixed_quantities = 0
        
    def convert_imperial_to_grams(self, quantity, unit):
        """Convert imperial units to grams"""
        unit = unit.lower().strip()
        
        if unit in ['oz', 'ounce', 'ounces']:
            return quantity * 28.3495
        elif unit in ['lb', 'lbs', 'pound', 'pounds']:
            return quantity * 453.592
        elif unit in ['cup', 'cups']:
            return quantity * 240  # 1 cup = 240ml (approximate)
        elif unit in ['tbsp', 'tablespoon', 'tablespoons']:
            return quantity * 15  # 1 tbsp = 15ml
        elif unit in ['tsp', 'teaspoon', 'teaspoons']:
            return quantity * 5  # 1 tsp = 5ml
        elif unit in ['g', 'gram', 'grams']:
            return quantity
        elif unit in ['kg', 'kilogram']:
            return quantity * 1000
        elif unit in ['ml', 'milliliter', 'milliliters']:
            return quantity  # 1ml ≈ 1g for most ingredients
        elif unit in ['l', 'liter', 'liters']:
            return quantity * 1000
        
        return quantity  # Unknown unit, return as-is
    
    def extract_quantity_from_name(self, ingredient_name):
        """Extract quantity from ingredient name, handling complex cases"""
        if not ingredient_name:
            return None
        
        # Pattern: "X-Y oz" or "X to Y oz" - use the larger value
        match = re.search(r'(\d+(?:\.\d+)?)\s*-\s*to\s*(\d+(?:\.\d+)?)\s*-\s*(?:ounce|oz)', ingredient_name, re.IGNORECASE)
        if match:
            return max(float(match.group(1)), float(match.group(2))) * 28.3495, 'g'
        
        # Pattern: "X lb Y oz" or "(Xlb Yoz)" - convert to grams
        match = re.search(r'(?:\(|^)(\d+)\s*(?:lb|lbs|pound|pounds)\s*(\d+)\s*(?:oz|ounce|ounces)', ingredient_name, re.IGNORECASE)
        if match:
            lbs = float(match.group(1))
            oz = float(match.group(2))
            total_g = (lbs * 453.592) + (oz * 28.3495)
            return total_g, 'g'
        
        # Pattern: "X 1/2-ounce" or "X Y/Z-ounce"
        match = re.search(r'(\d+)\s+(\d+)/(\d+)\s*-\s*(?:ounce|oz)', ingredient_name, re.IGNORECASE)
        if match:
            whole = float(match.group(1))
            num = float(match.group(2))
            denom = float(match.group(3))
            oz = whole + (num / denom)
            return oz * 28.3495, 'g'
        
        # Pattern: "X.Y-ounce" (e.g., "13.5-ounce")
        match = re.search(r'(\d+\.\d+)\s*-\s*(?:ounce|oz)', ingredient_name, re.IGNORECASE)
        if match:
            oz = float(match.group(1))
            return oz * 28.3495, 'g'
        
        # Pattern: "X-ounce" or "X oz" or "(X-oz)"
        match = re.search(r'\(?(\d+(?:\.\d+)?)\s*-\s*(?:oz|ounce|ounces)\)?', ingredient_name, re.IGNORECASE)
        if match:
            oz = float(match.group(1))
            return oz * 28.3495, 'g'
        
        match = re.search(r'\b(\d+(?:\.\d+)?)\s*(?:oz|ounce|ounces)\b', ingredient_name, re.IGNORECASE)
        if match:
            oz = float(match.group(1))
            return oz * 28.3495, 'g'
        
        # Pattern: "X lb" or "X pound"
        match = re.search(r'\b(\d+(?:\.\d+)?)\s*(?:lb|lbs|pound|pounds)\b', ingredient_name, re.IGNORECASE)
        if match:
            lb = float(match.group(1))
            return lb * 453.592, 'g'
        
        return None
    
    def should_fix_quantity(self, ingredient, expected_value):
        """Check if ingredient quantity needs fixing"""
        if expected_value is None:
            return False
        
        expected_g, expected_unit = expected_value
        current_g = ingredient.quantity if ingredient.unit.lower() in ['g', 'gram', 'grams'] else None
        
        # If we can't determine current grams, check if unit needs conversion
        if current_g is None:
            current_g = self.convert_imperial_to_grams(ingredient.quantity, ingredient.unit)
        
        # Fix if current is way off (less than 70% or more than 150% of expected)
        if current_g < expected_g * 0.7 or current_g > expected_g * 1.5:
            return True
        
        return False
    
    def fix_ingredient(self, ingredient):
        """Fix a single ingredient"""
        updated = False
        ingredient_name = ingredient.ingredient.name if ingredient.ingredient else ""
        
        # Step 1: Convert imperial units in unit field to grams
        imperial_units = ['oz', 'ounce', 'ounces', 'lb', 'lbs', 'pound', 'pounds', 
                         'cup', 'cups', 'tbsp', 'tablespoon', 'tablespoons', 
                         'tsp', 'teaspoon', 'teaspoons']
        
        if any(imp in ingredient.unit.lower() for imp in imperial_units):
            old_quantity = ingredient.quantity
            old_unit = ingredient.unit
            new_quantity = self.convert_imperial_to_grams(ingredient.quantity, ingredient.unit)
            
            ingredient.quantity = round(new_quantity, 1)
            ingredient.unit = 'g'
            
            recipe_title = ingredient.recipe.title if ingredient.recipe else "Unknown"
            logger.info(f"✅ Converted unit: {recipe_title[:50]}")
            logger.info(f"   {ingredient_name[:60]}")
            logger.info(f"   {old_quantity} {old_unit} → {ingredient.quantity}g")
            
            self.converted_units += 1
            updated = True
        
        # Step 2: Extract quantity from name and fix if needed
        expected_value = self.extract_quantity_from_name(ingredient_name)
        
        if expected_value and self.should_fix_quantity(ingredient, expected_value):
            expected_g, expected_unit = expected_value
            
            old_quantity = ingredient.quantity
            old_unit = ingredient.unit
            
            # Convert current to grams for comparison
            current_g = ingredient.quantity
            if ingredient.unit.lower() not in ['g', 'gram', 'grams']:
                current_g = self.convert_imperial_to_grams(ingredient.quantity, ingredient.unit)
            
            # Only fix if way off
            if abs(current_g - expected_g) > expected_g * 0.3:
                ingredient.quantity = round(expected_g, 1)
                ingredient.unit = 'g'
                
                recipe_title = ingredient.recipe.title if ingredient.recipe else "Unknown"
                logger.info(f"✅ Fixed quantity from name: {recipe_title[:50]}")
                logger.info(f"   {ingredient_name[:60]}")
                logger.info(f"   {old_quantity} {old_unit} → {ingredient.quantity}g")
                
                self.fixed_quantities += 1
                updated = True
        
        return updated
    
    def fix_all_ingredients(self):
        """Fix all ingredients"""
        logger.info("🔍 Starting comprehensive ingredient fix...")
        
        recipes = self.db.query(Recipe).all()
        logger.info(f"Found {len(recipes)} recipes to check")
        
        for recipe in recipes:
            for ingredient in recipe.ingredients:
                if self.fix_ingredient(ingredient):
                    self.fixed_count += 1
        
        # Commit changes
        self.db.commit()
        
        logger.info(f"🎉 Fix complete!")
        logger.info(f"   Fixed {self.fixed_count} ingredients")
        logger.info(f"   Converted {self.converted_units} imperial units")
        logger.info(f"   Fixed {self.fixed_quantities} quantities from names")
        
        return self.fixed_count
    
    def verify_fixes(self):
        """Verify all fixes were successful"""
        logger.info("🔍 Verifying fixes...")
        
        recipes = self.db.query(Recipe).all()
        remaining_issues = []
        imperial_units = ['oz', 'ounce', 'ounces', 'lb', 'lbs', 'pound', 'pounds', 
                         'cup', 'cups', 'tbsp', 'tablespoon', 'tablespoons', 
                         'tsp', 'teaspoon', 'teaspoons']
        
        for recipe in recipes:
            for ingredient in recipe.ingredients:
                ingredient_name = ingredient.ingredient.name if ingredient.ingredient else ""
                
                # Check for imperial units in unit field
                if any(imp in ingredient.unit.lower() for imp in imperial_units):
                    remaining_issues.append({
                        'recipe': recipe.title,
                        'ingredient': ingredient_name,
                        'quantity': ingredient.quantity,
                        'unit': ingredient.unit,
                        'issue': 'imperial_unit_in_field'
                    })
        
        if remaining_issues:
            logger.warning(f"⚠️  Found {len(remaining_issues)} ingredients with remaining issues:")
            for issue in remaining_issues[:5]:
                logger.warning(f"   {issue['recipe'][:50]}: {issue['quantity']} {issue['unit']} - {issue['ingredient'][:50]}")
        else:
            logger.info("✅ All imperial units have been converted")
    
    def close(self):
        """Close database connection"""
        self.db.close()

def main():
    """Main function"""
    fixer = ComprehensiveIngredientFixer()
    
    try:
        fixed_count = fixer.fix_all_ingredients()
        fixer.verify_fixes()
        
        logger.info(f"🎉 SUCCESS!")
        logger.info(f"   Fixed {fixed_count} ingredients")
        
    except Exception as e:
        logger.error(f"❌ Fix failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        fixer.close()

if __name__ == "__main__":
    main()

