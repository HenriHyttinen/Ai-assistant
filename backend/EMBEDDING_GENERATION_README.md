# Embedding Generation Guide

## Overview

This guide explains how to generate vector embeddings for recipes and ingredients to enable RAG (Retrieval-Augmented Generation) functionality.

## Requirements

- **Python 3.8+**
- **sentence-transformers** library
- Compatible numpy and scipy versions

## Known Issues

### Scipy/Numpy Compatibility

There may be compatibility issues between numpy 2.x and scipy 1.16.x. If you encounter errors like:

```
ValueError: All ufuncs must have type `numpy.ufunc`. Received (<ufunc 'sph_legendre_p'>, ...)
```

**Quick Fix (Recommended):**

Run the automated fix script:

```bash
cd backend
./scripts/fix_dependencies.sh
```

**Manual Fix:**

1. **Ensure compatible versions** (requirements.txt specifies these):
   ```bash
   pip install "numpy>=1.24.0,<2.0.0"
   pip install "scipy>=1.11.0,<1.17.0"
   pip install --upgrade sentence-transformers scikit-learn
   ```

2. **Or reinstall from requirements.txt**:
   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

**Note**: `requirements.txt` has been updated to pin compatible versions. The fix script handles this automatically.

## Generating Embeddings

### Recipe Embeddings

Generate embeddings for all recipes:

```bash
cd backend
python scripts/generate_recipe_embeddings.py
```

**What it does:**
- Loads all active recipes from database
- Generates 384-dimensional embeddings using `all-MiniLM-L6-v2`
- Stores embeddings in `Recipe.embedding` column (JSON array)
- Processes in batches of 50 for efficiency

**Expected output:**
- ✅ Loaded sentence transformer model from model_cache
- Processing batch X/Y...
- ✅ Updated N recipes with embeddings
- 🎉 Successfully generated embeddings for N recipes!

### Ingredient Embeddings

Generate embeddings for all ingredients:

```bash
cd backend
python scripts/generate_ingredient_embeddings.py
```

**What it does:**
- Loads all ingredients from database
- Generates 384-dimensional embeddings using `all-MiniLM-L6-v2`
- Stores embeddings in `Ingredient.embedding` column (JSON array)
- Processes in batches of 100 for efficiency (larger batches since ingredient text is simpler)

**Expected output:**
- ✅ Loaded sentence transformer model from model_cache
- Processing batch X/Y...
- ✅ Updated N ingredients with embeddings
- 🎉 Successfully generated embeddings for N ingredients!

## Verification

After generating embeddings, verify they were created correctly:

```bash
python verify_database.py
```

This will check:
- Recipe count with embeddings (should be 800/800)
- Ingredient count with embeddings (should be 15,694/15,694)
- Embedding dimensions (should be 384)

## Usage in RAG

Once embeddings are generated, the RAG system will automatically use them for:
- Recipe similarity search
- Ingredient-based retrieval
- Duplicate prevention
- Enhanced AI recipe generation

The embeddings are used in:
- `backend/ai/nutrition_ai.py:_retrieve_similar_recipes()`
- Sequential prompting Step 1 (Initial Assessment + RAG retrieval)

## Troubleshooting

### Model cache not loading

If you see "model_cache embedding_model is None":
1. Check that sentence-transformers is installed: `pip install sentence-transformers`
2. Check numpy/scipy compatibility (see Known Issues above)
3. Try restarting Python environment

### Embeddings not being generated

If the script runs but no embeddings are created:
1. Check database connection
2. Verify recipes/ingredients exist in database
3. Check logs for specific error messages
4. Ensure model_cache.embedding_model is not None

### Slow generation

Embedding generation can take time:
- Recipes: ~10-15 minutes for 800 recipes
- Ingredients: ~30-45 minutes for 15,694 ingredients

This is normal. The scripts process in batches and commit after each batch to prevent data loss.

