import React, { useState, useEffect } from 'react';
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
} from '@chakra-ui/react';
import {
  FiUtensils,
  FiBookOpen,
  FiShoppingCart,
  FiBarChart3,
  FiSettings,
  FiPlus,
  FiRefreshCw,
} from 'react-icons/fi';
import { t } from '../utils/translations';
import NutritionPreferences from '../components/nutrition/NutritionPreferences';
import MealPlanning from '../components/nutrition/MealPlanning';
import RecipeSearch from '../components/nutrition/RecipeSearch';
import ShoppingList from '../components/nutrition/ShoppingList';
import NutritionalAnalysis from '../components/nutrition/NutritionalAnalysis';

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
  }, []);

  const loadNutritionData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Load nutrition preferences
      const prefsResponse = await fetch('/api/nutrition/preferences');
      const preferences = prefsResponse.ok ? await prefsResponse.json() : null;
      
      // Load meal plans
      const mealPlansResponse = await fetch('/api/nutrition/meal-plans?limit=5');
      const mealPlans = mealPlansResponse.ok ? await mealPlansResponse.json() : [];
      
      // Load recent recipes
      const recipesResponse = await fetch('/api/nutrition/recipes/search?limit=6');
      const recipes = recipesResponse.ok ? await recipesResponse.json() : [];
      
      // Load shopping lists
      const shoppingListsResponse = await fetch('/api/nutrition/shopping-lists');
      const shoppingLists = shoppingListsResponse.ok ? await shoppingListsResponse.json() : [];
      
      setNutritionData({
        preferences,
        mealPlans,
        recipes,
        shoppingLists,
        nutritionalLogs: []
      });
      
    } catch (err) {
      console.error('Error loading nutrition data:', err);
      setError('Failed to load nutrition data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

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
                  <Icon as={FiUtensils} boxSize={8} color="blue.500" />
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
                  <Icon as={FiBarChart3} boxSize={8} color="purple.500" />
                </HStack>
              </CardBody>
            </Card>
          </SimpleGrid>

          {/* Main Content Tabs */}
          <Card bg={cardBg} borderColor={borderColor}>
            <Tabs index={activeTab} onChange={setActiveTab} variant="enclosed">
              <TabList>
                <Tab>
                  <HStack spacing={2}>
                    <Icon as={FiSettings} />
                    <Text>{t('nutritionPreferences')}</Text>
                  </HStack>
                </Tab>
                <Tab>
                  <HStack spacing={2}>
                    <Icon as={FiUtensils} />
                    <Text>{t('mealPlanning')}</Text>
                  </HStack>
                </Tab>
                <Tab>
                  <HStack spacing={2}>
                    <Icon as={FiBookOpen} />
                    <Text>{t('recipes')}</Text>
                  </HStack>
                </Tab>
                <Tab>
                  <HStack spacing={2}>
                    <Icon as={FiShoppingCart} />
                    <Text>{t('shoppingList')}</Text>
                  </HStack>
                </Tab>
                <Tab>
                  <HStack spacing={2}>
                    <Icon as={FiBarChart3} />
                    <Text>{t('nutritionalAnalysis')}</Text>
                  </HStack>
                </Tab>
              </TabList>

              <TabPanels>
                <TabPanel px={0} py={6}>
                  <NutritionPreferences 
                    preferences={nutritionData?.preferences}
                    onUpdate={handleDataUpdate}
                  />
                </TabPanel>

                <TabPanel px={0} py={6}>
                  <MealPlanning 
                    mealPlans={nutritionData?.mealPlans || []}
                    onUpdate={handleDataUpdate}
                  />
                </TabPanel>

                <TabPanel px={0} py={6}>
                  <RecipeSearch 
                    recipes={nutritionData?.recipes || []}
                    onUpdate={handleDataUpdate}
                  />
                </TabPanel>

                <TabPanel px={0} py={6}>
                  <ShoppingList 
                    shoppingLists={nutritionData?.shoppingLists || []}
                    onUpdate={handleDataUpdate}
                  />
                </TabPanel>

                <TabPanel px={0} py={6}>
                  <NutritionalAnalysis 
                    nutritionalLogs={nutritionData?.nutritionalLogs || []}
                    onUpdate={handleDataUpdate}
                  />
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
