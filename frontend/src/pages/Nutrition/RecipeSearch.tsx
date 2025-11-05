import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  Heading,
  Text,
  Button,
  VStack,
  HStack,
  Badge,
  Input,
  Select,
  FormControl,
  FormLabel,
  InputGroup,
  InputLeftElement,
  Checkbox,
  CheckboxGroup,
  Stack,
  useColorModeValue,
  Alert,
  AlertIcon,
  Spinner,
  Center,
  Divider,
  IconButton,
  Icon,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  useDisclosure,
  useToast,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper
} from '@chakra-ui/react';
import { t } from '../../utils/translations';
import { 
  FiSearch, 
  FiClock, 
  FiCoffee,
  FiStar,
  FiHeart,
  FiMoreVertical,
  FiEye,
  FiPlus,
  FiFilter
} from 'react-icons/fi';
import MicronutrientFilters from '../../components/nutrition/MicronutrientFilters';
import AddToMealPlanModal from '../../components/nutrition/AddToMealPlanModal';

interface Recipe {
  id: string;
  title: string;
  cuisine: string;
  meal_type: string;
  servings: number;
  summary?: string; // Recipe summary/description
  calories?: number;
  protein?: number;
  carbs?: number;
  fats?: number;
  calculated_calories?: number;
  calculated_protein?: number;
  calculated_carbs?: number;
  calculated_fats?: number;
  // Per-serving nutrition (for daily logging)
  per_serving_calories?: number;
  per_serving_protein?: number;
  per_serving_carbs?: number;
  per_serving_fats?: number;
  per_serving_sodium?: number;
  // Total recipe nutrition (for full recipe display)
  total_calories?: number;
  total_protein?: number;
  total_carbs?: number;
  total_fats?: number;
  total_sodium?: number;
  prep_time: number;
  cook_time: number;
  difficulty_level: 'easy' | 'medium' | 'hard';
  dietary_tags: string[];
  ingredients?: (string | { name?: string; quantity?: number | string; unit?: string })[];
  instructions?: (string | { step?: number; description?: string })[];
  ingredients_list?: (string | { name?: string; quantity?: number | string; unit?: string })[];
  instructions_list?: (string | { step?: number; description?: string })[];
  rating: number;
  image?: string;
}

interface RecipeSearchProps {
  user?: any;
}

const RecipeSearch: React.FC<RecipeSearchProps> = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    cuisine: '',
    mealType: '',
    difficulty: '',
    maxCalories: '',
    maxPrepTime: ''
  });
  const [micronutrientFilters, setMicronutrientFilters] = useState({
    nutrients: [] as string[],
    minValues: {} as Record<string, number>,
    maxValues: {} as Record<string, number>,
    categories: [] as string[]
  });
  const [sortBy, setSortBy] = useState('');
  const [sortOrder, setSortOrder] = useState('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageKey, setPageKey] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [totalResults, setTotalResults] = useState(0);
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);
  const [userPreferences, setUserPreferences] = useState<any>(null);
  const [previewServings, setPreviewServings] = useState<number>(1);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();
  
  // Add to meal plan modal state
  const [addToMealPlanRecipe, setAddToMealPlanRecipe] = useState<Recipe | null>(null);
  const { isOpen: isAddToMealPlanOpen, onOpen: onAddToMealPlanOpen, onClose: onAddToMealPlanClose } = useDisclosure();
  

  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    loadUserPreferences();
    loadRecipes();
  }, []);

  const loadUserPreferences = async () => {
    try {
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        return;
      }
      
      const response = await fetch('http://localhost:8000/nutrition/preferences', {
        headers: { Authorization: `Bearer ${session.access_token}` }
      });
      
      if (response.ok) {
        const preferences = await response.json();
        setUserPreferences(preferences);
      }
    } catch (error) {
      console.error('Error loading user preferences:', error);
    }
  };

  // Auto-search when sorting or pagination changes
  useEffect(() => {
    if (currentPage > 0) { // Only load if currentPage is valid
      loadRecipes();
    }
  }, [sortBy, sortOrder, currentPage, pageKey]);


  const loadRecipes = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get Supabase session token for authentication
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        setError('Please log in to search recipes');
        return;
      }
      
      const headers = { Authorization: `Bearer ${session.access_token}` };
      
      // Use current filters and pagination
      const searchRequest = {
        query: searchQuery || undefined,
        cuisine: filters.cuisine || undefined,
        meal_type: filters.mealType || undefined,
        difficulty_level: filters.difficulty || undefined,
        max_calories: filters.maxCalories ? parseInt(filters.maxCalories) : undefined,
        max_prep_time: filters.maxPrepTime && filters.maxPrepTime !== '' ? parseInt(filters.maxPrepTime) : undefined,
        sort_by: sortBy || undefined,
        sort_order: sortOrder,
        limit: 20,
        page: currentPage,
        // Include user preferences for automatic filtering
        user_preferences: userPreferences ? {
          dietary_preferences: userPreferences.dietary_preferences || [],
          allergies: userPreferences.allergies || [],
          disliked_ingredients: userPreferences.disliked_ingredients || []
        } : undefined
      };
      
      const response = await fetch('http://localhost:8000/nutrition/recipes/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...headers
        },
        body: JSON.stringify(searchRequest)
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('🔍 FRONTEND RECEIVED RESPONSE:', data);
        console.log('🔍 FRONTEND RECEIVED RECIPES:', data.recipes?.length || 0);
        if (data.recipes && data.recipes.length > 0) {
          console.log('🔍 FIRST FEW RECIPES:', data.recipes.slice(0, 3).map((r: any) => `${r.title}: ${r.prep_time}min`));
        }
        
        // Force React to re-render by clearing recipes first
        setRecipes([]);
        
        // Use setTimeout to ensure the state update happens
        setTimeout(() => {
          if (data && Array.isArray(data)) {
            // Simple array response
            setRecipes(data);
            setTotalResults(data.length);
            setTotalPages(1);
          } else if (data && data.recipes && Array.isArray(data.recipes)) {
            // Paginated response
            setRecipes(data.recipes);
            setTotalResults(data.total || 0);
            setTotalPages(data.pages || 1);
          } else {
            console.error('Invalid data received:', data);
            setError('Invalid data received from server');
            setRecipes([]);
          }
        }, 0);
        setError(null);
      } else {
        throw new Error('Failed to load recipes');
      }
      
    } catch (err: any) {
      console.error('Error loading recipes:', err);
      setError('Failed to load recipes');
      setRecipes([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Reset to page 1 when searching with new filters
      setCurrentPage(1);
      setPageKey(prev => prev + 1);
      
      // Get Supabase session token for authentication
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        setError('Please log in to search recipes');
        return;
      }
      
      const headers = { Authorization: `Bearer ${session.access_token}` };
      
      // Search recipes with current filters
      const searchRequest = {
        query: searchQuery || undefined,
        cuisine: filters.cuisine || undefined,
        meal_type: filters.mealType || undefined,
        difficulty_level: filters.difficulty || undefined,
        max_calories: filters.maxCalories ? parseInt(filters.maxCalories) : undefined,
        max_prep_time: filters.maxPrepTime && filters.maxPrepTime !== '' ? parseInt(filters.maxPrepTime) : undefined,
        sort_by: sortBy || undefined,
        sort_order: sortOrder,
        limit: 20, // Increased default limit
        page: 1, // Always start from page 1 when searching
        // Micronutrient filters
        micronutrient_filters: micronutrientFilters.nutrients.length > 0 ? {
          nutrients: micronutrientFilters.nutrients,
          min_values: micronutrientFilters.minValues,
          max_values: micronutrientFilters.maxValues,
          categories: micronutrientFilters.categories
        } : undefined,
        // Include user preferences for automatic filtering
        user_preferences: userPreferences ? {
          dietary_preferences: userPreferences.dietary_preferences || [],
          allergies: userPreferences.allergies || [],
          disliked_ingredients: userPreferences.disliked_ingredients || []
        } : undefined
      };
      
      console.log('🔍 FRONTEND SENDING REQUEST:', searchRequest);
      
      
      const response = await fetch('http://localhost:8000/nutrition/recipes/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...headers
        },
        body: JSON.stringify(searchRequest)
      });
      
      if (response.ok) {
        const data = await response.json();
        // Force React to re-render by clearing recipes first
        setRecipes([]);
        
        // Use setTimeout to ensure the state update happens
        setTimeout(() => {
          if (Array.isArray(data)) {
            // Simple array response
            setRecipes(data);
            setTotalResults(data.length);
            setTotalPages(1);
          } else {
            // Paginated response
            setRecipes(data.recipes || []);
            setTotalResults(data.total || 0);
            setTotalPages(data.pages || 1);
          }
        }, 0);
        setError(null);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to search recipes');
      }
    } catch (err: any) {
      console.error('Search error:', err);
      setError('Failed to search recipes');
    } finally {
      setLoading(false);
    }
  };

  const handleRecipeView = (recipe: Recipe) => {
    setSelectedRecipe(recipe);
    setPreviewServings(recipe.servings || 1);
    onOpen();
  };

  const handleServingsChange = (newServings: number) => {
    if (newServings > 0 && newServings <= 20) {
      setPreviewServings(newServings);
    }
  };

  const calculateScaledNutrition = (servings: number) => {
    if (!selectedRecipe) return { calories: 0, protein: 0, carbs: 0, fats: 0 };
    const baseServings = selectedRecipe.servings || 1;
    const scaleFactor = servings / baseServings;
    
    return {
      calories: Math.round((selectedRecipe.calculated_calories || 0) * scaleFactor),
      protein: Math.round((selectedRecipe.calculated_protein || 0) * scaleFactor * 10) / 10,
      carbs: Math.round((selectedRecipe.calculated_carbs || 0) * scaleFactor * 10) / 10,
      fats: Math.round((selectedRecipe.calculated_fats || 0) * scaleFactor * 10) / 10,
    };
  };

  const calculateScaledIngredient = (ingredient: any, servings: number) => {
    if (!selectedRecipe || !ingredient) return ingredient;
    const baseServings = selectedRecipe.servings || 1;
    const scaleFactor = servings / baseServings;
    
    if (typeof ingredient === 'string') {
      return ingredient; // Can't scale string ingredients
    }
    
    const quantity = parseFloat(ingredient.quantity) || 0;
    const scaledQuantity = quantity * scaleFactor;
    
    return {
      ...ingredient,
      quantity: scaledQuantity.toFixed(2),
      original_quantity: quantity,
      scaled: true
    };
  };

  const handleAddToMealPlan = (recipe: Recipe) => {
    setAddToMealPlanRecipe(recipe);
    onAddToMealPlanOpen();
  };

  const handleRecipeAdded = () => {
    // Refresh the page or show success message
    toast({
      title: "Recipe Added!",
      description: "Recipe has been added to your meal plan",
      status: "success",
      duration: 3000,
      isClosable: true,
    });
  };

  const handleClearFilters = () => {
    setSearchQuery('');
    setFilters({
      cuisine: '',
      mealType: '',
      difficulty: '',
      maxCalories: '',
      maxPrepTime: ''
    });
    setMicronutrientFilters({
      nutrients: [],
      minValues: {},
      maxValues: {},
      categories: []
    });
    setSortBy('');
    setSortOrder('asc');
    setCurrentPage(1);
    loadRecipes();
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'green';
      case 'medium': return 'yellow';
      case 'hard': return 'red';
      default: return 'gray';
    }
  };

  if (loading && recipes.length === 0) {
    return (
      <Center h="400px">
        <VStack spacing={4}>
          <Spinner size="xl" />
          <Text>{t('nutrition.loading', 'en')}</Text>
        </VStack>
      </Center>
    );
  }

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <Box>
          <Heading size="lg" mb={2}>
            {t('nutrition.recipeSearch.title', 'en')}
          </Heading>
          <Text color="gray.600" mb={4}>
            {t('nutrition.recipeSearch.subtitle', 'en')}
          </Text>
          
          {/* Search Help */}
          <Alert status="info" borderRadius="md" mb={4}>
            <AlertIcon />
            <Box>
              <Text fontWeight="semibold" mb={2}>Search Tips:</Text>
              <VStack align="start" spacing={1} fontSize="sm">
                <Text>• <Text as="span" fontWeight="bold">pasta, chicken, curry</Text> - Search by ingredients or cuisine</Text>
                <Text>• <Text as="span" fontWeight="bold">quick, easy, healthy</Text> - Search by cooking style</Text>
                <Text>• <Text as="span" fontWeight="bold">#1, #10, #50</Text> - Find specific recipe numbers</Text>
                <Text>• <Text as="span" fontWeight="bold">range:1-20</Text> - Get recipes in a range</Text>
                <Text>• <Text as="span" fontWeight="bold">first:10, last:10</Text> - Get first or last N recipes</Text>
              </VStack>
            </Box>
          </Alert>
        </Box>

        {/* Search and Filters */}
        <Card bg={cardBg} borderColor={borderColor}>
          <CardBody>
            <VStack spacing={4} align="stretch">
              {/* Search Bar */}
              <HStack spacing={2}>
                <InputGroup flex={1}>
                  <InputLeftElement>
                    <FiSearch />
                  </InputLeftElement>
                  <Input
                    placeholder="Search recipes by name, ingredients, or cuisine..."
                    value={searchQuery}
                    onChange={(e: any) => setSearchQuery(e.target.value)}
                    onKeyPress={(e: any) => e.key === 'Enter' && handleSearch()}
                    list="search-suggestions"
                  />
                  <datalist id="search-suggestions">
                    <option value="pasta" />
                    <option value="chicken" />
                    <option value="curry" />
                    <option value="pizza" />
                    <option value="salad" />
                    <option value="soup" />
                    <option value="dessert" />
                    <option value="breakfast" />
                    <option value="quick" />
                    <option value="healthy" />
                    <option value="vegetarian" />
                    <option value="vegan" />
                    <option value="gluten-free" />
                    <option value="low-carb" />
                    <option value="high-protein" />
                    <option value="#1" />
                    <option value="#10" />
                    <option value="#50" />
                    <option value="range:1-20" />
                    <option value="first:10" />
                    <option value="last:10" />
                  </datalist>
                </InputGroup>
                <Button
                  colorScheme="blue"
                  leftIcon={<FiSearch />}
                  onClick={handleSearch}
                  isLoading={loading}
                  px={8}
                >
                  Search
                </Button>
                <Button
                  variant="outline"
                  onClick={handleClearFilters}
                  size="md"
                >
                  Clear
                </Button>
              </HStack>

              {/* Micronutrient Filters */}
              <MicronutrientFilters 
                onFiltersChange={setMicronutrientFilters}
                initialFilters={micronutrientFilters}
              />

              {/* Basic Filters */}
              <Grid templateColumns={{ base: '1fr', md: 'repeat(3, 1fr)' }} gap={4}>
                <FormControl>
                  <FormLabel>{t('nutrition.cuisine', 'en')}</FormLabel>
                  <Select
                    value={filters.cuisine}
                    onChange={(e: any) => setFilters({...filters, cuisine: e.target.value})}
                  >
                    <option value="">{t('nutrition.allCuisines', 'en')}</option>
                    <option value="Mediterranean">Mediterranean</option>
                    <option value="Asian">Asian</option>
                    <option value="International">International</option>
                    <option value="Italian">Italian</option>
                    <option value="Mexican">Mexican</option>
                    <option value="French">French</option>
                    <option value="Chinese">Chinese</option>
                    <option value="Thai">Thai</option>
                    <option value="Japanese">Japanese</option>
                    <option value="Korean">Korean</option>
                    <option value="Indian">Indian</option>
                    <option value="Greek">Greek</option>
                    <option value="Spanish">Spanish</option>
                    <option value="German">German</option>
                    <option value="American">American</option>
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel>{t('nutrition.mealType', 'en')}</FormLabel>
                  <Select
                    value={filters.mealType}
                    onChange={(e: any) => setFilters({...filters, mealType: e.target.value})}
                  >
                    <option value="">{t('nutrition.allMealTypes', 'en')}</option>
                    <option value="breakfast">{t('nutrition.breakfast', 'en')}</option>
                    <option value="lunch">{t('nutrition.lunch', 'en')}</option>
                    <option value="dinner">{t('nutrition.dinner', 'en')}</option>
                    <option value="snack">{t('nutrition.snack', 'en')}</option>
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel>{t('nutrition.difficulty', 'en')}</FormLabel>
                  <Select
                    value={filters.difficulty}
                    onChange={(e: any) => setFilters({...filters, difficulty: e.target.value})}
                  >
                    <option value="">{t('nutrition.allDifficulties', 'en')}</option>
                    <option value="easy">{t('nutrition.easy', 'en')}</option>
                    <option value="medium">{t('nutrition.medium', 'en')}</option>
                    <option value="hard">{t('nutrition.hard', 'en')}</option>
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel>{t('nutrition.maxCalories', 'en')}</FormLabel>
                  <Input
                    type="number"
                    placeholder="e.g. 500"
                    value={filters.maxCalories}
                    onChange={(e: any) => setFilters({...filters, maxCalories: e.target.value})}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>{t('nutrition.maxPrepTime', 'en')}</FormLabel>
                  <Input
                    type="number"
                    placeholder="e.g. 30"
                    value={filters.maxPrepTime}
                    onChange={(e: any) => setFilters({...filters, maxPrepTime: e.target.value})}
                  />
                </FormControl>

              </Grid>

              <Button colorScheme="blue" onClick={handleSearch} isLoading={loading}>
                <FiSearch />
                {t('nutrition.search', 'en')}
              </Button>
            </VStack>
          </CardBody>
        </Card>

        {/* Sorting and Results Info */}
        <Card bg={cardBg} borderColor={borderColor}>
          <CardBody>
            <HStack justify="space-between" align="center" wrap="wrap" spacing={4}>
              <VStack align="start" spacing={2}>
                <Text fontSize="sm" color="gray.600">
                  {totalResults > 0 ? t('recipeSearch.showingResults', 'en').replace('{start}', '1').replace('{end}', String(Array.isArray(recipes) ? recipes.length : 0)).replace('{total}', String(totalResults)) : t('recipeSearch.noResults')}
                </Text>
                {totalPages > 1 && (
                  <Text fontSize="sm" color="gray.600">
                    {t('recipeSearch.page')} {currentPage} {t('recipeSearch.of')} {totalPages}
                  </Text>
                )}
              </VStack>
              
              <HStack spacing={4} wrap="wrap">
                <FormControl minW="200px">
                  <FormLabel fontSize="sm">Sort by</FormLabel>
                  <Select
                    value={sortBy}
                    onChange={(e: any) => setSortBy(e.target.value)}
                    placeholder="Default order"
                  >
                    <option value="title">Title (A-Z)</option>
                    <option value="calories">Calories (Low to High)</option>
                    <option value="protein">Protein (Low to High)</option>
                    <option value="prep_time">Prep Time (Short to Long)</option>
                    <option value="difficulty">Difficulty (Easy to Hard)</option>
                    <option value="id">Recipe Number</option>
                  </Select>
                </FormControl>
                
                {sortBy && (
                  <FormControl minW="120px">
                    <FormLabel fontSize="sm">Order</FormLabel>
                    <Select
                      value={sortOrder}
                      onChange={(e: any) => setSortOrder(e.target.value)}
                    >
                      <option value="asc">Ascending</option>
                      <option value="desc">Descending</option>
                    </Select>
                  </FormControl>
                )}
              </HStack>
            </HStack>
          </CardBody>
        </Card>

        {error && (
          <Alert status="error">
            <AlertIcon />
            {error}
          </Alert>
        )}

        {/* Recipe Results */}
        <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4} key={`recipes-${sortBy}-${sortOrder}-${currentPage}`}>
          {Array.isArray(recipes) ? recipes.map((recipe, index) => (
            <Card key={`${recipe.id}-${index}-${sortBy}-${sortOrder}`} bg={cardBg} borderColor={borderColor} position="relative" maxW="sm" mx="auto" w="full" overflow="hidden">
              <CardHeader pb={2}>
                <HStack justify="space-between" align="start" spacing={2}>
                  <VStack align="start" spacing={1} flex={1} minW={0}>
                    <Heading size="sm" noOfLines={2} wordBreak="break-word" width="100%">
                      {recipe.title.replace(/\s*\(#\d+\)\s*$/, '')}
                    </Heading>
                    {/* Dietary Tags - Prominently displayed */}
                    {recipe.dietary_tags && recipe.dietary_tags.length > 0 && (
                      <Box width="100%" overflow="hidden">
                        <HStack spacing={1} wrap="wrap" maxW="100%" overflow="hidden">
                          {recipe.dietary_tags
                            .filter((tag: string) => 
                              ['vegetarian', 'vegan', 'contains-peanuts', 'contains-tree-nuts', 
                               'contains-nightshades', 'contains-dairy', 'contains-eggs', 
                               'contains-gluten', 'contains-soy', 'contains-fish'].includes(tag.toLowerCase())
                            )
                            .slice(0, 5)
                            .map((tag: string) => {
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
                                  key={tag} 
                                  colorScheme={colorScheme} 
                                  size="sm" 
                                  fontSize="xs"
                                  noOfLines={1}
                                  maxW="100%"
                                  wordBreak="break-word"
                                  textTransform="capitalize"
                                  flexShrink={0}
                                >
                                  {tag.replace('contains-', '').replace('-', ' ')}
                                </Badge>
                              );
                            })}
                          {recipe.dietary_tags.length > 5 && (
                            <Text fontSize="xs" color="gray.500" noOfLines={1} flexShrink={0}>+{recipe.dietary_tags.length - 5}</Text>
                          )}
                        </HStack>
                      </Box>
                    )}
                    <Box width="100%" overflow="hidden">
                      <HStack spacing={2} wrap="wrap" maxW="100%" overflow="hidden">
                        <Badge colorScheme="purple" size="sm" noOfLines={1} maxW="100%" wordBreak="break-word" flexShrink={0}>
                        {recipe.meal_type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </Badge>
                    </HStack>
                    </Box>
                  </VStack>
                  {recipe.id && recipe.id.startsWith('recipe_') && (
                    <Badge 
                      colorScheme="gray" 
                      size="sm" 
                      fontSize="xs"
                      position="absolute"
                      top={2}
                      right={2}
                      flexShrink={0}
                    >
                      #{parseInt(recipe.id.replace('recipe_', ''))}
                    </Badge>
                  )}
                  <Menu flexShrink={0}>
                    <MenuButton as={IconButton} icon={<FiMoreVertical />} size="sm" variant="ghost" />
                    <MenuList>
                      <MenuItem icon={<FiEye />} onClick={() => handleRecipeView(recipe)}>
                        {t('nutrition.viewRecipe', 'en')}
                      </MenuItem>
                      <MenuItem icon={<FiPlus />} onClick={() => handleAddToMealPlan(recipe)}>
                        {t('nutrition.addToMealPlan', 'en')}
                      </MenuItem>
                      <MenuItem icon={<FiHeart />}>
                        {t('nutrition.saveRecipe', 'en')}
                      </MenuItem>
                    </MenuList>
                  </Menu>
                </HStack>
              </CardHeader>
              <CardBody pt={0}>
                <VStack spacing={3} align="stretch" overflow="hidden">
                  {/* Nutritional Info */}
                  <VStack spacing={2} align="stretch" width="100%">
                    {/* Total Recipe Nutrition */}
                    <Box width="100%" overflow="hidden">
                      <Text fontSize="xs" color="gray.500" mb={1}>Total Recipe ({recipe.servings || 1} {recipe.servings === 1 ? 'serving' : 'servings'})</Text>
                      <HStack justify="space-between" fontSize="sm" spacing={2}>
                        <Text fontWeight="bold" flex={1} minW={0} wordBreak="break-word">{Math.round(recipe.total_calories || recipe.calculated_calories || 0)} {t('nutrition.calories', 'en')}</Text>
                        <Text fontWeight="bold" flex={1} minW={0} wordBreak="break-word">{Math.round(recipe.total_protein || recipe.calculated_protein || 0)}g {t('nutrition.protein', 'en')}</Text>
                      </HStack>
                      <HStack justify="space-between" fontSize="sm" spacing={2}>
                        <Text flex={1} minW={0} wordBreak="break-word">{Math.round(recipe.total_carbs || recipe.calculated_carbs || 0)}g {t('nutrition.carbs', 'en')}</Text>
                        <Text flex={1} minW={0} wordBreak="break-word">{Math.round(recipe.total_fats || recipe.calculated_fats || 0)}g {t('nutrition.fats', 'en')}</Text>
                      </HStack>
                    </Box>
                    
                    {/* Per-Serving Nutrition */}
                    <Box width="100%" overflow="hidden">
                      <Text fontSize="xs" color="gray.500" mb={1}>Per Serving</Text>
                      <SimpleGrid columns={2} spacing={2} fontSize="sm">
                        <Box>
                          <Text fontWeight="bold" color="blue.600" fontSize="xs" noOfLines={1}>
                            {(() => {
                              const perServing = recipe.per_serving_calories || 
                                (recipe.total_calories && recipe.servings ? Math.round(recipe.total_calories / recipe.servings) : 0) ||
                                (recipe.calculated_calories || 0);
                              return Math.round(perServing);
                            })()} {t('nutrition.calories', 'en')}
                          </Text>
                        </Box>
                        <Box>
                          <Text fontWeight="bold" color="blue.600" fontSize="xs" noOfLines={1}>
                            {(() => {
                              const perServing = recipe.per_serving_protein || 
                                (recipe.total_protein && recipe.servings ? recipe.total_protein / recipe.servings : 0) ||
                                (recipe.calculated_protein || 0);
                              return Math.round(perServing * 10) / 10;
                            })()}g {t('nutrition.protein', 'en')}
                          </Text>
                        </Box>
                        <Box>
                          <Text color="blue.600" fontSize="xs" noOfLines={1}>
                            {(() => {
                              const perServing = recipe.per_serving_carbs || 
                                (recipe.total_carbs && recipe.servings ? recipe.total_carbs / recipe.servings : 0) ||
                                (recipe.calculated_carbs || 0);
                              return Math.round(perServing * 10) / 10;
                            })()}g {t('nutrition.carbs', 'en')}
                          </Text>
                        </Box>
                        <Box>
                          <Text color="blue.600" fontSize="xs" noOfLines={1}>
                            {(() => {
                              const perServing = recipe.per_serving_fats || 
                                (recipe.total_fats && recipe.servings ? recipe.total_fats / recipe.servings : 0) ||
                                (recipe.calculated_fats || 0);
                              return Math.round(perServing * 10) / 10;
                            })()}g {t('nutrition.fats', 'en')}
                          </Text>
                        </Box>
                      </SimpleGrid>
                    </Box>
                  </VStack>

                  <Divider />

                  {/* Recipe Details */}
                  <HStack justify="space-between" fontSize="sm">
                    <HStack>
                      <FiClock />
                      <Text>{recipe.prep_time} min</Text>
                    </HStack>
                    <Badge colorScheme={getDifficultyColor(recipe.difficulty_level)} size="sm">
                      {recipe.difficulty_level}
                    </Badge>
                  </HStack>

                  {/* Dietary Tags */}
                  {recipe.dietary_tags && recipe.dietary_tags.length > 0 && (
                    <Box width="100%" overflow="hidden">
                      <HStack wrap="wrap" spacing={1} maxW="100%">
                        {recipe.dietary_tags.slice(0, 6).map((tag) => (
                          <Badge 
                            key={tag} 
                            size="sm" 
                            colorScheme="green" 
                            variant="subtle"
                            noOfLines={1}
                            maxW="100%"
                            wordBreak="break-word"
                          >
                        {tag}
                      </Badge>
                    ))}
                        {recipe.dietary_tags.length > 6 && (
                          <Text fontSize="xs" color="gray.500" noOfLines={1}>
                            +{recipe.dietary_tags.length - 6} more
                          </Text>
                        )}
                  </HStack>
                    </Box>
                  )}

                  {/* Actions */}
                  <HStack spacing={2}>
                    <Button size="sm" colorScheme="blue" flex={1} onClick={() => handleRecipeView(recipe)}>
                      {t('nutrition.viewRecipe', 'en')}
                    </Button>
                    <Button size="sm" variant="outline" flex={1}>
                      {t('nutrition.addToMealPlan', 'en')}
                    </Button>
                  </HStack>
                </VStack>
              </CardBody>
            </Card>
          )) : null}
        </SimpleGrid>

        {/* Pagination */}
        {totalPages > 1 && (
          <Card bg={cardBg} borderColor={borderColor} mt={6}>
            <CardBody>
              <HStack justify="center" spacing={2} wrap="wrap">
                {/* First Page */}
                <Button
                  size="sm"
                  variant={currentPage === 1 ? "solid" : "outline"}
                  colorScheme={currentPage === 1 ? "blue" : "gray"}
                  onClick={() => {
                    setCurrentPage(1);
                    setPageKey(prev => prev + 1);
                  }}
                >
{t('recipeSearch.first')}
                </Button>
                
                {/* Previous Page */}
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    setCurrentPage(Math.max(1, currentPage - 1));
                    setPageKey(prev => prev + 1);
                  }}
                  isDisabled={currentPage === 1}
                >
{t('recipeSearch.previous')}
                </Button>
                
                {/* Page numbers with proper logic */}
                {(() => {
                  const pages = [];
                  // const maxVisible = 5; // Unused for now
                  
                  // Always show page 1
                  pages.push(
                    <Button
                      key="page-1"
                      size="sm"
                      variant={currentPage === 1 ? "solid" : "outline"}
                      colorScheme={currentPage === 1 ? "blue" : "gray"}
                      onClick={() => {
                        setCurrentPage(1);
                        setPageKey(prev => prev + 1);
                      }}
                    >
                      1
                    </Button>
                  );
                  
                  // Calculate visible pages around current page
                  let startPage = Math.max(2, currentPage - 1);
                  let endPage = Math.min(totalPages - 1, currentPage + 1);
                  
                  // Adjust if we're near the beginning
                  if (currentPage <= 3) {
                    startPage = 2;
                    endPage = Math.min(5, totalPages - 1);
                  }
                  
                  // Adjust if we're near the end
                  if (currentPage >= totalPages - 2) {
                    startPage = Math.max(2, totalPages - 4);
                    endPage = totalPages - 1;
                  }
                  
                  // Add ellipsis after page 1 if needed
                  if (startPage > 2) {
                    pages.push(<Text key="ellipsis1">...</Text>);
                  }
                  
                  // Add visible page numbers (excluding 1 and last page)
                  for (let i = startPage; i <= endPage; i++) {
                    if (i !== 1 && i !== totalPages) {
                      pages.push(
                        <Button
                          key={`page-${i}`}
                          size="sm"
                          variant={currentPage === i ? "solid" : "outline"}
                          colorScheme={currentPage === i ? "blue" : "gray"}
                          onClick={() => {
                            setCurrentPage(i);
                            setPageKey(prev => prev + 1);
                          }}
                        >
                          {i}
                        </Button>
                      );
                    }
                  }
                  
                  // Add ellipsis before last page if needed
                  if (endPage < totalPages - 1) {
                    pages.push(<Text key="ellipsis2">...</Text>);
                  }
                  
                  // Always show last page if there are multiple pages
                  if (totalPages > 1) {
                    pages.push(
                      <Button
                        key={`page-${totalPages}`}
                        size="sm"
                        variant={currentPage === totalPages ? "solid" : "outline"}
                        colorScheme={currentPage === totalPages ? "blue" : "gray"}
                        onClick={() => {
                          setCurrentPage(totalPages);
                          setPageKey(prev => prev + 1);
                        }}
                      >
                        {totalPages}
                      </Button>
                    );
                  }
                  
                  return pages;
                })()}
                
                {/* Next Page */}
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    setCurrentPage(Math.min(totalPages, currentPage + 1));
                    setPageKey(prev => prev + 1);
                  }}
                  isDisabled={currentPage === totalPages}
                >
{t('recipeSearch.next')}
                </Button>
                
                {/* Last Page */}
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    setCurrentPage(totalPages);
                    setPageKey(prev => prev + 1);
                  }}
                  isDisabled={currentPage === totalPages}
                >
{t('recipeSearch.last')}
                </Button>
              </HStack>
            </CardBody>
          </Card>
        )}

        {(!Array.isArray(recipes) || recipes.length === 0) && !loading && (
          <Center h="200px">
            <VStack spacing={4}>
              <FiCoffee size={48} color="gray" />
              <Text color="gray.600">{t('nutrition.noRecipesFound', 'en')}</Text>
              <Button colorScheme="blue" onClick={loadRecipes}>
                {t('nutrition.loadAllRecipes', 'en')}
              </Button>
            </VStack>
          </Center>
        )}

        {/* Recipe Detail Modal */}
        <Modal isOpen={isOpen} onClose={onClose} size="xl">
          <ModalOverlay />
          <ModalContent>
            <ModalHeader pr={8}>
              <Text noOfLines={2} wordBreak="break-word">{selectedRecipe?.title}</Text>
            </ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              {selectedRecipe && (
                <VStack spacing={4} align="stretch">
                  {/* Serving Size Adjuster */}
                  <Box borderBottom="1px" borderColor="gray.200" pb={4}>
                    <VStack align="stretch" spacing={3}>
                      <Heading size="sm" mb={2}>Portion Size</Heading>
                      <HStack spacing={2} align="center" justify="space-between">
                        <HStack spacing={2} align="center" flex={1}>
                          <Button
                            size="md"
                            colorScheme="blue"
                            borderRadius="full"
                            onClick={() => handleServingsChange(Math.max(0.25, previewServings - 0.25))}
                          >
                            −
                          </Button>
                          
                          <NumberInput
                            value={previewServings}
                            min={0.25}
                            max={20}
                            step={0.25}
                            precision={2}
                            onChange={(_, value) => handleServingsChange(value)}
                            width="120px"
                          >
                            <NumberInputField 
                              textAlign="center" 
                              fontWeight="semibold"
                              fontSize="md"
                            />
                          </NumberInput>
                          
                          <Text fontSize="sm" color="gray.600" minW="60px">
                            serving{previewServings !== 1 ? 's' : ''}
                          </Text>
                          
                          <Button
                            size="md"
                            colorScheme="blue"
                            borderRadius="full"
                            onClick={() => handleServingsChange(Math.min(20, previewServings + 0.25))}
                          >
                            +
                          </Button>
                        </HStack>
                        
                        <Button
                          size="sm"
                          variant="ghost"
                          colorScheme="blue"
                          onClick={() => {
                            const originalServings = selectedRecipe.servings || 1;
                            handleServingsChange(originalServings);
                          }}
                        >
                          Reset
                        </Button>
                      </HStack>
                      
                      {/* Preview of scaled nutrition */}
                      {previewServings !== (selectedRecipe.servings || 1) && (
                        <Box p={3} bg="blue.50" borderRadius="md" borderLeft="3px" borderColor="blue.500">
                          <Text fontSize="sm" color="gray.700" mb={1} fontWeight="semibold">
                            Preview Nutrition ({previewServings} servings):
                          </Text>
                          <HStack spacing={4}>
                            {(() => {
                              const scaled = calculateScaledNutrition(previewServings);
                              return (
                                <>
                                  <Text fontSize="sm" color="blue.700">{scaled.calories} cal</Text>
                                  <Text fontSize="sm" color="green.700">P: {scaled.protein}g</Text>
                                  <Text fontSize="sm" color="orange.700">C: {scaled.carbs}g</Text>
                                  <Text fontSize="sm" color="purple.700">F: {scaled.fats}g</Text>
                                </>
                              );
                            })()}
                          </HStack>
                        </Box>
                      )}
                    </VStack>
                  </Box>

                  {/* Recipe Info */}
                  <HStack justify="space-between">
                    <HStack spacing={4}>
                      <Text fontSize="sm">
                        {previewServings === (selectedRecipe.servings || 1) 
                          ? (selectedRecipe.calculated_calories || 0)
                          : calculateScaledNutrition(previewServings).calories
                        } {t('nutrition.calories', 'en')}
                      </Text>
                      <Text fontSize="sm">
                        {previewServings === (selectedRecipe.servings || 1)
                          ? (selectedRecipe.calculated_protein || 0)
                          : calculateScaledNutrition(previewServings).protein
                        }g {t('nutrition.protein', 'en')}
                      </Text>
                      <Text fontSize="sm">
                        {previewServings === (selectedRecipe.servings || 1)
                          ? (selectedRecipe.calculated_carbs || 0)
                          : calculateScaledNutrition(previewServings).carbs
                        }g {t('nutrition.carbs', 'en')}
                      </Text>
                      <Text fontSize="sm">
                        {previewServings === (selectedRecipe.servings || 1)
                          ? (selectedRecipe.calculated_fats || 0)
                          : calculateScaledNutrition(previewServings).fats
                        }g {t('nutrition.fats', 'en')}
                      </Text>
                    </HStack>
                    <HStack spacing={2}>
                      <FiClock />
                      <Text fontSize="sm">{selectedRecipe.prep_time} min</Text>
                      <FiStar />
                      <Text fontSize="sm">{selectedRecipe.rating}</Text>
                    </HStack>
                  </HStack>

                  {/* Dietary Tags */}
                  <HStack wrap="wrap" spacing={1}>
                    {(selectedRecipe.dietary_tags || []).map((tag: string) => (
                      <Badge key={tag} size="sm" colorScheme="green" variant="subtle">
                        {tag}
                      </Badge>
                    ))}
                  </HStack>

                  <Divider />

                  {/* Ingredients */}
                  <Box>
                    <Heading size="sm" mb={2}>
                      {t('nutrition.ingredients', 'en')}
                      {previewServings !== (selectedRecipe.servings || 1) && (
                        <Text as="span" fontSize="xs" color="blue.600" fontWeight="normal" ml={2}>
                          (scaled for {previewServings} servings)
                        </Text>
                      )}
                    </Heading>
                    <VStack spacing={2} align="stretch">
                      {(selectedRecipe.ingredients_list || selectedRecipe.ingredients || []).map((ingredient: any, index: number) => {
                        const scaledIngredient = calculateScaledIngredient(ingredient, previewServings);
                        return (
                          <Text key={index} fontSize="sm" pl={4} borderLeft="3px solid" borderColor="blue.200">
                            {typeof scaledIngredient === 'string' 
                              ? scaledIngredient 
                              : `${scaledIngredient.name || 'Unknown'} - ${scaledIngredient.quantity || ''}${scaledIngredient.unit || 'g'}`
                            }
                          </Text>
                        );
                      })}
                    </VStack>
                  </Box>

                  {/* Instructions */}
                  <Box>
                    <Heading size="sm" mb={2}>{t('nutrition.instructions', 'en')}</Heading>
                    <VStack spacing={2} align="stretch">
                      {(selectedRecipe.instructions_list || selectedRecipe.instructions || []).map((instruction: any, index: number) => (
                        <Box key={index} p={3} bg="gray.50" borderRadius="md">
                          <Text fontWeight="bold" color="blue.600" mb={1}>
                            Step {typeof instruction === 'string' ? index + 1 : (instruction.step || index + 1)}
                          </Text>
                          <Text fontSize="sm">
                            {typeof instruction === 'string' ? instruction : (instruction.description || '')}
                          </Text>
                        </Box>
                      ))}
                    </VStack>
                  </Box>
                </VStack>
              )}
            </ModalBody>
            <ModalFooter>
              <Button variant="ghost" mr={3} onClick={onClose}>
                {t('close', 'en')}
              </Button>
              <Button 
                colorScheme="blue"
                onClick={() => {
                  onClose();
                  setAddToMealPlanRecipe(selectedRecipe);
                  onAddToMealPlanOpen();
                }}
              >
                {t('nutrition.addToMealPlan', 'en')} ({previewServings} servings)
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>

        {/* Add to Meal Plan Modal */}
        {addToMealPlanRecipe && (
          <AddToMealPlanModal
            isOpen={isAddToMealPlanOpen}
            onClose={onAddToMealPlanClose}
            recipe={addToMealPlanRecipe}
            onRecipeAdded={handleRecipeAdded}
            initialServings={previewServings}
          />
        )}
      </VStack>
    </Box>
  );
};

export default RecipeSearch;
