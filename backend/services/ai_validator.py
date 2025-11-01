#!/usr/bin/env python3
"""
AI Recipe Validator Service

This service validates and corrects AI-generated recipes using the ingredient database.
It acts as a guardrail against AI hallucinations by:
1. Matching AI ingredient names to database ingredients
2. Validating nutrition values against ingredient calculations
3. Correcting invalid or impossible values
4. Enriching AI recipes with accurate micronutrients
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from models.recipe import Ingredient, Recipe
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class AIRecipeValidator:
    """
    Validates and corrects AI-generated recipes using the ingredient database
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.ingredient_cache = {}  # Cache ingredient lookups
        self.match_threshold = 0.7  # Similarity threshold for ingredient matching
    
    def validate_and_correct_recipe(
        self, 
        ai_recipe: Dict[str, Any],
        recalculate_nutrition: bool = True,
        correct_ingredient_names: bool = True
    ) -> Dict[str, Any]:
        """
        Validate and correct an AI-generated recipe
        
        Args:
            ai_recipe: AI-generated recipe dictionary
            recalculate_nutrition: If True, recalculate nutrition from ingredients
            correct_ingredient_names: If True, match and correct ingredient names
            
        Returns:
            Validated and corrected recipe dictionary
        """
        try:
            corrected_recipe = ai_recipe.copy()
            
            # Step 1: Validate and correct ingredient names
            if correct_ingredient_names:
                corrected_recipe = self._validate_ingredient_names(corrected_recipe)
            
            # Step 2: Recalculate nutrition from ingredients
            if recalculate_nutrition:
                corrected_recipe = self._recalculate_nutrition_from_ingredients(corrected_recipe)
            
            # Step 3: Validate nutrition values are realistic
            corrected_recipe = self._validate_nutrition_realism(corrected_recipe)
            
            # Step 4: Enrich with micronutrients if available
            corrected_recipe = self._enrich_with_micronutrients(corrected_recipe)
            
            return corrected_recipe
            
        except Exception as e:
            logger.error(f"Error validating AI recipe: {e}")
            return ai_recipe  # Return original if validation fails
    
    def _validate_ingredient_names(self, recipe: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate ingredient names against database and correct if needed
        """
        ingredients = recipe.get('ingredients', [])
        if not ingredients:
            return recipe
        
        corrected_ingredients = []
        corrections_made = []
        
        for ingredient in ingredients:
            ing_name = ingredient.get('name', '').strip()
            if not ing_name:
                continue
            
            # Try to find matching ingredient in database
            matched_ingredient = self._find_matching_ingredient(ing_name)
            
            if matched_ingredient:
                # Use database ingredient name for consistency
                corrected_ingredient = ingredient.copy()
                corrected_ingredient['name'] = matched_ingredient.name
                corrected_ingredient['database_id'] = matched_ingredient.id
                corrected_ingredients.append(corrected_ingredient)
                
                if matched_ingredient.name.lower() != ing_name.lower():
                    corrections_made.append(f"{ing_name} → {matched_ingredient.name}")
            else:
                # Keep original if no match found
                corrected_ingredients.append(ingredient)
        
        recipe['ingredients'] = corrected_ingredients
        
        if corrections_made:
            logger.info(f"🔍 Corrected {len(corrections_made)} ingredient names: {', '.join(corrections_made)}")
        
        return recipe
    
    def _find_matching_ingredient(self, name: str) -> Optional[Ingredient]:
        """
        Find matching ingredient in database using fuzzy matching
        """
        name_lower = name.lower().strip()
        
        # Check cache first
        if name_lower in self.ingredient_cache:
            return self.ingredient_cache[name_lower]
        
        # Try exact match first
        ingredient = self.db.query(Ingredient).filter(
            func.lower(Ingredient.name) == name_lower
        ).first()
        
        if ingredient:
            self.ingredient_cache[name_lower] = ingredient
            return ingredient
        
        # Try partial match using SQLAlchemy ILIKE for case-insensitive matching
        ingredient = self.db.query(Ingredient).filter(
            or_(
                func.lower(Ingredient.name).contains(name_lower),
                Ingredient.name.ilike(f'%{name_lower}%')
            )
        ).first()
        
        if ingredient:
            self.ingredient_cache[name_lower] = ingredient
            return ingredient
        
        # Try fuzzy matching
        all_ingredients = self.db.query(Ingredient).filter(
            Ingredient.calories > 0  # Only match ingredients with data
        ).limit(1000).all()
        
        best_match = None
        best_score = 0
        
        for ing in all_ingredients:
            score = self._similarity(name_lower, ing.name.lower())
            if score > best_score and score >= self.match_threshold:
                best_score = score
                best_match = ing
        
        if best_match:
            self.ingredient_cache[name_lower] = best_match
        
        return best_match
    
    def _similarity(self, a: str, b: str) -> float:
        """Calculate string similarity using SequenceMatcher"""
        return SequenceMatcher(None, a, b).ratio()
    
    def _recalculate_nutrition_from_ingredients(
        self, 
        recipe: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Recalculate nutrition values from ingredients using database
        This overrides any AI-hallucinated nutrition values
        """
        ingredients = recipe.get('ingredients', [])
        if not ingredients:
            return recipe
        
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fats = 0
        total_fiber = 0
        total_sodium = 0
        ingredients_with_data = 0
        
        for ingredient in ingredients:
            ing_name = ingredient.get('name', '').strip()
            quantity = ingredient.get('quantity', 0)
            unit = ingredient.get('unit', 'g')
            
            if not ing_name or quantity <= 0:
                continue
            
            # Convert to grams if needed
            quantity_g = self._convert_to_grams(quantity, unit)
            if quantity_g <= 0:
                continue
            
            # Find ingredient in database
            db_ingredient = self._find_matching_ingredient(ing_name)
            
            if db_ingredient and db_ingredient.calories and db_ingredient.calories > 0:
                # Calculate nutrition from database values
                multiplier = quantity_g / 100.0
                
                total_calories += (db_ingredient.calories or 0) * multiplier
                total_protein += (db_ingredient.protein or 0) * multiplier
                total_carbs += (db_ingredient.carbs or 0) * multiplier
                total_fats += (db_ingredient.fats or 0) * multiplier
                total_fiber += (db_ingredient.fiber or 0) * multiplier
                total_sodium += (db_ingredient.sodium or 0) * multiplier
                
                ingredients_with_data += 1
        
        # Only update if we found nutrition data
        if ingredients_with_data > 0:
            servings = recipe.get('servings', 1) or 1
            if servings <= 0:
                servings = 1
            
            # CRITICAL FIX: Calculate PER-SERVING values, not total!
            # Divide by servings to get per-serving nutrition
            per_serving_calories = round(total_calories / servings, 1)
            per_serving_protein = round(total_protein / servings, 1)
            per_serving_carbs = round(total_carbs / servings, 1)
            per_serving_fats = round(total_fats / servings, 1)
            per_serving_fiber = round(total_fiber / servings, 1)
            per_serving_sodium = round(total_sodium / servings, 1)
            
            # Update recipe nutrition - store PER-SERVING values
            nutrition = recipe.get('nutrition', {})
            original_calories = nutrition.get('calories', 0)
            
            nutrition.update({
                'calories': int(per_serving_calories),  # PER-SERVING, not total!
                'protein': round(per_serving_protein, 1),
                'carbs': round(per_serving_carbs, 1),
                'fats': round(per_serving_fats, 1),
                'fiber': round(per_serving_fiber, 1),
                'sodium': round(per_serving_sodium, 1),
                'per_serving_calories': int(per_serving_calories),  # Explicitly store per-serving
                'per_serving_protein': round(per_serving_protein, 1),
                'per_serving_carbs': round(per_serving_carbs, 1),
                'per_serving_fats': round(per_serving_fats, 1)
            })
            
            recipe['nutrition'] = nutrition
            
            # Also update top-level values - use PER-SERVING
            recipe['calories'] = int(per_serving_calories)  # PER-SERVING!
            recipe['protein'] = round(per_serving_protein, 1)
            recipe['carbs'] = round(per_serving_carbs, 1)
            recipe['fats'] = round(per_serving_fats, 1)
            
            # Log significant differences
            if original_calories > 0:
                diff_percent = abs(total_calories - original_calories) / original_calories * 100
                if diff_percent > 20:
                    logger.info(f"📊 Corrected nutrition: {original_calories} → {int(total_calories)} cal "
                              f"({diff_percent:.1f}% difference) for {recipe.get('title', 'recipe')}")
        
        return recipe
    
    def _convert_to_grams(self, quantity: float, unit: str) -> float:
        """Convert quantity to grams"""
        unit_lower = unit.lower().strip()
        
        # Already in grams
        if unit_lower in ['g', 'gram', 'grams']:
            return quantity
        
        # Convert from milliliters (assuming density ~1g/ml for most foods)
        if unit_lower in ['ml', 'milliliter', 'milliliters']:
            return quantity
        
        # Convert from kilograms
        if unit_lower in ['kg', 'kilogram', 'kilograms']:
            return quantity * 1000
        
        # Default: assume grams
        return quantity
    
    def _validate_nutrition_realism(self, recipe: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate that nutrition values are realistic
        Check calories formula: calories = protein*4 + carbs*4 + fats*9
        """
        nutrition = recipe.get('nutrition', {})
        calories = nutrition.get('calories', 0)
        protein = nutrition.get('protein', 0)
        carbs = nutrition.get('carbs', 0)
        fats = nutrition.get('fats', 0)
        
        if calories > 0 and protein >= 0 and carbs >= 0 and fats >= 0:
            calculated_calories = (protein * 4) + (carbs * 4) + (fats * 9)
            
            # Check if difference is significant (>10%)
            if calculated_calories > 0:
                diff_percent = abs(calories - calculated_calories) / calculated_calories * 100
                
                if diff_percent > 10:
                    # Correct calories to match formula
                    corrected_calories = round(calculated_calories, 1)
                    nutrition['calories'] = int(corrected_calories)
                    recipe['nutrition'] = nutrition
                    recipe['calories'] = int(corrected_calories)
                    
                    logger.info(f"🔧 Corrected calories formula: {calories} → {int(corrected_calories)} cal")
        
        return recipe
    
    def _enrich_with_micronutrients(self, recipe: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate and add micronutrients from ingredients
        """
        ingredients = recipe.get('ingredients', [])
        if not ingredients:
            return recipe
        
        micronutrients = {
            'vitamin_c': 0, 'vitamin_d': 0, 'vitamin_b12': 0,
            'iron': 0, 'calcium': 0, 'magnesium': 0,
            'zinc': 0, 'potassium': 0, 'folate': 0
        }
        
        for ingredient in ingredients:
            ing_name = ingredient.get('name', '').strip()
            quantity = ingredient.get('quantity', 0)
            unit = ingredient.get('unit', 'g')
            
            if not ing_name or quantity <= 0:
                continue
            
            quantity_g = self._convert_to_grams(quantity, unit)
            if quantity_g <= 0:
                continue
            
            db_ingredient = self._find_matching_ingredient(ing_name)
            
            if db_ingredient:
                multiplier = quantity_g / 100.0
                
                micronutrients['vitamin_c'] += (db_ingredient.vitamin_c or 0) * multiplier
                micronutrients['vitamin_d'] += (db_ingredient.vitamin_d or 0) * multiplier
                micronutrients['vitamin_b12'] += (db_ingredient.vitamin_b12 or 0) * multiplier
                micronutrients['iron'] += (db_ingredient.iron or 0) * multiplier
                micronutrients['calcium'] += (db_ingredient.calcium or 0) * multiplier
                micronutrients['magnesium'] += (db_ingredient.magnesium or 0) * multiplier
                micronutrients['zinc'] += (db_ingredient.zinc or 0) * multiplier
                micronutrients['potassium'] += (db_ingredient.potassium or 0) * multiplier
                micronutrients['folate'] += (db_ingredient.folate or 0) * multiplier
        
        # Round and add to recipe
        servings = recipe.get('servings', 1) or 1
        if servings <= 0:
            servings = 1
        
        nutrition = recipe.get('nutrition', {})
        for key, value in micronutrients.items():
            if value > 0:
                nutrition[f'per_serving_{key}'] = round(value / servings, 2)
                nutrition[f'total_{key}'] = round(value, 2)
        
        recipe['nutrition'] = nutrition
        
        return recipe

