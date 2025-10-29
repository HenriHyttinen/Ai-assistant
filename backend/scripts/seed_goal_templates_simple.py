#!/usr/bin/env python3
"""
Simple seed script for goal templates without importing User model
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.nutrition_goals import GoalTemplate, GoalType, GoalFrequency

def seed_goal_templates():
    """Seed the database with goal templates"""
    db = SessionLocal()
    
    try:
        # Check if templates already exist
        existing_count = db.query(GoalTemplate).count()
        if existing_count > 0:
            print(f"✅ {existing_count} goal templates already exist. Skipping seed.")
            return
        
        templates = [
            # Weight Management Goals
            GoalTemplate(
                name="Lose 1 Pound Per Week",
                description="A healthy and sustainable weight loss goal",
                goal_type=GoalType.WEIGHT_LOSS,
                default_target_value=1.0,
                default_unit="lbs",
                default_frequency=GoalFrequency.WEEKLY,
                default_duration_days=84,  # 12 weeks
                category="weight_management",
                difficulty_level=3,
                instructions="Track your weight weekly and aim for a 1-pound loss per week through a combination of diet and exercise.",
                tips="Focus on creating a calorie deficit of 500 calories per day through diet and exercise.",
                common_challenges="Plateaus, water weight fluctuations, and social eating situations.",
                success_metrics="Consistent weekly weight loss, improved energy levels, and better body composition."
            ),
            
            GoalTemplate(
                name="Eat 2000 Calories Daily",
                description="Maintain a consistent daily calorie intake",
                goal_type=GoalType.CALORIES,
                default_target_value=2000,
                default_unit="cal",
                default_frequency=GoalFrequency.DAILY,
                default_duration_days=30,
                category="nutrition",
                difficulty_level=2,
                instructions="Track your daily calorie intake and aim to consume exactly 2000 calories each day.",
                tips="Use a food scale and nutrition tracking app for accuracy. Plan meals in advance.",
                common_challenges="Estimating portion sizes, tracking hidden calories, and social eating.",
                success_metrics="Consistent daily calorie intake within 50 calories of target."
            ),
            
            GoalTemplate(
                name="Eat 100g Protein Daily",
                description="Meet daily protein requirements for muscle health",
                goal_type=GoalType.PROTEIN,
                default_target_value=100,
                default_unit="g",
                default_frequency=GoalFrequency.DAILY,
                default_duration_days=30,
                category="nutrition",
                difficulty_level=2,
                instructions="Consume at least 100g of protein each day from various sources.",
                tips="Include protein in every meal. Good sources include lean meats, fish, eggs, dairy, and legumes.",
                common_challenges="Getting enough protein without excess calories, variety in protein sources.",
                success_metrics="Consistent daily protein intake, improved muscle recovery, and satiety."
            ),
            
            GoalTemplate(
                name="Eat 25g Fiber Daily",
                description="Meet daily fiber requirements for digestive health",
                goal_type=GoalType.FIBER,
                default_target_value=25,
                default_unit="g",
                default_frequency=GoalFrequency.DAILY,
                default_duration_days=30,
                category="health",
                difficulty_level=2,
                instructions="Consume at least 25g of fiber each day from whole foods.",
                tips="Focus on fruits, vegetables, whole grains, and legumes. Increase gradually to avoid digestive issues.",
                common_challenges="Getting enough fiber without excess calories, digestive discomfort during transition.",
                success_metrics="Consistent daily fiber intake, improved digestive health, and satiety."
            ),
            
            GoalTemplate(
                name="Drink 8 Glasses of Water Daily",
                description="Stay properly hydrated throughout the day",
                goal_type=GoalType.WATER,
                default_target_value=64,
                default_unit="oz",
                default_frequency=GoalFrequency.DAILY,
                default_duration_days=30,
                category="health",
                difficulty_level=1,
                instructions="Drink 8 glasses (64 oz) of water each day.",
                tips="Carry a water bottle, set reminders, and drink water with meals.",
                common_challenges="Remembering to drink water, frequent bathroom breaks, and taste preferences.",
                success_metrics="Consistent daily water intake, improved energy levels, and better skin health."
            ),
            
            GoalTemplate(
                name="Limit Sodium to 2300mg Daily",
                description="Maintain healthy sodium intake for heart health",
                goal_type=GoalType.SODIUM,
                default_target_value=2300,
                default_unit="mg",
                default_frequency=GoalFrequency.DAILY,
                default_duration_days=30,
                category="health",
                difficulty_level=3,
                instructions="Keep daily sodium intake at or below 2300mg.",
                tips="Read nutrition labels, cook at home, and limit processed foods.",
                common_challenges="Hidden sodium in processed foods, restaurant meals, and taste preferences.",
                success_metrics="Consistent low sodium intake, improved blood pressure, and heart health."
            )
        ]
        
        # Add all templates to database
        for template in templates:
            db.add(template)
        
        db.commit()
        print(f"✅ Successfully seeded {len(templates)} goal templates!")
        
    except Exception as e:
        print(f"❌ Error seeding goal templates: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_goal_templates()


