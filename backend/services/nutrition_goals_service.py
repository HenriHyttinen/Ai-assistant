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
    GoalFilter, GoalSearch, GoalAnalytics, GoalInsights,
    GoalType as SchemaGoalType, GoalFrequency as SchemaGoalFrequency,
    GoalStatus as SchemaGoalStatus
)
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, date
from dateutil import parser as date_parser
import math

class NutritionGoalsService:
    
    # Goal CRUD operations
    def create_goal(self, db: Session, user_id: str, goal_data: NutritionGoalCreate) -> NutritionGoalResponse:
        """Create a new nutrition goal for a user"""
        # Convert schema enums to model enums for database storage
        goal_dict = goal_data.model_dump()
        
        # Convert goal_type from schema enum to model enum (or string)
        goal_type_value = goal_dict.get('goal_type')
        if isinstance(goal_type_value, SchemaGoalType):
            goal_type_value = goal_type_value.value
        elif hasattr(goal_type_value, 'value'):
            goal_type_value = goal_type_value.value
        # Try to convert to model enum, fallback to string
        try:
            goal_type_enum = GoalType(goal_type_value) if isinstance(goal_type_value, str) else goal_type_value
        except (ValueError, TypeError):
            goal_type_enum = goal_type_value  # Use string value directly with native_enum=False
        goal_dict['goal_type'] = goal_type_enum
        
        # Convert frequency from schema enum to model enum (or string)
        frequency_value = goal_dict.get('frequency')
        if isinstance(frequency_value, SchemaGoalFrequency):
            frequency_value = frequency_value.value
        elif hasattr(frequency_value, 'value'):
            frequency_value = frequency_value.value
        # Try to convert to model enum, fallback to string
        try:
            frequency_enum = GoalFrequency(frequency_value) if isinstance(frequency_value, str) else frequency_value
        except (ValueError, TypeError):
            frequency_enum = frequency_value  # Use string value directly with native_enum=False
        goal_dict['frequency'] = frequency_enum
        
        # Convert date strings to datetime objects if needed
        start_date = goal_dict.get('start_date')
        if isinstance(start_date, str):
            try:
                # Try ISO format first (most common)
                # Handle simple date strings like '2025-11-01'
                if len(start_date) == 10 and start_date.count('-') == 2:
                    date_obj = date.fromisoformat(start_date)
                    start_date = datetime.combine(date_obj, datetime.min.time())
                else:
                    start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                try:
                    # Fallback to dateutil parser for other formats
                    start_date = date_parser.parse(start_date)
                except (ValueError, TypeError):
                    # Fallback to datetime.now() if parsing fails
                    start_date = datetime.now()
        elif not isinstance(start_date, datetime):
            start_date = datetime.now()
        goal_dict['start_date'] = start_date
        
        target_date = goal_dict.get('target_date')
        if target_date is not None:
            if isinstance(target_date, str):
                try:
                    # Try ISO format first (most common)
                    # Handle simple date strings like '2025-12-01'
                    if len(target_date) == 10 and target_date.count('-') == 2:
                        date_obj = date.fromisoformat(target_date)
                        target_date = datetime.combine(date_obj, datetime.min.time())
                    else:
                        target_date = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    try:
                        # Fallback to dateutil parser for other formats
                        target_date = date_parser.parse(target_date)
                    except (ValueError, TypeError):
                        target_date = None
            elif not isinstance(target_date, datetime):
                target_date = None
        goal_dict['target_date'] = target_date
        
        db_goal = NutritionGoal(
            user_id=user_id,
            **goal_dict
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
        try:
            # Query with raw enum values to avoid SQLAlchemy enum mapping issues
            from sqlalchemy import text
            
            query_sql = """
                SELECT id, name, description, goal_type, default_target_value, 
                       default_unit, default_frequency, default_duration_days,
                       category, difficulty_level, is_public, usage_count,
                       instructions, tips, common_challenges, success_metrics,
                       created_at, updated_at
                FROM goal_templates
                WHERE is_public = true
            """
            
            params = {}
            if category:
                query_sql += " AND category = :category"
                params['category'] = category
            
            query_sql += " ORDER BY usage_count DESC"
            
            result = db.execute(text(query_sql), params)
            
            # Format templates manually from raw database values
            formatted_templates = []
            for row in result:
                try:
                    # Create a mock template object from row data
                    template_dict = {
                        'id': row[0],
                        'name': row[1],
                        'description': row[2],
                        'goal_type': row[3],  # Raw string value
                        'default_target_value': row[4],
                        'default_unit': row[5],
                        'default_frequency': row[6],  # Raw string value
                        'default_duration_days': row[7],
                        'category': row[8],
                        'difficulty_level': row[9],
                        'is_public': row[10],
                        'usage_count': row[11],
                        'instructions': row[12],
                        'tips': row[13],
                        'common_challenges': row[14],
                        'success_metrics': row[15],
                        'created_at': row[16],
                        'updated_at': row[17]
                    }
                    # Use the formatting method with dict-like object
                    formatted = self._format_template_response_from_dict(template_dict)
                    formatted_templates.append(formatted)
                except Exception as e:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Error formatting template {row[0]}: {str(e)}", exc_info=True)
                    continue
            
            return formatted_templates
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error getting goal templates: {str(e)}", exc_info=True)
            raise
    
    def create_goal_from_template(self, db: Session, user_id: str, template_id: int, customizations: Optional[Dict] = None) -> NutritionGoalResponse:
        """Create a goal from a template"""
        # Query template with raw SQL to avoid enum mapping issues
        from sqlalchemy import text
        
        result = db.execute(
            text("SELECT goal_type, name, description, default_target_value, default_unit, default_frequency, default_duration_days FROM goal_templates WHERE id = :id"),
            {'id': template_id}
        ).first()
        
        if not result:
            raise ValueError("Template not found")
        
        # Extract values from raw query result
        goal_type_value = result[0]  # Raw string value
        template_name = result[1]
        template_description = result[2]
        default_target_value = result[3]
        default_unit = result[4]
        frequency_value = result[5]  # Raw string value
        default_duration_days = result[6]
        
        # Convert enum values properly
        if isinstance(goal_type_value, GoalType):
            goal_type_value = goal_type_value.value
        elif hasattr(goal_type_value, 'value'):
            goal_type_value = goal_type_value.value
        elif not isinstance(goal_type_value, str):
            goal_type_value = str(goal_type_value) if goal_type_value else "calories"
        
        if isinstance(frequency_value, GoalFrequency):
            frequency_value = frequency_value.value
        elif hasattr(frequency_value, 'value'):
            frequency_value = frequency_value.value
        elif not isinstance(frequency_value, str):
            frequency_value = str(frequency_value) if frequency_value else "daily"
        
        # Convert to schema enums
        try:
            goal_type_enum = SchemaGoalType(goal_type_value)
            frequency_enum = SchemaGoalFrequency(frequency_value)
        except (ValueError, TypeError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Invalid enum value in template {template_id}: goal_type={goal_type_value}, frequency={frequency_value}. Using defaults.")
            # Try to map common values
            goal_type_map = {
                "weight_loss": SchemaGoalType.WEIGHT_LOSS,
                "weight_gain": SchemaGoalType.WEIGHT_GAIN,
                "weight_maintenance": SchemaGoalType.WEIGHT_MAINTENANCE,
            }
            goal_type_enum = goal_type_map.get(goal_type_value.lower() if goal_type_value else "", SchemaGoalType.CALORIES)
            frequency_enum = SchemaGoalFrequency.DAILY
        
        # Create goal from template
        goal_data = NutritionGoalCreate(
            goal_type=goal_type_enum,
            goal_name=template_name,
            description=template_description,
            target_value=default_target_value,
            unit=default_unit,
            frequency=frequency_enum,
            start_date=datetime.now(),
            target_date=datetime.now() + timedelta(days=default_duration_days) if default_duration_days else None
        )
        
        # Apply customizations
        if customizations:
            for key, value in customizations.items():
                if hasattr(goal_data, key):
                    setattr(goal_data, key, value)
        
        # Create the goal first
        goal_response = self.create_goal(db, user_id, goal_data)
        
        # Increment template usage (commit happens in create_goal)
        try:
            db.execute(
                text("UPDATE goal_templates SET usage_count = usage_count + 1 WHERE id = :id"),
                {'id': template_id}
            )
            db.commit()
        except Exception as e:
            # Log but don't fail if usage count update fails
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to increment template usage count for template {template_id}: {str(e)}")
            db.rollback()
        
        return goal_response
    
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
        
        # Convert enum values from model to schema enums
        goal_type_value = goal.goal_type
        if isinstance(goal_type_value, GoalType):
            goal_type_value = goal_type_value.value
        elif hasattr(goal_type_value, 'value'):
            goal_type_value = goal_type_value.value
        elif not isinstance(goal_type_value, str):
            goal_type_value = str(goal_type_value) if goal_type_value else "calories"
        
        frequency_value = goal.frequency
        if isinstance(frequency_value, GoalFrequency):
            frequency_value = frequency_value.value
        elif hasattr(frequency_value, 'value'):
            frequency_value = frequency_value.value
        elif not isinstance(frequency_value, str):
            frequency_value = str(frequency_value) if frequency_value else "daily"
        
        status_value = goal.status
        if isinstance(status_value, GoalStatus):
            status_value = status_value.value
        elif hasattr(status_value, 'value'):
            status_value = status_value.value
        elif not isinstance(status_value, str):
            status_value = str(status_value) if status_value else "active"
        
        # Convert to schema enums
        try:
            goal_type_enum = SchemaGoalType(goal_type_value)
            frequency_enum = SchemaGoalFrequency(frequency_value)
            status_enum = SchemaGoalStatus(status_value)
        except (ValueError, TypeError) as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error converting enum values for goal {goal.id}: {str(e)}")
            goal_type_enum = SchemaGoalType.CALORIES
            frequency_enum = SchemaGoalFrequency.DAILY
            status_enum = SchemaGoalStatus.ACTIVE
        
        # Load related data
        progress_logs = db.query(GoalProgressLog).filter(GoalProgressLog.goal_id == goal.id).all()
        milestones = db.query(GoalMilestone).filter(GoalMilestone.goal_id == goal.id).all()
        
        return NutritionGoalResponse(
            id=goal.id,
            user_id=goal.user_id,
            goal_type=goal_type_enum,
            goal_name=goal.goal_name,
            description=goal.description,
            target_value=goal.target_value,
            current_value=goal.current_value,
            unit=goal.unit,
            frequency=frequency_enum,
            start_date=goal.start_date,
            target_date=goal.target_date,
            is_flexible=goal.is_flexible,
            status=status_enum,
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
    
    def _format_template_response_from_dict(self, template_dict: dict) -> GoalTemplateResponse:
        """Format template from dictionary (for raw database queries)"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Convert enum values properly - handle both enum objects and string values
        goal_type_value = template_dict.get('goal_type')
        if isinstance(goal_type_value, GoalType):
            goal_type_value = goal_type_value.value  # Get the string value
        elif hasattr(goal_type_value, 'value'):
            goal_type_value = goal_type_value.value
        elif isinstance(goal_type_value, str):
            # Already a string, use as-is
            pass
        else:
            # Fallback: try to get string representation
            goal_type_value = str(goal_type_value) if goal_type_value else "calories"
        
        frequency_value = template_dict.get('default_frequency')
        if isinstance(frequency_value, GoalFrequency):
            frequency_value = frequency_value.value
        elif hasattr(frequency_value, 'value'):
            frequency_value = frequency_value.value
        elif isinstance(frequency_value, str):
            # Already a string, use as-is
            pass
        else:
            # Fallback: try to get string representation
            frequency_value = str(frequency_value) if frequency_value else "daily"
        
        # Validate and convert to schema enum
        try:
            goal_type_enum = SchemaGoalType(goal_type_value)
            frequency_enum = SchemaGoalFrequency(frequency_value)
        except (ValueError, TypeError) as e:
            # If enum value doesn't match, log warning with details and use a default
            logger.warning(
                f"Invalid enum value in template {template_dict.get('id')}: "
                f"goal_type={goal_type_value} (type: {type(goal_type_value)}), "
                f"frequency={frequency_value} (type: {type(frequency_value)}). "
                f"Error: {str(e)}. Using defaults."
            )
            # Try to map common values
            goal_type_map = {
                "weight_loss": SchemaGoalType.WEIGHT_LOSS,
                "weight_gain": SchemaGoalType.WEIGHT_GAIN,
                "weight_maintenance": SchemaGoalType.WEIGHT_MAINTENANCE,
            }
            goal_type_enum = goal_type_map.get(goal_type_value.lower() if goal_type_value else "", SchemaGoalType.CALORIES)
            frequency_enum = SchemaGoalFrequency.DAILY  # Default fallback
        
        return GoalTemplateResponse(
            id=template_dict.get('id'),
            name=template_dict.get('name'),
            description=template_dict.get('description'),
            goal_type=goal_type_enum,
            default_target_value=template_dict.get('default_target_value'),
            default_unit=template_dict.get('default_unit'),
            default_frequency=frequency_enum,
            default_duration_days=template_dict.get('default_duration_days'),
            category=template_dict.get('category'),
            difficulty_level=template_dict.get('difficulty_level'),
            is_public=template_dict.get('is_public'),
            usage_count=template_dict.get('usage_count'),
            instructions=template_dict.get('instructions'),
            tips=template_dict.get('tips'),
            common_challenges=template_dict.get('common_challenges'),
            success_metrics=template_dict.get('success_metrics'),
            created_at=template_dict.get('created_at'),
            updated_at=template_dict.get('updated_at')
        )
    
    def _format_template_response(self, template: GoalTemplate) -> GoalTemplateResponse:
        """Format template for API response"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Convert enum values properly - handle both enum objects and string values
        goal_type_value = template.goal_type
        if isinstance(goal_type_value, GoalType):
            goal_type_value = goal_type_value.value  # Get the string value
        elif hasattr(goal_type_value, 'value'):
            goal_type_value = goal_type_value.value
        elif isinstance(goal_type_value, str):
            # Already a string, use as-is
            pass
        else:
            # Fallback: try to get string representation
            goal_type_value = str(goal_type_value) if goal_type_value else "calories"
        
        frequency_value = template.default_frequency
        if isinstance(frequency_value, GoalFrequency):
            frequency_value = frequency_value.value
        elif hasattr(frequency_value, 'value'):
            frequency_value = frequency_value.value
        elif isinstance(frequency_value, str):
            # Already a string, use as-is
            pass
        else:
            # Fallback: try to get string representation
            frequency_value = str(frequency_value) if frequency_value else "daily"
        
        # Validate and convert to schema enum
        try:
            goal_type_enum = SchemaGoalType(goal_type_value)
            frequency_enum = SchemaGoalFrequency(frequency_value)
        except (ValueError, TypeError) as e:
            # If enum value doesn't match, log warning with details and use a default
            logger.warning(
                f"Invalid enum value in template {template.id}: "
                f"goal_type={goal_type_value} (type: {type(goal_type_value)}), "
                f"frequency={frequency_value} (type: {type(frequency_value)}). "
                f"Error: {str(e)}. Using defaults."
            )
            # Try to map common values
            goal_type_map = {
                "weight_loss": SchemaGoalType.WEIGHT_LOSS,
                "weight_gain": SchemaGoalType.WEIGHT_GAIN,
                "weight_maintenance": SchemaGoalType.WEIGHT_MAINTENANCE,
            }
            goal_type_enum = goal_type_map.get(goal_type_value.lower(), SchemaGoalType.CALORIES)
            frequency_enum = SchemaGoalFrequency.DAILY  # Default fallback
        
        return GoalTemplateResponse(
            id=template.id,
            name=template.name,
            description=template.description,
            goal_type=goal_type_enum,
            default_target_value=template.default_target_value,
            default_unit=template.default_unit,
            default_frequency=frequency_enum,
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







