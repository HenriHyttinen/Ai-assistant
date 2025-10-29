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
  FiTrendingUp, 
  FiTrendingDown, 
  FiMinus,
  FiTarget,
  FiBarChart
} from 'react-icons/fi';
import type { NutritionTrends, NutritionTrend } from '../../services/nutritionAnalyticsService';

interface TrendChartProps {
  trends: NutritionTrends;
}

const TrendChart: React.FC<TrendChartProps> = ({ trends }) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.400');

  const getTrendIcon = (direction: string) => {
    switch (direction) {
      case 'increasing':
        return <Icon as={FiTrendingUp} color="green.500" />;
      case 'decreasing':
        return <Icon as={FiTrendingDown} color="red.500" />;
      default:
        return <Icon as={FiMinus} color="gray.500" />;
    }
  };

  const getTrendColor = (direction: string) => {
    switch (direction) {
      case 'increasing':
        return 'green';
      case 'decreasing':
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
      case 'carbs':
      case 'fat':
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
      case 'carbs':
        return 'Carbohydrates';
      case 'fat':
        return 'Fat';
      case 'fiber':
        return 'Fiber';
      case 'sodium':
        return 'Sodium';
      default:
        return nutrient.charAt(0).toUpperCase() + nutrient.slice(1);
    }
  };

  if (trends.total_days_logged === 0) {
    return (
      <VStack spacing={6} align="stretch">
        <Heading size="md">Nutrition Trends</Heading>
        <Alert status="info" borderRadius="lg">
          <AlertIcon />
          <VStack align="start" spacing={2}>
            <Text fontWeight="semibold">No trend data available</Text>
            <Text fontSize="sm">Start logging your meals to see nutrition trends over time.</Text>
          </VStack>
        </Alert>
      </VStack>
    );
  }

  return (
    <VStack spacing={6} align="stretch">
      <Heading size="md">Nutrition Trends</Heading>
      
      {/* Summary Stats */}
      <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={4}>
        <Card>
          <CardBody textAlign="center">
            <Stat>
              <StatLabel>Days Tracked</StatLabel>
              <StatNumber>{trends.total_days_logged}</StatNumber>
              <StatHelpText>out of {trends.period_days} days</StatHelpText>
            </Stat>
          </CardBody>
        </Card>
        
        <Card>
          <CardBody textAlign="center">
            <Stat>
              <StatLabel>Avg Calories</StatLabel>
              <StatNumber>{trends.summary.avg_calories.toFixed(0)}</StatNumber>
              <StatHelpText>per day</StatHelpText>
            </Stat>
          </CardBody>
        </Card>
        
        <Card>
          <CardBody textAlign="center">
            <Stat>
              <StatLabel>Avg Protein</StatLabel>
              <StatNumber>{trends.summary.avg_protein.toFixed(1)}g</StatNumber>
              <StatHelpText>per day</StatHelpText>
            </Stat>
          </CardBody>
        </Card>
        
        <Card>
          <CardBody textAlign="center">
            <Stat>
              <StatLabel>Avg Fiber</StatLabel>
              <StatNumber>{trends.summary.avg_fiber.toFixed(1)}g</StatNumber>
              <StatHelpText>per day</StatHelpText>
            </Stat>
          </CardBody>
        </Card>
      </SimpleGrid>

      {/* Individual Trends */}
      {Object.keys(trends.trends).length === 0 ? (
        <Alert status="info" borderRadius="lg">
          <AlertIcon />
          <VStack align="start" spacing={2}>
            <Text fontWeight="semibold">No trend data available</Text>
            <Text fontSize="sm">Keep logging your meals to see trend analysis.</Text>
          </VStack>
        </Alert>
      ) : (
        <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
          {Object.entries(trends.trends).map(([nutrient, trend]) => (
            <Card key={nutrient}>
              <CardHeader>
                <HStack justify="space-between">
                  <HStack spacing={2}>
                    <Icon as={FiBarChart} color="blue.500" />
                    <Text fontWeight="semibold">
                      {getNutrientDisplayName(nutrient)}
                    </Text>
                  </HStack>
                  <HStack spacing={2}>
                    {getTrendIcon(trend.direction)}
                    <Badge colorScheme={getTrendColor(trend.direction)}>
                      {trend.direction}
                    </Badge>
                  </HStack>
                </HStack>
              </CardHeader>
              <CardBody>
                <VStack spacing={4} align="stretch">
                  {/* Current vs Previous */}
                  <HStack justify="space-between">
                    <Text fontSize="sm" color={textColor}>Current Average</Text>
                    <Text fontWeight="bold" fontSize="lg">
                      {trend.current_avg.toFixed(1)}{getNutrientUnit(nutrient)}
                    </Text>
                  </HStack>
                  
                  <HStack justify="space-between">
                    <Text fontSize="sm" color={textColor}>Previous Average</Text>
                    <Text fontSize="lg">
                      {trend.previous_avg.toFixed(1)}{getNutrientUnit(nutrient)}
                    </Text>
                  </HStack>
                  
                  {/* Change Percentage */}
                  <Box p={3} bg={bgColor} borderRadius="md" border="1px" borderColor={borderColor}>
                    <HStack justify="space-between">
                      <Text fontSize="sm" color={textColor}>Change</Text>
                      <Text 
                        fontSize="lg" 
                        fontWeight="bold"
                        color={trend.change_percent > 0 ? 'green.500' : trend.change_percent < 0 ? 'red.500' : 'gray.500'}
                      >
                        {trend.change_percent > 0 ? '+' : ''}{trend.change_percent.toFixed(1)}%
                      </Text>
                    </HStack>
                  </Box>
                  
                  {/* Trend Strength */}
                  <Box>
                    <HStack justify="space-between" mb={2}>
                      <Text fontSize="sm" color={textColor}>Trend Strength</Text>
                      <Text fontSize="sm" fontWeight="semibold">
                        {Math.min(trend.strength * 10, 100).toFixed(0)}%
                      </Text>
                    </HStack>
                    <Progress 
                      value={Math.min(trend.strength * 10, 100)} 
                      colorScheme={getTrendColor(trend.direction)}
                      size="lg"
                    />
                  </Box>
                  
                  {/* Trend Description */}
                  <Text fontSize="xs" color={textColor} textAlign="center">
                    {trend.direction === 'increasing' && 'Your intake is trending upward'}
                    {trend.direction === 'decreasing' && 'Your intake is trending downward'}
                    {trend.direction === 'stable' && 'Your intake is relatively stable'}
                  </Text>
                </VStack>
              </CardBody>
            </Card>
          ))}
        </SimpleGrid>
      )}

      {/* Quick Insights */}
      <Card>
        <CardHeader>
          <HStack spacing={2}>
            <Icon as={FiTarget} color="purple.500" />
            <Heading size="sm">Quick Insights</Heading>
          </HStack>
        </CardHeader>
        <CardBody>
          <VStack spacing={3} align="stretch">
            <Text fontSize="sm" color={textColor}>
              Based on your {trends.total_days_logged} days of data:
            </Text>
            
            <HStack align="start" spacing={3}>
              <Icon as={FiTrendingUp} color="green.500" />
              <Text fontSize="sm">
                {Object.values(trends.trends).filter(t => t.direction === 'increasing').length} nutrients are trending upward
              </Text>
            </HStack>
            
            <HStack align="start" spacing={3}>
              <Icon as={FiTrendingDown} color="red.500" />
              <Text fontSize="sm">
                {Object.values(trends.trends).filter(t => t.direction === 'decreasing').length} nutrients are trending downward
              </Text>
            </HStack>
            
            <HStack align="start" spacing={3}>
              <Icon as={FiMinus} color="gray.500" />
              <Text fontSize="sm">
                {Object.values(trends.trends).filter(t => t.direction === 'stable').length} nutrients are stable
              </Text>
            </HStack>
          </VStack>
        </CardBody>
      </Card>
    </VStack>
  );
};

export default TrendChart;
