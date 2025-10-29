import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Card,
  CardBody,
  CardHeader,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Badge,
  Icon,
  useColorModeValue,
  Progress,
  Divider,
  Alert,
  AlertIcon,
  Spinner,
  Button,
  useDisclosure
} from '@chakra-ui/react';
import { 
  FiTarget, 
  FiTrendingUp, 
  FiTrendingDown,
  FiCheck,
  FiAlertTriangle,
  FiBarChart,
  FiRefreshCw
} from 'react-icons/fi';
import mealPlanRecipeService from '../../services/mealPlanRecipeService';
import type { NutritionSummary } from '../../services/mealPlanRecipeService';
import ServingSizeAdjuster from './ServingSizeAdjuster';

interface MealPlanNutritionSummaryProps {
  mealPlanId: string;
  mealDate?: string;
  targetCalories?: number;
  targetProtein?: number;
  targetCarbs?: number;
  targetFat?: number;
}

const MealPlanNutritionSummary: React.FC<MealPlanNutritionSummaryProps> = ({
  mealPlanId,
  mealDate,
  targetCalories,
  targetProtein,
  targetCarbs,
  targetFat
}) => {
  const [summary, setSummary] = useState<NutritionSummary | null>(null);
  const [loading, setLoading] = useState(false);
  const [refreshing, setRefreshing] = useState(false);
  const { isOpen, onOpen, onClose } = useDisclosure();

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  useEffect(() => {
    loadNutritionSummary();
  }, [mealPlanId, mealDate]);

  const loadNutritionSummary = async () => {
    try {
      setLoading(true);
      const data = await mealPlanRecipeService.getNutritionSummary(mealPlanId, mealDate);
      setSummary(data);
    } catch (error) {
      console.error('Error loading nutrition summary:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadNutritionSummary();
    setRefreshing(false);
  };

  const getTargetStatus = (current: number, target: number | undefined, nutrient: string) => {
    if (!target) return { status: 'neutral', message: 'No target set', color: 'gray' };
    
    const percentage = (current / target) * 100;
    
    if (percentage >= 90 && percentage <= 110) {
      return { status: 'good', message: 'On target', color: 'green' };
    } else if (percentage < 90) {
      return { status: 'low', message: `${Math.round(100 - percentage)}% below target`, color: 'red' };
    } else {
      return { status: 'high', message: `${Math.round(percentage - 100)}% above target`, color: 'orange' };
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'good':
        return <Icon as={FiCheck} color="green.500" />;
      case 'low':
        return <Icon as={FiTrendingDown} color="red.500" />;
      case 'high':
        return <Icon as={FiTrendingUp} color="orange.500" />;
      default:
        return <Icon as={FiTarget} color="gray.500" />;
    }
  };

  if (loading) {
    return (
      <Card>
        <CardBody>
          <HStack justify="center" py={8}>
            <Spinner />
            <Text>Loading nutrition summary...</Text>
          </HStack>
        </CardBody>
      </Card>
    );
  }

  if (!summary) {
    return (
      <Alert status="error" borderRadius="lg">
        <AlertIcon />
        <Text>Failed to load nutrition summary</Text>
      </Alert>
    );
  }

  const caloriesStatus = getTargetStatus(summary.total_nutrition.calories, targetCalories, 'calories');
  const proteinStatus = getTargetStatus(summary.total_nutrition.protein, targetProtein, 'protein');
  const carbsStatus = getTargetStatus(summary.total_nutrition.carbs, targetCarbs, 'carbs');
  const fatStatus = getTargetStatus(summary.total_nutrition.fat, targetFat, 'fat');

  return (
    <VStack spacing={6} align="stretch">
      {/* Header */}
      <HStack justify="space-between">
        <Text fontSize="lg" fontWeight="semibold">Nutrition Summary</Text>
        <HStack spacing={2}>
          <Button
            size="sm"
            variant="outline"
            onClick={handleRefresh}
            isLoading={refreshing}
            leftIcon={<Icon as={FiRefreshCw} />}
          >
            Refresh
          </Button>
          <Button
            size="sm"
            colorScheme="blue"
            onClick={onOpen}
            leftIcon={<Icon as={FiBarChart} />}
          >
            Adjust Servings
          </Button>
        </HStack>
      </HStack>

      {/* Total Nutrition */}
      <Card>
        <CardHeader>
          <Text fontSize="md" fontWeight="semibold">Total Nutrition</Text>
        </CardHeader>
        <CardBody>
          <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
            <Stat>
              <StatLabel>Calories</StatLabel>
              <StatNumber>{summary.total_nutrition.calories.toFixed(0)}</StatNumber>
              <StatHelpText>
                <HStack spacing={1}>
                  {getStatusIcon(caloriesStatus.status)}
                  <Text fontSize="xs" color={`${caloriesStatus.color}.500`}>
                    {caloriesStatus.message}
                  </Text>
                </HStack>
              </StatHelpText>
              {targetCalories && (
                <Progress 
                  value={Math.min((summary.total_nutrition.calories / targetCalories) * 100, 100)} 
                  colorScheme={caloriesStatus.color}
                  size="sm"
                  mt={2}
                />
              )}
            </Stat>

            <Stat>
              <StatLabel>Protein</StatLabel>
              <StatNumber>{summary.total_nutrition.protein.toFixed(1)}g</StatNumber>
              <StatHelpText>
                <HStack spacing={1}>
                  {getStatusIcon(proteinStatus.status)}
                  <Text fontSize="xs" color={`${proteinStatus.color}.500`}>
                    {proteinStatus.message}
                  </Text>
                </HStack>
              </StatHelpText>
              {targetProtein && (
                <Progress 
                  value={Math.min((summary.total_nutrition.protein / targetProtein) * 100, 100)} 
                  colorScheme={proteinStatus.color}
                  size="sm"
                  mt={2}
                />
              )}
            </Stat>

            <Stat>
              <StatLabel>Carbs</StatLabel>
              <StatNumber>{summary.total_nutrition.carbs.toFixed(1)}g</StatNumber>
              <StatHelpText>
                <HStack spacing={1}>
                  {getStatusIcon(carbsStatus.status)}
                  <Text fontSize="xs" color={`${carbsStatus.color}.500`}>
                    {carbsStatus.message}
                  </Text>
                </HStack>
              </StatHelpText>
              {targetCarbs && (
                <Progress 
                  value={Math.min((summary.total_nutrition.carbs / targetCarbs) * 100, 100)} 
                  colorScheme={carbsStatus.color}
                  size="sm"
                  mt={2}
                />
              )}
            </Stat>

            <Stat>
              <StatLabel>Fat</StatLabel>
              <StatNumber>{summary.total_nutrition.fat.toFixed(1)}g</StatNumber>
              <StatHelpText>
                <HStack spacing={1}>
                  {getStatusIcon(fatStatus.status)}
                  <Text fontSize="xs" color={`${fatStatus.color}.500`}>
                    {fatStatus.message}
                  </Text>
                </HStack>
              </StatHelpText>
              {targetFat && (
                <Progress 
                  value={Math.min((summary.total_nutrition.fat / targetFat) * 100, 100)} 
                  colorScheme={fatStatus.color}
                  size="sm"
                  mt={2}
                />
              )}
            </Stat>
          </SimpleGrid>
        </CardBody>
      </Card>

      {/* Meal Type Breakdown */}
      <Card>
        <CardHeader>
          <Text fontSize="md" fontWeight="semibold">Meal Type Breakdown</Text>
        </CardHeader>
        <CardBody>
          <VStack spacing={4} align="stretch">
            {Object.entries(summary.meal_type_breakdown).map(([mealType, nutrition]) => (
              <Box key={mealType}>
                <HStack justify="space-between" mb={2}>
                  <Text fontWeight="semibold" textTransform="capitalize">
                    {mealType.replace('_', ' ')}
                  </Text>
                  <Badge colorScheme="blue" variant="outline">
                    {nutrition.recipe_count} recipe{nutrition.recipe_count !== 1 ? 's' : ''}
                  </Badge>
                </HStack>
                
                <SimpleGrid columns={4} spacing={4}>
                  <Text fontSize="sm" color="gray.600">
                    {nutrition.calories.toFixed(0)} cal
                  </Text>
                  <Text fontSize="sm" color="gray.600">
                    {nutrition.protein.toFixed(1)}g protein
                  </Text>
                  <Text fontSize="sm" color="gray.600">
                    {nutrition.carbs.toFixed(1)}g carbs
                  </Text>
                  <Text fontSize="sm" color="gray.600">
                    {nutrition.fat.toFixed(1)}g fat
                  </Text>
                </SimpleGrid>
              </Box>
            ))}
          </VStack>
        </CardBody>
      </Card>

      {/* Summary Stats */}
      <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
        <Card>
          <CardBody textAlign="center">
            <Stat>
              <StatLabel>Total Recipes</StatLabel>
              <StatNumber>{summary.recipe_count}</StatNumber>
              <StatHelpText>in this meal plan</StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card>
          <CardBody textAlign="center">
            <Stat>
              <StatLabel>Avg Calories</StatLabel>
              <StatNumber>
                {summary.recipe_count > 0 
                  ? (summary.total_nutrition.calories / summary.recipe_count).toFixed(0)
                  : 0
                }
              </StatNumber>
              <StatHelpText>per recipe</StatHelpText>
            </Stat>
          </CardBody>
        </Card>

        <Card>
          <CardBody textAlign="center">
            <Stat>
              <StatLabel>Date</StatLabel>
              <StatNumber fontSize="lg">
                {summary.date 
                  ? new Date(summary.date).toLocaleDateString()
                  : 'All dates'
                }
              </StatNumber>
            </Stat>
          </CardBody>
        </Card>
      </SimpleGrid>

      {/* Serving Size Adjuster Modal */}
      <ServingSizeAdjuster
        mealPlanId={mealPlanId}
        targetCalories={targetCalories}
        targetProtein={targetProtein}
        onServingsUpdated={loadNutritionSummary}
      />
    </VStack>
  );
};

export default MealPlanNutritionSummary;
