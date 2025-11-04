#!/usr/bin/env python3
"""
Fix All Recipe Ingredient Quantities

This script comprehensively fixes ingredient quantities by:
1. Properly parsing units like "slices", "pieces", "cups", etc.
2. Converting to grams based on realistic weights
3. Adding missing ingredient nutrition data
4. Recalculating all recipe nutrition from corrected ingredients
"""

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import Recipe, RecipeIngredient, Ingredient
from typing import Dict, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Standard weights for common units
STANDARD_WEIGHTS = {
    # Bread & Sandwiches
    'slice': {
        'bread': 30, 'rye bread': 30, 'white bread': 30, 'wheat bread': 30,
        'toast': 30, 'french bread': 30, 'roll': 50, 'bun': 50,
        'ham': 15, 'turkey': 15, 'chicken': 20, 'beef': 20,
        'cheese': 20, 'swiss cheese': 20, 'cheddar cheese': 20, 'monterey jack': 20,
    },
    # Meat & Protein
    'piece': {
        'chicken breast': 150, 'chicken thigh': 100, 'chicken wing': 50,
        'pork chop': 150, 'steak': 200, 'fish fillet': 150,
        'sausage': 100, 'patty': 100,
    },
    'halves': {
        'chicken breast': 75,  # Each half
    },
    # Vegetables & Fruits
    'small': {
        'onion': 100, 'potato': 150, 'tomato': 100,
        'cucumber': 100, 'apple': 100,
    },
    'medium': {
        'onion': 150, 'potato': 200, 'tomato': 150,
        'cucumber': 150, 'apple': 150, 'orange': 150,
    },
    'large': {
        'onion': 200, 'potato': 300, 'tomato': 200,
        'cucumber': 200, 'apple': 200, 'orange': 200,
    },
    # Standard conversions
    'cup': 240,  # ml
    'tablespoon': 15,  # ml
    'teaspoon': 5,  # ml
    'pound': 453.6,  # grams
    'ounce': 28.35,  # grams
}

class IngredientQuantityFixer:
    def __init__(self):
        self.db = SessionLocal()
        self.fixed_count = 0
        self.recalculated_count = 0
        self.missing_ingredients = []
        
    def fix_all_recipes(self):
        """Fix all recipe ingredient quantities"""
        logger.info("🔍 Starting comprehensive ingredient quantity fix...")
        
        recipes = self.db.query(Recipe).all()
        logger.info(f"Found {len(recipes)} recipes to process")
        
        for i, recipe in enumerate(recipes, 1):
            try:
                fixed = self._fix_recipe_ingredients(recipe)
                if fixed:
                    self.fixed_count += 1
                    
                    # Recalculate nutrition
                    self._recalculate_recipe_nutrition(recipe)
                    self.recalculated_count += 1
                
                if i % 50 == 0:
                    self.db.commit()
                    logger.info(f"Progress: {i}/{len(recipes)} recipes processed...")
                    
            except Exception as e:
                logger.error(f"Error processing recipe {recipe.title}: {e}")
                continue
        
        self.db.commit()
        
        logger.info(f"\n📊 Summary:")
        logger.info(f"   Recipes fixed: {self.fixed_count}/{len(recipes)}")
        logger.info(f"   Recipes recalculated: {self.recalculated_count}/{len(recipes)}")
        logger.info(f"   Missing ingredients to add: {len(self.missing_ingredients)}")
    
    def _fix_recipe_ingredients(self, recipe: Recipe) -> bool:
        """Fix ingredient quantities for a single recipe"""
        fixed = False
        
        for ri in recipe.ingredients:
            ing = ri.ingredient
            if not ing:
                continue
            
            original_qty = ri.quantity or 0
            unit = ri.unit or 'g'
            if unit is None:
                unit = 'g'
            unit_str = str(unit).lower().strip()
            name = ing.name.lower()
            
            # Check if this ingredient needs fixing
            needs_fix = False
            
            # Check for unit types that need conversion (slices, pieces, etc.)
            units_needing_conversion = ['slice', 'slices', 'piece', 'pieces', 'thin', 'small', 'medium', 'large', 'halves', 'halve']
            if unit_str in units_needing_conversion:
                needs_fix = True
            # Also check for very small quantities that might be parsing errors
            elif original_qty > 0 and original_qty < 10:
                # But skip if it's a small amount of spices/condiments
                spice_keywords = ['salt', 'pepper', 'spice', 'herb', 'garlic', 'cumin', 'cayenne', 'dill']
                if not any(kw in name for kw in spice_keywords):
                    needs_fix = True
            
            if needs_fix:
                # First try to parse quantity from ingredient name (more accurate)
                corrected_qty = self._parse_quantity_from_name(ing.name, unit_str)
                
                # If we couldn't parse from name, estimate from unit
                if not corrected_qty:
                    corrected_qty = self._estimate_from_unit(ing.name, original_qty, unit_str)
                
                # Apply fix if we got a reasonable correction
                if corrected_qty and corrected_qty > original_qty * 1.2:  # At least 20% increase
                    ri.quantity = corrected_qty
                    ri.unit = 'g'
                    fixed = True
                    if original_qty < 10 or corrected_qty > original_qty * 2:
                        logger.info(f"✅ Fixed {ing.name[:40]}: {original_qty:.2f}{unit} → {corrected_qty:.2f}g")
            
            # Check for ingredients with no nutrition data
            if not ing.calories or ing.calories == 0:
                # Try to add nutrition data for common ingredients
                self._add_missing_ingredient_nutrition(ing)
        
        return fixed
    
    def _parse_quantity_from_name(self, ingredient_name: str, unit: str) -> Optional[float]:
        """Extract quantity from ingredient name"""
        name_lower = ingredient_name.lower()
        
        # Look for number patterns
        # "2 slices bread" → 2 slices
        # "4 chicken breast halves" → 4 halves
        # "1/2 cup flour" → 0.5 cup
        
        # Check for slices
        slice_match = re.search(r'(\d+(?:\s+\d+/\d+)?)\s*slice', name_lower)
        if slice_match:
            qty = self._parse_number(slice_match.group(1))
            ingredient_type = self._extract_ingredient_type(name_lower)
            weight_per_slice = STANDARD_WEIGHTS.get('slice', {}).get(ingredient_type, 30)
            return qty * weight_per_slice
        
        # Check for pieces/halves
        piece_match = re.search(r'(\d+(?:\s+\d+/\d+)?)\s*(?:piece|pieces|halves|halve)', name_lower)
        if piece_match:
            qty = self._parse_number(piece_match.group(1))
            ingredient_type = self._extract_ingredient_type(name_lower)
            weight_per_piece = STANDARD_WEIGHTS.get('piece', {}).get(ingredient_type, 100)
            return qty * weight_per_piece
        
        # Check for cups, tablespoons, etc.
        vol_match = re.search(r'(\d+(?:\s+\d+/\d+)?)\s*(cup|cups|tbsp|tablespoon|tsp|teaspoon)', name_lower)
        if vol_match:
            qty = self._parse_number(vol_match.group(1))
            vol_unit = vol_match.group(2)
            multiplier = STANDARD_WEIGHTS.get(vol_unit, 240)
            return qty * multiplier
        
        return None
    
    def _parse_number(self, num_str: str) -> float:
        """Parse number string including fractions"""
        num_str = num_str.strip()
        
        # Handle fractions like "1 1/2" or "1/2"
        if ' ' in num_str:
            parts = num_str.split()
            if len(parts) == 2 and '/' in parts[1]:
                whole = float(parts[0])
                frac = parts[1].split('/')
                return whole + (float(frac[0]) / float(frac[1]))
        
        if '/' in num_str:
            frac = num_str.split('/')
            return float(frac[0]) / float(frac[1])
        
        return float(num_str)
    
    def _extract_ingredient_type(self, name: str) -> str:
        """Extract ingredient type from name"""
        name_lower = name.lower()
        
        # Check for bread types
        if any(b in name_lower for b in ['bread', 'toast', 'roll', 'bun']):
            if 'rye' in name_lower:
                return 'rye bread'
            return 'bread'
        
        # Check for cheese types
        if 'cheese' in name_lower:
            if 'swiss' in name_lower:
                return 'swiss cheese'
            elif 'cheddar' in name_lower:
                return 'cheddar cheese'
            elif 'monterey' in name_lower or 'jack' in name_lower:
                return 'monterey jack'
            return 'cheese'
        
        # Check for meat types
        if any(m in name_lower for m in ['ham', 'turkey', 'chicken', 'beef']):
            if 'ham' in name_lower:
                return 'ham'
            elif 'chicken' in name_lower:
                return 'chicken'
            elif 'turkey' in name_lower:
                return 'turkey'
            return 'ham'  # Default
        
        return 'bread'  # Default fallback
    
    def _estimate_from_unit(self, ingredient_name: str, current_qty: float, unit: str) -> Optional[float]:
        """Estimate quantity from unit type"""
        name_lower = ingredient_name.lower()
        unit_lower = unit.lower()
        
        # Handle slices
        if unit_lower in ['slice', 'slices']:
            ingredient_type = self._extract_ingredient_type(name_lower)
            weight_per_slice = STANDARD_WEIGHTS.get('slice', {}).get(ingredient_type, 30)
            return current_qty * weight_per_slice
        
        # Handle pieces/halves
        if unit_lower in ['piece', 'pieces', 'halves', 'halve']:
            ingredient_type = self._extract_ingredient_type(name_lower)
            weight_per_piece = STANDARD_WEIGHTS.get('piece', {}).get(ingredient_type, 100)
            if 'halves' in unit_lower or 'halve' in unit_lower:
                weight_per_piece = STANDARD_WEIGHTS.get('halves', {}).get(ingredient_type, 75)
            return current_qty * weight_per_piece
        
        # Handle size descriptors
        if unit_lower in ['small', 'medium', 'large', 'thin']:
            weight_map = {
                'small': STANDARD_WEIGHTS.get('small', {}),
                'medium': STANDARD_WEIGHTS.get('medium', {}),
                'large': STANDARD_WEIGHTS.get('large', {}),
                'thin': {'ham': 15, 'cheese': 20, 'bread': 20}  # Thin slices
            }
            
            if unit_lower in weight_map:
                weights = weight_map[unit_lower]
                ingredient_type = self._extract_ingredient_type(name_lower)
                weight_per_unit = weights.get(ingredient_type, 100)
                return current_qty * weight_per_unit
        
        # Handle volume units
        if unit_lower in ['cup', 'cups', 'tbsp', 'tablespoon', 'tablespoons', 'tsp', 'teaspoon', 'teaspoons', 'ml']:
            if unit_lower in ['cup', 'cups']:
                multiplier = STANDARD_WEIGHTS['cup']
            elif unit_lower in ['tbsp', 'tablespoon', 'tablespoons']:
                multiplier = STANDARD_WEIGHTS['tablespoon']
            elif unit_lower in ['tsp', 'teaspoon', 'teaspoons']:
                multiplier = STANDARD_WEIGHTS['teaspoon']
            else:  # ml
                multiplier = 1  # Already in grams/ml
            return current_qty * multiplier
        
        return None
    
    def _add_missing_ingredient_nutrition(self, ingredient: Ingredient):
        """Add nutrition data for missing ingredients"""
        name_lower = ingredient.name.lower()
        
        # Common missing ingredients
        nutrition_map = {
            'orzo': {'calories': 131, 'protein': 5, 'carbs': 25, 'fats': 1.1, 'fiber': 1.8},
            'panko': {'calories': 394, 'protein': 13, 'carbs': 75, 'fats': 2, 'fiber': 2.5},
            'sausage': {'calories': 301, 'protein': 13, 'carbs': 2, 'fats': 27},
            'bratwurst': {'calories': 301, 'protein': 13, 'carbs': 2, 'fats': 27},
            'mirin': {'calories': 240, 'protein': 0, 'carbs': 45, 'fats': 0},
            'rice wine': {'calories': 83, 'protein': 0, 'carbs': 5, 'fats': 0},
        }
        
        for key, nutrition in nutrition_map.items():
            if key in name_lower:
                ingredient.calories = nutrition.get('calories', 0)
                ingredient.protein = nutrition.get('protein', 0)
                ingredient.carbs = nutrition.get('carbs', 0)
                ingredient.fats = nutrition.get('fats', 0)
                ingredient.fiber = nutrition.get('fiber', 0)
                self.db.add(ingredient)
                logger.debug(f"Added nutrition data for {ingredient.name}")
                break
    
    def _recalculate_recipe_nutrition(self, recipe: Recipe):
        """Recalculate recipe nutrition from ingredients"""
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fats = 0
        total_fiber = 0
        total_sodium = 0
        
        for ri in recipe.ingredients:
            ing = ri.ingredient
            if not ing:
                continue
            
            qty = ri.quantity or 0
            if qty <= 0:
                continue
            
            multiplier = qty / 100.0
            
            total_calories += (ing.calories or 0) * multiplier
            total_protein += (ing.protein or 0) * multiplier
            total_carbs += (ing.carbs or 0) * multiplier
            total_fats += (ing.fats or 0) * multiplier
            total_fiber += (ing.fiber or 0) * multiplier
            total_sodium += (ing.sodium or 0) * multiplier
        
        servings = recipe.servings or 1
        if servings <= 0:
            servings = 1
            recipe.servings = 1
        
        # Update recipe nutrition
        recipe.total_calories = round(total_calories, 1)
        recipe.total_protein = round(total_protein, 1)
        recipe.total_carbs = round(total_carbs, 1)
        recipe.total_fat = round(total_fats, 1)
        
        recipe.per_serving_calories = round(total_calories / servings, 1)
        recipe.per_serving_protein = round(total_protein / servings, 1)
        recipe.per_serving_carbs = round(total_carbs / servings, 1)
        recipe.per_serving_fat = round(total_fats / servings, 1)
        recipe.per_serving_sodium = round(total_sodium / servings, 1)
        
        self.db.add(recipe)
    
    def close(self):
        """Close database connection"""
        self.db.close()

def main():
    """Main function"""
    fixer = IngredientQuantityFixer()
    
    try:
        fixer.fix_all_recipes()
        logger.info(f"\n🎉 Ingredient quantity fix complete!")
        
    except Exception as e:
        logger.error(f"❌ Fix failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        fixer.close()

if __name__ == "__main__":
    main()

