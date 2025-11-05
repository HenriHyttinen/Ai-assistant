# Test Suite Documentation

This directory contains the test suite for the Numbers Don't Lie backend.

## Test Structure

```
tests/
├── conftest.py              # Pytest fixtures and configuration
├── unit/                    # Unit tests
│   ├── test_rag_retrieval.py
│   └── test_function_calling.py
├── integration/             # Integration tests
│   ├── test_sequential_prompting.py
│   ├── test_meal_plan_generation.py
│   └── test_shopping_list.py
└── api/                     # API endpoint tests (to be added)
```

## Running Tests

### Prerequisites

1. Make sure you're in the `backend` directory:
   ```bash
   cd backend
   ```

2. Activate the virtual environment:
   ```bash
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate  # On Windows
   ```

3. Install test dependencies (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

### Run All Tests
```bash
# From backend directory
pytest
# or
python -m pytest
```

**Note:** If you get "collected 0 items", make sure:
- You're running from the `backend/` directory (not `backend/tests/`)
- The virtual environment is activated
- Test files are not ignored by `.gitignore` (they should be tracked by git)

### Run Specific Test Categories
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/

# API tests only
pytest tests/api/
```

### Run Specific Test File
```bash
pytest tests/integration/test_sequential_prompting.py
```

### Run Specific Test Function
```bash
pytest tests/integration/test_sequential_prompting.py::TestSequentialPrompting::test_step1_initial_assessment_and_rag
```

### Run with Coverage
```bash
pytest --cov=backend --cov-report=html
```

## Test Coverage

### Completed Tests

1. **Sequential Prompting (4 Steps)**
   - Step 1: Initial Assessment + RAG
   - Step 2: Recipe Generation
   - Step 3: Nutrition Validation (Function Calling)
   - Step 4: Refinement
   - Meal Type Constraints
   - Duplicate Prevention
   - RAG Integration

2. **RAG Retrieval**
   - Similarity Calculation (Cosine Similarity)
   - Meal Type Filtering
   - Top-K Limiting
   - Embedding Generation
   - Empty Database Handling

3. **Function Calling**
   - Nutrition Calculation (Database Lookup)
   - Piece-Based Ingredients
   - Fallback Estimation
   - Ingredient Suggestions
   - Lower-Calorie Alternatives
   - Unit Conversion

4. **Meal Plan Generation**
   - Daily Meal Plans
   - Weekly Meal Plans
   - Progressive Generation
   - Duplicate Prevention (30-day)
   - Calorie Distribution
   - Dietary Preference Filtering
   - Allergy Exclusion
   - Flexible Meal Structures

5. **Shopping List Generation**
   - List Creation
   - Ingredient Categorization
   - Quantity Aggregation
   - Quantity Adjustments
   - Ingredient Removal
   - Multiple Categories
   - Empty Meal Plan Handling

## Test Fixtures

Common fixtures are defined in `conftest.py`:

- `db_session`: In-memory SQLite database session
- `mock_user`: Mock user object
- `sample_user_preferences`: Standard user preferences
- `sample_recipe_data`: Sample recipe data
- `sample_ingredient_data`: Sample ingredient data
- `sample_recipe`: Sample recipe in database
- `sample_ingredient`: Sample ingredient in database
- `mock_openai_response`: Mock OpenAI API response
- `mock_embedding_model`: Mock SentenceTransformer model

## Notes

- Tests use in-memory SQLite database for isolation
- OpenAI API calls are mocked to avoid costs
- Embedding models are mocked for faster execution
- Tests are designed to be independent and runnable in parallel

## Future Test Additions

- API endpoint tests (FastAPI TestClient)
- End-to-end workflow tests
- Performance/load tests
- Error handling tests
- Edge case tests

