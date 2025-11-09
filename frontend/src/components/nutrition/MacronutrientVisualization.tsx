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
  Icon
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
  Legend
} from 'recharts';
import { 
  FiPieChart, 
  FiBarChart, 
  FiTrendingUp, 
  FiTarget,
  FiActivity,
  FiZap,
  FiInfo
} from 'react-icons/fi';

interface MacronutrientData {
  calories: number;
  protein: number;
  carbs: number;
  fats: number;
  fiber?: number;
  sugar?: number;
  sodium?: number;
}

interface MacronutrientTargets {
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
  }>;
}

interface MacronutrientVisualizationProps {
  currentData: MacronutrientData;
  targets: MacronutrientTargets;
  dailyBreakdown?: DailyBreakdown[];
  period?: 'daily' | 'weekly' | 'monthly';
  onPeriodChange?: (period: 'daily' | 'weekly' | 'monthly') => void;
}

const MacronutrientVisualization: React.FC<MacronutrientVisualizationProps> = ({
  currentData,
  targets,
  dailyBreakdown = [],
  period = 'daily',
  onPeriodChange
}) => {
  const [chartType, setChartType] = useState<'pie' | 'bar' | 'trend'>('pie');
  const [selectedMacro, setSelectedMacro] = useState<'all' | 'protein' | 'carbs' | 'fats'>('all');
  const [isContainerReady, setIsContainerReady] = useState(false);
  const containerRef = React.useRef<HTMLDivElement>(null);
  const chartCardRef = React.useRef<HTMLDivElement>(null);
  
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

  // Calculate target percentages
  const targetPercentages = useMemo(() => {
    const proteinCalories = targets.protein * 4;
    const carbsCalories = targets.carbs * 4;
    const fatsCalories = targets.fats * 9;
    const totalCalories = proteinCalories + carbsCalories + fatsCalories;

    if (totalCalories === 0) {
      return { protein: 0, carbs: 0, fats: 0 };
    }

    return {
      protein: (proteinCalories / totalCalories) * 100,
      carbs: (carbsCalories / totalCalories) * 100,
      fats: (fatsCalories / totalCalories) * 100
    };
  }, [targets]);

  // Prepare pie chart data
  const pieChartData = [
    {
      name: 'Protein',
      value: currentData.protein * 4,
      grams: currentData.protein,
      percentage: macroPercentages.protein,
      color: '#3182ce',
      targetPercentage: targetPercentages.protein
    },
    {
      name: 'Carbs',
      value: currentData.carbs * 4,
      grams: currentData.carbs,
      percentage: macroPercentages.carbs,
      color: '#38a169',
      targetPercentage: targetPercentages.carbs
    },
    {
      name: 'Fats',
      value: currentData.fats * 9,
      grams: currentData.fats,
      percentage: macroPercentages.fats,
      color: '#d69e2e',
      targetPercentage: targetPercentages.fats
    }
  ];

  // Prepare bar chart data
  const barChartData = [
    {
      macro: 'Protein',
      current: currentData.protein,
      target: targets.protein,
      percentage: (currentData.protein / targets.protein) * 100,
      color: '#3182ce'
    },
    {
      macro: 'Carbs',
      current: currentData.carbs,
      target: targets.carbs,
      percentage: (currentData.carbs / targets.carbs) * 100,
      color: '#38a169'
    },
    {
      macro: 'Fats',
      current: currentData.fats,
      target: targets.fats,
      percentage: (currentData.fats / targets.fats) * 100,
      color: '#d69e2e'
    }
  ];

  // Prepare trend data
  const trendData = dailyBreakdown.map(day => ({
    date: new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    protein: day.protein,
    carbs: day.carbs,
    fats: day.fats,
    calories: day.calories
  }));

  // Custom tooltip for pie chart
  const CustomPieTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <Box
          bg="white"
          p={3}
          borderRadius="md"
          boxShadow="lg"
          border="1px solid"
          borderColor="gray.200"
        >
          <Text fontWeight="bold" color={data.color}>
            {data.name}
          </Text>
          <Text fontSize="sm">
            {data.grams.toFixed(1)}g ({data.percentage.toFixed(1)}%)
          </Text>
          <Text fontSize="sm" color="gray.600">
            {data.value.toFixed(0)} calories
          </Text>
          <Text fontSize="xs" color="gray.500">
            Target: {data.targetPercentage.toFixed(1)}%
          </Text>
        </Box>
      );
    }
    return null;
  };

  // Custom tooltip for bar chart
  const CustomBarTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <Box
          bg="white"
          p={3}
          borderRadius="md"
          boxShadow="lg"
          border="1px solid"
          borderColor="gray.200"
        >
          <Text fontWeight="bold">{label}</Text>
          <Text fontSize="sm">
            Current: {data.current.toFixed(1)}g
          </Text>
          <Text fontSize="sm">
            Target: {data.target.toFixed(1)}g
          </Text>
          <Text fontSize="sm" color={data.percentage > 100 ? 'red.500' : 'green.500'}>
            {data.percentage.toFixed(1)}% of target
          </Text>
        </Box>
      );
    }
    return null;
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 90 && percentage <= 110) return 'green';
    if (percentage >= 80 && percentage <= 120) return 'yellow';
    return 'red';
  };

  // Don't render if we don't have proper data
  if (!currentData || !targets) {
    return (
      <Box p={6} textAlign="center">
        <Text color="gray.500">No nutritional data available</Text>
      </Box>
    );
  }

  return (
    <VStack spacing={6} align="stretch" ref={containerRef}>
      {/* Header with controls */}
      <Card bg={cardBg} borderColor={borderColor}>
        <CardHeader>
          <Flex justify="space-between" align="center" wrap="wrap" gap={4}>
            <Heading size="md" display="flex" alignItems="center" gap={2}>
              <Icon as={FiPieChart} />
              Macronutrient Breakdown
            </Heading>
            
            <HStack spacing={4}>
              {/* Chart type selector */}
              <ButtonGroup size="sm" isAttached variant="outline">
                <Button
                  leftIcon={<FiPieChart />}
                  onClick={() => {
                    setChartType('pie');
                    // CRITICAL FIX: Scroll to graph when chart type changes
                    setTimeout(() => {
                      chartCardRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }, 100);
                  }}
                  colorScheme={chartType === 'pie' ? 'blue' : undefined}
                >
                  Pie
                </Button>
                <Button
                  leftIcon={<FiBarChart />}
                  onClick={() => {
                    setChartType('bar');
                    // CRITICAL FIX: Scroll to graph when chart type changes
                    setTimeout(() => {
                      chartCardRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }, 100);
                  }}
                  colorScheme={chartType === 'bar' ? 'blue' : undefined}
                >
                  Bar
                </Button>
                <Button
                  leftIcon={<FiTrendingUp />}
                  onClick={() => {
                    setChartType('trend');
                    // CRITICAL FIX: Scroll to graph when chart type changes
                    setTimeout(() => {
                      chartCardRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }, 100);
                  }}
                  colorScheme={chartType === 'trend' ? 'blue' : undefined}
                  isDisabled={dailyBreakdown.length === 0}
                >
                  Trend
                </Button>
              </ButtonGroup>

              {/* Period selector */}
              {onPeriodChange && (
                <Select
                  size="sm"
                  value={period}
                  onChange={(e) => {
                    onPeriodChange(e.target.value as any);
                    // CRITICAL FIX: Scroll to graph when period changes
                    setTimeout(() => {
                      chartCardRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
                    }, 100);
                  }}
                  width="120px"
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </Select>
              )}
            </HStack>
          </Flex>
        </CardHeader>
      </Card>

      {/* Main visualization */}
      <Card bg={cardBg} borderColor={borderColor} ref={chartCardRef}>
        <CardBody>
          <Box height="400px" minHeight="300px" minWidth="300px" width="100%">
            {isContainerReady && chartType === 'pie' && pieChartData.length > 0 && (
              <ResponsiveContainer width="100%" height={350} minHeight={300} minWidth={300}>
                <PieChart>
                  <Pie
                    data={pieChartData}
                    cx="50%"
                    cy="50%"
                    outerRadius={120}
                    fill="#8884d8"
                    dataKey="value"
                    label={({ name, percentage }) => `${name}: ${percentage.toFixed(1)}%`}
                  >
                    {pieChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <RechartsTooltip content={<CustomPieTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            )}

            {isContainerReady && chartType === 'bar' && barChartData.length > 0 && (
              <ResponsiveContainer width="100%" height={350} minHeight={300} minWidth={300}>
                <BarChart data={barChartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="macro" stroke="#718096" />
                  <YAxis stroke="#718096" />
                  <RechartsTooltip content={<CustomBarTooltip />} />
                  <Bar dataKey="current" fill="#3182ce" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="target" fill="#e2e8f0" radius={[4, 4, 0, 0]} opacity={0.3} />
                </BarChart>
              </ResponsiveContainer>
            )}

            {isContainerReady && chartType === 'trend' && dailyBreakdown.length > 0 && (
              <ResponsiveContainer width="100%" height={350} minHeight={300} minWidth={300}>
                <AreaChart data={trendData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="date" stroke="#718096" />
                  <YAxis yAxisId="left" stroke="#718096" />
                  <YAxis yAxisId="right" orientation="right" stroke="#e53e3e" />
                  <RechartsTooltip />
                  <Legend />
                  <Line
                    yAxisId="right"
                    type="monotone"
                    dataKey="calories"
                    stroke="#e53e3e"
                    strokeWidth={2}
                    dot={{ r: 4 }}
                    name="Calories"
                  />
                  <Area
                    type="monotone"
                    dataKey="protein"
                    stackId="1"
                    stroke="#3182ce"
                    fill="#3182ce"
                    fillOpacity={0.6}
                    name="Protein (g)"
                  />
                  <Area
                    type="monotone"
                    dataKey="carbs"
                    stackId="1"
                    stroke="#38a169"
                    fill="#38a169"
                    fillOpacity={0.6}
                    name="Carbs (g)"
                  />
                  <Area
                    type="monotone"
                    dataKey="fats"
                    stackId="1"
                    stroke="#d69e2e"
                    fill="#d69e2e"
                    fillOpacity={0.6}
                    name="Fats (g)"
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}

            {chartType === 'pie' && pieChartData.length === 0 && (
              <Flex height="100%" align="center" justify="center">
                <VStack spacing={4}>
                  <Icon as={FiPieChart} boxSize={8} color="gray.400" />
                  <Text color="gray.500" textAlign="center">
                    No macronutrient data available for pie chart
                  </Text>
                </VStack>
              </Flex>
            )}

            {chartType === 'bar' && barChartData.length === 0 && (
              <Flex height="100%" align="center" justify="center">
                <VStack spacing={4}>
                  <Icon as={FiBarChart} boxSize={8} color="gray.400" />
                  <Text color="gray.500" textAlign="center">
                    No macronutrient data available for bar chart
                  </Text>
                </VStack>
              </Flex>
            )}

            {chartType === 'trend' && dailyBreakdown.length === 0 && (
              <Flex height="100%" align="center" justify="center">
                <VStack spacing={4}>
                  <Icon as={FiInfo} boxSize={8} color="gray.400" />
                  <Text color="gray.500" textAlign="center">
                    No trend data available. Log meals over multiple days to see trends.
                  </Text>
                </VStack>
              </Flex>
            )}
          </Box>
        </CardBody>
      </Card>

      {/* Detailed breakdown */}
      <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
        {pieChartData.map((macro) => (
          <Card key={macro.name} bg={cardBg} borderColor={borderColor}>
            <CardBody>
              <VStack spacing={3} align="stretch">
                <HStack justify="space-between">
                  <Text fontWeight="semibold" color={macro.color}>
                    {macro.name}
                  </Text>
                  <Badge colorScheme={getProgressColor((macro.grams / targets[macro.name.toLowerCase() as keyof MacronutrientTargets]) * 100)}>
                    {((macro.grams / targets[macro.name.toLowerCase() as keyof MacronutrientTargets]) * 100).toFixed(0)}%
                  </Badge>
                </HStack>

                <Stat>
                  <StatLabel>Current</StatLabel>
                  <StatNumber fontSize="lg">{macro.grams.toFixed(1)}g</StatNumber>
                  <StatHelpText>
                    {macro.percentage.toFixed(1)}% of calories
                  </StatHelpText>
                </Stat>

                <Divider />

                <Stat>
                  <StatLabel>Target</StatLabel>
                  <StatNumber fontSize="sm" color="gray.600">
                    {targets[macro.name.toLowerCase() as keyof MacronutrientTargets]}g
                  </StatNumber>
                  <StatHelpText>
                    {macro.targetPercentage.toFixed(1)}% of calories
                  </StatHelpText>
                </Stat>

                <Progress
                  value={(macro.grams / targets[macro.name.toLowerCase() as keyof MacronutrientTargets]) * 100}
                  colorScheme={getProgressColor((macro.grams / targets[macro.name.toLowerCase() as keyof MacronutrientTargets]) * 100)}
                  size="sm"
                />
              </VStack>
            </CardBody>
          </Card>
        ))}
      </SimpleGrid>

      {/* Summary insights */}
      <Card bg={cardBg} borderColor={borderColor}>
        <CardHeader>
          <Heading size="sm" display="flex" alignItems="center" gap={2}>
            <Icon as={FiTarget} />
            Macro Balance Analysis
          </Heading>
        </CardHeader>
        <CardBody>
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
            <VStack align="stretch" spacing={3}>
              <Text fontWeight="semibold" color="blue.500">Current Distribution</Text>
              {pieChartData.map((macro) => (
                <HStack key={macro.name} justify="space-between">
                  <Text fontSize="sm">{macro.name}</Text>
                  <Text fontSize="sm" fontWeight="semibold" color={macro.color}>
                    {macro.percentage.toFixed(1)}%
                  </Text>
                </HStack>
              ))}
            </VStack>

            <VStack align="stretch" spacing={3}>
              <Text fontWeight="semibold" color="green.500">Target Distribution</Text>
              {pieChartData.map((macro) => (
                <HStack key={macro.name} justify="space-between">
                  <Text fontSize="sm">{macro.name}</Text>
                  <Text fontSize="sm" fontWeight="semibold" color="green.500">
                    {macro.targetPercentage.toFixed(1)}%
                  </Text>
                </HStack>
              ))}
            </VStack>
          </SimpleGrid>
        </CardBody>
      </Card>
    </VStack>
  );
};

export default MacronutrientVisualization;

