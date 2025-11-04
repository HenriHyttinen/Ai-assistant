"""
Recipe Quality Enhancement Service

This service analyzes and enhances AI-generated recipes to ensure:
- Professional cooking techniques
- Flavor complexity and balance
- Texture variety
- Detailed instructions
- Proper ingredient pairing
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class RecipeQualityScore:
    """Recipe quality score breakdown"""
    total_score: float  # 0-100
    flavor_complexity: float  # 0-25
    cooking_techniques: float  # 0-20
    instruction_detail: float  # 0-20
    ingredient_pairing: float  # 0-15
    texture_variety: float  # 0-10
    presentation: float  # 0-10
    improvements: List[str]  # Suggested improvements


class RecipeQualityService:
    """Service to analyze and enhance recipe quality"""
    
    # Professional flavor profiles by cuisine
    FLAVOR_PROFILES = {
        "Mediterranean": ["olive oil", "lemon", "oregano", "garlic", "basil", "rosemary"],
        "Asian": ["soy", "ginger", "sesame", "scallions", "garlic", "chili"],
        "Indian": ["garam masala", "turmeric", "cumin", "coriander", "ginger", "garlic"],
        "Mexican": ["lime", "cilantro", "cumin", "chili", "onion", "garlic"],
        "French": ["butter", "wine", "herbs de provence", "shallots", "garlic", "cream"],
        "Thai": ["coconut milk", "lemongrass", "fish sauce", "lime", "chili", "ginger"],
        "Middle Eastern": ["sumac", "tahini", "pomegranate", "za'atar", "lemon", "garlic"],
        "Italian": ["basil", "oregano", "tomatoes", "parmesan", "olive oil", "garlic"],
    }
    
    # Professional cooking techniques
    COOKING_TECHNIQUES = [
        "sear", "sauté", "roast", "braise", "steam", "grill", "braise", "caramelize",
        "deglaze", "marinate", "toast", "bloom", "reduce", "braise", "sear"
    ]
    
    # Texture indicators
    TEXTURE_INDICATORS = {
        "crispy": ["crispy", "crunchy", "toasted", "fried", "seared", "golden brown"],
        "creamy": ["creamy", "smooth", "soft", "tender", "velvety"],
        "crunchy": ["crunchy", "crisp", "fresh", "raw", "snap"],
        "tender": ["tender", "soft", "melt-in-mouth", "juicy"]
    }
    
    def analyze_recipe_quality(self, recipe: Dict[str, Any]) -> RecipeQualityScore:
        """Analyze recipe quality and return detailed score"""
        try:
            title = recipe.get("title", "")
            cuisine = recipe.get("cuisine", "").lower()
            ingredients = recipe.get("ingredients", [])
            instructions = recipe.get("instructions", [])
            summary = recipe.get("summary", "")
            
            # Extract ingredient names
            ingredient_names = [ing.get("name", "").lower() for ing in ingredients]
            ingredient_text = " ".join(ingredient_names)
            
            # Extract instruction text
            instruction_text = " ".join([
                step.get("description", "") if isinstance(step, dict) else str(step)
                for step in instructions
            ]).lower()
            
            # Score flavor complexity (0-25)
            flavor_score = self._score_flavor_complexity(ingredient_text, instruction_text, cuisine)
            
            # Score cooking techniques (0-20)
            technique_score = self._score_cooking_techniques(instruction_text, ingredient_text)
            
            # Score instruction detail (0-20)
            instruction_score = self._score_instruction_detail(instructions, instruction_text)
            
            # Score ingredient pairing (0-15)
            pairing_score = self._score_ingredient_pairing(ingredient_names, cuisine)
            
            # Score texture variety (0-10)
            texture_score = self._score_texture_variety(ingredient_text, instruction_text)
            
            # Score presentation (0-10)
            presentation_score = self._score_presentation(instruction_text, ingredient_text)
            
            # Calculate total score
            total_score = (
                flavor_score + technique_score + instruction_score + 
                pairing_score + texture_score + presentation_score
            )
            
            # Generate improvement suggestions
            improvements = self._generate_improvements(
                total_score, flavor_score, technique_score, instruction_score,
                pairing_score, texture_score, presentation_score,
                recipe, cuisine
            )
            
            return RecipeQualityScore(
                total_score=total_score,
                flavor_complexity=flavor_score,
                cooking_techniques=technique_score,
                instruction_detail=instruction_score,
                ingredient_pairing=pairing_score,
                texture_variety=texture_score,
                presentation=presentation_score,
                improvements=improvements
            )
            
        except Exception as e:
            logger.error(f"Error analyzing recipe quality: {e}")
            return RecipeQualityScore(
                total_score=50.0,
                flavor_complexity=12.5,
                cooking_techniques=10.0,
                instruction_detail=10.0,
                ingredient_pairing=7.5,
                texture_variety=5.0,
                presentation=5.0,
                improvements=["Unable to analyze recipe quality"]
            )
    
    def _score_flavor_complexity(self, ingredient_text: str, instruction_text: str, cuisine: str) -> float:
        """Score flavor complexity (0-25)"""
        score = 0.0
        cuisine = cuisine.lower()
        
        # Check for aromatics (5 points)
        aromatics = ["onion", "garlic", "ginger", "shallot", "leek"]
        if any(aromatic in ingredient_text for aromatic in aromatics):
            score += 5.0
        
        # Check for acid (5 points)
        acids = ["lemon", "lime", "vinegar", "wine", "citrus"]
        if any(acid in ingredient_text for acid in acids):
            score += 5.0
        
        # Check for herbs (5 points)
        herbs = ["basil", "cilantro", "parsley", "oregano", "rosemary", "thyme", "dill"]
        if any(herb in ingredient_text for herb in herbs):
            score += 5.0
        
        # Check for spices (5 points)
        spices = ["cumin", "coriander", "turmeric", "paprika", "garam masala", "curry"]
        if any(spice in ingredient_text for spice in spices):
            score += 5.0
        
        # Check cuisine-specific flavors (5 points)
        if cuisine in self.FLAVOR_PROFILES:
            profile_ingredients = self.FLAVOR_PROFILES[cuisine]
            matches = sum(1 for ing in profile_ingredients if ing in ingredient_text)
            if matches >= 3:
                score += 5.0
            elif matches >= 2:
                score += 3.0
            elif matches >= 1:
                score += 1.0
        
        return min(score, 25.0)
    
    def _score_cooking_techniques(self, instruction_text: str, ingredient_text: str) -> float:
        """Score cooking techniques (0-20)"""
        score = 0.0
        found_techniques = []
        
        # Check for professional techniques in instructions
        for technique in self.COOKING_TECHNIQUES:
            if technique in instruction_text:
                found_techniques.append(technique)
                score += 2.0
        
        # Bonus for multiple techniques (4 points)
        if len(found_techniques) >= 3:
            score += 4.0
        elif len(found_techniques) >= 2:
            score += 2.0
        
        # Check for timing cues (2 points)
        if any(word in instruction_text for word in ["minutes", "until", "golden", "tender", "brown"]):
            score += 2.0
        
        return min(score, 20.0)
    
    def _score_instruction_detail(self, instructions: List[Any], instruction_text: str) -> float:
        """Score instruction detail (0-20)"""
        score = 0.0
        
        # Check number of steps (5 points)
        num_steps = len(instructions)
        if num_steps >= 6:
            score += 5.0
        elif num_steps >= 5:
            score += 4.0
        elif num_steps >= 4:
            score += 3.0
        elif num_steps >= 3:
            score += 2.0
        
        # Check for detailed descriptions (5 points)
        avg_length = sum(
            len(str(step.get("description", "") if isinstance(step, dict) else step))
            for step in instructions
        ) / max(num_steps, 1)
        
        if avg_length >= 100:
            score += 5.0
        elif avg_length >= 70:
            score += 4.0
        elif avg_length >= 50:
            score += 3.0
        elif avg_length >= 30:
            score += 2.0
        
        # Check for timing cues (5 points)
        if any(word in instruction_text for word in ["minutes", "seconds", "until", "when"]):
            score += 5.0
        
        # Check for visual cues (5 points)
        visual_cues = ["golden", "brown", "tender", "translucent", "fragrant", "caramelized"]
        if any(cue in instruction_text for cue in visual_cues):
            score += 5.0
        
        return min(score, 20.0)
    
    def _score_ingredient_pairing(self, ingredient_names: List[str], cuisine: str) -> float:
        """Score ingredient pairing (0-15)"""
        score = 0.0
        cuisine = cuisine.lower()
        
        # Check for balanced ingredients (5 points)
        has_protein = any(word in " ".join(ingredient_names) for word in ["chicken", "beef", "fish", "tofu", "egg", "cheese"])
        has_vegetable = any(word in " ".join(ingredient_names) for word in ["onion", "tomato", "pepper", "carrot", "broccoli", "spinach"])
        has_carb = any(word in " ".join(ingredient_names) for word in ["rice", "pasta", "bread", "potato", "quinoa"])
        
        if has_protein and has_vegetable:
            score += 3.0
        if has_carb:
            score += 2.0
        
        # Check cuisine-specific pairings (10 points)
        if cuisine in self.FLAVOR_PROFILES:
            profile_ingredients = self.FLAVOR_PROFILES[cuisine]
            matches = sum(1 for ing in profile_ingredients if any(ing in name for name in ingredient_names))
            if matches >= 4:
                score += 10.0
            elif matches >= 3:
                score += 7.0
            elif matches >= 2:
                score += 5.0
            elif matches >= 1:
                score += 2.0
        
        return min(score, 15.0)
    
    def _score_texture_variety(self, ingredient_text: str, instruction_text: str) -> float:
        """Score texture variety (0-10)"""
        score = 0.0
        combined_text = ingredient_text + " " + instruction_text
        
        # Check for different textures
        textures_found = []
        for texture_type, indicators in self.TEXTURE_INDICATORS.items():
            if any(indicator in combined_text for indicator in indicators):
                textures_found.append(texture_type)
                score += 2.5
        
        # Bonus for multiple textures
        if len(textures_found) >= 3:
            score += 2.5
        
        return min(score, 10.0)
    
    def _score_presentation(self, instruction_text: str, ingredient_text: str) -> float:
        """Score presentation elements (0-10)"""
        score = 0.0
        combined_text = instruction_text + " " + ingredient_text
        
        # Check for garnishes (3 points)
        garnishes = ["garnish", "sprinkle", "garnish", "topped", "drizzle", "finish"]
        if any(word in combined_text for word in garnishes):
            score += 3.0
        
        # Check for finishing touches (3 points)
        finishes = ["finish", "drizzle", "garnish", "serve", "plate", "garnish"]
        if any(word in combined_text for word in finishes):
            score += 3.0
        
        # Check for fresh elements (4 points)
        fresh = ["fresh", "zest", "chopped", "minced", "sliced"]
        if any(word in combined_text for word in fresh):
            score += 4.0
        
        return min(score, 10.0)
    
    def _generate_improvements(
        self, total_score: float, flavor_score: float, technique_score: float,
        instruction_score: float, pairing_score: float, texture_score: float,
        presentation_score: float, recipe: Dict[str, Any], cuisine: str
    ) -> List[str]:
        """Generate improvement suggestions"""
        improvements = []
        
        if flavor_score < 15:
            improvements.append("Add more aromatics (onion, garlic, ginger) to build flavor base")
            improvements.append("Include acid elements (lemon, vinegar, wine) to balance flavors")
            if cuisine in self.FLAVOR_PROFILES:
                missing = [ing for ing in self.FLAVOR_PROFILES[cuisine.lower()] 
                           if ing not in str(recipe.get("ingredients", [])).lower()]
                if missing:
                    improvements.append(f"Add {cuisine} flavors: {', '.join(missing[:3])}")
        
        if technique_score < 12:
            improvements.append("Include more professional cooking techniques (sear, roast, braise)")
            improvements.append("Add timing cues and visual indicators ('until golden brown', 'cook for 5 minutes')")
        
        if instruction_score < 12:
            improvements.append("Expand instructions with more detail and step-by-step guidance")
            improvements.append("Include specific cooking times, temperatures, and visual cues")
        
        if pairing_score < 8:
            improvements.append("Ensure balanced ingredients (protein + vegetables + carbs)")
            if cuisine in self.FLAVOR_PROFILES:
                improvements.append(f"Use authentic {cuisine} ingredient combinations")
        
        if texture_score < 5:
            improvements.append("Add texture variety: include crispy, creamy, and crunchy elements")
        
        if presentation_score < 5:
            improvements.append("Add finishing touches: fresh herbs, garnishes, or finishing oils")
            improvements.append("Include plating and presentation tips in instructions")
        
        if total_score < 70:
            improvements.append("Recipe needs overall enhancement - consider professional chef techniques")
        
        return improvements[:5]  # Limit to 5 suggestions
    
    def enhance_recipe(self, recipe: Dict[str, Any], min_score: float = 70.0) -> Dict[str, Any]:
        """Enhance recipe quality if below threshold"""
        score = self.analyze_recipe_quality(recipe)
        
        if score.total_score >= min_score:
            logger.info(f"Recipe quality score: {score.total_score:.1f}/100 - Good quality")
            return recipe
        
        logger.warning(f"Recipe quality score: {score.total_score:.1f}/100 - Below threshold, suggestions: {score.improvements}")
        
        # Return recipe with quality metadata
        enhanced = recipe.copy()
        enhanced["quality_score"] = {
            "total": round(score.total_score, 1),
            "breakdown": {
                "flavor_complexity": round(score.flavor_complexity, 1),
                "cooking_techniques": round(score.cooking_techniques, 1),
                "instruction_detail": round(score.instruction_detail, 1),
                "ingredient_pairing": round(score.ingredient_pairing, 1),
                "texture_variety": round(score.texture_variety, 1),
                "presentation": round(score.presentation, 1),
            },
            "improvements": score.improvements
        }
        
        return enhanced

