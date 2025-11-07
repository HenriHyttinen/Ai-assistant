# Docker Quick Fixes for Common Issues

## Issue 1: No Recipes Found

**Problem**: Recipe search returns no results.

**Solution**: Seed recipes into the database.

```bash
# Seed recipes and ingredients (takes a few minutes)
docker-compose exec app bash -c "cd /app/backend && python scripts/comprehensive_seeder.py"

# Or set SEED_RECIPES=true in docker-compose.yml and restart
docker-compose restart app
```

**Check if recipes exist**:
```bash
docker-compose exec app python -c "from database import SessionLocal; from models.recipe import Recipe; db = SessionLocal(); count = db.query(Recipe).filter(Recipe.is_active == True).count(); print(f'Active recipes: {count}'); db.close()"
```

## Issue 2: "Please set up your nutrition preferences first"

**Problem**: Meal plan generation fails because nutrition preferences don't exist.

**Solution**: Create nutrition preferences first through the frontend, or use the API:

```bash
# Check if preferences exist
docker-compose exec db psql -U postgres -d health_app -c "SELECT user_id, id FROM user_nutrition_preferences;"

# The frontend should create preferences when you set them up in the UI
# If that's failing, check backend logs:
docker-compose logs app --tail=100 | grep -i "nutrition preferences"
```

**Note**: The frontend should use `POST /nutrition/preferences` to create preferences, not `PUT` (which is for updating existing ones).

## Issue 3: 500 Error When Saving Preferences

**Problem**: PUT request to `/nutrition/preferences` returns 500.

**Cause**: PUT expects preferences to already exist. If they don't exist, it should return 404, but there might be a database error.

**Solution**:
1. Check backend logs for the actual error:
   ```bash
   docker-compose logs app --tail=100 | grep -i error
   ```

2. Make sure the `user_nutrition_preferences` table exists:
   ```bash
   docker-compose exec db psql -U postgres -d health_app -c "\d user_nutrition_preferences"
   ```

3. If table doesn't exist, restart the app to run migrations:
   ```bash
   docker-compose restart app
   ```

## Issue 4: Missing Database Tables

**Problem**: Errors like "relation does not exist" (e.g., `micronutrient_goals`).

**Solution**: Restart the app to run migrations with all models:

```bash
# Restart app (migrations run on startup)
docker-compose restart app

# Watch logs to see migrations
docker-compose logs -f app
```

## Quick Diagnostic Commands

```bash
# Check all container status
docker-compose ps

# Check backend logs
docker-compose logs app --tail=100

# Check database connection
docker-compose exec db pg_isready -U postgres

# Check if recipes table exists and has data
docker-compose exec db psql -U postgres -d health_app -c "SELECT COUNT(*) FROM recipes WHERE is_active = true;"

# Check if preferences table exists
docker-compose exec db psql -U postgres -d health_app -c "\d user_nutrition_preferences"

# Check all tables
docker-compose exec db psql -U postgres -d health_app -c "\dt"
```

## Complete Reset (if needed)

If everything is broken, you can reset:

```bash
# Stop all containers
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker-compose down -v

# Rebuild and start
docker-compose up -d --build

# Seed recipes (optional, takes time)
docker-compose exec app bash -c "cd /app/backend && SEED_RECIPES=true python scripts/comprehensive_seeder.py"
```

