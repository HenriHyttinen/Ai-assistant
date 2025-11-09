# Numbers Don't Lie - Health & Nutrition Platform

A comprehensive health and nutrition tracking platform I built for meal planning, recipe management, and nutritional analysis. Built with FastAPI backend and React frontend.

## What This Does

This platform helps users track their health metrics, plan meals, and manage their nutrition goals. It's got meal planning with AI-generated recipes, a recipe database with search and filtering, nutritional tracking, and integration with health analytics.

## Features

### Meal Planning
- Daily and weekly meal plan generation using AI
- Support for 17 dietary preferences (vegetarian, vegan, keto, paleo, etc.)
- Handles 13 common allergies and intolerances
- Cultural meal patterns (Mediterranean, Asian, Indian, Mexican, etc.)
- Recipe database with 500+ entries (requires embedding generation for search)
- Accurate nutritional calculations from ingredient database

### Recipe Management
- Search and filter recipes by name, ingredients, cuisine, dietary restrictions
- Filter by macronutrients (protein, carbs, fats) and calories
- Generate custom recipes based on preferences
- Ingredient substitution suggestions
- Portion size adjustments with automatic nutrition recalculation

### Nutritional Analysis
- Track calories, protein, carbs, fats, vitamins, and minerals
- Visual progress tracking with charts
- AI-powered insights and recommendations
- Goal tracking with BMI and activity level integration
- Wellness score updates based on nutrition data

### Goal Management
- Set and track nutrition goals
- Achievement system for motivation
- Milestone tracking and streak counting

### Additional Features
- Shopping list generation with ingredient categorization
- Meal plan versioning and restore functionality
- Integration with health dashboard
- Error handling with fallback mechanisms

## Quick Start

### Prerequisites
- **Python 3.11 or 3.12** (Python 3.14 NOT supported - many packages lack pre-built wheels)
- **Node.js 16+** (for frontend)
- **PostgreSQL 12+** (optional, SQLite works for development)
- **pip** (Python package manager)
- **npm** (Node package manager)

**For detailed setup instructions, see [SETUP_FOR_REVIEWERS.md](./SETUP_FOR_REVIEWERS.md)**

### Manual Setup (Required)

#### 1. Backend Setup

```bash
# Clone the repository
git clone <repository-url>
cd numbers-dont-lie

# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your settings (see Environment Variables below)

# Initialize database
python database_setup/init_db.py

# Seed basic recipes and ingredients
python scripts/comprehensive_seeder.py

# Import full ingredient database (IMPORTANT - adds 5,388 ingredients)
python scripts/import_ingredients_from_json.py

# Generate embeddings (REQUIRED for recipe search and RAG)
python scripts/generate_recipe_embeddings.py
python scripts/generate_ingredient_embeddings.py

# Recalculate recipe nutrition from ingredients (IMPORTANT - fixes 0 calorie issue)
python scripts/recalculate_recipe_nutrition.py

# Start the backend server
uvicorn main:app --reload
```

The backend API will be available at:
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

#### 2. Frontend Setup (in a new terminal)

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the frontend development server
npm run dev
```

The frontend will be available at `http://localhost:5173` (or the port Vite assigns)

### Environment Variables

Create a `backend/.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql://postgres:postgres@localhost/numbers_dont_lie
# OR for SQLite (development):
# DATABASE_URL=sqlite:///./numbers_dont_lie.db

# JWT Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI (optional - for AI meal generation)
OPENAI_API_KEY=your-openai-api-key
USE_OPENAI=true

# Supabase (optional - for authentication)
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key
```

### Database Setup

After initializing the database, seed it with recipes and ingredients:

**Step 1: Seed Basic Recipes and Ingredients**

```bash
cd backend
python scripts/comprehensive_seeder.py
```

This will seed:
- 500+ recipes
- ~155 basic ingredients

**Step 2: Import Full Ingredient Database (IMPORTANT)**

The comprehensive seeder only creates ~155 ingredients. To get the full ingredient database (5,388 ingredients), import from JSON:

```bash
cd backend
python scripts/import_ingredients_from_json.py
```

This will:
- Import 5,388 ingredients from `ingredients_list.json`
- Add to existing ingredients (total: ~5,543 ingredients)

**Step 3: Generate Embeddings (REQUIRED for Recipe Search)**

Embeddings are required for recipe search and RAG functionality. Generate them after seeding:

```bash
cd backend

# Generate recipe embeddings (takes ~5-15 minutes)
python scripts/generate_recipe_embeddings.py

# Generate ingredient embeddings (takes ~2-5 minutes)
python scripts/generate_ingredient_embeddings.py
```

**Step 4: Recalculate Recipe Nutrition (IMPORTANT - Fixes 0 Calorie Issue)**

The seeder creates recipes with ingredients but doesn't calculate nutrition. Recalculate nutrition from ingredients:

```bash
cd backend
python scripts/recalculate_recipe_nutrition.py
```

This will:
- Calculate calories, protein, carbs, fats from recipe ingredients
- Update per-serving and total nutrition values
- Fix recipes showing 0 calories/nutrition

**Summary:**
1. ✅ Seed basic data: `python scripts/comprehensive_seeder.py` (500 recipes, 155 ingredients)
2. ✅ Import full ingredients: `python scripts/import_ingredients_from_json.py` (adds 5,388 ingredients)
3. ✅ Generate embeddings: Run both embedding scripts (required for search/RAG)
4. ✅ Recalculate nutrition: `python scripts/recalculate_recipe_nutrition.py` (fixes 0 calorie issue)

## Dietary Preferences & Restrictions

### Supported Dietary Preferences (17)
1. vegetarian
2. vegan
3. gluten-free
4. dairy-free
5. keto
6. paleo
7. mediterranean
8. pescatarian
9. low-carb
10. low-fat
11. high-protein
12. diabetic-friendly
13. heart-healthy
14. anti-inflammatory
15. raw
16. halal
17. kosher

### Supported Allergies/Intolerances (13)
1. nuts
2. tree_nuts
3. peanuts
4. eggs
5. dairy
6. soy
7. wheat
8. gluten
9. fish
10. shellfish
11. sesame
12. mustard
13. sulfites

All dietary preferences and allergies are validated through Pydantic schemas and properly filtered in meal generation and recipe search.

## Architecture

### Backend (FastAPI)
- OpenAI GPT-3.5-turbo integration with sequential prompting
- PostgreSQL database with SQLAlchemy ORM
- Redis caching for performance
- Supabase JWT authentication
- SentenceTransformers for vector search
- Function calling for nutritional calculations

### Frontend (React + Chakra UI)
- Chakra UI for responsive design
- React Context for state management
- Recharts for data visualization
- Supabase client for authentication
- Mobile-first responsive design

### Database
- **Recipes**: 500+ recipes with vector embeddings for RAG
- **Ingredients**: 5,388+ ingredients with comprehensive nutritional data (requires import from JSON)
- All recipes and ingredients have vector embeddings for similarity search

## API Endpoints

### Core Nutrition
- `POST /nutrition/meal-plans/generate` - Generate meal plans
- `POST /nutrition/meal-plans/generate-enhanced` - Enhanced meal plans
- `GET /nutrition/preferences` - Get user preferences
- `PUT /nutrition/preferences` - Update preferences
- `GET /nutrition/comprehensive-ai-analysis` - Nutritional analysis

### Recipes
- `GET /nutrition/recipes/search` - Search recipes with filters
- `GET /nutrition/recipes/{id}` - Get recipe details
- `POST /nutrition/recipes/generate` - Generate custom recipes
- `POST /nutrition/recipes/{id}/substitute` - Ingredient substitution

### Goals & Analytics
- `GET /nutrition-goals/dashboard/summary` - Goals dashboard
- `POST /nutrition-goals` - Create nutrition goals
- `GET /nutrition-analytics/trends` - Nutritional trends
- `GET /achievements/check` - Check for new achievements

## Project Requirements

### Core Requirements
- 17 dietary preferences supported
- 13 food allergies/intolerances handled
- ISO 8601 date format throughout
- Sequential prompting with 4 steps
- Function calling for nutritional calculations
- RAG implementation with 500+ recipes
- Recipe management with search, filter, and generation
- Nutritional analysis with macro tracking and visualization
- Cross-feature integration with health dashboard

## Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Database Setup
```bash
# Run migrations
cd backend
python -c "from database import engine; from models import Base; Base.metadata.create_all(bind=engine)"

# Seed initial data
python scripts/comprehensive_seeder.py
```

## AI Integration

### Sequential Prompting Strategy
The system uses a 4-step sequential prompting process:
1. **Strategy Generation**: Analyze user profile and define meal plan approach
2. **Meal Structure**: Design specific meals and timing
3. **Recipe Generation**: Create detailed recipes with RAG enhancement
4. **Nutritional Analysis**: Evaluate and adjust nutritional balance

### Function Calling Implementation
- Nutritional Calculations: Accurate macro/micro nutrient analysis from ingredient database
- Ingredient Substitution: AI-driven alternatives based on availability
- Portion Scaling: Automatic quantity and nutrition recalculation
- Dietary Compliance: Verification against user restrictions

### RAG System
- Vector Database: 500+ recipes with embeddings
- Similarity Search: Cosine similarity for recipe retrieval
- Context Augmentation: Enhanced prompts with retrieved examples
- Ingredient Database: 5,388+ ingredients with nutritional data (requires import from JSON)

## Error Handling

The system includes comprehensive error handling:
- Graceful degradation with fallback to cached data when AI fails
- Retry logic with exponential backoff for transient failures
- Circuit breaker to prevent cascade failures
- User-friendly error messages

## Security

### Authentication & Authorization
- Supabase integration with secure JWT token handling
- Role-based access control
- Secure handling of health data
- Proper CORS configuration

## Performance

### Optimization Strategies
- Database indexing for optimized queries
- Redis caching layer for frequently accessed data
- Lazy loading for on-demand components
- Vector embeddings for fast similarity search

## Testing

Current test coverage is minimal. Manual testing has been performed throughout development. See `backend/docs/TESTING_COVERAGE.md` for details.

## Documentation

Additional documentation is available:
- API documentation at `/docs` endpoint
- Comprehensive inline code comments
- System design documentation in `backend/docs/`
- Production deployment instructions

## Bonus Features

I've implemented several bonus features beyond the core requirements:

1. **Progressive Meal Generation** - Generate meals one slot at a time
2. **Meal Plan Versioning** - Track and restore previous versions
3. **Manual Portion Adjustment UI** - Live preview with automatic recalculation
4. **Atomic Meal Swapping** - Swap meals between slots
5. **Comprehensive Micronutrient Tracking** - 18+ vitamins and minerals
6. **Enhanced Duplicate Prevention** - 30-day window with multi-signature detection
7. **Automatic Portion Adjustment** - Smart scaling based on calorie targets
8. **Dynamic Grid Sizing** - Support for 3-6 meals per day
9. **Standardized Unit Conversion** - Automatic conversion to g/ml/piece
10. **Database-Backed Nutrition Calculation** - Uses 5,388+ ingredient database (requires import from JSON)
11. **Nutritionist-Recommended Calorie Distribution** - Optimal meal distribution
12. **LocalStorage State Persistence** - Offline support
13. **Enhanced Recipe Search & Filtering** - Comprehensive filters including macronutrients
14. **Ingredient Substitution Service** - AI-powered suggestions
15. **Shopping List Categorization** - Automatic ingredient grouping
16. **Comprehensive Error Handling** - Multiple fallback strategies

## Acknowledgments

- OpenAI for GPT-3.5-turbo API
- Supabase for authentication and database
- Chakra UI for component library
- Recharts for data visualization
- SentenceTransformers for vector embeddings
