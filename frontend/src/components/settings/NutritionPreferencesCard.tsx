import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  FormControl,
  FormLabel,
  Checkbox,
  CheckboxGroup,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Badge,
  useToast,
  SimpleGrid,
  Divider,
  Alert,
  AlertIcon,
  Spinner,
  Collapse,
  useDisclosure,
  Icon,
} from '@chakra-ui/react';
import { FiChevronDown, FiChevronUp, FiSettings } from 'react-icons/fi';

interface NutritionPreferencesCardProps {
  onSave: (preferences: any) => Promise<void>;
  onLoad: () => Promise<any>;
}

const NutritionPreferencesCard: React.FC<NutritionPreferencesCardProps> = ({
  onSave,
  onLoad,
}) => {
  const [formData, setFormData] = useState({
    dietary_preferences: [],
    allergies: [],
    daily_calorie_target: 2000,
    protein_target: 100,
    carbs_target: 200,
    fats_target: 60,
  });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [hasPreferences, setHasPreferences] = useState(false);
  const { isOpen, onToggle } = useDisclosure();
  const toast = useToast();

  useEffect(() => {
    loadPreferences();
  }, []);

  // Normalize allergies for display (convert backend format to frontend format)
  // Backend uses "tree_nuts" but frontend displays "tree-nuts"
  const normalizeAllergiesForDisplay = (allergies: string[]): string[] => {
    if (!allergies || allergies.length === 0) return [];
    return allergies.map(a => {
      if (a === 'tree_nuts') return 'tree-nuts';
      return a;
    });
  };

  const loadPreferences = async () => {
    setLoading(true);
    try {
      const preferences = await onLoad();
      if (preferences) {
        setFormData({
          dietary_preferences: preferences.dietary_preferences || [],
          allergies: normalizeAllergiesForDisplay(preferences.allergies || []),
          daily_calorie_target: preferences.daily_calorie_target || 2000,
          protein_target: preferences.protein_target || 100,
          carbs_target: preferences.carbs_target || 200,
          fats_target: preferences.fats_target || 60,
        });
        setHasPreferences(true);
      }
    } catch (error) {
      console.log('No nutrition preferences found, using defaults');
    } finally {
      setLoading(false);
    }
  };

  // Normalize allergies to match backend format
  // Backend expects: ['nuts', 'tree_nuts', 'peanuts', 'eggs', 'dairy', 'soy', 'wheat', 'gluten', 'fish', 'shellfish', 'sesame', 'mustard', 'sulfites']
  const normalizeAllergies = (allergies: string[]): string[] => {
    if (!allergies || allergies.length === 0) return [];
    
    const allergyMapping: Record<string, string> = {
      'tree-nuts': 'tree_nuts',
      'tree_nuts': 'tree_nuts',
      'dairy free': 'dairy',
      'dairy-free': 'dairy',
      'dairy': 'dairy',
    };
    
    const validAllergies = [
      'nuts', 'tree_nuts', 'peanuts', 'eggs', 'dairy', 'soy', 
      'wheat', 'gluten', 'fish', 'shellfish', 'sesame', 'mustard', 'sulfites'
    ];
    
    return allergies
      .map(a => {
        const normalized = allergyMapping[a.toLowerCase()] || a.toLowerCase();
        return normalized;
      })
      .filter(a => validAllergies.includes(a))
      .filter((a, index, arr) => arr.indexOf(a) === index); // Remove duplicates
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // Normalize allergies before saving
      const normalizedData = {
        ...formData,
        allergies: normalizeAllergies(formData.allergies || []),
      };
      await onSave(normalizedData);
      setHasPreferences(true);
      toast({
        title: 'Success',
        description: 'Nutrition preferences saved successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to save nutrition preferences',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setSaving(false);
    }
  };

  const dietaryOptions = [
    'vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'keto', 'paleo',
    'mediterranean', 'low-carb', 'high-protein', 'low-fat', 'diabetic-friendly',
    'heart-healthy', 'anti-inflammatory', 'raw', 'pescatarian'
  ];

  const allergyOptions = [
    'dairy', 'eggs', 'gluten', 'wheat', 'nuts', 'tree-nuts', 'peanuts',
    'fish', 'shellfish', 'soy', 'sesame', 'mustard', 'sulfites'
  ];

  if (loading) {
    return (
      <Card>
        <CardBody>
          <HStack justify="center">
            <Spinner size="sm" />
            <Text>Loading nutrition preferences...</Text>
          </HStack>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <HStack justify="space-between">
          <HStack>
            <Icon as={FiSettings} />
            <Heading size="md">Nutrition Preferences</Heading>
            {hasPreferences && (
              <Badge colorScheme="green" variant="subtle">
                Configured
              </Badge>
            )}
          </HStack>
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggle}
            rightIcon={isOpen ? <FiChevronUp /> : <FiChevronDown />}
          >
            {isOpen ? 'Hide' : 'Show'}
          </Button>
        </HStack>
      </CardHeader>
      
      <Collapse in={isOpen}>
        <CardBody pt={0}>
          <VStack spacing={6} align="stretch">
            {/* Dietary Preferences */}
            <FormControl>
              <FormLabel>Dietary Preferences</FormLabel>
              <CheckboxGroup
                value={formData.dietary_preferences}
                onChange={(value) => setFormData(prev => ({ ...prev, dietary_preferences: value }))}
              >
                <SimpleGrid columns={3} spacing={2}>
                  {dietaryOptions.map((option) => (
                    <Checkbox key={option} value={option} size="sm">
                      {option.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </Checkbox>
                  ))}
                </SimpleGrid>
              </CheckboxGroup>
            </FormControl>

            <Divider />

            {/* Allergies */}
            <FormControl>
              <FormLabel>Allergies & Intolerances</FormLabel>
              <CheckboxGroup
                value={formData.allergies}
                onChange={(value) => setFormData(prev => ({ ...prev, allergies: value }))}
              >
                <SimpleGrid columns={3} spacing={2}>
                  {allergyOptions.map((option) => (
                    <Checkbox key={option} value={option} size="sm">
                      {option.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </Checkbox>
                  ))}
                </SimpleGrid>
              </CheckboxGroup>
            </FormControl>

            <Divider />

            {/* Nutritional Targets */}
            <FormControl>
              <FormLabel>Daily Calorie Target</FormLabel>
              <NumberInput
                value={formData.daily_calorie_target}
                onChange={(valueString, valueNumber) => 
                  setFormData(prev => ({ ...prev, daily_calorie_target: valueNumber || 2000 }))
                }
                min={800}
                max={5000}
                step={50}
              >
                <NumberInputField />
                <NumberInputStepper>
                  <NumberIncrementStepper />
                  <NumberDecrementStepper />
                </NumberInputStepper>
              </NumberInput>
            </FormControl>

            <SimpleGrid columns={3} spacing={4}>
              <FormControl>
                <FormLabel>Protein (g)</FormLabel>
                <NumberInput
                  value={formData.protein_target}
                  onChange={(valueString, valueNumber) => 
                    setFormData(prev => ({ ...prev, protein_target: valueNumber || 100 }))
                  }
                  min={20}
                  max={300}
                  step={5}
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
                  value={formData.carbs_target}
                  onChange={(valueString, valueNumber) => 
                    setFormData(prev => ({ ...prev, carbs_target: valueNumber || 200 }))
                  }
                  min={50}
                  max={500}
                  step={10}
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
                  value={formData.fats_target}
                  onChange={(valueString, valueNumber) => 
                    setFormData(prev => ({ ...prev, fats_target: valueNumber || 60 }))
                  }
                  min={20}
                  max={200}
                  step={5}
                >
                  <NumberInputField />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
              </FormControl>
            </SimpleGrid>

            <Alert status="info" borderRadius="md">
              <AlertIcon />
              <Box>
                <Text fontSize="sm">
                  These preferences will automatically filter recipes and meal plans to match your dietary needs.
                </Text>
              </Box>
            </Alert>

            <HStack justify="flex-end">
              <Button
                colorScheme="blue"
                onClick={handleSave}
                isLoading={saving}
                loadingText="Saving..."
              >
                Save Nutrition Preferences
              </Button>
            </HStack>
          </VStack>
        </CardBody>
      </Collapse>
    </Card>
  );
};

export default NutritionPreferencesCard;







