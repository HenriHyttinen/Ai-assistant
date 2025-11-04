import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Heading,
  Button,
  Card,
  CardBody,
  CardHeader,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Badge,
  Icon,
  useColorModeValue,
  Spinner,
  Alert,
  AlertIcon,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Progress,
  Divider,
  useDisclosure
} from '@chakra-ui/react';
import { 
  FiTarget, 
  FiTrendingUp, 
  FiCheck, 
  FiClock, 
  FiPlus,
  FiBarChart,
  FiCalendar,
  FiRefreshCw
} from 'react-icons/fi';
import nutritionGoalsService from '../../services/nutritionGoalsService';
import type { 
  GoalDashboard, 
  NutritionGoal, 
  GoalTemplate,
  GoalProgressSummary 
} from '../../services/nutritionGoalsService';
import CreateGoalModal from './CreateGoalModal';
import GoalCard from './GoalCard';
import GoalProgressChart from './GoalProgressChart';
import GoalInsights from './GoalInsights';

const GoalsDashboard: React.FC = () => {
  const [dashboardData, setDashboardData] = useState<GoalDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const { isOpen, onOpen, onClose } = useDisclosure();

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.400');

  const loadDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await nutritionGoalsService.getGoalDashboard();
      setDashboardData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load goals dashboard');
    } finally {
      setLoading(false);
    }
  }, []);
  
  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);
  
  // Listen for daily log updates to refresh goals
  useEffect(() => {
    const handleDailyLogUpdate = () => {
      // Refresh dashboard when daily log is updated
      loadDashboardData();
    };
    
    window.addEventListener('dailyLogUpdated', handleDailyLogUpdate);
    return () => {
      window.removeEventListener('dailyLogUpdated', handleDailyLogUpdate);
    };
  }, [loadDashboardData]);

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  const handleGoalCreated = () => {
    onClose();
    loadDashboardData();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'green';
      case 'paused':
        return 'yellow';
      case 'completed':
        return 'blue';
      case 'cancelled':
        return 'red';
      default:
        return 'gray';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <Icon as={FiTarget} color="green.500" />;
      case 'paused':
        return <Icon as={FiClock} color="yellow.500" />;
      case 'completed':
        return <Icon as={FiCheck} color="blue.500" />;
      case 'cancelled':
        return <Icon as={FiTarget} color="red.500" />;
      default:
        return <Icon as={FiTarget} color="gray.500" />;
    }
  };

  if (loading) {
    return (
      <Box p={6}>
        <VStack spacing={4}>
          <Spinner size="lg" />
          <Text>Loading goals dashboard...</Text>
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
            <Text fontWeight="semibold">Failed to load goals</Text>
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
            <Text fontWeight="semibold">No goals found</Text>
            <Text fontSize="sm">Create your first nutrition goal to get started!</Text>
            <Button size="sm" colorScheme="blue" onClick={onOpen}>
              Create Goal
            </Button>
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
          <Heading size="lg">Nutrition Goals</Heading>
          <HStack spacing={3}>
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
              onClick={onOpen}
              leftIcon={<Icon as={FiPlus} />}
            >
              Create Goal
            </Button>
          </HStack>
        </HStack>
        
        <Text color={textColor}>
          Track your nutrition goals and monitor your progress toward better health
        </Text>
      </VStack>

      {/* Summary Stats */}
      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={4} mb={6}>
        <Card>
          <CardBody textAlign="center">
            <Stat>
              <StatLabel>Total Goals</StatLabel>
              <StatNumber>{dashboardData.summary.total_goals}</StatNumber>
              <StatHelpText>
                {dashboardData.summary.active_goals} active
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>
        
        <Card>
          <CardBody textAlign="center">
            <Stat>
              <StatLabel>Completed</StatLabel>
                <StatNumber>{dashboardData.summary.completed_goals}</StatNumber>
              <StatHelpText>
                {dashboardData.summary.total_goals > 0 
                  ? Math.round((dashboardData.summary.completed_goals / dashboardData.summary.total_goals) * 100)
                  : 0}% completion rate
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>
        
        <Card>
          <CardBody textAlign="center">
            <Stat>
              <StatLabel>Best Streak</StatLabel>
              <StatNumber>{dashboardData.summary.best_streak}</StatNumber>
              <StatHelpText>days</StatHelpText>
            </Stat>
          </CardBody>
        </Card>
        
        <Card>
          <CardBody textAlign="center">
            <Stat>
              <StatLabel>Goals On Track</StatLabel>
              <StatNumber>{dashboardData.summary.goals_on_track}</StatNumber>
              <StatHelpText>
                out of {dashboardData.summary.active_goals} active
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>
      </SimpleGrid>

      {/* Main Content Tabs */}
      <Tabs>
        <TabList>
          <Tab>Active Goals</Tab>
          <Tab>Progress Charts</Tab>
          <Tab>Insights</Tab>
        </TabList>

        <TabPanels>
          {/* Active Goals Tab */}
          <TabPanel px={0}>
            <VStack spacing={6} align="stretch">
              <Heading size="md">Your Active Goals</Heading>
              
              {dashboardData.active_goals.length === 0 ? (
                <Alert status="info" borderRadius="lg">
                  <AlertIcon />
                  <VStack align="start" spacing={2}>
                    <Text fontWeight="semibold">No active goals</Text>
                    <Text fontSize="sm">Create a new goal to start tracking your nutrition progress.</Text>
                    <Button size="sm" colorScheme="blue" onClick={onOpen}>
                      Create Your First Goal
                    </Button>
                  </VStack>
                </Alert>
              ) : (
                <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
                  {dashboardData.active_goals.map((goal) => (
                    <GoalCard key={goal.goal_id} goal={goal} onUpdate={loadDashboardData} />
                  ))}
                </SimpleGrid>
              )}
            </VStack>
          </TabPanel>

          {/* Progress Charts Tab */}
          <TabPanel px={0}>
            <GoalProgressChart goals={dashboardData.active_goals} />
          </TabPanel>

          {/* Insights Tab */}
          <TabPanel px={0}>
            <GoalInsights dashboardData={dashboardData} />
          </TabPanel>

          {/* Recent Achievements removed per requirements */}
        </TabPanels>
      </Tabs>

      {/* Create Goal Modal */}
      <CreateGoalModal 
        isOpen={isOpen} 
        onClose={onClose} 
        onGoalCreated={handleGoalCreated} 
      />
    </Box>
  );
};

export default GoalsDashboard;


