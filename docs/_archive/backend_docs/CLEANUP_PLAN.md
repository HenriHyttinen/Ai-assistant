# Scripts Cleanup Plan

## Current Situation
- **Total scripts**: ~77 Python files
- **Essential scripts**: 3
- **Legacy/obsolete**: ~74

## Essential Scripts (KEEP)

Only these 3 are needed for reviewers and production:

1. `comprehensive_seeder.py` - Seeds database with recipes/ingredients
2. `generate_recipe_embeddings.py` - Generates RAG embeddings  
3. `seed_goals_direct.py` - Seeds goal templates

## Recommendation

### Option 1: Archive (Recommended) ✅
Move all non-essential scripts to `_legacy/` folder:
- Keeps them for reference if needed
- Clean main scripts folder (3 files vs 77)
- Makes it obvious what reviewers need

### Option 2: Delete
Delete all non-essential scripts:
- Cleaner repository
- But loses development history

## Action Plan

I've created `move_legacy_scripts.sh` that will:
1. Create `_legacy/` folder
2. Move all scripts except the 3 essential ones
3. Keep documentation files

**To execute:**
```bash
cd backend/scripts
./move_legacy_scripts.sh
```

This will reduce the scripts folder from ~77 files to just **3 essential scripts + documentation**.

## After Cleanup

The `backend/scripts/` folder will contain:
```
scripts/
├── comprehensive_seeder.py          ⭐ Essential
├── generate_recipe_embeddings.py    ⭐ Essential
├── seed_goals_direct.py             ⭐ Essential
├── README.md
├── ESSENTIAL_SCRIPTS.md
├── KEEP_OR_REMOVE.md
└── _legacy/                         📦 All other scripts (for reference)
```

## Impact

✅ **Benefits:**
- Cleaner repository
- Clear what reviewers need
- Less confusion
- Faster navigation

❌ **No Loss:**
- All legacy scripts still available in `_legacy/`
- Development history preserved
- Can reference if needed

