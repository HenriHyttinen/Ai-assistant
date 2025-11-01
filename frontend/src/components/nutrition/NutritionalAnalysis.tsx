import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  ButtonGroup,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Badge,
  Progress,
  useToast,
  SimpleGrid,
  Icon,
  Flex,
  Spinner,
  Alert,
  AlertIcon,
  Divider,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
} from '@chakra-ui/react';
import { FiBarChart, FiTrendingUp, FiTrendingDown, FiTarget, FiRefreshCw } from 'react-icons/fi';
import { t } from '../../utils/translations';
import MacronutrientVisualization from './MacronutrientVisualization';
import AdvancedNutritionDashboard from './AdvancedNutritionDashboard';

interface NutritionalAnalysisProps {
  nutritionalLogs?: any[];
  onUpdate?: () => void;
}

const NutritionalAnalysis: React.FC<NutritionalAnalysisProps> = ({
  nutritionalLogs = [],
  onUpdate = () => {},
}) => {
  const [analysisType, setAnalysisType] = useState<'daily' | 'weekly' | 'monthly'>('daily');
  const [loading, setLoading] = useState(false);
  const [dashboardMode, setDashboardMode] = useState<'basic' | 'advanced'>('advanced');
  const [analysisData, setAnalysisData] = useState<any>({
    totals: {
      calories: 0,
      protein: 0,
      carbs: 0,
      fats: 0,
    },
    targets: {
      calories: 2000,
      protein: 150,
      carbs: 250,
      fats: 65,
    },
    deficits: {
      calories: 0,
      protein: 0,
      carbs: 0,
      fats: 0,
    },
    percentages: {
      calories: 0,
      protein: 0,
      carbs: 0,
      fats: 0,
    },
    ai_insights: {
      achievements: ['No data available yet'],
      concerns: ['Please log some meals to see analysis'],
      suggestions: ['Start by logging your daily meals'],
    },
  });
  const toast = useToast();

  const loadAnalysis = async () => {
    try {
      setLoading(true);
      
      const endDate = new Date();
      const startDate = new Date();
      
      if (analysisType === 'daily') {
        startDate.setDate(endDate.getDate()); // Same day for daily analysis
      } else if (analysisType === 'weekly') {
        startDate.setDate(endDate.getDate() - 6); // Last 7 days including today
      } else {
        startDate.setDate(endDate.getDate() - 29); // Last 30 days including today
      }

      // Get Supabase session token
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        throw new Error('No authentication session found');
      }
      
      // Add cache-busting parameter to force fresh data
      const timestamp = new Date().getTime();
      const endpoint = dashboardMode === 'advanced' 
        ? 'advanced-analytics' 
        : 'nutritional-analysis';
      
      const response = await fetch(
        `http://localhost:8000/nutrition/${endpoint}?start_date=${startDate.toISOString().split('T')[0]}&end_date=${endDate.toISOString().split('T')[0]}&analysis_type=${analysisType}&_t=${timestamp}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${session.access_token}`,
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache'
          },
        }
      );

      if (response.ok) {
        const data = await response.json();
        console.log('🔍 NutritionalAnalysis API Response:', data);
        setAnalysisData(data);
        
        toast({
          title: 'Analysis Updated',
          description: `Nutritional analysis loaded for ${analysisType} period.`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || `Failed to load analysis: ${response.status}`);
      }
    } catch (error) {
      console.error('Error loading analysis:', error);
      
      // Set mock data for development/demo purposes
      const mockData = {
        totals: {
          calories: 1850,
          protein: 95,
          carbs: 180,
          fats: 65,
        },
        targets: {
          calories: 2000,
          protein: 150,
          carbs: 250,
          fats: 65,
        },
        deficits: {
          calories: 150,
          protein: 55,
          carbs: 70,
          fats: 0,
        },
        percentages: {
          calories: 92.5,
          protein: 63.3,
          carbs: 72.0,
          fats: 100.0,
        },
        daily_breakdown: [
          { date: '2024-01-01', calories: 1850, protein: 95, carbs: 180, fats: 65, meals: [] },
          { date: '2024-01-02', calories: 2100, protein: 120, carbs: 220, fats: 70, meals: [] },
          { date: '2024-01-03', calories: 1950, protein: 110, carbs: 190, fats: 60, meals: [] }
        ],
        meal_distribution: {
          breakfast: 25,
          lunch: 35,
          dinner: 30,
          snacks: 10
        },
        ai_insights: {
          achievements: [
            'Great job meeting your fat intake goal!',
            'Consistent daily calorie intake this week'
          ],
          concerns: [
            'Protein intake is below target - consider adding lean meats or legumes',
            'Carb intake could be increased for better energy levels'
          ],
          suggestions: [
            'Add a protein shake to your morning routine',
            'Include more whole grains in your meals',
            'Consider meal prepping for consistent nutrition'
          ],
          trends: [
            'Calorie intake has been stable over the past week',
            'Protein consumption is trending upward'
          ]
        },
      };
      
      setAnalysisData(mockData);
      
      toast({
        title: 'Demo Mode',
        description: 'Showing sample data. Log some meals to see real analysis.',
        status: 'info',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    loadAnalysis();
  }, [analysisType, dashboardMode]);

  const getProgressColor = (percentage: number) => {
    if (percentage >= 90 && percentage <= 110) return 'green';
    if (percentage >= 70 && percentage < 90) return 'yellow';
    if (percentage > 110) return 'red';
    return 'red';
  };

  const getTrendIcon = (value: number, target: number) => {
    if (value >= target * 0.9 && value <= target * 1.1) return FiTarget;
    if (value < target) return FiTrendingDown;
    return FiTrendingUp;
  };

  return (
    <VStack spacing={6} align="stretch">
      <Box>
        <Heading size="lg" mb={2}>
          {t('nutritionalAnalysis', 'en')}
        </Heading>
        <Text color="gray.600">
          Track your nutritional intake and get AI-powered insights
        </Text>
      </Box>

      {/* Analysis Controls */}
      <Card>
        <CardHeader>
          <HStack justify="space-between" align="center">
            <Heading size="md">Analysis Settings</Heading>
            <Button
              leftIcon={<FiRefreshCw />}
              onClick={loadAnalysis}
              isLoading={loading}
              size="sm"
              colorScheme="blue"
              variant="outline"
            >
              Refresh Data
            </Button>
          </HStack>
        </CardHeader>
        <CardBody>
          <VStack spacing={4} align="stretch">
            {/* Dashboard Mode Toggle */}
            <Box>
              <Text fontWeight="semibold" mb={2}>Dashboard Mode</Text>
              <ButtonGroup isAttached>
                <Button
                  colorScheme={dashboardMode === 'advanced' ? 'blue' : 'gray'}
                  variant={dashboardMode === 'advanced' ? 'solid' : 'outline'}
                  onClick={() => setDashboardMode('advanced')}
                  isDisabled={loading}
                >
                  Advanced Dashboard
                </Button>
                <Button
                  colorScheme={dashboardMode === 'basic' ? 'blue' : 'gray'}
                  variant={dashboardMode === 'basic' ? 'solid' : 'outline'}
                  onClick={() => setDashboardMode('basic')}
                  isDisabled={loading}
                >
                  Basic View
                </Button>
              </ButtonGroup>
            </Box>
            
            {/* Analysis Period */}
            <Box>
              <Text fontWeight="semibold" mb={2}>Analysis Period</Text>
              <HStack spacing={4}>
                <Button
                  colorScheme={analysisType === 'daily' ? 'blue' : 'gray'}
                  variant={analysisType === 'daily' ? 'solid' : 'outline'}
                  onClick={() => setAnalysisType('daily')}
                  isDisabled={loading}
                >
                  {t('dailyIntake', 'en')}
                </Button>
                <Button
                  colorScheme={analysisType === 'weekly' ? 'blue' : 'gray'}
                  variant={analysisType === 'weekly' ? 'solid' : 'outline'}
                  onClick={() => setAnalysisType('weekly')}
                  isDisabled={loading}
                >
                  {t('weeklyIntake', 'en')}
                </Button>
                <Button
                  colorScheme={analysisType === 'monthly' ? 'blue' : 'gray'}
                  variant={analysisType === 'monthly' ? 'solid' : 'outline'}
                  onClick={() => setAnalysisType('monthly')}
                  isDisabled={loading}
                >
                  {t('monthlyIntake', 'en')}
                </Button>
              </HStack>
            </Box>
          </VStack>
        </CardBody>
      </Card>

      {loading ? (
        <Box textAlign="center" py={8}>
          <Spinner size="xl" color="blue.500" />
          <Text mt={4}>Loading analysis...</Text>
        </Box>
      ) : analysisData ? (
        dashboardMode === 'advanced' ? (
          <AdvancedNutritionDashboard
            currentData={{
              calories: analysisData.totals?.calories || 0,
              protein: analysisData.totals?.protein || 0,
              carbs: analysisData.totals?.carbs || 0,
              fats: analysisData.totals?.fats || 0,
              fiber: analysisData.totals?.fiber || 0,
              sugar: analysisData.totals?.sugar || 0,
              sodium: analysisData.totals?.sodium || 0
            }}
            targets={{
              calories: analysisData.targets?.calories || 2000,
              protein: analysisData.targets?.protein || 150,
              carbs: analysisData.targets?.carbs || 250,
              fats: analysisData.targets?.fats || 65
            }}
            dailyBreakdown={analysisData.daily_breakdown || []}
            mealDistribution={analysisData.meal_distribution}
            period={analysisType}
            onPeriodChange={setAnalysisType}
            aiInsights={analysisData.ai_insights}
          />
        ) : (
          <VStack spacing={6} align="stretch">
          {/* Quick Stats Summary */}
          <Card>
            <CardHeader>
              <Heading size="md">Quick Overview</Heading>
            </CardHeader>
            <CardBody>
              <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
                <VStack>
                  <Text fontSize="sm" color="gray.600">Calories</Text>
                  <Text fontSize="2xl" fontWeight="bold" color="blue.500">
                    {analysisData?.totals?.calories?.toFixed(0) || 0}
                  </Text>
                  <Text fontSize="xs" color="gray.500">
                    of {analysisData?.targets?.calories || 0} target
                  </Text>
                </VStack>
                <VStack>
                  <Text fontSize="sm" color="gray.600">Protein</Text>
                  <Text fontSize="2xl" fontWeight="bold" color="green.500">
                    {analysisData?.totals?.protein?.toFixed(1) || 0}g
                  </Text>
                  <Text fontSize="xs" color="gray.500">
                    {((analysisData?.totals?.protein || 0) / (analysisData?.targets?.protein || 1) * 100).toFixed(0)}% of target
                  </Text>
                </VStack>
                <VStack>
                  <Text fontSize="sm" color="gray.600">Carbs</Text>
                  <Text fontSize="2xl" fontWeight="bold" color="yellow.500">
                    {analysisData?.totals?.carbs?.toFixed(1) || 0}g
                  </Text>
                  <Text fontSize="xs" color="gray.500">
                    {((analysisData?.totals?.carbs || 0) / (analysisData?.targets?.carbs || 1) * 100).toFixed(0)}% of target
                  </Text>
                </VStack>
                <VStack>
                  <Text fontSize="sm" color="gray.600">Fats</Text>
                  <Text fontSize="2xl" fontWeight="bold" color="orange.500">
                    {analysisData?.totals?.fats?.toFixed(1) || 0}g
                  </Text>
                  <Text fontSize="xs" color="gray.500">
                    {((analysisData?.totals?.fats || 0) / (analysisData?.targets?.fats || 1) * 100).toFixed(0)}% of target
                  </Text>
                </VStack>
              </SimpleGrid>
            </CardBody>
          </Card>

          {/* Nutritional Overview */}
          <Card>
            <CardHeader>
              <Heading size="md">Nutritional Overview</Heading>
            </CardHeader>
            <CardBody>
              <SimpleGrid columns={{ base: 2, md: 4 }} spacing={6}>
                <Stat>
                  <StatLabel>{t('calories', 'en')}</StatLabel>
                  <StatNumber>{analysisData?.totals?.calories?.toFixed(0) || 0}</StatNumber>
                  <StatHelpText>
                    <StatArrow type={(analysisData?.deficits?.calories || 0) > 0 ? 'increase' : 'decrease'} />
                    {Math.abs(analysisData?.deficits?.calories || 0).toFixed(0)} {(analysisData?.deficits?.calories || 0) > 0 ? 'deficit' : 'surplus'}
                  </StatHelpText>
                </Stat>

                <Stat>
                  <StatLabel>{t('protein', 'en')}</StatLabel>
                  <StatNumber>{analysisData?.totals?.protein?.toFixed(1) || 0}g</StatNumber>
                  <StatHelpText>
                    <StatArrow type={(analysisData?.deficits?.protein || 0) > 0 ? 'increase' : 'decrease'} />
                    {Math.abs(analysisData?.deficits?.protein || 0).toFixed(1)}g {(analysisData?.deficits?.protein || 0) > 0 ? 'deficit' : 'surplus'}
                  </StatHelpText>
                </Stat>

                <Stat>
                  <StatLabel>{t('carbs', 'en')}</StatLabel>
                  <StatNumber>{analysisData?.totals?.carbs?.toFixed(1) || 0}g</StatNumber>
                  <StatHelpText>
                    <StatArrow type={(analysisData?.deficits?.carbs || 0) > 0 ? 'increase' : 'decrease'} />
                    {Math.abs(analysisData?.deficits?.carbs || 0).toFixed(1)}g {(analysisData?.deficits?.carbs || 0) > 0 ? 'deficit' : 'surplus'}
                  </StatHelpText>
                </Stat>

                <Stat>
                  <StatLabel>{t('fats', 'en')}</StatLabel>
                  <StatNumber>{analysisData?.totals?.fats?.toFixed(1) || 0}g</StatNumber>
                  <StatHelpText>
                    <StatArrow type={(analysisData?.deficits?.fats || 0) > 0 ? 'increase' : 'decrease'} />
                    {Math.abs(analysisData?.deficits?.fats || 0).toFixed(1)}g {(analysisData?.deficits?.fats || 0) > 0 ? 'deficit' : 'surplus'}
                  </StatHelpText>
                </Stat>
              </SimpleGrid>
            </CardBody>
          </Card>

          {/* Progress Tracking */}
          <Card>
            <CardHeader>
              <Heading size="md">{t('progressTowardsGoal', 'en')}</Heading>
            </CardHeader>
            <CardBody>
              <VStack spacing={4}>
                <Box w="full">
                  <HStack justify="space-between" mb={2}>
                    <Text fontWeight="semibold">{t('calories', 'en')}</Text>
                    <Text fontSize="sm" color="gray.600">
                      {analysisData?.totals?.calories?.toFixed(0) || 0} / {analysisData?.targets?.calories || 0}
                    </Text>
                  </HStack>
                  <Progress
                    value={analysisData?.percentages?.calories || 0}
                    colorScheme={getProgressColor(analysisData?.percentages?.calories || 0)}
                    size="lg"
                    borderRadius="md"
                  />
                  <Text fontSize="sm" color="gray.600" mt={1}>
                    {(analysisData?.percentages?.calories || 0).toFixed(1)}% of target
                  </Text>
                </Box>

                <Box w="full">
                  <HStack justify="space-between" mb={2}>
                    <Text fontWeight="semibold">{t('protein', 'en')}</Text>
                    <Text fontSize="sm" color="gray.600">
                      {analysisData?.totals?.protein?.toFixed(1) || 0}g / {analysisData?.targets?.protein || 0}g
                    </Text>
                  </HStack>
                  <Progress
                    value={analysisData?.percentages?.protein || 0}
                    colorScheme={getProgressColor(analysisData?.percentages?.protein || 0)}
                    size="lg"
                    borderRadius="md"
                  />
                  <Text fontSize="sm" color="gray.600" mt={1}>
                    {(analysisData?.percentages?.protein || 0).toFixed(1)}% of target
                  </Text>
                </Box>

                <Box w="full">
                  <HStack justify="space-between" mb={2}>
                    <Text fontWeight="semibold">{t('carbs', 'en')}</Text>
                    <Text fontSize="sm" color="gray.600">
                      {analysisData?.totals?.carbs?.toFixed(1) || 0}g / {analysisData?.targets?.carbs || 0}g
                    </Text>
                  </HStack>
                  <Progress
                    value={analysisData?.percentages?.carbs || 0}
                    colorScheme={getProgressColor(analysisData?.percentages?.carbs || 0)}
                    size="lg"
                    borderRadius="md"
                  />
                  <Text fontSize="sm" color="gray.600" mt={1}>
                    {(analysisData?.percentages?.carbs || 0).toFixed(1)}% of target
                  </Text>
                </Box>

                <Box w="full">
                  <HStack justify="space-between" mb={2}>
                    <Text fontWeight="semibold">{t('fats', 'en')}</Text>
                    <Text fontSize="sm" color="gray.600">
                      {analysisData?.totals?.fats?.toFixed(1) || 0}g / {analysisData?.targets?.fats || 0}g
                    </Text>
                  </HStack>
                  <Progress
                    value={analysisData?.percentages?.fats || 0}
                    colorScheme={getProgressColor(analysisData?.percentages?.fats || 0)}
                    size="lg"
                    borderRadius="md"
                  />
                  <Text fontSize="sm" color="gray.600" mt={1}>
                    {(analysisData?.percentages?.fats || 0).toFixed(1)}% of target
                  </Text>
                </Box>
              </VStack>
            </CardBody>
          </Card>

          {/* Macronutrient Visualization */}
          <MacronutrientVisualization
            currentData={{
              calories: analysisData.totals.calories,
              protein: analysisData.totals.protein,
              carbs: analysisData.totals.carbs,
              fats: analysisData.totals.fats
            }}
            targets={{
              calories: analysisData.targets.calories,
              protein: analysisData.targets.protein,
              carbs: analysisData.targets.carbs,
              fats: analysisData.targets.fats
            }}
            dailyBreakdown={analysisData.daily_breakdown || []}
            period={analysisType}
            onPeriodChange={setAnalysisType}
          />

          {/* AI Insights */}
          {analysisData.ai_insights && (
            <Card>
              <CardHeader>
                <Heading size="md">{t('nutritionalInsights', 'en')}</Heading>
              </CardHeader>
              <CardBody>
                <VStack spacing={4} align="stretch">
                  {analysisData.ai_insights.achievements && analysisData.ai_insights.achievements.length > 0 && (
                    <Box>
                      <Text fontWeight="semibold" color="green.600" mb={2}>
                        {t('achievements', 'en')}
                      </Text>
                      {analysisData.ai_insights.achievements.map((achievement: string, index: number) => (
                        <HStack key={index} mb={1}>
                          <Icon as={FiTrendingUp} color="green.500" />
                          <Text fontSize="sm">{achievement}</Text>
                        </HStack>
                      ))}
                    </Box>
                  )}

                  {analysisData.ai_insights.concerns && analysisData.ai_insights.concerns.length > 0 && (
                    <Box>
                      <Text fontWeight="semibold" color="red.600" mb={2}>
                        {t('concerns', 'en')}
                      </Text>
                      {analysisData.ai_insights.concerns.map((concern: string, index: number) => (
                        <HStack key={index} mb={1}>
                          <Icon as={FiTrendingDown} color="red.500" />
                          <Text fontSize="sm">{concern}</Text>
                        </HStack>
                      ))}
                    </Box>
                  )}

                  {analysisData.ai_insights.suggestions && analysisData.ai_insights.suggestions.length > 0 && (
                    <Box>
                      <Text fontWeight="semibold" color="blue.600" mb={2}>
                        {t('suggestions', 'en')}
                      </Text>
                      {analysisData.ai_insights.suggestions.map((suggestion: string, index: number) => (
                        <HStack key={index} mb={1}>
                          <Icon as={FiBarChart} color="blue.500" />
                          <Text fontSize="sm">{suggestion}</Text>
                        </HStack>
                      ))}
                    </Box>
                  )}
                </VStack>
              </CardBody>
            </Card>
          )}
        </VStack>
        )
      ) : (
        <Alert status="info" borderRadius="lg">
          <AlertIcon />
          <Box>
            <Text fontWeight="semibold">No nutritional data available</Text>
            <Text>Start logging your meals to see nutritional analysis!</Text>
          </Box>
        </Alert>
      )}
    </VStack>
  );
};

export default NutritionalAnalysis;
