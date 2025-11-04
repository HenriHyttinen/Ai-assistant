import React, { useState } from 'react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  VStack,
  HStack,
  Text,
  FormControl,
  FormLabel,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Textarea,
  Button,
  useToast,
  Icon,
  useColorModeValue,
  Alert,
  AlertIcon,
  Divider,
  SimpleGrid,
  Badge,
  Box
} from '@chakra-ui/react';
import { 
  FiTarget, 
  FiTrendingUp, 
  FiCalendar,
  FiStar,
  FiHeart
} from 'react-icons/fi';
import nutritionGoalsService from '../../services/nutritionGoalsService';

interface LogProgressModalProps {
  isOpen: boolean;
  onClose: () => void;
  goalId: number;
  goalName: string;
  targetValue: number;
  unit: string;
  onProgressLogged: () => void;
}

const LogProgressModal: React.FC<LogProgressModalProps> = ({
  isOpen,
  onClose,
  goalId,
  goalName,
  targetValue,
  unit,
  onProgressLogged
}) => {
  const [progressData, setProgressData] = useState({
    achieved_value: 0,
    notes: '',
    difficulty_rating: undefined as number | undefined,
    mood_rating: undefined as number | undefined
  });
  const [logging, setLogging] = useState(false);

  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.800');

  const handleInputChange = (field: string, value: any) => {
    setProgressData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleLogProgress = async () => {
    try {
      setLogging(true);
      
      await nutritionGoalsService.logProgress({
        goal_id: goalId,
        date: new Date().toISOString(),
        achieved_value: progressData.achieved_value,
        notes: progressData.notes || undefined,
        difficulty_rating: progressData.difficulty_rating || undefined,
        mood_rating: progressData.mood_rating || undefined
      });
      
      toast({
        title: "Progress Logged!",
        description: `Great job on your ${goalName} goal!`,
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      
      onProgressLogged();
      onClose();
      
      // Reset form
      setProgressData({
        achieved_value: 0,
        notes: '',
        difficulty_rating: undefined,
        mood_rating: undefined
      });
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to log progress",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLogging(false);
    }
  };

  const getProgressPercentage = () => {
    if (targetValue === 0) return 0;
    return Math.min((progressData.achieved_value / targetValue) * 100, 100);
  };

  const getProgressColor = () => {
    const percentage = getProgressPercentage();
    if (percentage >= 100) return 'green';
    if (percentage >= 80) return 'blue';
    if (percentage >= 50) return 'yellow';
    return 'red';
  };

  const getProgressMessage = () => {
    const percentage = getProgressPercentage();
    if (percentage >= 100) return "🎉 Goal achieved!";
    if (percentage >= 80) return "🔥 Almost there!";
    if (percentage >= 50) return "👍 Good progress!";
    if (percentage > 0) return "💪 Keep going!";
    return "Start logging your progress!";
  };

  const getUnitDisplay = (unit: string) => {
    switch (unit) {
      case 'cal':
        return 'calories';
      case 'g':
        return 'grams';
      case 'mg':
        return 'milligrams';
      case 'oz':
        return 'ounces';
      case 'lbs':
        return 'pounds';
      default:
        return unit;
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="md">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>
          <HStack spacing={3}>
            <Icon as={FiTarget} color="blue.500" />
            <VStack align="start" spacing={0}>
              <Text>Log Progress</Text>
              <Text fontSize="sm" color="gray.500">{goalName}</Text>
            </VStack>
          </HStack>
        </ModalHeader>
        <ModalCloseButton />
        
        <ModalBody>
          <VStack spacing={6} align="stretch">
            {/* Progress Summary */}
            <Alert status="info" borderRadius="lg">
              <AlertIcon />
              <VStack align="start" spacing={1}>
                <Text fontWeight="semibold">Today's Progress</Text>
                <Text fontSize="sm">
                  Target: {targetValue} {getUnitDisplay(unit)}
                </Text>
              </VStack>
            </Alert>

            {/* Value Input */}
            <FormControl isRequired>
              <FormLabel>How much did you achieve today?</FormLabel>
              <NumberInput
                value={typeof progressData.achieved_value === 'number' && !isNaN(progressData.achieved_value) ? progressData.achieved_value : ''}
                onChange={(_, value) => handleInputChange('achieved_value', typeof value === 'number' && !isNaN(value) ? value : 0)}
                min={0}
                precision={2}
                size="lg"
              >
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
              <Text fontSize="sm" color="gray.500" mt={1}>
                Enter your progress in {getUnitDisplay(unit)}
              </Text>
            </FormControl>

            {/* Progress Visualization */}
            {progressData.achieved_value > 0 && (
              <Box p={4} bg={bgColor} borderRadius="lg" border="1px" borderColor="gray.200">
                <VStack spacing={3} align="stretch">
                  <HStack justify="space-between">
                    <Text fontSize="sm" fontWeight="semibold">Progress</Text>
                    <Badge colorScheme={getProgressColor()} size="lg">
                      {getProgressPercentage().toFixed(0)}%
                    </Badge>
                  </HStack>
                  
                  <Box>
                    <HStack justify="space-between" mb={1}>
                      <Text fontSize="sm" color="gray.600">
                        {progressData.achieved_value} / {targetValue} {getUnitDisplay(unit)}
                      </Text>
                      <Text fontSize="sm" color="gray.600">
                        {targetValue - progressData.achieved_value > 0 
                          ? `${(targetValue - progressData.achieved_value).toFixed(0)} remaining`
                          : 'Goal achieved!'
                        }
                      </Text>
                    </HStack>
                    <Box
                      w="100%"
                      h="8px"
                      bg="gray.200"
                      borderRadius="full"
                      overflow="hidden"
                    >
                      <Box
                        w={`${Math.min(getProgressPercentage(), 100)}%`}
                        h="100%"
                        bg={`${getProgressColor()}.500`}
                        transition="width 0.3s ease"
                      />
                    </Box>
                  </Box>
                  
                  <Text fontSize="sm" textAlign="center" fontWeight="semibold" color={`${getProgressColor()}.600`}>
                    {getProgressMessage()}
                  </Text>
                </VStack>
              </Box>
            )}

            <Divider />

            {/* Additional Information */}
            <VStack spacing={4} align="stretch">
              <Text fontSize="md" fontWeight="semibold">Additional Information (Optional)</Text>
              
              <FormControl>
                <FormLabel>Notes about today's progress</FormLabel>
                <Textarea
                  value={progressData.notes}
                  onChange={(e) => handleInputChange('notes', e.target.value)}
                  placeholder="How did it go? Any challenges or successes?"
                  rows={3}
                />
              </FormControl>

              <SimpleGrid columns={2} spacing={4}>
                <FormControl>
                  <FormLabel>
                    <HStack spacing={1}>
                      <Icon as={FiStar} />
                      <Text>Difficulty (1-5)</Text>
                    </HStack>
                  </FormLabel>
                  <NumberInput
                    value={progressData.difficulty_rating !== undefined && typeof progressData.difficulty_rating === 'number' && !isNaN(progressData.difficulty_rating) ? progressData.difficulty_rating : ''}
                    onChange={(_, value) => handleInputChange('difficulty_rating', typeof value === 'number' && !isNaN(value) ? value : undefined)}
                    min={1}
                    max={5}
                  >
                    <NumberInputField placeholder="Rate difficulty" />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                  <Text fontSize="xs" color="gray.500">
                    1 = Very Easy, 5 = Very Hard
                  </Text>
                </FormControl>

                <FormControl>
                  <FormLabel>
                    <HStack spacing={1}>
                      <Icon as={FiHeart} />
                      <Text>Mood (1-5)</Text>
                    </HStack>
                  </FormLabel>
                  <NumberInput
                    value={progressData.mood_rating !== undefined && typeof progressData.mood_rating === 'number' && !isNaN(progressData.mood_rating) ? progressData.mood_rating : ''}
                    onChange={(_, value) => handleInputChange('mood_rating', typeof value === 'number' && !isNaN(value) ? value : undefined)}
                    min={1}
                    max={5}
                  >
                    <NumberInputField placeholder="Rate mood" />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                  <Text fontSize="xs" color="gray.500">
                    1 = Poor, 5 = Excellent
                  </Text>
                </FormControl>
              </SimpleGrid>
            </VStack>
          </VStack>
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            Cancel
          </Button>
          <Button
            colorScheme="blue"
            onClick={handleLogProgress}
            isLoading={logging}
            loadingText="Logging..."
            isDisabled={progressData.achieved_value <= 0}
          >
            Log Progress
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default LogProgressModal;







