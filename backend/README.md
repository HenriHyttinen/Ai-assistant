# Numbers Don't Lie - Backend API

FastAPI backend service for the Numbers Don't Lie wellness platform. Handles health data management, user authentication, analytics, and nutrition planning.

## What's Included

- **Secure Authentication** - JWT-based auth with OAuth2 (Google, GitHub) and 2FA support
- **Health Profile Management** - User health data and preferences
- **Activity Tracking** - Log and monitor daily activities and exercise
- **Analytics Engine** - Health metrics calculation and trend analysis
- **Goal Management** - Set, track, and manage wellness objectives
- **Data Export** - Export user data in multiple formats
- **AI Integration** - OpenAI-powered health recommendations and insights
- **Nutrition Planning** - Meal plan generation with 17 dietary preferences and 13 allergies
- **Recipe Management** - 500+ recipe database with RAG-based search and AI generation
- **Ingredient Database** - 5,388+ ingredients with comprehensive nutritional data (requires import from JSON)

## Prerequisites

- Python 3.11 or 3.12 (Python 3.14 NOT supported)
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
Create a `.env` file in the backend directory:
```
DATABASE_URL=postgresql://postgres:postgres@localhost/numbers_dont_lie
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
OPENAI_API_KEY=your-openai-api-key
```

4. Initialize the database:
```bash
python database_setup/init_db.py
```

5. Seed the database:

**Step 1: Seed Basic Recipes and Ingredients**
```bash
python scripts/comprehensive_seeder.py
```

This will seed:
- 500+ recipes
- ~155 basic ingredients

**Step 2: Import Full Ingredient Database (IMPORTANT)**

The comprehensive seeder only creates ~155 ingredients. To get the full ingredient database (5,388 ingredients), import from JSON:

```bash
python scripts/import_ingredients_from_json.py
```

This will:
- Import 5,388 ingredients from `ingredients_list.json`
- Add to existing ingredients (total: ~5,543 ingredients)

**Step 3: Generate Embeddings (REQUIRED for Recipe Search)**

Embeddings are required for recipe search and RAG functionality:

```bash
# Generate recipe embeddings (takes ~5-15 minutes)
python scripts/generate_recipe_embeddings.py

# Generate ingredient embeddings (takes ~2-5 minutes)
python scripts/generate_ingredient_embeddings.py
```

## Running the Server

To run the development server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Testing

Run the test suite:
```bash
pytest
```

Note: Current test coverage is minimal. Manual testing has been performed throughout development.

## Project Structure

```
backend/
├── alembic/              # Database migrations
├── models/              # SQLAlchemy models
├── routes/              # API endpoints
├── schemas/             # Pydantic models
├── services/            # Business logic
├── ai/                  # AI integration (OpenAI, RAG)
├── utils/               # Utility functions
├── database_setup/     # Database initialization scripts
├── scripts/             # Utility scripts (seeding, etc.)
├── docs/                # Documentation
├── alembic.ini          # Alembic configuration
├── database.py          # Database configuration
├── main.py             # FastAPI application
└── requirements.txt     # Project dependencies
```

## Dietary Preferences & Restrictions

The backend supports comprehensive dietary preferences and allergy filtering:

### Dietary Preferences (17)
- **Plant-based**: vegetarian, vegan, pescatarian
- **Health-focused**: keto, paleo, low-carb, low-fat, high-protein
- **Medical**: diabetic-friendly, heart-healthy, anti-inflammatory
- **Cultural/Religious**: mediterranean, halal, kosher, raw

### Allergies/Intolerances (13)
- **Nuts**: nuts, tree_nuts, peanuts
- **Dairy/Protein**: eggs, dairy, soy, fish, shellfish
- **Grains**: wheat, gluten
- **Other**: sesame, mustard, sulfites

Preferences are defined in `backend/constants/dietary.py` and validated in `backend/schemas/nutrition.py`.

## AI Integration

### Sequential Prompting

The system uses a 4-step sequential prompting process for meal generation:

1. **Step 1: Initial Assessment + RAG** - Analyzes meal type requirements and retrieves similar recipes
2. **Step 2: Recipe Generation** - Creates unique recipes with RAG guidance
3. **Step 3: Nutrition Validation** - Uses function calling to calculate accurate nutrition from ingredient database
4. **Step 4: Refinement** - Adjusts portions if needed to meet calorie targets

See [`docs/PROMPT_ENGINEERING.md`](docs/PROMPT_ENGINEERING.md) for detailed documentation.

### AI Model Selection

**GPT-3.5-turbo** is used for meal plan generation:
- Cost-effective ($0.0015 per 1K tokens)
- Fast response times (~2-3 seconds per meal)
- Sufficient quality for nutrition planning
- Function calling support for accurate calculations

See [`docs/MODEL_RATIONALE.md`](docs/MODEL_RATIONALE.md) for detailed rationale.

### RAG (Retrieval-Augmented Generation)

The system uses vector embeddings for similarity search:
- **Embedding Model**: `SentenceTransformer('all-MiniLM-L6-v2')` (384 dimensions)
- **Recipe Database**: 500+ recipes with vector embeddings
- **Ingredient Database**: 5,388+ ingredients with nutritional data (requires import from JSON)
- **Similarity Search**: Cosine similarity with meal type filtering

See [`docs/RAG_IMPLEMENTATION.md`](docs/RAG_IMPLEMENTATION.md) for implementation details.

### Error Handling

Comprehensive error handling with multiple fallback strategies:
- **Circuit Breaker**: Prevents cascading failures
- **Retry Logic**: Exponential backoff for transient errors
- **Fallback Strategies**: Cached responses, simplified AI, rule-based generation
- **Logging**: Comprehensive error logging with context

See [`docs/ERROR_HANDLING.md`](docs/ERROR_HANDLING.md) for detailed approach.

## Database Setup

### Quick Setup (One Command)

```bash
./setup_complete.sh
```

This script:
1. Creates all database tables
2. Seeds 500+ recipes and ~155 basic ingredients (import from JSON for full 5,388 ingredients)
3. Generates vector embeddings for RAG
4. Verifies database population

### Manual Setup

1. **Create Database**:
   ```bash
   python database_setup/init_db.py
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
- Ingredient count (≥500, target: 5,388+ with JSON import)
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
GET /nutrition/recipes/search?cuisine=Italian&meal_type=dinner&max_calories=600&min_protein=20
```

#### Generate AI Recipe
```bash
POST /nutrition/recipes/generate
{
  "query": "healthy chicken pasta recipe"
}
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

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run tests: `pytest`
4. Verify database: `python verify_database.py`
5. Update documentation if needed
6. Submit a pull request

## License

This project is licensed under the MIT License.
