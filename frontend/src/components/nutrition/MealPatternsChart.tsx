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
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Progress,
  Badge,
  Icon,
  useColorModeValue,
  Alert,
  AlertIcon
} from '@chakra-ui/react';
import { 
  FiClock, 
  FiUsers, 
  FiCoffee, 
  FiSun, 
  FiMoon,
  FiTrendingUp,
  FiTarget
} from 'react-icons/fi';
import type { MealPattern } from '../../services/nutritionAnalyticsService';

interface MealPatternsChartProps {
  mealPatterns: MealPattern;
}

const MealPatternsChart: React.FC<MealPatternsChartProps> = ({ mealPatterns }) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.400');

  const getMealIcon = (mealType: string) => {
    switch (mealType.toLowerCase()) {
      case 'breakfast':
        return <Icon as={FiCoffee} color="orange.500" />;
      case 'lunch':
        return <Icon as={FiSun} color="yellow.500" />;
      case 'dinner':
        return <Icon as={FiMoon} color="blue.500" />;
      case 'snack':
        return <Icon as={FiUsers} color="green.500" />;
      default:
        return <Icon as={FiClock} color="gray.500" />;
    }
  };

  const getMealColor = (mealType: string) => {
    switch (mealType.toLowerCase()) {
      case 'breakfast':
        return 'orange';
      case 'lunch':
        return 'yellow';
      case 'dinner':
        return 'blue';
      case 'snack':
        return 'green';
      default:
        return 'gray';
    }
  };

  const formatTime = (timeString?: string) => {
    if (!timeString) return 'N/A';
    return timeString;
  };

  const getConsistencyColor = (percentage: number) => {
    if (percentage >= 80) return 'green';
    if (percentage >= 60) return 'yellow';
    return 'red';
  };

  const getConsistencyText = (percentage: number) => {
    if (percentage >= 80) return 'Excellent';
    if (percentage >= 60) return 'Good';
    if (percentage >= 40) return 'Fair';
    return 'Needs Improvement';
  };

  if (mealPatterns.total_meals_logged === 0) {
    return (
      <VStack spacing={6} align="stretch">
        <Heading size="md">Meal Patterns</Heading>
        <Alert status="info" borderRadius="lg">
          <AlertIcon />
          <VStack align="start" spacing={2}>
            <Text fontWeight="semibold">No meal data available</Text>
            <Text fontSize="sm">Start logging your meals to see pattern analysis.</Text>
          </VStack>
        </Alert>
      </VStack>
    );
  }

  return (
    <VStack spacing={6} align="stretch">
      <Heading size="md">Meal Patterns & Timing</Heading>
      
      {/* Overview Stats */}
      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={4}>
        <Card>
          <CardBody textAlign="center">
            <Stat>
              <StatLabel>Total Meals</StatLabel>
              <StatNumber>{mealPatterns.total_meals_logged}</StatNumber>
              <StatHelpText>logged</StatHelpText>
            </Stat>
          </CardBody>
        </Card>
        
        <Card>
          <CardBody textAlign="center">
            <Stat>
              <StatLabel>Avg Meals/Day</StatLabel>
              <StatNumber>{mealPatterns.avg_meals_per_day}</StatNumber>
              <StatHelpText>per day</StatHelpText>
            </Stat>
          </CardBody>
        </Card>
        
        <Card>
          <CardBody textAlign="center">
            <Stat>
              <StatLabel>Breakfast Consistency</StatLabel>
              <StatNumber>
                <Badge colorScheme={getConsistencyColor(mealPatterns.meal_consistency.breakfast)}>
                  {mealPatterns.meal_consistency.breakfast.toFixed(0)}%
                </Badge>
              </StatNumber>
              <StatHelpText>{getConsistencyText(mealPatterns.meal_consistency.breakfast)}</StatHelpText>
            </Stat>
          </CardBody>
        </Card>
        
        <Card>
          <CardBody textAlign="center">
            <Stat>
              <StatLabel>Dinner Consistency</StatLabel>
              <StatNumber>
                <Badge colorScheme={getConsistencyColor(mealPatterns.meal_consistency.dinner)}>
                  {mealPatterns.meal_consistency.dinner.toFixed(0)}%
                </Badge>
              </StatNumber>
              <StatHelpText>{getConsistencyText(mealPatterns.meal_consistency.dinner)}</StatHelpText>
            </Stat>
          </CardBody>
        </Card>
      </SimpleGrid>

      {/* Meal Timing */}
      <Card>
        <CardHeader>
          <HStack spacing={2}>
            <Icon as={FiClock} color="blue.500" />
            <Heading size="sm">Average Meal Times</Heading>
          </HStack>
        </CardHeader>
        <CardBody>
          <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
            <VStack spacing={2}>
              <HStack spacing={2}>
                {getMealIcon('breakfast')}
                <Text fontWeight="semibold">Breakfast</Text>
              </HStack>
              <Text fontSize="lg" fontWeight="bold">
                {formatTime(mealPatterns.meal_timing.breakfast_avg_time)}
              </Text>
            </VStack>
            
            <VStack spacing={2}>
              <HStack spacing={2}>
                {getMealIcon('lunch')}
                <Text fontWeight="semibold">Lunch</Text>
              </HStack>
              <Text fontSize="lg" fontWeight="bold">
                {formatTime(mealPatterns.meal_timing.lunch_avg_time)}
              </Text>
            </VStack>
            
            <VStack spacing={2}>
              <HStack spacing={2}>
                {getMealIcon('dinner')}
                <Text fontWeight="semibold">Dinner</Text>
              </HStack>
              <Text fontSize="lg" fontWeight="bold">
                {formatTime(mealPatterns.meal_timing.dinner_avg_time)}
              </Text>
            </VStack>
          </SimpleGrid>
        </CardBody>
      </Card>

      {/* Meal Consistency */}
      <Card>
        <CardHeader>
          <HStack spacing={2}>
            <Icon as={FiTrendingUp} color="green.500" />
            <Heading size="sm">Meal Consistency</Heading>
          </HStack>
        </CardHeader>
        <CardBody>
          <VStack spacing={4} align="stretch">
            {Object.entries(mealPatterns.meal_consistency).map(([mealType, percentage]) => (
              <Box key={mealType}>
                <HStack justify="space-between" mb={2}>
                  <HStack spacing={2}>
                    {getMealIcon(mealType)}
                    <Text fontWeight="semibold" textTransform="capitalize">
                      {mealType}
                    </Text>
                  </HStack>
                  <Text fontSize="sm" color={textColor}>
                    {percentage.toFixed(1)}%
                  </Text>
                </HStack>
                <Progress 
                  value={percentage} 
                  colorScheme={getConsistencyColor(percentage)}
                  size="lg"
                />
                <Text fontSize="xs" color={textColor} mt={1}>
                  {getConsistencyText(percentage)}
                </Text>
              </Box>
            ))}
          </VStack>
        </CardBody>
      </Card>

      {/* Calorie Distribution */}
      {Object.keys(mealPatterns.calorie_distribution).length > 0 && (
        <Card>
          <CardHeader>
            <HStack spacing={2}>
              <Icon as={FiTarget} color="purple.500" />
              <Heading size="sm">Calorie Distribution by Meal</Heading>
            </HStack>
          </CardHeader>
          <CardBody>
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
              {Object.entries(mealPatterns.calorie_distribution).map(([mealType, data]) => (
                <Box key={mealType} p={4} bg={bgColor} borderRadius="md" border="1px" borderColor={borderColor}>
                  <VStack spacing={2} align="stretch">
                    <HStack justify="space-between">
                      <HStack spacing={2}>
                        {getMealIcon(mealType)}
                        <Text fontWeight="semibold" textTransform="capitalize">
                          {mealType}
                        </Text>
                      </HStack>
                      <Badge colorScheme={getMealColor(mealType)}>
                        {data.percentage.toFixed(0)}%
                      </Badge>
                    </HStack>
                    
                    <Text fontSize="lg" fontWeight="bold">
                      {data.avg_calories.toFixed(0)} calories
                    </Text>
                    
                    <Text fontSize="sm" color={textColor}>
                      {data.total_meals} meals logged
                    </Text>
                  </VStack>
                </Box>
              ))}
            </SimpleGrid>
          </CardBody>
        </Card>
      )}

      {/* Meal Type Frequency */}
      {Object.keys(mealPatterns.meal_type_frequency).length > 0 && (
        <Card>
          <CardHeader>
            <Heading size="sm">Meal Type Frequency</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={3} align="stretch">
              {Object.entries(mealPatterns.meal_type_frequency)
                .sort(([,a], [,b]) => b - a)
                .map(([mealType, count]) => (
                <HStack key={mealType} justify="space-between">
                  <HStack spacing={2}>
                    {getMealIcon(mealType)}
                    <Text textTransform="capitalize">{mealType}</Text>
                  </HStack>
                  <HStack spacing={2}>
                    <Text fontWeight="semibold">{count}</Text>
                    <Text fontSize="sm" color={textColor}>meals</Text>
                  </HStack>
                </HStack>
              ))}
            </VStack>
          </CardBody>
        </Card>
      )}
    </VStack>
  );
};

export default MealPatternsChart;
