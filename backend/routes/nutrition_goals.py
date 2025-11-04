from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models.user import User
from auth.supabase_auth import get_current_user_supabase as get_current_user
from services.nutrition_goals_service import NutritionGoalsService
from schemas.nutrition_goals import (
    NutritionGoalCreate, NutritionGoalUpdate, NutritionGoalResponse,
    GoalProgressLogCreate, GoalProgressLogUpdate, GoalProgressLogResponse,
    GoalMilestoneCreate, GoalMilestoneUpdate, GoalMilestoneResponse,
    GoalTemplateCreate, GoalTemplateResponse,
    GoalDashboard, GoalAnalytics, GoalInsights,
    GoalSearch, GoalFilter, GoalType, GoalStatus, GoalFrequency
)

router = APIRouter(prefix="/nutrition-goals", tags=["Nutrition Goals"])

# Goal CRUD operations
@router.post("/", response_model=NutritionGoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    goal_data: NutritionGoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new nutrition goal"""
    service = NutritionGoalsService()
    try:
        goal = service.create_goal(db, current_user.id, goal_data)
        return goal
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{goal_id}", response_model=NutritionGoalResponse)
def get_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific goal by ID"""
    service = NutritionGoalsService()
    goal = service.get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return goal

@router.get("/", response_model=List[NutritionGoalResponse])
def get_user_goals(
    query: Optional[str] = Query(None, description="Search query"),
    status: Optional[GoalStatus] = Query(None, description="Filter by status"),
    goal_type: Optional[GoalType] = Query(None, description="Filter by goal type"),
    frequency: Optional[GoalFrequency] = Query(None, description="Filter by frequency"),
    priority: Optional[int] = Query(None, ge=1, le=5, description="Filter by priority"),
    is_public: Optional[bool] = Query(None, description="Filter by public status"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all goals for the current user with filtering and pagination"""
    service = NutritionGoalsService()
    
    # Build search parameters
    search_params = GoalSearch(
        query=query,
        filters=GoalFilter(
            status=status,
            goal_type=goal_type,
            frequency=frequency,
            priority=priority,
            is_public=is_public
        ) if any([status, goal_type, frequency, priority, is_public]) else None,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit,
        offset=offset
    )
    
    goals = service.get_user_goals(db, current_user.id, search_params)
    return goals

@router.put("/{goal_id}", response_model=NutritionGoalResponse)
def update_goal(
    goal_id: int,
    goal_data: NutritionGoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a goal"""
    service = NutritionGoalsService()
    goal = service.update_goal(db, goal_id, current_user.id, goal_data)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return goal

@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a goal"""
    service = NutritionGoalsService()
    if not service.delete_goal(db, goal_id, current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")

# Progress tracking
@router.post("/progress", response_model=GoalProgressLogResponse, status_code=status.HTTP_201_CREATED)
def log_progress(
    progress_data: GoalProgressLogCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Log progress for a goal"""
    service = NutritionGoalsService()
    try:
        progress_log = service.log_progress(db, current_user.id, progress_data)
        return progress_log
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{goal_id}/progress", response_model=List[GoalProgressLogResponse])
def get_goal_progress(
    goal_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days to retrieve"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get progress history for a goal"""
    service = NutritionGoalsService()
    progress_logs = service.get_goal_progress(db, goal_id, current_user.id, days)
    return progress_logs

@router.put("/progress/{log_id}", response_model=GoalProgressLogResponse)
def update_progress_log(
    log_id: int,
    progress_data: GoalProgressLogUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a progress log"""
    service = NutritionGoalsService()
    # This would need to be implemented in the service
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")

@router.delete("/progress/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_progress_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a progress log"""
    service = NutritionGoalsService()
    # This would need to be implemented in the service
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")

# Milestones
@router.post("/milestones", response_model=GoalMilestoneResponse, status_code=status.HTTP_201_CREATED)
def create_milestone(
    milestone_data: GoalMilestoneCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a milestone for a goal"""
    service = NutritionGoalsService()
    try:
        milestone = service.create_milestone(db, current_user.id, milestone_data)
        return milestone
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/{goal_id}/milestones", response_model=List[GoalMilestoneResponse])
def get_goal_milestones(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get milestones for a goal"""
    service = NutritionGoalsService()
    # Verify goal belongs to user
    goal = service.get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    
    milestones = db.query(GoalMilestone).filter(GoalMilestone.goal_id == goal_id).all()
    return [service._format_milestone_response(milestone) for milestone in milestones]

@router.put("/milestones/{milestone_id}", response_model=GoalMilestoneResponse)
def update_milestone(
    milestone_id: int,
    milestone_data: GoalMilestoneUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a milestone"""
    service = NutritionGoalsService()
    # This would need to be implemented in the service
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")

@router.delete("/milestones/{milestone_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_milestone(
    milestone_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a milestone"""
    service = NutritionGoalsService()
    # This would need to be implemented in the service
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Not implemented yet")

@router.post("/{goal_id}/check-milestones", response_model=List[GoalMilestoneResponse])
def check_milestones(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check and update milestone achievements for a goal"""
    service = NutritionGoalsService()
    # Verify goal belongs to user
    goal = service.get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    
    achieved_milestones = service.check_milestones(db, goal_id)
    return achieved_milestones

# Dashboard and analytics
@router.get("/dashboard/summary", response_model=GoalDashboard)
def get_goal_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive goal dashboard"""
    service = NutritionGoalsService()
    dashboard = service.get_goal_dashboard(db, current_user.id)
    return dashboard

@router.get("/{goal_id}/analytics", response_model=GoalAnalytics)
def get_goal_analytics(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed analytics for a specific goal"""
    service = NutritionGoalsService()
    analytics = service.get_goal_analytics(db, goal_id, current_user.id)
    if not analytics:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    return analytics

# Templates
@router.get("/templates/", response_model=List[GoalTemplateResponse])
def get_goal_templates(
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    """Get available goal templates"""
    try:
        service = NutritionGoalsService()
        templates = service.get_goal_templates(db, category)
        return templates
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error getting goal templates: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading templates: {str(e)}"
        )

@router.post("/templates/{template_id}/create-goal", response_model=NutritionGoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal_from_template(
    template_id: int,
    customizations: Optional[dict] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a goal from a template"""
    service = NutritionGoalsService()
    try:
        goal = service.create_goal_from_template(db, current_user.id, template_id, customizations)
        return goal
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error creating goal from template {template_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating goal from template: {str(e)}"
        )

# Bulk operations
@router.post("/bulk/progress", response_model=List[GoalProgressLogResponse], status_code=status.HTTP_201_CREATED)
def log_bulk_progress(
    progress_data: List[GoalProgressLogCreate],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Log progress for multiple goals at once"""
    service = NutritionGoalsService()
    results = []
    for data in progress_data:
        try:
            progress_log = service.log_progress(db, current_user.id, data)
            results.append(progress_log)
        except ValueError as e:
            # Log error but continue with other entries
            continue
    return results

@router.post("/bulk/check-milestones", response_model=List[GoalMilestoneResponse])
def check_all_milestones(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check milestones for all active goals"""
    service = NutritionGoalsService()
    all_achieved = []
    
    # Get all active goals
    active_goals = db.query(NutritionGoal).filter(
        NutritionGoal.user_id == current_user.id,
        NutritionGoal.status == GoalStatus.ACTIVE
    ).all()
    
    for goal in active_goals:
        achieved = service.check_milestones(db, goal.id)
        all_achieved.extend(achieved)
    
    return all_achieved

# Goal insights and recommendations
@router.get("/{goal_id}/insights", response_model=GoalInsights)
def get_goal_insights(
    goal_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get AI-powered insights and recommendations for a goal"""
    service = NutritionGoalsService()
    # Verify goal belongs to user
    goal = service.get_goal(db, goal_id, current_user.id)
    if not goal:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Goal not found")
    
    # This would need to be implemented with AI insights
    # For now, return basic insights
    insights = GoalInsights(
        insights=[
            f"Your {goal.goal_name} goal is {goal.progress_percentage:.1f}% complete",
            f"You've achieved this goal {goal.days_achieved} out of {goal.total_days} days",
            f"Your current streak is {goal.streak_days} days"
        ],
        recommendations=[
            "Log your progress daily to maintain consistency",
            "Set smaller milestones to stay motivated",
            "Review your goal regularly and adjust if needed"
        ],
        challenges=[
            "Consistency can be difficult to maintain",
            "Life events may disrupt your routine"
        ],
        successes=[
            f"You've maintained a {goal.best_streak}-day streak",
            f"You're {goal.progress_percentage:.1f}% toward your target"
        ],
        next_actions=[
            "Continue logging daily progress",
            "Celebrate your current streak",
            "Consider setting a new milestone"
        ]
    )
    
    return insights
