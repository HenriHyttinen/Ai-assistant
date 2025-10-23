import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Badge,
  Select,
  Input,
  useToast,
  SimpleGrid,
  Divider,
  Icon,
  Flex,
  Spinner,
  Alert,
  AlertIcon,
} from '@chakra-ui/react';
import { FiPlus, FiRefreshCw, FiCalendar, FiClock } from 'react-icons/fi';
import { t } from '../../utils/translations';

interface MealPlanningProps {
  mealPlans: any[];
  onUpdate: () => void;
}

const MealPlanning: React.FC<MealPlanningProps> = ({
  mealPlans,
  onUpdate,
}) => {
  const [generating, setGenerating] = useState(false);
  const [planType, setPlanType] = useState<'daily' | 'weekly'>('daily');
  const [startDate, setStartDate] = useState(new Date().toISOString().split('T')[0]);
  const [endDate, setEndDate] = useState('');
  const toast = useToast();

  const handleGenerateMealPlan = async () => {
    try {
      setGenerating(true);
      
      const planRequest = {
        plan_type: planType,
        start_date: startDate,
        end_date: planType === 'weekly' ? endDate : null,
      };

      const response = await fetch('/api/nutrition/meal-plans/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(planRequest),
      });

      if (response.ok) {
        toast({
          title: 'Meal plan generated successfully!',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        onUpdate();
      } else {
        throw new Error('Failed to generate meal plan');
      }
    } catch (error) {
      console.error('Error generating meal plan:', error);
      toast({
        title: 'Error generating meal plan',
        description: 'Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setGenerating(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  return (
    <VStack spacing={6} align="stretch">
      <Box>
        <Heading size="lg" mb={2}>
          {t('mealPlanning')}
        </Heading>
        <Text color="gray.600">
          Generate AI-powered meal plans tailored to your preferences
        </Text>
      </Box>

      {/* Generate New Meal Plan */}
      <Card>
        <CardHeader>
          <Heading size="md">Generate New Meal Plan</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={4}>
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} w="full">
              <Box>
                <Text mb={2} fontWeight="semibold">Plan Type</Text>
                <Select
                  value={planType}
                  onChange={(e) => setPlanType(e.target.value as 'daily' | 'weekly')}
                >
                  <option value="daily">{t('dailyPlan')}</option>
                  <option value="weekly">{t('weeklyPlan')}</option>
                </Select>
              </Box>

              <Box>
                <Text mb={2} fontWeight="semibold">Start Date</Text>
                <Input
                  type="date"
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                />
              </Box>

              {planType === 'weekly' && (
                <Box>
                  <Text mb={2} fontWeight="semibold">End Date</Text>
                  <Input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    min={startDate}
                  />
                </Box>
              )}
            </SimpleGrid>

            <Button
              colorScheme="blue"
              size="lg"
              onClick={handleGenerateMealPlan}
              isLoading={generating}
              loadingText="Generating..."
              leftIcon={<Icon as={FiPlus} />}
            >
              {t('generateMealPlan')}
            </Button>
          </VStack>
        </CardBody>
      </Card>

      {/* Existing Meal Plans */}
      <Box>
        <HStack justify="space-between" mb={4}>
          <Heading size="md">Your Meal Plans</Heading>
          <Button
            variant="outline"
            size="sm"
            onClick={onUpdate}
            leftIcon={<Icon as={FiRefreshCw} />}
          >
            Refresh
          </Button>
        </HStack>

        {mealPlans.length === 0 ? (
          <Alert status="info" borderRadius="lg">
            <AlertIcon />
            <Box>
              <Text fontWeight="semibold">No meal plans yet</Text>
              <Text>Generate your first meal plan to get started!</Text>
            </Box>
          </Alert>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
            {mealPlans.map((plan) => (
              <Card key={plan.id} variant="outline">
                <CardHeader>
                  <HStack justify="space-between">
                    <Heading size="sm">{t('mealPlan')}</Heading>
                    <Badge colorScheme="blue" variant="subtle">
                      {plan.plan_type}
                    </Badge>
                  </HStack>
                </CardHeader>
                <CardBody>
                  <VStack spacing={3} align="stretch">
                    <HStack>
                      <Icon as={FiCalendar} color="gray.500" />
                      <Text fontSize="sm" color="gray.600">
                        {formatDate(plan.start_date)}
                      </Text>
                    </HStack>

                    {plan.end_date && (
                      <HStack>
                        <Icon as={FiCalendar} color="gray.500" />
                        <Text fontSize="sm" color="gray.600">
                          to {formatDate(plan.end_date)}
                        </Text>
                      </HStack>
                    )}

                    <HStack>
                      <Icon as={FiClock} color="gray.500" />
                      <Text fontSize="sm" color="gray.600">
                        {plan.meals?.length || 0} meals
                      </Text>
                    </HStack>

                    <Divider />

                    <HStack justify="space-between">
                      <Button size="sm" variant="outline">
                        View Details
                      </Button>
                      <Button size="sm" colorScheme="blue">
                        Regenerate
                      </Button>
                    </HStack>
                  </VStack>
                </CardBody>
              </Card>
            ))}
          </SimpleGrid>
        )}
      </Box>
    </VStack>
  );
};

export default MealPlanning;
