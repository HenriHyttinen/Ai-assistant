# Docker Troubleshooting Guide

## 503 Service Unavailable Errors

If you're seeing 503 errors from the frontend, it means:
- ✅ Frontend is running (nginx is serving the frontend)
- ❌ Backend is not responding (backend API is not accessible)

## Step 1: Check Container Status

```bash
docker-compose ps
```

You should see:
- `db` (PostgreSQL) - Status should be "Up"
- `redis` - Status should be "Up"
- `app` (Backend) - Status should be "Up"

If `app` is not running or keeps restarting, check the logs.

## Step 2: Check Backend Logs

```bash
# View recent backend logs
docker-compose logs app --tail=100

# View all backend logs
docker-compose logs app

# Follow logs in real-time
docker-compose logs -f app
```

Look for:
- ✅ "Starting Numbers Don't Lie Health App..."
- ✅ "Database is ready!"
- ✅ "Backend started with PID..."
- ❌ Python errors
- ❌ Database connection errors
- ❌ Import errors

## Step 3: Check Database Connection

```bash
# Check if database is ready
docker-compose exec db pg_isready -U postgres

# Check database logs
docker-compose logs db --tail=20

# Test database connection from app container
docker-compose exec app python -c "
from database import engine
try:
    conn = engine.connect()
    print('✅ Database connection successful')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
"
```

## Step 4: Test Backend Directly

```bash
# Test backend health endpoint (bypass nginx)
curl http://localhost:8000/health

# Or from inside the container
docker-compose exec app curl http://localhost:8000/health

# Check if backend is listening on port 8000
docker-compose exec app netstat -tlnp | grep 8000
```

## Step 5: Check Nginx Configuration

```bash
# Check nginx logs
docker-compose exec app cat /var/log/nginx/error.log

# Test nginx configuration
docker-compose exec app nginx -t

# Check if nginx is running
docker-compose exec app ps aux | grep nginx
```

## Common Issues and Fixes

### Issue 1: Backend Container Not Running

**Symptoms:**
- `docker-compose ps` shows app container as "Exited" or "Restarting"

**Fix:**
```bash
# Restart the app container
docker-compose restart app

# Or rebuild and restart
docker-compose up -d --build app

# Check logs for errors
docker-compose logs app
```

### Issue 2: Database Connection Failed

**Symptoms:**
- Logs show: "could not connect to server"
- "Connection refused" errors

**Fix:**
```bash
# Check if database is running
docker-compose ps db

# Restart database
docker-compose restart db

# Wait for database to be ready
docker-compose exec db pg_isready -U postgres

# Check DATABASE_URL in app container
docker-compose exec app env | grep DATABASE_URL
```

### Issue 3: Backend Startup Error

**Symptoms:**
- Python import errors
- Missing modules
- Configuration errors

**Fix:**
```bash
# Check backend logs
docker-compose logs app | grep -i error

# Rebuild the container
docker-compose up -d --build app

# Check Python environment
docker-compose exec app python --version
docker-compose exec app pip list | grep -i fastapi
```

### Issue 4: Port Already in Use

**Symptoms:**
- "Address already in use" errors
- Port 8000 or 80 already taken

**Fix:**
```bash
# Check what's using port 8000
sudo lsof -i :8000

# Check what's using port 80
sudo lsof -i :80

# Stop conflicting services or change ports in docker-compose.yml
```

### Issue 5: Nginx Not Routing to Backend

**Symptoms:**
- Frontend loads but all API calls return 503
- Backend is running but nginx can't reach it

**Fix:**
```bash
# Check nginx configuration
docker-compose exec app cat /etc/nginx/nginx.conf | grep -A 5 "location"

# Test nginx routing
docker-compose exec app curl http://localhost:8000/health

# Restart nginx
docker-compose exec app nginx -s reload
```

## Quick Diagnostic Commands

Run these in sequence to diagnose the issue:

```bash
# 1. Check all containers
docker-compose ps

# 2. Check backend logs
docker-compose logs app --tail=50

# 3. Test database
docker-compose exec db pg_isready -U postgres

# 4. Test backend directly
curl http://localhost:8000/health

# 5. Test through nginx
curl http://localhost/health

# 6. Check nginx logs
docker-compose exec app tail -20 /var/log/nginx/error.log
```

## Restart Everything

If all else fails, restart all services:

```bash
# Stop all services
docker-compose down

# Remove volumes (clean slate - WARNING: deletes data)
docker-compose down -v

# Rebuild and start
docker-compose up -d --build

# Watch logs
docker-compose logs -f
```

## Getting Help

If you're still having issues, provide:
1. Output of `docker-compose ps`
2. Output of `docker-compose logs app --tail=100`
3. Output of `docker-compose logs db --tail=20`
4. Any error messages you see

