from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import time
from typing import Callable
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
from routes.auth import router as auth_router
from routes.health import router as health_router
from routes.health_profile import router as health_profile_router
from routes.export import router as export_router
from routes.goals import router as goals_router
from routes.settings import router as settings_router
from routes.consent import router as consent_router
from routes.achievements import router as achievements_router
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

# Create the FastAPI app
app = FastAPI(
    title="Numbers Don't Lie API",
    description="My wellness tracking app API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:5176",
        "http://127.0.0.1:5176",
        "http://localhost:5177",
        "http://127.0.0.1:5177",
        "http://localhost:5178",
        "http://127.0.0.1:5178",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "https://dcffc4808b2c.ngrok-free.app",
    ],
    allow_origin_regex=r"^https://.*\\.ngrok-free\\.app$|^http://(localhost|127\\.0\\.0\\.1):(5173|5174|5175|5176|5177|5178|8080)$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add security middleware
app.add_middleware(SecurityMiddleware, force_https=False)  # Set to True in production

# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)
app.middleware("http")(ai_rate_limit_middleware)
app.middleware("http")(auth_rate_limit_middleware)

# Add error handling middleware
@app.middleware("http")
async def error_handling_middleware(request: Request, call_next: Callable):
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled error: {str(e)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(health_router, prefix="/health", tags=["Health"])
app.include_router(health_profile_router, prefix="/health", tags=["Health Profile"])
app.include_router(export_router, tags=["Export"])
app.include_router(goals_router, prefix="/goals", tags=["Goals"])
app.include_router(settings_router, prefix="/settings", tags=["Settings"])
app.include_router(consent_router, tags=["Data Consent"])
app.include_router(achievements_router, prefix="/achievements", tags=["Achievements"])

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

# Start background tasks
@app.on_event("startup")
async def startup_event():
    start_background_tasks()
    logger.info("Application started")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.LOG_LEVEL.lower()
    ) 