# Testing Coverage Documentation

## Current Testing Status

The project currently has **minimal automated test coverage**. Manual testing has been performed during development, but a comprehensive automated test suite has not been implemented.

### Existing Test Files

1. **`backend/test_meal_planning_fix.py`**
   - **Type**: Manual test script
   - **Coverage**: Basic meal planning functionality
   - **Tests**: 
     - Meal plan generation
     - Recipe structure validation
     - Nutrition calculation verification
   - **Status**: Basic functionality testing

2. **`test_nutrition_api.py`** (root level)
   - **Type**: Empty placeholder
   - **Coverage**: None
   - **Status**: Not implemented

3. **Other test files** (root level):
   - `test_comprehensive_fixes.py`
   - `test_version_history.py`
   - `test_nutrition_frontend.py`
   - `test_rate_limit.py`
   - **Status**: Need to be verified

### Missing Test Coverage

The following critical areas lack automated test coverage:

#### 1. Sequential Prompting (4 Steps)
- ❌ Step 1: Initial Assessment + RAG retrieval
- ❌ Step 2: Recipe Generation with RAG guidance
- ❌ Step 3: Nutrition validation via function calling
- ❌ Step 4: Refinement and portion adjustment
- **Priority**: High (core functionality)

#### 2. RAG Retrieval
- ❌ `_retrieve_similar_recipes` function
- ❌ Embedding generation and storage
- ❌ Similarity calculations (cosine similarity)
- ❌ Meal type filtering in RAG
- ❌ Integration with recipe generation
- **Priority**: High (core functionality)

#### 3. Function Calling
- ❌ `calculate_nutrition` function
- ❌ `get_ingredient_suggestions` function
- ❌ `suggest_lower_calorie_alternatives` function
- ❌ Ingredient database lookup
- ❌ Fallback nutrition estimation
- **Priority**: High (nutrition accuracy)

#### 4. Meal Plan Generation
- ❌ Daily meal plan generation
- ❌ Weekly meal plan generation
- ❌ Progressive meal plan generation (on-demand)
- ❌ Duplicate prevention (30-day check)
- ❌ Calorie distribution across meals
- ❌ Dietary preference filtering
- ❌ Allergy exclusion
- **Priority**: High (core functionality)

#### 5. Shopping List Generation
- ❌ Shopping list creation from meal plan
- ❌ Ingredient categorization (8+ categories)
- ❌ Quantity aggregation
- ❌ Quantity adjustments
- ❌ Ingredient removal
- **Priority**: Medium

#### 6. Meal Management
- ❌ Meal swapping (atomic swap)
- ❌ Meal movement between dates
- ❌ Manual meal additions from database
- ❌ Meal regeneration
- ❌ Portion adjustment
- **Priority**: Medium

#### 7. Nutrition Calculation
- ❌ Per-serving vs. total nutrition
- ❌ Ingredient-based nutrition calculation
- ❌ Micronutrient tracking (18+ micronutrients)
- ❌ Unit standardization (g, ml, piece)
- ❌ Piece-based ingredient handling (eggs, bananas)
- **Priority**: High (nutrition accuracy)

#### 8. API Endpoints
- ❌ POST `/nutrition/meal-plans/generate` (progressive)
- ❌ POST `/nutrition/meal-plans/{id}/generate-meal-slot`
- ❌ POST `/nutrition/meal-plans/{id}/meals` (add recipe)
- ❌ POST `/nutrition/meal-plans/{id}/move-meal`
- ❌ POST `/nutrition/meal-plans/{id}/adjust-portion`
- ❌ GET `/nutrition/meal-plans/{id}`
- ❌ GET `/nutrition/meal-plans/{id}/alternatives`
- ❌ GET `/recipes/search`
- ❌ POST `/recipes/generate`
- **Priority**: High (API correctness)

#### 9. Error Handling
- ❌ HTTPException status codes
- ❌ Fallback mechanisms (circuit breaker, retry logic)
- ❌ Invalid input handling
- ❌ Database error handling
- ❌ AI service error handling
- **Priority**: Medium

#### 10. Data Validation
- ❌ Pydantic schema validation
- ❌ Dietary preference validation (17 preferences)
- ❌ Allergy validation (13 allergies)
- ❌ ISO 8601 date/time formatting
- ❌ Standardized unit validation
- **Priority**: Medium

## Recommended Test Structure

### Unit Tests
```
tests/
├── unit/
│   ├── test_rag_retrieval.py
│   ├── test_function_calling.py
│   ├── test_nutrition_calculation.py
│   ├── test_meal_plan_service.py
│   ├── test_shopping_list_service.py
│   └── test_portion_adjustment.py
```

### Integration Tests
```
tests/
├── integration/
│   ├── test_sequential_prompting.py
│   ├── test_meal_plan_generation.py
│   ├── test_meal_management.py
│   └── test_shopping_list_generation.py
```

### API Tests
```
tests/
├── api/
│   ├── test_meal_plan_endpoints.py
│   ├── test_recipe_endpoints.py
│   ├── test_nutrition_endpoints.py
│   └── test_shopping_list_endpoints.py
```

### Test Framework Recommendations

1. **pytest** for Python tests
2. **pytest-asyncio** for async endpoint tests
3. **pytest-mock** for mocking dependencies
4. **fastapi-testclient** for API endpoint testing
5. **faker** for generating test data

### Test Data Requirements

1. **Mock Database**: Use in-memory SQLite or PostgreSQL test database
2. **Mock AI Service**: Mock OpenAI API calls to avoid costs
3. **Test Recipes**: Pre-seeded test recipes (100+ recipes)
4. **Test Ingredients**: Pre-seeded test ingredients (500+ ingredients)
5. **Test Users**: Mock user accounts with various preferences

## Testing Priorities

### Phase 1: Critical Functionality (High Priority)
1. Sequential prompting (4 steps)
2. RAG retrieval and similarity search
3. Function calling (nutrition calculation)
4. Meal plan generation (daily, weekly, progressive)
5. Duplicate prevention

### Phase 2: Core Features (Medium Priority)
1. Meal management (swap, move, add, regenerate)
2. Portion adjustment
3. Shopping list generation
4. API endpoint correctness

### Phase 3: Edge Cases and Error Handling (Lower Priority)
1. Error handling and fallbacks
2. Input validation
3. Edge cases (empty preferences, extreme calorie targets)
4. Performance and load testing

## Test Coverage Goals

- **Unit Test Coverage**: ≥80% for core services
- **Integration Test Coverage**: ≥70% for critical workflows
- **API Test Coverage**: 100% of all endpoints
- **Critical Path Coverage**: 100% for sequential prompting and RAG

## Notes

- Manual testing has been performed throughout development
- The system is production-ready but lacks automated test coverage
- Tests should be added incrementally, starting with critical functionality
- Consider adding tests before major refactoring or new features

