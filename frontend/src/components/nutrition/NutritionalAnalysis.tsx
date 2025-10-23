import React, { useState } from 'react';
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
import { FiBarChart3, FiTrendingUp, FiTrendingDown, FiTarget } from 'react-icons/fi';
import { t } from '../../utils/translations';

interface NutritionalAnalysisProps {
  nutritionalLogs: any[];
  onUpdate: () => void;
}

const NutritionalAnalysis: React.FC<NutritionalAnalysisProps> = ({
  nutritionalLogs,
  onUpdate,
}) => {
  const [analysisType, setAnalysisType] = useState<'daily' | 'weekly' | 'monthly'>('daily');
  const [loading, setLoading] = useState(false);
  const [analysisData, setAnalysisData] = useState<any>(null);
  const toast = useToast();

  const loadAnalysis = async () => {
    try {
      setLoading(true);
      
      const endDate = new Date();
      const startDate = new Date();
      
      if (analysisType === 'daily') {
        startDate.setDate(endDate.getDate() - 1);
      } else if (analysisType === 'weekly') {
        startDate.setDate(endDate.getDate() - 7);
      } else {
        startDate.setMonth(endDate.getMonth() - 1);
      }

      const response = await fetch(
        `/api/nutrition/nutritional-analysis?start_date=${startDate.toISOString().split('T')[0]}&end_date=${endDate.toISOString().split('T')[0]}&analysis_type=${analysisType}`
      );

      if (response.ok) {
        const data = await response.json();
        setAnalysisData(data);
      } else {
        throw new Error('Failed to load analysis');
      }
    } catch (error) {
      console.error('Error loading analysis:', error);
      toast({
        title: 'Error loading analysis',
        description: 'Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  React.useEffect(() => {
    loadAnalysis();
  }, [analysisType]);

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
          {t('nutritionalAnalysis')}
        </Heading>
        <Text color="gray.600">
          Track your nutritional intake and get AI-powered insights
        </Text>
      </Box>

      {/* Analysis Controls */}
      <Card>
        <CardHeader>
          <Heading size="md">Analysis Period</Heading>
        </CardHeader>
        <CardBody>
          <HStack spacing={4}>
            <Button
              colorScheme={analysisType === 'daily' ? 'blue' : 'gray'}
              variant={analysisType === 'daily' ? 'solid' : 'outline'}
              onClick={() => setAnalysisType('daily')}
            >
              {t('dailyIntake')}
            </Button>
            <Button
              colorScheme={analysisType === 'weekly' ? 'blue' : 'gray'}
              variant={analysisType === 'weekly' ? 'solid' : 'outline'}
              onClick={() => setAnalysisType('weekly')}
            >
              {t('weeklyIntake')}
            </Button>
            <Button
              colorScheme={analysisType === 'monthly' ? 'blue' : 'gray'}
              variant={analysisType === 'monthly' ? 'solid' : 'outline'}
              onClick={() => setAnalysisType('monthly')}
            >
              {t('monthlyIntake')}
            </Button>
          </HStack>
        </CardBody>
      </Card>

      {loading ? (
        <Box textAlign="center" py={8}>
          <Spinner size="xl" color="blue.500" />
          <Text mt={4}>Loading analysis...</Text>
        </Box>
      ) : analysisData ? (
        <VStack spacing={6} align="stretch">
          {/* Nutritional Overview */}
          <Card>
            <CardHeader>
              <Heading size="md">Nutritional Overview</Heading>
            </CardHeader>
            <CardBody>
              <SimpleGrid columns={{ base: 2, md: 4 }} spacing={6}>
                <Stat>
                  <StatLabel>{t('calories')}</StatLabel>
                  <StatNumber>{analysisData.totals.calories.toFixed(0)}</StatNumber>
                  <StatHelpText>
                    <StatArrow type={analysisData.deficits.calories > 0 ? 'increase' : 'decrease'} />
                    {Math.abs(analysisData.deficits.calories).toFixed(0)} {analysisData.deficits.calories > 0 ? 'deficit' : 'surplus'}
                  </StatHelpText>
                </Stat>

                <Stat>
                  <StatLabel>{t('protein')}</StatLabel>
                  <StatNumber>{analysisData.totals.protein.toFixed(1)}g</StatNumber>
                  <StatHelpText>
                    <StatArrow type={analysisData.deficits.protein > 0 ? 'increase' : 'decrease'} />
                    {Math.abs(analysisData.deficits.protein).toFixed(1)}g {analysisData.deficits.protein > 0 ? 'deficit' : 'surplus'}
                  </StatHelpText>
                </Stat>

                <Stat>
                  <StatLabel>{t('carbs')}</StatLabel>
                  <StatNumber>{analysisData.totals.carbs.toFixed(1)}g</StatNumber>
                  <StatHelpText>
                    <StatArrow type={analysisData.deficits.carbs > 0 ? 'increase' : 'decrease'} />
                    {Math.abs(analysisData.deficits.carbs).toFixed(1)}g {analysisData.deficits.carbs > 0 ? 'deficit' : 'surplus'}
                  </StatHelpText>
                </Stat>

                <Stat>
                  <StatLabel>{t('fats')}</StatLabel>
                  <StatNumber>{analysisData.totals.fats.toFixed(1)}g</StatNumber>
                  <StatHelpText>
                    <StatArrow type={analysisData.deficits.fats > 0 ? 'increase' : 'decrease'} />
                    {Math.abs(analysisData.deficits.fats).toFixed(1)}g {analysisData.deficits.fats > 0 ? 'deficit' : 'surplus'}
                  </StatHelpText>
                </Stat>
              </SimpleGrid>
            </CardBody>
          </Card>

          {/* Progress Tracking */}
          <Card>
            <CardHeader>
              <Heading size="md">{t('progressTowardsGoal')}</Heading>
            </CardHeader>
            <CardBody>
              <VStack spacing={4}>
                <Box w="full">
                  <HStack justify="space-between" mb={2}>
                    <Text fontWeight="semibold">{t('calories')}</Text>
                    <Text fontSize="sm" color="gray.600">
                      {analysisData.totals.calories.toFixed(0)} / {analysisData.targets.calories}
                    </Text>
                  </HStack>
                  <Progress
                    value={analysisData.percentages.calories}
                    colorScheme={getProgressColor(analysisData.percentages.calories)}
                    size="lg"
                    borderRadius="md"
                  />
                  <Text fontSize="sm" color="gray.600" mt={1}>
                    {analysisData.percentages.calories.toFixed(1)}% of target
                  </Text>
                </Box>

                <Box w="full">
                  <HStack justify="space-between" mb={2}>
                    <Text fontWeight="semibold">{t('protein')}</Text>
                    <Text fontSize="sm" color="gray.600">
                      {analysisData.totals.protein.toFixed(1)}g / {analysisData.targets.protein}g
                    </Text>
                  </HStack>
                  <Progress
                    value={analysisData.percentages.protein}
                    colorScheme={getProgressColor(analysisData.percentages.protein)}
                    size="lg"
                    borderRadius="md"
                  />
                  <Text fontSize="sm" color="gray.600" mt={1}>
                    {analysisData.percentages.protein.toFixed(1)}% of target
                  </Text>
                </Box>

                <Box w="full">
                  <HStack justify="space-between" mb={2}>
                    <Text fontWeight="semibold">{t('carbs')}</Text>
                    <Text fontSize="sm" color="gray.600">
                      {analysisData.totals.carbs.toFixed(1)}g / {analysisData.targets.carbs}g
                    </Text>
                  </HStack>
                  <Progress
                    value={analysisData.percentages.carbs}
                    colorScheme={getProgressColor(analysisData.percentages.carbs)}
                    size="lg"
                    borderRadius="md"
                  />
                  <Text fontSize="sm" color="gray.600" mt={1}>
                    {analysisData.percentages.carbs.toFixed(1)}% of target
                  </Text>
                </Box>

                <Box w="full">
                  <HStack justify="space-between" mb={2}>
                    <Text fontWeight="semibold">{t('fats')}</Text>
                    <Text fontSize="sm" color="gray.600">
                      {analysisData.totals.fats.toFixed(1)}g / {analysisData.targets.fats}g
                    </Text>
                  </HStack>
                  <Progress
                    value={analysisData.percentages.fats}
                    colorScheme={getProgressColor(analysisData.percentages.fats)}
                    size="lg"
                    borderRadius="md"
                  />
                  <Text fontSize="sm" color="gray.600" mt={1}>
                    {analysisData.percentages.fats.toFixed(1)}% of target
                  </Text>
                </Box>
              </VStack>
            </CardBody>
          </Card>

          {/* AI Insights */}
          {analysisData.ai_insights && (
            <Card>
              <CardHeader>
                <Heading size="md">{t('nutritionalInsights')}</Heading>
              </CardHeader>
              <CardBody>
                <VStack spacing={4} align="stretch">
                  {analysisData.ai_insights.achievements && analysisData.ai_insights.achievements.length > 0 && (
                    <Box>
                      <Text fontWeight="semibold" color="green.600" mb={2}>
                        {t('achievements')}
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
                        {t('concerns')}
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
                        {t('suggestions')}
                      </Text>
                      {analysisData.ai_insights.suggestions.map((suggestion: string, index: number) => (
                        <HStack key={index} mb={1}>
                          <Icon as={FiBarChart3} color="blue.500" />
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
