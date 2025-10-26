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
  FiPieChart
} from 'react-icons/fi';

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

  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    loadNutritionData();
  }, []);

  const setupDefaultPreferences = async () => {
    try {
      // Get Supabase session token for authentication
      const { supabase } = await import('../../lib/supabase');
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
      const { supabase } = await import('../../lib/supabase');
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
        const mealPlans = await mealPlanResponse.json();
        if (mealPlans.length > 0) {
          setMealPlan(mealPlans[0]);
        }
      }
      
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

        {/* Quick Stats */}
        <Grid templateColumns={{ base: '1fr', md: 'repeat(4, 1fr)' }} gap={4}>
          <Card bg={cardBg} borderColor={borderColor}>
            <CardBody>
              <Stat>
                <StatLabel>{t('nutrition.calories', 'en')}</StatLabel>
                <StatNumber>{nutritionalData?.calories || 0}</StatNumber>
                <StatHelpText>
                  <Progress 
                    value={getCalorieProgress()} 
                    colorScheme={getProgressColor(getCalorieProgress())}
                    size="sm"
                  />
                  {Math.round(getCalorieProgress())}% of {goals.calories}
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={borderColor}>
            <CardBody>
              <Stat>
                <StatLabel>{t('nutrition.protein', 'en')}</StatLabel>
                <StatNumber>{nutritionalData?.protein || 0}g</StatNumber>
                <StatHelpText>
                  <Progress 
                    value={getMacroProgress(nutritionalData?.protein || 0, goals.protein)} 
                    colorScheme={getProgressColor(getMacroProgress(nutritionalData?.protein || 0, goals.protein))}
                    size="sm"
                  />
                  {Math.round(getMacroProgress(nutritionalData?.protein || 0, goals.protein))}% of {goals.protein}g
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={borderColor}>
            <CardBody>
              <Stat>
                <StatLabel>{t('nutrition.carbs', 'en')}</StatLabel>
                <StatNumber>{nutritionalData?.carbs || 0}g</StatNumber>
                <StatHelpText>
                  <Progress 
                    value={getMacroProgress(nutritionalData?.carbs || 0, goals.carbs)} 
                    colorScheme={getProgressColor(getMacroProgress(nutritionalData?.carbs || 0, goals.carbs))}
                    size="sm"
                  />
                  {Math.round(getMacroProgress(nutritionalData?.carbs || 0, goals.carbs))}% of {goals.carbs}g
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={borderColor}>
            <CardBody>
              <Stat>
                <StatLabel>{t('nutrition.fats', 'en')}</StatLabel>
                <StatNumber>{nutritionalData?.fats || 0}g</StatNumber>
                <StatHelpText>
                  <Progress 
                    value={getMacroProgress(nutritionalData?.fats || 0, goals.fats)} 
                    colorScheme={getProgressColor(getMacroProgress(nutritionalData?.fats || 0, goals.fats))}
                    size="sm"
                  />
                  {Math.round(getMacroProgress(nutritionalData?.fats || 0, goals.fats))}% of {goals.fats}g
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </Grid>

        {/* Today's Meal Plan */}
        <Card bg={cardBg} borderColor={borderColor}>
          <CardHeader>
            <HStack justify="space-between">
              <Heading size="md">{t('nutrition.todaysMeals', 'en')}</Heading>
                <Button size="sm" colorScheme="blue" leftIcon={<FiCoffee />}>
                  {t('nutrition.generateMealPlan', 'en')}
                </Button>
            </HStack>
          </CardHeader>
          <CardBody>
            {mealPlan ? (
              <VStack spacing={4} align="stretch">
                {mealPlan.meals.map((meal, index) => (
                  <Box key={meal.id} p={4} borderWidth={1} borderRadius="md" borderColor={borderColor}>
                    <HStack justify="space-between" mb={2}>
                      <VStack align="start" spacing={1}>
                        <Text fontWeight="bold">{meal.name}</Text>
                        <Badge colorScheme="blue" size="sm">{meal.type}</Badge>
                      </VStack>
                      <Text fontSize="sm" color="gray.600">
                        {meal.calories} {t('nutrition.calories', 'en')}
                      </Text>
                    </HStack>
                    <HStack spacing={4} fontSize="sm" color="gray.600">
                      <Text>{meal.protein}g {t('nutrition.protein', 'en')}</Text>
                      <Text>{meal.carbs}g {t('nutrition.carbs', 'en')}</Text>
                      <Text>{meal.fats}g {t('nutrition.fats', 'en')}</Text>
                    </HStack>
                  </Box>
                ))}
                <Divider />
                <HStack justify="space-between" fontWeight="bold">
                  <Text>{t('nutrition.total', 'en')}</Text>
                  <Text>{mealPlan.totalCalories} {t('nutrition.calories', 'en')}</Text>
                </HStack>
              </VStack>
            ) : (
              <Text color="gray.500">{t('nutrition.noMealPlan', 'en')}</Text>
            )}
          </CardBody>
        </Card>

        {/* Quick Actions */}
        <Grid templateColumns={{ base: '1fr', md: 'repeat(3, 1fr)' }} gap={4}>
          <Card bg={cardBg} borderColor={borderColor}>
            <CardBody>
              <VStack spacing={3}>
                <FiTarget size={24} />
                <Text fontWeight="bold">{t('nutrition.setGoals', 'en')}</Text>
                <Text fontSize="sm" color="gray.600" textAlign="center">
                  {t('nutrition.setGoalsDescription', 'en')}
                </Text>
                <Button size="sm" colorScheme="green" width="full">
                  {t('nutrition.setGoals', 'en')}
                </Button>
              </VStack>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={borderColor}>
            <CardBody>
              <VStack spacing={3}>
                <FiShoppingCart size={24} />
                <Text fontWeight="bold">{t('nutrition.shoppingList', 'en')}</Text>
                <Text fontSize="sm" color="gray.600" textAlign="center">
                  {t('nutrition.shoppingListDescription', 'en')}
                </Text>
                <Button size="sm" colorScheme="orange" width="full">
                  {t('nutrition.generateShoppingList', 'en')}
                </Button>
              </VStack>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={borderColor}>
            <CardBody>
              <VStack spacing={3}>
                <FiPieChart size={24} />
                <Text fontWeight="bold">{t('nutrition.analysis', 'en')}</Text>
                <Text fontSize="sm" color="gray.600" textAlign="center">
                  {t('nutrition.analysisDescription', 'en')}
                </Text>
                <Button size="sm" colorScheme="purple" width="full">
                  {t('nutrition.viewAnalysis', 'en')}
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
      </VStack>
    </Box>
  );
};

export default NutritionDashboard;
