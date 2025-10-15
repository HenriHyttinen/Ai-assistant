"""
Data normalization utilities for AI processing.
This module handles conversion between different measurement systems
and ensures data is in the correct format for AI analysis.
"""

from typing import Dict, Any, Optional
from decimal import Decimal, ROUND_HALF_UP

def normalize_weight(weight: float, measurement_system: str) -> float:
    """
    Normalize weight to kg for AI processing.
    
    Args:
        weight: Weight value
        measurement_system: 'metric' or 'imperial'
    
    Returns:
        Weight in kg
    """
    if measurement_system == 'imperial':
        # Convert pounds to kg (1 lb = 0.453592 kg)
        return round(weight * 0.453592, 2)
    return round(weight, 2)  # Already in kg

def normalize_height(height: float, measurement_system: str) -> float:
    """
    Normalize height to cm for AI processing.
    
    Args:
        height: Height value
        measurement_system: 'metric' or 'imperial'
    
    Returns:
        Height in cm
    """
    if measurement_system == 'imperial':
        # Convert inches to cm (1 inch = 2.54 cm)
        return round(height * 2.54, 2)
    return round(height, 2)  # Already in cm

def normalize_health_data_for_ai(health_data: Dict[str, Any], user_settings: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Normalize health data for AI processing according to task requirements.
    
    This function ensures all metrics are in the correct units (kg, cm) and
    removes PII while maintaining data structure for AI consumption.
    
    Args:
        health_data: Raw health data from user profile
        user_settings: User settings including measurement system preference
    
    Returns:
        Normalized data structure for AI processing
    """
    # Default to metric if no settings provided
    measurement_system = 'metric'
    if user_settings and 'measurement_system' in user_settings:
        measurement_system = user_settings['measurement_system']
    
    # Create normalized structure
    normalized_data = {
        "user_metrics": {
            "current_state": {},
            "target_state": {},
            "preferences": [],
            "restrictions": [],
            "activity_metrics": {},
            "fitness_assessment": {}
        }
    }
    
    # Normalize current state metrics
    if 'weight' in health_data and health_data['weight']:
        normalized_data["user_metrics"]["current_state"]["weight"] = normalize_weight(
            health_data['weight'], measurement_system
        )
    
    if 'height' in health_data and health_data['height']:
        normalized_data["user_metrics"]["current_state"]["height"] = normalize_height(
            health_data['height'], measurement_system
        )
    
    if 'activity_level' in health_data:
        normalized_data["user_metrics"]["current_state"]["activity_level"] = health_data['activity_level']
    
    # Normalize target state metrics
    if 'target_weight' in health_data and health_data['target_weight']:
        normalized_data["user_metrics"]["target_state"]["weight"] = normalize_weight(
            health_data['target_weight'], measurement_system
        )
    
    if 'target_activity_level' in health_data:
        normalized_data["user_metrics"]["target_state"]["activity_level"] = health_data['target_activity_level']
    
    # Process preferences (remove PII, keep relevant data)
    if 'dietary_preferences' in health_data and health_data['dietary_preferences']:
        try:
            import json
            preferences = json.loads(health_data['dietary_preferences']) if isinstance(health_data['dietary_preferences'], str) else health_data['dietary_preferences']
            normalized_data["user_metrics"]["preferences"] = preferences
        except (json.JSONDecodeError, TypeError):
            normalized_data["user_metrics"]["preferences"] = []
    
    # Process restrictions
    if 'dietary_restrictions' in health_data and health_data['dietary_restrictions']:
        try:
            import json
            restrictions = json.loads(health_data['dietary_restrictions']) if isinstance(health_data['dietary_restrictions'], str) else health_data['dietary_restrictions']
            normalized_data["user_metrics"]["restrictions"] = restrictions
        except (json.JSONDecodeError, TypeError):
            normalized_data["user_metrics"]["restrictions"] = []
    
    # Activity metrics
    if 'weekly_activity_frequency' in health_data:
        normalized_data["user_metrics"]["activity_metrics"]["weekly_frequency"] = health_data['weekly_activity_frequency']
    
    if 'exercise_types' in health_data and health_data['exercise_types']:
        try:
            import json
            exercise_types = json.loads(health_data['exercise_types']) if isinstance(health_data['exercise_types'], str) else health_data['exercise_types']
            normalized_data["user_metrics"]["activity_metrics"]["exercise_types"] = exercise_types
        except (json.JSONDecodeError, TypeError):
            normalized_data["user_metrics"]["activity_metrics"]["exercise_types"] = []
    
    if 'average_session_duration' in health_data:
        normalized_data["user_metrics"]["activity_metrics"]["session_duration"] = health_data['average_session_duration']
    
    # Fitness assessment
    if 'fitness_level' in health_data:
        normalized_data["user_metrics"]["fitness_assessment"]["level"] = health_data['fitness_level']
    
    if 'endurance_level' in health_data:
        normalized_data["user_metrics"]["fitness_assessment"]["endurance"] = health_data['endurance_level']
    
    if 'current_endurance_minutes' in health_data:
        normalized_data["user_metrics"]["fitness_assessment"]["endurance_minutes"] = health_data['current_endurance_minutes']
    
    if 'pushup_count' in health_data:
        normalized_data["user_metrics"]["fitness_assessment"]["pushup_count"] = health_data['pushup_count']
    
    if 'squat_count' in health_data:
        normalized_data["user_metrics"]["fitness_assessment"]["squat_count"] = health_data['squat_count']
    
    return normalized_data

def convert_weight_for_display(weight_kg: float, measurement_system: str) -> float:
    """
    Convert weight from kg to display units based on user preference.
    
    Args:
        weight_kg: Weight in kg
        measurement_system: 'metric' or 'imperial'
    
    Returns:
        Weight in display units
    """
    if measurement_system == 'imperial':
        # Convert kg to pounds (1 kg = 2.20462 lbs)
        return round(weight_kg * 2.20462, 1)
    return round(weight_kg, 1)  # Already in kg

def convert_height_for_display(height_cm: float, measurement_system: str) -> float:
    """
    Convert height from cm to display units based on user preference.
    
    Args:
        height_cm: Height in cm
        measurement_system: 'metric' or 'imperial'
    
    Returns:
        Height in display units
    """
    if measurement_system == 'imperial':
        # Convert cm to inches (1 cm = 0.393701 inches)
        return round(height_cm * 0.393701, 1)
    return round(height_cm, 1)  # Already in cm
