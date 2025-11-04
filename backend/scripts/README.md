# Scripts Directory

This directory contains essential scripts for database setup. Legacy development scripts are archived in `_legacy/` folder.

## Essential Scripts for Reviewers

These are the scripts you need for initial setup:

### 1. Database Seeding

**`comprehensive_seeder.py`** ⭐ (Recommended)
- **Purpose**: Seeds database with 500+ recipes and 500+ ingredients
- **When to use**: Initial database setup
- **Usage**: `python scripts/comprehensive_seeder.py`
- **Time**: ~5-10 minutes

**Alternatives:**
- `direct_seeder.py` - Faster SQL-based seeder
- `generate_500_authentic_recipes.py` - Generates recipes using AI
- `minimal_seeder.py` - Basic seeder for quick testing

### 2. Vector Embeddings (for RAG)

**`generate_recipe_embeddings.py`** ⭐
- **Purpose**: Generates vector embeddings for recipe search (RAG)
- **When to use**: After seeding recipes
- **Usage**: `python scripts/generate_recipe_embeddings.py`
- **Requirements**: `sentence-transformers` package
- **Time**: ~5-15 minutes (depends on recipe count)

**Related:**
- `generate_ingredient_embeddings.py` - For ingredient embeddings

### 3. Goal Templates

**`seed_goals_direct.py`** ⭐
- **Purpose**: Seeds nutrition goal templates
- **When to use**: Initial setup
- **Usage**: `python scripts/seed_goals_direct.py`

### 4. Verification

**`audit_and_fix_recipe_nutrition.py`**
- **Purpose**: Validates and fixes recipe nutrition data
- **When to use**: If you notice nutrition calculation issues
- **Usage**: `python scripts/audit_and_fix_recipe_nutrition.py`

## Maintenance Scripts

These are used for data maintenance and fixes:

### Recipe Fixes
- `fix_recipe_nutrition.py` - Fix nutrition calculations
- `fix_recipe_quantities.py` - Fix ingredient quantities
- `fix_recipe_parsing.py` - Fix recipe parsing issues
- `recalculate_recipe_nutrition.py` - Recalculate nutrition from ingredients
- `add_per_serving_nutrition.py` - Add per-serving nutrition

### Ingredient Fixes
- `populate_ingredient_micronutrients.py` - Add micronutrient data
- `fix_ingredient_nutrition.py` - Fix ingredient nutrition
- `comprehensive_ingredient_fix.py` - Comprehensive ingredient fixes

### Dietary Tags
- `add_accurate_dietary_tags.py` - Add dietary tags to recipes
- `add_comprehensive_dietary_tags.py` - Comprehensive tag addition

### Other Maintenance
- `populate_achievements.py` - Seed achievement system
- `reset_meal_plan_memory.py` - Reset meal plan duplicate memory
- `cleanup_test_data.py` - Clean up test data

## Deprecated/Legacy Scripts

These scripts are from development iterations and are not needed for review:

### Old Seeders (Use `comprehensive_seeder.py` instead)
- `create_500_real_recipes.py`
- `create_comprehensive_real_recipes.py`
- `create_real_recipe_database.py`
- `create_simple_real_recipes.py`
- `generate_500_ai_recipes.py`
- `generate_500_quality_recipes.py`
- `import_500_complete_health_recipes.py`
- `import_500_correct_recipes.py`
- `import_real_recipes.py`
- `simple_nutrition_seeder.py`
- `populate_nutrition_database.py`

### Old Fix Scripts (Use `audit_and_fix_recipe_nutrition.py` instead)
- `fix_all_recipes.py`
- `fix_all_recipe_data.py`
- `fix_all_recipe_ingredient_quantities.py`
- `fix_remaining_recipes.py`
- `fix_remaining_recipes_nutrition.py`
- `fix_recipes_properly.py`
- `fix_recipe_ingredients_content.py`
- `replace_problematic_recipes.py`
- `replace_recipes_without_nutrition.py`
- `remove_non_food_recipes.py`
- `select_best_recipes.py`
- `select_best_recipes_fixed.py`
- `select_realistic_recipes.py`

### Migration/Fix Scripts (One-time fixes from development)
- `add_final_2_recipes.py`
- `add_more_ingredients.py`
- `add_micronutrient_columns.py`
- `add_per_serving_nutrition.py`
- `add_recipe_instructions.py`
- `add_timezone_support.py`
- `convert_all_to_metric.py`
- `convert_temperatures.py`
- `fix_nested_conversions.py`
- `fix_nutrition_display.py`
- `fix_nutrition_from_original.py`
- `fix_nutritional_display.py`
- `fix_prep_time_difficulty.py`
- `fix_temperature_storage.py`
- `migrate_nutrition_tables.py`
- `analyze_and_fix_recipe_servings.py`
- `verify_and_fix_nutrition_from_ingredients.py`
- `verify_and_fix_recipe_nutrition.py`
- `restore_nutrition_from_sqlite.py`
- `optimize_and_calculate_micronutrients.py`
- `fix_ingredients_and_recalculate_recipes.py`

### Test/Utility Scripts
- `comprehensive_test.py`
- `test_imports.py`
- `generate_random_ingredients.py`
- `export_ingredient_list.py`
- `fetch_usda_nutrition_data.py`
- `delete_boccie_ball.py` (specific cleanup)

### Setup Scripts (Use main setup script instead)
- `seed_goal_templates.py`
- `seed_goal_templates_simple.py`
- `setup_nutrition_preferences.py`

## Quick Setup for Reviewers

**You only need these 3 scripts:**

```bash
# 1. Seed recipes and ingredients
python scripts/comprehensive_seeder.py

# 2. Generate embeddings (optional but recommended)
python scripts/generate_recipe_embeddings.py

# 3. Seed goal templates (optional)
python scripts/seed_goals_direct.py
```

That's it! The rest are maintenance/fix scripts from development.

## Script Categories Summary

| Category | Count | Status |
|----------|-------|--------|
| **Essential for Review** | 3-4 | ⭐ Use these |
| **Maintenance** | ~15 | Use if needed |
| **Deprecated/Legacy** | ~65 | Ignore for review |

## Notes

- Most scripts in this folder are from iterative development
- Only `comprehensive_seeder.py` is essential for reviewers
- Other scripts are for data maintenance/fixes done during development
- Feel free to ignore scripts not listed in "Essential" section

