import {
  Box,
  Card,
  CardHeader,
  CardBody,
  Heading,
  Text,
  VStack,
  HStack,
  Button,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  useToast,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Spinner,
  useBreakpointValue,
} from '@chakra-ui/react';
import { useState, useEffect } from 'react';
import { useApp } from '../../contexts/AppContext';
import { t } from '../../utils/translations';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts';

interface IngredientAnalyticsCardProps {
  // No props needed - fetches data internally
}

interface IngredientData {
  name: string;
  total_quantity: number;
  unit: string;
  recipe_count: number;
  database_recipes: number;
  ai_recipes: number;
  categories: string[];
}

interface CategoryData {
  category: string;
  recipe_count: number;
  total_quantity: number;
}

interface AnalyticsData {
  total_ingredients: number;
  total_recipes: number;
  database_recipes: number;
  ai_recipes: number;
  top_ingredients: IngredientData[];
  category_distribution: CategoryData[];
  all_ingredients: IngredientData[];
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d', '#ffc658', '#ff7c7c'];

const IngredientAnalyticsCard: React.FC<IngredientAnalyticsCardProps> = () => {
  const { language } = useApp();
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();
  const [loading, setLoading] = useState(false);
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData | null>(null);
  const isMobile = useBreakpointValue({ base: true, md: false });

  const fetchAnalytics = async () => {
    setLoading(true);
    try {
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        toast({ 
          title: 'Please log in', 
          status: 'warning', 
          duration: 2500, 
          isClosable: true 
        });
        return;
      }

      const response = await fetch('http://localhost:8000/nutrition/ingredients/analytics', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAnalyticsData(data);
      } else {
        throw new Error('Failed to fetch ingredient analytics');
      }
    } catch (err: any) {
      console.error('Error fetching ingredient analytics:', err);
      toast({
        title: 'Error',
        description: 'Failed to load ingredient analytics',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen && !analyticsData) {
      fetchAnalytics();
    }
  }, [isOpen]);

  // Prepare chart data
  const topIngredientsChartData = analyticsData?.top_ingredients.map(ing => ({
    name: ing.name.length > 15 ? ing.name.substring(0, 15) + '...' : ing.name,
    fullName: ing.name,
    quantity: Math.round(ing.total_quantity),
    recipes: ing.recipe_count,
    database: ing.database_recipes,
    ai: ing.ai_recipes,
  })) || [];

  const categoryChartData = analyticsData?.category_distribution.map(cat => ({
    name: cat.category,
    quantity: Math.round(cat.total_quantity),
    recipes: cat.recipe_count,
  })) || [];

  return (
    <>
      <Card>
        <CardHeader>
          <HStack justify="space-between">
            <Heading size="md">Ingredient Analytics</Heading>
            <Button 
              size="sm" 
              colorScheme="blue" 
              variant="outline"
              onClick={() => {
                onOpen();
                if (!analyticsData) {
                  fetchAnalytics();
                }
              }}
            >
              Graphs
            </Button>
          </HStack>
        </CardHeader>
        <CardBody>
          <VStack spacing={4} align="stretch">
            <SimpleGrid columns={2} spacing={4}>
              <Stat>
                <StatLabel>Total Ingredients</StatLabel>
                <StatNumber fontSize="2xl" color="blue.600">
                  {analyticsData?.total_ingredients || 0}
                </StatNumber>
                <StatHelpText>Unique ingredients</StatHelpText>
              </Stat>
              <Stat>
                <StatLabel>Total Recipes</StatLabel>
                <StatNumber fontSize="2xl" color="green.600">
                  {analyticsData?.total_recipes || 0}
                </StatNumber>
                <StatHelpText>
                  {analyticsData?.database_recipes || 0} database + {analyticsData?.ai_recipes || 0} AI
                </StatHelpText>
              </Stat>
            </SimpleGrid>
          </VStack>
        </CardBody>
      </Card>

      {/* Ingredient Analytics Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size={isMobile ? "sm" : "xl"}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Ingredient Analytics</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {loading ? (
              <VStack spacing={4} py={8}>
                <Spinner size="xl" color="blue.500" />
                <Text>Loading ingredient analytics...</Text>
              </VStack>
            ) : analyticsData ? (
              <VStack spacing={6} align="stretch">
                {/* Overview Stats */}
                <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
                  <Stat textAlign="center">
                    <StatLabel>Total Ingredients</StatLabel>
                    <StatNumber fontSize="xl" color="blue.600">
                      {analyticsData.total_ingredients}
                    </StatNumber>
                  </Stat>
                  <Stat textAlign="center">
                    <StatLabel>Total Recipes</StatLabel>
                    <StatNumber fontSize="xl" color="green.600">
                      {analyticsData.total_recipes}
                    </StatNumber>
                  </Stat>
                  <Stat textAlign="center">
                    <StatLabel>Database Recipes</StatLabel>
                    <StatNumber fontSize="xl" color="purple.600">
                      {analyticsData.database_recipes}
                    </StatNumber>
                  </Stat>
                  <Stat textAlign="center">
                    <StatLabel>AI Recipes</StatLabel>
                    <StatNumber fontSize="xl" color="orange.600">
                      {analyticsData.ai_recipes}
                    </StatNumber>
                  </Stat>
                </SimpleGrid>

                {/* Top Ingredients Bar Chart */}
                {topIngredientsChartData.length > 0 && (
                  <Box>
                    <Text fontSize="lg" fontWeight="bold" mb={4}>
                      Top 20 Most Used Ingredients
                    </Text>
                    <Box p={4} bg="white" borderRadius="md" border="1px" borderColor="gray.200" height="400px" minWidth="300px">
                      <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={topIngredientsChartData}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                          <XAxis 
                            dataKey="name" 
                            stroke="#718096"
                            angle={-45}
                            textAnchor="end"
                            height={100}
                          />
                          <YAxis stroke="#718096" />
                          <Tooltip 
                            formatter={(value: any, name: any, props: any) => {
                              if (name === 'quantity') {
                                return [`${value} g`, 'Total Quantity'];
                              } else if (name === 'recipes') {
                                return [`${value} recipes`, 'Recipe Count'];
                              }
                              return [value, name];
                            }}
                            labelFormatter={(label: any, payload: any) => {
                              if (payload && payload[0] && payload[0].payload) {
                                return payload[0].payload.fullName;
                              }
                              return label;
                            }}
                          />
                          <Bar dataKey="quantity" fill="#0088FE" name="Total Quantity (g)" />
                        </BarChart>
                      </ResponsiveContainer>
                    </Box>
                  </Box>
                )}

                {/* Category Distribution Pie Chart */}
                {categoryChartData.length > 0 && (
                  <Box>
                    <Text fontSize="lg" fontWeight="bold" mb={4}>
                      Ingredient Category Distribution
                    </Text>
                    <Box p={4} bg="white" borderRadius="md" border="1px" borderColor="gray.200" height="400px" minWidth="300px">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie
                            data={categoryChartData}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                            outerRadius={120}
                            fill="#8884d8"
                            dataKey="quantity"
                          >
                            {categoryChartData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip 
                            formatter={(value: any) => [`${Math.round(value)} g`, 'Total Quantity']}
                          />
                          <Legend />
                        </PieChart>
                      </ResponsiveContainer>
                    </Box>
                  </Box>
                )}

                {/* Top Ingredients List */}
                {analyticsData.top_ingredients.length > 0 && (
                  <Box>
                    <Text fontSize="lg" fontWeight="bold" mb={4}>
                      Top Ingredients Details
                    </Text>
                    <VStack spacing={2} align="stretch" maxH="300px" overflowY="auto">
                      {analyticsData.top_ingredients.slice(0, 10).map((ing, index) => (
                        <HStack key={index} justify="space-between" p={2} bg="gray.50" borderRadius="md">
                          <VStack align="start" spacing={0}>
                            <Text fontWeight="semibold">{ing.name}</Text>
                            <Text fontSize="sm" color="gray.600">
                              {ing.recipe_count} recipes ({ing.database_recipes} DB, {ing.ai_recipes} AI)
                            </Text>
                          </VStack>
                          <Text fontWeight="bold" color="blue.600">
                            {Math.round(ing.total_quantity)} {ing.unit}
                          </Text>
                        </HStack>
                      ))}
                    </VStack>
                  </Box>
                )}
              </VStack>
            ) : (
              <VStack spacing={4} py={8}>
                <Text>No ingredient data available</Text>
                <Button onClick={fetchAnalytics} colorScheme="blue">
                  Load Analytics
                </Button>
              </VStack>
            )}
          </ModalBody>
        </ModalContent>
      </Modal>
    </>
  );
};

export default IngredientAnalyticsCard;

