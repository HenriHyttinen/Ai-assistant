# Docker Setup Instructions

## Fixing Docker Permissions

If you get a "Permission denied" error when running `docker-compose`, you need to add your user to the `docker` group.

### Step 1: Add your user to the docker group

Run this command (it will ask for your password):

```bash
sudo usermod -aG docker $USER
```

### Step 2: Apply the group changes

You have two options:

**Option A: Log out and log back in** (recommended)
- Close your terminal/session completely
- Log out and log back into your system
- The group membership will be active in new sessions

**Option B: Use newgrp** (works immediately in current session)
```bash
newgrp docker
```

### Step 3: Verify it works

After applying the group changes, verify Docker works:

```bash
docker ps
```

If this works without errors, you're all set!

## Building and Running with Docker

Once permissions are fixed, you can build and run the application:

```bash
# Build and start all services
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v
```

## Seeding Recipes and Ingredients

To seed the database with recipes and ingredients (optional, takes 10-20 minutes):

**When `SEED_RECIPES=true` is set, the Docker container will automatically:**
1. Seed basic recipes and ingredients (~155 ingredients)
2. Import full ingredient database (adds 5,388 ingredients)
3. Generate recipe embeddings (REQUIRED for RAG - takes 5-15 minutes)
4. Generate ingredient embeddings (REQUIRED for RAG - takes 2-5 minutes)
5. Recalculate recipe nutrition from ingredients (fixes 0 calorie issue)

```bash
# Option 1: Set environment variable in docker-compose.yml
# Add this to the app service environment section:
# SEED_RECIPES=true

# Option 2: Run manually after startup
docker-compose exec app bash -c "cd /app/backend && python scripts/comprehensive_seeder.py"
docker-compose exec app bash -c "cd /app/backend && python scripts/import_ingredients_from_json.py"
docker-compose exec app bash -c "cd /app/backend && python scripts/generate_recipe_embeddings.py"
docker-compose exec app bash -c "cd /app/backend && python scripts/generate_ingredient_embeddings.py"
docker-compose exec app bash -c "cd /app/backend && python scripts/recalculate_recipe_nutrition.py"
```

## Troubleshooting

### Still getting permission errors?

1. Make sure you logged out and back in after adding to docker group
2. Verify group membership: `groups | grep docker`
3. Check docker socket permissions: `ls -la /var/run/docker.sock`
4. Try: `sudo chmod 666 /var/run/docker.sock` (less secure, temporary fix)

### Docker daemon not running?

```bash
# Check if Docker is running
sudo systemctl status docker

# Start Docker if not running
sudo systemctl start docker

# Enable Docker to start on boot
sudo systemctl enable docker
```

