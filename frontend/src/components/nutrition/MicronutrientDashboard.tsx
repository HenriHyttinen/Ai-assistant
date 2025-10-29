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
import { FiTarget, FiTrendingUp, FiAlertTriangle, FiCheckCircle } from 'react-icons/fi';
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
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        console.error('No valid session found');
        return;
      }

      const response = await fetch('http://localhost:8000/micronutrients/dashboard', {
        headers: {
          'Authorization': `Bearer ${session.access_token}`
        }
      });
      if (response.ok) {
        const data = await response.json();
        setDashboard(data);
      }
    } catch (error) {
      console.error('Error fetching micronutrient dashboard:', error);
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
          <Heading size="lg">Micronutrient Tracking</Heading>
          <HStack>
            <Button leftIcon={<FiTarget />} onClick={onGoalsOpen} colorScheme="blue">
              Set Goals
            </Button>
            <Button leftIcon={<FiTrendingUp />} onClick={onIntakeOpen} colorScheme="green">
              Log Intake
            </Button>
          </HStack>
        </HStack>

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
