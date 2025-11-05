import React, { useState, useEffect } from 'react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  VStack,
  HStack,
  FormControl,
  FormLabel,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Text,
  Divider,
  useToast,
  Grid,
  GridItem,
  Box,
  Badge
} from '@chakra-ui/react';

interface MicronutrientGoal {
  id: number;
  user_id: number;
  vitamin_d_target: number;
  vitamin_b12_target: number;
  iron_target: number;
  calcium_target: number;
  magnesium_target: number;
  vitamin_c_target: number;
  folate_target: number;
  zinc_target: number;
  potassium_target: number;
  fiber_target: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface MicronutrientGoalsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  currentGoals: MicronutrientGoal | null;
}

const MicronutrientGoalsModal: React.FC<MicronutrientGoalsModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  currentGoals
}) => {
  const [goals, setGoals] = useState({
    vitamin_d_target: 15.0,
    vitamin_b12_target: 2.4,
    iron_target: 18.0,
    calcium_target: 1000.0,
    magnesium_target: 400.0,
    vitamin_c_target: 90.0,
    folate_target: 400.0,
    zinc_target: 11.0,
    potassium_target: 3500.0,
    fiber_target: 25.0,
  });
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  useEffect(() => {
    if (currentGoals) {
      setGoals({
        vitamin_d_target: currentGoals.vitamin_d_target || 15.0,
        vitamin_b12_target: currentGoals.vitamin_b12_target || 2.4,
        iron_target: currentGoals.iron_target || 18.0,
        calcium_target: currentGoals.calcium_target || 1000.0,
        magnesium_target: currentGoals.magnesium_target || 400.0,
        vitamin_c_target: currentGoals.vitamin_c_target || 90.0,
        folate_target: currentGoals.folate_target || 400.0,
        zinc_target: currentGoals.zinc_target || 11.0,
        potassium_target: currentGoals.potassium_target || 3500.0,
        fiber_target: currentGoals.fiber_target || 25.0,
      });
    }
  }, [currentGoals]);

  const micronutrients = [
    { key: 'vitamin_d_target', name: 'Vitamin D', unit: 'mcg', description: 'Essential for bone health and immune function' },
    { key: 'vitamin_b12_target', name: 'Vitamin B12', unit: 'mcg', description: 'Important for nerve function and red blood cell formation' },
    { key: 'iron_target', name: 'Iron', unit: 'mg', description: 'Necessary for oxygen transport in blood' },
    { key: 'calcium_target', name: 'Calcium', unit: 'mg', description: 'Critical for bone and teeth health' },
    { key: 'magnesium_target', name: 'Magnesium', unit: 'mg', description: 'Supports muscle and nerve function' },
    { key: 'vitamin_c_target', name: 'Vitamin C', unit: 'mg', description: 'Antioxidant that supports immune system' },
    { key: 'folate_target', name: 'Folate', unit: 'mcg', description: 'Important for cell division and DNA synthesis' },
    { key: 'zinc_target', name: 'Zinc', unit: 'mg', description: 'Supports immune function and wound healing' },
    { key: 'potassium_target', name: 'Potassium', unit: 'mg', description: 'Essential for heart and muscle function' },
    { key: 'fiber_target', name: 'Fiber', unit: 'g', description: 'Supports digestive health and satiety' },
  ];

  const handleSubmit = async () => {
    setLoading(true);
    try {
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        console.error('No valid session found');
        return;
      }

      const response = await fetch('http://localhost:8000/micronutrients/goals', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify(goals)
      });

      if (response.ok) {
        toast({
          title: 'Goals updated successfully',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        onSuccess();
        onClose();
      } else {
        throw new Error('Failed to update goals');
      }
    } catch (error) {
      toast({
        title: 'Error updating goals',
        description: 'Please try again later',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setGoals({
      vitamin_d_target: 15.0,
      vitamin_b12_target: 2.4,
      iron_target: 18.0,
      calcium_target: 1000.0,
      magnesium_target: 400.0,
      vitamin_c_target: 90.0,
      folate_target: 400.0,
      zinc_target: 11.0,
      potassium_target: 3500.0,
      fiber_target: 25.0,
    });
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior="inside">
      <ModalOverlay />
      <ModalContent maxH="90vh">
        <ModalHeader>Set Micronutrient Goals</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack spacing={6} align="stretch">
            <Text fontSize="sm" color="gray.600">
              Set your daily micronutrient targets. These values are based on general recommendations for adults.
              Consult with a healthcare provider for personalized recommendations.
            </Text>

            <Grid templateColumns="repeat(2, 1fr)" gap={4}>
              {micronutrients.map((nutrient) => (
                <GridItem key={nutrient.key}>
                  <Box p={4} borderWidth={1} borderRadius="md" bg="gray.50">
                    <VStack spacing={3} align="stretch">
                      <HStack justify="space-between">
                        <Text fontWeight="semibold">{nutrient.name}</Text>
                        <Badge colorScheme="blue">{nutrient.unit}</Badge>
                      </HStack>
                      
                      <Text fontSize="sm" color="gray.600">
                        {nutrient.description}
                      </Text>
                      
                      <FormControl>
                        <FormLabel fontSize="sm">Daily Target</FormLabel>
                        <NumberInput
                          value={goals[nutrient.key as keyof typeof goals]}
                          onChange={(valueString, valueNumber) => {
                            if (!isNaN(valueNumber)) {
                              setGoals(prev => ({
                                ...prev,
                                [nutrient.key]: valueNumber
                              }));
                            }
                          }}
                          min={0}
                          precision={1}
                        >
                          <NumberInputField />
                          <NumberInputStepper>
                            <NumberIncrementStepper />
                            <NumberDecrementStepper />
                          </NumberInputStepper>
                        </NumberInput>
                      </FormControl>
                    </VStack>
                  </Box>
                </GridItem>
              ))}
            </Grid>

            <Divider />

            <Box p={4} bg="blue.50" borderRadius="md">
              <Text fontSize="sm" fontWeight="semibold" color="blue.800" mb={2}>
                Important Notes:
              </Text>
              <VStack spacing={1} align="start">
                <Text fontSize="sm" color="blue.700">
                  • These are general recommendations and may vary based on age, gender, and health conditions
                </Text>
                <Text fontSize="sm" color="blue.700">
                  • Consult with a healthcare provider for personalized recommendations
                </Text>
                <Text fontSize="sm" color="blue.700">
                  • Some micronutrients have different requirements for men and women
                </Text>
              </VStack>
            </Box>
          </VStack>
        </ModalBody>

        <ModalFooter>
          <HStack spacing={3}>
            <Button variant="outline" onClick={handleReset}>
              Reset to Defaults
            </Button>
            <Button variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button
              colorScheme="blue"
              onClick={handleSubmit}
              isLoading={loading}
              loadingText="Saving..."
            >
              Save Goals
            </Button>
          </HStack>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default MicronutrientGoalsModal;
