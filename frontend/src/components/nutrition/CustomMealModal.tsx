import React, { useState, useEffect } from 'react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  Button,
  VStack,
  HStack,
  FormControl,
  FormLabel,
  Input,
  Select,
  Textarea,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Divider,
  Text,
  Badge,
  IconButton,
  useToast,
  Box
} from '@chakra-ui/react';
import { FiPlus, FiTrash2 } from 'react-icons/fi';

interface Ingredient {
  name: string;
  quantity: number;
  unit: string;
}

interface Instruction {
  step: number;
  description: string;
}

interface CustomMealData {
  meal_name: string;
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  cuisine: string;
  prep_time: number;
  cook_time: number;
  servings: number;
  difficulty: 'easy' | 'medium' | 'hard';
  summary: string;
  ingredients: Ingredient[];
  instructions: Instruction[];
  dietary_tags: string[];
  nutrition: {
    calories: number;
    protein: number;
    carbs: number;
    fats: number;
  };
}

interface CustomMealModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (mealData: CustomMealData) => void;
  initialData?: Partial<CustomMealData>;
  selectedDate?: string; // ROOT CAUSE FIX: Allow passing selected date
  selectedMealType?: string; // ROOT CAUSE FIX: Allow passing selected meal type
}

const CustomMealModal: React.FC<CustomMealModalProps> = ({
  isOpen,
  onClose,
  onSave,
  initialData,
  selectedDate,
  selectedMealType
}) => {
  const [formData, setFormData] = useState<CustomMealData>({
    meal_name: '',
    meal_type: 'breakfast',
    cuisine: '',
    prep_time: 0,
    cook_time: 0,
    servings: 1,
    difficulty: 'easy',
    summary: '',
    ingredients: [{ name: '', quantity: 0, unit: 'g' }],
    instructions: [{ step: 1, description: '' }],
    dietary_tags: [],
    nutrition: {
      calories: 0,
      protein: 0,
      carbs: 0,
      fats: 0
    },
    ...initialData
  });

  // Update formData when modal opens/closes or initialData changes
  useEffect(() => {
    if (isOpen) {
      // ROOT CAUSE FIX: Pre-fill date and meal_type if provided
      const baseData: Partial<CustomMealData> = {};
      if (selectedDate) {
        (baseData as any).meal_date = selectedDate;
        (baseData as any).date = selectedDate;
      }
      if (selectedMealType) {
        baseData.meal_type = selectedMealType as any;
      }
      
      if (initialData) {
        // Editing: use initialData with proper defaults for missing fields
        setFormData({
          meal_name: initialData.meal_name ?? '',
          meal_type: initialData.meal_type ?? (selectedMealType as any) ?? 'breakfast',
          cuisine: initialData.cuisine ?? '',
          prep_time: initialData.prep_time ?? 0,
          cook_time: initialData.cook_time ?? 0,
          servings: initialData.servings ?? 1,
          difficulty: initialData.difficulty ?? 'easy',
          summary: initialData.summary ?? '',
          ingredients: initialData.ingredients && initialData.ingredients.length > 0 
            ? initialData.ingredients 
            : [{ name: '', quantity: 0, unit: 'g' }],
          instructions: initialData.instructions && initialData.instructions.length > 0
            ? initialData.instructions
            : [{ step: 1, description: '' }],
          dietary_tags: initialData.dietary_tags ?? [],
          nutrition: {
            calories: initialData.nutrition?.calories ?? 0,
            protein: initialData.nutrition?.protein ?? 0,
            carbs: initialData.nutrition?.carbs ?? 0,
            fats: initialData.nutrition?.fats ?? 0
          },
          ...baseData
        });
      } else {
        // Creating new meal: reset to empty/0 defaults, but use selected date/type if provided
        setFormData({
          meal_name: '',
          meal_type: (selectedMealType as any) ?? 'breakfast',
          cuisine: '',
          prep_time: 0,
          cook_time: 0,
          servings: 1,
          difficulty: 'easy',
          summary: '',
          ingredients: [{ name: '', quantity: 0, unit: 'g' }],
          instructions: [{ step: 1, description: '' }],
          dietary_tags: [],
          nutrition: {
            calories: 0,
            protein: 0,
            carbs: 0,
            fats: 0
          },
          ...baseData
        });
      }
      // Reset new ingredient/instruction/tag inputs
      setNewIngredient({ name: '', quantity: 0, unit: 'g' });
      setNewInstruction('');
      setNewDietaryTag('');
    }
  }, [isOpen, initialData]);

  const [newIngredient, setNewIngredient] = useState({ name: '', quantity: 0, unit: 'g' });
  const [newInstruction, setNewInstruction] = useState('');
  const [newDietaryTag, setNewDietaryTag] = useState('');
  
  const toast = useToast();

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleNutritionChange = (field: string, value: number) => {
    setFormData(prev => ({
      ...prev,
      nutrition: {
        ...prev.nutrition,
        [field]: value
      }
    }));
  };

  const addIngredient = () => {
    if (newIngredient.name.trim()) {
      setFormData(prev => ({
        ...prev,
        ingredients: [...prev.ingredients, { ...newIngredient }]
      }));
      setNewIngredient({ name: '', quantity: 0, unit: 'g' });
    }
  };

  const removeIngredient = (index: number) => {
    setFormData(prev => ({
      ...prev,
      ingredients: prev.ingredients.filter((_, i) => i !== index)
    }));
  };

  const addInstruction = () => {
    if (newInstruction.trim()) {
      setFormData(prev => ({
        ...prev,
        instructions: [...prev.instructions, { 
          step: prev.instructions.length + 1, 
          description: newInstruction 
        }]
      }));
      setNewInstruction('');
    }
  };

  const removeInstruction = (index: number) => {
    setFormData(prev => ({
      ...prev,
      instructions: prev.instructions
        .filter((_, i) => i !== index)
        .map((inst, i) => ({ ...inst, step: i + 1 }))
    }));
  };

  const addDietaryTag = () => {
    if (newDietaryTag.trim() && !formData.dietary_tags.includes(newDietaryTag)) {
      setFormData(prev => ({
        ...prev,
        dietary_tags: [...prev.dietary_tags, newDietaryTag]
      }));
      setNewDietaryTag('');
    }
  };

  const removeDietaryTag = (tag: string) => {
    setFormData(prev => ({
      ...prev,
      dietary_tags: prev.dietary_tags.filter(t => t !== tag)
    }));
  };

  const handleSave = () => {
    if (!formData.meal_name.trim()) {
      toast({
        title: 'Please enter a meal name',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    if (formData.ingredients.length === 0) {
      toast({
        title: 'Please add at least one ingredient',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    if (formData.instructions.length === 0) {
      toast({
        title: 'Please add at least one instruction',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    onSave(formData);
    onClose();
  };

  const unitOptions = ['g', 'kg', 'ml', 'l', 'cups', 'tbsp', 'tsp', 'pieces', 'slices'];

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior="inside">
      <ModalOverlay />
      <ModalContent maxH="90vh">
        <ModalHeader>Add Custom Meal</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack spacing={6} align="stretch">
            {/* Basic Information */}
            <VStack spacing={4} align="stretch">
              <Text fontWeight="semibold" fontSize="lg">Basic Information</Text>
              
              <HStack spacing={4}>
                <FormControl isRequired>
                  <FormLabel>Meal Name</FormLabel>
                  <Input
                    value={formData.meal_name}
                    onChange={(e) => handleInputChange('meal_name', e.target.value)}
                    placeholder={formData.meal_name ? undefined : "e.g., Grilled Chicken Salad"}
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
                  </Select>
                </FormControl>
              </HStack>

              <HStack spacing={4}>
                <FormControl>
                  <FormLabel>Cuisine</FormLabel>
                  <Input
                    value={formData.cuisine}
                    onChange={(e) => handleInputChange('cuisine', e.target.value)}
                    placeholder={formData.cuisine ? undefined : "e.g., Mediterranean, Italian, Asian"}
                  />
                </FormControl>
                
                <FormControl>
                  <FormLabel>Difficulty</FormLabel>
                  <Select
                    value={formData.difficulty}
                    onChange={(e) => handleInputChange('difficulty', e.target.value)}
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </Select>
                </FormControl>
              </HStack>

              <FormControl>
                <FormLabel>Summary</FormLabel>
                <Textarea
                  value={formData.summary}
                  onChange={(e) => handleInputChange('summary', e.target.value)}
                  placeholder={formData.summary ? undefined : "Brief description of the meal..."}
                  rows={2}
                />
              </FormControl>
            </VStack>

            <Divider />

            {/* Timing and Servings */}
            <VStack spacing={4} align="stretch">
              <Text fontWeight="semibold" fontSize="lg">Timing & Servings</Text>
              
              <HStack spacing={4}>
                <FormControl>
                  <FormLabel>Prep Time (minutes)</FormLabel>
                  <NumberInput
                    value={formData.prep_time}
                    onChange={(_, value) => handleInputChange('prep_time', value)}
                    min={0}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>
                
                <FormControl>
                  <FormLabel>Cook Time (minutes)</FormLabel>
                  <NumberInput
                    value={formData.cook_time}
                    onChange={(_, value) => handleInputChange('cook_time', value)}
                    min={0}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>
                
                <FormControl>
                  <FormLabel>Servings</FormLabel>
                  <NumberInput
                    value={formData.servings}
                    onChange={(_, value) => handleInputChange('servings', value)}
                    min={1}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>
              </HStack>
            </VStack>

            <Divider />

            {/* Ingredients */}
            <VStack spacing={4} align="stretch">
              <Text fontWeight="semibold" fontSize="lg">Ingredients</Text>
              
              {formData.ingredients.map((ingredient, index) => (
                <HStack key={index} spacing={2}>
                  <Input
                    value={ingredient.name}
                    onChange={(e) => {
                      const newIngredients = [...formData.ingredients];
                      newIngredients[index].name = e.target.value;
                      setFormData(prev => ({ ...prev, ingredients: newIngredients }));
                    }}
                    placeholder={ingredient.name ? undefined : "Ingredient name"}
                    flex={2}
                  />
                  <NumberInput
                    value={ingredient.quantity}
                    onChange={(_, value) => {
                      const newIngredients = [...formData.ingredients];
                      newIngredients[index].quantity = value;
                      setFormData(prev => ({ ...prev, ingredients: newIngredients }));
                    }}
                    min={0}
                    w="100px"
                  >
                    <NumberInputField />
                  </NumberInput>
                  <Select
                    value={ingredient.unit}
                    onChange={(e) => {
                      const newIngredients = [...formData.ingredients];
                      newIngredients[index].unit = e.target.value;
                      setFormData(prev => ({ ...prev, ingredients: newIngredients }));
                    }}
                    w="120px"
                  >
                    {unitOptions.map(unit => (
                      <option key={unit} value={unit}>{unit}</option>
                    ))}
                  </Select>
                  <IconButton
                    icon={<FiTrash2 />}
                    size="sm"
                    variant="ghost"
                    colorScheme="red"
                    onClick={() => removeIngredient(index)}
                    aria-label="Remove ingredient"
                  />
                </HStack>
              ))}
              
              <HStack spacing={2}>
                <Input
                  value={newIngredient.name}
                  onChange={(e) => setNewIngredient(prev => ({ ...prev, name: e.target.value }))}
                  placeholder={newIngredient.name ? undefined : "Add new ingredient"}
                  flex={2}
                />
                <NumberInput
                  value={newIngredient.quantity}
                  onChange={(_, value) => setNewIngredient(prev => ({ ...prev, quantity: value }))}
                  min={0}
                  w="100px"
                >
                  <NumberInputField />
                </NumberInput>
                <Select
                  value={newIngredient.unit}
                  onChange={(e) => setNewIngredient(prev => ({ ...prev, unit: e.target.value }))}
                  w="120px"
                >
                  {unitOptions.map(unit => (
                    <option key={unit} value={unit}>{unit}</option>
                  ))}
                </Select>
                <IconButton
                  icon={<FiPlus />}
                  size="sm"
                  colorScheme="blue"
                  onClick={addIngredient}
                  aria-label="Add ingredient"
                />
              </HStack>
            </VStack>

            <Divider />

            {/* Instructions */}
            <VStack spacing={4} align="stretch">
              <Text fontWeight="semibold" fontSize="lg">Instructions</Text>
              
              {formData.instructions.map((instruction, index) => (
                <HStack key={index} spacing={2} align="start">
                  <Badge colorScheme="blue" minW="30px" textAlign="center">
                    {instruction.step}
                  </Badge>
                  <Textarea
                    value={instruction.description}
                    onChange={(e) => {
                      const newInstructions = [...formData.instructions];
                      newInstructions[index].description = e.target.value;
                      setFormData(prev => ({ ...prev, instructions: newInstructions }));
                    }}
                    placeholder={instruction.description ? undefined : "Instruction description"}
                    flex={1}
                    rows={2}
                  />
                  <IconButton
                    icon={<FiTrash2 />}
                    size="sm"
                    variant="ghost"
                    colorScheme="red"
                    onClick={() => removeInstruction(index)}
                    aria-label="Remove instruction"
                  />
                </HStack>
              ))}
              
              <HStack spacing={2}>
                <Textarea
                  value={newInstruction}
                  onChange={(e) => setNewInstruction(e.target.value)}
                  placeholder={newInstruction ? undefined : "Add new instruction"}
                  flex={1}
                  rows={2}
                />
                <IconButton
                  icon={<FiPlus />}
                  size="sm"
                  colorScheme="blue"
                  onClick={addInstruction}
                  aria-label="Add instruction"
                />
              </HStack>
            </VStack>

            <Divider />

            {/* Nutritional Information */}
            <VStack spacing={4} align="stretch">
              <Text fontWeight="semibold" fontSize="lg">Nutritional Information (per serving)</Text>
              
              <HStack spacing={4}>
                <FormControl>
                  <FormLabel>Calories</FormLabel>
                  <NumberInput
                    value={formData.nutrition.calories}
                    onChange={(_, value) => handleNutritionChange('calories', value)}
                    min={0}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>
                
                <FormControl>
                  <FormLabel>Protein (g)</FormLabel>
                  <NumberInput
                    value={formData.nutrition.protein}
                    onChange={(_, value) => handleNutritionChange('protein', value)}
                    min={0}
                    step={0.1}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>
                
                <FormControl>
                  <FormLabel>Carbs (g)</FormLabel>
                  <NumberInput
                    value={formData.nutrition.carbs}
                    onChange={(_, value) => handleNutritionChange('carbs', value)}
                    min={0}
                    step={0.1}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>
                
                <FormControl>
                  <FormLabel>Fats (g)</FormLabel>
                  <NumberInput
                    value={formData.nutrition.fats}
                    onChange={(_, value) => handleNutritionChange('fats', value)}
                    min={0}
                    step={0.1}
                  >
                    <NumberInputField />
                    <NumberInputStepper>
                      <NumberIncrementStepper />
                      <NumberDecrementStepper />
                    </NumberInputStepper>
                  </NumberInput>
                </FormControl>
              </HStack>
            </VStack>

            <Divider />

            {/* Dietary Tags */}
            <VStack spacing={4} align="stretch">
              <Text fontWeight="semibold" fontSize="lg">Dietary Tags</Text>
              
              <HStack spacing={2} wrap="wrap">
                {formData.dietary_tags.map((tag, index) => (
                  <Badge
                    key={index}
                    colorScheme="green"
                    cursor="pointer"
                    onClick={() => removeDietaryTag(tag)}
                  >
                    {tag} ×
                  </Badge>
                ))}
              </HStack>
              
              <HStack spacing={2}>
                <Input
                  value={newDietaryTag}
                  onChange={(e) => setNewDietaryTag(e.target.value)}
                  placeholder={newDietaryTag ? undefined : "Add dietary tag (e.g., vegetarian, gluten-free)"}
                  flex={1}
                />
                <Button size="sm" colorScheme="blue" onClick={addDietaryTag}>
                  Add Tag
                </Button>
              </HStack>
            </VStack>
          </VStack>
        </ModalBody>
        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            Cancel
          </Button>
          <Button colorScheme="blue" onClick={handleSave}>
            Save Custom Meal
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default CustomMealModal;








