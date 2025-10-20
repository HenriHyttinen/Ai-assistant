# Reviewer Troubleshooting Guide

## Common Issues and Solutions

### 1. "no such table: user_settings" Error
**Problem:** You see this error in the backend logs or frontend console.

**Solution:**
```bash
cd backend
source venv/bin/activate
python3 setup_reviewer.py
```

### 2. CORS Errors in Frontend
**Problem:** You see "CORS Missing Allow Origin" errors in the browser console.

**Solution:**
- Make sure the backend is running on port 8000
- Make sure the frontend is running on port 5173
- Check that both are running simultaneously

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
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
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

## Quick Verification Steps

1. **Check Backend:** Visit http://localhost:8000 - should show API welcome message
2. **Check Frontend:** Visit http://localhost:5173 - should show login page
3. **Check Database:** Run `python3 setup_reviewer.py` if you get table errors
4. **Check Logs:** Look at terminal output for any error messages

## 7. "no such column: activity_logs.performed_at" Error

**Problem:** You see errors like `(sqlite3.OperationalError) no such column: activity_logs.performed_at` in the backend logs.

**Reason:** The database was created before the `performed_at` column was added to the `activity_logs` table.

**Solution:** Run the column fix script:

```bash
cd backend
source venv/bin/activate
python3 fix_performed_at_column.py
```

This will:
- Add the missing `performed_at` column to the `activity_logs` table
- Populate it with existing `created_at` values
- Fix the "no such column" error

After running this, restart your backend server.

---

## Getting Help

If you encounter issues not covered here:
1. Check the terminal logs for error messages
2. Make sure you're in the correct directory
3. Ensure virtual environment is activated (`source venv/bin/activate`)
4. Try the quick setup script: `python3 setup_reviewer.py`
