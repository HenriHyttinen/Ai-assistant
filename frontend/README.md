# Frontend

React + TypeScript frontend for the health and nutrition platform. Built with Vite, Chakra UI, and React.

## Features

- **Health Dashboard** - Track health metrics, BMI, wellness score, and activity levels
- **Meal Planning** - Create and manage daily/weekly meal plans with AI-generated recipes
- **Recipe Search** - Search and filter recipes by cuisine, dietary restrictions, macronutrients, and more
- **Nutrition Tracking** - Track calories, macros, and micronutrients with visual charts
- **Goal Management** - Set and track nutrition goals with progress visualization
- **Shopping Lists** - Generate shopping lists from meal plans with ingredient categorization
- **Responsive Design** - Mobile-first design that works on all devices

## Prerequisites

- Node.js 18+ and npm
- Backend API running (see backend README)

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create environment file (if needed):
```bash
cp .env.example .env
```

3. Start development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173` (or the port Vite assigns)

## Building for Production

```bash
npm run build
```

The built files will be in the `dist/` directory.

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable React components
│   ├── pages/          # Page components
│   ├── services/        # API service functions
│   ├── lib/            # Utilities and configurations
│   ├── hooks/          # Custom React hooks
│   └── App.tsx         # Main app component
├── public/             # Static assets
└── package.json        # Dependencies
```

## Key Technologies

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Chakra UI** - Component library
- **Recharts** - Data visualization
- **React Router** - Navigation
- **Supabase** - Authentication client

## Development

### Running the Dev Server

```bash
npm run dev
```

### Building

```bash
npm run build
```

### Linting

```bash
npm run lint
```

## Environment Variables

Create a `.env` file in the frontend directory:

```
VITE_SUPABASE_URL=your-supabase-url
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
VITE_API_URL=http://localhost:8000
```

## Features Overview

### Health Dashboard
- View current health metrics (weight, BMI, wellness score)
- Track progress over time with charts
- Set and monitor health goals

### Meal Planning
- Generate daily or weekly meal plans
- Progressive meal generation (one slot at a time)
- Swap meals between dates
- Adjust portion sizes with live preview
- View meal alternatives

### Recipe Search
- Search by name, ingredients, or cuisine
- Filter by dietary preferences and allergies
- Filter by macronutrients (protein, carbs, fats)
- Filter by calories and prep time
- View recipe details and instructions

### Nutrition Tracking
- Daily nutritional intake tracking
- Macro and micronutrient analysis
- Visual charts for trends
- Goal progress tracking

## Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request
