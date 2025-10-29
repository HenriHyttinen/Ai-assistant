#!/usr/bin/env python3
"""
Direct SQL seed script for goal templates
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from sqlalchemy import text

def seed_goal_templates():
    """Seed the database with goal templates using direct SQL"""
    
    try:
        with engine.connect() as conn:
            # Check if templates already exist
            result = conn.execute(text("SELECT COUNT(*) FROM goal_templates"))
            count = result.scalar()
            
            if count > 0:
                print(f"✅ {count} goal templates already exist. Skipping seed.")
                return
            
            # Insert goal templates
            templates = [
                ("Lose 1 Pound Per Week", "A healthy and sustainable weight loss goal", "weight_loss", 1.0, "lbs", "weekly", 84, "weight_management", 3, "Track your weight weekly and aim for a 1-pound loss per week through a combination of diet and exercise.", "Focus on creating a calorie deficit of 500 calories per day through diet and exercise.", "Plateaus, water weight fluctuations, and social eating situations.", "Consistent weekly weight loss, improved energy levels, and better body composition."),
                ("Eat 2000 Calories Daily", "Maintain a consistent daily calorie intake", "calories", 2000, "cal", "daily", 30, "nutrition", 2, "Track your daily calorie intake and aim to consume exactly 2000 calories each day.", "Use a food scale and nutrition tracking app for accuracy. Plan meals in advance.", "Estimating portion sizes, tracking hidden calories, and social eating.", "Consistent daily calorie intake within 50 calories of target."),
                ("Eat 100g Protein Daily", "Meet daily protein requirements for muscle health", "protein", 100, "g", "daily", 30, "nutrition", 2, "Consume at least 100g of protein each day from various sources.", "Include protein in every meal. Good sources include lean meats, fish, eggs, dairy, and legumes.", "Getting enough protein without excess calories, variety in protein sources.", "Consistent daily protein intake, improved muscle recovery, and satiety."),
                ("Eat 25g Fiber Daily", "Meet daily fiber requirements for digestive health", "fiber", 25, "g", "daily", 30, "health", 2, "Consume at least 25g of fiber each day from whole foods.", "Focus on fruits, vegetables, whole grains, and legumes. Increase gradually to avoid digestive issues.", "Getting enough fiber without excess calories, digestive discomfort during transition.", "Consistent daily fiber intake, improved digestive health, and satiety."),
                ("Drink 8 Glasses of Water Daily", "Stay properly hydrated throughout the day", "water", 64, "oz", "daily", 30, "health", 1, "Drink 8 glasses (64 oz) of water each day.", "Carry a water bottle, set reminders, and drink water with meals.", "Remembering to drink water, frequent bathroom breaks, and taste preferences.", "Consistent daily water intake, improved energy levels, and better skin health."),
                ("Limit Sodium to 2300mg Daily", "Maintain healthy sodium intake for heart health", "sodium", 2300, "mg", "daily", 30, "health", 3, "Keep daily sodium intake at or below 2300mg.", "Read nutrition labels, cook at home, and limit processed foods.", "Hidden sodium in processed foods, restaurant meals, and taste preferences.", "Consistent low sodium intake, improved blood pressure, and heart health.")
            ]
            
            for template in templates:
                conn.execute(text("""
                    INSERT INTO goal_templates (
                        name, description, goal_type, default_target_value, default_unit,
                        default_frequency, default_duration_days, category, difficulty_level,
                        instructions, tips, common_challenges, success_metrics,
                        is_public, usage_count, created_at, updated_at
                    ) VALUES (:name, :description, :goal_type, :target_value, :unit,
                        :frequency, :duration_days, :category, :difficulty,
                        :instructions, :tips, :challenges, :metrics,
                        :is_public, :usage_count, :created_at, :updated_at)
                """), {
                    "name": template[0], "description": template[1], "goal_type": template[2], 
                    "target_value": template[3], "unit": template[4], "frequency": template[5], 
                    "duration_days": template[6], "category": template[7], "difficulty": template[8], 
                    "instructions": template[9], "tips": template[10], "challenges": template[11], 
                    "metrics": template[12], "is_public": True, "usage_count": 0,
                    "created_at": "2024-01-01 00:00:00", "updated_at": "2024-01-01 00:00:00"
                })
            
            conn.commit()
            print(f"✅ Successfully seeded {len(templates)} goal templates!")
            
    except Exception as e:
        print(f"❌ Error seeding goal templates: {e}")

if __name__ == "__main__":
    seed_goal_templates()
