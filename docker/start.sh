#!/bin/bash

# Startup script for Numbers Don't Lie Health App
set -e

echo "Starting Numbers Don't Lie Health App..."

# Function to wait for database
wait_for_db() {
    echo "Waiting for database to be ready..."
    while ! nc -z $DB_HOST $DB_PORT; do
        sleep 1
    done
    echo "Database is ready!"
}

# Function to run database migrations
run_migrations() {
    echo "Running database migrations..."
    cd /app/backend
    python -c "
from database import engine, Base
# Import all models so SQLAlchemy knows about them
from models.user import User
from models.health_profile import HealthProfile
from models.activity_log import ActivityLog
from models.metrics_history import MetricsHistory
from models.goal import Goal
from models.user_settings import UserSettings
from models.consent import DataConsent
from models.achievement import Achievement, UserAchievement
from models.recipe import Recipe, Ingredient, RecipeIngredient, RecipeInstruction
from models.nutrition import (
    UserNutritionPreferences, MealPlan, MealPlanMeal, MealPlanRecipe,
    NutritionalLog, ShoppingList, ShoppingListItem
)
from models.recipe_rating import RecipeRating, RecipeReview, ReviewHelpful
from models.nutrition_goals import NutritionGoal, GoalProgressLog, GoalMilestone, GoalTemplate
from models.micronutrients import MicronutrientGoal, DailyMicronutrientIntake, MicronutrientDeficiency
from models.nutrition_education import (
    NutritionArticle, NutritionTip, QuizQuestion, UserEducationProgress,
    UserQuizAnswer, UserLearningPath, DailyNutritionTip, NutritionFact
)
Base.metadata.create_all(bind=engine)
print('Database migrations completed')
"
}

# Function to seed initial data
seed_data() {
    echo "Seeding initial data..."
    cd /app/backend
    
    # Seed goals (optional)
    python -c "
from scripts.seed_goals_direct import seed_goal_templates
try:
    seed_goal_templates()
    print('Goal templates seeded')
except Exception as e:
    print(f'Goal seeding failed: {e}')
" || echo "Goal seeding skipped"
    
    # Seed recipes and ingredients (optional - takes time)
    if [ "${SEED_RECIPES:-false}" = "true" ]; then
        echo "Seeding recipes and ingredients (this may take a few minutes)..."
        python scripts/comprehensive_seeder.py || echo "Recipe seeding skipped"
        
        # Import full ingredient database (adds 5,388 ingredients)
        echo "Importing full ingredient database..."
        python scripts/import_ingredients_from_json.py || echo "Ingredient import skipped"
        
        # Generate embeddings (REQUIRED for RAG)
        echo "Generating recipe embeddings (this may take 5-15 minutes)..."
        python scripts/generate_recipe_embeddings.py || echo "Recipe embedding generation skipped"
        
        echo "Generating ingredient embeddings (this may take 2-5 minutes)..."
        python scripts/generate_ingredient_embeddings.py || echo "Ingredient embedding generation skipped"
        
        # Recalculate recipe nutrition from ingredients (IMPORTANT - fixes 0 calorie issue)
        echo "Recalculating recipe nutrition from ingredients..."
        python scripts/recalculate_recipe_nutrition.py || echo "Nutrition recalculation skipped"
    else
        echo "Recipe seeding skipped (set SEED_RECIPES=true to enable)"
    fi
}

# Function to start backend
start_backend() {
    echo "Starting backend server..."
    cd /app/backend
    # Don't use --reload in production Docker container
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    echo "Backend started with PID $BACKEND_PID"
    # Wait a bit for backend to start
    sleep 2
}

# Function to start nginx
start_nginx() {
    echo "Starting nginx..."
    nginx -g "daemon off;" &
    NGINX_PID=$!
    echo "Nginx started with PID $NGINX_PID"
}

# Function to handle shutdown
cleanup() {
    echo "Shutting down..."
    kill $BACKEND_PID $NGINX_PID 2>/dev/null || true
    exit 0
}

# Set up signal handlers
trap cleanup SIGTERM SIGINT

# Construct DATABASE_URL if not set and individual DB vars are provided
if [ -z "$DATABASE_URL" ] && [ -n "$DB_HOST" ]; then
    export DATABASE_URL="postgresql://${DB_USER:-postgres}:${DB_PASSWORD:-password}@${DB_HOST}:${DB_PORT:-5432}/${DB_NAME:-health_app}"
fi

# Wait for database
if [ -n "$DATABASE_URL" ]; then
    # Extract host from DATABASE_URL if it's PostgreSQL
    if [[ "$DATABASE_URL" == postgresql://* ]]; then
        DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
        DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
        if [ -n "$DB_HOST" ] && [ "$DB_HOST" != "localhost" ]; then
            wait_for_db
        fi
    fi
fi

# Run database setup
run_migrations

# Seed data (optional - can be skipped if already seeded)
if [ "${SEED_DATABASE:-true}" = "true" ]; then
    seed_data
fi

# Start services
start_backend
start_nginx

echo "Numbers Don't Lie Health App is running!"
echo "Frontend: http://localhost"
echo "Backend API: http://localhost:8000"
echo "Health Check: http://localhost/health"

# Wait for any process to exit
wait
