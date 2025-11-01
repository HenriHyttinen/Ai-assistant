"""
Recipe Rating and Review Service
Handles all business logic for recipe ratings, reviews, and statistics
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from models.recipe_rating import RecipeRating, RecipeReview, ReviewHelpful
from models.recipe import Recipe
from models.user import User
from schemas.recipe_rating import (
    RecipeRatingCreate, RecipeRatingUpdate, RecipeRatingResponse,
    RecipeReviewCreate, RecipeReviewUpdate, RecipeReviewResponse,
    ReviewHelpfulCreate, RecipeStatsResponse, UserRatingSummary,
    RecipeRatingFilter, RecipeReviewFilter
)
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class RecipeRatingService:
    def __init__(self):
        self.logger = logger

    # Rating methods
    def create_rating(self, db: Session, rating_data: RecipeRatingCreate, user_id: str) -> RecipeRatingResponse:
        """Create a new recipe rating"""
        try:
            # Check if user already rated this recipe
            existing_rating = db.query(RecipeRating).filter(
                and_(
                    RecipeRating.user_id == user_id,
                    RecipeRating.recipe_id == rating_data.recipe_id
                )
            ).first()
            
            if existing_rating:
                raise ValueError("User has already rated this recipe")
            
            # Create new rating
            rating = RecipeRating(
                user_id=user_id,
                recipe_id=rating_data.recipe_id,
                rating=rating_data.rating,
                review_text=rating_data.review_text,
                is_verified=rating_data.is_verified,
                difficulty_rating=rating_data.difficulty_rating,
                taste_rating=rating_data.taste_rating,
                would_make_again=rating_data.would_make_again
            )
            
            db.add(rating)
            db.commit()
            db.refresh(rating)
            
            return RecipeRatingResponse.from_orm(rating)
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error creating rating: {str(e)}")
            raise

    def update_rating(self, db: Session, rating_id: int, user_id: str, rating_data: RecipeRatingUpdate) -> RecipeRatingResponse:
        """Update an existing recipe rating"""
        try:
            rating = db.query(RecipeRating).filter(
                and_(
                    RecipeRating.id == rating_id,
                    RecipeRating.user_id == user_id
                )
            ).first()
            
            if not rating:
                raise ValueError("Rating not found or not owned by user")
            
            # Update fields
            for field, value in rating_data.dict(exclude_unset=True).items():
                setattr(rating, field, value)
            
            rating.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(rating)
            
            return RecipeRatingResponse.from_orm(rating)
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error updating rating: {str(e)}")
            raise

    def delete_rating(self, db: Session, rating_id: int, user_id: str) -> bool:
        """Delete a recipe rating"""
        try:
            rating = db.query(RecipeRating).filter(
                and_(
                    RecipeRating.id == rating_id,
                    RecipeRating.user_id == user_id
                )
            ).first()
            
            if not rating:
                raise ValueError("Rating not found or not owned by user")
            
            db.delete(rating)
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error deleting rating: {str(e)}")
            raise

    def get_user_rating(self, db: Session, recipe_id: str, user_id: str) -> Optional[RecipeRatingResponse]:
        """Get user's rating for a specific recipe"""
        try:
            rating = db.query(RecipeRating).filter(
                and_(
                    RecipeRating.recipe_id == recipe_id,
                    RecipeRating.user_id == user_id
                )
            ).first()
            
            if rating:
                return RecipeRatingResponse.from_orm(rating)
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting user rating: {str(e)}")
            raise

    # Review methods
    def create_review(self, db: Session, review_data: RecipeReviewCreate, user_id: str) -> RecipeReviewResponse:
        """Create a new recipe review"""
        try:
            # Check if user already reviewed this recipe
            existing_review = db.query(RecipeReview).filter(
                and_(
                    RecipeReview.user_id == user_id,
                    RecipeReview.recipe_id == review_data.recipe_id
                )
            ).first()
            
            if existing_review:
                raise ValueError("User has already reviewed this recipe")
            
            # Create new review
            review = RecipeReview(
                user_id=user_id,
                recipe_id=review_data.recipe_id,
                title=review_data.title,
                content=review_data.content,
                is_helpful=review_data.is_helpful,
                cooking_tips=review_data.cooking_tips,
                modifications=review_data.modifications
            )
            
            db.add(review)
            db.commit()
            db.refresh(review)
            
            # Get helpful counts
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
            
            return response
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error creating review: {str(e)}")
            raise

    def update_review(self, db: Session, review_id: int, user_id: str, review_data: RecipeReviewUpdate) -> RecipeReviewResponse:
        """Update an existing recipe review"""
        try:
            review = db.query(RecipeReview).filter(
                and_(
                    RecipeReview.id == review_id,
                    RecipeReview.user_id == user_id
                )
            ).first()
            
            if not review:
                raise ValueError("Review not found or not owned by user")
            
            # Update fields
            for field, value in review_data.dict(exclude_unset=True).items():
                setattr(review, field, value)
            
            review.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(review)
            
            # Get helpful counts
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
            
            return response
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error updating review: {str(e)}")
            raise

    def delete_review(self, db: Session, review_id: int, user_id: str) -> bool:
        """Delete a recipe review"""
        try:
            review = db.query(RecipeReview).filter(
                and_(
                    RecipeReview.id == review_id,
                    RecipeReview.user_id == user_id
                )
            ).first()
            
            if not review:
                raise ValueError("Review not found or not owned by user")
            
            db.delete(review)
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error deleting review: {str(e)}")
            raise

    def get_recipe_reviews(self, db: Session, recipe_id: str, limit: int = 20, offset: int = 0, 
                          filter_data: Optional[RecipeReviewFilter] = None) -> List[RecipeReviewResponse]:
        """Get reviews for a specific recipe"""
        try:
            query = db.query(RecipeReview).filter(RecipeReview.recipe_id == recipe_id)
            
            if filter_data:
                if filter_data.helpful_only:
                    query = query.filter(RecipeReview.is_helpful == True)
                if filter_data.verified_only:
                    # Join with ratings to check if verified
                    query = query.join(RecipeRating, 
                                     and_(RecipeRating.recipe_id == RecipeReview.recipe_id,
                                          RecipeRating.user_id == RecipeReview.user_id,
                                          RecipeRating.is_verified == True))
                if filter_data.has_tips:
                    query = query.filter(RecipeReview.cooking_tips.isnot(None))
                if filter_data.has_modifications:
                    query = query.filter(RecipeReview.modifications.isnot(None))
            
            reviews = query.order_by(desc(RecipeReview.created_at)).offset(offset).limit(limit).all()
            
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
            self.logger.error(f"Error getting recipe reviews: {str(e)}")
            raise

    # Helpful vote methods
    def vote_helpful(self, db: Session, vote_data: ReviewHelpfulCreate, user_id: str) -> bool:
        """Vote on whether a review is helpful"""
        try:
            # Check if user already voted on this review
            existing_vote = db.query(ReviewHelpful).filter(
                and_(
                    ReviewHelpful.user_id == user_id,
                    ReviewHelpful.review_id == vote_data.review_id
                )
            ).first()
            
            if existing_vote:
                # Update existing vote
                existing_vote.is_helpful = vote_data.is_helpful
                existing_vote.updated_at = datetime.utcnow()
            else:
                # Create new vote
                vote = ReviewHelpful(
                    user_id=user_id,
                    review_id=vote_data.review_id,
                    is_helpful=vote_data.is_helpful
                )
                db.add(vote)
            
            db.commit()
            return True
            
        except Exception as e:
            db.rollback()
            self.logger.error(f"Error voting helpful: {str(e)}")
            raise

    # Statistics methods
    def get_recipe_stats(self, db: Session, recipe_id: str) -> RecipeStatsResponse:
        """Get comprehensive statistics for a recipe"""
        try:
            # Basic rating stats
            rating_stats = db.query(
                func.avg(RecipeRating.rating).label('avg_rating'),
                func.count(RecipeRating.id).label('total_ratings'),
                func.count(RecipeRating.id).filter(RecipeRating.is_verified == True).label('verified_cooks'),
                func.avg(RecipeRating.difficulty_rating).label('avg_difficulty'),
                func.avg(RecipeRating.taste_rating).label('avg_taste'),
                func.count(RecipeRating.id).filter(RecipeRating.would_make_again == True).label('would_make_again_count')
            ).filter(RecipeRating.recipe_id == recipe_id).first()
            
            # Rating distribution
            distribution = {}
            for rating in range(1, 6):
                count = db.query(RecipeRating).filter(
                    and_(
                        RecipeRating.recipe_id == recipe_id,
                        RecipeRating.rating == rating
                    )
                ).count()
                distribution[str(rating)] = count
            
            # Review count
            total_reviews = db.query(RecipeReview).filter(RecipeReview.recipe_id == recipe_id).count()
            
            # Calculate percentages
            avg_rating = float(rating_stats.avg_rating) if rating_stats.avg_rating else 0.0
            total_ratings = rating_stats.total_ratings or 0
            verified_cooks = rating_stats.verified_cooks or 0
            would_make_again_count = rating_stats.would_make_again_count or 0
            would_make_again_percentage = (would_make_again_count / total_ratings * 100) if total_ratings > 0 else 0.0
            
            return RecipeStatsResponse(
                recipe_id=recipe_id,
                average_rating=round(avg_rating, 2),
                total_ratings=total_ratings,
                rating_distribution=distribution,
                total_reviews=total_reviews,
                verified_cooks=verified_cooks,
                would_make_again_percentage=round(would_make_again_percentage, 1),
                average_difficulty_rating=round(float(rating_stats.avg_difficulty), 2) if rating_stats.avg_difficulty else None,
                average_taste_rating=round(float(rating_stats.avg_taste), 2) if rating_stats.avg_taste else None
            )
            
        except Exception as e:
            self.logger.error(f"Error getting recipe stats: {str(e)}")
            raise

    def get_user_rating_summary(self, db: Session, user_id: str) -> UserRatingSummary:
        """Get summary of user's ratings and reviews"""
        try:
            # Basic counts
            total_ratings = db.query(RecipeRating).filter(RecipeRating.user_id == user_id).count()
            total_reviews = db.query(RecipeReview).filter(RecipeReview.user_id == user_id).count()
            
            # Average rating given
            avg_rating = db.query(func.avg(RecipeRating.rating)).filter(
                RecipeRating.user_id == user_id
            ).scalar()
            
            # Most rated cuisine
            cuisine_stats = db.query(
                Recipe.cuisine,
                func.count(RecipeRating.id).label('count')
            ).join(RecipeRating, RecipeRating.recipe_id == Recipe.id).filter(
                RecipeRating.user_id == user_id
            ).group_by(Recipe.cuisine).order_by(desc('count')).first()
            
            # Favorite recipe (highest rated)
            favorite_recipe = db.query(
                Recipe.title,
                RecipeRating.rating
            ).join(RecipeRating, RecipeRating.recipe_id == Recipe.id).filter(
                RecipeRating.user_id == user_id
            ).order_by(desc(RecipeRating.rating)).first()
            
            return UserRatingSummary(
                total_ratings=total_ratings,
                total_reviews=total_reviews,
                average_rating_given=round(float(avg_rating), 2) if avg_rating else None,
                most_rated_cuisine=cuisine_stats[0] if cuisine_stats else None,
                favorite_recipe=favorite_recipe[0] if favorite_recipe else None
            )
            
        except Exception as e:
            self.logger.error(f"Error getting user rating summary: {str(e)}")
            raise

    def search_recipes_by_rating(self, db: Session, filter_data: RecipeRatingFilter, 
                                limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Search recipes based on rating criteria"""
        try:
            # Start with recipes that have ratings
            query = db.query(Recipe).join(RecipeRating, RecipeRating.recipe_id == Recipe.id)
            
            # Apply filters
            if filter_data.min_rating:
                query = query.filter(RecipeRating.rating >= filter_data.min_rating)
            if filter_data.max_rating:
                query = query.filter(RecipeRating.rating <= filter_data.max_rating)
            if filter_data.verified_only:
                query = query.filter(RecipeRating.is_verified == True)
            if filter_data.would_make_again is not None:
                query = query.filter(RecipeRating.would_make_again == filter_data.would_make_again)
            if filter_data.cuisine:
                query = query.filter(Recipe.cuisine == filter_data.cuisine)
            if filter_data.meal_type:
                query = query.filter(Recipe.meal_type == filter_data.meal_type)
            if filter_data.difficulty_level:
                query = query.filter(Recipe.difficulty_level == filter_data.difficulty_level)
            
            # Group by recipe and calculate average rating
            query = query.group_by(Recipe.id).having(
                func.count(RecipeRating.id) >= filter_data.min_reviews
            )
            
            # Order by average rating
            recipes = query.order_by(desc(func.avg(RecipeRating.rating))).offset(offset).limit(limit).all()
            
            # Get stats for each recipe
            result = []
            for recipe in recipes:
                stats = self.get_recipe_stats(db, recipe.id)
                recipe_dict = {
                    "id": recipe.id,
                    "title": recipe.title,
                    "cuisine": recipe.cuisine,
                    "meal_type": recipe.meal_type,
                    "difficulty_level": recipe.difficulty_level,
                    "prep_time": recipe.prep_time,
                    "cook_time": recipe.cook_time,
                    "servings": recipe.servings,
                    "image_url": recipe.image_url,
                    "dietary_tags": recipe.dietary_tags,
                    "per_serving_calories": recipe.per_serving_calories,
                    "per_serving_protein": recipe.per_serving_protein,
                    "per_serving_carbs": recipe.per_serving_carbs,
                    "per_serving_fat": recipe.per_serving_fat,
                    "average_rating": stats.average_rating,
                    "total_ratings": stats.total_ratings,
                    "total_reviews": stats.total_reviews
                }
                result.append(recipe_dict)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error searching recipes by rating: {str(e)}")
            raise







