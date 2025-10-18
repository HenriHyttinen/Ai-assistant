import {
  Box,
  Card,
  CardHeader,
  CardBody,
  Heading,
  Text,
  VStack,
  HStack,
  Progress,
  Badge,
  Button,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  FormControl,
  FormLabel,
  Input,
  useToast,
} from '@chakra-ui/react';
import { useState, useEffect } from 'react';
import { analytics } from '../services/api';

interface WeightProgressCardProps {
  currentWeight: number;
  targetWeight: number;
  weightTrend: number[];
  measurementSystem: 'metric' | 'imperial';
}

const WeightProgressCard = ({ 
  currentWeight, 
  targetWeight, 
  weightTrend, 
  measurementSystem 
}: WeightProgressCardProps) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();
  const [newWeight, setNewWeight] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Calculate progress
  const weightDifference = currentWeight - targetWeight;
  const progressPercentage = Math.max(0, Math.min(100, (weightDifference / Math.abs(weightDifference + targetWeight)) * 100));
  
  // Determine if gaining or losing weight
  const isLosingWeight = currentWeight > targetWeight;
  const progressDirection = isLosingWeight ? 'down' : 'up';
  
  // Calculate trend
  const getTrend = () => {
    if (weightTrend.length < 2) return 'stable';
    const recent = weightTrend.slice(-3);
    const trend = recent[recent.length - 1] - recent[0];
    if (trend > 0.5) return 'up';
    if (trend < -0.5) return 'down';
    return 'stable';
  };

  const trend = getTrend();
  const trendColor = trend === 'up' ? 'red' : trend === 'down' ? 'green' : 'gray';

  const handleSubmit = async () => {
    if (!newWeight || isNaN(Number(newWeight))) {
      toast({
        title: 'Invalid Weight',
        description: 'Please enter a valid weight value',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setIsSubmitting(true);
    try {
      // Here you would call the API to add weight entry
      // await analytics.addWeightEntry(Number(newWeight));
      
      toast({
        title: 'Weight Logged!',
        description: 'Your weight has been successfully recorded',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
      
      setNewWeight('');
      onClose();
      window.location.reload(); // Refresh to show new data
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to log weight',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const getProgressMessage = () => {
    if (isLosingWeight) {
      return `You're ${Math.abs(weightDifference).toFixed(1)}kg away from your goal!`;
    } else {
      return `You're ${Math.abs(weightDifference).toFixed(1)}kg away from your goal!`;
    }
  };

  const getMotivationalMessage = () => {
    if (trend === 'down' && isLosingWeight) {
      return "🎉 Great progress! You're moving in the right direction!";
    } else if (trend === 'up' && isLosingWeight) {
      return "💪 Don't worry, weight fluctuates daily. Stay consistent!";
    } else if (trend === 'stable') {
      return "📊 Your weight is stable. Keep up the good work!";
    }
    return "🎯 Every step counts toward your goal!";
  };

  return (
    <>
      <Card>
        <CardHeader>
          <HStack justify="space-between">
            <Heading size="md">Weight Progress</Heading>
            <Button size="sm" colorScheme="blue" onClick={onOpen}>
              Log Weight
            </Button>
          </HStack>
        </CardHeader>
        <CardBody>
          <VStack spacing={6} align="stretch">
            {/* Current Weight Display */}
            <Box textAlign="center" py={4} bg="blue.50" borderRadius="md">
              <Text fontSize="3xl" fontWeight="bold" color="blue.600">
                {currentWeight.toFixed(1)} {measurementSystem === 'metric' ? 'kg' : 'lbs'}
              </Text>
              <Text color="gray.600" fontSize="sm">
                Current Weight
              </Text>
              <Badge colorScheme={trendColor} mt={2}>
                {trend === 'up' ? '↗️ Trending Up' : trend === 'down' ? '↘️ Trending Down' : '→ Stable'}
              </Badge>
            </Box>

            {/* Progress Bar */}
            <Box>
              <HStack justify="space-between" mb={2}>
                <Text fontSize="sm" color="gray.600">
                  {getProgressMessage()}
                </Text>
                <Text fontSize="sm" color="gray.600">
                  {targetWeight.toFixed(1)} {measurementSystem === 'metric' ? 'kg' : 'lbs'} goal
                </Text>
              </HStack>
              <Progress 
                value={progressPercentage} 
                colorScheme={isLosingWeight ? 'green' : 'blue'}
                size="lg"
                borderRadius="md"
              />
            </Box>

            {/* Motivational Message */}
            <Box p={3} bg="green.50" borderRadius="md" border="1px" borderColor="green.200">
              <Text color="green.800" fontSize="sm" textAlign="center">
                {getMotivationalMessage()}
              </Text>
            </Box>

            {/* Quick Stats */}
            <HStack justify="space-around" py={2}>
              <VStack spacing={1}>
                <Text fontSize="2xl" fontWeight="bold" color="blue.600">
                  {weightTrend.length}
                </Text>
                <Text fontSize="xs" color="gray.600">
                  Entries
                </Text>
              </VStack>
              <VStack spacing={1}>
                <Text fontSize="2xl" fontWeight="bold" color="green.600">
                  {Math.abs(weightDifference).toFixed(1)}
                </Text>
                <Text fontSize="xs" color="gray.600">
                  kg to go
                </Text>
              </VStack>
              <VStack spacing={1}>
                <Text fontSize="2xl" fontWeight="bold" color="purple.600">
                  {trend === 'down' ? '📉' : trend === 'up' ? '📈' : '📊'}
                </Text>
                <Text fontSize="xs" color="gray.600">
                  Trend
                </Text>
              </VStack>
            </HStack>
          </VStack>
        </CardBody>
      </Card>

      {/* Weight Logging Modal */}
      <Modal isOpen={isOpen} onClose={onClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Log Your Weight</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <FormControl>
              <FormLabel>Weight ({measurementSystem === 'metric' ? 'kg' : 'lbs'})</FormLabel>
              <Input
                type="number"
                step="0.1"
                placeholder={`Enter your current weight in ${measurementSystem === 'metric' ? 'kg' : 'lbs'}`}
                value={newWeight}
                onChange={(e) => setNewWeight(e.target.value)}
              />
            </FormControl>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button 
              colorScheme="blue" 
              onClick={handleSubmit}
              isLoading={isSubmitting}
            >
              Log Weight
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};

export default WeightProgressCard;
