# Numbers Don't Lie - Health Tracking App

A comprehensive wellness platform that leverages AI to provide personalized health insights, track wellness metrics, and guide users toward their health goals.

## For Reviewers - Quick Access

### Database Setup (Required First)
**If you get "no such table" errors, run this first:**
```bash
cd backend
source venv/bin/activate
python3 setup_database.py
```

### Option 1: Use Pre-configured Test Account (Recommended)
**Setup the test account:**
```bash
cd backend
source venv/bin/activate
python3 setup_reviewer_account.py
```

**Or manually (if script has issues):**
```bash
# 1. Register the account
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "reviewer@test.com", "password": "testpass123"}'

# 2. Verify the account  
curl -X POST "http://localhost:8000/auth/verify-email-simple?email=reviewer@test.com"
```

**Then login with:**
- Email: `reviewer@test.com`
- Password: `testpass123`

### Option 2: Create Your Own Account
1. **Register** with any email (e.g., `your-email@example.com`)
2. **Verify your account** using this simple command:
   ```bash
   curl -X POST "http://localhost:8000/auth/verify-email-simple?email=your-email@example.com"
   ```
3. **Login** with your email and password
4. **2FA Code** (if prompted): Use `123456` (after enabling 2FA in Settings)

**Demo Features to Test:**
- ✅ Health Profile (create/edit with translations)
- ✅ AI Insights (change fitness goals to see different recommendations)
- ✅ Data Consent (Settings → Data Consent)
- ✅ Multi-language support (Settings → Language)
- ✅ 2FA Setup (Settings → Two-Factor Authentication)

## Features

- **Health Profile** - Store your basic health info (weight, height, goals, etc.)
- **AI Insights** - Get personalized recommendations based on your data
- **Progress Tracking** - See your progress over time with charts
- **Goal Setting** - Set fitness goals and track progress
- **Secure Authentication** - Email/password + OAuth (Google, GitHub) + 2FA
- **Data Export** - Download your data if you want to switch apps

## Tech Stack

- **Backend**: Python with FastAPI
- **Frontend**: React with TypeScript (Vite)
- **Database**: SQLite
- **AI**: OpenAI API for recommendations
- **Auth**: JWT tokens + OAuth2 (Google, GitHub)
- **UI**: Chakra UI
- **Charts**: Recharts

## Quick Start

### Backend
```bash
cd backend
source venv/bin/activate
python -m uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

**URLs:**
- Frontend: http://localhost:5173 (or 5174/5175 if busy)
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Testing Features

### Email Verification
- Register through frontend
- Check backend console for verification command
- Run the curl command to verify
- Login with your credentials

### Two-Factor Authentication (2FA)
1. **Enable 2FA** - Go to Settings → Two-Factor Authentication
2. **Scan QR Code** - Use Google Authenticator or any TOTP app
3. **Save Backup Codes** - 8 recovery codes (save these!)
4. **Test Login** - Enter code from authenticator app or use backup codes

### Password Reset
1. **Request Reset** - Go to Login → "Forgot your password?"
2. **Check Console** - Backend shows reset link
3. **Reset Password** - Click link and set new password

## Setup

### Requirements
- Python 3.8+
- Node.js 16+
- OpenAI API key (optional - shows mock data without it)

### Environment Variables
Create `.env` in backend directory:
```
OPENAI_API_KEY=your_key_here
SECRET_KEY=some_random_string
DATABASE_URL=sqlite:///./app.db
```

### Installation
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python init_db.py

# Frontend
cd frontend
npm install
```

## Notes

- AI features work without API key (shows mock data)
- Email verification links display in console for testing
- All data stored locally in SQLite
