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
  Button,
  ButtonGroup,
  Select,
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
  AreaChart,
  Area,
  Legend,
  ReferenceLine
} from 'recharts';
import { 
  FiPieChart, 
  FiBarChart, 
  FiTrendingUp, 
  FiTarget,
  FiInfo
} from 'react-icons/fi';

interface CalorieData {
  calories: number;
}

interface CalorieTarget {
  calories: number;
}

interface DailyBreakdown {
  date: string;
  calories: number;
  calorieTarget?: number;
}

interface CalorieVisualizationProps {
  currentData: CalorieData;
  target: CalorieTarget;
  dailyBreakdown?: DailyBreakdown[];
  period?: 'daily' | 'weekly' | 'monthly';
  onPeriodChange?: (period: 'daily' | 'weekly' | 'monthly') => void;
}

const CalorieVisualization: React.FC<CalorieVisualizationProps> = ({
  currentData,
  target,
  dailyBreakdown = [],
  period = 'daily',
  onPeriodChange
}) => {
  const [chartType, setChartType] = useState<'pie' | 'bar' | 'trend'>('pie');
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

    const timer = setTimeout(checkContainerSize, 500);
    
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

  const targetCalories = target.calories || 2000;
  const currentCalories = currentData.calories || 0;
  const remaining = Math.max(0, targetCalories - currentCalories);
  const surplus = Math.max(0, currentCalories - targetCalories);
  const percentage = targetCalories > 0 ? (currentCalories / targetCalories) * 100 : 0;

  // Prepare pie chart data (consumed vs remaining)
  const pieChartData = useMemo(() => {
    const data = [];
    
    if (currentCalories > 0) {
      data.push({
        name: 'Consumed',
        value: Math.min(currentCalories, targetCalories),
        color: percentage <= 100 ? '#38a169' : '#e53e3e'
      });
    }
    
    if (remaining > 0) {
      data.push({
        name: 'Remaining',
        value: remaining,
        color: '#e2e8f0'
      });
    }
    
    if (surplus > 0) {
      data.push({
        name: 'Surplus',
        value: surplus,
        color: '#e53e3e'
      });
    }
    
    return data;
  }, [currentCalories, targetCalories, remaining, surplus, percentage]);

  // Prepare bar chart data (current vs target)
  const barChartData = [
    {
      name: 'Calories',
      current: currentCalories,
      target: targetCalories,
      percentage: percentage,
      color: percentage <= 100 ? '#38a169' : '#e53e3e'
    }
  ];

  // Prepare trend data with target/max line and user intake line
  // ROOT CAUSE FIX: Target line should always show daily target, regardless of period (weekly/monthly)
  // This allows users to compare each day's intake against the daily target, even in weekly/monthly views
  const trendData = useMemo(() => {
    if (!dailyBreakdown || dailyBreakdown.length === 0) {
      return [];
    }
    
    // ROOT CAUSE FIX: Always use daily target for the target line
    // Even in weekly/monthly views, we want to compare each day against the daily target
    const dailyTarget = targetCalories; // This is the daily target
    
    const data = dailyBreakdown.map(day => {
      const dayCalories = day.calories || 0;
      
      return {
        date: new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        calories: dayCalories, // User's actual intake (daily/weekly/monthly depending on period)
        target: dailyTarget, // Always daily target for comparison
        calorieDeficitSurplus: dayCalories - dailyTarget,
        caloriePercentage: dailyTarget > 0 ? (dayCalories / dailyTarget) * 100 : 0
      };
    });
    
    console.log('📊 CalorieVisualization trendData:', data);
    console.log('📊 dailyBreakdown length:', dailyBreakdown.length);
    console.log('📊 dailyTarget (for target line):', dailyTarget);
    console.log('📊 period:', period);
    
    return data;
  }, [dailyBreakdown, targetCalories, period]);

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
            {data.value.toFixed(0)} calories
          </Text>
          {data.name === 'Consumed' && (
            <Text fontSize="xs" color="gray.500">
              {percentage.toFixed(1)}% of target
            </Text>
          )}
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
            Current: {data.current.toFixed(0)} cal
          </Text>
          <Text fontSize="sm">
            Target: {data.target.toFixed(0)} cal
          </Text>
          <Text fontSize="sm" color={data.percentage > 100 ? 'red.500' : 'green.500'}>
            {data.percentage.toFixed(1)}% of target
          </Text>
        </Box>
      );
    }
    return null;
  };

  // Custom tooltip for trend chart
  const CustomTrendTooltip = ({ active, payload, label }: any) => {
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
          <Text fontWeight="bold" mb={2}>{label}</Text>
          {payload.map((entry: any, index: number) => (
            <Text key={index} fontSize="sm" color={entry.color}>
              {entry.name}: {typeof entry.value === 'number' ? entry.value.toFixed(0) : entry.value} cal
            </Text>
          ))}
          {data.calorieDeficitSurplus !== undefined && (
            <Text 
              fontSize="sm" 
              color={data.calorieDeficitSurplus >= 0 ? 'red.500' : 'green.500'}
              mt={1}
            >
              {data.calorieDeficitSurplus >= 0 ? '+' : ''}{data.calorieDeficitSurplus.toFixed(0)} 
              {' '}({data.calorieDeficitSurplus >= 0 ? 'surplus' : 'deficit'})
            </Text>
          )}
          {data.target && (
            <Text fontSize="xs" color="gray.500" mt={1}>
              Target: {data.target} cal ({data.caloriePercentage.toFixed(1)}%)
            </Text>
          )}
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

  if (!currentData || !target) {
    return (
      <Box p={6} textAlign="center">
        <Text color="gray.500">No calorie data available</Text>
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
              <Icon as={FiTarget} />
              Calorie Visualization
            </Heading>
            
            <HStack spacing={4}>
              {/* Chart type selector */}
              <ButtonGroup size="sm" isAttached variant="outline">
                <Button
                  leftIcon={<FiPieChart />}
                  onClick={() => {
                    setChartType('pie');
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
                    label={({ name, value }) => `${name}: ${value.toFixed(0)} cal`}
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
                  <XAxis dataKey="name" stroke="#718096" />
                  <YAxis stroke="#718096" />
                  <RechartsTooltip content={<CustomBarTooltip />} />
                  <Bar dataKey="current" fill={barChartData[0].color} radius={[4, 4, 0, 0]} />
                  <Bar dataKey="target" fill="#e2e8f0" radius={[4, 4, 0, 0]} opacity={0.3} />
                </BarChart>
              </ResponsiveContainer>
            )}

            {isContainerReady && chartType === 'trend' && trendData.length > 0 && (
              <ResponsiveContainer width="100%" height={350} minHeight={300} minWidth={300}>
                <LineChart data={trendData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="date" stroke="#718096" />
                  <YAxis stroke="#718096" label={{ value: 'Calories', angle: -90, position: 'insideLeft' }} />
                  <RechartsTooltip content={<CustomTrendTooltip />} />
                  <Legend />
                  {/* Target/Max line - always shows daily target, regardless of period */}
                  {/* ROOT CAUSE FIX: Target line is always daily target for comparison */}
                  {/* This allows users to see how each day/week/month compares to the daily target */}
                  <Line
                    type="monotone"
                    dataKey="target"
                    stroke="#9ca3af"
                    strokeWidth={2}
                    strokeDasharray="5 5"
                    dot={false}
                    name="Daily Target (Max)"
                    legendType="line"
                  />
                  {/* User's actual intake line - shows daily/weekly/monthly intake */}
                  {/* This shows the user's actual calorie consumption over time */}
                  <Line
                    type="monotone"
                    dataKey="calories"
                    stroke="#e53e3e"
                    strokeWidth={2.5}
                    dot={{ r: 5, fill: '#e53e3e' }}
                    name={`${period === 'daily' ? 'Daily' : period === 'weekly' ? 'Weekly' : 'Monthly'} Intake`}
                  />
                  {/* Reference line at daily target for easy comparison */}
                  <ReferenceLine 
                    y={targetCalories} 
                    stroke="#9ca3af" 
                    strokeDasharray="3 3" 
                    label={{ value: 'Daily Target', position: 'topRight' }} 
                  />
                </LineChart>
              </ResponsiveContainer>
            )}

            {chartType === 'pie' && pieChartData.length === 0 && (
              <Flex height="100%" align="center" justify="center">
                <VStack spacing={4}>
                  <Icon as={FiPieChart} boxSize={8} color="gray.400" />
                  <Text color="gray.500" textAlign="center">
                    No calorie data available for pie chart
                  </Text>
                </VStack>
              </Flex>
            )}

            {chartType === 'bar' && barChartData.length === 0 && (
              <Flex height="100%" align="center" justify="center">
                <VStack spacing={4}>
                  <Icon as={FiBarChart} boxSize={8} color="gray.400" />
                  <Text color="gray.500" textAlign="center">
                    No calorie data available for bar chart
                  </Text>
                </VStack>
              </Flex>
            )}

            {chartType === 'trend' && trendData.length === 0 && (
              <Flex height="100%" align="center" justify="center">
                <VStack spacing={4}>
                  <Icon as={FiInfo} boxSize={8} color="gray.400" />
                  <Text color="gray.500" textAlign="center">
                    No trend data available. Log meals over multiple days to see trends.
                  </Text>
                  <Text fontSize="sm" color="gray.400" textAlign="center">
                    Daily breakdown: {dailyBreakdown.length} days
                  </Text>
                </VStack>
              </Flex>
            )}
          </Box>
        </CardBody>
      </Card>

      {/* Summary stats */}
      <Card bg={cardBg} borderColor={borderColor}>
        <CardBody>
          <VStack spacing={4} align="stretch">
            <HStack justify="space-between">
              <Text fontWeight="semibold" color="#e53e3e">
                Current Calories
              </Text>
              <Badge colorScheme={getProgressColor(percentage)}>
                {percentage.toFixed(1)}%
              </Badge>
            </HStack>

            <Box>
              <HStack justify="space-between" mb={2}>
                <Text fontSize="sm">{currentCalories.toFixed(0)} cal</Text>
                <Text fontSize="sm" color="gray.600">
                  / {targetCalories.toFixed(0)} cal
                </Text>
              </HStack>
              <Progress
                value={Math.min(percentage, 100)}
                colorScheme={getProgressColor(percentage)}
                size="lg"
                borderRadius="md"
              />
            </Box>

            {remaining > 0 && (
              <Text fontSize="sm" color="green.500">
                {remaining.toFixed(0)} calories remaining to reach target
              </Text>
            )}

            {surplus > 0 && (
              <Text fontSize="sm" color="red.500">
                {surplus.toFixed(0)} calories over target (surplus)
              </Text>
            )}
          </VStack>
        </CardBody>
      </Card>
    </VStack>
  );
};

export default CalorieVisualization;

