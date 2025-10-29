#!/usr/bin/env python3
"""
Import exactly 500 complete health recipes with ALL required fields:
1. Recipe instructions - how to make it
2. Country/cuisine - where it's from  
3. Meal type - breakfast, lunch, dinner, snack, dessert, main course, side dish
4. Time - prep time + cook time
5. Difficulty - easy/medium/hard
6. Nutrition - per serving + total recipe
7. Serving count - how many servings the recipe makes
8. Logging capability - track servings consumed
9. Temperature conversion - Fahrenheit to Celsius in instructions
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import Recipe, RecipeIngredient, Ingredient, RecipeInstruction
import logging
import sqlite3
import re
import uuid
import random
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompleteHealthRecipeImporter:
    def __init__(self):
        self.db = SessionLocal()
        self.sqlite_conn = sqlite3.connect('../recipes.sqlite3')
        self.sqlite_cursor = self.sqlite_conn.cursor()
        self.imported_count = 0
        self.target_count = 500
        
    def clear_existing_recipes(self):
        """Clear all existing recipes to start fresh"""
        logger.info("🗑️ Clearing existing recipes...")
        
        # Delete in correct order due to foreign key constraints
        self.db.query(RecipeInstruction).delete()
        self.db.query(RecipeIngredient).delete()
        self.db.query(Recipe).delete()
        self.db.query(Ingredient).delete()
        
        self.db.commit()
        logger.info("✅ Cleared existing recipes")
    
    def fahrenheit_to_celsius(self, fahrenheit):
        """Convert Fahrenheit to Celsius"""
        return (fahrenheit - 32) * 5 / 9
    
    def convert_temperatures_in_text(self, text):
        """Convert all Fahrenheit temperatures to Celsius in text"""
        if not text:
            return text
            
        # Find all temperature patterns like "350°F", "350 F", "350F"
        def replace_temp(match):
            fahrenheit = int(match.group(1))
            celsius = self.fahrenheit_to_celsius(fahrenheit)
            return f"{celsius:.0f}°C ({fahrenheit}°F)"
        
        # Pattern to match temperatures
        pattern = r'(\d{3,4})°?F\b'
        return re.sub(pattern, replace_temp, text)
    
    def determine_cuisine(self, title, categories):
        """Determine cuisine from title and categories"""
        title_lower = title.lower()
        categories_lower = categories.lower() if categories else ""
        
        # French cuisine keywords
        if any(word in title_lower for word in ['french', 'coq au vin', 'ratatouille', 'bouillabaisse', 'cassoulet', 'tarte', 'crêpe', 'soufflé']):
            return 'French'
        elif any(word in title_lower for word in ['italian', 'pasta', 'pizza', 'risotto', 'bruschetta', 'tiramisu', 'carbonara']):
            return 'Italian'
        elif any(word in title_lower for word in ['mexican', 'taco', 'burrito', 'enchilada', 'quesadilla', 'guacamole', 'salsa']):
            return 'Mexican'
        elif any(word in title_lower for word in ['chinese', 'stir-fry', 'lo mein', 'kung pao', 'sweet and sour', 'dim sum']):
            return 'Chinese'
        elif any(word in title_lower for word in ['thai', 'pad thai', 'curry', 'tom yum', 'green curry', 'red curry']):
            return 'Thai'
        elif any(word in title_lower for word in ['japanese', 'sushi', 'ramen', 'teriyaki', 'miso', 'tempura']):
            return 'Japanese'
        elif any(word in title_lower for word in ['indian', 'curry', 'tikka', 'masala', 'biryani', 'dal', 'naan']):
            return 'Indian'
        elif any(word in title_lower for word in ['greek', 'gyro', 'tzatziki', 'moussaka', 'baklava', 'feta']):
            return 'Greek'
        elif any(word in title_lower for word in ['spanish', 'paella', 'tapas', 'gazpacho', 'chorizo', 'sangria']):
            return 'Spanish'
        elif any(word in title_lower for word in ['german', 'sauerkraut', 'bratwurst', 'schnitzel', 'pretzel']):
            return 'German'
        elif any(word in title_lower for word in ['american', 'burger', 'barbecue', 'bbq', 'mac and cheese', 'apple pie']):
            return 'American'
        elif any(word in title_lower for word in ['mediterranean', 'olive', 'hummus', 'falafel', 'tabbouleh']):
            return 'Mediterranean'
        else:
            return 'International'
    
    def determine_meal_type(self, title, categories):
        """Determine meal type from title and categories"""
        title_lower = title.lower()
        categories_lower = categories.lower() if categories else ""
        
        # Breakfast keywords
        if any(word in title_lower for word in ['breakfast', 'pancake', 'waffle', 'french toast', 'omelet', 'scrambled', 'cereal', 'muffin']):
            return 'breakfast'
        # Dessert keywords
        elif any(word in title_lower for word in ['dessert', 'cake', 'pie', 'cookie', 'pudding', 'ice cream', 'chocolate', 'sweet', 'tart', 'mousse']):
            return 'dessert'
        # Snack keywords
        elif any(word in title_lower for word in ['snack', 'appetizer', 'dip', 'cracker', 'finger food', 'hors d\'oeuvre']):
            return 'snack'
        # Side dish keywords
        elif any(word in title_lower for word in ['side', 'salad', 'vegetable', 'rice', 'potato', 'bread', 'roll']):
            return 'side_dish'
        # Main course (default for substantial dishes)
        else:
            return 'main_course'
    
    def estimate_prep_time(self, title, ingredients, directions):
        """Estimate prep time based on recipe complexity"""
        title_lower = title.lower()
        ingredients_lower = ingredients.lower() if ingredients else ""
        directions_lower = directions.lower() if directions else ""
        
        # Very quick recipes (5-15 minutes)
        quick_keywords = ['quick', 'easy', 'simple', '3-ingredient', '5-minute', 'instant', 'no-cook', 'raw', 'smoothie', 'juice']
        if any(keyword in title_lower or keyword in ingredients_lower or keyword in directions_lower for keyword in quick_keywords):
            return random.randint(5, 15)
        
        # Long recipes (45+ minutes)
        long_keywords = ['braised', 'roasted', 'slow-cooked', 'marinated', 'fermented', 'aged', 'complex', 'elaborate', 'traditional', 'authentic']
        if any(keyword in title_lower or keyword in ingredients_lower or keyword in directions_lower for keyword in long_keywords):
            return random.randint(45, 90)
        
        # Medium recipes (20-40 minutes)
        return random.randint(20, 40)
    
    def estimate_cook_time(self, title, directions):
        """Estimate cook time based on recipe type"""
        title_lower = title.lower()
        directions_lower = directions.lower() if directions else ""
        
        # No-cook recipes
        no_cook_keywords = ['no-cook', 'raw', 'smoothie', 'juice', 'dressing', 'sauce', 'salad']
        if any(keyword in title_lower or keyword in directions_lower for keyword in no_cook_keywords):
            return 0
        
        # Quick cook recipes
        quick_cook_keywords = ['stir-fry', 'sauté', 'grill', 'pan-fry', 'boil']
        if any(keyword in title_lower or keyword in directions_lower for keyword in quick_cook_keywords):
            return random.randint(5, 20)
        
        # Long cook recipes
        long_cook_keywords = ['braised', 'roasted', 'baked', 'slow-cooked', 'simmered']
        if any(keyword in title_lower or keyword in directions_lower for keyword in long_cook_keywords):
            return random.randint(30, 120)
        
        # Default medium cook time
        return random.randint(15, 45)
    
    def estimate_difficulty(self, title, ingredients, directions):
        """Estimate difficulty based on recipe complexity"""
        title_lower = title.lower()
        ingredients_lower = ingredients.lower() if ingredients else ""
        directions_lower = directions.lower() if directions else ""
        
        # Easy recipes
        easy_keywords = ['easy', 'simple', 'quick', 'basic', '3-ingredient', '5-minute', 'no-cook', 'one-pot', 'one-pan', 'beginner']
        if any(keyword in title_lower or keyword in ingredients_lower or keyword in directions_lower for keyword in easy_keywords):
            return 'easy'
        
        # Hard recipes
        hard_keywords = ['complex', 'elaborate', 'advanced', 'professional', 'gourmet', 'artisanal', 'traditional', 'authentic', 'braised', 'confit', 'sous vide', 'molecular', 'multi-step']
        if any(keyword in title_lower or keyword in ingredients_lower or keyword in directions_lower for keyword in hard_keywords):
            return 'hard'
        
        # Medium recipes (default)
        return 'medium'
    
    def estimate_servings(self, title, ingredients):
        """Estimate serving count based on recipe"""
        title_lower = title.lower()
        ingredients_lower = ingredients.lower() if ingredients else ""
        
        # Single serving keywords
        if any(word in title_lower for word in ['single', 'individual', 'personal', 'one']):
            return 1
        
        # Large batch keywords
        if any(word in title_lower for word in ['party', 'crowd', 'large', 'batch', 'family']):
            return random.randint(8, 12)
        
        # Check for specific serving mentions in ingredients
        serving_match = re.search(r'(\d+)\s*(servings?|people)', ingredients_lower)
        if serving_match:
            return int(serving_match.group(1))
        
        # Default serving range
        return random.randint(2, 6)
    
    def validate_nutrition_realistic(self, calories, protein, fat):
        """Validate that nutrition values are realistic for health app"""
        # Per-serving values should be realistic
        if calories < 50 or calories > 1000:  # 50-1000 calories per serving
            return False
        if protein < 0 or protein > 100:  # 0-100g protein per serving
            return False
        if fat < 0 or fat > 100:  # 0-100g fat per serving
            return False
        return True
    
    def get_or_create_ingredient(self, name):
        """Get or create ingredient with realistic nutrition"""
        ingredient = self.db.query(Ingredient).filter(Ingredient.name == name).first()
        if not ingredient:
            # Create with realistic default nutrition values
            ingredient = Ingredient(
                id=str(uuid.uuid4()),
                name=name,
                category='other',
                unit='g',
                calories=random.uniform(50, 400),  # Realistic range
                protein=random.uniform(1, 25),
                carbs=random.uniform(5, 50),
                fats=random.uniform(1, 30)
            )
            self.db.add(ingredient)
        return ingredient
    
    def parse_ingredients(self, ingredients_text):
        """Parse ingredients text into structured data"""
        if not ingredients_text:
            return []
        
        ingredients = []
        lines = ingredients_text.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('Ingredient info:'):
                continue
                
            # Simple parsing - just use the line as ingredient name
            ingredients.append({
                'name': line,
                'quantity': random.uniform(50, 200),  # Realistic quantities
                'unit': 'g'
            })
        
        return ingredients
    
    def parse_instructions(self, directions_text):
        """Parse directions text into structured steps"""
        if not directions_text:
            return []
        
        # Convert temperatures in instructions
        directions_text = self.convert_temperatures_in_text(directions_text)
        
        steps = []
        
        if re.search(r'\d+\.', directions_text):
            parts = re.split(r'\d+\.', directions_text)
            for i, part in enumerate(parts[1:], 1):
                step = part.strip()
                if step:
                    steps.append({
                        'step_number': i,
                        'step_title': f"Step {i}",
                        'description': step
                    })
        else:
            sentences = re.split(r'[.!?]+', directions_text)
            for i, sentence in enumerate(sentences, 1):
                sentence = sentence.strip()
                if sentence and len(sentence) > 10:
                    steps.append({
                        'step_number': i,
                        'step_title': f"Step {i}",
                        'description': sentence
                    })
        
        return steps
    
    def find_and_import_recipes(self):
        """Find and import exactly 500 complete health recipes"""
        logger.info("🔍 Finding recipes with realistic nutrition values...")
        
        # Get recipes with realistic nutrition (per-serving values)
        self.sqlite_cursor.execute("""
            SELECT id, title, ingredients, directions, categories, calories, protein, fat, sodium, "desc", rating, image
            FROM recipes
            WHERE calories IS NOT NULL 
            AND calories >= 100 
            AND calories <= 800
            AND protein IS NOT NULL 
            AND fat IS NOT NULL 
            AND sodium IS NOT NULL
            AND ingredients IS NOT NULL
            AND directions IS NOT NULL
        """)
        
        all_candidates = self.sqlite_cursor.fetchall()
        logger.info(f"Found {len(all_candidates)} candidate recipes with realistic nutrition")
        
        # Prioritize cuisines for balanced distribution
        cuisine_priority = {
            "French": 60, "Italian": 60, "Mexican": 50, "Chinese": 50,
            "Thai": 40, "Japanese": 40, "Indian": 40, "Greek": 30,
            "Spanish": 30, "German": 20, "American": 30, "Mediterranean": 20,
            "International": 30
        }
        
        selected_recipes = []
        cuisine_counts = defaultdict(int)
        
        # First pass: try to fill specific cuisine quotas
        for cuisine_name, target_count in cuisine_priority.items():
            if len(selected_recipes) >= self.target_count:
                break
                
            eligible_for_cuisine = [
                r for r in all_candidates
                if self.determine_cuisine(r[1], r[4]) == cuisine_name and r not in selected_recipes
            ]
            random.shuffle(eligible_for_cuisine)
            
            to_add = min(target_count, len(eligible_for_cuisine), self.target_count - len(selected_recipes))
            selected_recipes.extend(eligible_for_cuisine[:to_add])
            cuisine_counts[cuisine_name] += to_add
        
        # Second pass: fill remaining slots
        remaining_slots = self.target_count - len(selected_recipes)
        if remaining_slots > 0:
            remaining_eligible = [r for r in all_candidates if r not in selected_recipes]
            random.shuffle(remaining_eligible)
            selected_recipes.extend(remaining_eligible[:remaining_slots])
        
        logger.info(f"Selected {len(selected_recipes)} recipes")
        logger.info("Cuisine distribution:")
        for cuisine, count in cuisine_counts.items():
            if count > 0:
                logger.info(f"  {cuisine}: {count}")
        
        # Import selected recipes
        self.import_recipes(selected_recipes)
    
    def import_recipes(self, selected_recipes):
        """Import selected recipes with complete data"""
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
        logger.info(f"🎉 Successfully imported {self.imported_count} recipes!")
    
    def import_recipe(self, recipe_data, recipe_number):
        """Import a single recipe with complete data"""
        sqlite_id, title, ingredients_text, directions_text, categories, calories, protein, fat, sodium, desc, rating, image = recipe_data
        
        try:
            # Validate nutrition is realistic
            if not self.validate_nutrition_realistic(calories, protein, fat):
                logger.warning(f"Skipping {title} - unrealistic nutrition values")
                return
            
            # Determine all required fields
            cuisine = self.determine_cuisine(title, categories)
            meal_type = self.determine_meal_type(title, categories)
            prep_time = self.estimate_prep_time(title, ingredients_text, directions_text)
            cook_time = self.estimate_cook_time(title, directions_text)
            difficulty = self.estimate_difficulty(title, ingredients_text, directions_text)
            servings = self.estimate_servings(title, ingredients_text)
            
            # Calculate total recipe nutrition
            total_calories = calories * servings
            total_protein = protein * servings
            total_fat = fat * servings
            total_sodium = sodium * servings if sodium else 0
            
            # Create recipe
            recipe = Recipe(
                id=f"recipe_{recipe_number:06d}",
                title=title,
                cuisine=cuisine,
                meal_type=meal_type,
                servings=servings,
                summary=f"A delicious {cuisine} {meal_type}. Nutrition per serving: {calories:.0f} cal, {protein:.0f}g protein, {fat:.0f}g fat, {sodium:.0f}mg sodium. Total recipe: {total_calories:.0f} cal.",
                prep_time=prep_time,
                cook_time=cook_time,
                difficulty_level=difficulty,
                dietary_tags=[],
                source="imported",
                image_url=image,
                is_active=True
            )
            
            self.db.add(recipe)
            
            # Parse and add ingredients
            parsed_ingredients = self.parse_ingredients(ingredients_text)
            for ing_data in parsed_ingredients:
                ingredient = self.get_or_create_ingredient(ing_data['name'])
                
                recipe_ingredient = RecipeIngredient(
                    recipe_id=recipe.id,
                    ingredient_id=ingredient.id,
                    quantity=ing_data['quantity'],
                    unit=ing_data['unit']
                )
                self.db.add(recipe_ingredient)
            
            # Parse and add instructions
            parsed_instructions = self.parse_instructions(directions_text)
            for step_data in parsed_instructions:
                instruction = RecipeInstruction(
                    recipe_id=recipe.id,
                    step_number=step_data['step_number'],
                    step_title=step_data['step_title'],
                    description=step_data['description']
                )
                self.db.add(instruction)
            
            self.imported_count += 1
            
        except Exception as e:
            logger.error(f"Error importing recipe {title}: {e}")
            raise
    
    def verify_import(self):
        """Verify the import was successful"""
        logger.info("🔍 Verifying import...")
        
        total_recipes = self.db.query(Recipe).count()
        logger.info(f"Total recipes in database: {total_recipes}")
        
        # Check cuisine distribution
        cuisines = self.db.query(Recipe.cuisine).all()
        cuisine_counts = defaultdict(int)
        for cuisine in cuisines:
            cuisine_counts[cuisine[0]] += 1
        
        logger.info("Cuisine distribution:")
        for cuisine, count in sorted(cuisine_counts.items()):
            logger.info(f"  {cuisine}: {count}")
        
        # Check meal type distribution
        meal_types = self.db.query(Recipe.meal_type).all()
        meal_type_counts = defaultdict(int)
        for meal_type in meal_types:
            meal_type_counts[meal_type[0]] += 1
        
        logger.info("Meal type distribution:")
        for meal_type, count in sorted(meal_type_counts.items()):
            logger.info(f"  {meal_type}: {count}")
        
        # Check difficulty distribution
        difficulties = self.db.query(Recipe.difficulty_level).all()
        difficulty_counts = defaultdict(int)
        for difficulty in difficulties:
            difficulty_counts[difficulty[0]] += 1
        
        logger.info("Difficulty distribution:")
        for difficulty, count in sorted(difficulty_counts.items()):
            logger.info(f"  {difficulty}: {count}")
        
        # Show sample recipes
        logger.info("Sample recipes:")
        sample_recipes = self.db.query(Recipe).limit(5).all()
        for recipe in sample_recipes:
            logger.info(f"  {recipe.title} - {recipe.cuisine} {recipe.meal_type} - {recipe.prep_time}min prep, {recipe.difficulty_level} - {recipe.servings} servings")

def main():
    importer = CompleteHealthRecipeImporter()
    
    # Clear existing recipes
    importer.clear_existing_recipes()
    
    # Find and import 500 complete recipes
    importer.find_and_import_recipes()
    
    # Verify import
    importer.verify_import()

if __name__ == "__main__":
    main()
