#!/usr/bin/env python3
"""
Export Full Ingredient List

Exports all ingredients with their current nutrition data.
Focuses on ingredients used in recipes and highlights missing data.
"""

import sys
import os
import csv
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import Recipe, RecipeIngredient, Ingredient
from sqlalchemy import func
from collections import Counter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def export_ingredients():
    """Export all ingredients to CSV and JSON"""
    db = SessionLocal()
    
    try:
        # Get all ingredients that are actually used in recipes
        used_ingredient_ids = db.query(RecipeIngredient.ingredient_id).distinct().all()
        used_ingredient_ids = [x[0] for x in used_ingredient_ids if x[0]]
        
        # Get all ingredients used in recipes
        used_ingredients = db.query(Ingredient).filter(
            Ingredient.id.in_(used_ingredient_ids)
        ).all()
        
        logger.info(f"Found {len(used_ingredients)} ingredients used in recipes")
        
        # Count usage frequency
        usage_counts = db.query(
            RecipeIngredient.ingredient_id,
            func.count(RecipeIngredient.id).label('usage_count')
        ).group_by(RecipeIngredient.ingredient_id).all()
        
        usage_map = {ing_id: count for ing_id, count in usage_counts}
        
        # Categorize ingredients
        ingredients_data = []
        missing_data = []
        partial_data = []
        complete_data = []
        
        for ingredient in used_ingredients:
            usage = usage_map.get(ingredient.id, 0)
            
            # Check if has complete nutrition data
            has_calories = ingredient.calories and ingredient.calories > 0
            has_protein = ingredient.protein is not None
            has_carbs = ingredient.carbs is not None
            has_fats = ingredient.fats is not None
            has_complete = has_calories and has_protein and has_carbs and has_fats
            
            ingredient_info = {
                'id': ingredient.id,
                'name': ingredient.name,
                'category': ingredient.category,
                'unit': ingredient.unit,
                'default_quantity': ingredient.default_quantity,
                'calories': ingredient.calories or 0,
                'protein': ingredient.protein or 0,
                'carbs': ingredient.carbs or 0,
                'fats': ingredient.fats or 0,
                'fiber': ingredient.fiber or 0,
                'sugar': ingredient.sugar or 0,
                'sodium': ingredient.sodium or 0,
                'usage_count': usage,
                'has_complete_data': has_complete,
                'missing_data': []
            }
            
            # Track what's missing
            if not has_calories:
                ingredient_info['missing_data'].append('calories')
            if not has_protein:
                ingredient_info['missing_data'].append('protein')
            if not has_carbs:
                ingredient_info['missing_data'].append('carbs')
            if not has_fats:
                ingredient_info['missing_data'].append('fats')
            
            ingredients_data.append(ingredient_info)
            
            if not has_complete:
                if not has_calories:
                    missing_data.append(ingredient_info)
                else:
                    partial_data.append(ingredient_info)
            else:
                complete_data.append(ingredient_info)
        
        # Sort by usage count (most used first)
        ingredients_data.sort(key=lambda x: x['usage_count'], reverse=True)
        missing_data.sort(key=lambda x: x['usage_count'], reverse=True)
        
        # Export to CSV
        csv_filename = 'ingredients_list.csv'
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'name', 'category', 'unit', 'default_quantity',
                'calories', 'protein', 'carbs', 'fats', 'fiber', 'sugar', 'sodium',
                'usage_count', 'has_complete_data', 'missing_data'
            ])
            writer.writeheader()
            for ing in ingredients_data:
                row = ing.copy()
                row['missing_data'] = ', '.join(row['missing_data']) if row['missing_data'] else 'none'
                writer.writerow(row)
        
        logger.info(f"✅ Exported to {csv_filename}")
        
        # Export missing data to separate CSV
        missing_csv_filename = 'ingredients_missing_data.csv'
        with open(missing_csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'name', 'category', 'usage_count', 'missing_data',
                'calories', 'protein', 'carbs', 'fats'
            ])
            writer.writeheader()
            for ing in missing_data:
                row = {
                    'name': ing['name'],
                    'category': ing['category'],
                    'usage_count': ing['usage_count'],
                    'missing_data': ', '.join(ing['missing_data']),
                    'calories': ing['calories'],
                    'protein': ing['protein'],
                    'carbs': ing['carbs'],
                    'fats': ing['fats']
                }
                writer.writerow(row)
        
        logger.info(f"✅ Exported missing data to {missing_csv_filename}")
        
        # Export to JSON (for programmatic use)
        json_filename = 'ingredients_list.json'
        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(ingredients_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"✅ Exported to {json_filename}")
        
        # Print summary
        print("\n" + "="*80)
        print("📊 INGREDIENT EXPORT SUMMARY")
        print("="*80)
        print(f"\n✅ Total ingredients used in recipes: {len(used_ingredients)}")
        print(f"   • Complete data: {len(complete_data)} ({len(complete_data)/len(used_ingredients)*100:.1f}%)")
        print(f"   • Partial data: {len(partial_data)} ({len(partial_data)/len(used_ingredients)*100:.1f}%)")
        print(f"   • Missing data: {len(missing_data)} ({len(missing_data)/len(used_ingredients)*100:.1f}%)")
        
        print(f"\n📋 Top 20 Most Used Ingredients Missing Data:")
        for i, ing in enumerate(missing_data[:20], 1):
            print(f"   {i:2d}. {ing['name'][:50]:50} (used {ing['usage_count']:3d}x) - Missing: {', '.join(ing['missing_data'])}")
        
        print(f"\n📄 Files created:")
        print(f"   • {csv_filename} - Full ingredient list")
        print(f"   • {missing_csv_filename} - Ingredients missing data only")
        print(f"   • {json_filename} - Full data in JSON format")
        print("\n" + "="*80)
        
        return ingredients_data
        
    finally:
        db.close()

if __name__ == "__main__":
    export_ingredients()

