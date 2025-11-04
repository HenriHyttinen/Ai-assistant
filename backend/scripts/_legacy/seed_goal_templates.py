#!/usr/bin/env python3
"""
Seed goal templates for nutrition goals
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.nutrition_goals import GoalTemplate, GoalType, GoalFrequency
from datetime import datetime

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
                name="Gain 0.5 Pounds Per Week",
                description="Healthy weight gain for muscle building",
                goal_type=GoalType.WEIGHT_GAIN,
                default_target_value=0.5,
                default_unit="lbs",
                default_frequency=GoalFrequency.WEEKLY,
                default_duration_days=112,  # 16 weeks
                category="weight_management",
                difficulty_level=3,
                instructions="Track your weight weekly and aim for a 0.5-pound gain per week through proper nutrition and strength training.",
                tips="Focus on a calorie surplus of 250 calories per day with adequate protein intake.",
                common_challenges="Ensuring weight gain is mostly muscle, not fat, and maintaining appetite.",
                success_metrics="Consistent weekly weight gain, increased strength, and improved muscle definition."
            ),
            
            # Calorie Goals
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
                name="Calorie Deficit for Weight Loss",
                description="Create a daily calorie deficit for weight loss",
                goal_type=GoalType.CALORIES,
                default_target_value=1500,
                default_unit="cal",
                default_frequency=GoalFrequency.DAILY,
                default_duration_days=90,
                category="weight_management",
                difficulty_level=4,
                instructions="Maintain a daily calorie intake of 1500 calories to create a deficit for weight loss.",
                tips="Focus on high-volume, low-calorie foods. Stay hydrated and get adequate sleep.",
                common_challenges="Hunger management, social situations, and maintaining energy levels.",
                success_metrics="Consistent calorie deficit, steady weight loss, and maintained energy levels."
            ),
            
            # Protein Goals
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
                name="High Protein for Muscle Building",
                description="High protein intake for muscle building and recovery",
                goal_type=GoalType.PROTEIN,
                default_target_value=150,
                default_unit="g",
                default_frequency=GoalFrequency.DAILY,
                default_duration_days=60,
                category="fitness",
                difficulty_level=3,
                instructions="Consume 150g of protein daily to support muscle building and recovery.",
                tips="Distribute protein intake throughout the day. Consider protein supplements if needed.",
                common_challenges="High protein intake can be expensive and may cause digestive issues.",
                success_metrics="Consistent high protein intake, improved muscle mass, and recovery."
            ),
            
            # Fiber Goals
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
            
            # Water Goals
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
            
            # Sodium Goals
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
            ),
            
            # Vitamin Goals
            GoalTemplate(
                name="Get 100mg Vitamin C Daily",
                description="Meet daily vitamin C requirements for immune health",
                goal_type=GoalType.VITAMIN_C,
                default_target_value=100,
                default_unit="mg",
                default_frequency=GoalFrequency.DAILY,
                default_duration_days=30,
                category="health",
                difficulty_level=1,
                instructions="Consume at least 100mg of vitamin C each day from food sources.",
                tips="Focus on citrus fruits, berries, and vegetables. Vitamin C is water-soluble and needs daily intake.",
                common_challenges="Getting enough from food alone, seasonal availability of fresh produce.",
                success_metrics="Consistent daily vitamin C intake, improved immune function, and skin health."
            ),
            
            GoalTemplate(
                name="Get 1000mg Calcium Daily",
                description="Meet daily calcium requirements for bone health",
                goal_type=GoalType.CALCIUM,
                default_target_value=1000,
                default_unit="mg",
                default_frequency=GoalFrequency.DAILY,
                default_duration_days=30,
                category="health",
                difficulty_level=2,
                instructions="Consume at least 1000mg of calcium each day from food sources.",
                tips="Include dairy products, leafy greens, and fortified foods. Consider vitamin D for absorption.",
                common_challenges="Lactose intolerance, getting enough from non-dairy sources, absorption issues.",
                success_metrics="Consistent daily calcium intake, improved bone health, and muscle function."
            ),
            
            # Iron Goals
            GoalTemplate(
                name="Get 18mg Iron Daily",
                description="Meet daily iron requirements for energy and health",
                goal_type=GoalType.IRON,
                default_target_value=18,
                default_unit="mg",
                default_frequency=GoalFrequency.DAILY,
                default_duration_days=30,
                category="health",
                difficulty_level=3,
                instructions="Consume at least 18mg of iron each day from food sources.",
                tips="Include iron-rich foods like lean meats, spinach, and legumes. Pair with vitamin C for absorption.",
                common_challenges="Iron absorption issues, vegetarian/vegan diets, and digestive sensitivity.",
                success_metrics="Consistent daily iron intake, improved energy levels, and blood health."
            ),
            
            # Weight Maintenance
            GoalTemplate(
                name="Maintain Current Weight",
                description="Maintain your current weight within a healthy range",
                goal_type=GoalType.WEIGHT_MAINTENANCE,
                default_target_value=0,
                default_unit="lbs",
                default_frequency=GoalFrequency.WEEKLY,
                default_duration_days=365,
                category="weight_management",
                difficulty_level=2,
                instructions="Maintain your current weight within 2-3 pounds of your starting weight.",
                tips="Focus on consistent eating habits, regular exercise, and monitoring your weight weekly.",
                common_challenges="Holiday weight gain, lifestyle changes, and aging metabolism.",
                success_metrics="Stable weight maintenance, consistent energy levels, and healthy habits."
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







