import {
  Box,
  Grid,
  GridItem,
  Heading,
  Text,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  Stack,
  VStack,
  Spinner,
  Alert,
  AlertIcon,
  Button,
  useDisclosure,
} from '@chakra-ui/react';
import { useState, useEffect, useCallback } from 'react';
import { analytics, healthProfile } from '../services/api';
import { useApp } from '../contexts/AppContext';
import ActivityLogModal from '../components/ActivityLogModal';
import WeightProgressCard from '../components/WeightProgressCard';
import { t } from '../utils/translations';

interface HealthAnalytics {
  current_bmi: number;
  current_wellness_score: number;
  weight_trend: number[];
  activity_summary: {
    activity_count: number;
    total_duration: number;
    average_duration: number;
    activity_types: string[];
  };
  progress_towards_goal: number;
}

interface HealthProfile {
  weight: number;
  height: number;
  target_weight?: number;
  updated_at: string;
}

interface AIInsights {
  insights: string[];
  metrics: {
    bmi: number;
    bmi_category: string;
    wellness_score: number;
  };
}

const Dashboard = () => {
  const { measurementSystem, language } = useApp();
  const { isOpen: isActivityModalOpen, onOpen: onActivityModalOpen, onClose: onActivityModalClose } = useDisclosure();
  
  const [analyticsData, setAnalyticsData] = useState<HealthAnalytics | null>(null);
  const [profileData, setProfileData] = useState<HealthProfile | null>(null);
  const [aiInsights, setAiInsights] = useState<AIInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch analytics data
      const analyticsResponse = await analytics.getAnalytics();
      setAnalyticsData(analyticsResponse);

      // Fetch health profile
      const profileResponse = await healthProfile.getProfile();
      setProfileData(profileResponse);

      // Fetch AI insights
      try {
        const insightsResponse = await healthProfile.getInsights();
        if (insightsResponse && insightsResponse.data && insightsResponse.data.insights) {
          setAiInsights(insightsResponse.data);
        }
      } catch (insightsError) {
        console.error('Failed to refresh insights:', insightsError);
        // Set fallback insights for development
        setAiInsights({
          insights: [
            "Welcome to your health journey! Start by logging your weight and activities.",
            "Set up your health profile to get personalized insights.",
            "Track your daily activities to see your progress over time.",
            "✅ You're taking the first step towards better health!",
            "💡 Consider setting specific, achievable health goals"
          ],
          metrics: {
            bmi: 0,
            bmi_category: "Unknown",
            wellness_score: 0
          }
        });
      }
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Listen for profile updates from other pages
  useEffect(() => {
    const handleStorageChange = () => {
      if (localStorage.getItem('profile_updated') === 'true') {
        window.location.reload();
        localStorage.removeItem('profile_updated');
      }
    };

    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  // Get BMI category
  const getBMICategory = (bmi: number, lang: string) => {
    if (bmi < 18.5) return t('underweight', lang);
    if (bmi < 25) return t('normal', lang);
    if (bmi < 30) return t('overweight', lang);
    return t('obese', lang);
  };


  if (loading) {
    return (
      <Box p={4} display="flex" justifyContent="center" alignItems="center" minH="400px">
        <VStack spacing={4}>
          <Spinner size="xl" color="blue.500" />
          <Text color="gray.600">{t('loading', language)}</Text>
        </VStack>
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={4}>
        <Alert status="error">
          <AlertIcon />
          {error}
        </Alert>
      </Box>
    );
  }

  if (!analyticsData || !profileData) {
    return (
      <Box p={4}>
        <VStack spacing={4}>
          <Spinner size="lg" color="blue.500" />
          <Text color="gray.500">Loading dashboard data...</Text>
        </VStack>
      </Box>
    );
  }

  const bmiCategory = getBMICategory(analyticsData?.current_bmi || 0, language);

  return (
    <Box p={4}>
      <Heading mb={6}>{t('dashboard', language)}</Heading>

      {/* Key Metrics */}
      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={6} mb={8}>
        <Card>
          <CardBody>
            <Stat>
              <StatLabel>{t('bmi', language)}</StatLabel>
              <StatNumber color={analyticsData?.current_bmi < 25 ? 'green.500' : analyticsData?.current_bmi < 30 ? 'orange.500' : 'red.500'}>
                {analyticsData?.current_bmi?.toFixed(1) || '0.0'}
              </StatNumber>
              <StatHelpText>
                <StatArrow type={analyticsData?.current_bmi < 25 ? 'increase' : 'decrease'} />
                {bmiCategory}
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <Stat>
              <StatLabel>{t('wellnessScore', language)}</StatLabel>
              <StatNumber color={analyticsData?.current_wellness_score >= 80 ? 'green.500' : analyticsData?.current_wellness_score >= 60 ? 'orange.500' : 'red.500'}>
                {analyticsData?.current_wellness_score?.toFixed(0) || '0'}/100
              </StatNumber>
              <StatHelpText>
                <StatArrow type={analyticsData?.current_wellness_score >= 70 ? 'increase' : 'decrease'} />
                {analyticsData?.current_wellness_score >= 80 ? t('excellent' as any, language) : analyticsData?.current_wellness_score >= 60 ? t('good' as any, language) : t('needsImprovement' as any, language)}
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <Stat>
              <StatLabel>{t('progressTowardsGoal' as any, language)}</StatLabel>
              <StatNumber color={analyticsData?.progress_towards_goal >= 80 ? 'green.500' : analyticsData?.progress_towards_goal >= 50 ? 'orange.500' : 'blue.500'}>
                {analyticsData?.progress_towards_goal?.toFixed(0) || '0'}%
              </StatNumber>
              <StatHelpText>
                <StatArrow type={analyticsData?.progress_towards_goal >= 50 ? 'increase' : 'decrease'} />
                {t('towardsGoal', language)}
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card>
          <CardBody>
            <Stat>
              <StatLabel>{t('totalActivities', language)}</StatLabel>
              <StatNumber color={analyticsData?.activity_summary?.activity_count >= 5 ? 'green.500' : analyticsData?.activity_summary?.activity_count >= 3 ? 'orange.500' : 'blue.500'}>
                {analyticsData?.activity_summary?.activity_count || 0}
              </StatNumber>
              <StatHelpText>
                <StatArrow type={analyticsData?.activity_summary?.activity_count >= 3 ? 'increase' : 'decrease'} />
                {t('thisWeek' as any, language)}
              </StatHelpText>
            </Stat>
          </CardBody>
        </Card>
      </SimpleGrid>

      <Grid templateColumns={{ base: '1fr', lg: '2fr 1fr' }} gap={6}>
        <GridItem>
          <WeightProgressCard
            currentWeight={profileData?.weight || 0}
            targetWeight={profileData?.target_weight || 0}
            weightTrend={analyticsData?.weight_trend || []}
            measurementSystem={measurementSystem}
          />
        </GridItem>

        <GridItem>
          <Card bg="rgba(255, 255, 255, 0.95)" backdropFilter="blur(10px)" border="1px solid rgba(255, 255, 255, 0.2)" boxShadow="0 8px 32px rgba(0, 0, 0, 0.1)">
            <CardHeader>
              <Heading size="md">{t('activitySummary', language)}</Heading>
            </CardHeader>
            <CardBody>
              <Stack spacing={4}>
                <Box>
                  <Text fontWeight="bold" color="gray.500">{t('totalActivities', language)}</Text>
                  <Text fontSize="2xl">{analyticsData?.activity_summary?.activity_count || 0}</Text>
                </Box>
                <Box>
                  <Text fontWeight="bold" color="gray.500">{t('totalDuration', language)}</Text>
                  <Text fontSize="2xl">{analyticsData?.activity_summary?.total_duration || 0} {t('minTotal', language)}</Text>
                </Box>
                <Box>
                  <Text fontWeight="bold" color="gray.500">{t('averageDuration', language)}</Text>
                  <Text fontSize="2xl">{analyticsData?.activity_summary?.average_duration || 0} min</Text>
                </Box>
                <Box>
                  <Text fontWeight="bold" color="gray.500">{t('activityTypes', language)}</Text>
                  <Text fontSize="sm">
                    {analyticsData?.activity_summary?.activity_types?.join(', ') || t('noneRecorded', language)}
                  </Text>
                </Box>
                <Button colorScheme="green" onClick={onActivityModalOpen}>
                  {t('logTodaysActivity', language)}
                </Button>
              </Stack>
            </CardBody>
          </Card>
        </GridItem>
      </Grid>

      {/* AI Insights */}
      <Card mt={6} bg="rgba(255, 255, 255, 0.95)" backdropFilter="blur(10px)" border="1px solid rgba(255, 255, 255, 0.2)" boxShadow="0 8px 32px rgba(0, 0, 0, 0.1)">
        <CardHeader>
          <Heading size="md">{t('personalizedHealthInsights', language)}</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={4} align="stretch">
            {aiInsights?.insights?.map((insight, index) => (
              <Box key={index} p={4} bg="blue.50" borderRadius="md" border="1px" borderColor="blue.200">
                <Text color="blue.800">{insight}</Text>
              </Box>
            )) || (
              <Box p={4} bg="blue.50" borderRadius="md" border="1px" borderColor="blue.200">
                <Text color="blue.800">Welcome to your health journey! Start by logging your weight and activities.</Text>
              </Box>
            )}
          </VStack>
        </CardBody>
      </Card>

      <ActivityLogModal
        isOpen={isActivityModalOpen}
        onClose={onActivityModalClose}
        onActivityLogged={() => {
          // Refresh data when activity is logged
          window.location.reload();
        }}
      />
    </Box>
  );
};

export default Dashboard;
