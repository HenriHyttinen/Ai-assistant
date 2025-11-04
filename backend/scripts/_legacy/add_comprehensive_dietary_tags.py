#!/usr/bin/env python3
"""
Add comprehensive dietary tags and allergen information to all recipes.
This script analyzes ingredients to detect:
- Dietary restrictions (vegetarian, vegan, gluten-free, etc.)
- Common allergens (dairy, eggs, nuts, fish, shellfish, soy, etc.)
- Other dietary considerations (low-sodium, high-protein, etc.)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import Recipe
from sqlalchemy.orm import Session
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveDietaryAnalyzer:
    def __init__(self, db: Session):
        self.db = db
        
        # Comprehensive allergen and dietary detection patterns
        self.allergen_patterns = {
            # Dairy products
            'dairy': [
                'milk', 'cheese', 'butter', 'cream', 'yogurt', 'sour cream', 'buttermilk',
                'mozzarella', 'cheddar', 'parmesan', 'ricotta', 'feta', 'goat cheese',
                'mascarpone', 'cream cheese', 'heavy cream', 'half and half', 'whey',
                'casein', 'lactose', 'ghee', 'kefir', 'buttermilk'
            ],
            
            # Eggs
            'eggs': [
                'egg', 'eggs', 'egg white', 'egg yolk', 'whole egg', 'beaten egg',
                'egg wash', 'mayonnaise', 'mayo', 'hollandaise', 'béarnaise'
            ],
            
            # Gluten/Wheat
            'gluten': [
                'wheat', 'flour', 'bread', 'pasta', 'noodles', 'couscous', 'bulgur',
                'semolina', 'spelt', 'barley', 'rye', 'triticale', 'malt', 'beer',
                'soy sauce', 'teriyaki', 'worcestershire', 'breadcrumbs', 'panko',
                'all-purpose flour', 'bread flour', 'cake flour', 'pastry flour'
            ],
            
            # Nuts
            'nuts': [
                'almond', 'almonds', 'walnut', 'walnuts', 'pecan', 'pecans', 'hazelnut',
                'hazelnuts', 'pistachio', 'pistachios', 'cashew', 'cashews', 'macadamia',
                'macadamias', 'brazil nut', 'brazil nuts', 'pine nut', 'pine nuts',
                'nut butter', 'almond butter', 'peanut butter', 'cashew butter'
            ],
            
            # Tree nuts (separate from peanuts)
            'tree-nuts': [
                'almond', 'almonds', 'walnut', 'walnuts', 'pecan', 'pecans', 'hazelnut',
                'hazelnuts', 'pistachio', 'pistachios', 'cashew', 'cashews', 'macadamia',
                'macadamias', 'brazil nut', 'brazil nuts', 'pine nut', 'pine nuts',
                'chestnut', 'chestnuts', 'beechnut', 'beechnuts'
            ],
            
            # Peanuts (legume, not tree nut)
            'peanuts': [
                'peanut', 'peanuts', 'peanut butter', 'peanut oil', 'groundnut'
            ],
            
            # Fish
            'fish': [
                'salmon', 'tuna', 'cod', 'halibut', 'bass', 'trout', 'mackerel', 'sardine',
                'sardines', 'anchovy', 'anchovies', 'herring', 'snapper', 'grouper',
                'mahi mahi', 'tilapia', 'sole', 'flounder', 'catfish', 'perch',
                'fish sauce', 'worcestershire sauce'
            ],
            
            # Shellfish
            'shellfish': [
                'shrimp', 'prawn', 'prawns', 'crab', 'crabmeat', 'lobster', 'crayfish',
                'crawfish', 'scallop', 'scallops', 'mussel', 'mussels', 'clam', 'clams',
                'oyster', 'oysters', 'squid', 'octopus', 'cuttlefish', 'sea urchin',
                'crab meat', 'lobster meat', 'shrimp paste', 'fish sauce'
            ],
            
            # Soy
            'soy': [
                'soy', 'soybean', 'soybeans', 'soy sauce', 'tamari', 'miso', 'tofu',
                'tempeh', 'edamame', 'soy milk', 'soy protein', 'soy flour', 'soy oil',
                'teriyaki sauce', 'worcestershire sauce', 'soy lecithin'
            ],
            
            # Sesame
            'sesame': [
                'sesame', 'sesame seed', 'sesame seeds', 'sesame oil', 'tahini',
                'sesame paste', 'halva', 'hummus'
            ],
            
            # Mustard
            'mustard': [
                'mustard', 'mustard seed', 'mustard seeds', 'mustard powder',
                'dijon mustard', 'yellow mustard', 'brown mustard', 'mustard greens'
            ],
            
            # Sulfites
            'sulfites': [
                'sulfite', 'sulfites', 'sulfur dioxide', 'sodium sulfite', 'potassium sulfite',
                'wine', 'dried fruit', 'dried apricot', 'dried apple', 'raisin', 'raisins',
                'prune', 'prunes', 'dried cranberry', 'dried cherry'
            ],
            
            # Nightshades (common sensitivity)
            'nightshades': [
                'tomato', 'tomatoes', 'potato', 'potatoes', 'eggplant', 'pepper',
                'bell pepper', 'chili pepper', 'paprika', 'cayenne', 'tobacco'
            ]
        }
        
        # Dietary restriction patterns
        self.dietary_patterns = {
            'vegetarian': {
                'exclude': ['beef', 'pork', 'chicken', 'turkey', 'lamb', 'veal', 'duck',
                           'fish', 'salmon', 'tuna', 'shrimp', 'crab', 'lobster', 'bacon',
                           'ham', 'sausage', 'pepperoni', 'salami', 'chorizo', 'prosciutto',
                           'anchovy', 'anchovies', 'fish sauce', 'worcestershire sauce',
                           'gelatin', 'rennet', 'lard', 'suet', 'broth', 'stock'],
                'include': ['vegetable', 'fruit', 'grain', 'legume', 'nut', 'seed']
            },
            
            'vegan': {
                'exclude': ['beef', 'pork', 'chicken', 'turkey', 'lamb', 'veal', 'duck',
                           'fish', 'salmon', 'tuna', 'shrimp', 'crab', 'lobster', 'bacon',
                           'ham', 'sausage', 'pepperoni', 'salami', 'chorizo', 'prosciutto',
                           'anchovy', 'anchovies', 'fish sauce', 'worcestershire sauce',
                           'gelatin', 'rennet', 'lard', 'suet', 'broth', 'stock',
                           'milk', 'cheese', 'butter', 'cream', 'yogurt', 'sour cream',
                           'egg', 'eggs', 'mayonnaise', 'honey', 'beeswax'],
                'include': ['vegetable', 'fruit', 'grain', 'legume', 'nut', 'seed']
            },
            
            'gluten-free': {
                'exclude': ['wheat', 'flour', 'bread', 'pasta', 'noodles', 'couscous',
                           'bulgur', 'semolina', 'spelt', 'barley', 'rye', 'triticale',
                           'malt', 'beer', 'soy sauce', 'teriyaki', 'worcestershire',
                           'breadcrumbs', 'panko', 'all-purpose flour', 'bread flour'],
                'include': ['rice', 'quinoa', 'buckwheat', 'millet', 'amaranth', 'corn',
                           'potato', 'sweet potato', 'cassava', 'tapioca']
            },
            
            'dairy-free': {
                'exclude': ['milk', 'cheese', 'butter', 'cream', 'yogurt', 'sour cream',
                           'buttermilk', 'mozzarella', 'cheddar', 'parmesan', 'ricotta',
                           'feta', 'goat cheese', 'mascarpone', 'cream cheese', 'heavy cream',
                           'half and half', 'whey', 'casein', 'lactose', 'ghee', 'kefir'],
                'include': ['coconut milk', 'almond milk', 'soy milk', 'oat milk', 'rice milk']
            },
            
            'nut-free': {
                'exclude': ['almond', 'almonds', 'walnut', 'walnuts', 'pecan', 'pecans',
                           'hazelnut', 'hazelnuts', 'pistachio', 'pistachios', 'cashew',
                           'cashews', 'macadamia', 'macadamias', 'brazil nut', 'brazil nuts',
                           'pine nut', 'pine nuts', 'peanut', 'peanuts', 'nut butter',
                           'almond butter', 'peanut butter', 'cashew butter'],
                'include': ['seed', 'seeds', 'sunflower seed', 'pumpkin seed', 'chia seed']
            },
            
            'soy-free': {
                'exclude': ['soy', 'soybean', 'soybeans', 'soy sauce', 'tamari', 'miso',
                           'tofu', 'tempeh', 'edamame', 'soy milk', 'soy protein', 'soy flour',
                           'soy oil', 'teriyaki sauce', 'worcestershire sauce', 'soy lecithin'],
                'include': ['coconut aminos', 'liquid aminos', 'bragg liquid aminos']
            }
        }
        
        # Additional dietary considerations
        self.health_patterns = {
            'low-sodium': ['low sodium', 'no salt', 'unsalted', 'reduced sodium'],
            'low-sugar': ['no sugar', 'sugar-free', 'unsweetened', 'no added sugar'],
            'high-protein': ['high protein', 'protein-rich', 'lean protein'],
            'low-carb': ['low carb', 'keto', 'ketogenic', 'no carb'],
            'high-fiber': ['high fiber', 'fiber-rich', 'whole grain'],
            'anti-inflammatory': ['turmeric', 'ginger', 'garlic', 'onion', 'berries', 'leafy greens'],
            'heart-healthy': ['olive oil', 'avocado', 'nuts', 'fish', 'omega-3'],
            'diabetic-friendly': ['low glycemic', 'complex carb', 'fiber-rich', 'no added sugar']
        }

    def analyze_ingredients(self, ingredients_text: str, title: str) -> tuple[list, list]:
        """Analyze ingredients for allergens and dietary restrictions"""
        if not ingredients_text:
            return [], []
            
        # Convert to lowercase for analysis
        text = f"{title} {ingredients_text}".lower()
        
        detected_allergens = []
        detected_dietary = []
        
        # Check for allergens
        for allergen, patterns in self.allergen_patterns.items():
            for pattern in patterns:
                if pattern in text:
                    detected_allergens.append(allergen)
                    break
        
        # Check for dietary restrictions
        for diet, rules in self.dietary_patterns.items():
            # Check if any excluded ingredients are present
            has_excluded = any(exclude in text for exclude in rules['exclude'])
            
            if not has_excluded:
                # Check if it has some included ingredients (for vegetarian/vegan)
                if diet in ['vegetarian', 'vegan']:
                    has_included = any(include in text for include in rules['include'])
                    if has_included:
                        detected_dietary.append(diet)
                else:
                    detected_dietary.append(diet)
        
        # Check for health patterns
        for health_tag, patterns in self.health_patterns.items():
            if any(pattern in text for pattern in patterns):
                detected_dietary.append(health_tag)
        
        # Additional logic for specific dietary tags
        if 'meat' not in text and 'fish' not in text and 'poultry' not in text:
            if 'dairy' not in detected_allergens and 'eggs' not in detected_allergens:
                if 'vegetarian' not in detected_dietary:
                    detected_dietary.append('vegetarian')
                if 'vegan' not in detected_dietary and 'honey' not in text:
                    detected_dietary.append('vegan')
        
        # Remove duplicates and sort
        detected_allergens = sorted(list(set(detected_allergens)))
        detected_dietary = sorted(list(set(detected_dietary)))
        
        return detected_dietary, detected_allergens

    def update_all_recipes(self):
        """Update all recipes with comprehensive dietary tags and allergens"""
        recipes = self.db.query(Recipe).all()
        total_recipes = len(recipes)
        
        logger.info(f"Analyzing {total_recipes} recipes for comprehensive dietary tags...")
        
        updated_count = 0
        
        for i, recipe in enumerate(recipes, 1):
            if i % 50 == 0:
                logger.info(f"Processed {i}/{total_recipes} recipes...")
            
            # Get ingredients text
            ingredients_text = ""
            if recipe.ingredients:
                for ingredient in recipe.ingredients:
                    if hasattr(ingredient, 'ingredient') and ingredient.ingredient:
                        ingredients_text += f"{ingredient.ingredient.name} "
                    if hasattr(ingredient, 'quantity') and ingredient.quantity:
                        ingredients_text += f"{ingredient.quantity} "
                    if hasattr(ingredient, 'unit') and ingredient.unit:
                        ingredients_text += f"{ingredient.unit} "
                    if hasattr(ingredient, 'notes') and ingredient.notes:
                        ingredients_text += f"{ingredient.notes} "
                    ingredients_text += " "
            
            # Analyze for dietary tags and allergens
            dietary_tags, allergens = self.analyze_ingredients(ingredients_text, recipe.title)
            
            # Combine dietary tags and allergens
            all_tags = dietary_tags + [f"contains-{allergen}" for allergen in allergens]
            
            # Update recipe
            recipe.dietary_tags = all_tags
            updated_count += 1
        
        # Commit changes
        self.db.commit()
        logger.info(f"Updated {updated_count} recipes with comprehensive dietary tags")
        
        return updated_count

    def verify_results(self):
        """Verify the results of the dietary tag update"""
        logger.info("Verifying dietary tag updates...")
        
        # Count recipes by dietary tag
        all_tags = []
        recipes = self.db.query(Recipe).all()
        
        for recipe in recipes:
            if recipe.dietary_tags:
                all_tags.extend(recipe.dietary_tags)
        
        # Count frequency
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Sort by frequency
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        
        logger.info(f"Total unique tags: {len(sorted_tags)}")
        logger.info("Tag distribution:")
        for tag, count in sorted_tags[:20]:  # Top 20
            logger.info(f"  {tag}: {count} recipes")
        
        # Check specific categories
        categories = {
            'Dietary': ['vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'nut-free', 'soy-free'],
            'Allergens': ['contains-dairy', 'contains-eggs', 'contains-gluten', 'contains-nuts', 
                         'contains-fish', 'contains-shellfish', 'contains-soy', 'contains-sesame'],
            'Health': ['low-sodium', 'low-sugar', 'high-protein', 'low-carb', 'high-fiber']
        }
        
        for category, tags in categories.items():
            logger.info(f"\n{category} tags:")
            for tag in tags:
                count = tag_counts.get(tag, 0)
                logger.info(f"  {tag}: {count} recipes")

def main():
    """Main function to update all recipes with comprehensive dietary tags"""
    db = SessionLocal()
    
    try:
        analyzer = ComprehensiveDietaryAnalyzer(db)
        
        # Update all recipes
        updated_count = analyzer.update_all_recipes()
        
        # Verify results
        analyzer.verify_results()
        
        logger.info(f"✅ Successfully updated {updated_count} recipes with comprehensive dietary tags!")
        
    except Exception as e:
        logger.error(f"❌ Error updating dietary tags: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    main()







