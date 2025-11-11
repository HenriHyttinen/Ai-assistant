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
  Icon,
  useDisclosure,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
} from '@chakra-ui/react';
import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { MdPersonAdd, MdPerson } from 'react-icons/md';
import { analytics, healthProfile } from '../services/api';
import { useApp } from '../contexts/AppContext';
import { getErrorMessage } from '../utils/errorUtils';
import ActivityLogModal from '../components/ActivityLogModal';
import WeightProgressCard from '../components/WeightProgressCard';
import { t } from '../utils/translations';

interface HealthAnalytics {
  current_bmi: number;
  current_wellness_score: number;
  weight_trend: number[];
  weight_trend_timestamps: string[];
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
  fitness_goal?: string;
  updated_at: string;
}

interface AIInsights {
  insights: string[];
  metrics: {
    bmi: number;
    bmi_category: string;
    wellness_score: number;
  };
  is_cached?: boolean;
  is_fallback?: boolean;
  cache_timestamp?: number;
}

const Dashboard = () => {
  const { measurementSystem, language, user } = useApp();

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
  const { isOpen: isActivityModalOpen, onOpen: onActivityModalOpen, onClose: onActivityModalClose } = useDisclosure();
  
  const [analyticsData, setAnalyticsData] = useState<HealthAnalytics | null>(null);
  const [profileData, setProfileData] = useState<HealthProfile | null>(null);
  const [aiInsights, setAiInsights] = useState<AIInsights | null>(null);
  const [nutritionalInsights, setNutritionalInsights] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [needsHealthProfile, setNeedsHealthProfile] = useState(false);
  const [chartsReady, setChartsReady] = useState(false);
  const [aiRequestCount, setAiRequestCount] = useState(0);

  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      setNeedsHealthProfile(false);
      
      // Check if user is fully authenticated before making API calls
      if (!user || !user.id || !user.email) {
        console.log('User not fully authenticated, skipping dashboard API calls');
        setLoading(false);
        return;
      }
      
      console.log('Starting dashboard data fetch...');
      
      // First, try to fetch health profile
      let profileResponse;
      try {
        console.log('Fetching health profile...');
        // API service already has 15s timeout and caching built-in
        profileResponse = await healthProfile.getProfile();
        setProfileData(profileResponse.data);
        console.log('Health profile fetched successfully');
      } catch (profileError: any) {
        console.error('Health profile fetch error:', profileError);
        // Handle timeout gracefully - API service will use cached data if available
        if (profileError?.message?.includes('timeout') || 
            profileError?.code === 'ECONNABORTED' || 
            profileError?.message?.includes('timed out')) {
          console.warn('Health profile fetch timed out - API service should use cached data if available');
          // If we get a timeout, the API service interceptor should have already tried cached data
          // If still no data, user doesn't have a profile yet
          setNeedsHealthProfile(true);
          setLoading(false);
          return;
        } else if (profileError?.response?.status === 404) {
          // User doesn't have a health profile yet
          setNeedsHealthProfile(true);
          setLoading(false);
          return;
        }
        throw profileError;
      }
        
        console.log('Fetching analytics and insights in parallel...');
        
        // Fetch analytics and insights in parallel for better performance
        const analyticsWithRetry = async () => {
          try {
            return await Promise.race([
              analytics.getAnalytics(),
              new Promise((_, reject) => 
                setTimeout(() => reject(new Error('Analytics timeout')), 15000)
              )
            ]);
          } catch (err: any) {
            // One quick retry with shorter timeout
            if (err?.message === 'Analytics timeout' || err?.code === 'ECONNABORTED') {
              console.warn('Analytics timeout, retrying once...');
              try {
                return await Promise.race([
                  analytics.getAnalytics(),
                  new Promise((_, reject) => 
                    setTimeout(() => reject(new Error('Analytics timeout (retry)')), 5000)
                  )
                ]);
              } catch (retryErr) {
                throw retryErr;
              }
            }
            throw err;
          }
        };

        const [analyticsResult, insightsResult] = await Promise.allSettled([
          analyticsWithRetry().catch((error: any) => {
            console.warn('Analytics fetch warning:', error?.message || error);
            if (error?.response?.status === 404) {
              throw new Error('Analytics not found - profile incomplete');
            }
            throw error;
          }),
          Promise.race([
            healthProfile.getInsights(),
            new Promise((_, reject) => 
              setTimeout(() => reject(new Error('Insights timeout')), 12000)
            )
          ]).catch((error: any) => {
            console.warn('Insights fetch warning:', error?.message || error);
            // Return fallback insights instead of throwing
            return {
              data: {
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
              }
            };
          })
        ]);
        
        // Handle analytics result
        if (analyticsResult.status === 'fulfilled') {
          setAnalyticsData(analyticsResult.value.data);
          console.log('Analytics data fetched successfully');
        } else {
          console.error('Analytics failed:', analyticsResult.reason);
          if (analyticsResult.reason.message === 'Analytics not found - profile incomplete') {
            setNeedsHealthProfile(true);
            setLoading(false);
            return;
          }
        }
        
        // Handle insights result
        if (insightsResult.status === 'fulfilled') {
          const insightsResponse = insightsResult.value;
          if (insightsResponse && insightsResponse.data && insightsResponse.data.insights) {
            setAiInsights(insightsResponse.data);
            console.log('AI insights fetched successfully');
          }
        } else {
          console.error('Insights failed:', insightsResult.reason);
        }

        // Fetch nutritional insights asynchronously (non-blocking) with delay and concurrency limit
        setTimeout(() => {
          // Limit concurrent AI requests to prevent overwhelming the backend
          if (aiRequestCount >= 2) {
            console.log('AI request limit reached, skipping nutritional insights');
            return;
          }
          
          setAiRequestCount(prev => prev + 1);
          
          import('../services/nutritionAnalyticsService').then(({ default: nutritionAnalyticsService }) => {
            Promise.race([
              nutritionAnalyticsService.getComprehensiveAnalysis('2024-01-01', '2024-12-31', 'daily'),
              new Promise((_, reject) => setTimeout(() => reject(new Error('Nutritional insights timeout')), 15000))
            ])
              .then(nutritionalData => {
                setNutritionalInsights(nutritionalData);
                setAiRequestCount(prev => Math.max(0, prev - 1)); // Decrement counter
              })
              .catch(nutritionalError => {
                console.warn('Failed to load nutritional insights:', nutritionalError);
                setNutritionalInsights(null);
                setAiRequestCount(prev => Math.max(0, prev - 1)); // Decrement counter
              });
          }).catch(error => {
            console.warn('Failed to import nutrition analytics service:', error);
            setAiRequestCount(prev => Math.max(0, prev - 1)); // Decrement counter
          });
        }, 2000); // Delay by 2 seconds to not overwhelm the backend
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchData();
  }, [user]);

  // allow layout to settle to avoid 0x0 chart warnings
  useEffect(() => {
    if (!loading && !error) {
      const id = setTimeout(() => setChartsReady(true), 150);
      return () => clearTimeout(id);
    } else {
      setChartsReady(false);
    }
  }, [loading, error]);


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
          {getErrorMessage(error)}
        </Alert>
      </Box>
    );
  }

  if (needsHealthProfile) {
    return (
      <Box p={6} textAlign="center">
        <VStack spacing={6} maxW="600px" mx="auto">
          <Icon as={MdPersonAdd} boxSize={16} color="blue.500" />
          <Heading size="lg" color="gray.700">
            {t('welcomeToHealthTracking', language)}
          </Heading>
          <Text fontSize="lg" color="gray.600" lineHeight="1.6">
            {t('createHealthProfileMessage', language)}
          </Text>
          <VStack spacing={4} align="stretch" w="full">
            <Button
              as={Link}
              to="/profile"
              colorScheme="blue"
              size="lg"
              leftIcon={<Icon as={MdPerson} />}
            >
              {t('createHealthProfile', language)}
            </Button>
            <Text fontSize="sm" color="gray.500">
              {t('healthProfileBenefits', language)}
            </Text>
          </VStack>
        </VStack>
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
          {chartsReady ? (
            <WeightProgressCard
              currentWeight={profileData?.weight || 0}
              targetWeight={profileData?.target_weight || 0}
              weightTrend={analyticsData?.weight_trend || []}
              weightTrendTimestamps={analyticsData?.weight_trend_timestamps || []}
              measurementSystem={measurementSystem}
              fitnessGoal={profileData?.fitness_goal}
            />
          ) : (
            <Card><CardBody><Spinner size="md" color="blue.500" /></CardBody></Card>
          )}
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
                  <Text fontSize="2xl">{formatDuration(analyticsData?.activity_summary?.total_duration || 0)}</Text>
                </Box>
                <Box>
                  <Text fontWeight="bold" color="gray.500">{t('averageDuration', language)}</Text>
                  <Text fontSize="2xl">{formatDuration(analyticsData?.activity_summary?.average_duration || 0)}</Text>
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

      {/* AI Insights - Grouped Health and Nutritional Insights */}
      <Card mt={6} bg="rgba(255, 255, 255, 0.95)" backdropFilter="blur(10px)" border="1px solid rgba(255, 255, 255, 0.2)" boxShadow="0 8px 32px rgba(0, 0, 0, 0.1)">
        <CardHeader>
          <Heading size="md">{t('personalizedHealthInsights', language)}</Heading>
          {/* Cache Status Indicator */}
          {aiInsights && (
            <Box mt={2}>
              {aiInsights.is_fallback ? (
                <Text fontSize="sm" color="orange.600" fontWeight="medium">
                  🌐 Offline Mode - Using cached insights
                </Text>
              ) : aiInsights.is_cached ? (
                <Text fontSize="sm" color="blue.600" fontWeight="medium">
                  💾 Cached insights (faster loading)
                </Text>
              ) : (
                <Text fontSize="sm" color="green.600" fontWeight="medium">
                  ✨ Fresh AI insights
                </Text>
              )}
              {/* Goal-specific indicator */}
              {aiInsights.insights && aiInsights.insights.some(insight => 
                insight.toLowerCase().includes('weight loss') || 
                insight.toLowerCase().includes('muscle gain') ||
                insight.toLowerCase().includes('endurance') ||
                insight.toLowerCase().includes('strength')
              ) && (
                <Text fontSize="xs" color="purple.600" mt={1}>
                  🎯 Goal-specific insights
                </Text>
              )}
            </Box>
          )}
        </CardHeader>
        <CardBody>
          <Tabs variant="enclosed" colorScheme="blue">
            <TabList>
              <Tab>🏃‍♂️ Health Insights</Tab>
              <Tab>🥗 Nutritional Insights</Tab>
            </TabList>

            <TabPanels>
              {/* Health Insights Tab */}
              <TabPanel px={0}>
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
              </TabPanel>

              {/* Nutritional Insights Tab */}
              <TabPanel px={0}>
                <VStack spacing={4} align="stretch">
                  {nutritionalInsights ? (
                    <>
                      {/* Achievements */}
                      {nutritionalInsights.ai_insights?.achievements && nutritionalInsights.ai_insights.achievements.length > 0 && (
                        <Box>
                          <Text fontWeight="semibold" color="green.600" mb={2}>
                            🎉 Achievements
                          </Text>
                          {nutritionalInsights.ai_insights.achievements.map((achievement: string, index: number) => (
                            <Box key={index} p={3} bg="green.50" borderRadius="md" border="1px" borderColor="green.200" mb={2}>
                              <Text color="green.800" fontSize="sm">{achievement}</Text>
                            </Box>
                          ))}
                        </Box>
                      )}

                      {/* Concerns */}
                      {nutritionalInsights.ai_insights?.concerns && nutritionalInsights.ai_insights.concerns.length > 0 && (
                        <Box>
                          <Text fontWeight="semibold" color="orange.600" mb={2}>
                            ⚠️ Areas for Improvement
                          </Text>
                          {nutritionalInsights.ai_insights.concerns.map((concern: string, index: number) => (
                            <Box key={index} p={3} bg="orange.50" borderRadius="md" border="1px" borderColor="orange.200" mb={2}>
                              <Text color="orange.800" fontSize="sm">{concern}</Text>
                            </Box>
                          ))}
                        </Box>
                      )}

                      {/* Suggestions */}
                      {nutritionalInsights.ai_insights?.suggestions && nutritionalInsights.ai_insights.suggestions.length > 0 && (
                        <Box>
                          <Text fontWeight="semibold" color="purple.600" mb={2}>
                            💡 Recommendations
                          </Text>
                          {nutritionalInsights.ai_insights.suggestions.map((suggestion: string, index: number) => (
                            <Box key={index} p={3} bg="purple.50" borderRadius="md" border="1px" borderColor="purple.200" mb={2}>
                              <Text color="purple.800" fontSize="sm">{suggestion}</Text>
                            </Box>
                          ))}
                        </Box>
                      )}
                    </>
                  ) : (
                    <Box p={4} bg="gray.50" borderRadius="md" border="1px" borderColor="gray.200">
                      <Text color="gray.600" textAlign="center">
                        Start logging your meals to see personalized nutritional insights!
                      </Text>
                    </Box>
                  )}
                </VStack>
              </TabPanel>
            </TabPanels>
          </Tabs>
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
