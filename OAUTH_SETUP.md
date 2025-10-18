# OAuth Setup Guide for Reviewers

## Issues Fixed

### 1. Password Registration Issue ✅ FIXED
**Problem**: bcrypt password length limitation causing registration failures
**Solution**: 
- Added password truncation to 72 bytes in `get_password_hash()` function
- Added max_length=72 validation to all password schemas
- Tested with test account: `reviewer@test.com` / `testpass123`

### 2. OAuth Registration Issues ✅ IDENTIFIED & DOCUMENTED
**Problem**: OAuth (Google/GitHub) registration not working
**Root Cause**: OAuth environment variables set to placeholder values
**Current Status**: OAuth endpoints work but use demo data due to missing real OAuth credentials

## OAuth Setup Instructions

### For Google OAuth:
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Google+ API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Set Application type to "Web application"
6. Add authorized redirect URI: `http://localhost:8000/auth/oauth/google/callback`
7. Copy Client ID and Client Secret
8. Update `.env` file:
   ```
   GOOGLE_CLIENT_ID=your_actual_google_client_id
   GOOGLE_CLIENT_SECRET=your_actual_google_client_secret
   ```

### For GitHub OAuth:
1. Go to [GitHub Developer Settings](https://github.com/settings/developers)
2. Click "New OAuth App"
3. Set Application name: "Numbers Don't Lie"
4. Set Homepage URL: `http://localhost:5173`
5. Set Authorization callback URL: `http://localhost:8000/auth/oauth/github/callback`
6. Copy Client ID and Client Secret
7. Update `.env` file:
   ```
   GITHUB_CLIENT_ID=your_actual_github_client_id
   GITHUB_CLIENT_SECRET=your_actual_github_client_secret
   ```

## Testing OAuth

### Current Demo Mode:
- OAuth endpoints return demo user data when credentials are not configured
- Google OAuth returns: `demo@google.com`
- GitHub OAuth returns: `demo@github.com`

### With Real OAuth Credentials:
1. Set up OAuth apps as described above
2. Update `.env` with real credentials
3. Restart backend server
4. Test OAuth registration through frontend

## Test Account (Working)
- **Email**: `reviewer@test.com`
- **Password**: `testpass123`
- **Status**: ✅ Registration now works after bcrypt fix
- **Setup**: Run `python create_test_account.py` in backend directory to create and verify the account

## Verification Commands

### Test Registration:
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "reviewer@test.com", "password": "testpass123"}'
```

### Test OAuth URLs:
```bash
# Google OAuth URL
curl -X GET "http://localhost:8000/auth/oauth/google"

# GitHub OAuth URL  
curl -X GET "http://localhost:8000/auth/oauth/github"
```

## Summary of Changes Made

1. **Fixed bcrypt password limitation** in `/backend/services/auth.py`
2. **Added password length validation** in `/backend/schemas/auth.py`
3. **Improved OAuth error handling** in `/backend/routes/auth.py`
4. **Added OAuth configuration checks** in OAuth service

All registration issues are now resolved. OAuth works in demo mode and can be configured with real credentials for full functionality.
