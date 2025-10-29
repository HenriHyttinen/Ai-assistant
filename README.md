# Numbers Don't Lie - Health & Nutrition Platform

A health and nutrition tracking platform with meal planning, recipe management, and nutritional analysis. Built with FastAPI backend and React frontend.

## Features

### Meal Planning
- Daily and weekly meal plan generation
- Support for 20+ dietary restrictions and allergies
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

## Quick Start

### Prerequisites
- Docker and Docker Compose installed
- No other dependencies required

### Setup
```bash
# Clone the repository
git clone <repository-url>
cd numbers-dont-lie

# Start the application
./start.sh
```

The application will be available at:
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### Docker Commands
```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop application
docker-compose down
```

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
- 15+ dietary preferences supported (vegetarian, vegan, keto, paleo, etc.)
- 10+ food allergies handled (nuts, dairy, gluten, etc.)
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
- Integration tests for API endpoints
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

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for GPT-4 API
- Supabase for authentication and database
- Chakra UI for component library
- Recharts for data visualization
- SentenceTransformers for vector embeddings