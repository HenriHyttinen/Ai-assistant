#!/bin/bash
# Script to move legacy scripts to _legacy folder

mkdir -p _legacy

# Essential scripts to KEEP
ESSENTIAL=(
    "comprehensive_seeder.py"
    "generate_recipe_embeddings.py"
    "seed_goals_direct.py"
    "README.md"
    "ESSENTIAL_SCRIPTS.md"
    "KEEP_OR_REMOVE.md"
    "move_legacy_scripts.sh"
)

# Move all other .py and .sh files to _legacy
for file in *.py *.sh; do
    if [[ -f "$file" ]]; then
        if [[ ! " ${ESSENTIAL[@]} " =~ " ${file} " ]]; then
            echo "Moving $file to _legacy/"
            mv "$file" _legacy/ 2>/dev/null || echo "  (skipped $file)"
        fi
    fi
done

echo "Done! Essential scripts kept, others moved to _legacy/"
