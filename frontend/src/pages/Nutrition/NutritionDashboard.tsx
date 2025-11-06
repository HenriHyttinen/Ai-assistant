import React, { useState, useEffect, useMemo } from 'react';
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
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Divider,
  useColorModeValue,
  Alert,
  AlertIcon,
  Spinner,
  Center
} from '@chakra-ui/react';
import { t } from '../../utils/translations';
import { 
  FiTrendingUp, 
  FiTarget, 
  FiClock, 
  FiShoppingCart,
  FiHeart,
  FiActivity,
  FiCoffee,
  FiPieChart,
  FiZap,
  FiPlus
} from 'react-icons/fi';
import MicronutrientAnalysis from '../../components/nutrition/MicronutrientAnalysis';
import MacronutrientVisualization from '../../components/nutrition/MacronutrientVisualization';

interface NutritionalData {
  calories: number;
  protein: number;
  carbs: number;
  fats: number;
  fiber: number;
  sugar: number;
  sodium: number;
}

interface MealPlan {
  id: string;
  date: string;
  meals: Array<{
    id: string;
    name: string;
    type: string;
    calories: number;
    protein: number;
    carbs: number;
    fats: number;
  }>;
  totalCalories: number;
  totalProtein: number;
  totalCarbs: number;
  totalFats: number;
}

interface NutritionDashboardProps {
  user?: any;
}

const NutritionDashboard: React.FC<NutritionDashboardProps> = ({ user = null }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [nutritionalData, setNutritionalData] = useState<NutritionalData | null>(null);
  const [mealPlan, setMealPlan] = useState<MealPlan | null>(null);
  const [goals, setGoals] = useState({
    calories: 2000,
    protein: 150,
    carbs: 250,
    fats: 65
  });
  const [activeTab, setActiveTab] = useState<'overview' | 'micronutrients'>('overview');
  const [showAllMeals, setShowAllMeals] = useState(false);
  const [dailyLogEntries, setDailyLogEntries] = useState<any[]>([]); // CRITICAL FIX: Add missing state

  // (moved todayTotals below gridAssignments to avoid temporal dead zone)

  // Build a 7x4 assignment for weekly plans (same logic as MealPlanning)
  const gridAssignments = useMemo(() => {
    if (!mealPlan || mealPlan.plan_type !== 'weekly') return {};
    
    const start = new Date(mealPlan.start_date || mealPlan.date);
    const weekDates: string[] = [];
    for (let i = 0; i < 7; i++) {
      const d = new Date(start);
      d.setDate(start.getDate() + i);
      weekDates.push(d.toISOString().split('T')[0]);
    }
    
    const result: Record<string, Record<'breakfast'|'lunch'|'dinner'|'snack', any | null>> = {};
    weekDates.forEach(d => {
      result[d] = { breakfast: null, lunch: null, dinner: null, snack: null };
    });
    
    const all = (mealPlan?.meals || []) as any[];
    // First pass: honor explicit dates
    all.forEach(m => {
      const d = m.meal_date || m.date;
      const t = (m.meal_type || m.type) as 'breakfast'|'lunch'|'dinner'|'snack';
      if (d && result[d] && t && !result[d][t]) {
        result[d][t] = m;
      }
    });
    
    // Second pass: assign remaining by round-robin per type
    const remainingByType: Record<string, any[]> = { breakfast: [], lunch: [], dinner: [], snack: [] } as any;
    all.forEach(m => {
      const d = m.meal_date || m.date;
      const t = (m.meal_type || m.type) as keyof typeof remainingByType;
      if (!t) return;
      const alreadyPlaced = d && result[d] && Object.values(result[d]).includes(m);
      if (!alreadyPlaced) remainingByType[t].push(m);
    });
    
    (['breakfast','lunch','dinner','snack'] as const).forEach(slot => {
      let idx = 0;
      remainingByType[slot].forEach(m => {
        for (let i = 0; i < weekDates.length; i++) {
          const day = weekDates[(idx + i) % weekDates.length];
          if (!result[day][slot]) {
            result[day][slot] = m;
            idx = (idx + i + 1) % weekDates.length;
            break;
          }
        }
      });
    });
    
    return result;
  }, [mealPlan]);

  // CRITICAL FIX: Derive today's totals from meal plan AND daily log entries
  const todayTotals = useMemo(() => {
    const today = new Date().toISOString().split('T')[0];
    let meals: any[] = [];
    
    // Get meals from meal plan
    if (mealPlan) {
      if (mealPlan.plan_type === 'weekly' && Object.keys(gridAssignments).length > 0) {
        const todayMeals = gridAssignments[today] || {};
        meals = Object.values(todayMeals).filter(Boolean);
      } else {
        const all = (mealPlan.meals || []) as any[];
        meals = all.filter((m: any) => {
          const d = m.meal_date || m.date || mealPlan.date;
          return d?.slice(0, 10) === today;
        });
      }
    }
    
    // CRITICAL FIX: Add daily log entries to totals
    const logMeals = dailyLogEntries.map((entry: any) => ({
      calories: entry.calories || 0,
      protein: entry.protein || 0,
      carbs: entry.carbs || 0,
      fats: entry.fats || 0,
    }));
    
    // Combine meal plan meals and daily log entries
    const allMeals = [...meals, ...logMeals];
    
    if (!allMeals.length) {
      // Fallback to nutritional analysis data if available
      return {
        calories: nutritionalData?.calories || 0,
        protein: nutritionalData?.protein || 0,
        carbs: nutritionalData?.carbs || 0,
        fats: nutritionalData?.fats || 0,
      };
    }
    
    const sum = (arr: any[], key: 'calories'|'protein'|'carbs'|'fats') =>
      arr.reduce((s, m) => {
        const value = m[key] || m.recipe?.nutrition?.[key] || 0;
        return s + (typeof value === 'number' ? value : 0);
      }, 0);
    
    return {
      calories: sum(allMeals, 'calories'),
      protein: sum(allMeals, 'protein'),
      carbs: sum(allMeals, 'carbs'),
      fats: sum(allMeals, 'fats'),
    };
  }, [mealPlan, gridAssignments, dailyLogEntries, nutritionalData]);

  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    loadNutritionData();
  }, []);

  // CRITICAL FIX: Listen for meal plan updates from other pages
  useEffect(() => {
    const handleMealPlanUpdate = () => {
      console.log('🔄 Meal plan updated, reloading dashboard...');
      loadNutritionData();
    };
    
    // Listen for custom events when meal plan is updated
    window.addEventListener('mealPlanUpdated', handleMealPlanUpdate);
    window.addEventListener('dailyLogUpdated', handleMealPlanUpdate);
    
    return () => {
      window.removeEventListener('mealPlanUpdated', handleMealPlanUpdate);
      window.removeEventListener('dailyLogUpdated', handleMealPlanUpdate);
    };
  }, []);

  const setupDefaultPreferences = async () => {
    try {
      // Get Supabase session token for authentication
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      const headers = session?.access_token ? { Authorization: `Bearer ${session.access_token}` } : {};
      
      // Create default nutrition preferences
      const defaultPreferences = {
        dietary_preferences: [],
        allergies: [],
        disliked_ingredients: [],
        cuisine_preferences: ["International"],
        daily_calorie_target: 2000,
        protein_target: 150,
        carbs_target: 250,
        fats_target: 65,
        meals_per_day: 3,
        preferred_meal_times: {
          breakfast: "08:00",
          lunch: "13:00",
          dinner: "19:00"
        },
        timezone: "UTC"
      };
      
      const response = await fetch('http://localhost:8000/nutrition/preferences', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...headers
        },
        body: JSON.stringify(defaultPreferences)
      });
      
      if (response.ok) {
        console.log('Default nutrition preferences created successfully');
      } else {
        console.error('Failed to create default preferences:', response.status);
      }
    } catch (error) {
      console.error('Error setting up default preferences:', error);
    }
  };

  const loadNutritionData = async () => {
    try {
      setLoading(true);
      
      // Get Supabase session token for authentication
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        console.error('No Supabase session found');
        setError('Please log in to access nutrition features');
        return;
      }
      
      const headers = { Authorization: `Bearer ${session.access_token}` };
      console.log('Using Supabase token for nutrition API calls');
      
      // Load nutrition preferences
      const preferencesResponse = await fetch('http://localhost:8000/nutrition/preferences', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...headers
        }
      });
      
      if (preferencesResponse.ok) {
        const preferences = await preferencesResponse.json();
        setGoals({
          calories: preferences.daily_calorie_target || 2000,
          protein: preferences.protein_target || 150,
          carbs: preferences.carbs_target || 250,
          fats: preferences.fats_target || 65
        });
      } else if (preferencesResponse.status === 404) {
        // User doesn't have preferences yet - use defaults
        console.log('No nutrition preferences found, using defaults');
        setGoals({
          calories: 2000,
          protein: 150,
          carbs: 250,
          fats: 65
        });
        
        // Set up default nutrition preferences
        await setupDefaultPreferences();
      } else if (preferencesResponse.status === 401) {
        // Not authenticated - show error
        setError('Please log in to access nutrition features');
        return;
      }
      
      // Load today's meal plan
      const today = new Date().toISOString().split('T')[0];
      const mealPlanResponse = await fetch(`http://localhost:8000/nutrition/meal-plans?date=${today}&limit=1`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...headers
        }
      });
      
      if (mealPlanResponse.ok) {
        const byDate = await mealPlanResponse.json();
        const todayStr = today;
        const pickMealsForToday = (plan: any) => {
          const meals = (plan?.meals || []).filter((m: any) => {
            const d = m?.meal_date || m?.date || plan?.date;
            return (d || '').slice(0, 10) === todayStr;
          });
          return { plan, meals };
        };

        if (byDate.length > 0) {
          const chosen = pickMealsForToday(byDate[0]);
          if (chosen.meals.length > 0) {
            setMealPlan(byDate[0]);
            console.log('✅ Loaded meal plan with', chosen.meals.length, 'meals for today');
          } else {
            // CRITICAL FIX: Fallback to latest weekly plan that contains today
            const weeklyResp = await fetch('http://localhost:8000/nutrition/meal-plans?plan_type=weekly&limit=1', {
              method: 'GET',
              headers: { 'Content-Type': 'application/json', ...headers }
            });
            if (weeklyResp.ok) {
              const weekly = await weeklyResp.json();
              if (weekly.length > 0) {
                const weeklyPlan = weekly[0];
                const weeklyMeals = pickMealsForToday(weeklyPlan);
                if (weeklyMeals.meals.length > 0) {
                  setMealPlan(weeklyPlan);
                  console.log('✅ Loaded weekly meal plan with', weeklyMeals.meals.length, 'meals for today');
                } else {
                  console.log('⚠️ Weekly plan found but no meals for today');
                }
              }
            }
          }
        } else {
          // CRITICAL FIX: If no plan found by date, try weekly plan
          console.log('⚠️ No meal plan found for date, trying weekly plan...');
          const weeklyResp = await fetch('http://localhost:8000/nutrition/meal-plans?plan_type=weekly&limit=1', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json', ...headers }
          });
          if (weeklyResp.ok) {
            const weekly = await weeklyResp.json();
            if (weekly.length > 0) {
              const weeklyPlan = weekly[0];
              const weeklyMeals = pickMealsForToday(weeklyPlan);
              if (weeklyMeals.meals.length > 0) {
                setMealPlan(weeklyPlan);
                console.log('✅ Loaded weekly meal plan with', weeklyMeals.meals.length, 'meals for today');
              }
            }
          }
        }
      }
      
      // CRITICAL FIX: Load daily log entries for today (not just meal plan meals)
      const dailyLogResponse = await fetch(`http://localhost:8000/daily-logging/daily-log/${today}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...headers
        }
      });
      
      let dailyLogEntries: any[] = [];
      if (dailyLogResponse.ok) {
        const dailyLogData = await dailyLogResponse.json();
        dailyLogEntries = dailyLogData.entries || [];
        console.log('📊 Loaded daily log entries:', dailyLogEntries.length);
      }
      
      // Store daily log entries in state for display
      setDailyLogEntries(dailyLogEntries);
      
      // Load nutritional analysis for today
      const analysisResponse = await fetch(`http://localhost:8000/nutrition/nutritional-analysis?start_date=${today}&end_date=${today}&analysis_type=daily`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          ...headers
        }
      });
      
      if (analysisResponse.ok) {
        const analysis = await analysisResponse.json();
        setNutritionalData({
          calories: analysis.totals?.calories || 0,
          protein: analysis.totals?.protein || 0,
          carbs: analysis.totals?.carbs || 0,
          fats: analysis.totals?.fats || 0,
          fiber: analysis.totals?.fiber || 0,
          sugar: analysis.totals?.sugar || 0,
          sodium: analysis.totals?.sodium || 0
        });
      } else {
        // Fallback to mock data if API fails
        setNutritionalData({
          calories: 1850,
          protein: 120,
          carbs: 180,
          fats: 55,
          fiber: 25,
          sugar: 45,
          sodium: 2100
        });
      }

      setError(null);
    } catch (err) {
      console.error('Error loading nutrition data:', err);
      setError('Failed to load nutrition data');
      
      // Fallback to mock data
      setNutritionalData({
        calories: 1850,
        protein: 120,
        carbs: 180,
        fats: 55,
        fiber: 25,
        sugar: 45,
        sodium: 2100
      });
    } finally {
      setLoading(false);
    }
  };

  const getCalorieProgress = () => {
    if (!nutritionalData) return 0;
    return Math.min((nutritionalData.calories / goals.calories) * 100, 100);
  };

  const getMacroProgress = (current: number, target: number) => {
    return Math.min((current / target) * 100, 100);
  };

  const getProgressColor = (progress: number) => {
    if (progress < 80) return 'red';
    if (progress < 100) return 'yellow';
    return 'green';
  };

  if (loading) {
    return (
      <Center h="400px">
        <VStack spacing={4}>
          <Spinner size="xl" />
          <Text>{t('nutrition.loading', 'en')}</Text>
        </VStack>
      </Center>
    );
  }

  if (error) {
    return (
      <Alert status="error">
        <AlertIcon />
        {error}
      </Alert>
    );
  }

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <Box>
          <Heading size="lg" mb={2}>
            {t('nutrition.dashboard.title', 'en')}
          </Heading>
          <Text color="gray.600">
            {t('nutrition.dashboard.subtitle', 'en')}
          </Text>
        </Box>

        {/* Navigation Tabs */}
        <HStack spacing={4} mb={4}>
          <Button
            variant={activeTab === 'overview' ? 'solid' : 'outline'}
            colorScheme="blue"
            leftIcon={<FiPieChart />}
            onClick={() => setActiveTab('overview')}
          >
            Overview
          </Button>
          <Button
            variant={activeTab === 'micronutrients' ? 'solid' : 'outline'}
            colorScheme="purple"
            leftIcon={<FiZap />}
            onClick={() => setActiveTab('micronutrients')}
          >
            Micronutrients
          </Button>
        </HStack>

        {/* Content based on active tab */}
        {activeTab === 'overview' ? (
          <>
            {/* Quick Stats */}
            <Grid templateColumns={{ base: '1fr', md: 'repeat(4, 1fr)' }} gap={4}>
          <Card bg={cardBg} borderColor={borderColor}>
            <CardBody>
              <Stat>
                <StatLabel>{t('nutrition.calories', 'en')}</StatLabel>
                <StatNumber>{todayTotals.calories}</StatNumber>
                <StatHelpText>
                  <Progress 
                    value={Math.min((todayTotals.calories / goals.calories) * 100, 100)} 
                    colorScheme={getProgressColor(Math.min((todayTotals.calories / goals.calories) * 100, 100))}
                    size="sm"
                  />
                  {Math.round(Math.min((todayTotals.calories / goals.calories) * 100, 100))}% of {goals.calories}
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={borderColor}>
            <CardBody>
              <Stat>
                <StatLabel>{t('nutrition.protein', 'en')}</StatLabel>
                <StatNumber>{todayTotals.protein}g</StatNumber>
                <StatHelpText>
                  <Progress 
                    value={getMacroProgress(todayTotals.protein, goals.protein)} 
                    colorScheme={getProgressColor(getMacroProgress(todayTotals.protein, goals.protein))}
                    size="sm"
                  />
                  {Math.round(getMacroProgress(todayTotals.protein, goals.protein))}% of {goals.protein}g
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={borderColor}>
            <CardBody>
              <Stat>
                <StatLabel>{t('nutrition.carbs', 'en')}</StatLabel>
                <StatNumber>{todayTotals.carbs}g</StatNumber>
                <StatHelpText>
                  <Progress 
                    value={getMacroProgress(todayTotals.carbs, goals.carbs)} 
                    colorScheme={getProgressColor(getMacroProgress(todayTotals.carbs, goals.carbs))}
                    size="sm"
                  />
                  {Math.round(getMacroProgress(todayTotals.carbs, goals.carbs))}% of {goals.carbs}g
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={borderColor}>
            <CardBody>
              <Stat>
                <StatLabel>{t('nutrition.fats', 'en')}</StatLabel>
                <StatNumber>{todayTotals.fats}g</StatNumber>
                <StatHelpText>
                  <Progress 
                    value={getMacroProgress(todayTotals.fats, goals.fats)} 
                    colorScheme={getProgressColor(getMacroProgress(todayTotals.fats, goals.fats))}
                    size="sm"
                  />
                  {Math.round(getMacroProgress(todayTotals.fats, goals.fats))}% of {goals.fats}g
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </Grid>

        {/* Today's Meal Plan (compact, collapsible) */}
        <Card bg={cardBg} borderColor={borderColor}>
          <CardHeader>
            <HStack justify="space-between">
              <Heading size="md">Today's Meals</Heading>
              {!mealPlan && (
                <Button
                  size="sm"
                  colorScheme="blue"
                  leftIcon={<FiCoffee />}
                  onClick={() => {
                    // Navigate to Meal Planning tab
                    const event = new CustomEvent('navigateToTab', { detail: { tabIndex: 2 } });
                    window.dispatchEvent(event);
                  }}
                >
                  Create Meal Plan
                </Button>
              )}
            </HStack>
          </CardHeader>
          <CardBody>
            {mealPlan ? (
              <VStack spacing={4} align="stretch">
                {(() => {
                  const today = new Date().toISOString().split('T')[0];
                  
                  // Use grid assignments for weekly plans, fallback to old logic for daily
                  let meals: any[] = [];
                  if (mealPlan.plan_type === 'weekly' && Object.keys(gridAssignments).length > 0) {
                    // Get today's meals from grid assignments
                    const todayMeals = gridAssignments[today] || {};
                    meals = Object.values(todayMeals).filter(Boolean);
                  } else {
                    // Fallback to old logic for daily plans
                    const all = mealPlan.meals || [];
                    meals = all.filter((m: any) => {
                      const d = m.meal_date || m.date || mealPlan.date;
                      return d?.slice(0, 10) === today;
                    });
                  }
                  
                  // CRITICAL FIX: Include daily log entries in the meals list
                  // Convert daily log entries to meal format for display
                  const logMeals = dailyLogEntries.map((entry: any) => ({
                    id: entry.id || `log_${entry.food_name}_${entry.meal_type}`,
                    meal_name: entry.food_name,
                    meal_type: entry.meal_type,
                    date: today,
                    meal_date: today,
                    calories: entry.calories || 0,
                    protein: entry.protein || 0,
                    carbs: entry.carbs || 0,
                    fats: entry.fats || 0,
                    is_daily_log: true // Flag to identify daily log entries
                  }));
                  
                  // Combine meal plan meals and daily log entries
                  const allMeals = [...meals, ...logMeals];
                  
                  const visible = showAllMeals ? allMeals : allMeals.slice(0, 6);
                  return (
                    <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)' }} gap={3}>
                      {visible.map((meal: any) => {
                        const title = meal.name || meal.meal_name || meal.recipe?.title || 'Meal';
                        const type = meal.type || meal.meal_type || 'meal';
                        const calories = meal.calories || meal.recipe?.nutrition?.calories || 0;
                        const protein = meal.protein || meal.recipe?.nutrition?.protein || 0;
                        const carbs = meal.carbs || meal.recipe?.nutrition?.carbs || 0;
                        const fats = meal.fats || meal.recipe?.nutrition?.fats || 0;
                        return (
                          <Box key={(meal.id ?? `${meal.meal_plan_id || 'mp'}_${(meal.meal_type || type)}_${(meal.meal_date || meal.date || new Date().toISOString().split('T')[0])}_${title}`)} p={3} borderWidth={1} borderRadius="md" borderColor={borderColor} _hover={{ bg: 'gray.50' }}>
                            <HStack justify="space-between" mb={1}>
                              <VStack align="start" spacing={0}>
                                <Text fontWeight="semibold" noOfLines={1}>{title}</Text>
                                <Badge colorScheme="blue" size="xs" textTransform="capitalize">{type}</Badge>
                              </VStack>
                              <Text fontSize="sm" color="gray.600" fontWeight="bold">{calories} cal</Text>
                            </HStack>
                            <HStack spacing={3} fontSize="xs" color="gray.600">
                              <Text>{protein}g protein</Text>
                              <Text>{carbs}g carbs</Text>
                              <Text>{fats}g fats</Text>
                            </HStack>
                          </Box>
                        );
                      })}
                    </Grid>
                  );
                })()}
                <Divider />
                <HStack justify="space-between" fontWeight="bold" p={2} bg="gray.50" borderRadius="md">
                  <Text>Total</Text>
                  <HStack>
                  <Text>{todayTotals.calories} calories</Text>
                  {(() => {
                    // CRITICAL FIX: Use todayTotals which includes both meal plan and daily log entries
                    const total = todayTotals.calories;
                    const target = goals.calories || 2000;
                    return total < target * 0.95 ? (
                      <Button size="xs" variant="outline" colorScheme="green"
                        onClick={async () => {
                          try {
                            const { supabase } = await import('../../lib/supabase.ts');
                            const { data: { session } } = await supabase.auth.getSession();
                            if (!session?.access_token || !mealPlan?.id) return;
                            const today = new Date().toISOString().split('T')[0];
                            await fetch(`http://localhost:8000/nutrition/meal-plans/${mealPlan.id}/top-up?meal_date=${today}`, {
                              method: 'POST',
                              headers: { 'Authorization': `Bearer ${session.access_token}` }
                            });
                            // reload latest weekly plan
                            const weeklyResp = await fetch('http://localhost:8000/nutrition/meal-plans?plan_type=weekly&limit=1', { headers: { 'Authorization': `Bearer ${session.access_token}` }});
                            if (weeklyResp.ok) {
                              const weekly = await weeklyResp.json();
                              if (weekly.length > 0) setMealPlan(weekly[0]);
                            }
                          } catch {}
                        }}
                      >Top up to target</Button>
                    ) : null;
                  })()}
                  </HStack>
                </HStack>
                {(() => {
                  const today = new Date().toISOString().split('T')[0];
                  
                  // Use same logic as above for consistency
                  let meals: any[] = [];
                  if (mealPlan.plan_type === 'weekly' && Object.keys(gridAssignments).length > 0) {
                    const todayMeals = gridAssignments[today] || {};
                    meals = Object.values(todayMeals).filter(Boolean);
                  } else {
                    const all = mealPlan.meals || [];
                    meals = all.filter((m: any) => {
                      const d = m.meal_date || m.date || mealPlan.date;
                      return d?.slice(0, 10) === today;
                    });
                  }
                  
                  return meals.length > 6;
                })() && (
                  <Button size="sm" variant="outline" onClick={() => setShowAllMeals(!showAllMeals)}>
                    {showAllMeals ? 'Show Less' : (() => {
                      const today = new Date().toISOString().split('T')[0];
                      
                      // Use same logic as above for consistency
                      let meals: any[] = [];
                      if (mealPlan.plan_type === 'weekly' && Object.keys(gridAssignments).length > 0) {
                        const todayMeals = gridAssignments[today] || {};
                        meals = Object.values(todayMeals).filter(Boolean);
                      } else {
                        const all = mealPlan.meals || [];
                        meals = all.filter((m: any) => {
                          const d = m.meal_date || m.date || mealPlan.date;
                          return d?.slice(0, 10) === today;
                        });
                      }
                      
                      return `Show All (${meals.length})`;
                    })()}
                  </Button>
                )}
              </VStack>
            ) : (
              <VStack spacing={4} py={8}>
                <FiCoffee size={48} color="#CBD5E0" />
                <Text color="gray.500" textAlign="center">
                  No meal plan available for today
                </Text>
                <Text fontSize="sm" color="gray.400" textAlign="center">
                  Create a meal plan to get started with your nutrition journey
                </Text>
                <HStack spacing={2}>
                  <Button
                    size="sm"
                    colorScheme="blue"
                    leftIcon={<FiCoffee />}
                    onClick={() => {
                      const event = new CustomEvent('navigateToTab', { detail: { tabIndex: 2 } });
                      window.dispatchEvent(event);
                    }}
                  >
                    Create Meal Plan
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    leftIcon={<FiPlus />}
                    onClick={() => {
                    const event = new CustomEvent('navigateToTab', { detail: { tabIndex: 7 } });
                      window.dispatchEvent(event);
                    }}
                  >
                    Add Food Entry
                  </Button>
                </HStack>
              </VStack>
            )}
          </CardBody>
        </Card>

        {/* Quick Actions */}
        <Grid templateColumns={{ base: '1fr', md: 'repeat(3, 1fr)' }} gap={4}>
          <Card bg={cardBg} borderColor={borderColor} _hover={{ shadow: 'md' }} transition="all 0.2s">
            <CardBody>
              <VStack spacing={3}>
                <FiTarget size={24} color="#38A169" />
                <Text fontWeight="bold" color="green.600">Set Goals</Text>
                <Text fontSize="sm" color="gray.600" textAlign="center">
                  Set your daily nutrition targets
                </Text>
                <Button 
                  size="sm" 
                  colorScheme="green" 
                  width="full"
                  onClick={() => {
                    // Navigate to Goals tab
                    const event = new CustomEvent('navigateToTab', { detail: { tabIndex: 3 } });
                    window.dispatchEvent(event);
                  }}
                >
                  Set Goals
                </Button>
              </VStack>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={borderColor} _hover={{ shadow: 'md' }} transition="all 0.2s">
            <CardBody>
              <VStack spacing={3}>
                <FiShoppingCart size={24} color="#DD6B20" />
                <Text fontWeight="bold" color="orange.600">Shopping List</Text>
                <Text fontSize="sm" color="gray.600" textAlign="center">
                  Generate shopping list from meal plans
                </Text>
                <Button 
                  size="sm" 
                  colorScheme="orange" 
                  width="full"
                  onClick={() => {
                    // Navigate to Shopping tab
                    const event = new CustomEvent('navigateToTab', { detail: { tabIndex: 6 } });
                    window.dispatchEvent(event);
                  }}
                >
                  Generate Shopping List
                </Button>
              </VStack>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={borderColor} _hover={{ shadow: 'md' }} transition="all 0.2s">
            <CardBody>
              <VStack spacing={3}>
                <FiPieChart size={24} color="#805AD5" />
                <Text fontWeight="bold" color="purple.600">Analysis</Text>
                <Text fontSize="sm" color="gray.600" textAlign="center">
                  View detailed nutritional analysis
                </Text>
                <Button 
                  size="sm" 
                  colorScheme="purple" 
                  width="full"
                  onClick={() => {
                    // Navigate to Analysis tab
                    const event = new CustomEvent('navigateToTab', { detail: { tabIndex: 8 } });
                    window.dispatchEvent(event);
                  }}
                >
                  View Analysis
                </Button>
              </VStack>
            </CardBody>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Card bg={cardBg} borderColor={borderColor}>
          <CardHeader>
            <Heading size="md">{t('nutrition.recentActivity', 'en')}</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={3} align="stretch">
              <HStack justify="space-between">
                <HStack>
                  <FiActivity />
                  <Text>{t('nutrition.mealLogged', 'en')}</Text>
                </HStack>
                <Text fontSize="sm" color="gray.600">2 hours ago</Text>
              </HStack>
              <HStack justify="space-between">
                <HStack>
                  <FiTarget />
                  <Text>{t('nutrition.goalUpdated', 'en')}</Text>
                </HStack>
                <Text fontSize="sm" color="gray.600">1 day ago</Text>
              </HStack>
              <HStack justify="space-between">
                <HStack>
                  <FiCoffee />
                  <Text>{t('nutrition.mealPlanGenerated', 'en')}</Text>
                </HStack>
                <Text fontSize="sm" color="gray.600">2 days ago</Text>
              </HStack>
            </VStack>
          </CardBody>
        </Card>

          </>
        ) : (
          <>
            <MicronutrientAnalysis userId={user?.id} onUpdate={loadNutritionData} />
            <MacronutrientVisualization
              currentData={{
                calories: nutritionalData?.calories || 0,
                protein: nutritionalData?.protein || 0,
                carbs: nutritionalData?.carbs || 0,
                fats: nutritionalData?.fats || 0
              }}
              targets={{
                calories: goals.calories,
                protein: goals.protein,
                carbs: goals.carbs,
                fats: goals.fats
              }}
              dailyBreakdown={[]}
              period="daily"
            />
          </>
        )}
      </VStack>
    </Box>
  );
};

export default NutritionDashboard;

