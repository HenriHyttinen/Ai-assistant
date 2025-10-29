import React, { useState, useMemo } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Badge,
  Progress,
  useColorModeValue,
  SimpleGrid,
  Select,
  Button,
  ButtonGroup,
  Tooltip,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Divider,
  Flex,
  Icon,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Spinner,
  Alert,
  AlertIcon,
  Center
} from '@chakra-ui/react';
import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  Area,
  AreaChart,
  Legend,
  ScatterChart,
  Scatter,
  RadialBarChart,
  RadialBar,
  ComposedChart
} from 'recharts';
import { 
  FiPieChart, 
  FiBarChart, 
  FiTrendingUp, 
  FiTarget,
  FiActivity,
  FiZap,
  FiInfo,
  FiCalendar,
  FiClock,
  FiHeart,
  FiAward,
  FiAlertTriangle,
  FiCheckCircle
} from 'react-icons/fi';

interface NutritionData {
  calories: number;
  protein: number;
  carbs: number;
  fats: number;
  fiber?: number;
  sugar?: number;
  sodium?: number;
}

interface NutritionTargets {
  calories: number;
  protein: number;
  carbs: number;
  fats: number;
}

interface DailyBreakdown {
  date: string;
  calories: number;
  protein: number;
  carbs: number;
  fats: number;
  meals: Array<{
    meal_type: string;
    calories: number;
    protein: number;
    carbs: number;
    fats: number;
    time: string;
  }>;
}

interface MealDistribution {
  breakfast: number;
  lunch: number;
  dinner: number;
  snacks: number;
}

interface AdvancedNutritionDashboardProps {
  currentData: NutritionData;
  targets: NutritionTargets;
  dailyBreakdown?: DailyBreakdown[];
  mealDistribution?: MealDistribution;
  period?: 'daily' | 'weekly' | 'monthly';
  onPeriodChange?: (period: 'daily' | 'weekly' | 'monthly') => void;
  aiInsights?: {
    achievements: string[];
    concerns: string[];
    suggestions: string[];
    trends: string[];
  };
}

const AdvancedNutritionDashboard: React.FC<AdvancedNutritionDashboardProps> = ({
  currentData,
  targets,
  dailyBreakdown = [],
  mealDistribution,
  period = 'daily',
  onPeriodChange,
  aiInsights
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [chartType, setChartType] = useState<'pie' | 'bar' | 'trend' | 'radial'>('pie');
  const [isContainerReady, setIsContainerReady] = useState(false);
  const containerRef = React.useRef<HTMLDivElement>(null);
  
  // Ensure container is ready before rendering charts
  React.useEffect(() => {
    const checkContainerSize = () => {
      if (containerRef.current) {
        const rect = containerRef.current.getBoundingClientRect();
        if (rect.width > 0 && rect.height > 0) {
          setIsContainerReady(true);
        }
      }
    };

    // Initial check with longer delay
    const timer = setTimeout(checkContainerSize, 500);
    
    // Use ResizeObserver to detect when container is properly sized
    let resizeObserver: ResizeObserver | null = null;
    if (containerRef.current) {
      resizeObserver = new ResizeObserver((entries) => {
        for (const entry of entries) {
          if (entry.contentRect.width > 0 && entry.contentRect.height > 0) {
            setIsContainerReady(true);
          }
        }
      });
      resizeObserver.observe(containerRef.current);
    }

    return () => {
      clearTimeout(timer);
      if (resizeObserver) {
        resizeObserver.disconnect();
      }
    };
  }, []);
  
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  // Calculate macronutrient percentages
  const macroPercentages = useMemo(() => {
    const proteinCalories = currentData.protein * 4;
    const carbsCalories = currentData.carbs * 4;
    const fatsCalories = currentData.fats * 9;
    const totalCalories = proteinCalories + carbsCalories + fatsCalories;

    if (totalCalories === 0) {
      return { protein: 0, carbs: 0, fats: 0 };
    }

    return {
      protein: (proteinCalories / totalCalories) * 100,
      carbs: (carbsCalories / totalCalories) * 100,
      fats: (fatsCalories / totalCalories) * 100
    };
  }, [currentData]);

  // Calculate progress towards targets
  const progressData = useMemo(() => {
    return {
      calories: (currentData.calories / targets.calories) * 100,
      protein: (currentData.protein / targets.protein) * 100,
      carbs: (currentData.carbs / targets.carbs) * 100,
      fats: (currentData.fats / targets.fats) * 100
    };
  }, [currentData, targets]);

  // Prepare radial chart data for progress visualization
  const radialData = [
    {
      name: 'Calories',
      value: Math.min(progressData.calories, 100),
      target: 100,
      color: '#3182ce'
    },
    {
      name: 'Protein',
      value: Math.min(progressData.protein, 100),
      target: 100,
      color: '#38a169'
    },
    {
      name: 'Carbs',
      value: Math.min(progressData.carbs, 100),
      target: 100,
      color: '#d69e2e'
    },
    {
      name: 'Fats',
      value: Math.min(progressData.fats, 100),
      target: 100,
      color: '#e53e3e'
    }
  ];

  // Prepare meal distribution data
  const mealData = mealDistribution ? [
    { name: 'Breakfast', value: mealDistribution.breakfast, color: '#ff6b6b' },
    { name: 'Lunch', value: mealDistribution.lunch, color: '#4ecdc4' },
    { name: 'Dinner', value: mealDistribution.dinner, color: '#45b7d1' },
    { name: 'Snacks', value: mealDistribution.snacks, color: '#96ceb4' }
  ] : [];

  // Prepare trend data
  const trendData = dailyBreakdown.map(day => ({
    date: new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    calories: day.calories,
    protein: day.protein,
    carbs: day.carbs,
    fats: day.fats,
    total: day.calories
  }));

  // Calculate weekly averages
  const weeklyAverages = useMemo(() => {
    if (dailyBreakdown.length === 0) return null;
    
    const totals = dailyBreakdown.reduce((acc, day) => ({
      calories: acc.calories + day.calories,
      protein: acc.protein + day.protein,
      carbs: acc.carbs + day.carbs,
      fats: acc.fats + day.fats
    }), { calories: 0, protein: 0, carbs: 0, fats: 0 });

    const days = dailyBreakdown.length;
    return {
      calories: totals.calories / days,
      protein: totals.protein / days,
      carbs: totals.carbs / days,
      fats: totals.fats / days
    };
  }, [dailyBreakdown]);

  // Calculate nutrition score
  const nutritionScore = useMemo(() => {
    const scores = Object.values(progressData);
    const averageScore = scores.reduce((sum, score) => sum + Math.min(score, 100), 0) / scores.length;
    return Math.round(averageScore);
  }, [progressData]);

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'green';
    if (score >= 70) return 'yellow';
    return 'red';
  };

  const getScoreIcon = (score: number) => {
    if (score >= 90) return FiCheckCircle;
    if (score >= 70) return FiTarget;
    return FiAlertTriangle;
  };

  // Custom tooltip components
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <Box
          bg="white"
          p={3}
          borderRadius="md"
          boxShadow="lg"
          border="1px solid"
          borderColor="gray.200"
        >
          <Text fontWeight="bold" mb={2}>{label}</Text>
          {payload.map((entry: any, index: number) => (
            <Text key={index} fontSize="sm" color={entry.color}>
              {entry.name}: {entry.value.toFixed(1)}
            </Text>
          ))}
        </Box>
      );
    }
    return null;
  };

  return (
    <VStack spacing={6} align="stretch" ref={containerRef}>
      {/* Header with nutrition score */}
      <Card bg={cardBg} borderColor={borderColor}>
        <CardHeader>
          <Flex justify="space-between" align="center" wrap="wrap" gap={4}>
            <VStack align="start" spacing={1}>
              <Heading size="lg" display="flex" alignItems="center" gap={2}>
                <Icon as={FiActivity} />
                Advanced Nutrition Dashboard
              </Heading>
              <Text color={textColor}>
                Comprehensive nutritional analysis and insights
              </Text>
            </VStack>
            
            <VStack align="end" spacing={2}>
              <HStack>
                <Icon as={getScoreIcon(nutritionScore)} color={`${getScoreColor(nutritionScore)}.500`} />
                <Text fontWeight="bold" fontSize="lg">
                  Nutrition Score
                </Text>
              </HStack>
              <Badge
                colorScheme={getScoreColor(nutritionScore)}
                fontSize="lg"
                px={3}
                py={1}
                borderRadius="full"
              >
                {nutritionScore}/100
              </Badge>
            </VStack>
          </Flex>
        </CardHeader>
      </Card>

      {/* Main dashboard tabs */}
      <Tabs index={activeTab} onChange={setActiveTab} variant="enclosed">
        <TabList>
          <Tab>Overview</Tab>
          <Tab>Macronutrients</Tab>
          <Tab>Meal Patterns</Tab>
          <Tab>Trends</Tab>
          <Tab>Insights</Tab>
        </TabList>

        <TabPanels>
          {/* Overview Tab */}
          <TabPanel px={0}>
            <VStack spacing={6} align="stretch">
              {/* Quick stats */}
              <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
                <Card bg={cardBg} borderColor={borderColor}>
                  <CardBody>
                    <Stat>
                      <StatLabel>Calories</StatLabel>
                      <StatNumber color="blue.500">
                        {currentData.calories.toFixed(0)}
                      </StatNumber>
                      <StatHelpText>
                        {targets.calories.toFixed(0)} target
                      </StatHelpText>
                    </Stat>
                  </CardBody>
                </Card>

                <Card bg={cardBg} borderColor={borderColor}>
                  <CardBody>
                    <Stat>
                      <StatLabel>Protein</StatLabel>
                      <StatNumber color="green.500">
                        {currentData.protein.toFixed(1)}g
                      </StatNumber>
                      <StatHelpText>
                        {targets.protein.toFixed(1)}g target
                      </StatHelpText>
                    </Stat>
                  </CardBody>
                </Card>

                <Card bg={cardBg} borderColor={borderColor}>
                  <CardBody>
                    <Stat>
                      <StatLabel>Carbs</StatLabel>
                      <StatNumber color="yellow.500">
                        {currentData.carbs.toFixed(1)}g
                      </StatNumber>
                      <StatHelpText>
                        {targets.carbs.toFixed(1)}g target
                      </StatHelpText>
                    </Stat>
                  </CardBody>
                </Card>

                <Card bg={cardBg} borderColor={borderColor}>
                  <CardBody>
                    <Stat>
                      <StatLabel>Fats</StatLabel>
                      <StatNumber color="orange.500">
                        {currentData.fats.toFixed(1)}g
                      </StatNumber>
                      <StatHelpText>
                        {targets.fats.toFixed(1)}g target
                      </StatHelpText>
                    </Stat>
                  </CardBody>
                </Card>
              </SimpleGrid>

              {/* Progress visualization */}
              <Card bg={cardBg} borderColor={borderColor}>
                <CardHeader>
                  <Heading size="md">Progress Towards Goals</Heading>
                </CardHeader>
                <CardBody>
                  <Box height="300px" minWidth="300px" width="100%">
                    {isContainerReady ? (
                      <ResponsiveContainer width="100%" height="100%" minWidth={300} minHeight={200}>
                        <RadialBarChart cx="50%" cy="50%" innerRadius="20%" outerRadius="80%" data={radialData}>
                          <RadialBar dataKey="value" cornerRadius={10} fill="#8884d8" />
                          <RechartsTooltip content={<CustomTooltip />} />
                          <Legend />
                        </RadialBarChart>
                      </ResponsiveContainer>
                    ) : (
                      <Flex height="100%" align="center" justify="center">
                        <Spinner size="lg" color="blue.500" />
                      </Flex>
                    )}
                  </Box>
                </CardBody>
              </Card>
            </VStack>
          </TabPanel>

          {/* Macronutrients Tab */}
          <TabPanel px={0}>
            <VStack spacing={6} align="stretch">
              {/* Chart type selector */}
              <Card bg={cardBg} borderColor={borderColor}>
                <CardBody>
                  <HStack justify="space-between" wrap="wrap" gap={4}>
                    <Heading size="md">Macronutrient Analysis</Heading>
                    <ButtonGroup size="sm" isAttached variant="outline">
                      <Button
                        leftIcon={<FiPieChart />}
                        onClick={() => setChartType('pie')}
                        colorScheme={chartType === 'pie' ? 'blue' : undefined}
                      >
                        Distribution
                      </Button>
                      <Button
                        leftIcon={<FiBarChart />}
                        onClick={() => setChartType('bar')}
                        colorScheme={chartType === 'bar' ? 'blue' : undefined}
                      >
                        Comparison
                      </Button>
                      <Button
                        leftIcon={<FiTrendingUp />}
                        onClick={() => setChartType('trend')}
                        colorScheme={chartType === 'trend' ? 'blue' : undefined}
                        isDisabled={dailyBreakdown.length === 0}
                      >
                        Trends
                      </Button>
                    </ButtonGroup>
                  </HStack>
                </CardBody>
              </Card>

              {/* Chart visualization */}
              <Card bg={cardBg} borderColor={borderColor}>
                <CardBody>
                  <Box height="400px" minWidth="400px" width="100%">
                    {isContainerReady && chartType === 'pie' ? (
                      <ResponsiveContainer width="100%" height="100%" minWidth={400} minHeight={200}>
                        <PieChart>
                          <Pie
                            data={[
                              { name: 'Protein', value: currentData.protein * 4, color: '#3182ce' },
                              { name: 'Carbs', value: currentData.carbs * 4, color: '#38a169' },
                              { name: 'Fats', value: currentData.fats * 9, color: '#d69e2e' }
                            ]}
                            cx="50%"
                            cy="50%"
                            outerRadius={120}
                            fill="#8884d8"
                            dataKey="value"
                            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                          >
                            {[
                              { name: 'Protein', value: currentData.protein * 4, color: '#3182ce' },
                              { name: 'Carbs', value: currentData.carbs * 4, color: '#38a169' },
                              { name: 'Fats', value: currentData.fats * 9, color: '#d69e2e' }
                            ].map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                          <RechartsTooltip />
                        </PieChart>
                      </ResponsiveContainer>
                    ) : !isContainerReady ? (
                      <Flex height="100%" align="center" justify="center">
                        <Spinner size="lg" color="blue.500" />
                      </Flex>
                    ) : null}

                    {isContainerReady && chartType === 'bar' ? (
                      <ResponsiveContainer width="100%" height="100%" minWidth={400} minHeight={200}>
                        <BarChart data={[
                          { macro: 'Protein', current: currentData.protein, target: targets.protein },
                          { macro: 'Carbs', current: currentData.carbs, target: targets.carbs },
                          { macro: 'Fats', current: currentData.fats, target: targets.fats }
                        ]} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="macro" />
                          <YAxis />
                          <RechartsTooltip />
                          <Bar dataKey="current" fill="#3182ce" />
                          <Bar dataKey="target" fill="#e2e8f0" opacity={0.7} />
                        </BarChart>
                      </ResponsiveContainer>
                    ) : !isContainerReady ? (
                      <Flex height="100%" align="center" justify="center">
                        <Spinner size="lg" color="blue.500" />
                      </Flex>
                    ) : null}

                    {isContainerReady && chartType === 'trend' && dailyBreakdown.length > 0 ? (
                      <ResponsiveContainer width="100%" height="100%" minWidth={400} minHeight={200}>
                        <AreaChart data={trendData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis />
                          <RechartsTooltip />
                          <Legend />
                          <Area type="monotone" dataKey="protein" stackId="1" stroke="#3182ce" fill="#3182ce" name="Protein (g)" />
                          <Area type="monotone" dataKey="carbs" stackId="1" stroke="#38a169" fill="#38a169" name="Carbs (g)" />
                          <Area type="monotone" dataKey="fats" stackId="1" stroke="#d69e2e" fill="#d69e2e" name="Fats (g)" />
                        </AreaChart>
                      </ResponsiveContainer>
                    ) : !isContainerReady ? (
                      <Flex height="100%" align="center" justify="center">
                        <Spinner size="lg" color="blue.500" />
                      </Flex>
                    ) : null}
                  </Box>
                </CardBody>
              </Card>
            </VStack>
          </TabPanel>

          {/* Meal Patterns Tab */}
          <TabPanel px={0}>
            <VStack spacing={6} align="stretch">
              {mealDistribution && (
                <Card bg={cardBg} borderColor={borderColor}>
                  <CardHeader>
                    <Heading size="md">Meal Distribution</Heading>
                  </CardHeader>
                  <CardBody>
                    <Box height="300px" minWidth="300px" width="100%">
                      {isContainerReady ? (
                        <ResponsiveContainer width="100%" height="100%" minWidth={300} minHeight={200}>
                        <PieChart>
                          <Pie
                            data={mealData}
                            cx="50%"
                            cy="50%"
                            outerRadius={100}
                            fill="#8884d8"
                            dataKey="value"
                            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                          >
                            {mealData.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={entry.color} />
                            ))}
                          </Pie>
                          <RechartsTooltip />
                        </PieChart>
                        </ResponsiveContainer>
                      ) : (
                        <Flex height="100%" align="center" justify="center">
                          <Spinner size="lg" color="blue.500" />
                        </Flex>
                      )}
                    </Box>
                  </CardBody>
                </Card>
              )}

              {/* Weekly averages */}
              {weeklyAverages && (
                <Card bg={cardBg} borderColor={borderColor}>
                  <CardHeader>
                    <Heading size="md">Weekly Averages</Heading>
                  </CardHeader>
                  <CardBody>
                    <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
                      <Stat>
                        <StatLabel>Avg Calories</StatLabel>
                        <StatNumber>{weeklyAverages.calories.toFixed(0)}</StatNumber>
                      </Stat>
                      <Stat>
                        <StatLabel>Avg Protein</StatLabel>
                        <StatNumber>{weeklyAverages.protein.toFixed(1)}g</StatNumber>
                      </Stat>
                      <Stat>
                        <StatLabel>Avg Carbs</StatLabel>
                        <StatNumber>{weeklyAverages.carbs.toFixed(1)}g</StatNumber>
                      </Stat>
                      <Stat>
                        <StatLabel>Avg Fats</StatLabel>
                        <StatNumber>{weeklyAverages.fats.toFixed(1)}g</StatNumber>
                      </Stat>
                    </SimpleGrid>
                  </CardBody>
                </Card>
              )}
            </VStack>
          </TabPanel>

          {/* Trends Tab */}
          <TabPanel px={0}>
            <VStack spacing={6} align="stretch">
              {dailyBreakdown.length > 0 ? (
                <Card bg={cardBg} borderColor={borderColor}>
                  <CardHeader>
                    <Heading size="md">Nutrition Trends</Heading>
                  </CardHeader>
                  <CardBody>
                  <Box height="400px" minWidth="400px" width="100%">
                    {isContainerReady ? (
                      <ResponsiveContainer width="100%" height="100%" minWidth={400} minHeight={200}>
                        <LineChart data={trendData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="date" />
                          <YAxis />
                          <RechartsTooltip />
                          <Legend />
                          <Line type="monotone" dataKey="calories" stroke="#3182ce" strokeWidth={2} name="Calories" />
                          <Line type="monotone" dataKey="protein" stroke="#38a169" strokeWidth={2} name="Protein (g)" />
                          <Line type="monotone" dataKey="carbs" stroke="#d69e2e" strokeWidth={2} name="Carbs (g)" />
                          <Line type="monotone" dataKey="fats" stroke="#e53e3e" strokeWidth={2} name="Fats (g)" />
                        </LineChart>
                      </ResponsiveContainer>
                    ) : (
                      <Flex height="100%" align="center" justify="center">
                        <Spinner size="lg" color="blue.500" />
                      </Flex>
                    )}
                  </Box>
                  </CardBody>
                </Card>
              ) : (
                <Alert status="info">
                  <AlertIcon />
                  <Text>No trend data available. Log meals over multiple days to see trends.</Text>
                </Alert>
              )}
            </VStack>
          </TabPanel>

          {/* Insights Tab */}
          <TabPanel px={0}>
            <VStack spacing={6} align="stretch">
              {aiInsights && (
                <>
                  {aiInsights.achievements.length > 0 && (
                    <Card bg={cardBg} borderColor={borderColor}>
                      <CardHeader>
                        <Heading size="md" color="green.500" display="flex" alignItems="center" gap={2}>
                          <Icon as={FiAward} />
                          Achievements
                        </Heading>
                      </CardHeader>
                      <CardBody>
                        <VStack spacing={2} align="stretch">
                          {aiInsights.achievements.map((achievement, index) => (
                            <HStack key={index}>
                              <Icon as={FiCheckCircle} color="green.500" />
                              <Text>{achievement}</Text>
                            </HStack>
                          ))}
                        </VStack>
                      </CardBody>
                    </Card>
                  )}

                  {aiInsights.concerns.length > 0 && (
                    <Card bg={cardBg} borderColor={borderColor}>
                      <CardHeader>
                        <Heading size="md" color="red.500" display="flex" alignItems="center" gap={2}>
                          <Icon as={FiAlertTriangle} />
                          Areas for Improvement
                        </Heading>
                      </CardHeader>
                      <CardBody>
                        <VStack spacing={2} align="stretch">
                          {aiInsights.concerns.map((concern, index) => (
                            <HStack key={index}>
                              <Icon as={FiAlertTriangle} color="red.500" />
                              <Text>{concern}</Text>
                            </HStack>
                          ))}
                        </VStack>
                      </CardBody>
                    </Card>
                  )}

                  {aiInsights.suggestions.length > 0 && (
                    <Card bg={cardBg} borderColor={borderColor}>
                      <CardHeader>
                        <Heading size="md" color="blue.500" display="flex" alignItems="center" gap={2}>
                          <Icon as={FiZap} />
                          Recommendations
                        </Heading>
                      </CardHeader>
                      <CardBody>
                        <VStack spacing={2} align="stretch">
                          {aiInsights.suggestions.map((suggestion, index) => (
                            <HStack key={index}>
                              <Icon as={FiInfo} color="blue.500" />
                              <Text>{suggestion}</Text>
                            </HStack>
                          ))}
                        </VStack>
                      </CardBody>
                    </Card>
                  )}
                </>
              )}
            </VStack>
          </TabPanel>
        </TabPanels>
      </Tabs>
    </VStack>
  );
};

export default AdvancedNutritionDashboard;
