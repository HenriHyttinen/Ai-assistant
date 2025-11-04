# Essential Scripts for Reviewers

For reviewers, you only need **3 scripts** for setup:

## Required Scripts

### 1. `comprehensive_seeder.py` ⭐
**Purpose**: Seeds database with 500+ recipes and 500+ ingredients  
**Usage**: `python scripts/comprehensive_seeder.py`  
**Time**: ~5-10 minutes  
**When**: Initial database setup

### 2. `generate_recipe_embeddings.py` ⭐ (Optional but recommended)
**Purpose**: Generates vector embeddings for RAG (recipe search)  
**Usage**: `python scripts/generate_recipe_embeddings.py`  
**Requirements**: `sentence-transformers` package  
**Time**: ~5-15 minutes  
**When**: After seeding recipes

### 3. `seed_goals_direct.py` ⭐ (Optional)
**Purpose**: Seeds nutrition goal templates  
**Usage**: `python scripts/seed_goals_direct.py`  
**When**: Initial setup

## Quick Setup

```bash
cd backend
source venv/bin/activate

# 1. Seed recipes and ingredients (REQUIRED)
python scripts/comprehensive_seeder.py

# 2. Generate embeddings (OPTIONAL but recommended for RAG)
python scripts/generate_recipe_embeddings.py

# 3. Seed goal templates (OPTIONAL)
python scripts/seed_goals_direct.py
```

## That's It!

All other scripts in this folder are:
- Development maintenance scripts (one-time fixes)
- Legacy seeders (superseded by `comprehensive_seeder.py`)
- Testing/debugging scripts
- Data migration scripts (already applied)

**For review purposes, you can ignore all other scripts.**

