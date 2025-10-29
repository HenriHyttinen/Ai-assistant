from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from services.achievement_service import AchievementService
from auth.supabase_auth import get_current_user_supabase as get_current_user
from models.user import User
from typing import List, Dict

router = APIRouter()

@router.get("/")
async def get_user_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all achievements for the current user"""
    try:
        achievement_service = AchievementService(db)
        achievements = achievement_service.get_user_achievements(current_user.id)
        return {"achievements": achievements}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching achievements: {str(e)}")

@router.get("/available")
async def get_available_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all available achievements with user's progress"""
    try:
        achievement_service = AchievementService(db)
        achievements = achievement_service.get_available_achievements(current_user.id)
        return {"achievements": achievements}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching available achievements: {str(e)}")

@router.post("/check")
async def check_new_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check for new achievements and return any that were just unlocked"""
    try:
        achievement_service = AchievementService(db)
        new_achievements = achievement_service.check_and_award_achievements(current_user.id)
        return {"new_achievements": new_achievements, "count": len(new_achievements)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking achievements: {str(e)}")
