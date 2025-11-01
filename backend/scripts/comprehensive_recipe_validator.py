#!/usr/bin/env python3
"""
Comprehensive Recipe Validator

This script validates all recipes in the database and identifies issues:
1. Suspiciously low/high calorie counts
2. Missing or incorrect ingredient data
3. Recipes where calculated nutrition doesn't match stored values
4. Ingredient quantities that seem unrealistic
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import Recipe, RecipeIngredient, Ingredient
from typing import List, Dict, Any, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveRecipeValidator:
    def __init__(self):
        self.db = SessionLocal()
        self.issues = []
        self.recipes_checked = 0
        self.recipes_with_issues = 0
        
    def validate_all_recipes(self) -> Dict[str, Any]:
        """Validate all recipes and return a comprehensive report"""
        logger.info("🔍 Starting comprehensive recipe validation...")
        
        recipes = self.db.query(Recipe).all()
        logger.info(f"Found {len(recipes)} recipes to validate")
        
        for i, recipe in enumerate(recipes, 1):
            self.recipes_checked += 1
            recipe_issues = self._validate_single_recipe(recipe)
            
            if recipe_issues:
                self.recipes_with_issues += 1
                self.issues.append({
                    'recipe_id': recipe.id,
                    'title': recipe.title,
                    'issues': recipe_issues
                })
            
            if i % 50 == 0:
                logger.info(f"Progress: {i}/{len(recipes)} recipes checked...")
        
        logger.info(f"✅ Validation complete: {self.recipes_with_issues} recipes with issues out of {self.recipes_checked} total")
        
        return self._generate_report()
    
    def _validate_single_recipe(self, recipe: Recipe) -> List[str]:
        """Validate a single recipe and return list of issues"""
        issues = []
        
        # 1. Check if recipe has ingredients
        if not recipe.ingredients or len(recipe.ingredients) == 0:
            issues.append("No ingredients")
            return issues
        
        # 2. Calculate nutrition from ingredients
        calculated = self._calculate_nutrition_from_ingredients(recipe)
        
        if not calculated or calculated['ingredient_count'] == 0:
            issues.append("No ingredients with nutrition data")
            return issues
        
        # 3. Check calorie count (suspiciously low)
        per_serving_cal = recipe.per_serving_calories or 0
        calculated_per_serving = calculated['total_calories'] / (recipe.servings or 1)
        
        # Check if calories seem too low based on recipe type
        if per_serving_cal > 0:
            if per_serving_cal < 50:
                issues.append(f"Very low calories: {per_serving_cal:.0f} cal/serving")
            
            # Check if calculated vs stored differ significantly
            if calculated_per_serving > 0:
                diff_percent = abs(per_serving_cal - calculated_per_serving) / calculated_per_serving * 100
                if diff_percent > 30:
                    issues.append(f"Large mismatch: stored {per_serving_cal:.0f} vs calculated {calculated_per_serving:.0f} cal ({diff_percent:.0f}% diff)")
        
        # 4. Check protein levels (suspiciously low for protein-containing recipes)
        per_serving_protein = recipe.per_serving_protein or 0
        calculated_protein = calculated['total_protein'] / (recipe.servings or 1)
        
        # Check if recipe title suggests protein but protein is low
        title_lower = recipe.title.lower()
        has_protein_keywords = any(kw in title_lower for kw in ['chicken', 'beef', 'pork', 'fish', 'ham', 'turkey', 'meat', 'salami'])
        
        if has_protein_keywords and per_serving_protein < 10:
            issues.append(f"Low protein for protein dish: {per_serving_protein:.1f}g/serving")
        
        # 5. Check ingredient quantities
        suspicious_quantities = []
        for ri in recipe.ingredients:
            ing = ri.ingredient
            if not ing:
                continue
            
            qty = ri.quantity or 0
            ing_name = ing.name.lower()
            
            # Check for very small quantities that might be errors
            if qty > 0 and qty < 1:
                # Allow for small spices/condiments
                if not any(spice in ing_name for spice in ['salt', 'pepper', 'spice', 'herb', 'garlic', 'oil']):
                    suspicious_quantities.append(f"{ing.name}: {qty:.2f}g")
            
            # Check for ingredients with no nutrition data
            if not ing.calories or ing.calories == 0:
                # Important ingredients should have data
                if any(kw in ing_name for kw in ['chicken', 'beef', 'fish', 'cheese', 'bread', 'rice', 'pasta']):
                    suspicious_quantities.append(f"{ing.name}: no nutrition data")
        
        if suspicious_quantities:
            issues.append(f"Suspicious quantities/data: {', '.join(suspicious_quantities[:3])}")
        
        # 6. Check servings match recipe size
        if recipe.servings and recipe.servings > 10:
            issues.append(f"High serving count: {recipe.servings} servings")
        
        if recipe.servings and recipe.servings < 1:
            issues.append(f"Invalid serving count: {recipe.servings}")
        
        return issues
    
    def _calculate_nutrition_from_ingredients(self, recipe: Recipe) -> Dict[str, Any]:
        """Calculate nutrition from recipe ingredients"""
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fats = 0
        ingredient_count = 0
        
        for ri in recipe.ingredients:
            ing = ri.ingredient
            if not ing:
                continue
            
            qty = ri.quantity or 0
            if qty <= 0:
                continue
            
            multiplier = qty / 100.0
            
            calories = (ing.calories or 0) * multiplier
            protein = (ing.protein or 0) * multiplier
            carbs = (ing.carbs or 0) * multiplier
            fats = (ing.fats or 0) * multiplier
            
            if calories > 0 or protein > 0 or carbs > 0 or fats > 0:
                total_calories += calories
                total_protein += protein
                total_carbs += carbs
                total_fats += fats
                ingredient_count += 1
        
        return {
            'total_calories': round(total_calories, 1),
            'total_protein': round(total_protein, 1),
            'total_carbs': round(total_carbs, 1),
            'total_fats': round(total_fats, 1),
            'ingredient_count': ingredient_count
        }
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report of issues"""
        # Categorize issues
        critical_issues = []
        warning_issues = []
        
        for issue_data in self.issues:
            recipe_issues = issue_data['issues']
            has_critical = any('No ingredients' in i or 'no nutrition data' in i for i in recipe_issues)
            has_low_cal = any('Very low calories' in i or 'Low protein' in i for i in recipe_issues)
            
            if has_critical:
                critical_issues.append(issue_data)
            elif has_low_cal:
                warning_issues.append(issue_data)
        
        # Statistics
        very_low_cal = len([i for i in self.issues if any('Very low calories' in j for j in i['issues'])])
        low_protein = len([i for i in self.issues if any('Low protein' in j for j in i['issues'])])
        large_mismatch = len([i for i in self.issues if any('Large mismatch' in j for j in i['issues'])])
        no_data = len([i for i in self.issues if any('No ingredients' in j or 'no nutrition data' in j for j in i['issues'])])
        
        report = {
            'total_recipes': self.recipes_checked,
            'recipes_with_issues': self.recipes_with_issues,
            'critical_issues': len(critical_issues),
            'warning_issues': len(warning_issues),
            'statistics': {
                'very_low_calories': very_low_cal,
                'low_protein_for_protein_dishes': low_protein,
                'large_mismatch_calculated_vs_stored': large_mismatch,
                'missing_ingredient_data': no_data
            },
            'critical_recipes': critical_issues[:50],  # Top 50
            'warning_recipes': warning_issues[:50],  # Top 50
            'all_issues': self.issues
        }
        
        return report
    
    def print_report(self, report: Dict[str, Any]):
        """Print a formatted report"""
        print("\n" + "="*80)
        print("📊 COMPREHENSIVE RECIPE VALIDATION REPORT")
        print("="*80)
        
        print(f"\n✅ Total Recipes Checked: {report['total_recipes']}")
        print(f"⚠️  Recipes with Issues: {report['recipes_with_issues']} ({report['recipes_with_issues']/report['total_recipes']*100:.1f}%)")
        print(f"🔴 Critical Issues: {report['critical_issues']}")
        print(f"🟡 Warning Issues: {report['warning_issues']}")
        
        print("\n📈 Issue Statistics:")
        stats = report['statistics']
        print(f"   • Very Low Calories (<50 cal/serving): {stats['very_low_calories']}")
        print(f"   • Low Protein for Protein Dishes: {stats['low_protein_for_protein_dishes']}")
        print(f"   • Large Mismatch (calculated vs stored >30%): {stats['large_mismatch_calculated_vs_stored']}")
        print(f"   • Missing Ingredient Data: {stats['missing_ingredient_data']}")
        
        if report['critical_recipes']:
            print(f"\n🔴 Top Critical Issues (showing first 20):")
            for issue in report['critical_recipes'][:20]:
                print(f"\n   Recipe: {issue['title'][:60]}")
                for issue_desc in issue['issues']:
                    print(f"      - {issue_desc}")
        
        if report['warning_recipes']:
            print(f"\n🟡 Top Warnings (showing first 20):")
            for issue in report['warning_recipes'][:20]:
                print(f"\n   Recipe: {issue['title'][:60]}")
                for issue_desc in issue['issues']:
                    print(f"      - {issue_desc}")
    
    def close(self):
        """Close database connection"""
        self.db.close()

def main():
    """Main function"""
    validator = ComprehensiveRecipeValidator()
    
    try:
        report = validator.validate_all_recipes()
        validator.print_report(report)
        
        # Save report to file
        import json
        with open('recipe_validation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"\n📄 Full report saved to recipe_validation_report.json")
        logger.info(f"\n🎉 Validation complete!")
        
    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        validator.close()

if __name__ == "__main__":
    main()

