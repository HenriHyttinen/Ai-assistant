import {
  Box,
  Heading,
  FormControl,
  FormLabel,
  Input,
  Select,
  Button,
  VStack,
  HStack,
  Text,
  Card,
  CardBody,
  SimpleGrid,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  Textarea,
} from '@chakra-ui/react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { useState, useEffect } from 'react';
import { healthProfile, analytics, settings } from '../services/api';
import { 
  convertWeightForDisplay, 
  convertWeightToKg, 
  convertHeightForDisplay, 
  convertHeightToCm,
  getWeightUnit,
  getHeightUnit,
  getTargetWeightUnit
} from '../utils/unitConversion';

function toSafeErrorString(value: any): string {
  if (!value) return 'Unexpected error';
  if (typeof value === 'string') return value;
  if (Array.isArray(value)) {
    const msgs = value
      .map((v) => (typeof v === 'string' ? v : v?.msg || v?.message))
      .filter(Boolean);
    if (msgs.length > 0) return msgs.join(', ');
  }
  if (typeof value === 'object') {
    if (value.msg || value.message) return value.msg || value.message;
    try {
      return JSON.stringify(value);
    } catch {
      return 'Unexpected error';
    }
  }
  return String(value);
}

function prepareNumericSafePayload(values: any): any {
  const numericFields = [
    'age',
    'height',
    'weight',
    'weekly_activity_frequency',
    'current_endurance_minutes',
    'pushup_count',
    'squat_count',
    'endurance_level',
    'target_weight',
  ];
  const payload: any = {};
  Object.entries(values).forEach(([key, value]) => {
    if (value === '' || value === null || typeof value === 'undefined') {
      return;
    }
    if (numericFields.includes(key)) {
      const num = Number(value);
      if (!Number.isNaN(num)) {
        payload[key] = num;
      }
      return;
    }
    payload[key] = value;
  });
  return payload;
}

const validationSchema = Yup.object({
  age: Yup.number().required('Age is required').min(13, 'Must be at least 13 years old'),
  gender: Yup.string().required('Gender is required'),
  height: Yup.number().required('Height is required').min(100, 'Height must be at least 100cm'),
  weight: Yup.number().required('Weight is required').min(30, 'Weight must be at least 30kg'),
  occupation_type: Yup.string().required('Occupation type is required'),
  activity_level: Yup.string().required('Activity level is required'),
  fitness_goal: Yup.string().required('Primary goal is required'),
  weekly_activity_frequency: Yup.number()
    .required('Weekly activity frequency is required')
    .min(0, 'Must be between 0 and 7')
    .max(7, 'Must be between 0 and 7'),
  current_endurance_minutes: Yup.number().min(0, 'Must be 0 or greater'),
  pushup_count: Yup.number().min(0, 'Must be 0 or greater'),
  squat_count: Yup.number().min(0, 'Must be 0 or greater'),
});

interface HealthMetrics {
  bmi: number;
  wellness_score: number;
  activity_level: string;
  progress: number;
}

const Profile = () => {
  const toast = useToast();
  const [profileData, setProfileData] = useState<any>(null);
  const [metrics, setMetrics] = useState<HealthMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [needsCreate, setNeedsCreate] = useState(false);
  const [measurementSystem, setMeasurementSystem] = useState<'metric' | 'imperial'>('metric');

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Load measurement system settings first
        try {
          const settingsResponse = await settings.getSettings();
          setMeasurementSystem(settingsResponse.data.measurementSystem);
        } catch (settingsError) {
          // Settings not found, using default metric system
        }
        
        const response = await healthProfile.getProfile();
        setProfileData(response.data);
        
        // Fetch analytics for metrics
        const analyticsResponse = await analytics.getAnalytics();
        const analyticsData = analyticsResponse.data;
        
        setMetrics({
          bmi: analyticsData.current_bmi,
          wellness_score: analyticsData.current_wellness_score,
          activity_level: response.data.activity_level,
          progress: analyticsData.progress_towards_goal,
        });
      } catch (err: any) {
        if (err?.response?.status === 404) {
          setNeedsCreate(true);
          setError(null);
        } else {
          const detail = err?.response?.data?.detail ?? 'Failed to load profile';
          setError(toSafeErrorString(detail));
        }
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, []);


  const formik = useFormik({
    initialValues: {
      age: profileData?.age || '',
      gender: profileData?.gender || '',
      height: profileData?.height ? convertHeightForDisplay(profileData.height, measurementSystem) : '',
      weight: profileData?.weight ? convertWeightForDisplay(profileData.weight, measurementSystem) : '',
      occupation_type: profileData?.occupation_type || '',
      activity_level: profileData?.activity_level || '',
      fitness_goal: profileData?.fitness_goal || '',
      target_weight: profileData?.target_weight ? convertWeightForDisplay(profileData.target_weight, measurementSystem) : '',
      target_activity_level: profileData?.target_activity_level || '',
      preferred_exercise_time: profileData?.preferred_exercise_time || '',
      preferred_exercise_environment: profileData?.preferred_exercise_environment || '',
      weekly_activity_frequency: profileData?.weekly_activity_frequency || '',
      exercise_types: profileData?.exercise_types || '',
      average_session_duration: profileData?.average_session_duration || '',
      fitness_level: profileData?.fitness_level || '',
      endurance_level: profileData?.endurance_level || '',
      strength_indicators: profileData?.strength_indicators || '',
      current_endurance_minutes: profileData?.current_endurance_minutes || '',
      pushup_count: profileData?.pushup_count || '',
      squat_count: profileData?.squat_count || '',
      dietary_preferences: profileData?.dietary_preferences || '',
      dietary_restrictions: profileData?.dietary_restrictions || '',
      meal_preferences: profileData?.meal_preferences || '',
    },
    validationSchema,
    enableReinitialize: true,
    onSubmit: async (values: any) => {
      try {
        setSaving(true);
        const payload = prepareNumericSafePayload(values);
        
        // Convert units to metric (kg, cm) for backend storage
        if (payload.weight) {
          payload.weight = convertWeightToKg(payload.weight, measurementSystem);
        }
        if (payload.height) {
          payload.height = convertHeightToCm(payload.height, measurementSystem);
        }
        if (payload.target_weight) {
          payload.target_weight = convertWeightToKg(payload.target_weight, measurementSystem);
        }
        
        if (needsCreate) {
          await healthProfile.createProfile(payload);
          setNeedsCreate(false);
        } else {
          await healthProfile.updateProfile(payload);
        }
        toast({
          title: needsCreate ? 'Profile Created' : 'Profile Updated',
          description: needsCreate
            ? 'Your health profile has been created successfully.'
            : 'Your health profile has been updated successfully.',
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
        
        // Refresh data
        const response = await healthProfile.getProfile();
        setProfileData(response.data);
        // Refresh analytics metrics after creation/update
        try {
          const analyticsResponse = await analytics.getAnalytics();
          const analyticsData = analyticsResponse.data;
          setMetrics({
            bmi: analyticsData.current_bmi,
            wellness_score: analyticsData.current_wellness_score,
            activity_level: response.data.activity_level,
            progress: analyticsData.progress_towards_goal,
          });
        } catch (_) {
          // ignore analytics failure here
        }
      } catch (err: any) {
        toast({
          title: 'Update Failed',
          description: toSafeErrorString(err?.response?.data?.detail ?? 'Failed to update profile'),
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setSaving(false);
      }
    },
  });

  // Reload form when measurement system changes
  useEffect(() => {
    if (profileData) {
      const convertedValues = {
        ...formik.values,
        height: profileData?.height ? convertHeightForDisplay(profileData.height, measurementSystem) : '',
        weight: profileData?.weight ? convertWeightForDisplay(profileData.weight, measurementSystem) : '',
        target_weight: profileData?.target_weight ? convertWeightForDisplay(profileData.target_weight, measurementSystem) : '',
      };
      
      formik.setValues(convertedValues);
    }
  }, [measurementSystem]);

  // Reload measurement system when page becomes visible (user navigates back from Settings)
  useEffect(() => {
    const handleFocus = async () => {
      if (profileData) {
        try {
          const settingsResponse = await settings.getSettings();
          const newMeasurementSystem = settingsResponse.data.measurementSystem;
          if (newMeasurementSystem !== measurementSystem) {
            setMeasurementSystem(newMeasurementSystem);
          }
        } catch (settingsError) {
          // Settings not found, using current measurement system
        }
      }
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [measurementSystem, profileData]);

  if (loading) {
    return (
      <Box p={4} display="flex" justifyContent="center" alignItems="center" minH="400px">
        <Spinner size="xl" />
      </Box>
    );
  }

  if (error) {
    return (
      <Box p={4}>
        <Alert status="error">
          <AlertIcon />
          {error}
        </Alert>
      </Box>
    );
  }

  return (
    <Box p={4}>
      <Heading mb={6}>Health Profile</Heading>
      {needsCreate && (
        <Box mb={6}>
          <Alert status="info">
            <AlertIcon />
            No health profile found. Please fill the form below to create one.
          </Alert>
        </Box>
      )}

      <form onSubmit={formik.handleSubmit}>
        <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={8}>
          {/* Basic Information */}
          <Card>
            <CardBody>
              <Heading size="md" mb={4}>Basic Information</Heading>
              <VStack spacing={4} align="stretch">
                <FormControl isInvalid={formik.touched.age && formik.errors.age}>
                  <FormLabel>Age</FormLabel>
                  <Input
                    type="number"
                    {...formik.getFieldProps('age')}
                  />
                  {formik.touched.age && formik.errors.age && (
                    <Text color="red.500" fontSize="sm">{formik.errors.age}</Text>
                  )}
                </FormControl>

                <FormControl isInvalid={formik.touched.gender && formik.errors.gender}>
                  <FormLabel>Gender</FormLabel>
                  <Select {...formik.getFieldProps('gender')}>
                    <option value="">Select gender</option>
                    <option value="male">Male</option>
                    <option value="female">Female</option>
                    <option value="other">Other</option>
                  </Select>
                  {formik.touched.gender && formik.errors.gender && (
                    <Text color="red.500" fontSize="sm">{formik.errors.gender}</Text>
                  )}
                </FormControl>

                <HStack>
                  <FormControl isInvalid={formik.touched.height && formik.errors.height}>
                    <FormLabel>Height ({getHeightUnit(measurementSystem)})</FormLabel>
                    <Input
                      type="number"
                      {...formik.getFieldProps('height')}
                    />
                    {formik.touched.height && formik.errors.height && (
                      <Text color="red.500" fontSize="sm">{formik.errors.height}</Text>
                    )}
                  </FormControl>

                  <FormControl isInvalid={formik.touched.weight && formik.errors.weight}>
                    <FormLabel>Weight ({getWeightUnit(measurementSystem)})</FormLabel>
                    <Input
                      type="number"
                      {...formik.getFieldProps('weight')}
                    />
                    {formik.touched.weight && formik.errors.weight && (
                      <Text color="red.500" fontSize="sm">{formik.errors.weight}</Text>
                    )}
                  </FormControl>
                </HStack>

                <FormControl isInvalid={formik.touched.occupation_type && formik.errors.occupation_type}>
                  <FormLabel>Occupation Type</FormLabel>
                  <Select {...formik.getFieldProps('occupation_type')}>
                    <option value="">Select occupation type</option>
                    <option value="sedentary">Sedentary (Office work)</option>
                    <option value="light">Light (Standing work)</option>
                    <option value="moderate">Moderate (Physical work)</option>
                    <option value="active">Active (Heavy physical work)</option>
                  </Select>
                  {formik.touched.occupation_type && formik.errors.occupation_type && (
                    <Text color="red.500" fontSize="sm">{formik.errors.occupation_type}</Text>
                  )}
                </FormControl>

                <FormControl isInvalid={formik.touched.activity_level && formik.errors.activity_level}>
                  <FormLabel>Activity Level</FormLabel>
                  <Select {...formik.getFieldProps('activity_level')}>
                    <option value="">Select activity level</option>
                    <option value="sedentary">Sedentary</option>
                    <option value="light">Light</option>
                    <option value="moderate">Moderate</option>
                    <option value="active">Active</option>
                    <option value="very_active">Very Active</option>
                  </Select>
                  {formik.touched.activity_level && formik.errors.activity_level && (
                    <Text color="red.500" fontSize="sm">{formik.errors.activity_level}</Text>
                  )}
                </FormControl>
              </VStack>
            </CardBody>
          </Card>

          {/* Dietary Information */}
          <Card>
            <CardBody>
              <Heading size="md" mb={4}>Dietary Information</Heading>
              <VStack spacing={4} align="stretch">
                <FormControl>
                  <FormLabel>Dietary Preferences</FormLabel>
                  <Textarea
                    placeholder="e.g., vegetarian, vegan, Mediterranean diet, low-carb..."
                    {...formik.getFieldProps('dietary_preferences')}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Dietary Restrictions</FormLabel>
                  <Textarea
                    placeholder="e.g., gluten-free, dairy-free, nut allergies..."
                    {...formik.getFieldProps('dietary_restrictions')}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Meal Preferences</FormLabel>
                  <Textarea
                    placeholder="e.g., prefer breakfast, skip lunch, heavy dinner..."
                    {...formik.getFieldProps('meal_preferences')}
                  />
                </FormControl>
              </VStack>
            </CardBody>
          </Card>

          {/* Fitness Goals */}
          <Card>
            <CardBody>
              <Heading size="md" mb={4}>Fitness Goals</Heading>
              <VStack spacing={4} align="stretch">
                <FormControl isInvalid={formik.touched.fitness_goal && formik.errors.fitness_goal}>
                  <FormLabel>Primary Goal</FormLabel>
                  <Select {...formik.getFieldProps('fitness_goal')}>
                    <option value="">Select primary goal</option>
                    <option value="weight_loss">Weight Loss</option>
                    <option value="muscle_gain">Muscle Gain</option>
                    <option value="general_fitness">General Fitness</option>
                    <option value="endurance">Endurance</option>
                    <option value="strength">Strength</option>
                  </Select>
                  {formik.touched.fitness_goal && formik.errors.fitness_goal && (
                    <Text color="red.500" fontSize="sm">{formik.errors.fitness_goal}</Text>
                  )}
                </FormControl>

                <HStack>
                  <FormControl>
                    <FormLabel>Target Weight ({getTargetWeightUnit(measurementSystem)})</FormLabel>
                    <Input
                      type="number"
                      {...formik.getFieldProps('target_weight')}
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel>Target Activity Level</FormLabel>
                    <Select {...formik.getFieldProps('target_activity_level')}>
                      <option value="">Select target level</option>
                      <option value="sedentary">Sedentary</option>
                      <option value="light">Light</option>
                      <option value="moderate">Moderate</option>
                      <option value="active">Active</option>
                      <option value="very_active">Very Active</option>
                    </Select>
                  </FormControl>
                </HStack>

                <FormControl isInvalid={formik.touched.weekly_activity_frequency && formik.errors.weekly_activity_frequency}>
                  <FormLabel>Weekly Activity Frequency (days)</FormLabel>
                  <Input
                    type="number"
                    min="0"
                    max="7"
                    {...formik.getFieldProps('weekly_activity_frequency')}
                  />
                  {formik.touched.weekly_activity_frequency && formik.errors.weekly_activity_frequency && (
                    <Text color="red.500" fontSize="sm">{formik.errors.weekly_activity_frequency}</Text>
                  )}
                </FormControl>
              </VStack>
            </CardBody>
          </Card>

          {/* Exercise Preferences */}
          <Card>
            <CardBody>
              <Heading size="md" mb={4}>Exercise Preferences</Heading>
              <VStack spacing={4} align="stretch">
                <FormControl>
                  <FormLabel>Preferred Exercise Time</FormLabel>
                  <Select {...formik.getFieldProps('preferred_exercise_time')}>
                    <option value="">Select preferred time</option>
                    <option value="morning">Morning</option>
                    <option value="afternoon">Afternoon</option>
                    <option value="evening">Evening</option>
                    <option value="flexible">Flexible</option>
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel>Preferred Exercise Environment</FormLabel>
                  <Select {...formik.getFieldProps('preferred_exercise_environment')}>
                    <option value="">Select environment</option>
                    <option value="home">Home</option>
                    <option value="gym">Gym</option>
                    <option value="outdoors">Outdoors</option>
                    <option value="mixed">Mixed</option>
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel>Exercise Types</FormLabel>
                  <Textarea
                    placeholder="e.g., cardio, strength training, yoga, swimming..."
                    {...formik.getFieldProps('exercise_types')}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>Average Session Duration</FormLabel>
                  <Select {...formik.getFieldProps('average_session_duration')}>
                    <option value="">Select duration</option>
                    <option value="15-30min">15-30 minutes</option>
                    <option value="30-60min">30-60 minutes</option>
                    <option value="60+min">60+ minutes</option>
                  </Select>
                </FormControl>
              </VStack>
            </CardBody>
          </Card>

          {/* Fitness Assessment */}
          <Card>
            <CardBody>
              <Heading size="md" mb={4}>Fitness Assessment</Heading>
              <VStack spacing={4} align="stretch">
                <FormControl>
                  <FormLabel>Fitness Level</FormLabel>
                  <Select {...formik.getFieldProps('fitness_level')}>
                    <option value="">Select fitness level</option>
                    <option value="beginner">Beginner</option>
                    <option value="intermediate">Intermediate</option>
                    <option value="advanced">Advanced</option>
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel>Endurance Level (1-10)</FormLabel>
                  <Input
                    type="number"
                    min="1"
                    max="10"
                    {...formik.getFieldProps('endurance_level')}
                  />
                </FormControl>

                <FormControl isInvalid={formik.touched.current_endurance_minutes && formik.errors.current_endurance_minutes}>
                  <FormLabel>Current Endurance (minutes)</FormLabel>
                  <Input
                    type="number"
                    placeholder="How long can you run/walk?"
                    {...formik.getFieldProps('current_endurance_minutes')}
                  />
                  {formik.touched.current_endurance_minutes && formik.errors.current_endurance_minutes && (
                    <Text color="red.500" fontSize="sm">{formik.errors.current_endurance_minutes}</Text>
                  )}
                </FormControl>

                <HStack>
                  <FormControl isInvalid={formik.touched.pushup_count && formik.errors.pushup_count}>
                    <FormLabel>Push-ups (max)</FormLabel>
                    <Input
                      type="number"
                      {...formik.getFieldProps('pushup_count')}
                    />
                    {formik.touched.pushup_count && formik.errors.pushup_count && (
                      <Text color="red.500" fontSize="sm">{formik.errors.pushup_count}</Text>
                    )}
                  </FormControl>

                  <FormControl isInvalid={formik.touched.squat_count && formik.errors.squat_count}>
                    <FormLabel>Squats (max)</FormLabel>
                    <Input
                      type="number"
                      {...formik.getFieldProps('squat_count')}
                    />
                    {formik.touched.squat_count && formik.errors.squat_count && (
                      <Text color="red.500" fontSize="sm">{formik.errors.squat_count}</Text>
                    )}
                  </FormControl>
                </HStack>

                <FormControl>
                  <FormLabel>Strength Indicators</FormLabel>
                  <Textarea
                    placeholder="e.g., can lift X kg, can do X pull-ups..."
                    {...formik.getFieldProps('strength_indicators')}
                  />
                </FormControl>
              </VStack>
            </CardBody>
          </Card>

          {/* Current Health Metrics */}
          <Card>
            <CardBody>
              <Heading size="md" mb={4}>Current Health Metrics</Heading>
              <VStack spacing={4} align="stretch">
                <Box>
                  <Text fontWeight="bold">BMI</Text>
                  <Text fontSize="xl">{metrics?.bmi ? metrics.bmi.toFixed(1) : 'Calculating...'}</Text>
                </Box>
                <Box>
                  <Text fontWeight="bold">Wellness Score</Text>
                  <Text fontSize="xl">{metrics?.wellness_score ? metrics.wellness_score.toFixed(1) : 'Calculating...'}</Text>
                </Box>
                <Box>
                  <Text fontWeight="bold">Activity Level</Text>
                  <Text fontSize="xl">{metrics?.activity_level || 'Not set'}</Text>
                </Box>
                <Box>
                  <Text fontWeight="bold">Progress Towards Goal</Text>
                  <Text fontSize="xl">{metrics?.progress ? `${metrics.progress.toFixed(1)}%` : 'Calculating...'}</Text>
                </Box>
              </VStack>
            </CardBody>
          </Card>
        </SimpleGrid>

        <Box mt={8} textAlign="center">
          <Button
            type="submit"
            colorScheme="blue"
            size="lg"
            isLoading={saving}
          >
            Save Profile
          </Button>
        </Box>
      </form>
    </Box>
  );
};

export default Profile; 