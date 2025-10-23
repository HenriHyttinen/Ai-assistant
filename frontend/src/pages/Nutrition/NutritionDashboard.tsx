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
import { useTranslation } from 'react-i18next';
import { 
  FiTrendingUp, 
  FiTarget, 
  FiClock, 
  FiShoppingCart,
  FiHeart,
  FiActivity,
  FiChefHat,
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

const NutritionDashboard: React.FC<NutritionDashboardProps> = ({ user }) => {
  const { t } = useTranslation();
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

  const loadNutritionData = async () => {
    try {
      setLoading(true);
      // Simulate API call - in real implementation, this would call the backend
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock data for demonstration
      setNutritionalData({
        calories: 1850,
        protein: 120,
        carbs: 180,
        fats: 55,
        fiber: 25,
        sugar: 45,
        sodium: 2100
      });

      setMealPlan({
        id: 'mp_1',
        date: new Date().toISOString().split('T')[0],
        meals: [
          {
            id: 'm1',
            name: 'Mediterranean Omelet',
            type: 'breakfast',
            calories: 400,
            protein: 28,
            carbs: 15,
            fats: 25
          },
          {
            id: 'm2',
            name: 'Quinoa Buddha Bowl',
            type: 'lunch',
            calories: 420,
            protein: 18,
            carbs: 50,
            fats: 15
          },
          {
            id: 'm3',
            name: 'Baked Salmon with Vegetables',
            type: 'dinner',
            calories: 550,
            protein: 40,
            carbs: 25,
            fats: 30
          }
        ],
        totalCalories: 1370,
        totalProtein: 86,
        totalCarbs: 90,
        totalFats: 70
      });

      setError(null);
    } catch (err) {
      setError('Failed to load nutrition data');
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
          <Text>{t('nutrition.loading')}</Text>
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
            {t('nutrition.dashboard.title')}
          </Heading>
          <Text color="gray.600">
            {t('nutrition.dashboard.subtitle')}
          </Text>
        </Box>

        {/* Quick Stats */}
        <Grid templateColumns={{ base: '1fr', md: 'repeat(4, 1fr)' }} gap={4}>
          <Card bg={cardBg} borderColor={borderColor}>
            <CardBody>
              <Stat>
                <StatLabel>{t('nutrition.calories')}</StatLabel>
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
                <StatLabel>{t('nutrition.protein')}</StatLabel>
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
                <StatLabel>{t('nutrition.carbs')}</StatLabel>
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
                <StatLabel>{t('nutrition.fats')}</StatLabel>
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
              <Heading size="md">{t('nutrition.todaysMeals')}</Heading>
              <Button size="sm" colorScheme="blue" leftIcon={<FiChefHat />}>
                {t('nutrition.generateMealPlan')}
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
                        {meal.calories} {t('nutrition.calories')}
                      </Text>
                    </HStack>
                    <HStack spacing={4} fontSize="sm" color="gray.600">
                      <Text>{meal.protein}g {t('nutrition.protein')}</Text>
                      <Text>{meal.carbs}g {t('nutrition.carbs')}</Text>
                      <Text>{meal.fats}g {t('nutrition.fats')}</Text>
                    </HStack>
                  </Box>
                ))}
                <Divider />
                <HStack justify="space-between" fontWeight="bold">
                  <Text>{t('nutrition.total')}</Text>
                  <Text>{mealPlan.totalCalories} {t('nutrition.calories')}</Text>
                </HStack>
              </VStack>
            ) : (
              <Text color="gray.500">{t('nutrition.noMealPlan')}</Text>
            )}
          </CardBody>
        </Card>

        {/* Quick Actions */}
        <Grid templateColumns={{ base: '1fr', md: 'repeat(3, 1fr)' }} gap={4}>
          <Card bg={cardBg} borderColor={borderColor}>
            <CardBody>
              <VStack spacing={3}>
                <FiTarget size={24} />
                <Text fontWeight="bold">{t('nutrition.setGoals')}</Text>
                <Text fontSize="sm" color="gray.600" textAlign="center">
                  {t('nutrition.setGoalsDescription')}
                </Text>
                <Button size="sm" colorScheme="green" width="full">
                  {t('nutrition.setGoals')}
                </Button>
              </VStack>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={borderColor}>
            <CardBody>
              <VStack spacing={3}>
                <FiShoppingCart size={24} />
                <Text fontWeight="bold">{t('nutrition.shoppingList')}</Text>
                <Text fontSize="sm" color="gray.600" textAlign="center">
                  {t('nutrition.shoppingListDescription')}
                </Text>
                <Button size="sm" colorScheme="orange" width="full">
                  {t('nutrition.generateShoppingList')}
                </Button>
              </VStack>
            </CardBody>
          </Card>

          <Card bg={cardBg} borderColor={borderColor}>
            <CardBody>
              <VStack spacing={3}>
                <FiPieChart size={24} />
                <Text fontWeight="bold">{t('nutrition.analysis')}</Text>
                <Text fontSize="sm" color="gray.600" textAlign="center">
                  {t('nutrition.analysisDescription')}
                </Text>
                <Button size="sm" colorScheme="purple" width="full">
                  {t('nutrition.viewAnalysis')}
                </Button>
              </VStack>
            </CardBody>
          </Card>
        </Grid>

        {/* Recent Activity */}
        <Card bg={cardBg} borderColor={borderColor}>
          <CardHeader>
            <Heading size="md">{t('nutrition.recentActivity')}</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={3} align="stretch">
              <HStack justify="space-between">
                <HStack>
                  <FiActivity />
                  <Text>{t('nutrition.mealLogged')}</Text>
                </HStack>
                <Text fontSize="sm" color="gray.600">2 hours ago</Text>
              </HStack>
              <HStack justify="space-between">
                <HStack>
                  <FiTarget />
                  <Text>{t('nutrition.goalUpdated')}</Text>
                </HStack>
                <Text fontSize="sm" color="gray.600">1 day ago</Text>
              </HStack>
              <HStack justify="space-between">
                <HStack>
                  <FiChefHat />
                  <Text>{t('nutrition.mealPlanGenerated')}</Text>
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
