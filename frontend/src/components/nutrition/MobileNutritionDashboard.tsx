import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  SimpleGrid,
  Card,
  CardBody,
  CardHeader,
  Badge,
  Progress,
  useColorModeValue,
  useBreakpointValue,
  Icon,
  Divider,
  Collapse,
  IconButton,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
} from '@chakra-ui/react';
import { FiChevronDown, FiChevronUp, FiTrendingUp, FiTarget, FiCoffee, FiBarChart } from 'react-icons/fi';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface NutritionData {
  dailyCalories: number;
  dailyProtein: number;
  dailyCarbs: number;
  dailyFat: number;
  dailyFiber: number;
  dailySodium: number;
  weeklyTrend: Array<{
    date: string;
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
  }>;
  goals: {
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
    fiber: number;
    sodium: number;
  };
  recommendations: string[];
}

const MobileNutritionDashboard: React.FC = () => {
  const [nutritionData, setNutritionData] = useState<NutritionData | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['overview']));
  
  const isMobile = useBreakpointValue({ base: true, md: false });
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  useEffect(() => {
    // Simulate data loading
    setTimeout(() => {
      setNutritionData({
        dailyCalories: 1850,
        dailyProtein: 120,
        dailyCarbs: 180,
        dailyFat: 65,
        dailyFiber: 25,
        dailySodium: 2200,
        weeklyTrend: [
          { date: 'Mon', calories: 1800, protein: 115, carbs: 175, fat: 60 },
          { date: 'Tue', calories: 1900, protein: 125, carbs: 185, fat: 70 },
          { date: 'Wed', calories: 1750, protein: 110, carbs: 170, fat: 55 },
          { date: 'Thu', calories: 2000, protein: 130, carbs: 200, fat: 75 },
          { date: 'Fri', calories: 1850, protein: 120, carbs: 180, fat: 65 },
          { date: 'Sat', calories: 2100, protein: 140, carbs: 210, fat: 80 },
          { date: 'Sun', calories: 1950, protein: 125, carbs: 190, fat: 70 },
        ],
        goals: {
          calories: 2000,
          protein: 150,
          carbs: 200,
          fat: 80,
          fiber: 30,
          sodium: 2300,
        },
        recommendations: [
          'Increase protein intake by 20g',
          'Add more fiber-rich foods',
          'Consider reducing sodium intake',
        ],
      });
      setLoading(false);
    }, 1000);
  }, []);

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const calculateProgress = (current: number, target: number) => {
    return Math.min(100, (current / target) * 100);
  };

  const getProgressColor = (progress: number) => {
    if (progress >= 100) return 'green';
    if (progress >= 75) return 'blue';
    if (progress >= 50) return 'yellow';
    return 'red';
  };

  if (loading) {
    return (
      <Box p={4} textAlign="center">
        <Text>Loading nutrition data...</Text>
      </Box>
    );
  }

  if (!nutritionData) {
    return (
      <Box p={4} textAlign="center">
        <Text>No nutrition data available</Text>
      </Box>
    );
  }

  const macroData = [
    { name: 'Protein', value: nutritionData.dailyProtein, target: nutritionData.goals.protein, unit: 'g', color: '#8884d8' },
    { name: 'Carbs', value: nutritionData.dailyCarbs, target: nutritionData.goals.carbs, unit: 'g', color: '#82ca9d' },
    { name: 'Fat', value: nutritionData.dailyFat, target: nutritionData.goals.fat, unit: 'g', color: '#ffc658' },
  ];

  return (
    <VStack spacing={4} align="stretch" p={4}>
      {/* Header */}
      <HStack justify="space-between" align="center">
        <Text fontSize="xl" fontWeight="bold">
          Nutrition Dashboard
        </Text>
        <Badge colorScheme="green" fontSize="sm">
          Today
        </Badge>
      </HStack>

      {/* Overview Section */}
      <Card bg={bgColor} borderColor={borderColor}>
        <CardHeader pb={2}>
          <HStack justify="space-between">
            <HStack>
              <Icon as={FiBarChart} />
              <Text fontWeight="semibold">Overview</Text>
            </HStack>
            <IconButton
              aria-label="Toggle overview"
              icon={expandedSections.has('overview') ? <FiChevronUp /> : <FiChevronDown />}
              size="sm"
              variant="ghost"
              onClick={() => toggleSection('overview')}
            />
          </HStack>
        </CardHeader>
        <Collapse in={expandedSections.has('overview')}>
          <CardBody pt={0}>
            <VStack spacing={4}>
              {/* Calories */}
              <Box w="full">
                <HStack justify="space-between" mb={2}>
                  <Text fontSize="sm" fontWeight="medium">Calories</Text>
                  <Text fontSize="sm" color={textColor}>
                    {nutritionData.dailyCalories} / {nutritionData.goals.calories}
                  </Text>
                </HStack>
                <Progress
                  value={calculateProgress(nutritionData.dailyCalories, nutritionData.goals.calories)}
                  colorScheme={getProgressColor(calculateProgress(nutritionData.dailyCalories, nutritionData.goals.calories))}
                  size="lg"
                  borderRadius="md"
                />
              </Box>

              {/* Macros Grid */}
              <SimpleGrid columns={2} spacing={3} w="full">
                {macroData.map((macro) => (
                  <Box key={macro.name} p={3} borderWidth={1} borderRadius="md" borderColor={borderColor}>
                    <VStack spacing={2}>
                      <Text fontSize="sm" fontWeight="medium">{macro.name}</Text>
                      <Text fontSize="lg" fontWeight="bold" color={macro.color}>
                        {macro.value}{macro.unit}
                      </Text>
                      <Text fontSize="xs" color={textColor}>
                        of {macro.target}{macro.unit}
                      </Text>
                      <Progress
                        value={calculateProgress(macro.value, macro.target)}
                        colorScheme={getProgressColor(calculateProgress(macro.value, macro.target))}
                        size="sm"
                        w="full"
                      />
                    </VStack>
                  </Box>
                ))}
              </SimpleGrid>
            </VStack>
          </CardBody>
        </Collapse>
      </Card>

      {/* Weekly Trend Section */}
      <Card bg={bgColor} borderColor={borderColor}>
        <CardHeader pb={2}>
          <HStack justify="space-between">
            <HStack>
              <Icon as={FiTrendingUp} />
              <Text fontWeight="semibold">Weekly Trend</Text>
            </HStack>
            <IconButton
              aria-label="Toggle trend"
              icon={expandedSections.has('trend') ? <FiChevronUp /> : <FiChevronDown />}
              size="sm"
              variant="ghost"
              onClick={() => toggleSection('trend')}
            />
          </HStack>
        </CardHeader>
        <Collapse in={expandedSections.has('trend')}>
          <CardBody pt={0}>
            <Box h="200px">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={nutritionData.weeklyTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="calories" stroke="#8884d8" strokeWidth={2} />
                  <Line type="monotone" dataKey="protein" stroke="#82ca9d" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </Box>
          </CardBody>
        </Collapse>
      </Card>

      {/* Goals Section */}
      <Card bg={bgColor} borderColor={borderColor}>
        <CardHeader pb={2}>
          <HStack justify="space-between">
            <HStack>
              <Icon as={FiTarget} />
              <Text fontWeight="semibold">Goals Progress</Text>
            </HStack>
            <IconButton
              aria-label="Toggle goals"
              icon={expandedSections.has('goals') ? <FiChevronUp /> : <FiChevronDown />}
              size="sm"
              variant="ghost"
              onClick={() => toggleSection('goals')}
            />
          </HStack>
        </CardHeader>
        <Collapse in={expandedSections.has('goals')}>
          <CardBody pt={0}>
            <VStack spacing={3}>
              <SimpleGrid columns={2} spacing={3} w="full">
                <Stat textAlign="center">
                  <StatLabel fontSize="xs">Fiber</StatLabel>
                  <StatNumber fontSize="md">{nutritionData.dailyFiber}g</StatNumber>
                  <StatHelpText fontSize="xs">
                    <StatArrow type="increase" />
                    {Math.round(calculateProgress(nutritionData.dailyFiber, nutritionData.goals.fiber))}%
                  </StatHelpText>
                </Stat>
                <Stat textAlign="center">
                  <StatLabel fontSize="xs">Sodium</StatLabel>
                  <StatNumber fontSize="md">{nutritionData.dailySodium}mg</StatNumber>
                  <StatHelpText fontSize="xs">
                    <StatArrow type="decrease" />
                    {Math.round(calculateProgress(nutritionData.dailySodium, nutritionData.goals.sodium))}%
                  </StatHelpText>
                </Stat>
              </SimpleGrid>
            </VStack>
          </CardBody>
        </Collapse>
      </Card>

      {/* Recommendations Section */}
      <Card bg={bgColor} borderColor={borderColor}>
        <CardHeader pb={2}>
          <HStack justify="space-between">
            <HStack>
              <Icon as={FiCoffee} />
              <Text fontWeight="semibold">Recommendations</Text>
            </HStack>
            <IconButton
              aria-label="Toggle recommendations"
              icon={expandedSections.has('recommendations') ? <FiChevronUp /> : <FiChevronDown />}
              size="sm"
              variant="ghost"
              onClick={() => toggleSection('recommendations')}
            />
          </HStack>
        </CardHeader>
        <Collapse in={expandedSections.has('recommendations')}>
          <CardBody pt={0}>
            <VStack spacing={2} align="stretch">
              {nutritionData.recommendations.map((rec, index) => (
                <HStack key={index} align="start">
                  <Text fontSize="sm" color="green.500">•</Text>
                  <Text fontSize="sm">{rec}</Text>
                </HStack>
              ))}
            </VStack>
          </CardBody>
        </Collapse>
      </Card>

      {/* Quick Actions */}
      <HStack spacing={2} justify="center" pt={4}>
        <Button size="sm" colorScheme="blue" flex={1}>
          Log Meal
        </Button>
        <Button size="sm" colorScheme="green" flex={1}>
          View Recipes
        </Button>
        <Button size="sm" colorScheme="purple" flex={1}>
          Set Goals
        </Button>
      </HStack>
    </VStack>
  );
};

export default MobileNutritionDashboard;







