from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime

# Base schemas
class RecipeRatingBase(BaseModel):
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    review_text: Optional[str] = Field(None, max_length=2000, description="Optional review text")
    is_verified: bool = Field(False, description="Whether user actually cooked this recipe")
    difficulty_rating: Optional[int] = Field(None, ge=1, le=5, description="How hard was it to make (1-5)")
    taste_rating: Optional[int] = Field(None, ge=1, le=5, description="How did it taste (1-5)")
    would_make_again: bool = Field(True, description="Would user make this recipe again")

class RecipeReviewBase(BaseModel):
    title: Optional[str] = Field(None, max_length=200, description="Optional review title")
    content: str = Field(..., min_length=10, max_length=5000, description="Review content")
    is_helpful: bool = Field(True, description="Is this review helpful to others")
    cooking_tips: Optional[str] = Field(None, max_length=1000, description="Tips for cooking this recipe")
    modifications: Optional[str] = Field(None, max_length=1000, description="What user changed/modified")

# Create schemas
class RecipeRatingCreate(RecipeRatingBase):
    recipe_id: str = Field(..., description="ID of the recipe being rated")

class RecipeReviewCreate(RecipeReviewBase):
    recipe_id: str = Field(..., description="ID of the recipe being reviewed")

class ReviewHelpfulCreate(BaseModel):
    review_id: int = Field(..., description="ID of the review")
    is_helpful: bool = Field(..., description="True if helpful, False if not helpful")

# Update schemas
class RecipeRatingUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    review_text: Optional[str] = Field(None, max_length=2000)
    is_verified: Optional[bool] = None
    difficulty_rating: Optional[int] = Field(None, ge=1, le=5)
    taste_rating: Optional[int] = Field(None, ge=1, le=5)
    would_make_again: Optional[bool] = None

class RecipeReviewUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    content: Optional[str] = Field(None, min_length=10, max_length=5000)
    is_helpful: Optional[bool] = None
    cooking_tips: Optional[str] = Field(None, max_length=1000)
    modifications: Optional[str] = Field(None, max_length=1000)

# Response schemas
class RecipeRatingResponse(RecipeRatingBase):
    id: int
    user_id: str
    recipe_id: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RecipeReviewResponse(RecipeReviewBase):
    id: int
    user_id: str
    recipe_id: str
    created_at: datetime
    updated_at: datetime
    helpful_count: int = Field(0, description="Number of helpful votes")
    not_helpful_count: int = Field(0, description="Number of not helpful votes")
    
    class Config:
        from_attributes = True

class ReviewHelpfulResponse(BaseModel):
    id: int
    user_id: str
    review_id: int
    is_helpful: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Recipe statistics
class RecipeStatsResponse(BaseModel):
    recipe_id: str
    average_rating: float = Field(..., ge=0, le=5)
    total_ratings: int = Field(..., ge=0)
    rating_distribution: dict = Field(..., description="Distribution of ratings (1-5 stars)")
    total_reviews: int = Field(..., ge=0)
    verified_cooks: int = Field(..., ge=0, description="Number of verified cooks")
    would_make_again_percentage: float = Field(..., ge=0, le=100)
    average_difficulty_rating: Optional[float] = Field(None, ge=1, le=5)
    average_taste_rating: Optional[float] = Field(None, ge=1, le=5)

# User rating/review summary
class UserRatingSummary(BaseModel):
    total_ratings: int = Field(0, ge=0)
    total_reviews: int = Field(0, ge=0)
    average_rating_given: Optional[float] = Field(None, ge=0, le=5)
    most_rated_cuisine: Optional[str] = None
    favorite_recipe: Optional[str] = None

# Search and filter schemas
class RecipeRatingFilter(BaseModel):
    min_rating: Optional[float] = Field(None, ge=1, le=5)
    max_rating: Optional[float] = Field(None, ge=1, le=5)
    verified_only: bool = Field(False)
    would_make_again: Optional[bool] = None
    min_reviews: int = Field(0, ge=0)
    cuisine: Optional[str] = None
    meal_type: Optional[str] = None
    difficulty_level: Optional[str] = None

class RecipeReviewFilter(BaseModel):
    recipe_id: Optional[str] = None
    user_id: Optional[str] = None
    helpful_only: bool = Field(False)
    verified_only: bool = Field(False)
    has_tips: bool = Field(False)
    has_modifications: bool = Field(False)







