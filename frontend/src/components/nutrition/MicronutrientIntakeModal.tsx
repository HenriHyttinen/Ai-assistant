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
  Badge,
  Input,
  Select
} from '@chakra-ui/react';
import { FiCalendar, FiSave } from 'react-icons/fi';

interface MicronutrientData {
  vitamin_d: number;
  vitamin_b12: number;
  iron: number;
  calcium: number;
  magnesium: number;
  vitamin_c: number;
  folate: number;
  zinc: number;
  potassium: number;
  fiber: number;
}

interface MicronutrientIntakeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
  todayIntake: MicronutrientData | null;
}

const MicronutrientIntakeModal: React.FC<MicronutrientIntakeModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
  todayIntake
}) => {
  const [intake, setIntake] = useState<MicronutrientData>({
    vitamin_d: 0,
    vitamin_b12: 0,
    iron: 0,
    calcium: 0,
    magnesium: 0,
    vitamin_c: 0,
    folate: 0,
    zinc: 0,
    potassium: 0,
    fiber: 0,
  });
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  useEffect(() => {
    if (todayIntake) {
      setIntake(todayIntake);
    } else {
      setIntake({
        vitamin_d: 0,
        vitamin_b12: 0,
        iron: 0,
        calcium: 0,
        magnesium: 0,
        vitamin_c: 0,
        folate: 0,
        zinc: 0,
        potassium: 0,
        fiber: 0,
      });
    }
  }, [todayIntake]);

  const micronutrients = [
    { key: 'vitamin_d', name: 'Vitamin D', unit: 'mcg', description: 'From sunlight, fatty fish, fortified foods' },
    { key: 'vitamin_b12', name: 'Vitamin B12', unit: 'mcg', description: 'From meat, fish, dairy, fortified cereals' },
    { key: 'iron', name: 'Iron', unit: 'mg', description: 'From red meat, spinach, lentils, fortified cereals' },
    { key: 'calcium', name: 'Calcium', unit: 'mg', description: 'From dairy, leafy greens, sardines, almonds' },
    { key: 'magnesium', name: 'Magnesium', unit: 'mg', description: 'From nuts, seeds, leafy greens, whole grains' },
    { key: 'vitamin_c', name: 'Vitamin C', unit: 'mg', description: 'From citrus fruits, bell peppers, strawberries' },
    { key: 'folate', name: 'Folate', unit: 'mcg', description: 'From leafy greens, legumes, fortified grains' },
    { key: 'zinc', name: 'Zinc', unit: 'mg', description: 'From meat, shellfish, nuts, dairy' },
    { key: 'potassium', name: 'Potassium', unit: 'mg', description: 'From bananas, sweet potatoes, spinach, beans' },
    { key: 'fiber', name: 'Fiber', unit: 'g', description: 'From whole grains, fruits, vegetables, legumes' },
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

      const response = await fetch('http://localhost:8000/micronutrients/intake', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify({
          date: new Date(selectedDate).toISOString(),
          ...intake
        })
      });

      if (response.ok) {
        toast({
          title: 'Intake logged successfully',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        onSuccess();
        onClose();
      } else {
        throw new Error('Failed to log intake');
      }
    } catch (error) {
      toast({
        title: 'Error logging intake',
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
    setIntake({
      vitamin_d: 0,
      vitamin_b12: 0,
      iron: 0,
      calcium: 0,
      magnesium: 0,
      vitamin_c: 0,
      folate: 0,
      zinc: 0,
      potassium: 0,
      fiber: 0,
    });
  };

  const getTotalIntake = () => {
    return Object.values(intake).reduce((sum, value) => sum + value, 0);
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior="inside">
      <ModalOverlay />
      <ModalContent maxH="90vh">
        <ModalHeader>
          <HStack>
            <FiCalendar />
            <Text>Log Micronutrient Intake</Text>
          </HStack>
        </ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack spacing={6} align="stretch">
            {/* Date Selection */}
            <FormControl>
              <FormLabel>Date</FormLabel>
              <Input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
                max={new Date().toISOString().split('T')[0]}
              />
            </FormControl>

            <Text fontSize="sm" color="gray.600">
              Log your daily micronutrient intake. You can estimate based on the foods you've consumed
              or use nutrition labels and databases for more accurate values.
            </Text>

            {/* Micronutrient Inputs */}
            <Grid templateColumns="repeat(2, 1fr)" gap={4}>
              {micronutrients.map((nutrient) => (
                <GridItem key={nutrient.key}>
                  <Box p={4} borderWidth={1} borderRadius="md" bg="gray.50">
                    <VStack spacing={3} align="stretch">
                      <HStack justify="space-between">
                        <Text fontWeight="semibold">{nutrient.name}</Text>
                        <Badge colorScheme="green">{nutrient.unit}</Badge>
                      </HStack>
                      
                      <Text fontSize="sm" color="gray.600">
                        {nutrient.description}
                      </Text>
                      
                      <FormControl>
                        <FormLabel fontSize="sm">Amount Consumed</FormLabel>
                        <NumberInput
                          value={intake[nutrient.key as keyof MicronutrientData]}
                          onChange={(valueString, valueNumber) => {
                            if (!isNaN(valueNumber)) {
                              setIntake(prev => ({
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

            {/* Summary */}
            <Box p={4} bg="green.50" borderRadius="md">
              <HStack justify="space-between">
                <Text fontWeight="semibold" color="green.800">
                  Total Micronutrients Logged:
                </Text>
                <Badge colorScheme="green" fontSize="md">
                  {getTotalIntake().toFixed(1)} units
                </Badge>
              </HStack>
            </Box>

            {/* Tips */}
            <Box p={4} bg="blue.50" borderRadius="md">
              <Text fontSize="sm" fontWeight="semibold" color="blue.800" mb={2}>
                Tips for Accurate Logging:
              </Text>
              <VStack spacing={1} align="start">
                <Text fontSize="sm" color="blue.700">
                  • Use nutrition labels on packaged foods
                </Text>
                <Text fontSize="sm" color="blue.700">
                  • Check online nutrition databases for fresh foods
                </Text>
                <Text fontSize="sm" color="blue.700">
                  • Consider cooking methods that may affect nutrient content
                </Text>
                <Text fontSize="sm" color="blue.700">
                  • Log throughout the day for better accuracy
                </Text>
              </VStack>
            </Box>
          </VStack>
        </ModalBody>

        <ModalFooter>
          <HStack spacing={3}>
            <Button variant="outline" onClick={handleReset}>
              Clear All
            </Button>
            <Button variant="ghost" onClick={onClose}>
              Cancel
            </Button>
            <Button
              colorScheme="green"
              onClick={handleSubmit}
              isLoading={loading}
              loadingText="Saving..."
              leftIcon={<FiSave />}
            >
              Log Intake
            </Button>
          </HStack>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default MicronutrientIntakeModal;
