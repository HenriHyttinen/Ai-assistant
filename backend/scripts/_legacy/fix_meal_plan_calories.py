#!/usr/bin/env python3
"""
Quick script to fix daily calorie totals for existing meal plans.
This applies the latest fixes to meals that were generated before improvements.

Usage:
    python3 scripts/fix_meal_plan_calories.py <meal_plan_id> [target_date]
    
Examples:
    python3 scripts/fix_meal_plan_calories.py "plan-123"                    # Fix all dates
    python3 scripts/fix_meal_plan_calories.py "plan-123" "2024-11-05"      # Fix specific date
"""

import sys
import os
import requests
import json
from typing import Optional

# Add parent directory to path to import backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
# You'll need to set your auth token or use the backend directly
AUTH_TOKEN = os.getenv("AUTH_TOKEN", "")

def fix_meal_plan_calories(meal_plan_id: str, target_date: Optional[str] = None):
    """Fix daily calorie totals for a meal plan"""
    
    url = f"{BASE_URL}/api/nutrition/meal-plans/{meal_plan_id}/fix-daily-totals"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    if AUTH_TOKEN:
        headers["Authorization"] = f"Bearer {AUTH_TOKEN}"
    
    params = {}
    if target_date:
        params["target_date"] = target_date
    
    print(f"🔧 Fixing meal plan: {meal_plan_id}")
    if target_date:
        print(f"   Target date: {target_date}")
    else:
        print(f"   All dates in meal plan")
    
    try:
        response = requests.post(url, headers=headers, params=params)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"   Message: {result.get('message', 'N/A')}")
            print(f"   Fixed dates: {', '.join(result.get('fixed_dates', []))}")
            print(f"   Daily target: {result.get('daily_target', 'N/A')} cal")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Connection error: Cannot connect to {BASE_URL}")
        print(f"   Make sure the backend is running!")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def fix_via_database(meal_plan_id: str, target_date: Optional[str] = None):
    """Fix meal plan directly via database (if API is not accessible)"""
    try:
        from database import SessionLocal
        from models.nutrition import MealPlan, MealPlanMeal
        from services.integration_service import IntegrationService
        from datetime import datetime
        
        db = SessionLocal()
        
        # Get meal plan
        meal_plan = db.query(MealPlan).filter(MealPlan.id == meal_plan_id).first()
        if not meal_plan:
            print(f"❌ Meal plan {meal_plan_id} not found")
            return False
        
        # Get user preferences
        integration_service = IntegrationService()
        user_preferences = integration_service.get_integrated_nutrition_preferences(db, meal_plan.user_id)
        daily_target = user_preferences.get('daily_calorie_target', 2000)
        meals_per_day = user_preferences.get('meals_per_day', 4)
        
        print(f"🔧 Fixing meal plan: {meal_plan_id}")
        print(f"   User ID: {meal_plan.user_id}")
        print(f"   Daily target: {daily_target} cal")
        print(f"   Meals per day: {meals_per_day}")
        
        # Get dates to fix
        if target_date:
            dates_to_fix = [datetime.strptime(target_date, "%Y-%m-%d").date()]
        else:
            meals = db.query(MealPlanMeal).filter(
                MealPlanMeal.meal_plan_id == meal_plan_id,
                MealPlanMeal.meal_name.isnot(None)
            ).all()
            dates_to_fix = list(set([m.meal_date for m in meals]))
        
        fixed_dates = []
        
        for target_date_obj in dates_to_fix:
            all_meals_for_date = db.query(MealPlanMeal).filter(
                MealPlanMeal.meal_plan_id == meal_plan_id,
                MealPlanMeal.meal_date == target_date_obj,
                MealPlanMeal.meal_name.isnot(None)
            ).all()
            
            if len(all_meals_for_date) != meals_per_day:
                print(f"  ⚠️ Skipping {target_date_obj}: {len(all_meals_for_date)} meals (expected {meals_per_day})")
                continue
            
            current_total = sum(m.calories or 0 for m in all_meals_for_date)
            final_diff = daily_target - current_total
            
            print(f"  📊 {target_date_obj}: {current_total} cal (target: {daily_target}, diff: {final_diff} cal)")
            
            # Enforce minimums first
            min_cal_by_type = {
                'breakfast': 300,
                'lunch': 400,
                'dinner': 400,
                'snack': 150
            }
            
            scaled_min = False
            for meal in all_meals_for_date:
                min_required = min_cal_by_type.get(meal.meal_type, 150)
                if meal.calories and meal.calories < min_required:
                    scale_factor = min_required / max(meal.calories, 1)
                    old_cal = meal.calories
                    meal.calories = int(old_cal * scale_factor)
                    if meal.protein:
                        meal.protein = int(meal.protein * scale_factor)
                    if meal.carbs:
                        meal.carbs = int(meal.carbs * scale_factor)
                    if meal.fats:
                        meal.fats = int(meal.fats * scale_factor)
                    
                    if meal.recipe_details and isinstance(meal.recipe_details, dict):
                        if 'nutrition' not in meal.recipe_details:
                            meal.recipe_details['nutrition'] = {}
                        meal.recipe_details['nutrition']['calories'] = meal.calories
                        meal.recipe_details['nutrition']['per_serving_calories'] = meal.calories
                    
                    print(f"    ⬆️ {meal.meal_type} '{meal.meal_name}': {old_cal} → {meal.calories} cal (minimum)")
                    scaled_min = True
            
            if scaled_min:
                # Recalculate after minimum enforcement
                current_total = sum(m.calories or 0 for m in all_meals_for_date)
                final_diff = daily_target - current_total
                print(f"    📊 After minimum enforcement: {current_total} cal (diff: {final_diff} cal)")
            
            # Scale all meals proportionally to match target
            if abs(final_diff) > 5:
                scale_factor = daily_target / max(current_total, 1)
                print(f"    📊 Scaling all meals by {scale_factor:.4f}x")
                
                for meal in all_meals_for_date:
                    old_cal = meal.calories or 0
                    new_cal = round(old_cal * scale_factor)
                    meal.calories = max(1, new_cal)
                    
                    if meal.protein:
                        meal.protein = round(meal.protein * scale_factor)
                    if meal.carbs:
                        meal.carbs = round(meal.carbs * scale_factor)
                    if meal.fats:
                        meal.fats = round(meal.fats * scale_factor)
                    
                    if meal.recipe_details and isinstance(meal.recipe_details, dict):
                        if 'nutrition' not in meal.recipe_details:
                            meal.recipe_details['nutrition'] = {}
                        meal.recipe_details['nutrition']['calories'] = meal.calories
                        meal.recipe_details['nutrition']['per_serving_calories'] = meal.calories
                    
                    if old_cal != meal.calories:
                        print(f"      {meal.meal_type} '{meal.meal_name}': {old_cal} → {meal.calories} cal")
                
                # Handle rounding errors
                final_check = sum(m.calories or 0 for m in all_meals_for_date)
                final_check_diff = daily_target - final_check
                if abs(final_check_diff) > 0:
                    largest_meal = max(all_meals_for_date, key=lambda m: m.calories or 0)
                    largest_meal.calories = max(1, (largest_meal.calories or 0) + final_check_diff)
                    if largest_meal.recipe_details and isinstance(largest_meal.recipe_details, dict):
                        if 'nutrition' not in largest_meal.recipe_details:
                            largest_meal.recipe_details['nutrition'] = {}
                        largest_meal.recipe_details['nutrition']['calories'] = largest_meal.calories
                        largest_meal.recipe_details['nutrition']['per_serving_calories'] = largest_meal.calories
                    print(f"    🔧 Rounding adjustment: {final_check_diff} cal to largest meal")
                
                final_check = sum(m.calories or 0 for m in all_meals_for_date)
                accuracy_diff = abs(daily_target - final_check)
                accuracy_pct = ((daily_target - accuracy_diff) / daily_target * 100) if daily_target > 0 else 0
                
                print(f"    ✅ Fixed: {final_check} cal (target: {daily_target}, diff: {accuracy_diff} cal, {accuracy_pct:.2f}% accuracy)")
                fixed_dates.append(str(target_date_obj))
            else:
                print(f"    ✅ Already accurate: {current_total} cal (diff: {final_diff} cal)")
                fixed_dates.append(str(target_date_obj))
            
            db.commit()
        
        db.close()
        
        print(f"\n✅ Successfully fixed {len(fixed_dates)} date(s): {', '.join(fixed_dates)}")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/fix_meal_plan_calories.py <meal_plan_id> [target_date]")
        print("\nExamples:")
        print('  python3 scripts/fix_meal_plan_calories.py "plan-123"')
        print('  python3 scripts/fix_meal_plan_calories.py "plan-123" "2024-11-05"')
        sys.exit(1)
    
    meal_plan_id = sys.argv[1]
    target_date = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Try API first, fall back to direct database access
    print("Attempting to fix via API...")
    success = fix_meal_plan_calories(meal_plan_id, target_date)
    
    if not success:
        print("\nFalling back to direct database access...")
        success = fix_via_database(meal_plan_id, target_date)
    
    sys.exit(0 if success else 1)

