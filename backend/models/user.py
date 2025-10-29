from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base
from .base import TimestampMixin

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String, nullable=True)
    backup_codes = Column(String, nullable=True)  # JSON string of backup codes
    oauth_provider = Column(String, nullable=True)
    oauth_id = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)

    # Relationships - basic ones needed for authentication
    # Temporarily commented out to fix SQLAlchemy relationship issues
    # recipe_ratings = relationship("RecipeRating", back_populates="user", lazy="select")
    # recipe_reviews = relationship("RecipeReview", back_populates="user", lazy="select")
    # review_helpful_votes = relationship("ReviewHelpful", back_populates="user", lazy="select")
    
    # Other relationships will be added as needed 