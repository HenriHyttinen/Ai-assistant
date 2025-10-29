import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Heading,
  Button,
  Select,
  Card,
  CardBody,
  CardHeader,
  Spinner,
  Alert,
  AlertIcon,
  useColorModeValue,
  SimpleGrid,
  Badge,
  Divider,
  Icon,
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  useDisclosure
} from '@chakra-ui/react';
import { 
  FiTrendingUp, 
  FiTrendingDown, 
  FiMinus, 
  FiTarget, 
  FiClock, 
  FiUsers,
  FiCheck,
  FiAlertTriangle,
  FiInfo,
  FiDownload,
  FiRefreshCw
} from 'react-icons/fi';
import nutritionAnalyticsService from '../../services/nutritionAnalyticsService';
import type { AnalyticsDashboard as AnalyticsDashboardType, NutritionInsight, NutritionTrend } from '../../services/nutritionAnalyticsService';
import TrendChart from './TrendChart';
import InsightsPanel from './InsightsPanel';
import MealPatternsChart from './MealPatternsChart';
import GoalsProgressChart from './GoalsProgressChart';

const AnalyticsDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<AnalyticsDashboardType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState(30);
  const [refreshing, setRefreshing] = useState(false);
  const { isOpen, onOpen, onClose } = useDisclosure();

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.400');

  const periodOptions = [
    { value: 7, label: 'Last 7 days' },
    { value: 30, label: 'Last 30 days' },
    { value: 90, label: 'Last 90 days' },
    { value: 365, label: 'Last year' }
  ];

  useEffect(() => {
    loadDashboardData();
  }, [selectedPeriod]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await nutritionAnalyticsService.getAnalyticsDashboard(selectedPeriod);
      setDashboardData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const handleExport = async () => {
    try {
      const data = await nutritionAnalyticsService.exportAnalyticsData(selectedPeriod, 'json');
      // Create and download file
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `nutrition-analytics-${selectedPeriod}days.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export failed:', err);
    }
  };

  const getTrendIcon = (direction: string) => {
    switch (direction) {
      case 'increasing':
        return <Icon as={FiTrendingUp} color="green.500" />;
      case 'decreasing':
        return <Icon as={FiTrendingDown} color="red.500" />;
      default:
        return <Icon as={FiMinus} color="gray.500" />;
    }
  };

  const getTrendColor = (direction: string) => {
    switch (direction) {
      case 'increasing':
        return 'green';
      case 'decreasing':
        return 'red';
      default:
        return 'gray';
    }
  };

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'warning':
        return <Icon as={FiAlertTriangle} color="orange.500" />;
      case 'success':
        return <Icon as={FiCheck} color="green.500" />;
      default:
        return <Icon as={FiInfo} color="blue.500" />;
    }
  };

  const getInsightColor = (type: string) => {
    switch (type) {
      case 'warning':
        return 'orange';
      case 'success':
        return 'green';
      default:
        return 'blue';
    }
  };

  if (loading) {
    return (
      <Box p={6}>
        <VStack spacing={4}>
          <Spinner size="lg" />
          <Text>Loading analytics dashboard...</Text>
        </VStack>
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={6}>
        <Alert status="error" borderRadius="lg">
          <AlertIcon />
          <VStack align="start" spacing={2}>
            <Text fontWeight="semibold">Failed to load analytics</Text>
            <Text fontSize="sm">{error}</Text>
            <Button size="sm" colorScheme="blue" onClick={loadDashboardData}>
              Try Again
            </Button>
          </VStack>
        </Alert>
      </Box>
    );
  }

  if (!dashboardData) {
    return (
      <Box p={6}>
        <Alert status="info" borderRadius="lg">
          <AlertIcon />
          <VStack align="start" spacing={2}>
            <Text fontWeight="semibold">No data available</Text>
            <Text fontSize="sm">Start logging your meals to see analytics insights.</Text>
          </VStack>
        </Alert>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <VStack spacing={4} align="stretch" mb={6}>
        <HStack justify="space-between" align="center">
          <Heading size="lg">Nutrition Analytics</Heading>
          <HStack spacing={3}>
            <Select
              value={selectedPeriod}
              onChange={(e) => setSelectedPeriod(Number(e.target.value))}
              size="sm"
              w="200px"
            >
              {periodOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </Select>
            <Button
              size="sm"
              variant="outline"
              onClick={handleRefresh}
              isLoading={refreshing}
              leftIcon={<Icon as={FiRefreshCw} />}
            >
              Refresh
            </Button>
            <Button
              size="sm"
              colorScheme="blue"
              onClick={handleExport}
              leftIcon={<Icon as={FiDownload} />}
            >
              Export
            </Button>
          </HStack>
        </HStack>
        
        <Text color={textColor}>
          Comprehensive insights into your nutrition patterns and progress over the last {selectedPeriod} days
        </Text>
      </VStack>

      {/* Summary Stats */}
      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={4} mb={6}>
        <Card>
          <CardBody textAlign="center">
            <Stat>
              <StatLabel>Days Tracked</StatLabel>
              <StatNumber>{dashboardData.trends.total_days_logged}</StatNumber>
              <StatHelpText>out of {selectedPeriod} days</StatHelpText>
            </Stat>
          </CardBody>
        </Card>
        
        <Card>
          <CardBody textAlign="center">
            <Stat>
              <StatLabel>Avg Calories</StatLabel>
              <StatNumber>{dashboardData.trends.summary.avg_calories.toFixed(0)}</StatNumber>
              <StatHelpText>per day</StatHelpText>
            </Stat>
          </CardBody>
        </Card>
        
        <Card>
          <CardBody textAlign="center">
            <Stat>
              <StatLabel>Avg Protein</StatLabel>
              <StatNumber>{dashboardData.trends.summary.avg_protein.toFixed(1)}g</StatNumber>
              <StatHelpText>per day</StatHelpText>
            </Stat>
          </CardBody>
        </Card>
        
        <Card>
          <CardBody textAlign="center">
            <Stat>
              <StatLabel>Goals Status</StatLabel>
              <StatNumber>
                <Badge 
                  colorScheme={
                    dashboardData.goals_progress.overall_status === 'excellent' ? 'green' :
                    dashboardData.goals_progress.overall_status === 'good' ? 'blue' :
                    dashboardData.goals_progress.overall_status === 'fair' ? 'yellow' : 'red'
                  }
                  size="lg"
                >
                  {dashboardData.goals_progress.overall_status.replace('_', ' ').toUpperCase()}
                </Badge>
              </StatNumber>
            </Stat>
          </CardBody>
        </Card>
      </SimpleGrid>

      {/* Main Content Tabs */}
      <Tabs>
        <TabList>
          <Tab>Trends</Tab>
          <Tab>Insights</Tab>
          <Tab>Meal Patterns</Tab>
          <Tab>Goals Progress</Tab>
        </TabList>

        <TabPanels>
          {/* Trends Tab */}
          <TabPanel px={0}>
            <VStack spacing={6} align="stretch">
              <Heading size="md">Nutrition Trends</Heading>
              
              {Object.keys(dashboardData.trends.trends).length === 0 ? (
                <Alert status="info" borderRadius="lg">
                  <AlertIcon />
                  <Text>No trend data available. Start logging your meals to see trends.</Text>
                </Alert>
              ) : (
                <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
                  {Object.entries(dashboardData.trends.trends).map(([nutrient, trend]) => (
                    <Card key={nutrient}>
                      <CardHeader>
                        <HStack justify="space-between">
                          <Text fontSize="lg" fontWeight="semibold" textTransform="capitalize">
                            {nutrient.replace('_', ' ')}
                          </Text>
                          <HStack spacing={2}>
                            {getTrendIcon(trend.direction)}
                            <Badge colorScheme={getTrendColor(trend.direction)}>
                              {trend.direction}
                            </Badge>
                          </HStack>
                        </HStack>
                      </CardHeader>
                      <CardBody>
                        <VStack spacing={4} align="stretch">
                          <HStack justify="space-between">
                            <Text fontSize="sm" color={textColor}>Current Average</Text>
                            <Text fontWeight="semibold">{trend.current_avg.toFixed(1)}</Text>
                          </HStack>
                          
                          <HStack justify="space-between">
                            <Text fontSize="sm" color={textColor}>Previous Average</Text>
                            <Text>{trend.previous_avg.toFixed(1)}</Text>
                          </HStack>
                          
                          <HStack justify="space-between">
                            <Text fontSize="sm" color={textColor}>Change</Text>
                            <Text 
                              color={trend.change_percent > 0 ? 'green.500' : trend.change_percent < 0 ? 'red.500' : 'gray.500'}
                              fontWeight="semibold"
                            >
                              {trend.change_percent > 0 ? '+' : ''}{trend.change_percent.toFixed(1)}%
                            </Text>
                          </HStack>
                          
                          <Box>
                            <Text fontSize="sm" color={textColor} mb={2}>Trend Strength</Text>
                            <Progress 
                              value={Math.min(trend.strength * 10, 100)} 
                              colorScheme={getTrendColor(trend.direction)}
                              size="sm"
                            />
                          </Box>
                        </VStack>
                      </CardBody>
                    </Card>
                  ))}
                </SimpleGrid>
              )}
            </VStack>
          </TabPanel>

          {/* Insights Tab */}
          <TabPanel px={0}>
            <InsightsPanel insights={dashboardData.insights} />
          </TabPanel>

          {/* Meal Patterns Tab */}
          <TabPanel px={0}>
            <MealPatternsChart mealPatterns={dashboardData.meal_patterns} />
          </TabPanel>

          {/* Goals Progress Tab */}
          <TabPanel px={0}>
            <GoalsProgressChart goalsProgress={dashboardData.goals_progress} />
          </TabPanel>
        </TabPanels>
      </Tabs>
    </Box>
  );
};

export default AnalyticsDashboard;
