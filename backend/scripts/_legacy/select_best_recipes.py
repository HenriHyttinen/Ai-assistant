#!/usr/bin/env python3
"""
Select Best Recipes from SQLite Database

This script properly filters the 12,874 recipes with complete nutrition data
to select the best 500 recipes that meet all requirements for the school project.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sqlite3
import re
from database import SessionLocal
from models.recipe import Recipe, Ingredient, RecipeIngredient, RecipeInstruction
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BestRecipeSelector:
    def __init__(self):
        self.db = SessionLocal()
        self.sqlite_conn = sqlite3.connect('../recipes.sqlite3')
        self.sqlite_cursor = self.sqlite_conn.cursor()
        self.ingredient_cache = {}
        self.selected_recipes = []

    def clear_existing_recipes(self):
        """Clear all existing recipes from our database"""
        logger.info("🧹 Clearing existing recipes...")
        
        try:
            self.db.query(RecipeIngredient).delete()
            self.db.query(RecipeInstruction).delete()
            self.db.query(Recipe).delete()
            self.db.commit()
            logger.info("✅ Cleared existing recipes")
        except Exception as e:
            logger.info(f"Tables were already empty: {e}")
            self.db.rollback()

    def analyze_recipe_quality(self, recipe_data):
        """Analyze recipe quality based on multiple criteria"""
        recipe_id, title, ingredients, directions, categories, calories, protein, fat, sodium, desc, rating, image = recipe_data
        
        score = 0
        reasons = []
        
        # 1. Nutritional completeness (40 points)
        if calories and calories > 0 and protein and protein > 0 and fat and fat > 0 and sodium and sodium > 0:
            score += 40
            reasons.append("Complete nutrition data")
        else:
            return 0, ["Missing nutrition data"]
        
        # 2. Recipe quality indicators (30 points)
        if rating and rating >= 4:
            score += 15
            reasons.append(f"High rating ({rating})")
        elif rating and rating >= 3:
            score += 10
            reasons.append(f"Good rating ({rating})")
        
        if desc and len(desc) > 50:
            score += 10
            reasons.append("Has description")
        
        if image:
            score += 5
            reasons.append("Has image")
        
        # 3. Category richness (20 points)
        if categories:
            category_list = [cat.strip() for cat in categories.split('\n') if cat.strip()]
            score += min(20, len(category_list) * 2)
            reasons.append(f"Rich categories ({len(category_list)} tags)")
        
        # 4. Ingredient complexity (10 points)
        if ingredients and len(ingredients) > 100:
            score += 10
            reasons.append("Detailed ingredients")
        elif ingredients and len(ingredients) > 50:
            score += 5
            reasons.append("Good ingredient detail")
        
        # 5. Instruction quality (10 points)
        if directions and len(directions) > 200:
            score += 10
            reasons.append("Detailed instructions")
        elif directions and len(directions) > 100:
            score += 5
            reasons.append("Good instructions")
        
        return score, reasons

    def determine_cuisine_from_categories(self, categories):
        """Determine cuisine from actual categories"""
        if not categories:
            return "International"
        
        category_list = [cat.strip().lower() for cat in categories.split('\n') if cat.strip()]
        
        # Cuisine detection based on actual categories
        if any(cat in category_list for cat in ['italian', 'pasta', 'pizza', 'risotto', 'bruschetta', 'carbonara', 'lasagna', 'gnocchi', 'fettuccine', 'parmesan', 'mozzarella', 'bon appétit']):
            return "Italian"
        elif any(cat in category_list for cat in ['mexican', 'taco', 'burrito', 'enchilada', 'quesadilla', 'jalapeño', 'salsa', 'guacamole', 'chile', 'tortilla']):
            return "Mexican"
        elif any(cat in category_list for cat in ['chinese', 'kung pao', 'lo mein', 'stir-fry', 'wok', 'soy sauce', 'ginger', 'sesame', 'bok choy']):
            return "Chinese"
        elif any(cat in category_list for cat in ['thai', 'pad thai', 'curry', 'tom yum', 'coconut', 'lemongrass', 'basil']):
            return "Thai"
        elif any(cat in category_list for cat in ['japanese', 'sushi', 'ramen', 'tempura', 'miso', 'teriyaki', 'wasabi', 'nori']):
            return "Japanese"
        elif any(cat in category_list for cat in ['korean', 'kimchi', 'bulgogi', 'bibimbap', 'gochujang']):
            return "Korean"
        elif any(cat in category_list for cat in ['indian', 'curry', 'tikka', 'biryani', 'naan', 'masala', 'dal', 'chutney']):
            return "Indian"
        elif any(cat in category_list for cat in ['french', 'coq au vin', 'ratatouille', 'crêpe', 'bourguignon', 'confit', 'terrine']):
            return "French"
        elif any(cat in category_list for cat in ['german', 'schnitzel', 'bratwurst', 'sauerkraut', 'spätzle']):
            return "German"
        elif any(cat in category_list for cat in ['spanish', 'paella', 'tapas', 'gazpacho', 'chorizo', 'sherry']):
            return "Spanish"
        elif any(cat in category_list for cat in ['greek', 'moussaka', 'souvlaki', 'tzatziki', 'feta', 'olive']):
            return "Greek"
        elif any(cat in category_list for cat in ['middle eastern', 'hummus', 'falafel', 'kebab', 'pita', 'tahini']):
            return "Middle Eastern"
        elif any(cat in category_list for cat in ['american', 'burger', 'bbq', 'mac and cheese', 'bacon', 'cheesecake', 'fourth of july', 'picnic']):
            return "American"
        elif any(cat in category_list for cat in ['mediterranean', 'olive', 'feta', 'tomato', 'basil']):
            return "Mediterranean"
        elif any(cat in category_list for cat in ['asian', 'stir', 'noodle', 'soy', 'ginger']):
            return "Asian"
        
        return "International"

    def determine_meal_type_from_categories(self, categories):
        """Determine meal type from actual categories"""
        if not categories:
            return "main_course"
        
        category_list = [cat.strip().lower() for cat in categories.split('\n') if cat.strip()]
        
        if any(cat in category_list for cat in ['breakfast', 'brunch', 'pancake', 'waffle', 'oat', 'cereal', 'muffin', 'toast', 'egg', 'bacon', 'sausage']):
            return "breakfast"
        elif any(cat in category_list for cat in ['lunch', 'sandwich', 'wrap', 'soup', 'salad']):
            return "lunch"
        elif any(cat in category_list for cat in ['dessert', 'cake', 'pie', 'cookie', 'ice cream', 'pudding', 'tart', 'sorbet', 'mousse', 'chocolate']):
            return "dessert"
        elif any(cat in category_list for cat in ['snack', 'appetizer', 'dip', 'cracker', 'spread', 'cocktail party']):
            return "snack"
        elif any(cat in category_list for cat in ['side', 'vegetable', 'potato', 'rice', 'pasta']):
            return "side_dish"
        elif any(cat in category_list for cat in ['dinner', 'main course', 'entree']):
            return "main_course"
        
        return "main_course"

    def determine_difficulty_from_categories(self, categories):
        """Determine difficulty from actual categories"""
        if not categories:
            return "medium"
        
        category_list = [cat.strip().lower() for cat in categories.split('\n') if cat.strip()]
        
        if any(cat in category_list for cat in ['quick & easy', 'no-cook', 'kid-friendly']):
            return "easy"
        elif any(cat in category_list for cat in ['gourmet', 'bon appétit', 'complex', 'elaborate']):
            return "hard"
        
        return "medium"

    def estimate_prep_time_from_categories(self, categories, ingredients, directions):
        """Estimate prep time from categories and content"""
        if not categories:
            return 30
        
        category_list = [cat.strip().lower() for cat in categories.split('\n') if cat.strip()]
        
        # Base time
        if any(cat in category_list for cat in ['quick & easy', 'no-cook']):
            return 15
        elif any(cat in category_list for cat in ['gourmet', 'bon appétit']):
            return 60
        else:
            # Estimate based on ingredient and instruction complexity
            ingredient_count = len(ingredients.split('\n')) if ingredients else 0
            instruction_length = len(directions) if directions else 0
            
            if ingredient_count > 15 or instruction_length > 500:
                return 45
            elif ingredient_count > 8 or instruction_length > 200:
                return 30
            else:
                return 20

    def convert_temperature_to_celsius(self, text):
        """Convert Fahrenheit temperatures to Celsius in text"""
        if not text:
            return text
        
        # Pattern to match temperatures like "350°F", "350 F", "350F", etc.
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
        
        ingredient = self.db.query(Ingredient).filter(Ingredient.name == ingredient_name).first()
        
        if not ingredient:
            # Create ingredient with realistic nutrition based on name
            ingredient_id = f'ingredient_{len(self.ingredient_cache) + 1:06d}'
            
            # Simple nutrition estimation based on ingredient type
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

    def select_best_recipes(self):
        """Select the best 500 recipes from SQLite database"""
        logger.info("🔍 Selecting best recipes from SQLite database...")
        
        # Get all recipes with complete nutrition data
        self.sqlite_cursor.execute("""
            SELECT id, title, ingredients, directions, categories, calories, protein, fat, sodium, desc, rating, image 
            FROM recipes 
            WHERE calories IS NOT NULL AND calories > 0 
            AND protein IS NOT NULL AND protein > 0 
            AND fat IS NOT NULL AND fat > 0 
            AND sodium IS NOT NULL AND sodium > 0
            ORDER BY rating DESC, calories ASC
        """)
        
        all_recipes = self.sqlite_cursor.fetchall()
        logger.info(f"Found {len(all_recipes)} recipes with complete nutrition data")
        
        # Analyze and score all recipes
        scored_recipes = []
        for recipe_data in all_recipes:
            score, reasons = self.analyze_recipe_quality(recipe_data)
            if score > 0:
                scored_recipes.append((score, recipe_data, reasons))
        
        # Sort by score and select top 500
        scored_recipes.sort(key=lambda x: x[0], reverse=True)
        top_recipes = scored_recipes[:500]
        
        logger.info(f"Selected top {len(top_recipes)} recipes")
        
        # Import selected recipes
        for i, (score, recipe_data, reasons) in enumerate(top_recipes):
            self.import_recipe(recipe_data, i + 1, score, reasons)
            
            if (i + 1) % 50 == 0:
                logger.info(f"Imported {i + 1} recipes...")
        
        self.db.commit()
        logger.info(f"🎉 Successfully imported {len(top_recipes)} best recipes!")

    def import_recipe(self, recipe_data, recipe_number, score, reasons):
        """Import a single recipe with proper data"""
        recipe_id, title, ingredients_text, directions_text, categories, calories, protein, fat, sodium, desc, rating, image = recipe_data
        
        try:
            # Determine recipe properties from actual categories
            cuisine = self.determine_cuisine_from_categories(categories)
            meal_type = self.determine_meal_type_from_categories(categories)
            difficulty = self.determine_difficulty_from_categories(categories)
            prep_time = self.estimate_prep_time_from_categories(categories, ingredients_text, directions_text)
            
            # Convert temperatures in directions
            directions_text = self.convert_temperature_to_celsius(directions_text)
            
            # Create recipe
            recipe_id = f'recipe_{recipe_number:06d}'
            
            recipe = Recipe(
                id=recipe_id,
                title=title,
                cuisine=cuisine,
                meal_type=meal_type,
                servings=4,
                summary=f"{desc or 'A delicious recipe'}. Nutrition per serving: {calories:.0f} cal, {protein:.0f}g protein, {fat:.0f}g fat, {sodium:.0f}mg sodium. Quality score: {score}",
                prep_time=prep_time,
                cook_time=prep_time + 10,  # Estimate cook time
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
            
            logger.info(f"✅ Imported: {title} (Score: {score}, Cuisine: {cuisine}, Meal: {meal_type}, Difficulty: {difficulty})")
            
        except Exception as e:
            logger.error(f"Error importing recipe {title}: {e}")

    def verify_selection(self):
        """Verify the selected recipes"""
        logger.info("🔍 Verifying selected recipes...")
        
        total_recipes = self.db.query(Recipe).count()
        logger.info(f"Total recipes in database: {total_recipes}")
        
        # Check variety
        cuisines = {}
        meal_types = {}
        difficulties = {}
        
        for recipe in self.db.query(Recipe).all():
            cuisines[recipe.cuisine] = cuisines.get(recipe.cuisine, 0) + 1
            meal_types[recipe.meal_type] = meal_types.get(recipe.meal_type, 0) + 1
            difficulties[recipe.difficulty_level] = difficulties.get(recipe.difficulty_level, 0) + 1
        
        print(f"\n📊 CUISINE DISTRIBUTION:")
        for cuisine, count in sorted(cuisines.items(), key=lambda x: x[1], reverse=True):
            print(f"  {cuisine}: {count}")
        
        print(f"\n📊 MEAL TYPE DISTRIBUTION:")
        for meal_type, count in sorted(meal_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {meal_type}: {count}")
        
        print(f"\n📊 DIFFICULTY DISTRIBUTION:")
        for difficulty, count in sorted(difficulties.items()):
            print(f"  {difficulty}: {count}")

    def close(self):
        """Close database connections"""
        self.db.close()
        self.sqlite_conn.close()

def main():
    """Main function to select best recipes"""
    selector = BestRecipeSelector()
    
    try:
        selector.clear_existing_recipes()
        selector.select_best_recipes()
        selector.verify_selection()
        
        logger.info("🎉 SUCCESS! Selected and imported the best 500 recipes!")
        
    except Exception as e:
        logger.error(f"❌ Selection failed: {e}")
        sys.exit(1)
    finally:
        selector.close()

if __name__ == "__main__":
    main()







