import React, { useState, useCallback } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Progress,
  useToast,
  SimpleGrid,
  Icon,
  Spinner,
  Alert,
  AlertIcon,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
} from '@chakra-ui/react';
import { FiBarChart, FiTrendingUp, FiTrendingDown, FiTarget, FiRefreshCw } from 'react-icons/fi';
import { t } from '../../utils/translations';
import MacronutrientVisualization from './MacronutrientVisualization';
import CalorieVisualization from './CalorieVisualization';

interface NutritionalAnalysisProps {
  nutritionalLogs?: any[];
  onUpdate?: () => void;
}

const NutritionalAnalysis: React.FC<NutritionalAnalysisProps> = () => {
  const [analysisType, setAnalysisType] = useState<'daily' | 'weekly' | 'monthly'>('daily');
  const [loading, setLoading] = useState(false);
  const [dailyTarget, setDailyTarget] = useState<number>(2000); // ROOT CAUSE FIX: Store daily target from preferences
  const [dailyTargets, setDailyTargets] = useState<{calories: number; protein: number; carbs: number; fats: number}>({
    calories: 2000,
    protein: 150,
    carbs: 250,
    fats: 65
  }); // ROOT CAUSE FIX: Store all daily targets from preferences
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

  // ROOT CAUSE FIX: Load user preferences to get daily target
  const loadPreferences = useCallback(async () => {
    try {
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        return; // Can't load preferences without session
      }
      
      const response = await fetch(
        'http://localhost:8000/nutrition/preferences',
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${session.access_token}`,
          },
        }
      );
      
      if (response.ok) {
        const prefs = await response.json();
        console.log('🎯 Loaded preferences:', prefs);
        // ROOT CAUSE FIX: Use daily targets from preferences
        // Backend uses: daily_calorie_target, protein_target, carbs_target, fats_target
        const newDailyTargets = {
          calories: prefs.daily_calorie_target || 2000,
          protein: prefs.protein_target || 150,
          carbs: prefs.carbs_target || 250,
          fats: prefs.fats_target || 65
        };
        setDailyTargets(newDailyTargets);
        setDailyTarget(newDailyTargets.calories);
        console.log('✅ Daily targets from preferences:', newDailyTargets);
      }
    } catch (error) {
      console.error('Error loading preferences:', error);
      // Use default if preferences can't be loaded
    }
  }, []);

  const loadAnalysis = useCallback(async () => {
    try {
      setLoading(true);
      
      // Use UTC dates to avoid timezone issues
      const now = new Date();
      const endDate = new Date(Date.UTC(now.getFullYear(), now.getMonth(), now.getDate()));
      let startDate = new Date(endDate);
      
      if (analysisType === 'daily') {
        // Same day for daily analysis
        startDate = new Date(endDate);
      } else if (analysisType === 'weekly') {
        // Last 7 days including today
        startDate = new Date(endDate);
        startDate.setUTCDate(startDate.getUTCDate() - 6);
      } else {
        // Last 30 days including today
        startDate = new Date(endDate);
        startDate.setUTCDate(startDate.getUTCDate() - 29);
      }
      
      // Format as YYYY-MM-DD for API call
      const formatDate = (date: Date) => {
        return `${date.getUTCFullYear()}-${String(date.getUTCMonth() + 1).padStart(2, '0')}-${String(date.getUTCDate()).padStart(2, '0')}`;
      };
      
      const startDateStr = formatDate(startDate);
      const endDateStr = formatDate(endDate);
      
      console.log(`📊 Loading ${analysisType} analysis: ${startDateStr} to ${endDateStr}`);

      // Get Supabase session token
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        throw new Error('No authentication session found');
      }
      
      // Add cache-busting parameter to force fresh data
      const timestamp = new Date().getTime();
      
      const response = await fetch(
        `http://localhost:8000/nutrition/advanced-analytics?start_date=${startDateStr}&end_date=${endDateStr}&analysis_type=${analysisType}&_t=${timestamp}`,
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
        console.log('📊 Totals:', data.totals);
        console.log('🎯 Targets:', data.targets);
        console.log('📈 Progress:', data.progress);
        console.log('📅 Daily breakdown:', data.daily_breakdown);
        
        // Validate that we have actual data (not empty analysis)
        if (!data.totals || (data.totals.calories === 0 && data.totals.protein === 0 && data.totals.carbs === 0 && data.totals.fats === 0)) {
          console.warn('⚠️ Received empty analysis - no nutrition data found');
          toast({
            title: 'No Data Available',
            description: `No nutritional logs found for ${analysisType} period (${startDateStr} to ${endDateStr}). Please log some meals first.`,
            status: 'info',
            duration: 5000,
            isClosable: true,
          });
        }
        
        // Ensure response has the expected structure with defaults
        const defaultDeficits = {
          calories: 0,
          protein: 0,
          carbs: 0,
          fats: 0,
          fiber: 0,
          sugar: 0,
          sodium: 0,
        };
        const defaultPercentages = {
          calories: 0,
          protein: 0,
          carbs: 0,
          fats: 0,
          fiber: 0,
          sugar: 0,
          sodium: 0,
        };
        
        // Merge deficits and percentages with defaults (handles empty objects)
        const deficits = data.deficits || data.progress?.deficits || {};
        const percentages = data.percentages || data.progress?.percentages || {};
        
        setAnalysisData({
          totals: data.totals || {
            calories: 0,
            protein: 0,
            carbs: 0,
            fats: 0,
          },
          targets: data.targets || {
            calories: 2000,
            protein: 150,
            carbs: 250,
            fats: 65,
          },
          deficits: { ...defaultDeficits, ...deficits },
          percentages: { ...defaultPercentages, ...percentages },
          daily_breakdown: data.daily_breakdown || [],
          meal_distribution: data.meal_distribution || {},
          ai_insights: data.ai_insights || {
            achievements: [],
            concerns: [],
            suggestions: []
          },
        });
        
        toast({
          title: 'Analysis Updated',
          description: `Nutritional analysis loaded for ${analysisType} period.`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      } else {
        const errorText = await response.text();
        let errorData;
        try {
          errorData = JSON.parse(errorText);
        } catch {
          errorData = { detail: errorText || `HTTP ${response.status}: ${response.statusText}` };
        }
        
        console.error('❌ API Error:', errorData);
        throw new Error(errorData.detail || `Failed to load ${analysisType} analysis (HTTP ${response.status})`);
      }
    } catch (error) {
      console.error('Error loading analysis:', error);
      
      // Set empty data structure on error instead of mock data
      setAnalysisData({
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
          fiber: 0,
          sugar: 0,
          sodium: 0,
        },
        percentages: {
          calories: 0,
          protein: 0,
          carbs: 0,
          fats: 0,
          fiber: 0,
          sugar: 0,
          sodium: 0,
        },
        daily_breakdown: [],
        meal_distribution: {},
        ai_insights: {
          achievements: ['No data available yet'],
          concerns: ['Please log some meals to see analysis'],
          suggestions: ['Start by logging your daily meals'],
        },
      });
      
      toast({
        title: 'No Data Available',
        description: error instanceof Error ? error.message : 'Please log some meals to see analysis.',
        status: 'info',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  }, [analysisType, toast]);

  // ROOT CAUSE FIX: Load preferences on mount to get daily target
  React.useEffect(() => {
    loadPreferences();
  }, [loadPreferences]);

  React.useEffect(() => {
    loadAnalysis();
  }, [loadAnalysis]);

  const getProgressColor = (percentage: number) => {
    if (percentage >= 90 && percentage <= 110) return 'green';
    if (percentage >= 70 && percentage < 90) return 'yellow';
    if (percentage > 110) return 'red';
    return 'red';
  };

  // ROOT CAUSE FIX: Calculate period targets from daily targets
  // For weekly: multiply daily targets by 7
  // For monthly: multiply daily targets by 30
  // For daily: use daily targets as-is
  const getPeriodTargets = useCallback(() => {
    const days = analysisType === 'daily' ? 1 : analysisType === 'weekly' ? 7 : 30;
    return {
      calories: dailyTargets.calories * days,
      protein: dailyTargets.protein * days,
      carbs: dailyTargets.carbs * days,
      fats: dailyTargets.fats * days
    };
  }, [analysisType, dailyTargets]);

  const periodTargets = getPeriodTargets();


  return (
    <VStack spacing={6} align="stretch">
      <Box>
        <Heading size="lg" mb={2}>
          {t('nutritionalAnalysis', 'en')}
        </Heading>
        <Text color="gray.600">
          Track your nutritional intake and get personalized insights
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
                    of {periodTargets.calories.toFixed(0)} target
                  </Text>
                </VStack>
                <VStack>
                  <Text fontSize="sm" color="gray.600">Protein</Text>
                  <Text fontSize="2xl" fontWeight="bold" color="green.500">
                    {analysisData?.totals?.protein?.toFixed(1) || 0}g
                  </Text>
                  <Text fontSize="xs" color="gray.500">
                    {((analysisData?.totals?.protein || 0) / (periodTargets.protein || 1) * 100).toFixed(0)}% of target
                  </Text>
                </VStack>
                <VStack>
                  <Text fontSize="sm" color="gray.600">Carbs</Text>
                  <Text fontSize="2xl" fontWeight="bold" color="yellow.500">
                    {analysisData?.totals?.carbs?.toFixed(1) || 0}g
                  </Text>
                  <Text fontSize="xs" color="gray.500">
                    {((analysisData?.totals?.carbs || 0) / (periodTargets.carbs || 1) * 100).toFixed(0)}% of target
                  </Text>
                </VStack>
                <VStack>
                  <Text fontSize="sm" color="gray.600">Fats</Text>
                  <Text fontSize="2xl" fontWeight="bold" color="orange.500">
                    {analysisData?.totals?.fats?.toFixed(1) || 0}g
                  </Text>
                  <Text fontSize="xs" color="gray.500">
                    {((analysisData?.totals?.fats || 0) / (periodTargets.fats || 1) * 100).toFixed(0)}% of target
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
                    <StatArrow type={(analysisData?.deficits?.calories ?? 0) > 0 ? 'increase' : 'decrease'} />
                    {Math.abs(analysisData?.deficits?.calories ?? 0).toFixed(0)} {(analysisData?.deficits?.calories ?? 0) > 0 ? 'deficit' : 'surplus'}
                  </StatHelpText>
                </Stat>

                <Stat>
                  <StatLabel>{t('protein', 'en')}</StatLabel>
                  <StatNumber>{analysisData?.totals?.protein?.toFixed(1) || 0}g</StatNumber>
                  <StatHelpText>
                    <StatArrow type={(analysisData?.deficits?.protein ?? 0) > 0 ? 'increase' : 'decrease'} />
                    {Math.abs(analysisData?.deficits?.protein ?? 0).toFixed(1)}g {(analysisData?.deficits?.protein ?? 0) > 0 ? 'deficit' : 'surplus'}
                  </StatHelpText>
                </Stat>

                <Stat>
                  <StatLabel>{t('carbs', 'en')}</StatLabel>
                  <StatNumber>{analysisData?.totals?.carbs?.toFixed(1) || 0}g</StatNumber>
                  <StatHelpText>
                    <StatArrow type={(analysisData?.deficits?.carbs ?? 0) > 0 ? 'increase' : 'decrease'} />
                    {Math.abs(analysisData?.deficits?.carbs ?? 0).toFixed(1)}g {(analysisData?.deficits?.carbs ?? 0) > 0 ? 'deficit' : 'surplus'}
                  </StatHelpText>
                </Stat>

                <Stat>
                  <StatLabel>{t('fats', 'en')}</StatLabel>
                  <StatNumber>{analysisData?.totals?.fats?.toFixed(1) || 0}g</StatNumber>
                  <StatHelpText>
                    <StatArrow type={(analysisData?.deficits?.fats ?? 0) > 0 ? 'increase' : 'decrease'} />
                    {Math.abs(analysisData?.deficits?.fats ?? 0).toFixed(1)}g {(analysisData?.deficits?.fats ?? 0) > 0 ? 'deficit' : 'surplus'}
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
                      {analysisData?.totals?.calories?.toFixed(0) || 0} / {periodTargets.calories.toFixed(0)}
                    </Text>
                  </HStack>
                  <Progress
                    value={((analysisData?.totals?.calories || 0) / (periodTargets.calories || 1) * 100)}
                    colorScheme={getProgressColor((analysisData?.totals?.calories || 0) / (periodTargets.calories || 1) * 100)}
                    size="lg"
                    borderRadius="md"
                  />
                  <Text fontSize="sm" color="gray.600" mt={1}>
                    {((analysisData?.totals?.calories || 0) / (periodTargets.calories || 1) * 100).toFixed(1)}% of target
                  </Text>
                </Box>

                <Box w="full">
                  <HStack justify="space-between" mb={2}>
                    <Text fontWeight="semibold">{t('protein', 'en')}</Text>
                    <Text fontSize="sm" color="gray.600">
                      {analysisData?.totals?.protein?.toFixed(1) || 0}g / {periodTargets.protein.toFixed(1)}g
                    </Text>
                  </HStack>
                  <Progress
                    value={((analysisData?.totals?.protein || 0) / (periodTargets.protein || 1) * 100)}
                    colorScheme={getProgressColor((analysisData?.totals?.protein || 0) / (periodTargets.protein || 1) * 100)}
                    size="lg"
                    borderRadius="md"
                  />
                  <Text fontSize="sm" color="gray.600" mt={1}>
                    {((analysisData?.totals?.protein || 0) / (periodTargets.protein || 1) * 100).toFixed(1)}% of target
                  </Text>
                </Box>

                <Box w="full">
                  <HStack justify="space-between" mb={2}>
                    <Text fontWeight="semibold">{t('carbs', 'en')}</Text>
                    <Text fontSize="sm" color="gray.600">
                      {analysisData?.totals?.carbs?.toFixed(1) || 0}g / {periodTargets.carbs.toFixed(1)}g
                    </Text>
                  </HStack>
                  <Progress
                    value={((analysisData?.totals?.carbs || 0) / (periodTargets.carbs || 1) * 100)}
                    colorScheme={getProgressColor((analysisData?.totals?.carbs || 0) / (periodTargets.carbs || 1) * 100)}
                    size="lg"
                    borderRadius="md"
                  />
                  <Text fontSize="sm" color="gray.600" mt={1}>
                    {((analysisData?.totals?.carbs || 0) / (periodTargets.carbs || 1) * 100).toFixed(1)}% of target
                  </Text>
                </Box>

                <Box w="full">
                  <HStack justify="space-between" mb={2}>
                    <Text fontWeight="semibold">{t('fats', 'en')}</Text>
                    <Text fontSize="sm" color="gray.600">
                      {analysisData?.totals?.fats?.toFixed(1) || 0}g / {periodTargets.fats.toFixed(1)}g
                    </Text>
                  </HStack>
                  <Progress
                    value={((analysisData?.totals?.fats || 0) / (periodTargets.fats || 1) * 100)}
                    colorScheme={getProgressColor((analysisData?.totals?.fats || 0) / (periodTargets.fats || 1) * 100)}
                    size="lg"
                    borderRadius="md"
                  />
                  <Text fontSize="sm" color="gray.600" mt={1}>
                    {((analysisData?.totals?.fats || 0) / (periodTargets.fats || 1) * 100).toFixed(1)}% of target
                  </Text>
                </Box>
              </VStack>
            </CardBody>
          </Card>

          {/* Calorie Visualization */}
          <CalorieVisualization
            currentData={{
              calories: analysisData?.totals?.calories || 0
            }}
            target={{
              calories: dailyTarget // ROOT CAUSE FIX: Always use daily target from preferences, not aggregated target
            }}
            dailyBreakdown={(analysisData?.daily_breakdown || []).map((day: any) => ({
              date: day.date,
              calories: day.calories,
              calorieTarget: dailyTarget // ROOT CAUSE FIX: Always use daily target for each day
            }))}
            period={analysisType}
            onPeriodChange={setAnalysisType}
          />

          {/* Macronutrient Visualization */}
          <MacronutrientVisualization
            currentData={{
              calories: analysisData?.totals?.calories || 0,
              protein: analysisData?.totals?.protein || 0,
              carbs: analysisData?.totals?.carbs || 0,
              fats: analysisData?.totals?.fats || 0
            }}
            targets={{
              calories: analysisData?.targets?.calories || 2000,
              protein: analysisData?.targets?.protein || 150,
              carbs: analysisData?.targets?.carbs || 250,
              fats: analysisData?.targets?.fats || 65
            }}
            dailyBreakdown={analysisData?.daily_breakdown || []}
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
