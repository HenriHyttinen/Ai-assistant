# Critical Issues Report - Meal Planning System

## Executive Summary
After thorough investigation of screenshots and codebase, multiple critical issues have been identified affecting AI recipe generation, calorie calculations, ingredient quantities, meal plan persistence, and slot filling.

---

## Issue #1: AI Recipes Not Showing (CRITICAL)

### Symptoms:
- All recipes show "RECIPE DATABASE" tag
- Only 1 AI recipe visible in entire weekly plan (expected 50/50 split = 14 AI recipes)
- AI generation is happening but flags are not persisting

### Root Causes Found:
1. **In `hybrid_meal_generator.py`**: AI meals are generated with `ai_generated: True` flag, but:
   - The flag might not be properly set in all code paths
   - Fallback meals might be overwriting AI flags

2. **In `nutrition_service.py`**: When saving meal plans:
   - Line 1024: `ai_generated` is set in `recipe_details` correctly for weekly plans
   - Line 1116: `ai_generated` is set for non-weekly plans
   - BUT: The flag might be getting lost when recipe is created in database via `_create_recipe_from_ai`
   - When AI recipe is saved to database, it loses the `ai_generated` flag in `recipe_details`

3. **Frontend Display**: Frontend checks multiple locations for AI flag:
   - `cellMeal?.ai_generated`
   - `cellMeal?.recipe?.ai_generated`
   - `cellMeal?.recipe_details?.ai_generated`
   - `cellMeal?.recipes[0]?.ai_generated`
   - But if the flag isn't in `recipe_details` in the database, it won't show

### Evidence:
- Screenshot shows all recipes with "RECIPE DATABASE" tag
- Only one recipe on Friday breakfast shows as AI

---

## Issue #2: Calorie Calculations Wrong (CRITICAL)

### Symptoms:
- Daily totals: Monday 4158 cal, Friday 3262 cal (should be ~2000 cal)
- Recipe cards showing: "Baked Apples" 1623 cal, "Toasted Hazelnut Salad" 1554 cal, "Pineapple" 713 cal
- These are TOTAL recipe calories, not per-serving

### Root Causes Found:
1. **Database Recipes**: 
   - Some recipes have `total_calories` but `per_serving_calories` might be wrong
   - When `_recipe_to_meal_format` is called, it uses `recipe.per_serving_calories`, but if that's wrong, meal gets wrong calories
   
2. **AI Recipe Nutrition Calculation**:
   - In `ai_validator.py` line 231: `nutrition['calories'] = int(total_calories)` - This is TOTAL calories, not per-serving!
   - The validator calculates TOTAL recipe nutrition from ingredients, then stores it as TOTAL, but it should store as PER-SERVING
   - When AI recipes are created, they calculate total nutrition but don't divide by servings

3. **Meal Plan Calories**:
   - In `nutrition_service.py` lines 1005, 1097: `meal.calories = nutrition_data.get("calories", 0)`
   - If `nutrition_data` contains TOTAL calories (not per-serving), meal gets wrong value
   - Daily totals sum these wrong per-meal values

4. **Frontend Calculation**:
   - Frontend tries to calculate per-serving but might be getting total values
   - The fallback logic divides by servings if > 500 cal, but if recipe already has per-serving flag, it uses that (wrong) value

### Evidence:
- Recipe "Baked Apples" shows 1623 cal - this is likely total for entire recipe (not per serving)
- Daily totals are 2x-3x the target of 2000 kcal

---

## Issue #3: Ingredient Quantity/Unit Issues (CRITICAL)

### Symptoms:
- "shallots, chopped fine (about 1/2 cup) - 480g" - WAY TOO HIGH (should be ~50-70g)
- "medium-large onion, chopped fine (about 1 1/2 cups) - 1g" - WAY TOO LOW (should be ~150-200g)
- Solid ingredients using "ml" unit: pistachios 78.86ml, raisins 44.36ml, butter 29.57ml
- Water showing 177.44ml in ingredients but 960ml/4 cups in instructions

### Root Causes Found:
1. **Unit Conversion Errors**:
   - Scripts converting cups/volume to grams incorrectly
   - "1/2 cup shallots" = 480g is WRONG (1 cup chopped shallots ≈ 100-140g, so 1/2 cup = 50-70g)
   - The conversion is treating volume (ml) as weight (g) 1:1, which is wrong for solids

2. **Ingredient Name Parsing**:
   - "medium-large onion" = 1g suggests parsing is extracting "1" from somewhere and using it as grams
   - Should extract "medium-large" and convert to ~175g

3. **Volume vs Weight**:
   - Ingredients like pistachios, raisins, butter are SOLIDS and should be in GRAMS
   - They're being stored with "ml" unit, which is wrong
   - The system is treating ml = g (1:1) which only works for water

4. **Instructions vs Ingredients Mismatch**:
   - Water in ingredients: 177.44ml
   - Water in instructions: "water (3/960ml (4.0 cup))"
   - This is a massive discrepancy (177ml vs 960ml)
   - Instructions are showing converted values that don't match ingredient list

### Evidence:
- Multiple recipes show incorrect ingredient quantities
- Units are inconsistent (ml for solids)

---

## Issue #4: Empty Meal Slots (HIGH)

### Symptoms:
- Thursday: 0 cal (all 4 slots empty)
- Saturday: 0 cal (all 4 slots empty)  
- Sunday: 0 cal (all 4 slots empty)
- Wednesday: 983 cal (2 slots empty - Dinner and Snack)
- Total: 14 out of 28 slots empty (50%!)

### Root Causes Found:
1. **Fill Logic Not Working**:
   - In `hybrid_meal_generator.py` line 441: Fill logic exists but might not be executing
   - The uniqueness check might be preventing fills
   - The 7-day uniqueness check reduced from 30 days, but might still be too restrictive for first-time users

2. **Meal Generation Failure**:
   - AI generation might be failing silently
   - Database recipe selection might not find enough recipes
   - The combination logic might not be filling all slots

3. **Weekly Plan Structure**:
   - For weekly plans, 28 meals (7 days * 4 meals) should be generated
   - The generator might not be producing all 28 meals
   - The ordering/bucketing logic might be losing meals

### Evidence:
- Screenshots show multiple empty "Add Recipe" buttons
- Daily calorie totals of 0 for Thursday, Saturday, Sunday

---

## Issue #5: Meal Plan Disappearing (HIGH)

### Symptoms:
- User navigates to different part of site, comes back, meal plan is gone
- Shows "No Meal Plan Yet" screen

### Root Causes Found:
1. **Frontend State Management**:
   - `loadMealPlan()` only loads if meal plan exists for the selected date
   - If user navigates away, React state is lost
   - No localStorage persistence of meal plan data
   - `useEffect` on line 328 might not be reloading correctly

2. **Date Matching**:
   - `loadMealPlan()` queries by `date=${selectedDate}`
   - If the meal plan was created with a different date, it won't be found
   - Weekly plans have a `start_date` that might not match the selected date

3. **Backend Query**:
   - The query might not be finding the meal plan due to date mismatch
   - Weekly plans might need special handling

### Evidence:
- User reports meal plan disappears after navigation
- "No Meal Plan Yet" screen appears after returning

---

## Issue #6: Calorie Target Mismatch

### Symptoms:
- User sets 2000 kcal daily target in preferences
- Macro targets: 100g protein, 200g carbs, 60g fats = 1740 kcal from macros
- But daily target shows 2000 kcal (260 kcal discrepancy)

### Root Causes Found:
1. **Macro Calculation**:
   - Protein: 100g * 4 = 400 kcal ✓
   - Carbs: 200g * 4 = 800 kcal ✓
   - Fats: 60g * 9 = 540 kcal ✓
   - Total = 1740 kcal
   - But daily target is 2000 kcal
   - This suggests the calorie target is set independently of macros

2. **No Validation**:
   - System allows setting calorie target that doesn't match macro totals
   - This causes confusion in meal planning

---

## Priority Fixes Required

### IMMEDIATE (Fix Now):
1. ✅ Fix AI recipe flag persistence in `recipe_details`
2. ✅ Fix calorie calculations to use per-serving (divide totals by servings)
3. ✅ Fix ingredient quantity conversions (shallots, onions, etc.)
4. ✅ Ensure all 28 meal slots are filled
5. ✅ Fix meal plan persistence/loading

### HIGH PRIORITY:
6. Fix ingredient unit standardization (ml vs g for solids)
7. Fix instruction/ingredient quantity mismatches
8. Add validation for calorie/macro consistency

### MEDIUM PRIORITY:
9. Improve error handling for AI generation failures
10. Add better logging for debugging

---

## Recommended Fixes Order

1. **AI Recipe Flagging** - Ensure `ai_generated` flag persists in `recipe_details`
2. **Calorie Calculations** - Fix AI validator to calculate per-serving nutrition
3. **Ingredient Quantities** - Fix conversion scripts and recalculation
4. **Slot Filling** - Ensure generator fills all slots with 50/50 balance
5. **Persistence** - Add localStorage or better state management

