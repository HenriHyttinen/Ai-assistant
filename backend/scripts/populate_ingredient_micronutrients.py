#!/usr/bin/env python3
"""
Populate Ingredient Micronutrients

This script adds realistic micronutrient values to ingredients in the database.
Uses common nutritional data for vitamins, minerals, and other micronutrients.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import Ingredient
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Micronutrient data per 100g for common ingredients
# Based on USDA nutritional database and standard nutritional references
MICRONUTRIENT_DATA = {
    # Proteins - Fish & Seafood (high in Omega-3, Vitamin D, B12)
    'salmon': {
        'vitamin_d': 988, 'vitamin_b12': 3.2, 'iron': 0.8, 'calcium': 12,
        'vitamin_c': 0, 'magnesium': 29, 'folate': 25, 'zinc': 0.64, 'potassium': 363,
        'phosphorus': 240, 'omega_3': 2.26, 'omega_6': 0.17, 'selenium': 46.8
    },
    'tuna': {
        'vitamin_d': 227, 'vitamin_b12': 2.2, 'iron': 1.0, 'calcium': 8,
        'vitamin_c': 0, 'magnesium': 28, 'folate': 2, 'zinc': 0.77, 'potassium': 323,
        'phosphorus': 248, 'omega_3': 0.42, 'omega_6': 0.01, 'selenium': 108.2
    },
    'fish': {
        'vitamin_d': 400, 'vitamin_b12': 2.0, 'iron': 0.9, 'calcium': 10,
        'vitamin_c': 0, 'magnesium': 30, 'folate': 10, 'zinc': 0.7, 'potassium': 350,
        'phosphorus': 230, 'omega_3': 1.5, 'omega_6': 0.1, 'selenium': 50
    },
    'shrimp': {
        'vitamin_d': 5, 'vitamin_b12': 1.1, 'iron': 0.3, 'calcium': 54,
        'vitamin_c': 0, 'magnesium': 37, 'folate': 13, 'zinc': 1.64, 'potassium': 220,
        'phosphorus': 214, 'omega_3': 0.26, 'omega_6': 0.02, 'selenium': 38.0
    },
    
    # Proteins - Meat
    'chicken': {
        'vitamin_d': 5, 'vitamin_b12': 0.3, 'iron': 0.9, 'calcium': 15,
        'vitamin_c': 0, 'magnesium': 23, 'folate': 5, 'zinc': 1.3, 'potassium': 220,
        'phosphorus': 196, 'omega_3': 0.03, 'omega_6': 0.48, 'selenium': 14.4
    },
    'beef': {
        'vitamin_d': 3, 'vitamin_b12': 2.5, 'iron': 2.6, 'calcium': 18,
        'vitamin_c': 0, 'magnesium': 21, 'folate': 8, 'zinc': 5.2, 'potassium': 315,
        'phosphorus': 198, 'omega_3': 0.05, 'omega_6': 0.38, 'selenium': 26.0
    },
    'pork': {
        'vitamin_d': 7, 'vitamin_b12': 0.7, 'iron': 0.9, 'calcium': 13,
        'vitamin_c': 0, 'magnesium': 22, 'folate': 5, 'zinc': 2.0, 'potassium': 362,
        'phosphorus': 198, 'omega_3': 0.03, 'omega_6': 0.47, 'selenium': 44.8
    },
    
    # Dairy & Eggs
    'eggs': {
        'vitamin_d': 87, 'vitamin_b12': 0.89, 'iron': 1.75, 'calcium': 56,
        'vitamin_c': 0, 'magnesium': 12, 'folate': 44, 'zinc': 1.29, 'potassium': 138,
        'phosphorus': 198, 'omega_3': 0.03, 'omega_6': 1.36, 'selenium': 30.7
    },
    'milk': {
        'vitamin_d': 48, 'vitamin_b12': 0.45, 'iron': 0.03, 'calcium': 113,
        'vitamin_c': 0, 'magnesium': 10, 'folate': 5, 'zinc': 0.38, 'potassium': 143,
        'phosphorus': 85, 'omega_3': 0.01, 'omega_6': 0.02, 'selenium': 3.7
    },
    'cheese': {
        'vitamin_d': 17, 'vitamin_b12': 0.83, 'iron': 0.14, 'calcium': 721,
        'vitamin_c': 0, 'magnesium': 28, 'folate': 18, 'zinc': 2.54, 'potassium': 76,
        'phosphorus': 512, 'omega_3': 0.02, 'omega_6': 0.09, 'selenium': 12.8
    },
    'yogurt': {
        'vitamin_d': 0, 'vitamin_b12': 0.75, 'iron': 0.04, 'calcium': 110,
        'vitamin_c': 0, 'magnesium': 11, 'folate': 7, 'zinc': 0.52, 'potassium': 141,
        'phosphorus': 95, 'omega_3': 0.01, 'omega_6': 0.02, 'selenium': 9.7
    },
    
    # Vegetables (high in Vitamin C, Folate, Potassium)
    'spinach': {
        'vitamin_d': 0, 'vitamin_b12': 0, 'iron': 2.7, 'calcium': 99,
        'vitamin_c': 28.1, 'magnesium': 79, 'folate': 194, 'zinc': 0.53, 'potassium': 558,
        'phosphorus': 49, 'omega_3': 0.14, 'omega_6': 0.03, 'selenium': 1.0
    },
    'broccoli': {
        'vitamin_d': 0, 'vitamin_b12': 0, 'iron': 0.73, 'calcium': 47,
        'vitamin_c': 89.2, 'magnesium': 21, 'folate': 63, 'zinc': 0.41, 'potassium': 316,
        'phosphorus': 66, 'omega_3': 0.10, 'omega_6': 0.02, 'selenium': 2.5
    },
    'kale': {
        'vitamin_d': 0, 'vitamin_b12': 0, 'iron': 1.47, 'calcium': 150,
        'vitamin_c': 120, 'magnesium': 47, 'folate': 141, 'zinc': 0.56, 'potassium': 491,
        'phosphorus': 92, 'omega_3': 0.18, 'omega_6': 0.14, 'selenium': 0.9
    },
    'tomatoes': {
        'vitamin_d': 0, 'vitamin_b12': 0, 'iron': 0.27, 'calcium': 10,
        'vitamin_c': 13.7, 'magnesium': 11, 'folate': 15, 'zinc': 0.17, 'potassium': 237,
        'phosphorus': 24, 'omega_3': 0.00, 'omega_6': 0.08, 'selenium': 0.2
    },
    'bell peppers': {
        'vitamin_d': 0, 'vitamin_b12': 0, 'iron': 0.43, 'calcium': 10,
        'vitamin_c': 80.4, 'magnesium': 10, 'folate': 46, 'zinc': 0.25, 'potassium': 211,
        'phosphorus': 20, 'omega_3': 0.01, 'omega_6': 0.03, 'selenium': 0.2
    },
    'carrots': {
        'vitamin_d': 0, 'vitamin_b12': 0, 'iron': 0.30, 'calcium': 33,
        'vitamin_c': 5.9, 'magnesium': 12, 'folate': 19, 'zinc': 0.24, 'potassium': 320,
        'phosphorus': 35, 'omega_3': 0.00, 'omega_6': 0.11, 'selenium': 0.1,
        'vitamin_a': 16706  # High in Vitamin A (IU)
    },
    
    # Fruits (high in Vitamin C, Potassium)
    'oranges': {
        'vitamin_d': 0, 'vitamin_b12': 0, 'iron': 0.10, 'calcium': 40,
        'vitamin_c': 53.2, 'magnesium': 10, 'folate': 30, 'zinc': 0.07, 'potassium': 181,
        'phosphorus': 14, 'omega_3': 0.02, 'omega_6': 0.03, 'selenium': 0.5
    },
    'apples': {
        'vitamin_d': 0, 'vitamin_b12': 0, 'iron': 0.12, 'calcium': 6,
        'vitamin_c': 4.6, 'magnesium': 5, 'folate': 3, 'zinc': 0.04, 'potassium': 107,
        'phosphorus': 11, 'omega_3': 0.01, 'omega_6': 0.04, 'selenium': 0.0
    },
    'bananas': {
        'vitamin_d': 0, 'vitamin_b12': 0, 'iron': 0.26, 'calcium': 5,
        'vitamin_c': 8.7, 'magnesium': 27, 'folate': 20, 'zinc': 0.15, 'potassium': 358,
        'phosphorus': 22, 'omega_3': 0.03, 'omega_6': 0.05, 'selenium': 1.0
    },
    
    # Legumes (high in Folate, Iron, Magnesium)
    'lentils': {
        'vitamin_d': 0, 'vitamin_b12': 0, 'iron': 3.3, 'calcium': 19,
        'vitamin_c': 1.5, 'magnesium': 36, 'folate': 181, 'zinc': 1.27, 'potassium': 369,
        'phosphorus': 180, 'omega_3': 0.11, 'omega_6': 0.14, 'selenium': 2.8
    },
    'chickpeas': {
        'vitamin_d': 0, 'vitamin_b12': 0, 'iron': 2.89, 'calcium': 49,
        'vitamin_c': 1.3, 'magnesium': 48, 'folate': 172, 'zinc': 1.53, 'potassium': 291,
        'phosphorus': 168, 'omega_3': 0.04, 'omega_6': 2.67, 'selenium': 3.7
    },
    'beans': {
        'vitamin_d': 0, 'vitamin_b12': 0, 'iron': 2.1, 'calcium': 28,
        'vitamin_c': 0.8, 'magnesium': 43, 'folate': 149, 'zinc': 1.06, 'potassium': 340,
        'phosphorus': 140, 'omega_3': 0.06, 'omega_6': 0.22, 'selenium': 1.2
    },
    
    # Nuts & Seeds (high in Magnesium, Zinc, Omega-3/6)
    'almonds': {
        'vitamin_d': 0, 'vitamin_b12': 0, 'iron': 3.71, 'calcium': 269,
        'vitamin_c': 0, 'magnesium': 270, 'folate': 44, 'zinc': 3.12, 'potassium': 733,
        'phosphorus': 481, 'omega_3': 0.01, 'omega_6': 12.1, 'selenium': 4.1
    },
    'walnuts': {
        'vitamin_d': 0, 'vitamin_b12': 0, 'iron': 2.91, 'calcium': 98,
        'vitamin_c': 1.3, 'magnesium': 158, 'folate': 98, 'zinc': 3.09, 'potassium': 441,
        'phosphorus': 346, 'omega_3': 9.08, 'omega_6': 38.09, 'selenium': 4.9
    },
    'chia seeds': {
        'vitamin_d': 0, 'vitamin_b12': 0, 'iron': 7.72, 'calcium': 631,
        'vitamin_c': 1.6, 'magnesium': 335, 'folate': 49, 'zinc': 4.58, 'potassium': 407,
        'phosphorus': 860, 'omega_3': 17.83, 'omega_6': 5.84, 'selenium': 55.2
    },
    
    # Grains
    'oats': {
        'vitamin_d': 0, 'vitamin_b12': 0, 'iron': 4.72, 'calcium': 54,
        'vitamin_c': 0, 'magnesium': 177, 'folate': 56, 'zinc': 3.97, 'potassium': 429,
        'phosphorus': 523, 'omega_3': 0.11, 'omega_6': 2.42, 'selenium': 34.0
    },
    'quinoa': {
        'vitamin_d': 0, 'vitamin_b12': 0, 'iron': 4.57, 'calcium': 47,
        'vitamin_c': 0, 'magnesium': 197, 'folate': 184, 'zinc': 3.1, 'potassium': 563,
        'phosphorus': 457, 'omega_3': 0.35, 'omega_6': 3.29, 'selenium': 8.5
    },
}

def get_micronutrients_for_ingredient(ingredient_name):
    """Get micronutrient values for an ingredient by matching name"""
    name_lower = ingredient_name.lower()
    
    # Try exact matches first
    for key, values in MICRONUTRIENT_DATA.items():
        if key in name_lower or name_lower in key:
            return values
    
    # Category-based defaults
    if any(x in name_lower for x in ['fish', 'salmon', 'tuna', 'cod', 'mackerel', 'sardine']):
        return MICRONUTRIENT_DATA.get('fish', MICRONUTRIENT_DATA['salmon'])
    elif any(x in name_lower for x in ['chicken', 'poultry']):
        return MICRONUTRIENT_DATA['chicken']
    elif any(x in name_lower for x in ['beef', 'steak']):
        return MICRONUTRIENT_DATA['beef']
    elif any(x in name_lower for x in ['pork', 'bacon']):
        return MICRONUTRIENT_DATA['pork']
    elif any(x in name_lower for x in ['egg']):
        return MICRONUTRIENT_DATA['eggs']
    elif any(x in name_lower for x in ['cheese', 'cheddar', 'mozzarella', 'parmesan']):
        return MICRONUTRIENT_DATA['cheese']
    elif any(x in name_lower for x in ['milk', 'dairy']):
        return MICRONUTRIENT_DATA['milk']
    elif any(x in name_lower for x in ['spinach', 'leafy']):
        return MICRONUTRIENT_DATA['spinach']
    elif any(x in name_lower for x in ['broccoli']):
        return MICRONUTRIENT_DATA['broccoli']
    elif any(x in name_lower for x in ['tomato']):
        return MICRONUTRIENT_DATA['tomatoes']
    elif any(x in name_lower for x in ['orange']):
        return MICRONUTRIENT_DATA['oranges']
    elif any(x in name_lower for x in ['lentil']):
        return MICRONUTRIENT_DATA['lentils']
    elif any(x in name_lower for x in ['chickpea', 'garbanzo']):
        return MICRONUTRIENT_DATA['chickpeas']
    elif any(x in name_lower for x in ['bean', 'black bean', 'kidney bean']):
        return MICRONUTRIENT_DATA['beans']
    elif any(x in name_lower for x in ['almond']):
        return MICRONUTRIENT_DATA['almonds']
    elif any(x in name_lower for x in ['walnut']):
        return MICRONUTRIENT_DATA['walnuts']
    elif any(x in name_lower for x in ['chia']):
        return MICRONUTRIENT_DATA['chia seeds']
    elif any(x in name_lower for x in ['oat']):
        return MICRONUTRIENT_DATA['oats']
    elif any(x in name_lower for x in ['quinoa']):
        return MICRONUTRIENT_DATA['quinoa']
    
    return None

class MicronutrientPopulator:
    def __init__(self):
        self.db = SessionLocal()
        self.updated_count = 0
        self.skipped_count = 0
    
    def populate_all(self):
        """Populate micronutrients for all ingredients"""
        logger.info("🔍 Finding ingredients to update...")
        
        ingredients = self.db.query(Ingredient).all()
        logger.info(f"Found {len(ingredients)} ingredients")
        
        for i, ingredient in enumerate(ingredients, 1):
            try:
                micronutrients = get_micronutrients_for_ingredient(ingredient.name)
                
                if micronutrients:
                    # Only update if values are missing or zero
                    updated = False
                    
                    if not ingredient.vitamin_c or ingredient.vitamin_c == 0:
                        ingredient.vitamin_c = micronutrients.get('vitamin_c', 0)
                        updated = True
                    
                    if not ingredient.vitamin_d or ingredient.vitamin_d == 0:
                        ingredient.vitamin_d = micronutrients.get('vitamin_d', 0)
                        updated = True
                    
                    if not ingredient.vitamin_b12 or ingredient.vitamin_b12 == 0:
                        ingredient.vitamin_b12 = micronutrients.get('vitamin_b12', 0)
                        updated = True
                    
                    if not ingredient.iron or ingredient.iron == 0:
                        ingredient.iron = micronutrients.get('iron', 0)
                        updated = True
                    
                    if not ingredient.calcium or ingredient.calcium == 0:
                        ingredient.calcium = micronutrients.get('calcium', 0)
                        updated = True
                    
                    if not ingredient.magnesium or ingredient.magnesium == 0:
                        ingredient.magnesium = micronutrients.get('magnesium', 0)
                        updated = True
                    
                    if not ingredient.folate or ingredient.folate == 0:
                        ingredient.folate = micronutrients.get('folate', 0)
                        updated = True
                    
                    if not ingredient.zinc or ingredient.zinc == 0:
                        ingredient.zinc = micronutrients.get('zinc', 0)
                        updated = True
                    
                    if not ingredient.potassium or ingredient.potassium == 0:
                        ingredient.potassium = micronutrients.get('potassium', 0)
                        updated = True
                    
                    if not ingredient.omega_3 or ingredient.omega_3 == 0:
                        ingredient.omega_3 = micronutrients.get('omega_3', 0)
                        updated = True
                    
                    if not ingredient.omega_6 or ingredient.omega_6 == 0:
                        ingredient.omega_6 = micronutrients.get('omega_6', 0)
                        updated = True
                    
                    if updated:
                        self.db.add(ingredient)
                        self.updated_count += 1
                    else:
                        self.skipped_count += 1
                else:
                    self.skipped_count += 1
                
                if i % 100 == 0:
                    self.db.commit()
                    logger.info(f"Progress: {i}/{len(ingredients)} ingredients processed...")
                    
            except Exception as e:
                logger.error(f"Error processing ingredient {ingredient.name}: {e}")
                continue
        
        self.db.commit()
        
        logger.info(f"\n📊 Summary:")
        logger.info(f"   Ingredients updated: {self.updated_count}")
        logger.info(f"   Ingredients skipped: {self.skipped_count}")
    
    def close(self):
        """Close database connection"""
        self.db.close()

def main():
    """Main function"""
    populator = MicronutrientPopulator()
    
    try:
        populator.populate_all()
        logger.info(f"\n🎉 Micronutrient population complete!")
        
    except Exception as e:
        logger.error(f"❌ Population failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        populator.close()

if __name__ == "__main__":
    main()

