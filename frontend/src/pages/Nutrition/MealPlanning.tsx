import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import {
  Box,
  Grid,
  SimpleGrid,
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
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
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
  AlertTitle,
  AlertDescription,
  Spinner,
  Center,
  Menu,
  MenuButton,
  MenuList,
  MenuItem
} from '@chakra-ui/react';
import { useToast } from '@chakra-ui/react';
import { t } from '../../utils/translations';
import CustomMealModal from '../../components/nutrition/CustomMealModal';
import MealPlanVersionHistory from '../../components/nutrition/MealPlanVersionHistory';
import MealPlanVersionComparison from '../../components/nutrition/MealPlanVersionComparison';
import AddToMealPlanModal from '../../components/nutrition/AddToMealPlanModal';
import { 
  FiPlus, 
  FiRefreshCw,
  FiCoffee,
  FiRotateCcw,
  FiShoppingCart,
  FiGitBranch,
  FiTrash2,
  FiPieChart
} from 'react-icons/fi';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';

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
  recipe?: {
    title?: string;
    cuisine?: string;
    summary?: string;
    ingredients?: Array<{name: string, quantity: number, unit: string}>;
    instructions?: Array<{step: number, description: string}>;
    dietary_tags?: string[];
    difficulty?: string;
    prep_time?: number;
    cook_time?: number;
    servings?: number;
    nutrition?: {
      calories: number;
      protein: number;
      carbs: number;
      fats: number;
    };
    ai_generated?: boolean;
    database_fallback?: boolean;
  };
  cuisine?: string;
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

const MealPlanning: React.FC<MealPlanningProps> = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [streamingProgress, setStreamingProgress] = useState<string | null>(null);
  const [generatingMeals, setGeneratingMeals] = useState<Set<string>>(new Set());
  const [isGenerating, setIsGenerating] = useState(false); // CRITICAL: Track if meal plan generation is in progress
  const justGeneratedRef = useRef<number | null>(null); // CRITICAL: Track when meal plan was just generated (timestamp)
  const localStorageRestoredRef = useRef<boolean>(false); // CRITICAL: Track if we've already restored from localStorage in this session
  const loadMealPlanTimeoutRef = useRef<NodeJS.Timeout | null>(null); // CRITICAL: Track debounce timeout
  const [mealPlan, setMealPlan] = useState<MealPlan | null>(null);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [planType, setPlanType] = useState<'daily' | 'weekly'>(() => {
    try {
      const saved = typeof window !== 'undefined' ? (localStorage.getItem('mealPlanView') as 'daily' | 'weekly' | null) : null;
      return saved || 'weekly';
    } catch {
      return 'weekly';
    }
  });
  const [selectedDay, setSelectedDay] = useState<string | null>(null);
  const [mealsPerDay, setMealsPerDay] = useState<number>(() => {
    // CRITICAL FIX: Load mealsPerDay from localStorage on mount to persist user's choice
    // Cap at 5 (max supported by grid)
    try {
      const saved = typeof window !== 'undefined' ? localStorage.getItem('mealsPerDay') : null;
      const value = saved ? parseInt(saved, 10) : 4;
      return value > 5 ? 5 : value; // Cap at 5
    } catch {
      return 4;
    }
  });
  
  // CRITICAL FIX: Persist mealsPerDay to localStorage whenever it changes
  // Also cap at 5 to ensure consistency
  useEffect(() => {
    try {
      // Cap at 5 (max supported by grid)
      if (mealsPerDay > 5) {
        setMealsPerDay(5);
        localStorage.setItem('mealsPerDay', '5');
      } else {
      localStorage.setItem('mealsPerDay', mealsPerDay.toString());
      }
    } catch (e) {
      console.warn('Failed to save mealsPerDay to localStorage:', e);
    }
  }, [mealsPerDay]);
  const [preferences, setPreferences] = useState({
    dietaryRestrictions: [] as string[],
    allergies: [] as string[],
    dislikedIngredients: [] as string[],
    cuisinePreferences: [] as string[],
    calorieTarget: 2000,
    mealsPerDay: 3
  });

  const { isOpen, onOpen, onClose } = useDisclosure();
  const [selectedMeal, setSelectedMeal] = useState<Meal | null>(null);
  const [selectedRecipe, setSelectedRecipe] = useState<Meal | null>(null);
  const { isOpen: isRecipeOpen, onOpen: onRecipeOpen, onClose: onRecipeClose } = useDisclosure();
  const [alternatives, setAlternatives] = useState<{[key: string]: any[]}>({});
  const { isOpen: isAltOpen, onOpen: onAltOpen, onClose: _onAltClose } = useDisclosure();
  const [altMealType, setAltMealType] = useState<string | null>(null);
  const [altSearch, setAltSearch] = useState<string>('');
  const [altSearchDebounced, setAltSearchDebounced] = useState<string>('');
  const alternativesCacheRef = useRef<{[key:string]: { items: any[]; ts: number }} >({});
  const controllersRef = useRef<{[key:string]: AbortController | null}>({});
  const ALT_TTL_MS = 15 * 60 * 1000;
  
  // Versioning state
  const [showVersionHistory, setShowVersionHistory] = useState(false);
  const [versionComparison] = useState<{version1Id?: string, version2Id?: string}>({});
  const [loadingAlternatives, setLoadingAlternatives] = useState<{[key: string]: boolean}>({});
  const { isOpen: isCustomMealOpen, onOpen: onCustomMealOpen, onClose: onCustomMealClose } = useDisclosure();
  const [editingMealId, setEditingMealId] = useState<string | null>(null);
  const [editingMealData, setEditingMealData] = useState<any>(null);
  
  // Recipe selector for adding recipes to grid
  const [recipeSelectorOpen, setRecipeSelectorOpen] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState<{date: string, mealType: string} | null>(null);
  const [availableRecipes, setAvailableRecipes] = useState<any[]>([]);
  const [recipeSearch, setRecipeSearch] = useState('');
  
  // Add to meal plan modal state
  const [addToMealPlanRecipe, setAddToMealPlanRecipe] = useState<any | null>(null);
  const { isOpen: isAddToMealPlanOpen, onOpen: onAddToMealPlanOpen, onClose: onAddToMealPlanClose } = useDisclosure();
  
  // Preview servings for recipe view modal
  const [previewServings, setPreviewServings] = useState<number>(1);
  
  // Ingredient graphs modal state
  const { isOpen: isIngredientGraphsOpen, onOpen: onIngredientGraphsOpen, onClose: onIngredientGraphsClose } = useDisclosure();

  // Ingredient substitution state
  const [substitutionIngredient, setSubstitutionIngredient] = useState<string | null>(null);
  const [substitutionSuggestions, setSubstitutionSuggestions] = useState<any[]>([]);
  const [loadingSubstitutions, setLoadingSubstitutions] = useState(false);
  const { isOpen: isSubstitutionOpen, onOpen: onSubstitutionOpen, onClose: onSubstitutionClose } = useDisclosure();

  // Simple swap state - first click selects meal, second click swaps
  const [swapMode, setSwapMode] = useState(false);
  const [swapSourceMeal, setSwapSourceMeal] = useState<{id: string, date: string, mealType: string, isUserRecipe?: boolean} | null>(null);

  // Track recently added meals to display in box below grid
  // Load from localStorage on mount to persist across page switches, week changes, and grid resets
  // This is a persistent list of user-created meals that should not disappear
  const [recentlyAddedMeals, setRecentlyAddedMeals] = useState<Meal[]>(() => {
    try {
      if (typeof window !== 'undefined') {
        const saved = localStorage.getItem('recentlyAddedMeals');
        if (saved) {
          const parsed = JSON.parse(saved);
          return Array.isArray(parsed) ? parsed : [];
        }
      }
    } catch (e) {
      console.warn('Failed to load recently added meals from localStorage:', e);
    }
    return [];
  });
  
  // CRITICAL FIX: Persist recentlyAddedMeals to localStorage whenever it changes
  useEffect(() => {
    try {
      if (typeof window !== 'undefined') {
        localStorage.setItem('recentlyAddedMeals', JSON.stringify(recentlyAddedMeals));
      }
    } catch (e) {
      console.warn('Failed to save recently added meals to localStorage:', e);
    }
  }, [recentlyAddedMeals]);

  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const toast = useToast();

  // Cancel swap mode on ESC key or outside click
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && swapMode) {
        setSwapMode(false);
        setSwapSourceMeal(null);
        toast({
          title: 'Swap cancelled',
          description: 'Press Swap button again to start swapping',
          status: 'info',
          duration: 2000,
          isClosable: true
        });
      }
    };
    
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [swapMode, toast]);

  const weekDates = useMemo(() => {
    if (planType !== 'weekly') return [] as string[];
    const start = new Date(selectedDate);
    // Start from Monday (0 = Sunday, 1 = Monday)
    const dayOfWeek = start.getDay();
    const mondayOffset = dayOfWeek === 0 ? -6 : 1 - dayOfWeek; // If Sunday, go back 6 days to Monday
    start.setDate(start.getDate() + mondayOffset);
    
    const dates: string[] = [];
    for (let i = 0; i < 7; i++) {
      const d = new Date(start);
      d.setDate(start.getDate() + i);
      dates.push(d.toISOString().split('T')[0]);
    }
    return dates;
  }, [selectedDate, planType]);

  // Recipe selector functions
  const openRecipeSelector = async (date: string, mealType: string) => {
    setSelectedSlot({ date, mealType });
    setRecipeSearch('');
    setAvailableRecipes([]);
    setRecipeSelectorOpen(true);
    
    // Load available recipes
    try {
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        toast({ title: 'Please log in', status: 'warning', duration: 2500, isClosable: true });
        return;
      }

      const response = await fetch('http://localhost:8000/nutrition/recipes/search', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: '',
          meal_type: mealType,
          limit: 50,
          page: 1,
        })
      });

      if (response.ok) {
        const data = await response.json();
        setAvailableRecipes(data.recipes || []);
      }
    } catch (err) {
      console.error('Error loading recipes:', err);
      toast({ title: 'Failed to load recipes', status: 'error', duration: 3000, isClosable: true });
    }
  };

  const generateMealSlot = async (date: string, mealType: string) => {
    if (!mealPlan) {
      toast({ 
        title: 'No meal plan structure', 
        description: 'Please create a meal plan structure first', 
        status: 'warning', 
        duration: 3000, 
        isClosable: true 
      });
      return;
    }
    
    // CRITICAL FIX: Prevent multiple simultaneous generations
    const slotKey = `${date}-${mealType}`;
    if (generatingMeals.has(slotKey) || isGenerating) {
      toast({
        title: 'Generation in progress',
        description: 'Please wait for the current generation to complete.',
        status: 'info',
        duration: 2000,
        isClosable: true,
      });
      return;
    }
    
    // CRITICAL FIX: Normalize meal type for backend (morning snack -> snack)
    const normalizedMealType = mealType === 'morning snack' || mealType === 'afternoon snack' || mealType === 'evening snack' 
      ? 'snack' 
      : mealType.toLowerCase();
    
    try {
      setGeneratingMeals(prev => new Set(prev).add(slotKey));
      setLoading(true); // CRITICAL: Set global loading state
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        toast({ title: 'Please log in', status: 'warning', duration: 2500, isClosable: true });
        return;
      }

      // ROOT CAUSE FIX: Send ORIGINAL mealType (morning snack/afternoon snack) to backend
      // The backend will normalize it internally but preserve the original in recipe_details.meal_type
      // This allows the frontend to correctly assign snacks to specific slots
      const response = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/generate-meal-slot`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          meal_date: date,
          meal_type: mealType.toLowerCase(),  // ROOT CAUSE FIX: Send original mealType (morning snack/afternoon snack), not normalized
        }),
      });

      if (response.ok) {
        const result = await response.json();
        const dayName = new Date(date).toLocaleDateString(undefined, {weekday: 'long'});
        
        // ROOT CAUSE FIX: Check what meal_type the backend actually preserved in recipe_details
        const backendPreservedType = result.meal?.recipe?.meal_type || result.meal?.recipe_details?.meal_type;
        console.log(`🔍 Backend preserved meal_type: ${backendPreservedType}, Frontend mealType: ${mealType}`);
        
        // ROOT CAUSE FIX: Use backend's preserved meal_type if available, otherwise use frontend mealType
        // This ensures we use the exact meal_type that the backend stored (e.g., 'afternoon snack')
        const preservedMealType = backendPreservedType || mealType;
        console.log(`✅ Using preserved meal_type: ${preservedMealType}`);
        
        // CRITICAL FIX: Immediately update state for the specific slot to show the meal instantly
        // Immediately update the meal plan with the new meal, preserving the original mealType for frontend
        const updatedMeal = {
          ...result.meal,
          meal_date: date,
          meal_type: preservedMealType, // ROOT CAUSE FIX: Use preserved meal_type from backend
          date: date,
          type: preservedMealType, // ROOT CAUSE FIX: Use preserved meal_type from backend
          // Store preserved meal_type in recipe and recipe_details for correct slot assignment
          recipe: {
            ...(result.meal.recipe || {}),
            meal_type: preservedMealType // ROOT CAUSE FIX: Use preserved meal_type from backend
          },
          recipe_details: {
            ...(result.meal.recipe || result.meal.recipe_details || {}),
            meal_type: preservedMealType // ROOT CAUSE FIX: Use preserved meal_type from backend
          }
        };
        
        setMealPlan(prev => {
          if (!prev) return null;
          // Check if meal already exists for this exact slot (update) or add new
          // CRITICAL FIX: Match by exact slot (date + specific meal type), not just any snack
          const existingIndex = prev.meals.findIndex(
            (m: any) => {
              const mDate = m.meal_date || m.date;
              const mType = m.meal_type || m.type;
              // First check date - must match exactly
              if (mDate !== date) return false;
              
              // CRITICAL: For snack variants, check the preserved meal_type in recipe_details
              // This ensures we only match the specific snack slot (morning/afternoon/evening)
              if (mealType === 'morning snack' || mealType === 'afternoon snack' || mealType === 'evening snack') {
                // Check preserved meal_type from previous updates
                const preservedType = m.recipe?.meal_type || m.recipe_details?.meal_type || mType;
                // Only match if preserved type matches the exact slot we're updating
                return preservedType === mealType;
              }
              
              // For non-snacks, exact match
              return mType === mealType;
            }
          );
          
          if (existingIndex !== -1) {
            // Update existing meal
            const updated = [...prev.meals];
            updated[existingIndex] = updatedMeal;
            return { ...prev, meals: updated };
          } else {
            // Add new meal
            return { ...prev, meals: [...prev.meals, updatedMeal] };
          }
        });
        
        // Remove from generating set immediately
        setGeneratingMeals(prev => {
          const next = new Set(prev);
          next.delete(slotKey);
          return next;
        });
        setLoading(false); // CRITICAL: Clear global loading state when done
        
        toast({ 
          title: 'Meal Generated!', 
          description: `${result.meal.meal_name} added to ${dayName} ${mealType}`, 
          status: 'success', 
          duration: 2000, 
          isClosable: true 
        });
        setRecipeSelectorOpen(false);
        setSelectedSlot(null);
        
        // CRITICAL FIX: Notify dashboard to reload
        window.dispatchEvent(new CustomEvent('mealPlanUpdated', { detail: { date } }));
        
        // Reload from backend after a short delay to ensure consistency (but UI is already updated)
        setTimeout(() => loadMealPlan(), 1000); // Give state update time to render
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate meal');
      }
    } catch (err: any) {
      console.error('Error generating meal:', err);
      toast({ 
        title: 'Failed to generate meal', 
        description: err.message || 'Please try again', 
        status: 'error', 
        duration: 3000, 
        isClosable: true 
      });
    } finally {
      setGeneratingMeals(prev => {
        const next = new Set(prev);
        next.delete(slotKey);
        return next;
      });
      setLoading(false); // CRITICAL: Clear global loading state in finally block
    }
  };

  const addRecipeToGrid = async (recipe: any) => {
    if (!selectedSlot || !mealPlan) return;
    
    try {
      setLoading(true);
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        toast({ title: 'Please log in', status: 'warning', duration: 2500, isClosable: true });
        return;
      }

      const response = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/meals`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          recipe_id: recipe.id,
          meal_date: selectedSlot.date,
          meal_type: selectedSlot.mealType,
        }),
      });

              if (response.ok) {
                const result = await response.json();
                const dayName = new Date(selectedSlot.date).toLocaleDateString(undefined, {weekday: 'long'});
                toast({ 
                  title: 'Recipe added successfully!', 
                  description: `Added to ${dayName} ${selectedSlot.mealType} - synced across all views`, 
                  status: 'success', 
                  duration: 3000, 
                  isClosable: true 
                });
                
                // Store the added recipe to display in the box below grid
                const mealData = result.meal || result;
                const addedMeal: Meal = {
                  id: mealData.id || mealData.meal_id || recipe.id,
                  meal_name: mealData.meal_name || recipe.title || recipe.name || recipe.meal_name,
                  meal_type: (mealData.meal_type || selectedSlot.mealType) as any,
                  calories: mealData.calories || recipe.per_serving_calories || recipe.calories || recipe.nutrition?.calories || 0,
                  protein: mealData.protein || recipe.protein || recipe.nutrition?.protein || 0,
                  carbs: mealData.carbs || recipe.carbs || recipe.nutrition?.carbs || 0,
                  fats: mealData.fats || recipe.fats || recipe.nutrition?.fats || 0,
                  recipe: mealData.recipe || recipe,
                  dietary_tags: mealData.recipe?.dietary_tags || recipe.dietary_tags || recipe.dietaryTags || []
                };
                // CRITICAL FIX: Add the meal to the persistent list of recently added meals
                setRecentlyAddedMeals(prev => {
                  const existingIndex = prev.findIndex(m => {
                    const mId = m.id || (m as any).meal_id || (m as any).mealId;
                    const mName = m.meal_name || m.name || (m as any).mealName;
                    return String(mId) === String(addedMeal.id) || mName === addedMeal.meal_name;
                  });
                  
                  if (existingIndex >= 0) {
                    // Update existing meal
                    const updated = [...prev];
                    updated[existingIndex] = addedMeal;
                    return updated;
                  } else {
                    // Add new meal to the list
                    return [...prev, addedMeal];
                }
                });
                
                setRecipeSelectorOpen(false);
                setSelectedSlot(null);
                // CRITICAL FIX: Notify dashboard to reload
                window.dispatchEvent(new CustomEvent('mealPlanUpdated'));
                loadMealPlan(); // Reload to show the new meal
              } else {
                throw new Error('Failed to add recipe');
              }
    } catch (err: any) {
      console.error('Error adding recipe:', err);
      toast({ title: 'Failed to add recipe', description: err.message, status: 'error', duration: 3000, isClosable: true });
    } finally {
      setLoading(false);
    }
  };

  // Helper to get meal types based on mealsPerDay
  const getMealTypes = (mealsPerDay: number): string[] => {
    if (mealsPerDay <= 3) {
      return ['breakfast', 'lunch', 'dinner'];
    } else if (mealsPerDay === 4) {
      return ['breakfast', 'lunch', 'dinner', 'snack'];
    } else if (mealsPerDay === 5) {
      // Better UX: breakfast, lunch, dinner, and two snacks with clearer labels
      return ['breakfast', 'lunch', 'dinner', 'morning snack', 'afternoon snack'];
    } else {
      // 6+ meals: breakfast, morning snack, lunch, afternoon snack, dinner, evening snack
      const types = ['breakfast', 'morning snack', 'lunch', 'afternoon snack'];
      if (mealsPerDay >= 6) {
        types.push('dinner');
        if (mealsPerDay >= 7) {
          types.push('evening snack');
        }
      }
      return types;
    }
  };

  // Build dynamic assignment based on mealsPerDay (e.g., 5x7 for 5 meals/day)
  const mealTypes = useMemo(() => getMealTypes(mealsPerDay), [mealsPerDay]);
  
  const gridAssignments = useMemo(() => {
    // Use indexed slots to handle duplicate meal types (e.g., multiple snacks)
    // Structure: Record<date, Record<slotIndex, meal>>
    const result: Record<string, Record<number, any | null>> = {};
    weekDates.forEach(d => {
      result[d] = {};
      mealTypes.forEach((_, idx) => {
        result[d][idx] = null;
      });
    });
    const all = (mealPlan?.meals || []) as any[];
    
    // ROOT CAUSE DEBUG: Log exactly what meals we have before processing
    console.log('🔍 GRID ASSIGNMENTS DEBUG:', {
      mealPlanId: mealPlan?.id,
      totalMeals: all.length,
      meals: all.map(m => ({
        id: m.id || m.meal_id || m.mealId,
        name: m.meal_name || m.mealName,
        date: m.meal_date || m.date,
        type: m.meal_type || m.type,
        preservedType: m.recipe?.meal_type || m.recipe_details?.meal_type
      }))
    });
    
    // CRITICAL FIX: Pre-process snacks - collect and assign in order per day
    // Group snacks by date for ordered assignment
    // Also check for preserved meal_type in recipe_details (from immediate state update)
    const snacksByDate: Record<string, any[]> = {};
    const nonSnackMeals: any[] = [];
    
    all.forEach(m => {
      const t = (m.meal_type || m.type) as string;
      // ROOT CAUSE FIX: Categorize meals based ONLY on their current meal_type (as set by backend swap)
      // After a swap, the backend updates meal_type to reflect the new slot (e.g., dinner -> snack, snack -> dinner)
      // We should trust the backend's meal_type, not try to infer from preservedType
      // A meal is a snack ONLY if its current meal_type is explicitly a snack type
      // This prevents meals with meal_type='dinner' from being incorrectly categorized as snacks
      // CRITICAL: After swapping, a snack might have meal_type='dinner', so it should NOT be in snacksByDate
      const isSnack = t === 'snack' || 
                      t === 'morning snack' || 
                      t === 'afternoon snack' || 
                      t === 'evening snack';
      
      if (isSnack) {
        const d = m.meal_date || m.date;
        if (d) {
          if (!snacksByDate[d]) {
            snacksByDate[d] = [];
          }
          // CRITICAL: Check if this meal is already in snacksByDate for this date (deduplicate by ID)
          const mealId = m.id || m.meal_id || m.mealId;
          const isDuplicate = mealId && snacksByDate[d].some((existing: any) => {
            const existingId = existing.id || existing.meal_id || existing.mealId;
            return existingId === mealId;
          });
          
          if (!isDuplicate) {
            // ROOT CAUSE FIX: Since we're in the isSnack block, we know t is already a snack type
            // Use the current meal_type directly (it's what the backend set after the swap)
            // The preservedType in recipe_details is only used later for specific slot assignment (morning vs afternoon)
            console.log(`🔍 Adding snack to snacksByDate: id=${mealId}, name='${m.meal_name || m.mealName}', meal_type='${t}'`);
            
            // Store with current meal_type (backend's authoritative value after swap)
            snacksByDate[d].push({
              ...m,
              meal_type: t,
              type: t,
              // Preserve recipe and recipe_details for later slot assignment logic
              recipe: m.recipe || {},
              recipe_details: m.recipe_details || {}
            });
          }
        }
      } else {
        nonSnackMeals.push(m);
      }
    });
    
    // ROOT CAUSE FIX: Simplified non-snack meal assignment - allow any meal to be assigned to any slot
    // After swapping, meals can have any meal_type, so we should allow flexible assignment
    // CRITICAL: After swapping, a snack might have meal_type='dinner', so it should be assigned to a dinner slot
    // First, try to match by meal_type, but if that fails, assign to any available slot (including snack slots)
    nonSnackMeals.forEach(m => {
      const d = m.meal_date || m.date;
      const t = (m.meal_type || m.type) as string;
      if (!d || !result[d] || !t) return;
      
      let assigned = false;
      
      // First, try to match by meal_type (preferred)
      if (mealTypes.includes(t)) {
        for (let idx = 0; idx < mealTypes.length; idx++) {
          // CRITICAL FIX: After swapping, allow meals to be assigned to ANY slot, including snack slots
          // This allows snacks swapped with dinners to be assigned to dinner slots, and vice versa
          // Try to match by meal_type first (preferred)
          if (mealTypes[idx] === t && !result[d][idx]) {
            result[d][idx] = m;
            assigned = true;
            break;
          }
        }
      }
      
      // If not assigned yet, assign to first available slot (flexible assignment - ANY slot, including snacks)
      if (!assigned) {
        for (let idx = 0; idx < mealTypes.length; idx++) {
          // CRITICAL FIX: Allow assignment to ANY slot, including snack slots
          // This allows swapped meals to be assigned anywhere
          if (!result[d][idx]) {
            result[d][idx] = m;
            assigned = true;
            break;
          }
        }
      }
    });
    
    // ROOT CAUSE FIX: Simplified snack assignment - assign snacks to slots by order
    // Find all snack slot indices in order (morning snack, afternoon snack, etc.)
    const snackSlotIndices: number[] = [];
    mealTypes.forEach((mt, idx) => {
      if (mt === 'morning snack' || mt === 'afternoon snack' || mt === 'evening snack' || mt === 'snack') {
        snackSlotIndices.push(idx);
      }
    });
    
    // Sort to ensure correct order
    snackSlotIndices.sort((a, b) => a - b);
    
    // ROOT CAUSE DEBUG: Log snacks by date to see what we're processing
    console.log(`🔍 Snacks by date:`, Object.keys(snacksByDate).map(date => ({
      date,
      count: snacksByDate[date].length,
      snacks: snacksByDate[date].map((s: any) => ({
        id: s.id || s.meal_id || s.mealId,
        name: s.meal_name || s.mealName,
        meal_type: s.meal_type || s.type,
        recipe_meal_type: s.recipe?.meal_type,
        recipe_details_meal_type: s.recipe_details?.meal_type
      }))
    })));
    
    // ROOT CAUSE FIX: Simplified snack assignment - assign snacks to slots by order
    // Track assigned meals globally to prevent duplicates
    const globalAssignedMealIds = new Set<string | number>();
    
    // CRITICAL FIX: First, try to preserve original slot positions for snacks
    // This handles snack-to-snack swaps by preserving their original positions
    // Build a map of meal ID to its original slot position (before swap)
    const mealIdToOriginalSlot: Record<string | number, number> = {};
    all.forEach(m => {
      const mealId = m.id || m.meal_id || m.mealId;
      if (!mealId) return;
      
      // Try to find which slot this meal was originally in
      // Check if it's already in the grid from a previous assignment
      const mealDate = m.meal_date || m.date;
      if (mealDate && result[mealDate]) {
        // Check if this meal is already assigned to a slot
        for (let idx = 0; idx < mealTypes.length; idx++) {
          if (result[mealDate][idx] && 
              (result[mealDate][idx].id === mealId || 
               result[mealDate][idx].meal_id === mealId || 
               result[mealDate][idx].mealId === mealId)) {
            mealIdToOriginalSlot[mealId] = idx;
            break;
          }
        }
      }
    });
    
    Object.keys(snacksByDate).forEach(date => {
      const daySnacks = snacksByDate[date];
      if (!result[date] || snackSlotIndices.length === 0) return;
      
      // Track assigned meals for this date
      const dateAssignedMealIds = new Set<string | number>();
      
      // CRITICAL FIX: First, try to assign snacks to their original slot positions (if available)
      // This preserves snack-to-snack swaps
      daySnacks.forEach((snack) => {
        const snackId = snack.id || snack.meal_id || snack.mealId;
        const snackDate = snack.meal_date || snack.date;
        
        // Skip if already assigned or date mismatch
        if (snackId && (globalAssignedMealIds.has(snackId) || dateAssignedMealIds.has(snackId))) {
          return;
        }
        if (snackDate !== date) {
          return;
        }
        
        // CRITICAL FIX: Try to preserve original slot position first (for snack-to-snack swaps)
        let assigned = false;
        if (snackId && mealIdToOriginalSlot[snackId] !== undefined) {
          const originalSlot = mealIdToOriginalSlot[snackId];
          // Check if original slot is a snack slot and is available
          if (snackSlotIndices.includes(originalSlot) && !result[date][originalSlot]) {
            result[date][originalSlot] = snack;
          if (snackId) {
            dateAssignedMealIds.add(snackId);
            globalAssignedMealIds.add(snackId);
          }
            console.log(`✅ Assigned snack ${snackId} '${snack.meal_name || snack.mealName}' to ${date} original slot ${originalSlot}`);
            assigned = true;
        }
        }
      
        // If not assigned to original slot, assign to first available snack slot (by order)
        if (!assigned) {
          for (let i = 0; i < snackSlotIndices.length; i++) {
            const slotIdx = snackSlotIndices[i];
            if (!result[date][slotIdx]) {
              // Found available slot - assign snack
              result[date][slotIdx] = snack;
              if (snackId) {
                dateAssignedMealIds.add(snackId);
                globalAssignedMealIds.add(snackId);
              }
              console.log(`✅ Assigned snack ${snackId} '${snack.meal_name || snack.mealName}' to ${date} slot ${slotIdx}`);
              break; // Stop after assigning to first available slot
            }
          }
        }
      });
    });
    
    // Second pass: assign remaining meals by round-robin, matching meal type to slot
    // ROOT CAUSE FIX: Track which meals have already been assigned to prevent duplicates
    const assignedMealIdsSet = new Set<string | number>();
    // Collect all assigned meal IDs from the result grid
    Object.keys(result).forEach(date => {
      Object.values(result[date]).forEach(meal => {
        if (meal) {
          const mealId = meal.id || meal.meal_id || meal.mealId;
          if (mealId) {
            assignedMealIdsSet.add(mealId);
          }
        }
      });
    });
    
    const remainingByType: Record<string, any[]> = {};
    mealTypes.forEach((mt, idx) => {
      if (!remainingByType[mt]) {
        remainingByType[mt] = [];
      }
    });
    
    // ROOT CAUSE FIX: Do NOT process snacks here - they were already handled in snack assignment logic above
    // Snacks should only be assigned ONCE to ONE slot, not to all snack slots
    all.forEach(m => {
      const d = m.meal_date || m.date;
      const t = (m.meal_type || m.type) as string;
      if (!t) return;
      
      // ROOT CAUSE FIX: Skip if meal is already assigned (prevent duplicates)
      const mealId = m.id || m.meal_id || m.mealId;
      if (mealId && assignedMealIdsSet.has(mealId)) {
        return; // Already assigned, skip
      }
      
      const alreadyPlaced = d && result[d] && Object.values(result[d]).includes(m);
      if (alreadyPlaced) return;
      
      // ROOT CAUSE FIX: Do NOT process snacks in this second pass - they were already assigned above
      // This prevents snacks from being added to all snack slot buckets
      if (t === 'snack') {
        // Skip snacks - they were already processed in snack assignment logic above
        return;
      }
      
      if (mealTypes.includes(t)) {
        // Regular meal type matching (non-snacks only)
        if (remainingByType[t]) {
          remainingByType[t].push(m);
        }
      }
    });
    
    // Assign remaining meals to matching slots
    mealTypes.forEach((slot, slotIdx) => {
      let idx = 0;
      remainingByType[slot]?.forEach(m => {
        for (let i = 0; i < weekDates.length; i++) {
          const day = weekDates[(idx + i) % weekDates.length];
          if (!result[day][slotIdx]) {
            result[day][slotIdx] = m;
            idx = (idx + i + 1) % weekDates.length;
            break;
          }
        }
      });
    });
    
    return result;
  }, [mealPlan, weekDates, mealTypes]);

  // Debounce alternatives search input
  useEffect(() => {
    const id = setTimeout(() => setAltSearchDebounced(altSearch.trim().toLowerCase()), 200);
    return () => clearTimeout(id);
  }, [altSearch]);

  // Persist planType selection
  useEffect(() => {
    try {
      if (typeof window !== 'undefined') {
        localStorage.setItem('mealPlanView', planType);
      }
    } catch {}
  }, [planType]);

  // Load user preferences on mount
  useEffect(() => {
    const loadUserPreferences = async () => {
      try {
        const { supabase } = await import('../../lib/supabase.ts');
        const { data: { session } } = await supabase.auth.getSession();
        if (!session?.access_token) return;

        const response = await fetch('http://localhost:8000/nutrition/preferences', {
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
            'Content-Type': 'application/json'
          }
        });

        if (response.ok) {
          const prefs = await response.json();
          // CRITICAL FIX: Cap meals_per_day at 5 (max supported by grid)
          let loadedMealsPerDay = prefs.meals_per_day || 4;
          if (loadedMealsPerDay > 5) {
            loadedMealsPerDay = 5;
            console.warn('⚠️ Capped meals_per_day from', prefs.meals_per_day, 'to 5 (max supported)');
          }
          setPreferences({
            dietaryRestrictions: prefs.dietary_preferences || [],
            allergies: prefs.allergies || [],
            dislikedIngredients: prefs.disliked_ingredients || [],
            cuisinePreferences: prefs.cuisine_preferences || [],
            calorieTarget: prefs.daily_calorie_target || prefs.calorie_target || 2000,
            mealsPerDay: loadedMealsPerDay
          });
          // CRITICAL FIX: Always sync mealsPerDay state with preferences (force update)
          setMealsPerDay(loadedMealsPerDay);
          localStorage.setItem('mealsPerDay', loadedMealsPerDay.toString());
          console.log('🔄 Synced mealsPerDay from preferences:', loadedMealsPerDay);
          console.log('📊 Loaded user preferences:', {
            calorieTarget: prefs.daily_calorie_target || prefs.calorie_target || 2000,
            mealsPerDay: loadedMealsPerDay
          });
        }
      } catch (error) {
        console.warn('Failed to load user preferences:', error);
      }
    };

    loadUserPreferences();
  }, []);
  
  // CRITICAL FIX: When preferences are loaded, they should override localStorage
  // This ensures preferences take precedence over localStorage when navigating back
  useEffect(() => {
    if (preferences.mealsPerDay && preferences.mealsPerDay !== mealsPerDay) {
      setMealsPerDay(preferences.mealsPerDay);
      localStorage.setItem('mealsPerDay', preferences.mealsPerDay.toString());
    }
  }, [preferences.mealsPerDay]);

  const loadMealPlan = useCallback(async () => {
    // CRITICAL: Skip loading if we're currently generating a meal plan
    // This prevents race conditions where loadMealPlan restores from localStorage
    // while generateMealPlan is still running
    if (isGenerating) {
      console.log('⏸️ Skipping loadMealPlan - generation in progress');
      return;
    }
    
    // CRITICAL: Don't restore from localStorage if we just generated a meal plan (< 2 seconds ago)
    // This prevents loadMealPlan from restoring immediately after generation completes
    if (justGeneratedRef.current && Date.now() - justGeneratedRef.current < 2000) {
      console.log('⏸️ Skipping loadMealPlan - meal plan just generated, preventing localStorage restore');
      return;
    }
    
    // CRITICAL FIX: Prevent multiple localStorage restores in rapid succession
    // Only restore from localStorage once per session unless meal plan changes
    // This prevents the "✅ Restored meal plan from localStorage" message from appearing multiple times
    const currentMealPlanId = mealPlan?.id;
    const lastMealPlanId = typeof window !== 'undefined' ? localStorage.getItem('lastMealPlanId') : null;
    
    // If we already have the meal plan loaded and it matches localStorage, skip localStorage restore
    if (currentMealPlanId && lastMealPlanId && currentMealPlanId === lastMealPlanId && !localStorageRestoredRef.current) {
      // First load - allow localStorage restore
      localStorageRestoredRef.current = true;
    } else if (currentMealPlanId && lastMealPlanId && currentMealPlanId === lastMealPlanId && localStorageRestoredRef.current) {
      // Already loaded this meal plan from localStorage - skip restore to prevent duplicates
      console.log('⏸️ Skipping localStorage restore - meal plan already loaded:', currentMealPlanId);
      // But still fetch from API to ensure data is fresh
      // Don't return early - continue to API fetch
    }
    
    try {
      setLoading(true);
      setError(null);
      
      // Get Supabase session token for authentication
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      const headers: Record<string, string> = {
        'Content-Type': 'application/json'
      };
      
      if (session?.access_token) {
        headers.Authorization = `Bearer ${session.access_token}`;
      }
      
      // CRITICAL FIX: For weekly plans, calculate the Monday of the week containing selectedDate
      // This ensures we load the weekly plan that contains the selected date
      let queryDate = selectedDate;
      if (planType === 'weekly') {
        const start = new Date(selectedDate);
        const dayOfWeek = start.getDay();
        const mondayOffset = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
        start.setDate(start.getDate() + mondayOffset);
        queryDate = start.toISOString().split('T')[0];
      }
      
      // CRITICAL FIX: Don't try localStorage if we're generating (prevents race conditions)
      // Check this BEFORE accessing localStorage
      if (isGenerating) {
        console.log('⏸️ Skipping localStorage check - generation in progress');
      } else {
        // CRITICAL FIX: Try to load from localStorage first (for quick restore after navigation)
        // BUT ONLY if we're not currently generating (avoid race conditions)
        try {
          const lastMealPlanId = localStorage.getItem('lastMealPlanId');
          const lastMealPlanDate = localStorage.getItem('lastMealPlanDate');
          const lastMealPlanType = localStorage.getItem('lastMealPlanType');
          
          // For weekly plans, compare normalized dates (both should be Monday)
          // For daily plans, compare selectedDate directly
          const compareDate = planType === 'weekly' ? queryDate : selectedDate;
          
          if (lastMealPlanId && lastMealPlanDate && lastMealPlanType === planType) {
          // Try loading by ID first (faster and more reliable)
          // CRITICAL: Only try localStorage restore if NOT currently generating AND not already restored
          if (!isGenerating && (!localStorageRestoredRef.current || currentMealPlanId !== lastMealPlanId)) {
            const idResponse = await fetch(`http://localhost:8000/nutrition/meal-plans/${lastMealPlanId}`, {
              method: 'GET',
              headers
            });
            
            if (idResponse.ok) {
              const plan = await idResponse.json();
              // CRITICAL: Verify meal plan exists and has meals before restoring
              if (!plan.id || !plan.meals || plan.meals.length === 0) {
                console.log('⚠️ Meal plan in localStorage is invalid (no meals) - clearing');
                localStorage.removeItem('lastMealPlanId');
                localStorage.removeItem('lastMealPlanDate');
                localStorage.removeItem('lastMealPlanType');
                localStorageRestoredRef.current = false; // Reset ref
                return; // Continue to API fetch
              }
              
              // Verify it matches the current date/type
              const planStartDate = plan.start_date ? new Date(plan.start_date).toISOString().split('T')[0] : null;
              // For weekly plans, check if queryDate (Monday) matches plan start_date (should also be Monday now)
              // For daily plans, check if selectedDate matches plan start_date
              if (planStartDate === compareDate && plan.plan_type === planType) {
                // CRITICAL: Double-check we're still not generating (extra safety)
                if (!isGenerating && (!localStorageRestoredRef.current || currentMealPlanId !== plan.id)) {
                  console.log('✅ Restored meal plan from localStorage:', plan.id, `(${plan.meals.length} meals)`);
                  
                  // CRITICAL FIX: Mark that we've restored from localStorage for this meal plan
                  localStorageRestoredRef.current = true;
                  
                  // CRITICAL FIX: Deduplicate meals by ID before restoring (prevent duplicates)
                  const seenMealIds = new Set<string | number>();
                  const deduplicatedMeals = (plan.meals || []).filter((meal: any) => {
                    const mealId = meal.id || meal.meal_id || meal.mealId;
                    if (!mealId) return true; // Keep meals without IDs (shouldn't happen, but safe fallback)
                    if (seenMealIds.has(mealId)) {
                      console.warn('⚠️ Duplicate meal detected and removed (localStorage):', mealId, meal.meal_name);
                      return false; // Skip duplicate
                    }
                    seenMealIds.add(mealId);
                    return true;
                  });
                  
                  setMealPlan(null);
                  await new Promise(resolve => setTimeout(resolve, 0));
                  setMealPlan({
                    ...plan,
                    meals: deduplicatedMeals
                  });
                  setSelectedDay(null);
                  
                  // CRITICAL FIX: Only update mealsPerDay from backend if not already set by user
                  // This preserves the user's grid size choice
                  const currentMealsPerDay = parseInt(localStorage.getItem('mealsPerDay') || '0', 10);
                  if (!currentMealsPerDay || currentMealsPerDay <= 0) {
                    // Only set from backend if no user preference is saved
                    if (plan.user_preferences?.meals_per_day) {
                      setMealsPerDay(plan.user_preferences.meals_per_day);
                    } else {
                      // Try to load from user preferences API
                      try {
                        const prefsResponse = await fetch('http://localhost:8000/nutrition/preferences', { headers });
                        if (prefsResponse.ok) {
                          const prefs = await prefsResponse.json();
                          if (prefs.meals_per_day) {
                            setMealsPerDay(prefs.meals_per_day);
                          }
                        }
                      } catch (e) {
                        console.warn('Could not load meals_per_day from preferences:', e);
                      }
                    }
                  } else {
                    // User has already set mealsPerDay - preserve it
                    console.log(`Preserving user's mealsPerDay: ${currentMealsPerDay}`);
                  }
                  
                  return;
                } else {
                  console.log('⏸️ Skipping localStorage restore - already restored or generation in progress');
                }
              } else {
                // Plan exists but doesn't match date/type - clear stale localStorage
                console.log('⚠️ Stale meal plan in localStorage - clearing (date/type mismatch)');
                localStorage.removeItem('lastMealPlanId');
                localStorage.removeItem('lastMealPlanDate');
                localStorage.removeItem('lastMealPlanType');
                localStorageRestoredRef.current = false; // Reset ref
              }
            } else if (idResponse.status === 404) {
              // Meal plan doesn't exist in database - clear stale localStorage entry
              console.log('⚠️ Meal plan in localStorage not found in database (404) - clearing');
              localStorage.removeItem('lastMealPlanId');
              localStorage.removeItem('lastMealPlanDate');
              localStorage.removeItem('lastMealPlanType');
              localStorageRestoredRef.current = false; // Reset ref
            } else {
              // Other error - clear localStorage and try API fetch
              console.log('⚠️ Error fetching meal plan from localStorage ID - clearing');
              localStorage.removeItem('lastMealPlanId');
              localStorage.removeItem('lastMealPlanDate');
              localStorage.removeItem('lastMealPlanType');
              localStorageRestoredRef.current = false; // Reset ref
            }
          } else {
            console.log('⏸️ Skipping localStorage check - already restored or generation in progress');
          }
          }
        } catch (localStorageErr) {
          console.warn('Error checking localStorage:', localStorageErr);
        }
      }
      
      // CRITICAL: Only try API if not generating (localStorage was already checked)
      if (isGenerating) {
        console.log('⏸️ Skipping API fetch - generation in progress');
        setLoading(false);
        return;
      }
      
      // Try to load existing meal plan for the selected date and plan type
      const url = `http://localhost:8000/nutrition/meal-plans?date=${queryDate}&plan_type=${planType}&limit=1`;
      console.log('Loading meal plan from:', url);
      
      const response = await fetch(url, {
        method: 'GET',
        headers
      });
      
      if (response.ok) {
        const mealPlans = await response.json();
        console.log('Meal plans from API:', mealPlans);
        console.log('Meal plans count:', mealPlans.length);
        
        if (mealPlans.length > 0) {
          const plan = mealPlans[0];
          console.log('Setting meal plan:', plan);
          console.log('Meal plan ID:', plan.id);
          console.log('Meal plan type:', plan.plan_type);
          // Clear any stale localStorage entries and save the valid plan
          localStorage.removeItem('lastMealPlanId');
          localStorage.removeItem('lastMealPlanDate');
          localStorage.removeItem('lastMealPlanType');
          // CRITICAL FIX: Reset localStorage restore ref when loading different meal plan from API
          localStorageRestoredRef.current = false;
          console.log('Meals count:', plan.meals?.length || 0);
          
          // CRITICAL FIX: Deduplicate meals by ID before setting (prevent duplicates)
          const seenMealIds = new Set<string | number>();
          const deduplicatedMeals = (plan.meals || []).filter((meal: any) => {
            const mealId = meal.id || meal.meal_id || meal.mealId;
            if (!mealId) return true; // Keep meals without IDs (shouldn't happen, but safe fallback)
            if (seenMealIds.has(mealId)) {
              console.warn('⚠️ Duplicate meal detected and removed:', mealId, meal.meal_name);
              return false; // Skip duplicate
            }
            seenMealIds.add(mealId);
            return true;
          });
          
          // CRITICAL FIX: Force state update
          setMealPlan(null);
          await new Promise(resolve => setTimeout(resolve, 0));
          setMealPlan({
            ...plan,
            meals: deduplicatedMeals
          });
          setSelectedDay(null); // reset any day filter
          
          // CRITICAL FIX: Only update mealsPerDay from backend if not already set by user
          // This preserves the user's grid size choice and prevents resetting during meal generation
          const currentMealsPerDay = parseInt(localStorage.getItem('mealsPerDay') || '0', 10);
          if (!currentMealsPerDay || currentMealsPerDay <= 0) {
            // Only set from backend if no user preference is saved
            if (plan.user_preferences?.meals_per_day) {
              setMealsPerDay(plan.user_preferences.meals_per_day);
            } else {
              // Try to load from user preferences API
              try {
                const prefsResponse = await fetch('http://localhost:8000/nutrition/preferences', { headers });
                if (prefsResponse.ok) {
                  const prefs = await prefsResponse.json();
                  if (prefs.meals_per_day) {
                    setMealsPerDay(prefs.meals_per_day);
                  }
                }
              } catch (e) {
                console.warn('Could not load meals_per_day from preferences:', e);
              }
            }
          } else {
            // User has already set mealsPerDay - preserve it
            console.log(`Preserving user's mealsPerDay: ${currentMealsPerDay}`);
          }
          
          // CRITICAL: Save to localStorage for persistence
          // For weekly plans, save queryDate (Monday), for daily plans save selectedDate
          try {
            if (plan.id) {
              localStorage.setItem('lastMealPlanId', plan.id);
              localStorage.setItem('lastMealPlanDate', planType === 'weekly' ? queryDate : selectedDate);
              localStorage.setItem('lastMealPlanType', planType);
            }
          } catch (e) {
            console.warn('Failed to save to localStorage:', e);
          }
          return;
        } else {
          console.log('No meal plan found for date:', queryDate, 'plan_type:', planType);
          // Clear stale localStorage when no plan found
          localStorage.removeItem('lastMealPlanId');
          localStorage.removeItem('lastMealPlanDate');
          localStorage.removeItem('lastMealPlanType');
        }
      } else {
        const errorText = await response.text();
        console.error('Failed to load meal plan:', response.status, errorText);
      }
      
      // If no meal plan exists, show empty state
      setMealPlan(null);
      
    } catch (err) {
      console.error('Error loading meal plan:', err);
      setError('Failed to load meal plan');
      toast({ title: 'Failed to load meal plan', status: 'error', duration: 3000, isClosable: true });
      setMealPlan(null);
    } finally {
      setLoading(false);
    }
  }, [selectedDate, planType, isGenerating]);

  // CRITICAL FIX: Load meal plan when component mounts and when dependencies change
  // Also add visibility change listener to reload when returning to page
  // BUT skip if we're currently generating (prevent race conditions)
  useEffect(() => {
    const loadOnVisibilityChange = () => {
      if (document.visibilityState === 'visible' && !isGenerating) {
        // Reload when page becomes visible again (user navigated back)
        // BUT skip if generation is in progress
        loadMealPlan();
      }
    };
    
    document.addEventListener('visibilitychange', loadOnVisibilityChange);
    
    // Load on mount and when dependencies change
    // BUT skip if generation is in progress
    if (!isGenerating) {
      loadMealPlan();
    }
    
    return () => {
      document.removeEventListener('visibilitychange', loadOnVisibilityChange);
    };
  }, [loadMealPlan, isGenerating]);

  const generateMealPlan = async () => {
    try {
      setIsGenerating(true); // CRITICAL: Mark generation as in progress
      setLoading(true);
      setError(null);
      setStreamingProgress('Creating meal plan structure...');
      
      // CRITICAL FIX: Reset localStorage restore ref when generating new meal plan
      localStorageRestoredRef.current = false;
      
      // Clear current meal plan to show loading state
      setMealPlan(null);
      
      // Get Supabase session token for authentication
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        setError('Please log in to generate meal plans');
        toast({ title: 'Please log in', status: 'warning', duration: 2500, isClosable: true });
        return;
      }
      
      const headers = { Authorization: `Bearer ${session.access_token}` };
      console.log('🚀 PROGRESSIVE GENERATION: Creating meal plan structure first (lighter approach)');
      console.log('Calorie target:', preferences.calorieTarget);
      
      // Get API base URL from environment or use default
      const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';
      
      // STEP 1: Create empty meal plan structure first (lightweight - PROGRESSIVE MODE)
      const createResponse = await fetch(`${API_BASE_URL}/nutrition/meal-plans/generate?progressive=true`, {
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
            meals_per_day: mealsPerDay,
            dietary_preferences: preferences.dietaryRestrictions,
            allergies: preferences.allergies,
            disliked_ingredients: preferences.dislikedIngredients || [],
            cuisine_preferences: preferences.cuisinePreferences
          }
        })
      });
      
      let mealPlanId: string | null = null;
      let mealPlanStructure: any = null;
      
      if (createResponse.ok) {
        mealPlanStructure = await createResponse.json();
        mealPlanId = mealPlanStructure.id;
        console.log('✅ Meal plan structure created (progressive mode):', mealPlanId);
        
        // Set empty structure so user sees the grid with empty slots
        // User can now click "Generate AI" on each slot to fill progressively
        setMealPlan(mealPlanStructure);
        setStreamingProgress(null);
        toast({ 
          title: 'Meal plan structure created!', 
          description: 'Click "Generate Recipe" on empty slots to fill them one by one (lighter approach).', 
          status: 'success', 
          duration: 4000, 
          isClosable: true 
        });
        // CRITICAL FIX: Notify dashboard to reload
        window.dispatchEvent(new CustomEvent('mealPlanUpdated'));
        return; // Exit early - user fills slots progressively
      } else {
        // Structure creation failed
        let errorData: any = { detail: 'Failed to create meal plan structure' };
        let responseText = '';
        try {
          responseText = await createResponse.text();
          console.error('❌ Meal plan creation failed:', {
            status: createResponse.status,
            statusText: createResponse.statusText,
            responseText: responseText.substring(0, 500) // First 500 chars
          });
          
          if (responseText) {
            try {
              errorData = JSON.parse(responseText);
            } catch (parseErr) {
              // Response is not JSON, use the text as error message
              errorData = { 
                detail: responseText || createResponse.statusText || `Server returned ${createResponse.status} error` 
              };
            }
          }
        } catch (fetchError) {
          console.error('❌ Error fetching error response:', fetchError);
          errorData = { 
            detail: createResponse.statusText || `Server returned ${createResponse.status} error` 
          };
        }
        
        // Log the extracted error data
        console.error('❌ Extracted error data:', errorData);
        
        if (createResponse.status === 400 && errorData.detail && errorData.detail.includes('nutrition preferences')) {
          setError('Please set up your nutrition preferences first. Go to the Nutrition Dashboard to configure your preferences.');
          toast({ title: 'Set up nutrition preferences first', status: 'info', duration: 3000, isClosable: true });
        } else {
          // Extract error message from multiple possible fields
          let errorMessage = errorData.detail || errorData.message || errorData.error || responseText;
          
          // If error message is empty or just whitespace, provide a default based on status code
          if (!errorMessage || errorMessage.trim() === '' || errorMessage === 'Error generating meal plan: ') {
            if (createResponse.status === 500) {
              errorMessage = 'Internal server error. Please check backend logs for details.';
            } else if (createResponse.status === 401) {
              errorMessage = 'Authentication failed. Please log in again.';
            } else if (createResponse.status === 403) {
              errorMessage = 'Permission denied.';
            } else if (createResponse.status === 404) {
              errorMessage = 'Endpoint not found.';
            } else {
              errorMessage = `Server error (${createResponse.status}): ${createResponse.statusText || 'Unknown error'}`;
            }
          }
          
          // Remove redundant "Error generating meal plan: " prefix if present
          if (errorMessage.startsWith('Error generating meal plan: ')) {
            errorMessage = errorMessage.substring('Error generating meal plan: '.length).trim() || 'Unknown error occurred';
          }
          
          console.error('❌ Throwing error with message:', errorMessage);
          throw new Error(errorMessage);
        }
      }
    } catch (err: any) {
      console.error('❌ Error generating meal plan - Full error object:', err);
      console.error('❌ Error type:', typeof err);
      console.error('❌ Error keys:', Object.keys(err || {}));
      
      // Extract error message from various possible error formats
      let errorMessage = 'Failed to generate meal plan';
      if (err?.message) {
        errorMessage = err.message;
      } else if (err?.response?.data?.detail) {
        errorMessage = err.response.data.detail;
      } else if (err?.response?.data?.message) {
        errorMessage = err.response.data.message;
      } else if (err?.detail) {
        errorMessage = err.detail;
      } else if (typeof err === 'string') {
        errorMessage = err;
      } else if (err?.toString && err.toString() !== '[object Object]') {
        errorMessage = err.toString();
      }
      
      console.error('❌ Final error message to display:', errorMessage);
      setError(errorMessage);
      toast({ 
        title: 'Failed to generate meal plan', 
        description: errorMessage,
        status: 'error', 
        duration: 5000, 
        isClosable: true 
      });
    } finally {
      setIsGenerating(false); // CRITICAL: Clear generation flag
      // CRITICAL: Clear the "just generated" ref after generation completes
      // This allows localStorage restore again after 2 seconds (safety window)
      setTimeout(() => {
        justGeneratedRef.current = null;
      }, 2500); // Clear after 2.5 seconds (slightly longer than the 2-second check)
      setLoading(false);
    }
  };

  // CRITICAL FIX: Generate complete meal plan by generating all meals for each day sequentially
  // Uses the same working code path as "Generate Day's Meals" button - ensures smooth updates and correct values
  const generateCompleteMealPlan = async () => {
    if (!mealPlan) {
      toast({ 
        title: 'No meal plan structure', 
        description: 'Please create a meal plan structure first', 
        status: 'warning', 
        duration: 3000, 
        isClosable: true 
      });
      return;
    }

    try {
      setIsGenerating(true);
      setLoading(true);
      setError(null);
      
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        setError('Please log in to generate meal plans');
        toast({ title: 'Please log in', status: 'warning', duration: 2500, isClosable: true });
        return;
      }

      // CRITICAL FIX: Generate all meals for each day sequentially (same as "Generate Day's Meals" button)
      // This uses the same working code path as daily generation, ensuring smooth updates
      const mealTypes = mealsPerDay === 5 
        ? ['breakfast', 'lunch', 'dinner', 'morning snack', 'afternoon snack']
        : mealsPerDay === 4
        ? ['breakfast', 'lunch', 'dinner', 'snack']
        : ['breakfast', 'lunch', 'dinner'];
      
      // CRITICAL FIX: For weekly plans, use weekDates to ensure Monday to Sunday order
      const datesToGenerate = planType === 'weekly' ? weekDates : [selectedDate];
      const days = datesToGenerate.length;
      let totalGenerated = 0;
      
      // Generate all meals for each day sequentially - when one day is done, start next
      // For weekly plans, this ensures Monday to Sunday order
      for (let dayIndex = 0; dayIndex < days; dayIndex++) {
        const dateStr = datesToGenerate[dayIndex];
        const dayName = new Date(dateStr).toLocaleDateString(undefined, {weekday: 'long', month: 'short', day: 'numeric'});
        
        // Find empty slots for this day
        const emptyMealTypes = mealTypes.filter((mealType) => {
          const existingMeal = mealPlan.meals.find((m: any) => {
            const mDate = m.meal_date || m.date;
            const mType = m.meal_type || m.type;
            return mDate === dateStr && mType === mealType;
          });
          return !existingMeal;
        });
        
        if (emptyMealTypes.length === 0) {
          setStreamingProgress(`Day ${dayIndex + 1}/${days} (${dayName}): All meals already exist, skipping...`);
          await new Promise(resolve => setTimeout(resolve, 300));
          continue;
        }
        
        // Generate all empty meals for this day sequentially
        setStreamingProgress(`Day ${dayIndex + 1}/${days} (${dayName}): Generating ${emptyMealTypes.length} meals...`);
        
        for (let i = 0; i < emptyMealTypes.length; i++) {
          const mealType = emptyMealTypes[i];
          const slotKey = `${dateStr}-${mealType}`;
          
          // CRITICAL FIX: Track which specific meal slot is generating (only show loading for that button)
          setGeneratingMeals(prev => new Set(prev).add(slotKey));
          setStreamingProgress(`Day ${dayIndex + 1}/${days} (${dayName}): Generating ${mealType}... (${i + 1}/${emptyMealTypes.length})`);
          
          try {
            const response = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/generate-meal-slot`, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${session.access_token}`,
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                meal_date: dateStr,
                meal_type: mealType.toLowerCase(),
              }),
            });

            if (response.ok) {
              const result = await response.json();
              totalGenerated++;
              
              // CRITICAL FIX: Remove from generating set immediately after success
              setGeneratingMeals(prev => {
                const next = new Set(prev);
                next.delete(slotKey);
                return next;
              });
              
              // Update meal plan immediately for smooth progressive updates
              const updatedMeal = {
                ...result.meal,
                meal_date: dateStr,
                meal_type: mealType,
                date: dateStr,
                type: mealType,
                recipe: {
                  ...(result.meal.recipe || {}),
                  meal_type: mealType
                },
                recipe_details: {
                  ...(result.meal.recipe || result.meal.recipe_details || {}),
                  meal_type: mealType
                }
              };
              
              setMealPlan(prev => {
                if (!prev) return null;
                const existingIndex = prev.meals.findIndex(
                  (m: any) => {
                    const mDate = m.meal_date || m.date;
                    const mType = m.meal_type || m.type;
                    return mDate === dateStr && mType === mealType;
                  }
                );
                
                if (existingIndex >= 0) {
                  const updatedMeals = [...prev.meals];
                  updatedMeals[existingIndex] = updatedMeal;
                  return { ...prev, meals: updatedMeals };
                } else {
                  return { ...prev, meals: [...prev.meals, updatedMeal] };
                }
              });
              
              // Small delay for smooth visual updates
              await new Promise(resolve => setTimeout(resolve, 200));
            } else {
              // CRITICAL FIX: Remove from generating set on error
              setGeneratingMeals(prev => {
                const next = new Set(prev);
                next.delete(slotKey);
                return next;
              });
              console.warn(`Failed to generate ${mealType} for ${dateStr}`);
            }
          } catch (err) {
            // CRITICAL FIX: Remove from generating set on exception
            setGeneratingMeals(prev => {
              const next = new Set(prev);
              next.delete(slotKey);
              return next;
            });
            console.error(`Error generating ${mealType} for ${dateStr}:`, err);
            // Continue with next meal instead of failing completely
          }
        }
        
        // Day complete - show progress and small delay before next day
        setStreamingProgress(`Day ${dayIndex + 1}/${days} (${dayName}): Complete! ✅`);
        await new Promise(resolve => setTimeout(resolve, 500));
      }
      
      // Reload meal plan to ensure consistency
      await loadMealPlan();
      
      // CRITICAL: Automatically adjust portions to fit nutrition target
      if (mealPlan?.id && totalGenerated > 0) {
        setStreamingProgress('Adjusting portions to fit your nutrition target...');
        
        try {
          const { supabase } = await import('../../lib/supabase.ts');
          const { data: { session } } = await supabase.auth.getSession();
          
          if (session?.access_token) {
            // For weekly plans, adjust all days. For daily plans, adjust the selected date
            const datesToAdjust = planType === 'weekly' ? weekDates : [selectedDate];
            
            // Adjust all days in parallel
            const adjustmentPromises = datesToAdjust.map(async (date) => {
              try {
                const response = await fetch(
                  `http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/fix-daily-totals?target_date=${date}`,
                  {
                    method: 'POST',
                    headers: {
                      'Authorization': `Bearer ${session.access_token}`,
                    },
                  }
                );
                return response.ok;
              } catch (err) {
                console.error(`Error adjusting daily total for ${date}:`, err);
                return false;
              }
            });
            
            await Promise.all(adjustmentPromises);
            
            // Reload meal plan after adjustment
            await loadMealPlan();
          }
        } catch (err) {
          console.error('Error adjusting daily totals:', err);
          // Don't fail the whole generation if adjustment fails
        }
      }
      
      setStreamingProgress(null);
      toast({ 
        title: 'Meal plan generated!', 
        description: `Generated ${totalGenerated} meals across ${days} day${days > 1 ? 's' : ''}. Portions adjusted to fit your nutrition target.`, 
        status: 'success', 
        duration: 4000, 
        isClosable: true 
      });
      
      // CRITICAL FIX: Notify dashboard to reload
      window.dispatchEvent(new CustomEvent('mealPlanUpdated'));
      
    } catch (err: any) {
      console.error('Error generating complete meal plan:', err);
      setError(err.message || 'Failed to generate meal plan');
      toast({ 
        title: 'Failed to generate meal plan', 
        description: err.message || 'Please try again', 
        status: 'error', 
        duration: 5000, 
        isClosable: true 
      });
    } finally {
      setIsGenerating(false);
      setLoading(false);
      setStreamingProgress(null);
      // CRITICAL FIX: Clear all generating meals on completion
      setGeneratingMeals(new Set());
    }
  };

  const handleMealEdit = (meal: Meal) => {
    setSelectedMeal(meal);
    onOpen();
  };

  // Load ingredient substitution suggestions for meal plan recipes
  const loadSubstitutionSuggestions = async (ingredientName: string) => {
    if (!selectedRecipe) return;
    
    // CRITICAL: Check if meal has recipe_details with ingredients in database before making API call
    // We MUST check the original meal object from mealPlan.meals, not the normalized selectedRecipe
    // because the backend checks the database, not the frontend state
    const mealId = (selectedRecipe as any).meal_id || selectedRecipe.id;
    const mealFromPlan = mealPlan?.meals?.find((m: any) => 
      (m.id === mealId) || (m.meal_id === mealId)
    );
    
    // Check recipe_details from the original meal object (what's in the database)
    const recipeDetailsFromDB = (mealFromPlan as any)?.recipe_details || (mealFromPlan?.recipe as any)?.recipe_details;
    
    // Check if recipe_details exists in database and has ingredients
    const hasRecipeDetailsWithIngredients = recipeDetailsFromDB && 
      recipeDetailsFromDB.ingredients && 
      Array.isArray(recipeDetailsFromDB.ingredients) &&
      recipeDetailsFromDB.ingredients.length > 0;
    
    if (!hasRecipeDetailsWithIngredients) {
      console.warn('⚠️ Cannot substitute - missing recipe_details with ingredients in database:', {
        mealId,
        hasMealFromPlan: !!mealFromPlan,
        hasRecipeDetails: !!recipeDetailsFromDB,
        recipeDetailsStructure: recipeDetailsFromDB ? JSON.stringify(recipeDetailsFromDB, null, 2) : 'null'
      });
      toast({
        title: 'Cannot substitute ingredients',
        description: 'This meal does not have detailed recipe information stored. Please regenerate this meal to enable ingredient substitution.',
        status: 'warning',
        duration: 5000,
        isClosable: true,
      });
      return;
    }
    
    try {
      setLoadingSubstitutions(true);
      setSubstitutionIngredient(ingredientName);
      
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        toast({ title: 'Please log in', status: 'warning', duration: 2500, isClosable: true });
        return;
      }
      
      const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';
      
      // Check if this is a meal plan meal (has meal_id) or AI-generated recipe
      const mealId = (selectedRecipe as any).meal_id || (selectedRecipe as any).id;
      const mealPlanId = mealPlan?.id;
      
      if (!mealPlanId || !mealId) {
        toast({
          title: 'Cannot substitute',
          description: 'This recipe is not part of a meal plan',
          status: 'warning',
          duration: 3000,
          isClosable: true,
        });
        return;
      }
      
      // Convert mealId to integer if it's a string
      const mealIdInt = typeof mealId === 'string' ? parseInt(mealId, 10) : mealId;
      if (isNaN(mealIdInt)) {
        toast({
          title: 'Invalid meal ID',
          description: 'Cannot determine meal ID',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
        return;
      }
      
      // Use meal plan meal substitution endpoint
      const response = await fetch(
        `${API_BASE_URL}/nutrition/meal-plans/${mealPlanId}/meals/${mealIdInt}/substitutions/${encodeURIComponent(ingredientName)}?reason=dietary_preference`,
        {
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        setSubstitutionSuggestions(data.suggestions || []);
        onSubstitutionOpen();
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to load substitutions' }));
        const errorMessage = errorData.detail || 'Please try again';
        
        // Check if error is about missing recipe details
        if (errorMessage.includes('recipe details') || errorMessage.includes('ingredient information')) {
          toast({
            title: 'Cannot substitute ingredients',
            description: 'This meal does not have detailed recipe information. Only AI-generated recipes or meals with full recipe details can have ingredients substituted.',
            status: 'warning',
            duration: 5000,
            isClosable: true,
          });
        } else {
          toast({
            title: 'Failed to load substitutions',
            description: errorMessage,
            status: 'error',
            duration: 3000,
            isClosable: true,
          });
        }
      }
    } catch (err: any) {
      console.error('Error loading substitutions:', err);
      toast({
        title: 'Error loading substitutions',
        description: err.message || 'Please try again',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoadingSubstitutions(false);
    }
  };

  // Apply ingredient substitution to meal plan meal
  const applySubstitution = async (substitution: any) => {
    if (!selectedRecipe || !substitutionIngredient || !mealPlan) return;
    
    try {
      setLoading(true);
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        toast({ title: 'Please log in', status: 'warning', duration: 2500, isClosable: true });
        return;
      }
      
      const mealId = (selectedRecipe as any).meal_id || (selectedRecipe as any).id;
      if (!mealId) {
        toast({
          title: 'Cannot substitute',
          description: 'This recipe is not part of a meal plan',
          status: 'warning',
          duration: 3000,
          isClosable: true,
        });
        return;
      }
      
      // Convert mealId to integer if it's a string
      const mealIdInt = typeof mealId === 'string' ? parseInt(mealId, 10) : mealId;
      if (isNaN(mealIdInt)) {
        toast({
          title: 'Invalid meal ID',
          description: 'Cannot determine meal ID',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
        return;
      }
      
      const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(
        `${API_BASE_URL}/nutrition/meal-plans/${mealPlan.id}/meals/${mealIdInt}/substitutions/apply`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            ingredient_name: substitutionIngredient,
            substitution: substitution
          }),
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        toast({
          title: 'Substitution applied!',
          description: `${substitutionIngredient} replaced with ${substitution.name}`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        onSubstitutionClose();
        
        // CRITICAL FIX: Update selectedRecipe with the updated recipe_details from backend
        // This ensures the recipe card doesn't go empty after substitution
        if (data.updated_recipe_details && selectedRecipe) {
          const updatedRecipeDetails = data.updated_recipe_details;
          
          // Store the updated recipe data in a variable to preserve it
          const updatedSelectedRecipe = {
            ...selectedRecipe,
            recipe_details: updatedRecipeDetails,
            ingredients: updatedRecipeDetails.ingredients || selectedRecipe.ingredients || [],
            instructions: updatedRecipeDetails.instructions || selectedRecipe.instructions || [],
            calories: updatedRecipeDetails.per_serving_calories || updatedRecipeDetails.calories || selectedRecipe.calories,
            protein: updatedRecipeDetails.per_serving_protein || updatedRecipeDetails.protein || selectedRecipe.protein,
            carbs: updatedRecipeDetails.per_serving_carbs || updatedRecipeDetails.carbs || selectedRecipe.carbs,
            fats: updatedRecipeDetails.per_serving_fats || updatedRecipeDetails.fats || selectedRecipe.fats,
            nutrition: updatedRecipeDetails.nutrition || (selectedRecipe as any).nutrition
          };
          
          // CRITICAL: Update selectedRecipe immediately using functional update
          // This ensures the updated data persists even after loadMealPlan updates state
          setSelectedRecipe(prev => {
            // If prev exists and has the same ID, update it with new data
            // Otherwise, just use the updated data
            const prevAny = prev as any;
            if (prev && (prevAny.id === updatedSelectedRecipe.id || prevAny.meal_id === (updatedSelectedRecipe as any).meal_id)) {
              return updatedSelectedRecipe;
            }
            return updatedSelectedRecipe;
          });
          
          // Reload meal plan to update the grid
          await loadMealPlan();
          
          // CRITICAL: After loadMealPlan completes, ensure selectedRecipe still has the updated data
          // Use functional update to preserve the updated data even if mealPlan state changed
          setSelectedRecipe(prev => {
            const prevAny = prev as any;
            if (prev && (prevAny.id === updatedSelectedRecipe.id || prevAny.meal_id === (updatedSelectedRecipe as any).meal_id)) {
              // Keep the updated data we set above
              return updatedSelectedRecipe;
            }
            return prev;
          });
        } else {
          // If no updated_recipe_details, just reload the meal plan
          await loadMealPlan();
        }
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to apply substitution' }));
        const errorMessage = errorData.detail || 'Please try again';
        
        // Check if error is about missing recipe details
        if (errorMessage.includes('recipe details') || errorMessage.includes('ingredient information')) {
          toast({
            title: 'Cannot substitute ingredients',
            description: 'This meal does not have detailed recipe information. Only AI-generated recipes or meals with full recipe details can have ingredients substituted.',
            status: 'warning',
            duration: 5000,
            isClosable: true,
          });
        } else {
          toast({
            title: 'Failed to apply substitution',
            description: errorMessage,
            status: 'error',
            duration: 3000,
            isClosable: true,
          });
        }
      }
    } catch (err: any) {
      console.error('Error applying substitution:', err);
      toast({
        title: 'Error applying substitution',
        description: err.message || 'Please try again',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const estimateNutritionFromIngredients = (ingredients: any[]): { calories: number; protein: number; carbs: number; fats: number } => {
    const per100g: Record<string, [number, number, number, number]> = {
      'chicken breast': [165, 31, 0, 3.6],
      'chickpea': [364, 19, 61, 6],
      'chickpeas': [364, 19, 61, 6],
      'olive oil': [884, 0, 0, 100],
      'tomato': [18, 0.9, 3.9, 0.2],
      'cucumber': [16, 0.7, 3.6, 0.1],
      'lettuce': [15, 1.4, 2.9, 0.2],
      'bell pepper': [31, 1, 6, 0.3],
      'pepper': [31, 1, 6, 0.3],
      'carrot': [41, 0.9, 10, 0.2],
      'onion': [40, 1.1, 9.3, 0.1],
      'garlic': [149, 6.4, 33, 0.5],
      'feta': [265, 14, 4, 21],
      'hummus': [166, 8, 14, 9.6],
      'rice': [130, 2.4, 28, 0.3],
      'quinoa': [120, 4.4, 21, 1.9],
      'pasta': [131, 5, 25, 1.1],
      'yogurt': [59, 10, 3.6, 0.4],
    };
    const total = { calories: 0, protein: 0, carbs: 0, fats: 0 };
    (ingredients || []).forEach((ing: any) => {
      const name = (typeof ing === 'string' ? ing : String(ing?.name || '')).toLowerCase();
      const qty = typeof ing === 'string' ? 0 : Number(ing?.quantity || 0);
      const unit = typeof ing === 'string' ? 'g' : String(ing?.unit || 'g').toLowerCase();
      const match = Object.keys(per100g).find(k => name.includes(k));
      if (!match || !qty) return;
      const grams = unit === 'ml' ? qty : qty;
      const [cal, p, c, f] = per100g[match];
      const factor = grams / 100;
      total.calories += cal * factor;
      total.protein += p * factor;
      total.carbs += c * factor;
      total.fats += f * factor;
    });
    return {
      calories: Math.round(total.calories),
      protein: Math.round(total.protein),
      carbs: Math.round(total.carbs),
      fats: Math.round(total.fats),
    };
  };

  // Handle serving size changes with preview
  const handleServingsChange = (newServings: number) => {
    if (!selectedRecipe || newServings <= 0) return;
    
    // Update preview servings state
    setPreviewServings(newServings);
    
    // Always allow preview - no need to check for meal ID
    const selectedRecipeAny = selectedRecipe as any;
    const currentServings = selectedRecipeAny.servings || selectedRecipe.recipe?.servings || 1;
    const multiplier = newServings / currentServings;
    
    // Preview the adjusted nutrition
    const previewCalories = Math.round((selectedRecipe.calories || selectedRecipeAny.per_serving_calories || 0) * multiplier);
    const previewProtein = Math.round((selectedRecipe.protein || 0) * multiplier);
    const previewCarbs = Math.round((selectedRecipe.carbs || 0) * multiplier);
    const previewFats = Math.round((selectedRecipe.fats || 0) * multiplier);
    
    setSelectedRecipe(prev => prev ? {
      ...prev,
      servings: newServings,
      previewCalories,
      previewProtein,
      previewCarbs,
      previewFats,
      previewMultiplier: multiplier
    } : null);
  };

  const handleViewRecipe = (meal: Meal) => {
    const m: any = meal as any;
    const candidate = m.recipe || m.recipe_details || (Array.isArray(m.recipes) ? m.recipes[0] : null) || m;
    const normalized: any = { ...candidate };

    // CRITICAL FIX: Extract ingredients from various nested locations
    // Database recipes store ingredients in recipe_details.ingredients
    normalized.ingredients = normalized.ingredients 
      || candidate?.ingredients 
      || m.recipe?.ingredients 
      || m.recipe_details?.ingredients 
      || m.ingredients 
      || [];

    // CRITICAL FIX: Extract instructions from various nested locations
    // Database recipes store instructions in recipe_details.instructions
    normalized.instructions = normalized.instructions 
      || candidate?.instructions 
      || m.recipe?.instructions 
      || m.recipe_details?.instructions 
      || m.instructions 
      || [];

    // CRITICAL FIX: Ensure instructions have proper step numbers
    if (Array.isArray(normalized.instructions)) {
      normalized.instructions = normalized.instructions.map((inst: any, idx: number) => {
        if (typeof inst === 'string') {
          return inst; // Keep string format as-is
        }
        // Ensure step number is present (use step_number, step, or index)
        const step = inst.step_number || inst.step || (idx + 1);
        return {
          ...inst,
          step: step,
          step_number: step, // Ensure both formats exist
          description: inst.description || inst.text || ''
        };
      });
    }

    // Find nutrition from any possible location
    const nutrition = (candidate?.nutrition)
      || (m.recipe?.nutrition)
      || (m.recipe_details?.nutrition)
      || (m.nutrition)
      || null;

    const toNum = (v: any) => (typeof v === 'number' ? v : parseFloat(v) || 0);

    if (nutrition) {
      normalized.nutrition = nutrition;
      normalized.calories = toNum(nutrition.calories ?? normalized.calories ?? nutrition.per_serving_calories);
      normalized.protein = toNum(nutrition.protein ?? normalized.protein ?? nutrition.per_serving_protein);
      normalized.carbs = toNum(nutrition.carbs ?? normalized.carbs ?? nutrition.per_serving_carbs);
      normalized.fats = toNum(nutrition.fats ?? normalized.fats ?? nutrition.per_serving_fats);
    }

    // CRITICAL FIX: Also check for per_serving values at top level
    if (!normalized.calories && (normalized.per_serving_calories || candidate?.per_serving_calories)) {
      normalized.calories = toNum(normalized.per_serving_calories || candidate?.per_serving_calories);
    }
    if (!normalized.protein && (normalized.per_serving_protein || candidate?.per_serving_protein)) {
      normalized.protein = toNum(normalized.per_serving_protein || candidate?.per_serving_protein);
    }
    if (!normalized.carbs && (normalized.per_serving_carbs || candidate?.per_serving_carbs)) {
      normalized.carbs = toNum(normalized.per_serving_carbs || candidate?.per_serving_carbs);
    }
    if (!normalized.fats && (normalized.per_serving_fats || candidate?.per_serving_fats)) {
      normalized.fats = toNum(normalized.per_serving_fats || candidate?.per_serving_fats);
    }

    // Fallback from meal-level totals
    normalized.calories = toNum(normalized.calories ?? m.calories);
    normalized.protein = toNum(normalized.protein ?? m.protein);
    normalized.carbs = toNum(normalized.carbs ?? m.carbs);
    normalized.fats = toNum(normalized.fats ?? m.fats);

    // If still zero across the board, estimate from ingredients
    if ((!normalized.calories && !normalized.protein && !normalized.carbs && !normalized.fats) && Array.isArray(normalized.ingredients)) {
      const est = estimateNutritionFromIngredients(normalized.ingredients);
      normalized.calories = est.calories;
      normalized.protein = est.protein;
      normalized.carbs = est.carbs;
      normalized.fats = est.fats;
      normalized.nutrition = { ...normalized.nutrition, ...est };
    }

    // Title fallback
    normalized.title = normalized.title || m.meal_name || m.name || 'Recipe Details';

    // CRITICAL FIX: Ensure dietary tags are extracted
    normalized.dietary_tags = normalized.dietary_tags || normalized.dietaryTags || candidate?.dietary_tags || m.recipe_details?.dietary_tags || [];

    // CRITICAL: Preserve meal ID so serving size adjuster works
    normalized.id = m.id || normalized.id || (m as any).meal_id;
    normalized.meal_id = normalized.meal_id || m.id || (m as any).meal_id;
    
    // CRITICAL: Preserve servings from meal/recipe
    normalized.servings = normalized.servings || normalized.recipe?.servings || m.recipe_details?.servings || candidate?.servings || 1;
    normalized.recipe = {
      ...(normalized.recipe || {}),
      servings: normalized.servings || 1
    };
    
    // CRITICAL: Preserve recipe_details structure for ingredient substitution
    // This is needed because the backend checks recipe_details.ingredients
    if (m.recipe_details && typeof m.recipe_details === 'object') {
      normalized.recipe_details = m.recipe_details;
    } else if (candidate?.recipe_details && typeof candidate.recipe_details === 'object') {
      normalized.recipe_details = candidate.recipe_details;
    } else if (m.recipe && typeof m.recipe === 'object' && m.recipe.recipe_details) {
      normalized.recipe_details = m.recipe.recipe_details;
    } else if (normalized.ingredients && normalized.ingredients.length > 0) {
      // CRITICAL FIX: If we have ingredients but no recipe_details, create one from normalized data
      // This ensures substitution works for AI-generated recipes that might not have recipe_details preserved
      normalized.recipe_details = {
        ingredients: normalized.ingredients,
        instructions: normalized.instructions || [],
        dietary_tags: normalized.dietary_tags || [],
        servings: normalized.servings || 1,
        ai_generated: normalized.ai_generated !== false,
        title: normalized.title || m.meal_name || m.name || 'Recipe',
        ...(normalized.nutrition ? { nutrition: normalized.nutrition } : {})
      };
    }

    setSelectedRecipe(normalized as any);
    setPreviewServings(normalized.servings || 1);
    onRecipeOpen();
  };

  const getCachedAlternatives = (mealType: string) => {
    const entry = alternativesCacheRef.current[mealType];
    if (!entry) return null;
    if (Date.now() - entry.ts > ALT_TTL_MS) return null;
    return entry.items;
  };

  const prefetchAlternatives = async (mealType: string) => {
    if (!mealPlan?.id) return;
    // Use cache if fresh
    const cached = getCachedAlternatives(mealType);
    if (cached) {
      setAlternatives(prev => ({ ...prev, [mealType]: cached }));
      return;
    }
    try {
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.access_token) return;
      // Abort any in-flight request for this meal type
      if (controllersRef.current[mealType]) controllersRef.current[mealType]!.abort();
      const controller = new AbortController();
      controllersRef.current[mealType] = controller;
      const response = await fetch(
        `http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/alternatives/${mealType}?count=3`,
        { headers: { Authorization: `Bearer ${session.access_token}` }, signal: controller.signal }
      );
      if (response.ok) {
        const data = await response.json();
        alternativesCacheRef.current[mealType] = { items: data.alternatives, ts: Date.now() };
        setAlternatives(prev => ({ ...prev, [mealType]: data.alternatives }));
      }
    } catch (e) {
      // Ignore abort errors
    }
  };

  // Simple two-click swap function
  const handleSimpleSwap = async (mealId: string, date: string, mealType: string) => {
    if (!mealPlan?.id) return;
    
    // First click: enter swap mode and select source meal
    if (!swapMode || !swapSourceMeal) {
      // CRITICAL FIX: Allow empty mealId for user recipe replacement mode
      if (!mealId && !swapSourceMeal?.isUserRecipe) {
        return; // Don't allow empty mealId for normal swap mode
      }
      setSwapMode(true);
      setSwapSourceMeal({ id: mealId, date, mealType });
      toast({
        title: 'Swap mode active',
        description: 'Click another meal to swap with this one',
        status: 'info',
        duration: 3000,
        isClosable: true
      });
      return;
    }
    
    // Second click: perform the swap
    if (swapSourceMeal.id === mealId) {
      // Same meal clicked - cancel swap
      setSwapMode(false);
      setSwapSourceMeal(null);
      toast({
        title: 'Swap cancelled',
        description: 'Same meal selected',
        status: 'info',
        duration: 2000,
        isClosable: true
      });
      return;
    }
    
    // CRITICAL FIX: Handle user recipe replacement (replace, not swap)
    // When user recipe is being replaced, delete the AI recipe in the grid slot and move user recipe there
    if (swapSourceMeal.isUserRecipe) {
      try {
        const { supabase } = await import('../../lib/supabase.ts');
        const { data: { session } } = await supabase.auth.getSession();
        
        if (!session?.access_token) {
          toast({ title: 'Please log in', status: 'error', duration: 2000, isClosable: true });
          setSwapMode(false);
          setSwapSourceMeal(null);
          return;
        }
        
        // CRITICAL FIX: Validate user recipe ID
        if (!swapSourceMeal.id || swapSourceMeal.id === '') {
          throw new Error('User recipe ID is missing. Please try again.');
        }
        
        // CRITICAL FIX: Validate date and mealType
        if (!date || !mealType) {
          throw new Error('Target date and meal type are required.');
        }
        
        // CRITICAL FIX: Fetch meal plan directly from API to ensure we have the latest data
        // This ensures the custom meal is in the meal plan before trying to move it
        // Don't rely on state which might be stale
        // Note: supabase and session are already declared above, so we reuse them
        
        // Fetch meal plan directly from API
        const mealPlanResponse = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
            'Content-Type': 'application/json',
          },
        });
        
        if (!mealPlanResponse.ok) {
          throw new Error('Failed to fetch meal plan');
        }
        
        const freshMealPlan = await mealPlanResponse.json();
        
        // CRITICAL FIX: First, check if this meal was removed from grid (needs recreation)
        // This check must happen BEFORE we try to find it in the meal plan
        const foundRecentlyAddedMeal = recentlyAddedMeals.find(m => {
          const mId = m.id || (m as any).meal_id || (m as any).mealId;
          return String(mId) === String(swapSourceMeal.id);
        });
        
        const mealNotInGrid = foundRecentlyAddedMeal && (foundRecentlyAddedMeal as any)._notInGrid;
        const customMealData = (foundRecentlyAddedMeal as any)?._customMealData;
        const recipeId = (foundRecentlyAddedMeal as any)?.recipe_id || (foundRecentlyAddedMeal as any)?.recipe?.id || customMealData?.recipe_id;
        
        console.log(`🔍 Looking for meal: swapSourceMeal.id=${swapSourceMeal.id}, recentlyAddedMeal=${foundRecentlyAddedMeal ? JSON.stringify({ id: foundRecentlyAddedMeal.id, name: foundRecentlyAddedMeal.meal_name || foundRecentlyAddedMeal.name }) : 'null'}, mealNotInGrid=${mealNotInGrid}, recipeId=${recipeId}`);
        
        // CRITICAL FIX: If meal was removed from grid, skip ID lookup and go straight to recreation
        // Don't try to find it by ID since it doesn't exist in the meal plan anymore
        let actualMealId = swapSourceMeal.id;
        
        // CRITICAL FIX: If meal was removed from grid OR if it's a custom meal not in the plan, skip lookup
        // Check if meal is in recentlyAddedMeals but not in the meal plan (was removed)
        const mealInPlanById = freshMealPlan && freshMealPlan.meals ? freshMealPlan.meals.find((m: any) => {
          const mId = m.id || m.meal_id || m.mealId;
          return String(mId) === String(swapSourceMeal.id);
        }) : null;
        
        // If meal was removed from grid OR not found in meal plan but is in recentlyAddedMeals, skip lookup
        const shouldRecreate = mealNotInGrid || (!mealInPlanById && foundRecentlyAddedMeal);
        
        if (shouldRecreate) {
          // Meal was removed from grid or not in meal plan - skip ID lookup, will recreate it
          console.log(`ℹ️ Meal was removed from grid or not in meal plan, will recreate it (skipping ID lookup). mealNotInGrid=${mealNotInGrid}, mealInPlanById=${!!mealInPlanById}, foundRecentlyAddedMeal=${!!foundRecentlyAddedMeal}`);
        } else if (freshMealPlan && freshMealPlan.meals) {
          // CRITICAL FIX: Only try to find meal in meal plan if it wasn't removed from grid
          // If it was removed, we'll recreate it later
          console.log(`📋 Meal plan has ${freshMealPlan.meals.length} meals`);
          
          // Try to find by ID first
          const mealInPlan = freshMealPlan.meals.find((m: any) => {
            const mId = m.id || m.meal_id || m.mealId;
            const match = String(mId) === String(swapSourceMeal.id);
            if (match) {
              console.log(`✅ Found meal by ID: ${mId} === ${swapSourceMeal.id}`);
            }
            return match;
          });
          
          if (mealInPlan) {
            // Use the ID from the meal plan (more reliable)
            const mealInPlanAny = mealInPlan as any;
            actualMealId = String(mealInPlanAny.id || mealInPlanAny.meal_id || mealInPlanAny.mealId);
            console.log(`✅ Found meal in plan: ${actualMealId}`);
          } else {
            // Meal not found by ID - try to find by name (fallback)
            console.log(`⚠️ Meal not found by ID, trying to find by name...`);
            
            // Try with foundRecentlyAddedMeal if available
            if (foundRecentlyAddedMeal) {
              const targetName = foundRecentlyAddedMeal.meal_name || foundRecentlyAddedMeal.name;
              console.log(`🔍 Looking for meal by name: "${targetName}"`);
              
              const mealByName = freshMealPlan.meals.find((m: any) => {
                const mealName = m.meal_name || m.name || (m as any).mealName;
                const match = mealName === targetName;
                if (match) {
                  console.log(`✅ Found meal by name: "${mealName}" === "${targetName}"`);
                }
                return match;
              });
              
              if (mealByName) {
                const mealByNameAny = mealByName as any;
                actualMealId = String(mealByNameAny.id || mealByNameAny.meal_id || mealByNameAny.mealId);
                console.log(`✅ Found meal by name: ${actualMealId}`);
              } else {
                // Try case-insensitive match
                const mealByCaseInsensitiveName = freshMealPlan.meals.find((m: any) => {
                  const mealName = (m.meal_name || m.name || (m as any).mealName || '').toLowerCase();
                  const targetNameLower = (targetName || '').toLowerCase();
                  return mealName === targetNameLower;
                });
                
                if (mealByCaseInsensitiveName) {
                  const mealByNameAny = mealByCaseInsensitiveName as any;
                  actualMealId = String(mealByNameAny.id || mealByNameAny.meal_id || mealByNameAny.mealId);
                  console.log(`✅ Found meal by case-insensitive name: ${actualMealId}`);
                } else {
                  // Meal not found - but if it was removed from grid, that's OK
                  if (!mealNotInGrid) {
                    // Only throw error if meal wasn't removed from grid
                    console.error(`❌ Meal not found in meal plan. Looking for:`, {
                      id: swapSourceMeal.id,
                      name: targetName
                    });
                    const availableMeals = freshMealPlan.meals.map((m: any) => ({
                      id: m.id || m.meal_id || m.mealId,
                      name: m.meal_name || m.name || (m as any).mealName
                    }));
                    console.error(`❌ Available meals (${availableMeals.length}):`, availableMeals);
                    console.error(`❌ Available meal IDs:`, availableMeals.map((m: any) => m.id));
                    console.error(`❌ Looking for ID: "${swapSourceMeal.id}" (type: ${typeof swapSourceMeal.id})`);
                    throw new Error(`Meal not found in meal plan. Please try adding the meal again.`);
                  } else {
                    console.log(`ℹ️ Meal was removed from grid, will recreate it: id=${swapSourceMeal.id}`);
                  }
                }
              }
            } else {
              // No recentlyAddedMeal to search by name
              // CRITICAL FIX: If meal not found but we have swapSourceMeal.id, use it anyway
              // The meal was created successfully, so we can trust the ID
              // This handles the case where the meal was just created and might not be in the meal plan yet
              console.warn(`⚠️ Meal not found in meal plan, but using provided ID: ${swapSourceMeal.id}`);
              console.warn(`⚠️ This might be a timing issue - the meal will be in the meal plan soon`);
              actualMealId = swapSourceMeal.id;
              console.log(`✅ Using swapSourceMeal.id: ${actualMealId}`);
            }
          }
        } else {
          // CRITICAL FIX: If meal plan has no meals but we have swapSourceMeal.id, use it anyway
          if (swapSourceMeal.id) {
            console.warn(`⚠️ Meal plan has no meals, but using provided ID: ${swapSourceMeal.id}`);
            actualMealId = swapSourceMeal.id;
            console.log(`✅ Using swapSourceMeal.id: ${actualMealId}`);
          } else {
            throw new Error('Meal plan has no meals. Please try adding the meal again.');
          }
        }
        
        // CRITICAL FIX: Check if meal was removed from grid (not in meal plan)
        // If so, we need to recreate it first before moving it
        // Note: We already checked mealNotInGrid and customMealData above, so we can use those values
        if (shouldRecreate) {
          // CRITICAL FIX: Meal was removed from grid, recreate it first
          console.log(`🔄 Meal was removed from grid, recreating it first`);
          
          // Step 1: Delete the AI recipe in the grid slot (if it exists)
          if (mealId && mealId !== '') {
            const deleteResponse = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/meals/${mealId}`, {
              method: 'DELETE',
              headers: {
                'Authorization': `Bearer ${session.access_token}`,
                'Content-Type': 'application/json',
              },
            });
            
            if (!deleteResponse.ok && deleteResponse.status !== 404) {
              const errorData = await deleteResponse.json().catch(() => ({ detail: 'Failed to delete meal' }));
              throw new Error(errorData.detail || 'Failed to delete meal');
            }
          }
          
          // Step 2: Recreate the meal using recipe_id if available, otherwise use custom meal data
          if (recipeId && customMealData) {
            // CRITICAL FIX: Use recipe endpoint if we have a recipe_id
            console.log(`🔄 Recreating meal using recipe_id: ${recipeId}`);
            
            const addRecipeUrl = `http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/meals`;
            const addRecipeData = {
              recipe_id: recipeId,
              meal_date: date,
              meal_type: mealType
            };
            
            const addRecipeResponse = await fetch(addRecipeUrl, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${session.access_token}`,
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(addRecipeData),
            });
            
            if (!addRecipeResponse.ok) {
              const errorData = await addRecipeResponse.json().catch(() => ({ detail: 'Failed to add recipe' }));
              throw new Error(errorData.detail || 'Failed to add recipe');
            }
            
            const addRecipeResult = await addRecipeResponse.json();
            const newMealId = addRecipeResult.meal?.id || addRecipeResult.meal_id || addRecipeResult.id;
            
            if (!newMealId) {
              throw new Error('Failed to get meal ID after adding recipe');
            }
            
            console.log(`✅ Meal recreated using recipe: newId=${newMealId}`);
            
            // Update the meal ID in the recently added meals list
            setRecentlyAddedMeals(prev => prev.map(m => {
              const mId = m.id || (m as any).meal_id || (m as any).mealId;
              if (String(mId) === String(swapSourceMeal.id)) {
                return {
                  ...m,
                  id: String(newMealId),
                  _notInGrid: false // Mark as in grid now
                };
              }
              return m;
            }));
            
            // Reload meal plan and exit
            await loadMealPlan();
            setSwapMode(false);
            setSwapSourceMeal(null);
            toast({
              title: 'Meal added successfully',
              description: 'Custom meal has been added to the grid',
              status: 'success',
              duration: 3000,
              isClosable: true
            });
            return;
          } else if (customMealData) {
            // Fallback: Recreate using custom meal endpoint
            console.log(`🔄 Recreating meal using custom meal data`);
            
            const recreateUrl = `http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/custom-meal`;
            const recreateData = {
              ...customMealData,
              meal_date: date, // Use target date
              meal_type: mealType // Use target meal type
            };
            
            const recreateResponse = await fetch(recreateUrl, {
              method: 'POST',
              headers: {
                'Authorization': `Bearer ${session.access_token}`,
                'Content-Type': 'application/json',
              },
              body: JSON.stringify(recreateData),
            });
            
            if (!recreateResponse.ok) {
              const errorData = await recreateResponse.json().catch(() => ({ detail: 'Failed to recreate meal' }));
              throw new Error(errorData.detail || 'Failed to recreate meal');
            }
            
            const recreateResult = await recreateResponse.json();
            const newMealId = recreateResult.meal_id || recreateResult.meal?.id || recreateResult.id;
            
            if (!newMealId) {
              throw new Error('Failed to get meal ID after recreation');
            }
            
            console.log(`✅ Meal recreated: newId=${newMealId}`);
            
            // Update the meal ID in the recently added meals list
            setRecentlyAddedMeals(prev => prev.map(m => {
              const mId = m.id || (m as any).meal_id || (m as any).mealId;
              if (String(mId) === String(swapSourceMeal.id)) {
                return {
                  ...m,
                  id: String(newMealId),
                  _notInGrid: false // Mark as in grid now
                };
              }
              return m;
            }));
            
            // Reload meal plan and exit
            await loadMealPlan();
            setSwapMode(false);
            setSwapSourceMeal(null);
            toast({
              title: 'Meal added successfully',
              description: 'Custom meal has been added to the grid',
              status: 'success',
              duration: 3000,
              isClosable: true
            });
            return;
          } else {
            throw new Error('Cannot recreate meal: missing custom meal data');
          }
        }
        
        // CRITICAL FIX: Ensure meal ID is a valid integer (only if meal is in grid)
        const mealIdInt = parseInt(actualMealId, 10);
        if (isNaN(mealIdInt)) {
          throw new Error(`Invalid meal ID: ${actualMealId}. Please try adding the meal again.`);
        }
        actualMealId = String(mealIdInt);
        
        console.log(`🔄 Replacing meal: userRecipeId=${actualMealId}, targetDate=${date}, targetMealType=${mealType}, existingMealId=${mealId || 'none'}`);
        
        // Step 1: Delete the AI recipe in the grid slot (if it exists)
        if (mealId && mealId !== '') {
          const deleteResponse = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/meals/${mealId}`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${session.access_token}`,
              'Content-Type': 'application/json',
            },
          });
          
          if (!deleteResponse.ok && deleteResponse.status !== 404) {
            const errorData = await deleteResponse.json().catch(() => ({ detail: 'Failed to delete meal' }));
            throw new Error(errorData.detail || 'Failed to delete meal');
          }
        }
        
        // Step 2: Move user recipe to the grid slot
        const moveUrl = `http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/meals/${actualMealId}/move?target_date=${date}&target_meal_type=${mealType}`;
        console.log(`🔄 Moving meal to: ${moveUrl}`);
        
        const moveResponse = await fetch(moveUrl, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
            'Content-Type': 'application/json',
          },
        });
        
        if (moveResponse.ok) {
          await moveResponse.json(); // Response not needed, just check if successful
          toast({
            title: 'Meal replaced successfully',
            description: `Your custom recipe has replaced the meal in ${mealType}`,
            status: 'success',
            duration: 3000,
            isClosable: true
          });
          
          // CRITICAL FIX: Keep the recently added meal in the list - don't clear it
          // The user wants to see it in "recently added meals" even after swapping to grid
          // Only clear it when explicitly dismissed or deleted
          
          // CRITICAL FIX: Exit swap mode BEFORE reloading to prevent state conflicts
          setSwapMode(false);
          setSwapSourceMeal(null);
          
          // Reload meal plan to reflect changes (after swap mode is cleared)
          await loadMealPlan();
          
          // CRITICAL FIX: Notify dashboard to reload
          window.dispatchEvent(new CustomEvent('mealPlanUpdated'));
        } else {
          const errorData = await moveResponse.json().catch(() => ({ detail: 'Failed to move meal' }));
          const errorMessage = errorData.detail || errorData.message || 'Failed to move meal';
          console.error(`❌ Move failed: ${errorMessage}`, errorData);
          throw new Error(errorMessage);
        }
      } catch (error) {
        console.error('Error replacing meal:', error);
        toast({
          title: 'Failed to replace meal',
          description: (error as Error).message,
          status: 'error',
          duration: 3000,
          isClosable: true
        });
        setSwapMode(false);
        setSwapSourceMeal(null);
      }
      return;
    }
    
    // Normal swap: perform swap via API
    // CRITICAL FIX: Require mealId for normal swap (not user recipe replacement)
    if (!mealId) {
      toast({ 
        title: 'Cannot swap', 
        description: 'Please select a meal to swap with', 
        status: 'warning', 
        duration: 2000, 
        isClosable: true 
      });
      return;
    }
    
    try {
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        toast({ title: 'Please log in', status: 'error', duration: 2000, isClosable: true });
        setSwapMode(false);
        setSwapSourceMeal(null);
        return;
      }
      
      const response = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/meals/swap`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify({
          meal_id_1: parseInt(swapSourceMeal.id),
          meal_id_2: parseInt(mealId)
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        toast({
          title: 'Meals swapped successfully',
          description: `${result.meal_1.meal_name} ↔ ${result.meal_2.meal_name}`,
          status: 'success',
          duration: 3000,
          isClosable: true
        });
        
        // CRITICAL FIX: Exit swap mode BEFORE reloading to prevent state conflicts
        setSwapMode(false);
        setSwapSourceMeal(null);
        
        // Reload meal plan to reflect changes (after swap mode is cleared)
        await loadMealPlan();
        
        // CRITICAL FIX: Notify dashboard to reload
        window.dispatchEvent(new CustomEvent('mealPlanUpdated'));
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to swap meals' }));
        throw new Error(errorData.detail || 'Swap failed');
      }
    } catch (error) {
      console.error('Error swapping meals:', error);
      toast({
        title: 'Failed to swap meals',
        description: (error as Error).message,
        status: 'error',
        duration: 3000,
        isClosable: true
      });
      setSwapMode(false);
      setSwapSourceMeal(null);
    }
  };

  const loadAlternatives = async (mealType: string) => {
    if (!mealPlan?.id) return;
    
    setLoadingAlternatives((prev: {[key: string]: boolean}) => ({ ...prev, [mealType]: true }));
    
    try {
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        setError('Please log in to load alternatives');
        toast({ title: 'Please log in', status: 'warning', duration: 2500, isClosable: true });
        return;
      }

      // Open the modal immediately for better UX; it will populate once data arrives
      setAltMealType(mealType);
      setAltSearch('');
      onAltOpen();

      // Serve from cache if fresh
      const cached = getCachedAlternatives(mealType);
      if (cached) {
        setAlternatives(prev => ({ ...prev, [mealType]: cached }));
        return;
      }
      
      // Abort any in-flight request for this meal type
      if (controllersRef.current[mealType]) controllersRef.current[mealType]!.abort();
      const controller = new AbortController();
      controllersRef.current[mealType] = controller;
      const response = await fetch(
        `http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/alternatives/${mealType}?count=3`,
        {
          headers: { Authorization: `Bearer ${session.access_token}` },
          signal: controller.signal
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        setAlternatives(prev => ({ ...prev, [mealType]: data.alternatives }));
        alternativesCacheRef.current[mealType] = { items: data.alternatives, ts: Date.now() };
      }
    } catch (err: any) {
      // Ignore intentional aborts
      if (err?.name === 'AbortError') {
        return;
      }
      console.error('Error loading alternatives:', err);
      toast({ title: 'Failed to load alternatives', status: 'error', duration: 3000, isClosable: true });
    } finally {
      setLoadingAlternatives((prev: {[key: string]: boolean}) => ({ ...prev, [mealType]: false }));
    }
  };

  const onAltClose = () => {
    // Clear state so late responses won't trigger reopen visuals
    if (altMealType) {
      setAlternatives(prev => ({ ...prev, [altMealType]: prev[altMealType] || [] }));
      // Abort any in-flight fetch for the modal we're closing
      if (controllersRef.current[altMealType]) controllersRef.current[altMealType]!.abort();
    }
    setAltMealType(null);
    setAltSearch('');
    _onAltClose();
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
    onAltClose();
    toast({ title: 'Meal replaced', status: 'success', duration: 2000, isClosable: true });
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
      const { supabase } = await import('../../lib/supabase.ts');
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

  const moveMealToDate = async (mealId: string | number | undefined, targetDate: string, targetMealType?: string) => {
    if (!mealPlan) return;
    if (!mealId) {
      toast({ title: 'Meal ID is missing', status: 'error', duration: 2500, isClosable: true });
      return;
    }
    try {
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.access_token) return;
      const params = new URLSearchParams({ target_date: targetDate });
      if (targetMealType) params.set('target_meal_type', targetMealType);
      const resp = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/meals/${mealId}/move?${params.toString()}`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${session.access_token}` }
      });
      if (resp.ok) {
        const responseData = await resp.json().catch(() => ({}));
        // CRITICAL FIX: Reload meal plan to get updated data BEFORE showing toast
        await loadMealPlan();
        // CRITICAL FIX: Notify dashboard to reload
        window.dispatchEvent(new CustomEvent('mealPlanUpdated'));
        // Check if it was a swap (has source_meal and target_meal) or just a move
        if (responseData.source_meal && responseData.target_meal) {
          toast({ 
            title: 'Meals swapped successfully', 
            description: `${responseData.source_meal.meal_name} ↔ ${responseData.target_meal.meal_name}`,
            status: 'success', 
            duration: 2000, 
            isClosable: true 
          });
        } else {
          toast({ title: 'Meal moved successfully', status: 'success', duration: 1500, isClosable: true });
        }
      } else {
        const errorData = await resp.json().catch(() => ({ detail: 'Failed to move meal' }));
        toast({ title: 'Failed to move meal', description: errorData.detail || 'Unknown error', status: 'error', duration: 2500, isClosable: true });
      }
    } catch (e) {
      console.error('moveMealToDate error', e);
      toast({ title: 'Error moving meal', description: (e as Error).message, status: 'error', duration: 2500, isClosable: true });
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
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        setError('Please log in to add custom meals');
        return;
      }
      
      // Determine if we're creating or updating
      const isEditing = editingMealId !== null;
      const url = isEditing 
        ? `http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/custom-meal/${editingMealId}`
        : `http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/custom-meal`;
      
      // CRITICAL FIX: Add meal_date to custom meal data if not present
      const mealDataWithDate = {
        ...customMealData,
        meal_date: customMealData.meal_date || customMealData.date || selectedDate
      };
      
      // Save custom meal to backend (POST for create, PUT for update)
      const response = await fetch(url, {
        method: isEditing ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify(mealDataWithDate)
      });
      
      if (response.ok) {
        const result = await response.json();
        
        // CRITICAL FIX: Get the actual meal ID from the backend response FIRST
        // Backend returns: { "meal_id": ..., "meal": { "id": ... } }
        const backendMealId = result.meal_id || result.meal?.id || result.id;
        if (!backendMealId) {
          throw new Error('Failed to get meal ID from backend response');
        }
        
        console.log(`✅ Custom meal created: backendMealId=${backendMealId}, name='${customMealData.meal_name}'`);
        
        // CRITICAL FIX: Fetch meal plan directly from API to ensure we have the latest data
        // Don't rely on state which might be stale
        const mealPlanResponse = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
            'Content-Type': 'application/json',
          },
        });
        
        if (!mealPlanResponse.ok) {
          throw new Error('Failed to fetch meal plan after creating custom meal');
        }
        
        const freshMealPlan = await mealPlanResponse.json();
        console.log(`📋 Fetched fresh meal plan with ${freshMealPlan.meals?.length || 0} meals`);
        
        // CRITICAL FIX: Find the meal in the fresh meal plan to ensure we have the correct ID
        // The meal might have been assigned to a different slot by the backend
        let actualMeal: any = null;
        if (freshMealPlan && freshMealPlan.meals) {
          actualMeal = freshMealPlan.meals.find((m: any) => {
            const mId = m.id || m.meal_id || m.mealId;
            return String(mId) === String(backendMealId);
          });
          
          if (actualMeal) {
            console.log(`✅ Found meal in fresh meal plan: id=${actualMeal.id || actualMeal.meal_id || actualMeal.mealId}`);
          } else {
            console.warn(`⚠️ Meal not found by ID in fresh meal plan, trying by name...`);
          }
        }
        
        // If meal not found by ID, try to find by name (fallback)
        if (!actualMeal && freshMealPlan && freshMealPlan.meals) {
          actualMeal = freshMealPlan.meals.find((m: any) => {
            const mealName = m.meal_name || m.name || (m as any).mealName;
            return mealName === customMealData.meal_name;
          });
          
          if (actualMeal) {
            console.log(`✅ Found meal by name in fresh meal plan: id=${actualMeal.id || actualMeal.meal_id || actualMeal.mealId}`);
          }
        }
        
        // CRITICAL FIX: If meal not found in meal plan, use backend response
        // The meal was created successfully, so we can trust the backend response
        // The meal will be in the meal plan, it might just not be in the response yet
        let mealId: string | number;
        let mealDate: string;
        let mealType: string;
        
        if (actualMeal) {
          // Use the actual meal from the meal plan (most reliable)
          mealId = actualMeal.id || actualMeal.meal_id || actualMeal.mealId;
          mealDate = actualMeal.meal_date || actualMeal.date || (result.meal_date || result.meal?.meal_date || selectedDate);
          mealType = actualMeal.meal_type || actualMeal.type || (result.meal_type || result.meal?.meal_type || customMealData.meal_type);
          console.log(`✅ Using meal from meal plan: id=${mealId}`);
        } else {
          // CRITICAL FIX: If meal not found, use backend response
          // The backend created the meal successfully, so we can trust the response
          console.warn(`⚠️ Meal not found in meal plan immediately, using backend response ID: ${backendMealId}`);
          mealId = backendMealId;
          mealDate = result.meal_date || result.meal?.meal_date || selectedDate;
          mealType = result.meal_type || result.meal?.meal_type || customMealData.meal_type;
          console.log(`✅ Using backend response: id=${mealId}, date=${mealDate}, type=${mealType}`);
        }
        
        // CRITICAL FIX: Reload meal plan state to update UI
        await loadMealPlan();
        
        // Create a new meal object from the custom meal data
        // CRITICAL: Use the actual meal ID from the meal plan (not backend response)
        const newMeal: Meal & { meal_date?: string; date?: string } = {
          id: String(mealId), // CRITICAL: Use ID from actual meal in meal plan
          meal_name: customMealData.meal_name,
          meal_type: mealType as 'breakfast' | 'lunch' | 'dinner' | 'snack',
          meal_date: mealDate, // CRITICAL: Use actual date from meal plan
          date: mealDate, // CRITICAL: Use actual date from meal plan
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
        
        console.log(`✅ Custom meal created: id=${newMeal.id}, name='${newMeal.meal_name}', date=${newMeal.meal_date}, type=${newMeal.meal_type}`);
        
        // CRITICAL FIX: Remove the meal from the grid immediately after creation
        // The backend automatically adds it to the meal plan, but we want it only in "My Custom Meals"
        // We'll delete it from the meal plan but keep all the meal data for later use
        let mealRemovedFromGrid = false;
        try {
          const deleteResponse = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/meals/${mealId}`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${session.access_token}`,
              'Content-Type': 'application/json',
            },
          });
          
          if (deleteResponse.ok || deleteResponse.status === 404) {
            mealRemovedFromGrid = true;
            console.log(`✅ Removed meal from grid (keeping in My Custom Meals): id=${mealId}`);
          } else {
            console.warn(`⚠️ Failed to remove meal from grid: ${deleteResponse.status}`);
            // Continue anyway - the meal will be in the grid but also in My Custom Meals
          }
        } catch (deleteErr) {
          console.warn('⚠️ Error removing meal from grid:', deleteErr);
          // Continue anyway - the meal will be in the grid but also in My Custom Meals
        }
        
        // CRITICAL FIX: Store the full meal data (not just ID) in case we need to recreate it
        // Add a flag to indicate this meal is not in the grid yet
        // Also store recipe_id if available from the backend response
        const backendRecipeId = result.recipe_id || result.meal?.recipe_id || result.recipe?.id;
        
        const mealForStorage: Meal & { meal_date?: string; date?: string; _customMealData?: any; _notInGrid?: boolean; recipe_id?: string } = {
          ...newMeal,
          id: String(backendMealId || newMeal.id), // Use backend meal ID if available
          _customMealData: customMealData, // Store full custom meal data for recreation
          _notInGrid: mealRemovedFromGrid, // Flag to indicate if meal was removed from grid
          recipe_id: backendRecipeId // Store recipe_id for easy recreation
        };
        
        // CRITICAL FIX: Add the meal to the persistent list of recently added meals
        // Check if meal already exists (by ID or name) to avoid duplicates
        setRecentlyAddedMeals(prev => {
          const existingIndex = prev.findIndex(m => {
            const mId = m.id || (m as any).meal_id || (m as any).mealId;
            const mName = m.meal_name || m.name || (m as any).mealName;
            return String(mId) === String(mealId) || mName === customMealData.meal_name;
          });
          
          if (existingIndex >= 0) {
            // Update existing meal
            const updated = [...prev];
            updated[existingIndex] = mealForStorage;
            return updated;
          } else {
            // Add new meal to the list
            return [...prev, mealForStorage];
          }
        });
        
        // CRITICAL FIX: Reload meal plan AFTER removing the meal from grid
        // This ensures the grid doesn't show the meal
        await loadMealPlan();
        
        // Clear editing state
        const wasEditing = editingMealId !== null;
        setEditingMealId(null);
        setEditingMealData(null);
        onCustomMealClose();
        
        toast({
          title: wasEditing ? 'Custom meal updated!' : 'Custom meal added!',
          description: wasEditing 
            ? 'Your custom meal has been updated in the meal plan.'
            : 'Your custom meal has been added to the meal plan.',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        
        console.log(`✅ Custom meal ${wasEditing ? 'updated' : 'added'} successfully`);
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
      const { supabase } = await import('../../lib/supabase.ts');
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
        toast({ title: 'Meal regenerated', status: 'success', duration: 2000, isClosable: true });
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
      const { supabase } = await import('../../lib/supabase.ts');
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
        toast({ title: `${mealType} regenerated`, status: 'success', duration: 2000, isClosable: true });
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
    
    setLoading(true);
    setError(null);
    setStreamingProgress(null);
    setGeneratingMeals(new Set());
    
    try {
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.access_token) {
        setError('Please log in to regenerate meal plan');
        return;
      }
      
      // Use streaming endpoint for progressive updates
      const response = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/regenerate-streaming`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      });
      
      if (!response.ok) {
        // Fallback to non-streaming endpoint if not found
        if (response.status === 404) {
          const fallback = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/regenerate-entire`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${session.access_token}` }
          });
          if (fallback.ok) {
            const result = await fallback.json();
            setMealPlan(prev => {
              if (!prev) return null;
              return {
                ...prev,
                meals: prev.meals.map(meal => {
                  const regenerated = result.regenerated_meals?.find((rm: any) => rm.id === meal.id);
                  return regenerated ? {
                    ...meal,
                    meal_name: regenerated.meal_name,
                    calories: regenerated.calories,
                    protein: regenerated.protein,
                    carbs: regenerated.carbs,
                    fats: regenerated.fats,
                    cuisine: regenerated.cuisine
                  } : meal;
                })
              };
            });
            toast({ title: 'Plan regenerated', status: 'success', duration: 2000, isClosable: true });
            
            // CRITICAL FIX: Reload meal plan from database after regeneration
            if (mealPlan?.id) {
              try {
                const reloadResponse = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}`, {
                  method: 'GET',
                  headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${session.access_token}`
                  }
                });
                
                if (reloadResponse.ok) {
                  const reloadedPlan = await reloadResponse.json();
                  console.log('Reloaded meal plan after regeneration (fallback):', reloadedPlan);
                  console.log('Reloaded meals count:', reloadedPlan.meals?.length || 0);
                  
                  // Force state update
                  setMealPlan(null);
                  await new Promise(resolve => setTimeout(resolve, 0));
                  setMealPlan(reloadedPlan);
                  return; // Done via fallback
                }
              } catch (reloadErr) {
                console.error('Error reloading meal plan after regeneration (fallback):', reloadErr);
              }
            }
            
            return; // Done via fallback
          }
        }
        throw new Error('Failed to start streaming regeneration');
      }
      
      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('Streaming not supported');
      }
      
      const decoder = new TextDecoder();
      let buffer = '';
      let iterationCount = 0;
      const MAX_ITERATIONS = 1000; // Safety limit to prevent infinite loops
      let completed = false;
      
      while (!completed && iterationCount < MAX_ITERATIONS) {
        iterationCount++;
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              
              if (data.type === 'completion') {
                completed = true;
              }
              
              if (data.type === 'meal_update') {
                // Update the specific meal in real-time
                setMealPlan(prev => {
                  if (!prev) return null;
                  const updatedMeals = [...prev.meals];
                  const mealIndex = updatedMeals.findIndex(m => m.id === data.meal_id);
                  
                  if (mealIndex !== -1) {
                    updatedMeals[mealIndex] = {
                      ...updatedMeals[mealIndex],
                      meal_name: data.meal_name,
                      calories: data.calories,
                      protein: data.protein,
                      carbs: data.carbs,
                      fats: data.fats,
                      cuisine: data.cuisine,
                      recipe: data.recipe
                    };
                  }
                  
                  return { ...prev, meals: updatedMeals };
                });
                
                // Update progress
                setStreamingProgress(data.progress);
                
                // Remove from generating set
                setGeneratingMeals(prev => {
                  const newSet = new Set(prev);
                  newSet.delete(data.meal_id);
                  return newSet;
                });
                
                // Suppress per-meal toasts; progress is shown via streamingProgress banner
              } else if (data.type === 'meal_error') {
                console.error(`Error generating meal ${data.meal_id}:`, data.error);
                setGeneratingMeals(prev => {
                  const newSet = new Set(prev);
                  newSet.delete(data.meal_id);
                  return newSet;
                });
              } else if (data.type === 'completion' || data.type === 'complete') {
                completed = true;
                setStreamingProgress(null);
                toast({ title: 'All meals regenerated!', status: 'success', duration: 2000, isClosable: true });
                
                // CRITICAL FIX: Reload meal plan from database after regeneration completes
                // This ensures we have the latest state with all meals properly saved
                if (mealPlan?.id) {
                  try {
                    const reloadResponse = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}`, {
                      method: 'GET',
                      headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${session.access_token}`
                      }
                    });
                    
                    if (reloadResponse.ok) {
                      const reloadedPlan = await reloadResponse.json();
                      console.log('Reloaded meal plan after regeneration:', reloadedPlan);
                      console.log('Reloaded meals count:', reloadedPlan.meals?.length || 0);
                      
                      // Force state update
                      setMealPlan(null);
                      await new Promise(resolve => setTimeout(resolve, 0));
                      setMealPlan(reloadedPlan);
                    }
                  } catch (reloadErr) {
                    console.error('Error reloading meal plan after regeneration:', reloadErr);
                  }
                }
              }
            } catch (e) {
              console.error('Error parsing streaming data:', e);
            }
          }
        }
      }
      
      // Safety check - if we hit max iterations, break and reload
      if (iterationCount >= MAX_ITERATIONS && !completed) {
        console.warn('Stream reached max iterations, forcing completion');
        setStreamingProgress(null);
        
        // Reload meal plan
        if (mealPlan?.id) {
          try {
            const reloadResponse = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}`, {
              method: 'GET',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${session.access_token}`
              }
            });
            if (reloadResponse.ok) {
              const reloadedPlan = await reloadResponse.json();
              setMealPlan(null);
              await new Promise(resolve => setTimeout(resolve, 0));
              setMealPlan(reloadedPlan);
            }
          } catch (err) {
            console.error('Error reloading after max iterations:', err);
          }
        }
      }
      
    } catch (err) {
      console.error('Error in streaming regeneration:', err);
      setError('Failed to regenerate meal plan');
      toast({ title: 'Failed to regenerate meal plan', status: 'error', duration: 3000, isClosable: true });
    } finally {
      setLoading(false);
      setStreamingProgress(null);
      setGeneratingMeals(new Set());
    }
  };

  const generateShoppingListFromMealPlan = async () => {
    if (!mealPlan) return;
    
    try {
      setLoading(true);
      
      // Get Supabase session token for authentication
      const { supabase } = await import('../../lib/supabase.ts');
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
        toast({ title: 'Shopping list generated', status: 'success', duration: 2000, isClosable: true });
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
      const { supabase } = await import('../../lib/supabase.ts');
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
        toast({ title: 'Shopping list generated', status: 'success', duration: 2000, isClosable: true });
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
      const { supabase } = await import('../../lib/supabase.ts');
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
        body: JSON.stringify({
          meal_types: mealTypes,
          list_name: `Shopping List - ${mealTypes.join(', ')}`
        })
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
      const { supabase } = await import('../../lib/supabase.ts');
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
        
        // Update selected recipe if it's the same meal - use result directly
        if (selectedRecipe?.id === mealId) {
          setSelectedRecipe((prev: any) => {
            if (!prev) return null;
            return {
              ...prev,
              calories: result.updated_meal.calories,
              protein: result.updated_meal.protein,
              carbs: result.updated_meal.carbs,
              fats: result.updated_meal.fats,
              servings: result.updated_meal.servings,
              recipe: {
                ...prev.recipe,
                servings: result.updated_meal.servings,
                ingredients: result.adjusted_ingredients,
                nutrition: result.adjusted_nutrition
              },
              // Clear preview since change has been applied
              previewCalories: undefined,
              previewMultiplier: undefined,
              previewProtein: undefined,
              previewCarbs: undefined,
              previewFats: undefined
            } as any;
          });
        }
        
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
      const { supabase } = await import('../../lib/supabase.ts');
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
      const { supabase } = await import('../../lib/supabase.ts');
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
      
      const { supabase } = await import('../../lib/supabase.ts');
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

  const handleLogDayToDailyIntake = async (date: string) => {
    if (!mealPlan) return;
    setLoading(true);
    try {
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.access_token) {
        toast({ title: 'Please log in', status: 'warning', duration: 2500, isClosable: true });
        return;
      }

      // Get meals for this specific day
      const dayMeals = Object.values(gridAssignments[date] || {}).filter(Boolean);
      if (dayMeals.length === 0) {
        toast({ title: 'No meals to log for this day', status: 'warning', duration: 2000, isClosable: true });
        return;
      }

      const response = await fetch(
        `http://localhost:8000/daily-logging/log-from-meal-plan?log_date=${date}&meal_plan_id=${mealPlan.id}`,
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
        toast({ title: `${new Date(date).toLocaleDateString()} logged successfully`, description: `Logged ${result.logged_meals} meals. Goals and daily log will be updated.`, status: 'success', duration: 3000, isClosable: true });
        
        // Trigger a custom event to notify other components to refresh
        window.dispatchEvent(new CustomEvent('dailyLogUpdated', { detail: { date } }));
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        const errorMessage = errorData.detail || `Server error: ${response.status}`;
        console.error('Backend error:', errorMessage);
        throw new Error(errorMessage);
      }
    } catch (err: any) {
      console.error('Error logging day:', err);
      toast({ title: 'Failed to log day', description: err.message, status: 'error', duration: 3000, isClosable: true });
    } finally {
      setLoading(false);
    }
  };
  
  const handleAddToDailyLog = async (recipe: any) => {
    if (!recipe) return;
    setLoading(true);
    try {
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.access_token) {
        toast({ title: 'Please log in', status: 'warning', duration: 2500, isClosable: true });
        return;
      }
      
      const today = new Date().toISOString().split('T')[0];
      const servings = previewServings || recipe.servings || recipe.recipe?.servings || 1;
      
      // Calculate nutrition per serving
      const baseCalories = recipe.per_serving_calories ?? recipe.recipe?.per_serving_calories ?? recipe.calories ?? recipe.nutrition?.calories ?? 0;
      const baseProtein = recipe.per_serving_protein ?? recipe.recipe?.per_serving_protein ?? recipe.protein ?? recipe.nutrition?.protein ?? 0;
      const baseCarbs = recipe.per_serving_carbs ?? recipe.recipe?.per_serving_carbs ?? recipe.carbs ?? recipe.nutrition?.carbs ?? 0;
      const baseFats = recipe.per_serving_fats ?? recipe.per_serving_fat ?? recipe.recipe?.per_serving_fats ?? recipe.recipe?.per_serving_fat ?? recipe.fats ?? recipe.nutrition?.fats ?? 0;
      
      // Scale by servings
      const scaledCalories = Math.round(baseCalories * servings);
      const scaledProtein = Math.round(baseProtein * servings);
      const scaledCarbs = Math.round(baseCarbs * servings);
      const scaledFats = Math.round(baseFats * servings);
      
      // Determine meal type from recipe
      const mealType = recipe.meal_type || recipe.type || recipe.recipe?.meal_type || 'breakfast';
      
      const response = await fetch(
        'http://localhost:8000/daily-logging/log-daily-intake',
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            log_date: today,
            entries: [{
              recipe_id: recipe.id || recipe.recipe_id,
              food_name: recipe.title || recipe.meal_name || recipe.name || 'Recipe',
              quantity: servings,
              unit: 'serving',
              meal_type: mealType,
              calories: scaledCalories,
              protein: scaledProtein,
              carbs: scaledCarbs,
              fats: scaledFats
            }]
          })
        }
      );
      
      if (response.ok) {
        toast({ 
          title: 'Added to Daily Log!', 
          description: `${recipe.title || recipe.meal_name || recipe.name} (${servings} serving${servings !== 1 ? 's' : ''}) added to your daily log.`, 
          status: 'success', 
          duration: 3000, 
          isClosable: true 
        });
        onRecipeClose();
        // Trigger a custom event to notify other components to refresh
        window.dispatchEvent(new CustomEvent('dailyLogUpdated', { detail: { date: today } }));
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to add to daily log' }));
        throw new Error(errorData.detail || 'Failed to add to daily log');
      }
    } catch (err: any) {
      console.error('Error adding to daily log:', err);
      toast({ 
        title: 'Failed to add to daily log', 
        description: err.message || 'Please try again', 
        status: 'error', 
        duration: 3000, 
        isClosable: true 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleFixDailyTotal = async (date: string) => {
    if (!mealPlan) return;
    setLoading(true);
    try {
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.access_token) {
        toast({ title: 'Please log in', status: 'warning', duration: 2500, isClosable: true });
        return;
      }

      const response = await fetch(
        `http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/fix-daily-totals?target_date=${date}`,
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
        toast({ 
          title: 'Daily total adjusted', 
          description: `Meals adjusted to match your daily target (${result.fixed_dates?.length || 1} day(s) fixed)`, 
          status: 'success', 
          duration: 3000, 
          isClosable: true 
        });
        
        // Force reload meal plan to see updated values
        if (mealPlan?.id) {
          const planId = mealPlan.id;
          console.log('🔄 Reloading meal plan after fix:', planId);
          
          // Clear localStorage cache to force fresh fetch
          try {
            localStorage.removeItem('lastMealPlanId');
            localStorage.removeItem('lastMealPlanDate');
            localStorage.removeItem('lastMealPlanType');
          } catch (e) {
            console.warn('Failed to clear localStorage cache:', e);
          }
          
          // Clear the meal plan state to force a fresh fetch
          setMealPlan(null);
          
          // Force reload after a brief delay
          setTimeout(async () => {
            try {
              await loadMealPlan();
              console.log('✅ Meal plan reloaded successfully');
              
              // Also try to refetch directly via API to ensure we have latest data
              const { supabase } = await import('../../lib/supabase.ts');
              const { data: { session } } = await supabase.auth.getSession();
              if (session?.access_token) {
                const response = await fetch(
                  `http://localhost:8000/nutrition/meal-plans/${planId}`,
                  {
                    headers: {
                      'Authorization': `Bearer ${session.access_token}`,
                      'Content-Type': 'application/json'
                    }
                  }
                );
                if (response.ok) {
                  const updatedPlan = await response.json();
                  setMealPlan(updatedPlan);
                  console.log('✅ Force-refetched meal plan from API');
                }
              }
            } catch (error) {
              console.error('❌ Error reloading meal plan:', error);
            }
          }, 300);
        }
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        const errorMessage = errorData.detail || `Server error: ${response.status}`;
        console.error('Backend error:', errorMessage);
        throw new Error(errorMessage);
      }
    } catch (err: any) {
      console.error('Error fixing daily total:', err);
      toast({ 
        title: 'Error fixing daily total', 
        description: err.message || 'Failed to adjust meals to match target', 
        status: 'error', 
        duration: 3000, 
        isClosable: true 
      });
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
          <Spinner size="xl" color="blue.500" />
            <Text fontSize="lg" fontWeight="semibold">Generating your meal plan...</Text>
            <Text fontSize="sm" color="gray.600">Generating your personalized meal plan... This may take 1-2 minutes.</Text>
        </VStack>
      </Center>
    );
  }

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <Box>
          <VStack align="stretch" spacing={4}>
            <HStack justify="space-between">
              <VStack align="start" spacing={1}>
                <Heading size="lg">Meal Planning</Heading>
                <Text color="gray.600">Plan your meals for the week</Text>
              </VStack>
              <HStack spacing={2}>
                {!mealPlan && (
                  <>
                    <Button 
                      colorScheme="blue" 
                      leftIcon={<FiCoffee />}
                      onClick={async () => {
                        await generateMealPlan();
                      }}
                      isLoading={loading}
                    >
                      Create Meal Plan Structure
                    </Button>
                    <Button 
                      colorScheme="purple" 
                      leftIcon={<FiCoffee />}
                      onClick={async () => {
                        // CRITICAL FIX: Generate complete meal plan (not progressive)
                        await generateCompleteMealPlan();
                      }}
                      isLoading={loading}
                      variant="outline"
                    >
                      Generate Full {planType === 'weekly' ? 'Weekly' : 'Daily'} Plan
                    </Button>
                  </>
                )}
                {mealPlan && (
                  <>
                    <Button 
                      colorScheme="purple" 
                      leftIcon={<FiCoffee />}
                      onClick={async () => {
                        // CRITICAL FIX: Generate all meals for existing plan
                        await generateCompleteMealPlan();
                      }}
                      isLoading={loading || isGenerating}
                      variant="outline"
                    >
                      Generate All Meals
                    </Button>
                    <Button 
                      variant="outline" 
                      leftIcon={<FiGitBranch />}
                      onClick={() => setShowVersionHistory(!showVersionHistory)}
                    >
                      Version History
                    </Button>
                  </>
                )}
              </HStack>
            </HStack>

            {/* Plan Type and Date Selection */}
            <HStack spacing={4} wrap="wrap">
              <FormControl maxW="200px">
                <FormLabel fontSize="sm">Plan Type</FormLabel>
                <Select
                  value={planType}
                  onChange={(e: React.ChangeEvent<HTMLSelectElement>) => {
                    const newPlanType = e.target.value as 'daily' | 'weekly';
                    setPlanType(newPlanType);
                    
                    // Show sync feedback
                    toast({
                      title: `Switched to ${newPlanType} view`,
                      description: `All meals are synchronized across both views`,
                      status: 'info',
                      duration: 2000,
                      isClosable: true
                    });
                  }}
                  size="sm"
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                </Select>
              </FormControl>

              <FormControl maxW="200px">
                <FormLabel fontSize="sm">Select Date</FormLabel>
                <Input
                  type="date"
                  value={selectedDate}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSelectedDate(e.target.value)}
                  size="sm"
                />
              </FormControl>

              <FormControl maxW="200px">
                <FormLabel fontSize="sm">Meals per day</FormLabel>
                <Select
                  size="sm"
                  value={mealsPerDay}
                  onChange={async (e: React.ChangeEvent<HTMLSelectElement>) => {
                    const newMealsPerDay = parseInt(e.target.value, 10);
                    setMealsPerDay(newMealsPerDay);
                    // CRITICAL FIX: Also update preferences to persist across navigation
                    try {
                      const { supabase } = await import('../../lib/supabase.ts');
                      const { data: { session } } = await supabase.auth.getSession();
                      if (session?.access_token) {
                        // Update preferences with new meals_per_day
                        const response = await fetch('http://localhost:8000/nutrition/preferences', {
                          method: 'PUT',
                          headers: {
                            'Authorization': `Bearer ${session.access_token}`,
                            'Content-Type': 'application/json'
                          },
                          body: JSON.stringify({
                            meals_per_day: newMealsPerDay
                          })
                        });
                        if (response.ok) {
                          console.log('✅ Updated meals_per_day in preferences:', newMealsPerDay);
                        }
                      }
                    } catch (error) {
                      console.warn('Failed to update meals_per_day in preferences:', error);
                    }
                  }}
                >
                  <option value={3}>3</option>
                  <option value={4}>4</option>
                  <option value={5}>5</option>
                </Select>
              </FormControl>

              {mealPlan && (
                <HStack spacing={2}>
                  <Button 
                    colorScheme="red" 
                    variant="outline"
                    leftIcon={<FiTrash2 />}
                    onClick={async () => {
                      if (!mealPlan) return;
                      if (!window.confirm('Are you sure you want to delete this meal plan? You can then create a new empty structure.')) return;
                      
                      try {
                        setLoading(true);
                        const { supabase } = await import('../../lib/supabase.ts');
                        const { data: { session } } = await supabase.auth.getSession();
                        
                        if (!session?.access_token) {
                          toast({ title: 'Please log in', status: 'warning', duration: 2500, isClosable: true });
                          return;
                        }
                        
                        const response = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}`, {
                          method: 'DELETE',
                          headers: {
                            'Authorization': `Bearer ${session.access_token}`,
                            'Content-Type': 'application/json',
                          },
                        });
                        
                        if (response.ok) {
                          // Clear localStorage
                          localStorage.removeItem('lastMealPlanId');
                          localStorage.removeItem('lastMealPlanDate');
                          localStorage.removeItem('lastMealPlanType');
                          
                          // CRITICAL FIX: Reset localStorage restore ref when resetting meal plan
                          localStorageRestoredRef.current = false;
                          
                          // Clear meal plan
                          setMealPlan(null);
                          toast({ 
                            title: 'Meal plan deleted', 
                            description: 'You can now create a new empty structure', 
                            status: 'success', 
                            duration: 3000, 
                            isClosable: true 
                          });
                        } else {
                          throw new Error('Failed to delete meal plan');
                        }
                      } catch (err: any) {
                        console.error('Error deleting meal plan:', err);
                        toast({ 
                          title: 'Failed to delete meal plan', 
                          description: err.message || 'Please try again', 
                          status: 'error', 
                          duration: 3000, 
                          isClosable: true 
                        });
                      } finally {
                        setLoading(false);
                      }
                    }}
                    isLoading={loading}
                    size="sm"
                  >
                    Reset Meal Plan
                  </Button>
                  <Button 
                    colorScheme="purple" 
                    leftIcon={<FiShoppingCart />}
                    onClick={generateShoppingListFromMealPlan}
                    isLoading={loading}
                    size="sm"
                  >
                    Generate Shopping List
                  </Button>
                </HStack>
              )}
            </HStack>
          </VStack>

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


        </Box>

        {error && (
          <Alert status="error">
            <AlertIcon />
            <Box>
              <AlertTitle>AI Generation Failed</AlertTitle>
              <AlertDescription>
                {error}
                <br />
                <Text mt={2} fontSize="sm">
                  💡 <strong>Tip:</strong> Use the "Recipe Search" feature to find recipes from our database of 500+ quality recipes, or try generating a meal plan again.
                </Text>
              </AlertDescription>
            </Box>
          </Alert>
        )}

        {/* Empty State */}
        {!mealPlan && !loading && (
          <Card bg={cardBg} borderColor={borderColor}>
            <CardBody>
              <VStack spacing={6} py={12}>
                <FiCoffee size={64} color="#CBD5E0" />
                <VStack spacing={2} textAlign="center">
                  <Heading size="md" color="gray.600">No Meal Plan Yet</Heading>
                  <Text color="gray.500" maxW="md">
                    Generate a personalized meal plan based on your preferences and nutritional goals
                  </Text>
                </VStack>
                <VStack spacing={3}>
                  <Text fontSize="sm" color="gray.400">
                    Click "Create Meal Plan Structure" above to get started, then use "Generate Recipe" or "Pick from Database" on each meal slot
                  </Text>
                </VStack>
              </VStack>
            </CardBody>
          </Card>
        )}


        {/* Meal Planning Grid - Show for both weekly and daily plans */}
        {mealPlan && (
          <VStack align="stretch" spacing={6}>
            <Box>
                <HStack justify="space-between" align="center" mb={2}>
                  <Heading size="sm">
                    {planType === 'weekly' ? 'Weekly Planner' : `Daily Planner - ${new Date(selectedDate).toLocaleDateString(undefined, {weekday: 'long', month: 'short', day: 'numeric'})}`}
                  </Heading>
                  <HStack spacing={2} fontSize="sm" color="gray.600">
                    <Text>🔄</Text>
                    <Text>Synced across views</Text>
                  </HStack>
                </HStack>
                
                {/* Sync Info Banner */}
                <Alert status="info" borderRadius="md" mb={4}>
                  <AlertIcon />
                  <Box>
                    <AlertTitle fontSize="sm">Synchronized Planning</AlertTitle>
                    <AlertDescription fontSize="xs">
                      Changes made in {planType === 'weekly' ? 'weekly' : 'daily'} view are automatically synced. 
                      Switch between views to see the same meals across different timeframes.
                    </AlertDescription>
                  </Box>
                </Alert>
                <Box overflowX="auto" borderWidth={1} borderRadius="md" borderColor={borderColor}>
                  <Grid 
                    templateColumns={`150px repeat(${mealTypes.length}, minmax(${mealsPerDay <= 4 ? 220 : mealsPerDay === 5 ? 180 : 160}px, 1fr))`} 
                    gap={0}
                    sx={{
                      // Improve readability for 5+ meals with better spacing
                      '& > *': {
                        fontSize: mealsPerDay > 4 ? 'xs' : 'sm'
                      }
                    }}
                  >
                    {/* Header */}
                    <Box p={mealsPerDay > 4 ? 1.5 : 2} bg="gray.50" borderRightWidth={1} borderBottomWidth={1} borderColor={borderColor}></Box>
                    {mealTypes.map((h, idx) => (
                      <Box 
                        key={`header-${idx}-${h}`} 
                        p={mealsPerDay > 4 ? 1.5 : 2} 
                        bg="gray.50" 
                        borderRightWidth={1} 
                        borderBottomWidth={1} 
                        borderColor={borderColor} 
                        fontWeight="semibold" 
                        textTransform="capitalize"
                        fontSize={mealsPerDay > 4 ? "xs" : "sm"}
                        textAlign="center"
                      >
                        {h.replace('morning snack', 'Morning Snack').replace('afternoon snack', 'Afternoon Snack').replace('evening snack', 'Evening Snack')}
                      </Box>
                    ))}
                    {/* Rows */}
                    {(planType === 'weekly' ? weekDates : [selectedDate]).map(d => {
                      const dayMeals = Object.values(gridAssignments[d] || {}).filter(Boolean);
                      const dayCalories = dayMeals.reduce((sum: number, meal: any) => {
                        // CRITICAL FIX: Backend now returns top-level "calories" field (per-serving)
                        // This should be the primary field to use - it's explicitly set to per-serving calories
                        let c = meal.calories ??  // Top priority - backend's primary per-serving field
                                meal.per_serving_calories ??  // Explicit per-serving field
                                meal.recipe_details?.nutrition?.per_serving_calories ??  // From recipe_details
                                meal.recipe?.per_serving_calories ??  // From recipe object
                                meal.recipe?.nutrition?.per_serving_calories ??  // From recipe.nutrition
                                meal.recipe?.nutrition?.calories ??  // From recipe.nutrition.calories (should be per-serving)
                                meal.recipe?.calories ??  // From recipe.calories
                                0;
                        
                        // Last resort: estimate from ingredients
                        if ((!c || c === 0 || Number.isNaN(Number(c))) && Array.isArray(meal?.recipe?.ingredients)) {
                          const est = estimateNutritionFromIngredients(meal.recipe.ingredients);
                          c = est.calories;
                        }
                        
                        const num = typeof c === 'number' ? c : parseFloat(String(c)) || 0;
                        
                        // CRITICAL DEBUG: Log every meal's calories to track discrepancies
                        if (meal.meal_name) {
                          console.log(`📊 ${d} - ${meal.meal_name}: ${num} cal (calories: ${meal.calories}, per_serving_calories: ${meal.per_serving_calories}, recipe.calories: ${meal.recipe?.calories})`);
                        }
                        
                        return sum + num;
                      }, 0);
                      const isToday = d === new Date().toISOString().split('T')[0];
                      const isSelectedDate = d === selectedDate;
                      return (
                        <React.Fragment key={`row-${d}`}>
                          <Box p={2} borderRightWidth={1} borderBottomWidth={1} borderColor={borderColor} bg={isSelectedDate ? 'blue.50' : isToday ? 'green.50' : undefined} fontWeight="semibold">
                            <VStack spacing={1} align="start">
                              <HStack spacing={1}>
                                <Text fontSize="sm">{new Date(d).toLocaleDateString(undefined,{weekday:'long'})}</Text>
                                {isSelectedDate && planType === 'daily' && <Text fontSize="xs" color="blue.600">📍</Text>}
                                {isToday && <Text fontSize="xs" color="green.600">Today</Text>}
                              </HStack>
                              <Text fontSize="xs" color="gray.600">{new Date(d).toLocaleDateString(undefined,{month:'short', day:'numeric'})}</Text>
                              <HStack spacing={1} align="center">
                                <Text fontSize="xs" color="blue.600" fontWeight="bold">{dayCalories} cal</Text>
                                {preferences?.calorieTarget && dayCalories > 0 && (
                                  <Text fontSize="xs" color="gray.500">
                                    / {preferences.calorieTarget} cal
                                  </Text>
                                )}
                              </HStack>
                              {dayCalories > 0 && preferences?.calorieTarget && Math.abs(dayCalories - preferences.calorieTarget) > 10 && (
                                <Button 
                                  size="xs" 
                                  colorScheme="orange" 
                                  variant="outline" 
                                  onClick={() => handleFixDailyTotal(d)}
                                  isLoading={loading}
                                >
                                  Fix Daily Total
                                </Button>
                              )}
                              {(() => {
                                // Check if day has empty slots
                                const emptySlots = mealTypes.filter((slot, slotIdx) => !gridAssignments[d]?.[slotIdx]);
                                const hasEmptySlots = emptySlots.length > 0;
                                
                                return hasEmptySlots && mealPlan ? (
                                  <Button 
                                    size="xs" 
                                    colorScheme="blue" 
                                    variant="outline" 
                                    onClick={async () => {
                                      if (!mealPlan) return;
                                      
                                      try {
                                        setLoading(true);
                                        const { supabase } = await import('../../lib/supabase.ts');
                                        const { data: { session } } = await supabase.auth.getSession();
                                        
                                        if (!session?.access_token) {
                                          toast({ title: 'Please log in', status: 'warning', duration: 2500, isClosable: true });
                                          return;
                                        }
                                        
                                        // Generate all empty slots for this day
                                        const emptyMealTypes = mealTypes.filter((slot, slotIdx) => !gridAssignments[d]?.[slotIdx]);
                                        
                                        toast({
                                          title: 'Generating meals...',
                                          description: `Generating ${emptyMealTypes.length} meals for ${new Date(d).toLocaleDateString(undefined, {weekday: 'long'})}`,
                                          status: 'info',
                                          duration: 3000,
                                          isClosable: true,
                                        });
                                        
                                        // Generate each empty slot sequentially
                                        for (const mealType of emptyMealTypes) {
                                          await generateMealSlot(d, mealType);
                                          // Small delay between generations to avoid rate limiting
                                          await new Promise(resolve => setTimeout(resolve, 500));
                                        }
                                        
                                        // CRITICAL: Automatically adjust portions to fit nutrition target
                                        if (mealPlan?.id && emptyMealTypes.length > 0) {
                                          try {
                                            const { supabase } = await import('../../lib/supabase.ts');
                                            const { data: { session } } = await supabase.auth.getSession();
                                            
                                            if (session?.access_token) {
                                              // Show adjustment message
                                              toast({
                                                title: 'Adjusting portions...',
                                                description: 'Fitting meals to your nutrition target',
                                                status: 'info',
                                                duration: 2000,
                                                isClosable: true,
                                              });
                                              
                                              // Adjust daily total for this day
                                              const response = await fetch(
                                                `http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/fix-daily-totals?target_date=${d}`,
                                                {
                                                  method: 'POST',
                                                  headers: {
                                                    'Authorization': `Bearer ${session.access_token}`,
                                                  },
                                                }
                                              );
                                              
                                              if (response.ok) {
                                                // Reload meal plan after adjustment
                                                await loadMealPlan();
                                              }
                                            }
                                          } catch (err) {
                                            console.error('Error adjusting daily total:', err);
                                            // Don't fail the whole generation if adjustment fails
                                          }
                                        }
                                        
                                        toast({
                                          title: 'Meals generated!',
                                          description: `Generated ${emptyMealTypes.length} meals for ${new Date(d).toLocaleDateString(undefined, {weekday: 'long'})}. Portions adjusted to fit your nutrition target.`,
                                          status: 'success',
                                          duration: 3000,
                                          isClosable: true,
                                        });
                                        
                                        await loadMealPlan();
                                      } catch (err: any) {
                                        console.error('Error generating day meals:', err);
                                        toast({ 
                                          title: 'Failed to generate meals', 
                                          description: err.message, 
                                          status: 'error', 
                                          duration: 3000, 
                                          isClosable: true 
                                        });
                                      } finally {
                                        setLoading(false);
                                      }
                                    }}
                                    isLoading={loading}
                                  >
                                    Generate Day's Meals
                                  </Button>
                                ) : null;
                              })()}
                              {dayCalories > 0 && (
                                <Button size="xs" colorScheme="green" variant="outline" onClick={() => handleLogDayToDailyIntake(d)}>
                                  Log Day
                                </Button>
                              )}
                              {swapMode && (
                                <Button 
                                  size="xs" 
                                  colorScheme="gray" 
                                  variant="ghost" 
                                  onClick={() => {
                                    setSwapMode(false);
                                    setSwapSourceMeal(null);
                                    toast({
                                      title: 'Swap cancelled',
                                      status: 'info',
                                      duration: 2000,
                                      isClosable: true
                                    });
                                  }}
                                >
                                  Cancel Swap (ESC)
                                </Button>
                              )}
                            </VStack>
                          </Box>
                        {mealTypes.map((slot, slotIdx) => {
                          const cellMeal = gridAssignments[d]?.[slotIdx] || null;
                          // ROOT CAUSE FIX: Don't normalize slot - pass original to generateMealSlot
                          // generateMealSlot will handle normalization internally for the backend
                          // But we need the original (morning snack/afternoon snack) for correct slot assignment
                          return (
                            <Box 
                              key={`${d}-${slotIdx}-${slot}`} 
                              p={mealsPerDay > 4 ? 1 : 1.5} 
                              borderRightWidth={1} 
                              borderBottomWidth={1} 
                              borderColor={swapMode && swapSourceMeal?.id !== (cellMeal?.id || cellMeal?.meal_id || cellMeal?.mealId) && cellMeal ? "orange.300" : swapMode && swapSourceMeal?.id === (cellMeal?.id || cellMeal?.meal_id || cellMeal?.mealId) ? "green.400" : borderColor}
                              borderWidth={swapMode && cellMeal ? 2 : 1}
                              bg={swapMode && swapSourceMeal?.id === (cellMeal?.id || cellMeal?.meal_id || cellMeal?.mealId) ? "green.50" : swapMode && cellMeal ? "orange.50" : undefined}
                              minH={mealsPerDay > 4 ? "180px" : "auto"}
                              transition="all 0.2s"
                            >
                              {cellMeal ? (
                                <VStack align="stretch" spacing={mealsPerDay > 4 ? 1.5 : 2} h="100%" justify="space-between">
                                  <VStack align="stretch" spacing={1}>
                                    <HStack justify="space-between" align="start" spacing={1}>
                                      <Text 
                                        fontSize={mealsPerDay > 4 ? "xs" : "sm"} 
                                        fontWeight="semibold" 
                                        noOfLines={2} 
                                        flex={1}
                                        cursor="pointer"
                                        onClick={() => handleViewRecipe(cellMeal)}
                                        _hover={{ color: "blue.500", textDecoration: "underline" }}
                                      >
                                        {cellMeal.meal_name || cellMeal.name}
                                      </Text>
                                      <HStack spacing={1} align="center">
                                      {generatingMeals.has(`${d}-${slotIdx}-${slot}`) ? (
                                        <Badge size={mealsPerDay > 4 ? "xs" : "sm"} colorScheme="orange" variant="subtle">
                                          <HStack spacing={0.5}>
                                            <Spinner size="xs" />
                                            {mealsPerDay > 4 ? null : <Text fontSize="xs">Generating</Text>}
                                          </HStack>
                                        </Badge>
                                      ) : (
                                        (cellMeal?.ai_generated === true || 
                                         cellMeal?.recipe?.ai_generated === true ||
                                         cellMeal?.recipe_details?.ai_generated === true ||
                                         (Array.isArray(cellMeal?.recipes) && cellMeal.recipes[0]?.ai_generated === true)) ? (
                                          <Badge size={mealsPerDay > 4 ? "xs" : "sm"} colorScheme="purple" variant="subtle" fontSize={mealsPerDay > 4 ? "9px" : "11px"}>AI</Badge>
                                        ) : (
                                          <Badge size={mealsPerDay > 4 ? "xs" : "sm"} colorScheme="green" variant="subtle" fontSize={mealsPerDay > 4 ? "9px" : "11px"}>Recipe</Badge>
                                        )
                                      )}
                                        <Button
                                          size={mealsPerDay > 4 ? "2xs" : "xs"}
                                          variant="ghost"
                                          colorScheme="red"
                                          onClick={async (e: React.MouseEvent) => {
                                            e.stopPropagation();
                                            const mealId = cellMeal?.id || cellMeal?.meal_id || cellMeal?.mealId;
                                            if (!mealId || !mealPlan) return;
                                            
                                            if (!window.confirm(`Are you sure you want to delete "${cellMeal.meal_name || cellMeal.name}"?`)) {
                                              return;
                                            }
                                            
                                            try {
                                              setLoading(true);
                                              const { supabase } = await import('../../lib/supabase.ts');
                                              const { data: { session } } = await supabase.auth.getSession();
                                              
                                              if (!session?.access_token) {
                                                toast({ title: 'Please log in', status: 'warning', duration: 2500, isClosable: true });
                                                return;
                                              }
                                              
                                              const response = await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/meals/${mealId}`, {
                                                method: 'DELETE',
                                                headers: {
                                                  'Authorization': `Bearer ${session.access_token}`,
                                                  'Content-Type': 'application/json',
                                                },
                                              });
                                              
                                              if (response.ok || response.status === 404) {
                                                toast({
                                                  title: 'Meal deleted',
                                                  description: 'The meal has been removed from the grid',
                                                  status: 'success',
                                                  duration: 2000,
                                                  isClosable: true,
                                                });
                                                
                                                // Reload meal plan to reflect changes
                                                await loadMealPlan();
                                                
                                                // Notify dashboard to reload
                                                window.dispatchEvent(new CustomEvent('mealPlanUpdated'));
                                              } else {
                                                const errorData = await response.json().catch(() => ({ detail: 'Failed to delete meal' }));
                                                throw new Error(errorData.detail || 'Failed to delete meal');
                                              }
                                            } catch (err: any) {
                                              console.error('Error deleting meal:', err);
                                              toast({
                                                title: 'Failed to delete meal',
                                                description: err.message || 'Please try again',
                                                status: 'error',
                                                duration: 3000,
                                                isClosable: true,
                                              });
                                            } finally {
                                              setLoading(false);
                                            }
                                          }}
                                          aria-label="Delete meal"
                                          title="Delete this meal from the grid"
                                          p={mealsPerDay > 4 ? 0.5 : 1}
                                          minW="auto"
                                          h="auto"
                                          fontSize={mealsPerDay > 4 ? "12px" : "14px"}
                                          _hover={{ bg: "red.50", color: "red.600" }}
                                        >
                                          ×
                                        </Button>
                                      </HStack>
                                    </HStack>
                                    
                                    {/* CRITICAL: Add nutrition information prominently */}
                                    {/* CRITICAL FIX: Use same priority order as daily total calculation for consistency */}
                                    {(() => {
                                      const calories = Math.round(
                                        cellMeal?.calories ??  // Top priority - backend's primary per-serving field (same as daily total)
                                        cellMeal?.per_serving_calories ??  // Explicit per-serving field
                                        cellMeal?.recipe_details?.nutrition?.per_serving_calories ??  // From recipe_details
                                        cellMeal?.recipe?.per_serving_calories ??  // From recipe object
                                        cellMeal?.recipe?.nutrition?.per_serving_calories ??  // From recipe.nutrition
                                        cellMeal?.recipe?.nutrition?.calories ??  // From recipe.nutrition.calories
                                        cellMeal?.recipe?.calories ??  // From recipe.calories
                                        0
                                      );
                                      const protein = Math.round(cellMeal?.protein ?? cellMeal?.recipe?.nutrition?.protein ?? cellMeal?.recipe_details?.nutrition?.protein ?? 0);
                                      const carbs = Math.round(cellMeal?.carbs ?? cellMeal?.recipe?.nutrition?.carbs ?? cellMeal?.recipe_details?.nutrition?.carbs ?? 0);
                                      const fats = Math.round(cellMeal?.fats ?? cellMeal?.recipe?.nutrition?.fats ?? cellMeal?.recipe_details?.nutrition?.fats ?? 0);
                                      
                                      return (
                                        <Box 
                                          p={mealsPerDay > 4 ? 1 : 1.5} 
                                          bg={mealsPerDay > 4 ? "gray.50" : "blue.50"} 
                                          borderRadius="md"
                                          borderWidth={mealsPerDay > 4 ? 0 : 1}
                                          borderColor="blue.200"
                                        >
                                          <VStack spacing={0.5} align="stretch">
                                            <HStack justify="space-between" align="center">
                                              <Text 
                                                fontSize={mealsPerDay > 4 ? "10px" : "xs"} 
                                                fontWeight="bold" 
                                                color={mealsPerDay > 4 ? "gray.700" : "blue.600"}
                                              >
                                                {calories} cal
                                              </Text>
                                              {(protein > 0 || carbs > 0 || fats > 0) && (
                                                <HStack spacing={mealsPerDay > 4 ? 1 : 2} fontSize={mealsPerDay > 4 ? "9px" : "10px"} color="gray.600">
                                                  {protein > 0 && <Text>P: {protein}g</Text>}
                                                  {carbs > 0 && <Text>C: {carbs}g</Text>}
                                                  {fats > 0 && <Text>F: {fats}g</Text>}
                                                </HStack>
                                              )}
                                            </HStack>
                                          </VStack>
                                        </Box>
                                      );
                                    })()}
                                  </VStack>
                                  
                                  {/* CRITICAL FIX: Add dietary tags to meal cards */}
                                  {(() => {
                                    const dietaryTags = cellMeal?.dietary_tags || 
                                                       cellMeal?.dietaryTags ||
                                                       cellMeal?.recipe?.dietary_tags ||
                                                       cellMeal?.recipe_details?.dietary_tags || [];
                                    
                                    if (Array.isArray(dietaryTags) && dietaryTags.length > 0) {
                                      const maxTags = mealsPerDay > 4 ? 2 : 3;
                                      return (
                                        <HStack spacing={0.5} wrap="wrap" maxW="100%">
                                          {dietaryTags.slice(0, maxTags).map((tag: string) => {
                                            const tagLower = tag.toLowerCase();
                                            let colorScheme = "gray";
                                            
                                            // Color code dietary tags
                                            if (tagLower === 'vegetarian') colorScheme = "green";
                                            else if (tagLower === 'vegan') colorScheme = "teal";
                                            else if (tagLower.includes('peanut') || tagLower.includes('nut-free')) colorScheme = "red";
                                            else if (tagLower.includes('tree-nut')) colorScheme = "orange";
                                            else if (tagLower.includes('nightshade')) colorScheme = "purple";
                                            else if (tagLower.includes('dairy') || tagLower.includes('eggs') || 
                                                     tagLower.includes('gluten') || tagLower.includes('soy') || 
                                                     tagLower.includes('fish') || tagLower.includes('contains-')) colorScheme = "red";
                                            else if (tagLower.includes('sugar') || tagLower.includes('paleo')) colorScheme = "blue";
                                            
                                            return (
                                              <Badge 
                                                key={tag} 
                                                size={mealsPerDay > 4 ? "2xs" : "xs"} 
                                                colorScheme={colorScheme} 
                                                variant="subtle"
                                                noOfLines={1}
                                                fontSize={mealsPerDay > 4 ? "8px" : "9px"}
                                                textTransform="capitalize"
                                                maxW={mealsPerDay > 4 ? "70px" : "100px"}
                                                px={mealsPerDay > 4 ? 1 : 1.5}
                                              >
                                                {tag.replace('contains-', '').replace(/-/g, ' ').substring(0, mealsPerDay > 4 ? 8 : 10)}
                                              </Badge>
                                            );
                                          })}
                                          {dietaryTags.length > maxTags && (
                                            <Text fontSize={mealsPerDay > 4 ? "8px" : "9px"} color="gray.500">+{dietaryTags.length - maxTags}</Text>
                                          )}
                                        </HStack>
                                      );
                                    }
                                    return null;
                                  })()}
                                  
                                  <VStack spacing={mealsPerDay > 4 ? 1 : 1.5} align="stretch" mt="auto">
                                    <HStack spacing={1} wrap="wrap">
                                      <Button 
                                        size={mealsPerDay > 4 ? "2xs" : "xs"} 
                                        onClick={() => handleViewRecipe(cellMeal)} 
                                        variant="outline" 
                                        colorScheme="blue"
                                        flex={1} 
                                        minW={mealsPerDay > 4 ? "50px" : "60px"}
                                        fontSize={mealsPerDay > 4 ? "10px" : "12px"}
                                        title="View full recipe details"
                                      >
                                        View
                                      </Button>
                                      <Button 
                                        size={mealsPerDay > 4 ? "2xs" : "xs"} 
                                        onClick={() => loadAlternatives(slot)}
                                        variant="outline" 
                                        colorScheme="teal"
                                        flex={1} 
                                        minW={mealsPerDay > 4 ? "50px" : "60px"}
                                        fontSize={mealsPerDay > 4 ? "10px" : "12px"}
                                        title="See alternative meal suggestions"
                                      >
                                        Alt
                                      </Button>
                                      <Button 
                                        size={mealsPerDay > 4 ? "2xs" : "xs"} 
                                        onClick={() => {
                                          const mealId = cellMeal?.id || cellMeal?.meal_id || cellMeal?.mealId;
                                          if (mealId) {
                                            handleSimpleSwap(String(mealId), d, slot);
                                          }
                                        }}
                                        variant="outline" 
                                        colorScheme={swapMode && swapSourceMeal?.id === (cellMeal?.id || cellMeal?.meal_id || cellMeal?.mealId) ? "green" : "orange"}
                                        flex={1} 
                                        minW={mealsPerDay > 4 ? "50px" : "60px"}
                                        fontSize={mealsPerDay > 4 ? "10px" : "12px"}
                                        title={swapMode && swapSourceMeal?.id === (cellMeal?.id || cellMeal?.meal_id || cellMeal?.mealId) 
                                          ? "Selected - click another meal to swap" 
                                          : swapMode 
                                          ? "Click to swap with selected meal" 
                                          : "Click to select meal for swapping"}
                                      >
                                        {swapMode && swapSourceMeal?.id === (cellMeal?.id || cellMeal?.meal_id || cellMeal?.mealId) ? "Selected" : "Swap"}
                                      </Button>
                                    </HStack>
                                    {mealsPerDay <= 4 && (
                                      <Menu>
                                        <MenuButton as={Button} size="xs" variant="ghost" width="100%" title="Move this meal to another day">
                                          Move
                                        </MenuButton>
                                        <MenuList>
                                          {weekDates.filter(x=>x!==d).map(x => (
                                            <MenuItem 
                                              key={x} 
                                              onClick={() => {
                                                const mealId = cellMeal?.id || cellMeal?.meal_id || cellMeal?.mealId;
                                                if (!mealId) {
                                                  toast({ 
                                                    title: 'Cannot move meal', 
                                                    description: 'Meal ID not found', 
                                                    status: 'error', 
                                                    duration: 2500, 
                                                    isClosable: true 
                                                  });
                                                  return;
                                                }
                                                moveMealToDate(mealId, x, slot);
                                              }}
                                            >
                                              To {new Date(x).toLocaleDateString(undefined,{weekday:'long'})}
                                            </MenuItem>
                                          ))}
                                        </MenuList>
                                      </Menu>
                                    )}
                                    <HStack spacing={mealsPerDay > 4 ? 0.5 : 1} wrap="wrap">
                                      <Button 
                                        size={mealsPerDay > 4 ? "2xs" : "xs"} 
                                        variant="outline" 
                                        colorScheme="purple"
                                        onClick={() => generateMealSlot(d, slot)}
                                        isLoading={generatingMeals.has(`${d}-${slotIdx}-${slot}`)}
                                        leftIcon={mealsPerDay > 4 ? undefined : <FiCoffee />}
                                        flex={1}
                                        minW={mealsPerDay > 4 ? "60px" : "80px"}
                                        fontSize={mealsPerDay > 4 ? "9px" : "12px"}
                                        px={mealsPerDay > 4 ? 1 : 2}
                                        title="Generate a new recipe"
                                      >
                                        {mealsPerDay > 4 ? 'Gen' : 'Regenerate'}
                                      </Button>
                                      <Button 
                                        size={mealsPerDay > 4 ? "2xs" : "xs"} 
                                        variant="outline" 
                                        colorScheme="green"
                                        onClick={() => openRecipeSelector(d, slot)}
                                        flex={1}
                                        minW={mealsPerDay > 4 ? "60px" : "80px"}
                                        fontSize={mealsPerDay > 4 ? "9px" : "12px"}
                                        px={mealsPerDay > 4 ? 1 : 2}
                                        title="Pick from database recipes"
                                      >
                                        {mealsPerDay > 4 ? 'Pick' : 'Pick Recipe'}
                                      </Button>
                                    </HStack>
                                  </VStack>
                                </VStack>
                              ) : (
                                <VStack spacing={mealsPerDay > 4 ? 1.5 : 2} align="stretch">
                                  {/* CRITICAL FIX: Allow user recipe replacement in empty slots */}
                                  {swapMode && swapSourceMeal?.isUserRecipe ? (
                                    <Button 
                                      size={mealsPerDay > 4 ? "2xs" : "xs"} 
                                      variant="solid" 
                                      colorScheme="orange"
                                      onClick={() => handleSimpleSwap('', d, slot)}
                                      width="100%"
                                      fontSize={mealsPerDay > 4 ? "10px" : "12px"}
                                      py={mealsPerDay > 4 ? 2 : 3}
                                    >
                                      {mealsPerDay > 4 ? 'Place Here' : 'Place Recipe Here'}
                                    </Button>
                                  ) : (
                                    <>
                                  <Button 
                                    size={mealsPerDay > 4 ? "2xs" : "xs"} 
                                    variant="outline" 
                                    colorScheme="blue"
                                    onClick={() => generateMealSlot(d, slot)}
                                    isLoading={generatingMeals.has(`${d}-${slotIdx}-${slot}`)}
                                    leftIcon={mealsPerDay > 4 ? undefined : <FiCoffee />}
                                    width="100%"
                                    fontSize={mealsPerDay > 4 ? "10px" : "12px"}
                                    py={mealsPerDay > 4 ? 2 : 3}
                                  >
                                    {generatingMeals.has(`${d}-${slotIdx}-${slot}`) ? (mealsPerDay > 4 ? '...' : 'Generating...') : (mealsPerDay > 4 ? 'Generate' : 'Generate Recipe')}
                                  </Button>
                                  <Button 
                                    size={mealsPerDay > 4 ? "2xs" : "xs"} 
                                    variant="outline" 
                                    colorScheme="green"
                                    onClick={() => openRecipeSelector(d, slot)}
                                    width="100%"
                                    fontSize={mealsPerDay > 4 ? "10px" : "12px"}
                                    py={mealsPerDay > 4 ? 2 : 3}
                                  >
                                    {mealsPerDay > 4 ? 'Pick Recipe' : 'Pick from Database'}
                                  </Button>
                                    </>
                                  )}
                                </VStack>
                              )}
                            </Box>
                          );
                        })}
                        </React.Fragment>
                      );
                    })}
                  </Grid>
                </Box>
            </Box>
          </VStack>
        )}


        {/* Alternatives Modal */}
        <Modal isOpen={isAltOpen} onClose={onAltClose} size="4xl">
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>
              {altMealType ? `${altMealType.charAt(0).toUpperCase() + altMealType.slice(1)} Alternatives` : 'Alternatives'}
            </ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <HStack mb={4}>
                <Input placeholder="Search title or cuisine" value={altSearch} onChange={(e: React.ChangeEvent<HTMLInputElement>) => setAltSearch(e.target.value)} />
              </HStack>
              <Grid templateColumns="repeat(auto-fit, minmax(280px, 1fr))" gap={4}>
                {(altMealType ? (alternatives[altMealType] || []) : []).filter((a: any) => {
                  const q = altSearch.trim().toLowerCase();
                  if (!q) return true;
                  return (
                    (a.meal_name || '').toLowerCase().includes(q) ||
                    (a.recipe?.cuisine || '').toLowerCase().includes(q)
                  );
                }).map((alternative: any, index: number) => (
                  <Card key={index} bg={cardBg} borderColor={borderColor}>
                    <CardHeader>
                      <VStack align="start" spacing={1}>
                        <HStack justify="space-between" align="start" w="full">
                          <Heading size="sm" flex={1}>{alternative.meal_name}</Heading>
                          {alternative.recipe?.database_fallback ? (
                            <Badge size="sm" colorScheme="blue" variant="subtle">Database</Badge>
                          ) : alternative.recipe?.ai_generated !== false ? (
                            <Badge size="sm" colorScheme="purple" variant="subtle">AI</Badge>
                          ) : (
                            <Badge size="sm" colorScheme="green" variant="subtle">Recipe</Badge>
                          )}
                        </HStack>
                        <Badge colorScheme="green" size="sm">{alternative.recipe?.cuisine}</Badge>
                      </VStack>
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
                          <Button size="sm" colorScheme="blue" onClick={() => altMealType && selectAlternative(altMealType, alternative)}>
                            Select
                          </Button>
                          <Button size="sm" variant="outline" onClick={() => handleViewRecipe(alternative)}>
                            View Recipe
                          </Button>
                        </HStack>
                      </VStack>
                    </CardBody>
                  </Card>
                ))}
              </Grid>
            </ModalBody>
            <ModalFooter>
              <Button onClick={onAltClose}>Close</Button>
            </ModalFooter>
          </ModalContent>
        </Modal>

        {/* Recently Added Meals Display Box */}
        {recentlyAddedMeals.length > 0 && (
          <Card bg={cardBg} borderColor="green.300" borderWidth={2} mt={4}>
            <CardBody>
              <VStack align="stretch" spacing={4}>
                <HStack justify="space-between" align="center">
                  <Heading size="md" color="green.600">
                    ✓ My Custom Meals ({recentlyAddedMeals.length})
                  </Heading>
                  <Text fontSize="sm" color="gray.500">
                    These meals persist across week changes and grid resets
                  </Text>
                </HStack>
                
                <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
                  {recentlyAddedMeals.map((meal, index) => {
                    const mealId = meal.id || (meal as any).meal_id || (meal as any).mealId;
                    const mealName = meal.meal_name || meal.name || (meal as any).mealName || 'Custom Meal';
                    const mealType = meal.meal_type || meal.type || 'meal';
                    const mealCalories = meal.calories ?? (meal.recipe as any)?.per_serving_calories ?? meal.recipe?.nutrition?.calories ?? (meal.recipe as any)?.calories ?? 0;
                    
                    return (
                      <Card key={mealId || index} bg={cardBg} borderWidth={1} borderColor="green.200">
                        <CardBody>
                          <VStack align="stretch" spacing={2}>
                <HStack justify="space-between" align="start">
                  <VStack align="start" spacing={1} flex={1}>
                    <HStack spacing={2}>
                                  <Text fontSize="sm" fontWeight="semibold" noOfLines={1}>
                                    {mealName}
                                  </Text>
                                  <Badge colorScheme="green" variant="subtle" size="xs">
                                    {mealType}
                      </Badge>
                    </HStack>
                  </VStack>
                  <Button
                    size="xs"
                    variant="ghost"
                    onClick={() => {
                                  // Remove this meal from the list
                                  setRecentlyAddedMeals(prev => prev.filter(m => {
                                    const mId = m.id || (m as any).meal_id || (m as any).mealId;
                                    return String(mId) !== String(mealId);
                                  }));
                    }}
                                aria-label="Remove meal"
                  >
                    ×
                  </Button>
                </HStack>
                
                            <HStack spacing={3} fontSize="xs" color="gray.600">
                  <Text fontWeight="semibold">
                                {Math.round(mealCalories)} cal
                  </Text>
                              {meal.protein && <Text>P: {Math.round(meal.protein)}g</Text>}
                              {meal.carbs && <Text>C: {Math.round(meal.carbs)}g</Text>}
                              {meal.fats && <Text>F: {Math.round(meal.fats)}g</Text>}
                </HStack>
                
                            <HStack spacing={2} wrap="wrap">
                  <Button
                                size="xs"
                    colorScheme="blue"
                    variant="outline"
                    onClick={() => {
                                  handleViewRecipe(meal);
                    }}
                  >
                                View
                  </Button>
                  <Button
                                size="xs"
                    colorScheme="green"
                    variant="outline"
                    onClick={() => {
                        // Convert meal data to CustomMealData format
                                  const mealData = meal.recipe || meal;
                                  const mealDataAny = mealData as any;
                                  const mealAny = meal as any;
                        const customMealData = {
                                    meal_name: meal.meal_name ?? meal.name ?? mealDataAny?.title ?? '',
                                    meal_type: (meal.meal_type ?? meal.type ?? 'breakfast') as any,
                          cuisine: mealData?.cuisine ?? '',
                                    prep_time: mealData?.prep_time ?? meal.prep_time ?? 0,
                                    cook_time: mealData?.cook_time ?? meal.cook_time ?? 0,
                                    servings: mealDataAny?.servings ?? 1,
                                    difficulty: (mealData?.difficulty ?? meal.difficulty_level ?? 'easy') as any,
                                    summary: mealDataAny?.summary ?? '',
                                    ingredients: mealData?.ingredients ?? meal.ingredients ?? [{ name: '', quantity: 0, unit: 'g' }],
                                    instructions: mealData?.instructions ?? meal.instructions ?? [{ step: 1, description: '' }],
                                    dietary_tags: mealData?.dietary_tags ?? meal.dietary_tags ?? [],
                          nutrition: {
                                      calories: meal.calories ?? mealDataAny?.nutrition?.calories ?? mealDataAny?.per_serving_calories ?? 0,
                                      protein: meal.protein ?? mealDataAny?.nutrition?.protein ?? 0,
                                      carbs: meal.carbs ?? mealDataAny?.nutrition?.carbs ?? 0,
                                      fats: meal.fats ?? mealDataAny?.nutrition?.fats ?? 0
                          }
                        };
                                  setEditingMealId(meal.id);
                        setEditingMealData(customMealData);
                        onCustomMealOpen();
                    }}
                  >
                                Edit
                  </Button>
                  <Button
                                size="xs"
                                colorScheme={swapMode && swapSourceMeal?.id === String(mealId) ? "gray" : "orange"}
                                variant={swapMode && swapSourceMeal?.id === String(mealId) ? "outline" : "solid"}
                                onClick={() => {
                                  if (!mealPlan) return;
                                  
                                  // CRITICAL FIX: Toggle replace mode - if already active, deactivate it
                                  if (swapMode && swapSourceMeal?.id === String(mealId)) {
                                    // Deactivate replace mode
                                    setSwapMode(false);
                                    setSwapSourceMeal(null);
                                    toast({
                                      title: 'Replace mode cancelled',
                                      description: 'You can click "Swap to Grid" again to reactivate',
                                      status: 'info',
                                      duration: 2000,
                                      isClosable: true
                                    });
                        return;
                      }
                      
                                  // CRITICAL FIX: Validate meal ID before entering replace mode
                                  const mealAny = meal as any;
                                  const mealIdToUse = meal.id || mealAny.meal_id || mealAny.mealId;
                                  if (!mealIdToUse) {
                                    toast({
                                      title: 'Cannot swap',
                                      description: 'Meal ID is missing. Please try adding the meal again.',
                                      status: 'error',
                                      duration: 3000,
                                      isClosable: true
                                    });
                          return;
                        }
                        
                                  // Enter replace mode - user will click a grid slot to replace
                                  setSwapMode(true);
                                  setSwapSourceMeal({ 
                                    id: String(mealIdToUse), 
                                    date: mealAny.meal_date || mealAny.date || '', 
                                    mealType: meal.meal_type || meal.type || '',
                                    isUserRecipe: true // Flag to indicate this is a user recipe replacement
                                  });
                          toast({
                                    title: 'Replace mode active',
                                    description: 'Click a meal in the grid to replace it with your custom recipe',
                                    status: 'info',
                          duration: 3000, 
                          isClosable: true 
                        });
                    }}
                  >
                                {swapMode && swapSourceMeal?.id === String(mealId) ? 'Cancel' : 'Swap to Grid'}
                  </Button>
                </HStack>
                          </VStack>
                        </CardBody>
                      </Card>
                    );
                  })}
                </SimpleGrid>
              </VStack>
            </CardBody>
          </Card>
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
                    <Textarea value={selectedMeal.ingredients?.join(', ') || ''} />
                  </FormControl>
                  <FormControl>
                    <FormLabel>{t('nutrition.instructions', 'en')}</FormLabel>
                    <Textarea value={selectedMeal.instructions?.join('\n') || ''} rows={4} />
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
              <HStack justify="space-between" align="start" w="full" pr={8}>
                <VStack align="start" spacing={1} flex={1}>
                  <Text>{(selectedRecipe as any)?.title || selectedRecipe?.meal_name || selectedRecipe?.name || 'Recipe Details'}</Text>
                  <HStack spacing={2}>
                  {(selectedRecipe as any)?.database_fallback ? (
                    <Badge colorScheme="blue" variant="subtle">Database</Badge>
                  ) : (selectedRecipe as any)?.ai_generated !== false ? (
                    <Badge colorScheme="purple" variant="subtle">AI Generated</Badge>
                  ) : (
                    <Badge colorScheme="green" variant="subtle">Recipe Database</Badge>
                  )}
                </HStack>
                </VStack>
                {selectedRecipe?.ingredients && selectedRecipe.ingredients.length > 0 && (
                  <Button
                    size="xs"
                    leftIcon={<FiPieChart />}
                    colorScheme="blue"
                    variant="outline"
                    onClick={onIngredientGraphsOpen}
                    px={3}
                    py={1.5}
                    minW="auto"
                    iconSpacing={1.5}
                    fontSize="xs"
                    h="auto"
                  >
                    Graphs
                  </Button>
                )}
              </HStack>
            </ModalHeader>
            <ModalCloseButton />
            <ModalBody maxH="80vh" overflowY="auto">
              {selectedRecipe && (
                <VStack spacing={6} align="stretch">
                  {/* Nutritional Information */}
                  <Box>
                    <Heading size="md" mb={3}>Nutritional Information</Heading>
                    <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                      <Box p={3} bg="blue.50" borderRadius="md">
                        <Text fontSize="sm" color="gray.600">Calories</Text>
                        <Text fontSize="lg" fontWeight="bold">
                          {(selectedRecipe as any)?.per_serving_calories ?? 
                           (selectedRecipe.recipe as any)?.per_serving_calories ??
                           selectedRecipe.calories ?? 
                           selectedRecipe.recipe?.nutrition?.calories ?? 
                           0}
                        </Text>
                      </Box>
                      <Box p={3} bg="green.50" borderRadius="md">
                        <Text fontSize="sm" color="gray.600">Protein</Text>
                        <Text fontSize="lg" fontWeight="bold">
                          {(selectedRecipe as any)?.per_serving_protein ?? 
                           (selectedRecipe.recipe as any)?.per_serving_protein ??
                           selectedRecipe.protein ?? 
                           selectedRecipe.recipe?.nutrition?.protein ?? 
                           0}g
                        </Text>
                      </Box>
                      <Box p={3} bg="orange.50" borderRadius="md">
                        <Text fontSize="sm" color="gray.600">Carbs</Text>
                        <Text fontSize="lg" fontWeight="bold">
                          {(selectedRecipe as any)?.per_serving_carbs ?? 
                           (selectedRecipe.recipe as any)?.per_serving_carbs ??
                           selectedRecipe.carbs ?? 
                           selectedRecipe.recipe?.nutrition?.carbs ?? 
                           0}g
                        </Text>
                      </Box>
                      <Box p={3} bg="purple.50" borderRadius="md">
                        <Text fontSize="sm" color="gray.600">Fats</Text>
                        <Text fontSize="lg" fontWeight="bold">
                          {(selectedRecipe as any)?.per_serving_fat ?? 
                           (selectedRecipe as any)?.per_serving_fats ??
                           (selectedRecipe.recipe as any)?.per_serving_fat ??
                           (selectedRecipe.recipe as any)?.per_serving_fats ??
                           selectedRecipe.fats ?? 
                           selectedRecipe.recipe?.nutrition?.fats ?? 
                           0}g
                        </Text>
                      </Box>
                    </Grid>
                  </Box>

                  {/* Portion Adjustment - Compact design */}
                  <Box borderTop="1px" borderColor="gray.200" pt={4}>
                    <HStack justify="space-between" align="center" mb={2}>
                      <Text fontSize="sm" fontWeight="semibold" color="gray.700">Portion Size</Text>
                      {(selectedRecipe.id || (selectedRecipe as any).meal_id) && (
                        <Button
                          size="xs"
                          variant="ghost"
                          colorScheme="blue"
                          onClick={async () => {
                            const mealId = selectedRecipe.id || (selectedRecipe as any).meal_id;
                            const newServings = ((selectedRecipe as any).servings || selectedRecipe.recipe?.servings || 1) as number;
                            if (mealId && newServings > 0) {
                              try {
                                setLoading(true);
                                await adjustMealPortion(mealId, newServings);
                                toast({
                                  title: 'Portion adjusted',
                                  description: `Recipe servings updated to ${newServings}`,
                                  status: 'success',
                                  duration: 2000,
                                  isClosable: true
                                });
                                // adjustMealPortion already updates selectedRecipe state
                                // No additional update needed here
                              } catch (err) {
                                toast({
                                  title: 'Error',
                                  description: 'Failed to adjust portion size',
                                  status: 'error',
                                  duration: 2000,
                                  isClosable: true
                                });
                              } finally {
                                setLoading(false);
                              }
                            }
                          }}
                          isLoading={loading}
                          isDisabled={loading || !((selectedRecipe as any).previewMultiplier && (selectedRecipe as any).previewMultiplier !== 1)}
                        >
                          Apply Change
                        </Button>
                      )}
                    </HStack>
                    
                    <HStack spacing={2} align="center" justify="center" w="full">
                      <Button
                        size="sm"
                        colorScheme="blue"
                        borderRadius="full"
                        width="32px"
                        height="32px"
                        fontSize="md"
                        onClick={() => {
                          const newServings = Math.max(0.25, previewServings - 0.25);
                          handleServingsChange(newServings);
                        }}
                        isDisabled={loading}
                      >
                        −
                      </Button>
                      
                      <FormControl width="100px">
                        <NumberInput
                          value={previewServings}
                          min={0.25}
                          max={10}
                          step={0.25}
                          precision={2}
                          onChange={(_valueString: string, valueNumber: number) => {
                            if (valueNumber > 0) {
                              handleServingsChange(valueNumber);
                            }
                          }}
                          size="sm"
                        >
                          <NumberInputField 
                            textAlign="center" 
                            fontWeight="semibold"
                            fontSize="sm"
                            bg="white"
                          />
                        </NumberInput>
                      </FormControl>
                      
                      <Text fontSize="sm" color="gray.600" minW="50px" textAlign="center">
                        serving{previewServings !== 1 ? 's' : ''}
                      </Text>
                      
                      <Button
                        size="sm"
                        colorScheme="blue"
                        borderRadius="full"
                        width="32px"
                        height="32px"
                        fontSize="md"
                        onClick={() => {
                          const newServings = Math.min(10, previewServings + 0.25);
                          handleServingsChange(newServings);
                        }}
                        isDisabled={loading}
                      >
                        +
                      </Button>
                      
                      <Button
                        size="xs"
                        variant="ghost"
                        colorScheme="gray"
                        onClick={() => {
                          const originalServings = selectedRecipe?.recipe?.servings || (selectedRecipe as any)?.servings || 1;
                          handleServingsChange(originalServings);
                        }}
                        isDisabled={loading}
                      >
                        Reset
                      </Button>
                    </HStack>
                    
                    {/* Compact preview of adjusted nutrition - only show when changed */}
                    {(selectedRecipe as any).previewCalories && (selectedRecipe as any).previewMultiplier !== 1 && (
                      <Box mt={2} p={2} bg="blue.50" borderRadius="sm" borderLeft="2px" borderColor="blue.400">
                        <HStack spacing={3} fontSize="xs">
                          <Text color="blue.700" fontWeight="semibold">
                            {(selectedRecipe as any).previewCalories} cal
                          </Text>
                          {(selectedRecipe as any).previewProtein > 0 && (
                            <Text color="green.700">P: {(selectedRecipe as any).previewProtein}g</Text>
                          )}
                          {(selectedRecipe as any).previewCarbs > 0 && (
                            <Text color="orange.700">C: {(selectedRecipe as any).previewCarbs}g</Text>
                          )}
                          {(selectedRecipe as any).previewFats > 0 && (
                            <Text color="purple.700">F: {(selectedRecipe as any).previewFats}g</Text>
                          )}
                        </HStack>
                      </Box>
                    )}
                  </Box>
                  

                  {/* Ingredients */}
                  {selectedRecipe.ingredients && selectedRecipe.ingredients.length > 0 && (
                    <Box>
                      <Heading size="md" mb={3}>Ingredients</Heading>
                      <VStack align="stretch" spacing={2}>
                        {selectedRecipe.ingredients.map((ingredient: any, index: number) => {
                          // Calculate adjusted quantity if portion has been changed
                          const currentServings = (selectedRecipe as any).servings || selectedRecipe.recipe?.servings || 1;
                          const originalServings = (ingredient.original_servings || selectedRecipe.recipe?.servings || ingredient.servings || 1);
                          const multiplier = currentServings / originalServings;
                          const adjustedQuantity = typeof ingredient === 'object' && ingredient.quantity 
                            ? (multiplier !== 1 ? (ingredient.quantity * multiplier).toFixed(1) : ingredient.quantity)
                            : null;
                          
                          const ingredientName = typeof ingredient === 'string' 
                            ? ingredient 
                            : (ingredient.name || 'Unknown');
                          const ingredientDisplay = typeof ingredient === 'string' 
                            ? ingredient 
                            : `${ingredient.name} - ${adjustedQuantity || ingredient.quantity}${ingredient.unit || 'g'}${multiplier !== 1 && (selectedRecipe as any).previewCalories ? ' (adjusted)' : ''}`;
                          
                          // CRITICAL: Check if this meal can be modified (has recipe_details with ingredients in database)
                          // We MUST check the original meal object from mealPlan.meals, not the normalized selectedRecipe
                          // because the backend checks the database, not the frontend state
                          const mealId = (selectedRecipe as any).meal_id || selectedRecipe.id;
                          const mealFromPlan = mealPlan?.meals?.find((m: any) => 
                            (m.id === mealId) || (m.meal_id === mealId)
                          );
                          
                          // Check recipe_details from the original meal object (what's in the database)
                          const recipeDetailsFromDB = (mealFromPlan as any)?.recipe_details || (mealFromPlan?.recipe as any)?.recipe_details;
                          
                          // Check if recipe_details exists in database and has ingredients
                          const hasRecipeDetailsWithIngredients = recipeDetailsFromDB && 
                            recipeDetailsFromDB.ingredients && 
                            Array.isArray(recipeDetailsFromDB.ingredients) &&
                            recipeDetailsFromDB.ingredients.length > 0;
                          
                          // Only show substitute button if meal has recipe_details with ingredients in database
                          // This ensures the backend check will pass
                          const canSubstitute = hasRecipeDetailsWithIngredients;
                          
                          return (
                            <HStack key={index} spacing={2} align="center">
                              <Text pl={4} borderLeft="3px solid" borderColor="blue.200" flex={1}>
                                {ingredientDisplay}
                              </Text>
                              {canSubstitute && (
                                <Button
                                  size="xs"
                                  variant="ghost"
                                  colorScheme="blue"
                                  onClick={() => loadSubstitutionSuggestions(ingredientName)}
                                  isLoading={loadingSubstitutions && substitutionIngredient === ingredientName}
                                  title="Find substitutions"
                                >
                                  Substitute
                                </Button>
                              )}
                            </HStack>
                          );
                        })}
                      </VStack>
                      {(selectedRecipe as any).previewCalories && (
                        <Text fontSize="xs" color="gray.500" mt={2} fontStyle="italic">
                          * Ingredient quantities shown with adjusted portion size
                        </Text>
                      )}
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
                  {selectedRecipe && (selectedRecipe?.dietaryTags || selectedRecipe?.dietary_tags) && 
                   (selectedRecipe?.dietaryTags || selectedRecipe?.dietary_tags || []).length > 0 && (
                    <Box>
                      <Heading size="md" mb={3}>Dietary Information</Heading>
                      <HStack spacing={2} flexWrap="wrap">
                        {(() => {
                          const tags = (selectedRecipe?.dietaryTags || selectedRecipe?.dietary_tags || []) as string[];
                          const ingredientsList = (selectedRecipe?.ingredients || []).map((i: any) => typeof i === 'string' ? i.toLowerCase() : String(i?.name || '').toLowerCase());
                          const text = `${((selectedRecipe as any)?.title || selectedRecipe?.meal_name || '')}`.toLowerCase() + ' ' + ingredientsList.join(' ');
                          const meat = ["chicken","beef","pork","lamb","turkey","bacon","ham","sausage","salami","fish","salmon","tuna","shrimp","prawn","anchovy","chorizo"].some(k=>text.includes(k));
                          const dairyOrEgg = ["milk","cheese","yogurt","butter","cream","feta","mozzarella","parmesan","egg"].some(k=>text.includes(k));
                          const gluten = ["wheat","flour","bread","pasta","noodle","tortilla","barley","rye","cracker","breadcrumbs"].some(k=>text.includes(k));
                          let normalized = Array.from(new Set(tags.map(t=>t.toLowerCase())));
                          if (meat) {
                            normalized = normalized.filter(t=>t!=="vegetarian" && t!=="vegan");
                          } else if (dairyOrEgg) {
                            // Eggs/dairy present: ensure vegan is not shown; do NOT auto-add vegetarian
                            normalized = normalized.filter(t=>t!=="vegan");
                          } else {
                            // No meat and no dairy/egg: do NOT auto-add tags; trust backend
                            // Keep existing tags as-is
                          }
                          if (gluten) normalized = normalized.filter(t=>t!=="gluten-free");
                          return normalized.map((tag, index) => (
                            <Badge key={index} colorScheme="blue" variant="subtle">{tag}</Badge>
                          ));
                        })()}
                      </HStack>
                    </Box>
                  )}

                  {/* Fallback message if no detailed recipe info */}
                  {(() => {
                    // Check if we have ingredients or instructions in the normalized object
                    const hasIngredients = selectedRecipe.ingredients && selectedRecipe.ingredients.length > 0;
                    const hasInstructions = selectedRecipe.instructions && selectedRecipe.instructions.length > 0;
                    
                    // Only show error message if we truly have no ingredients AND no instructions
                    // AND we don't have recipe_details in the database (which would allow substitution)
                    const mealId = (selectedRecipe as any).meal_id || selectedRecipe.id;
                    const mealFromPlan = mealPlan?.meals?.find((m: any) => 
                      (m.id === mealId) || (m.meal_id === mealId)
                    );
                    const hasRecipeDetailsInDB = (mealFromPlan as any)?.recipe_details || (mealFromPlan?.recipe as any)?.recipe_details;
                    
                    // Only show error if we have no ingredients, no instructions, AND no recipe_details in DB
                    return !hasIngredients && !hasInstructions && !hasRecipeDetailsInDB;
                  })() && (
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
              <Button variant="ghost" mr={3} onClick={onRecipeClose}>
                Close
              </Button>
              <Button 
                colorScheme="green"
                variant="outline"
                mr={3}
                onClick={async () => {
                  await handleAddToDailyLog(selectedRecipe);
                }}
                isLoading={loading}
                fontSize="xs"
                px={3}
                py={1.5}
                size="sm"
              >
                Add to Daily Log ({previewServings} {previewServings !== 1 ? 'servings' : 'serving'})
              </Button>
              <Button 
                colorScheme="blue"
                onClick={() => {
                  onRecipeClose();
                  setAddToMealPlanRecipe(selectedRecipe);
                  onAddToMealPlanOpen();
                }}
                fontSize="xs"
                px={3}
                py={1.5}
                size="sm"
              >
                Add to Meal Plan ({previewServings} {previewServings !== 1 ? 'servings' : 'serving'})
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>

        {/* Recipe Selector Modal */}
        <Modal isOpen={recipeSelectorOpen} onClose={() => setRecipeSelectorOpen(false)} size="4xl">
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>
              Add Recipe to {selectedSlot ? `${new Date(selectedSlot.date).toLocaleDateString(undefined, {weekday: 'long'})} ${selectedSlot.mealType.charAt(0).toUpperCase() + selectedSlot.mealType.slice(1)}` : 'Meal Plan'}
            </ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              <VStack spacing={4} align="stretch">
                <Input 
                  placeholder="Search recipes..." 
                  value={recipeSearch} 
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => setRecipeSearch(e.target.value)} 
                />
                <Grid templateColumns="repeat(auto-fit, minmax(300px, 1fr))" gap={4}>
                  {availableRecipes.filter(recipe => {
                    const search = recipeSearch.toLowerCase();
                    return !search || 
                      (recipe.title || recipe.name)?.toLowerCase().includes(search) ||
                      recipe.cuisine?.toLowerCase().includes(search) ||
                      (recipe.summary || recipe.description)?.toLowerCase().includes(search);
                  }).map((recipe: any) => {
                    // CRITICAL FIX: Remove any string-based tag/category fields that cause blue bordered text overflow
                    // Explicitly remove these fields to prevent rendering
                    const cleanedRecipe = { ...recipe };
                    delete cleanedRecipe.tags;
                    delete cleanedRecipe.categories;
                    delete cleanedRecipe.keywords;
                    delete cleanedRecipe.metadata;
                    // Ensure dietary_tags is always an array, never a string
                    if (typeof cleanedRecipe.dietary_tags === 'string') {
                      cleanedRecipe.dietary_tags = [];
                    }
                    
                    return (
                    <Card key={recipe.id} bg={cardBg} borderColor={borderColor}>
                      <CardHeader>
                        <VStack align="start" spacing={2}>
                          <HStack justify="space-between" align="start" w="full">
                            <Heading size="sm" flex={1}>{recipe.title || recipe.name || 'Untitled Recipe'}</Heading>
                            <Badge colorScheme="green" variant="subtle">Recipe Database</Badge>
                          </HStack>
                          {/* CRITICAL FIX: REMOVED entire HStack that was rendering cuisine, difficulty_level, meal_type badges */}
                          {/* These badges were displaying misformatted descriptive keywords (FISH, MARINATE, BACKYARD, etc.) */}
                          {/* Completely removed to prevent blue bordered text overflow issue */}
                        </VStack>
                      </CardHeader>
                      <CardBody>
                        <VStack spacing={3} align="stretch">
                          {recipe.summary || recipe.description ? (
                            <Text fontSize="sm" color="gray.600" noOfLines={2}>
                              {recipe.summary || recipe.description}
                            </Text>
                          ) : null}
                          {/* CRITICAL FIX: Explicitly DO NOT render any string-based tag fields */}
                          {/* Do NOT render recipe.tags, recipe.categories, recipe.keywords, or dietary_tags as a string */}
                          {/* These fields contain descriptive keywords (FISH, MARINATE, BACKYARD, etc.) that should NOT be displayed */}
                          {(() => {
                            // Completely prevent rendering of any string-based tag fields
                            // Explicitly check for and skip string-based fields
                            if (typeof recipe.tags === 'string' || typeof recipe.categories === 'string' || 
                                typeof recipe.keywords === 'string' || typeof recipe.metadata === 'string') {
                              // Do NOT render these string fields - they contain misformatted descriptive keywords
                              return null;
                            }
                            
                            // Only render dietary_tags if it's a valid array
                            if (!recipe.dietary_tags || !Array.isArray(recipe.dietary_tags) || recipe.dietary_tags.length === 0) {
                              return null;
                            }
                            
                            // Also skip if dietary_tags is a string (should never happen, but prevent rendering if it does)
                            if (typeof recipe.dietary_tags === 'string') {
                              return null;
                            }
                            
                            // Dietary Tags - Match style from RecipeSearch
                            // CRITICAL FIX: Filter out descriptive keywords that aren't actual dietary tags
                            // These are old/misformed tags like "FISH", "MARINATE", "BACKYARD", "GRILL", etc.
                            const descriptiveKeywords = new Set([
                              'fish', 'marinate', 'backyard', 'bbq', 'grill', 'barbecue', 'summer', 'winter',
                              'spring', 'fall', 'easy', 'hard', 'snack', 'dinner', 'lunch', 'breakfast',
                              'chicken', 'beef', 'pork', 'lamb', 'turkey', 'garlic', 'onion', 'lime',
                              'cucumber', 'cantaloupe', 'avocado', 'parsley', 'cumin', 'mexican', 'international',
                              'father\'s day', 'tailgating', 'mayonnaise', 'cheddar', 'hot pepper', 'sugar conscious',
                              'peanut free', 'advance prep required', 'paleo', 'dairy free', 'wheat/gluten-free'
                            ]);
                            
                            // Only show actual dietary/allergen tags, not descriptive keywords
                            const actualDietaryTags = recipe.dietary_tags.filter((tag: string) => {
                              const tagLower = tag.toLowerCase();
                              // Skip if it's a descriptive keyword
                              if (descriptiveKeywords.has(tagLower)) return false;
                              // Skip if it's a single uppercase word (likely a keyword)
                              if (/^[A-Z]+$/.test(tag) && tag.length > 2) return false;
                              // Keep actual dietary/allergen tags
                              return tagLower.includes('vegetarian') || tagLower.includes('vegan') || 
                                     tagLower.includes('gluten') || tagLower.includes('dairy') || 
                                     tagLower.includes('nut') || tagLower.includes('soy') || 
                                     tagLower.includes('egg') || tagLower.includes('fish') ||
                                     tagLower.includes('contains-') || tagLower.includes('free') ||
                                     tagLower.includes('nightshade') || tagLower.includes('sugar') ||
                                     tagLower.includes('paleo') || tagLower.includes('balanced');
                            });
                            
                            if (actualDietaryTags.length === 0) return null;
                            
                            return (
                              <Box width="100%" overflow="hidden">
                                <HStack wrap="wrap" spacing={1} maxW="100%">
                                  {actualDietaryTags.slice(0, 6).map((tag: string) => {
                                    const tagLower = tag.toLowerCase();
                                    let colorScheme = "gray";
                                    
                                    // Color code dietary tags
                                    if (tagLower === 'vegetarian') colorScheme = "green";
                                    else if (tagLower === 'vegan') colorScheme = "teal";
                                    else if (tagLower.includes('peanut') || tagLower.includes('nut-free')) colorScheme = "red";
                                    else if (tagLower.includes('tree-nut')) colorScheme = "orange";
                                    else if (tagLower.includes('nightshade')) colorScheme = "purple";
                                    else if (tagLower.includes('dairy') || tagLower.includes('eggs') || 
                                             tagLower.includes('gluten') || tagLower.includes('soy') || 
                                             tagLower.includes('fish') || tagLower.includes('contains-')) colorScheme = "red";
                                    else if (tagLower.includes('sugar') || tagLower.includes('paleo')) colorScheme = "blue";
                                    
                                    return (
                                      <Badge 
                                        key={tag} 
                                        size="sm" 
                                        colorScheme={colorScheme} 
                                        variant="subtle"
                                        noOfLines={1}
                                        textTransform="capitalize"
                                        maxW="100%"
                                        wordBreak="break-word"
                                        whiteSpace="normal"
                                      >
                                        {tag.replace('contains-', '').replace(/-/g, ' ')}
                                      </Badge>
                                    );
                                  })}
                                  {actualDietaryTags.length > 6 && (
                                    <Text fontSize="xs" color="gray.500" noOfLines={1}>
                                      +{actualDietaryTags.length - 6} more
                                    </Text>
                                  )}
                                </HStack>
                              </Box>
                            );
                          })()}
                          
                          <HStack justify="space-between" fontSize="sm" color="gray.600">
                            <HStack spacing={2}>
                              <Text>{recipe.prep_time || 0} min</Text>
                              {recipe.cook_time && <Text>• {recipe.cook_time} min cook</Text>}
                            </HStack>
                            <Text fontWeight="semibold">
                              {recipe.per_serving_calories || recipe.nutrition?.per_serving_calories || recipe.nutrition?.calories || recipe.calculated_calories || 0} cal
                            </Text>
                          </HStack>
                          
                          <HStack spacing={2} pt={1}>
                            <Button 
                              size="sm" 
                              colorScheme="green" 
                              onClick={() => addRecipeToGrid(recipe)}
                              isLoading={loading}
                              flex={1}
                            >
                              Add to Plan
                            </Button>
                            <Button 
                              size="sm" 
                              variant="outline" 
                              onClick={() => handleViewRecipe(recipe)}
                              flex={1}
                            >
                              View Recipe
                            </Button>
                          </HStack>
                        </VStack>
                      </CardBody>
                    </Card>
                    );
                  })}
                </Grid>
                {availableRecipes.length === 0 && (
                  <Center py={8}>
                    <VStack spacing={2}>
                      <Text color="gray.500">No recipes found</Text>
                      <Text fontSize="sm" color="gray.400">Try adjusting your search terms</Text>
                    </VStack>
                  </Center>
                )}
              </VStack>
            </ModalBody>
            <ModalFooter>
              <Button onClick={() => setRecipeSelectorOpen(false)}>Close</Button>
            </ModalFooter>
          </ModalContent>
        </Modal>

        {/* Custom Meal Modal */}
        <CustomMealModal
          isOpen={isCustomMealOpen}
          onClose={() => {
            onCustomMealClose();
            setEditingMealId(null);
            setEditingMealData(null);
          }}
          onSave={handleCustomMealSave}
          initialData={editingMealData || undefined}
          selectedDate={selectedDate} // ROOT CAUSE FIX: Pass selected date to modal
          selectedMealType={selectedSlot?.mealType} // ROOT CAUSE FIX: Pass selected meal type to modal
        />
        
        {/* Add to Meal Plan Modal */}
        {addToMealPlanRecipe && (
          <AddToMealPlanModal
            isOpen={isAddToMealPlanOpen}
            onClose={onAddToMealPlanClose}
            recipe={addToMealPlanRecipe}
            onRecipeAdded={() => {
              toast({
                title: 'Recipe Added!',
                description: 'Recipe has been added to your meal plan',
                status: 'success',
                duration: 3000,
                isClosable: true,
              });
              loadMealPlan();
            }}
            initialServings={previewServings}
          />
        )}
        
        {/* Ingredient Graphs Modal */}
        <Modal isOpen={isIngredientGraphsOpen} onClose={onIngredientGraphsClose} size="xl">
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>
              <Text>Ingredient Values - {(selectedRecipe as any)?.title || selectedRecipe?.meal_name || selectedRecipe?.name || 'Recipe'}</Text>
            </ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              {selectedRecipe && selectedRecipe.ingredients && selectedRecipe.ingredients.length > 0 ? (
                <VStack spacing={6} align="stretch">
                  <Box>
                    <Heading size="md" mb={4}>Ingredient Macronutrients (Protein, Carbs, Fats)</Heading>
                    <Box p={4} bg="white" borderRadius="md" border="1px" borderColor="gray.200" height="400px">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart
                          data={(() => {
                            const selectedRecipeAny = selectedRecipe as any;
                            const currentServings = previewServings || selectedRecipeAny.servings || selectedRecipe.recipe?.servings || 1;
                            const originalServings = selectedRecipe.recipe?.servings || selectedRecipeAny.servings || 1;
                            const multiplier = currentServings / originalServings;
                            
                            // Nutrition per 100g lookup
                            const per100g: Record<string, [number, number, number]> = {
                              'chicken breast': [31, 0, 3.6],
                              'chicken': [31, 0, 3.6],
                              'chickpea': [19, 61, 6],
                              'chickpeas': [19, 61, 6],
                              'olive oil': [0, 0, 100],
                              'oil': [0, 0, 100],
                              'tomato': [0.9, 3.9, 0.2],
                              'cucumber': [0.7, 3.6, 0.1],
                              'lettuce': [1.4, 2.9, 0.2],
                              'bell pepper': [1, 6, 0.3],
                              'pepper': [1, 6, 0.3],
                              'carrot': [0.9, 10, 0.2],
                              'onion': [1.1, 9.3, 0.1],
                              'garlic': [6.4, 33, 0.5],
                              'feta': [14, 4, 21],
                              'cheese': [20, 2, 25],
                              'hummus': [8, 14, 9.6],
                              'rice': [2.4, 28, 0.3],
                              'quinoa': [4.4, 21, 1.9],
                              'pasta': [5, 25, 1.1],
                              'yogurt': [10, 3.6, 0.4],
                              'egg': [6, 0.6, 5],
                              'eggs': [6, 0.6, 5],
                              'ham': [18, 1.5, 5],
                              'mushroom': [3.1, 3.3, 0.3],
                              'mushrooms': [3.1, 3.3, 0.3],
                              'bread': [9, 49, 3.2],
                              'rye bread': [9, 49, 3.2],
                              'swiss cheese': [25, 1.5, 27],
                              'mayonnaise': [1, 0.6, 75],
                              'mustard': [3.7, 5.8, 3.3],
                              'dill': [3.5, 7, 1.1],
                              'zucchini': [1.2, 3.1, 0.2],
                              'parsley': [3, 6, 0.8],
                            };
                            
                            return (selectedRecipe.ingredients || []).map((ingredient: any) => {
                              let name = '';
                              let quantity = 0;
                              let unit = 'g';
                              
                              if (typeof ingredient === 'string') {
                                name = ingredient;
                                quantity = 0;
                              } else {
                                name = ingredient.name || 'Unknown';
                                quantity = parseFloat(ingredient.quantity) || 0;
                                unit = ingredient.unit || 'g';
                                // Scale quantity by servings multiplier
                                quantity = quantity * multiplier;
                              }
                              
                              // Convert to grams
                              let quantityInGrams = quantity;
                              if (unit.toLowerCase() === 'ml' || unit.toLowerCase() === 'l') {
                                quantityInGrams = quantity; // 1ml ≈ 1g for most liquids
                              } else if (unit.toLowerCase() === 'kg') {
                                quantityInGrams = quantity * 1000;
                              } else if (unit.toLowerCase() === 'oz') {
                                quantityInGrams = quantity * 28.35;
                              } else if (unit.toLowerCase() === 'lb') {
                                quantityInGrams = quantity * 453.6;
                              } else if (unit.toLowerCase() === 'unit' || unit.toLowerCase() === 'units' || unit.toLowerCase() === 'piece' || unit.toLowerCase() === 'pieces') {
                                // For eggs, assume 1 unit = 50g
                                if (name.toLowerCase().includes('egg')) {
                                  quantityInGrams = quantity * 50;
                                } else {
                                  quantityInGrams = quantity * 100; // Default assumption
                                }
                              }
                              
                              // Find matching nutrition data
                              const nameLower = name.toLowerCase();
                              const match = Object.keys(per100g).find(k => nameLower.includes(k));
                              let protein = 0;
                              let carbs = 0;
                              let fats = 0;
                              
                              if (match && quantityInGrams > 0) {
                                const [p, c, f] = per100g[match];
                                const factor = quantityInGrams / 100.0;
                                protein = Math.round(p * factor * 10) / 10;
                                carbs = Math.round(c * factor * 10) / 10;
                                fats = Math.round(f * factor * 10) / 10;
                              }
                              
                              return {
                                name: name.length > 15 ? name.substring(0, 15) + '...' : name,
                                fullName: name,
                                protein: protein,
                                carbs: carbs,
                                fats: fats,
                                quantity: quantityInGrams,
                                unit: unit
                              };
                            }).filter((item: any) => item.protein > 0 || item.carbs > 0 || item.fats > 0);
                          })()}
                          margin={{ top: 5, right: 30, left: 20, bottom: 80 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                          <XAxis 
                            dataKey="name" 
                            angle={-45} 
                            textAnchor="end" 
                            height={100}
                            interval={0}
                            tick={{ fontSize: 10 }}
                          />
                          <YAxis 
                            label={{ value: 'Macronutrients (g)', angle: -90, position: 'insideLeft', style: { textAnchor: 'middle' } }}
                            tick={{ fontSize: 10 }}
                          />
                          <Tooltip 
                            formatter={(value: any, name: string) => {
                              // The name parameter is the dataKey ('protein', 'carbs', 'fats')
                              const label = name === 'protein' ? 'Protein' : name === 'carbs' ? 'Carbs' : name === 'fats' ? 'Fats' : name;
                              return [`${value}g`, label];
                            }}
                            labelFormatter={(label: string) => {
                              const item = (() => {
                                const selectedRecipeAny = selectedRecipe as any;
                                const currentServings = previewServings || selectedRecipeAny.servings || selectedRecipe.recipe?.servings || 1;
                                const originalServings = selectedRecipe.recipe?.servings || selectedRecipeAny.servings || 1;
                                const multiplier = currentServings / originalServings;
                                return (selectedRecipe.ingredients || []).find((ing: any) => {
                                  const ingName = typeof ing === 'string' ? ing : (ing.name || '');
                                  return ingName.length > 15 ? ingName.substring(0, 15) + '...' === label : ingName === label;
                                });
                              })();
                              return typeof item === 'string' ? item : (item?.name || label);
                            }}
                          />
                          <Legend />
                          <Bar dataKey="protein" stackId="a" fill="#22c55e" name="Protein" />
                          <Bar dataKey="carbs" stackId="a" fill="#f59e0b" name="Carbs" />
                          <Bar dataKey="fats" stackId="a" fill="#8b5cf6" name="Fats" />
                        </BarChart>
                      </ResponsiveContainer>
                    </Box>
                  </Box>
                  
                  <Box>
                    <Heading size="sm" mb={2}>Ingredient Macronutrients</Heading>
                    <VStack align="stretch" spacing={2}>
                      {(() => {
                        const selectedRecipeAny = selectedRecipe as any;
                        const currentServings = previewServings || selectedRecipeAny.servings || selectedRecipe.recipe?.servings || 1;
                        const originalServings = selectedRecipe.recipe?.servings || selectedRecipeAny.servings || 1;
                        const multiplier = currentServings / originalServings;
                        
                        // Nutrition per 100g lookup (same as in graph)
                        const per100g: Record<string, [number, number, number]> = {
                          'chicken breast': [31, 0, 3.6],
                          'chicken': [31, 0, 3.6],
                          'chickpea': [19, 61, 6],
                          'chickpeas': [19, 61, 6],
                          'olive oil': [0, 0, 100],
                          'oil': [0, 0, 100],
                          'tomato': [0.9, 3.9, 0.2],
                          'cucumber': [0.7, 3.6, 0.1],
                          'lettuce': [1.4, 2.9, 0.2],
                          'bell pepper': [1, 6, 0.3],
                          'pepper': [1, 6, 0.3],
                          'carrot': [0.9, 10, 0.2],
                          'onion': [1.1, 9.3, 0.1],
                          'garlic': [6.4, 33, 0.5],
                          'feta': [14, 4, 21],
                          'cheese': [20, 2, 25],
                          'hummus': [8, 14, 9.6],
                          'rice': [2.4, 28, 0.3],
                          'quinoa': [4.4, 21, 1.9],
                          'pasta': [5, 25, 1.1],
                          'yogurt': [10, 3.6, 0.4],
                          'egg': [6, 0.6, 5],
                          'eggs': [6, 0.6, 5],
                          'ham': [18, 1.5, 5],
                          'mushroom': [3.1, 3.3, 0.3],
                          'mushrooms': [3.1, 3.3, 0.3],
                          'bread': [9, 49, 3.2],
                          'rye bread': [9, 49, 3.2],
                          'swiss cheese': [25, 1.5, 27],
                          'mayonnaise': [1, 0.6, 75],
                          'mustard': [3.7, 5.8, 3.3],
                          'dill': [3.5, 7, 1.1],
                          'zucchini': [1.2, 3.1, 0.2],
                          'parsley': [3, 6, 0.8],
                        };
                        
                        return (selectedRecipe.ingredients || []).map((ingredient: any, index: number) => {
                          let name = '';
                          let quantity = 0;
                          let unit = 'g';
                          
                          if (typeof ingredient === 'string') {
                            name = ingredient;
                            quantity = 0;
                          } else {
                            name = ingredient.name || 'Unknown';
                            quantity = parseFloat(ingredient.quantity) || 0;
                            unit = ingredient.unit || 'g';
                            quantity = quantity * multiplier;
                          }
                          
                          // Convert to grams
                          let quantityInGrams = quantity;
                          if (unit.toLowerCase() === 'ml' || unit.toLowerCase() === 'l') {
                            quantityInGrams = quantity;
                          } else if (unit.toLowerCase() === 'kg') {
                            quantityInGrams = quantity * 1000;
                          } else if (unit.toLowerCase() === 'oz') {
                            quantityInGrams = quantity * 28.35;
                          } else if (unit.toLowerCase() === 'lb') {
                            quantityInGrams = quantity * 453.6;
                          } else if (unit.toLowerCase() === 'unit' || unit.toLowerCase() === 'units' || unit.toLowerCase() === 'piece' || unit.toLowerCase() === 'pieces') {
                            if (name.toLowerCase().includes('egg')) {
                              quantityInGrams = quantity * 50;
                            } else {
                              quantityInGrams = quantity * 100;
                            }
                          }
                          
                          // Calculate macronutrients
                          const nameLower = name.toLowerCase();
                          const match = Object.keys(per100g).find(k => nameLower.includes(k));
                          let protein = 0;
                          let carbs = 0;
                          let fats = 0;
                          
                          if (match && quantityInGrams > 0) {
                            const [p, c, f] = per100g[match];
                            const factor = quantityInGrams / 100.0;
                            protein = Math.round(p * factor * 10) / 10;
                            carbs = Math.round(c * factor * 10) / 10;
                            fats = Math.round(f * factor * 10) / 10;
                          }
                          
                          return (
                            <HStack key={index} justify="space-between" p={2} bg="gray.50" borderRadius="md">
                              <Text fontWeight="semibold">{name}</Text>
                              <HStack spacing={3}>
                                {protein > 0 && <Text fontSize="sm" color="green.600">P: {protein}g</Text>}
                                {carbs > 0 && <Text fontSize="sm" color="orange.600">C: {carbs}g</Text>}
                                {fats > 0 && <Text fontSize="sm" color="purple.600">F: {fats}g</Text>}
                                {(protein === 0 && carbs === 0 && fats === 0) && <Text fontSize="sm" color="gray.500">N/A</Text>}
                              </HStack>
                            </HStack>
                          );
                        });
                      })()}
                    </VStack>
                  </Box>
                </VStack>
              ) : (
                <Text color="gray.500">No ingredients available for this recipe.</Text>
              )}
            </ModalBody>
            <ModalFooter>
              <Button onClick={onIngredientGraphsClose}>Close</Button>
            </ModalFooter>
          </ModalContent>
        </Modal>

        {/* Ingredient Substitution Modal */}
        <Modal isOpen={isSubstitutionOpen} onClose={onSubstitutionClose} size="lg">
          <ModalOverlay />
          <ModalContent>
            <ModalHeader>
              <Text>Substitute: {substitutionIngredient}</Text>
            </ModalHeader>
            <ModalCloseButton />
            <ModalBody pb={6}>
              {loadingSubstitutions ? (
                <Box textAlign="center" py={8}>
                  <Spinner size="xl" color="blue.500" />
                  <Text mt={4} color="gray.600">Finding substitutions...</Text>
                </Box>
              ) : substitutionSuggestions.length > 0 ? (
                <VStack spacing={3} align="stretch">
                  <Text fontSize="sm" color="gray.600">
                    AI-generated substitution suggestions for <strong>{substitutionIngredient}</strong>:
                  </Text>
                  {substitutionSuggestions.map((suggestion: any, index: number) => (
                    <Card key={index} variant="outline">
                      <CardBody>
                        <VStack spacing={2} align="stretch">
                          <HStack justify="space-between">
                            <Text fontWeight="semibold">{suggestion.name}</Text>
                            <Badge colorScheme="green">{suggestion.quantity} {suggestion.unit}</Badge>
                          </HStack>
                          {suggestion.reason && (
                            <Text fontSize="sm" color="gray.600">{suggestion.reason}</Text>
                          )}
                          {suggestion.nutrition_adjustment && (
                            <Text fontSize="xs" color="gray.500" fontStyle="italic">
                              {typeof suggestion.nutrition_adjustment === 'object' 
                                ? (() => {
                                    const adj = suggestion.nutrition_adjustment;
                                    const changes = [];
                                    if (adj.calories_change) changes.push(`Calories: ${adj.calories_change > 0 ? '+' : ''}${adj.calories_change}`);
                                    if (adj.protein_change) changes.push(`Protein: ${adj.protein_change > 0 ? '+' : ''}${adj.protein_change}g`);
                                    if (adj.carbs_change) changes.push(`Carbs: ${adj.carbs_change > 0 ? '+' : ''}${adj.carbs_change}g`);
                                    if (adj.fats_change) changes.push(`Fats: ${adj.fats_change > 0 ? '+' : ''}${adj.fats_change}g`);
                                    return changes.length > 0 ? changes.join(', ') : 'Nutrition may change';
                                  })()
                                : suggestion.nutrition_adjustment}
                            </Text>
                          )}
                          <Button
                            size="sm"
                            colorScheme="blue"
                            onClick={() => applySubstitution(suggestion)}
                            isLoading={loading}
                          >
                            Use This Substitution
                          </Button>
                        </VStack>
                      </CardBody>
                    </Card>
                  ))}
                </VStack>
              ) : (
                <Text color="gray.500" textAlign="center" py={8}>
                  No substitution suggestions found. Try a different ingredient.
                </Text>
              )}
            </ModalBody>
          </ModalContent>
        </Modal>

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
