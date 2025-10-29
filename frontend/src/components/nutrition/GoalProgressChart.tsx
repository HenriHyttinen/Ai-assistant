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
  Alert,
  AlertIcon,
  useColorModeValue
} from '@chakra-ui/react';
import type { GoalProgressSummary } from '../../services/nutritionGoalsService';

interface GoalProgressChartProps {
  goals: GoalProgressSummary[];
}

const GoalProgressChart: React.FC<GoalProgressChartProps> = ({ goals }) => {
  const bgColor = useColorModeValue('white', 'gray.800');

  if (goals.length === 0) {
    return (
      <Alert status="info" borderRadius="lg">
        <AlertIcon />
        <Text>No active goals to display progress for.</Text>
      </Alert>
    );
  }

  return (
    <VStack spacing={6} align="stretch">
      <Heading size="md">Progress Charts</Heading>
      
      <Card>
        <CardHeader>
          <Text fontSize="lg" fontWeight="semibold">Goal Progress Overview</Text>
        </CardHeader>
        <CardBody>
          <Text>Progress charts will be implemented here.</Text>
          <Text fontSize="sm" color="gray.500">
            This will show visual progress tracking for all your active goals.
          </Text>
        </CardBody>
      </Card>
    </VStack>
  );
};

export default GoalProgressChart;
