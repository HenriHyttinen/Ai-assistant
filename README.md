# Numbers Don't Lie - Health Tracking App

A comprehensive wellness platform that leverages AI to provide personalized health insights, track wellness metrics, and guide users toward their health goals.

## For Reviewers - Quick Access

### Quick Fix for Missing Dependencies
**If you get `ModuleNotFoundError: No module named 'supabase'` or `No module named 'lib'`:**
```bash
cd backend
source venv/bin/activate
python fix_dependencies.py
```

**Manual fix if the script doesn't work:**
```bash
cd backend
source venv/bin/activate
pip install supabase==2.3.0
touch lib/__init__.py auth/__init__.py ai/__init__.py middleware/__init__.py schemas/__init__.py
```

### Database Setup (Required First)
**If you get "no such table" errors, run this first:**

**For Quick Setup (Recommended for Reviewers):**
```bash
cd backend/database_setup
source ../venv/bin/activate
python3 setup_reviewer.py
```

**For Full Setup:**
```bash
cd backend/database_setup
source ../venv/bin/activate
python3 setup_database.py
```

**Having Issues?** See [docs/REVIEWER_TROUBLESHOOTING.md](docs/REVIEWER_TROUBLESHOOTING.md) for common problems and solutions.

### Option 1: Use Pre-configured Test Account (Recommended)
**Setup the test account:**
```bash
cd backend/database_setup
source ../venv/bin/activate
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
- **AI-Powered Insights** - Get personalized health recommendations using OpenAI GPT-3.5
- **Multi-language Support** - AI insights in English, Spanish, French, and German
- **Progress Tracking** - See your progress over time with charts
- **Goal Setting** - Set fitness goals and track progress
- **Secure Authentication** - OAuth (Google, GitHub, Discord, Facebook, Apple) + Supabase
- **Data Export** - Download your data if you want to switch apps
- **Dietary Restrictions** - AI respects your dietary needs and restrictions
- **Fallback System** - Works without AI when API is unavailable

## Project Structure

```
numbers-dont-lie/
├── backend/                 # FastAPI backend
│   ├── database_setup/     # Database scripts and migrations
│   ├── models/            # Database models
│   ├── routes/            # API endpoints
│   ├── services/          # Business logic
│   └── static/            # Static files
├── frontend/              # React frontend
├── docs/                  # Documentation
├── tests/                 # Test HTML files
├── oauth-pages/           # OAuth consent pages
└── README.md
```

## Tech Stack

- **Backend**: Python with FastAPI
- **Frontend**: React with TypeScript (Vite)
- **Database**: SQLite
- **AI**: OpenAI GPT-3.5 Turbo for personalized health insights
- **Auth**: Supabase Auth + OAuth2 (Google, GitHub, Discord, Facebook, Apple)
- **UI**: Chakra UI
- **Charts**: Recharts
- **Rate Limiting**: Custom sliding window algorithm
- **CORS**: Configured for development and production

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
- OpenAI API key (for AI insights - fallback available without it)

### Environment Variables
The `.env` file is already configured with:
```
# AI Configuration
OPENAI_API_KEY=sk-proj-... (configured)
USE_OPENAI=true

# Supabase Configuration  
SUPABASE_URL=https://idaenyycsiewbvxtdecn.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# OAuth Providers (configured)
GOOGLE_CLIENT_ID=409374284979-...
GITHUB_CLIENT_ID=Ov23liz8cgEtvuAlwlnh
# Discord, Facebook, Apple also configured
```

### Installation
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd database_setup
python init_db.py

# Frontend
cd frontend
npm install
```

### Troubleshooting

**If you get `ModuleNotFoundError: No module named 'supabase'`:**
```bash
cd backend
source venv/bin/activate
pip install supabase==2.3.0
```

**If you get `ModuleNotFoundError: No module named 'lib'` or similar:**
```bash
cd backend
touch lib/__init__.py auth/__init__.py ai/__init__.py middleware/__init__.py schemas/__init__.py
```

**If you get import errors:**
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

**Complete fix for all common issues:**
```bash
cd backend
source venv/bin/activate
python fix_dependencies.py
```

## AI Features

### AI-Powered Health Insights
- **Personalized Recommendations**: Based on your health profile, goals, and activity data
- **Multi-language Support**: Insights in English, Spanish, French, and German
- **Dietary Restrictions**: AI respects your dietary needs and medical conditions
- **Goal-Oriented**: Tailored advice based on your active fitness goals
- **Fallback System**: Works without OpenAI API (shows general health tips)

### AI Configuration
- **Model**: OpenAI GPT-3.5 Turbo
- **Cost Control**: Intelligent fallback when API is unavailable
- **Data Privacy**: Health data is normalized and PII is removed before AI processing
- **Rate Limiting**: Prevents API abuse and controls costs

## Notes

- AI features work with fallback when API is unavailable
- All OAuth providers are configured and working
- All data stored locally in SQLite
- Rate limiting prevents API abuse
- CORS configured for development and production
