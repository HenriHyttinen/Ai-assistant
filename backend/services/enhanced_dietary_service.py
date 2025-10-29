"""
Enhanced Dietary Restrictions and Personalization Service

This service provides advanced dietary restriction handling, cultural/religious considerations,
and sophisticated personalization features for AI meal planning.
"""

from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class DietaryRestrictionType(Enum):
    """Types of dietary restrictions"""
    ALLERGY = "allergy"
    INTOLERANCE = "intolerance"
    RELIGIOUS = "religious"
    CULTURAL = "cultural"
    MEDICAL = "medical"
    ETHICAL = "ethical"
    PREFERENCE = "preference"

class DietarySeverity(Enum):
    """Severity levels for dietary restrictions"""
    MILD = "mild"  # Can have small amounts
    MODERATE = "moderate"  # Should avoid but not life-threatening
    SEVERE = "severe"  # Must completely avoid
    CRITICAL = "critical"  # Life-threatening

@dataclass
class DietaryRestriction:
    """Represents a dietary restriction with context"""
    name: str
    restriction_type: DietaryRestrictionType
    severity: DietarySeverity
    excluded_ingredients: List[str]
    excluded_cooking_methods: List[str] = None
    cultural_context: Optional[str] = None
    notes: Optional[str] = None

class EnhancedDietaryService:
    """Enhanced service for handling complex dietary restrictions and personalization"""
    
    def __init__(self):
        self.dietary_restrictions_db = self._initialize_dietary_restrictions()
        self.cultural_dietary_patterns = self._initialize_cultural_patterns()
        self.medical_dietary_considerations = self._initialize_medical_patterns()
        
    def _initialize_dietary_restrictions(self) -> Dict[str, DietaryRestriction]:
        """Initialize comprehensive dietary restrictions database"""
        return {
            # Allergies
            "peanut_allergy": DietaryRestriction(
                name="Peanut Allergy",
                restriction_type=DietaryRestrictionType.ALLERGY,
                severity=DietarySeverity.CRITICAL,
                excluded_ingredients=["peanuts", "peanut oil", "peanut butter", "groundnuts"],
                excluded_cooking_methods=["deep frying with peanut oil"],
                notes="Life-threatening allergy - must avoid all peanut products"
            ),
            "tree_nut_allergy": DietaryRestriction(
                name="Tree Nut Allergy",
                restriction_type=DietaryRestrictionType.ALLERGY,
                severity=DietarySeverity.CRITICAL,
                excluded_ingredients=["almonds", "walnuts", "cashews", "pistachios", "hazelnuts", "pecans", "macadamia nuts"],
                notes="Life-threatening allergy - must avoid all tree nuts"
            ),
            "shellfish_allergy": DietaryRestriction(
                name="Shellfish Allergy",
                restriction_type=DietaryRestrictionType.ALLERGY,
                severity=DietarySeverity.CRITICAL,
                excluded_ingredients=["shrimp", "crab", "lobster", "mussels", "oysters", "scallops", "clams"],
                notes="Life-threatening allergy - must avoid all shellfish"
            ),
            "dairy_allergy": DietaryRestriction(
                name="Dairy Allergy",
                restriction_type=DietaryRestrictionType.ALLERGY,
                severity=DietarySeverity.SEVERE,
                excluded_ingredients=["milk", "cheese", "yogurt", "butter", "cream", "whey", "casein"],
                notes="Must avoid all dairy products"
            ),
            "egg_allergy": DietaryRestriction(
                name="Egg Allergy",
                restriction_type=DietaryRestrictionType.ALLERGY,
                severity=DietarySeverity.SEVERE,
                excluded_ingredients=["eggs", "egg whites", "egg yolks", "mayonnaise", "hollandaise"],
                notes="Must avoid all egg products"
            ),
            "soy_allergy": DietaryRestriction(
                name="Soy Allergy",
                restriction_type=DietaryRestrictionType.ALLERGY,
                severity=DietarySeverity.SEVERE,
                excluded_ingredients=["soy", "soybeans", "tofu", "tempeh", "miso", "soy sauce", "edamame"],
                notes="Must avoid all soy products"
            ),
            "wheat_allergy": DietaryRestriction(
                name="Wheat Allergy",
                restriction_type=DietaryRestrictionType.ALLERGY,
                severity=DietarySeverity.SEVERE,
                excluded_ingredients=["wheat", "wheat flour", "bread", "pasta", "couscous", "bulgur"],
                notes="Must avoid all wheat products"
            ),
            "sesame_allergy": DietaryRestriction(
                name="Sesame Allergy",
                restriction_type=DietaryRestrictionType.ALLERGY,
                severity=DietarySeverity.SEVERE,
                excluded_ingredients=["sesame", "sesame oil", "tahini", "halva"],
                notes="Must avoid all sesame products"
            ),
            
            # Intolerances
            "lactose_intolerance": DietaryRestriction(
                name="Lactose Intolerance",
                restriction_type=DietaryRestrictionType.INTOLERANCE,
                severity=DietarySeverity.MODERATE,
                excluded_ingredients=["milk", "fresh cheese", "yogurt", "ice cream"],
                notes="Can tolerate aged cheeses and lactose-free products"
            ),
            "gluten_intolerance": DietaryRestriction(
                name="Gluten Intolerance",
                restriction_type=DietaryRestrictionType.INTOLERANCE,
                severity=DietarySeverity.MODERATE,
                excluded_ingredients=["wheat", "barley", "rye", "triticale"],
                notes="Must avoid gluten-containing grains"
            ),
            "fodmap_intolerance": DietaryRestriction(
                name="FODMAP Intolerance",
                restriction_type=DietaryRestrictionType.INTOLERANCE,
                severity=DietarySeverity.MODERATE,
                excluded_ingredients=["onions", "garlic", "apples", "mangoes", "cauliflower", "mushrooms", "legumes"],
                notes="Low FODMAP diet for IBS management"
            ),
            
            # Religious/Cultural
            "halal": DietaryRestriction(
                name="Halal",
                restriction_type=DietaryRestrictionType.RELIGIOUS,
                severity=DietarySeverity.SEVERE,
                excluded_ingredients=["pork", "alcohol", "gelatin", "non-halal meat"],
                excluded_cooking_methods=["cooking with alcohol", "non-halal meat preparation"],
                cultural_context="Islamic dietary laws",
                notes="Must follow Islamic dietary guidelines"
            ),
            "kosher": DietaryRestriction(
                name="Kosher",
                restriction_type=DietaryRestrictionType.RELIGIOUS,
                severity=DietarySeverity.SEVERE,
                excluded_ingredients=["pork", "shellfish", "mixing meat and dairy"],
                excluded_cooking_methods=["mixing meat and dairy", "non-kosher preparation"],
                cultural_context="Jewish dietary laws",
                notes="Must follow Jewish dietary guidelines"
            ),
            "jain": DietaryRestriction(
                name="Jain",
                restriction_type=DietaryRestrictionType.RELIGIOUS,
                severity=DietarySeverity.SEVERE,
                excluded_ingredients=["root vegetables", "onions", "garlic", "potatoes", "carrots", "beets"],
                cultural_context="Jainism dietary principles",
                notes="Avoids root vegetables and certain foods"
            ),
            "buddhist_vegetarian": DietaryRestriction(
                name="Buddhist Vegetarian",
                restriction_type=DietaryRestrictionType.RELIGIOUS,
                severity=DietarySeverity.SEVERE,
                excluded_ingredients=["meat", "fish", "poultry", "eggs", "dairy"],
                cultural_context="Buddhist dietary principles",
                notes="Strict vegetarian diet following Buddhist principles"
            ),
            
            # Medical
            "diabetes": DietaryRestriction(
                name="Diabetes Management",
                restriction_type=DietaryRestrictionType.MEDICAL,
                severity=DietarySeverity.MODERATE,
                excluded_ingredients=["high-sugar foods", "refined carbohydrates", "sugary drinks"],
                notes="Focus on low glycemic index foods"
            ),
            "hypertension": DietaryRestriction(
                name="Hypertension Management",
                restriction_type=DietaryRestrictionType.MEDICAL,
                severity=DietarySeverity.MODERATE,
                excluded_ingredients=["high-sodium foods", "processed meats", "canned foods"],
                notes="Low sodium diet for blood pressure management"
            ),
            "heart_disease": DietaryRestriction(
                name="Heart Disease Prevention",
                restriction_type=DietaryRestrictionType.MEDICAL,
                severity=DietarySeverity.MODERATE,
                excluded_ingredients=["trans fats", "saturated fats", "high-cholesterol foods"],
                notes="Heart-healthy diet focusing on lean proteins and healthy fats"
            ),
            "kidney_disease": DietaryRestriction(
                name="Kidney Disease Management",
                restriction_type=DietaryRestrictionType.MEDICAL,
                severity=DietarySeverity.MODERATE,
                excluded_ingredients=["high-potassium foods", "high-phosphorus foods", "excess protein"],
                notes="Renal diet with controlled protein, potassium, and phosphorus"
            ),
            
            # Ethical
            "vegan": DietaryRestriction(
                name="Vegan",
                restriction_type=DietaryRestrictionType.ETHICAL,
                severity=DietarySeverity.SEVERE,
                excluded_ingredients=["meat", "fish", "poultry", "dairy", "eggs", "honey", "gelatin"],
                notes="No animal products or by-products"
            ),
            "vegetarian": DietaryRestriction(
                name="Vegetarian",
                restriction_type=DietaryRestrictionType.ETHICAL,
                severity=DietarySeverity.MODERATE,
                excluded_ingredients=["meat", "fish", "poultry"],
                notes="No meat, fish, or poultry but may include dairy and eggs"
            ),
            "pescatarian": DietaryRestriction(
                name="Pescatarian",
                restriction_type=DietaryRestrictionType.ETHICAL,
                severity=DietarySeverity.MILD,
                excluded_ingredients=["meat", "poultry"],
                notes="Includes fish and seafood but no meat or poultry"
            ),
        }
    
    def _initialize_cultural_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize cultural dietary patterns and preferences"""
        return {
            "mediterranean": {
                "preferred_ingredients": ["olive oil", "tomatoes", "garlic", "herbs", "fish", "legumes"],
                "cooking_methods": ["grilling", "roasting", "sautéing"],
                "avoided_ingredients": ["processed foods", "excessive dairy"],
                "cultural_notes": "Focus on fresh, seasonal ingredients and healthy fats"
            },
            "asian": {
                "preferred_ingredients": ["rice", "soy sauce", "ginger", "garlic", "vegetables", "fish"],
                "cooking_methods": ["stir-frying", "steaming", "braising"],
                "avoided_ingredients": ["excessive dairy", "heavy creams"],
                "cultural_notes": "Balance of flavors and textures, emphasis on vegetables"
            },
            "indian": {
                "preferred_ingredients": ["spices", "legumes", "rice", "vegetables", "yogurt"],
                "cooking_methods": ["currying", "tandoori", "steaming"],
                "avoided_ingredients": ["beef", "pork"],
                "cultural_notes": "Rich in spices and vegetarian options"
            },
            "mexican": {
                "preferred_ingredients": ["beans", "corn", "chilies", "tomatoes", "avocado"],
                "cooking_methods": ["grilling", "braising", "frying"],
                "avoided_ingredients": ["excessive dairy"],
                "cultural_notes": "Bold flavors and fresh ingredients"
            },
            "middle_eastern": {
                "preferred_ingredients": ["olive oil", "herbs", "legumes", "grains", "vegetables"],
                "cooking_methods": ["grilling", "roasting", "braising"],
                "avoided_ingredients": ["pork", "alcohol"],
                "cultural_notes": "Often follows halal dietary laws"
            }
        }
    
    def _initialize_medical_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize medical dietary considerations"""
        return {
            "autoimmune": {
                "avoided_ingredients": ["gluten", "dairy", "nightshades", "processed foods"],
                "preferred_ingredients": ["anti-inflammatory foods", "omega-3 rich foods"],
                "notes": "Anti-inflammatory diet for autoimmune conditions"
            },
            "digestive_issues": {
                "avoided_ingredients": ["spicy foods", "acidic foods", "high-fiber foods"],
                "preferred_ingredients": ["easily digestible foods", "probiotic foods"],
                "notes": "Gentle on digestive system"
            },
            "weight_management": {
                "avoided_ingredients": ["high-calorie foods", "processed foods", "sugary drinks"],
                "preferred_ingredients": ["lean proteins", "vegetables", "whole grains"],
                "notes": "Calorie-controlled and nutrient-dense"
            }
        }
    
    def analyze_dietary_restrictions(self, user_restrictions: List[str]) -> Dict[str, Any]:
        """
        Analyze user's dietary restrictions and return comprehensive dietary profile
        
        Args:
            user_restrictions: List of dietary restriction names
            
        Returns:
            Dictionary with analyzed dietary profile
        """
        analyzed_restrictions = []
        excluded_ingredients = set()
        excluded_cooking_methods = set()
        severity_levels = []
        cultural_contexts = []
        medical_considerations = []
        
        for restriction_name in user_restrictions:
            restriction_key = restriction_name.lower().replace(" ", "_")
            
            if restriction_key in self.dietary_restrictions_db:
                restriction = self.dietary_restrictions_db[restriction_key]
                analyzed_restrictions.append(restriction)
                
                # Collect excluded ingredients
                excluded_ingredients.update(restriction.excluded_ingredients)
                
                # Collect excluded cooking methods
                if restriction.excluded_cooking_methods:
                    excluded_cooking_methods.update(restriction.excluded_cooking_methods)
                
                # Track severity levels
                severity_levels.append(restriction.severity.value)
                
                # Track cultural contexts
                if restriction.cultural_context:
                    cultural_contexts.append(restriction.cultural_context)
                
                # Track medical considerations
                if restriction.restriction_type == DietaryRestrictionType.MEDICAL:
                    medical_considerations.append(restriction.name)
        
        # Determine overall severity
        overall_severity = self._determine_overall_severity(severity_levels)
        
        # Get dietary compatibility recommendations
        compatibility_recommendations = self._get_compatibility_recommendations(analyzed_restrictions)
        
        return {
            "analyzed_restrictions": analyzed_restrictions,
            "excluded_ingredients": list(excluded_ingredients),
            "excluded_cooking_methods": list(excluded_cooking_methods),
            "overall_severity": overall_severity,
            "cultural_contexts": cultural_contexts,
            "medical_considerations": medical_considerations,
            "compatibility_recommendations": compatibility_recommendations,
            "dietary_complexity_score": self._calculate_dietary_complexity_score(analyzed_restrictions)
        }
    
    def _determine_overall_severity(self, severity_levels: List[str]) -> str:
        """Determine overall severity based on individual restriction severities"""
        if not severity_levels:
            return "none"
        
        severity_hierarchy = {
            "critical": 4,
            "severe": 3,
            "moderate": 2,
            "mild": 1
        }
        
        max_severity = max(severity_levels, key=lambda x: severity_hierarchy.get(x, 0))
        return max_severity
    
    def _get_compatibility_recommendations(self, restrictions: List[DietaryRestriction]) -> List[str]:
        """Get recommendations for managing multiple dietary restrictions"""
        recommendations = []
        
        # Check for conflicting restrictions
        has_vegan = any(r.name.lower() == "vegan" for r in restrictions)
        has_vegetarian = any(r.name.lower() == "vegetarian" for r in restrictions)
        has_pescatarian = any(r.name.lower() == "pescatarian" for r in restrictions)
        
        if has_vegan and (has_vegetarian or has_pescatarian):
            recommendations.append("Vegan diet is most restrictive - focus on plant-based options")
        
        # Check for religious restrictions
        religious_restrictions = [r for r in restrictions if r.restriction_type == DietaryRestrictionType.RELIGIOUS]
        if len(religious_restrictions) > 1:
            recommendations.append("Multiple religious dietary laws detected - ensure all requirements are met")
        
        # Check for medical restrictions
        medical_restrictions = [r for r in restrictions if r.restriction_type == DietaryRestrictionType.MEDICAL]
        if medical_restrictions:
            recommendations.append("Medical dietary restrictions present - prioritize health requirements")
        
        return recommendations
    
    def _calculate_dietary_complexity_score(self, restrictions: List[DietaryRestriction]) -> int:
        """Calculate a complexity score for dietary restrictions (0-100)"""
        if not restrictions:
            return 0
        
        score = 0
        
        # Base score for number of restrictions
        score += len(restrictions) * 10
        
        # Additional points for severity
        for restriction in restrictions:
            if restriction.severity == DietarySeverity.CRITICAL:
                score += 20
            elif restriction.severity == DietarySeverity.SEVERE:
                score += 15
            elif restriction.severity == DietarySeverity.MODERATE:
                score += 10
            elif restriction.severity == DietarySeverity.MILD:
                score += 5
        
        # Additional points for restriction types
        type_scores = {
            DietaryRestrictionType.ALLERGY: 15,
            DietaryRestrictionType.RELIGIOUS: 10,
            DietaryRestrictionType.MEDICAL: 12,
            DietaryRestrictionType.INTOLERANCE: 8,
            DietaryRestrictionType.ETHICAL: 5,
            DietaryRestrictionType.CULTURAL: 3,
            DietaryRestrictionType.PREFERENCE: 2
        }
        
        for restriction in restrictions:
            score += type_scores.get(restriction.restriction_type, 0)
        
        return min(score, 100)  # Cap at 100
    
    def get_personalized_dietary_guidance(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get personalized dietary guidance based on user profile
        
        Args:
            user_profile: User's health profile, preferences, and restrictions
            
        Returns:
            Personalized dietary guidance
        """
        guidance = {
            "primary_dietary_focus": [],
            "nutrient_priorities": [],
            "meal_timing_recommendations": [],
            "cooking_method_preferences": [],
            "ingredient_substitutions": {},
            "cultural_adaptations": [],
            "medical_considerations": []
        }
        
        # Analyze dietary restrictions
        if "dietary_restrictions" in user_profile:
            dietary_analysis = self.analyze_dietary_restrictions(user_profile["dietary_restrictions"])
            guidance["dietary_analysis"] = dietary_analysis
        
        # Health-based recommendations
        if "health_conditions" in user_profile:
            for condition in user_profile["health_conditions"]:
                if condition in self.medical_dietary_considerations:
                    medical_pattern = self.medical_dietary_considerations[condition]
                    guidance["medical_considerations"].append(medical_pattern)
        
        # Cultural adaptations
        if "cultural_background" in user_profile:
            culture = user_profile["cultural_background"]
            if culture in self.cultural_dietary_patterns:
                guidance["cultural_adaptations"].append(self.cultural_dietary_patterns[culture])
        
        # Age and life stage considerations
        if "age" in user_profile:
            age = user_profile["age"]
            if age < 18:
                guidance["nutrient_priorities"].append("Focus on growth and development nutrients")
            elif age > 65:
                guidance["nutrient_priorities"].append("Focus on bone health and cognitive function")
        
        # Activity level considerations
        if "activity_level" in user_profile:
            activity = user_profile["activity_level"].lower()
            if activity in ["high", "very_high"]:
                guidance["nutrient_priorities"].append("Increased protein and carbohydrate needs")
                guidance["meal_timing_recommendations"].append("Pre and post-workout nutrition")
        
        return guidance
    
    def suggest_ingredient_substitutions(self, excluded_ingredients: List[str], 
                                       cuisine_type: str = None) -> Dict[str, List[str]]:
        """
        Suggest ingredient substitutions for excluded ingredients
        
        Args:
            excluded_ingredients: List of ingredients to avoid
            cuisine_type: Optional cuisine type for culturally appropriate substitutions
            
        Returns:
            Dictionary mapping excluded ingredients to substitution suggestions
        """
        substitutions = {
            "dairy": ["coconut milk", "almond milk", "oat milk", "cashew cream"],
            "gluten": ["rice flour", "almond flour", "coconut flour", "quinoa flour"],
            "eggs": ["flax eggs", "chia eggs", "applesauce", "banana"],
            "meat": ["tofu", "tempeh", "seitan", "mushrooms", "legumes"],
            "nuts": ["seeds", "sunflower seeds", "pumpkin seeds", "coconut"],
            "soy": ["coconut aminos", "tamari", "miso alternatives"],
            "sugar": ["stevia", "monk fruit", "erythritol", "maple syrup"],
            "salt": ["herbs", "spices", "lemon juice", "vinegar"]
        }
        
        result = {}
        for ingredient in excluded_ingredients:
            ingredient_lower = ingredient.lower()
            for key, subs in substitutions.items():
                if key in ingredient_lower:
                    result[ingredient] = subs
                    break
        
        return result


