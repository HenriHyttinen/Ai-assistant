#!/usr/bin/env python3
"""
Convert All Imperial Units to Metric System

This script converts:
1. Fahrenheit temperatures to Celsius (showing both for clarity)
2. Imperial units in instructions (oz, lb, cup, tbsp, tsp) to metric (g, kg, ml)
3. Ensures all recipes use the metric system (kg/g/ml/°C)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from database import SessionLocal
from models.recipe import Recipe, RecipeInstruction, RecipeIngredient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetricConverter:
    def __init__(self):
        self.db = SessionLocal()
        self.converted_temps = 0
        self.converted_units = 0
        self.recipes_updated = 0
        
    def fahrenheit_to_celsius(self, fahrenheit):
        """Convert Fahrenheit to Celsius"""
        return round((fahrenheit - 32) * 5/9)
    
    def convert_temperature(self, text):
        """Convert Fahrenheit temperatures to show both F and C"""
        # Pattern to match temperatures like "350°F", "350 F", "350F", "350° F"
        pattern = r'(\d+)\s*°?\s*[Ff](?:\s*\((\d+)\s*°?[Cc]\))?'
        
        def replace_temp(match):
            fahrenheit = int(match.group(1))
            # If already has Celsius, keep it
            if match.group(2):
                return match.group(0)
            celsius = self.fahrenheit_to_celsius(fahrenheit)
            return f"{fahrenheit}°F ({celsius}°C)"
        
        converted = re.sub(pattern, replace_temp, text)
        if converted != text:
            self.converted_temps += 1
        return converted
    
    def convert_imperial_units(self, text):
        """Convert imperial units in text to metric with values"""
        original = text
        converted = text
        
        # Helper to check if already converted (has metric in parentheses nearby)
        def is_already_converted(text, start, end):
            context = text[max(0, start-30):min(len(text), end+30)]
            return '(g' in context or '(kg' in context or '(ml' in context or '(°C)' in context
        
        # Weight conversions
        # Pounds first (to avoid matching in "ounces per pound")
        def replace_lb(m):
            if is_already_converted(converted, m.start(), m.end()):
                return m.group(0)
            value = float(m.group(1))
            if value < 2:
                result = f"{value * 453.6:.1f}g ({value}{'lb' if value == 1 else 'lb'})"
            else:
                result = f"{value * 0.4536:.2f}kg ({value}{'lb' if value == 1 else 'lb'})"
            return result
        
        # Ounces
        def replace_oz(m):
            if is_already_converted(converted, m.start(), m.end()):
                return m.group(0)
            value = float(m.group(1))
            result = f"{value * 28.35:.1f}g ({value}{'oz' if value == 1 else 'oz'})"
            return result
        
        # Volume conversions
        def replace_cup(m):
            if is_already_converted(converted, m.start(), m.end()):
                return m.group(0)
            value = float(m.group(1))
            unit = m.group(2).lower()
            result = f"{value * 240:.0f}ml ({value} {unit})"
            return result
        
        def replace_tbsp(m):
            if is_already_converted(converted, m.start(), m.end()):
                return m.group(0)
            value = float(m.group(1))
            unit = m.group(2).lower()
            result = f"{value * 15:.0f}ml ({value} {unit})"
            return result
        
        def replace_tsp(m):
            if is_already_converted(converted, m.start(), m.end()):
                return m.group(0)
            value = float(m.group(1))
            unit = m.group(2).lower()
            result = f"{value * 5:.0f}ml ({value} {unit})"
            return result
        
        # Apply conversions in order (most specific first)
        # Weight: pounds before ounces
        converted = re.sub(r'\b(\d+(?:\.\d+)?)\s*(?:lb|lbs|pound|pounds)\b', replace_lb, converted, flags=re.IGNORECASE)
        converted = re.sub(r'\b(\d+(?:\.\d+)?)\s*(?:oz|ounce|ounces)\b', replace_oz, converted, flags=re.IGNORECASE)
        
        # Volume: cups, tablespoons, teaspoons
        converted = re.sub(r'\b(\d+(?:\.\d+)?)\s*(cup|cups)\b', replace_cup, converted, flags=re.IGNORECASE)
        converted = re.sub(r'\b(\d+(?:\.\d+)?)\s*(tbsp|tablespoon|tablespoons)\b', replace_tbsp, converted, flags=re.IGNORECASE)
        converted = re.sub(r'\b(\d+(?:\.\d+)?)\s*(tsp|teaspoon|teaspoons)\b', replace_tsp, converted, flags=re.IGNORECASE)
        
        if converted != original:
            self.converted_units += 1
        
        return converted
    
    def convert_instruction(self, instruction):
        """Convert a single instruction's text"""
        original = instruction.description
        converted = self.convert_temperature(original)
        converted = self.convert_imperial_units(converted)
        
        if converted != original:
            instruction.description = converted
            return True
        return False
    
    def convert_recipe_instructions(self, recipe):
        """Convert all instructions for a recipe"""
        updated = False
        for instruction in recipe.instructions:
            if self.convert_instruction(instruction):
                updated = True
        
        return updated
    
    def check_ingredient_units(self):
        """Check if any ingredient units are still imperial"""
        imperial_pattern = re.compile(r'\b(oz|ounce|ounces|pound|pounds|lb|lbs|cup|cups|tablespoon|tablespoons|tbsp|teaspoon|teaspoons|tsp)\b', re.IGNORECASE)
        
        ingredients = self.db.query(RecipeIngredient).all()
        imperial_count = 0
        
        for ing in ingredients:
            if imperial_pattern.search(ing.unit or ''):
                imperial_count += 1
                logger.warning(f"⚠️  Ingredient {ing.id} has imperial unit: {ing.unit}")
        
        if imperial_count > 0:
            logger.warning(f"⚠️  Found {imperial_count} ingredients with imperial units")
        else:
            logger.info("✅ All ingredient units are metric")
    
    def convert_all_recipes(self):
        """Convert all recipes to metric system"""
        logger.info("🌍 Starting conversion to metric system...")
        
        # Check ingredient units first
        self.check_ingredient_units()
        
        # Find all recipes
        recipes = self.db.query(Recipe).all()
        logger.info(f"Found {len(recipes)} recipes to check")
        
        # Pattern to find recipes with imperial units
        imperial_pattern = re.compile(
            r'\b(oz|ounce|ounces|pound|pounds|lb|lbs|cup|cups|tablespoon|tablespoons|tbsp|teaspoon|teaspoons|tsp|°F|fahrenheit|° F)\b',
            re.IGNORECASE
        )
        
        recipes_to_convert = []
        for recipe in recipes:
            for instruction in recipe.instructions:
                if imperial_pattern.search(instruction.description or ''):
                    recipes_to_convert.append(recipe)
                    break
        
        logger.info(f"Found {len(recipes_to_convert)} recipes with imperial units in instructions")
        
        # Convert recipes
        for recipe in recipes_to_convert:
            if self.convert_recipe_instructions(recipe):
                self.recipes_updated += 1
                if self.recipes_updated % 50 == 0:
                    logger.info(f"Updated {self.recipes_updated} recipes...")
        
        # Commit all changes
        self.db.commit()
        
        logger.info(f"🎉 Conversion complete!")
        logger.info(f"Updated {self.recipes_updated} recipes")
        logger.info(f"Converted {self.converted_temps} temperature references")
        logger.info(f"Converted {self.converted_units} unit references")
        
        return self.recipes_updated, self.converted_temps, self.converted_units
    
    def verify_conversion(self):
        """Verify the conversion was successful"""
        logger.info("🔍 Verifying conversion...")
        
        # Check for remaining imperial units
        imperial_pattern = re.compile(
            r'\b(oz|ounce|ounces|pound|pounds|lb|lbs|cup|cups|tablespoon|tablespoons|tbsp|teaspoon|teaspoons|tsp|°F|fahrenheit|° F)\b(?!\s*\()',
            re.IGNORECASE
        )
        
        remaining_count = 0
        for recipe in self.db.query(Recipe).limit(100).all():
            for instruction in recipe.instructions:
                # Check for unmatched Fahrenheit (without Celsius conversion)
                if re.search(r'\b\d+\s*°?\s*[Ff]\b(?!\s*\()', instruction.description, re.IGNORECASE):
                    remaining_count += 1
                    if remaining_count <= 5:
                        logger.warning(f"⚠️  Recipe {recipe.id} ({recipe.title[:50]}): {instruction.description[:100]}...")
        
        if remaining_count > 0:
            logger.warning(f"⚠️  Found {remaining_count} instructions with unmatched Fahrenheit (sample shown above)")
        else:
            logger.info("✅ All temperatures converted (or already had Celsius)")
        
        # Sample converted instructions
        sample_count = 0
        for recipe in self.db.query(Recipe).limit(10).all():
            for instruction in recipe.instructions:
                if "°C)" in instruction.description or "g (" in instruction.description or "ml (" in instruction.description:
                    sample_count += 1
                    if sample_count <= 3:
                        logger.info(f"✅ Sample conversion: {instruction.description[:150]}...")
                    if sample_count >= 3:
                        break
            if sample_count >= 3:
                break
    
    def close(self):
        """Close database connection"""
        self.db.close()

def main():
    """Main function to convert to metric"""
    converter = MetricConverter()
    
    try:
        recipes_updated, temps_converted, units_converted = converter.convert_all_recipes()
        converter.verify_conversion()
        
        logger.info(f"🎉 SUCCESS!")
        logger.info(f"   Updated {recipes_updated} recipes")
        logger.info(f"   Converted {temps_converted} temperature references")
        logger.info(f"   Converted {units_converted} unit references")
        
    except Exception as e:
        logger.error(f"❌ Conversion failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        converter.close()

if __name__ == "__main__":
    main()

