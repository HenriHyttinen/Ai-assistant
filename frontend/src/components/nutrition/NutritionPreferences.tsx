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
        preferred_meal_times: preferences.preferred_meal_times || {
          breakfast: '08:00',
          lunch: '12:30',
          dinner: '19:00'
        },
        timezone: preferences.timezone || 'UTC'
      });
    }
  }, [preferences]);

  const dietaryOptions = [
    'vegetarian', 'vegan', 'gluten-free', 'dairy-free', 'keto', 'paleo',
    'mediterranean', 'low-carb', 'high-protein', 'low-fat', 'diabetic-friendly',
    'heart-healthy', 'anti-inflammatory', 'raw', 'pescatarian'
  ];

  const allergyOptions = [
    'nuts', 'peanuts', 'tree-nuts', 'dairy', 'eggs', 'soy', 'wheat', 'gluten',
    'fish', 'shellfish', 'sesame', 'mustard', 'sulfites'
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
      
      const response = await fetch('http://localhost:8000/nutrition/preferences', {
        method: preferences ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        toast({
          title: 'Preferences saved successfully!',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        onUpdate();
      } else {
        throw new Error('Failed to save preferences');
      }
    } catch (error) {
      console.error('Error saving preferences:', error);
      toast({
        title: 'Error saving preferences',
        description: 'Please try again.',
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
              <FormControl>
                <FormLabel>{t('calorieTarget', 'en')}</FormLabel>
                <NumberInput
                  value={formData.daily_calorie_target}
                  onChange={(value) => handleInputChange('daily_calorie_target', parseInt(value) || 0)}
                  min={800}
                  max={5000}
                >
                  <NumberInputField />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
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
                >
                  <NumberInputField />
                  <NumberInputStepper>
                    <NumberIncrementStepper />
                    <NumberDecrementStepper />
                  </NumberInputStepper>
                </NumberInput>
              </FormControl>
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

              <Divider />

              <Text fontWeight="semibold">{t('preferredMealTimes', 'en')}</Text>
              
              <FormControl>
                <FormLabel>{t('breakfast', 'en')}</FormLabel>
                <Input
                  type="time"
                  value={formData.preferred_meal_times.breakfast}
                  onChange={(e) => handleMealTimeChange('breakfast', e.target.value)}
                />
              </FormControl>

              <FormControl>
                <FormLabel>{t('lunch', 'en')}</FormLabel>
                <Input
                  type="time"
                  value={formData.preferred_meal_times.lunch}
                  onChange={(e) => handleMealTimeChange('lunch', e.target.value)}
                />
              </FormControl>

              <FormControl>
                <FormLabel>{t('dinner', 'en')}</FormLabel>
                <Input
                  type="time"
                  value={formData.preferred_meal_times.dinner}
                  onChange={(e) => handleMealTimeChange('dinner', e.target.value)}
                />
              </FormControl>
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
