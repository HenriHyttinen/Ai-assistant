from typing import Dict, Any, List
import os
import re
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client only if API key is available
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
else:
    client = None

print("AI imports are working!")

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
        'weight_loss': "Your goal is weight loss. Focus on creating sustainable habits that will help you achieve a healthy calorie deficit.",
        'muscle_gain': "Your goal is muscle gain. Prioritize strength training and proper nutrition to support muscle growth.",
        'endurance': "Your goal is improving endurance. Focus on cardiovascular fitness and stamina building.",
        'strength': "Your goal is building strength. Concentrate on progressive resistance training and proper form.",
        'general_fitness': "Your goal is general fitness. Maintain a balanced approach to health and wellness."
    }
    
    mock_insights = {
        'en': {
            "status_analysis": goal_analysis.get(fitness_goal, goal_analysis['general_fitness']),
            "recommendations": goal_recommendations.get(fitness_goal, goal_recommendations['general_fitness']),
            "strengths": [
                "Consistent exercise routine",
                "Good understanding of your fitness goals"
            ],
            "improvements": [
                "Focus on sleep quality and duration",
                "Consider adding more variety to your routine"
            ]
        },
        'es': {
            "status_analysis": "Basándome en tu perfil de salud, estás en un buen camino hacia el bienestar. Tu nivel de actividad actual y objetivos de fitness muestran un impulso positivo.",
            "recommendations": [
                "Aumenta tu ingesta diaria de agua a 8-10 vasos",
                "Agrega 15 minutos de estiramiento a tu rutina matutina",
                "Intenta incorporar más alimentos integrales a tu dieta"
            ],
            "strengths": [
                "Rutina de ejercicio consistente",
                "Buena comprensión de tus objetivos de fitness"
            ],
            "improvements": [
                "Enfócate en la calidad y duración del sueño",
                "Considera agregar entrenamiento de fuerza a tu rutina"
            ]
        },
        'fr': {
            "status_analysis": "Basé sur votre profil de santé, vous êtes sur la bonne voie vers le bien-être. Votre niveau d'activité actuel et vos objectifs de fitness montrent un élan positif.",
            "recommendations": [
                "Augmentez votre apport quotidien en eau à 8-10 verres",
                "Ajoutez 15 minutes d'étirement à votre routine matinale",
                "Essayez d'incorporer plus d'aliments entiers dans votre alimentation"
            ],
            "strengths": [
                "Routine d'exercice cohérente",
                "Bonne compréhension de vos objectifs de fitness"
            ],
            "improvements": [
                "Concentrez-vous sur la qualité et la durée du sommeil",
                "Considérez ajouter l'entraînement en force à votre routine"
            ]
        },
        'de': {
            "status_analysis": "Basierend auf Ihrem Gesundheitsprofil sind Sie auf dem richtigen Weg zum Wohlbefinden. Ihr aktuelles Aktivitätsniveau und Ihre Fitnessziele zeigen positive Dynamik.",
            "recommendations": [
                "Erhöhen Sie Ihre tägliche Wasseraufnahme auf 8-10 Gläser",
                "Fügen Sie 15 Minuten Dehnen zu Ihrer Morgenroutine hinzu",
                "Versuchen Sie, mehr Vollwertkost in Ihre Ernährung einzubeziehen"
            ],
            "strengths": [
                "Konsistente Trainingsroutine",
                "Gutes Verständnis Ihrer Fitnessziele"
            ],
            "improvements": [
                "Konzentrieren Sie sich auf Schlafqualität und -dauer",
                "Erwägen Sie, Krafttraining zu Ihrer Routine hinzuzufügen"
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
            restriction_lower = restriction.lower().replace('_', ' ')
            if restriction_lower in restriction_keywords:
                keywords = restriction_keywords[restriction_lower]
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
    """Get personalized health insights based on user data with proper normalization."""
    
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
    {language_instruction}
    
    Here's someone's health info (normalized for analysis) - give them personalized advice:
    
    Current State:
    - Height: {current_state.get('height', 'N/A')} cm
    - Weight: {current_state.get('weight', 'N/A')} kg
    - Activity Level: {current_state.get('activity_level', 'N/A')}
    - Fitness Goal: {current_state.get('fitness_goal', 'N/A')}
    
    Target State:
    - Target Weight: {target_state.get('weight', 'N/A')} kg
    - Target Activity Level: {target_state.get('activity_level', 'N/A')}
    
    Activity Metrics:
    - Weekly Activity: {activity_metrics.get('weekly_frequency', 'N/A')} days
    - Exercise Types: {', '.join(activity_metrics.get('exercise_types', []))}
    - Session Duration: {activity_metrics.get('session_duration', 'N/A')}
    
    Fitness Assessment:
    - Fitness Level: {fitness_assessment.get('level', 'N/A')}
    - Endurance Level: {fitness_assessment.get('endurance', 'N/A')}/10
    - Endurance Minutes: {fitness_assessment.get('endurance_minutes', 'N/A')}
    - Pushup Count: {fitness_assessment.get('pushup_count', 'N/A')}
    - Squat Count: {fitness_assessment.get('squat_count', 'N/A')}
    
    Preferences: {', '.join(preferences) if preferences else 'None'}
    Dietary Restrictions: {', '.join(restrictions) if restrictions else 'None'}
    
    Keep in mind:
    - Don't suggest anything that goes against their dietary restrictions
    - Make sure recommendations match their fitness level
    - Focus on their specific fitness goal: {current_state.get('fitness_goal', 'N/A')}
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
        validated_insights = validate_ai_response(structured_insights, dietary_restrictions)
        
        return validated_insights
        
    except Exception as e:
        # Error messages in different languages
        error_messages = {
            'en': {
                "status_analysis": "Unable to generate analysis at this time.",
                "recommendations": ["Please try again later."]
            },
            'es': {
                "status_analysis": "No se puede generar el análisis en este momento.",
                "recommendations": ["Por favor, inténtelo de nuevo más tarde."]
            },
            'fr': {
                "status_analysis": "Impossible de générer l'analyse pour le moment.",
                "recommendations": ["Veuillez réessayer plus tard."]
            },
            'de': {
                "status_analysis": "Analyse kann derzeit nicht generiert werden.",
                "recommendations": ["Bitte versuchen Sie es später erneut."]
            }
        }
        
        error_msg = error_messages.get(language, error_messages['en'])
        
        return {
            "error": f"Failed to generate insights: {str(e)}",
            "status_analysis": error_msg["status_analysis"],
            "recommendations": error_msg["recommendations"],
            "strengths": [],
            "improvements": []
        }

def generate_weekly_summary(health_data: Dict[str, Any], 
                          activity_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate a weekly summary of health progress and recommendations."""
    
    # Prepare activity summary
    activity_summary = {
        "total_activities": len(activity_logs),
        "total_duration": sum(log["duration"] for log in activity_logs),
        "activity_types": list(set(log["activity_type"] for log in activity_logs))
    }
    
    prompt = f"""
    Based on the following weekly activity summary and health profile, provide a weekly progress report:
    
    Health Profile:
    - Current Weight: {health_data['weight']} kg
    - Target Weight: {health_data.get('target_weight', 'Not set')} kg
    - Activity Level: {health_data['activity_level']}
    - Fitness Goal: {health_data['fitness_goal']}
    
    Weekly Activity Summary:
    - Total Activities: {activity_summary['total_activities']}
    - Total Duration: {activity_summary['total_duration']} minutes
    - Activity Types: {', '.join(activity_summary['activity_types'])}
    
    Please provide:
    1. A brief weekly progress summary
    2. 2 achievements to celebrate
    3. 2 specific goals for the next week
    4. 1 motivational message
    """
    
    # Check if OpenAI client is available
    if not client:
        print("OpenAI API key not available, using mock weekly summary")
        return {
            "week_summary": "Great progress this week! Keep up the excellent work on your health journey.",
            "achievements": ["Consistent exercise routine", "Healthy eating habits"],
            "next_week_goals": ["Increase water intake", "Add more variety to workouts"],
            "motivation": "You're making fantastic progress! Every small step counts towards your bigger health goals."
        }
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a supportive health and wellness coach. Provide an encouraging weekly summary that celebrates progress and sets clear goals."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=400
        )
        
        summary = response.choices[0].message.content
        
        # Parse the response into structured format
        sections = summary.split('\n\n')
        structured_summary = {
            "progress_summary": sections[0] if len(sections) > 0 else "",
            "achievements": sections[1].split('\n')[1:] if len(sections) > 1 else [],
            "next_week_goals": sections[2].split('\n')[1:] if len(sections) > 2 else [],
            "motivational_message": sections[3] if len(sections) > 3 else ""
        }
        
        return structured_summary
        
    except Exception as e:
        return {
            "error": f"Failed to generate weekly summary: {str(e)}",
            "progress_summary": "Unable to generate summary at this time.",
            "achievements": [],
            "next_week_goals": [],
            "motivational_message": "Keep up the good work!"
        } 