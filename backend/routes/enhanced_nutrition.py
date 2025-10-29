from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
from datetime import date, timedelta
import json
import statistics

from database import get_db
from auth.supabase_auth import get_current_user_supabase as get_current_user
from services.enhanced_nutrition_service import EnhancedNutritionService
from models.enhanced_nutrition import FoodComposition, NutritionalAnalysis, HealthMetrics, NutritionalCorrelation
from schemas.enhanced_nutrition import (
    NutritionalProfileResponse, NutritionalProfileCreate, NutritionalProfileUpdate, NutritionalProfileSearch,
    DailyNutritionalIntakeResponse, DailyNutritionalIntakeCreate, DailyNutritionalIntakeUpdate,
    FoodCompositionResponse, FoodCompositionCreate, FoodCompositionUpdate, FoodCompositionSearch,
    NutritionalAnalysisResponse, NutritionalAnalysisCreate, NutritionalAnalysisUpdate, NutritionalAnalysisSearch,
    HealthMetricsResponse, HealthMetricsCreate, HealthMetricsUpdate,
    NutritionalCorrelationResponse, NutritionalCorrelationCreate,
    NutritionalDashboard, NutritionalInsights
)

router = APIRouter()

# Nutritional Profile Routes
@router.post("/profiles", response_model=NutritionalProfileResponse)
async def create_nutritional_profile(
    profile_data: NutritionalProfileCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new nutritional profile"""
    service = EnhancedNutritionService(db)
    return service.create_nutritional_profile(current_user["sub"], profile_data)

@router.get("/profiles/{profile_id}", response_model=NutritionalProfileResponse)
async def get_nutritional_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a nutritional profile by ID"""
    service = EnhancedNutritionService(db)
    profile = service.get_nutritional_profile(profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.get("/profiles", response_model=List[NutritionalProfileResponse])
async def get_nutritional_profiles(
    profile_name: Optional[str] = Query(None, description="Filter by profile name"),
    is_default: Optional[bool] = Query(None, description="Filter by default status"),
    limit: int = Query(20, ge=1, le=100, description="Number of profiles to return"),
    offset: int = Query(0, ge=0, description="Number of profiles to skip"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get nutritional profiles for the current user"""
    service = EnhancedNutritionService(db)
    search_params = NutritionalProfileSearch(
        profile_name=profile_name,
        is_default=is_default,
        limit=limit,
        offset=offset
    )
    return service.get_user_profiles(current_user["sub"], search_params)

@router.put("/profiles/{profile_id}", response_model=NutritionalProfileResponse)
async def update_nutritional_profile(
    profile_id: int,
    profile_data: NutritionalProfileUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a nutritional profile"""
    service = EnhancedNutritionService(db)
    profile = service.update_nutritional_profile(profile_id, profile_data)
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile

@router.delete("/profiles/{profile_id}")
async def delete_nutritional_profile(
    profile_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a nutritional profile"""
    service = EnhancedNutritionService(db)
    success = service.delete_nutritional_profile(profile_id)
    if not success:
        raise HTTPException(status_code=404, detail="Profile not found")
    return {"message": "Profile deleted successfully"}

# Daily Nutritional Intake Routes
@router.post("/intake", response_model=DailyNutritionalIntakeResponse)
async def create_daily_intake(
    intake_data: DailyNutritionalIntakeCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create or update daily nutritional intake"""
    service = EnhancedNutritionService(db)
    return service.create_daily_intake(current_user["sub"], intake_data)

@router.get("/intake/{intake_date}", response_model=DailyNutritionalIntakeResponse)
async def get_daily_intake(
    intake_date: date,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get daily intake for a specific date"""
    service = EnhancedNutritionService(db)
    intake = service.get_daily_intake(current_user["sub"], intake_date)
    if not intake:
        raise HTTPException(status_code=404, detail="Intake not found for this date")
    return intake

@router.get("/intake", response_model=List[DailyNutritionalIntakeResponse])
async def get_intake_range(
    start_date: date = Query(..., description="Start date for intake range"),
    end_date: date = Query(..., description="End date for intake range"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get daily intakes for a date range"""
    service = EnhancedNutritionService(db)
    return service.get_intake_range(current_user["sub"], start_date, end_date)

@router.put("/intake/{intake_date}", response_model=DailyNutritionalIntakeResponse)
async def update_daily_intake(
    intake_date: date,
    intake_data: DailyNutritionalIntakeUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update daily nutritional intake"""
    service = EnhancedNutritionService(db)
    
    # Get existing intake
    existing_intake = service.get_daily_intake(current_user["sub"], intake_date)
    if not existing_intake:
        raise HTTPException(status_code=404, detail="Intake not found for this date")
    
    # Update the intake
    update_data = intake_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(existing_intake, field, value)
    
    # Recalculate metrics
    service._calculate_intake_metrics(existing_intake)
    
    db.commit()
    db.refresh(existing_intake)
    return existing_intake

# Food Composition Routes
@router.post("/foods", response_model=FoodCompositionResponse)
async def create_food_composition(
    food_data: FoodCompositionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new food composition entry"""
    service = EnhancedNutritionService(db)
    return service.create_food_composition(food_data)

@router.get("/foods", response_model=List[FoodCompositionResponse])
async def search_food_composition(
    food_name: Optional[str] = Query(None, description="Search by food name"),
    food_group: Optional[str] = Query(None, description="Filter by food group"),
    sub_group: Optional[str] = Query(None, description="Filter by sub group"),
    nutrient_density_level: Optional[str] = Query(None, description="Filter by nutrient density level"),
    processing_level: Optional[str] = Query(None, description="Filter by processing level"),
    is_organic: Optional[bool] = Query(None, description="Filter by organic status"),
    is_gluten_free: Optional[bool] = Query(None, description="Filter by gluten-free status"),
    is_dairy_free: Optional[bool] = Query(None, description="Filter by dairy-free status"),
    allergens: Optional[str] = Query(None, description="Comma-separated list of allergens to filter by"),
    limit: int = Query(20, ge=1, le=100, description="Number of foods to return"),
    offset: int = Query(0, ge=0, description="Number of foods to skip"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Search food composition database"""
    service = EnhancedNutritionService(db)
    search_params = FoodCompositionSearch(
        food_name=food_name,
        food_group=food_group,
        sub_group=sub_group,
        nutrient_density_level=nutrient_density_level,
        processing_level=processing_level,
        is_organic=is_organic,
        is_gluten_free=is_gluten_free,
        is_dairy_free=is_dairy_free,
        allergens=allergens.split(",") if allergens else None,
        limit=limit,
        offset=offset
    )
    return service.search_food_composition(search_params)

@router.get("/foods/{food_id}", response_model=FoodCompositionResponse)
async def get_food_composition(
    food_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get food composition by ID"""
    food = db.query(FoodComposition).filter(FoodComposition.id == food_id).first()
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")
    return food

@router.put("/foods/{food_id}", response_model=FoodCompositionResponse)
async def update_food_composition(
    food_id: int,
    food_data: FoodCompositionUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update food composition"""
    food = db.query(FoodComposition).filter(FoodComposition.id == food_id).first()
    if not food:
        raise HTTPException(status_code=404, detail="Food not found")
    
    update_data = food_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        if field in ["allergens", "cross_contamination_risks", "storage_conditions", "preparation_methods"] and value is not None:
            setattr(food, field, json.dumps(value))
        else:
            setattr(food, field, value)
    
    db.commit()
    db.refresh(food)
    return food

# Nutritional Analysis Routes
@router.post("/analyses", response_model=NutritionalAnalysisResponse)
async def create_nutritional_analysis(
    analysis_data: NutritionalAnalysisCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new nutritional analysis"""
    service = EnhancedNutritionService(db)
    return service.create_nutritional_analysis(current_user["sub"], analysis_data)

@router.get("/analyses", response_model=List[NutritionalAnalysisResponse])
async def get_nutritional_analyses(
    analysis_type: Optional[str] = Query(None, description="Filter by analysis type"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    min_nutrition_score: Optional[float] = Query(None, description="Minimum nutrition score"),
    max_nutrition_score: Optional[float] = Query(None, description="Maximum nutrition score"),
    limit: int = Query(20, ge=1, le=100, description="Number of analyses to return"),
    offset: int = Query(0, ge=0, description="Number of analyses to skip"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get nutritional analyses for the current user"""
    service = EnhancedNutritionService(db)
    search_params = NutritionalAnalysisSearch(
        analysis_type=analysis_type,
        start_date=start_date,
        end_date=end_date,
        min_nutrition_score=min_nutrition_score,
        max_nutrition_score=max_nutrition_score,
        limit=limit,
        offset=offset
    )
    return service.get_nutritional_analyses(current_user["sub"], search_params)

@router.get("/analyses/{analysis_id}", response_model=NutritionalAnalysisResponse)
async def get_nutritional_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get nutritional analysis by ID"""
    analysis = db.query(NutritionalAnalysis).filter(
        and_(
            NutritionalAnalysis.id == analysis_id,
            NutritionalAnalysis.user_id == current_user["sub"]
        )
    ).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis

# Health Metrics Routes
@router.post("/health-metrics", response_model=HealthMetricsResponse)
async def create_health_metric(
    metric_data: HealthMetricsCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new health metric entry"""
    service = EnhancedNutritionService(db)
    return service.create_health_metric(current_user["sub"], metric_data)

@router.get("/health-metrics", response_model=List[HealthMetricsResponse])
async def get_health_metrics(
    metric_type: Optional[str] = Query(None, description="Filter by metric type"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get health metrics for the current user"""
    service = EnhancedNutritionService(db)
    return service.get_health_metrics(current_user["sub"], metric_type, start_date, end_date)

@router.put("/health-metrics/{metric_id}", response_model=HealthMetricsResponse)
async def update_health_metric(
    metric_id: int,
    metric_data: HealthMetricsUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update health metric"""
    metric = db.query(HealthMetrics).filter(
        and_(
            HealthMetrics.id == metric_id,
            HealthMetrics.user_id == current_user["sub"]
        )
    ).first()
    if not metric:
        raise HTTPException(status_code=404, detail="Health metric not found")
    
    update_data = metric_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(metric, field, value)
    
    db.commit()
    db.refresh(metric)
    return metric

@router.delete("/health-metrics/{metric_id}")
async def delete_health_metric(
    metric_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete health metric"""
    metric = db.query(HealthMetrics).filter(
        and_(
            HealthMetrics.id == metric_id,
            HealthMetrics.user_id == current_user["sub"]
        )
    ).first()
    if not metric:
        raise HTTPException(status_code=404, detail="Health metric not found")
    
    db.delete(metric)
    db.commit()
    return {"message": "Health metric deleted successfully"}

# Dashboard Routes
@router.get("/dashboard", response_model=NutritionalDashboard)
async def get_nutritional_dashboard(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get comprehensive nutritional dashboard"""
    service = EnhancedNutritionService(db)
    return service.get_nutritional_dashboard(current_user["sub"])

# Correlation Routes
@router.post("/correlations", response_model=NutritionalCorrelationResponse)
async def create_nutritional_correlation(
    correlation_data: NutritionalCorrelationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new nutritional correlation"""
    correlation = NutritionalCorrelation(
        user_id=current_user["sub"],
        correlation_date=correlation_data.correlation_date,
        nutrient_name=correlation_data.nutrient_name,
        health_metric_type=correlation_data.health_metric_type,
        correlation_coefficient=correlation_data.correlation_coefficient,
        correlation_strength=correlation_data.correlation_strength,
        p_value=correlation_data.p_value,
        sample_size=correlation_data.sample_size,
        analysis_period_days=correlation_data.analysis_period_days,
        start_date=correlation_data.start_date,
        end_date=correlation_data.end_date
    )
    
    db.add(correlation)
    db.commit()
    db.refresh(correlation)
    return correlation

@router.get("/correlations", response_model=List[NutritionalCorrelationResponse])
async def get_nutritional_correlations(
    nutrient_name: Optional[str] = Query(None, description="Filter by nutrient name"),
    health_metric_type: Optional[str] = Query(None, description="Filter by health metric type"),
    correlation_strength: Optional[str] = Query(None, description="Filter by correlation strength"),
    limit: int = Query(20, ge=1, le=100, description="Number of correlations to return"),
    offset: int = Query(0, ge=0, description="Number of correlations to skip"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get nutritional correlations for the current user"""
    query = db.query(NutritionalCorrelation).filter(NutritionalCorrelation.user_id == current_user["sub"])
    
    if nutrient_name:
        query = query.filter(NutritionalCorrelation.nutrient_name.ilike(f"%{nutrient_name}%"))
    
    if health_metric_type:
        query = query.filter(NutritionalCorrelation.health_metric_type == health_metric_type)
    
    if correlation_strength:
        query = query.filter(NutritionalCorrelation.correlation_strength == correlation_strength)
    
    return query.order_by(desc(NutritionalCorrelation.correlation_date)).offset(offset).limit(limit).all()

# Utility Routes
@router.get("/insights", response_model=NutritionalInsights)
async def get_nutritional_insights(
    analysis_period: str = Query("weekly", description="Analysis period: daily, weekly, monthly"),
    start_date: Optional[date] = Query(None, description="Start date for analysis"),
    end_date: Optional[date] = Query(None, description="End date for analysis"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get nutritional insights and recommendations"""
    service = EnhancedNutritionService(db)
    
    # Set default dates based on analysis period
    if not start_date or not end_date:
        today = date.today()
        if analysis_period == "daily":
            start_date = today
            end_date = today
        elif analysis_period == "weekly":
            start_date = today - timedelta(days=6)
            end_date = today
        elif analysis_period == "monthly":
            start_date = today - timedelta(days=29)
            end_date = today
    
    # Get intakes for the period
    intakes = service.get_intake_range(current_user["sub"], start_date, end_date)
    
    # Get analyses for the period
    analyses = service.get_nutritional_analyses(
        current_user["sub"],
        NutritionalAnalysisSearch(
            start_date=start_date,
            end_date=end_date,
            limit=10
        )
    )
    
    # Get correlations
    correlations = db.query(NutritionalCorrelation).filter(
        and_(
            NutritionalCorrelation.user_id == current_user["sub"],
            NutritionalCorrelation.start_date >= start_date,
            NutritionalCorrelation.end_date <= end_date
        )
    ).all()
    
    # Generate insights (simplified)
    key_findings = []
    nutrient_gaps = []
    excess_nutrients = []
    recommendations = []
    
    if intakes:
        avg_calories = statistics.mean([i.calories_consumed for i in intakes])
        avg_protein = statistics.mean([i.protein_grams for i in intakes])
        avg_fiber = statistics.mean([i.fiber_grams for i in intakes])
        
        if avg_calories < 1200:
            key_findings.append("Low calorie intake detected")
            recommendations.append("Consider increasing portion sizes or adding healthy snacks")
        
        if avg_protein < 50:
            nutrient_gaps.append("Protein")
            recommendations.append("Include more protein-rich foods in your diet")
        
        if avg_fiber < 25:
            nutrient_gaps.append("Fiber")
            recommendations.append("Add more fruits, vegetables, and whole grains")
    
    return NutritionalInsights(
        user_id=current_user["sub"],
        analysis_period=analysis_period,
        period_start=start_date,
        period_end=end_date,
        key_findings=key_findings,
        nutrient_gaps=nutrient_gaps,
        excess_nutrients=excess_nutrients,
        recommendations=recommendations,
        significant_correlations=correlations
    )
