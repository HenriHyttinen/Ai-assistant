# Numbers Don't Lie - Health & Nutrition Platform

A health and nutrition tracking platform I built that combines meal planning, recipe management, nutritional analysis, and a conversational assistant. This project brings together three main components: health analytics, nutrition tracking, and an AI assistant - all working together in one platform. Built with FastAPI backend and React frontend.

## What This Does

This platform combines three main parts:

1. **Health Analytics**: Track your health metrics, wellness score, activity levels, set goals, and see your progress over time.

2. **Nutrition System**: Plan meals, search recipes, track what you eat, and analyze your nutrition. Includes a recipe database with 500+ recipes and support for different dietary preferences.

3. **Conversational Assistant**: Ask questions about your health data, meal plans, recipes, and nutrition in natural language. It can help you understand your progress and find recipes.

Everything runs from this single project - no separate setup needed. Just follow the setup instructions below.

## Features

### Meal Planning
- Generate daily and weekly meal plans
- Support for 17 dietary preferences (vegetarian, vegan, keto, paleo, etc.)
- Handles 13 common allergies and intolerances
- Different cuisine options (Mediterranean, Asian, Indian, Mexican, etc.)
- Recipe database with 500+ recipes
- Nutritional calculations from ingredient database

### Recipe Management
- Search and filter recipes by name, ingredients, cuisine, dietary restrictions
- Filter by macronutrients (protein, carbs, fats) and calories
- Generate custom recipes based on preferences
- Ingredient substitution suggestions
- Portion size adjustments with automatic nutrition recalculation

### Nutritional Analysis
- Track calories, protein, carbs, fats, vitamins, and minerals
- Visual progress tracking with charts
- Personalized insights and recommendations
- Goal tracking with BMI and activity level integration
- Wellness score updates based on nutrition data

### Goal Management
- Set and track nutrition goals
- Achievement system for motivation
- Milestone tracking and streak counting

### Conversational Assistant
- Ask questions about your health and nutrition in plain language
- Get info about your BMI, weight, wellness score, and activity levels
- Check your meal plans for specific dates
- Analyze your nutrition and track progress
- Get recipe details with ingredients and instructions
- Generate charts and visualizations from your data
- Conversation history so it remembers context

### Additional Features
- Shopping list generation with ingredient categorization
- Meal plan versioning and restore functionality
- Integration with health dashboard
- Error handling with fallback mechanisms

## Quick Start

### Prerequisites
- **Python 3.11 or 3.12** (Python 3.14 doesn't work well - some packages won't install)
- **Node.js 16+** (for the frontend)
- **PostgreSQL** (optional - SQLite works fine for development and testing)
- **pip** and **npm** installed

**Note:** I recommend using SQLite for development - it's simpler and doesn't require setting up PostgreSQL. Just use `sqlite:///./numbers_dont_lie.db` in your `.env` file.

### Manual Setup (Required)

#### 1. Backend Setup

```bash
# Clone the repository
git clone https://gitea.kood.tech/henrijuhanihyttinen/ai-assistant
cd ai-assistant

# Go to backend folder
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (this might take a few minutes)
pip install -r requirements.txt

# Set up environment file
cp .env.example .env
# Edit .env - at minimum set DATABASE_URL (see below for SQLite setup)

# Create database tables
python database_setup/init_db.py

# Seed recipes and ingredients (optional but recommended)
python scripts/comprehensive_seeder.py

# Import full ingredient database (adds 5,388 ingredients)
python scripts/import_ingredients_from_json.py

# Generate embeddings for recipe search (takes 5-15 minutes)
python scripts/generate_recipe_embeddings.py
python scripts/generate_ingredient_embeddings.py

# Fix nutrition calculations (important!)
python scripts/recalculate_recipe_nutrition.py

# Start the backend
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

Create a `backend/.env` file. The easiest setup uses SQLite (no database server needed):

```env
# Database - SQLite is easiest for development
DATABASE_URL=sqlite:///./numbers_dont_lie.db

# JWT Authentication - just use any random string
SECRET_KEY=your-random-secret-key-here-make-it-long
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI (optional - for meal generation features)
OPENAI_API_KEY=your-openai-api-key-if-you-have-one
USE_OPENAI=true

# Supabase (optional - for authentication)
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key
```

**For SQLite (recommended for testing):** Just use `DATABASE_URL=sqlite:///./numbers_dont_lie.db` - that's it! No database server needed.

**For PostgreSQL:** Use `DATABASE_URL=postgresql://postgres:postgres@localhost/numbers_dont_lie` (make sure PostgreSQL is running).

### Database Setup - Step by Step

After running `python database_setup/init_db.py`, you need to populate the database:

**1. Seed recipes and ingredients:**
```bash
cd backend
python scripts/comprehensive_seeder.py
```
This adds 500+ recipes and about 155 basic ingredients. Takes a couple minutes.

**2. Import full ingredient database:**
```bash
python scripts/import_ingredients_from_json.py
```
This adds 5,388 more ingredients from the JSON file. Takes a minute or two.

**3. Generate embeddings (for recipe search):**
```bash
python scripts/generate_recipe_embeddings.py
python scripts/generate_ingredient_embeddings.py
```
These take 5-15 minutes total but are needed for recipe search to work properly.

**4. Fix nutrition calculations:**
```bash
python scripts/recalculate_recipe_nutrition.py
```
This calculates nutrition from ingredients. Important - without this, recipes show 0 calories.

**Quick summary:** Run all 4 steps in order. The embedding generation takes the longest but you can start the server before it finishes if you want to test other features.

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
- FastAPI for the API
- PostgreSQL or SQLite database with SQLAlchemy
- Redis caching (optional)
- Supabase for authentication
- Vector search for recipe matching
- Function calling for data access

### Project Structure
```
ai-assistant/  (or whatever you name the folder when cloning)
├── backend/
│   ├── routes/
│   │   └── assistant.py          # AI Assistant API endpoints
│   ├── services/
│   │   └── conversation_service.py  # AI Assistant conversation logic
│   ├── ai/
│   │   └── assistant_ai.py       # AI Assistant core logic
│   └── models/
│       └── conversation.py       # AI Assistant database models
├── frontend/
│   └── src/
│       ├── pages/
│       │   └── Assistant.tsx      # AI Assistant page
│       └── components/
│           └── assistant/         # AI Assistant components
└── README.md
```

**Note:** The folder name doesn't matter - you can clone it to any folder name. All code runs from `/backend` and `/frontend` relative to the project root. The database name (`numbers_dont_lie`) is just a name - it's not tied to the folder name.

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

### AI Assistant
- `POST /api/assistant/chat` - Send message to AI assistant
- `GET /api/assistant/conversations` - Get all conversations
- `GET /api/assistant/conversations/{id}/messages` - Get conversation messages
- `DELETE /api/assistant/conversations/{id}` - Delete conversation

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

## How It Works

**Meal Plan Generation:**
The system uses a multi-step process to generate meal plans:
1. Analyzes your profile and preferences
2. Designs meals based on your goals
3. Finds or creates recipes that match
4. Calculates and balances nutrition

**Recipe Search:**
- Uses vector embeddings to find similar recipes
- Searches by ingredients, cuisine, dietary restrictions
- Matches recipes based on similarity

**Nutrition Calculations:**
- Calculates macros and micros from ingredient database
- Supports ingredient substitutions
- Automatically adjusts nutrition when you change portion sizes

## Error Handling

The system handles errors gracefully:
- Falls back to cached data if something fails
- Retries failed requests automatically
- Shows user-friendly error messages
- Prevents cascading failures

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

## Extra Features

Some additional things I added:

1. Progressive meal generation - build meals one at a time
2. Meal plan versioning - save and restore previous versions
3. Live portion adjustment - see nutrition update as you change servings
4. Meal swapping - swap meals between different days
5. Micronutrient tracking - tracks 18+ vitamins and minerals
6. Duplicate prevention - avoids repeating meals too often
7. Automatic portion scaling - adjusts based on calorie goals
8. Flexible meal grid - supports 3-6 meals per day
9. Unit conversion - automatically converts to standard units
10. Database-backed nutrition - uses ingredient database for accurate calculations
11. Smart calorie distribution - spreads calories across meals optimally
12. Offline support - saves state locally
13. Advanced recipe search - filter by macros, cuisine, dietary needs
14. Ingredient substitution - suggests alternatives
15. Shopping list organization - groups ingredients by category
16. Error recovery - handles failures gracefully

## Acknowledgments

Thanks to:
- OpenAI for the API
- Supabase for authentication
- Chakra UI for the component library
- Recharts for charts
- SentenceTransformers for vector embeddings
