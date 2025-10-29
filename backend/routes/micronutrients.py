from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from auth.supabase_auth import get_current_user_supabase as get_current_user
from models.user import User
from services.micronutrient_service import MicronutrientService
from schemas.micronutrients import (
    MicronutrientGoalCreate, MicronutrientGoalResponse,
    DailyMicronutrientIntakeCreate, DailyMicronutrientIntakeResponse,
    MicronutrientAnalysis, MicronutrientDashboard, MicronutrientDeficiencyResponse,
    MicronutrientSearchFilter
)

router = APIRouter(tags=["micronutrients"])

@router.post("/goals", response_model=MicronutrientGoalResponse)
def create_or_update_goals(
    goals_data: MicronutrientGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update micronutrient goals"""
    try:
        service = MicronutrientService()
        return service.create_or_update_goals(db, current_user.id, goals_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating/updating goals: {str(e)}"
        )

@router.get("/goals", response_model=Optional[MicronutrientGoalResponse])
def get_user_goals(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's micronutrient goals"""
    try:
        service = MicronutrientService()
        return service.get_user_goals(db, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting goals: {str(e)}"
        )

@router.post("/intake", response_model=DailyMicronutrientIntakeResponse)
def log_daily_intake(
    intake_data: DailyMicronutrientIntakeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Log daily micronutrient intake"""
    try:
        service = MicronutrientService()
        return service.log_daily_intake(db, current_user.id, intake_data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error logging intake: {str(e)}"
        )

@router.get("/intake/{date}", response_model=Optional[DailyMicronutrientIntakeResponse])
def get_daily_intake(
    date: datetime,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get daily micronutrient intake for a specific date"""
    try:
        service = MicronutrientService()
        return service.get_daily_intake(db, current_user.id, date)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting daily intake: {str(e)}"
        )

@router.get("/dashboard", response_model=MicronutrientDashboard)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get micronutrient dashboard"""
    try:
        service = MicronutrientService()
        return service.get_dashboard(db, current_user.id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting dashboard: {str(e)}"
        )

@router.get("/deficiencies", response_model=List[MicronutrientDeficiencyResponse])
def get_deficiencies(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current micronutrient deficiencies"""
    try:
        service = MicronutrientService()
        # Get today's intake to analyze deficiencies
        today = datetime.utcnow().date()
        today_intake = service.get_daily_intake(db, current_user.id, datetime.combine(today, datetime.min.time()))
        current_intake = today_intake.dict() if today_intake else {}
        return service.analyze_deficiencies(db, current_user.id, current_intake)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting deficiencies: {str(e)}"
        )

@router.get("/weekly-average", response_model=dict)
def get_weekly_average(
    start_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get weekly average micronutrient intake"""
    try:
        service = MicronutrientService()
        if not start_date:
            # Default to start of current week
            today = datetime.utcnow().date()
            start_date = today - timedelta(days=today.weekday())
            start_date = datetime.combine(start_date, datetime.min.time())
        
        return service.get_weekly_average(db, current_user.id, start_date)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting weekly average: {str(e)}"
        )

@router.get("/analysis", response_model=MicronutrientAnalysis)
def get_analysis(
    start_date: datetime,
    end_date: datetime,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get micronutrient analysis for a period"""
    try:
        service = MicronutrientService()
        
        # Get goals
        goals = service.get_user_goals(db, current_user.id)
        if not goals:
            goals = service.create_or_update_goals(db, current_user.id, MicronutrientGoalCreate())
        
        # Get average intake for the period
        period_days = (end_date - start_date).days
        if period_days <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End date must be after start date"
            )
        
        # Calculate period average
        total_intake = {}
        micronutrients = [
            "vitamin_d", "vitamin_b12", "iron", "calcium", "magnesium",
            "vitamin_c", "folate", "zinc", "potassium", "fiber"
        ]
        
        for nutrient in micronutrients:
            total_intake[nutrient] = 0
        
        # Get all intakes in the period
        intakes = db.query(DailyMicronutrientIntake).filter(
            and_(
                DailyMicronutrientIntake.user_id == current_user.id,
                DailyMicronutrientIntake.date >= start_date,
                DailyMicronutrientIntake.date <= end_date
            )
        ).all()
        
        if intakes:
            for intake in intakes:
                for nutrient in micronutrients:
                    total_intake[nutrient] += getattr(intake, f"{nutrient}_intake", 0)
            
            # Calculate averages
            for nutrient in micronutrients:
                total_intake[nutrient] /= len(intakes)
        
        # Analyze deficiencies
        deficiencies = service.analyze_deficiencies(db, current_user.id, total_intake)
        
        # Generate recommendations
        recommendations = service._generate_recommendations(deficiencies, total_intake)
        
        # Calculate overall score
        overall_score = service._calculate_overall_score(goals, total_intake)
        
        return MicronutrientAnalysis(
            period_start=start_date,
            period_end=end_date,
            average_intake=total_intake,
            goal_targets=goals.dict(),
            deficiencies=deficiencies,
            recommendations=recommendations,
            overall_score=overall_score
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting analysis: {str(e)}"
        )

@router.post("/recipes/search")
def search_recipes_by_micronutrients(
    filter_data: MicronutrientSearchFilter,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search recipes based on micronutrient content"""
    try:
        from models.recipe import Recipe
        
        query = db.query(Recipe).filter(Recipe.is_active == True)
        
        # Apply micronutrient filters
        if filter_data.min_vitamin_d:
            query = query.filter(Recipe.per_serving_vitamin_d >= filter_data.min_vitamin_d)
        if filter_data.min_vitamin_b12:
            query = query.filter(Recipe.per_serving_vitamin_b12 >= filter_data.min_vitamin_b12)
        if filter_data.min_iron:
            query = query.filter(Recipe.per_serving_iron >= filter_data.min_iron)
        if filter_data.min_calcium:
            query = query.filter(Recipe.per_serving_calcium >= filter_data.min_calcium)
        if filter_data.min_magnesium:
            query = query.filter(Recipe.per_serving_magnesium >= filter_data.min_magnesium)
        if filter_data.min_vitamin_c:
            query = query.filter(Recipe.per_serving_vitamin_c >= filter_data.min_vitamin_c)
        if filter_data.min_folate:
            query = query.filter(Recipe.per_serving_folate >= filter_data.min_folate)
        if filter_data.min_zinc:
            query = query.filter(Recipe.per_serving_zinc >= filter_data.min_zinc)
        if filter_data.min_potassium:
            query = query.filter(Recipe.per_serving_potassium >= filter_data.min_potassium)
        if filter_data.min_fiber:
            query = query.filter(Recipe.per_serving_fiber >= filter_data.min_fiber)
        
        recipes = query.limit(50).all()
        
        return {
            "recipes": [
                {
                    "id": recipe.id,
                    "title": recipe.title,
                    "cuisine": recipe.cuisine,
                    "meal_type": recipe.meal_type,
                    "servings": recipe.servings,
                    "prep_time": recipe.prep_time,
                    "cook_time": recipe.cook_time,
                    "difficulty_level": recipe.difficulty_level,
                    "dietary_tags": recipe.dietary_tags,
                    "per_serving_vitamin_d": recipe.per_serving_vitamin_d,
                    "per_serving_vitamin_b12": recipe.per_serving_vitamin_b12,
                    "per_serving_iron": recipe.per_serving_iron,
                    "per_serving_calcium": recipe.per_serving_calcium,
                    "per_serving_magnesium": recipe.per_serving_magnesium,
                    "per_serving_vitamin_c": recipe.per_serving_vitamin_c,
                    "per_serving_folate": recipe.per_serving_folate,
                    "per_serving_zinc": recipe.per_serving_zinc,
                    "per_serving_potassium": recipe.per_serving_potassium,
                    "per_serving_fiber": recipe.per_serving_fiber,
                }
                for recipe in recipes
            ],
            "total": len(recipes)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching recipes: {str(e)}"
        )