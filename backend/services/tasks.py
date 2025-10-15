from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import BackgroundTasks
import asyncio
import logging

from .email import send_weekly_summary_email, send_goal_achievement_email
from .analytics import calculate_weekly_summary, check_goal_achievements
from models.user import User
from database import SessionLocal

logger = logging.getLogger(__name__)

async def send_weekly_summaries():
    """Send weekly summary emails to all users."""
    try:
        db = SessionLocal()
        # Get all active users
        users = db.query(User).filter(User.is_active == True).all()
        
        for user in users:
            try:
                # Calculate weekly summary
                summary = calculate_weekly_summary(user.id, db)
                
                # Send email
                await send_weekly_summary_email(user.email, summary)
                
                logger.info(f"Sent weekly summary to user {user.id}")
            except Exception as e:
                logger.error(f"Error sending weekly summary to user {user.id}: {str(e)}")
                continue
    except Exception as e:
        logger.error(f"Error in send_weekly_summaries: {str(e)}")
    finally:
        db.close()

async def check_and_notify_goals():
    """Check for achieved goals and send notifications."""
    try:
        db = SessionLocal()
        # Get all active users
        users = db.query(User).filter(User.is_active == True).all()
        
        for user in users:
            try:
                # Check for achieved goals
                achievements = check_goal_achievements(user.id, db)
                
                for achievement in achievements:
                    # Send achievement notification
                    await send_goal_achievement_email(user.email, achievement)
                    
                logger.info(f"Processed goals for user {user.id}")
            except Exception as e:
                logger.error(f"Error processing goals for user {user.id}: {str(e)}")
                continue
    except Exception as e:
        logger.error(f"Error in check_and_notify_goals: {str(e)}")
    finally:
        db.close()

async def run_periodic_tasks():
    """Run all periodic tasks."""
    while True:
        try:
            # Get current time
            now = datetime.utcnow()
            
            # Run weekly summaries on Monday at 9 AM UTC
            if now.weekday() == 0 and now.hour == 9:
                await send_weekly_summaries()
            
            # Check goals every day at 8 AM UTC
            if now.hour == 8:
                await check_and_notify_goals()
            
            # Sleep for 1 hour
            await asyncio.sleep(3600)
        except Exception as e:
            logger.error(f"Error in run_periodic_tasks: {str(e)}")
            await asyncio.sleep(60)  # Sleep for 1 minute on error

def start_background_tasks():
    """Start background tasks."""
    loop = asyncio.get_event_loop()
    loop.create_task(run_periodic_tasks())
    logger.info("Started background tasks") 