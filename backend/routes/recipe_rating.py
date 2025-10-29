"""
Recipe Rating and Review API Routes
Provides endpoints for rating recipes, writing reviews, and getting statistics
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.user import User
from auth.supabase_auth import get_current_user_supabase as get_current_user
from services.recipe_rating_service import RecipeRatingService
from schemas.recipe_rating import (
    RecipeRatingCreate, RecipeRatingUpdate, RecipeRatingResponse,
    RecipeReviewCreate, RecipeReviewUpdate, RecipeReviewResponse,
    ReviewHelpfulCreate, RecipeStatsResponse, UserRatingSummary,
    RecipeRatingFilter, RecipeReviewFilter
)

router = APIRouter(prefix="/recipe-ratings", tags=["recipe-ratings"])

# Rating endpoints
@router.post("/rate", response_model=RecipeRatingResponse)
def create_recipe_rating(
    rating_data: RecipeRatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Rate a recipe (1-5 stars)"""
    try:
        service = RecipeRatingService()
        return service.create_rating(db, rating_data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/rate/{rating_id}", response_model=RecipeRatingResponse)
def update_recipe_rating(
    rating_id: int,
    rating_data: RecipeRatingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a recipe rating"""
    try:
        service = RecipeRatingService()
        return service.update_rating(db, rating_id, current_user.id, rating_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/rate/{rating_id}")
def delete_recipe_rating(
    rating_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a recipe rating"""
    try:
        service = RecipeRatingService()
        success = service.delete_rating(db, rating_id, current_user.id)
        if success:
            return {"message": "Rating deleted successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rating not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/rate/{recipe_id}", response_model=Optional[RecipeRatingResponse])
def get_user_recipe_rating(
    recipe_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user's rating for a specific recipe"""
    try:
        service = RecipeRatingService()
        return service.get_user_rating(db, recipe_id, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Review endpoints
@router.post("/review", response_model=RecipeReviewResponse)
def create_recipe_review(
    review_data: RecipeReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Write a review for a recipe"""
    try:
        service = RecipeRatingService()
        return service.create_review(db, review_data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.put("/review/{review_id}", response_model=RecipeReviewResponse)
def update_recipe_review(
    review_id: int,
    review_data: RecipeReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a recipe review"""
    try:
        service = RecipeRatingService()
        return service.update_review(db, review_id, current_user.id, review_data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/review/{review_id}")
def delete_recipe_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a recipe review"""
    try:
        service = RecipeRatingService()
        success = service.delete_review(db, review_id, current_user.id)
        if success:
            return {"message": "Review deleted successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/review/{recipe_id}", response_model=List[RecipeReviewResponse])
def get_recipe_reviews(
    recipe_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    helpful_only: bool = Query(False),
    verified_only: bool = Query(False),
    has_tips: bool = Query(False),
    has_modifications: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get reviews for a specific recipe"""
    try:
        service = RecipeRatingService()
        filter_data = RecipeReviewFilter(
            recipe_id=recipe_id,
            helpful_only=helpful_only,
            verified_only=verified_only,
            has_tips=has_tips,
            has_modifications=has_modifications
        )
        return service.get_recipe_reviews(db, recipe_id, limit, offset, filter_data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Helpful vote endpoints
@router.post("/review/{review_id}/helpful")
def vote_review_helpful(
    review_id: int,
    is_helpful: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Vote on whether a review is helpful"""
    try:
        service = RecipeRatingService()
        vote_data = ReviewHelpfulCreate(review_id=review_id, is_helpful=is_helpful)
        success = service.vote_helpful(db, vote_data, current_user.id)
        if success:
            return {"message": "Vote recorded successfully"}
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to record vote")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Statistics endpoints
@router.get("/stats/{recipe_id}", response_model=RecipeStatsResponse)
def get_recipe_stats(
    recipe_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive statistics for a recipe"""
    try:
        service = RecipeRatingService()
        return service.get_recipe_stats(db, recipe_id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/user-summary", response_model=UserRatingSummary)
def get_user_rating_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get summary of user's ratings and reviews"""
    try:
        service = RecipeRatingService()
        return service.get_user_rating_summary(db, current_user.id)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Search endpoints
@router.post("/search", response_model=List[dict])
def search_recipes_by_rating(
    filter_data: RecipeRatingFilter,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Search recipes based on rating criteria"""
    try:
        service = RecipeRatingService()
        return service.search_recipes_by_rating(db, filter_data, limit, offset)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Top rated recipes
@router.get("/top-rated", response_model=List[dict])
def get_top_rated_recipes(
    limit: int = Query(10, ge=1, le=50),
    min_ratings: int = Query(5, ge=1),
    cuisine: Optional[str] = Query(None),
    meal_type: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get top rated recipes"""
    try:
        service = RecipeRatingService()
        filter_data = RecipeRatingFilter(
            min_rating=4.0,
            min_reviews=min_ratings,
            cuisine=cuisine,
            meal_type=meal_type
        )
        return service.search_recipes_by_rating(db, filter_data, limit, 0)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

# Recent reviews
@router.get("/recent-reviews", response_model=List[RecipeReviewResponse])
def get_recent_reviews(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get recent recipe reviews"""
    try:
        service = RecipeRatingService()
        # Get recent reviews across all recipes
        from models.recipe_rating import RecipeReview
        from sqlalchemy import desc
        
        reviews = db.query(RecipeReview).order_by(desc(RecipeReview.created_at)).limit(limit).all()
        
        # Get helpful counts for each review
        result = []
        for review in reviews:
            helpful_count = db.query(ReviewHelpful).filter(
                and_(
                    ReviewHelpful.review_id == review.id,
                    ReviewHelpful.is_helpful == True
                )
            ).count()
            
            not_helpful_count = db.query(ReviewHelpful).filter(
                and_(
                    ReviewHelpful.review_id == review.id,
                    ReviewHelpful.is_helpful == False
                )
            ).count()
            
            response = RecipeReviewResponse.from_orm(review)
            response.helpful_count = helpful_count
            response.not_helpful_count = not_helpful_count
            result.append(response)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
