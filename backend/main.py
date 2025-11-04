from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
import time
from typing import Callable
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import logging

from database import engine, Base
# Need to import all models so SQLAlchemy knows about them
from models.user import User
from models.health_profile import HealthProfile
from models.activity_log import ActivityLog
from models.metrics_history import MetricsHistory
from models.goal import Goal
from models.user_settings import UserSettings
from models.consent import DataConsent
from models.achievement import Achievement, UserAchievement
# Import nutrition models
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
# from models.enhanced_nutrition import (
#     NutritionalProfile, DailyNutritionalIntake, FoodComposition,
#     NutritionalAnalysis, HealthMetrics, NutritionalCorrelation
# )
from routes.auth import router as auth_router
from routes.health import router as health_router
from routes.health_profile import router as health_profile_router
from routes.export import router as export_router
from routes.goals import router as goals_router
from routes.settings import router as settings_router
from routes.consent import router as consent_router
from routes.achievements import router as achievements_router
from routes.micronutrients import router as micronutrients_router
from routes.nutrition_education import router as nutrition_education_router
from routes.enhanced_nutrition import router as enhanced_nutrition_router
from routes.nutrition import router as nutrition_router
from routes.daily_logging import router as daily_logging_router
from routes.ai_monitoring import router as ai_monitoring_router
from routes.meal_plan_versioning import router as meal_plan_versioning_router
from routes.recipe_rating import router as recipe_rating_router
from routes.nutrition_analytics import router as nutrition_analytics_router
from routes.nutrition_goals import router as nutrition_goals_router
from routes.meal_plan_recipes import router as meal_plan_recipes_router
from services.tasks import start_background_tasks
from config import get_settings
from logging_config import setup_logging
from middleware.rate_limit import rate_limit_middleware, ai_rate_limit_middleware, auth_rate_limit_middleware
from middleware.security import SecurityMiddleware

# Load env vars
load_dotenv()

# Set up logging
setup_logging()
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create all the database tables
Base.metadata.create_all(bind=engine)

# Lifespan handler for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_background_tasks()  # Re-enabled AI background tasks
    logger.info("Application started")
    yield
    # Shutdown
    logger.info("Application shutting down")

# Create the FastAPI app
app = FastAPI(
    title="Numbers Don't Lie API",
    description="My wellness tracking app API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware - must be added FIRST to process all responses, including errors
# Allow all common localhost origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",  # No port (defaults to 80)
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:8080",
        "http://127.0.0.1",  # No port (defaults to 80)
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
        "http://127.0.0.1:8080",
    ],
    allow_origin_regex=r"^https://.*\.ngrok-free\.app$|^http://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,  # Can be True with explicit origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(SecurityMiddleware, force_https=False)

app.middleware("http")(rate_limit_middleware)
app.middleware("http")(auth_rate_limit_middleware)

# Add error handling middleware - runs BEFORE CORS middleware
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next: Callable):
    try:
        response = await call_next(request)
        # Ensure CORS headers are present on successful responses too
        # (in case CORS middleware didn't run for some reason)
        origin = request.headers.get("origin")
        if origin and origin in [
            "http://localhost", "http://127.0.0.1",
            "http://localhost:5173", "http://127.0.0.1:5173",
            "http://localhost:5174", "http://127.0.0.1:5174",
            "http://localhost:8080", "http://127.0.0.1:8080",
        ]:
            if "Access-Control-Allow-Origin" not in response.headers:
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
        return response
    except HTTPException as e:
        # Re-raise HTTPException so CORS middleware can process it
        raise
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}", exc_info=True)
        # Ensure CORS headers are included even on errors
        response = JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
        # Add CORS headers manually
        origin = request.headers.get("origin")
        if origin and origin in [
            "http://localhost", "http://127.0.0.1",
            "http://localhost:5173", "http://127.0.0.1:5173",
            "http://localhost:5174", "http://127.0.0.1:5174",
            "http://localhost:8080", "http://127.0.0.1:8080",
        ]:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
            response.headers["Access-Control-Allow-Headers"] = "*"
        return response

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(health_profile_router, prefix="/health", tags=["Health Profile"])
app.include_router(export_router, tags=["Export"])
app.include_router(goals_router, prefix="/goals", tags=["Goals"])
app.include_router(settings_router, prefix="/settings", tags=["Settings"])
app.include_router(nutrition_router, prefix="/nutrition", tags=["Nutrition"])
app.include_router(consent_router, tags=["Data Consent"])
app.include_router(achievements_router, prefix="/achievements", tags=["Achievements"])
app.include_router(micronutrients_router, prefix="/micronutrients", tags=["Micronutrients"])
app.include_router(nutrition_education_router, prefix="/nutrition-education", tags=["Nutrition Education"])
app.include_router(enhanced_nutrition_router, prefix="/enhanced-nutrition", tags=["Enhanced Nutrition"])
app.include_router(daily_logging_router, prefix="/daily-logging", tags=["Daily Logging"])
app.include_router(ai_monitoring_router, tags=["AI Monitoring"])
app.include_router(meal_plan_versioning_router, tags=["Meal Plan Versioning"])
app.include_router(recipe_rating_router, tags=["Recipe Ratings"])
app.include_router(nutrition_analytics_router, tags=["Nutrition Analytics"])
app.include_router(nutrition_goals_router, tags=["Nutrition Goals"])
app.include_router(meal_plan_recipes_router, tags=["Meal Plan Recipes"])

@app.get("/")
async def root():
    return {
        "message": "Welcome to Numbers Don't Lie API",
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }

@app.get("/oauth_test_final.html")
async def oauth_test():
    """Serve the OAuth test page."""
    from fastapi.responses import FileResponse
    return FileResponse("static/oauth_test_final.html")

# Background tasks are now handled in the lifespan handler

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    ) 