import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardHeader,
  CardBody,
  Heading,
  Text,
  Button,
  VStack,
  HStack,
  Badge,
  Select,
  Input,
  FormControl,
  FormLabel,
  Textarea,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  useDisclosure,
  useColorModeValue,
  Alert,
  AlertIcon,
  Spinner,
  Center,
  Divider,
  IconButton,
  Menu,
  MenuButton,
  MenuList,
  MenuItem
} from '@chakra-ui/react';
import { t } from '../../utils/translations';
import CustomMealModal from '../../components/nutrition/CustomMealModal';
import MealPlanVersionHistory from '../../components/nutrition/MealPlanVersionHistory';
import MealPlanVersionComparison from '../../components/nutrition/MealPlanVersionComparison';
import { 
  FiPlus, 
  FiEdit, 
  FiTrash2, 
  FiRefreshCw,
  FiCoffee,
  FiClock,
  FiTarget,
  FiMoreVertical,
  FiLogIn,
  FiMove,
  FiArrowUp,
  FiArrowDown,
  FiRotateCcw,
  FiShoppingCart,
  FiUsers,
  FiGitBranch
} from 'react-icons/fi';

interface Meal {
  id: string;
  name?: string;
  meal_name?: string;
  type?: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  meal_type?: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  calories: number;
  protein: number;
  carbs: number;
  fats: number;
  prepTime?: number;
  prep_time?: number;
  cook_time?: number;
  difficulty?: 'easy' | 'medium' | 'hard';
  difficulty_level?: 'easy' | 'medium' | 'hard';
  dietaryTags?: string[];
  dietary_tags?: string[];
  ingredients?: Array<{name: string, quantity: number, unit: string}> | string[];
  instructions?: Array<{step: number, description: string}> | string[];
}

interface MealPlan {
  id: string;
  date: string;
  meals: Meal[];
  total_nutrition: {
    calories: number;
    protein: number;
    carbs: number;
    fats: number;
  };
}

interface MealPlanningProps {
  user?: any;
}

const MealPlanning: React.FC<MealPlanningProps> = ({ user = null }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mealPlan, setMealPlan] = useState<MealPlan | null>(null);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [planType, setPlanType] = useState<'daily' | 'weekly'>('daily');
  const [preferences, setPreferences] = useState({
    dietaryRestrictions: [] as string[],
    allergies: [] as string[],
    cuisinePreferences: [] as string[],
    calorieTarget: 2000,
    mealsPerDay: 3
  });

  const { isOpen, onOpen, onClose } = useDisclosure();
  const [selectedMeal, setSelectedMeal] = useState<Meal | null>(null);
  const [selectedRecipe, setSelectedRecipe] = useState<Meal | null>(null);
  const { isOpen: isRecipeOpen, onOpen: onRecipeOpen, onClose: onRecipeClose } = useDisclosure();
  const [alternatives, setAlternatives] = useState<{[key: string]: any[]}>({});
  
  // Versioning state
  const [showVersionHistory, setShowVersionHistory] = useState(false);
  const [versionComparison, setVersionComparison] = useState<{version1Id?: string, version2Id?: string}>({});
  const [loadingAlternatives, setLoadingAlternatives] = useState<{[key: string]: boolean}>({});
  const { isOpen: isCustomMealOpen, onOpen: onCustomMealOpen, onClose: onCustomMealClose } = useDisclosure();

  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    loadMealPlan();
  }, [selectedDate, planType]);

  const loadMealPlan = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get Supabase session token for authentication
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      const headers = session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
      
      // Try to load existing meal plan for the selected date
      const response = await fetch(`http://localhost:8000/nutrition/meal-plans?date=${selectedDate}&limit=1`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...headers
        }
      });
      
      if (response.ok) {
        const mealPlans = await response.json();
        console.log('Meal plans from API:', mealPlans);
        if (mealPlans.length > 0) {
          console.log('Setting meal plan:', mealPlans[0]);
          setMealPlan(mealPlans[0]);
          return;
        }
      }
      
      // If no meal plan exists, show empty state
      setMealPlan(null);
      
    } catch (err) {
      console.error('Error loading meal plan:', err);
      setError('Failed to load meal plan');
      setMealPlan(null);
    } finally {
      setLoading(false);
    }
  };

  const generateMealPlan = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Clear current meal plan to show loading state
      setMealPlan(null);
      
      // Get Supabase session token for authentication
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        setError('Please log in to generate meal plans');
        return;
      }
      
      const headers = { Authorization: `Bearer ${session.access_token}` };
      console.log('Generating meal plan with authentication');
      console.log('Calorie target:', preferences.calorieTarget);
      
      // Generate new meal plan using AI
      const response = await fetch('http://localhost:8000/nutrition/meal-plans/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...headers
        },
        body: JSON.stringify({
          plan_type: planType,
          start_date: selectedDate,
          end_date: planType === 'weekly' ? new Date(new Date(selectedDate).getTime() + 6 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] : selectedDate,
          generation_strategy: 'balanced',
          preferences_override: {
            daily_calorie_target: preferences.calorieTarget,
            meals_per_day: preferences.mealsPerDay,
            dietary_preferences: preferences.dietaryRestrictions,
            allergies: preferences.allergies,
            cuisine_preferences: preferences.cuisinePreferences
          }
        })
      });
      
          if (response.ok) {
            const newMealPlan = await response.json();
            console.log('Generated meal plan:', newMealPlan);
            setMealPlan(newMealPlan);
          } else if (response.status === 400) {
            const errorData = await response.json();
            if (errorData.detail && errorData.detail.includes('nutrition preferences')) {
              setError('Please set up your nutrition preferences first. Go to the Nutrition Dashboard to configure your preferences.');
            } else {
              throw new Error('Failed to generate meal plan');
            }
          } else {
            throw new Error('Failed to generate meal plan');
          }
    } catch (err) {
      console.error('Error generating meal plan:', err);
      setError('Failed to generate meal plan');
    } finally {
      setLoading(false);
    }
  };

  const handleMealEdit = (meal: Meal) => {
    setSelectedMeal(meal);
    onOpen();
  };

  const handleViewRecipe = (meal: Meal) => {
    setSelectedRecipe(meal);
    onRecipeOpen();
  };

  const loadAlternatives = async (mealType: string) => {
    if (!mealPlan?.id) return;
    
    setLoadingAlternatives(prev => ({ ...prev, [mealType]: true }));
    
    try {
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        setError('Please log in to load alternatives');
        return;
      }
      
      const response = await fetch(
        `http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/alternatives/${mealType}?count=3`,
        {
          headers: { Authorization: `Bearer ${session.access_token}` }
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        setAlternatives(prev => ({ ...prev, [mealType]: data.alternatives }));
      }
    } catch (err) {
      console.error('Error loading alternatives:', err);
    } finally {
      setLoadingAlternatives(prev => ({ ...prev, [mealType]: false }));
    }
  };

  const selectAlternative = (mealType: string, alternative: any) => {
    if (!mealPlan) return;
    
    const updatedMeals = mealPlan.meals.map(meal => 
      meal.meal_type === mealType ? alternative : meal
    );
    
    setMealPlan({
      ...mealPlan,
      meals: updatedMeals
    });
    
    // Clear alternatives for this meal type
    setAlternatives(prev => ({ ...prev, [mealType]: [] }));
  };

  const reorderMeal = async (mealId: string, direction: 'up' | 'down') => {
    if (!mealPlan) return;
    
    const meals = [...mealPlan.meals];
    const currentIndex = meals.findIndex(meal => meal.id === mealId);
    
    if (currentIndex === -1) return;
    
    const newIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1;
    
    // Check bounds
    if (newIndex < 0 || newIndex >= meals.length) return;
    
    // Swap meals
    [meals[currentIndex], meals[newIndex]] = [meals[newIndex], meals[currentIndex]];
    
    // Update local state
    setMealPlan({
      ...mealPlan,
      meals: meals
    });
    
    // Save order to backend
    try {
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (session?.access_token) {
        const mealOrder = meals.map(meal => meal.id);
        
        await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/reorder`, {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${session.access_token}`
          },
          body: JSON.stringify({ meal_order: mealOrder })
        });
      }
    } catch (err) {
      console.error('Error saving meal order:', err);
      // Revert local state on error
      setMealPlan({
        ...mealPlan,
        meals: mealPlan.meals
      });
    }
  };

  const swapMealsBetweenDays = async (sourceMealId: string, targetDate: string) => {
    if (!mealPlan) return;
    
    try {
      setLoading(true);
      
      // Get the source meal
      const sourceMeal = mealPlan.meals.find(meal => meal.id === sourceMealId);
      if (!sourceMeal) return;
      
      // For now, we'll just show a message - full implementation would require
      // loading the target day's meal plan and swapping meals
      console.log(`Swapping meal ${sourceMeal.meal_name} to ${targetDate}`);
      
      // TODO: Implement full cross-day swapping
      // This would require:
      // 1. Loading the target day's meal plan
      // 2. Finding a compatible meal to swap
      // 3. Updating both meal plans
      
    } catch (err) {
      console.error('Error swapping meals between days:', err);
      setError('Failed to swap meals between days');
    } finally {
      setLoading(false);
    }
  };

  const handleCustomMealSave = async (customMealData: any) => {
    if (!mealPlan) return;
    
    try {
      setLoading(true);
      
      // Get Supabase session token for authentication
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        setError('Please log in to add custom meals');
        return;
      }
      
      // Save custom meal to backend
      const response = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/custom-meal`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify(customMealData)
      });
      
      if (response.ok) {
        const result = await response.json();
        
        // Create a new meal object from the custom meal data
        const newMeal: Meal = {
          id: result.meal_id,
          meal_name: customMealData.meal_name,
          meal_type: customMealData.meal_type,
          calories: customMealData.nutrition.calories,
          protein: customMealData.nutrition.protein,
          carbs: customMealData.nutrition.carbs,
          fats: customMealData.nutrition.fats,
          prep_time: customMealData.prep_time,
          cook_time: customMealData.cook_time,
          difficulty_level: customMealData.difficulty,
          dietary_tags: customMealData.dietary_tags,
          ingredients: customMealData.ingredients,
          instructions: customMealData.instructions,
          // Add recipe details for the view recipe functionality
          recipe: {
            title: customMealData.meal_name,
            cuisine: customMealData.cuisine,
            prep_time: customMealData.prep_time,
            cook_time: customMealData.cook_time,
            servings: customMealData.servings,
            difficulty: customMealData.difficulty,
            summary: customMealData.summary,
            ingredients: customMealData.ingredients,
            instructions: customMealData.instructions,
            dietary_tags: customMealData.dietary_tags,
            nutrition: customMealData.nutrition
          }
        };
        
        // Add the new meal to the meal plan
        setMealPlan({
          ...mealPlan,
          meals: [...mealPlan.meals, newMeal]
        });
        
        console.log('✅ Custom meal added successfully');
      } else {
        throw new Error('Failed to save custom meal');
      }
    } catch (err) {
      console.error('Error saving custom meal:', err);
      setError('Failed to save custom meal');
    } finally {
      setLoading(false);
    }
  };

  const regenerateIndividualMeal = async (mealId: string) => {
    if (!mealPlan) return;
    
    try {
      setLoading(true);
      
      // Get Supabase session token for authentication
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        setError('Please log in to regenerate meals');
        return;
      }
      
      const response = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/regenerate-meal/${mealId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        
        // Update the meal in local state
        setMealPlan(prev => {
          if (!prev) return null;
          return {
            ...prev,
            meals: prev.meals.map(meal => 
              meal.id === mealId 
                ? {
                    ...meal,
                    meal_name: result.new_meal.meal_name,
                    calories: result.new_meal.calories,
                    protein: result.new_meal.protein,
                    carbs: result.new_meal.carbs,
                    fats: result.new_meal.fats,
                    cuisine: result.new_meal.cuisine,
                    recipe: result.new_meal.recipe_details
                  }
                : meal
            )
          };
        });
        
        console.log('✅ Meal regenerated successfully');
      } else {
        throw new Error('Failed to regenerate meal');
      }
    } catch (err) {
      console.error('Error regenerating meal:', err);
      setError('Failed to regenerate meal');
    } finally {
      setLoading(false);
    }
  };

  const regenerateMealType = async (mealType: string) => {
    if (!mealPlan) return;
    
    try {
      setLoading(true);
      
      // Get Supabase session token for authentication
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        setError('Please log in to regenerate meals');
        return;
      }
      
      const response = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/regenerate-meal-type/${mealType}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        
        // Update all meals of this type in local state
        setMealPlan(prev => {
          if (!prev) return null;
          return {
            ...prev,
            meals: prev.meals.map(meal => {
              if (meal.meal_type === mealType) {
                const regeneratedMeal = result.regenerated_meals.find((rm: any) => rm.id === meal.id);
                if (regeneratedMeal) {
                  return {
                    ...meal,
                    meal_name: regeneratedMeal.meal_name,
                    calories: regeneratedMeal.calories,
                    protein: regeneratedMeal.protein,
                    carbs: regeneratedMeal.carbs,
                    fats: regeneratedMeal.fats,
                    cuisine: regeneratedMeal.cuisine
                  };
                }
              }
              return meal;
            })
          };
        });
        
        console.log(`✅ ${mealType} meals regenerated successfully`);
      } else {
        throw new Error('Failed to regenerate meal type');
      }
    } catch (err) {
      console.error('Error regenerating meal type:', err);
      setError('Failed to regenerate meal type');
    } finally {
      setLoading(false);
    }
  };

  const regenerateEntireMealPlan = async () => {
    if (!mealPlan) return;
    
    try {
      setLoading(true);
      
      // Get Supabase session token for authentication
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        setError('Please log in to regenerate meal plan');
        return;
      }
      
      const response = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/regenerate-entire`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        
        // Update all meals in local state
        setMealPlan(prev => {
          if (!prev) return null;
          return {
            ...prev,
            meals: prev.meals.map(meal => {
              const regeneratedMeal = result.regenerated_meals.find((rm: any) => rm.id === meal.id);
              if (regeneratedMeal) {
                return {
                  ...meal,
                  meal_name: regeneratedMeal.meal_name,
                  calories: regeneratedMeal.calories,
                  protein: regeneratedMeal.protein,
                  carbs: regeneratedMeal.carbs,
                  fats: regeneratedMeal.fats,
                  cuisine: regeneratedMeal.cuisine
                };
              }
              return meal;
            })
          };
        });
        
        console.log('✅ Entire meal plan regenerated successfully');
      } else {
        throw new Error('Failed to regenerate meal plan');
      }
    } catch (err) {
      console.error('Error regenerating meal plan:', err);
      setError('Failed to regenerate meal plan');
    } finally {
      setLoading(false);
    }
  };

  const generateShoppingListFromMealPlan = async () => {
    if (!mealPlan) return;
    
    try {
      setLoading(true);
      
      // Get Supabase session token for authentication
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        setError('Please log in to generate shopping lists');
        return;
      }
      
      const response = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/generate-shopping-list`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('✅ Shopping list generated successfully:', result);
        // You could show a success message or redirect to shopping list view
      } else {
        throw new Error('Failed to generate shopping list');
      }
    } catch (err) {
      console.error('Error generating shopping list:', err);
      setError('Failed to generate shopping list');
    } finally {
      setLoading(false);
    }
  };

  const generateShoppingListFromMeal = async (mealId: string) => {
    try {
      setLoading(true);
      
      // Get Supabase session token for authentication
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        setError('Please log in to generate shopping lists');
        return;
      }
      
      const response = await fetch(`http://localhost:8000/nutrition/meals/${mealId}/generate-shopping-list`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('✅ Shopping list generated successfully:', result);
        // You could show a success message or redirect to shopping list view
      } else {
        throw new Error('Failed to generate shopping list');
      }
    } catch (err) {
      console.error('Error generating shopping list:', err);
      setError('Failed to generate shopping list');
    } finally {
      setLoading(false);
    }
  };

  const generateShoppingListFromMealTypes = async (mealTypes: string[]) => {
    if (!mealPlan) return;
    
    try {
      setLoading(true);
      
      // Get Supabase session token for authentication
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        setError('Please log in to generate shopping lists');
        return;
      }
      
      const response = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/generate-shopping-list-by-types`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify(mealTypes)
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('✅ Shopping list generated successfully:', result);
        // You could show a success message or redirect to shopping list view
      } else {
        throw new Error('Failed to generate shopping list');
      }
    } catch (err) {
      console.error('Error generating shopping list:', err);
      setError('Failed to generate shopping list');
    } finally {
      setLoading(false);
    }
  };

  const adjustMealPortion = async (mealId: string, newServings: number) => {
    try {
      setLoading(true);
      
      // Get Supabase session token for authentication
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        setError('Please log in to adjust portions');
        return;
      }
      
      const response = await fetch(`http://localhost:8000/nutrition/meals/${mealId}/adjust-portions`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify({ new_servings: newServings })
      });
      
      if (response.ok) {
        const result = await response.json();
        
        // Update the meal in local state
        setMealPlan(prev => {
          if (!prev) return null;
          return {
            ...prev,
            meals: prev.meals.map(meal => 
              meal.id === mealId 
                ? {
                    ...meal,
                    calories: result.updated_meal.calories,
                    protein: result.updated_meal.protein,
                    carbs: result.updated_meal.carbs,
                    fats: result.updated_meal.fats,
                    recipe: {
                      ...meal.recipe,
                      servings: result.updated_meal.servings,
                      ingredients: result.adjusted_ingredients,
                      nutrition: result.adjusted_nutrition
                    }
                  }
                : meal
            )
          };
        });
        
        console.log('✅ Meal portion adjusted successfully');
      } else {
        throw new Error('Failed to adjust meal portion');
      }
    } catch (err) {
      console.error('Error adjusting meal portion:', err);
      setError('Failed to adjust meal portion');
    } finally {
      setLoading(false);
    }
  };

  const getPortionSuggestions = async (mealId: string) => {
    try {
      setLoading(true);
      
      // Get Supabase session token for authentication
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        setError('Please log in to get portion suggestions');
        return;
      }
      
      const response = await fetch(`http://localhost:8000/nutrition/meals/${mealId}/portion-suggestions`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('✅ Portion suggestions:', result);
        // You could show these suggestions in a modal or dropdown
        return result;
      } else {
        throw new Error('Failed to get portion suggestions');
      }
    } catch (err) {
      console.error('Error getting portion suggestions:', err);
      setError('Failed to get portion suggestions');
    } finally {
      setLoading(false);
    }
  };

  const handleMealDelete = (mealId: string) => {
    if (mealPlan) {
      const updatedMeals = mealPlan.meals.filter(meal => meal.id !== mealId);
      setMealPlan({
        ...mealPlan,
        meals: updatedMeals
      });
    }
  };

  const handleSwapMeal = async (mealType: string) => {
    setLoading(true);
    try {
      // Get Supabase session token for authentication
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        setError('Please log in to swap meals');
        return;
      }

      // Generate a new meal plan to get a different meal for this type
      const response = await fetch('http://localhost:8000/nutrition/meal-plans/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify({
          plan_type: planType,
          start_date: selectedDate,
          end_date: planType === 'weekly' ? new Date(new Date(selectedDate).getTime() + 6 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] : selectedDate,
          generation_strategy: 'balanced',
          preferences_override: {
            daily_calorie_target: preferences.calorieTarget,
            meals_per_day: preferences.mealsPerDay,
            dietary_preferences: preferences.dietaryRestrictions,
            allergies: preferences.allergies,
            cuisine_preferences: preferences.cuisinePreferences
          }
        })
      });

      if (response.ok) {
        const newMealPlan = await response.json();
        // Find the new meal of the same type
        const newMeal = newMealPlan.meals.find((meal: any) => meal.meal_type === mealType);
        if (newMeal && mealPlan) {
          // Replace the old meal with the new one
          const updatedMeals = mealPlan.meals.map(meal => 
            meal.meal_type === mealType ? newMeal : meal
          );
          setMealPlan({
            ...mealPlan,
            meals: updatedMeals
          });
        }
      } else {
        throw new Error('Failed to generate new meal');
      }
    } catch (err) {
      console.error('Error swapping meal:', err);
      setError('Failed to swap meal');
    } finally {
      setLoading(false);
    }
  };

  const handleLogToDailyIntake = async () => {
    if (!mealPlan) return;
    
    try {
      setLoading(true);
      
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        alert('Please log in');
        return;
      }
      
      const today = new Date().toISOString().split('T')[0];
      
      const response = await fetch(
        `http://localhost:8000/daily-logging/log-from-meal-plan?log_date=${today}&meal_plan_id=${mealPlan.id}`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (response.ok) {
        const result = await response.json();
        alert(`Successfully logged ${result.logged_meals} meals to daily intake!`);
      } else {
        throw new Error('Failed to log meal plan');
      }
    } catch (error) {
      console.error('Error logging meal plan:', error);
      alert('Error logging meal plan to daily intake');
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'green';
      case 'medium': return 'yellow';
      case 'hard': return 'red';
      default: return 'gray';
    }
  };

  if (loading && !mealPlan) {
    return (
      <Center h="400px">
        <VStack spacing={4}>
          <Spinner size="xl" />
          <Text>{t('nutrition.loading', 'en')}</Text>
        </VStack>
      </Center>
    );
  }

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <Box>
          <HStack justify="space-between" mb={4}>
            <VStack align="start" spacing={1}>
              <Heading size="lg">{t('nutrition.mealPlanning.title', 'en')}</Heading>
              <Text color="gray.600">{t('nutrition.mealPlanning.subtitle', 'en')}</Text>
            </VStack>
            <HStack spacing={2}>
              <Button 
                colorScheme="blue" 
                leftIcon={<FiRefreshCw />}
                onClick={generateMealPlan}
                isLoading={loading}
              >
                {t('nutrition.generateMealPlan', 'en')}
              </Button>
              {mealPlan && (
                <Button 
                  variant="outline" 
                  leftIcon={<FiGitBranch />}
                  onClick={() => setShowVersionHistory(!showVersionHistory)}
                >
                  Version History
                </Button>
              )}
            </HStack>
            <Button 
              colorScheme="green" 
              leftIcon={<FiRotateCcw />}
              onClick={regenerateEntireMealPlan}
              isLoading={loading}
              isDisabled={!mealPlan}
            >
              Regenerate All Meals
            </Button>
            <Button 
              colorScheme="purple" 
              leftIcon={<FiShoppingCart />}
              onClick={generateShoppingListFromMealPlan}
              isLoading={loading}
              isDisabled={!mealPlan}
            >
              Generate Shopping List
            </Button>
          </HStack>

          {/* Version History */}
          {showVersionHistory && mealPlan && (
            <Box mb={6}>
              <MealPlanVersionHistory 
                mealPlanId={mealPlan.id}
                onVersionRestored={(newPlanId) => {
                  // Refresh the meal plan with the new ID
                  setMealPlan({...mealPlan, id: newPlanId});
                  setShowVersionHistory(false);
                }}
              />
            </Box>
          )}

          {/* Meal Type Regeneration Controls */}
          {mealPlan && (
            <HStack spacing={2} mb={4} wrap="wrap">
              <Text fontSize="sm" color="gray.600" mr={2}>Regenerate by type:</Text>
              {['breakfast', 'lunch', 'dinner', 'snack'].map(mealType => (
                <Button
                  key={mealType}
                  size="sm"
                  variant="outline"
                  leftIcon={<FiRotateCcw />}
                  onClick={() => regenerateMealType(mealType)}
                  isLoading={loading}
                  isDisabled={!mealPlan.meals.some(meal => meal.meal_type === mealType || meal.type === mealType)}
                >
                  {mealType.charAt(0).toUpperCase() + mealType.slice(1)}
                </Button>
              ))}
            </HStack>
          )}

          {/* Shopping List Generation Controls */}
          {mealPlan && (
            <HStack spacing={2} mb={4} wrap="wrap">
              <Text fontSize="sm" color="gray.600" mr={2}>Shopping lists by type:</Text>
              {['breakfast', 'lunch', 'dinner', 'snack'].map(mealType => (
                <Button
                  key={`shopping-${mealType}`}
                  size="sm"
                  variant="outline"
                  colorScheme="purple"
                  leftIcon={<FiShoppingCart />}
                  onClick={() => generateShoppingListFromMealTypes([mealType])}
                  isLoading={loading}
                  isDisabled={!mealPlan.meals.some(meal => meal.meal_type === mealType || meal.type === mealType)}
                >
                  {mealType.charAt(0).toUpperCase() + mealType.slice(1)} List
                </Button>
              ))}
            </HStack>
          )}

          {/* Date Selector */}
          <HStack spacing={4}>
            <FormControl>
              <FormLabel>Plan Type</FormLabel>
              <Select
                value={planType}
                onChange={(e) => setPlanType(e.target.value as 'daily' | 'weekly')}
                maxW="150px"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
              </Select>
            </FormControl>
            <FormControl>
              <FormLabel>{t('nutrition.selectDate', 'en')}</FormLabel>
              <Input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                maxW="200px"
              />
            </FormControl>
          </HStack>
        </Box>

        {error && (
          <Alert status="error">
            <AlertIcon />
            {error}
          </Alert>
        )}

        {/* Meal Plan Summary */}
        {mealPlan && (
          <Card bg={cardBg} borderColor={borderColor}>
            <CardHeader>
              <HStack justify="space-between">
                <Heading size="md">{t('nutrition.mealPlanSummary', 'en')}</Heading>
                <HStack spacing={4}>
                  <Text fontSize="sm" color="gray.600">
                    {mealPlan.total_nutrition?.calories || 0} {t('nutrition.calories', 'en')}
                  </Text>
                  <Text fontSize="sm" color="gray.600">
                    {mealPlan.total_nutrition?.protein || 0}g {t('nutrition.protein', 'en')}
                  </Text>
                  <Text fontSize="sm" color="gray.600">
                    {mealPlan.total_nutrition?.carbs || 0}g {t('nutrition.carbs', 'en')}
                  </Text>
                  <Text fontSize="sm" color="gray.600">
                    {mealPlan.total_nutrition?.fats || 0}g {t('nutrition.fats', 'en')}
                  </Text>
                </HStack>
              </HStack>
            </CardHeader>
            <CardBody pt={0}>
              <HStack justify="space-between">
                <Text fontSize="sm" color="gray.600">
                  Log this meal plan to your daily intake
                </Text>
                <Button
                  leftIcon={<FiLogIn />}
                  colorScheme="green"
                  size="sm"
                  onClick={handleLogToDailyIntake}
                  isLoading={loading}
                >
                  Log to Daily Intake
                </Button>
              </HStack>
            </CardBody>
          </Card>
        )}

        {/* Meals */}
        {mealPlan && (
          <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }} gap={4}>
            {(mealPlan.meals || []).map((meal, index) => (
              <Card key={meal.id} bg={cardBg} borderColor={borderColor} position="relative">
                <CardHeader>
                  <HStack justify="space-between">
                    <VStack align="start" spacing={1}>
                      <HStack spacing={2}>
                        <Badge colorScheme="gray" size="sm">#{index + 1}</Badge>
                        <Heading size="sm">{meal.meal_name || meal.name || 'Untitled Meal'}</Heading>
                      </HStack>
                      <Badge colorScheme="blue" size="sm">
                        {(meal.meal_type || meal.type || 'meal').replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </Badge>
                    </VStack>
                    <Menu>
                      <MenuButton as={IconButton} icon={<FiMoreVertical />} size="sm" variant="ghost" />
                      <MenuList>
                        <MenuItem icon={<FiRefreshCw />} onClick={() => loadAlternatives(meal.meal_type)}>
                          Show Alternatives
                        </MenuItem>
                        <MenuItem icon={<FiRotateCcw />} onClick={() => regenerateIndividualMeal(meal.id)}>
                          Regenerate This Meal
                        </MenuItem>
                        <MenuItem icon={<FiShoppingCart />} onClick={() => generateShoppingListFromMeal(meal.id)}>
                          Generate Shopping List
                        </MenuItem>
                        <MenuItem icon={<FiUsers />} onClick={() => getPortionSuggestions(meal.id)}>
                          Portion Suggestions
                        </MenuItem>
                        <MenuItem icon={<FiArrowUp />} onClick={() => reorderMeal(meal.id, 'up')}>
                          Move Up
                        </MenuItem>
                        <MenuItem icon={<FiArrowDown />} onClick={() => reorderMeal(meal.id, 'down')}>
                          Move Down
                        </MenuItem>
                        <MenuItem icon={<FiEdit />} onClick={() => handleMealEdit(meal)}>
                          {t('nutrition.editMeal', 'en')}
                        </MenuItem>
                        <MenuItem icon={<FiTrash2 />} onClick={() => handleMealDelete(meal.id)} color="red.500">
                          {t('nutrition.deleteMeal', 'en')}
                        </MenuItem>
                      </MenuList>
                    </Menu>
                  </HStack>
                </CardHeader>
                <CardBody>
                  <VStack spacing={3} align="stretch">
                    {/* Nutritional Info */}
                    <VStack spacing={1} align="stretch">
                      <Text fontSize="xs" color="gray.500">Per Serving</Text>
                      <HStack justify="space-between" fontSize="sm">
                        <Text fontWeight="bold">{meal.calories || 0} {t('nutrition.calories', 'en')}</Text>
                        <Text fontWeight="bold">{meal.protein || 0}g {t('nutrition.protein', 'en')}</Text>
                      </HStack>
                      <HStack justify="space-between" fontSize="sm">
                        <Text>{meal.carbs || 0}g {t('nutrition.carbs', 'en')}</Text>
                        <Text>{meal.fats || 0}g {t('nutrition.fats', 'en')}</Text>
                      </HStack>
                    </VStack>

                    <Divider />

                    {/* Meal Details */}
                    <HStack justify="space-between" fontSize="sm">
                      <HStack>
                        <FiClock />
                        <Text>{meal.prep_time || meal.prepTime || 0} min</Text>
                      </HStack>
                      <Badge colorScheme={getDifficultyColor(meal.difficulty_level || meal.difficulty || 'easy')} size="sm">
                        {meal.difficulty_level || meal.difficulty || 'easy'}
                      </Badge>
                    </HStack>

                    {/* Dietary Tags */}
                    <HStack wrap="wrap" spacing={1}>
                      {(meal.dietary_tags || meal.dietaryTags || []).map((tag) => (
                        <Badge key={tag} size="sm" colorScheme="green" variant="subtle">
                          {tag}
                        </Badge>
                      ))}
                    </HStack>

                    {/* Actions */}
                    <HStack spacing={2}>
                      <Button 
                        size="sm" 
                        colorScheme="blue" 
                        flex={1}
                        onClick={() => handleViewRecipe(meal)}
                      >
                        {t('nutrition.viewRecipe', 'en')}
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline" 
                        flex={1}
                        onClick={() => handleSwapMeal(meal.meal_type)}
                        isLoading={loading}
                      >
                        {t('nutrition.swapMeal', 'en')}
                      </Button>
                    </HStack>
                  </VStack>
                </CardBody>
              </Card>
            ))}
          </Grid>
        )}

        {/* Alternatives Display */}
        {Object.keys(alternatives).length > 0 && (
          <Box mt={6}>
            <Heading size="md" mb={4}>Alternative Options</Heading>
            {Object.entries(alternatives).map(([mealType, altList]) => (
              <Box key={mealType} mb={6}>
                <Text fontWeight="semibold" mb={3} textTransform="capitalize">
                  {mealType} Alternatives
                </Text>
                <Grid templateColumns="repeat(auto-fit, minmax(300px, 1fr))" gap={4}>
                  {altList.map((alternative, index) => (
                    <Card key={index} bg={cardBg} borderColor={borderColor}>
                      <CardHeader>
                        <HStack justify="space-between">
                          <VStack align="start" spacing={1}>
                            <Heading size="sm">{alternative.meal_name}</Heading>
                            <Badge colorScheme="green" size="sm">{alternative.recipe?.cuisine}</Badge>
                          </VStack>
                        </HStack>
                      </CardHeader>
                      <CardBody>
                        <VStack spacing={3} align="stretch">
                          <HStack justify="space-between" fontSize="sm">
                            <Text>{alternative.recipe?.nutrition?.calories || 0} calories</Text>
                            <Text>{alternative.recipe?.nutrition?.protein || 0}g protein</Text>
                          </HStack>
                          <Text fontSize="sm" color="gray.600">
                            {alternative.recipe?.summary || 'A delicious alternative option'}
                          </Text>
                          <HStack spacing={2}>
                            <Button
                              size="sm"
                              colorScheme="blue"
                              onClick={() => selectAlternative(mealType, alternative)}
                            >
                              Select This Option
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => handleViewRecipe(alternative)}
                            >
                              View Recipe
                            </Button>
                          </HStack>
                        </VStack>
                      </CardBody>
                    </Card>
                  ))}
                </Grid>
              </Box>
            ))}
          </Box>
        )}

        {/* Add Meal Button */}
        <Card bg={cardBg} borderColor={borderColor} borderStyle="dashed">
          <CardBody>
            <Center h="200px">
              <VStack spacing={4}>
                <FiPlus size={48} color="gray" />
                <Text color="gray.600">{t('nutrition.addMeal', 'en')}</Text>
                <Button colorScheme="blue" leftIcon={<FiCoffee />} onClick={onCustomMealOpen}>
                  {t('nutrition.addMeal', 'en')}
                </Button>
              </VStack>
            </Center>
          </CardBody>
        </Card>

        {/* Meal Edit Modal */}
        <Modal isOpen={isOpen} onClose={onClose} size="lg">
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>{t('nutrition.editMeal', 'en')}</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              {selectedMeal && (
                <VStack spacing={4} align="stretch">
                  <FormControl>
                    <FormLabel>{t('nutrition.mealName', 'en')}</FormLabel>
                    <Input value={selectedMeal.name} />
                  </FormControl>
                  <FormControl>
                    <FormLabel>{t('nutrition.mealType', 'en')}</FormLabel>
                    <Select value={selectedMeal.type}>
                      <option value="breakfast">{t('nutrition.breakfast', 'en')}</option>
                      <option value="lunch">{t('nutrition.lunch', 'en')}</option>
                      <option value="dinner">{t('nutrition.dinner', 'en')}</option>
                      <option value="snack">{t('nutrition.snack', 'en')}</option>
                    </Select>
                  </FormControl>
                  <FormControl>
                    <FormLabel>{t('nutrition.ingredients', 'en')}</FormLabel>
                    <Textarea value={selectedMeal.ingredients.join(', ')} />
                  </FormControl>
                  <FormControl>
                    <FormLabel>{t('nutrition.instructions', 'en')}</FormLabel>
                    <Textarea value={selectedMeal.instructions.join('\n')} rows={4} />
                  </FormControl>
                </VStack>
              )}
            </ModalBody>
            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onClose}>
                {t('cancel', 'en')}
              </Button>
              <Button colorScheme="blue">
                {t('save', 'en')}
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>

        {/* Recipe View Modal */}
        <Modal isOpen={isRecipeOpen} onClose={onRecipeClose} size="lg">
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>
              {selectedRecipe?.meal_name || selectedRecipe?.name || 'Recipe Details'}
            </ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              {selectedRecipe && (
                <VStack spacing={6} align="stretch">
                  {/* Nutritional Information */}
                  <Box>
                    <Heading size="md" mb={3}>Nutritional Information</Heading>
                    <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                      <Box p={3} bg="blue.50" borderRadius="md">
                        <Text fontSize="sm" color="gray.600">Calories</Text>
                        <Text fontSize="lg" fontWeight="bold">{selectedRecipe.calories}</Text>
                      </Box>
                      <Box p={3} bg="green.50" borderRadius="md">
                        <Text fontSize="sm" color="gray.600">Protein</Text>
                        <Text fontSize="lg" fontWeight="bold">{selectedRecipe.protein}g</Text>
                      </Box>
                      <Box p={3} bg="orange.50" borderRadius="md">
                        <Text fontSize="sm" color="gray.600">Carbs</Text>
                        <Text fontSize="lg" fontWeight="bold">{selectedRecipe.carbs}g</Text>
                      </Box>
                      <Box p={3} bg="purple.50" borderRadius="md">
                        <Text fontSize="sm" color="gray.600">Fats</Text>
                        <Text fontSize="lg" fontWeight="bold">{selectedRecipe.fats}g</Text>
                      </Box>
                    </Grid>
                  </Box>

                  {/* Preparation Info */}
                  <Box>
                    <Heading size="md" mb={3}>Preparation</Heading>
                    <HStack spacing={4}>
                      <Box>
                        <Text fontSize="sm" color="gray.600">Prep Time</Text>
                        <Text fontWeight="bold">{selectedRecipe.prepTime || selectedRecipe.prep_time || 0} min</Text>
                      </Box>
                      {selectedRecipe.cook_time && (
                        <Box>
                          <Text fontSize="sm" color="gray.600">Cook Time</Text>
                          <Text fontWeight="bold">{selectedRecipe.cook_time} min</Text>
                        </Box>
                      )}
                      <Box>
                        <Text fontSize="sm" color="gray.600">Difficulty</Text>
                        <Badge colorScheme={
                          (selectedRecipe.difficulty || selectedRecipe.difficulty_level) === 'easy' ? 'green' :
                          (selectedRecipe.difficulty || selectedRecipe.difficulty_level) === 'medium' ? 'yellow' : 'red'
                        }>
                          {(selectedRecipe.difficulty || selectedRecipe.difficulty_level || 'easy').toUpperCase()}
                        </Badge>
                      </Box>
                    </HStack>
                  </Box>

                  {/* Ingredients */}
                  {selectedRecipe.ingredients && selectedRecipe.ingredients.length > 0 && (
                    <Box>
                      <Heading size="md" mb={3}>Ingredients</Heading>
                      <VStack align="stretch" spacing={2}>
                        {selectedRecipe.ingredients.map((ingredient, index) => (
                          <Text key={index} pl={4} borderLeft="3px solid" borderColor="blue.200">
                            {typeof ingredient === 'string' 
                              ? ingredient 
                              : `${ingredient.name} - ${ingredient.quantity}${ingredient.unit}`
                            }
                          </Text>
                        ))}
                      </VStack>
                    </Box>
                  )}

                  {/* Instructions */}
                  {selectedRecipe.instructions && selectedRecipe.instructions.length > 0 && (
                    <Box>
                      <Heading size="md" mb={3}>Instructions</Heading>
                      <VStack align="stretch" spacing={3}>
                        {selectedRecipe.instructions.map((instruction, index) => (
                          <Box key={index} p={3} bg="gray.50" borderRadius="md">
                            <Text fontWeight="bold" color="blue.600" mb={1}>
                              Step {typeof instruction === 'string' ? index + 1 : instruction.step}
                            </Text>
                            <Text>
                              {typeof instruction === 'string' ? instruction : instruction.description}
                            </Text>
                          </Box>
                        ))}
                      </VStack>
                    </Box>
                  )}

                  {/* Dietary Tags */}
                  {(selectedRecipe.dietaryTags || selectedRecipe.dietary_tags) && 
                   (selectedRecipe.dietaryTags || selectedRecipe.dietary_tags).length > 0 && (
                    <Box>
                      <Heading size="md" mb={3}>Dietary Information</Heading>
                      <HStack spacing={2} flexWrap="wrap">
                        {(selectedRecipe.dietaryTags || selectedRecipe.dietary_tags).map((tag, index) => (
                          <Badge key={index} colorScheme="blue" variant="subtle">
                            {tag}
                          </Badge>
                        ))}
                      </HStack>
                    </Box>
                  )}

                  {/* Fallback message if no detailed recipe info */}
                  {(!selectedRecipe.ingredients || selectedRecipe.ingredients.length === 0) && 
                   (!selectedRecipe.instructions || selectedRecipe.instructions.length === 0) && (
                    <Box textAlign="center" py={8}>
                      <Text color="gray.500" mb={4}>
                        Detailed recipe information is not available for this meal.
                      </Text>
                      <Text fontSize="sm" color="gray.400">
                        This is a simple meal plan entry. For detailed recipes, try generating a new meal plan.
                      </Text>
                    </Box>
                  )}
                </VStack>
              )}
            </ModalBody>
            <ModalFooter>
              <Button colorScheme="blue" onClick={onRecipeClose}>
                Close
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>

        {/* Custom Meal Modal */}
        <CustomMealModal
          isOpen={isCustomMealOpen}
          onClose={onCustomMealClose}
          onSave={handleCustomMealSave}
        />

        {/* Version Comparison */}
        {versionComparison.version1Id && versionComparison.version2Id && (
          <MealPlanVersionComparison
            mealPlanId={mealPlan?.id || ''}
            version1Id={versionComparison.version1Id}
            version2Id={versionComparison.version2Id}
          />
        )}
      </VStack>
    </Box>
  );
};

export default MealPlanning;
