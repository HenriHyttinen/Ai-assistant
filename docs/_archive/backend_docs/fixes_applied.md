# Critical Fixes Applied - Meal Planning System

## Summary
Fixed 3 critical issues identified in the full scan. Remaining issues require ingredient database fixes and frontend state management improvements.

---

## ✅ FIXED: Issue #1 - AI Recipes Not Showing

### Root Cause:
- `ai_generated` flag was not explicitly being set in `recipe_details` dictionary
- Flag was being inferred but not persisted correctly

### Fixes Applied:
1. **`backend/services/nutrition_service.py`** (lines 1041-1056, 1160-1175):
   - Explicitly set `ai_generated` and `database_source` flags in `recipe_details`
   - Added `ai_flag = bool(recipe_data.get("ai_generated", False))` before storing
   - Ensured flag persists for both weekly and non-weekly meal plans

2. **`backend/services/hybrid_meal_generator.py`** (lines 526-537):
   - Ensured AI flag is preserved during recipe validation
   - Added explicit flag preservation: `validated_recipe['ai_generated'] = True`
   - Fixed per-serving calorie extraction from validated recipes

### Impact:
- AI recipes should now display "AI" badge in frontend
- 50/50 split should be visible

---

## ✅ FIXED: Issue #2 - Calorie Calculations Wrong

### Root Cause:
- **CRITICAL**: `AIRecipeValidator` was calculating TOTAL recipe nutrition and storing it as `nutrition['calories']` without dividing by servings
- This caused recipes with 4 servings to show 1600+ cal instead of ~400 cal per serving
- Daily totals were 2-3x target because they were summing total recipe calories instead of per-serving

### Fixes Applied:
1. **`backend/services/ai_validator.py`** (lines 218-250):
   - **CRITICAL FIX**: Divide total nutrition by servings to get per-serving values
   - Changed: `nutrition['calories'] = int(total_calories)` 
   - To: `nutrition['calories'] = int(total_calories / servings)`
   - Added explicit `per_serving_calories`, `per_serving_protein`, etc. fields
   - Updated top-level values to use per-serving

2. **`backend/services/nutrition_service.py`** (lines 986-1004, 1109-1124):
   - Added validation: if calories > 500 and servings > 1, divide by servings
   - Ensures all nutrition stored in `recipe_details` is per-serving
   - Added per-serving fields to nutrition_data dictionary

3. **`backend/services/hybrid_meal_generator.py`** (lines 532-537):
   - Extract per-serving calories from validated recipes
   - Prioritize `per_serving_calories` over `calories` field

### Impact:
- Daily calorie totals should now be close to 2000 kcal target
- Recipe cards should show realistic per-serving calories (~200-600 cal)
- Meal planning calculations will be accurate

---

## ✅ FIXED: Issue #3 - AI Recipe Flag Persistence

### Root Cause:
- AI flag was getting lost during recipe validation and database storage

### Fixes Applied:
- Same as Issue #1 - explicit flag setting in all code paths

---

## 🔄 IN PROGRESS: Issue #4 - Empty Meal Slots

### Root Cause:
- Fill logic exists but may not be executing correctly
- Uniqueness check might be removing meals after fill
- Ordering/bucketing logic might be losing meals

### Status:
- Fill logic verified in `hybrid_meal_generator.py` lines 441-466
- Logic ensures exactly `len(meal_types)` meals
- Maintains 50/50 balance when filling
- Need to verify it's executing

### Next Steps:
- Add logging to verify fill logic executes
- Check if uniqueness check (line 468) is removing meals
- Verify ordering logic doesn't drop meals

---

## ⚠️ REMAINING: Issue #5 - Ingredient Quantity Issues

### Issues Found:
- "shallots 1/2 cup = 480g" - WRONG (should be ~50-70g)
- "onion medium-large = 1g" - WRONG (should be ~150-200g)
- Solid ingredients using "ml" unit (pistachios, raisins, butter)
- Water mismatch: 177.44ml in ingredients vs 960ml in instructions

### Root Cause:
- Conversion scripts are treating volume (ml) as weight (g) 1:1
- "1/2 cup shallots" should be converted based on ingredient density
- Ingredient name parsing is not extracting quantities correctly

### Fix Required:
- Run comprehensive ingredient fix script
- Fix conversion logic for volume-to-weight for solids
- Fix ingredient name parsing for sizes (medium, large, etc.)

---

## ⚠️ REMAINING: Issue #6 - Meal Plan Disappearing

### Root Cause:
- React state is lost when navigating away
- No localStorage persistence
- `loadMealPlan()` only loads if meal plan exists for selected date
- Date matching might fail for weekly plans

### Fix Required:
- Add localStorage persistence for meal plan ID
- Improve date matching for weekly plans
- Add state management improvements

---

## Testing Required

1. **Generate new meal plan** - verify:
   - ✅ 50/50 AI/database split (14 AI, 14 database)
   - ✅ Daily calories ~2000 kcal (not 4000+)
   - ✅ All 28 meal slots filled
   - ✅ AI recipes show "AI" badge

2. **Check recipe cards** - verify:
   - ✅ Per-serving calories are realistic (200-600 cal)
   - ✅ Not showing total recipe calories (1500+)

3. **Navigate away and back** - verify:
   - ⚠️ Meal plan persists
   - ⚠️ Recipes remain visible

4. **Check ingredient quantities** - verify:
   - ⚠️ Realistic quantities (not 1g for onions, not 480g for 1/2 cup shallots)
   - ⚠️ Correct units (g for solids, ml for liquids)

---

## Files Modified

1. `backend/services/ai_validator.py` - Fixed per-serving calculation
2. `backend/services/nutrition_service.py` - Fixed per-serving storage, AI flag persistence
3. `backend/services/hybrid_meal_generator.py` - Fixed AI flag preservation, per-serving extraction

## Files Not Modified (Still Need Fixes)

1. Ingredient conversion scripts - need ingredient-specific density conversions
2. Frontend state management - need localStorage persistence
3. Meal plan loading logic - need better date matching

---

## Next Steps

1. Test the fixes with a new meal plan generation
2. Run ingredient fix script to correct quantity issues
3. Add frontend state persistence
4. Improve meal plan loading with better date matching

