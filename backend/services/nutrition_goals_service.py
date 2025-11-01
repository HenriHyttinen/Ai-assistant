from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, desc, asc, and_, or_
from models.nutrition_goals import (
    NutritionGoal, GoalProgressLog, GoalMilestone, GoalTemplate,
    GoalType, GoalStatus, GoalFrequency
)
from models.user import User
from schemas.nutrition_goals import (
    NutritionGoalCreate, NutritionGoalUpdate, NutritionGoalResponse,
    GoalProgressLogCreate, GoalProgressLogUpdate, GoalProgressLogResponse,
    GoalMilestoneCreate, GoalMilestoneUpdate, GoalMilestoneResponse,
    GoalTemplateCreate, GoalTemplateResponse,
    GoalSummary, GoalProgressSummary, GoalDashboard,
    GoalFilter, GoalSearch, GoalAnalytics, GoalInsights
)
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import math

class NutritionGoalsService:
    
    # Goal CRUD operations
    def create_goal(self, db: Session, user_id: str, goal_data: NutritionGoalCreate) -> NutritionGoalResponse:
        """Create a new nutrition goal for a user"""
        db_goal = NutritionGoal(
            user_id=user_id,
            **goal_data.model_dump()
        )
        db.add(db_goal)
        db.commit()
        db.refresh(db_goal)
        
        # Create automatic milestones
        self._create_automatic_milestones(db, db_goal)
        
        return self._format_goal_response(db, db_goal)
    
    def get_goal(self, db: Session, goal_id: int, user_id: str) -> Optional[NutritionGoalResponse]:
        """Get a specific goal by ID"""
        goal = db.query(NutritionGoal).filter(
            NutritionGoal.id == goal_id,
            NutritionGoal.user_id == user_id
        ).first()
        return self._format_goal_response(db, goal) if goal else None
    
    def get_user_goals(self, db: Session, user_id: str, search_params: GoalSearch) -> List[NutritionGoalResponse]:
        """Get all goals for a user with filtering and sorting"""
        query = db.query(NutritionGoal).filter(NutritionGoal.user_id == user_id)
        
        # Apply filters
        if search_params.filters:
            filters = search_params.filters
            if filters.status:
                query = query.filter(NutritionGoal.status == filters.status)
            if filters.goal_type:
                query = query.filter(NutritionGoal.goal_type == filters.goal_type)
            if filters.frequency:
                query = query.filter(NutritionGoal.frequency == filters.frequency)
            if filters.priority:
                query = query.filter(NutritionGoal.priority == filters.priority)
            if filters.is_public is not None:
                query = query.filter(NutritionGoal.is_public == filters.is_public)
            if filters.start_date_from:
                query = query.filter(NutritionGoal.start_date >= filters.start_date_from)
            if filters.start_date_to:
                query = query.filter(NutritionGoal.start_date <= filters.start_date_to)
            if filters.target_date_from:
                query = query.filter(NutritionGoal.target_date >= filters.target_date_from)
            if filters.target_date_to:
                query = query.filter(NutritionGoal.target_date <= filters.target_date_to)
        
        # Apply text search
        if search_params.query:
            query = query.filter(
                or_(
                    NutritionGoal.goal_name.ilike(f"%{search_params.query}%"),
                    NutritionGoal.description.ilike(f"%{search_params.query}%")
                )
            )
        
        # Apply sorting
        sort_column = getattr(NutritionGoal, search_params.sort_by)
        if search_params.sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Apply pagination
        goals = query.offset(search_params.offset).limit(search_params.limit).all()
        return [self._format_goal_response(db, goal) for goal in goals]
    
    def update_goal(self, db: Session, goal_id: int, user_id: str, goal_data: NutritionGoalUpdate) -> Optional[NutritionGoalResponse]:
        """Update a goal"""
        goal = db.query(NutritionGoal).filter(
            NutritionGoal.id == goal_id,
            NutritionGoal.user_id == user_id
        ).first()
        
        if not goal:
            return None
        
        # Update fields
        for key, value in goal_data.model_dump(exclude_unset=True).items():
            setattr(goal, key, value)
        
        # Recalculate progress if target value changed
        if goal_data.target_value is not None:
            self._recalculate_goal_progress(db, goal)
        
        db.add(goal)
        db.commit()
        db.refresh(goal)
        
        return self._format_goal_response(db, goal)
    
    def delete_goal(self, db: Session, goal_id: int, user_id: str) -> bool:
        """Delete a goal and all related data"""
        goal = db.query(NutritionGoal).filter(
            NutritionGoal.id == goal_id,
            NutritionGoal.user_id == user_id
        ).first()
        
        if not goal:
            return False
        
        db.delete(goal)
        db.commit()
        return True
    
    # Progress tracking
    def log_progress(self, db: Session, user_id: str, progress_data: GoalProgressLogCreate) -> GoalProgressLogResponse:
        """Log progress for a goal on a specific date"""
        goal = db.query(NutritionGoal).filter(
            NutritionGoal.id == progress_data.goal_id,
            NutritionGoal.user_id == user_id
        ).first()
        
        if not goal:
            raise ValueError("Goal not found")
        
        # Check if progress already exists for this date
        existing_log = db.query(GoalProgressLog).filter(
            GoalProgressLog.goal_id == progress_data.goal_id,
            GoalProgressLog.date == progress_data.date
        ).first()
        
        if existing_log:
            # Update existing log
            for key, value in progress_data.model_dump(exclude_unset=True).items():
                setattr(existing_log, key, value)
            db_log = existing_log
        else:
            # Create new log
            db_log = GoalProgressLog(
                user_id=user_id,
                **progress_data.model_dump()
            )
            db.add(db_log)
        
        # Calculate progress metrics
        db_log.target_value = goal.target_value
        db_log.is_achieved = db_log.achieved_value >= goal.target_value
        db_log.progress_percentage = min((db_log.achieved_value / goal.target_value) * 100, 100)
        
        db.commit()
        db.refresh(db_log)
        
        # Update goal progress
        self._update_goal_progress(db, goal)
        
        return self._format_progress_log_response(db_log)
    
    def get_goal_progress(self, db: Session, goal_id: int, user_id: str, days: int = 30) -> List[GoalProgressLogResponse]:
        """Get progress history for a goal"""
        goal = db.query(NutritionGoal).filter(
            NutritionGoal.id == goal_id,
            NutritionGoal.user_id == user_id
        ).first()
        
        if not goal:
            return []
        
        start_date = datetime.now() - timedelta(days=days)
        progress_logs = db.query(GoalProgressLog).filter(
            GoalProgressLog.goal_id == goal_id,
            GoalProgressLog.date >= start_date
        ).order_by(GoalProgressLog.date.desc()).all()
        
        return [self._format_progress_log_response(log) for log in progress_logs]
    
    # Milestones
    def create_milestone(self, db: Session, user_id: str, milestone_data: GoalMilestoneCreate) -> GoalMilestoneResponse:
        """Create a milestone for a goal"""
        goal = db.query(NutritionGoal).filter(
            NutritionGoal.id == milestone_data.goal_id,
            NutritionGoal.user_id == user_id
        ).first()
        
        if not goal:
            raise ValueError("Goal not found")
        
        db_milestone = GoalMilestone(
            user_id=user_id,
            **milestone_data.model_dump()
        )
        db.add(db_milestone)
        db.commit()
        db.refresh(db_milestone)
        
        return self._format_milestone_response(db_milestone)
    
    def check_milestones(self, db: Session, goal_id: int) -> List[GoalMilestoneResponse]:
        """Check and update milestone achievements"""
        goal = db.query(NutritionGoal).filter(NutritionGoal.id == goal_id).first()
        if not goal:
            return []
        
        milestones = db.query(GoalMilestone).filter(
            GoalMilestone.goal_id == goal_id,
            GoalMilestone.is_achieved == False
        ).all()
        
        achieved_milestones = []
        for milestone in milestones:
            if goal.current_value >= milestone.target_value:
                milestone.is_achieved = True
                milestone.achieved_date = datetime.now()
                milestone.achieved_value = goal.current_value
                achieved_milestones.append(self._format_milestone_response(milestone))
        
        db.commit()
        return achieved_milestones
    
    # Dashboard and analytics
    def get_goal_dashboard(self, db: Session, user_id: str) -> GoalDashboard:
        """Get comprehensive goal dashboard data"""
        goals = db.query(NutritionGoal).filter(NutritionGoal.user_id == user_id).all()
        
        # Calculate summary
        summary = self._calculate_goal_summary(db, user_id, goals)
        
        # Get active goals with progress
        active_goals = [g for g in goals if g.status == GoalStatus.ACTIVE]
        active_goal_summaries = [self._format_goal_progress_summary(db, goal) for goal in active_goals]
        
        # Get recent achievements
        recent_achievements = db.query(GoalProgressLog).filter(
            GoalProgressLog.user_id == user_id,
            GoalProgressLog.is_achieved == True
        ).order_by(GoalProgressLog.date.desc()).limit(5).all()
        
        # Get upcoming milestones
        upcoming_milestones = db.query(GoalMilestone).join(NutritionGoal).filter(
            NutritionGoal.user_id == user_id,
            GoalMilestone.is_achieved == False
        ).order_by(GoalMilestone.target_value.asc()).limit(5).all()
        
        # Get streak leaderboard
        streak_leaderboard = db.query(NutritionGoal).filter(
            NutritionGoal.user_id == user_id,
            NutritionGoal.status == GoalStatus.ACTIVE
        ).order_by(desc(NutritionGoal.streak_days)).limit(5).all()
        
        return GoalDashboard(
            summary=summary,
            active_goals=active_goal_summaries,
            recent_achievements=[self._format_progress_log_response(log) for log in recent_achievements],
            upcoming_milestones=[self._format_milestone_response(milestone) for milestone in upcoming_milestones],
            streak_leaderboard=[{
                "goal_name": goal.goal_name,
                "streak_days": goal.streak_days,
                "goal_type": goal.goal_type
            } for goal in streak_leaderboard]
        )
    
    def get_goal_analytics(self, db: Session, goal_id: int, user_id: str) -> Optional[GoalAnalytics]:
        """Get detailed analytics for a specific goal"""
        goal = db.query(NutritionGoal).filter(
            NutritionGoal.id == goal_id,
            NutritionGoal.user_id == user_id
        ).first()
        
        if not goal:
            return None
        
        # Get progress logs
        progress_logs = db.query(GoalProgressLog).filter(
            GoalProgressLog.goal_id == goal_id
        ).order_by(GoalProgressLog.date.asc()).all()
        
        # Calculate analytics
        total_days = len(progress_logs)
        days_achieved = len([log for log in progress_logs if log.is_achieved])
        achievement_rate = (days_achieved / total_days * 100) if total_days > 0 else 0
        
        # Calculate trend
        if len(progress_logs) >= 7:
            recent_avg = sum([log.progress_percentage for log in progress_logs[-7:]]) / 7
            earlier_avg = sum([log.progress_percentage for log in progress_logs[-14:-7]]) / 7 if len(progress_logs) >= 14 else recent_avg
            trend_direction = "improving" if recent_avg > earlier_avg else "declining" if recent_avg < earlier_avg else "stable"
        else:
            trend_direction = "stable"
        
        # Weekly and monthly progress
        weekly_progress = self._calculate_weekly_progress(progress_logs)
        monthly_progress = self._calculate_monthly_progress(progress_logs)
        
        # Milestone data
        milestones = db.query(GoalMilestone).filter(GoalMilestone.goal_id == goal_id).all()
        milestone_achievements = len([m for m in milestones if m.is_achieved])
        
        return GoalAnalytics(
            goal_id=goal.id,
            goal_name=goal.goal_name,
            goal_type=goal.goal_type,
            total_days=total_days,
            days_achieved=days_achieved,
            achievement_rate=achievement_rate,
            current_streak=goal.streak_days,
            best_streak=goal.best_streak,
            average_progress=sum([log.progress_percentage for log in progress_logs]) / total_days if total_days > 0 else 0,
            trend_direction=trend_direction,
            weekly_progress=weekly_progress,
            monthly_progress=monthly_progress,
            milestone_achievements=milestone_achievements,
            total_milestones=len(milestones)
        )
    
    # Template management
    def get_goal_templates(self, db: Session, category: Optional[str] = None) -> List[GoalTemplateResponse]:
        """Get available goal templates"""
        query = db.query(GoalTemplate).filter(GoalTemplate.is_public == True)
        
        if category:
            query = query.filter(GoalTemplate.category == category)
        
        templates = query.order_by(desc(GoalTemplate.usage_count)).all()
        return [self._format_template_response(template) for template in templates]
    
    def create_goal_from_template(self, db: Session, user_id: str, template_id: int, customizations: Optional[Dict] = None) -> NutritionGoalResponse:
        """Create a goal from a template"""
        template = db.query(GoalTemplate).filter(GoalTemplate.id == template_id).first()
        if not template:
            raise ValueError("Template not found")
        
        # Create goal from template
        goal_data = NutritionGoalCreate(
            goal_type=template.goal_type,
            goal_name=template.name,
            description=template.description,
            target_value=template.default_target_value,
            unit=template.default_unit,
            frequency=template.default_frequency,
            start_date=datetime.now(),
            target_date=datetime.now() + timedelta(days=template.default_duration_days) if template.default_duration_days else None
        )
        
        # Apply customizations
        if customizations:
            for key, value in customizations.items():
                if hasattr(goal_data, key):
                    setattr(goal_data, key, value)
        
        # Increment template usage
        template.usage_count += 1
        db.add(template)
        
        return self.create_goal(db, user_id, goal_data)
    
    # Helper methods
    def _create_automatic_milestones(self, db: Session, goal: NutritionGoal):
        """Create automatic milestones for a goal"""
        milestones = [
            (0.25, f"25% of {goal.goal_name}"),
            (0.5, f"50% of {goal.goal_name}"),
            (0.75, f"75% of {goal.goal_name}"),
            (1.0, f"Complete {goal.goal_name}")
        ]
        
        for percentage, name in milestones:
            milestone = GoalMilestone(
                goal_id=goal.id,
                user_id=goal.user_id,
                milestone_name=name,
                target_value=goal.target_value * percentage,
                is_automatic=True
            )
            db.add(milestone)
        
        db.commit()
    
    def _update_goal_progress(self, db: Session, goal: NutritionGoal):
        """Update goal progress metrics"""
        # Get recent progress logs
        recent_logs = db.query(GoalProgressLog).filter(
            GoalProgressLog.goal_id == goal.id
        ).order_by(GoalProgressLog.date.desc()).all()
        
        if not recent_logs:
            return
        
        # Update current value (most recent)
        goal.current_value = recent_logs[0].achieved_value
        
        # Calculate progress percentage
        goal.progress_percentage = min((goal.current_value / goal.target_value) * 100, 100)
        
        # Calculate days achieved and streak
        days_achieved = len([log for log in recent_logs if log.is_achieved])
        goal.days_achieved = days_achieved
        goal.total_days = len(recent_logs)
        
        # Calculate current streak
        current_streak = 0
        for log in recent_logs:
            if log.is_achieved:
                current_streak += 1
            else:
                break
        
        goal.streak_days = current_streak
        goal.best_streak = max(goal.best_streak, current_streak)
        
        # Update status
        if goal.progress_percentage >= 100:
            goal.status = GoalStatus.COMPLETED
        
        db.add(goal)
        db.commit()
    
    def _recalculate_goal_progress(self, db: Session, goal: NutritionGoal):
        """Recalculate goal progress after target value change"""
        self._update_goal_progress(db, goal)
    
    def _calculate_goal_summary(self, db: Session, user_id: str, goals: List[NutritionGoal]) -> GoalSummary:
        """Calculate goal summary statistics"""
        total_goals = len(goals)
        active_goals = len([g for g in goals if g.status == GoalStatus.ACTIVE])
        completed_goals = len([g for g in goals if g.status == GoalStatus.COMPLETED])
        paused_goals = len([g for g in goals if g.status == GoalStatus.PAUSED])
        
        total_streak_days = sum([g.streak_days for g in goals if g.status == GoalStatus.ACTIVE])
        best_streak = max([g.best_streak for g in goals], default=0)
        
        # Goals achieved today
        today = datetime.now().date()
        goals_achieved_today = len([
            g for g in goals if g.status == GoalStatus.ACTIVE and 
            any(log.date.date() == today and log.is_achieved for log in g.progress_logs)
        ])
        
        # Goals on track (progress >= 80% of expected)
        goals_on_track = len([
            g for g in goals if g.status == GoalStatus.ACTIVE and g.progress_percentage >= 80
        ])
        
        goals_behind = active_goals - goals_on_track
        
        return GoalSummary(
            total_goals=total_goals,
            active_goals=active_goals,
            completed_goals=completed_goals,
            paused_goals=paused_goals,
            total_streak_days=total_streak_days,
            best_streak=best_streak,
            goals_achieved_today=goals_achieved_today,
            goals_on_track=goals_on_track,
            goals_behind=goals_behind
        )
    
    def _format_goal_response(self, db: Session, goal: NutritionGoal) -> Optional[NutritionGoalResponse]:
        """Format goal for API response"""
        if not goal:
            return None
        
        # Load related data
        progress_logs = db.query(GoalProgressLog).filter(GoalProgressLog.goal_id == goal.id).all()
        milestones = db.query(GoalMilestone).filter(GoalMilestone.goal_id == goal.id).all()
        
        return NutritionGoalResponse(
            id=goal.id,
            user_id=goal.user_id,
            goal_type=goal.goal_type,
            goal_name=goal.goal_name,
            description=goal.description,
            target_value=goal.target_value,
            current_value=goal.current_value,
            unit=goal.unit,
            frequency=goal.frequency,
            start_date=goal.start_date,
            target_date=goal.target_date,
            is_flexible=goal.is_flexible,
            status=goal.status,
            priority=goal.priority,
            is_public=goal.is_public,
            progress_percentage=goal.progress_percentage,
            days_achieved=goal.days_achieved,
            total_days=goal.total_days,
            streak_days=goal.streak_days,
            best_streak=goal.best_streak,
            created_at=goal.created_at,
            updated_at=goal.updated_at,
            progress_logs=[self._format_progress_log_response(log) for log in progress_logs],
            milestones=[self._format_milestone_response(milestone) for milestone in milestones]
        )
    
    def _format_progress_log_response(self, log: GoalProgressLog) -> GoalProgressLogResponse:
        """Format progress log for API response"""
        return GoalProgressLogResponse(
            id=log.id,
            goal_id=log.goal_id,
            user_id=log.user_id,
            date=log.date,
            achieved_value=log.achieved_value,
            target_value=log.target_value,
            is_achieved=log.is_achieved,
            progress_percentage=log.progress_percentage,
            notes=log.notes,
            difficulty_rating=log.difficulty_rating,
            mood_rating=log.mood_rating,
            created_at=log.created_at,
            updated_at=log.updated_at
        )
    
    def _format_milestone_response(self, milestone: GoalMilestone) -> GoalMilestoneResponse:
        """Format milestone for API response"""
        return GoalMilestoneResponse(
            id=milestone.id,
            goal_id=milestone.goal_id,
            user_id=milestone.user_id,
            milestone_name=milestone.milestone_name,
            description=milestone.description,
            target_value=milestone.target_value,
            achieved_value=milestone.achieved_value,
            is_achieved=milestone.is_achieved,
            achieved_date=milestone.achieved_date,
            is_automatic=milestone.is_automatic,
            reward_description=milestone.reward_description,
            created_at=milestone.created_at,
            updated_at=milestone.updated_at
        )
    
    def _format_template_response(self, template: GoalTemplate) -> GoalTemplateResponse:
        """Format template for API response"""
        return GoalTemplateResponse(
            id=template.id,
            name=template.name,
            description=template.description,
            goal_type=template.goal_type,
            default_target_value=template.default_target_value,
            default_unit=template.default_unit,
            default_frequency=template.default_frequency,
            default_duration_days=template.default_duration_days,
            category=template.category,
            difficulty_level=template.difficulty_level,
            is_public=template.is_public,
            usage_count=template.usage_count,
            instructions=template.instructions,
            tips=template.tips,
            common_challenges=template.common_challenges,
            success_metrics=template.success_metrics,
            created_at=template.created_at,
            updated_at=template.updated_at
        )
    
    def _format_goal_progress_summary(self, db: Session, goal: NutritionGoal) -> GoalProgressSummary:
        """Format goal progress summary for dashboard"""
        # Get next milestone
        next_milestone = db.query(GoalMilestone).filter(
            GoalMilestone.goal_id == goal.id,
            GoalMilestone.is_achieved == False
        ).order_by(GoalMilestone.target_value.asc()).first()
        
        # Calculate days remaining
        days_remaining = None
        if goal.target_date:
            days_remaining = (goal.target_date - datetime.now()).days
        
        # Check if on track
        is_on_track = goal.progress_percentage >= 80
        
        # Get last achieved date
        last_achieved = db.query(GoalProgressLog).filter(
            GoalProgressLog.goal_id == goal.id,
            GoalProgressLog.is_achieved == True
        ).order_by(GoalProgressLog.date.desc()).first()
        
        return GoalProgressSummary(
            goal_id=goal.id,
            goal_name=goal.goal_name,
            goal_type=goal.goal_type,
            target_value=goal.target_value,
            current_value=goal.current_value,
            progress_percentage=goal.progress_percentage,
            status=goal.status,
            streak_days=goal.streak_days,
            days_remaining=days_remaining,
            is_on_track=is_on_track,
            last_achieved=last_achieved.date if last_achieved else None,
            next_milestone=self._format_milestone_response(next_milestone) if next_milestone else None
        )
    
    def _calculate_weekly_progress(self, progress_logs: List[GoalProgressLog]) -> List[dict]:
        """Calculate weekly progress data"""
        # Group logs by week
        weekly_data = {}
        for log in progress_logs:
            week_start = log.date - timedelta(days=log.date.weekday())
            week_key = week_start.strftime("%Y-%W")
            
            if week_key not in weekly_data:
                weekly_data[week_key] = {
                    "week_start": week_start,
                    "total_progress": 0,
                    "days_achieved": 0,
                    "total_days": 0
                }
            
            weekly_data[week_key]["total_progress"] += log.progress_percentage
            weekly_data[week_key]["total_days"] += 1
            if log.is_achieved:
                weekly_data[week_key]["days_achieved"] += 1
        
        # Format for response
        return [
            {
                "week_start": data["week_start"].isoformat(),
                "average_progress": data["total_progress"] / data["total_days"] if data["total_days"] > 0 else 0,
                "days_achieved": data["days_achieved"],
                "total_days": data["total_days"]
            }
            for data in weekly_data.values()
        ]
    
    def _calculate_monthly_progress(self, progress_logs: List[GoalProgressLog]) -> List[dict]:
        """Calculate monthly progress data"""
        # Group logs by month
        monthly_data = {}
        for log in progress_logs:
            month_key = log.date.strftime("%Y-%m")
            
            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    "month": month_key,
                    "total_progress": 0,
                    "days_achieved": 0,
                    "total_days": 0
                }
            
            monthly_data[month_key]["total_progress"] += log.progress_percentage
            monthly_data[month_key]["total_days"] += 1
            if log.is_achieved:
                monthly_data[month_key]["days_achieved"] += 1
        
        # Format for response
        return [
            {
                "month": data["month"],
                "average_progress": data["total_progress"] / data["total_days"] if data["total_days"] > 0 else 0,
                "days_achieved": data["days_achieved"],
                "total_days": data["total_days"]
            }
            for data in monthly_data.values()
        ]







