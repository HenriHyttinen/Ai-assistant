import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Badge,
  Button,
  ButtonGroup,
  Select,
  Input,
  InputGroup,
  InputLeftElement,
  Icon,
  Flex,
  Spinner,
  Alert,
  AlertIcon,
  Tooltip,
  Divider,
  SimpleGrid,
  Image,
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  useToast,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  List,
  ListItem,
  ListIcon
} from '@chakra-ui/react';
import { 
  FiSearch, 
  FiHeart, 
  FiClock, 
  FiUsers, 
  FiStar,
  FiTrendingUp,
  FiTarget,
  FiShuffle,
  FiZap,
  FiHome,
  FiCoffee,
  FiSun,
  FiMoon,
  FiPackage,
  FiCheck
} from 'react-icons/fi';
import PlaceholderImage from '../common/PlaceholderImage';
import SafeImage from '../common/SafeImage';
import StarRating from '../recipe/StarRating';
import RecipeStats from '../recipe/RecipeStats';
import recipeRatingService from '../../services/recipeRatingService';

interface RecipeRecommendation {
  id: string;
  title: string;
  cuisine: string;
  meal_type: string;
  prep_time: number;
  cook_time: number;
  difficulty_level: string;
  servings: number;
  summary?: string;
  image_url?: string;
  dietary_tags: string[];
  per_serving_calories: number;
  per_serving_protein: number;
  per_serving_carbs: number;
  per_serving_fat: number;
  total_calories: number;
  total_protein: number;
  total_carbs: number;
  total_fat: number;
  recommendation_score?: number;
  recommendation_reason?: string;
  rank?: number;
  based_on?: string;
  nutrition_score?: number;
  similarity_score?: number;
  diversity_score?: number;
  trending_score?: number;
  context_score?: number;
  total_score?: number;
  ingredients?: (string | { name?: string; quantity?: number | string; unit?: string; notes?: string })[];
  instructions?: (string | { step?: number; step_number?: number; description?: string; title?: string; time_required?: number })[];
}

interface RecommendationResponse {
  recommendations: RecipeRecommendation[];
  total: number;
  recommendation_type?: string;
  context?: string;
  meal_type?: string;
  user_id: string;
}

const RecipeRecommendations: React.FC = () => {
  const [recommendations, setRecommendations] = useState<RecipeRecommendation[]>([]);
  const [loading, setLoading] = useState(false);
  const [recommendationType, setRecommendationType] = useState('mixed');
  const [context, setContext] = useState('');
  const [selectedMealType, setSelectedMealType] = useState('breakfast');
  const [activeTab, setActiveTab] = useState(0);
  const [limit, setLimit] = useState(10);
  const [selectedRecipe, setSelectedRecipe] = useState<RecipeRecommendation | null>(null);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();
  
  // Rating-related state
  const [recipeStats, setRecipeStats] = useState<{ [key: string]: any }>({});
  const [userRatings, setUserRatings] = useState<{ [key: string]: any }>({});
  const [loadingStats, setLoadingStats] = useState<{ [key: string]: boolean }>({});

  const recommendationTypes = [
    { value: 'mixed', label: 'Mixed', icon: FiShuffle, description: 'Combined recommendations' },
    { value: 'nutritional', label: 'Nutritional', icon: FiTarget, description: 'Based on nutritional needs' },
    { value: 'similar', label: 'Similar', icon: FiTrendingUp, description: 'Similar to your recent meals' },
    { value: 'trending', label: 'Trending', icon: FiZap, description: 'Popular choices' },
    { value: 'diverse', label: 'Diverse', icon: FiHome, description: 'Add variety to your diet' }
  ];

  const mealTypes = [
    { value: 'breakfast', label: 'Breakfast', icon: FiCoffee },
    { value: 'lunch', label: 'Lunch', icon: FiSun },
    { value: 'dinner', label: 'Dinner', icon: FiMoon },
    { value: 'snacks', label: 'Snacks', icon: FiPackage }
  ];

  const loadRecommendations = async (type: string = recommendationType) => {
    try {
      setLoading(true);
      
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      let endpoint = `/nutrition/recommendations?recommendation_type=${type}&limit=${limit}`;
      
      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token || ''}`,
        },
      });

      if (response.ok) {
        const data: RecommendationResponse = await response.json();
        setRecommendations(data.recommendations || []);
      } else {
        throw new Error(`Failed to load recommendations: ${response.status}`);
      }
    } catch (error) {
      console.error('Error loading recommendations:', error);
      toast({
        title: 'Error',
        description: 'Failed to load recommendations',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const loadContextualRecommendations = async () => {
    if (!context.trim()) return;
    
    try {
      setLoading(true);
      
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      const response = await fetch(
        `http://localhost:8000/nutrition/recommendations/contextual?context=${encodeURIComponent(context)}&limit=${limit}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${session?.access_token || ''}`,
          },
        }
      );

      if (response.ok) {
        const data: RecommendationResponse = await response.json();
        setRecommendations(data.recommendations || []);
      } else {
        throw new Error(`Failed to load contextual recommendations: ${response.status}`);
      }
    } catch (error) {
      console.error('Error loading contextual recommendations:', error);
      toast({
        title: 'Error',
        description: 'Failed to load contextual recommendations',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const loadMealSpecificRecommendations = async (mealType: string) => {
    try {
      setLoading(true);
      
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      const response = await fetch(
        `http://localhost:8000/nutrition/recommendations/meal/${mealType}?limit=${limit}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${session?.access_token || ''}`,
          },
        }
      );

      if (response.ok) {
        const data: RecommendationResponse = await response.json();
        setRecommendations(data.recommendations || []);
      } else {
        throw new Error(`Failed to load meal-specific recommendations: ${response.status}`);
      }
    } catch (error) {
      console.error('Error loading meal-specific recommendations:', error);
      toast({
        title: 'Error',
        description: 'Failed to load meal-specific recommendations',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleViewRecipe = (recipe: RecipeRecommendation) => {
    setSelectedRecipe(recipe);
    onOpen();
  };

  const handleAddToMealPlan = async (recipe: RecipeRecommendation) => {
    try {
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        toast({
          title: 'Error',
          description: 'Please log in to add recipes to meal plans',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
        return;
      }

      // Get today's date
      const today = new Date().toISOString().split('T')[0];
      
      // First, get or create today's meal plan
      const mealPlanResponse = await fetch(
        `http://localhost:8000/nutrition/meal-plans?date=${today}&limit=1`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${session.access_token}`,
          },
        }
      );

      let mealPlanId;
      if (mealPlanResponse.ok) {
        const mealPlans = await mealPlanResponse.json();
        if (mealPlans.length > 0) {
          mealPlanId = mealPlans[0].id;
        } else {
          // Create a new meal plan for today
          const createResponse = await fetch('http://localhost:8000/nutrition/meal-plans', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${session.access_token}`,
            },
            body: JSON.stringify({
              date: today,
              name: `Meal Plan - ${today}`
            })
          });
          
          if (createResponse.ok) {
            const newMealPlan = await createResponse.json();
            mealPlanId = newMealPlan.id;
          } else {
            throw new Error('Failed to create meal plan');
          }
        }
      } else {
        throw new Error('Failed to get meal plan');
      }

      // Add the recipe as a custom meal to the meal plan
      const addMealResponse = await fetch(
        `http://localhost:8000/nutrition/meal-plans/${mealPlanId}/custom-meal`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${session.access_token}`,
          },
          body: JSON.stringify({
            meal_type: recipe.meal_type,
            meal_name: recipe.title,
            cuisine: recipe.cuisine,
            nutrition: {
              calories: recipe.per_serving_calories,
              protein: recipe.per_serving_protein,
              carbs: recipe.per_serving_carbs,
              fats: recipe.per_serving_fat
            },
            recipe_id: recipe.id,
            summary: recipe.summary || '',
            prep_time: recipe.prep_time,
            cook_time: recipe.cook_time,
            difficulty_level: recipe.difficulty_level,
            servings: recipe.servings,
            dietary_tags: recipe.dietary_tags || []
          })
        }
      );

      if (addMealResponse.ok) {
        toast({
          title: 'Success',
          description: `Added "${recipe.title}" to your meal plan`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      } else {
        throw new Error('Failed to add meal to plan');
      }
    } catch (error) {
      console.error('Error adding recipe to meal plan:', error);
      toast({
        title: 'Error',
        description: 'Failed to add recipe to meal plan',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  // Rating functions
  const loadRecipeStats = async (recipeId: string) => {
    if (loadingStats[recipeId] || recipeStats[recipeId]) return;
    
    try {
      setLoadingStats(prev => ({ ...prev, [recipeId]: true }));
      const stats = await recipeRatingService.getRecipeStats(recipeId);
      setRecipeStats(prev => ({ ...prev, [recipeId]: stats }));
    } catch (error) {
      console.error('Error loading recipe stats:', error);
    } finally {
      setLoadingStats(prev => ({ ...prev, [recipeId]: false }));
    }
  };

  const loadUserRating = async (recipeId: string) => {
    if (userRatings[recipeId]) return;
    
    try {
      const rating = await recipeRatingService.getUserRating(recipeId);
      setUserRatings(prev => ({ ...prev, [recipeId]: rating }));
    } catch (error) {
      console.error('Error loading user rating:', error);
    }
  };

  const handleVoteHelpful = async (reviewId: number, isHelpful: boolean) => {
    try {
      await recipeRatingService.voteHelpful(reviewId, isHelpful);
      // Refresh the selected recipe's reviews if it's open
      if (selectedRecipe) {
        // This would refresh the reviews in the modal
        // For now, we'll just show a success message
      }
    } catch (error) {
      throw error; // Re-throw to be handled by the component
    }
  };

  useEffect(() => {
    loadRecommendations();
  }, []);

  const getMealTypeIcon = (mealType: string) => {
    const meal = mealTypes.find(m => m.value === mealType);
    return meal ? meal.icon : FiHome;
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy': return 'green';
      case 'medium': return 'yellow';
      case 'hard': return 'red';
      default: return 'gray';
    }
  };

  const formatMealType = (mealType: string) => {
    return mealType.charAt(0).toUpperCase() + mealType.slice(1);
  };

  const getRecommendationIcon = (type: string) => {
    const recType = recommendationTypes.find(t => t.value === type);
    return recType ? recType.icon : FiStar;
  };

  return (
    <VStack spacing={6} align="stretch">
      <Box>
        <Heading size="lg" mb={2}>
          Recipe Recommendations
        </Heading>
        <Text color="gray.600">
          Discover personalized recipes based on your preferences and nutritional needs
        </Text>
      </Box>

      {/* Recommendation Controls */}
      <Card>
        <CardHeader>
          <Heading size="md">Recommendation Settings</Heading>
        </CardHeader>
        <CardBody>
          <Tabs index={activeTab} onChange={setActiveTab}>
            <TabList>
              <Tab>Personalized</Tab>
              <Tab>Contextual</Tab>
              <Tab>Meal Specific</Tab>
            </TabList>

            <TabPanels>
              {/* Personalized Recommendations */}
              <TabPanel px={0}>
                <VStack spacing={4} align="stretch">
                  <Box>
                    <Text fontWeight="semibold" mb={2}>Recommendation Type</Text>
                    <SimpleGrid columns={{ base: 2, md: 5 }} spacing={2}>
                      {recommendationTypes.map((type) => (
                        <Button
                          key={type.value}
                          leftIcon={<Icon as={type.icon} />}
                          colorScheme={recommendationType === type.value ? 'blue' : 'gray'}
                          variant={recommendationType === type.value ? 'solid' : 'outline'}
                          onClick={() => setRecommendationType(type.value)}
                          size="sm"
                        >
                          {type.label}
                        </Button>
                      ))}
                    </SimpleGrid>
                  </Box>

                  <HStack>
                    <Text fontWeight="semibold">Limit:</Text>
                    <Select
                      value={limit}
                      onChange={(e) => setLimit(parseInt(e.target.value))}
                      width="100px"
                      size="sm"
                    >
                      <option value={5}>5</option>
                      <option value={10}>10</option>
                      <option value={20}>20</option>
                      <option value={50}>50</option>
                    </Select>
                    <Button
                      colorScheme="blue"
                      onClick={() => loadRecommendations()}
                      isLoading={loading}
                      loadingText="Loading..."
                    >
                      Get Recommendations
                    </Button>
                  </HStack>
                </VStack>
              </TabPanel>

              {/* Contextual Recommendations */}
              <TabPanel px={0}>
                <VStack spacing={4} align="stretch">
                  <Box>
                    <Text fontWeight="semibold" mb={2}>Search Context</Text>
                    <InputGroup>
                      <InputLeftElement>
                        <Icon as={FiSearch} />
                      </InputLeftElement>
                      <Input
                        placeholder="e.g., 'high protein', 'quick meal', 'Italian dinner'"
                        value={context}
                        onChange={(e) => setContext(e.target.value)}
                        onKeyPress={(e) => e.key === 'Enter' && loadContextualRecommendations()}
                      />
                    </InputGroup>
                  </Box>
                  <Button
                    colorScheme="blue"
                    onClick={loadContextualRecommendations}
                    isLoading={loading}
                    loadingText="Searching..."
                    isDisabled={!context.trim()}
                  >
                    Find Recipes
                  </Button>
                </VStack>
              </TabPanel>

              {/* Meal Specific Recommendations */}
              <TabPanel px={0}>
                <VStack spacing={4} align="stretch">
                  <Box>
                    <Text fontWeight="semibold" mb={2}>Meal Type</Text>
                    <SimpleGrid columns={{ base: 2, md: 4 }} spacing={2}>
                      {mealTypes.map((meal) => (
                        <Button
                          key={meal.value}
                          leftIcon={<Icon as={meal.icon} />}
                          colorScheme={selectedMealType === meal.value ? 'blue' : 'gray'}
                          variant={selectedMealType === meal.value ? 'solid' : 'outline'}
                          onClick={() => setSelectedMealType(meal.value)}
                          size="sm"
                        >
                          {meal.label}
                        </Button>
                      ))}
                    </SimpleGrid>
                  </Box>
                  <Button
                    colorScheme="blue"
                    onClick={() => loadMealSpecificRecommendations(selectedMealType)}
                    isLoading={loading}
                    loadingText="Loading..."
                  >
                    Get {formatMealType(selectedMealType)} Recipes
                  </Button>
                </VStack>
              </TabPanel>
            </TabPanels>
          </Tabs>
        </CardBody>
      </Card>

      {/* Recommendations Display */}
      {loading ? (
        <Box textAlign="center" py={8}>
          <Spinner size="xl" color="blue.500" />
          <Text mt={4}>Loading recommendations...</Text>
        </Box>
      ) : recommendations.length > 0 ? (
        <VStack spacing={4} align="stretch">
          <HStack justify="space-between">
            <Text fontWeight="semibold">
              {recommendations.length} Recommendations Found
            </Text>
            {recommendationType && (
              <HStack spacing={2}>
                <Icon as={getRecommendationIcon(recommendationType)} />
                <Badge colorScheme="blue">
                  {recommendationTypes.find(t => t.value === recommendationType)?.label}
                </Badge>
              </HStack>
            )}
          </HStack>

          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
            {recommendations.map((recipe, index) => (
              <Card key={recipe.id} maxW="sm" mx="auto" w="full" overflow="hidden">
                <CardHeader pb={2}>
                  <HStack justify="space-between" align="start" spacing={2}>
                    <VStack align="start" spacing={1} flex={1} minW={0}>
                      <Heading size="sm" noOfLines={2} wordBreak="break-word" width="100%">
                        {recipe.title}
                      </Heading>
                      {/* Dietary Tags - Prominently displayed */}
                      {recipe.dietary_tags && recipe.dietary_tags.length > 0 && (
                        <HStack spacing={1} wrap="wrap" maxW="100%" overflow="hidden">
                          {recipe.dietary_tags
                            .filter((tag: string) => 
                              ['vegetarian', 'vegan', 'contains-peanuts', 'contains-tree-nuts', 
                               'contains-nightshades', 'contains-dairy', 'contains-eggs', 
                               'contains-gluten', 'contains-soy', 'contains-fish'].includes(tag.toLowerCase())
                            )
                            .slice(0, 5)
                            .map((tag: string, idx: number) => {
                              const tagLower = tag.toLowerCase();
                              let colorScheme = "gray";
                              
                              if (tagLower === 'vegetarian') colorScheme = "green";
                              else if (tagLower === 'vegan') colorScheme = "teal";
                              else if (tagLower.includes('peanut')) colorScheme = "red";
                              else if (tagLower.includes('tree-nut')) colorScheme = "orange";
                              else if (tagLower.includes('nightshade')) colorScheme = "purple";
                              else if (tagLower.includes('dairy') || tagLower.includes('eggs') || 
                                       tagLower.includes('gluten') || tagLower.includes('soy') || 
                                       tagLower.includes('fish')) colorScheme = "red";
                              
                              return (
                                <Badge 
                                  key={idx} 
                                  colorScheme={colorScheme} 
                                  size="sm" 
                                  fontSize="xs"
                                  noOfLines={1}
                                  textTransform="capitalize"
                                >
                                  {tag.replace('contains-', '').replace('-', ' ')}
                        </Badge>
                              );
                            })}
                          {recipe.dietary_tags.length > 5 && (
                            <Text fontSize="xs" color="gray.500">+{recipe.dietary_tags.length - 5}</Text>
                          )}
                        </HStack>
                      )}
                      <HStack spacing={2}>
                        <Badge
                          colorScheme={getDifficultyColor(recipe.difficulty_level)}
                          size="sm"
                        >
                          {recipe.difficulty_level}
                        </Badge>
                      </HStack>
                    </VStack>
                    {recipe.rank && (
                      <Badge colorScheme="blue" variant="solid">
                        #{recipe.rank}
                      </Badge>
                    )}
                  </HStack>
                </CardHeader>

                <CardBody pt={0}>
                  <VStack spacing={3} align="stretch">
                    {/* Recipe Image */}
                    <SafeImage
                      src={recipe.image_url}
                      alt={recipe.title}
                      borderRadius="md"
                      height="150px"
                      objectFit="cover"
                      fallbackText="Recipe Image"
                      fallbackIcon={FiHome}
                    />

                    {/* Recipe Info */}
                    <HStack spacing={4} fontSize="sm" color="gray.600">
                      <HStack>
                        <Icon as={FiClock} />
                        <Text>{recipe.prep_time + recipe.cook_time}min</Text>
                      </HStack>
                      <HStack>
                        <Icon as={getMealTypeIcon(recipe.meal_type)} />
                        <Text>{formatMealType(recipe.meal_type)}</Text>
                      </HStack>
                      <HStack>
                        <Icon as={FiUsers} />
                        <Text>{recipe.servings} servings</Text>
                      </HStack>
                    </HStack>

                    {/* Nutrition Info */}
                    {/* Total Recipe */}
                    <Box>
                      <Text fontSize="xs" color="gray.500" mb={1}>
                        Total Recipe ({recipe.servings || 1} {recipe.servings === 1 ? 'serving' : 'servings'})
                      </Text>
                      <SimpleGrid columns={2} spacing={2} mb={3}>
                        <Stat size="sm">
                          <StatLabel>Calories</StatLabel>
                          <StatNumber fontSize="sm">
                            {Math.round(recipe.total_calories || (recipe.per_serving_calories || 0) * (recipe.servings || 1))}
                          </StatNumber>
                        </Stat>
                        <Stat size="sm">
                          <StatLabel>Protein</StatLabel>
                          <StatNumber fontSize="sm">
                            {((recipe.total_protein || (recipe.per_serving_protein || 0) * (recipe.servings || 1))).toFixed(1)}g
                          </StatNumber>
                        </Stat>
                        <Stat size="sm">
                          <StatLabel>Carbs</StatLabel>
                          <StatNumber fontSize="sm">
                            {((recipe.total_carbs || (recipe.per_serving_carbs || 0) * (recipe.servings || 1))).toFixed(1)}g
                          </StatNumber>
                        </Stat>
                        <Stat size="sm">
                          <StatLabel>Fat</StatLabel>
                          <StatNumber fontSize="sm">
                            {((recipe.total_fat || recipe.total_fats || (recipe.per_serving_fat || recipe.per_serving_fats || 0) * (recipe.servings || 1))).toFixed(1)}g
                          </StatNumber>
                        </Stat>
                      </SimpleGrid>
                    </Box>
                    
                    {/* Per Serving */}
                    <Box width="100%" overflow="hidden">
                      <Text fontSize="xs" color="gray.500" mb={1}>Per Serving</Text>
                      <SimpleGrid columns={2} spacing={2}>
                        <Box overflow="hidden">
                          <Text fontSize="xs" color="gray.600" mb={0.5}>Calories</Text>
                          <Text fontWeight="bold" color="blue.600" fontSize="sm" noOfLines={1}>
                            {(recipe.per_serving_calories || (recipe.total_calories && recipe.servings ? recipe.total_calories / recipe.servings : 0) || 0).toFixed(0)}
                          </Text>
                        </Box>
                        <Box overflow="hidden">
                          <Text fontSize="xs" color="gray.600" mb={0.5}>Protein</Text>
                          <Text fontWeight="bold" color="blue.600" fontSize="sm" noOfLines={1}>
                            {((recipe.per_serving_protein || (recipe.total_protein && recipe.servings ? recipe.total_protein / recipe.servings : 0) || 0)).toFixed(1)}g
                          </Text>
                        </Box>
                        <Box overflow="hidden">
                          <Text fontSize="xs" color="gray.600" mb={0.5}>Carbs</Text>
                          <Text color="blue.600" fontSize="sm" noOfLines={1}>
                            {((recipe.per_serving_carbs || (recipe.total_carbs && recipe.servings ? recipe.total_carbs / recipe.servings : 0) || 0)).toFixed(1)}g
                          </Text>
                        </Box>
                        <Box overflow="hidden">
                          <Text fontSize="xs" color="gray.600" mb={0.5}>Fat</Text>
                          <Text color="blue.600" fontSize="sm" noOfLines={1}>
                            {(() => {
                              const perServing = recipe.per_serving_fat || recipe.per_serving_fats || 
                                ((recipe.total_fat || recipe.total_fats) && recipe.servings ? (recipe.total_fat || recipe.total_fats) / recipe.servings : 0) || 0;
                              return perServing.toFixed(1);
                            })()}g
                          </Text>
                        </Box>
                      </SimpleGrid>
                    </Box>

                    {/* Rating Display */}
                    <Box>
                      {loadingStats[recipe.id] ? (
                        <HStack spacing={2}>
                          <Spinner size="sm" />
                          <Text fontSize="sm" color="gray.500">Loading ratings...</Text>
                        </HStack>
                      ) : recipeStats[recipe.id] ? (
                        <VStack spacing={2} align="stretch">
                          <HStack justify="space-between">
                            <StarRating
                              rating={recipeStats[recipe.id].average_rating}
                              size="sm"
                              showNumber={true}
                            />
                            <Text fontSize="xs" color="gray.500">
                              ({recipeStats[recipe.id].total_ratings} ratings)
                            </Text>
                          </HStack>
                          {recipeStats[recipe.id].verified_cooks > 0 && (
                            <Text fontSize="xs" color="blue.600">
                              {recipeStats[recipe.id].verified_cooks} verified cooks
                            </Text>
                          )}
                        </VStack>
                      ) : (
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => loadRecipeStats(recipe.id)}
                          leftIcon={<Icon as={FiStar} />}
                        >
                          Load Ratings
                        </Button>
                      )}
                    </Box>


                    {/* Recommendation Reason */}
                    {recipe.recommendation_reason && (
                      <Box>
                        <Text fontSize="xs" color="blue.600" fontStyle="italic">
                          💡 {recipe.recommendation_reason}
                        </Text>
                      </Box>
                    )}

                    {/* Based On */}
                    {recipe.based_on && (
                      <Box>
                        <Text fontSize="xs" color="gray.500">
                          Similar to: {recipe.based_on}
                        </Text>
                      </Box>
                    )}

                    {/* Action Buttons */}
                    <HStack spacing={2}>
                      <Button 
                        size="sm" 
                        colorScheme="blue" 
                        flex={1}
                        onClick={() => handleViewRecipe(recipe)}
                      >
                        View Recipe
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline"
                        onClick={() => handleAddToMealPlan(recipe)}
                        title="Add to Meal Plan"
                      >
                        <Icon as={FiCoffee} />
                      </Button>
                      <Button size="sm" variant="outline">
                        <Icon as={FiHeart} />
                      </Button>
                    </HStack>
                  </VStack>
                </CardBody>
              </Card>
            ))}
          </SimpleGrid>
        </VStack>
      ) : (
        <Alert status="info" borderRadius="lg">
          <AlertIcon />
          <Box>
            <Text fontWeight="semibold">No recommendations available</Text>
            <Text>Try adjusting your search criteria or check back later.</Text>
          </Box>
        </Alert>
      )}

      {/* Recipe Detail Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent maxW="800px">
          <ModalHeader pr={8}>
            <VStack align="start" spacing={2} flex={1} minW={0}>
              <Heading size="lg" noOfLines={2} wordBreak="break-word">{selectedRecipe?.title}</Heading>
              <HStack spacing={2}>
                <Badge colorScheme="purple">{selectedRecipe?.cuisine}</Badge>
                <Badge colorScheme={getDifficultyColor(selectedRecipe?.difficulty_level || '')}>
                  {selectedRecipe?.difficulty_level}
                </Badge>
                <Badge colorScheme="blue">
                  {selectedRecipe?.meal_type?.replace('_', ' ').toUpperCase()}
                </Badge>
              </HStack>
            </VStack>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            {selectedRecipe && (
              <VStack spacing={6} align="stretch">
                {/* Recipe Image */}
                <Box>
                  <SafeImage
                    src={selectedRecipe.image_url}
                    alt={selectedRecipe.title}
                    borderRadius="md"
                    height="300px"
                    objectFit="cover"
                    fallbackText="Recipe Image"
                    fallbackIcon={FiHome}
                  />
                </Box>

                {/* Recipe Info */}
                <SimpleGrid columns={4} spacing={4}>
                  <Stat textAlign="center">
                    <StatLabel>Prep Time</StatLabel>
                    <StatNumber>{selectedRecipe.prep_time} min</StatNumber>
                  </Stat>
                  <Stat textAlign="center">
                    <StatLabel>Cook Time</StatLabel>
                    <StatNumber>{selectedRecipe.cook_time} min</StatNumber>
                  </Stat>
                  <Stat textAlign="center">
                    <StatLabel>Total Time</StatLabel>
                    <StatNumber>{selectedRecipe.prep_time + selectedRecipe.cook_time} min</StatNumber>
                  </Stat>
                  <Stat textAlign="center">
                    <StatLabel>Servings</StatLabel>
                    <StatNumber>{selectedRecipe.servings}</StatNumber>
                  </Stat>
                </SimpleGrid>

                {/* Nutrition Information */}
                <Box>
                  <Heading size="md" mb={4}>Nutrition Information</Heading>
                  <SimpleGrid columns={2} spacing={4}>
                    <Box>
                      <Text fontWeight="semibold" mb={2}>Per Serving</Text>
                      <SimpleGrid columns={2} spacing={2}>
                        <Stat size="sm">
                          <StatLabel>Calories</StatLabel>
                          <StatNumber>{selectedRecipe.per_serving_calories.toFixed(0)}</StatNumber>
                        </Stat>
                        <Stat size="sm">
                          <StatLabel>Protein</StatLabel>
                          <StatNumber>{selectedRecipe.per_serving_protein.toFixed(1)}g</StatNumber>
                        </Stat>
                        <Stat size="sm">
                          <StatLabel>Carbs</StatLabel>
                          <StatNumber>{selectedRecipe.per_serving_carbs.toFixed(1)}g</StatNumber>
                        </Stat>
                        <Stat size="sm">
                          <StatLabel>Fat</StatLabel>
                          <StatNumber>{selectedRecipe.per_serving_fat.toFixed(1)}g</StatNumber>
                        </Stat>
                      </SimpleGrid>
                    </Box>
                    <Box>
                      <Text fontWeight="semibold" mb={2}>Total Recipe</Text>
                      <SimpleGrid columns={2} spacing={2}>
                        <Stat size="sm">
                          <StatLabel>Calories</StatLabel>
                          <StatNumber>{selectedRecipe.total_calories.toFixed(0)}</StatNumber>
                        </Stat>
                        <Stat size="sm">
                          <StatLabel>Protein</StatLabel>
                          <StatNumber>{selectedRecipe.total_protein.toFixed(1)}g</StatNumber>
                        </Stat>
                        <Stat size="sm">
                          <StatLabel>Carbs</StatLabel>
                          <StatNumber>{selectedRecipe.total_carbs.toFixed(1)}g</StatNumber>
                        </Stat>
                        <Stat size="sm">
                          <StatLabel>Fat</StatLabel>
                          <StatNumber>{selectedRecipe.total_fat.toFixed(1)}g</StatNumber>
                        </Stat>
                      </SimpleGrid>
                    </Box>
                  </SimpleGrid>
                </Box>

                {/* Dietary Tags */}
                {selectedRecipe.dietary_tags && selectedRecipe.dietary_tags.length > 0 && (
                  <Box>
                    <Text fontWeight="semibold" mb={2}>Dietary Tags</Text>
                    <HStack spacing={2} wrap="wrap">
                      {selectedRecipe.dietary_tags.map((tag, idx) => (
                        <Badge key={idx} colorScheme="green" size="md">
                          {tag.replace('-', ' ').toUpperCase()}
                        </Badge>
                      ))}
                    </HStack>
                  </Box>
                )}

                {/* Recipe Summary */}
                {selectedRecipe.summary && (
                  <Box>
                    <Text fontWeight="semibold" mb={2}>Description</Text>
                    <Text>{selectedRecipe.summary}</Text>
                  </Box>
                )}

                {/* Recommendation Info */}
                {(selectedRecipe.recommendation_reason || selectedRecipe.based_on) && (
                  <Box>
                    <Text fontWeight="semibold" mb={2}>Why We Recommend This</Text>
                    {selectedRecipe.recommendation_reason && (
                      <Text mb={2} color="blue.600" fontStyle="italic">
                        💡 {selectedRecipe.recommendation_reason}
                      </Text>
                    )}
                    {selectedRecipe.based_on && (
                      <Text fontSize="sm" color="gray.600">
                        Similar to: {selectedRecipe.based_on}
                      </Text>
                    )}
                  </Box>
                )}

                {/* Ingredients */}
                {selectedRecipe.ingredients && selectedRecipe.ingredients.length > 0 && (
                  <Box>
                    <Text fontWeight="semibold" mb={3}>Ingredients</Text>
                    <List spacing={2}>
                      {selectedRecipe.ingredients.map((ingredient: any, idx: number) => (
                        <ListItem key={idx}>
                          <HStack align="start">
                            <ListIcon as={FiCheck} color="green.500" />
                            <Text>
                              {typeof ingredient === 'string' ? (
                                ingredient
                              ) : (
                                <>
                              <Text as="span" fontWeight="semibold">
                                    {ingredient.quantity || ''} {ingredient.unit || ''}
                              </Text>
                                  {' '}{ingredient.name || ''}
                              {ingredient.notes && (
                                <Text as="span" color="gray.600" fontSize="sm">
                                  {' '}({ingredient.notes})
                                </Text>
                                  )}
                                </>
                              )}
                            </Text>
                          </HStack>
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}

                {/* Instructions */}
                {selectedRecipe.instructions && selectedRecipe.instructions.length > 0 && (
                  <Box>
                    <Text fontWeight="semibold" mb={3}>Instructions</Text>
                    <VStack spacing={4} align="stretch">
                      {selectedRecipe.instructions.map((instruction: any, idx: number) => (
                        <Box key={idx} p={4} bg="gray.50" borderRadius="md">
                          {typeof instruction === 'string' ? (
                            <Text>{instruction}</Text>
                          ) : (
                            <>
                          <HStack mb={2}>
                            <Badge colorScheme="blue" size="sm">
                                  Step {instruction.step || instruction.step_number || idx + 1}
                            </Badge>
                            {instruction.time_required && (
                              <Badge colorScheme="gray" size="sm">
                                {instruction.time_required} min
                              </Badge>
                            )}
                          </HStack>
                              {instruction.title && (
                          <Text fontWeight="semibold" mb={1}>
                            {instruction.title}
                          </Text>
                              )}
                              <Text>{instruction.description || ''}</Text>
                            </>
                          )}
                        </Box>
                      ))}
                    </VStack>
                  </Box>
                )}

                {/* Note if no ingredients/instructions */}
                {(!selectedRecipe.ingredients || selectedRecipe.ingredients.length === 0) && 
                 (!selectedRecipe.instructions || selectedRecipe.instructions.length === 0) && (
                  <Alert status="info" borderRadius="md">
                    <AlertIcon />
                    <Box>
                      <Text fontSize="sm">
                        <strong>Note:</strong> This recipe is from our database but detailed ingredients and instructions 
                        may not be available. You can search for this recipe in the Recipes section for more details.
                      </Text>
                    </Box>
                  </Alert>
                )}
              </VStack>
            )}
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Close
            </Button>
            {selectedRecipe && (
              <Button 
                colorScheme="blue" 
                onClick={() => {
                  onClose();
                  handleAddToMealPlan(selectedRecipe);
                }}
              >
                Add to Meal Plan
              </Button>
            )}
          </ModalFooter>
        </ModalContent>
      </Modal>
    </VStack>
  );
};

export default RecipeRecommendations;
