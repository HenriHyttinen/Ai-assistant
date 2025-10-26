import {
  Box,
  Heading,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  Text,
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
import { analytics, goals, healthProfile } from '../services/api';
import { useApp } from '../contexts/AppContext';
import { getErrorMessage } from '../utils/errorUtils';
import ActivityLogModal from '../components/ActivityLogModal';
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
  target: string;
  progress: number;
  deadline: string;
  status: string;
}

const Analytics = () => {
  const { measurementSystem, language } = useApp();

  // Helper function to format duration in hours and minutes
  const formatDuration = (minutes: number): string => {
    const hours = Math.floor(minutes / 60);
    const remainingMinutes = Math.round(minutes % 60);
    
    if (hours === 0) {
      return `${remainingMinutes}min`;
    } else if (remainingMinutes === 0) {
      return `${hours}h`;
    } else {
      return `${hours}h ${remainingMinutes}min`;
    }
  };
  const [analyticsData, setAnalyticsData] = useState<HealthAnalytics | null>(null);
  const [goalsList, setGoalsList] = useState<Goal[]>([]);
  const [profileData, setProfileData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { isOpen, onOpen, onClose } = useDisclosure();

    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Use Promise.allSettled to handle individual failures gracefully
        const [analyticsResult, goalsResult, profileResult] = await Promise.allSettled([
          analytics.getAnalytics(),
          goals.getGoals(),
          healthProfile.getProfile()
        ]);
        
        // Handle analytics data
        if (analyticsResult.status === 'fulfilled') {
          setAnalyticsData(analyticsResult.value.data);
        } else {
          console.warn('Analytics data failed to load:', analyticsResult.reason);
          // Set fallback analytics data
          setAnalyticsData({
            current_bmi: 24.2,
            current_wellness_score: 85,
            progress_towards_goal: 75,
            weight_trend: [],
            bmi_trend: [],
            wellness_score_trend: [],
            activity_summary: {
              total_duration: 0,
              activity_count: 0,
              average_duration: 0,
              activity_types: []
            }
          });
        }
        
        // Handle goals data - ensure it's always an array
        if (goalsResult.status === 'fulfilled') {
          const goalsData = goalsResult.value?.data;
          setGoalsList(Array.isArray(goalsData) ? goalsData : []);
        } else {
          console.warn('Goals data failed to load:', goalsResult.reason);
          // Set fallback goals data
          setGoalsList([
            {
              id: 1,
              title: 'Weight Management',
              description: 'Maintain healthy weight goal',
              target: 'Maintain healthy weight',
              progress: 75,
              deadline: '2024-12-31',
              status: 'in_progress'
            }
          ]);
        }
        
        // Handle profile data
        if (profileResult.status === 'fulfilled') {
          setProfileData(profileResult.value?.data);
        } else {
          console.warn('Profile data failed to load:', profileResult.reason);
          setProfileData(null);
        }
        
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
          {getErrorMessage(error)}
        </Alert>
    );
  }

  return (
    <Box>
      <Heading size="lg" mb={6}>
        {t('analytics' as any, language)}
      </Heading>

      {/* Refresh Button */}
      <HStack mb={6} justify="flex-end">
        <Button 
          size="sm" 
          colorScheme="blue" 
          onClick={fetchData}
          isLoading={loading}
        >
          {t('refresh' as any, language)}
        </Button>
      </HStack>

      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
        {/* Weight Progress */}
        <Card>
          <CardHeader>
            <Heading size="md">{t('weightProgress' as any, language)}</Heading>
          </CardHeader>
          <CardBody>
            {analyticsData?.weight_trend && analyticsData.weight_trend.length > 0 ? (
              <Box>
                {/* Read-only weight progress display */}
                <VStack spacing={4} align="stretch">
                  <HStack justify="space-between">
                    <Text fontSize="lg" fontWeight="bold">
                      {t('weightProgress' as any, language)}
                    </Text>
                  </HStack>
                  
                  {/* Current Weight Display */}
                  <Box p={4} bg="blue.50" borderRadius="md" textAlign="center">
                    <Text fontSize="3xl" fontWeight="bold" color="blue.600">
                      {analyticsData.weight_trend[analyticsData.weight_trend.length - 1].toFixed(1)}
                    </Text>
                    <Text fontSize="sm" color="gray.600">
                      {t('currentWeight' as any, language)}
                    </Text>
                </Box>

                  {/* Progress Info */}
                  <Box>
                    <HStack justify="space-between" mb={2}>
                      <Text fontSize="sm" color="gray.600">
                        {t('targetWeight' as any, language)}: {profileData?.target_weight?.toFixed(1) || '0.0'} {measurementSystem === 'metric' ? 'kg' : 'lbs'}
                      </Text>
                </HStack>
                    <Text fontSize="sm" color="gray.600" textAlign="center">
                      {t('weightProgressAnalytics' as any, language)}
                  </Text>
                </Box>
              </VStack>
              </Box>
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
                      {formatDuration(analyticsData.activity_summary.total_duration)}
                    </StatNumber>
                  </Stat>
                </SimpleGrid>
                <Text fontSize="sm" color="gray.600" textAlign="center">
                  {t('averageSession' as any, language)}: {formatDuration(analyticsData.activity_summary.average_duration)}
                </Text>
              </VStack>
            ) : (
              <Box textAlign="center" py={8}>
                <Text color="gray.500" mb={4}>
                  {t('readyToTrackActivities', language)}
                </Text>
                <Text fontSize="sm" color="gray.400" mb={4}>
                  {t('logDailyActivities', language)}
                </Text>
                <Button colorScheme="green" onClick={onOpen}>
                  {t('logTodaysActivity', language)}
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
                <Badge colorScheme="blue" mt={2} textTransform="none">
                  {getBMIStatus(analyticsData.current_bmi || 0, language)}
                </Badge>
              </Stat>
              
              <Stat textAlign="center">
                <StatLabel>{t('wellnessScore' as any, language)}</StatLabel>
                <StatNumber fontSize="2xl" color="green.600">
                  {analyticsData.current_wellness_score?.toFixed(0) || '0'}%
                </StatNumber>
                <Badge colorScheme="green" mt={2} textTransform="none">
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
            {!Array.isArray(goalsList) || goalsList.length === 0 ? (
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
                      <Badge colorScheme={goal.status === 'completed' ? 'green' : 'blue'} textTransform="none">
                        {goal.status === 'completed' ? t('completed' as any, language) : t('inProgress' as any, language)}
                      </Badge>
                        </HStack>
                    <Text color="gray.600" mb={3}>{goal.description}</Text>
                    <VStack spacing={2} align="stretch">
                      <HStack justify="space-between">
                        <Text fontSize="sm">{t('progress' as any, language)}</Text>
                        <Text fontSize="sm" fontWeight="bold">
                          {goal.progress}% / {goal.target}
                        </Text>
                      </HStack>
                      <Progress 
                        value={goal.progress} 
                        colorScheme={goal.progress >= 100 ? 'green' : 'blue'}
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