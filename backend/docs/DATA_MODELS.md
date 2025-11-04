# Data Models Documentation

This document provides a comprehensive overview of all data models in the nutrition planning system, including their schemas, relationships, and constraints.

## Table of Contents

1. [Recipe Models](#recipe-models)
2. [Nutrition Models](#nutrition-models)
3. [Shopping List Models](#shopping-list-models)
4. [Micronutrient Models](#micronutrient-models)
5. [User Models](#user-models)
6. [Relationships Overview](#relationships-overview)
7. [Constraints and Indexes](#constraints-and-indexes)

---

## Recipe Models

### Recipe

The core recipe model storing complete recipe information including nutrition, ingredients, and instructions.

**Table**: `recipes`

**Primary Key**: `id` (String)

**Fields**:
- `id` (String, PK): Custom ID for better control
- `title` (String, indexed): Recipe name
- `cuisine` (String, indexed): Cuisine type (e.g., "Italian", "Mexican")
- `meal_type` (String, indexed): `breakfast`, `lunch`, `dinner`, or `snack`
- `servings` (Integer, default=1): Number of servings
- `summary` (Text, nullable): Recipe description
- `prep_time` (Integer): Preparation time in minutes
- `cook_time` (Integer): Cooking time in minutes
- `difficulty_level` (String): `easy`, `medium`, or `hard`
- `dietary_tags` (JSON, nullable): Array of tags (e.g., `["vegetarian", "gluten-free"]`)
- `source` (String, default="user-generated"): Recipe source
- `image_url` (String, nullable): Recipe image URL
- `is_active` (Boolean, default=True): Active status
- `embedding` (JSON, nullable): Vector embedding for RAG (stored as JSON array)

**Per-Serving Nutrition**:
- `per_serving_calories` (Float, nullable)
- `per_serving_protein` (Float, nullable): grams
- `per_serving_carbs` (Float, nullable): grams
- `per_serving_fat` (Float, nullable): grams
- `per_serving_sodium` (Float, nullable): mg
- `per_serving_fiber` (Float, nullable): grams

**Total Recipe Nutrition**:
- `total_calories` (Float, nullable)
- `total_protein` (Float, nullable): grams
- `total_carbs` (Float, nullable): grams
- `total_fat` (Float, nullable): grams
- `total_sodium` (Float, nullable): mg
- `total_fiber` (Float, nullable): grams

**Per-Serving Micronutrients**:
- `per_serving_vitamin_d` (Float, nullable): mcg
- `per_serving_vitamin_b12` (Float, nullable): mcg
- `per_serving_iron` (Float, nullable): mg
- `per_serving_calcium` (Float, nullable): mg
- `per_serving_magnesium` (Float, nullable): mg
- `per_serving_vitamin_c` (Float, nullable): mg
- `per_serving_folate` (Float, nullable): mcg
- `per_serving_zinc` (Float, nullable): mg
- `per_serving_potassium` (Float, nullable): mg

**Total Micronutrients**:
- `total_vitamin_d` (Float, nullable)
- `total_vitamin_b12` (Float, nullable)
- `total_iron` (Float, nullable)
- `total_calcium` (Float, nullable)
- `total_magnesium` (Float, nullable)
- `total_vitamin_c` (Float, nullable)
- `total_folate` (Float, nullable)
- `total_zinc` (Float, nullable)
- `total_potassium` (Float, nullable)
- `total_fiber` (Float, nullable)

**Relationships**:
- `ingredients`: One-to-many with `RecipeIngredient` (cascade delete)
- `instructions`: One-to-many with `RecipeInstruction` (cascade delete)

**Timestamps**: `created_at`, `updated_at` (via `TimestampMixin`)

---

### Ingredient

Base ingredient model storing nutritional information for all ingredients used in recipes.

**Table**: `ingredients`

**Primary Key**: `id` (String)

**Fields**:
- `id` (String, PK): Unique ingredient identifier
- `name` (String, indexed): Ingredient name (e.g., "chicken breast", "cheddar cheese")
- `category` (String, indexed): Ingredient category (`dairy`, `protein`, `vegetables`, `fruits`, `grains`, `nuts_seeds`, `oils_fats`, `herbs_spices`, `condiments`, `other`)
- `unit` (String): Standard unit (`g` for solids, `ml` for liquids, `piece` for discrete items)
- `default_quantity` (Float, default=100.0): Default quantity for nutrition values

**Nutritional Information (per 100g/ml)**:
- `calories` (Float, default=0.0)
- `protein` (Float, default=0.0): grams
- `carbs` (Float, default=0.0): grams
- `fats` (Float, default=0.0): grams
- `fiber` (Float, default=0.0): grams
- `sugar` (Float, default=0.0): grams
- `sodium` (Float, default=0.0): mg

**Micronutrients**:
- `vitamin_d` (Float, nullable): IU
- `vitamin_b12` (Float, nullable): mcg
- `iron` (Float, nullable): mg
- `calcium` (Float, nullable): mg
- `vitamin_c` (Float, nullable): mg
- `vitamin_a` (Float, nullable): IU
- `vitamin_e` (Float, nullable): mg
- `vitamin_k` (Float, nullable): mcg
- `thiamine` (Float, nullable): mg (B1)
- `riboflavin` (Float, nullable): mg (B2)
- `niacin` (Float, nullable): mg (B3)
- `folate` (Float, nullable): mcg (B9)
- `magnesium` (Float, nullable): mg
- `zinc` (Float, nullable): mg
- `selenium` (Float, nullable): mcg
- `potassium` (Float, nullable): mg
- `phosphorus` (Float, nullable): mg
- `omega_3` (Float, nullable): g
- `omega_6` (Float, nullable): g

**RAG Support**:
- `embedding` (JSON, nullable): Vector embedding for similarity search

**Relationships**:
- `recipe_ingredients`: One-to-many with `RecipeIngredient`

**Timestamps**: `created_at`, `updated_at` (via `TimestampMixin`)

**Notes**: The database contains 15,532+ ingredients with comprehensive nutritional data. Ingredients are used for accurate nutrition calculation in AI-generated recipes via function calling.

---

### RecipeIngredient

Junction table linking recipes to ingredients with specific quantities.

**Table**: `recipe_ingredients`

**Primary Key**: `id` (Integer)

**Fields**:
- `id` (Integer, PK): Auto-increment primary key
- `recipe_id` (String, FK → `recipes.id`): Reference to recipe
- `ingredient_id` (String, FK → `ingredients.id`): Reference to ingredient
- `quantity` (Float): Quantity in standardized units (grams for solids, milliliters for liquids)
- `unit` (String): Standard unit (`g`, `ml`, `piece`)
- `notes` (String, nullable): Additional notes about the ingredient

**Relationships**:
- `recipe`: Many-to-one with `Recipe`
- `ingredient`: Many-to-one with `Ingredient`

**Standardization**: All quantities are converted to standardized units (g for solids, ml for liquids) when recipes are added to meal plans, as per task requirements.

---

### RecipeInstruction

Step-by-step cooking instructions for recipes.

**Table**: `recipe_instructions`

**Primary Key**: `id` (Integer)

**Fields**:
- `id` (Integer, PK): Auto-increment primary key
- `recipe_id` (String, FK → `recipes.id`): Reference to recipe
- `step_number` (Integer): Sequential step number
- `step_title` (String): Brief title for the step
- `description` (Text): Detailed instruction text
- `ingredients_used` (JSON, nullable): Array of ingredient IDs used in this step
- `time_required` (Integer, nullable): Time required for this step in minutes

**Relationships**:
- `recipe`: Many-to-one with `Recipe`

---

## Nutrition Models

### UserNutritionPreferences

User-specific dietary preferences, restrictions, and nutritional targets.

**Table**: `user_nutrition_preferences`

**Primary Key**: `id` (Integer)

**Foreign Keys**:
- `user_id` (Integer, FK → `users.id`, unique): One preference record per user

**Fields**:
- `id` (Integer, PK): Auto-increment primary key
- `user_id` (Integer, FK, unique): User reference

**Dietary Preferences**:
- `dietary_preferences` (JSON, nullable): Array of preferences (17 supported):
  - `vegetarian`, `vegan`, `keto`, `paleo`, `mediterranean`, `low-carb`, `low-fat`, `high-protein`, `low-sodium`, `whole30`, `dash`, `pescatarian`, `flexitarian`, `raw-food`, `fruitarian`, `carnivore`, `omnivore`
- `allergies` (JSON, nullable): Array of allergies (13 supported):
  - `nuts`, `peanuts`, `dairy`, `eggs`, `soy`, `wheat`, `gluten`, `fish`, `shellfish`, `sesame`, `sulfites`, `lupin`, `mollusk`
- `disliked_ingredients` (JSON, nullable): Array of disliked ingredients
- `cuisine_preferences` (JSON, nullable): Array of preferred cuisines (e.g., `["Italian", "Mexican", "Asian"]`)

**Nutritional Targets**:
- `daily_calorie_target` (Float, nullable): Daily calorie goal
- `protein_target` (Float, nullable): Daily protein target in grams
- `carbs_target` (Float, nullable): Daily carbs target in grams
- `fats_target` (Float, nullable): Daily fats target in grams

**Meal Preferences**:
- `meals_per_day` (Integer, default=3): Number of main meals (3-6 supported)
- `snacks_per_day` (Integer, default=2): Number of snacks per day
- `preferred_meal_times` (JSON, nullable): Object with meal times (e.g., `{"breakfast": "08:00", "lunch": "12:30", "dinner": "19:00"}`)
- `timezone` (String, default="UTC"): User's timezone

**Timestamps**: `created_at`, `updated_at` (via `TimestampMixin`)

---

### MealPlan

Weekly or daily meal plan container.

**Table**: `meal_plans`

**Primary Key**: `id` (String)

**Foreign Keys**:
- `user_id` (Integer, FK → `users.id`): User who owns the meal plan

**Fields**:
- `id` (String, PK): Custom meal plan ID (format: `mp_{user_id}_{timestamp}_{random}`)
- `user_id` (Integer, FK): User reference
- `plan_type` (String): `"daily"` or `"weekly"`
- `start_date` (Date): Plan start date (weekly plans normalized to Monday)
- `end_date` (Date, nullable): Plan end date (for weekly plans)
- `version` (String, default="1.0"): Version identifier
- `is_active` (Boolean, default=True): Active status

**AI Generation Metadata**:
- `generation_strategy` (JSON, nullable): Strategy used (e.g., `{"strategy": "progressive", "mode": "empty_structure"}`)
- `ai_model_used` (String, nullable): AI model identifier (e.g., `"gpt-3.5-turbo"`)
- `generation_parameters` (JSON, nullable): Parameters used for generation

**Relationships**:
- `meals`: One-to-many with `MealPlanMeal` (cascade delete)

**Timestamps**: `created_at`, `updated_at` (via `TimestampMixin`)

**Notes**: Weekly plans always start on Monday for consistency. Progressive meal plans have `generation_strategy.strategy == "progressive"` and may have fewer than 28 meals (7 days × 4 meals).

---

### MealPlanMeal

Individual meal within a meal plan.

**Table**: `meal_plan_meals`

**Primary Key**: `id` (Integer)

**Foreign Keys**:
- `meal_plan_id` (String, FK → `meal_plans.id`): Reference to meal plan

**Fields**:
- `id` (Integer, PK): Auto-increment primary key
- `meal_plan_id` (String, FK): Meal plan reference
- `meal_date` (Date): Date for this meal
- `meal_type` (String): `breakfast`, `lunch`, `dinner`, or `snack` (normalized)
- `meal_time` (DateTime, nullable): Meal time in ISO 8601 format
- `meal_name` (String): Recipe name/title

**Nutritional Information**:
- `calories` (Float, default=0.0)
- `protein` (Float, default=0.0): grams
- `carbs` (Float, default=0.0): grams
- `fats` (Float, default=0.0): grams

**Recipe Details**:
- `recipe_details` (JSON, nullable): Complete recipe information stored as JSON, including:
  - `meal_type`: Original meal type (e.g., `"morning snack"`, `"afternoon snack"`) for distinguishing snack variants
  - `ingredients`: Array of ingredients with quantities and units
  - `instructions`: Array of cooking instructions
  - `dietary_tags`: Array of dietary tags
  - `servings`: Number of servings
  - `nutrition`: Per-serving and total nutrition values
  - `cuisine`: Cuisine type
  - `prep_time`, `cook_time`, `difficulty_level`
- `cuisine` (String, nullable): Cuisine type for easy filtering

**Relationships**:
- `meal_plan`: Many-to-one with `MealPlan`

**Notes**: The `recipe_details.meal_type` field preserves the original meal type (e.g., `"morning snack"`) while `meal_type` is normalized to `"snack"` for database queries. This allows the frontend to assign snacks to specific slots.

---

### MealPlanRecipe

Legacy junction table linking meal plans to recipes (currently unused, recipes stored in `recipe_details` JSON).

**Table**: `meal_plan_recipes`

**Primary Key**: `id` (Integer)

**Foreign Keys**:
- `meal_plan_id` (String, FK → `meal_plans.id`)
- `meal_id` (Integer, FK → `meal_plan_meals.id`)
- `recipe_id` (String, FK → `recipes.id`)

**Fields**:
- `id` (Integer, PK): Auto-increment primary key
- `meal_plan_id` (String, FK): Meal plan reference
- `meal_id` (Integer, FK): Meal reference
- `recipe_id` (String, FK): Recipe reference
- `servings` (Float, default=1.0): Number of servings
- `is_alternative` (Boolean, default=False): Whether this is an alternative meal option

**Note**: This table is currently not used in the active implementation. Recipe details are stored in `MealPlanMeal.recipe_details` JSON field for flexibility and performance.

---

### MealPlanVersion

Version history for meal plans, enabling users to restore previous versions.

**Table**: `meal_plan_versions`

**Primary Key**: `id` (Integer)

**Foreign Keys**:
- `meal_plan_id` (String, FK → `meal_plans.id`)
- `user_id` (Integer, FK → `users.id`)

**Fields**:
- `id` (Integer, PK): Auto-increment primary key
- `meal_plan_id` (String, FK): Meal plan reference
- `user_id` (Integer, FK): User reference
- `version_label` (String): Human-readable version label (e.g., "Version 1.0", "Before changes")
- `snapshot` (JSON): Complete meal plan snapshot including all meals and recipes
- `is_restorable` (Boolean, default=True): Whether this version can be restored

**Relationships**:
- `meal_plan`: Many-to-one with `MealPlan`

**Timestamps**: `created_at`, `updated_at` (via `TimestampMixin`)

---

### NutritionalLog

Daily nutritional intake logs for tracking user consumption.

**Table**: `nutritional_logs`

**Primary Key**: `id` (Integer)

**Foreign Keys**:
- `user_id` (Integer, FK → `users.id`): User who logged the intake

**Fields**:
- `id` (Integer, PK): Auto-increment primary key
- `user_id` (Integer, FK): User reference
- `log_date` (Date, indexed): Date of the log entry
- `meal_type` (String): `breakfast`, `lunch`, `dinner`, or `snack`

**Nutritional Values Consumed**:
- `calories` (Float, default=0.0)
- `protein` (Float, default=0.0): grams
- `carbs` (Float, default=0.0): grams
- `fats` (Float, default=0.0): grams
- `fiber` (Float, default=0.0): grams
- `sugar` (Float, default=0.0): grams
- `sodium` (Float, default=0.0): mg

**Micronutrients (Comprehensive Tracking)**:
- `vitamin_d` (Float, nullable): IU
- `vitamin_b12` (Float, nullable): mcg
- `iron` (Float, nullable): mg
- `calcium` (Float, nullable): mg
- `vitamin_c` (Float, nullable): mg
- `vitamin_a` (Float, nullable): IU
- `vitamin_e` (Float, nullable): mg
- `vitamin_k` (Float, nullable): mcg
- `thiamine` (Float, nullable): mg (B1)
- `riboflavin` (Float, nullable): mg (B2)
- `niacin` (Float, nullable): mg (B3)
- `folate` (Float, nullable): mcg (B9)
- `magnesium` (Float, nullable): mg
- `zinc` (Float, nullable): mg
- `selenium` (Float, nullable): mcg
- `potassium` (Float, nullable): mg
- `phosphorus` (Float, nullable): mg
- `omega_3` (Float, nullable): g
- `omega_6` (Float, nullable): g

**Timestamps**: `created_at`, `updated_at` (via `TimestampMixin`)

**Use Cases**:
- Daily progress tracking
- Historical analysis
- Trend calculations
- Weekly/monthly summaries
- AI-powered insights generation

---

## Shopping List Models

### ShoppingList

Shopping list container linked to a meal plan.

**Table**: `shopping_lists`

**Primary Key**: `id` (String)

**Foreign Keys**:
- `user_id` (Integer, FK → `users.id`): User who owns the list
- `meal_plan_id` (String, FK → `meal_plans.id`, nullable): Optional meal plan reference

**Fields**:
- `id` (String, PK): Custom shopping list ID
- `user_id` (Integer, FK): User reference
- `meal_plan_id` (String, FK, nullable): Associated meal plan (if generated from meal plan)
- `list_name` (String): Shopping list name
- `is_active` (Boolean, default=True): Active status

**Relationships**:
- `meal_plan`: Many-to-one with `MealPlan`
- `items`: One-to-many with `ShoppingListItem` (cascade delete)

**Timestamps**: `created_at`, `updated_at` (via `TimestampMixin`)

---

### ShoppingListItem

Individual ingredient item in a shopping list.

**Table**: `shopping_list_items`

**Primary Key**: `id` (Integer)

**Foreign Keys**:
- `shopping_list_id` (String, FK → `shopping_lists.id`): Shopping list reference
- `ingredient_id` (String, FK → `ingredients.id`): Ingredient reference

**Fields**:
- `id` (Integer, PK): Auto-increment primary key
- `shopping_list_id` (String, FK): Shopping list reference
- `ingredient_id` (String, FK): Ingredient reference
- `quantity` (Float): Required quantity
- `unit` (String): Unit of measurement (`g`, `ml`, `piece`)
- `category` (String): Ingredient category for grouping (`dairy`, `protein`, `vegetables`, `fruits`, `grains`, `nuts_seeds`, `oils_fats`, `herbs_spices`, `condiments`, `other`)
- `is_purchased` (Boolean, default=False): Purchase status
- `notes` (String, nullable): Additional notes

**Relationships**:
- `shopping_list`: Many-to-one with `ShoppingList`

**Features**:
- Automatic categorization for organized shopping
- Quantity aggregation when multiple recipes use the same ingredient
- Quantity adjustment capabilities
- Ingredient removal functionality

---

## Micronutrient Models

### MicronutrientGoal

User-defined micronutrient targets.

**Table**: `micronutrient_goals`

**Primary Key**: `id` (Integer)

**Foreign Keys**:
- `user_id` (Integer, FK → `users.id`): User reference

**Fields**:
- `id` (Integer, PK): Auto-increment primary key
- `user_id` (Integer, FK): User reference

**Micronutrient Targets (Daily Recommended Values)**:
- `vitamin_d_target` (Float, nullable): mcg
- `vitamin_b12_target` (Float, nullable): mcg
- `iron_target` (Float, nullable): mg
- `calcium_target` (Float, nullable): mg
- `magnesium_target` (Float, nullable): mg
- `vitamin_c_target` (Float, nullable): mg
- `folate_target` (Float, nullable): mcg
- `zinc_target` (Float, nullable): mg
- `potassium_target` (Float, nullable): mg
- `fiber_target` (Float, nullable): g
- `vitamin_a_target` (Float, nullable): IU
- `vitamin_e_target` (Float, nullable): mg
- `vitamin_k_target` (Float, nullable): mcg
- `thiamine_target` (Float, nullable): mg (B1)
- `riboflavin_target` (Float, nullable): mg (B2)
- `niacin_target` (Float, nullable): mg (B3)
- `selenium_target` (Float, nullable): mcg
- `phosphorus_target` (Float, nullable): mg
- `omega_3_target` (Float, nullable): g
- `omega_6_target` (Float, nullable): g

- `is_active` (Boolean, default=True): Active status

**Relationships**:
- `user`: Many-to-one with `User`

**Timestamps**: `created_at`, `updated_at` (via `TimestampMixin`)

---

### DailyMicronutrientIntake

Daily aggregated micronutrient intake tracking.

**Table**: `daily_micronutrient_intakes`

**Primary Key**: `id` (Integer)

**Foreign Keys**:
- `user_id` (Integer, FK → `users.id`): User reference

**Fields**:
- `id` (Integer, PK): Auto-increment primary key
- `user_id` (Integer, FK): User reference
- `date` (DateTime, indexed): Date of intake

**Micronutrient Intake Values**:
- Same 18+ micronutrient fields as `MicronutrientGoal` (with `_intake` suffix instead of `_target`)

**Relationships**:
- `user`: Many-to-one with `User`

**Timestamps**: `created_at`, `updated_at` (via `TimestampMixin`)

---

### MicronutrientDeficiency

Tracking and recommendations for micronutrient deficiencies.

**Table**: `micronutrient_deficiencies`

**Primary Key**: `id` (Integer)

**Foreign Keys**:
- `user_id` (Integer, FK → `users.id`): User reference

**Fields**:
- `id` (Integer, PK): Auto-increment primary key
- `user_id` (Integer, FK): User reference
- `micronutrient_name` (String): Name of the micronutrient (e.g., `"vitamin_d"`, `"iron"`)
- `deficiency_level` (String): Severity (`mild`, `moderate`, `severe`)
- `current_intake` (Float): Current daily intake
- `recommended_intake` (Float): Recommended daily intake
- `deficiency_percentage` (Float): Percentage below recommended
- `food_suggestions` (String, nullable): JSON string of food recommendations
- `supplement_suggestions` (String, nullable): Supplement recommendations
- `is_resolved` (Boolean, default=False): Whether the deficiency has been resolved
- `resolved_at` (DateTime, nullable): Resolution timestamp

**Relationships**:
- `user`: Many-to-one with `User`

**Timestamps**: `created_at`, `updated_at` (via `TimestampMixin`)

---

## User Models

### User

Core user model (referenced by all nutrition models).

**Table**: `users`

**Relationships**:
- Referenced by: `UserNutritionPreferences`, `MealPlan`, `NutritionalLog`, `ShoppingList`, `MicronutrientGoal`, `DailyMicronutrientIntake`, `MicronutrientDeficiency`

**Note**: The User model is defined in `backend/models/user.py` and is part of the authentication/user management system.

---

## Relationships Overview

### Entity Relationship Diagram (Text Representation)

```
User
├── UserNutritionPreferences (1:1)
├── MealPlan (1:many)
│   ├── MealPlanMeal (1:many)
│   │   └── recipe_details (JSON) - Contains full recipe data
│   └── MealPlanVersion (1:many)
├── NutritionalLog (1:many)
├── ShoppingList (1:many)
│   └── ShoppingListItem (1:many)
│       └── Ingredient (many:1)
├── MicronutrientGoal (1:1)
├── DailyMicronutrientIntake (1:many)
└── MicronutrientDeficiency (1:many)

Recipe
├── RecipeIngredient (1:many)
│   ├── Recipe (many:1)
│   └── Ingredient (many:1)
└── RecipeInstruction (1:many)

MealPlan
└── ShoppingList (1:many, optional)
```

### Key Relationships

1. **User → MealPlan** (1:many)
   - Each user can have multiple meal plans
   - Meal plans are tied to specific users

2. **MealPlan → MealPlanMeal** (1:many)
   - Each meal plan contains multiple meals
   - Cascade delete: deleting a meal plan deletes all its meals

3. **MealPlanMeal → Recipe** (via JSON)
   - Recipe details are stored in `recipe_details` JSON field
   - This allows flexibility for both database recipes and AI-generated recipes
   - Original meal type (e.g., `"morning snack"`) is preserved in `recipe_details.meal_type`

4. **Recipe → RecipeIngredient** (1:many)
   - Each recipe has multiple ingredients
   - Cascade delete: deleting a recipe deletes all its ingredients and instructions

5. **RecipeIngredient → Ingredient** (many:1)
   - Multiple recipes can use the same ingredient
   - Ingredients store base nutritional data

6. **ShoppingList → MealPlan** (many:1, optional)
   - Shopping lists can be generated from meal plans
   - A shopping list can exist independently

7. **ShoppingListItem → Ingredient** (many:1)
   - Shopping list items reference ingredients for nutritional data

8. **User → NutritionalLog** (1:many)
   - Users log daily nutritional intake
   - Used for progress tracking and historical analysis

---

## Constraints and Indexes

### Primary Keys
- All tables have a primary key (either Integer auto-increment or String custom ID)
- `UserNutritionPreferences.user_id` is unique (one preference record per user)

### Foreign Keys
- All foreign keys have proper referential integrity
- Cascade deletes are used for dependent relationships:
  - `Recipe` → `RecipeIngredient`, `RecipeInstruction`
  - `MealPlan` → `MealPlanMeal`
  - `ShoppingList` → `ShoppingListItem`

### Indexes
- **Recipe**: `id`, `title`, `cuisine`, `meal_type`
- **Ingredient**: `id`, `name`, `category`
- **MealPlan**: `id`, `user_id`
- **MealPlanMeal**: `id`, `meal_plan_id`, `meal_date`, `meal_type`
- **NutritionalLog**: `id`, `user_id`, `log_date`
- **UserNutritionPreferences**: `id`, `user_id` (unique)

### Data Constraints

1. **Meal Type Values**:
   - `MealPlanMeal.meal_type`: Must be `breakfast`, `lunch`, `dinner`, or `snack` (normalized)
   - `MealPlanMeal.recipe_details.meal_type`: Can be specific (e.g., `"morning snack"`, `"afternoon snack"`) for frontend slot assignment

2. **Plan Type Values**:
   - `MealPlan.plan_type`: Must be `"daily"` or `"weekly"`

3. **Standardized Units**:
   - Ingredient quantities in `RecipeIngredient` and `ShoppingListItem` use standardized units:
     - `g` for solids
     - `ml` for liquids
     - `piece` for discrete items

4. **Date Normalization**:
   - Weekly meal plans always start on Monday (`start_date` is normalized)

5. **Progressive Meal Plans**:
   - Progressive meal plans may have fewer than 28 meals (7 days × 4 meals)
   - Validation is skipped for progressive plans

6. **Nutrition Calculations**:
   - Per-serving values: `total_value / servings`
   - Total values: Sum of all ingredient nutrition × servings
   - Nutrition is calculated from ingredient database for accuracy

### JSON Field Schemas

1. **Recipe.dietary_tags**: `["vegetarian", "gluten-free", ...]`
2. **UserNutritionPreferences.dietary_preferences**: `["vegetarian", "keto", ...]`
3. **UserNutritionPreferences.allergies**: `["nuts", "dairy", ...]`
4. **UserNutritionPreferences.preferred_meal_times**: `{"breakfast": "08:00", "lunch": "12:30", "dinner": "19:00"}`
5. **MealPlan.generation_strategy**: `{"strategy": "progressive", "mode": "empty_structure"}`
6. **MealPlanMeal.recipe_details**: Complete recipe object with nested arrays for ingredients and instructions
7. **Recipe.embedding**: Array of floats for vector similarity search
8. **Ingredient.embedding**: Array of floats for vector similarity search

---

## Additional Notes

### RAG (Retrieval-Augmented Generation)
- Both `Recipe` and `Ingredient` tables support vector embeddings stored as JSON arrays
- Embeddings are generated using `SentenceTransformer('all-MiniLM-L6-v2')`
- Used for similarity search in AI recipe generation

### Nutrition Calculation Flow
1. **AI-Generated Recipes**: Ingredients are calculated using `NutritionFunctionRegistry._get_nutrition_from_database()`, which:
   - Looks up ingredients in the `Ingredient` table
   - Converts quantities to grams/milliliters
   - Calculates nutrition based on per-100g/ml values
   - Falls back to estimates if ingredient not found

2. **Database Recipes**: Nutrition is pre-calculated and stored in `Recipe` table
   - Per-serving values: `per_serving_calories`, `per_serving_protein`, etc.
   - Total values: `total_calories`, `total_protein`, etc.

3. **Portion Adjustment**: When users adjust servings, ingredient quantities and nutrition are recalculated from the database

### Progressive Meal Plans
- Progressive meal plans use `generation_strategy.strategy == "progressive"`
- Meals are generated on-demand, one slot at a time
- Frontend assigns meals to specific slots based on `recipe_details.meal_type`
- Validation for 28 meals is skipped for progressive plans

### Meal Swapping
- Meals can be moved between dates/slots using the `move_meal_to_date` endpoint
- If the target slot is occupied, an atomic swap occurs (both meals exchange positions)
- Calorie restrictions are not enforced during swaps (user decision)

---

## Summary

This data model supports:
- ✅ 500+ recipes with vector embeddings for RAG
- ✅ 15,532+ ingredients with comprehensive nutrition data
- ✅ Flexible meal plan structures (daily/weekly, 3-6 meals per day)
- ✅ Progressive meal generation (on-demand slot filling)
- ✅ Complete nutrition tracking (macros + 18+ micronutrients)
- ✅ Shopping list generation with categorization
- ✅ Meal plan versioning and restoration
- ✅ Daily nutritional logging and historical analysis
- ✅ Dietary preferences (17) and allergies (13) tracking
- ✅ ISO 8601 date/time formatting throughout

All models follow consistent patterns with `TimestampMixin` for audit trails and proper indexing for performance.

