#!/usr/bin/env python3
"""
Fix recipe prep times and difficulty levels based on recipe content
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import Recipe
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PrepTimeDifficultyFixer:
    def __init__(self):
        self.db = SessionLocal()
        
    def estimate_prep_time(self, recipe):
        """Estimate prep time based on recipe content"""
        title = recipe.title.lower()
        summary = recipe.summary.lower() if recipe.summary else ""
        
        # Quick recipes (5-15 minutes)
        quick_keywords = ['quick', 'easy', 'simple', '3-ingredient', '5-minute', 'instant', 'no-cook', 'raw', 'salad']
        if any(keyword in title or keyword in summary for keyword in quick_keywords):
            return 15
        
        # Very quick recipes (5-10 minutes)
        very_quick_keywords = ['instant', 'no-cook', 'raw', 'smoothie', 'juice', 'dressing', 'sauce']
        if any(keyword in title or keyword in summary for keyword in very_quick_keywords):
            return 10
        
        # Long recipes (45+ minutes)
        long_keywords = ['braised', 'roasted', 'slow-cooked', 'marinated', 'fermented', 'aged', 'complex', 'elaborate']
        if any(keyword in title or keyword in summary for keyword in long_keywords):
            return 60
        
        # Medium recipes (20-30 minutes)
        medium_keywords = ['baked', 'grilled', 'sautéed', 'stir-fried', 'pasta', 'rice', 'soup', 'stew']
        if any(keyword in title or keyword in summary for keyword in medium_keywords):
            return 25
        
        # Default medium
        return 20
    
    def estimate_difficulty(self, recipe):
        """Estimate difficulty based on recipe content"""
        title = recipe.title.lower()
        summary = recipe.summary.lower() if recipe.summary else ""
        
        # Easy recipes
        easy_keywords = ['easy', 'simple', 'quick', 'basic', '3-ingredient', '5-minute', 'no-cook', 'one-pot', 'one-pan']
        if any(keyword in title or keyword in summary for keyword in easy_keywords):
            return 'easy'
        
        # Hard recipes
        hard_keywords = ['complex', 'elaborate', 'advanced', 'professional', 'gourmet', 'artisanal', 'traditional', 'authentic', 'braised', 'confit', 'sous vide', 'molecular']
        if any(keyword in title or keyword in summary for keyword in hard_keywords):
            return 'hard'
        
        # Medium recipes (default)
        return 'medium'
    
    def fix_all_recipes(self):
        """Fix prep times and difficulties for all recipes"""
        logger.info("🔧 Fixing prep times and difficulties...")
        
        recipes = self.db.query(Recipe).all()
        fixed_count = 0
        
        for recipe in recipes:
            try:
                old_prep = recipe.prep_time
                old_diff = recipe.difficulty_level
                
                new_prep = self.estimate_prep_time(recipe)
                new_diff = self.estimate_difficulty(recipe)
                
                recipe.prep_time = new_prep
                recipe.difficulty_level = new_diff
                
                if old_prep != new_prep or old_diff != new_diff:
                    fixed_count += 1
                    if fixed_count % 50 == 0:
                        logger.info(f"Fixed {fixed_count} recipes...")
                        
            except Exception as e:
                logger.error(f"Error fixing recipe {recipe.title}: {e}")
                continue
        
        try:
            self.db.commit()
            logger.info(f"✅ Fixed prep times and difficulties for {fixed_count} recipes!")
            
            # Verify fixes
            self.verify_fixes()
        except Exception as e:
            logger.error(f"Error committing changes: {e}")
            self.db.rollback()
            raise
    
    def verify_fixes(self):
        """Verify that the fixes worked"""
        logger.info("🔍 Verifying fixes...")
        
        # Check distribution
        recipes = self.db.query(Recipe).all()
        
        prep_times = [r.prep_time for r in recipes]
        difficulties = [r.difficulty_level for r in recipes]
        
        print(f"\nPrep time distribution:")
        from collections import Counter
        prep_dist = Counter(prep_times)
        for time, count in sorted(prep_dist.items()):
            print(f"  {time}min: {count} recipes")
        
        print(f"\nDifficulty distribution:")
        diff_dist = Counter(difficulties)
        for diff, count in sorted(diff_dist.items()):
            print(f"  {diff}: {count} recipes")
        
        # Show some examples
        print(f"\nSample recipes:")
        for recipe in recipes[:5]:
            print(f"  {recipe.title}: {recipe.prep_time}min, {recipe.difficulty_level}")

def main():
    fixer = PrepTimeDifficultyFixer()
    fixer.fix_all_recipes()

if __name__ == "__main__":
    main()







