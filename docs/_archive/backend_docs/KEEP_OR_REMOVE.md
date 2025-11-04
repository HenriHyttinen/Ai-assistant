# Scripts: Keep or Remove?

## ✅ KEEP (Essential for Reviewers)

These 3 scripts are the **only ones reviewers need**:

1. **`comprehensive_seeder.py`** ⭐
   - Seeds 500+ recipes and ingredients
   - Referenced in all setup docs
   - Used by `setup_complete.sh`

2. **`generate_recipe_embeddings.py`** ⭐
   - Generates RAG embeddings
   - Referenced in setup docs
   - Used by `setup_complete.sh`

3. **`seed_goals_direct.py`** ⭐
   - Seeds goal templates
   - Referenced in Docker startup

**Total to keep: 3 scripts**

## ❌ REMOVE/MOVE TO ARCHIVE

All other ~82 scripts are:
- **One-time fixes** from development iterations
- **Legacy seeders** superseded by `comprehensive_seeder.py`
- **Test/debug scripts** not needed for production
- **Data migration scripts** (already applied)

### Categories to Archive:

#### Old Seeders (65+ scripts) - All superseded by `comprehensive_seeder.py`
- All `create_*.py` scripts
- All `generate_*.py` (except `generate_recipe_embeddings.py`)
- All `import_*.py` scripts
- All `*_seeder.py` (except `comprehensive_seeder.py`)

#### Fix Scripts (15+ scripts) - One-time fixes already applied
- All `fix_*.py` scripts
- All `verify_*.py` scripts
- All `replace_*.py` scripts
- All `*_fix.py` scripts

#### Migration Scripts - Already applied
- `add_*.py` (column migrations)
- `migrate_*.py`
- `convert_*.py`

#### Test/Utility Scripts
- `test_*.py`
- `comprehensive_test.py`
- `generate_random_ingredients.py`
- `export_*.py`
- `fetch_*.py`

## Recommendation

**Option 1: Archive (Recommended)**
Move all non-essential scripts to `scripts/_legacy/` folder:
- Keeps them for reference if needed
- Cleans up main scripts folder
- Makes it clear what reviewers need

**Option 2: Delete**
Delete all non-essential scripts:
- Cleaner repository
- Less confusion
- But loses development history

## Script Count

| Category | Count |
|----------|-------|
| **Essential (Keep)** | 3 |
| **Legacy (Archive/Delete)** | ~82 |
| **Total** | ~85 |

## Next Steps

1. Create `scripts/_legacy/` folder
2. Move non-essential scripts there
3. Update documentation to reference only essential scripts
4. Add `.gitkeep` to `_legacy/` if empty (or ignore it)

