import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Button,
  Card,
  CardBody,
  CardHeader,
  FormControl,
  FormLabel,
  Input,
  Select,
  VStack,
  HStack,
  Text,
  Badge,
  Divider,
  useToast,
  useColorModeValue,
  Heading,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  IconButton,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  SimpleGrid
} from '@chakra-ui/react';
import { FiPlus, FiTrash2, FiEdit, FiSave, FiX } from 'react-icons/fi';

interface FoodEntry {
  id: string;
  food_name: string;
  quantity: number;
  unit: string;
  meal_type: string;
  calories: number;
  protein: number;
  carbs: number;
  fats: number;
  recipe_id?: string;
}

interface DailyLogData {
  log_date: string;
  total_calories: number;
  total_protein: number;
  total_carbs: number;
  total_fats: number;
  meal_count: number;
  entries: FoodEntry[];
}

const DailyLogging: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );
  const [entries, setEntries] = useState<FoodEntry[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingEntry, setEditingEntry] = useState<FoodEntry | null>(null);
  const [newEntry, setNewEntry] = useState<Partial<FoodEntry>>({
    food_name: '',
    quantity: 1,
    unit: 'serving',
    meal_type: 'breakfast',
    calories: 0,
    protein: 0,
    carbs: 0,
    fats: 0
  });
  
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();
  
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  
  const loadDailyLog = useCallback(async () => {
    try {
      setLoading(true);
      
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        toast({
          title: 'Please log in',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
        return;
      }
      
      const response = await fetch(
        `http://localhost:8000/daily-logging/daily-log/${selectedDate}`,
        {
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (response.ok) {
        const data: DailyLogData = await response.json();
        setEntries(data.entries || []);
      } else {
        setEntries([]);
      }
    } catch (error) {
      console.error('Error loading daily log:', error);
      toast({
        title: 'Error loading daily log',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  }, [selectedDate, toast]);
  
  useEffect(() => {
    loadDailyLog();
  }, [loadDailyLog]);
  
  // Listen for daily log updates from meal planning
  useEffect(() => {
    const handleDailyLogUpdate = (event: CustomEvent) => {
      const updatedDate = event.detail?.date;
      // If the updated date matches the selected date, refresh
      if (updatedDate && updatedDate === selectedDate) {
        loadDailyLog();
      }
    };
    
    window.addEventListener('dailyLogUpdated', handleDailyLogUpdate as EventListener);
    return () => {
      window.removeEventListener('dailyLogUpdated', handleDailyLogUpdate as EventListener);
    };
  }, [selectedDate, loadDailyLog]);
  
  const saveDailyLog = async () => {
    try {
      setLoading(true);
      
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        toast({
          title: 'Please log in',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
        return;
      }
      
      const requestData = {
        log_date: selectedDate,
        entries: entries.map(entry => ({
          food_name: entry.food_name,
          quantity: entry.quantity,
          unit: entry.unit,
          meal_type: entry.meal_type,
          calories: entry.calories,
          protein: entry.protein,
          carbs: entry.carbs,
          fats: entry.fats,
          recipe_id: entry.recipe_id
        }))
      };
      
      const response = await fetch(
        'http://localhost:8000/daily-logging/log-daily-intake',
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestData),
        }
      );
      
      if (response.ok) {
        toast({
          title: 'Daily log saved successfully',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        loadDailyLog();
      } else {
        throw new Error('Failed to save daily log');
      }
    } catch (error) {
      console.error('Error saving daily log:', error);
      toast({
        title: 'Error saving daily log',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const addFromMealPlan = async () => {
    try {
      setLoading(true);
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.access_token) {
        toast({ title: 'Please log in', status: 'warning', duration: 2500, isClosable: true });
        return;
      }
      // Get the latest plan for the selected date
      const planResp = await fetch(`http://localhost:8000/nutrition/meal-plans?date=${selectedDate}&limit=1`, {
        headers: { 'Authorization': `Bearer ${session.access_token}` }
      });
      if (!planResp.ok) {
        toast({ title: 'No meal plan for this date', status: 'info', duration: 2500, isClosable: true });
        return;
      }
      const plans = await planResp.json();
      if (!plans || plans.length === 0) {
        toast({ title: 'No meal plan for this date', status: 'info', duration: 2500, isClosable: true });
        return;
      }
      const planId = plans[0].id;
      // Log from meal plan to the selected date
      const logResp = await fetch(`http://localhost:8000/daily-logging/log-from-meal-plan?log_date=${selectedDate}&meal_plan_id=${planId}`, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${session.access_token}` }
      });
      if (logResp.ok) {
        toast({ title: 'Added from meal plan', status: 'success', duration: 2500, isClosable: true });
        await loadDailyLog();
      } else {
        const errText = await logResp.text();
        throw new Error(errText || 'Failed to add from meal plan');
      }
    } catch (e) {
      console.error('Add from meal plan failed:', e);
      toast({ title: 'Failed to add from meal plan', status: 'error', duration: 3000, isClosable: true });
    } finally {
      setLoading(false);
    }
  };
  
  const addEntry = () => {
    if (!newEntry.food_name || newEntry.calories === 0) {
      toast({
        title: 'Please fill in food name and calories',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }
    
    const entry: FoodEntry = {
      id: Date.now().toString(),
      food_name: newEntry.food_name!,
      quantity: newEntry.quantity || 1,
      unit: newEntry.unit || 'serving',
      meal_type: newEntry.meal_type || 'breakfast',
      calories: newEntry.calories || 0,
      protein: newEntry.protein || 0,
      carbs: newEntry.carbs || 0,
      fats: newEntry.fats || 0,
      recipe_id: newEntry.recipe_id
    };
    
    setEntries([...entries, entry]);
    setNewEntry({
      food_name: '',
      quantity: 1,
      unit: 'serving',
      meal_type: 'breakfast',
      calories: 0,
      protein: 0,
      carbs: 0,
      fats: 0
    });
    onClose();
  };
  
  const editEntry = (entry: FoodEntry) => {
    setEditingEntry(entry);
    onOpen();
  };
  
  const updateEntry = () => {
    if (!editingEntry) return;
    
    setEntries(entries.map(entry => 
      entry.id === editingEntry.id ? editingEntry : entry
    ));
    setEditingEntry(null);
    onClose();
  };
  
  const deleteEntry = async (entryId: string) => {
    try {
      setLoading(true);
      
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        toast({
          title: 'Please log in',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
        return;
      }
      
      const response = await fetch(
        `http://localhost:8000/daily-logging/daily-log-entry/${entryId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
            'Content-Type': 'application/json',
          },
        }
      );
      
      if (response.ok) {
        toast({
          title: 'Entry deleted successfully',
          status: 'success',
          duration: 2000,
          isClosable: true,
        });
        // Reload the log to reflect changes
        await loadDailyLog();
      } else {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to delete entry' }));
        throw new Error(errorData.detail || 'Failed to delete entry');
      }
    } catch (error) {
      console.error('Error deleting entry:', error);
      toast({
        title: 'Error deleting entry',
        description: (error as Error).message,
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };
  
  const getMealTypeColor = (mealType: string) => {
    switch (mealType) {
      case 'breakfast': return 'yellow';
      case 'lunch': return 'blue';
      case 'dinner': return 'purple';
      case 'snack': return 'green';
      default: return 'gray';
    }
  };
  
  const totalCalories = entries.reduce((sum, entry) => sum + entry.calories, 0);
  const totalProtein = entries.reduce((sum, entry) => sum + entry.protein, 0);
  const totalCarbs = entries.reduce((sum, entry) => sum + entry.carbs, 0);
  const totalFats = entries.reduce((sum, entry) => sum + entry.fats, 0);
  
  return (
    <Box p={6}>
      <Heading mb={6}>Daily Food Logging</Heading>
      
      {/* Date Selection */}
      <Card bg={cardBg} borderColor={borderColor} mb={6}>
        <CardBody>
          <HStack spacing={4}>
            <FormControl>
              <FormLabel>Select Date</FormLabel>
              <Input
                type="date"
                value={selectedDate}
                onChange={(e) => setSelectedDate(e.target.value)}
              />
            </FormControl>
            <Button
              colorScheme="blue"
              onClick={saveDailyLog}
              isLoading={loading}
              isDisabled={entries.length === 0}
            >
              Save Log
            </Button>
          </HStack>
        </CardBody>
      </Card>
      
      {/* Daily Summary */}
      <Card bg={cardBg} borderColor={borderColor} mb={6}>
        <CardHeader>
          <Heading size="md">Daily Summary - {selectedDate}</Heading>
        </CardHeader>
        <CardBody>
          <HStack spacing={8} wrap="wrap">
            <VStack key="calories" align="start">
              <Text fontSize="sm" color="gray.500">Total Calories</Text>
              <Text fontSize="2xl" fontWeight="bold">{totalCalories.toFixed(0)}</Text>
            </VStack>
            <VStack key="protein" align="start">
              <Text fontSize="sm" color="gray.500">Protein</Text>
              <Text fontSize="2xl" fontWeight="bold">{totalProtein.toFixed(1)}g</Text>
            </VStack>
            <VStack key="carbs" align="start">
              <Text fontSize="sm" color="gray.500">Carbs</Text>
              <Text fontSize="2xl" fontWeight="bold">{totalCarbs.toFixed(1)}g</Text>
            </VStack>
            <VStack key="fats" align="start">
              <Text fontSize="sm" color="gray.500">Fats</Text>
              <Text fontSize="2xl" fontWeight="bold">{totalFats.toFixed(1)}g</Text>
            </VStack>
            <VStack key="meals" align="start">
              <Text fontSize="sm" color="gray.500">Meals</Text>
              <Text fontSize="2xl" fontWeight="bold">{entries.length}</Text>
            </VStack>
          </HStack>
        </CardBody>
      </Card>
      
      {/* Quick Add Buttons */}
      <Card bg={cardBg} borderColor={borderColor} mb={6}>
        <CardHeader>
          <Heading size="md">Quick Add</Heading>
        </CardHeader>
        <CardBody>
          <HStack spacing={4} wrap="wrap">
            <Button
              leftIcon={<FiPlus />}
              colorScheme="green"
              onClick={onOpen}
              variant="outline"
            >
              Add Food Entry
            </Button>
            <Button
              leftIcon={<FiPlus />}
              colorScheme="blue"
              onClick={() => {/* Navigate to recipe search */}}
              variant="outline"
            >
              Add from Recipes
            </Button>
            <Button
              leftIcon={<FiPlus />}
              colorScheme="purple"
              onClick={addFromMealPlan}
              variant="outline"
            >
              Add from Meal Plan
            </Button>
          </HStack>
        </CardBody>
      </Card>
      
      {/* Daily Summary */}
      {entries.length > 0 && (
        <Card bg={cardBg} borderColor={borderColor} mb={4}>
          <CardBody>
            <VStack spacing={4}>
              <Heading size="md">Daily Summary</Heading>
              <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4} w="full">
                <VStack key="calories-summary">
                  <Text fontSize="sm" color="gray.600">Total Calories</Text>
                  <Text fontSize="2xl" fontWeight="bold" color="blue.500">
                    {totalCalories.toFixed(0)}
                  </Text>
                </VStack>
                <VStack key="protein-summary">
                  <Text fontSize="sm" color="gray.600">Protein</Text>
                  <Text fontSize="2xl" fontWeight="bold" color="green.500">
                    {totalProtein.toFixed(1)}g
                  </Text>
                </VStack>
                <VStack key="carbs-summary">
                  <Text fontSize="sm" color="gray.600">Carbs</Text>
                  <Text fontSize="2xl" fontWeight="bold" color="orange.500">
                    {totalCarbs.toFixed(1)}g
                  </Text>
                </VStack>
                <VStack key="fats-summary">
                  <Text fontSize="sm" color="gray.600">Fats</Text>
                  <Text fontSize="2xl" fontWeight="bold" color="purple.500">
                    {totalFats.toFixed(1)}g
                  </Text>
                </VStack>
              </SimpleGrid>
            </VStack>
          </CardBody>
        </Card>
      )}

      {/* Food Entries by Meal Type */}
      {entries.length === 0 ? (
        <Card bg={cardBg} borderColor={borderColor}>
          <CardBody>
            <Text textAlign="center" color="gray.500" py={8}>
              No food entries for this date. Click "Add Food Entry" to start logging.
            </Text>
          </CardBody>
        </Card>
      ) : (
        <VStack spacing={4} align="stretch">
          {['breakfast', 'lunch', 'dinner', 'snack']
            .filter(mealType => {
              const mealEntries = entries.filter(entry => entry.meal_type === mealType);
              return mealEntries.length > 0;
            })
            .map(mealType => {
            const mealEntries = entries.filter(entry => entry.meal_type === mealType);
            const mealCalories = mealEntries.reduce((sum, entry) => sum + entry.calories, 0);
            const mealProtein = mealEntries.reduce((sum, entry) => sum + entry.protein, 0);
            
            return (
              <Card key={mealType} bg={cardBg} borderColor={borderColor}>
                <CardHeader>
                  <HStack key={`${mealType}-header`} justify="space-between">
                    <Heading size="md" textTransform="capitalize">{mealType}</Heading>
                    <HStack key={`${mealType}-summary`} spacing={4}>
                      <Text fontSize="sm" color="gray.600">
                        {mealCalories.toFixed(0)} cal
                      </Text>
                      <Text fontSize="sm" color="gray.600">
                        {mealProtein.toFixed(1)}g protein
                      </Text>
                    </HStack>
                  </HStack>
                </CardHeader>
                <CardBody>
                  <VStack spacing={3} align="stretch">
                    {mealEntries.map((entry) => (
                      <HStack key={entry.id} justify="space-between" p={3} bg="gray.50" borderRadius="md">
                        <VStack align="start" spacing={1} flex={1}>
                          <Text fontWeight="medium">{entry.food_name}</Text>
                          <Text fontSize="sm" color="gray.600">
                            {entry.quantity} {entry.unit}
                          </Text>
                        </VStack>
                        <HStack key={`${entry.id}-nutrition`} spacing={4}>
                          <Text fontSize="sm" fontWeight="bold">
                            {entry.calories.toFixed(0)} cal
                          </Text>
                          <Text fontSize="sm" color="gray.600">
                            {entry.protein.toFixed(1)}g protein
                          </Text>
                          <HStack key={`${entry.id}-actions`} spacing={2}>
                            <IconButton
                              icon={<FiEdit />}
                              size="sm"
                              onClick={() => editEntry(entry)}
                              aria-label="Edit entry"
                            />
                            <IconButton
                              icon={<FiTrash2 />}
                              size="sm"
                              colorScheme="red"
                              onClick={() => deleteEntry(entry.id)}
                              aria-label="Delete this entry"
                              title="Delete this food entry"
                            />
                          </HStack>
                        </HStack>
                      </HStack>
                    ))}
                  </VStack>
                </CardBody>
              </Card>
            );
          })}
        </VStack>
      )}
      
      {/* Add/Edit Entry Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            {editingEntry ? 'Edit Food Entry' : 'Add Food Entry'}
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <VStack spacing={4}>
              <FormControl>
                <FormLabel>Food Name</FormLabel>
                <Input
                  value={editingEntry?.food_name || newEntry.food_name || ''}
                  onChange={(e) => {
                    if (editingEntry) {
                      setEditingEntry({...editingEntry, food_name: e.target.value});
                    } else {
                      setNewEntry({...newEntry, food_name: e.target.value});
                    }
                  }}
                  placeholder="e.g., Grilled Chicken Breast"
                />
              </FormControl>
              
              <HStack key="quantity-unit-mealtype" spacing={4} w="full">
                <FormControl>
                  <FormLabel>Quantity</FormLabel>
                  <NumberInput
                    value={editingEntry?.quantity || newEntry.quantity || 1}
                    onChange={(value) => {
                      if (editingEntry) {
                        setEditingEntry({...editingEntry, quantity: parseFloat(value) || 1});
                      } else {
                        setNewEntry({...newEntry, quantity: parseFloat(value) || 1});
                      }
                    }}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>
                
                <FormControl>
                  <FormLabel>Unit</FormLabel>
                  <Select
                    value={editingEntry?.unit || newEntry.unit || 'serving'}
                    onChange={(e) => {
                      if (editingEntry) {
                        setEditingEntry({...editingEntry, unit: e.target.value});
                      } else {
                        setNewEntry({...newEntry, unit: e.target.value});
                      }
                    }}
                  >
                    <option value="serving">Serving</option>
                    <option value="g">Grams</option>
                    <option value="oz">Ounces</option>
                    <option value="cup">Cup</option>
                    <option value="tbsp">Tablespoon</option>
                    <option value="tsp">Teaspoon</option>
                  </Select>
                </FormControl>
                
                <FormControl>
                  <FormLabel>Meal Type</FormLabel>
                  <Select
                    value={editingEntry?.meal_type || newEntry.meal_type || 'breakfast'}
                    onChange={(e) => {
                      if (editingEntry) {
                        setEditingEntry({...editingEntry, meal_type: e.target.value});
                      } else {
                        setNewEntry({...newEntry, meal_type: e.target.value});
                      }
                    }}
                  >
                    <option value="breakfast">Breakfast</option>
                    <option value="lunch">Lunch</option>
                    <option value="dinner">Dinner</option>
                    <option value="snack">Snack</option>
                  </Select>
                </FormControl>
              </HStack>
              
              <HStack key="calories-protein" spacing={4} w="full">
                <FormControl>
                  <FormLabel>Calories</FormLabel>
                  <NumberInput
                    value={editingEntry?.calories || newEntry.calories || 0}
                    onChange={(value) => {
                      if (editingEntry) {
                        setEditingEntry({...editingEntry, calories: parseFloat(value) || 0});
                      } else {
                        setNewEntry({...newEntry, calories: parseFloat(value) || 0});
                      }
                    }}
                  >
                    <NumberInputField />
                  </NumberInput>
                </FormControl>
                
                <FormControl>
                  <FormLabel>Protein (g)</FormLabel>
                  <NumberInput
                    value={editingEntry?.protein || newEntry.protein || 0}
                    onChange={(value) => {
                      if (editingEntry) {
                        setEditingEntry({...editingEntry, protein: parseFloat(value) || 0});
                      } else {
                        setNewEntry({...newEntry, protein: parseFloat(value) || 0});
                      }
                    }}
                  >
                    <NumberInputField />
                  </NumberInput>
                </FormControl>
              </HStack>
              
              <HStack key="carbs-fats" spacing={4} w="full">
                <FormControl>
                  <FormLabel>Carbs (g)</FormLabel>
                  <NumberInput
                    value={editingEntry?.carbs || newEntry.carbs || 0}
                    onChange={(value) => {
                      if (editingEntry) {
                        setEditingEntry({...editingEntry, carbs: parseFloat(value) || 0});
                      } else {
                        setNewEntry({...newEntry, carbs: parseFloat(value) || 0});
                      }
                    }}
                  >
                    <NumberInputField />
                  </NumberInput>
                </FormControl>
                
                <FormControl>
                  <FormLabel>Fats (g)</FormLabel>
                  <NumberInput
                    value={editingEntry?.fats || newEntry.fats || 0}
                    onChange={(value) => {
                      if (editingEntry) {
                        setEditingEntry({...editingEntry, fats: parseFloat(value) || 0});
                      } else {
                        setNewEntry({...newEntry, fats: parseFloat(value) || 0});
                      }
                    }}
                  >
                    <NumberInputField />
                  </NumberInput>
                </FormControl>
              </HStack>
              
              <HStack key="action-buttons" spacing={4} w="full" pt={4}>
                <Button
                  colorScheme="blue"
                  onClick={editingEntry ? updateEntry : addEntry}
                  leftIcon={editingEntry ? <FiSave /> : <FiPlus />}
                >
                  {editingEntry ? 'Update Entry' : 'Add Entry'}
                </Button>
                <Button variant="ghost" onClick={onClose}>
                  Cancel
                </Button>
              </HStack>
            </VStack>
          </ModalBody>
        </ModalContent>
      </Modal>
    </Box>
  );
};

export default DailyLogging;







