import React, { useState, useEffect } from 'react';
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
  Button,
  useColorModeValue,
  Spinner,
  Alert,
  AlertIcon
} from '@chakra-ui/react';
import { FiTarget } from 'react-icons/fi';
import nutritionGoalsService from '../../services/nutritionGoalsService';
import type { NutritionGoal } from '../../services/nutritionGoalsService';

interface GoalDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  goalId: number;
  onUpdate: () => void;
}

const GoalDetailsModal: React.FC<GoalDetailsModalProps> = ({
  isOpen,
  onClose,
  goalId,
  onUpdate
}) => {
  const [goal, setGoal] = useState<NutritionGoal | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && goalId) {
      loadGoalDetails();
    }
  }, [isOpen, goalId]);

  const loadGoalDetails = async () => {
    try {
      setLoading(true);
      const goalData = await nutritionGoalsService.getGoal(goalId);
      setGoal(goalData);
    } catch (error) {
      console.error('Error loading goal details:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>
          <HStack spacing={2}>
            <FiTarget />
            <Text>Goal Details</Text>
          </HStack>
        </ModalHeader>
        <ModalCloseButton />
        
        <ModalBody>
          {loading ? (
            <HStack justify="center" py={8}>
              <Spinner />
              <Text>Loading goal details...</Text>
            </HStack>
          ) : goal ? (
            <VStack spacing={4} align="stretch">
              <Text fontSize="lg" fontWeight="semibold">{goal.goal_name}</Text>
              <Text color="gray.600">{goal.description}</Text>
              <Text>Target: {goal.target_value} {goal.unit}</Text>
              <Text>Progress: {goal.progress_percentage.toFixed(0)}%</Text>
              <Text>Streak: {goal.streak_days} days</Text>
            </VStack>
          ) : (
            <Alert status="error">
              <AlertIcon />
              <Text>Failed to load goal details</Text>
            </Alert>
          )}
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            Close
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default GoalDetailsModal;
