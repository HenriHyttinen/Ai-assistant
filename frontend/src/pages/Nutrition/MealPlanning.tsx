import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
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
import { 
  FiPlus, 
  FiRefreshCw,
  FiCoffee,
  FiRotateCcw,
  FiShoppingCart,
  FiGitBranch,
  FiTrash2
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
    try {
      const saved = typeof window !== 'undefined' ? localStorage.getItem('mealsPerDay') : null;
      return saved ? parseInt(saved, 10) : 4;
    } catch {
      return 4;
    }
  });
  
  // CRITICAL FIX: Persist mealsPerDay to localStorage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem('mealsPerDay', mealsPerDay.toString());
    } catch (e) {
      console.warn('Failed to save mealsPerDay to localStorage:', e);
    }
  }, [mealsPerDay]);
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
  
  // Recipe selector for adding recipes to grid
  const [recipeSelectorOpen, setRecipeSelectorOpen] = useState(false);
  const [selectedSlot, setSelectedSlot] = useState<{date: string, mealType: string} | null>(null);
  const [availableRecipes, setAvailableRecipes] = useState<any[]>([]);
  const [recipeSearch, setRecipeSearch] = useState('');

  // Simple swap state - first click selects meal, second click swaps
  const [swapMode, setSwapMode] = useState(false);
  const [swapSourceMeal, setSwapSourceMeal] = useState<{id: string, date: string, mealType: string} | null>(null);

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
      const { supabase } = await import('../../lib/supabase');
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
    
    // CRITICAL FIX: Normalize meal type for backend (morning snack -> snack)
    const normalizedMealType = mealType === 'morning snack' || mealType === 'afternoon snack' || mealType === 'evening snack' 
      ? 'snack' 
      : mealType.toLowerCase();
    
    const slotKey = `${date}-${mealType}`;
    try {
      setGeneratingMeals(prev => new Set(prev).add(slotKey));
      const { supabase } = await import('../../lib/supabase');
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
        
        toast({ 
          title: 'Meal Generated!', 
          description: `${result.meal.meal_name} added to ${dayName} ${mealType}`, 
          status: 'success', 
          duration: 2000, 
          isClosable: true 
        });
        setRecipeSelectorOpen(false);
        setSelectedSlot(null);
        
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
    }
  };

  const addRecipeToGrid = async (recipe: any) => {
    if (!selectedSlot || !mealPlan) return;
    
    try {
      setLoading(true);
      const { supabase } = await import('../../lib/supabase');
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
                const dayName = new Date(selectedSlot.date).toLocaleDateString(undefined, {weekday: 'long'});
                toast({ 
                  title: 'Recipe added successfully!', 
                  description: `Added to ${dayName} ${selectedSlot.mealType} - synced across all views`, 
                  status: 'success', 
                  duration: 3000, 
                  isClosable: true 
                });
                setRecipeSelectorOpen(false);
                setSelectedSlot(null);
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
      // CRITICAL: Also check recipe_details for preserved meal_type (morning snack/afternoon snack)
      const preservedType = m.recipe?.meal_type || m.recipe_details?.meal_type;
      const isSnack = t === 'snack' || t === 'morning snack' || t === 'afternoon snack' || t === 'evening snack' ||
                     preservedType === 'snack' || preservedType === 'morning snack' || preservedType === 'afternoon snack' || preservedType === 'evening snack';
      
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
            // ROOT CAUSE DEBUG: Log what preserved meal_type we're using
            const finalMealType = preservedType || t || 'snack';
            console.log(`🔍 Adding snack to snacksByDate: id=${mealId}, name='${m.meal_name || m.mealName}', preservedType='${preservedType}', t='${t}', finalMealType='${finalMealType}'`);
            
            // Store with preserved meal_type if available (for correct slot assignment)
            snacksByDate[d].push({
              ...m,
              // ROOT CAUSE FIX: Use preserved meal_type if available, otherwise use 'snack'
              // This ensures afternoon snack meals are stored with 'afternoon snack' type
              meal_type: finalMealType,
              type: finalMealType,
              // Also preserve the recipe and recipe_details so we can access them later
              recipe: m.recipe || {},
              recipe_details: m.recipe_details || {}
            });
          }
        }
      } else {
        nonSnackMeals.push(m);
      }
    });
    
    // First pass: honor explicit dates and try to match by meal type + position (non-snacks first)
    nonSnackMeals.forEach(m => {
      const d = m.meal_date || m.date;
      const t = (m.meal_type || m.type) as string;
      if (!d || !result[d] || !t) return;
      
      if (mealTypes.includes(t)) {
        // Find the first available slot with matching meal type
        for (let idx = 0; idx < mealTypes.length; idx++) {
          if (mealTypes[idx] === t && !result[d][idx]) {
            result[d][idx] = m;
            break;
          }
        }
      }
    });
    
    // CRITICAL FIX: Assign snacks to their specific slots based on preserved meal_type
    // First, create a map of snack slot types to indices
    const snackSlotMap: Record<string, number> = {};
    mealTypes.forEach((mt, idx) => {
      if (mt === 'morning snack' || mt === 'afternoon snack' || mt === 'evening snack' || mt === 'snack') {
        snackSlotMap[mt] = idx;
      }
    });
    
    // ROOT CAUSE DEBUG: Log snack slot map to verify it's correct
    console.log(`🔍 Snack slot map (mealTypes=${mealTypes.join(', ')})`, snackSlotMap);
    
    // Find snack slot indices in order (for fallback assignment)
    const snackSlotIndices: number[] = Object.values(snackSlotMap).sort((a, b) => a - b);
    
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
    
    // Assign snacks by date, prioritizing preserved meal_type
    // CRITICAL FIX: Track assigned meals globally across ALL dates to prevent duplicates across dates
    const globalAssignedMealIds = new Set<string | number>();
    
    Object.keys(snacksByDate).forEach(date => {
      const daySnacks = snacksByDate[date];
      if (!result[date] || snackSlotIndices.length === 0) return;
      
      // CRITICAL FIX: Track assigned meals for this date to prevent duplicates within the same date
      const dateAssignedMealIds = new Set<string | number>();
      
      // First pass: Assign snacks with preserved meal_type to matching slots
      const unassignedSnacks: any[] = [];
      daySnacks.forEach((snack) => {
        // CRITICAL: Skip if this meal is already assigned globally (prevent duplicates across dates)
        const snackId = snack.id || snack.meal_id || snack.mealId;
        if (snackId && globalAssignedMealIds.has(snackId)) {
          console.warn(`⚠️ Skipping meal ${snackId} '${snack.meal_name || snack.mealName}' - already assigned to another date/slot`);
          return; // Skip duplicates across dates
        }
        
        // CRITICAL: Also skip if already assigned on this date (prevent duplicates within same date)
        if (snackId && dateAssignedMealIds.has(snackId)) {
          console.warn(`⚠️ Skipping meal ${snackId} '${snack.meal_name || snack.mealName}' - already assigned to another slot on ${date}`);
          return; // Skip duplicates within same date
        }
        
        // Verify meal belongs to this date
        const snackDate = snack.meal_date || snack.date;
        if (snackDate !== date) {
          console.warn(`⚠️ Skipping meal ${snackId} '${snack.meal_name || snack.mealName}' - date mismatch: meal date=${snackDate}, target date=${date}`);
          return; // Skip if date doesn't match
        }
        
        // ROOT CAUSE FIX: Check preserved meal_type from recipe_details (backend stores it there)
        // Try multiple locations to find the preserved meal_type
        const preservedType = snack.recipe?.meal_type || snack.recipe_details?.meal_type || snack.meal_type || snack.type;
        
        // ROOT CAUSE FIX: Use preserved meal_type directly, don't fall back to 'snack'
        // This ensures we match the exact slot (morning snack vs afternoon snack)
        const snackType = preservedType || 'snack';
        
        // ROOT CAUSE DEBUG: Log what we're checking for slot assignment
        console.log(`🔍 Snack assignment check: snackId=${snackId}, name='${snack.meal_name || snack.mealName}', preservedType='${preservedType}', snackType='${snackType}', snackSlotMap=`, snackSlotMap);
        
        const targetSlotIdx = snackSlotMap[snackType];
        console.log(`🔍 targetSlotIdx=${targetSlotIdx}, slot already filled=${result[date]?.[targetSlotIdx] ? 'YES' : 'NO'}`);
        
        if (targetSlotIdx !== undefined && !result[date][targetSlotIdx]) {
          // Assign to specific slot based on preserved meal_type
          result[date][targetSlotIdx] = snack;
          if (snackId) {
            dateAssignedMealIds.add(snackId);
            globalAssignedMealIds.add(snackId);
          }
          console.log(`✅ Assigned snack ${snackId} '${snack.meal_name || snack.mealName}' to ${date} ${snackType} (slot ${targetSlotIdx})`);
        } else {
          // No matching slot or slot already filled - add to unassigned list
          if (targetSlotIdx === undefined) {
            console.warn(`⚠️ No matching slot found for snackType '${snackType}'. Available slots:`, Object.keys(snackSlotMap));
          } else if (result[date][targetSlotIdx]) {
            console.warn(`⚠️ Slot ${targetSlotIdx} (${snackType}) already filled for ${date}`);
          }
          unassignedSnacks.push(snack);
        }
      });
      
      // Second pass: Assign remaining snacks in order to available slots (only if not already assigned)
      // ROOT CAUSE FIX: Only assign each snack ONCE to the FIRST available slot
      unassignedSnacks.forEach((snack, snackOrder) => {
        // CRITICAL: Skip if this meal is already assigned globally or on this date
        const snackId = snack.id || snack.meal_id || snack.mealId;
        if (snackId && (globalAssignedMealIds.has(snackId) || dateAssignedMealIds.has(snackId))) {
          console.warn(`⚠️ Skipping unassigned snack ${snackId} '${snack.meal_name || snack.mealName}' - already assigned`);
          return; // Skip duplicates
        }
        
        // Verify meal belongs to this date
        const snackDate = snack.meal_date || snack.date;
        if (snackDate !== date) {
          console.warn(`⚠️ Skipping unassigned snack ${snackId} '${snack.meal_name || snack.mealName}' - date mismatch: meal date=${snackDate}, target date=${date}`);
          return; // Skip if date doesn't match
        }
        
        // ROOT CAUSE FIX: Find the FIRST available slot for this snack and assign it ONCE, then break
        // Double-check: Ensure snack is not already assigned before proceeding
        let isAlreadyAssigned = false;
        for (let checkIdx = 0; checkIdx < mealTypes.length; checkIdx++) {
          if (result[date] && result[date][checkIdx] && 
              (result[date][checkIdx].id === snackId || 
               result[date][checkIdx].meal_id === snackId || 
               result[date][checkIdx].mealId === snackId)) {
            isAlreadyAssigned = true;
            console.warn(`⚠️ Snack ${snackId} '${snack.meal_name || snack.mealName}' already assigned to ${date} slot ${checkIdx} - skipping`);
            break;
          }
        }
        
        if (isAlreadyAssigned) {
          return; // Already assigned, skip
        }
        
        if (snackOrder < snackSlotIndices.length) {
          // Find the first available slot
          for (let i = 0; i < snackSlotIndices.length; i++) {
            const targetSlot = snackSlotIndices[i];
            if (!result[date][targetSlot]) {
              // Found available slot - assign snack and STOP
              result[date][targetSlot] = snack;
              if (snackId) {
                dateAssignedMealIds.add(snackId);
                globalAssignedMealIds.add(snackId);
              }
              console.log(`✅ Assigned unassigned snack ${snackId} '${snack.meal_name || snack.mealName}' to ${date} slot ${targetSlot} (snackOrder=${snackOrder}, foundSlot=${i})`);
              break; // CRITICAL: Stop after assigning to first available slot
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
        const { supabase } = await import('../../lib/supabase');
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
          setPreferences({
            dietaryRestrictions: prefs.dietary_preferences || [],
            allergies: prefs.allergies || [],
            cuisinePreferences: prefs.cuisine_preferences || [],
            calorieTarget: prefs.daily_calorie_target || prefs.calorie_target || 2000,
            mealsPerDay: prefs.meals_per_day || 4
          });
          console.log('📊 Loaded user preferences:', {
            calorieTarget: prefs.daily_calorie_target || prefs.calorie_target || 2000,
            mealsPerDay: prefs.meals_per_day || 4
          });
        }
      } catch (error) {
        console.warn('Failed to load user preferences:', error);
      }
    };

    loadUserPreferences();
  }, []);

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
      const { supabase } = await import('../../lib/supabase');
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
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        setError('Please log in to generate meal plans');
        toast({ title: 'Please log in', status: 'warning', duration: 2500, isClosable: true });
        return;
      }
      
      const headers = { Authorization: `Bearer ${session.access_token}` };
      console.log('🚀 PROGRESSIVE GENERATION: Creating meal plan structure first (lighter approach)');
      console.log('Calorie target:', preferences.calorieTarget);
      
      // STEP 1: Create empty meal plan structure first (lightweight - PROGRESSIVE MODE)
      const createResponse = await fetch(`http://localhost:8000/nutrition/meal-plans/generate?progressive=true`, {
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
        return; // Exit early - user fills slots progressively
      } else {
        // Structure creation failed
        const errorData = await createResponse.json().catch(() => ({ detail: 'Failed to create meal plan structure' }));
        if (createResponse.status === 400 && errorData.detail && errorData.detail.includes('nutrition preferences')) {
          setError('Please set up your nutrition preferences first. Go to the Nutrition Dashboard to configure your preferences.');
          toast({ title: 'Set up nutrition preferences first', status: 'info', duration: 3000, isClosable: true });
        } else {
          throw new Error(errorData.detail || 'Failed to create meal plan structure');
        }
      }
    } catch (err) {
      console.error('Error generating meal plan:', err);
      setError('Failed to generate meal plan');
      toast({ title: 'Failed to generate meal plan', status: 'error', duration: 3000, isClosable: true });
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

  const handleMealEdit = (meal: Meal) => {
    setSelectedMeal(meal);
    onOpen();
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
    
    // Always allow preview - no need to check for meal ID
    const currentServings = selectedRecipe.servings || selectedRecipe.recipe?.servings || 1;
    const multiplier = newServings / currentServings;
    
    // Preview the adjusted nutrition
    const previewCalories = Math.round((selectedRecipe.calories || selectedRecipe.per_serving_calories || 0) * multiplier);
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

    setSelectedRecipe(normalized as any);
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
      const { supabase } = await import('../../lib/supabase');
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
    if (!mealPlan?.id || !mealId) return;
    
    // First click: enter swap mode and select source meal
    if (!swapMode || !swapSourceMeal) {
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
    
    // Perform swap via API
    try {
      const { supabase } = await import('../../lib/supabase');
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
        
        // Reload meal plan to reflect changes
        await loadMealPlan();
        
        // Exit swap mode
        setSwapMode(false);
        setSwapSourceMeal(null);
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
      const { supabase } = await import('../../lib/supabase');
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

  const moveMealToDate = async (mealId: string | number | undefined, targetDate: string, targetMealType?: string) => {
    if (!mealPlan) return;
    if (!mealId) {
      toast({ title: 'Meal ID is missing', status: 'error', duration: 2500, isClosable: true });
      return;
    }
    try {
      const { supabase } = await import('../../lib/supabase');
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
        // Reload meal plan to get updated data
        await loadMealPlan();
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
      const { supabase } = await import('../../lib/supabase');
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

  const handleLogDayToDailyIntake = async (date: string) => {
    if (!mealPlan) return;
    setLoading(true);
    try {
      const { supabase } = await import('../../lib/supabase');
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

  const handleFixDailyTotal = async (date: string) => {
    if (!mealPlan) return;
    setLoading(true);
    try {
      const { supabase } = await import('../../lib/supabase');
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
              const { supabase } = await import('../../lib/supabase');
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
                )}
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
                  onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setMealsPerDay(parseInt(e.target.value, 10))}
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
                        const { supabase } = await import('../../lib/supabase');
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
              {!mealPlan && (
                <Button 
                  colorScheme="blue" 
                  leftIcon={<FiCoffee />}
                  onClick={async () => {
                    // Auto-create empty meal plan structure for progressive generation
                    await generateMealPlan();
                  }}
                  isLoading={loading}
                  size="sm"
                >
                  Create Meal Plan Structure
                </Button>
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
                  <Button
                    colorScheme="blue"
                    size="lg"
                    leftIcon={<FiCoffee />}
                    onClick={async () => {
                      await generateMealPlan();
                    }}
                    isLoading={loading}
                  >
                    Create Meal Plan Structure
                  </Button>
                  <Text fontSize="sm" color="gray.400">
                    After creating the structure, click "Generate Recipe" or "Pick from Database" on each meal slot
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
                                        isLoading={loading || (generatingMeals.has(`${d}-${slotIdx}-${slot}`))}
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
                                  <Button 
                                    size={mealsPerDay > 4 ? "2xs" : "xs"} 
                                    variant="outline" 
                                    colorScheme="blue"
                                    onClick={() => generateMealSlot(d, slot)}
                                    isLoading={loading || (generatingMeals.has(`${d}-${slotIdx}-${slot}`))}
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
              <VStack align="start" spacing={1} pr={8}>
                <Text>{selectedRecipe?.title || selectedRecipe?.meal_name || selectedRecipe?.name || 'Recipe Details'}</Text>
                <HStack spacing={2}>
                {selectedRecipe?.database_fallback ? (
                  <Badge colorScheme="blue" variant="subtle">Database</Badge>
                ) : selectedRecipe?.ai_generated !== false ? (
                  <Badge colorScheme="purple" variant="subtle">AI Generated</Badge>
                ) : (
                  <Badge colorScheme="green" variant="subtle">Recipe Database</Badge>
                )}
              </HStack>
              </VStack>
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
                          {selectedRecipe.per_serving_calories ?? 
                           selectedRecipe.recipe?.per_serving_calories ??
                           selectedRecipe.calories ?? 
                           selectedRecipe.nutrition?.calories ?? 
                           0}
                        </Text>
                      </Box>
                      <Box p={3} bg="green.50" borderRadius="md">
                        <Text fontSize="sm" color="gray.600">Protein</Text>
                        <Text fontSize="lg" fontWeight="bold">
                          {selectedRecipe.per_serving_protein ?? 
                           selectedRecipe.recipe?.per_serving_protein ??
                           selectedRecipe.protein ?? 
                           selectedRecipe.nutrition?.protein ?? 
                           0}g
                        </Text>
                      </Box>
                      <Box p={3} bg="orange.50" borderRadius="md">
                        <Text fontSize="sm" color="gray.600">Carbs</Text>
                        <Text fontSize="lg" fontWeight="bold">
                          {selectedRecipe.per_serving_carbs ?? 
                           selectedRecipe.recipe?.per_serving_carbs ??
                           selectedRecipe.carbs ?? 
                           selectedRecipe.nutrition?.carbs ?? 
                           0}g
                        </Text>
                      </Box>
                      <Box p={3} bg="purple.50" borderRadius="md">
                        <Text fontSize="sm" color="gray.600">Fats</Text>
                        <Text fontSize="lg" fontWeight="bold">
                          {selectedRecipe.per_serving_fat ?? 
                           selectedRecipe.per_serving_fats ??
                           selectedRecipe.recipe?.per_serving_fat ??
                           selectedRecipe.recipe?.per_serving_fats ??
                           selectedRecipe.fats ?? 
                           selectedRecipe.nutrition?.fats ?? 
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
                            const newServings = (selectedRecipe.servings || selectedRecipe.recipe?.servings || 1) as number;
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
                          const currentServings = selectedRecipe.servings || selectedRecipe.recipe?.servings || 1;
                          const newServings = Math.max(0.25, currentServings - 0.25);
                          handleServingsChange(newServings);
                        }}
                        isDisabled={loading}
                      >
                        −
                      </Button>
                      
                      <FormControl width="100px">
                        <NumberInput
                          value={selectedRecipe.servings || selectedRecipe.recipe?.servings || 1}
                          min={0.25}
                          max={10}
                          step={0.25}
                          precision={2}
                          onChange={(valueString, valueNumber) => {
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
                        serving{((selectedRecipe.servings || selectedRecipe.recipe?.servings || 1) !== 1) ? 's' : ''}
                      </Text>
                      
                      <Button
                        size="sm"
                        colorScheme="blue"
                        borderRadius="full"
                        width="32px"
                        height="32px"
                        fontSize="md"
                        onClick={() => {
                          const currentServings = selectedRecipe.servings || selectedRecipe.recipe?.servings || 1;
                          const newServings = Math.min(10, currentServings + 0.25);
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
                          const originalServings = selectedRecipe.recipe?.servings || 1;
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
                          const currentServings = selectedRecipe.servings || selectedRecipe.recipe?.servings || 1;
                          const originalServings = (ingredient.original_servings || selectedRecipe.recipe?.servings || ingredient.servings || 1);
                          const multiplier = currentServings / originalServings;
                          const adjustedQuantity = typeof ingredient === 'object' && ingredient.quantity 
                            ? (multiplier !== 1 ? (ingredient.quantity * multiplier).toFixed(1) : ingredient.quantity)
                            : null;
                          
                          return (
                            <Text key={index} pl={4} borderLeft="3px solid" borderColor="blue.200">
                              {typeof ingredient === 'string' 
                                ? ingredient 
                                : `${ingredient.name} - ${adjustedQuantity || ingredient.quantity}${ingredient.unit || 'g'}${multiplier !== 1 && (selectedRecipe as any).previewCalories ? ' (adjusted)' : ''}`
                              }
                            </Text>
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
                          const text = `${(selectedRecipe?.title || selectedRecipe?.meal_name || '')}`.toLowerCase() + ' ' + ingredientsList.join(' ');
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
