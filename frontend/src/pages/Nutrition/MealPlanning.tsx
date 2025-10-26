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
import { 
  FiPlus, 
  FiEdit, 
  FiTrash2, 
  FiRefreshCw,
  FiCoffee,
  FiClock,
  FiTarget,
  FiMoreVertical,
  FiLogIn
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
  difficulty?: 'easy' | 'medium' | 'hard';
  difficulty_level?: 'easy' | 'medium' | 'hard';
  dietaryTags?: string[];
  dietary_tags?: string[];
  ingredients?: string[];
  instructions?: string[];
}

interface MealPlan {
  id: string;
  date: string;
  meals: Meal[];
  totalCalories: number;
  totalProtein: number;
  totalCarbs: number;
  totalFats: number;
}

interface MealPlanningProps {
  user?: any;
}

const MealPlanning: React.FC<MealPlanningProps> = ({ user = null }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [mealPlan, setMealPlan] = useState<MealPlan | null>(null);
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [preferences, setPreferences] = useState({
    dietaryRestrictions: [] as string[],
    allergies: [] as string[],
    cuisinePreferences: [] as string[],
    calorieTarget: 2000,
    mealsPerDay: 3
  });

  const { isOpen, onOpen, onClose } = useDisclosure();
  const [selectedMeal, setSelectedMeal] = useState<Meal | null>(null);

  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    loadMealPlan();
  }, [selectedDate]);

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
          plan_type: 'daily',
          start_date: selectedDate,
          end_date: selectedDate,
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

  const handleMealDelete = (mealId: string) => {
    if (mealPlan) {
      const updatedMeals = mealPlan.meals.filter(meal => meal.id !== mealId);
      setMealPlan({
        ...mealPlan,
        meals: updatedMeals,
        totalCalories: updatedMeals.reduce((sum, meal) => sum + meal.calories, 0),
        totalProtein: updatedMeals.reduce((sum, meal) => sum + meal.protein, 0),
        totalCarbs: updatedMeals.reduce((sum, meal) => sum + meal.carbs, 0),
        totalFats: updatedMeals.reduce((sum, meal) => sum + meal.fats, 0)
      });
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
            <Button 
              colorScheme="blue" 
              leftIcon={<FiRefreshCw />}
              onClick={generateMealPlan}
              isLoading={loading}
            >
              {t('nutrition.generateMealPlan', 'en')}
            </Button>
          </HStack>

          {/* Date Selector */}
          <HStack spacing={4}>
            <FormControl>
              <FormLabel>{t('nutrition.selectDate', 'en')}</FormLabel>
              <Input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                maxW="200px"
              />
            </FormControl>
            <FormControl>
              <FormLabel>{t('nutrition.calorieTarget', 'en')}</FormLabel>
              <Input
                type="number"
                value={preferences.calorieTarget}
                onChange={(e) => setPreferences({...preferences, calorieTarget: parseInt(e.target.value)})}
                maxW="150px"
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
                    {mealPlan.totalCalories} {t('nutrition.calories', 'en')}
                  </Text>
                  <Text fontSize="sm" color="gray.600">
                    {mealPlan.totalProtein}g {t('nutrition.protein', 'en')}
                  </Text>
                  <Text fontSize="sm" color="gray.600">
                    {mealPlan.totalCarbs}g {t('nutrition.carbs', 'en')}
                  </Text>
                  <Text fontSize="sm" color="gray.600">
                    {mealPlan.totalFats}g {t('nutrition.fats', 'en')}
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
            {(mealPlan.meals || []).map((meal) => (
              <Card key={meal.id} bg={cardBg} borderColor={borderColor}>
                <CardHeader>
                  <HStack justify="space-between">
                    <VStack align="start" spacing={1}>
                      <Heading size="sm">{meal.meal_name || meal.name || 'Untitled Meal'}</Heading>
                      <Badge colorScheme="blue" size="sm">{meal.meal_type || meal.type || 'meal'}</Badge>
                    </VStack>
                    <Menu>
                      <MenuButton as={IconButton} icon={<FiMoreVertical />} size="sm" variant="ghost" />
                      <MenuList>
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
                    <HStack justify="space-between" fontSize="sm">
                      <Text>{meal.calories || 0} {t('nutrition.calories', 'en')}</Text>
                      <Text>{meal.protein || 0}g {t('nutrition.protein', 'en')}</Text>
                    </HStack>
                    <HStack justify="space-between" fontSize="sm">
                      <Text>{meal.carbs || 0}g {t('nutrition.carbs', 'en')}</Text>
                      <Text>{meal.fats || 0}g {t('nutrition.fats', 'en')}</Text>
                    </HStack>

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
                      <Button size="sm" colorScheme="blue" flex={1}>
                        {t('nutrition.viewRecipe', 'en')}
                      </Button>
                      <Button size="sm" variant="outline" flex={1}>
                        {t('nutrition.swapMeal', 'en')}
                      </Button>
                    </HStack>
                  </VStack>
                </CardBody>
              </Card>
            ))}
          </Grid>
        )}

        {/* Add Meal Button */}
        <Card bg={cardBg} borderColor={borderColor} borderStyle="dashed">
          <CardBody>
            <Center h="200px">
              <VStack spacing={4}>
                <FiPlus size={48} color="gray" />
                <Text color="gray.600">{t('nutrition.addMeal', 'en')}</Text>
                <Button colorScheme="blue" leftIcon={<FiCoffee />}>
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
      </VStack>
    </Box>
  );
};

export default MealPlanning;
