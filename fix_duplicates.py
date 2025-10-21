#!/usr/bin/env python3
"""
Script to remove duplicate keys from translations.ts file
"""

import re

def fix_duplicate_keys():
    with open('/home/deepessence/numbers-dont-lie/frontend/src/utils/translations.ts', 'r') as f:
        content = f.read()
    
    # Split by language sections
    sections = content.split('  },\n  ')
    
    fixed_sections = []
    
    for i, section in enumerate(sections):
        if i == 0:  # First section (en:)
            fixed_sections.append(section)
            continue
            
        if i == len(sections) - 1:  # Last section (closing brace and functions)
            fixed_sections.append(section)
            continue
            
        # For language sections, remove duplicate keys
        lines = section.split('\n')
        seen_keys = set()
        fixed_lines = []
        
        for line in lines:
            # Check if this is a key-value pair
            if ':' in line and not line.strip().startswith('//'):
                # Extract the key
                key_match = re.match(r'\s*([^:]+):', line)
                if key_match:
                    key = key_match.group(1).strip()
                    if key in seen_keys:
                        # Skip duplicate key
                        continue
                    else:
                        seen_keys.add(key)
            
            fixed_lines.append(line)
        
        fixed_sections.append('\n'.join(fixed_lines))
    
    # Join sections back together
    fixed_content = '  },\n  '.join(fixed_sections)
    
    # Write the fixed content
    with open('/home/deepessence/numbers-dont-lie/frontend/src/utils/translations.ts', 'w') as f:
        f.write(fixed_content)
    
    print("Fixed duplicate keys in translations.ts")

if __name__ == "__main__":
    fix_duplicate_keys()

