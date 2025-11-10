import React from 'react';
import {
  Box,
  Card,
  CardHeader,
  CardBody,
  Heading,
  Text,
  VStack,
  HStack,
  Badge,
  Icon,
  Divider,
  useColorModeValue,
  SimpleGrid,
  Flex,
  Spinner,
  Center
} from '@chakra-ui/react';
import {
  FiTrendingUp,
  FiClock,
  FiShoppingCart,
  FiTarget,
  FiZap,
  FiArrowRight,
  FiCheckCircle,
  FiAlertCircle,
  FiInfo
} from 'react-icons/fi';

interface AIInsights {
  achievements?: string[];
  concerns?: string[];
  suggestions?: string[];
  meal_timing_advice?: string[];
  ingredient_recommendations?: string[];
  portion_advice?: string[];
  alternative_ingredients?: string[];
  meal_plan_optimizations?: string[];
}

interface AIInsightsOverviewProps {
  insights: AIInsights | null;
  loading?: boolean;
}

const AIInsightsOverview: React.FC<AIInsightsOverviewProps> = ({ insights, loading }) => {
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const headerBg = useColorModeValue('purple.50', 'purple.900');

  if (loading) {
    return (
      <Card bg={cardBg} borderColor={borderColor}>
        <CardBody>
          <Center py={8}>
            <Spinner size="lg" color="purple.500" />
            <Text ml={4}>Loading AI insights...</Text>
          </Center>
        </CardBody>
      </Card>
    );
  }

  if (!insights) {
    return (
      <Card bg={cardBg} borderColor={borderColor}>
        <CardHeader bg={headerBg}>
          <HStack>
            <Icon as={FiZap} color="purple.500" boxSize={6} />
            <Heading size="md">AI-Driven Nutritional Analysis</Heading>
          </HStack>
        </CardHeader>
        <CardBody>
          <Box p={4} bg="gray.50" borderRadius="md" border="1px" borderColor="gray.200">
            <Text color="gray.600" textAlign="center">
              Start logging your meals to see personalized AI-powered nutritional insights!
            </Text>
          </Box>
        </CardBody>
      </Card>
    );
  }

  const hasAnyInsights = 
    (insights.achievements && insights.achievements.length > 0) ||
    (insights.concerns && insights.concerns.length > 0) ||
    (insights.suggestions && insights.suggestions.length > 0) ||
    (insights.meal_timing_advice && insights.meal_timing_advice.length > 0) ||
    (insights.ingredient_recommendations && insights.ingredient_recommendations.length > 0) ||
    (insights.portion_advice && insights.portion_advice.length > 0) ||
    (insights.alternative_ingredients && insights.alternative_ingredients.length > 0) ||
    (insights.meal_plan_optimizations && insights.meal_plan_optimizations.length > 0);

  if (!hasAnyInsights) {
    return (
      <Card bg={cardBg} borderColor={borderColor}>
        <CardHeader bg={headerBg}>
          <HStack>
            <Icon as={FiZap} color="purple.500" boxSize={6} />
            <Heading size="md">AI-Driven Nutritional Analysis</Heading>
          </HStack>
        </CardHeader>
        <CardBody>
          <Box p={4} bg="gray.50" borderRadius="md" border="1px" borderColor="gray.200">
            <Text color="gray.600" textAlign="center">
              No insights available yet. Keep logging meals to receive personalized recommendations!
            </Text>
          </Box>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card bg={cardBg} borderColor={borderColor} boxShadow="md">
      <CardHeader bg={headerBg} borderTopRadius="md">
        <HStack justify="space-between">
          <HStack>
            <Icon as={FiZap} color="purple.500" boxSize={6} />
            <Heading size="md">AI-Driven Nutritional Analysis</Heading>
          </HStack>
          <Badge colorScheme="purple" fontSize="sm" px={3} py={1}>
            Powered by AI
          </Badge>
        </HStack>
        <Text fontSize="sm" color="gray.600" mt={2}>
          Personalized improvement suggestions based on your nutritional data
        </Text>
      </CardHeader>
      <CardBody>
        <VStack spacing={6} align="stretch">
          {/* Achievements */}
          {insights.achievements && insights.achievements.length > 0 && (
            <Box>
              <HStack mb={3}>
                <Icon as={FiCheckCircle} color="green.500" boxSize={5} />
                <Heading size="sm" color="green.600">
                  Achievements
                </Heading>
              </HStack>
              <VStack spacing={2} align="stretch">
                {insights.achievements.map((achievement, index) => (
                  <Box
                    key={index}
                    p={3}
                    bg="green.50"
                    borderRadius="md"
                    borderLeft="4px"
                    borderColor="green.400"
                  >
                    <HStack>
                      <Icon as={FiTrendingUp} color="green.500" />
                      <Text fontSize="sm" color="green.800">
                        {achievement}
                      </Text>
                    </HStack>
                  </Box>
                ))}
              </VStack>
            </Box>
          )}

          {/* Concerns */}
          {insights.concerns && insights.concerns.length > 0 && (
            <Box>
              <HStack mb={3}>
                <Icon as={FiAlertCircle} color="orange.500" boxSize={5} />
                <Heading size="sm" color="orange.600">
                  Areas for Attention
                </Heading>
              </HStack>
              <VStack spacing={2} align="stretch">
                {insights.concerns.map((concern, index) => (
                  <Box
                    key={index}
                    p={3}
                    bg="orange.50"
                    borderRadius="md"
                    borderLeft="4px"
                    borderColor="orange.400"
                  >
                    <Text fontSize="sm" color="orange.800">
                      {concern}
                    </Text>
                  </Box>
                ))}
              </VStack>
            </Box>
          )}

          <Divider />

          {/* Improvement Suggestions Overview */}
          <Box>
            <HStack mb={4}>
              <Icon as={FiInfo} color="purple.500" boxSize={5} />
              <Heading size="sm" color="purple.600">
                Improvement Suggestions
              </Heading>
            </HStack>
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
              {/* Food Recommendations */}
              {insights.ingredient_recommendations && insights.ingredient_recommendations.length > 0 && (
                <Box
                  p={4}
                  bg="blue.50"
                  borderRadius="md"
                  border="1px"
                  borderColor="blue.200"
                >
                  <HStack mb={3}>
                    <Icon as={FiShoppingCart} color="blue.500" boxSize={5} />
                    <Heading size="xs" color="blue.700">
                      Food Recommendations
                    </Heading>
                  </HStack>
                  <VStack spacing={2} align="stretch">
                    {insights.ingredient_recommendations.map((rec, index) => (
                      <HStack key={index} align="start">
                        <Icon as={FiArrowRight} color="blue.400" boxSize={4} mt={1} />
                        <Text fontSize="sm" color="blue.800">
                          {rec}
                        </Text>
                      </HStack>
                    ))}
                  </VStack>
                </Box>
              )}

              {/* Meal Timing Adjustments */}
              {insights.meal_timing_advice && insights.meal_timing_advice.length > 0 && (
                <Box
                  p={4}
                  bg="teal.50"
                  borderRadius="md"
                  border="1px"
                  borderColor="teal.200"
                >
                  <HStack mb={3}>
                    <Icon as={FiClock} color="teal.500" boxSize={5} />
                    <Heading size="xs" color="teal.700">
                      Meal Timing Adjustments
                    </Heading>
                  </HStack>
                  <VStack spacing={2} align="stretch">
                    {insights.meal_timing_advice.map((advice, index) => (
                      <HStack key={index} align="start">
                        <Icon as={FiArrowRight} color="teal.400" boxSize={4} mt={1} />
                        <Text fontSize="sm" color="teal.800">
                          {advice}
                        </Text>
                      </HStack>
                    ))}
                  </VStack>
                </Box>
              )}

              {/* Portion Size Modifications */}
              {insights.portion_advice && insights.portion_advice.length > 0 && (
                <Box
                  p={4}
                  bg="pink.50"
                  borderRadius="md"
                  border="1px"
                  borderColor="pink.200"
                >
                  <HStack mb={3}>
                    <Icon as={FiTarget} color="pink.500" boxSize={5} />
                    <Heading size="xs" color="pink.700">
                      Portion Size Modifications
                    </Heading>
                  </HStack>
                  <VStack spacing={2} align="stretch">
                    {insights.portion_advice.map((advice, index) => (
                      <HStack key={index} align="start">
                        <Icon as={FiArrowRight} color="pink.400" boxSize={4} mt={1} />
                        <Text fontSize="sm" color="pink.800">
                          {advice}
                        </Text>
                      </HStack>
                    ))}
                  </VStack>
                </Box>
              )}

              {/* Alternative Ingredients */}
              {insights.alternative_ingredients && insights.alternative_ingredients.length > 0 && (
                <Box
                  p={4}
                  bg="cyan.50"
                  borderRadius="md"
                  border="1px"
                  borderColor="cyan.200"
                >
                  <HStack mb={3}>
                    <Icon as={FiShoppingCart} color="cyan.500" boxSize={5} />
                    <Heading size="xs" color="cyan.700">
                      Alternative Ingredients
                    </Heading>
                  </HStack>
                  <VStack spacing={2} align="stretch">
                    {insights.alternative_ingredients.map((alt, index) => (
                      <HStack key={index} align="start">
                        <Icon as={FiArrowRight} color="cyan.400" boxSize={4} mt={1} />
                        <Text fontSize="sm" color="cyan.800">
                          {alt}
                        </Text>
                      </HStack>
                    ))}
                  </VStack>
                </Box>
              )}

              {/* Meal Plan Optimizations */}
              {insights.meal_plan_optimizations && insights.meal_plan_optimizations.length > 0 && (
                <Box
                  p={4}
                  bg="purple.50"
                  borderRadius="md"
                  border="1px"
                  borderColor="purple.200"
                >
                  <HStack mb={3}>
                    <Icon as={FiZap} color="purple.500" boxSize={5} />
                    <Heading size="xs" color="purple.700">
                      Meal Plan Optimizations
                    </Heading>
                  </HStack>
                  <VStack spacing={2} align="stretch">
                    {insights.meal_plan_optimizations.map((opt, index) => (
                      <HStack key={index} align="start">
                        <Icon as={FiArrowRight} color="purple.400" boxSize={4} mt={1} />
                        <Text fontSize="sm" color="purple.800">
                          {opt}
                        </Text>
                      </HStack>
                    ))}
                  </VStack>
                </Box>
              )}

              {/* General Suggestions */}
              {insights.suggestions && insights.suggestions.length > 0 && (
                <Box
                  p={4}
                  bg="indigo.50"
                  borderRadius="md"
                  border="1px"
                  borderColor="indigo.200"
                >
                  <HStack mb={3}>
                    <Icon as={FiInfo} color="indigo.500" boxSize={5} />
                    <Heading size="xs" color="indigo.700">
                      General Recommendations
                    </Heading>
                  </HStack>
                  <VStack spacing={2} align="stretch">
                    {insights.suggestions.map((suggestion, index) => (
                      <HStack key={index} align="start">
                        <Icon as={FiArrowRight} color="indigo.400" boxSize={4} mt={1} />
                        <Text fontSize="sm" color="indigo.800">
                          {suggestion}
                        </Text>
                      </HStack>
                    ))}
                  </VStack>
                </Box>
              )}
            </SimpleGrid>
          </Box>
        </VStack>
      </CardBody>
    </Card>
  );
};

export default AIInsightsOverview;

