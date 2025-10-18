import {
  Box,
  Heading,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  Text,
  Select,
  HStack,
  Spinner,
  Alert,
  AlertIcon,
  Button,
  Progress,
  VStack,
  Badge,
  Stat,
  StatLabel,
  StatNumber,
  useDisclosure,
} from '@chakra-ui/react';
import { useState, useEffect } from 'react';
import { analytics, goals } from '../services/api';
import { useApp } from '../contexts/AppContext';
import ActivityLogModal from '../components/ActivityLogModal';
import WeightProgressCard from '../components/WeightProgressCard';
import { t } from '../utils/translations';

// Helper functions for BMI and wellness score statuses
const getBMIStatus = (bmi: number, lang: string) => {
  if (bmi < 18.5) return t('underweight' as any, lang);
  if (bmi < 25) return t('normal' as any, lang);
  if (bmi < 30) return t('overweight' as any, lang);
  return t('obese' as any, lang);
};

const getWellnessStatus = (score: number, lang: string) => {
  if (score >= 80) return t('excellent' as any, lang);
  if (score >= 60) return t('good' as any, lang);
  return t('needsImprovement' as any, lang);
};

interface HealthAnalytics {
  current_bmi: number;
  current_wellness_score: number;
  weight_trend: number[];
  bmi_trend: number[];
  wellness_score_trend: number[];
  activity_summary: {
    total_duration: number;
    activity_count: number;
    average_duration: number;
    activity_types: string[];
  };
  progress_towards_goal: number;
}

interface Goal {
  id: number;
  title: string;
  description: string;
  target: number;
  current_progress: number;
  deadline: string;
  status: string;
}

const Analytics = () => {
  const { measurementSystem, language } = useApp();
  const [analyticsData, setAnalyticsData] = useState<HealthAnalytics | null>(null);
  const [goalsList, setGoalsList] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState('30');
  const { isOpen, onOpen, onClose } = useDisclosure();

    const fetchData = async () => {
      try {
        setLoading(true);
      const [analyticsResponse, goalsResponse] = await Promise.all([
        analytics.getAnalytics(),
        goals.getGoals()
      ]);
        
        setAnalyticsData(analyticsResponse.data);
        setGoalsList(goalsResponse.data);
    } catch (err) {
      setError('Failed to load analytics data');
      console.error('Analytics error:', err);
      } finally {
        setLoading(false);
      }
    };

  useEffect(() => {
    fetchData();
  }, []);


  if (loading) {
    return (
      <Box textAlign="center" py={8}>
        <Spinner size="xl" />
        <Text mt={4}>{t('loading' as any, language)}</Text>
      </Box>
    );
  }

  if (error) {
    return (
        <Alert status="error">
          <AlertIcon />
          {error}
        </Alert>
    );
  }

  return (
    <Box>
      <Heading size="lg" mb={6}>
        {t('analytics' as any, language)}
      </Heading>

      {/* Time Range Selector */}
      <HStack mb={6}>
        <Text>{t('timeRange' as any, language)}:</Text>
        <Select 
          value={timeRange}
          onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setTimeRange(e.target.value)}
          maxW="200px"
        >
          <option value="7">{t('last7Days' as any, language)}</option>
          <option value="30">{t('last30Days' as any, language)}</option>
          <option value="90">{t('last90Days' as any, language)}</option>
          <option value="365">{t('lastYear' as any, language)}</option>
        </Select>
      </HStack>

      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
        {/* Weight Progress */}
        <Card>
          <CardHeader>
            <Heading size="md">{t('weightProgress' as any, language)}</Heading>
          </CardHeader>
          <CardBody>
            {analyticsData?.weight_trend && analyticsData.weight_trend.length > 0 ? (
              <WeightProgressCard
                currentWeight={analyticsData.weight_trend[analyticsData.weight_trend.length - 1]}
                targetWeight={Number(goalsList.find(g => g.title.toLowerCase().includes('weight'))?.target) || 0}
                weightTrend={analyticsData.weight_trend}
                measurementSystem={measurementSystem}
              />
            ) : (
              <Box textAlign="center" py={8}>
                <Text color="gray.500" mb={4}>
                  {t('startYourWeightJourney' as any, language)}
                </Text>
                <Text fontSize="sm" color="gray.400" mb={4}>
                  {t('addEntries' as any, language)}
                </Text>
                <Button colorScheme="blue" onClick={onOpen}>
                  {t('logTodaysActivity' as any, language)}
                </Button>
              </Box>
            )}
          </CardBody>
        </Card>

        {/* Activity Summary */}
        <Card>
          <CardHeader>
            <Heading size="md">{t('weeklyActivity' as any, language)}</Heading>
          </CardHeader>
          <CardBody>
            {analyticsData?.activity_summary && analyticsData.activity_summary.activity_count > 0 ? (
              <VStack spacing={4} align="stretch">
                <SimpleGrid columns={2} spacing={4}>
                  <Stat textAlign="center">
                    <StatLabel>{t('totalActivities' as any, language)}</StatLabel>
                    <StatNumber fontSize="2xl" color="blue.600">
                      {analyticsData.activity_summary.activity_count}
                    </StatNumber>
                  </Stat>
                  <Stat textAlign="center">
                    <StatLabel>{t('totalDuration' as any, language)}</StatLabel>
                    <StatNumber fontSize="2xl" color="green.600">
                      {Math.round(analyticsData.activity_summary.total_duration / 60)}h
                    </StatNumber>
                  </Stat>
                </SimpleGrid>
                <Text fontSize="sm" color="gray.600" textAlign="center">
                  {t('averageSession' as any, language)}: {Math.round(analyticsData.activity_summary.average_duration)} {t('minutes' as any, language)}
                </Text>
              </VStack>
            ) : (
              <Box textAlign="center" py={8}>
                <Text color="gray.500" mb={4}>
                  {t('readyToTrackActivities' as any, language)}
                </Text>
                <Text fontSize="sm" color="gray.400" mb={4}>
                  {t('logDailyActivities' as any, language)}
                </Text>
                <Button colorScheme="green" onClick={onOpen}>
                  {t('logTodaysActivity' as any, language)}
                  </Button>
              </Box>
            )}
          </CardBody>
        </Card>
      </SimpleGrid>

      {/* Key Metrics */}
      {analyticsData && (
        <Card mt={6}>
          <CardHeader>
            <Heading size="md">{t('keyMetrics' as any, language)}</Heading>
          </CardHeader>
          <CardBody>
            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={6}>
              <Stat textAlign="center">
                <StatLabel>{t('currentBMI' as any, language)}</StatLabel>
                <StatNumber fontSize="2xl" color="blue.600">
                  {analyticsData.current_bmi?.toFixed(1) || '0.0'}
                </StatNumber>
                <Badge colorScheme="blue" mt={2}>
                  {getBMIStatus(analyticsData.current_bmi || 0, language)}
                </Badge>
              </Stat>
              
              <Stat textAlign="center">
                <StatLabel>{t('wellnessScore' as any, language)}</StatLabel>
                <StatNumber fontSize="2xl" color="green.600">
                  {analyticsData.current_wellness_score?.toFixed(0) || '0'}%
                </StatNumber>
                <Badge colorScheme="green" mt={2}>
                  {getWellnessStatus(analyticsData.current_wellness_score || 0, language)}
                </Badge>
              </Stat>
              
              <Stat textAlign="center">
                <StatLabel>{t('weeklyActivity' as any, language)}</StatLabel>
                <StatNumber fontSize="2xl" color="purple.600">
                  {analyticsData.activity_summary?.activity_count || 0}
                </StatNumber>
                <Text fontSize="sm" color="gray.500" mt={1}>
                  {t('activities' as any, language)} {t('thisWeek' as any, language)}
                </Text>
              </Stat>
            </SimpleGrid>
          </CardBody>
        </Card>
      )}

      {/* Goal Progress */}
      <Card mt={6}>
        <CardHeader>
          <Heading size="md">{t('goalProgress' as any, language)}</Heading>
          </CardHeader>
          <CardBody>
            {goalsList.length === 0 ? (
              <Box textAlign="center" py={8}>
              <Text color="gray.500" mb={4}>{t('noGoalsSetYet' as any, language)}</Text>
              <Button colorScheme="blue" as="a" href="/goals">{t('createYourFirstGoal' as any, language)}</Button>
              </Box>
            ) : (
              <VStack spacing={6} align="stretch">
                {/* Goal Statistics */}
              <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
                <Stat textAlign="center">
                  <StatLabel>{t('totalGoals' as any, language)}</StatLabel>
                  <StatNumber fontSize="2xl">{goalsList.length}</StatNumber>
                  </Stat>
                <Stat textAlign="center">
                  <StatLabel>{t('completed' as any, language)}</StatLabel>
                  <StatNumber fontSize="2xl" color="green.600">
                    {goalsList.filter(g => g.status === 'completed').length}
                  </StatNumber>
                  </Stat>
                <Stat textAlign="center">
                  <StatLabel>{t('inProgress' as any, language)}</StatLabel>
                  <StatNumber fontSize="2xl" color="blue.600">
                    {goalsList.filter(g => g.status === 'in_progress').length}
                  </StatNumber>
                  </Stat>
                </SimpleGrid>

              {/* Individual Goals */}
              <VStack spacing={4} align="stretch">
                {goalsList.map((goal) => (
                  <Box key={goal.id} p={4} border="1px" borderColor="gray.200" borderRadius="md">
                        <HStack justify="space-between" mb={2}>
                      <Text fontWeight="bold">{goal.title}</Text>
                      <Badge colorScheme={goal.status === 'completed' ? 'green' : 'blue'}>
                        {goal.status === 'completed' ? t('completed' as any, language) : t('inProgress' as any, language)}
                          </Badge>
                        </HStack>
                    <Text color="gray.600" mb={3}>{goal.description}</Text>
                    <VStack spacing={2} align="stretch">
                      <HStack justify="space-between">
                        <Text fontSize="sm">{t('progress' as any, language)}</Text>
                        <Text fontSize="sm" fontWeight="bold">
                          {goal.current_progress}% / {goal.target}
                        </Text>
                      </HStack>
                      <Progress 
                        value={(goal.current_progress / goal.target) * 100} 
                        colorScheme={goal.current_progress >= goal.target ? 'green' : 'blue'}
                        size="lg"
                        borderRadius="md"
                      />
                    </VStack>
                      </Box>
                    ))}
              </VStack>
              </VStack>
            )}
          </CardBody>
        </Card>

      {/* Activity Log Modal */}
      <ActivityLogModal
        isOpen={isOpen}
        onClose={onClose}
        onActivityLogged={() => {
          // Refresh data when activity is logged
          window.location.reload();
        }}
      />
    </Box>
  );
};

export default Analytics; 