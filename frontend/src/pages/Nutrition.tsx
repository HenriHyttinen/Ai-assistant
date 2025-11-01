import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Container,
  Heading,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  VStack,
  HStack,
  Text,
  Button,
  useColorModeValue,
  SimpleGrid,
  Card,
  CardBody,
  CardHeader,
  Badge,
  Icon,
  Flex,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Select,
} from '@chakra-ui/react';
import NutritionDashboard from './Nutrition/NutritionDashboard';
import MealPlanning from './Nutrition/MealPlanning';
import AnalyticsDashboard from '../components/nutrition/AnalyticsDashboard';
import GoalsDashboard from '../components/nutrition/GoalsDashboard';
import RecipeSearch from './Nutrition/RecipeSearch';
import DailyLogging from './Nutrition/DailyLogging';
import ShoppingList from '../components/nutrition/ShoppingList';
import EnhancedShoppingListGenerator from '../components/nutrition/EnhancedShoppingListGenerator';
import NutritionalAnalysis from '../components/nutrition/NutritionalAnalysis';
import NutritionPreferences from '../components/nutrition/NutritionPreferences';
import RecipeRecommendations from '../components/nutrition/RecipeRecommendations';
import MicronutrientDashboard from '../components/nutrition/MicronutrientDashboard';
import MicronutrientRecipeSearch from '../components/nutrition/MicronutrientRecipeSearch';
import {
  FiCoffee,
  FiBookOpen,
  FiShoppingCart,
  FiBarChart,
  FiSettings,
  FiPlus,
  FiRefreshCw,
  FiEdit3,
  FiStar,
  FiZap,
  FiTarget,
  FiDroplet,
} from 'react-icons/fi';
import { t } from '../utils/translations';

interface NutritionData {
  preferences: any;
  mealPlans: any[];
  recipes: any[];
  shoppingLists: any[];
  nutritionalLogs: any[];
}

const Nutrition: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [nutritionData, setNutritionData] = useState<NutritionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  useEffect(() => {
    loadNutritionData();
    
    // Listen for tab navigation events from dashboard
    const handleTabNavigation = (event: CustomEvent) => {
      setActiveTab(event.detail.tabIndex);
    };
    
    window.addEventListener('navigateToTab', handleTabNavigation as EventListener);
    
    return () => {
      window.removeEventListener('navigateToTab', handleTabNavigation as EventListener);
    };
  }, []);

  const loadNutritionData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get Supabase session token for authentication
      const { supabase } = await import('../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        throw new Error('No authentication session found');
      }
      
      const headers = { Authorization: `Bearer ${session.access_token}` };
      
      // Load nutrition data from API with integrated preferences
      const [preferencesRes, mealPlansRes, recipesRes, shoppingListsRes, logsRes] = await Promise.allSettled([
        fetch('http://localhost:8000/nutrition/preferences/integrated', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json', ...headers }
        }).then(res => res.ok ? res.json() : null),
        Promise.resolve({ data: [] }), // TODO: Implement meal plans API
        Promise.resolve({ data: [] }), // TODO: Implement recipes API
        Promise.resolve({ data: [] }), // TODO: Implement shopping lists API
        Promise.resolve({ data: [] })  // TODO: Implement nutritional logs API
      ]);
      
      setNutritionData({
        preferences: preferencesRes.status === 'fulfilled' ? preferencesRes.value : null,
        mealPlans: mealPlansRes.status === 'fulfilled' ? mealPlansRes.value.data : [],
        recipes: recipesRes.status === 'fulfilled' ? recipesRes.value.data : [],
        shoppingLists: shoppingListsRes.status === 'fulfilled' ? shoppingListsRes.value.data : [],
        nutritionalLogs: logsRes.status === 'fulfilled' ? logsRes.value.data : []
      });
      
    } catch (err) {
      console.error('Error loading nutrition data:', err);
      setError('Failed to load nutrition data. Please try again.');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleDataUpdate = () => {
    loadNutritionData();
  };

  if (loading) {
    return (
      <Box minH="100vh" bg={bgColor} py={8}>
        <Container maxW="7xl">
          <Flex justify="center" align="center" minH="400px">
            <VStack spacing={4}>
              <Spinner size="xl" color="blue.500" />
              <Text color="gray.600">Loading nutrition data...</Text>
            </VStack>
          </Flex>
        </Container>
      </Box>
    );
  }

  if (error) {
    return (
      <Box minH="100vh" bg={bgColor} py={8}>
        <Container maxW="7xl">
          <Alert status="error" borderRadius="lg">
            <AlertIcon />
            <Box>
              <AlertTitle>Error loading nutrition data!</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Box>
          </Alert>
        </Container>
      </Box>
    );
  }

  return (
    <Box minH="100vh" bg={bgColor}>
      <Container maxW="7xl" py={8}>
        <VStack spacing={8} align="stretch">
          {/* Header */}
          <Box>
            <Heading size="xl" mb={2} color="blue.600">
              {t('nutrition')}
            </Heading>
            <Text color="gray.600" fontSize="lg">
              Manage your nutrition, plan meals, and track your dietary goals
            </Text>
          </Box>

          {/* Quick Stats */}
          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6}>
            <Card bg={cardBg} borderColor={borderColor}>
              <CardBody>
                <HStack justify="space-between">
                  <VStack align="start" spacing={1}>
                    <Text fontSize="sm" color="gray.600">
                      {t('mealPlans')}
                    </Text>
                    <Text fontSize="2xl" fontWeight="bold" color="blue.500">
                      {nutritionData?.mealPlans.length || 0}
                    </Text>
                  </VStack>
                  <Icon as={FiCoffee} boxSize={8} color="blue.500" />
                </HStack>
              </CardBody>
            </Card>

            <Card bg={cardBg} borderColor={borderColor}>
              <CardBody>
                <HStack justify="space-between">
                  <VStack align="start" spacing={1}>
                    <Text fontSize="sm" color="gray.600">
                      {t('recipes')}
                    </Text>
                    <Text fontSize="2xl" fontWeight="bold" color="green.500">
                      {nutritionData?.recipes.length || 0}
                    </Text>
                  </VStack>
                  <Icon as={FiBookOpen} boxSize={8} color="green.500" />
                </HStack>
              </CardBody>
            </Card>

            <Card bg={cardBg} borderColor={borderColor}>
              <CardBody>
                <HStack justify="space-between">
                  <VStack align="start" spacing={1}>
                    <Text fontSize="sm" color="gray.600">
                      {t('shoppingList')}
                    </Text>
                    <Text fontSize="2xl" fontWeight="bold" color="orange.500">
                      {nutritionData?.shoppingLists.length || 0}
                    </Text>
                  </VStack>
                  <Icon as={FiShoppingCart} boxSize={8} color="orange.500" />
                </HStack>
              </CardBody>
            </Card>

            <Card bg={cardBg} borderColor={borderColor}>
              <CardBody>
                <HStack justify="space-between">
                  <VStack align="start" spacing={1}>
                    <Text fontSize="sm" color="gray.600">
                      {t('nutritionalAnalysis')}
                    </Text>
                    <Text fontSize="2xl" fontWeight="bold" color="purple.500">
                      Active
                    </Text>
                  </VStack>
                  <Icon as={FiBarChart} boxSize={8} color="purple.500" />
                </HStack>
              </CardBody>
            </Card>
          </SimpleGrid>

          {/* Main Content Tabs */}
          <Card bg={cardBg} borderColor={borderColor}>
            {/* Mobile-friendly selector to avoid horizontal scrolling */}
            <Box display={{ base: 'block', md: 'none' }} px={4} pt={4}>
              <Select
                value={activeTab}
                onChange={(e) => setActiveTab(parseInt(e.target.value, 10))}
                size="sm"
                variant="filled"
              >
                <option value={0}>Dashboard</option>
                <option value={1}>Preferences</option>
                <option value={2}>Meal Planning</option>
                <option value={3}>Goals</option>
                <option value={4}>Recommendations</option>
                <option value={5}>Recipes</option>
                <option value={6}>Shopping</option>
                <option value={7}>Daily Log</option>
                <option value={8}>Analysis</option>
                <option value={9}>Micronutrients</option>
                <option value={10}>Micro Search</option>
              </Select>
            </Box>

            <Tabs index={activeTab} onChange={setActiveTab} variant="soft-rounded" colorScheme="blue" size="sm" isLazy>
              <TabList
                display={{ base: 'none', md: 'flex' }}
                overflow="visible"
                whiteSpace="normal"
                flexWrap="wrap"
                gap={2}
                px={4}
                pt={4}
                bg={cardBg}
                borderTopLeftRadius="lg"
                borderTopRightRadius="lg"
                borderBottom="1px solid"
                borderColor={borderColor}
              >
                <Tab>
                  <HStack spacing={2}>
                    <Icon as={FiBarChart} />
                    <Text>Dashboard</Text>
                  </HStack>
                </Tab>
                <Tab>
                  <HStack spacing={2}>
                    <Icon as={FiSettings} />
                    <Text>Preferences</Text>
                  </HStack>
                </Tab>
                <Tab>
                  <HStack spacing={2}>
                    <Icon as={FiCoffee} />
                    <Text>Meal Planning</Text>
                  </HStack>
                </Tab>
                <Tab>
                  <HStack spacing={2}>
                    <Icon as={FiTarget} />
                    <Text>Goals</Text>
                  </HStack>
                </Tab>
                <Tab>
                  <HStack spacing={2}>
                    <Icon as={FiStar} />
                    <Text>Recommendations</Text>
                  </HStack>
                </Tab>
                <Tab>
                  <HStack spacing={2}>
                    <Icon as={FiBookOpen} />
                    <Text>Recipes</Text>
                  </HStack>
                </Tab>
                <Tab>
                  <HStack spacing={2}>
                    <Icon as={FiShoppingCart} />
                    <Text>Shopping</Text>
                  </HStack>
                </Tab>
                <Tab>
                  <HStack spacing={2}>
                    <Icon as={FiEdit3} />
                    <Text>Daily Log</Text>
                  </HStack>
                </Tab>
                <Tab>
                  <HStack spacing={2}>
                    <Icon as={FiBarChart} />
                    <Text>Analysis</Text>
                  </HStack>
                </Tab>
                <Tab>
                  <HStack spacing={2}>
                    <Icon as={FiDroplet} />
                    <Text>Micronutrients</Text>
                  </HStack>
                </Tab>
                <Tab>
                  <HStack spacing={2}>
                    <Icon as={FiTarget} />
                    <Text>Micro Search</Text>
                  </HStack>
                </Tab>
              </TabList>

              <TabPanels>
                <TabPanel px={0} py={6}>
                  <NutritionDashboard />
                </TabPanel>

                <TabPanel px={0} py={6}>
                  <NutritionPreferences 
                    preferences={null} 
                    onUpdate={() => {}} 
                  />
                </TabPanel>

                <TabPanel px={0} py={6}>
                  <MealPlanning />
                </TabPanel>
                <TabPanel px={0} py={6}>
                  <GoalsDashboard />
                </TabPanel>

                <TabPanel px={0} py={6}>
                  <RecipeRecommendations />
                </TabPanel>

                <TabPanel px={0} py={6}>
                  <RecipeSearch />
                </TabPanel>

                <TabPanel px={0} py={6}>
                  <ShoppingList />
                </TabPanel>

                <TabPanel px={0} py={6}>
                  <DailyLogging />
                </TabPanel>

                <TabPanel px={0} py={6}>
                  <NutritionalAnalysis />
                </TabPanel>

                <TabPanel px={0} py={6}>
                  <MicronutrientDashboard />
                </TabPanel>

                <TabPanel px={0} py={6}>
                  <MicronutrientRecipeSearch />
                </TabPanel>
              </TabPanels>
            </Tabs>
          </Card>
        </VStack>
      </Container>
    </Box>
  );
};

export default Nutrition;
