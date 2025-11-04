# Numbers Don't Lie - Backend API

A FastAPI backend service powering the Numbers Don't Lie wellness platform. Provides RESTful APIs for health data management, user authentication, and analytics.

## Core Features

- **Secure Authentication** - JWT-based auth with OAuth2 (Google, GitHub) and 2FA support
- **Health Profile Management** - Comprehensive user health data and preferences
- **Activity Tracking** - Log and monitor daily activities and exercise routines
- **Analytics Engine** - Advanced health metrics calculation and trend analysis
- **Goal Management** - Set, track, and manage personal wellness objectives
- **Data Export** - Export user data in multiple formats for external analysis
- **AI Integration** - OpenAI-powered health recommendations and insights
- **Nutrition Planning** - Meal plan generation with 17 dietary preferences and 13 allergies/intolerances
- **Recipe Management** - 500+ recipe database with RAG-based search and AI generation

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the backend directory with the following variables:
```
DATABASE_URL=postgresql://postgres:postgres@localhost/numbers_dont_lie
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

4. Initialize the database:
```bash
python init_db.py
```

5. Run database migrations:
```bash
alembic upgrade head
```

## Running the Server

To run the development server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Swagger UI documentation: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## Testing

Run the test suite:
```bash
pytest
```

## Project Structure

```
backend/
├── alembic/              # Database migrations
├── models/              # SQLAlchemy models
├── routes/              # API endpoints
├── schemas/             # Pydantic models
├── services/            # Business logic
├── utils/               # Utility functions
├── alembic.ini          # Alembic configuration
├── database.py          # Database configuration
├── init_db.py           # Database initialization
├── main.py             # FastAPI application
└── requirements.txt     # Project dependencies
```

## Dietary Preferences & Restrictions

The backend supports comprehensive dietary preferences and allergy filtering:

### Dietary Preferences (17)
All preferences are validated and used to filter recipes and guide meal generation:
- **Plant-based**: vegetarian, vegan, pescatarian
- **Health-focused**: keto, paleo, low-carb, low-fat, high-protein
- **Medical**: diabetic-friendly, heart-healthy, anti-inflammatory
- **Cultural/Religious**: mediterranean, halal, kosher, raw

### Allergies/Intolerances (13)
All allergens are excluded from meal plans and recipe suggestions:
- **Nuts**: nuts, tree_nuts, peanuts
- **Dairy/Protein**: eggs, dairy, soy, fish, shellfish
- **Grains**: wheat, gluten
- **Other**: sesame, mustard, sulfites

Preferences are defined in `backend/constants/dietary.py` and validated in `backend/schemas/nutrition.py`.

## Advanced Features

### Prompt Engineering

The system uses **Sequential Prompting with RAG** for high-quality meal generation:

1. **Step 1: Initial Assessment + RAG** - Analyzes meal type requirements and retrieves similar recipes
2. **Step 2: Recipe Generation** - Creates unique recipes with RAG guidance and strict meal type enforcement
3. **Step 3: Nutrition Validation** - Uses function calling to calculate accurate nutrition from ingredient database
4. **Step 4: Refinement** - Adjusts portions if needed to meet calorie targets

See [`docs/PROMPT_ENGINEERING.md`](docs/PROMPT_ENGINEERING.md) for detailed documentation.

### AI Model Selection

**GPT-3.5-turbo** is used for meal plan generation, providing:
- Cost-effective operation ($0.0015 per 1K tokens)
- Fast response times (~2-3 seconds per meal)
- Sufficient quality for nutrition planning tasks
- Function calling support for accurate calculations

See [`docs/MODEL_RATIONALE.md`](docs/MODEL_RATIONALE.md) for detailed rationale.

### RAG (Retrieval-Augmented Generation)

The system uses **vector embeddings** for similarity search:
- **Embedding Model**: `SentenceTransformer('all-MiniLM-L6-v2')` (384 dimensions)
- **Recipe Database**: 500+ recipes with vector embeddings
- **Ingredient Database**: 500+ ingredients (target: 15,532+)
- **Similarity Search**: Cosine similarity with meal type filtering

See [`docs/RAG_IMPLEMENTATION.md`](docs/RAG_IMPLEMENTATION.md) for implementation details.

### Error Handling

Comprehensive error handling with multiple fallback strategies:
- **Circuit Breaker**: Prevents cascading failures
- **Retry Logic**: Exponential backoff for transient errors
- **Fallback Strategies**: Cached responses, simplified AI, rule-based generation, mock responses
- **Logging**: Comprehensive error logging with context

See [`docs/ERROR_HANDLING.md`](docs/ERROR_HANDLING.md) for detailed approach.

## Bonus Features

The system includes 16 advanced features beyond core requirements:

1. **Meal Plan Versioning** - Track and restore previous meal plan versions
2. **Micronutrient Tracking** - Comprehensive tracking of 18+ vitamins and minerals
3. **Shopping List Generation** - Automatic ingredient aggregation and categorization
4. **Meal Swapping** - Atomic swap of meals between dates
5. **Portion Adjustment** - Manual and automatic portion size adjustments
6. **Alternative Meal Suggestions** - AI-powered meal alternatives based on preferences
7. **Progressive Meal Generation** - On-demand slot-by-slot meal generation
8. **Ingredient Substitution** - AI-powered substitution suggestions for dietary restrictions
9. **Recipe Rating System** - User ratings and reviews for recipes
10. **Nutritional Analytics** - Daily/weekly/monthly summaries and trend analysis
11. **Goal Tracking** - User-defined nutrition goals with progress tracking
12. **Historical Analysis** - Date range queries and comprehensive nutritional history
13. **AI-Powered Insights** - Personalized nutritional recommendations
14. **Health Data Integration** - BMI, activity level, and fitness goals for personalized targets
15. **Standardized Units** - Automatic conversion to g (solids), ml (liquids), piece (discrete)
16. **Duplicate Prevention** - 30-day duplicate detection across all meal plans

See the [Bonus Features section in main README](../../README.md#bonus-features) for complete details.

## Database Setup

### Quick Setup (One Command)

```bash
./setup_complete.sh
```

This script:
1. Creates all database tables
2. Seeds 500+ recipes and 500+ ingredients
3. Generates vector embeddings for RAG
4. Verifies database population

See [`REVIEWER_SETUP_COMPLETE.md`](REVIEWER_SETUP_COMPLETE.md) for detailed setup instructions.

### Manual Setup

1. **Create Database**:
   ```bash
   python init_db.py
   ```

2. **Seed Recipes and Ingredients**:
   ```bash
   python scripts/comprehensive_seeder.py
   ```

3. **Generate Embeddings**:
   ```bash
   python scripts/generate_recipe_embeddings.py
   ```

4. **Verify Database**:
   ```bash
   python verify_database.py
   ```

### Database Verification

Run the verification script to ensure database meets requirements:

```bash
python verify_database.py
```

This checks:
- Recipe count (≥500)
- Ingredient count (≥500, target: 15,532+)
- Embedding coverage (100% for recipes and ingredients)
- Embedding dimensions (384 for all-MiniLM-L6-v2)

See [`docs/VERIFICATION.md`](docs/VERIFICATION.md) for detailed verification guide.

## Documentation

Comprehensive documentation is available in the `docs/` directory:

- **[DATA_MODELS.md](docs/DATA_MODELS.md)** - Complete data model documentation
- **[PROMPT_ENGINEERING.md](docs/PROMPT_ENGINEERING.md)** - Sequential prompting strategy
- **[MODEL_RATIONALE.md](docs/MODEL_RATIONALE.md)** - AI model selection rationale
- **[RAG_IMPLEMENTATION.md](docs/RAG_IMPLEMENTATION.md)** - RAG implementation details
- **[ERROR_HANDLING.md](docs/ERROR_HANDLING.md)** - Error handling approach
- **[VERIFICATION.md](docs/VERIFICATION.md)** - Database verification guide
- **[TESTING_COVERAGE.md](docs/TESTING_COVERAGE.md)** - Testing coverage and recommendations
- **[REVIEWER_SETUP_COMPLETE.md](REVIEWER_SETUP_COMPLETE.md)** - Complete setup guide for reviewers

## Usage Guide

### Meal Plan Generation

#### Progressive Generation (Recommended)

1. **Create Empty Meal Plan Structure**:
   ```bash
   POST /nutrition/meal-plans/generate
   {
     "plan_type": "weekly",
     "progressive": true
   }
   ```

2. **Generate Individual Meals**:
   ```bash
   POST /nutrition/meal-plans/{meal_plan_id}/generate-meal-slot
   {
     "meal_date": "2025-11-01",
     "meal_type": "breakfast",
     "target_calories": 500
   }
   ```

3. **Add Recipe from Database**:
   ```bash
   POST /nutrition/meal-plans/{meal_plan_id}/meals
   {
     "recipe_id": "r_123",
     "meal_date": "2025-11-01",
     "meal_type": "lunch"
   }
   ```

#### Bulk Generation

```bash
POST /nutrition/meal-plans/generate
{
  "plan_type": "daily",
  "progressive": false
}
```

### Recipe Management

#### Search Recipes
```bash
GET /nutrition/recipes/search?cuisine=Italian&meal_type=dinner&max_calories=600
```

#### Generate AI Recipe
```bash
POST /nutrition/recipes/generate
{
  "query": "healthy chicken pasta recipe"
}
```

#### Get Recipe Details
```bash
GET /nutrition/recipes/{recipe_id}
```

### Meal Management

#### Move Meal
```bash
POST /nutrition/meal-plans/{meal_plan_id}/move-meal
{
  "meal_id": 123,
  "target_date": "2025-11-02",
  "target_meal_type": "lunch"
}
```

#### Adjust Portion
```bash
POST /nutrition/meal-plans/{meal_plan_id}/adjust-portion
{
  "meal_id": 123,
  "new_servings": 2.5
}
```

#### Get Meal Alternatives
```bash
GET /nutrition/meal-plans/{meal_plan_id}/alternatives?meal_id=123&count=5
```

### Shopping List Generation

```bash
POST /nutrition/shopping-lists/generate
{
  "meal_plan_id": "mp_1_20251101_123456_7890"
}
```

## Testing

Current test coverage is minimal. Manual testing has been performed throughout development.

### Running Existing Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest backend/test_meal_planning_fix.py

# Run with coverage
pytest --cov=backend --cov-report=html
```

### Test Coverage Gaps

See [`docs/TESTING_COVERAGE.md`](docs/TESTING_COVERAGE.md) for:
- Current test coverage status
- Missing test areas
- Recommended test structure
- Testing priorities

**Note**: Tests should be added incrementally, starting with critical functionality (sequential prompting, RAG, function calling).

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run tests: `pytest`
4. Verify database: `python verify_database.py`
5. Update documentation if needed
6. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 