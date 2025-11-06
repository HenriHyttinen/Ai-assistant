#!/usr/bin/env python3
"""
Import ingredients from ingredients_list.json file
This will add more ingredients to the database without deleting existing ones
"""
import sys
import os
import json
import random
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import Ingredient
from sqlalchemy import text

def import_ingredients_from_json(json_file_path=None, max_ingredients=None):
    """
    Import ingredients from JSON file
    
    Args:
        json_file_path: Path to the JSON file containing ingredients (None = auto-detect)
        max_ingredients: Maximum number of ingredients to import (None = all)
    """
    # Auto-detect file location if not provided
    if json_file_path is None:
        # Try multiple possible locations
        script_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(script_dir)
        possible_paths = [
            os.path.join(backend_dir, 'ingredients_list.json'),
            os.path.join(backend_dir, 'ingredients_list_cleaned.csv'),
            os.path.join(os.path.dirname(backend_dir), 'backend', 'ingredients_list.json'),
            'ingredients_list.json',
            os.path.join('..', 'ingredients_list.json'),
        ]
        
        json_file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                json_file_path = path
                break
        
        if json_file_path is None:
            print(f"❌ ingredients_list.json file not found!")
            print(f"   Searched in:")
            for path in possible_paths:
                print(f"     - {os.path.abspath(path)}")
            print(f"\n   Please ensure the file exists in one of these locations.")
            return
    
    print(f"📥 Loading ingredients from {json_file_path}...")
    
    # Check if file exists
    if not os.path.exists(json_file_path):
        print(f"❌ File not found: {json_file_path}")
        print(f"   Looking for: {os.path.abspath(json_file_path)}")
        return
    
    # Load JSON data
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            ingredients_data = json.load(f)
        print(f"✅ Loaded {len(ingredients_data)} ingredients from JSON")
    except Exception as e:
        print(f"❌ Error loading JSON file: {e}")
        return
    
    # Limit if specified
    if max_ingredients:
        ingredients_data = ingredients_data[:max_ingredients]
        print(f"📊 Limiting to {max_ingredients} ingredients")
    
    db = SessionLocal()
    try:
        # Get existing ingredient names to avoid duplicates
        existing_ingredients = {ing.name.lower() for ing in db.query(Ingredient).all()}
        print(f"📊 Found {len(existing_ingredients)} existing ingredients in database")
        
        # Get the highest existing ingredient ID number
        max_id = 0
        result = db.execute(text("SELECT id FROM ingredients WHERE id LIKE 'ing_%' ORDER BY CAST(SUBSTR(id, 5) AS INTEGER) DESC LIMIT 1"))
        row = result.fetchone()
        if row:
            try:
                max_id = int(row[0].split('_')[1])
            except:
                pass
        
        ingredients_created = 0
        ingredients_skipped = 0
        
        for ing_data in ingredients_data:
            # Skip if ingredient already exists (case-insensitive)
            if ing_data.get('name', '').lower() in existing_ingredients:
                ingredients_skipped += 1
                continue
            
            # Create ingredient
            max_id += 1
            ingredient = Ingredient(
                id=f"ing_{max_id}",
                name=ing_data.get('name', 'Unknown'),
                category=ing_data.get('category', 'other'),
                unit=ing_data.get('unit', 'g'),
                default_quantity=float(ing_data.get('default_quantity', 100.0)),
                calories=float(ing_data.get('calories', 0)),
                protein=float(ing_data.get('protein', 0)),
                carbs=float(ing_data.get('carbs', 0)),
                fats=float(ing_data.get('fats', 0)),
                fiber=float(ing_data.get('fiber', 0)),
                sugar=float(ing_data.get('sugar', 0)),
                sodium=float(ing_data.get('sodium', 0))
            )
            
            db.add(ingredient)
            existing_ingredients.add(ing_data.get('name', '').lower())
            ingredients_created += 1
            
            # Commit in batches of 100 for performance
            if ingredients_created % 100 == 0:
                db.commit()
                print(f"   ... imported {ingredients_created} ingredients so far...")
        
        # Final commit
        db.commit()
        
        print(f"\n✅ Import completed!")
        print(f"   - Created: {ingredients_created} new ingredients")
        print(f"   - Skipped: {ingredients_skipped} duplicates")
        
        # Verify final count
        final_count = db.query(Ingredient).count()
        print(f"   - Total ingredients in database: {final_count}")
        
    except Exception as e:
        print(f"❌ Error importing ingredients: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Import ingredients from JSON or CSV file')
    parser.add_argument('--file', default=None, help='Path to JSON/CSV file (auto-detects if not provided)')
    parser.add_argument('--max', type=int, default=None, help='Maximum number of ingredients to import')
    args = parser.parse_args()
    
    # Auto-detect file location if not provided
    json_path = args.file
    if json_path and not os.path.exists(json_path):
        # Try relative to backend directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        backend_dir = os.path.dirname(script_dir)
        possible_path = os.path.join(backend_dir, json_path)
        if os.path.exists(possible_path):
            json_path = possible_path
    
    import_ingredients_from_json(json_path, args.max)

