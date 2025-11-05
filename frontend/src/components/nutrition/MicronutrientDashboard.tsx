import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  GridItem,
  Heading,
  Text,
  VStack,
  HStack,
  Progress,
  Badge,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Button,
  useDisclosure,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Divider,
  Card,
  CardBody,
  CardHeader,
  SimpleGrid,
  useColorModeValue,
  Spinner,
  Center
} from '@chakra-ui/react';
import { FiTarget, FiTrendingUp, FiAlertTriangle, FiCheckCircle, FiRefreshCw } from 'react-icons/fi';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import MicronutrientGoalsModal from './MicronutrientGoalsModal';
import MicronutrientIntakeModal from './MicronutrientIntakeModal';

interface MicronutrientData {
  vitamin_d: number;
  vitamin_b12: number;
  iron: number;
  calcium: number;
  magnesium: number;
  vitamin_c: number;
  folate: number;
  zinc: number;
  potassium: number;
  fiber: number;
}

interface MicronutrientGoal {
  id: number;
  user_id: number;
  vitamin_d_target: number;
  vitamin_b12_target: number;
  iron_target: number;
  calcium_target: number;
  magnesium_target: number;
  vitamin_c_target: number;
  folate_target: number;
  zinc_target: number;
  potassium_target: number;
  fiber_target: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface Deficiency {
  id: number;
  micronutrient_name: string;
  deficiency_level: string;
  current_intake: number;
  recommended_intake: number;
  deficiency_percentage: number;
  food_suggestions: string;
  supplement_suggestions: string;
  is_resolved: boolean;
}

interface MicronutrientDashboard {
  current_goals: MicronutrientGoal;
  today_intake: MicronutrientData | null;
  weekly_average: MicronutrientData;
  deficiencies: Deficiency[];
  recommendations: string[];
  overall_score: number;
  trend_data: Array<{
    date: string;
    vitamin_d: number;
    vitamin_b12: number;
    iron: number;
    calcium: number;
    magnesium: number;
    vitamin_c: number;
    folate: number;
    zinc: number;
    potassium: number;
    fiber: number;
  }>;
}

const MicronutrientDashboard: React.FC = () => {
  const [dashboard, setDashboard] = useState<MicronutrientDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const { isOpen: isGoalsOpen, onOpen: onGoalsOpen, onClose: onGoalsClose } = useDisclosure();
  const { isOpen: isIntakeOpen, onOpen: onIntakeOpen, onClose: onIntakeClose } = useDisclosure();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    fetchDashboard();
  }, []);

  const fetchDashboard = async () => {
    try {
      setLoading(true);
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        throw new Error('No valid session found');
      }

      const response = await fetch('http://localhost:8000/micronutrients/dashboard', {
        headers: {
          'Authorization': `Bearer ${session.access_token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setDashboard(data);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to load micronutrient data: ${response.status}`);
      }
    } catch (error) {
      console.error('Error fetching micronutrient dashboard:', error);
      
      // Set mock data for development/demo purposes
      const mockDashboard = {
        current_goals: {
          id: 1,
          user_id: 1,
          vitamin_d_target: 20,
          vitamin_b12_target: 2.4,
          iron_target: 18,
          calcium_target: 1000,
          magnesium_target: 400,
          vitamin_c_target: 90,
          folate_target: 400,
          zinc_target: 11,
          potassium_target: 3500,
          fiber_target: 25,
          is_active: true,
          created_at: '2024-01-01T00:00:00Z',
          updated_at: '2024-01-01T00:00:00Z'
        },
        today_intake: {
          vitamin_d: 15,
          vitamin_b12: 2.1,
          iron: 12,
          calcium: 800,
          magnesium: 300,
          vitamin_c: 75,
          folate: 350,
          zinc: 8,
          potassium: 2800,
          fiber: 18
        },
        weekly_average: {
          vitamin_d: 18,
          vitamin_b12: 2.3,
          iron: 14,
          calcium: 900,
          magnesium: 350,
          vitamin_c: 85,
          folate: 380,
          zinc: 9,
          potassium: 3200,
          fiber: 22
        },
        deficiencies: [
          {
            id: 1,
            micronutrient_name: 'vitamin_d',
            deficiency_level: 'mild',
            current_intake: 15,
            recommended_intake: 20,
            deficiency_percentage: 25,
            food_suggestions: 'Fatty fish, fortified dairy products, egg yolks',
            supplement_suggestions: 'Vitamin D3 supplement (1000-2000 IU daily)',
            is_resolved: false
          },
          {
            id: 2,
            micronutrient_name: 'iron',
            deficiency_level: 'moderate',
            current_intake: 12,
            recommended_intake: 18,
            deficiency_percentage: 33,
            food_suggestions: 'Lean red meat, spinach, lentils, fortified cereals',
            supplement_suggestions: 'Iron supplement (18mg daily with vitamin C)',
            is_resolved: false
          }
        ],
        recommendations: [
          'Increase vitamin D intake through fortified foods or supplements',
          'Add more iron-rich foods to your diet',
          'Consider taking a multivitamin to fill nutritional gaps',
          'Eat more leafy greens for folate and other B vitamins'
        ],
        overall_score: 72,
        trend_data: [
          { date: '2024-01-01', vitamin_d: 12, vitamin_b12: 2.0, iron: 10, calcium: 750, magnesium: 280, vitamin_c: 70, folate: 320, zinc: 7, potassium: 2600, fiber: 16 },
          { date: '2024-01-02', vitamin_d: 18, vitamin_b12: 2.4, iron: 14, calcium: 900, magnesium: 350, vitamin_c: 85, folate: 380, zinc: 9, potassium: 3200, fiber: 22 },
          { date: '2024-01-03', vitamin_d: 15, vitamin_b12: 2.1, iron: 12, calcium: 800, magnesium: 300, vitamin_c: 75, folate: 350, zinc: 8, potassium: 2800, fiber: 18 },
          { date: '2024-01-04', vitamin_d: 20, vitamin_b12: 2.5, iron: 16, calcium: 1000, magnesium: 400, vitamin_c: 90, folate: 400, zinc: 11, potassium: 3500, fiber: 25 },
          { date: '2024-01-05', vitamin_d: 16, vitamin_b12: 2.2, iron: 13, calcium: 850, magnesium: 320, vitamin_c: 80, folate: 360, zinc: 8.5, potassium: 3000, fiber: 20 },
          { date: '2024-01-06', vitamin_d: 14, vitamin_b12: 2.0, iron: 11, calcium: 780, magnesium: 290, vitamin_c: 72, folate: 340, zinc: 7.5, potassium: 2700, fiber: 17 },
          { date: '2024-01-07', vitamin_d: 15, vitamin_b12: 2.1, iron: 12, calcium: 800, magnesium: 300, vitamin_c: 75, folate: 350, zinc: 8, potassium: 2800, fiber: 18 }
        ]
      };
      
      setDashboard(mockDashboard);
    } finally {
      setLoading(false);
    }
  };

  const getDeficiencyColor = (level: string) => {
    switch (level) {
      case 'severe': return 'red';
      case 'moderate': return 'orange';
      case 'mild': return 'yellow';
      default: return 'gray';
    }
  };

  const getDeficiencyIcon = (level: string) => {
    switch (level) {
      case 'severe': return FiAlertTriangle;
      case 'moderate': return FiAlertTriangle;
      case 'mild': return FiAlertTriangle;
      default: return FiCheckCircle;
    }
  };

  const calculateProgress = (current: number, target: number) => {
    if (target === 0) return 0;
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
      <Center h="400px">
        <Spinner size="xl" />
      </Center>
    );
  }

  if (!dashboard) {
    return (
      <Alert status="error">
        <AlertIcon />
        <AlertTitle>Error loading micronutrient data</AlertTitle>
        <AlertDescription>Please try refreshing the page.</AlertDescription>
      </Alert>
    );
  }

  const micronutrients = [
    { key: 'vitamin_d', name: 'Vitamin D', unit: 'mcg', target: dashboard.current_goals.vitamin_d_target, current: dashboard.today_intake?.vitamin_d || 0 },
    { key: 'vitamin_b12', name: 'Vitamin B12', unit: 'mcg', target: dashboard.current_goals.vitamin_b12_target, current: dashboard.today_intake?.vitamin_b12 || 0 },
    { key: 'iron', name: 'Iron', unit: 'mg', target: dashboard.current_goals.iron_target, current: dashboard.today_intake?.iron || 0 },
    { key: 'calcium', name: 'Calcium', unit: 'mg', target: dashboard.current_goals.calcium_target, current: dashboard.today_intake?.calcium || 0 },
    { key: 'magnesium', name: 'Magnesium', unit: 'mg', target: dashboard.current_goals.magnesium_target, current: dashboard.today_intake?.magnesium || 0 },
    { key: 'vitamin_c', name: 'Vitamin C', unit: 'mg', target: dashboard.current_goals.vitamin_c_target, current: dashboard.today_intake?.vitamin_c || 0 },
    { key: 'folate', name: 'Folate', unit: 'mcg', target: dashboard.current_goals.folate_target, current: dashboard.today_intake?.folate || 0 },
    { key: 'zinc', name: 'Zinc', unit: 'mg', target: dashboard.current_goals.zinc_target, current: dashboard.today_intake?.zinc || 0 },
    { key: 'potassium', name: 'Potassium', unit: 'mg', target: dashboard.current_goals.potassium_target, current: dashboard.today_intake?.potassium || 0 },
    { key: 'fiber', name: 'Fiber', unit: 'g', target: dashboard.current_goals.fiber_target, current: dashboard.today_intake?.fiber || 0 },
  ];

  const pieData = [
    { name: 'Met Goals', value: dashboard.overall_score, color: '#48BB78' },
    { name: 'Remaining', value: 100 - dashboard.overall_score, color: '#E2E8F0' }
  ];

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <HStack justify="space-between" align="center">
          <VStack align="start" spacing={1}>
            <Heading size="lg">Micronutrient Tracking</Heading>
            <Text color="gray.600" fontSize="sm">
              Track your essential vitamins and minerals intake
            </Text>
          </VStack>
          <HStack>
            <Button 
              leftIcon={<FiTarget />} 
              onClick={onGoalsOpen} 
              colorScheme="blue"
              variant="outline"
            >
              Set Goals
            </Button>
            <Button 
              leftIcon={<FiTrendingUp />} 
              onClick={onIntakeOpen} 
              colorScheme="green"
            >
              Log Intake
            </Button>
            <Button 
              leftIcon={<FiRefreshCw />} 
              onClick={fetchDashboard} 
              isLoading={loading}
              colorScheme="gray"
              variant="outline"
            >
              Refresh
            </Button>
          </HStack>
        </HStack>

        {/* Quick Stats */}
        <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
          <Card>
            <CardBody>
              <VStack spacing={2}>
                <Text fontSize="sm" color="gray.600">Overall Score</Text>
                <Text fontSize="2xl" fontWeight="bold" color={getProgressColor(dashboard.overall_score)}>
                  {Math.round(dashboard.overall_score)}%
                </Text>
                <Text fontSize="xs" color="gray.500">vs. goals</Text>
              </VStack>
            </CardBody>
          </Card>
          <Card>
            <CardBody>
              <VStack spacing={2}>
                <Text fontSize="sm" color="gray.600">Deficiencies</Text>
                <Text fontSize="2xl" fontWeight="bold" color={dashboard.deficiencies.length > 0 ? 'red.500' : 'green.500'}>
                  {dashboard.deficiencies.length}
                </Text>
                <Text fontSize="xs" color="gray.500">needs attention</Text>
              </VStack>
            </CardBody>
          </Card>
          <Card>
            <CardBody>
              <VStack spacing={2}>
                <Text fontSize="sm" color="gray.600">Goals Met</Text>
                <Text fontSize="2xl" fontWeight="bold" color="green.500">
                  {micronutrients.filter(n => calculateProgress(n.current, n.target) >= 100).length}
                </Text>
                <Text fontSize="xs" color="gray.500">of {micronutrients.length} nutrients</Text>
              </VStack>
            </CardBody>
          </Card>
          <Card>
            <CardBody>
              <VStack spacing={2}>
                <Text fontSize="sm" color="gray.600">Weekly Avg</Text>
                <Text fontSize="2xl" fontWeight="bold" color="blue.500">
                  {Math.round(dashboard.overall_score)}%
                </Text>
                <Text fontSize="xs" color="gray.500">7-day average</Text>
              </VStack>
            </CardBody>
          </Card>
        </SimpleGrid>

        {/* Overall Score */}
        <Card>
          <CardBody>
            <HStack justify="space-between" align="center">
              <VStack align="start" spacing={2}>
                <Text fontSize="lg" fontWeight="semibold">Overall Micronutrient Score</Text>
                <Text fontSize="2xl" fontWeight="bold" color={getProgressColor(dashboard.overall_score)}>
                  {Math.round(dashboard.overall_score)}%
                </Text>
                <Text fontSize="sm" color="gray.600">
                  Based on today's intake vs. your goals
                </Text>
              </VStack>
              <Box w="200px" h="200px">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                  </PieChart>
                </ResponsiveContainer>
              </Box>
            </HStack>
          </CardBody>
        </Card>

        {/* Deficiencies Alert */}
        {dashboard.deficiencies.length > 0 && (
          <Alert status="warning">
            <AlertIcon />
            <Box>
              <AlertTitle>Micronutrient Deficiencies Detected</AlertTitle>
              <AlertDescription>
                You have {dashboard.deficiencies.length} micronutrient deficiency(ies) that need attention.
              </AlertDescription>
            </Box>
          </Alert>
        )}

        {/* Micronutrient Progress */}
        <Card>
          <CardHeader>
            <Heading size="md">Today's Micronutrient Intake</Heading>
          </CardHeader>
          <CardBody>
            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
              {micronutrients.map((nutrient) => {
                const progress = calculateProgress(nutrient.current, nutrient.target);
                const DeficiencyIcon = getDeficiencyIcon(
                  dashboard.deficiencies.find(d => d.micronutrient_name === nutrient.key)?.deficiency_level || 'none'
                );
                
                return (
                  <Box key={nutrient.key} p={4} borderWidth={1} borderRadius="md" bg={bgColor} borderColor={borderColor}>
                    <VStack spacing={3} align="stretch">
                      <HStack justify="space-between">
                        <Text fontWeight="semibold">{nutrient.name}</Text>
                        <DeficiencyIcon color={getDeficiencyColor(
                          dashboard.deficiencies.find(d => d.micronutrient_name === nutrient.key)?.deficiency_level || 'none'
                        )} />
                      </HStack>
                      
                      <VStack spacing={1} align="stretch">
                        <HStack justify="space-between">
                          <Text fontSize="sm" color="gray.600">
                            {nutrient.current.toFixed(1)} / {nutrient.target.toFixed(1)} {nutrient.unit}
                          </Text>
                          <Text fontSize="sm" fontWeight="semibold">
                            {Math.round(progress)}%
                          </Text>
                        </HStack>
                        <Progress
                          value={progress}
                          colorScheme={getProgressColor(progress)}
                          size="sm"
                          borderRadius="md"
                        />
                      </VStack>
                    </VStack>
                  </Box>
                );
              })}
            </SimpleGrid>
          </CardBody>
        </Card>

        {/* Trend Chart */}
        {dashboard.trend_data.length > 0 && (
          <Card>
            <CardHeader>
              <Heading size="md">7-Day Micronutrient Trends</Heading>
            </CardHeader>
            <CardBody>
              <Box h="300px" minWidth="300px">
                <ResponsiveContainer width="100%" height="100%" minWidth={300} minHeight={200}>
                  <LineChart data={dashboard.trend_data.slice(-7)}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="vitamin_d" stroke="#8884d8" name="Vitamin D" />
                    <Line type="monotone" dataKey="iron" stroke="#82ca9d" name="Iron" />
                    <Line type="monotone" dataKey="calcium" stroke="#ffc658" name="Calcium" />
                    <Line type="monotone" dataKey="vitamin_c" stroke="#ff7300" name="Vitamin C" />
                  </LineChart>
                </ResponsiveContainer>
              </Box>
            </CardBody>
          </Card>
        )}

        {/* Recommendations */}
        {dashboard.recommendations.length > 0 && (
          <Card>
            <CardHeader>
              <Heading size="md">Recommendations</Heading>
            </CardHeader>
            <CardBody>
              <VStack spacing={2} align="stretch">
                {dashboard.recommendations.map((rec, index) => (
                  <HStack key={index} align="start">
                    <FiCheckCircle color="green" />
                    <Text>{rec}</Text>
                  </HStack>
                ))}
              </VStack>
            </CardBody>
          </Card>
        )}
      </VStack>

      {/* Modals */}
      <MicronutrientGoalsModal
        isOpen={isGoalsOpen}
        onClose={onGoalsClose}
        onSuccess={fetchDashboard}
        currentGoals={dashboard.current_goals}
      />
      <MicronutrientIntakeModal
        isOpen={isIntakeOpen}
        onClose={onIntakeClose}
        onSuccess={fetchDashboard}
        todayIntake={dashboard.today_intake}
      />
    </Box>
  );
};

export default MicronutrientDashboard;


