# Numbers Don't Lie - Setup Guide

This is a wellness platform built with FastAPI (backend) and React (frontend) that helps users track their health metrics, set goals, and get AI-powered insights.

## Prerequisites

- Python 3.8+ 
- Node.js 16+
- npm or yarn
- Git

## Quick Setup

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd numbers-dont-lie
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration (see Environment Variables section)

# Initialize database
python init_db.py

# Run database migrations
alembic upgrade head

# Start the backend server
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

### 4. Access the Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```env
# Database
DATABASE_URL=sqlite:///./dev.db

# Email (for development - optional)
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=your-email@example.com
MAIL_PORT=587
MAIL_SERVER=smtp.gmail.com
MAIL_FROM_NAME=Numbers Dont Lie
MAIL_STARTTLS=true
MAIL_SSL_TLS=false
USE_CREDENTIALS=true

# OAuth (optional - for Google/GitHub login)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret

# OpenAI API (optional - for AI insights)
OPENAI_API_KEY=your-openai-api-key

# JWT Secret (generate a random string)
SECRET_KEY=your-super-secret-jwt-key
```

## Features

### Core Features
- **User Authentication**: Email/password, Google OAuth, GitHub OAuth
- **Email Verification**: Account verification via email (with fallback to console output)
- **Password Reset**: Secure password reset with email tokens (with fallback to console output)
- **2FA Support**: Two-factor authentication with TOTP
- **Health Profile**: Complete health data collection and management
- **AI Insights**: Personalized health recommendations (requires OpenAI API key)
- **Analytics**: Data visualization and progress tracking
- **Goals Management**: Set and track health/fitness goals
- **Settings**: Language preferences, measurement system (metric/imperial)
- **Data Export**: GDPR-compliant data export

### Internationalization
- 4 Languages: English, Spanish, French, German
- Measurement Systems: Metric (kg/cm) and Imperial (lbs/inches)
- Real-time Translation: All UI elements translated dynamically

### Security Features
- Rate Limiting: API abuse prevention
- Input Validation: Comprehensive data validation
- Error Handling: Graceful error handling with user-friendly messages
- CORS Configuration: Proper cross-origin resource sharing

## Testing the Application

### 1. Create a Test Account
1. Go to http://localhost:5173
2. Click "Register" 
3. Fill in your details
4. Check your email for verification (if email is configured)
5. Verify your account

### 2. Complete Health Profile
1. Navigate to "Health Profile"
2. Fill in your health metrics
3. Save your profile

### 3. Explore Features
- Dashboard: View your wellness score and AI insights
- Analytics: See your progress charts
- Goals: Set and track health goals
- Settings: Change language and measurement system

## Troubleshooting

### Common Issues

**Backend won't start:**
- Check if Python virtual environment is activated
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8000 is available

**Frontend won't start:**
- Check if Node.js is installed: `node --version`
- Install dependencies: `npm install`
- Check if port 5173 is available

**Database errors:**
- Delete `dev.db` and run `python init_db.py` again
- Check if Alembic migrations are up to date: `alembic upgrade head`

**Email not working:**
- Check your email configuration in `.env`
- For Gmail, use an App Password instead of your regular password
- Email features are optional - the app works without email configuration
- If email fails, verification/reset links are shown in the console for development

**AI insights not working:**
- Add your OpenAI API key to `.env`
- Without the API key, the app will show mock insights

## Project Structure

```
numbers-dont-lie/
├── backend/                 # FastAPI backend
│   ├── ai/                 # AI insights generation
│   ├── alembic/            # Database migrations
│   ├── analytics/          # Health metrics calculations
│   ├── auth/               # Authentication logic
│   ├── middleware/         # Rate limiting, CORS
│   ├── models/             # SQLAlchemy models
│   ├── routes/             # API endpoints
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   ├── templates/          # Email templates
│   ├── utils/              # Utility functions
│   ├── main.py             # FastAPI app
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── public/             # Static assets
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── contexts/       # React contexts
│   │   ├── hooks/          # Custom hooks
│   │   ├── layouts/        # Layout components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── utils/          # Utility functions
│   ├── package.json        # Node dependencies
│   └── vite.config.ts      # Vite configuration
├── .gitignore              # Git ignore rules
├── README.md               # Project overview
└── SETUP.md                # This file
```

## Production Deployment

For production deployment:

1. **Environment Variables**: Set production values in `.env`
2. **Database**: Use PostgreSQL instead of SQLite
3. **Security**: Generate strong SECRET_KEY and JWT secrets
4. **Email**: Configure production email service
5. **Frontend**: Build with `npm run build`
6. **Backend**: Use production WSGI server (Gunicorn)

## What's Actually Implemented

### Email System
- **Full email infrastructure**: SMTP configuration, HTML templates, FastMail integration
- **Email verification**: Complete flow with HTML email templates
- **Password reset**: Complete flow with secure tokens and HTML templates
- **Development fallback**: If email fails, links are printed to console
- **Templates included**: verification_email.html, password_reset_email.html, 2fa_setup_email.html

### OAuth Authentication
- **Google OAuth**: Complete implementation with AuthLib integration
- **GitHub OAuth**: Complete implementation with AuthLib integration
- **OAuth callbacks**: Proper redirect handling and user creation
- **Environment variables**: GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET

### 2FA System
- **TOTP implementation**: Complete two-factor authentication
- **QR code generation**: For authenticator app setup
- **Backup codes**: Recovery mechanism
- **Email notifications**: 2FA setup instructions via email

## Development Notes

- The project uses SQLite for development (easy setup)
- All data is stored locally in the database
- Email features work with SMTP configuration, but have fallbacks for development
- AI insights require OpenAI API key (mock insights provided without key)
- OAuth features require Google/GitHub app configuration
- Email verification and password reset links are shown in console if email fails

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

