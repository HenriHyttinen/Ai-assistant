#!/usr/bin/env python3
"""
Fetch USDA Nutrition Data

Fetches accurate nutrition data from USDA FoodData Central API
for ingredients missing nutrition values.
"""

import sys
import os
import requests
import json
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import Ingredient
from typing import Dict, Optional, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class USDANutritionFetcher:
    """
    Fetches nutrition data from USDA FoodData Central API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('USDA_API_KEY', 'mGKlgKZsebhDF8m21oR3HgxcwrYvt6geLVk1LKUv')
        self.base_url = 'https://api.nal.usda.gov/fdc/v1'
        self.session = requests.Session()
        self.cache = {}  # Cache API responses
        self.updated_count = 0
        self.failed_count = 0
        self.skipped_count = 0
        self.db = SessionLocal()
        
    def search_food(self, query: str, max_results: int = 5) -> Optional[Dict]:
        """
        Search for food in USDA database
        """
        try:
            # Check cache first
            if query.lower() in self.cache:
                return self.cache[query.lower()]
            
            # API endpoint for food search
            url = f"{self.base_url}/foods/search"
            params = {
                'api_key': self.api_key,
                'query': query,
                'pageSize': max_results,
                'pageNumber': 1
            }
            
            # Add headers for better API response
            headers = {
                'Content-Type': 'application/json'
            }
            
            response = self.session.get(url, params=params, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('foods') and len(data.get('foods', [])) > 0:
                    # Cache the result
                    self.cache[query.lower()] = data
                    return data
                else:
                    logger.debug(f"No results found for '{query}'")
                    return None
            elif response.status_code == 429:
                logger.warning(f"Rate limited. Waiting 10 seconds...")
                time.sleep(10)
                return None
            elif response.status_code == 403:
                logger.error(f"API key invalid or quota exceeded. Check your USDA API key.")
                return None
            else:
                logger.warning(f"API error for '{query}': {response.status_code} - {response.text[:200]}")
                return None
                
        except Exception as e:
            logger.error(f"Error searching for '{query}': {e}")
            return None
    
    def extract_nutrition_from_food(self, food_item: Dict) -> Optional[Dict[str, float]]:
        """
        Extract nutrition values from USDA food item
        """
        try:
            nutrition = {
                'calories': 0,
                'protein': 0,
                'carbs': 0,
                'fats': 0,
                'fiber': 0,
                'sugar': 0,
                'sodium': 0
            }
            
            # Get food nutrients
            nutrients = food_item.get('foodNutrients', [])
            
            # Nutrient IDs in USDA database
            # USDA uses nutrientId and nutrientNumber
            nutrient_map = {
                1008: 'calories',  # Energy (kcal) - nutrientId 1008
                208: 'calories',   # Energy (kcal) - alternative ID
                1003: 'protein',   # Protein - nutrientId 1003
                203: 'protein',    # Protein - alternative number
                1005: 'carbs',     # Carbohydrate, by difference - nutrientId 1005
                205: 'carbs',      # Carbohydrate - alternative number
                1004: 'fats',      # Total lipid (fat) - nutrientId 1004
                204: 'fats',      # Total lipid - alternative number
                1079: 'fiber',     # Fiber, total dietary - nutrientId 1079
                291: 'fiber',     # Fiber - alternative number
                2000: 'sugar',    # Sugars, total including NLEA - nutrientId 2000
                269: 'sugar',     # Sugars - alternative number
                1093: 'sodium',   # Sodium, Na - nutrientId 1093
                307: 'sodium',    # Sodium - alternative number
            }
            
            for nutrient in nutrients:
                # USDA API format: nutrientId, nutrientName, value (not amount)
                nutrient_id = nutrient.get('nutrientId')
                nutrient_number = nutrient.get('nutrientNumber')
                nutrient_name = (nutrient.get('nutrientName') or '').lower()
                value = nutrient.get('value', 0)
                
                # Match by nutrientId first
                if nutrient_id and nutrient_id in nutrient_map:
                    key = nutrient_map[nutrient_id]
                    nutrition[key] = float(value) if value else 0
                # Match by nutrientNumber
                elif nutrient_number:
                    try:
                        num = int(nutrient_number)
                        if num in nutrient_map:
                            key = nutrient_map[num]
                            nutrition[key] = float(value) if value else 0
                    except (ValueError, TypeError):
                        pass
                # Fallback: match by name
                elif 'energy' in nutrient_name or 'calorie' in nutrient_name:
                    if value and value > 0:
                        nutrition['calories'] = float(value)
                elif 'protein' in nutrient_name:
                    if value and value > 0:
                        nutrition['protein'] = float(value)
                elif 'carbohydrate' in nutrient_name or 'carb' in nutrient_name:
                    if value and value > 0:
                        nutrition['carbs'] = float(value)
                elif 'fat' in nutrient_name or 'lipid' in nutrient_name:
                    if value and value > 0:
                        nutrition['fats'] = float(value)
                elif 'fiber' in nutrient_name:
                    if value and value > 0:
                        nutrition['fiber'] = float(value)
                elif 'sugar' in nutrient_name:
                    if value and value > 0:
                        nutrition['sugar'] = float(value)
                elif 'sodium' in nutrient_name:
                    if value and value > 0:
                        nutrition['sodium'] = float(value)
            
            # Return if we got at least calories or protein
            if nutrition['calories'] > 0 or nutrition['protein'] > 0:
                return nutrition
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting nutrition: {e}")
            return None
    
    def find_best_match(self, ingredient_name: str) -> Optional[Dict[str, float]]:
        """
        Find best nutrition match for an ingredient from USDA
        """
        # Clean ingredient name for search
        clean_name = self._clean_ingredient_name(ingredient_name)
        
        # Try direct search first
        search_result = self.search_food(clean_name)
        
        if not search_result or not search_result.get('foods'):
            # Try alternative names
            alternatives = self._get_alternative_names(clean_name)
            for alt in alternatives:
                search_result = self.search_food(alt)
                if search_result and search_result.get('foods'):
                    break
        
        if not search_result or not search_result.get('foods'):
            return None
        
        # Get first result (usually most relevant)
        food = search_result['foods'][0]
        
        # Extract nutrition
        nutrition = self.extract_nutrition_from_food(food)
        
        if nutrition:
            logger.info(f"✅ Found match for '{ingredient_name}': {food.get('description', 'Unknown')}")
            logger.info(f"   Nutrition: {nutrition['calories']:.1f} cal, {nutrition['protein']:.1f}g protein")
        
        return nutrition
    
    def _clean_ingredient_name(self, name: str) -> str:
        """
        Clean ingredient name for USDA search
        """
        import re
        
        # Remove preparation notes
        original = name
        name = name.lower()
        
        # Remove common preparation words
        prep_words = ['chopped', 'diced', 'sliced', 'minced', 'fresh', 'dried', 
                     'finely', 'coarsely', 'thinly', 'about', 'cups', 'tablespoons',
                     'teaspoons', 'optional', 'trimmed', 'peeled', 'pitted', 'seeded',
                     'grated', 'crushed', 'beaten', 'lightly', 'room temperature',
                     'divided', 'for garnish', 'to taste']
        
        for word in prep_words:
            name = name.replace(word, ' ')
        
        # Remove quantity info
        name = re.sub(r'\d+[\s/]*\d*\s*(cup|cups|tbsp|tsp|oz|lb|g|kg|ml)', '', name)
        name = re.sub(r'\([^)]*\)', ' ', name)  # Remove parentheses
        name = re.sub(r',[^,]*$', '', name)  # Remove trailing comma phrases
        
        # Remove leading hyphens and special chars
        name = re.sub(r'^[-,\s]+', '', name)
        name = re.sub(r'[-,\s]+$', '', name)
        
        # Clean up whitespace
        name = ' '.join(name.split())
        
        # If name is too short or empty, return original
        if len(name) < 2:
            return original.lower().strip()
        
        return name.strip()
    
    def _get_alternative_names(self, name: str) -> list:
        """
        Generate alternative search names
        """
        alternatives = [name]
        
        # Common substitutions
        substitutions = {
            'lemon juice': 'lemon juice raw',
            'lime juice': 'lime juice raw',
            'orange juice': 'orange juice raw',
            'parsley': 'parsley fresh',
            'thyme': 'thyme fresh',
            'oregano': 'oregano dried',
            'basil': 'basil fresh',
            'mayonnaise': 'mayonnaise regular',
            'mustard': 'mustard prepared yellow',
            'soy sauce': 'soy sauce made from soy and wheat',
            'water': 'water tap',
            'salt': 'salt table',
            'vanilla extract': 'vanilla extract',
            'cocoa powder': 'cocoa powder unsweetened',
            'cornstarch': 'cornstarch',
            'baking powder': 'baking powder double-acting',
            'baking soda': 'baking soda',
            'vinegar': 'vinegar distilled',
            'balsamic vinegar': 'vinegar balsamic',
            'red wine vinegar': 'vinegar red wine',
        }
        
        for key, value in substitutions.items():
            if key in name:
                alternatives.append(value)
                break
        
        return alternatives
    
    def update_ingredient_from_usda(self, ingredient: Ingredient) -> bool:
        """
        Update ingredient nutrition from USDA
        """
        try:
            # Skip if already has calories
            if ingredient.calories and ingredient.calories > 0:
                return False
            
            # Find nutrition data
            nutrition = self.find_best_match(ingredient.name)
            
            if not nutrition:
                return False
            
            # Update ingredient
            ingredient.calories = round(nutrition['calories'], 1)
            ingredient.protein = round(nutrition['protein'], 1)
            ingredient.carbs = round(nutrition['carbs'], 1)
            ingredient.fats = round(nutrition['fats'], 1)
            
            if nutrition['fiber'] > 0:
                ingredient.fiber = round(nutrition['fiber'], 1)
            if nutrition['sugar'] > 0:
                ingredient.sugar = round(nutrition['sugar'], 1)
            if nutrition['sodium'] > 0:
                ingredient.sodium = round(nutrition['sodium'], 1)
            
            self.db.add(ingredient)
            self.updated_count += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating {ingredient.name}: {e}")
            self.failed_count += 1
            return False
    
    def fetch_for_all_missing(self, limit: Optional[int] = None, only_used: bool = True):
        """
        Fetch nutrition data for ingredients missing calories
        Optimized to only fetch for ingredients actually used in recipes
        """
        logger.info("🔍 Finding ingredients missing nutrition data...")
        
        if only_used:
            # Only fetch for ingredients actually used in recipes (performance optimization)
            from models.recipe import RecipeIngredient
            from sqlalchemy import func, distinct
            
            # Get ingredient IDs that are actually used (simpler approach - avoids subquery issues)
            used_ingredient_ids = [
                rid for (rid,) in self.db.query(RecipeIngredient.ingredient_id).filter(
                    RecipeIngredient.ingredient_id.isnot(None)
                ).distinct().all()
            ]
            
            if not used_ingredient_ids:
                logger.warning("⚠️  No ingredients found in recipes. Fetching for all ingredients instead.")
                query = self.db.query(Ingredient).filter(Ingredient.calories == 0)
            else:
                # Get ingredients that are used AND missing calories
                query = self.db.query(Ingredient).filter(
                    Ingredient.id.in_(used_ingredient_ids),
                    Ingredient.calories == 0
                ).order_by(Ingredient.name)  # Order for consistency
                
                logger.info(f"✅ Optimized: Only fetching for {len(used_ingredient_ids)} ingredients used in recipes")
        else:
            # Fetch for all missing ingredients (slower)
            query = self.db.query(Ingredient).filter(
                Ingredient.calories == 0
            )
        
        if limit:
            query = query.limit(limit)
            logger.info(f"✅ Limited to first {limit} ingredients")
        
        ingredients = query.all()
        
        logger.info(f"Found {len(ingredients)} ingredients to update")
        
        for i, ingredient in enumerate(ingredients, 1):
            try:
                updated = self.update_ingredient_from_usda(ingredient)
                
                if not updated:
                    self.skipped_count += 1
                
                # Commit every 10 ingredients to avoid large transactions
                if i % 10 == 0:
                    self.db.commit()
                    logger.info(f"Progress: {i}/{len(ingredients)} ingredients processed "
                              f"({self.updated_count} updated, {self.skipped_count} skipped)")
                    time.sleep(1.5)  # Rate limiting - be nice to USDA API
                elif i % 5 == 0:
                    time.sleep(0.8)  # Rate limiting
                else:
                    time.sleep(0.3)  # Small delay between requests
                    
            except Exception as e:
                logger.error(f"Error processing ingredient {ingredient.name}: {e}")
                self.failed_count += 1
                continue
        
        self.db.commit()
        
        logger.info(f"\n📊 Summary:")
        logger.info(f"   ✅ Updated: {self.updated_count} ingredients")
        logger.info(f"   ⏭️  Skipped: {self.skipped_count} ingredients (no match found)")
        logger.info(f"   ❌ Failed: {self.failed_count} ingredients")
        logger.info(f"\n💡 Performance Note:")
        logger.info(f"   • Only updated ingredients used in recipes (optimized)")
        logger.info(f"   • Database queries will remain fast with proper indexing")
        logger.info(f"   • Can fetch more ingredients if needed")
    
    def close(self):
        """Close database connection"""
        self.db.close()

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch nutrition data from USDA API')
    parser.add_argument('--api-key', help='USDA API key (or set USDA_API_KEY env var)', 
                       default=os.getenv('USDA_API_KEY', 'DEMO_KEY'))
    parser.add_argument('--limit', type=int, help='Limit number of ingredients to process')
    parser.add_argument('--all', action='store_true', help='Fetch for all missing ingredients (not just used ones)')
    parser.add_argument('--test', action='store_true', help='Test with a few ingredients')
    
    args = parser.parse_args()
    
    fetcher = USDANutritionFetcher(api_key=args.api_key)
    
    try:
        if args.test:
            # Test with a few common ingredients
            test_ingredients = [
                'mayonnaise',
                'lemon juice',
                'vanilla extract',
                'soy sauce',
                'parsley'
            ]
            
            logger.info("🧪 Testing USDA API with sample ingredients...")
            for ing_name in test_ingredients:
                logger.info(f"\nTesting: {ing_name}")
                nutrition = fetcher.find_best_match(ing_name)
                if nutrition:
                    print(f"  ✅ Found: {nutrition}")
                else:
                    print(f"  ❌ Not found")
                    time.sleep(1)
        else:
            fetcher.fetch_for_all_missing(limit=args.limit, only_used=not args.all)
            logger.info(f"\n🎉 USDA nutrition fetch complete!")
            
            if fetcher.updated_count > 0:
                logger.info("\n🔄 Next step: Recalculate all recipes from updated ingredients")
                logger.info("   Run: python3 scripts/optimize_and_calculate_micronutrients.py")
        
    except Exception as e:
        logger.error(f"❌ Fetch failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        fetcher.close()

if __name__ == "__main__":
    main()

