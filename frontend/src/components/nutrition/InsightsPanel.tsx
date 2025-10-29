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
  Icon,
  Badge,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Divider,
  List,
  ListItem,
  ListIcon,
  useColorModeValue
} from '@chakra-ui/react';
import { 
  FiAlertTriangle, 
  FiCheck, 
  FiInfo, 
  FiTarget,
  FiTrendingUp,
  FiTrendingDown,
  FiMinus
} from 'react-icons/fi';
import type { NutritionInsights, NutritionInsight } from '../../services/nutritionAnalyticsService';

interface InsightsPanelProps {
  insights: NutritionInsights;
}

const InsightsPanel: React.FC<InsightsPanelProps> = ({ insights }) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.400');

  const getInsightIcon = (type: string) => {
    switch (type) {
      case 'warning':
        return <Icon as={FiAlertTriangle} color="orange.500" />;
      case 'success':
        return <Icon as={FiCheck} color="green.500" />;
      default:
        return <Icon as={FiInfo} color="blue.500" />;
    }
  };

  const getInsightColor = (type: string) => {
    switch (type) {
      case 'warning':
        return 'orange';
      case 'success':
        return 'green';
      default:
        return 'blue';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'red';
      case 'medium':
        return 'yellow';
      default:
        return 'gray';
    }
  };

  const getTrendIcon = (change: number) => {
    if (change > 0) return <Icon as={FiTrendingUp} color="green.500" />;
    if (change < 0) return <Icon as={FiTrendingDown} color="red.500" />;
    return <Icon as={FiMinus} color="gray.500" />;
  };

  return (
    <VStack spacing={6} align="stretch">
      <Heading size="md">Nutrition Insights & Recommendations</Heading>
      
      {/* Summary Stats */}
      <Card>
        <CardHeader>
          <Heading size="sm">Nutrition Summary</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={4} align="stretch">
            <HStack justify="space-between">
              <Text fontSize="sm" color={textColor}>Average Daily Calories</Text>
              <Text fontWeight="semibold">{insights.summary.avg_calories.toFixed(0)}</Text>
            </HStack>
            
            <HStack justify="space-between">
              <Text fontSize="sm" color={textColor}>Average Daily Protein</Text>
              <Text fontWeight="semibold">{insights.summary.avg_protein.toFixed(1)}g</Text>
            </HStack>
            
            <HStack justify="space-between">
              <Text fontSize="sm" color={textColor}>Average Daily Carbs</Text>
              <Text fontWeight="semibold">{insights.summary.avg_carbs.toFixed(1)}g</Text>
            </HStack>
            
            <HStack justify="space-between">
              <Text fontSize="sm" color={textColor}>Average Daily Fat</Text>
              <Text fontWeight="semibold">{insights.summary.avg_fat.toFixed(1)}g</Text>
            </HStack>
            
            <HStack justify="space-between">
              <Text fontSize="sm" color={textColor}>Average Daily Fiber</Text>
              <Text fontWeight="semibold">{insights.summary.avg_fiber.toFixed(1)}g</Text>
            </HStack>
            
            <HStack justify="space-between">
              <Text fontSize="sm" color={textColor}>Average Daily Sodium</Text>
              <Text fontWeight="semibold">{insights.summary.avg_sodium.toFixed(0)}mg</Text>
            </HStack>
            
            <HStack justify="space-between">
              <Text fontSize="sm" color={textColor}>Days Tracked</Text>
              <Text fontWeight="semibold">{insights.summary.total_days}</Text>
            </HStack>
          </VStack>
        </CardBody>
      </Card>

      {/* Insights */}
      {insights.insights.length === 0 ? (
        <Alert status="info" borderRadius="lg">
          <AlertIcon />
          <VStack align="start" spacing={2}>
            <AlertTitle>No insights available</AlertTitle>
            <AlertDescription>
              Keep logging your meals to receive personalized nutrition insights and recommendations.
            </AlertDescription>
          </VStack>
        </Alert>
      ) : (
        <VStack spacing={4} align="stretch">
          <Heading size="sm">Personalized Insights</Heading>
          
          {insights.insights.map((insight, index) => (
            <Alert 
              key={index}
              status={insight.type === 'warning' ? 'warning' : insight.type === 'success' ? 'success' : 'info'}
              borderRadius="lg"
            >
              <AlertIcon />
              <Box flex="1">
                <AlertTitle>
                  <HStack spacing={2}>
                    {getInsightIcon(insight.type)}
                    <Text>{insight.title}</Text>
                    <Badge colorScheme={getPriorityColor(insight.priority)} size="sm">
                      {insight.priority.toUpperCase()}
                    </Badge>
                  </HStack>
                </AlertTitle>
                <AlertDescription mt={2}>
                  {insight.message}
                </AlertDescription>
              </Box>
            </Alert>
          ))}
        </VStack>
      )}

      {/* Recommendations */}
      {insights.recommendations.length > 0 && (
        <Card>
          <CardHeader>
            <HStack spacing={2}>
              <Icon as={FiTarget} color="blue.500" />
              <Heading size="sm">Recommendations</Heading>
            </HStack>
          </CardHeader>
          <CardBody>
            <List spacing={3}>
              {insights.recommendations.map((recommendation, index) => (
                <ListItem key={index}>
                  <HStack align="start" spacing={3}>
                    <ListIcon as={FiTarget} color="blue.500" />
                    <Text fontSize="sm">{recommendation}</Text>
                  </HStack>
                </ListItem>
              ))}
            </List>
          </CardBody>
        </Card>
      )}

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <Heading size="sm">Quick Actions</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={3} align="stretch">
            <Text fontSize="sm" color={textColor}>
              Based on your nutrition patterns, here are some quick actions you can take:
            </Text>
            
            <List spacing={2}>
              <ListItem>
                <HStack align="start" spacing={3}>
                  <ListIcon as={FiCheck} color="green.500" />
                  <Text fontSize="sm">Log your meals consistently to get better insights</Text>
                </HStack>
              </ListItem>
              
              <ListItem>
                <HStack align="start" spacing={3}>
                  <ListIcon as={FiTarget} color="blue.500" />
                  <Text fontSize="sm">Set specific nutrition goals in your preferences</Text>
                </HStack>
              </ListItem>
              
              <ListItem>
                <HStack align="start" spacing={3}>
                  <ListIcon as={FiTrendingUp} color="purple.500" />
                  <Text fontSize="sm">Use meal planning to maintain consistent nutrition</Text>
                </HStack>
              </ListItem>
            </List>
          </VStack>
        </CardBody>
      </Card>
    </VStack>
  );
};

export default InsightsPanel;
