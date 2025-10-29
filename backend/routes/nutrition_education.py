from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from auth.supabase_auth import get_current_user_supabase as get_current_user
from services.nutrition_education_service import NutritionEducationService
from schemas.nutrition_education import (
    NutritionArticleResponse, NutritionArticleCreate, NutritionArticleUpdate,
    NutritionTipResponse, NutritionTipCreate, NutritionTipUpdate,
    QuizQuestionResponse, QuizQuestionCreate, QuizSessionCreate, QuizSubmission,
    UserEducationProgressResponse, UserEducationProgressCreate, UserEducationProgressUpdate,
    UserLearningPathResponse, UserLearningPathCreate, UserLearningPathUpdate,
    NutritionFactResponse, NutritionFactCreate, EducationContentSearch,
    UserEducationDashboard, LearningAnalytics, QuizResult
)

router = APIRouter()

# Article routes
@router.post("/articles", response_model=NutritionArticleResponse)
async def create_article(
    article_data: NutritionArticleCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new nutrition article"""
    service = NutritionEducationService(db)
    return service.create_article(article_data)

@router.get("/articles/{article_id}", response_model=NutritionArticleResponse)
async def get_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a nutrition article by ID"""
    service = NutritionEducationService(db)
    article = service.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Increment view count
    service.increment_article_views(article_id)
    
    return article

@router.get("/articles/slug/{slug}", response_model=NutritionArticleResponse)
async def get_article_by_slug(
    slug: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a nutrition article by slug"""
    service = NutritionEducationService(db)
    article = service.get_article_by_slug(slug)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    # Increment view count
    service.increment_article_views(article.id)
    
    return article

@router.get("/articles", response_model=List[NutritionArticleResponse])
async def get_articles(
    query: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Content category"),
    difficulty_level: Optional[str] = Query(None, description="Difficulty level"),
    content_type: Optional[str] = Query(None, description="Content type"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    is_featured: Optional[bool] = Query(None, description="Featured articles only"),
    is_published: Optional[bool] = Query(True, description="Published articles only"),
    limit: int = Query(20, ge=1, le=100, description="Number of articles to return"),
    offset: int = Query(0, ge=0, description="Number of articles to skip"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get nutrition articles with search and filter parameters"""
    service = NutritionEducationService(db)
    
    search_params = EducationContentSearch(
        query=query,
        category=category,
        difficulty_level=difficulty_level,
        content_type=content_type,
        tags=tags.split(",") if tags else None,
        is_featured=is_featured,
        is_published=is_published,
        limit=limit,
        offset=offset
    )
    
    return service.get_articles(search_params)

@router.put("/articles/{article_id}", response_model=NutritionArticleResponse)
async def update_article(
    article_id: int,
    article_data: NutritionArticleUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a nutrition article"""
    service = NutritionEducationService(db)
    article = service.update_article(article_id, article_data)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article

@router.delete("/articles/{article_id}")
async def delete_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a nutrition article"""
    service = NutritionEducationService(db)
    success = service.delete_article(article_id)
    if not success:
        raise HTTPException(status_code=404, detail="Article not found")
    return {"message": "Article deleted successfully"}

# Tip routes
@router.post("/tips", response_model=NutritionTipResponse)
async def create_tip(
    tip_data: NutritionTipCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new nutrition tip"""
    service = NutritionEducationService(db)
    return service.create_tip(tip_data)

@router.get("/tips/{tip_id}", response_model=NutritionTipResponse)
async def get_tip(
    tip_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a nutrition tip by ID"""
    service = NutritionEducationService(db)
    tip = service.get_tip(tip_id)
    if not tip:
        raise HTTPException(status_code=404, detail="Tip not found")
    return tip

@router.get("/tips", response_model=List[NutritionTipResponse])
async def get_tips(
    category: Optional[str] = Query(None, description="Tip category"),
    limit: int = Query(20, ge=1, le=100, description="Number of tips to return"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get nutrition tips"""
    service = NutritionEducationService(db)
    return service.get_tips(category=category, limit=limit)

@router.get("/tips/daily", response_model=NutritionTipResponse)
async def get_daily_tip(
    target_goals: Optional[str] = Query(None, description="Comma-separated target goals"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get today's nutrition tip"""
    service = NutritionEducationService(db)
    goals = target_goals.split(",") if target_goals else None
    tip = service.get_daily_tip(current_user["sub"], goals)
    if not tip:
        raise HTTPException(status_code=404, detail="No daily tip available")
    return tip

# Quiz routes
@router.post("/quiz/questions", response_model=QuizQuestionResponse)
async def create_quiz_question(
    question_data: QuizQuestionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new quiz question"""
    service = NutritionEducationService(db)
    return service.create_quiz_question(question_data)

@router.post("/quiz/session")
async def create_quiz_session(
    session_data: QuizSessionCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a quiz session with questions"""
    service = NutritionEducationService(db)
    return service.create_quiz_session(session_data)

@router.post("/quiz/submit", response_model=QuizResult)
async def submit_quiz(
    submission: QuizSubmission,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Submit quiz answers and get results"""
    service = NutritionEducationService(db)
    return service.submit_quiz_answers(current_user["sub"], submission)

# User progress routes
@router.post("/progress", response_model=UserEducationProgressResponse)
async def update_progress(
    progress_data: UserEducationProgressCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update user education progress"""
    service = NutritionEducationService(db)
    return service.update_user_progress(current_user["sub"], progress_data)

@router.get("/progress", response_model=List[UserEducationProgressResponse])
async def get_user_progress(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get user education progress"""
    service = NutritionEducationService(db)
    return service.db.query(UserEducationProgress).filter(
        UserEducationProgress.user_id == current_user["sub"]
    ).all()

# Dashboard routes
@router.get("/dashboard", response_model=UserEducationDashboard)
async def get_user_dashboard(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get user education dashboard"""
    service = NutritionEducationService(db)
    return service.get_user_dashboard(current_user["sub"])

@router.get("/analytics", response_model=LearningAnalytics)
async def get_learning_analytics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get user learning analytics"""
    service = NutritionEducationService(db)
    return service.get_learning_analytics(current_user["sub"])

# Nutrition facts routes
@router.post("/facts", response_model=NutritionFactResponse)
async def create_nutrition_fact(
    fact_data: NutritionFactCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new nutrition fact"""
    service = NutritionEducationService(db)
    return service.create_nutrition_fact(fact_data)

@router.get("/facts/random", response_model=NutritionFactResponse)
async def get_random_fact(
    category: Optional[str] = Query(None, description="Fact category"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a random nutrition fact"""
    service = NutritionEducationService(db)
    fact = service.get_random_nutrition_fact(category)
    if not fact:
        raise HTTPException(status_code=404, detail="No nutrition fact available")
    return fact

@router.get("/facts/featured", response_model=List[NutritionFactResponse])
async def get_featured_facts(
    limit: int = Query(5, ge=1, le=20, description="Number of facts to return"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get featured nutrition facts"""
    service = NutritionEducationService(db)
    return service.get_featured_facts(limit)

# Learning path routes
@router.post("/learning-paths", response_model=UserLearningPathResponse)
async def create_learning_path(
    path_data: UserLearningPathCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new learning path"""
    service = NutritionEducationService(db)
    path = UserLearningPath(
        user_id=current_user["sub"],
        path_name=path_data.path_name,
        description=path_data.description,
        target_goals=path_data.target_goals,
        difficulty_level=path_data.difficulty_level,
        estimated_duration_days=path_data.estimated_duration_days,
        content_sequence=path_data.content_sequence,
        total_steps=len(path_data.content_sequence)
    )
    db.add(path)
    db.commit()
    db.refresh(path)
    return path

@router.get("/learning-paths", response_model=List[UserLearningPathResponse])
async def get_user_learning_paths(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get user learning paths"""
    return db.query(UserLearningPath).filter(
        UserLearningPath.user_id == current_user["sub"]
    ).all()

@router.put("/learning-paths/{path_id}", response_model=UserLearningPathResponse)
async def update_learning_path(
    path_id: int,
    path_data: UserLearningPathUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a learning path"""
    path = db.query(UserLearningPath).filter(
        and_(
            UserLearningPath.id == path_id,
            UserLearningPath.user_id == current_user["sub"]
        )
    ).first()
    
    if not path:
        raise HTTPException(status_code=404, detail="Learning path not found")
    
    update_data = path_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(path, field, value)
    
    db.commit()
    db.refresh(path)
    return path


