import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
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
  useDisclosure
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
  FiPlus
} from 'react-icons/fi';

interface Recipe {
  id: string;
  title: string;
  cuisine: string;
  meal_type: string;
  calories?: number;
  protein?: number;
  carbs?: number;
  fats?: number;
  calculated_calories?: number;
  calculated_protein?: number;
  calculated_carbs?: number;
  calculated_fats?: number;
  prep_time: number;
  cook_time: number;
  difficulty_level: 'easy' | 'medium' | 'hard';
  dietary_tags: string[];
  ingredients?: string[];
  instructions?: string[];
  ingredients_list?: string[];
  instructions_list?: string[];
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
    dietaryTags: [] as string[],
    maxPrepTime: ''
  });
  const [sortBy, setSortBy] = useState('');
  const [sortOrder, setSortOrder] = useState('asc');
  const [currentPage, setCurrentPage] = useState(1);
  const [pageKey, setPageKey] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [totalResults, setTotalResults] = useState(0);
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);
  const { isOpen, onOpen, onClose } = useDisclosure();

  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    loadRecipes();
  }, []);

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
      const { supabase } = await import('../../lib/supabase');
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
        dietary_tags: filters.dietaryTags.length > 0 ? filters.dietaryTags : undefined,
        max_prep_time: filters.maxPrepTime && filters.maxPrepTime !== '' ? parseInt(filters.maxPrepTime) : undefined,
        sort_by: sortBy || undefined,
        sort_order: sortOrder,
        limit: 20,
        page: currentPage
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
      const { supabase } = await import('../../lib/supabase');
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
        dietary_tags: filters.dietaryTags.length > 0 ? filters.dietaryTags : undefined,
        max_prep_time: filters.maxPrepTime && filters.maxPrepTime !== '' ? parseInt(filters.maxPrepTime) : undefined,
        sort_by: sortBy || undefined,
        sort_order: sortOrder,
        limit: 20, // Increased default limit
        page: 1 // Always start from page 1 when searching
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
    onOpen();
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
          
          {/* Reviewer Search Help */}
          <Alert status="info" borderRadius="md" mb={4}>
            <AlertIcon />
            <Box>
              <Text fontWeight="semibold" mb={2}>Reviewer Search Patterns:</Text>
              <VStack align="start" spacing={1} fontSize="sm">
                <Text>• <Text as="span" fontWeight="bold">#1, #2, #10</Text> - Find specific recipe numbers</Text>
                <Text>• <Text as="span" fontWeight="bold">1, 2, 10</Text> - Same as above (without #)</Text>
                <Text>• <Text as="span" fontWeight="bold">r1, r2, r10</Text> - Alternative format</Text>
                <Text>• <Text as="span" fontWeight="bold">range:1-10</Text> - Get recipes 1 through 10</Text>
                <Text>• <Text as="span" fontWeight="bold">range:50-100</Text> - Get recipes 50 through 100</Text>
                <Text>• <Text as="span" fontWeight="bold">first:20</Text> - Get first 20 recipes</Text>
                <Text>• <Text as="span" fontWeight="bold">last:20</Text> - Get last 20 recipes</Text>
                <Text>• <Text as="span" fontWeight="bold">pasta, chicken, curry</Text> - Text search</Text>
              </VStack>
            </Box>
          </Alert>
        </Box>

        {/* Search and Filters */}
        <Card bg={cardBg} borderColor={borderColor}>
          <CardBody>
            <VStack spacing={4} align="stretch">
              {/* Search Bar */}
              <InputGroup>
                <InputLeftElement>
                  <FiSearch />
                </InputLeftElement>
                <Input
                  placeholder={t('nutrition.searchRecipes', 'en')}
                  value={searchQuery}
                  onChange={(e: any) => setSearchQuery(e.target.value)}
                  onKeyPress={(e: any) => e.key === 'Enter' && handleSearch()}
                  list="search-suggestions"
                />
                <datalist id="search-suggestions">
                  <option value="#1" />
                  <option value="#10" />
                  <option value="#50" />
                  <option value="#100" />
                  <option value="range:1-10" />
                  <option value="range:50-100" />
                  <option value="first:20" />
                  <option value="last:20" />
                  <option value="pasta" />
                  <option value="chicken" />
                  <option value="curry" />
                  <option value="pizza" />
                  <option value="salad" />
                </datalist>
              </InputGroup>

              {/* Filters */}
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

                <FormControl>
                  <FormLabel>{t('nutrition.dietaryTags', 'en')}</FormLabel>
                  <CheckboxGroup
                    value={filters.dietaryTags}
                    onChange={(values: any) => setFilters({...filters, dietaryTags: values as string[]})}
                  >
                    <Stack direction="row" wrap="wrap">
                      <Checkbox value="vegetarian">{t('vegetarian')}</Checkbox>
                      <Checkbox value="vegan">{t('vegan')}</Checkbox>
                      <Checkbox value="gluten-free">{t('glutenFree')}</Checkbox>
                      <Checkbox value="high-protein">High-protein</Checkbox>
                    </Stack>
                  </CheckboxGroup>
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
        <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }} gap={4} key={`recipes-${sortBy}-${sortOrder}-${currentPage}`}>
          {Array.isArray(recipes) ? recipes.map((recipe, index) => (
            <Card key={`${recipe.id}-${index}-${sortBy}-${sortOrder}`} bg={cardBg} borderColor={borderColor} position="relative">
              <CardHeader>
                <HStack justify="space-between">
                  <VStack align="start" spacing={1} flex="1">
                    <Heading size="sm">
                      {recipe.title.replace(/\s*\(#\d+\)\s*$/, '')}
                    </Heading>
                    <HStack spacing={2}>
                      <Badge colorScheme="blue" size="sm">{recipe.cuisine}</Badge>
                      <Badge colorScheme="purple" size="sm">{recipe.meal_type}</Badge>
                    </HStack>
                  </VStack>
                  {recipe.id && recipe.id.startsWith('recipe_') && (
                    <Badge 
                      colorScheme="gray" 
                      size="sm" 
                      fontSize="xs"
                      position="absolute"
                      top={2}
                      right={2}
                    >
                      #{parseInt(recipe.id.replace('recipe_', ''))}
                    </Badge>
                  )}
                  <Menu>
                    <MenuButton as={IconButton} icon={<FiMoreVertical />} size="sm" variant="ghost" />
                    <MenuList>
                      <MenuItem icon={<FiEye />} onClick={() => handleRecipeView(recipe)}>
                        {t('nutrition.viewRecipe', 'en')}
                      </MenuItem>
                      <MenuItem icon={<FiPlus />}>
                        {t('nutrition.addToMealPlan', 'en')}
                      </MenuItem>
                      <MenuItem icon={<FiHeart />}>
                        {t('nutrition.saveRecipe', 'en')}
                      </MenuItem>
                    </MenuList>
                  </Menu>
                </HStack>
              </CardHeader>
              <CardBody>
                <VStack spacing={3} align="stretch">
                  {/* Nutritional Info */}
                  <HStack justify="space-between" fontSize="sm">
                    <Text>{recipe.calculated_calories || 0} {t('nutrition.calories', 'en')}</Text>
                    <Text>{recipe.calculated_protein || 0}g {t('nutrition.protein', 'en')}</Text>
                  </HStack>
                  <HStack justify="space-between" fontSize="sm">
                    <Text>{recipe.calculated_carbs || 0}g {t('nutrition.carbs', 'en')}</Text>
                    <Text>{recipe.calculated_fats || 0}g {t('nutrition.fats', 'en')}</Text>
                  </HStack>

                  <Divider />

                  {/* Recipe Details */}
                  <HStack justify="space-between" fontSize="sm">
                    <HStack>
                      <FiClock />
                      <Text>{recipe.prep_time} min</Text>
                    </HStack>
                    <HStack>
                      <FiStar />
                      <Text>{recipe.rating}</Text>
                    </HStack>
                    <Badge colorScheme={getDifficultyColor(recipe.difficulty_level)} size="sm">
                      {recipe.difficulty_level}
                    </Badge>
                  </HStack>

                  {/* Dietary Tags */}
                  <HStack wrap="wrap" spacing={1}>
                    {recipe.dietary_tags.map((tag) => (
                      <Badge key={tag} size="sm" colorScheme="green" variant="subtle">
                        {tag}
                      </Badge>
                    ))}
                  </HStack>

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
        </Grid>

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
            <ModalHeader>{selectedRecipe?.title}</ModalHeader>
            <ModalCloseButton />
            <ModalBody>
              {selectedRecipe && (
                <VStack spacing={4} align="stretch">
                  {/* Recipe Info */}
                  <HStack justify="space-between">
                    <HStack spacing={4}>
                      <Text fontSize="sm">{selectedRecipe.calculated_calories || 0} {t('nutrition.calories', 'en')}</Text>
                      <Text fontSize="sm">{selectedRecipe.calculated_protein || 0}g {t('nutrition.protein', 'en')}</Text>
                      <Text fontSize="sm">{selectedRecipe.calculated_carbs || 0}g {t('nutrition.carbs', 'en')}</Text>
                      <Text fontSize="sm">{selectedRecipe.calculated_fats || 0}g {t('nutrition.fats', 'en')}</Text>
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
                    <Heading size="sm" mb={2}>{t('nutrition.ingredients', 'en')}</Heading>
                    <Text fontSize="sm">{(selectedRecipe.ingredients_list || selectedRecipe.ingredients || []).join(', ')}</Text>
                  </Box>

                  {/* Instructions */}
                  <Box>
                    <Heading size="sm" mb={2}>{t('nutrition.instructions', 'en')}</Heading>
                    <VStack spacing={2} align="stretch">
                      {(selectedRecipe.instructions_list || selectedRecipe.instructions || []).map((instruction, index) => (
                        <HStack key={index} align="start">
                          <Badge colorScheme="blue" size="sm">{index + 1}</Badge>
                          <Text fontSize="sm">{instruction}</Text>
                        </HStack>
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
              <Button colorScheme="blue">
                {t('nutrition.addToMealPlan', 'en')}
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </VStack>
    </Box>
  );
};

export default RecipeSearch;
