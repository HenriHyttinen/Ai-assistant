#!/usr/bin/env python3
"""
Convert Fahrenheit Temperatures to Celsius

This script converts Fahrenheit temperatures in recipe instructions to Celsius
while preserving the original Fahrenheit values for users with different locale settings.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
from database import SessionLocal
from models.recipe import Recipe, RecipeInstruction
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TemperatureConverter:
    def __init__(self):
        self.db = SessionLocal()
        self.converted_count = 0
        self.recipes_updated = 0

    def fahrenheit_to_celsius(self, fahrenheit):
        """Convert Fahrenheit to Celsius"""
        return round((fahrenheit - 32) * 5/9)

    def convert_temperature_in_text(self, text):
        """Convert Fahrenheit temperatures in text to show both F and C"""
        # Pattern to match temperatures like "350°F", "350 F", "350F", etc.
        pattern = r'(\d+)\s*°?\s*[Ff]'
        
        def replace_temp(match):
            fahrenheit = int(match.group(1))
            celsius = self.fahrenheit_to_celsius(fahrenheit)
            return f"{fahrenheit}°F ({celsius}°C)"
        
        return re.sub(pattern, replace_temp, text)

    def convert_recipe_instructions(self, recipe):
        """Convert temperatures in all instructions of a recipe"""
        updated = False
        
        for instruction in recipe.instructions:
            original_text = instruction.description
            converted_text = self.convert_temperature_in_text(original_text)
            
            if original_text != converted_text:
                instruction.description = converted_text
                self.converted_count += 1
                updated = True
                logger.debug(f"Converted: {original_text[:50]}... -> {converted_text[:50]}...")
        
        return updated

    def convert_all_recipes(self):
        """Convert temperatures in all recipes"""
        logger.info("🌡️ Starting temperature conversion from Fahrenheit to Celsius...")
        
        # Find all recipes with temperature data
        temp_pattern = r'(\d+)\s*°?\s*[Ff]'
        recipes_with_temps = []
        
        for recipe in self.db.query(Recipe).all():
            has_temp = False
            for instruction in recipe.instructions:
                if re.search(temp_pattern, instruction.description):
                    has_temp = True
                    break
            
            if has_temp:
                recipes_with_temps.append(recipe)
        
        logger.info(f"Found {len(recipes_with_temps)} recipes with temperature data")
        
        # Convert temperatures
        for recipe in recipes_with_temps:
            if self.convert_recipe_instructions(recipe):
                self.recipes_updated += 1
                logger.info(f"✅ Updated: {recipe.title}")
        
        # Commit all changes
        self.db.commit()
        
        logger.info(f"🎉 Conversion complete!")
        logger.info(f"Updated {self.recipes_updated} recipes")
        logger.info(f"Converted {self.converted_count} temperature references")
        
        return self.recipes_updated, self.converted_count

    def verify_conversion(self):
        """Verify the conversion was successful"""
        logger.info("🔍 Verifying conversion...")
        
        # Check a few recipes to see the conversion
        sample_recipes = self.db.query(Recipe).limit(5).all()
        
        for recipe in sample_recipes:
            for instruction in recipe.instructions:
                if "°F (" in instruction.description and "°C)" in instruction.description:
                    logger.info(f"✅ {recipe.title}: {instruction.description[:100]}...")
                    break

    def close(self):
        """Close database connection"""
        self.db.close()

def main():
    """Main function to convert temperatures"""
    converter = TemperatureConverter()
    
    try:
        recipes_updated, temps_converted = converter.convert_all_recipes()
        converter.verify_conversion()
        
        logger.info(f"🎉 SUCCESS! Converted {temps_converted} temperatures in {recipes_updated} recipes!")
        
    except Exception as e:
        logger.error(f"❌ Conversion failed: {e}")
        sys.exit(1)
    finally:
        converter.close()

if __name__ == "__main__":
    main()
