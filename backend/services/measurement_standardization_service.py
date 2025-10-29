"""
Service for standardizing measurements across the nutrition system
All measurements are standardized to common units: grams (g), milliliters (ml), kilocalories (kcal), and minutes
"""

from typing import Dict, Any, Optional, Union
import logging
import re

logger = logging.getLogger(__name__)

class MeasurementStandardizationService:
    """Service for standardizing measurements to common units"""
    
    # Standard units as per requirement
    STANDARD_UNITS = {
        'weight': 'g',      # grams for solids
        'volume': 'ml',     # milliliters for liquids
        'energy': 'kcal',   # kilocalories for energy
        'time': 'min'       # minutes for time
    }
    
    # Conversion factors to standard units
    CONVERSION_FACTORS = {
        # Weight conversions to grams
        'weight': {
            'g': 1.0,
            'gram': 1.0,
            'grams': 1.0,
            'kg': 1000.0,
            'kilogram': 1000.0,
            'kilograms': 1000.0,
            'oz': 28.3495,
            'ounce': 28.3495,
            'ounces': 28.3495,
            'lb': 453.592,
            'pound': 453.592,
            'pounds': 453.592,
            'piece': 1.0,  # For countable items, keep as is
            'pieces': 1.0,
            'item': 1.0,
            'items': 1.0
        },
        
        # Volume conversions to milliliters
        'volume': {
            'ml': 1.0,
            'milliliter': 1.0,
            'milliliters': 1.0,
            'l': 1000.0,
            'liter': 1000.0,
            'liters': 1000.0,
            'cup': 236.588,
            'cups': 236.588,
            'tbsp': 14.7868,
            'tablespoon': 14.7868,
            'tablespoons': 14.7868,
            'tsp': 4.92892,
            'teaspoon': 4.92892,
            'teaspoons': 4.92892,
            'fl oz': 29.5735,
            'fluid ounce': 29.5735,
            'fluid ounces': 29.5735,
            'pint': 473.176,
            'pints': 473.176,
            'quart': 946.353,
            'quarts': 946.353,
            'gallon': 3785.41,
            'gallons': 3785.41
        },
        
        # Energy conversions to kilocalories
        'energy': {
            'kcal': 1.0,
            'kilocalorie': 1.0,
            'kilocalories': 1.0,
            'cal': 0.001,
            'calorie': 0.001,
            'calories': 0.001,
            'kj': 0.239006,
            'kilojoule': 0.239006,
            'kilojoules': 0.239006
        },
        
        # Time conversions to minutes
        'time': {
            'min': 1.0,
            'minute': 1.0,
            'minutes': 1.0,
            'h': 60.0,
            'hour': 60.0,
            'hours': 60.0,
            'hr': 60.0,
            'hrs': 60.0,
            'sec': 0.0166667,
            'second': 0.0166667,
            'seconds': 0.0166667
        }
    }
    
    # Common ingredient unit mappings
    INGREDIENT_UNIT_MAPPINGS = {
        # Liquids (volume)
        'water': 'ml',
        'milk': 'ml',
        'oil': 'ml',
        'vinegar': 'ml',
        'broth': 'ml',
        'juice': 'ml',
        'wine': 'ml',
        'beer': 'ml',
        'cream': 'ml',
        'sauce': 'ml',
        'soup': 'ml',
        
        # Solids (weight)
        'flour': 'g',
        'sugar': 'g',
        'salt': 'g',
        'butter': 'g',
        'cheese': 'g',
        'meat': 'g',
        'chicken': 'g',
        'beef': 'g',
        'fish': 'g',
        'vegetables': 'g',
        'fruits': 'g',
        'nuts': 'g',
        'seeds': 'g',
        'rice': 'g',
        'pasta': 'g',
        'bread': 'g',
        'chocolate': 'g',
        'honey': 'g',
        'yogurt': 'g',
        
        # Countable items
        'egg': 'piece',
        'eggs': 'piece',
        'onion': 'piece',
        'onions': 'piece',
        'tomato': 'piece',
        'tomatoes': 'piece',
        'potato': 'piece',
        'potatoes': 'piece',
        'apple': 'piece',
        'apples': 'piece',
        'banana': 'piece',
        'bananas': 'piece',
        'lemon': 'piece',
        'lemons': 'piece',
        'lime': 'piece',
        'limes': 'piece',
        'garlic': 'piece',
        'clove': 'piece',
        'cloves': 'piece'
    }
    
    def __init__(self):
        pass
    
    def standardize_ingredient_measurement(self, ingredient_name: str, quantity: float, unit: str) -> Dict[str, Any]:
        """
        Standardize an ingredient measurement to common units
        
        Args:
            ingredient_name: Name of the ingredient
            quantity: Quantity value
            unit: Original unit
            
        Returns:
            Dictionary with standardized measurement
        """
        try:
            # Normalize ingredient name and unit
            normalized_ingredient = ingredient_name.lower().strip()
            normalized_unit = unit.lower().strip()
            
            # Determine if this is a weight or volume ingredient
            measurement_type = self._determine_measurement_type(normalized_ingredient, normalized_unit)
            
            # Convert to standard unit
            if measurement_type in self.CONVERSION_FACTORS:
                if normalized_unit in self.CONVERSION_FACTORS[measurement_type]:
                    conversion_factor = self.CONVERSION_FACTORS[measurement_type][normalized_unit]
                    standardized_quantity = quantity * conversion_factor
                    standardized_unit = self.STANDARD_UNITS[measurement_type]
                else:
                    # Unit not found, try to guess or use original
                    logger.warning(f"Unknown unit '{unit}' for ingredient '{ingredient_name}', using original")
                    standardized_quantity = quantity
                    standardized_unit = unit
            else:
                # Unknown measurement type, keep original
                logger.warning(f"Unknown measurement type for ingredient '{ingredient_name}', using original")
                standardized_quantity = quantity
                standardized_unit = unit
            
            return {
                'original_quantity': quantity,
                'original_unit': unit,
                'standardized_quantity': round(standardized_quantity, 2),
                'standardized_unit': standardized_unit,
                'measurement_type': measurement_type,
                'conversion_applied': normalized_unit != standardized_unit.lower()
            }
            
        except Exception as e:
            logger.error(f"Error standardizing ingredient measurement: {str(e)}")
            return {
                'original_quantity': quantity,
                'original_unit': unit,
                'standardized_quantity': quantity,
                'standardized_unit': unit,
                'measurement_type': 'unknown',
                'conversion_applied': False,
                'error': str(e)
            }
    
    def _determine_measurement_type(self, ingredient_name: str, unit: str) -> str:
        """
        Determine if an ingredient should be measured by weight or volume
        """
        # Check if unit already indicates type
        if unit in self.CONVERSION_FACTORS['weight']:
            return 'weight'
        elif unit in self.CONVERSION_FACTORS['volume']:
            return 'volume'
        elif unit in self.CONVERSION_FACTORS['time']:
            return 'time'
        elif unit in self.CONVERSION_FACTORS['energy']:
            return 'energy'
        
        # Check ingredient name for common patterns
        if ingredient_name in self.INGREDIENT_UNIT_MAPPINGS:
            mapped_unit = self.INGREDIENT_UNIT_MAPPINGS[ingredient_name]
            if mapped_unit in self.CONVERSION_FACTORS['weight']:
                return 'weight'
            elif mapped_unit in self.CONVERSION_FACTORS['volume']:
                return 'volume'
        
        # Default to weight for most ingredients
        return 'weight'
    
    def standardize_recipe_measurements(self, recipe_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize all measurements in a recipe
        """
        try:
            standardized_recipe = recipe_data.copy()
            
            # Standardize ingredients
            if 'ingredients' in recipe_data and isinstance(recipe_data['ingredients'], list):
                standardized_ingredients = []
                for ingredient in recipe_data['ingredients']:
                    if isinstance(ingredient, dict) and 'name' in ingredient and 'quantity' in ingredient:
                        unit = ingredient.get('unit', 'g')
                        standardized = self.standardize_ingredient_measurement(
                            ingredient['name'], 
                            float(ingredient['quantity']), 
                            unit
                        )
                        
                        standardized_ingredient = {
                            **ingredient,
                            'quantity': standardized['standardized_quantity'],
                            'unit': standardized['standardized_unit'],
                            'original_quantity': standardized['original_quantity'],
                            'original_unit': standardized['original_unit'],
                            'measurement_type': standardized['measurement_type']
                        }
                        standardized_ingredients.append(standardized_ingredient)
                    else:
                        standardized_ingredients.append(ingredient)
                
                standardized_recipe['ingredients'] = standardized_ingredients
            
            # Standardize prep and cook times
            if 'prep_time' in recipe_data:
                standardized_recipe['prep_time'] = self.standardize_time(recipe_data['prep_time'])
            
            if 'cook_time' in recipe_data:
                standardized_recipe['cook_time'] = self.standardize_time(recipe_data['cook_time'])
            
            # Standardize nutrition values (should already be in kcal)
            if 'nutrition' in recipe_data and isinstance(recipe_data['nutrition'], dict):
                standardized_nutrition = self.standardize_nutrition_values(recipe_data['nutrition'])
                standardized_recipe['nutrition'] = standardized_nutrition
            
            return standardized_recipe
            
        except Exception as e:
            logger.error(f"Error standardizing recipe measurements: {str(e)}")
            return recipe_data
    
    def standardize_time(self, time_value: Union[int, float, str]) -> int:
        """
        Standardize time to minutes
        """
        try:
            if isinstance(time_value, str):
                # Parse time strings like "30 min", "1 hour", "1h 30m"
                time_value = self._parse_time_string(time_value)
            
            # Assume input is in minutes if it's a number
            return int(time_value)
            
        except Exception as e:
            logger.error(f"Error standardizing time: {str(e)}")
            return int(time_value) if isinstance(time_value, (int, float)) else 0
    
    def _parse_time_string(self, time_str: str) -> int:
        """
        Parse time string and convert to minutes
        """
        time_str = time_str.lower().strip()
        total_minutes = 0
        
        # Pattern for "1h 30m" or "1 hour 30 minutes"
        hour_minute_pattern = r'(\d+)\s*(?:h|hour|hours)\s*(\d+)\s*(?:m|min|minute|minutes)'
        match = re.search(hour_minute_pattern, time_str)
        if match:
            hours = int(match.group(1))
            minutes = int(match.group(2))
            return hours * 60 + minutes
        
        # Pattern for just hours "1h" or "1 hour"
        hour_pattern = r'(\d+)\s*(?:h|hour|hours)'
        match = re.search(hour_pattern, time_str)
        if match:
            hours = int(match.group(1))
            return hours * 60
        
        # Pattern for just minutes "30m" or "30 minutes"
        minute_pattern = r'(\d+)\s*(?:m|min|minute|minutes)'
        match = re.search(minute_pattern, time_str)
        if match:
            return int(match.group(1))
        
        # Try to extract just the number
        number_pattern = r'(\d+)'
        match = re.search(number_pattern, time_str)
        if match:
            return int(match.group(1))
        
        return 0
    
    def standardize_nutrition_values(self, nutrition_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Standardize nutrition values to common units
        """
        try:
            standardized_nutrition = nutrition_data.copy()
            
            # Energy should be in kcal
            if 'calories' in nutrition_data:
                standardized_nutrition['calories'] = self._standardize_energy(nutrition_data['calories'])
            
            # Macronutrients should be in grams
            macronutrients = ['protein', 'carbs', 'carbohydrates', 'fats', 'fat', 'fiber', 'sugar']
            for nutrient in macronutrients:
                if nutrient in nutrition_data:
                    standardized_nutrition[nutrient] = self._standardize_weight(nutrition_data[nutrient])
            
            # Micronutrients should be in mg or mcg
            micronutrients = {
                'sodium': 'mg',
                'iron': 'mg',
                'calcium': 'mg',
                'magnesium': 'mg',
                'zinc': 'mg',
                'potassium': 'mg',
                'phosphorus': 'mg',
                'vitamin_c': 'mg',
                'vitamin_e': 'mg',
                'thiamine': 'mg',
                'riboflavin': 'mg',
                'niacin': 'mg',
                'vitamin_b12': 'mcg',
                'folate': 'mcg',
                'vitamin_k': 'mcg',
                'selenium': 'mcg',
                'vitamin_d': 'IU',
                'vitamin_a': 'IU'
            }
            
            for nutrient, unit in micronutrients.items():
                if nutrient in nutrition_data:
                    standardized_nutrition[nutrient] = self._standardize_micronutrient(
                        nutrition_data[nutrient], unit
                    )
            
            return standardized_nutrition
            
        except Exception as e:
            logger.error(f"Error standardizing nutrition values: {str(e)}")
            return nutrition_data
    
    def _standardize_energy(self, energy_value: Union[int, float, str]) -> float:
        """Standardize energy to kcal"""
        try:
            if isinstance(energy_value, str):
                energy_str = energy_value.lower().strip()
                if 'kj' in energy_str or 'kilojoule' in energy_str:
                    # Convert kJ to kcal
                    number = float(re.findall(r'[\d.]+', energy_str)[0])
                    return round(number * 0.239006, 1)
                elif 'cal' in energy_str and 'kcal' not in energy_str:
                    # Convert cal to kcal
                    number = float(re.findall(r'[\d.]+', energy_str)[0])
                    return round(number * 0.001, 1)
            
            return float(energy_value)
        except:
            return float(energy_value) if isinstance(energy_value, (int, float)) else 0.0
    
    def _standardize_weight(self, weight_value: Union[int, float, str]) -> float:
        """Standardize weight to grams"""
        try:
            if isinstance(weight_value, str):
                weight_str = weight_value.lower().strip()
                if 'oz' in weight_str or 'ounce' in weight_str:
                    # Convert oz to g
                    number = float(re.findall(r'[\d.]+', weight_str)[0])
                    return round(number * 28.3495, 1)
                elif 'lb' in weight_str or 'pound' in weight_str:
                    # Convert lb to g
                    number = float(re.findall(r'[\d.]+', weight_str)[0])
                    return round(number * 453.592, 1)
                elif 'kg' in weight_str or 'kilogram' in weight_str:
                    # Convert kg to g
                    number = float(re.findall(r'[\d.]+', weight_str)[0])
                    return round(number * 1000, 1)
            
            return float(weight_value)
        except:
            return float(weight_value) if isinstance(weight_value, (int, float)) else 0.0
    
    def _standardize_micronutrient(self, value: Union[int, float, str], target_unit: str) -> float:
        """Standardize micronutrient values"""
        try:
            if isinstance(value, str):
                value_str = value.lower().strip()
                if target_unit == 'mg':
                    if 'mcg' in value_str or 'μg' in value_str:
                        # Convert mcg to mg
                        number = float(re.findall(r'[\d.]+', value_str)[0])
                        return round(number * 0.001, 3)
                elif target_unit == 'mcg':
                    if 'mg' in value_str:
                        # Convert mg to mcg
                        number = float(re.findall(r'[\d.]+', value_str)[0])
                        return round(number * 1000, 1)
            
            return float(value)
        except:
            return float(value) if isinstance(value, (int, float)) else 0.0
    
    def get_standard_units(self) -> Dict[str, str]:
        """Get the standard units used in the system"""
        return self.STANDARD_UNITS.copy()
    
    def get_conversion_factors(self) -> Dict[str, Dict[str, float]]:
        """Get all conversion factors"""
        return self.CONVERSION_FACTORS.copy()
    
    def validate_measurement(self, quantity: float, unit: str, measurement_type: str) -> bool:
        """
        Validate that a measurement is in the correct format
        """
        try:
            if measurement_type not in self.CONVERSION_FACTORS:
                return False
            
            if unit.lower() not in self.CONVERSION_FACTORS[measurement_type]:
                return False
            
            if quantity < 0:
                return False
            
            return True
        except:
            return False



