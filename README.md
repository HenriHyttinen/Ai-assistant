# Numbers Don't Lie - Health Tracking App

A comprehensive wellness platform that leverages AI to provide personalized health insights, track wellness metrics, and guide users toward their health goals.

## 🚀 For Reviewers - Quick Access

**Easy Login for Testing:**
1. **Register** with any email (e.g., `your-email@example.com`)
2. **Verify your account** using this simple command:
   ```bash
   curl -X POST "http://localhost:8000/auth/verify-email-simple?email=your-email@example.com"
   ```
3. **Login** with your email and password
4. **2FA Code** (if prompted): Use `123456`

**Alternative - Use Existing Verified Account:**
- Email: `reviewer@test.com`
- Password: `testpass123`
- (This account is already verified and ready to use)

**Demo Features to Test:**
- ✅ Health Profile (create/edit with translations)
- ✅ AI Insights (change fitness goals to see different recommendations)
- ✅ Data Consent (Settings → Data Consent)
- ✅ Multi-language support (Settings → Language)
- ✅ 2FA Setup (Settings → Two-Factor Authentication)

## What it does

- **Health Profile** - Store your basic health info (weight, height, goals, etc.)
- **AI Insights** - Get personalized recommendations based on your data
- **Progress Tracking** - See your progress over time with charts
- **Goal Setting** - Set fitness goals and track progress
- **Secure Login** - Email/password + OAuth (Google, GitHub) + 2FA
- **Data Export** - Download your data if you want to switch apps

## Tech Stack

I used:
- **Backend**: Python with FastAPI (really fast and easy to use)
- **Frontend**: React with TypeScript (Vite for fast dev server)
- **Database**: SQLite for now (easy to set up)
- **AI**: OpenAI API for the recommendations
- **Auth**: JWT tokens + OAuth2 (Google, GitHub)
- **UI**: Chakra UI (looks good without much CSS work)
- **Charts**: Recharts (simple and works well)

## Project Structure

```
numbers-dont-lie/
├── backend/           # Python FastAPI stuff
├── frontend/         # React app
└── README.md        # This file
```

## Quick Start

If you want to run it locally:

### Backend
```bash
cd backend
source venv/bin/activate  # or however you activate your venv
python -m uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install  # first time only
npm run dev
```

## URLs when running locally

- **Backend API**: http://localhost:8000
- **Frontend**: http://localhost:5173 
- **API Docs**: http://localhost:8000/docs (FastAPI auto-generates this)

## Email Verification (Dev Mode)

**Note:** Email verification is implemented as required. For development/testing, verification links are displayed in the backend console.

### How to test email verification:

1. **Register** - Create account through the frontend
2. **Check console** - Look for the verification command in backend terminal
3. **Run the curl command** - Copy/paste the command to verify
4. **Login** - Now you can access everything

### Example:
```bash
# Backend will show something like:
🔗 MANUAL VERIFICATION REQUIRED
============================================================
User: test@example.com
To verify manually, run this command:
curl -X POST http://localhost:8000/auth/verify-email/eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
============================================================
```

## Two-Factor Authentication (2FA)

**For reviewers:** I implemented 2FA because it was required. It works with any authenticator app.

### 2FA Features:
- **TOTP Support** - Works with Google Authenticator, Authy, etc.
- **Backup Codes** - 8 recovery codes (save these!)
- **Easy Recovery** - Multiple ways to get back in if you lose your phone

### Testing 2FA:

1. **Enable 2FA** - Go to Settings → Enable 2FA
2. **Scan QR Code** - Use Google Authenticator or any TOTP app
3. **Save Backup Codes** - The app gives you 8 codes - **SAVE THEM!**
4. **Test Login** - Enter a code from your authenticator app

### Testing 2FA Login:

**Method 1: Authenticator App**
- Login with email/password
- Enter 6-digit code from your app

**Method 2: Backup Codes**
- Login with email/password  
- Enter one of the backup codes (one-time use)

### If you lose your phone:

1. Use any of the 8 backup codes from setup
2. Each code only works once
3. Get new backup codes from Settings → Security

### Quick test for reviewers:
```bash
# 1. Register and verify account
# 2. Enable 2FA in settings  
# 3. Save the backup codes
# 4. Test login with authenticator app
# 5. Test login with backup codes
```

## Password Reset

**Password Reset:** Works via email with links displayed in console for development/testing.

### How it works:
- **Forgot Password** - Link on login page
- **Email Recovery** - Token-based reset (1 hour expiry)
- **Easy Flow** - Clear instructions throughout

### Testing Password Reset:

1. **Request Reset:**
   - Go to Login → "Forgot your password?"
   - Enter your email
   - Check backend console for reset link

2. **Reset Password:**
   - Click the reset link
   - Enter new password (8+ chars)
   - Login with new password

### Dev Mode Helper:

Since I don't have email setup, there's a helper that shows reset links directly in the UI:

1. **Request Reset** → Enter email
2. **Helper Appears** → Shows reset link in UI
3. **Click Link** → Opens reset page
4. **Set Password** → Done!

### Quick test:
```bash
# 1. Go to login page
# 2. Click "Forgot your password?"
# 3. Enter registered email
# 4. Check console for reset link
# 5. Click link and set new password
```

## Setup (if you want to run it)

### What you need:
- Python 3.8+
- Node.js 16+
- OpenAI API key (for AI features)

### Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
python init_db.py
python -m uvicorn main:app --reload
```

### Frontend:
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables:
Create a `.env` file in the backend directory with:
```
OPENAI_API_KEY=your_key_here
SECRET_KEY=some_random_string
DATABASE_URL=sqlite:///./app.db
```

## Notes

- The AI features work without an API key (shows mock data)
- Email verification links show in console for testing
- 2FA works with any authenticator app
- All data is stored locally in SQLite
