# Numbers Don't Lie - Setup Guide

This is a wellness platform built with FastAPI (backend) and React (frontend) that helps users track their health metrics, set goals, and get personalized insights.

## Prerequisites

- **Python 3.11 or 3.12** (Python 3.14 NOT supported - many packages lack pre-built wheels)
- **Node.js 16+**
- **npm** or **yarn**
- **Git**
- **PostgreSQL 12+** (optional, SQLite works for development)

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
python database_setup/init_db.py

# Seed recipes and ingredients (optional but recommended)
python scripts/comprehensive_seeder.py

# Start the backend server
uvicorn main:app --reload
```

The backend will be available at:
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### 3. Frontend Setup

```bash
# Navigate to frontend directory (in a new terminal)
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:5173` (or the port Vite assigns)

### 4. Access the Application

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```env
# Database
DATABASE_URL=sqlite:///./numbers_dont_lie.db
# OR for PostgreSQL:
# DATABASE_URL=postgresql://postgres:postgres@localhost/numbers_dont_lie

# JWT Authentication
SECRET_KEY=your-random-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI (optional - for AI meal generation)
OPENAI_API_KEY=your-openai-api-key
USE_OPENAI=true

# Supabase (optional - for authentication)
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key

# Email (optional - for email verification)
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
```

## Database Setup

### Initialize Database

```bash
cd backend
python database_setup/init_db.py
```

This creates all necessary database tables.

### Seed Database (Optional but Recommended)

To populate the database with recipes and ingredients:

```bash
cd backend
python scripts/comprehensive_seeder.py
```

This seeds:
- 500+ recipes with vector embeddings
- 15,532+ ingredients with nutritional data
- Vector embeddings for RAG functionality

### Verify Database

To verify the database is set up correctly:

```bash
cd backend
python verify_database.py
```

## Features

### Core Features
- **User Authentication**: Email/password, Google OAuth, GitHub OAuth
- **Email Verification**: Account verification via email (with fallback to console output)
- **Password Reset**: Secure password reset with email tokens (with fallback to console output)
- **2FA Support**: Two-factor authentication with TOTP
- **Health Profile**: Complete health data collection and management
- **Meal Planning**: AI-generated meal plans with 17 dietary preferences and 13 allergies
- **Recipe Management**: 500+ recipe database with search and filtering
- **Nutrition Tracking**: Track calories, macros, and micronutrients
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

**Option A: Use Pre-configured Test Account (Recommended)**
```bash
cd backend
source venv/bin/activate
python create_test_account.py
```
Then login with:
- Email: `reviewer@test.com`
- Password: `testpass123`

**Option B: Create Your Own Account**
1. Go to http://localhost:5173
2. Click "Register" 
3. Fill in your details
4. Check your email for verification (if email is configured)
5. Verify your account using: `curl -X POST "http://localhost:8000/auth/verify-email-simple?email=your-email@example.com"`

### 2. Complete Health Profile
1. Navigate to "Health Profile"
2. Fill in your health metrics
3. Save your profile

### 3. Explore Features
- Dashboard: View your wellness score and AI insights
- Analytics: See your progress charts
- Meal Planning: Generate meal plans
- Recipe Search: Search and filter recipes
- Goals: Set and track health goals
- Settings: Change language and measurement system

## Troubleshooting

### Common Issues

**Backend won't start:**
- Check if Python virtual environment is activated
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check if port 8000 is available
- Verify Python version is 3.11 or 3.12

**Frontend won't start:**
- Check if Node.js is installed: `node --version`
- Install dependencies: `npm install`
- Check if port 5173 is available

**Database errors:**
- Delete database file and run `python database_setup/init_db.py` again
- Check DATABASE_URL in `.env`
- For SQLite, ensure write permissions
- For PostgreSQL, ensure it's running

**Email not working:**
- Check your email configuration in `.env`
- For Gmail, use an App Password instead of your regular password
- Email features are optional - the app works without email configuration
- If email fails, verification/reset links are shown in the console for development

**AI insights not working:**
- Add your OpenAI API key to `.env`
- Without the API key, the app will show mock insights
- Set `USE_OPENAI=false` to disable AI features

**Module import errors:**
- Make sure you're in the `backend/` directory when running scripts
- Ensure virtual environment is activated
- Verify all dependencies are installed

## Project Structure

```
numbers-dont-lie/
├── backend/                 # FastAPI backend
│   ├── ai/                 # AI integration (OpenAI, RAG)
│   ├── alembic/            # Database migrations
│   ├── analytics/          # Health metrics calculations
│   ├── auth/               # Authentication logic
│   ├── database_setup/     # Database initialization
│   ├── middleware/         # Rate limiting, CORS
│   ├── models/             # SQLAlchemy models
│   ├── routes/             # API endpoints
│   ├── schemas/            # Pydantic schemas
│   ├── services/           # Business logic
│   ├── scripts/            # Utility scripts (seeding, etc.)
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
├── docs/                    # Documentation
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

## Development Notes

- The project uses SQLite for development (easy setup)
- All data is stored locally in the database
- Email features work with SMTP configuration, but have fallbacks for development
- AI features require OpenAI API key (mock insights provided without key)
- OAuth features require Google/GitHub app configuration
- Email verification and password reset links are shown in console if email fails
- Database seeding is optional but recommended for full functionality

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request
