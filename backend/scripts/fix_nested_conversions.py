#!/usr/bin/env python3
"""
Fix Nested Conversions

Fixes instructions with nested conversions like:
"60ml (60ml (60ml (60ml (4.0 tablespoons))))"
to just:
"60ml (4.0 tablespoons)"
or even better:
"240ml (1 cup)"
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import SessionLocal
from models.recipe import RecipeInstruction
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NestedConversionFixer:
    def __init__(self):
        self.db = SessionLocal()
        self.fixed_count = 0
        self.instructions_fixed = 0
    
    def clean_nested_conversion(self, text):
        """Clean nested conversions like '60ml (60ml (60ml (60ml (4.0 tablespoons))))'"""
        original = text
        
        # Pattern 1: Nested metric units
        # Match: "60ml (60ml (60ml (60ml (4.0 tablespoons))))"
        # Result: "240ml (1 cup)" or "60ml (4.0 tablespoons)"
        pattern1 = r'(\d+(?:\.\d+)?)\s*(ml|g|kg)\s*\(\s*\1\s*\2\s*\(\s*\1\s*\2\s*\(\s*\1\s*\2\s*\(([^\)]+)\)\)\)\)'
        
        def replace_nested1(m):
            value = float(m.group(1))
            unit = m.group(2)
            final_part = m.group(3).strip()
            
            # Extract the final imperial value
            imperial_match = re.search(r'(\d+(?:\.\d+)?)\s*(cup|cups|tablespoon|tablespoons|teaspoon|teaspoons|oz|ounce|ounces|lb|lbs|pound|pounds)', final_part, re.IGNORECASE)
            
            if imperial_match:
                imperial_value = float(imperial_match.group(1))
                imperial_unit = imperial_match.group(2).lower()
                
                # Calculate correct metric value based on imperial
                # cups -> ml: 1 cup = 240ml
                # tbsp -> ml: 1 tbsp = 15ml
                # tsp -> ml: 1 tsp = 5ml
                # oz -> g: 1 oz = 28.35g
                # lb -> g: 1 lb = 453.6g
                
                if imperial_unit in ['cup', 'cups']:
                    correct_metric = imperial_value * 240
                    metric_unit = 'ml'
                    return f"{correct_metric:.0f}{metric_unit} ({imperial_value} {imperial_unit})"
                elif imperial_unit in ['tablespoon', 'tablespoons']:
                    correct_metric = imperial_value * 15
                    metric_unit = 'ml'
                    return f"{correct_metric:.0f}{metric_unit} ({imperial_value} {imperial_unit})"
                elif imperial_unit in ['teaspoon', 'teaspoons']:
                    correct_metric = imperial_value * 5
                    metric_unit = 'ml'
                    return f"{correct_metric:.0f}{metric_unit} ({imperial_value} {imperial_unit})"
                elif imperial_unit in ['oz', 'ounce', 'ounces']:
                    correct_metric = imperial_value * 28.35
                    metric_unit = 'g'
                    return f"{correct_metric:.1f}{metric_unit} ({imperial_value} {imperial_unit})"
                elif imperial_unit in ['lb', 'lbs', 'pound', 'pounds']:
                    correct_metric = imperial_value * 453.6
                    metric_unit = 'g'
                    return f"{correct_metric:.1f}{metric_unit} ({imperial_value} {imperial_unit})"
            
            # Fallback: just use the value we found and the final part
            return f"{value}{unit} ({final_part})"
        
        # Pattern 2: Three-level nesting
        pattern2 = r'(\d+(?:\.\d+)?)\s*(ml|g|kg)\s*\(\s*\1\s*\2\s*\(\s*\1\s*\2\s*\(([^\)]+)\)\)\)'
        
        def replace_nested2(m):
            value = float(m.group(1))
            unit = m.group(2)
            final_part = m.group(3).strip()
            
            imperial_match = re.search(r'(\d+(?:\.\d+)?)\s*(cup|cups|tablespoon|tablespoons|teaspoon|teaspoons|oz|ounce|ounces|lb|lbs|pound|pounds)', final_part, re.IGNORECASE)
            
            if imperial_match:
                imperial_value = float(imperial_match.group(1))
                imperial_unit = imperial_match.group(2).lower()
                
                if imperial_unit in ['cup', 'cups']:
                    correct_metric = imperial_value * 240
                    return f"{correct_metric:.0f}ml ({imperial_value} {imperial_unit})"
                elif imperial_unit in ['tablespoon', 'tablespoons']:
                    correct_metric = imperial_value * 15
                    return f"{correct_metric:.0f}ml ({imperial_value} {imperial_unit})"
                elif imperial_unit in ['teaspoon', 'teaspoons']:
                    correct_metric = imperial_value * 5
                    return f"{correct_metric:.0f}ml ({imperial_value} {imperial_unit})"
                elif imperial_unit in ['oz', 'ounce', 'ounces']:
                    correct_metric = imperial_value * 28.35
                    return f"{correct_metric:.1f}g ({imperial_value} {imperial_unit})"
                elif imperial_unit in ['lb', 'lbs', 'pound', 'pounds']:
                    correct_metric = imperial_value * 453.6
                    return f"{correct_metric:.1f}g ({imperial_value} {imperial_unit})"
            
            return f"{value}{unit} ({final_part})"
        
        # Pattern 3: Two-level nesting
        pattern3 = r'(\d+(?:\.\d+)?)\s*(ml|g|kg)\s*\(\s*\1\s*\2\s*\(([^\)]+)\)\)'
        
        def replace_nested3(m):
            value = float(m.group(1))
            unit = m.group(2)
            final_part = m.group(3).strip()
            
            imperial_match = re.search(r'(\d+(?:\.\d+)?)\s*(cup|cups|tablespoon|tablespoons|teaspoon|teaspoons|oz|ounce|ounces|lb|lbs|pound|pounds)', final_part, re.IGNORECASE)
            
            if imperial_match:
                imperial_value = float(imperial_match.group(1))
                imperial_unit = imperial_match.group(2).lower()
                
                if imperial_unit in ['cup', 'cups']:
                    correct_metric = imperial_value * 240
                    return f"{correct_metric:.0f}ml ({imperial_value} {imperial_unit})"
                elif imperial_unit in ['tablespoon', 'tablespoons']:
                    correct_metric = imperial_value * 15
                    return f"{correct_metric:.0f}ml ({imperial_value} {imperial_unit})"
                elif imperial_unit in ['teaspoon', 'teaspoons']:
                    correct_metric = imperial_value * 5
                    return f"{correct_metric:.0f}ml ({imperial_value} {imperial_unit})"
                elif imperial_unit in ['oz', 'ounce', 'ounces']:
                    correct_metric = imperial_value * 28.35
                    return f"{correct_metric:.1f}g ({imperial_value} {imperial_unit})"
                elif imperial_unit in ['lb', 'lbs', 'pound', 'pounds']:
                    correct_metric = imperial_value * 453.6
                    return f"{correct_metric:.1f}g ({imperial_value} {imperial_unit})"
            
            return f"{value}{unit} ({final_part})"
        
        # Apply patterns in order (most nested first)
        cleaned = text
        original_cleaned = cleaned
        
        # Try pattern 1 (4 levels)
        cleaned = re.sub(pattern1, replace_nested1, cleaned, flags=re.IGNORECASE)
        if cleaned != original_cleaned:
            self.fixed_count += 1
        
        original_cleaned = cleaned
        # Try pattern 2 (3 levels)
        cleaned = re.sub(pattern2, replace_nested2, cleaned, flags=re.IGNORECASE)
        if cleaned != original_cleaned:
            self.fixed_count += 1
        
        original_cleaned = cleaned
        # Try pattern 3 (2 levels)
        cleaned = re.sub(pattern3, replace_nested3, cleaned, flags=re.IGNORECASE)
        if cleaned != original_cleaned:
            self.fixed_count += 1
        
        # Also clean up any remaining nested patterns (simple repetition)
        # Pattern: "60ml (60ml" -> "60ml"
        simple_nested = r'(\d+(?:\.\d+)?)\s*(ml|g|kg)\s*\(\s*\1\s*\2\s*\('
        while re.search(simple_nested, cleaned, re.IGNORECASE):
            cleaned = re.sub(simple_nested, r'\1\2 (', cleaned, flags=re.IGNORECASE)
            self.fixed_count += 1
        
        return cleaned
    
    def fix_all_instructions(self):
        """Fix all instructions with nested conversions"""
        logger.info("🔍 Finding instructions with nested conversions...")
        
        all_instructions = self.db.query(RecipeInstruction).all()
        logger.info(f"Found {len(all_instructions)} instructions to check")
        
        fixed_instructions = []
        
        for i, instruction in enumerate(all_instructions, 1):
            original = instruction.description or ''
            
            if not original:
                continue
            
            # Check if it has nested patterns
            nested_pattern = r'(\d+(?:\.\d+)?)\s*(ml|g|kg)\s*\(\s*\1\s*\2\s*\('
            
            if re.search(nested_pattern, original, re.IGNORECASE):
                # Fix it
                cleaned = self.clean_nested_conversion(original)
                
                if cleaned != original:
                    instruction.description = cleaned
                    fixed_instructions.append(instruction)
                    self.instructions_fixed += 1
                    
                    if self.instructions_fixed % 100 == 0:
                        logger.info(f"Progress: Fixed {self.instructions_fixed} instructions...")
                        self.db.commit()
        
        # Commit all changes
        self.db.commit()
        
        logger.info(f"\n📊 Summary:")
        logger.info(f"   ✅ Fixed {self.instructions_fixed} instructions")
        logger.info(f"   ✅ Cleaned {self.fixed_count} nested conversions")
        
        return self.instructions_fixed

if __name__ == "__main__":
    fixer = NestedConversionFixer()
    try:
        fixer.fix_all_instructions()
        logger.info(f"\n🎉 Successfully fixed nested conversions!")
    except Exception as e:
        logger.error(f"❌ Fix failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

