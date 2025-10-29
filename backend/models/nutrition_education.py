from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base, TimestampMixin
import enum

class ContentType(str, enum.Enum):
    ARTICLE = "article"
    TIP = "tip"
    QUIZ = "quiz"
    VIDEO = "video"
    INFOGRAPHIC = "infographic"
    RECIPE_TIP = "recipe_tip"
    NUTRITION_FACT = "nutrition_fact"

class DifficultyLevel(str, enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ContentCategory(str, enum.Enum):
    MACRONUTRIENTS = "macronutrients"
    MICRONUTRIENTS = "micronutrients"
    WEIGHT_MANAGEMENT = "weight_management"
    SPORTS_NUTRITION = "sports_nutrition"
    MEDICAL_NUTRITION = "medical_nutrition"
    COOKING_TIPS = "cooking_tips"
    MEAL_PLANNING = "meal_planning"
    FOOD_SAFETY = "food_safety"
    SUSTAINABLE_EATING = "sustainable_eating"
    CULTURAL_NUTRITION = "cultural_nutrition"

class NutritionArticle(Base, TimestampMixin):
    __tablename__ = "nutrition_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    slug = Column(String, unique=True, nullable=False, index=True)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    content_type = Column(Enum(ContentType), nullable=False)
    category = Column(Enum(ContentCategory), nullable=False)
    difficulty_level = Column(Enum(DifficultyLevel), default=DifficultyLevel.BEGINNER)
    
    # Content metadata
    reading_time_minutes = Column(Integer, default=5)
    featured_image_url = Column(String, nullable=True)
    tags = Column(Text, nullable=True)  # JSON string of tags
    author = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    
    # Engagement metrics
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    bookmark_count = Column(Integer, default=0)
    
    # Content management
    is_published = Column(Boolean, default=True)
    is_featured = Column(Boolean, default=False)
    priority = Column(Integer, default=0)  # Higher number = higher priority
    target_audience = Column(String, nullable=True)  # e.g., "beginners", "athletes"
    
    # SEO and discoverability
    meta_description = Column(Text, nullable=True)
    keywords = Column(Text, nullable=True)
    
    # Relationships
    user_progress = relationship("UserEducationProgress", back_populates="article")
    quiz_questions = relationship("QuizQuestion", back_populates="article")

class NutritionTip(Base, TimestampMixin):
    __tablename__ = "nutrition_tips"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(Enum(ContentCategory), nullable=False)
    difficulty_level = Column(Enum(DifficultyLevel), default=DifficultyLevel.BEGINNER)
    
    # Tip metadata
    tip_type = Column(String, nullable=True)  # "daily", "weekly", "seasonal", "goal_specific"
    target_goals = Column(Text, nullable=True)  # JSON string of goal types this tip helps with
    target_dietary_restrictions = Column(Text, nullable=True)  # JSON string of dietary restrictions
    
    # Visual content
    image_url = Column(String, nullable=True)
    icon_name = Column(String, nullable=True)
    
    # Engagement
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    
    # Scheduling
    is_daily_tip = Column(Boolean, default=False)
    is_seasonal = Column(Boolean, default=False)
    seasonal_months = Column(Text, nullable=True)  # JSON string of months [1,2,3] for Jan,Feb,Mar

class QuizQuestion(Base, TimestampMixin):
    __tablename__ = "quiz_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    article_id = Column(Integer, ForeignKey("nutrition_articles.id"), nullable=True)
    question_text = Column(Text, nullable=False)
    question_type = Column(String, nullable=False)  # "multiple_choice", "true_false", "fill_blank"
    difficulty_level = Column(Enum(DifficultyLevel), default=DifficultyLevel.BEGINNER)
    category = Column(Enum(ContentCategory), nullable=False)
    
    # Question options (JSON string)
    options = Column(Text, nullable=True)  # For multiple choice questions
    correct_answer = Column(Text, nullable=False)
    explanation = Column(Text, nullable=True)
    
    # Question metadata
    points = Column(Integer, default=1)
    time_limit_seconds = Column(Integer, nullable=True)
    
    # Relationships
    article = relationship("NutritionArticle", back_populates="quiz_questions")
    user_answers = relationship("UserQuizAnswer", back_populates="question")

class UserEducationProgress(Base, TimestampMixin):
    __tablename__ = "user_education_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    article_id = Column(Integer, ForeignKey("nutrition_articles.id"), nullable=True)
    tip_id = Column(Integer, ForeignKey("nutrition_tips.id"), nullable=True)
    
    # Progress tracking
    progress_percentage = Column(Float, default=0.0)
    time_spent_seconds = Column(Integer, default=0)
    is_completed = Column(Boolean, default=False)
    completion_date = Column(DateTime, nullable=True)
    
    # User interaction
    is_bookmarked = Column(Boolean, default=False)
    is_liked = Column(Boolean, default=False)
    rating = Column(Integer, nullable=True)  # 1-5 star rating
    feedback = Column(Text, nullable=True)
    
    # Learning analytics
    last_accessed = Column(DateTime, default=func.now())
    access_count = Column(Integer, default=1)
    
    # Relationships
    user = relationship("User")
    article = relationship("NutritionArticle", back_populates="user_progress")

class UserQuizAnswer(Base, TimestampMixin):
    __tablename__ = "user_quiz_answers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("quiz_questions.id"), nullable=False)
    quiz_session_id = Column(String, nullable=True)  # Group answers from same quiz session
    
    # Answer data
    user_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    time_taken_seconds = Column(Integer, nullable=True)
    points_earned = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User")
    question = relationship("QuizQuestion", back_populates="user_answers")

class UserLearningPath(Base, TimestampMixin):
    __tablename__ = "user_learning_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    path_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Learning path configuration
    target_goals = Column(Text, nullable=True)  # JSON string of user goals
    difficulty_level = Column(Enum(DifficultyLevel), default=DifficultyLevel.BEGINNER)
    estimated_duration_days = Column(Integer, default=30)
    
    # Progress tracking
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer, default=0)
    completion_percentage = Column(Float, default=0.0)
    is_completed = Column(Boolean, default=False)
    completion_date = Column(DateTime, nullable=True)
    
    # Learning path content (JSON string of content IDs in order)
    content_sequence = Column(Text, nullable=False)
    
    # Relationships
    user = relationship("User")

class DailyNutritionTip(Base, TimestampMixin):
    __tablename__ = "daily_nutrition_tips"
    
    id = Column(Integer, primary_key=True, index=True)
    tip_id = Column(Integer, ForeignKey("nutrition_tips.id"), nullable=False)
    date = Column(DateTime, nullable=False, index=True)
    
    # Tip delivery
    is_sent = Column(Boolean, default=False)
    sent_count = Column(Integer, default=0)
    
    # Tip customization
    custom_title = Column(String, nullable=True)
    custom_content = Column(Text, nullable=True)
    
    # Relationships
    tip = relationship("NutritionTip")

class NutritionFact(Base, TimestampMixin):
    __tablename__ = "nutrition_facts"
    
    id = Column(Integer, primary_key=True, index=True)
    fact_text = Column(Text, nullable=False)
    category = Column(Enum(ContentCategory), nullable=False)
    difficulty_level = Column(Enum(DifficultyLevel), default=DifficultyLevel.BEGINNER)
    
    # Fact metadata
    source = Column(String, nullable=True)
    source_url = Column(String, nullable=True)
    fact_type = Column(String, nullable=True)  # "surprising", "myth_busting", "scientific"
    
    # Visual content
    image_url = Column(String, nullable=True)
    infographic_url = Column(String, nullable=True)
    
    # Engagement
    view_count = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    
    # Fact verification
    is_verified = Column(Boolean, default=True)
    verification_date = Column(DateTime, nullable=True)
    verified_by = Column(String, nullable=True)


