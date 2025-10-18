from typing import Dict, Any, List
import os
import re
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client only if API key is available
api_key = os.getenv("OPENAI_API_KEY")
# For development, disable OpenAI API to improve performance
if api_key and os.getenv("USE_OPENAI", "false").lower() == "true":
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
else:
    client = None


def generate_mock_insights(language: str = 'en', fitness_goal: str = 'general_fitness') -> Dict[str, Any]:
    """Generate mock insights when OpenAI API is not available."""
    
    # Goal-specific recommendations
    goal_recommendations = {
        'weight_loss': [
            "Focus on creating a calorie deficit through diet and exercise",
            "Increase cardio activities like walking, running, or cycling",
            "Track your daily calorie intake to ensure you're in a deficit"
        ],
        'muscle_gain': [
            "Prioritize strength training 3-4 times per week",
            "Increase protein intake to support muscle growth",
            "Focus on progressive overload in your workouts"
        ],
        'endurance': [
            "Gradually increase cardio duration and intensity",
            "Include interval training in your routine",
            "Focus on consistent aerobic exercise"
        ],
        'strength': [
            "Focus on compound movements like squats and deadlifts",
            "Increase weight gradually while maintaining good form",
            "Allow adequate rest between strength training sessions"
        ],
        'general_fitness': [
            "Maintain a balanced mix of cardio and strength training",
            "Focus on overall health and wellness",
            "Keep your routine varied and enjoyable"
        ]
    }
    
    goal_analysis = {
        'weight_loss': "Your current focus on weight loss is a great step towards better health. With consistent effort, you can achieve your goals.",
        'muscle_gain': "Building muscle takes time and dedication. Your commitment to strength training will pay off with proper nutrition and rest.",
        'endurance': "Improving endurance is about building cardiovascular fitness gradually. Consistency is key to seeing progress.",
        'strength': "Strength training builds both physical and mental resilience. Focus on proper form and progressive overload.",
        'general_fitness': "Maintaining overall fitness is about balance. Keep up the good work with your varied approach to health."
    }
    
    mock_insights = {
        'en': {
            "status_analysis": goal_analysis.get(fitness_goal, goal_analysis['general_fitness']),
            "recommendations": goal_recommendations.get(fitness_goal, goal_recommendations['general_fitness']),
            "strengths": [
                "You're taking proactive steps towards better health",
                "Your commitment to tracking your progress shows dedication"
            ],
            "improvements": [
                "Consider setting specific, measurable goals",
                "Focus on consistency over intensity"
            ]
        },
        'de': {
            "status_analysis": f"Dein aktueller Fokus auf {fitness_goal} ist ein großer Schritt zu besserer Gesundheit.",
            "recommendations": [
                "Konzentriere dich auf regelmäßige Bewegung",
                "Achte auf eine ausgewogene Ernährung",
                "Setze dir realistische Ziele"
            ],
            "strengths": [
                "Du unternimmst proaktive Schritte für bessere Gesundheit",
                "Dein Engagement beim Verfolgen deines Fortschritts zeigt Hingabe"
            ],
            "improvements": [
                "Überlege dir spezifische, messbare Ziele zu setzen",
                "Konzentriere dich auf Beständigkeit statt Intensität"
            ]
        },
        'es': {
            "status_analysis": f"Tu enfoque actual en {fitness_goal} es un gran paso hacia una mejor salud.",
            "recommendations": [
                "Enfócate en el ejercicio regular",
                "Mantén una dieta equilibrada",
                "Establece objetivos realistas"
            ],
            "strengths": [
                "Estás tomando pasos proactivos hacia una mejor salud",
                "Tu compromiso con el seguimiento del progreso muestra dedicación"
            ],
            "improvements": [
                "Considera establecer objetivos específicos y medibles",
                "Enfócate en la consistencia sobre la intensidad"
            ]
        },
        'fr': {
            "status_analysis": f"Votre focus actuel sur {fitness_goal} est un grand pas vers une meilleure santé.",
            "recommendations": [
                "Concentrez-vous sur l'exercice régulier",
                "Maintenez une alimentation équilibrée",
                "Fixez des objectifs réalistes"
            ],
            "strengths": [
                "Vous prenez des mesures proactives pour une meilleure santé",
                "Votre engagement à suivre vos progrès montre de la dévotion"
            ],
            "improvements": [
                "Considérez fixer des objectifs spécifiques et mesurables",
                "Concentrez-vous sur la cohérence plutôt que sur l'intensité"
            ]
        }
    }
    
    return mock_insights.get(language, mock_insights['en'])

def validate_ai_response(insights: Dict[str, Any], dietary_restrictions: List[str]) -> Dict[str, Any]:
    """Validate AI response against user's dietary restrictions and health restrictions."""
    
    # Common dietary restriction keywords to check for
    restriction_keywords = {
        'dairy_free': ['dairy', 'milk', 'cheese', 'yogurt', 'butter', 'cream'],
        'gluten_free': ['gluten', 'wheat', 'bread', 'pasta', 'cereal'],
        'nut_free': ['nuts', 'almonds', 'walnuts', 'peanuts', 'cashews'],
        'vegetarian': ['meat', 'chicken', 'beef', 'pork', 'fish', 'seafood'],
        'vegan': ['meat', 'dairy', 'eggs', 'honey', 'chicken', 'beef', 'pork', 'fish', 'seafood'],
        'low_sodium': ['salt', 'sodium', 'salted', 'brine'],
        'diabetic_friendly': ['sugar', 'sweet', 'candy', 'soda', 'juice'],
        'low_carb': ['carbohydrates', 'carbs', 'bread', 'pasta', 'rice', 'potatoes']
    }
    
    # Filter recommendations based on restrictions
    filtered_recommendations = []
    for recommendation in insights.get('recommendations', []):
        is_valid = True
        
        # Check against each dietary restriction
        for restriction in dietary_restrictions:
            restriction_key = restriction.lower()
            if restriction_key in restriction_keywords:
                keywords = restriction_keywords[restriction_key]
                recommendation_lower = recommendation.lower()
                
                # Check if recommendation contains restricted keywords
                for keyword in keywords:
                    if keyword in recommendation_lower:
                        is_valid = False
                        break
                
                if not is_valid:
                    break
        
        if is_valid:
            filtered_recommendations.append(recommendation)
    
    # If no valid recommendations, add a generic safe recommendation
    if not filtered_recommendations:
        filtered_recommendations = [
            "Consult with a healthcare provider for personalized recommendations",
            "Focus on maintaining a balanced diet within your restrictions",
            "Consider gentle exercise appropriate for your fitness level"
        ]
    
    return {
        "status_analysis": insights.get("status_analysis", ""),
        "recommendations": filtered_recommendations,
        "strengths": insights.get("strengths", []),
        "improvements": insights.get("improvements", []),
        "validation_applied": True,
        "original_recommendations_count": len(insights.get('recommendations', [])),
        "filtered_recommendations_count": len(filtered_recommendations)
    }

def generate_health_insights(health_data: Dict[str, Any], user_settings: Dict[str, Any] = None) -> Dict[str, Any]:
    """Generate health insights based on user data."""
    
    # Import normalization utilities
    from utils.normalization import normalize_health_data_for_ai
    
    # Normalize data for AI processing (ensures kg, cm, removes PII)
    normalized_data = normalize_health_data_for_ai(health_data, user_settings)
    
    # Get user's preferred language
    language = user_settings.get('language', 'en') if user_settings else 'en'
    
    # Language mapping for AI prompts
    language_instructions = {
        'en': 'Respond in English.',
        'es': 'Responde en español.',
        'fr': 'Répondez en français.',
        'de': 'Antworten Sie auf Deutsch.'
    }
    
    language_instruction = language_instructions.get(language, 'Respond in English.')
    
    # Extract normalized values
    current_state = normalized_data["user_metrics"]["current_state"]
    target_state = normalized_data["user_metrics"]["target_state"]
    preferences = normalized_data["user_metrics"]["preferences"]
    restrictions = normalized_data["user_metrics"]["restrictions"]
    activity_metrics = normalized_data["user_metrics"]["activity_metrics"]
    fitness_assessment = normalized_data["user_metrics"]["fitness_assessment"]
    
    # Build the prompt with normalized user info
    prompt = f"""
    User Health Profile:
    Current State: {current_state}
    Target State: {target_state}
    Preferences: {preferences}
    Restrictions: {restrictions}
    Activity Metrics: {activity_metrics}
    Fitness Assessment: {fitness_assessment}
    
    Please provide personalized health insights for this user. Consider their:
    - Current health metrics and fitness level
    - Goals and target state
    - Dietary preferences and restrictions
    - Activity patterns and exercise preferences
    - Fitness assessment results
    
    Guidelines:
    - Be encouraging and supportive
    - Provide practical, actionable advice
    - Respect their dietary restrictions
    - Consider their fitness level and goals
    - Tailor all advice to help them achieve their primary fitness goal
    - Keep it practical and doable
    - All measurements are normalized (kg, cm) for consistent analysis
    
    Give them:
    1. A quick health overview
    2. 3 specific things they can do (respect their dietary needs)
    3. 2 things they're doing well
    4. 2 areas to work on
    """
    
    # Check if OpenAI client is available
    if not client:
        print("OpenAI API key not available, using mock insights")
        fitness_goal = current_state.get('fitness_goal', 'general_fitness')
        return generate_mock_insights(language, fitness_goal)
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": f"You're a friendly health coach. Give practical, personalized advice that actually helps people. {language_instruction}"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        insights = response.choices[0].message.content
        
        # Parse the response into structured format
        sections = insights.split('\n\n')
        structured_insights = {
            "status_analysis": sections[0] if len(sections) > 0 else "",
            "recommendations": sections[1].split('\n')[1:] if len(sections) > 1 else [],
            "strengths": sections[2].split('\n')[1:] if len(sections) > 2 else [],
            "improvements": sections[3].split('\n')[1:] if len(sections) > 3 else []
        }
        
        # Validate recommendations against dietary restrictions
        validated_insights = validate_ai_response(structured_insights, restrictions)
        
        return validated_insights
        
    except Exception as e:
        # If OpenAI API fails (quota exceeded, network issues, etc.), fall back to mock insights
        print(f"OpenAI API error: {e}")
        print("Falling back to mock insights...")
        fitness_goal = current_state.get('fitness_goal', 'general_fitness')
        return generate_mock_insights(language, fitness_goal)

def generate_weekly_summary(health_data: Dict[str, Any], user_settings: Dict[str, Any] = None) -> Dict[str, Any]:
    """Generate weekly health summary."""
    
    # Get user's preferred language
    language = user_settings.get('language', 'en') if user_settings else 'en'
    
    # Basic summary structure
    summary = {
        'week_overview': f"Weekly health summary for {language}",
        'key_metrics': {
            'weight_change': 0.0,
            'activity_days': 0,
            'wellness_score_change': 0.0
        },
        'achievements': [
            "Maintained consistent activity levels",
            "Tracked health metrics regularly"
        ],
        'focus_areas': [
            "Continue current routine",
            "Monitor progress towards goals"
        ],
        'recommendations': [
            "Keep up the good work",
            "Stay consistent with your routine"
        ]
    }
    
    return summary
