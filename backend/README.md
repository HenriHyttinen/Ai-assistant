# Numbers Don't Lie - Backend API

A FastAPI backend service powering the Numbers Don't Lie wellness platform. Provides RESTful APIs for health data management, user authentication, and analytics.

## Core Features

- **Secure Authentication** - JWT-based auth with OAuth2 (Google, GitHub) and 2FA support
- **Health Profile Management** - Comprehensive user health data and preferences
- **Activity Tracking** - Log and monitor daily activities and exercise routines
- **Analytics Engine** - Advanced health metrics calculation and trend analysis
- **Goal Management** - Set, track, and manage personal wellness objectives
- **Data Export** - Export user data in multiple formats for external analysis
- **AI Integration** - OpenAI-powered health recommendations and insights

## Prerequisites

- Python 3.8+
- PostgreSQL 12+
- pip (Python package manager)

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file in the backend directory with the following variables:
```
DATABASE_URL=postgresql://postgres:postgres@localhost/numbers_dont_lie
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

4. Initialize the database:
```bash
python init_db.py
```

5. Run database migrations:
```bash
alembic upgrade head
```

## Running the Server

To run the development server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:
- Swagger UI documentation: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`

## Testing

Run the test suite:
```bash
pytest
```

## Project Structure

```
backend/
├── alembic/              # Database migrations
├── models/              # SQLAlchemy models
├── routes/              # API endpoints
├── schemas/             # Pydantic models
├── services/            # Business logic
├── utils/               # Utility functions
├── alembic.ini          # Alembic configuration
├── database.py          # Database configuration
├── init_db.py           # Database initialization
├── main.py             # FastAPI application
└── requirements.txt     # Project dependencies
```

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run tests
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 