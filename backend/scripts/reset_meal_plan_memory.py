#!/usr/bin/env python3
"""
Reset meal plan "recent memory" by clearing old meal plans or reducing the lookback window.

This script helps manage the "recent memory" that excludes meals from selection.
The memory is built from meal plans created in the last N days (default: 7 days).

Options:
1. Delete meal plans older than X days
2. Reduce the lookback window in the code
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.nutrition import MealPlan, MealPlanMeal
from datetime import date, timedelta
from sqlalchemy import and_
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_recent_meal_count(db, days: int = 7) -> dict:
    """Get statistics about recent meal plans"""
    since = date.today() - timedelta(days=days)
    
    # Count meal plans
    meal_plans = db.query(MealPlan).filter(
        MealPlan.start_date >= since
    ).all()
    
    # Count meals
    plan_ids = [p.id for p in meal_plans]
    if plan_ids:
        meals = db.query(MealPlanMeal).filter(
            MealPlanMeal.meal_plan_id.in_(plan_ids)
        ).all()
        unique_names = set(m.meal_name for m in meals if m.meal_name)
    else:
        unique_names = set()
    
    return {
        'meal_plan_count': len(meal_plans),
        'total_meals': len(meals) if plan_ids else 0,
        'unique_meal_names': len(unique_names),
        'days': days
    }

def delete_old_meal_plans(db, older_than_days: int = 7, user_id: int = None, confirm: bool = False, all_plans: bool = False):
    """
    Delete meal plans older than specified days, or ALL meal plans if all_plans=True.
    
    Args:
        db: Database session
        older_than_days: Delete meal plans older than this many days (default: 7)
        user_id: If specified, only delete for this user
        confirm: If False, just shows what would be deleted (dry run)
        all_plans: If True, delete ALL meal plans regardless of date (for testing)
    """
    if all_plans:
        query = db.query(MealPlan)
        if user_id:
            query = query.filter(MealPlan.user_id == user_id)
        plans_to_delete = query.all()
        
        if not plans_to_delete:
            logger.info("✅ No meal plans found")
            return 0
        
        logger.info(f"⚠️  Found {len(plans_to_delete)} meal plan(s) - ALL will be deleted!")
        
        if not confirm:
            logger.info("⚠️  DRY RUN - No meal plans will be deleted. Use --confirm to actually delete ALL plans.")
            logger.info(f"   Would delete: {len(plans_to_delete)} meal plan(s)")
            return 0
    else:
        cutoff_date = date.today() - timedelta(days=older_than_days)
        
        query = db.query(MealPlan).filter(MealPlan.start_date < cutoff_date)
        if user_id:
            query = query.filter(MealPlan.user_id == user_id)
        
        plans_to_delete = query.all()
        
        if not plans_to_delete:
            logger.info(f"✅ No meal plans found older than {older_than_days} days")
            return 0
        
        logger.info(f"📊 Found {len(plans_to_delete)} meal plan(s) older than {older_than_days} days")
        
        if not confirm:
            logger.info("⚠️  DRY RUN - No meal plans will be deleted. Use --confirm to actually delete.")
            return 0
    
    deleted_count = 0
    for plan in plans_to_delete:
        try:
            # Cascade delete will handle meals automatically
            db.delete(plan)
            deleted_count += 1
        except Exception as e:
            logger.error(f"Error deleting meal plan {plan.id}: {e}")
    
    db.commit()
    logger.info(f"✅ Deleted {deleted_count} meal plan(s)")
    return deleted_count

def archive_old_meal_plans(db, older_than_days: int = 7, user_id: int = None):
    """
    Archive old meal plans by setting is_active=False instead of deleting.
    
    Args:
        db: Database session
        older_than_days: Archive meal plans older than this many days
        user_id: If specified, only archive for this user
    """
    cutoff_date = date.today() - timedelta(days=older_than_days)
    
    query = db.query(MealPlan).filter(
        and_(
            MealPlan.start_date < cutoff_date,
            MealPlan.is_active == True
        )
    )
    if user_id:
        query = query.filter(MealPlan.user_id == user_id)
    
    old_plans = query.all()
    
    if not old_plans:
        logger.info(f"✅ No active meal plans found older than {older_than_days} days")
        return 0
    
    logger.info(f"📊 Found {len(old_plans)} active meal plan(s) older than {older_than_days} days")
    
    archived_count = 0
    for plan in old_plans:
        try:
            plan.is_active = False
            archived_count += 1
        except Exception as e:
            logger.error(f"Error archiving meal plan {plan.id}: {e}")
    
    db.commit()
    logger.info(f"✅ Archived {archived_count} meal plan(s) (set is_active=False)")
    return archived_count

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Reset meal plan recent memory')
    parser.add_argument('--action', choices=['stats', 'delete', 'archive'], default='stats',
                       help='Action to perform: stats (show), delete, or archive')
    parser.add_argument('--days', type=int, default=7,
                       help='Number of days for lookback/cleanup (default: 7)')
    parser.add_argument('--user-id', type=int, default=None,
                       help='Filter by user ID (optional)')
    parser.add_argument('--confirm', action='store_true',
                       help='Confirm deletion (required for delete action)')
    parser.add_argument('--older-than', type=int, default=7,
                       help='For delete/archive: delete plans older than this many days (default: 7)')
    parser.add_argument('--all', action='store_true',
                       help='Delete/archive ALL meal plans regardless of date (for testing)')
    
    args = parser.parse_args()
    
    db = SessionLocal()
    try:
        if args.action == 'stats':
            logger.info("📊 Meal Plan Memory Statistics")
            logger.info("=" * 50)
            
            stats = get_recent_meal_count(db, days=args.days)
            logger.info(f"📅 Lookback window: {stats['days']} days")
            logger.info(f"📋 Meal plans in last {stats['days']} days: {stats['meal_plan_count']}")
            logger.info(f"🍽️  Total meals: {stats['total_meals']}")
            logger.info(f"🔤 Unique meal names: {stats['unique_meal_names']}")
            logger.info("")
            logger.info(f"💡 These {stats['unique_meal_names']} meal names are currently being excluded from selection")
            logger.info("")
            logger.info("To reset memory:")
            logger.info("  python scripts/reset_meal_plan_memory.py --action delete --older-than 7 --confirm")
            logger.info("  python scripts/reset_meal_plan_memory.py --action archive --older-than 7")
            
        elif args.action == 'delete':
            if not args.confirm:
                logger.error("❌ --confirm flag is required for delete action")
                logger.info("This is a safety measure. Add --confirm to actually delete meal plans.")
                return
            
            if args.all:
                logger.info("🗑️  Deleting ALL meal plans (regardless of date)...")
            else:
                logger.info(f"🗑️  Deleting meal plans older than {args.older_than} days...")
            deleted = delete_old_meal_plans(db, older_than_days=args.older_than, 
                                           user_id=args.user_id, confirm=True, all_plans=args.all)
            
            # Show new stats
            logger.info("")
            logger.info("📊 Updated Statistics:")
            stats = get_recent_meal_count(db, days=args.days)
            logger.info(f"📋 Meal plans in last {args.days} days: {stats['meal_plan_count']}")
            logger.info(f"🔤 Unique meal names: {stats['unique_meal_names']}")
            
        elif args.action == 'archive':
            logger.info(f"📦 Archiving meal plans older than {args.older_than} days...")
            archived = archive_old_meal_plans(db, older_than_days=args.older_than, 
                                             user_id=args.user_id)
            
            # Show new stats
            logger.info("")
            logger.info("📊 Updated Statistics:")
            stats = get_recent_meal_count(db, days=args.days)
            logger.info(f"📋 Active meal plans in last {args.days} days: {stats['meal_plan_count']}")
            logger.info(f"🔤 Unique meal names: {stats['unique_meal_names']}")
            
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()

