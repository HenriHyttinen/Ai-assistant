# Individual Meal Generation - Implementation Summary

## Overview

The meal planning system now requires users to generate meals **one by one** for each slot in the grid. This is much lighter on the API and gives users full control.

## User Flow

### Step 1: Create Meal Plan Structure
- Click "Create Meal Plan Structure" button
- Creates empty meal plan (no meals generated)
- Grid appears with all 28 slots empty

### Step 2: Fill Slots Individually
For each empty slot, user has two options:

#### Option A: Generate AI Meal
- Click "Generate AI" button on empty slot
- Backend generates one meal using Sequential RAG (task.md compliant)
  - Step 1: Initial Assessment + RAG retrieval
  - Step 2: Recipe Generation with RAG guidance
  - Step 3: Nutrition validation via function calling
  - Step 4: Refinement if needed
- Meal appears in that slot immediately

#### Option B: Pick from Database
- Click "Pick from Database" button on empty slot
- Opens recipe selector modal
- User selects from 500+ database recipes
- Recipe added to that slot

### Step 3: Move/Reposition Meals
- Click "Move" menu on any meal
- Select target day to move meal to
- Meal is repositioned in grid

## Benefits

1. **Lighter on API**: One meal per request instead of 28 parallel requests
2. **No AI Queuing**: Meals generated on-demand as user clicks
3. **Better Results**: Sequential RAG per meal ensures quality
4. **User Control**: User chooses which slots to fill and when
5. **Prevents Duplicates**: Checks entire plan + recent meals (last 7 days)
6. **Flexible**: Mix AI-generated and database recipes

## Duplicate Prevention

When generating a meal:
- Checks existing meals in current meal plan
- Checks recent meals from last 7 days (all user's meal plans)
- Prevents duplicate recipe names
- Uses RAG to retrieve similar recipes and avoid creating duplicates

## Backend Endpoint

**POST `/meal-plans/{meal_plan_id}/generate-meal-slot`**

Request body:
```json
{
  "meal_date": "2025-10-31",
  "meal_type": "breakfast"
}
```

Response:
```json
{
  "message": "Meal generated successfully using Sequential RAG",
  "meal": {
    "id": "...",
    "meal_name": "Golden Sunrise Oatmeal",
    "meal_date": "2025-10-31",
    "meal_type": "breakfast",
    "calories": 400,
    "ai_generated": true,
    "recipe": { ... }
  }
}
```

## Frontend UI

### Empty Slot Buttons
```tsx
<VStack spacing={2}>
  <Button onClick={() => generateMealSlot(date, mealType)}>
    Generate AI
  </Button>
  <Button onClick={() => openRecipeSelector(date, mealType)}>
    Pick from Database
  </Button>
</VStack>
```

### Filled Slot Actions
- **View**: See recipe details
- **Swap**: Get alternatives for this meal type
- **Move**: Reposition meal to different day

## Removed Features

- ❌ "Generate Meal Plan" bulk generation button
- ❌ "Regenerate All Meals" button
- ❌ Bulk AI generation (28 meals at once)

## Remaining Features

- ✅ Individual meal generation per slot
- ✅ Database recipe selection per slot
- ✅ Move meals between days
- ✅ Swap meals with alternatives
- ✅ Version History
- ✅ Shopping List generation

## Testing

To test the new flow:
1. Delete existing meal plans or create a new structure
2. Click "Create Meal Plan Structure"
3. Grid appears with empty slots
4. Click "Generate AI" on any slot
5. Meal appears in that slot
6. Repeat for other slots
7. Mix with "Pick from Database" for some slots

