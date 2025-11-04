# Prompt Engineering Strategy

## Overview

The nutrition planning system uses sequential prompting with Retrieval-Augmented Generation (RAG) to generate personalized meal plans and recipes. This document outlines the prompt engineering approach, design principles, and implementation details.

## Sequential Prompting Architecture

The system implements a 4-step sequential prompting process for individual meal generation:

### Step 1: Initial Assessment
**Purpose**: Analyze meal type requirements and retrieve similar recipes to guide generation

**Implementation Location**: `backend/ai/nutrition_ai.py:_generate_single_meal_with_sequential_rag()` (Lines 1544-1592)

**Process**:
1. Analyze meal type constraints (breakfast, lunch, dinner, snack)
2. Retrieve similar recipes from database using RAG
3. Define meal type-specific allowed/forbidden items
4. Collect existing meal names from last 30 days to prevent duplicates

**RAG Integration**:
- Query: `"{meal_type} {target_cuisine} {target_calories} calories"`
- User embedding generated from dietary preferences
- Retrieves top 10 similar recipes filtered by meal_type
- Similar recipes used as negative examples (to avoid duplication)

**Meal Type Constraints**:
- **Breakfast**: Allowed - eggs, oatmeal, yogurt, smoothies, toast; Forbidden - heavy meats, curries, stews
- **Lunch**: Allowed - salads, sandwiches, soups, pasta bowls; Forbidden - heavy roasted meats, large casseroles
- **Dinner**: Allowed - roasted meats, fish, casseroles, curries; Forbidden - guacamole bowls, light salads, snacks
- **Snack**: Allowed - nuts, fruits, crackers, yogurt; Forbidden - full meals, large portions, heavy dishes

### Step 2: Recipe Generation
**Purpose**: Generate a unique recipe with RAG guidance and strict meal type enforcement

**Implementation Location**: `backend/ai/nutrition_ai.py:_generate_single_meal_with_sequential_rag()` (Lines 1594-1708)

**Key Prompt Elements**:
1. **Meal Type Enforcement**: Explicit allowed/forbidden lists with descriptions
2. **Duplicate Prevention**: Recent recipe names (last 30 days) listed to avoid
3. **Dietary Requirements**: Clear instructions about dietary preferences and allergies
   - **Critical**: If `dietary_preferences` is empty, MUST include animal proteins
   - **Critical**: DO NOT assume vegan/vegetarian unless explicitly specified
4. **Calorie Target**: Precise calorie target with portion size guidance
5. **RAG Context**: Similar recipes shown as negative examples (use as inspiration but create something different)

**Prompt Structure**:
```
Generate a single {meal_type} recipe: {target_calories} calories, {target_cuisine} cuisine.

MEAL TYPE ENFORCEMENT:
- This MUST be a proper {meal_type} food: {description}
- ALLOWED examples: {allowed_items}
- FORBIDDEN (DO NOT CREATE): {forbidden_items}

DUPLICATE PREVENTION:
- Recent recipes (last 30 days) to avoid: {existing_names}
- Do not use exact same title or similar variations

DIETARY REQUIREMENTS:
- Dietary preferences: {list}
- If empty: MUST INCLUDE ANIMAL PROTEINS (meat, fish, poultry, dairy, eggs)
- DO NOT ASSUME VEGAN/VEGETARIAN when dietary_preferences is empty
- Allergies (NEVER include): {list}

CALORIE TARGET:
- This meal must be EXACTLY {target_calories} calories (±20 cal for snacks, ±50 cal for main meals)
- Even small overages add up to exceed daily calorie limits
- Portion size guidance: {meal_type_specific_guidance}

RAG CONTEXT:
- Similar recipes to AVOID duplicating (use as inspiration but create something DIFFERENT):
  {similar_recipes_list}
```

### Step 3: Nutritional Analysis
**Purpose**: Calculate accurate nutrition from ingredients using function calling

**Implementation Location**: `backend/ai/nutrition_ai.py:_generate_single_meal_with_sequential_rag()` (Lines 1711-1765)

**Process**:
1. Extract ingredients from generated recipe
2. Call `_calculate_recipe_nutrition()` with ingredient list and database session
3. Replace AI placeholder nutrition values with calculated values
4. Use ingredient database for accurate nutrition (not estimates)

**Function Calling Integration**:
- Uses `NutritionFunctionRegistry._calculate_nutrition()` from `backend/ai/functions.py`
- Queries ingredient database using fuzzy matching
- Handles special cases (e.g., eggs as "piece", cheddar cheese matching)
- Falls back to estimates if database lookup fails

**Nutrition Calculation**:
- Per-serving nutrition calculated from ingredient quantities
- Standardized units (g for solids, ml for liquids)
- Special handling for piece-based ingredients (eggs, bananas)
- Micronutrients included when available in database

### Step 4: Refinement
**Purpose**: Adjust portions if calorie count significantly exceeds target

**Implementation Location**: `backend/ai/nutrition_ai.py:_generate_single_meal_with_sequential_rag()` (Lines 1767-1937)

**Process**:
1. Compare actual calories to target
2. Calculate scaling factor if over target
3. Scale ingredient quantities proportionally
4. Recalculate nutrition after adjustment
5. Apply stricter thresholds for snacks (20 cal) vs main meals (50 cal)

**Scaling Logic**:
- **Snacks**: Always scale to target if over (even by 1 cal)
- **Main Meals**: Scale if over by more than 50 cal
- Minimum ingredient quantities preserved for recipe integrity
- Aggressive scaling for large overages (>50% over target)

## RAG Prompt Design

### Retrieval Process
**Location**: `backend/ai/nutrition_ai.py:_retrieve_similar_recipes()` (Line 528)

**Embedding Model**: SentenceTransformer('all-MiniLM-L6-v2')
- 384-dimensional embeddings
- Fast inference, good semantic similarity

**Retrieval Strategy**:
1. Generate query embedding from meal type, cuisine, calorie target
2. Combine with user preference embedding
3. Filter by meal_type for relevance
4. Calculate cosine similarity with all recipe embeddings
5. Return top 10 most similar recipes

**Prompt Augmentation**:
Retrieved recipes included in prompt as negative examples:
```
Similar recipes to AVOID duplicating (use as inspiration but create something DIFFERENT):
1. Recipe Title: ingredient1, ingredient2, ingredient3
2. Recipe Title: ingredient1, ingredient2, ingredient3
...
```

## Meal Type Constraints

### Breakfast
- **Allowed**: Eggs, oatmeal, yogurt, smoothies, toast, pancakes, cereal, fruits, nuts, breakfast bowls
- **Forbidden**: Heavy meat dishes, large pasta portions, curries, stews, soups as main, guacamole bowls, dips
- **Calorie Target**: 25% of daily target (typically 400-600 cal)
- **Portion Guidance**: Light, energizing foods, moderate portions (100-150g protein, 50-75g carbs, 10-15ml oil)

### Lunch
- **Allowed**: Salads, sandwiches, soups, pasta, rice bowls, wraps, light protein dishes
- **Forbidden**: Heavy roasted meats, large casseroles, desserts, heavy fried foods
- **Calorie Target**: 35% of daily target (typically 600-800 cal)
- **Portion Guidance**: Balanced meals, moderate portions (150-200g protein, 75-100g carbs, 15-20ml oil)

### Dinner
- **Allowed**: Roasted meats, fish, casseroles, curries, hearty pasta dishes, stews, main courses
- **Forbidden**: Guacamole bowls, light salads, snacks, breakfast foods, simple dips, appetizers
- **Calorie Target**: 30% of daily target (typically 500-700 cal)
- **Portion Guidance**: Substantial main courses, moderate portions (150-200g protein, 75-100g carbs, 15-20ml oil)

### Snack
- **Allowed**: Nuts, fruits, crackers, yogurt, light bites, trail mix, veggie sticks, cheese, protein bars, small portions
- **Forbidden**: Full meals, large portions, heavy dishes, main courses, dinners, breakfast dishes
- **Calorie Target**: 10% of daily target (typically 100-200 cal)
- **Portion Guidance**: VERY small portions (25-40g protein max, 15-30g carbs max, 2-5ml oil max)
- **Special Handling**: Morning/afternoon/evening snacks stored as 'snack' but distinguished by slot position

## Duplicate Prevention Strategy

### 30-Day Window
- Prevents duplicate recipes across meal plans for at least a month
- Tracks meal names from last 30 days
- Passed to AI in prompt as explicit list to avoid

### Multi-Signature Detection
1. **Normalized Title Matching**: Checks if recipe title matches existing names (case-insensitive, punctuation normalized)
2. **Ingredient Signature**: Compares ingredient lists for similarity
3. **Instruction Signature**: Compares cooking instructions for similarity

### RAG Integration
- Retrieved recipes used as negative examples during generation
- Prompt explicitly instructs: "use as inspiration but create something DIFFERENT"
- Post-generation validation checks for duplicates and logs warnings

## Dietary Preference Handling

### Empty Dietary Preferences
**Critical Rule**: If `dietary_preferences` is empty, MUST include animal proteins (meat, fish, poultry, dairy, eggs)

**Prompt Instructions**:
```
- If dietary_preferences is EMPTY or NONE, the user has NO dietary restrictions.
- **DO NOT ASSUME VEGAN OR VEGETARIAN** when dietary_preferences is empty.
- **MUST INCLUDE ANIMAL PROTEINS** (meat, fish, poultry, dairy, eggs) when dietary_preferences is empty.
- Only use plant-based ingredients if dietary_preferences explicitly contains "vegan" or "vegetarian".
```

**Implementation**:
- Default recipe includes meat/fish/dairy unless dietary restrictions specified
- Dietary tags set to ["contains-meat"], ["contains-dairy"], or ["contains-eggs"] when no restrictions
- NOT ["vegetarian"] or ["vegan"] unless explicitly requested

### Allergies and Intolerances
- Explicitly listed in prompt as "NEVER include"
- Applied to both recipe generation and RAG retrieval filtering
- 13 supported allergies: nuts, tree_nuts, peanuts, eggs, dairy, soy, wheat, gluten, fish, shellfish, sesame, mustard, sulfites

## Calorie Target Enforcement

### Precision Requirements
- **Snacks**: Must be within ±20 cal of target
- **Main Meals**: Must be within ±50 cal of target
- Even small overages (e.g., +87 cal lunch, +29 cal snack) accumulate to exceed daily limits

### Portion Size Guidance
Prompts include specific portion guidance for each meal type:
- **Breakfast**: 100-150g protein, 50-75g carbs, 10-15ml oil
- **Lunch**: 150-200g protein, 75-100g carbs, 15-20ml oil
- **Dinner**: 150-200g protein, 75-100g carbs, 15-20ml oil
- **Snacks**: 25-40g protein max, 15-30g carbs max, 2-5ml oil max

### Automatic Adjustment
If generated recipe exceeds target:
1. Calculate scaling factor (target / actual)
2. Scale all ingredient quantities proportionally
3. Recalculate nutrition from adjusted ingredients
4. Verify final calories match target

## Prompt Engineering Best Practices

### 1. Explicit Instructions
- Use clear, unambiguous language
- Avoid assumptions - explicitly state requirements
- Include examples of allowed/forbidden items

### 2. Structured Format
- Use sections with clear headers
- Organize information hierarchically
- Use lists and bullet points for readability

### 3. Critical Rules Highlighted
- Use **bold** or UPPERCASE for critical instructions
- Repeat important constraints multiple times
- Provide examples of violations to avoid

### 4. Context Augmentation
- Include RAG-retrieved recipes as negative examples
- Provide recent meal history for duplicate prevention
- Include user preferences and health data

### 5. Validation in Prompts
- Specify JSON format requirements (strict)
- Include calorie precision requirements
- Define portion size constraints

## Error Handling in Prompts

### Fallback Instructions
If AI fails to follow constraints:
1. Log warning with actual vs expected values
2. Attempt automatic adjustment (Step 4: Refinement)
3. If adjustment fails, reject recipe and retry with explicit avoid list

### Retry Strategy
- Maximum 3 retry attempts
- Each retry adds previous meal name to `explicit_avoid_names`
- Prompts become more explicit with each retry

## Performance Considerations

### Prompt Size Optimization
- Limit retrieved recipes to top 5-10 for prompt size
- Limit existing meal names to 20 most recent
- Use concise recipe summaries in RAG context

### Model Selection
- Primary: GPT-3.5-turbo (cost-effective, sufficient for structured output)
- Temperature: 0.6-0.8 for variety while maintaining structure
- Fast API calls for individual meal generation

## Future Improvements

1. **Prompt Templates**: Parameterized templates for easier maintenance
2. **A/B Testing**: Compare prompt variations for quality improvements
3. **Few-Shot Learning**: Include high-quality examples in prompts
4. **Chain-of-Thought**: Add reasoning steps for complex constraints
5. **Prompt Versioning**: Track prompt versions for reproducibility

