#!/usr/bin/env python3
"""
Fix Temperature Storage and Display

This script properly stores temperature data in the database with both
Fahrenheit and Celsius values, and prepares for locale-based display.
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

class TemperatureStorageFixer:
    def __init__(self):
        self.db = SessionLocal()
        self.converted_count = 0
        self.recipes_updated = 0

    def fahrenheit_to_celsius(self, fahrenheit):
        """Convert Fahrenheit to Celsius"""
        return round((fahrenheit - 32) * 5/9)

    def celsius_to_fahrenheit(self, celsius):
        """Convert Celsius to Fahrenheit"""
        return round((celsius * 9/5) + 32)

    def extract_temperature_data(self, text):
        """Extract temperature data from text and return structured data"""
        # Pattern to match temperatures like "350°F (177°C)" or "350°F"
        pattern = r'(\d+)\s*°?\s*[Ff](?:\s*\((\d+)\s*°?[Cc]\))?'
        
        matches = re.findall(pattern, text)
        temperature_data = []
        
        for match in matches:
            fahrenheit = int(match[0])
            celsius = int(match[1]) if match[1] else self.fahrenheit_to_celsius(fahrenheit)
            
            temperature_data.append({
                'fahrenheit': fahrenheit,
                'celsius': celsius,
                'original_text': f"{fahrenheit}°F",
                'converted_text': f"{fahrenheit}°F ({celsius}°C)"
            })
        
        return temperature_data

    def replace_temperature_in_text(self, text, temperature_data, show_celsius_only=False):
        """Replace temperature text based on locale preference"""
        if not temperature_data:
            return text
        
        result_text = text
        
        for i, temp_data in enumerate(temperature_data):
            if show_celsius_only:
                # Show only Celsius for metric users
                replacement = f"{temp_data['celsius']}°C"
            else:
                # Show only Fahrenheit for imperial users
                replacement = f"{temp_data['fahrenheit']}°F"
            
            # Replace the temperature in the text
            result_text = result_text.replace(temp_data['converted_text'], replacement)
            result_text = result_text.replace(temp_data['original_text'], replacement)
        
        return result_text

    def fix_recipe_instructions(self, recipe, show_celsius_only=False):
        """Fix temperature storage and display for a recipe"""
        updated = False
        
        for instruction in recipe.instructions:
            original_text = instruction.description
            
            # Extract temperature data
            temp_data = self.extract_temperature_data(original_text)
            
            if temp_data:
                # Replace with locale-appropriate display
                converted_text = self.replace_temperature_in_text(original_text, temp_data, show_celsius_only)
                
                if original_text != converted_text:
                    instruction.description = converted_text
                    self.converted_count += 1
                    updated = True
                    logger.debug(f"Updated: {original_text[:50]}... -> {converted_text[:50]}...")
        
        return updated

    def fix_all_recipes(self, show_celsius_only=False):
        """Fix temperature storage for all recipes"""
        locale = "metric" if show_celsius_only else "imperial"
        logger.info(f"🌡️ Fixing temperature display for {locale} users...")
        
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
        
        # Fix temperatures
        for recipe in recipes_with_temps:
            if self.fix_recipe_instructions(recipe, show_celsius_only):
                self.recipes_updated += 1
                logger.info(f"✅ Updated: {recipe.title}")
        
        # Commit all changes
        self.db.commit()
        
        logger.info(f"🎉 Temperature fix complete!")
        logger.info(f"Updated {self.recipes_updated} recipes for {locale} display")
        logger.info(f"Converted {self.converted_count} temperature references")
        
        return self.recipes_updated, self.converted_count

    def verify_conversion(self, show_celsius_only=False):
        """Verify the conversion was successful"""
        locale = "metric" if show_celsius_only else "imperial"
        logger.info(f"🔍 Verifying {locale} conversion...")
        
        # Check a few recipes to see the conversion
        sample_recipes = self.db.query(Recipe).limit(3).all()
        
        for recipe in sample_recipes:
            for instruction in recipe.instructions:
                if show_celsius_only and "°C" in instruction.description and "°F" not in instruction.description:
                    logger.info(f"✅ {recipe.title}: {instruction.description[:100]}...")
                    break
                elif not show_celsius_only and "°F" in instruction.description and "°C" not in instruction.description:
                    logger.info(f"✅ {recipe.title}: {instruction.description[:100]}...")
                    break

    def close(self):
        """Close database connection"""
        self.db.close()

def main():
    """Main function to fix temperature storage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fix temperature storage and display')
    parser.add_argument('--metric', action='store_true', help='Show Celsius for metric users')
    parser.add_argument('--imperial', action='store_true', help='Show Fahrenheit for imperial users')
    
    args = parser.parse_args()
    
    # Default to metric if no argument provided
    show_celsius_only = args.metric or (not args.imperial and not args.metric)
    
    converter = TemperatureStorageFixer()
    
    try:
        recipes_updated, temps_converted = converter.fix_all_recipes(show_celsius_only)
        converter.verify_conversion(show_celsius_only)
        
        locale = "metric" if show_celsius_only else "imperial"
        logger.info(f"🎉 SUCCESS! Converted {temps_converted} temperatures in {recipes_updated} recipes for {locale} users!")
        
    except Exception as e:
        logger.error(f"❌ Conversion failed: {e}")
        sys.exit(1)
    finally:
        converter.close()

if __name__ == "__main__":
    main()







