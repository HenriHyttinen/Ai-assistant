import React from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Heading,
  Card,
  CardBody,
  CardHeader,
  SimpleGrid,
  Progress,
  Badge,
  Icon,
  useColorModeValue,
  Alert,
  AlertIcon,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  CircularProgress,
  CircularProgressLabel
} from '@chakra-ui/react';
import { 
  FiTarget, 
  FiCheck, 
  FiAlertTriangle, 
  FiTrendingUp,
  FiTrendingDown,
  FiMinus,
  FiAward
} from 'react-icons/fi';
import type { NutritionGoalsProgress, GoalProgress } from '../../services/nutritionAnalyticsService';

interface GoalsProgressChartProps {
  goalsProgress: NutritionGoalsProgress;
}

const GoalsProgressChart: React.FC<GoalsProgressChartProps> = ({ goalsProgress }) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.400');

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'on_track':
        return <Icon as={FiCheck} color="green.500" />;
      case 'below_target':
        return <Icon as={FiTrendingDown} color="red.500" />;
      case 'above_target':
        return <Icon as={FiTrendingUp} color="orange.500" />;
      default:
        return <Icon as={FiMinus} color="gray.500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'on_track':
        return 'green';
      case 'below_target':
        return 'red';
      case 'above_target':
        return 'orange';
      default:
        return 'gray';
    }
  };

  const getOverallStatusIcon = (status: string) => {
    switch (status) {
      case 'excellent':
        return <Icon as={FiAward} color="gold" />;
      case 'good':
        return <Icon as={FiCheck} color="green.500" />;
      case 'fair':
        return <Icon as={FiAlertTriangle} color="yellow.500" />;
      case 'needs_improvement':
        return <Icon as={FiAlertTriangle} color="red.500" />;
      default:
        return <Icon as={FiMinus} color="gray.500" />;
    }
  };

  const getOverallStatusColor = (status: string) => {
    switch (status) {
      case 'excellent':
        return 'green';
      case 'good':
        return 'blue';
      case 'fair':
        return 'yellow';
      case 'needs_improvement':
        return 'red';
      default:
        return 'gray';
    }
  };

  const getNutrientUnit = (nutrient: string) => {
    switch (nutrient) {
      case 'calories':
        return 'cal';
      case 'protein':
      case 'fiber':
        return 'g';
      case 'sodium':
        return 'mg';
      default:
        return '';
    }
  };

  const getNutrientDisplayName = (nutrient: string) => {
    switch (nutrient) {
      case 'calories':
        return 'Calories';
      case 'protein':
        return 'Protein';
      case 'fiber':
        return 'Fiber';
      case 'sodium':
        return 'Sodium';
      default:
        return nutrient.charAt(0).toUpperCase() + nutrient.slice(1);
    }
  };

  if (goalsProgress.days_tracked === 0) {
    return (
      <VStack spacing={6} align="stretch">
        <Heading size="md">Goals Progress</Heading>
        <Alert status="info" borderRadius="lg">
          <AlertIcon />
          <VStack align="start" spacing={2}>
            <Text fontWeight="semibold">No goal data available</Text>
            <Text fontSize="sm">Start logging your meals to track progress toward your nutrition goals.</Text>
          </VStack>
        </Alert>
      </VStack>
    );
  }

  return (
    <VStack spacing={6} align="stretch">
      <Heading size="md">Nutrition Goals Progress</Heading>
      
      {/* Overall Status */}
      <Card>
        <CardHeader>
          <HStack spacing={2}>
            {getOverallStatusIcon(goalsProgress.overall_status)}
            <Heading size="sm">Overall Progress</Heading>
          </HStack>
        </CardHeader>
        <CardBody>
          <HStack spacing={6} align="center">
            <CircularProgress
              value={goalsProgress.overall_status === 'excellent' ? 100 : 
                     goalsProgress.overall_status === 'good' ? 80 :
                     goalsProgress.overall_status === 'fair' ? 60 : 40}
              color={`${getOverallStatusColor(goalsProgress.overall_status)}.500`}
              size="80px"
            >
              <CircularProgressLabel>
                <VStack spacing={0}>
                  <Text fontSize="xs" fontWeight="bold">
                    {goalsProgress.overall_status === 'excellent' ? '100%' : 
                     goalsProgress.overall_status === 'good' ? '80%' :
                     goalsProgress.overall_status === 'fair' ? '60%' : '40%'}
                  </Text>
                  <Text fontSize="xs" color={textColor}>
                    {goalsProgress.days_tracked} days
                  </Text>
                </VStack>
              </CircularProgressLabel>
            </CircularProgress>
            
            <VStack align="start" spacing={2}>
              <HStack spacing={2}>
                <Badge 
                  colorScheme={getOverallStatusColor(goalsProgress.overall_status)}
                  size="lg"
                >
                  {goalsProgress.overall_status.replace('_', ' ').toUpperCase()}
                </Badge>
              </HStack>
              <Text fontSize="sm" color={textColor}>
                Based on {Object.keys(goalsProgress.progress).length} nutrition goals
              </Text>
              <Text fontSize="sm" color={textColor}>
                Tracked over {goalsProgress.days_tracked} days
              </Text>
            </VStack>
          </HStack>
        </CardBody>
      </Card>

      {/* Individual Goal Progress */}
      {Object.keys(goalsProgress.progress).length === 0 ? (
        <Alert status="info" borderRadius="lg">
          <AlertIcon />
          <VStack align="start" spacing={2}>
            <Text fontWeight="semibold">No goals set</Text>
            <Text fontSize="sm">Set nutrition goals in your preferences to track progress.</Text>
          </VStack>
        </Alert>
      ) : (
        <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
          {Object.entries(goalsProgress.progress).map(([nutrient, progress]) => (
            <Card key={nutrient}>
              <CardHeader>
                <HStack justify="space-between">
                  <HStack spacing={2}>
                    <Icon as={FiTarget} color="blue.500" />
                    <Text fontWeight="semibold">
                      {getNutrientDisplayName(nutrient)}
                    </Text>
                  </HStack>
                  <HStack spacing={2}>
                    {getStatusIcon(progress.status)}
                    <Badge colorScheme={getStatusColor(progress.status)}>
                      {progress.status.replace('_', ' ').toUpperCase()}
                    </Badge>
                  </HStack>
                </HStack>
              </CardHeader>
              <CardBody>
                <VStack spacing={4} align="stretch">
                  {/* Current vs Target */}
                  <HStack justify="space-between">
                    <Text fontSize="sm" color={textColor}>Current</Text>
                    <Text fontWeight="bold" fontSize="lg">
                      {progress.current.toFixed(0)}{getNutrientUnit(nutrient)}
                    </Text>
                  </HStack>
                  
                  <HStack justify="space-between">
                    <Text fontSize="sm" color={textColor}>Target</Text>
                    <Text fontSize="lg">
                      {progress.target.toFixed(0)}{getNutrientUnit(nutrient)}
                    </Text>
                  </HStack>
                  
                  {/* Progress Bar */}
                  <Box>
                    <HStack justify="space-between" mb={2}>
                      <Text fontSize="sm" color={textColor}>Progress</Text>
                      <Text fontSize="sm" fontWeight="semibold">
                        {progress.progress_percent.toFixed(0)}%
                      </Text>
                    </HStack>
                    <Progress 
                      value={progress.progress_percent} 
                      colorScheme={getStatusColor(progress.status)}
                      size="lg"
                    />
                  </Box>
                  
                  {/* Range Info */}
                  <Box p={3} bg={bgColor} borderRadius="md" border="1px" borderColor={borderColor}>
                    <VStack spacing={1} align="stretch">
                      <Text fontSize="xs" color={textColor} textAlign="center">
                        Target Range
                      </Text>
                      <Text fontSize="sm" textAlign="center" fontWeight="semibold">
                        {progress.min.toFixed(0)} - {progress.max.toFixed(0)} {getNutrientUnit(nutrient)}
                      </Text>
                    </VStack>
                  </Box>
                  
                  {/* Status Message */}
                  <Text fontSize="xs" color={textColor} textAlign="center">
                    {progress.status === 'on_track' && 'Great job! You\'re meeting your target.'}
                    {progress.status === 'below_target' && 'You\'re below your target. Consider increasing intake.'}
                    {progress.status === 'above_target' && 'You\'re above your target. Consider reducing intake.'}
                  </Text>
                </VStack>
              </CardBody>
            </Card>
          ))}
        </SimpleGrid>
      )}

      {/* Quick Tips */}
      <Card>
        <CardHeader>
          <Heading size="sm">Tips for Better Goal Achievement</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={3} align="stretch">
            <HStack align="start" spacing={3}>
              <Icon as={FiTarget} color="blue.500" />
              <Text fontSize="sm">
                Set realistic, achievable goals based on your lifestyle and preferences
              </Text>
            </HStack>
            
            <HStack align="start" spacing={3}>
              <Icon as={FiTrendingUp} color="green.500" />
              <Text fontSize="sm">
                Track your meals consistently to get accurate progress data
              </Text>
            </HStack>
            
            <HStack align="start" spacing={3}>
              <Icon as={FiCheck} color="purple.500" />
              <Text fontSize="sm">
                Use meal planning to help you stay on track with your goals
              </Text>
            </HStack>
            
            <HStack align="start" spacing={3}>
              <Icon as={FiAward} color="orange.500" />
              <Text fontSize="sm">
                Celebrate small wins and adjust goals as needed
              </Text>
            </HStack>
          </VStack>
        </CardBody>
      </Card>
    </VStack>
  );
};

export default GoalsProgressChart;
