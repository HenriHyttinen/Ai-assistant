import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Button,
  Icon,
  useColorModeValue,
  Card,
  CardBody,
  SimpleGrid,
  Badge,
  Alert,
  AlertIcon,
  Divider,
  Progress,
  Tooltip
} from '@chakra-ui/react';
import { 
  FiTarget, 
  FiTrendingUp, 
  FiTrendingDown,
  FiInfo,
  FiCheck,
  FiAlertTriangle
} from 'react-icons/fi';
import mealPlanRecipeService from '../../services/mealPlanRecipeService';
import type { ServingAdjustmentSuggestion } from '../../services/mealPlanRecipeService';

interface ServingSizeAdjusterProps {
  mealPlanId: string;
  targetCalories?: number;
  targetProtein?: number;
  onServingsUpdated: () => void;
}

const ServingSizeAdjuster: React.FC<ServingSizeAdjusterProps> = ({
  mealPlanId,
  targetCalories,
  targetProtein,
  onServingsUpdated
}) => {
  const [suggestions, setSuggestions] = useState<ServingAdjustmentSuggestion[]>([]);
  const [loading, setLoading] = useState(false);
  const [updating, setUpdating] = useState<{ [key: string]: boolean }>({});

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  useEffect(() => {
    loadSuggestions();
  }, [mealPlanId, targetCalories, targetProtein]);

  const loadSuggestions = async () => {
    try {
      setLoading(true);
      const data = await mealPlanRecipeService.getServingSuggestions(
        mealPlanId,
        targetCalories,
        targetProtein
      );
      setSuggestions(data);
    } catch (error) {
      console.error('Error loading serving suggestions:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleServingsUpdate = async (recipeId: string, newServings: number) => {
    try {
      setUpdating(prev => ({ ...prev, [recipeId]: true }));
      
      // This would need to be implemented in the service
      // For now, we'll just show a success message
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      onServingsUpdated();
    } catch (error) {
      console.error('Error updating servings:', error);
    } finally {
      setUpdating(prev => ({ ...prev, [recipeId]: false }));
    }
  };

  const getAdjustmentColor = (factor: number) => {
    if (factor >= 1.2) return 'green';
    if (factor >= 0.8) return 'blue';
    if (factor >= 0.5) return 'yellow';
    return 'red';
  };

  const getAdjustmentIcon = (factor: number) => {
    if (factor > 1) return <Icon as={FiTrendingUp} />;
    if (factor < 1) return <Icon as={FiTrendingDown} />;
    return <Icon as={FiCheck} />;
  };

  const getAdjustmentMessage = (factor: number, nutrient: string) => {
    if (factor > 1.2) return `Increase by ${Math.round((factor - 1) * 100)}% to meet ${nutrient} target`;
    if (factor < 0.8) return `Decrease by ${Math.round((1 - factor) * 100)}% to meet ${nutrient} target`;
    return `Perfect for ${nutrient} target`;
  };

  if (loading) {
    return (
      <Card>
        <CardBody>
          <HStack justify="center" py={8}>
            <Text>Loading serving suggestions...</Text>
          </HStack>
        </CardBody>
      </Card>
    );
  }

  if (suggestions.length === 0) {
    return (
      <Alert status="info" borderRadius="lg">
        <AlertIcon />
        <VStack align="start" spacing={2}>
          <Text fontWeight="semibold">No adjustments needed</Text>
          <Text fontSize="sm">
            Your current serving sizes are well-balanced for your nutritional targets.
          </Text>
        </VStack>
      </Alert>
    );
  }

  return (
    <VStack spacing={4} align="stretch">
      <HStack justify="space-between">
        <Text fontSize="lg" fontWeight="semibold">Serving Size Adjustments</Text>
        <Button size="sm" variant="outline" onClick={loadSuggestions}>
          Refresh
        </Button>
      </HStack>

      {suggestions.map((suggestion) => (
        <Card key={suggestion.recipe_id} bg={bgColor} borderColor={borderColor}>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <HStack justify="space-between" align="start">
                <VStack align="start" spacing={1} flex="1">
                  <Text fontWeight="semibold">{suggestion.recipe_title}</Text>
                  <Text fontSize="sm" color="gray.500">
                    Current: {suggestion.current_servings} servings
                  </Text>
                </VStack>
                <Badge colorScheme="blue" variant="outline">
                  {Object.keys(suggestion.adjustments).length} suggestions
                </Badge>
              </HStack>

              <Divider />

              <VStack spacing={3} align="stretch">
                {Object.entries(suggestion.adjustments).map(([nutrient, adjustment]) => (
                  <Box key={nutrient}>
                    <HStack justify="space-between" mb={2}>
                      <HStack spacing={2}>
                        <Icon 
                          as={getAdjustmentIcon(adjustment.factor)} 
                          color={`${getAdjustmentColor(adjustment.factor)}.500`}
                        />
                        <Text fontWeight="semibold" textTransform="capitalize">
                          {nutrient} Target
                        </Text>
                      </HStack>
                      <Badge colorScheme={getAdjustmentColor(adjustment.factor)}>
                        {adjustment.factor.toFixed(2)}x
                      </Badge>
                    </HStack>

                    <VStack spacing={2} align="stretch">
                      <HStack justify="space-between">
                        <Text fontSize="sm" color="gray.600">
                          Suggested servings: {adjustment.new_servings.toFixed(1)}
                        </Text>
                        <Text fontSize="sm" color="gray.600">
                          New {nutrient}: {adjustment.new_value.toFixed(0)}
                        </Text>
                      </HStack>

                      <Progress 
                        value={Math.min(adjustment.factor * 50, 100)} 
                        colorScheme={getAdjustmentColor(adjustment.factor)}
                        size="sm"
                      />

                      <Text fontSize="xs" color="gray.500">
                        {getAdjustmentMessage(adjustment.factor, nutrient)}
                      </Text>

                      <HStack spacing={2}>
                        <NumberInput
                          size="sm"
                          value={adjustment.new_servings}
                          onChange={(_, value) => {
                            // Update the suggestion in real-time
                            const newSuggestions = suggestions.map(s => 
                              s.recipe_id === suggestion.recipe_id 
                                ? {
                                    ...s,
                                    adjustments: {
                                      ...s.adjustments,
                                      [nutrient]: {
                                        ...adjustment,
                                        new_servings: value
                                      }
                                    }
                                  }
                                : s
                            );
                            setSuggestions(newSuggestions);
                          }}
                          min={0.25}
                          max={10}
                          step={0.25}
                          precision={2}
                          w="100px"
                        >
                          <NumberInputField />
                          <NumberInputStepper>
                            <NumberIncrementStepper />
                            <NumberDecrementStepper />
                          </NumberInputStepper>
                        </NumberInput>

                        <Button
                          size="sm"
                          colorScheme={getAdjustmentColor(adjustment.factor)}
                          onClick={() => handleServingsUpdate(
                            suggestion.recipe_id, 
                            adjustment.new_servings
                          )}
                          isLoading={updating[suggestion.recipe_id]}
                          loadingText="Updating..."
                        >
                          Apply
                        </Button>
                      </HStack>
                    </VStack>
                  </Box>
                ))}
              </VStack>

              <Divider />

              <HStack justify="space-between">
                <Text fontSize="sm" color="gray.600">
                  Multiple adjustments available
                </Text>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    // Apply all adjustments at once
                    Object.entries(suggestion.adjustments).forEach(([_, adjustment]) => {
                      handleServingsUpdate(suggestion.recipe_id, adjustment.new_servings);
                    });
                  }}
                  isLoading={updating[suggestion.recipe_id]}
                >
                  Apply All
                </Button>
              </HStack>
            </VStack>
          </CardBody>
        </Card>
      ))}

      <Alert status="info" borderRadius="lg">
        <AlertIcon />
        <VStack align="start" spacing={2}>
          <Text fontWeight="semibold">How it works</Text>
          <Text fontSize="sm">
            These suggestions help you adjust serving sizes to better meet your nutritional targets. 
            The adjustments are calculated based on your current meal plan and target values.
          </Text>
        </VStack>
      </Alert>
    </VStack>
  );
};

export default ServingSizeAdjuster;
