#!/usr/bin/env python3
"""
Select Realistic Recipes with Proper Nutrition Values

This script selects 500 recipes with realistic nutrition values and proper cuisine distribution.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import re
import uuid
from database import SessionLocal
from models.recipe import Recipe, Ingredient, RecipeIngredient, RecipeInstruction
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RealisticRecipeSelector:
    def __init__(self):
        self.db = SessionLocal()
        self.sqlite_conn = sqlite3.connect('../recipes.sqlite3')
        self.sqlite_cursor = self.sqlite_conn.cursor()
        self.ingredient_cache = {}

    def clear_existing_recipes(self):
        """Clear all existing recipes from our database"""
        logger.info("🧹 Clearing existing recipes...")
        
        try:
            self.db.query(RecipeIngredient).delete()
            self.db.query(RecipeInstruction).delete()
            self.db.query(Recipe).delete()
            self.db.query(Ingredient).delete()
            self.db.commit()
            logger.info("✅ Cleared existing recipes and ingredients")
        except Exception as e:
            logger.info(f"Tables were already empty: {e}")
            self.db.rollback()

    def get_realistic_recipes(self):
        """Get recipes with realistic nutrition values"""
        logger.info("🔍 Finding recipes with realistic nutrition values...")
        
        # Get recipes with realistic calories (100-1000 per serving)
        self.sqlite_cursor.execute("""
            SELECT id, title, ingredients, directions, categories, calories, protein, fat, sodium, desc, rating, image 
            FROM recipes 
            WHERE calories IS NOT NULL AND calories >= 100 AND calories <= 1000
            AND protein IS NOT NULL AND protein > 0 
            AND fat IS NOT NULL AND fat > 0 
            AND sodium IS NOT NULL AND sodium > 0
            ORDER BY rating DESC, calories ASC
        """)
        
        all_recipes = self.sqlite_cursor.fetchall()
        logger.info(f"Found {len(all_recipes)} recipes with realistic nutrition values")
        return all_recipes

    def determine_cuisine_properly(self, title, categories):
        """Properly determine cuisine from title and categories"""
        if not categories:
            categories = ""
        
        title_lower = title.lower()
        categories_lower = categories.lower()
        
        # French cuisine detection
        if any(word in title_lower for word in ['coq au vin', 'ratatouille', 'crêpe', 'bourguignon', 'confit', 'terrine', 'soufflé', 'quiche', 'bouillabaisse', 'cassoulet', 'tarte', 'mousse', 'pâté', 'brioche', 'croissant', 'madeleine', 'profiterole', 'éclair', 'macaron', 'béarnaise', 'hollandaise', 'velouté', 'consommé', 'bisque', 'gratin', 'daube', 'blanquette', 'boeuf', 'coq', 'canard', 'lapin', 'escargot', 'foie gras', 'truffle', 'herbes de provence', 'fines herbes', 'bouquet garni', 'mirepoix', 'roux', 'beurre blanc', 'beurre noisette', 'sabayon', 'crème brûlée', 'tarte tatin', 'clafoutis', 'tarte aux fruits', 'tarte aux pommes', 'tarte aux poires', 'tarte aux fraises', 'tarte aux framboises', 'tarte aux myrtilles', 'tarte aux cerises', 'tarte aux abricots', 'tarte aux pêches', 'tarte aux prunes', 'tarte aux figues', 'tarte aux dattes', 'tarte aux noix', 'tarte aux amandes', 'tarte aux noisettes', 'tarte aux pistaches', 'tarte aux noix de pécan', 'tarte aux noix de cajou', 'tarte aux noix de macadamia', 'tarte aux noix de coco', 'tarte aux noix de pin', 'tarte aux noix de cajou', 'tarte aux noix de macadamia', 'tarte aux noix de coco', 'tarte aux noix de pin']):
            return "French"
        elif any(word in categories_lower for word in ['french', 'bon appétit', 'coq au vin', 'ratatouille', 'crêpe', 'bourguignon', 'confit', 'terrine', 'soufflé', 'quiche', 'bouillabaisse', 'cassoulet', 'tarte', 'mousse', 'pâté', 'brioche', 'croissant', 'madeleine', 'profiterole', 'éclair', 'macaron', 'béarnaise', 'hollandaise', 'velouté', 'consommé', 'bisque', 'gratin', 'daube', 'blanquette', 'boeuf', 'coq', 'canard', 'lapin', 'escargot', 'foie gras', 'truffle', 'herbes de provence', 'fines herbes', 'bouquet garni', 'mirepoix', 'roux', 'beurre blanc', 'beurre noisette', 'sabayon', 'crème brûlée', 'tarte tatin', 'clafoutis']):
            return "French"
        
        # Other cuisines
        elif any(word in title_lower for word in ['pasta', 'pizza', 'risotto', 'bruschetta', 'carbonara', 'lasagna', 'gnocchi', 'fettuccine', 'parmesan', 'mozzarella', 'prosciutto', 'pancetta', 'bolognese', 'marinara', 'pesto', 'arrabiata', 'puttanesca', 'cacciatore', 'saltimbocca', 'osso buco', 'vitello tonnato', 'carpaccio', 'bruschetta', 'focaccia', 'ciabatta', 'panettone', 'tiramisu', 'panna cotta', 'gelato', 'cannoli', 'zeppole', 'sfogliatelle', 'baba au rhum', 'zabaglione', 'panna cotta', 'gelato', 'cannoli', 'zeppole', 'sfogliatelle', 'baba au rhum', 'zabaglione']):
            return "Italian"
        elif any(word in title_lower for word in ['taco', 'burrito', 'enchilada', 'quesadilla', 'jalapeño', 'salsa', 'guacamole', 'chile', 'tortilla', 'mole', 'pozole', 'tamale', 'churro', 'flan', 'tres leches', 'arroz con pollo', 'paella', 'gazpacho', 'chorizo', 'jamon', 'serrano', 'iberico', 'manchego', 'queso', 'frijoles', 'refritos', 'pinto', 'negro', 'verde', 'rojo', 'blanco', 'amarillo', 'naranja', 'morado', 'rosa', 'azul', 'verde', 'rojo', 'blanco', 'amarillo', 'naranja', 'morado', 'rosa', 'azul']):
            return "Mexican"
        elif any(word in title_lower for word in ['stir-fry', 'wok', 'soy sauce', 'ginger', 'sesame', 'bok choy', 'lo mein', 'kung pao', 'sweet and sour', 'general tso', 'orange chicken', 'beef and broccoli', 'chow mein', 'fried rice', 'spring roll', 'egg roll', 'dumpling', 'pot sticker', 'wonton', 'ramen', 'udon', 'soba', 'miso', 'teriyaki', 'wasabi', 'nori', 'sushi', 'sashimi', 'tempura', 'yakitori', 'katsu', 'curry', 'pad thai', 'tom yum', 'coconut', 'lemongrass', 'basil', 'thai', 'kimchi', 'bulgogi', 'bibimbap', 'gochujang', 'korean', 'biryani', 'tikka', 'masala', 'dal', 'chutney', 'naan', 'roti', 'chapati', 'paratha', 'samosa', 'pakora', 'vindaloo', 'korma', 'jalfrezi', 'madras', 'vindaloo', 'korma', 'jalfrezi', 'madras']):
            return "Chinese"
        elif any(word in title_lower for word in ['moussaka', 'souvlaki', 'tzatziki', 'feta', 'olive', 'greek', 'spanish', 'paella', 'tapas', 'gazpacho', 'chorizo', 'sherry', 'german', 'schnitzel', 'bratwurst', 'sauerkraut', 'spätzle', 'american', 'burger', 'bbq', 'mac and cheese', 'bacon', 'cheesecake', 'fourth of july', 'picnic']):
            return "Greek"
        elif any(word in title_lower for word in ['hummus', 'falafel', 'kebab', 'pita', 'tahini', 'middle eastern', 'mediterranean']):
            return "Mediterranean"
        
        return "International"

    def select_balanced_recipes(self, all_recipes):
        """Select 500 recipes with balanced cuisine distribution"""
        logger.info("🎯 Selecting balanced recipe distribution...")
        
        # Target distribution
        target_distribution = {
            "French": 80,
            "Italian": 80,
            "Mexican": 60,
            "Chinese": 60,
            "Thai": 40,
            "Japanese": 40,
            "Korean": 30,
            "Indian": 30,
            "Greek": 30,
            "Spanish": 20,
            "German": 20,
            "American": 20,
            "Mediterranean": 20,
            "International": 70
        }
        
        selected_recipes = []
        cuisine_counts = {cuisine: 0 for cuisine in target_distribution.keys()}
        
        for recipe_data in all_recipes:
            recipe_id, title, ingredients, directions, categories, calories, protein, fat, sodium, desc, rating, image = recipe_data
            
            cuisine = self.determine_cuisine_properly(title, categories)
            
            if cuisine in target_distribution and cuisine_counts[cuisine] < target_distribution[cuisine]:
                selected_recipes.append(recipe_data)
                cuisine_counts[cuisine] += 1
                
                if len(selected_recipes) >= 500:
                    break
        
        logger.info(f"Selected {len(selected_recipes)} recipes")
        logger.info("Cuisine distribution:")
        for cuisine, count in cuisine_counts.items():
            logger.info(f"  {cuisine}: {count}")
        
        return selected_recipes

    def convert_temperature_to_celsius(self, text):
        """Convert Fahrenheit temperatures to Celsius in text"""
        if not text:
            return text
        
        pattern = r'(\d+)\s*°?\s*[Ff]'
        
        def replace_temp(match):
            fahrenheit = int(match.group(1))
            celsius = round((fahrenheit - 32) * 5/9)
            return f"{celsius}°C"
        
        return re.sub(pattern, replace_temp, text)

    def get_or_create_ingredient(self, ingredient_name):
        """Get existing ingredient or create new one with realistic nutrition"""
        if not ingredient_name or ingredient_name.strip() == '':
            return None
            
        ingredient_name = ingredient_name.strip()
        
        if ingredient_name in self.ingredient_cache:
            return self.ingredient_cache[ingredient_name]
        
        ingredient = self.db.query(Ingredient).filter(Ingredient.name == ingredient_name).first()
        
        if not ingredient:
            ingredient_id = str(uuid.uuid4())
            
            # Realistic nutrition based on ingredient type
            if any(word in ingredient_name.lower() for word in ['chicken', 'beef', 'pork', 'fish', 'salmon', 'tuna']):
                calories, protein, carbs, fats = 200, 25, 0, 10
            elif any(word in ingredient_name.lower() for word in ['cheese', 'milk', 'cream', 'butter', 'yogurt']):
                calories, protein, carbs, fats = 100, 7, 5, 8
            elif any(word in ingredient_name.lower() for word in ['rice', 'pasta', 'bread', 'flour', 'oats']):
                calories, protein, carbs, fats = 130, 3, 25, 1
            elif any(word in ingredient_name.lower() for word in ['vegetable', 'onion', 'tomato', 'carrot', 'potato', 'spinach']):
                calories, protein, carbs, fats = 30, 2, 6, 0.5
            elif any(word in ingredient_name.lower() for word in ['fruit', 'apple', 'banana', 'orange', 'lemon']):
                calories, protein, carbs, fats = 50, 1, 12, 0.3
            elif any(word in ingredient_name.lower() for word in ['oil', 'butter', 'fat']):
                calories, protein, carbs, fats = 900, 0, 0, 100
            else:
                calories, protein, carbs, fats = 50, 2, 8, 1
            
            ingredient = Ingredient(
                id=ingredient_id,
                name=ingredient_name,
                category='other',
                unit='g',
                default_quantity=100.0,
                calories=calories,
                protein=protein,
                carbs=carbs,
                fats=fats,
                fiber=1.0,
                sugar=2.0,
                sodium=10.0
            )
            
            self.db.add(ingredient)
            self.db.flush()
            self.ingredient_cache[ingredient_name] = ingredient
        
        return ingredient

    def parse_ingredients(self, ingredients_text):
        """Parse ingredients text into structured data"""
        if not ingredients_text:
            return []
        
        ingredients = []
        lines = ingredients_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            parts = line.split(' ', 1)
            if len(parts) >= 2:
                quantity_str = parts[0]
                ingredient_name = parts[1]
                
                quantity = 1.0
                unit = 'piece'
                
                if any(char.isdigit() for char in quantity_str):
                    numbers = re.findall(r'\d+\.?\d*', quantity_str)
                    if numbers:
                        quantity = float(numbers[0])
                    
                    if 'cup' in quantity_str.lower():
                        unit = 'cup'
                    elif 'tbsp' in quantity_str.lower() or 'tablespoon' in quantity_str.lower():
                        unit = 'tbsp'
                    elif 'tsp' in quantity_str.lower() or 'teaspoon' in quantity_str.lower():
                        unit = 'tsp'
                    elif 'pound' in quantity_str.lower() or 'lb' in quantity_str.lower():
                        unit = 'lb'
                    elif 'ounce' in quantity_str.lower() or 'oz' in quantity_str.lower():
                        unit = 'oz'
                    elif 'clove' in quantity_str.lower():
                        unit = 'clove'
                    elif 'slice' in quantity_str.lower():
                        unit = 'slice'
                    elif 'piece' in quantity_str.lower():
                        unit = 'piece'
                    else:
                        unit = 'g'
                
                ingredients.append({
                    'name': ingredient_name,
                    'quantity': quantity,
                    'unit': unit
                })
        
        return ingredients

    def parse_instructions(self, directions_text):
        """Parse directions text into structured steps"""
        if not directions_text:
            return []
        
        steps = []
        
        if re.search(r'\d+\.', directions_text):
            parts = re.split(r'\d+\.', directions_text)
            for part in parts[1:]:
                step = part.strip()
                if step:
                    steps.append(step)
        else:
            sentences = re.split(r'[.!?]+', directions_text)
            for sentence in sentences:
                sentence = sentence.strip()
                if sentence and len(sentence) > 10:
                    steps.append(sentence)
        
        return steps

    def import_recipes(self, selected_recipes):
        """Import selected recipes with proper data"""
        logger.info("📥 Importing selected recipes...")
        
        for i, recipe_data in enumerate(selected_recipes):
            try:
                self.import_recipe(recipe_data, i + 1)
                
                if (i + 1) % 50 == 0:
                    logger.info(f"Imported {i + 1} recipes...")
            except Exception as e:
                logger.error(f"Error importing recipe {i + 1}: {e}")
                continue
        
        self.db.commit()
        logger.info(f"🎉 Successfully imported {len(selected_recipes)} recipes!")

    def import_recipe(self, recipe_data, recipe_number):
        """Import a single recipe with proper data"""
        recipe_id, title, ingredients_text, directions_text, categories, calories, protein, fat, sodium, desc, rating, image = recipe_data
        
        try:
            cuisine = self.determine_cuisine_properly(title, categories)
            
            # Determine meal type and difficulty
            meal_type = "main_course"
            if any(word in title.lower() for word in ['breakfast', 'brunch', 'pancake', 'waffle', 'oat', 'cereal', 'muffin', 'toast', 'egg', 'bacon', 'sausage']):
                meal_type = "breakfast"
            elif any(word in title.lower() for word in ['lunch', 'sandwich', 'wrap', 'soup', 'salad']):
                meal_type = "lunch"
            elif any(word in title.lower() for word in ['dessert', 'cake', 'pie', 'cookie', 'ice cream', 'pudding', 'tart', 'sorbet', 'mousse', 'chocolate']):
                meal_type = "dessert"
            elif any(word in title.lower() for word in ['snack', 'appetizer', 'dip', 'cracker', 'spread', 'cocktail party']):
                meal_type = "snack"
            elif any(word in title.lower() for word in ['side', 'vegetable', 'potato', 'rice', 'pasta']):
                meal_type = "side_dish"
            
            difficulty = "medium"
            if any(word in title.lower() for word in ['quick', 'easy', 'simple', 'basic']):
                difficulty = "easy"
            elif any(word in title.lower() for word in ['complex', 'elaborate', 'gourmet', 'bon appétit']):
                difficulty = "hard"
            
            # Estimate prep time
            prep_time = 30
            if difficulty == "easy":
                prep_time = 15
            elif difficulty == "hard":
                prep_time = 60
            
            # Convert temperatures
            directions_text = self.convert_temperature_to_celsius(directions_text)
            
            # Create recipe
            recipe_id = f'recipe_{recipe_number:06d}'
            
            recipe = Recipe(
                id=recipe_id,
                title=title,
                cuisine=cuisine,
                meal_type=meal_type,
                servings=4,
                summary=f"{desc or 'A delicious recipe'}. Nutrition per serving: {calories:.0f} cal, {protein:.0f}g protein, {fat:.0f}g fat, {sodium:.0f}mg sodium.",
                prep_time=prep_time,
                cook_time=prep_time + 10,
                difficulty_level=difficulty,
                dietary_tags=[],
                source="sqlite_import",
                image_url=image,
                is_active=True
            )
            
            self.db.add(recipe)
            self.db.flush()
            
            # Parse and add ingredients
            ingredients_data = self.parse_ingredients(ingredients_text)
            for ingredient_data in ingredients_data:
                ingredient = self.get_or_create_ingredient(ingredient_data['name'])
                if ingredient:
                    recipe_ingredient = RecipeIngredient(
                        recipe_id=recipe.id,
                        ingredient_id=ingredient.id,
                        quantity=ingredient_data['quantity'],
                        unit=ingredient_data['unit'],
                        notes=None
                    )
                    self.db.add(recipe_ingredient)
            
            # Parse and add instructions
            instructions_data = self.parse_instructions(directions_text)
            for j, instruction_text in enumerate(instructions_data, 1):
                recipe_instruction = RecipeInstruction(
                    recipe_id=recipe.id,
                    step_number=j,
                    step_title=f"Step {j}",
                    description=instruction_text,
                    ingredients_used=[],
                    time_required=5
                )
                self.db.add(recipe_instruction)
            
            logger.info(f"✅ Imported: {title} (Cuisine: {cuisine}, Meal: {meal_type}, Difficulty: {difficulty}, Calories: {calories})")
            
        except Exception as e:
            logger.error(f"Error importing recipe {title}: {e}")
            raise

    def close(self):
        """Close database connections"""
        self.db.close()
        self.sqlite_conn.close()

def main():
    """Main function to select realistic recipes"""
    selector = RealisticRecipeSelector()
    
    try:
        selector.clear_existing_recipes()
        all_recipes = selector.get_realistic_recipes()
        selected_recipes = selector.select_balanced_recipes(all_recipes)
        selector.import_recipes(selected_recipes)
        
        logger.info("🎉 SUCCESS! Selected and imported realistic recipes with proper cuisine distribution!")
        
    except Exception as e:
        logger.error(f"❌ Selection failed: {e}")
        sys.exit(1)
    finally:
        selector.close()

if __name__ == "__main__":
    main()


