# RAG (Retrieval-Augmented Generation) Implementation

## Overview

The system implements Retrieval-Augmented Generation (RAG) to enhance AI recipe generation with relevant examples from the recipe database. This document explains the embedding model, retrieval process, and how retrieved recipes guide generation.

## Architecture

### Components

1. **Vector Embeddings**: Recipe embeddings stored in database
2. **Similarity Search**: Cosine similarity for recipe retrieval
3. **Prompt Augmentation**: Retrieved recipes included in prompts as negative examples
4. **Meal Type Filtering**: Recipes filtered by meal_type for relevance

## Embedding Model

### Model Selection

**Primary Model**: SentenceTransformer('all-MiniLM-L6-v2')

**Specifications**:
- **Dimensions**: 384-dimensional embeddings
- **Context Length**: 256 tokens
- **Model Size**: ~90MB
- **Speed**: Fast inference (< 100ms per recipe)
- **Quality**: Good semantic similarity for recipe retrieval

**Location**: `backend/ai/nutrition_ai.py:__init__()` (Line 17-22)

### Embedding Generation

**Script**: `backend/scripts/generate_recipe_embeddings.py`

**Process**:
1. Load all recipes from database (batch processing)
2. Generate embeddings for each recipe:
   ```python
   recipe_text = f"{recipe.title} {recipe.summary} {ingredients_text}"
   embedding = model.encode(recipe_text)
   ```
3. Store embeddings in `Recipe.embedding` column (JSON array)
4. Commit in batches for efficiency

**Recipe Text Format**:
```
{title} {summary} {cuisine} {meal_type} {ingredient1} {ingredient2} ...
```

**Example**:
```
"Mediterranean Quinoa Bowl A healthy quinoa bowl Mediterranean lunch quinoa tomatoes cucumbers feta olive_oil"
```

## Retrieval Process

### Similarity Search

**Location**: `backend/ai/nutrition_ai.py:_retrieve_similar_recipes()` (Line 528)

**Process**:
1. **Generate Query Embedding**:
   ```python
   query = f"{meal_type} {target_cuisine} {target_calories} calories"
   query_embedding = embedding_model.encode([query])[0]
   ```

2. **Filter Recipes by Meal Type** (if specified):
   ```python
   if meal_type:
       recipes = db.query(Recipe).filter(
           Recipe.meal_type == meal_type,
           Recipe.is_active == True
       ).limit(100).all()
   ```

3. **Calculate Cosine Similarity**:
   ```python
   similarity = np.dot(query_embedding, recipe_embedding) / (
       np.linalg.norm(query_embedding) * np.linalg.norm(recipe_embedding)
   )
   ```

4. **Sort by Similarity**:
   - Rank recipes by similarity score (highest first)
   - Return top N recipes (typically 5-10)

**Return Format**:
```python
[
    {
        'title': 'Recipe Title',
        'cuisine': 'Mediterranean',
        'meal_type': 'lunch',
        'ingredients': [...],
        'similarity': 0.85
    },
    ...
]
```

### User Embedding Integration

**Purpose**: Incorporate user dietary preferences into query

**Location**: `backend/ai/nutrition_ai.py:_get_user_embedding()` (Line 515)

**Process**:
1. Encode user preferences:
   ```python
   prefs_text = f"{dietary_prefs} {cuisine_prefs} {allergies}"
   user_embedding = embedding_model.encode([prefs_text])[0]
   ```

2. Combine with query embedding:
   ```python
   combined_embedding = (query_embedding + user_embedding) / 2
   ```

**Benefits**:
- Prioritizes recipes matching user preferences
- Filters out recipes with allergens
- Considers cuisine preferences

## How Retrieved Recipes Guide Generation

### Prompt Augmentation

**Location**: `backend/ai/nutrition_ai.py:_generate_single_meal_with_sequential_rag()` (Lines 1597-1614)

**Process**:
Retrieved recipes are included in the prompt as **negative examples** to prevent duplication:

```
Similar recipes to AVOID duplicating (use as inspiration but create something DIFFERENT):
1. Mediterranean Quinoa Bowl: quinoa, tomatoes, cucumbers, feta
2. Greek Salad Wrap: lettuce, tomatoes, olives, feta
3. Mediterranean Veggie Bowl: quinoa, chickpeas, olives, tomatoes
```

### Key Instructions

1. **Avoid Duplication**:
   - Explicitly listed as recipes to avoid
   - Prompt instructs: "use as inspiration but create something DIFFERENT"
   - Prevents exact title matches

2. **Inspiration**:
   - Recipes provide context for appropriate ingredients
   - Help maintain cuisine authenticity
   - Guide portion sizes and meal types

3. **Diversity**:
   - Different main ingredients
   - Different cooking methods
   - Different flavor profiles

### RAG Integration in Sequential Prompting

**Step 1: Initial Assessment**
- Retrieves similar recipes for context
- Uses as negative examples for duplicate prevention
- Filters by meal_type for relevance

**Step 2: Recipe Generation**
- Includes retrieved recipes in prompt
- Uses as inspiration while creating something different
- Maintains cuisine and meal type consistency

## Database Requirements

### Recipe Count

**Requirement**: ≥500 recipes

**Current Status**: Target 500+ recipes configured in seeding scripts

**Location**: `backend/scripts/` (multiple seeder scripts)

### Ingredient Count

**Requirement**: ≥500 ingredients

**Current Status**: Database contains 15,532+ ingredients

**Location**: `Ingredient` table

**Exceeds Requirement**: Significantly exceeds minimum requirement

## Embedding Storage

### Database Schema

**Column**: `Recipe.embedding`
- **Type**: JSON array of floats
- **Length**: 384 values (embedding dimensions)
- **Example**: `[0.123, -0.456, 0.789, ...]`

### Storage Format

```python
recipe.embedding = embedding.tolist()  # Convert numpy array to list
# Stored as: [0.123, -0.456, 0.789, ...] (384 values)
```

### Retrieval

```python
recipe_embedding = np.array(recipe.embedding)  # Convert back to numpy
```

## Performance Characteristics

### Embedding Generation

**Speed**: ~100ms per recipe
**Batch Size**: 50 recipes per batch
**Total Time**: ~10 minutes for 500 recipes

### Similarity Search

**Speed**: < 50ms for 100 recipes
**Optimization**: Limits to top 100 candidates before similarity calculation

### Memory Usage

**Model Size**: ~90MB (SentenceTransformer)
**Embedding Storage**: ~1.5KB per recipe (384 floats × 4 bytes)
**Total for 500 recipes**: ~750KB

## Filtering Strategies

### Meal Type Filtering

**Purpose**: Ensure retrieved recipes match meal type

**Implementation**:
```python
if meal_type:
    recipes = db.query(Recipe).filter(
        Recipe.meal_type == meal_type
    ).limit(100).all()
```

**Benefits**:
- Avoids retrieving breakfast recipes for dinner generation
- Maintains meal type consistency
- Improves retrieval relevance

### Dietary Filtering

**Purpose**: Filter out recipes with allergens or incompatible dietary tags

**Implementation**:
- Applied after similarity search
- Checks dietary_tags against user allergies
- Removes incompatible recipes from results

### Active Recipe Filtering

**Purpose**: Only retrieve active (published) recipes

**Implementation**:
```python
recipes = db.query(Recipe).filter(
    Recipe.is_active == True
).limit(100).all()
```

## Use Cases

### 1. Individual Meal Generation

**Context**: Generate single meal using progressive generation

**Process**:
1. Retrieve top 10 similar recipes for meal_type
2. Include in prompt as negative examples
3. Generate new recipe inspired by but different from retrieved

**Location**: `backend/ai/nutrition_ai.py:_generate_single_meal_with_sequential_rag()` (Line 1556-1563)

### 2. Recipe Search

**Context**: User searches for recipes

**Process**:
1. Generate query embedding from search terms
2. Retrieve top 20 similar recipes
3. Rank by similarity and return

**Location**: `backend/services/recipe_recommendation_service.py:_vector_similarity_search()` (Line 480)

### 3. Meal Plan Generation

**Context**: Generate weekly meal plan

**Process**:
1. For each meal type, retrieve similar recipes
2. Use as negative examples to prevent duplicates
3. Generate diverse meal plan across week

**Location**: `backend/ai/nutrition_ai.py:_retrieve_relevant_recipes_for_meal_plan()` (Line 60)

## Benefits of RAG

### 1. Duplicate Prevention
- Retrieved recipes explicitly avoided
- Prevents repetition across meal plans
- Maintains variety for users

### 2. Quality Improvement
- Real recipe examples guide generation
- Maintains cuisine authenticity
- Ensures appropriate ingredient combinations

### 3. Dietary Compliance
- Recipes filtered by dietary preferences
- Allergens excluded from retrieval
- Matches user cuisine preferences

### 4. Context Awareness
- Meal type consistency
- Appropriate portion sizes
- Cooking method suggestions

## Future Improvements

### 1. Hybrid Search
- Combine vector similarity with keyword search
- Improve recall for specific ingredients
- Better handling of rare ingredient combinations

### 2. Fine-Tuned Embeddings
- Train embeddings specifically for recipe domain
- Better semantic understanding of cooking terms
- Improved similarity calculations

### 3. Multi-Modal Retrieval
- Include recipe images in embeddings
- Visual similarity for recipe matching
- Better user experience

### 4. Incremental Updates
- Update embeddings when recipes are added/modified
- Avoid full re-embedding for new recipes
- Real-time embedding generation

### 5. Clustering
- Group similar recipes for batch retrieval
- Improve efficiency for large databases
- Better organization of recipe database

## Conclusion

The RAG implementation provides:
- ✅ Semantic recipe retrieval using vector embeddings
- ✅ Duplicate prevention through negative examples
- ✅ Quality improvement through real recipe examples
- ✅ Dietary compliance through filtering
- ✅ Context awareness through meal type matching

The system exceeds requirements with 15,532+ ingredients and targets 500+ recipes for comprehensive coverage.

