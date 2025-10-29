from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class ContentType(str, Enum):
    ARTICLE = "article"
    TIP = "tip"
    QUIZ = "quiz"
    VIDEO = "video"
    INFOGRAPHIC = "infographic"
    RECIPE_TIP = "recipe_tip"
    NUTRITION_FACT = "nutrition_fact"

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class ContentCategory(str, Enum):
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

# Base schemas
class NutritionArticleBase(BaseModel):
    title: str
    slug: str
    summary: Optional[str] = None
    content: str
    content_type: ContentType
    category: ContentCategory
    difficulty_level: DifficultyLevel = DifficultyLevel.BEGINNER
    reading_time_minutes: int = 5
    featured_image_url: Optional[str] = None
    tags: Optional[List[str]] = None
    author: Optional[str] = None
    source_url: Optional[str] = None
    is_published: bool = True
    is_featured: bool = False
    priority: int = 0
    target_audience: Optional[str] = None
    meta_description: Optional[str] = None
    keywords: Optional[List[str]] = None

class NutritionArticleCreate(NutritionArticleBase):
    pass

class NutritionArticleUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    content_type: Optional[ContentType] = None
    category: Optional[ContentCategory] = None
    difficulty_level: Optional[DifficultyLevel] = None
    reading_time_minutes: Optional[int] = None
    featured_image_url: Optional[str] = None
    tags: Optional[List[str]] = None
    author: Optional[str] = None
    source_url: Optional[str] = None
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None
    priority: Optional[int] = None
    target_audience: Optional[str] = None
    meta_description: Optional[str] = None
    keywords: Optional[List[str]] = None

class NutritionArticleResponse(NutritionArticleBase):
    id: int
    view_count: int = 0
    like_count: int = 0
    share_count: int = 0
    bookmark_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NutritionTipBase(BaseModel):
    title: str
    content: str
    category: ContentCategory
    difficulty_level: DifficultyLevel = DifficultyLevel.BEGINNER
    tip_type: Optional[str] = None
    target_goals: Optional[List[str]] = None
    target_dietary_restrictions: Optional[List[str]] = None
    image_url: Optional[str] = None
    icon_name: Optional[str] = None
    is_featured: bool = False
    is_daily_tip: bool = False
    is_seasonal: bool = False
    seasonal_months: Optional[List[int]] = None

class NutritionTipCreate(NutritionTipBase):
    pass

class NutritionTipUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[ContentCategory] = None
    difficulty_level: Optional[DifficultyLevel] = None
    tip_type: Optional[str] = None
    target_goals: Optional[List[str]] = None
    target_dietary_restrictions: Optional[List[str]] = None
    image_url: Optional[str] = None
    icon_name: Optional[str] = None
    is_featured: Optional[bool] = None
    is_daily_tip: Optional[bool] = None
    is_seasonal: Optional[bool] = None
    seasonal_months: Optional[List[int]] = None

class NutritionTipResponse(NutritionTipBase):
    id: int
    view_count: int = 0
    like_count: int = 0
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class QuizQuestionBase(BaseModel):
    article_id: Optional[int] = None
    question_text: str
    question_type: str
    difficulty_level: DifficultyLevel = DifficultyLevel.BEGINNER
    category: ContentCategory
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: Optional[str] = None
    points: int = 1
    time_limit_seconds: Optional[int] = None

class QuizQuestionCreate(QuizQuestionBase):
    pass

class QuizQuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    question_type: Optional[str] = None
    difficulty_level: Optional[DifficultyLevel] = None
    category: Optional[ContentCategory] = None
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    points: Optional[int] = None
    time_limit_seconds: Optional[int] = None

class QuizQuestionResponse(QuizQuestionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserEducationProgressBase(BaseModel):
    article_id: Optional[int] = None
    tip_id: Optional[int] = None
    progress_percentage: float = 0.0
    time_spent_seconds: int = 0
    is_completed: bool = False
    is_bookmarked: bool = False
    is_liked: bool = False
    rating: Optional[int] = Field(None, ge=1, le=5)
    feedback: Optional[str] = None

class UserEducationProgressCreate(UserEducationProgressBase):
    pass

class UserEducationProgressUpdate(BaseModel):
    progress_percentage: Optional[float] = None
    time_spent_seconds: Optional[int] = None
    is_completed: Optional[bool] = None
    is_bookmarked: Optional[bool] = None
    is_liked: Optional[bool] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    feedback: Optional[str] = None

class UserEducationProgressResponse(UserEducationProgressBase):
    id: int
    user_id: str
    completion_date: Optional[datetime] = None
    last_accessed: datetime
    access_count: int = 1
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserQuizAnswerBase(BaseModel):
    question_id: int
    quiz_session_id: Optional[str] = None
    user_answer: str
    time_taken_seconds: Optional[int] = None

class UserQuizAnswerCreate(UserQuizAnswerBase):
    pass

class UserQuizAnswerResponse(UserQuizAnswerBase):
    id: int
    user_id: str
    is_correct: bool
    points_earned: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

class UserLearningPathBase(BaseModel):
    path_name: str
    description: Optional[str] = None
    target_goals: Optional[List[str]] = None
    difficulty_level: DifficultyLevel = DifficultyLevel.BEGINNER
    estimated_duration_days: int = 30
    content_sequence: List[int]

class UserLearningPathCreate(UserLearningPathBase):
    pass

class UserLearningPathUpdate(BaseModel):
    path_name: Optional[str] = None
    description: Optional[str] = None
    target_goals: Optional[List[str]] = None
    difficulty_level: Optional[DifficultyLevel] = None
    estimated_duration_days: Optional[int] = None
    content_sequence: Optional[List[int]] = None

class UserLearningPathResponse(UserLearningPathBase):
    id: int
    user_id: str
    current_step: int = 0
    total_steps: int = 0
    completion_percentage: float = 0.0
    is_completed: bool = False
    completion_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class NutritionFactBase(BaseModel):
    fact_text: str
    category: ContentCategory
    difficulty_level: DifficultyLevel = DifficultyLevel.BEGINNER
    source: Optional[str] = None
    source_url: Optional[str] = None
    fact_type: Optional[str] = None
    image_url: Optional[str] = None
    infographic_url: Optional[str] = None
    is_featured: bool = False
    is_verified: bool = True
    verified_by: Optional[str] = None

class NutritionFactCreate(NutritionFactBase):
    pass

class NutritionFactUpdate(BaseModel):
    fact_text: Optional[str] = None
    category: Optional[ContentCategory] = None
    difficulty_level: Optional[DifficultyLevel] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    fact_type: Optional[str] = None
    image_url: Optional[str] = None
    infographic_url: Optional[str] = None
    is_featured: Optional[bool] = None
    is_verified: Optional[bool] = None
    verified_by: Optional[str] = None

class NutritionFactResponse(NutritionFactBase):
    id: int
    view_count: int = 0
    verification_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Search and filter schemas
class EducationContentSearch(BaseModel):
    query: Optional[str] = None
    category: Optional[ContentCategory] = None
    difficulty_level: Optional[DifficultyLevel] = None
    content_type: Optional[ContentType] = None
    tags: Optional[List[str]] = None
    is_featured: Optional[bool] = None
    is_published: Optional[bool] = True
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

class QuizSessionCreate(BaseModel):
    article_id: Optional[int] = None
    category: Optional[ContentCategory] = None
    difficulty_level: Optional[DifficultyLevel] = None
    question_count: int = Field(10, ge=1, le=50)

class QuizSessionResponse(BaseModel):
    session_id: str
    questions: List[QuizQuestionResponse]
    total_questions: int
    time_limit_seconds: Optional[int] = None

class QuizSubmission(BaseModel):
    session_id: str
    answers: List[UserQuizAnswerCreate]

class QuizResult(BaseModel):
    session_id: str
    total_questions: int
    correct_answers: int
    total_points: int
    percentage: float
    time_taken_seconds: int
    answers: List[UserQuizAnswerResponse]

# Dashboard and analytics schemas
class UserEducationDashboard(BaseModel):
    total_articles_read: int
    total_tips_viewed: int
    total_quizzes_completed: int
    total_points_earned: int
    current_learning_path: Optional[UserLearningPathResponse] = None
    recent_activity: List[UserEducationProgressResponse]
    recommended_content: List[NutritionArticleResponse]
    daily_tip: Optional[NutritionTipResponse] = None

class LearningAnalytics(BaseModel):
    user_id: str
    total_time_spent_minutes: int
    favorite_categories: List[Dict[str, Any]]
    difficulty_progression: Dict[str, int]
    completion_rate: float
    streak_days: int
    achievements: List[str]


