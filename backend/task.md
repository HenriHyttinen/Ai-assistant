# counting-calories

## The Situation 👀
Imagine transforming your wellness platform into a personalized nutrition companion that truly understands each user. In this project, you'll expand your wellness platform with AI-powered meal planning and recipe generation. Your app will take user dietary preferences, restrictions, and health goals (established in Project 1) and create customized meal plans, recipes and help the user plan and manage their nutrition. You will learn how to structure prompts for content generation, manage complex data relationships and further refine your AI integration skills. Furthermore, you will learn useful techniques to compensate for the problems commonly associated with LLM's.

## Functional Requirements 📋
The first step to planning nutrition is to understand the user - their personal data, goals, constraints and preferences. You'll expand on and confirm the information already gathered in the previous project in order to create a system that generates daily or weekly meal plans, with accompanying recipes and nutritional values, based on user-provided data and preferences.

### User Preference
Collect and utilize the following information:
- Dietary preferences (vegetarian, keto, etc.)
- Allergies and intolerances
- Disliked ingredients
- Cuisine preferences
- Calorie and macronutrient targets
- Meal frequency and timing

Your nutritional planning must support at least 15 different dietary preferences and 10 food allergies/intolerances.

All dates and times throughout the application are required to use ISO 8601 standard. This means that users will also need to be able to specify their timezone. Don't request information already collected in Project 1. Use AI to suggest defaults when users are uncertain.

### Meal Planning
Create an AI system that generates and manages meal plans that feel like they were crafted by a personal nutritionist. Created AI system must have these functionalities:

**AI-Powered Generation:**
- Daily and weekly meal plans with nutritional balance
- Flexible meal structures (e.g., 3 meals + 2 snacks)
- Meal details including names, default time (e.g. breakfast, lunch, dinner, snack), and nutritional information
- Alternative meal suggestions

**Customization Tools:**
- Swap generated meals in a plan
- Manual meal additions
- Regeneration options for whole meal plan or individual meals

**Shopping List:**
- Automated generation from meal plans
- Ingredient categorization (at least 5 meaningful categories)
- Ingredient quantity adjustments
- Option to remove ingredients from shopping list

**Example Meal Plan Input Structure**
```json
{
    "user_preferences": {
        "dietary_restrictions": ["vegetarian", "gluten-free"],
        "cuisine_preferences": ["Italian", "Mexican"],
        "disliked_ingredients": ["mushrooms", "tofu"],
        "calorie_target": 2000,
        "macronutrient_targets": {"protein": 100, "carbs": 200, "fats": 60},
        "meals_per_day": 3,
        "preferred_meal_times": {"breakfast": "2024-01-01T08:00:00Z", "lunch": "2024-01-01T12:30:00Z", "dinner": "2024-01-01T19:00:00Z"}
    },
    "meal_plan_request": {
        "duration": "daily", 
        "date": "2024-07-29",
        "version": "1.0",
        "created_at": "2024-07-28T14:30:00Z"
    }
}
```

### GenAI Techniques
**Sequential Prompting**  
- Break down meal planning into multiple steps:
  - Initial Assessment: Analyze user profile to define meal plan strategy
  - Meal Structure: Design specific meals and timing
  - Recipe Generation: Creates detailed recipes
  - Nutritional Analysis: Evaluate nutritional balance
  - Refinement: Adjust to address nutritional gaps
- Your prompt sequence must have at least 3 steps.

**Function Calling**  
- Specialized functions for nutritional calculations
- Define functions, expose to AI, handle calls, process results

**Retrieval-Augmented Generation (RAG)**  
- Combine AI creativity with real recipes
- Retrieve relevant recipes, augment prompts, generate customized recipes
- Recipe database: ≥500 recipes and ≥500 ingredients
- Implement vector embeddings and relevance-based search

### Feature Requirements
**Recipe Management**
- Search and Filtering
- Recipe Details
- AI Recipe Generation
- Ingredient Substitution
- Portion Adjustment

**Data Structures**
- Standardized units for solids (g), liquids (ml), energy (kcal), and time (minutes)
- Recipe JSON and Nutrient Information JSON with all required fields

**Nutritional Analysis**
- Macro Tracking
- Goal Tracking
- AI-Driven Analysis

**Cross-Feature Integration**
- Daily progress tracking, historical analysis, AI-powered suggestions, integration with health data

**Important Considerations ❗**
- AI Model Selection
- Prompt Engineering
- Parameter Optimization
- Error Handling and API Reliability
- Content Management

**Extra requirements 📚**
- Dockerization
- Micronutrients
- Community-driven RAG
- Enhanced Nutritional Data

**Bonus functionality 🎁**
- Optional extra features

**What you'll learn 🧠**
- Structured content generation with AI
- Managing complex data relationships
- Parameter-based AI output control
- Iterative prompt refinement methodology
- Retrieval-augmented generation implementation
- Function calling for specialized tasks
- Sequential prompting for complex workflows
- Advanced AI integration strategies

### Deliverables and Review Requirements 📁
- Complete source code and configuration files
- Project documentation including overview, setup, usage, prompt engineering strategy, model rationale, data model documentation, error handling approach, bonus functionality
- Demonstrate full system functionality
- Explain design choices, integration with Project 1, and challenges solved

### Mandatory
- README contains project overview, setup instructions, usage guide
- Nutritional planning supports ≥15 dietary preferences and ≥10 allergies/intolerances
- System generates complete daily/weekly meal plans
- Meal structures customizable, alternative meal options
- Shopping list generation and modification
- Sequential prompting with ≥3 steps
- RAG with ≥500 recipes and ingredients
- Function calling for nutritional calculations
- Recipe and ingredient data structures complete
- Nutritional analysis with visualization and AI insights
- Error handling, fallback mechanisms, and content versioning

**Extra**
- Dockerized project
- Micronutrient tracking
- Community-driven RAG improvements
- Enhanced nutritional data
- Optional advanced features

### Evaluation Criteria
- Code quality and organization
- Documentation completeness and clarity
- Consistency in error handling and UX
- Testing coverage and quality
- Best practices implementation
- Professional-grade attention to detail
