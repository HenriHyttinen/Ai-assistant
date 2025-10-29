from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from typing import List, Optional, Dict, Any
import json
import uuid
from datetime import datetime, timedelta

from models.nutrition_education import (
    NutritionArticle, NutritionTip, QuizQuestion, UserEducationProgress,
    UserQuizAnswer, UserLearningPath, DailyNutritionTip, NutritionFact
)
from schemas.nutrition_education import (
    NutritionArticleCreate, NutritionArticleUpdate, NutritionTipCreate,
    NutritionTipUpdate, QuizQuestionCreate, UserEducationProgressCreate,
    UserEducationProgressUpdate, UserQuizAnswerCreate, UserLearningPathCreate,
    UserLearningPathUpdate, NutritionFactCreate, EducationContentSearch,
    QuizSessionCreate, QuizSubmission, UserEducationDashboard, LearningAnalytics
)

class NutritionEducationService:
    def __init__(self, db: Session):
        self.db = db

    # Article methods
    def create_article(self, article_data: NutritionArticleCreate) -> NutritionArticle:
        """Create a new nutrition article"""
        article = NutritionArticle(
            title=article_data.title,
            slug=article_data.slug,
            summary=article_data.summary,
            content=article_data.content,
            content_type=article_data.content_type,
            category=article_data.category,
            difficulty_level=article_data.difficulty_level,
            reading_time_minutes=article_data.reading_time_minutes,
            featured_image_url=article_data.featured_image_url,
            tags=json.dumps(article_data.tags) if article_data.tags else None,
            author=article_data.author,
            source_url=article_data.source_url,
            is_published=article_data.is_published,
            is_featured=article_data.is_featured,
            priority=article_data.priority,
            target_audience=article_data.target_audience,
            meta_description=article_data.meta_description,
            keywords=json.dumps(article_data.keywords) if article_data.keywords else None
        )
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return article

    def get_article(self, article_id: int) -> Optional[NutritionArticle]:
        """Get a nutrition article by ID"""
        return self.db.query(NutritionArticle).filter(NutritionArticle.id == article_id).first()

    def get_article_by_slug(self, slug: str) -> Optional[NutritionArticle]:
        """Get a nutrition article by slug"""
        return self.db.query(NutritionArticle).filter(NutritionArticle.slug == slug).first()

    def get_articles(self, search_params: EducationContentSearch) -> List[NutritionArticle]:
        """Get articles with search and filter parameters"""
        query = self.db.query(NutritionArticle)
        
        if search_params.query:
            query = query.filter(
                or_(
                    NutritionArticle.title.ilike(f"%{search_params.query}%"),
                    NutritionArticle.summary.ilike(f"%{search_params.query}%"),
                    NutritionArticle.content.ilike(f"%{search_params.query}%")
                )
            )
        
        if search_params.category:
            query = query.filter(NutritionArticle.category == search_params.category)
        
        if search_params.difficulty_level:
            query = query.filter(NutritionArticle.difficulty_level == search_params.difficulty_level)
        
        if search_params.content_type:
            query = query.filter(NutritionArticle.content_type == search_params.content_type)
        
        if search_params.is_featured is not None:
            query = query.filter(NutritionArticle.is_featured == search_params.is_featured)
        
        if search_params.is_published is not None:
            query = query.filter(NutritionArticle.is_published == search_params.is_published)
        
        if search_params.tags:
            for tag in search_params.tags:
                query = query.filter(NutritionArticle.tags.ilike(f"%{tag}%"))
        
        query = query.order_by(desc(NutritionArticle.priority), desc(NutritionArticle.created_at))
        
        return query.offset(search_params.offset).limit(search_params.limit).all()

    def update_article(self, article_id: int, article_data: NutritionArticleUpdate) -> Optional[NutritionArticle]:
        """Update a nutrition article"""
        article = self.get_article(article_id)
        if not article:
            return None
        
        update_data = article_data.dict(exclude_unset=True)
        
        # Handle JSON fields
        if 'tags' in update_data and update_data['tags'] is not None:
            update_data['tags'] = json.dumps(update_data['tags'])
        if 'keywords' in update_data and update_data['keywords'] is not None:
            update_data['keywords'] = json.dumps(update_data['keywords'])
        
        for field, value in update_data.items():
            setattr(article, field, value)
        
        self.db.commit()
        self.db.refresh(article)
        return article

    def delete_article(self, article_id: int) -> bool:
        """Delete a nutrition article"""
        article = self.get_article(article_id)
        if not article:
            return False
        
        self.db.delete(article)
        self.db.commit()
        return True

    def increment_article_views(self, article_id: int) -> None:
        """Increment article view count"""
        article = self.get_article(article_id)
        if article:
            article.view_count += 1
            self.db.commit()

    # Tip methods
    def create_tip(self, tip_data: NutritionTipCreate) -> NutritionTip:
        """Create a new nutrition tip"""
        tip = NutritionTip(
            title=tip_data.title,
            content=tip_data.content,
            category=tip_data.category,
            difficulty_level=tip_data.difficulty_level,
            tip_type=tip_data.tip_type,
            target_goals=json.dumps(tip_data.target_goals) if tip_data.target_goals else None,
            target_dietary_restrictions=json.dumps(tip_data.target_dietary_restrictions) if tip_data.target_dietary_restrictions else None,
            image_url=tip_data.image_url,
            icon_name=tip_data.icon_name,
            is_featured=tip_data.is_featured,
            is_daily_tip=tip_data.is_daily_tip,
            is_seasonal=tip_data.is_seasonal,
            seasonal_months=json.dumps(tip_data.seasonal_months) if tip_data.seasonal_months else None
        )
        self.db.add(tip)
        self.db.commit()
        self.db.refresh(tip)
        return tip

    def get_tip(self, tip_id: int) -> Optional[NutritionTip]:
        """Get a nutrition tip by ID"""
        return self.db.query(NutritionTip).filter(NutritionTip.id == tip_id).first()

    def get_daily_tip(self, user_id: str, target_goals: List[str] = None) -> Optional[NutritionTip]:
        """Get today's nutrition tip for a user"""
        today = datetime.now().date()
        
        # Try to get a tip that matches user goals
        if target_goals:
            for goal in target_goals:
                tip = self.db.query(NutritionTip).filter(
                    and_(
                        NutritionTip.is_daily_tip == True,
                        NutritionTip.target_goals.ilike(f"%{goal}%")
                    )
                ).first()
                if tip:
                    return tip
        
        # Fallback to any daily tip
        tip = self.db.query(NutritionTip).filter(NutritionTip.is_daily_tip == True).first()
        return tip

    def get_tips(self, category: Optional[str] = None, limit: int = 20) -> List[NutritionTip]:
        """Get nutrition tips with optional filtering"""
        query = self.db.query(NutritionTip)
        
        if category:
            query = query.filter(NutritionTip.category == category)
        
        return query.order_by(desc(NutritionTip.is_featured), desc(NutritionTip.created_at)).limit(limit).all()

    # Quiz methods
    def create_quiz_question(self, question_data: QuizQuestionCreate) -> QuizQuestion:
        """Create a new quiz question"""
        question = QuizQuestion(
            article_id=question_data.article_id,
            question_text=question_data.question_text,
            question_type=question_data.question_type,
            difficulty_level=question_data.difficulty_level,
            category=question_data.category,
            options=json.dumps(question_data.options) if question_data.options else None,
            correct_answer=question_data.correct_answer,
            explanation=question_data.explanation,
            points=question_data.points,
            time_limit_seconds=question_data.time_limit_seconds
        )
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def create_quiz_session(self, session_data: QuizSessionCreate) -> Dict[str, Any]:
        """Create a quiz session with questions"""
        session_id = str(uuid.uuid4())
        
        query = self.db.query(QuizQuestion)
        
        if session_data.article_id:
            query = query.filter(QuizQuestion.article_id == session_data.article_id)
        
        if session_data.category:
            query = query.filter(QuizQuestion.category == session_data.category)
        
        if session_data.difficulty_level:
            query = query.filter(QuizQuestion.difficulty_level == session_data.difficulty_level)
        
        questions = query.order_by(func.random()).limit(session_data.question_count).all()
        
        return {
            "session_id": session_id,
            "questions": questions,
            "total_questions": len(questions),
            "time_limit_seconds": max([q.time_limit_seconds for q in questions if q.time_limit_seconds]) if questions else None
        }

    def submit_quiz_answers(self, user_id: str, submission: QuizSubmission) -> Dict[str, Any]:
        """Submit quiz answers and calculate results"""
        total_questions = len(submission.answers)
        correct_answers = 0
        total_points = 0
        answers = []
        
        for answer_data in submission.answers:
            question = self.db.query(QuizQuestion).filter(QuizQuestion.id == answer_data.question_id).first()
            if not question:
                continue
            
            is_correct = answer_data.user_answer.strip().lower() == question.correct_answer.strip().lower()
            points_earned = question.points if is_correct else 0
            
            if is_correct:
                correct_answers += 1
                total_points += points_earned
            
            # Save user answer
            user_answer = UserQuizAnswer(
                user_id=user_id,
                question_id=answer_data.question_id,
                quiz_session_id=submission.session_id,
                user_answer=answer_data.user_answer,
                is_correct=is_correct,
                time_taken_seconds=answer_data.time_taken_seconds,
                points_earned=points_earned
            )
            self.db.add(user_answer)
            answers.append(user_answer)
        
        self.db.commit()
        
        percentage = (correct_answers / total_questions * 100) if total_questions > 0 else 0
        
        return {
            "session_id": submission.session_id,
            "total_questions": total_questions,
            "correct_answers": correct_answers,
            "total_points": total_points,
            "percentage": percentage,
            "time_taken_seconds": sum([a.time_taken_seconds for a in answers if a.time_taken_seconds]),
            "answers": answers
        }

    # User progress methods
    def update_user_progress(self, user_id: str, progress_data: UserEducationProgressCreate) -> UserEducationProgress:
        """Update user education progress"""
        # Check if progress already exists
        existing_progress = self.db.query(UserEducationProgress).filter(
            and_(
                UserEducationProgress.user_id == user_id,
                UserEducationProgress.article_id == progress_data.article_id,
                UserEducationProgress.tip_id == progress_data.tip_id
            )
        ).first()
        
        if existing_progress:
            # Update existing progress
            update_data = progress_data.dict(exclude_unset=True)
            for field, value in update_data.items():
                setattr(existing_progress, field, value)
            
            existing_progress.last_accessed = datetime.now()
            existing_progress.access_count += 1
            
            if progress_data.is_completed and not existing_progress.is_completed:
                existing_progress.completion_date = datetime.now()
            
            self.db.commit()
            self.db.refresh(existing_progress)
            return existing_progress
        else:
            # Create new progress
            progress = UserEducationProgress(
                user_id=user_id,
                article_id=progress_data.article_id,
                tip_id=progress_data.tip_id,
                progress_percentage=progress_data.progress_percentage,
                time_spent_seconds=progress_data.time_spent_seconds,
                is_completed=progress_data.is_completed,
                is_bookmarked=progress_data.is_bookmarked,
                is_liked=progress_data.is_liked,
                rating=progress_data.rating,
                feedback=progress_data.feedback
            )
            
            if progress_data.is_completed:
                progress.completion_date = datetime.now()
            
            self.db.add(progress)
            self.db.commit()
            self.db.refresh(progress)
            return progress

    def get_user_dashboard(self, user_id: str) -> UserEducationDashboard:
        """Get user education dashboard data"""
        # Get user progress statistics
        progress_stats = self.db.query(
            func.count(UserEducationProgress.id).label('total_articles_read'),
            func.sum(UserEducationProgress.time_spent_seconds).label('total_time_spent')
        ).filter(
            and_(
                UserEducationProgress.user_id == user_id,
                UserEducationProgress.article_id.isnot(None)
            )
        ).first()
        
        tips_viewed = self.db.query(func.count(UserEducationProgress.id)).filter(
            and_(
                UserEducationProgress.user_id == user_id,
                UserEducationProgress.tip_id.isnot(None)
            )
        ).scalar() or 0
        
        quizzes_completed = self.db.query(func.count(func.distinct(UserQuizAnswer.quiz_session_id))).filter(
            UserQuizAnswer.user_id == user_id
        ).scalar() or 0
        
        total_points = self.db.query(func.sum(UserQuizAnswer.points_earned)).filter(
            UserQuizAnswer.user_id == user_id
        ).scalar() or 0
        
        # Get recent activity
        recent_activity = self.db.query(UserEducationProgress).filter(
            UserEducationProgress.user_id == user_id
        ).order_by(desc(UserEducationProgress.last_accessed)).limit(5).all()
        
        # Get recommended content (featured articles)
        recommended_content = self.db.query(NutritionArticle).filter(
            and_(
                NutritionArticle.is_published == True,
                NutritionArticle.is_featured == True
            )
        ).limit(3).all()
        
        # Get daily tip
        daily_tip = self.get_daily_tip(user_id)
        
        # Get current learning path
        current_learning_path = self.db.query(UserLearningPath).filter(
            and_(
                UserLearningPath.user_id == user_id,
                UserLearningPath.is_completed == False
            )
        ).first()
        
        return UserEducationDashboard(
            total_articles_read=progress_stats.total_articles_read or 0,
            total_tips_viewed=tips_viewed,
            total_quizzes_completed=quizzes_completed,
            total_points_earned=total_points,
            current_learning_path=current_learning_path,
            recent_activity=recent_activity,
            recommended_content=recommended_content,
            daily_tip=daily_tip
        )

    def get_learning_analytics(self, user_id: str) -> LearningAnalytics:
        """Get user learning analytics"""
        # Calculate total time spent
        total_time = self.db.query(func.sum(UserEducationProgress.time_spent_seconds)).filter(
            UserEducationProgress.user_id == user_id
        ).scalar() or 0
        
        # Get favorite categories
        category_stats = self.db.query(
            NutritionArticle.category,
            func.count(NutritionArticle.id).label('count')
        ).join(UserEducationProgress).filter(
            UserEducationProgress.user_id == user_id
        ).group_by(NutritionArticle.category).all()
        
        favorite_categories = [{"category": cat, "count": count} for cat, count in category_stats]
        
        # Calculate completion rate
        total_started = self.db.query(func.count(UserEducationProgress.id)).filter(
            UserEducationProgress.user_id == user_id
        ).scalar() or 0
        
        total_completed = self.db.query(func.count(UserEducationProgress.id)).filter(
            and_(
                UserEducationProgress.user_id == user_id,
                UserEducationProgress.is_completed == True
            )
        ).scalar() or 0
        
        completion_rate = (total_completed / total_started * 100) if total_started > 0 else 0
        
        return LearningAnalytics(
            user_id=user_id,
            total_time_spent_minutes=total_time // 60,
            favorite_categories=favorite_categories,
            difficulty_progression={},  # TODO: Implement difficulty progression tracking
            completion_rate=completion_rate,
            streak_days=0,  # TODO: Implement streak calculation
            achievements=[]  # TODO: Implement achievements
        )

    # Nutrition facts methods
    def create_nutrition_fact(self, fact_data: NutritionFactCreate) -> NutritionFact:
        """Create a new nutrition fact"""
        fact = NutritionFact(
            fact_text=fact_data.fact_text,
            category=fact_data.category,
            difficulty_level=fact_data.difficulty_level,
            source=fact_data.source,
            source_url=fact_data.source_url,
            fact_type=fact_data.fact_type,
            image_url=fact_data.image_url,
            infographic_url=fact_data.infographic_url,
            is_featured=fact_data.is_featured,
            is_verified=fact_data.is_verified,
            verified_by=fact_data.verified_by
        )
        self.db.add(fact)
        self.db.commit()
        self.db.refresh(fact)
        return fact

    def get_random_nutrition_fact(self, category: Optional[str] = None) -> Optional[NutritionFact]:
        """Get a random nutrition fact"""
        query = self.db.query(NutritionFact).filter(NutritionFact.is_verified == True)
        
        if category:
            query = query.filter(NutritionFact.category == category)
        
        return query.order_by(func.random()).first()

    def get_featured_facts(self, limit: int = 5) -> List[NutritionFact]:
        """Get featured nutrition facts"""
        return self.db.query(NutritionFact).filter(
            and_(
                NutritionFact.is_featured == True,
                NutritionFact.is_verified == True
            )
        ).limit(limit).all()


