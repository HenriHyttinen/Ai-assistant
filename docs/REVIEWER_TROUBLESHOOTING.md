# Reviewer Troubleshooting Guide

## Common Issues and Solutions

### 1. "no such table: user_settings" Error
**Problem:** You see this error in the backend logs or frontend console.

**Solution:**
```bash
cd backend
source venv/bin/activate
python database_setup/init_db.py
```

This will create all necessary database tables.

### 2. CORS Errors in Frontend
**Problem:** You see "CORS Missing Allow Origin" errors in the browser console.

**Solution:**
- Make sure the backend is running on port 8000
- Make sure the frontend is running on port 5173
- Check that both are running simultaneously
- Verify CORS settings in `backend/main.py`

### 3. "Failed to load dashboard data" Error
**Problem:** New users see this error instead of the welcome message.

**Solution:**
- This should be fixed automatically with the latest code
- If you still see it, refresh the page
- The dashboard should now show "Welcome to Your Health Journey!" for new users

### 4. Backend Not Starting
**Problem:** Backend fails to start with "No module named uvicorn"

**Solution:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### 5. Frontend Not Starting
**Problem:** Frontend fails to start

**Solution:**
```bash
cd frontend
npm install
npm run dev
```

### 6. Port Already in Use
**Problem:** You get "Address already in use" errors

**Solution:**
- Kill existing processes: `pkill -f uvicorn` and `pkill -f vite`
- Or use different ports by setting environment variables
- Check what's using the port: `lsof -i :8000` (backend) or `lsof -i :5173` (frontend)

### 7. Database Not Found
**Problem:** You see "no such table" errors

**Solution:**
```bash
cd backend
source venv/bin/activate
python database_setup/init_db.py
```

This creates all necessary database tables.

### 8. "no such column: activity_logs.performed_at" Error
**Problem:** You see errors like `(sqlite3.OperationalError) no such column: activity_logs.performed_at` in the backend logs.

**Reason:** The database was created before the `performed_at` column was added to the `activity_logs` table.

**Solution:** Run the column fix script:

```bash
cd backend
source venv/bin/activate
python database_setup/fix_performed_at_column.py
```

This will:
- Add the missing `performed_at` column to the `activity_logs` table
- Populate it with existing `created_at` values
- Fix the "no such column" error

After running this, restart your backend server.

### 9. Python Version Issues
**Problem:** Package installation fails with compilation errors

**Solution:**
- Use Python 3.11 or 3.12 (Python 3.14 NOT supported)
- Check Python version: `python3 --version`
- Create new virtual environment with correct Python version

### 10. Module Import Errors
**Problem:** "ModuleNotFoundError: No module named 'models'"

**Solution:**
- Make sure you're in the `backend/` directory when running scripts
- Ensure virtual environment is activated
- Verify all dependencies are installed: `pip install -r requirements.txt`

## Quick Verification Steps

1. **Check Backend:** Visit http://localhost:8000 - should show API welcome message
2. **Check Frontend:** Visit http://localhost:5173 - should show login page
3. **Check API Docs:** Visit http://localhost:8000/docs - should show Swagger UI
4. **Check Database:** Run `python database_setup/init_db.py` if you get table errors
5. **Check Logs:** Look at terminal output for any error messages

## Getting Help

If you encounter issues not covered here:
1. Check the terminal logs for error messages
2. Make sure you're in the correct directory (`backend/` for backend scripts)
3. Ensure virtual environment is activated (`source venv/bin/activate`)
4. Verify all dependencies are installed
5. Check the main SETUP_FOR_REVIEWERS.md for detailed setup instructions
