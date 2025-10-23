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
  FiMoreVertical
} from 'react-icons/fi';

interface Meal {
  id: string;
  name: string;
  type: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  calories: number;
  protein: number;
  carbs: number;
  fats: number;
  prepTime: number;
  difficulty: 'easy' | 'medium' | 'hard';
  dietaryTags: string[];
  ingredients: string[];
  instructions: string[];
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
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock data
      setMealPlan({
        id: 'mp_1',
        date: selectedDate,
        meals: [
          {
            id: 'm1',
            name: 'Mediterranean Omelet',
            type: 'breakfast',
            calories: 400,
            protein: 28,
            carbs: 15,
            fats: 25,
            prepTime: 15,
            difficulty: 'easy',
            dietaryTags: ['vegetarian', 'high-protein'],
            ingredients: ['eggs', 'tomatoes', 'spinach', 'olive oil', 'cheese'],
            instructions: [
              'Heat olive oil in a non-stick pan over medium heat.',
              'Beat eggs in a bowl and season with salt and pepper.',
              'Add tomatoes and spinach to the pan, cook for 2 minutes.',
              'Pour beaten eggs over vegetables and cook until set.',
              'Sprinkle cheese on top and fold omelet in half.'
            ]
          },
          {
            id: 'm2',
            name: 'Quinoa Buddha Bowl',
            type: 'lunch',
            calories: 420,
            protein: 18,
            carbs: 50,
            fats: 15,
            prepTime: 20,
            difficulty: 'medium',
            dietaryTags: ['vegetarian', 'vegan', 'gluten-free'],
            ingredients: ['quinoa', 'broccoli', 'avocado', 'olive oil'],
            instructions: [
              'Cook quinoa according to package instructions.',
              'Steam broccoli until tender.',
              'Slice avocado and prepare vegetables.',
              'Arrange all ingredients in a bowl.',
              'Drizzle with olive oil and season to taste.'
            ]
          },
          {
            id: 'm3',
            name: 'Baked Salmon with Vegetables',
            type: 'dinner',
            calories: 550,
            protein: 40,
            carbs: 25,
            fats: 30,
            prepTime: 25,
            difficulty: 'medium',
            dietaryTags: ['gluten-free', 'high-protein', 'omega-3'],
            ingredients: ['salmon fillet', 'broccoli', 'olive oil'],
            instructions: [
              'Preheat oven to 400°F (200°C).',
              'Season salmon with salt, pepper, and olive oil.',
              'Toss broccoli with olive oil and seasonings.',
              'Place salmon and vegetables on a baking sheet.',
              'Bake for 20-25 minutes until salmon is flaky.'
            ]
          }
        ],
        totalCalories: 1370,
        totalProtein: 86,
        totalCarbs: 90,
        totalFats: 70
      });
    } catch (err) {
      setError('Failed to load meal plan');
    } finally {
      setLoading(false);
    }
  };

  const generateMealPlan = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Simulate API call to generate new meal plan
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Reload meal plan
      await loadMealPlan();
    } catch (err) {
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
          </Card>
        )}

        {/* Meals */}
        {mealPlan && (
          <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }} gap={4}>
            {mealPlan.meals.map((meal) => (
              <Card key={meal.id} bg={cardBg} borderColor={borderColor}>
                <CardHeader>
                  <HStack justify="space-between">
                    <VStack align="start" spacing={1}>
                      <Heading size="sm">{meal.name}</Heading>
                      <Badge colorScheme="blue" size="sm">{meal.type}</Badge>
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
                      <Text>{meal.calories} {t('nutrition.calories', 'en')}</Text>
                      <Text>{meal.protein}g {t('nutrition.protein', 'en')}</Text>
                    </HStack>
                    <HStack justify="space-between" fontSize="sm">
                      <Text>{meal.carbs}g {t('nutrition.carbs', 'en')}</Text>
                      <Text>{meal.fats}g {t('nutrition.fats', 'en')}</Text>
                    </HStack>

                    <Divider />

                    {/* Meal Details */}
                    <HStack justify="space-between" fontSize="sm">
                      <HStack>
                        <FiClock />
                        <Text>{meal.prepTime} min</Text>
                      </HStack>
                      <Badge colorScheme={getDifficultyColor(meal.difficulty)} size="sm">
                        {meal.difficulty}
                      </Badge>
                    </HStack>

                    {/* Dietary Tags */}
                    <HStack wrap="wrap" spacing={1}>
                      {meal.dietaryTags.map((tag) => (
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
                {t('common.cancel')}
              </Button>
              <Button colorScheme="blue">
                {t('common.save')}
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </VStack>
    </Box>
  );
};

export default MealPlanning;
