from typing import Dict, Any
import math

def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Calculate BMI using weight in kg and height in cm."""
    height_m = height_cm / 100
    return round(weight_kg / (height_m * height_m), 2)

def get_bmi_category(bmi: float) -> str:
    """Get BMI category based on calculated BMI value."""
    if bmi < 18.5:
        return "underweight"
    elif bmi < 25:
        return "normal"
    elif bmi < 30:
        return "overweight"
    else:
        return "obese"

def calculate_bmi_score(bmi: float) -> float:
    """Calculate a normalized score (0-100) based on BMI."""
    # Optimal BMI range is 18.5-24.9
    if 18.5 <= bmi <= 24.9:
        return 100
    elif bmi < 18.5:
        # Score decreases as BMI gets further from 18.5
        return max(0, 100 - (18.5 - bmi) * 20)
    else:
        # Score decreases as BMI gets further from 24.9
        return max(0, 100 - (bmi - 24.9) * 10)

def calculate_activity_score(activity_level: str, weekly_frequency: int) -> float:
    """Calculate a normalized score (0-100) based on activity level and frequency."""
    activity_multipliers = {
        "sedentary": 0.5,
        "light": 0.7,
        "moderate": 0.85,
        "active": 1.0,
        "very_active": 1.2
    }
    
    base_score = weekly_frequency * 14.28  # 100/7 to normalize weekly frequency
    multiplier = activity_multipliers.get(activity_level.lower(), 0.5)
    
    return min(100, base_score * multiplier)

def calculate_progress_score(current_weight: float, target_weight: float, 
                           current_activity: str, target_activity: str) -> float:
    """Calculate a normalized score (0-100) based on progress towards goals."""
    weight_progress = 0
    activity_progress = 0
    
    # Calculate weight progress
    if target_weight:
        weight_diff = abs(current_weight - target_weight)
        if weight_diff > 0:
            weight_progress = min(100, (1 / weight_diff) * 100)
    
    # Calculate activity progress
    activity_levels = ["sedentary", "light", "moderate", "active", "very_active"]
    if target_activity:
        current_index = activity_levels.index(current_activity.lower())
        target_index = activity_levels.index(target_activity.lower())
        activity_progress = min(100, abs(target_index - current_index) * 25)
    
    return (weight_progress + activity_progress) / 2

def calculate_habits_score(exercise_types: list, session_duration: str, 
                         fitness_level: str) -> float:
    """Calculate a normalized score (0-100) based on exercise habits."""
    score = 0
    
    # Exercise variety
    if exercise_types:
        score += min(100, len(exercise_types) * 20)
    
    # Session duration
    duration_scores = {
        "15-30min": 60,
        "30-60min": 80,
        "60+ min": 100
    }
    score += duration_scores.get(session_duration, 0)
    
    # Fitness level
    level_scores = {
        "beginner": 60,
        "intermediate": 80,
        "advanced": 100
    }
    if fitness_level:
        score += level_scores.get(fitness_level.lower(), 0)
    else:
        score += 50  # Default score for missing fitness level
    
    return score / 3

def calculate_wellness_score(health_data: Dict[str, Any]) -> float:
    """Calculate overall wellness score (0-100) based on various health metrics."""
    bmi = calculate_bmi(health_data["weight"], health_data["height"])
    bmi_score = calculate_bmi_score(bmi)
    
    activity_score = calculate_activity_score(
        health_data["activity_level"],
        health_data["weekly_activity_frequency"]
    )
    
    progress_score = calculate_progress_score(
        health_data["weight"],
        health_data.get("target_weight", health_data["weight"]),
        health_data["activity_level"],
        health_data.get("target_activity_level", health_data["activity_level"])
    )
    
    habits_score = calculate_habits_score(
        health_data["exercise_types"],
        health_data["average_session_duration"],
        health_data["fitness_level"]
    )
    
    # Weighted average of all scores
    wellness_score = (
        bmi_score * 0.3 +
        activity_score * 0.3 +
        progress_score * 0.2 +
        habits_score * 0.2
    )
    
    return round(wellness_score, 2) 