import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  FormControl,
  FormLabel,
  FormErrorMessage,
  Input,
  Select,
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
} from '@chakra-ui/react';
import { t } from '../../utils/translations';
import { FiPlus } from 'react-icons/fi';

interface NutritionPreferencesProps {
  preferences: any;
  onUpdate: () => void;
}

const NutritionPreferences: React.FC<NutritionPreferencesProps> = ({
  preferences,
  onUpdate,
}) => {
  const [formData, setFormData] = useState({
    dietary_preferences: [],
    allergies: [],
    disliked_ingredients: [],
    cuisine_preferences: [],
    daily_calorie_target: 2000,
    protein_target: 100,
    carbs_target: 200,
    fats_target: 60,
    meals_per_day: 3,
    snacks_per_day: 2,
    preferred_meal_times: {
      breakfast: '08:00',
      lunch: '12:30',
      dinner: '19:00'
    },
    timezone: 'UTC'
  });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const toast = useToast();

  useEffect(() => {
    if (preferences) {
      // Convert ISO 8601 datetime strings back to "HH:MM" format for display
      const convertTimeFromISO = (time: string | undefined): string => {
        if (!time) return '12:00';
        // If already in "HH:MM" format, return as-is
        if (typeof time === 'string' && time.match(/^\d{2}:\d{2}$/)) {
          return time;
        }
        // If in ISO 8601 format (e.g., "2000-01-01T08:00:00"), extract time
        if (typeof time === 'string' && time.includes('T')) {
          const match = time.match(/T(\d{2}):(\d{2})/);
          if (match) {
            return `${match[1]}:${match[2]}`;
          }
        }
        return '12:00'; // Default fallback
      };

      const mealTimes = preferences.preferred_meal_times || {
        breakfast: '08:00',
        lunch: '12:30',
        dinner: '19:00'
      };

      // Convert all meal times from ISO format to HH:MM format
      const convertedMealTimes = Object.fromEntries(
        Object.entries(mealTimes).map(([meal, time]) => [
          meal,
          convertTimeFromISO(time as string)
        ])
      );

      setFormData({
        dietary_preferences: preferences.dietary_preferences || [],
        allergies: preferences.allergies || [],
        disliked_ingredients: preferences.disliked_ingredients || [],
        cuisine_preferences: preferences.cuisine_preferences || [],
        daily_calorie_target: preferences.daily_calorie_target || 2000,
        protein_target: preferences.protein_target || 100,
        carbs_target: preferences.carbs_target || 200,
        fats_target: preferences.fats_target || 60,
        meals_per_day: preferences.meals_per_day || 3,
        snacks_per_day: preferences.snacks_per_day || 2,
        preferred_meal_times: convertedMealTimes,
        timezone: preferences.timezone || 'UTC'
      });
    }
  }, [preferences]);

  const dietaryOptions = [
    'vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'keto', 'paleo',
    'mediterranean', 'low-carb', 'high-protein', 'low-fat', 'diabetic-friendly',
    'heart-healthy', 'anti-inflammatory', 'raw', 'pescatarian'
  ];

  // Conflict detection for dietary preferences
  const dietaryConflicts = {
    'vegan': ['pescatarian', 'keto'],
    'pescatarian': ['vegan'],
    'keto': ['vegan', 'low-carb'],
    'low-carb': ['keto']
  };

  const allergyOptions = [
    'dairy', 'eggs', 'gluten', 'wheat', 'nuts', 'tree-nuts', 'peanuts', 
    'fish', 'shellfish', 'soy', 'sesame', 'mustard', 'sulfites', 'nightshades'
  ];

  const cuisineOptions = [
    'italian', 'mexican', 'asian', 'indian', 'mediterranean', 'american',
    'french', 'thai', 'chinese', 'japanese', 'korean', 'middle-eastern',
    'latin-american', 'european', 'african'
  ];

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleArrayChange = (field: string, values: string[]) => {
    setFormData(prev => ({
      ...prev,
      [field]: values
    }));
  };

  // Check for dietary preference conflicts
  const checkDietaryConflicts = (selectedPreferences: string[]) => {
    const conflicts = [];
    for (const preference of selectedPreferences) {
      if (dietaryConflicts[preference]) {
        for (const conflict of dietaryConflicts[preference]) {
          if (selectedPreferences.includes(conflict)) {
            conflicts.push(`${preference} and ${conflict} may be restrictive together`);
          }
        }
      }
    }
    return conflicts;
  };

  // Validate form data
  const validateForm = () => {
    const errors = [];
    
    // Check dietary conflicts
    const conflicts = checkDietaryConflicts(formData.dietary_preferences);
    if (conflicts.length > 0) {
      errors.push(...conflicts);
    }
    
    // Check nutritional targets
    if (formData.daily_calorie_target < 800 || formData.daily_calorie_target > 5000) {
      errors.push('Daily calorie target must be between 800 and 5000');
    }
    
    if (formData.protein_target < 20 || formData.protein_target > 300) {
      errors.push('Protein target must be between 20g and 300g');
    }
    
    if (formData.carbs_target < 50 || formData.carbs_target > 500) {
      errors.push('Carbs target must be between 50g and 500g');
    }
    
    if (formData.fats_target < 20 || formData.fats_target > 200) {
      errors.push('Fats target must be between 20g and 200g');
    }
    
    // Check macro ratios
    const totalMacros = formData.protein_target + formData.carbs_target + formData.fats_target;
    if (totalMacros < 100 || totalMacros > 1000) {
      errors.push('Total macro targets should be reasonable (100-1000g total)');
    }
    
    return errors;
  };

  const handleMealTimeChange = (meal: string, time: string) => {
    setFormData(prev => ({
      ...prev,
      preferred_meal_times: {
        ...prev.preferred_meal_times,
        [meal]: time
      }
    }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      
      // Validate form before saving
      const validationErrors = validateForm();
      if (validationErrors.length > 0) {
        toast({
          title: 'Validation Error',
          description: validationErrors.join(', '),
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        return;
      }
      
      // Get Supabase session token for authentication
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        toast({
          title: 'Authentication Required',
          description: 'Please log in to save preferences.',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
        return;
      }
      
      // Convert time format "HH:MM" to ISO 8601 datetime format
      // Backend expects ISO 8601 datetime strings, not just time strings
      const preparedData = {
        ...formData,
        preferred_meal_times: formData.preferred_meal_times ? 
          Object.fromEntries(
            Object.entries(formData.preferred_meal_times).map(([meal, time]) => {
              // Convert "08:00" to "2000-01-01T08:00:00" (ISO 8601 format)
              // Using a fixed date since we only care about the time
              if (typeof time === 'string' && time.match(/^\d{2}:\d{2}$/)) {
                return [meal, `2000-01-01T${time}:00`];
              }
              // If already in ISO format, keep it
              return [meal, time];
            })
          ) : undefined
      };

      // Get API base URL from environment or use default
      const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';

      const response = await fetch(`${API_BASE_URL}/nutrition/preferences`, {
        method: preferences ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`,
        },
        body: JSON.stringify(preparedData),
      });

      if (response.ok) {
        toast({
          title: 'Preferences saved successfully!',
          description: 'Your dietary preferences have been updated.',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        onUpdate();
      } else {
        // Extract error message from response
        let errorMessage = 'Failed to save preferences';
        try {
          const errorData = await response.json();
          // Handle Pydantic validation errors (422 response)
          if (errorData.detail && Array.isArray(errorData.detail)) {
            // Extract error messages from validation errors
            errorMessage = errorData.detail
              .map((err: any) => err.msg || err.message || JSON.stringify(err))
              .join(', ');
          } else if (errorData.detail) {
            errorMessage = typeof errorData.detail === 'string' 
              ? errorData.detail 
              : JSON.stringify(errorData.detail);
          } else if (errorData.message) {
            errorMessage = errorData.message;
          }
        } catch (parseError) {
          // If response is not JSON, use status text
          errorMessage = response.statusText || `Server returned ${response.status} error`;
        }
        throw new Error(errorMessage);
      }
    } catch (error: any) {
      console.error('Error saving preferences:', error);
      // Extract error message from various possible formats
      let errorMessage = 'Please try again.';
      if (error?.message) {
        errorMessage = error.message;
      } else if (typeof error === 'string') {
        errorMessage = error;
      } else if (error?.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (Array.isArray(detail)) {
          errorMessage = detail.map((err: any) => err.msg || err.message || JSON.stringify(err)).join(', ');
        } else {
          errorMessage = typeof detail === 'string' ? detail : JSON.stringify(detail);
        }
      }
      
      toast({
        title: 'Error saving preferences',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Box textAlign="center" py={8}>
        <Spinner size="xl" color="blue.500" />
        <Text mt={4}>Loading preferences...</Text>
      </Box>
    );
  }

  return (
    <VStack spacing={6} align="stretch">
      <Box>
        <Heading size="lg" mb={2}>
          {t('nutritionPreferences', 'en')}
        </Heading>
        <Text color="gray.600">
          Set up your dietary preferences, restrictions, and nutritional goals
        </Text>
      </Box>

      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={6}>
        {/* Dietary Preferences */}
        <Card>
          <CardHeader>
            <Heading size="md">{t('dietaryPreferences', 'en')}</Heading>
          </CardHeader>
          <CardBody>
            <FormControl>
              <FormLabel>Select your dietary preferences:</FormLabel>
              <CheckboxGroup
                value={formData.dietary_preferences}
                onChange={(values) => handleArrayChange('dietary_preferences', values as string[])}
              >
                <SimpleGrid columns={2} spacing={2}>
                  {dietaryOptions.map((option) => (
                    <Checkbox key={option} value={option}>
                      {t(option) || option.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </Checkbox>
                  ))}
                </SimpleGrid>
              </CheckboxGroup>
              {checkDietaryConflicts(formData.dietary_preferences).length > 0 && (
                <Alert status="warning" mt={2}>
                  <AlertIcon />
                  <Box>
                    <Text fontSize="sm" fontWeight="bold">Conflicting preferences detected:</Text>
                    {checkDietaryConflicts(formData.dietary_preferences).map((conflict, index) => (
                      <Text key={index} fontSize="sm">• {conflict}</Text>
                    ))}
                  </Box>
                </Alert>
              )}
            </FormControl>
          </CardBody>
        </Card>

        {/* Allergies & Restrictions */}
        <Card>
          <CardHeader>
            <Heading size="md">{t('allergies', 'en')} & Restrictions</Heading>
          </CardHeader>
          <CardBody>
            <FormControl mb={4}>
              <FormLabel>Allergies:</FormLabel>
              <CheckboxGroup
                value={formData.allergies}
                onChange={(values) => handleArrayChange('allergies', values as string[])}
              >
                <SimpleGrid columns={2} spacing={2}>
                  {allergyOptions.map((allergy) => (
                    <Checkbox key={allergy} value={allergy}>
                      {allergy.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </Checkbox>
                  ))}
                </SimpleGrid>
              </CheckboxGroup>
            </FormControl>

            <FormControl>
              <FormLabel>Disliked Ingredients:</FormLabel>
              <Input
                placeholder="Enter ingredients you dislike (comma-separated)"
                value={formData.disliked_ingredients.join(', ')}
                onChange={(e) => {
                  const ingredients = e.target.value.split(',', 'en').map(i => i.trim()).filter(i => i);
                  handleArrayChange('disliked_ingredients', ingredients);
                }}
              />
            </FormControl>
          </CardBody>
        </Card>

        {/* Cuisine Preferences */}
        <Card>
          <CardHeader>
            <Heading size="md">{t('cuisinePreferences', 'en')}</Heading>
          </CardHeader>
          <CardBody>
            <FormControl>
              <FormLabel>Preferred cuisines:</FormLabel>
              <CheckboxGroup
                value={formData.cuisine_preferences}
                onChange={(values) => handleArrayChange('cuisine_preferences', values as string[])}
              >
                <SimpleGrid columns={2} spacing={2}>
                  {cuisineOptions.map((cuisine) => (
                    <Checkbox key={cuisine} value={cuisine}>
                      {t(cuisine) || cuisine.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </Checkbox>
                  ))}
                </SimpleGrid>
              </CheckboxGroup>
            </FormControl>
          </CardBody>
        </Card>

        {/* Nutritional Targets */}
        <Card>
          <CardHeader>
            <Heading size="md">Nutritional Targets</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4}>
              {/* Presets */}
              <FormControl>
                <FormLabel>Quick Presets</FormLabel>
                <HStack spacing={2} wrap="wrap">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setFormData(prev => ({
                        ...prev,
                        daily_calorie_target: 1500,
                        protein_target: 120,
                        carbs_target: 150,
                        fats_target: 50
                      }));
                    }}
                  >
                    Weight Loss
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setFormData(prev => ({
                        ...prev,
                        daily_calorie_target: 2000,
                        protein_target: 150,
                        carbs_target: 250,
                        fats_target: 65
                      }));
                    }}
                  >
                    Maintenance
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setFormData(prev => ({
                        ...prev,
                        daily_calorie_target: 2500,
                        protein_target: 180,
                        carbs_target: 300,
                        fats_target: 80
                      }));
                    }}
                  >
                    Muscle Gain
                  </Button>
                </HStack>
              </FormControl>

              <Divider />

              <FormControl>
                <FormLabel>{t('calorieTarget', 'en')}</FormLabel>
                <NumberInput
                  value={formData.daily_calorie_target}
                  onChange={(value) => handleInputChange('daily_calorie_target', parseInt(value) || 0)}
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
                <Text fontSize="sm" color="gray.500">
                  Range: 800-5000 calories
                </Text>
              </FormControl>

              <FormControl>
                <FormLabel>{t('proteinTarget', 'en')}</FormLabel>
                <NumberInput
                  value={formData.protein_target}
                  onChange={(value) => handleInputChange('protein_target', parseInt(value) || 0)}
                  min={20}
                  max={300}
                >
                  <NumberInputField />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
              </FormControl>

              <FormControl>
                <FormLabel>{t('carbsTarget', 'en')}</FormLabel>
                <NumberInput
                  value={formData.carbs_target}
                  onChange={(value) => handleInputChange('carbs_target', parseInt(value) || 0)}
                  min={50}
                  max={500}
                >
                  <NumberInputField />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
              </FormControl>

              <FormControl>
                <FormLabel>{t('fatsTarget', 'en')}</FormLabel>
                <NumberInput
                  value={formData.fats_target}
                  onChange={(value) => handleInputChange('fats_target', parseInt(value) || 0)}
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
                <Text fontSize="sm" color="gray.500">
                  Range: 20-200g
                </Text>
              </FormControl>

              {/* Macro Split Visualization */}
              <Box w="full" p={4} bg="gray.50" borderRadius="md">
                <Text fontSize="sm" fontWeight="bold" mb={2}>Macro Split</Text>
                <VStack spacing={2}>
                  <HStack w="full" justify="space-between">
                    <Text fontSize="sm">Protein:</Text>
                    <Text fontSize="sm" fontWeight="bold">
                      {Math.round((formData.protein_target * 4 / formData.daily_calorie_target) * 100)}%
                    </Text>
                  </HStack>
                  <HStack w="full" justify="space-between">
                    <Text fontSize="sm">Carbs:</Text>
                    <Text fontSize="sm" fontWeight="bold">
                      {Math.round((formData.carbs_target * 4 / formData.daily_calorie_target) * 100)}%
                    </Text>
                  </HStack>
                  <HStack w="full" justify="space-between">
                    <Text fontSize="sm">Fats:</Text>
                    <Text fontSize="sm" fontWeight="bold">
                      {Math.round((formData.fats_target * 9 / formData.daily_calorie_target) * 100)}%
                    </Text>
                  </HStack>
                </VStack>
              </Box>
            </VStack>
          </CardBody>
        </Card>

        {/* Meal Schedule */}
        <Card>
          <CardHeader>
            <Heading size="md">Meal Schedule</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4}>
              <FormControl>
                <FormLabel>{t('mealsPerDay', 'en')}</FormLabel>
                <Select
                  value={formData.meals_per_day}
                  onChange={(e) => handleInputChange('meals_per_day', parseInt(e.target.value))}
                >
                  <option value={2}>2 meals</option>
                  <option value={3}>3 meals</option>
                  <option value={4}>4 meals</option>
                  <option value={5}>5 meals</option>
                  <option value={6}>6 meals</option>
                </Select>
              </FormControl>

              <FormControl>
                <FormLabel>Snacks per Day</FormLabel>
                <Select
                  value={formData.snacks_per_day}
                  onChange={(e) => handleInputChange('snacks_per_day', parseInt(e.target.value))}
                >
                  <option value={0}>No snacks</option>
                  <option value={1}>1 snack</option>
                  <option value={2}>2 snacks</option>
                  <option value={3}>3 snacks</option>
                  <option value={4}>4 snacks</option>
                  <option value={5}>5 snacks</option>
                </Select>
              </FormControl>

              <Divider />

              <Text fontWeight="semibold">{t('preferredMealTimes', 'en')}</Text>
              
              <VStack spacing={3} align="stretch">
                {Object.entries(formData.preferred_meal_times).map(([meal, time]) => (
                  <HStack key={meal} spacing={3}>
                    <FormControl flex={1}>
                      <FormLabel textTransform="capitalize">{meal}</FormLabel>
                      <Input
                        type="time"
                        value={time}
                        onChange={(e) => handleMealTimeChange(meal, e.target.value)}
                      />
                    </FormControl>
                    {Object.keys(formData.preferred_meal_times).length > 1 && (
                      <Button
                        size="sm"
                        colorScheme="red"
                        variant="outline"
                        onClick={() => {
                          const newTimes = { ...formData.preferred_meal_times };
                          delete newTimes[meal];
                          setFormData(prev => ({
                            ...prev,
                            preferred_meal_times: newTimes
                          }));
                        }}
                      >
                        Remove
                      </Button>
                    )}
                  </HStack>
                ))}
                
                <Button
                  size="sm"
                  variant="outline"
                  leftIcon={<FiPlus />}
                  onClick={() => {
                    const newMeal = `meal_${Date.now()}`;
                    setFormData(prev => ({
                      ...prev,
                      preferred_meal_times: {
                        ...prev.preferred_meal_times,
                        [newMeal]: '12:00'
                      }
                    }));
                  }}
                >
                  Add Meal Time
                </Button>
              </VStack>
            </VStack>
          </CardBody>
        </Card>

        {/* Timezone */}
        <Card>
          <CardHeader>
            <Heading size="md">{t('timezone', 'en')}</Heading>
          </CardHeader>
          <CardBody>
            <FormControl>
              <FormLabel>Select your timezone:</FormLabel>
              <Select
                value={formData.timezone}
                onChange={(e) => handleInputChange('timezone', e.target.value)}
              >
                <option value="UTC">UTC</option>
                <option value="America/New_York">Eastern Time</option>
                <option value="America/Chicago">Central Time</option>
                <option value="America/Denver">Mountain Time</option>
                <option value="America/Los_Angeles">Pacific Time</option>
                <option value="Europe/London">London</option>
                <option value="Europe/Paris">Paris</option>
                <option value="Asia/Tokyo">Tokyo</option>
                <option value="Asia/Shanghai">Shanghai</option>
                <option value="Australia/Sydney">Sydney</option>
              </Select>
            </FormControl>
          </CardBody>
        </Card>
      </SimpleGrid>

      {/* Save Button */}
      <Box textAlign="center">
        <Button
          colorScheme="blue"
          size="lg"
          onClick={handleSave}
          isLoading={saving}
          loadingText="Saving..."
        >
          Save Preferences
        </Button>
      </Box>
    </VStack>
  );
};

export default NutritionPreferences;
