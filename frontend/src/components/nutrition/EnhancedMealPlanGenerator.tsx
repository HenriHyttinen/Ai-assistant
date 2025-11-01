import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  VStack,
  HStack,
  Text,
  Badge,
  Divider,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  useToast,
  Spinner,
  Center,
  SimpleGrid,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  StatArrow,
  Progress,
  Tag,
  TagLabel,
  TagLeftIcon,
  Wrap,
  WrapItem,
  Tooltip,
  IconButton,
  Collapse,
  useDisclosure
} from '@chakra-ui/react';
import {
  FiChefHat,
  FiTarget,
  FiTrendingUp,
  FiGlobe,
  FiCalendar,
  FiStar,
  FiInfo,
  FiCheckCircle,
  FiAlertCircle,
  FiClock,
  FiUsers,
  FiHeart,
  FiZap
} from 'react-icons/fi';
import { MealPlanGenerationRequest } from '../../types/nutrition';

interface EnhancedMealPlanGeneratorProps {
  onMealPlanGenerated?: (mealPlan: any) => void;
}

interface EnhancementMetadata {
  dietary_compliance_score: number;
  personalization_score: number;
  variety_score: number;
  cultural_authenticity_score: number;
  seasonal_relevance_score: number;
  overall_enhancement_score: number;
  dietary_complexity_handled: number;
  restrictions_count: number;
  enhancement_features_used: string[];
}

interface EnhancedMealPlan {
  strategy: any;
  meal_plan: any;
  enhancement_metadata: EnhancementMetadata;
  enhancement_notes?: string[];
}

const EnhancedMealPlanGenerator: React.FC<EnhancedMealPlanGeneratorProps> = ({
  onMealPlanGenerated
}) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [enhancedMealPlan, setEnhancedMealPlan] = useState<EnhancedMealPlan | null>(null);
  const [error, setError] = useState<string | null>(null);
  const toast = useToast();
  const { isOpen, onToggle } = useDisclosure();

  const generateEnhancedMealPlan = async () => {
    setIsGenerating(true);
    setError(null);

    try {
      const planRequest: MealPlanGenerationRequest = {
        plan_type: 'daily',
        start_date: new Date().toISOString().split('T')[0],
        end_date: new Date().toISOString().split('T')[0],
        preferences_override: null
      };

      const response = await fetch('/api/nutrition/meal-plans/generate-enhanced', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify(planRequest)
      });

      if (!response.ok) {
        throw new Error('Failed to generate enhanced meal plan');
      }

      const mealPlan = await response.json();
      setEnhancedMealPlan(mealPlan);
      
      if (onMealPlanGenerated) {
        onMealPlanGenerated(mealPlan);
      }

      toast({
        title: 'Enhanced Meal Plan Generated!',
        description: 'Your personalized meal plan with advanced dietary restrictions is ready.',
        status: 'success',
        duration: 5000,
        isClosable: true
      });

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to generate meal plan';
      setError(errorMessage);
      toast({
        title: 'Error',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true
      });
    } finally {
      setIsGenerating(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'green';
    if (score >= 70) return 'yellow';
    return 'red';
  };

  const getScoreIcon = (score: number) => {
    if (score >= 90) return FiCheckCircle;
    if (score >= 70) return FiAlertCircle;
    return FiAlertCircle;
  };

  return (
    <Box>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <Box textAlign="center">
          <Heading size="lg" mb={2} color="blue.600">
            <HStack justify="center" spacing={2}>
              <FiChefHat />
              <Text>Enhanced AI Meal Planning</Text>
            </HStack>
          </Heading>
          <Text color="gray.600" fontSize="lg">
            Advanced personalization with dietary restrictions, cultural adaptations, and behavioral insights
          </Text>
        </Box>

        {/* Generate Button */}
        <Center>
          <Button
            onClick={generateEnhancedMealPlan}
            isLoading={isGenerating}
            loadingText="Generating Enhanced Meal Plan..."
            colorScheme="blue"
            size="lg"
            leftIcon={<FiZap />}
            isDisabled={isGenerating}
          >
            Generate Enhanced Meal Plan
          </Button>
        </Center>

        {/* Error Display */}
        {error && (
          <Alert status="error">
            <AlertIcon />
            <AlertTitle>Error!</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Loading State */}
        {isGenerating && (
          <Center py={8}>
            <VStack spacing={4}>
              <Spinner size="xl" color="blue.500" />
              <Text>Analyzing your preferences and generating personalized meal plan...</Text>
            </VStack>
          </Center>
        )}

        {/* Enhanced Meal Plan Results */}
        {enhancedMealPlan && (
          <Box>
            {/* Enhancement Metadata */}
            <Card mb={6}>
              <CardHeader>
                <HStack justify="space-between">
                  <Heading size="md">Enhancement Analysis</Heading>
                  <IconButton
                    aria-label="Toggle details"
                    icon={isOpen ? <FiInfo /> : <FiInfo />}
                    onClick={onToggle}
                    variant="ghost"
                  />
                </HStack>
              </CardHeader>
              <CardBody>
                <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4} mb={4}>
                  <Stat>
                    <StatLabel>Overall Enhancement Score</StatLabel>
                    <StatNumber color={getScoreColor(enhancedMealPlan.enhancement_metadata.overall_enhancement_score)}>
                      {enhancedMealPlan.enhancement_metadata.overall_enhancement_score}%
                    </StatNumber>
                    <StatHelpText>
                      <StatArrow type="increase" />
                      AI-powered personalization
                    </StatHelpText>
                  </Stat>

                  <Stat>
                    <StatLabel>Dietary Compliance</StatLabel>
                    <StatNumber color={getScoreColor(enhancedMealPlan.enhancement_metadata.dietary_compliance_score)}>
                      {enhancedMealPlan.enhancement_metadata.dietary_compliance_score}%
                    </StatNumber>
                    <StatHelpText>
                      <StatArrow type="increase" />
                      Restrictions handled
                    </StatHelpText>
                  </Stat>

                  <Stat>
                    <StatLabel>Personalization</StatLabel>
                    <StatNumber color={getScoreColor(enhancedMealPlan.enhancement_metadata.personalization_score)}>
                      {enhancedMealPlan.enhancement_metadata.personalization_score}%
                    </StatNumber>
                    <StatHelpText>
                      <StatArrow type="increase" />
                      Tailored to you
                    </StatHelpText>
                  </Stat>

                  <Stat>
                    <StatLabel>Variety Score</StatLabel>
                    <StatNumber color={getScoreColor(enhancedMealPlan.enhancement_metadata.variety_score)}>
                      {enhancedMealPlan.enhancement_metadata.variety_score}%
                    </StatNumber>
                    <StatHelpText>
                      <StatArrow type="increase" />
                      Meal diversity
                    </StatHelpText>
                  </Stat>

                  <Stat>
                    <StatLabel>Cultural Authenticity</StatLabel>
                    <StatNumber color={getScoreColor(enhancedMealPlan.enhancement_metadata.cultural_authenticity_score)}>
                      {enhancedMealPlan.enhancement_metadata.cultural_authenticity_score}%
                    </StatNumber>
                    <StatHelpText>
                      <StatArrow type="increase" />
                      Cultural fit
                    </StatHelpText>
                  </Stat>

                  <Stat>
                    <StatLabel>Seasonal Relevance</StatLabel>
                    <StatNumber color={getScoreColor(enhancedMealPlan.enhancement_metadata.seasonal_relevance_score)}>
                      {enhancedMealPlan.enhancement_metadata.seasonal_relevance_score}%
                    </StatNumber>
                    <StatHelpText>
                      <StatArrow type="increase" />
                      Seasonal ingredients
                    </StatHelpText>
                  </Stat>
                </SimpleGrid>

                <Collapse in={isOpen} animateOpacity>
                  <Box mt={4}>
                    <Divider mb={4} />
                    
                    {/* Dietary Complexity */}
                    <Box mb={4}>
                      <HStack mb={2}>
                        <FiTarget />
                        <Text fontWeight="bold">Dietary Complexity Handled</Text>
                      </HStack>
                      <Progress 
                        value={enhancedMealPlan.enhancement_metadata.dietary_complexity_handled} 
                        colorScheme="blue" 
                        size="sm" 
                        mb={2}
                      />
                      <Text fontSize="sm" color="gray.600">
                        {enhancedMealPlan.enhancement_metadata.restrictions_count} dietary restrictions processed
                      </Text>
                    </Box>

                    {/* Enhancement Features */}
                    <Box mb={4}>
                      <HStack mb={2}>
                        <FiZap />
                        <Text fontWeight="bold">Enhancement Features Used</Text>
                      </HStack>
                      <Wrap>
                        {enhancedMealPlan.enhancement_metadata.enhancement_features_used.map((feature, index) => (
                          <WrapItem key={index}>
                            <Tag colorScheme="blue" variant="subtle">
                              <TagLeftIcon as={FiCheckCircle} />
                              <TagLabel>{feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</TagLabel>
                            </Tag>
                          </WrapItem>
                        ))}
                      </Wrap>
                    </Box>

                    {/* Enhancement Notes */}
                    {enhancedMealPlan.enhancement_notes && enhancedMealPlan.enhancement_notes.length > 0 && (
                      <Box>
                        <HStack mb={2}>
                          <FiInfo />
                          <Text fontWeight="bold">Enhancement Notes</Text>
                        </HStack>
                        <VStack align="stretch" spacing={2}>
                          {enhancedMealPlan.enhancement_notes.map((note, index) => (
                            <Text key={index} fontSize="sm" color="gray.600" pl={4}>
                              • {note}
                            </Text>
                          ))}
                        </VStack>
                      </Box>
                    )}
                  </Box>
                </Collapse>
              </CardBody>
            </Card>

            {/* Strategy Information */}
            {enhancedMealPlan.strategy && (
              <Card mb={6}>
                <CardHeader>
                  <Heading size="md">AI Strategy: {enhancedMealPlan.strategy.strategy_name}</Heading>
                </CardHeader>
                <CardBody>
                  <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                    <Box>
                      <Text fontWeight="bold" mb={2}>Macro Distribution</Text>
                      <VStack align="stretch" spacing={2}>
                        {Object.entries(enhancedMealPlan.strategy.macro_distribution || {}).map(([macro, percentage]) => (
                          <HStack key={macro} justify="space-between">
                            <Text textTransform="capitalize">{macro}</Text>
                            <Text fontWeight="bold">{(Number(percentage) * 100).toFixed(1)}%</Text>
                          </HStack>
                        ))}
                      </VStack>
                    </Box>
                    
                    <Box>
                      <Text fontWeight="bold" mb={2}>Focus Areas</Text>
                      <Wrap>
                        {(enhancedMealPlan.strategy.focus_areas || []).map((area: string, index: number) => (
                          <WrapItem key={index}>
                            <Tag colorScheme="green" variant="subtle">
                              <TagLabel>{area.replace(/_/g, ' ')}</TagLabel>
                            </Tag>
                          </WrapItem>
                        ))}
                      </Wrap>
                    </Box>
                  </SimpleGrid>
                </CardBody>
              </Card>
            )}

            {/* Meal Plan Preview */}
            {enhancedMealPlan.meal_plan && (
              <Card>
                <CardHeader>
                  <Heading size="md">Your Enhanced Meal Plan</Heading>
                </CardHeader>
                <CardBody>
                  <Text color="gray.600" mb={4}>
                    This meal plan has been enhanced with advanced personalization, dietary restrictions handling, 
                    cultural adaptations, and seasonal considerations.
                  </Text>
                  
                  {/* Add meal plan display here */}
                  <Alert status="info">
                    <AlertIcon />
                    <AlertDescription>
                      Enhanced meal plan generated successfully! The detailed meal plan would be displayed here.
                    </AlertDescription>
                  </Alert>
                </CardBody>
              </Card>
            )}
          </Box>
        )}
      </VStack>
    </Box>
  );
};

export default EnhancedMealPlanGenerator;







