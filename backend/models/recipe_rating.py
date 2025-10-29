from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base, TimestampMixin

class RecipeRating(Base, TimestampMixin):
    __tablename__ = "recipe_ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    recipe_id = Column(String, ForeignKey("recipes.id"), nullable=False, index=True)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    review_text = Column(Text, nullable=True)  # Optional review text
    is_verified = Column(Boolean, default=False)  # User actually cooked this recipe
    difficulty_rating = Column(Integer, nullable=True)  # 1-5 (how hard was it to make)
    taste_rating = Column(Integer, nullable=True)  # 1-5 (how did it taste)
    would_make_again = Column(Boolean, default=True)  # Would user make this again
    
    # Relationships
    user = relationship("User")
    recipe = relationship("Recipe")
    
    # Ensure one rating per user per recipe
    __table_args__ = (
        UniqueConstraint('user_id', 'recipe_id', name='unique_user_recipe_rating'),
    )

class RecipeReview(Base, TimestampMixin):
    __tablename__ = "recipe_reviews"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    recipe_id = Column(String, ForeignKey("recipes.id"), nullable=False, index=True)
    title = Column(String, nullable=True)  # Optional review title
    content = Column(Text, nullable=False)  # Review content
    is_helpful = Column(Boolean, default=True)  # Is this review helpful to others
    cooking_tips = Column(Text, nullable=True)  # Tips for cooking this recipe
    modifications = Column(Text, nullable=True)  # What user changed/modified
    photos = Column(Text, nullable=True)  # JSON array of photo URLs (future feature)
    
    # Relationships
    user = relationship("User")
    recipe = relationship("Recipe")
    
    # Ensure one review per user per recipe
    __table_args__ = (
        UniqueConstraint('user_id', 'recipe_id', name='unique_user_recipe_review'),
    )

class ReviewHelpful(Base, TimestampMixin):
    __tablename__ = "review_helpful"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    review_id = Column(Integer, ForeignKey("recipe_reviews.id"), nullable=False, index=True)
    is_helpful = Column(Boolean, nullable=False)  # True = helpful, False = not helpful
    
    # Relationships
    user = relationship("User")
    review = relationship("RecipeReview")
    
    # Ensure one vote per user per review
    __table_args__ = (
        UniqueConstraint('user_id', 'review_id', name='unique_user_review_vote'),
    )
