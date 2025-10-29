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
  FormControl,
  FormLabel,
  Select,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Button,
  useToast,
  Icon,
  useColorModeValue,
  Divider,
  SimpleGrid,
  Card,
  CardBody,
  Badge,
  Alert,
  AlertIcon,
  Spinner,
  Input,
  Textarea
} from '@chakra-ui/react';
import { 
  FiTarget, 
  FiCalendar,
  FiClock,
  FiUsers,
  FiTrendingUp,
  FiInfo,
  FiPlus
} from 'react-icons/fi';
import mealPlanRecipeService from '../../services/mealPlanRecipeService';
import type { AddRecipeToMealPlanRequest } from '../../services/mealPlanRecipeService';
import mealPlanService from '../../services/mealPlanService';

interface AddToMealPlanModalProps {
  isOpen: boolean;
  onClose: () => void;
  recipe: {
    id: string;
    title: string;
    description?: string;
    cuisine: string;
    meal_type: string;
    prep_time?: number;
    cook_time?: number;
    difficulty_level?: string;
    servings: number;
    image_url?: string;
    dietary_tags?: string[];
    allergens?: string[];
    calories?: number;
    protein?: number;
    carbs?: number;
    fat?: number;
    sodium?: number;
  };
  onRecipeAdded: () => void;
}

const AddToMealPlanModal: React.FC<AddToMealPlanModalProps> = ({
  isOpen,
  onClose,
  recipe,
  onRecipeAdded
}) => {
  const [mealPlans, setMealPlans] = useState<any[]>([]);
  const [loadingPlans, setLoadingPlans] = useState(false);
  const [adding, setAdding] = useState(false);
  const [formData, setFormData] = useState({
    meal_plan_id: '',
    meal_date: new Date().toISOString().split('T')[0],
    meal_type: recipe.meal_type || 'main_course',
    servings: 1,
    meal_time: '',
    custom_meal_name: ''
  });

  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  useEffect(() => {
    if (isOpen) {
      loadMealPlans();
      // Reset form data
      setFormData({
        meal_plan_id: '',
        meal_date: new Date().toISOString().split('T')[0],
        meal_type: recipe.meal_type || 'main_course',
        servings: 1,
        meal_time: '',
        custom_meal_name: ''
      });
    }
  }, [isOpen, recipe]);

  const loadMealPlans = async () => {
    try {
      setLoadingPlans(true);
      const plans = await mealPlanService.getMealPlans();
      setMealPlans(plans);
    } catch (error) {
      console.error('Error loading meal plans:', error);
    } finally {
      setLoadingPlans(false);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleAddToMealPlan = async () => {
    if (!formData.meal_plan_id) {
      toast({
        title: "Error",
        description: "Please select a meal plan",
        status: "error",
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    try {
      setAdding(true);
      
      const request: AddRecipeToMealPlanRequest = {
        recipe_id: recipe.id,
        meal_date: formData.meal_date,
        meal_type: formData.meal_type,
        servings: formData.servings,
        meal_time: formData.meal_time || undefined,
        custom_meal_name: formData.custom_meal_name || undefined
      };

      await mealPlanRecipeService.addRecipeToMealPlan(formData.meal_plan_id, request);
      
      toast({
        title: "Recipe Added!",
        description: `${recipe.title} has been added to your meal plan`,
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      
      onRecipeAdded();
      onClose();
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to add recipe to meal plan",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setAdding(false);
    }
  };

  const calculateScaledNutrition = (servings: number) => {
    const baseServings = recipe.servings || 1;
    const scaleFactor = servings / baseServings;
    
    return {
      calories: Math.round((recipe.calories || 0) * scaleFactor),
      protein: Math.round((recipe.protein || 0) * scaleFactor * 10) / 10,
      carbs: Math.round((recipe.carbs || 0) * scaleFactor * 10) / 10,
      fat: Math.round((recipe.fat || 0) * scaleFactor * 10) / 10,
      sodium: Math.round((recipe.sodium || 0) * scaleFactor)
    };
  };

  const scaledNutrition = calculateScaledNutrition(formData.servings);

  const getMealTypeColor = (mealType: string) => {
    switch (mealType.toLowerCase()) {
      case 'breakfast':
        return 'orange';
      case 'lunch':
        return 'yellow';
      case 'dinner':
        return 'blue';
      case 'snack':
        return 'green';
      case 'main_course':
        return 'purple';
      case 'side_dish':
        return 'teal';
      default:
        return 'gray';
    }
  };

  const formatMealType = (mealType: string) => {
    return mealType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>
          <HStack spacing={3}>
            <Icon as={FiPlus} color="blue.500" />
            <VStack align="start" spacing={0}>
              <Text>Add to Meal Plan</Text>
              <Text fontSize="sm" color="gray.500">{recipe.title}</Text>
            </VStack>
          </HStack>
        </ModalHeader>
        <ModalCloseButton />
        
        <ModalBody>
          <VStack spacing={6} align="stretch">
            {/* Recipe Summary */}
            <Card bg={bgColor} borderColor={borderColor}>
              <CardBody>
                <VStack spacing={4} align="stretch">
                  <HStack justify="space-between" align="start">
                    <VStack align="start" spacing={2} flex="1">
                      <Text fontWeight="semibold" fontSize="lg">{recipe.title}</Text>
                      <HStack spacing={2}>
                        <Badge colorScheme={getMealTypeColor(recipe.meal_type)}>
                          {formatMealType(recipe.meal_type)}
                        </Badge>
                        <Badge colorScheme="gray" variant="outline">
                          {recipe.cuisine}
                        </Badge>
                      </HStack>
                      {recipe.description && (
                        <Text fontSize="sm" color="gray.600" noOfLines={2}>
                          {recipe.description}
                        </Text>
                      )}
                    </VStack>
                    {recipe.image_url && (
                      <Box
                        w="60px"
                        h="60px"
                        bg="gray.100"
                        borderRadius="md"
                        bgImage={`url(${recipe.image_url})`}
                        bgSize="cover"
                        bgPosition="center"
                      />
                    )}
                  </HStack>
                  
                  <Divider />
                  
                  <SimpleGrid columns={2} spacing={4}>
                    <HStack>
                      <Icon as={FiUsers} color="blue.500" />
                      <Text fontSize="sm">Serves: {recipe.servings}</Text>
                    </HStack>
                    <HStack>
                      <Icon as={FiClock} color="green.500" />
                      <Text fontSize="sm">
                        {recipe.prep_time && recipe.cook_time 
                          ? `${recipe.prep_time + recipe.cook_time} min`
                          : recipe.prep_time 
                          ? `${recipe.prep_time} min prep`
                          : recipe.cook_time
                          ? `${recipe.cook_time} min cook`
                          : 'Time not specified'
                        }
                      </Text>
                    </HStack>
                  </SimpleGrid>
                </VStack>
              </CardBody>
            </Card>

            {/* Form Fields */}
            <VStack spacing={4} align="stretch">
              <FormControl isRequired>
                <FormLabel>Select Meal Plan</FormLabel>
                {loadingPlans ? (
                  <HStack>
                    <Spinner size="sm" />
                    <Text fontSize="sm">Loading meal plans...</Text>
                  </HStack>
                ) : (
                  <Select
                    value={formData.meal_plan_id}
                    onChange={(e) => handleInputChange('meal_plan_id', e.target.value)}
                    placeholder="Choose a meal plan"
                  >
                    {mealPlans.map((plan) => (
                      <option key={plan.id} value={plan.id}>
                        {plan.plan_type === 'daily' 
                          ? `Daily Plan - ${new Date(plan.start_date).toLocaleDateString()}`
                          : `Weekly Plan - ${new Date(plan.start_date).toLocaleDateString()}`
                        }
                      </option>
                    ))}
                  </Select>
                )}
              </FormControl>

              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                <FormControl isRequired>
                  <FormLabel>Meal Date</FormLabel>
                  <Input
                    type="date"
                    value={formData.meal_date}
                    onChange={(e) => handleInputChange('meal_date', e.target.value)}
                  />
                </FormControl>

                <FormControl isRequired>
                  <FormLabel>Meal Type</FormLabel>
                  <Select
                    value={formData.meal_type}
                    onChange={(e) => handleInputChange('meal_type', e.target.value)}
                  >
                    <option value="breakfast">Breakfast</option>
                    <option value="lunch">Lunch</option>
                    <option value="dinner">Dinner</option>
                    <option value="snack">Snack</option>
                    <option value="main_course">Main Course</option>
                    <option value="side_dish">Side Dish</option>
                  </Select>
                </FormControl>
              </SimpleGrid>

              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                <FormControl isRequired>
                  <FormLabel>Servings</FormLabel>
                  <NumberInput
                    value={formData.servings}
                    onChange={(_, value) => handleInputChange('servings', value)}
                    min={0.25}
                    max={20}
                    step={0.25}
                    precision={2}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                  <Text fontSize="xs" color="gray.500">
                    Original recipe serves {recipe.servings}
                  </Text>
                </FormControl>

                <FormControl>
                  <FormLabel>Meal Time (Optional)</FormLabel>
                  <Input
                    type="time"
                    value={formData.meal_time}
                    onChange={(e) => handleInputChange('meal_time', e.target.value)}
                  />
                </FormControl>
              </SimpleGrid>

              <FormControl>
                <FormLabel>Custom Meal Name (Optional)</FormLabel>
                <Input
                  value={formData.custom_meal_name}
                  onChange={(e) => handleInputChange('custom_meal_name', e.target.value)}
                  placeholder="e.g., Special Birthday Dinner"
                />
              </FormControl>
            </VStack>

            {/* Nutrition Preview */}
            <Alert status="info" borderRadius="lg">
              <AlertIcon />
              <VStack align="start" spacing={2} flex="1">
                <Text fontWeight="semibold">Nutrition Preview ({formData.servings} servings)</Text>
                <SimpleGrid columns={2} spacing={2} w="full">
                  <Text fontSize="sm">Calories: {scaledNutrition.calories}</Text>
                  <Text fontSize="sm">Protein: {scaledNutrition.protein}g</Text>
                  <Text fontSize="sm">Carbs: {scaledNutrition.carbs}g</Text>
                  <Text fontSize="sm">Fat: {scaledNutrition.fat}g</Text>
                </SimpleGrid>
              </VStack>
            </Alert>
          </VStack>
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            Cancel
          </Button>
          <Button
            colorScheme="blue"
            onClick={handleAddToMealPlan}
            isLoading={adding}
            loadingText="Adding..."
            isDisabled={!formData.meal_plan_id || formData.servings <= 0}
          >
            Add to Meal Plan
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default AddToMealPlanModal;
