# Numbers Don't Lie - Health & Nutrition Platform

A health and nutrition tracking platform with meal planning, recipe management, and nutritional analysis. Built with FastAPI backend and React frontend.

## Features

### Meal Planning
- Daily and weekly meal plan generation
- Support for 17 dietary preferences and 13 allergies/intolerances
- Cultural meal patterns (Mediterranean, Asian, Indian, Mexican, etc.)
- Seasonal ingredient preferences
- User behavior analysis for better recommendations
- Multi-step AI generation process
- Recipe database with 500+ entries
- Accurate nutritional calculations

### Recipe Management
- Search and filter recipes by name, ingredients, cuisine, dietary restrictions
- Generate custom recipes based on preferences
- Ingredient substitution suggestions
- Portion size adjustments with automatic nutrition recalculation
- Recipe ratings and reviews

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
- Pre-defined goal templates

### Additional Features
- Personalized recommendations based on cultural and seasonal preferences
- Shopping list generation with ingredient categorization
- Meal plan versioning and restore functionality
- Integration with health dashboard
- Error handling with fallback mechanisms

### Bonus Features

#### 1. Progressive Meal Generation
- **On-demand generation**: Generate individual meal slots one at a time instead of bulk generation
- **Reduced API load**: Lighter requests, better performance
- **Improved UX**: Users see meals appear progressively as they fill the grid
- **Flexible workflow**: Users choose which slots to fill and in what order
- **Full compliance**: Each meal still uses Sequential RAG (4 steps) as per requirements
- **Location**: `backend/routes/nutrition.py:generate_meal_slot`, `frontend/src/pages/Nutrition/MealPlanning.tsx`

#### 2. Meal Plan Versioning
- **Version history**: Track all changes to meal plans over time
- **Restore functionality**: Revert to any previous version of a meal plan
- **Version comparison**: Compare different versions side-by-side
- **Automatic versioning**: New versions created on major changes
- **Version management API**: Full CRUD operations for versions
- **Location**: `backend/services/meal_plan_versioning_service.py`, `backend/routes/meal_plan_versioning.py`

#### 3. Manual Portion Adjustment UI
- **Live preview**: See calorie and nutrition changes in real-time
- **Ingredient recalculation**: Automatically scales all ingredients proportionally
- **Database-backed nutrition**: Recalculates nutrition from ingredient database
- **User-friendly controls**: Easy-to-use slider or input for serving adjustments
- **Location**: `backend/services/portion_adjustment_service.py`, `frontend/src/pages/Nutrition/MealPlanning.tsx`

#### 4. Atomic Meal Swapping
- **Smart swapping**: Swap two meals between slots instead of blocking moves
- **No calorie restrictions**: Users can swap freely as it's their decision
- **Preserves meal data**: All meal information transferred correctly
- **Frontend/backend sync**: Immediate UI updates with proper state management
- **Location**: `backend/routes/nutrition.py:move_meal_to_date`, `frontend/src/pages/Nutrition/MealPlanning.tsx`

#### 5. Comprehensive Micronutrient Tracking
- **18+ micronutrients**: Track vitamins (A, B complex, C, D, E, K), minerals (calcium, iron, magnesium, zinc, etc.)
- **Ingredient-based calculation**: Micronutrients calculated from ingredient database
- **Enrichment service**: Automatically populate micronutrient data for recipes
- **Analysis and insights**: Micronutrient diversity scoring and recommendations
- **Location**: `backend/services/micronutrient_service.py`, `backend/services/micronutrient_enrichment_service.py`

#### 6. Enhanced Duplicate Prevention
- **30-day window**: Prevents duplicate recipes across meal plans for at least a month
- **Multi-signature detection**: Checks normalized titles, ingredient signatures, and instruction signatures
- **RAG integration**: Uses retrieved recipes as negative examples during generation
- **Post-generation validation**: Additional checks after AI generation completes
- **Location**: `backend/services/hybrid_meal_generator.py`, `backend/ai/nutrition_ai.py`

#### 7. Automatic Portion Adjustment
- **Smart scaling**: Automatically adjusts portion sizes if calories exceed targets
- **Aggressive scaling for snacks**: Snacks scale to exact targets (1g/ml minimum)
- **Contextual scaling for meals**: Different thresholds for main meals (50 cal tolerance)
- **Maintains realism**: Preserves minimum ingredient quantities for recipe integrity
- **Ingredient recalculation**: All quantities and nutrition recalculated from database
- **Location**: `backend/ai/nutrition_ai.py:_generate_single_meal_with_sequential_rag`

#### 8. Dynamic Grid Sizing
- **Flexible meal structures**: Support for 3-6 meals per day
- **Dynamic grid layout**: UI automatically adjusts based on `mealsPerDay` setting
- **Smart snack assignment**: Distinguishes morning, afternoon, and evening snacks
- **Unique React keys**: Proper key management prevents rendering issues
- **Location**: `frontend/src/pages/Nutrition/MealPlanning.tsx`

#### 9. Standardized Unit Conversion
- **Consistent units**: All ingredients stored as grams (g) for solids, milliliters (ml) for liquids
- **Automatic conversion**: Converts piece-based ingredients (eggs, bananas) to grams
- **Database integration**: Uses standardized units from ingredient database
- **Nutrition accuracy**: Consistent units ensure accurate nutrition calculations
- **Location**: `backend/ai/functions.py:_convert_to_grams`, `backend/services/measurement_standardization_service.py`

#### 10. Database-Backed Nutrition Calculation
- **Ingredient database**: Uses 15,532+ ingredient entries for accurate nutrition
- **Fuzzy matching**: Intelligent ingredient name matching (e.g., "cheddar cheese" matches "cheese")
- **Fallback handling**: Estimates for unknown ingredients when database lookup fails
- **Per-piece handling**: Special logic for ingredients stored as "piece" (e.g., eggs)
- **Micronutrient lookup**: Includes micronutrients in nutrition calculations
- **Location**: `backend/ai/functions.py:_get_nutrition_from_database`

#### 11. Nutritionist-Recommended Calorie Distribution
- **Optimal distribution**: Breakfast 25%, Lunch 35%, Dinner 30%, Snacks 10%
- **Meal-specific targets**: Each meal type gets appropriate calorie allocation
- **Flexible adjustment**: Adjusts based on number of meals per day
- **AI guidance**: Prompts AI with target calories for each meal type
- **Location**: `backend/routes/nutrition.py:generate_meal_slot`

#### 12. LocalStorage State Persistence
- **Offline support**: Meal plans persist across browser sessions
- **Race condition prevention**: Refs prevent multiple simultaneous restores
- **Smart loading**: Prioritizes API fetch but falls back to localStorage
- **User preference persistence**: Stores plan type, selected date, meals per day
- **Location**: `frontend/src/pages/Nutrition/MealPlanning.tsx`

#### 13. Enhanced Recipe Search & Filtering
- **Comprehensive filters**: Cuisine, meal type, difficulty, calories, micronutrients
- **Pagination support**: Efficient handling of large result sets
- **Dietary compliance**: Filters respect dietary preferences and allergies
- **Location**: `backend/routes/recipes.py:search_recipes`

#### 14. Ingredient Substitution Service
- **AI-powered suggestions**: Intelligent alternatives based on dietary restrictions
- **Nutritional equivalence**: Suggests substitutes with similar nutrition profiles
- **Allergy-aware**: Excludes allergenic ingredients from suggestions
- **Location**: `backend/services/ingredient_substitution_service.py`

#### 15. Shopping List Categorization
- **8 ingredient categories**: protein, dairy, vegetables, fruits, grains, nuts_seeds, oils_fats, herbs_spices
- **Automatic categorization**: Ingredients automatically sorted into categories
- **Quantity aggregation**: Combines same ingredients across multiple recipes
- **Location**: `backend/services/shopping_list_service.py:_categorize_ingredient`

#### 16. Comprehensive Error Handling
- **Try/except blocks**: All critical operations wrapped in error handling
- **Fallback mechanisms**: Multiple fallback strategies for AI failures
- **User-friendly messages**: Clear error messages for frontend display
- **Detailed logging**: Comprehensive logging for debugging and monitoring
- **Location**: Throughout codebase, especially `backend/ai/nutrition_ai.py`, `backend/services/`

## Quick Start

### Prerequisites
- Docker and Docker Compose installed (or Docker Compose v2)
- **For manual setup**: Python 3.11 or 3.12 (Python 3.14 not recommended - see troubleshooting)
- No other dependencies required

**For detailed setup instructions, see [SETUP_FOR_REVIEWERS.md](./SETUP_FOR_REVIEWERS.md)**

### Docker Setup (Recommended)
```bash
# Clone the repository
git clone <repository-url>
cd numbers-dont-lie

# Copy environment file
cp backend/.env.example backend/.env
# Edit backend/.env if needed (optional for basic setup)

# Start the application
docker compose up --build
# OR (older versions): docker-compose up --build
```

### Manual Setup
See [SETUP_FOR_REVIEWERS.md](./SETUP_FOR_REVIEWERS.md) for step-by-step instructions.

The application will be available at:
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Docker Commands
```bash
# Build and start
docker compose up --build
# OR: docker-compose up --build (older versions)

# Run in background
docker compose up -d

# View logs
docker compose logs -f

# Stop application
docker compose down

# Check service status
docker compose ps
```

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
- OpenAI GPT-4 integration with sequential prompting
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

### AI Components
- Multi-step meal plan generation
- Recipe database with 500+ entries and vector embeddings
- Nutritional calculations and analysis
- User preference learning
- Cultural meal pattern adaptation

## API Endpoints

### Core Nutrition
- `POST /nutrition/meal-plans/generate` - Generate meal plans
- `POST /nutrition/meal-plans/generate-enhanced` - Enhanced meal plans
- `GET /nutrition/preferences` - Get user preferences
- `PUT /nutrition/preferences` - Update preferences
- `GET /nutrition/comprehensive-ai-analysis` - Nutritional analysis

### Recipes
- `GET /recipes/search` - Search recipes with filters
- `GET /recipes/{id}` - Get recipe details
- `POST /recipes/generate` - Generate custom recipes
- `POST /recipes/{id}/substitute` - Ingredient substitution

### Goals & Analytics
- `GET /nutrition-goals/dashboard/summary` - Goals dashboard
- `POST /nutrition-goals` - Create nutrition goals
- `GET /nutrition-analytics/trends` - Nutritional trends
- `GET /achievements/check` - Check for new achievements

## Project Requirements

### Core Requirements
- 17 dietary preferences supported (vegetarian, vegan, keto, paleo, etc.)
- 13 food allergies/intolerances handled (nuts, dairy, gluten, etc.)
- ISO 8601 date format throughout
- Sequential prompting with 3+ steps
- Function calling for nutritional calculations
- RAG implementation with 500+ recipes
- Recipe management with search, filter, and generation
- Nutritional analysis with macro tracking and visualization
- Cross-feature integration with health dashboard

### Advanced Features
- Enhanced dietary restrictions with severity levels
- Cultural meal patterns for 5+ cuisines
- Seasonal ingredient integration
- Behavioral pattern analysis
- Achievement system for motivation
- Meal plan versioning and restore
- Comprehensive error handling

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
python scripts/seed_goals_direct.py
```

## Data Models

### Recipe Schema
```json
{
  "id": "r789",
  "title": "Mediterranean Quinoa Bowl",
  "cuisine": "Mediterranean",
  "meal": "lunch",
  "servings": 2,
  "ingredients": [
    {"id": "ing123", "name": "quinoa", "quantity": 180, "unit": "g"}
  ],
  "nutrition": {
    "calories": 425,
    "protein": 12.5,
    "carbs": 48.3,
    "fats": 22.7
  },
  "dietary_tags": ["vegetarian", "gluten-free", "high-protein"],
  "preparation": [
    {"step": "Cook quinoa", "description": "Rinse and cook quinoa", "ingredients": ["ing123"]}
  ]
}
```

### Enhanced Nutritional Data
```json
{
  "glycemic_index": 45,
  "antioxidant_profile": {
    "polyphenols": "high",
    "flavonoids": "medium"
  },
  "nutrient_density_score": 8.5,
  "satiety_index": 76
}
```

## AI Integration

### Sequential Prompting Strategy
1. Strategy Generation: Analyze user profile and define meal plan approach
2. Meal Structure: Design specific meals and timing
3. Recipe Generation: Create detailed recipes with RAG enhancement
4. Nutritional Analysis: Evaluate and adjust nutritional balance
5. Refinement: Address gaps and optimize for user preferences

### Function Calling Implementation
- Nutritional Calculations: Accurate macro/micro nutrient analysis
- Ingredient Substitution: AI-driven alternatives based on availability
- Portion Scaling: Automatic quantity and nutrition recalculation
- Dietary Compliance: Verification against user restrictions

### RAG System
- Vector Database: 500+ recipes with embeddings
- Similarity Search: Cosine similarity for recipe retrieval
- Context Augmentation: Enhanced prompts with retrieved examples
- Quality Improvement: Community-driven recipe enhancement

## Error Handling

### API Reliability
- Graceful degradation with fallback to cached data when AI fails
- Retry logic with exponential backoff for transient failures
- Circuit breaker to prevent cascade failures
- User-friendly error messages

### Recovery Mechanisms
- Redis caching for frequently accessed data
- Alternative AI models when primary fails
- Comprehensive input validation
- Detailed error tracking and monitoring

## Mobile Optimization

### Responsive Design
- Mobile-first approach optimized for mobile devices
- Touch-friendly interface with large buttons
- Optimized loading and rendering
- Offline support with cached recipes and meal plans

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
- Image optimization with compression

## Testing

### Test Coverage
- Unit tests for backend services
- Integration tests for API endpointsudo docker-compose exec app grep -A 12 "allow_origins" /app/backend/main.py 2>&1 | head -15
- Frontend component testing
- End-to-end tests for user journeys

## Documentation

### Additional Resources
- API documentation available at `/docs` endpoint
- Comprehensive inline code comments
- System design documentation
- Production deployment instructions

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request


## Acknowledgments

- OpenAI for GPT-4 API
- Supabase for authentication and database
- Chakra UI for component library
- Recharts for data visualization
- SentenceTransformers for vector embeddings