import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Card,
  CardBody,
  CardHeader,
  Badge,
  useColorModeValue,
  useBreakpointValue,
  Icon,
  Divider,
  Collapse,
  SimpleGrid,
  Input,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Select,
  FormControl,
  FormLabel,
  useToast,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
} from '@chakra-ui/react';
import { FiPlus, FiMinus, FiEdit, FiTrash2, FiClock, FiCoffee, FiChevronDown, FiChevronUp } from 'react-icons/fi';

interface MealItem {
  id: string;
  name: string;
  quantity: number;
  unit: string;
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber: number;
  sodium: number;
}

interface Meal {
  id: string;
  type: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  time: string;
  items: MealItem[];
  totalCalories: number;
  totalProtein: number;
  totalCarbs: number;
  totalFat: number;
}

const MobileMealLogging: React.FC = () => {
  const [meals, setMeals] = useState<Meal[]>([]);
  const [selectedMealType, setSelectedMealType] = useState<'breakfast' | 'lunch' | 'dinner' | 'snack'>('breakfast');
  const [expandedMeals, setExpandedMeals] = useState<Set<string>>(new Set());
  const [showAddItem, setShowAddItem] = useState(false);
  const [newItem, setNewItem] = useState<Partial<MealItem>>({
    name: '',
    quantity: 1,
    unit: 'serving',
    calories: 0,
    protein: 0,
    carbs: 0,
    fat: 0,
    fiber: 0,
    sodium: 0,
  });
  
  const isMobile = useBreakpointValue({ base: true, md: false });
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  const toast = useToast();

  const mealTypes = [
    { key: 'breakfast', label: 'Breakfast', icon: FiCoffee, color: 'orange' },
    { key: 'lunch', label: 'Lunch', icon: FiCoffee, color: 'blue' },
    { key: 'dinner', label: 'Dinner', icon: FiCoffee, color: 'purple' },
    { key: 'snack', label: 'Snack', icon: FiCoffee, color: 'teal' },
  ];

  const units = ['serving', 'g', 'ml', 'cup', 'tbsp', 'tsp', 'piece', 'slice'];

  useEffect(() => {
    // Load sample data
    setMeals([
      {
        id: '1',
        type: 'breakfast',
        time: '08:00',
        items: [
          {
            id: '1',
            name: 'Oatmeal with berries',
            quantity: 1,
            unit: 'serving',
            calories: 300,
            protein: 12,
            carbs: 45,
            fat: 8,
            fiber: 6,
            sodium: 150,
          },
        ],
        totalCalories: 300,
        totalProtein: 12,
        totalCarbs: 45,
        totalFat: 8,
      },
      {
        id: '2',
        type: 'lunch',
        time: '12:30',
        items: [
          {
            id: '2',
            name: 'Grilled chicken salad',
            quantity: 1,
            unit: 'serving',
            calories: 450,
            protein: 35,
            carbs: 20,
            fat: 25,
            fiber: 8,
            sodium: 400,
          },
        ],
        totalCalories: 450,
        totalProtein: 35,
        totalCarbs: 20,
        totalFat: 25,
      },
    ]);
  }, []);

  const toggleMeal = (mealId: string) => {
    const newExpanded = new Set(expandedMeals);
    if (newExpanded.has(mealId)) {
      newExpanded.delete(mealId);
    } else {
      newExpanded.add(mealId);
    }
    setExpandedMeals(newExpanded);
  };

  const addMealItem = () => {
    if (!newItem.name || !newItem.quantity) {
      toast({
        title: 'Please fill in all required fields',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    const item: MealItem = {
      id: Date.now().toString(),
      name: newItem.name!,
      quantity: newItem.quantity!,
      unit: newItem.unit!,
      calories: newItem.calories || 0,
      protein: newItem.protein || 0,
      carbs: newItem.carbs || 0,
      fat: newItem.fat || 0,
      fiber: newItem.fiber || 0,
      sodium: newItem.sodium || 0,
    };

    // Find or create meal for selected type
    const existingMeal = meals.find(m => m.type === selectedMealType);
    if (existingMeal) {
      setMeals(meals.map(meal => 
        meal.id === existingMeal.id 
          ? {
              ...meal,
              items: [...meal.items, item],
              totalCalories: meal.totalCalories + item.calories,
              totalProtein: meal.totalProtein + item.protein,
              totalCarbs: meal.totalCarbs + item.carbs,
              totalFat: meal.totalFat + item.fat,
            }
          : meal
      ));
    } else {
      const newMeal: Meal = {
        id: Date.now().toString(),
        type: selectedMealType,
        time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
        items: [item],
        totalCalories: item.calories,
        totalProtein: item.protein,
        totalCarbs: item.carbs,
        totalFat: item.fat,
      };
      setMeals([...meals, newMeal]);
    }

    setNewItem({
      name: '',
      quantity: 1,
      unit: 'serving',
      calories: 0,
      protein: 0,
      carbs: 0,
      fat: 0,
      fiber: 0,
      sodium: 0,
    });
    setShowAddItem(false);

    toast({
      title: 'Meal item added successfully',
      status: 'success',
      duration: 3000,
      isClosable: true,
    });
  };

  const removeMealItem = (mealId: string, itemId: string) => {
    setMeals(meals.map(meal => {
      if (meal.id === mealId) {
        const item = meal.items.find(i => i.id === itemId);
        if (item) {
          return {
            ...meal,
            items: meal.items.filter(i => i.id !== itemId),
            totalCalories: meal.totalCalories - item.calories,
            totalProtein: meal.totalProtein - item.protein,
            totalCarbs: meal.totalCarbs - item.carbs,
            totalFat: meal.totalFat - item.fat,
          };
        }
      }
      return meal;
    }));
  };

  const getTotalNutrition = () => {
    return meals.reduce((total, meal) => ({
      calories: total.calories + meal.totalCalories,
      protein: total.protein + meal.totalProtein,
      carbs: total.carbs + meal.totalCarbs,
      fat: total.fat + meal.totalFat,
    }), { calories: 0, protein: 0, carbs: 0, fat: 0 });
  };

  const totalNutrition = getTotalNutrition();

  return (
    <VStack spacing={4} align="stretch" p={4}>
      {/* Header */}
      <HStack justify="space-between" align="center">
        <Text fontSize="xl" fontWeight="bold">
          Meal Logging
        </Text>
        <Badge colorScheme="green" fontSize="sm">
          Today
        </Badge>
      </HStack>

      {/* Daily Summary */}
      <Card bg={bgColor} borderColor={borderColor}>
        <CardHeader pb={2}>
          <Text fontWeight="semibold">Daily Summary</Text>
        </CardHeader>
        <CardBody pt={0}>
          <SimpleGrid columns={2} spacing={3}>
            <Box textAlign="center">
              <Text fontSize="2xl" fontWeight="bold" color="blue.500">
                {totalNutrition.calories}
              </Text>
              <Text fontSize="sm" color={textColor}>Calories</Text>
            </Box>
            <Box textAlign="center">
              <Text fontSize="2xl" fontWeight="bold" color="green.500">
                {totalNutrition.protein}g
              </Text>
              <Text fontSize="sm" color={textColor}>Protein</Text>
            </Box>
            <Box textAlign="center">
              <Text fontSize="2xl" fontWeight="bold" color="orange.500">
                {totalNutrition.carbs}g
              </Text>
              <Text fontSize="sm" color={textColor}>Carbs</Text>
            </Box>
            <Box textAlign="center">
              <Text fontSize="2xl" fontWeight="bold" color="purple.500">
                {totalNutrition.fat}g
              </Text>
              <Text fontSize="sm" color={textColor}>Fat</Text>
            </Box>
          </SimpleGrid>
        </CardBody>
      </Card>

      {/* Meal Type Selector */}
      <HStack spacing={2} overflowX="auto" pb={2}>
        {mealTypes.map((mealType) => (
          <Button
            key={mealType.key}
            size="sm"
            variant={selectedMealType === mealType.key ? 'solid' : 'outline'}
            colorScheme={mealType.color}
            leftIcon={<Icon as={mealType.icon} />}
            onClick={() => setSelectedMealType(mealType.key as any)}
            minW="fit-content"
          >
            {mealType.label}
          </Button>
        ))}
      </HStack>

      {/* Meals List */}
      <VStack spacing={3} align="stretch">
        {meals.map((meal) => (
          <Card key={meal.id} bg={bgColor} borderColor={borderColor}>
            <CardHeader pb={2}>
              <HStack justify="space-between">
                <HStack>
                  <Icon as={mealTypes.find(m => m.key === meal.type)?.icon} />
                  <Text fontWeight="semibold" textTransform="capitalize">
                    {meal.type}
                  </Text>
                  <Text fontSize="sm" color={textColor}>
                    {meal.time}
                  </Text>
                </HStack>
                <HStack>
                  <Text fontSize="sm" fontWeight="bold" color="blue.500">
                    {meal.totalCalories} cal
                  </Text>
                  <IconButton
                    aria-label="Toggle meal details"
                    icon={expandedMeals.has(meal.id) ? <FiChevronUp /> : <FiChevronDown />}
                    size="sm"
                    variant="ghost"
                    onClick={() => toggleMeal(meal.id)}
                  />
                </HStack>
              </HStack>
            </CardHeader>
            <Collapse in={expandedMeals.has(meal.id)}>
              <CardBody pt={0}>
                <VStack spacing={2} align="stretch">
                  {meal.items.map((item) => (
                    <HStack key={item.id} justify="space-between" p={2} borderWidth={1} borderRadius="md" borderColor={borderColor}>
                      <VStack align="start" spacing={1} flex={1}>
                        <Text fontWeight="medium" fontSize="sm">
                          {item.name}
                        </Text>
                        <Text fontSize="xs" color={textColor}>
                          {item.quantity} {item.unit} • {item.calories} cal
                        </Text>
                      </VStack>
                      <IconButton
                        aria-label="Remove item"
                        icon={<FiTrash2 />}
                        size="sm"
                        variant="ghost"
                        colorScheme="red"
                        onClick={() => removeMealItem(meal.id, item.id)}
                      />
                    </HStack>
                  ))}
                </VStack>
              </CardBody>
            </Collapse>
          </Card>
        ))}
      </VStack>

      {/* Add Item Button */}
      <Button
        leftIcon={<FiPlus />}
        colorScheme="blue"
        onClick={() => setShowAddItem(true)}
      >
        Add Food Item
      </Button>

      {/* Add Item Modal */}
      <Modal isOpen={showAddItem} onClose={() => setShowAddItem(false)} size="full">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Add Food Item</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4}>
              <FormControl>
                <FormLabel>Food Name</FormLabel>
                <Input
                  value={newItem.name || ''}
                  onChange={(e) => setNewItem({ ...newItem, name: e.target.value })}
                  placeholder="Enter food name"
                />
              </FormControl>

              <HStack spacing={4} w="full">
                <FormControl>
                  <FormLabel>Quantity</FormLabel>
                  <NumberInput
                    value={newItem.quantity}
                    onChange={(valueString, valueNumber) => {
                      if (!isNaN(valueNumber)) {
                        setNewItem({ ...newItem, quantity: valueNumber });
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

                <FormControl>
                  <FormLabel>Unit</FormLabel>
                  <Select
                    value={newItem.unit}
                    onChange={(e) => setNewItem({ ...newItem, unit: e.target.value })}
                  >
                    {units.map(unit => (
                      <option key={unit} value={unit}>{unit}</option>
                    ))}
                  </Select>
                </FormControl>
              </HStack>

              <SimpleGrid columns={2} spacing={4} w="full">
                <FormControl>
                  <FormLabel>Calories</FormLabel>
                  <NumberInput
                    value={newItem.calories}
                    onChange={(valueString, valueNumber) => {
                      if (!isNaN(valueNumber)) {
                        setNewItem({ ...newItem, calories: valueNumber });
                      }
                    }}
                    min={0}
                  >
                    <NumberInputField />
                  </NumberInput>
                </FormControl>

                <FormControl>
                  <FormLabel>Protein (g)</FormLabel>
                  <NumberInput
                    value={newItem.protein}
                    onChange={(valueString, valueNumber) => {
                      if (!isNaN(valueNumber)) {
                        setNewItem({ ...newItem, protein: valueNumber });
                      }
                    }}
                    min={0}
                    precision={1}
                  >
                    <NumberInputField />
                  </NumberInput>
                </FormControl>

                <FormControl>
                  <FormLabel>Carbs (g)</FormLabel>
                  <NumberInput
                    value={newItem.carbs}
                    onChange={(valueString, valueNumber) => {
                      if (!isNaN(valueNumber)) {
                        setNewItem({ ...newItem, carbs: valueNumber });
                      }
                    }}
                    min={0}
                    precision={1}
                  >
                    <NumberInputField />
                  </NumberInput>
                </FormControl>

                <FormControl>
                  <FormLabel>Fat (g)</FormLabel>
                  <NumberInput
                    value={newItem.fat}
                    onChange={(valueString, valueNumber) => {
                      if (!isNaN(valueNumber)) {
                        setNewItem({ ...newItem, fat: valueNumber });
                      }
                    }}
                    min={0}
                    precision={1}
                  >
                    <NumberInputField />
                  </NumberInput>
                </FormControl>
              </SimpleGrid>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={() => setShowAddItem(false)}>
              Cancel
            </Button>
            <Button colorScheme="blue" onClick={addMealItem}>
              Add Item
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </VStack>
  );
};

export default MobileMealLogging;







