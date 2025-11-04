# Rebuild Plan - AI Recipe Generation per task.md

## Current Issues
1. ❌ Using single fast calls instead of sequential prompting (task.md requires 3+ steps)
2. ❌ Not using RAG during meal generation (only exists for search)
3. ❌ Weak meal type enforcement (guacamole appearing as dinner)
4. ❌ No function calling for nutrition validation during generation
5. ❌ Duplicates occurring despite detection

## task.md Requirements

### Sequential Prompting (≥3 steps)
- Step 1: Initial Assessment - Analyze user profile, meal type requirements
- Step 2: Recipe Generation - Generate recipe with RAG guidance
- Step 3: Nutritional Analysis - Validate nutrition using function calling
- Step 4: Refinement - Adjust recipe if needed

### RAG (Retrieval-Augmented Generation)
- Retrieve similar recipes from 500+ database
- Use as inspiration AND to avoid duplicates
- Filter by meal_type to ensure proper examples

### Function Calling
- Calculate nutrition from ingredients
- Validate calorie counts
- Adjust if off by >100 calories

### Meal Type Enforcement
- Explicit ALLOWED/FORBIDDEN lists per meal type
- Dinner: NO guacamole bowls, dips, snacks
- Breakfast: NO heavy dinner dishes
- Clear constraints in prompts

## Implementation Plan

1. Add `_generate_single_meal_with_sequential_rag()` to `nutrition_ai.py`
   - Step 1: Initial Assessment + RAG retrieval
   - Step 2: Recipe Generation with RAG context
   - Step 3: Nutrition validation via function calling
   - Step 4: Refinement if calories off

2. Add `_generate_single_meal_fast()` as fallback (simple version)

3. Update `hybrid_meal_generator.py` to use sequential RAG method

4. Improve duplicate detection to check normalized titles across entire week

5. Fix calorie balancing to update all fields consistently

