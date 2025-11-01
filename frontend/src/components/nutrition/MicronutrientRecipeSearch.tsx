import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Heading,
  Text,
  Button,
  Grid,
  GridItem,
  Card,
  CardBody,
  CardHeader,
  Badge,
  FormControl,
  FormLabel,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Input,
  Select,
  useToast,
  Spinner,
  Center,
  SimpleGrid,
  Divider,
  useColorModeValue
} from '@chakra-ui/react';
import { Alert, AlertIcon } from '@chakra-ui/react';
import { FiSearch, FiFilter, FiStar } from 'react-icons/fi';

interface Recipe {
  id: string;
  title: string;
  cuisine: string;
  meal_type: string;
  servings: number;
  prep_time: number;
  cook_time: number;
  difficulty_level: string;
  dietary_tags: string[];
  per_serving_vitamin_d: number;
  per_serving_vitamin_b12: number;
  per_serving_iron: number;
  per_serving_calcium: number;
  per_serving_magnesium: number;
  per_serving_vitamin_c: number;
  per_serving_folate: number;
  per_serving_zinc: number;
  per_serving_potassium: number;
  per_serving_fiber: number;
}

interface MicronutrientRecipeSearchProps {
  onRecipeSelect?: (recipe: Recipe) => void;
}

const MicronutrientRecipeSearch: React.FC<MicronutrientRecipeSearchProps> = ({
  onRecipeSelect
}) => {
  const [filters, setFilters] = useState({
    min_vitamin_d: '',
    min_vitamin_b12: '',
    min_iron: '',
    min_calcium: '',
    min_magnesium: '',
    min_vitamin_c: '',
    min_folate: '',
    min_zinc: '',
    min_potassium: '',
    min_fiber: '',
    cuisine: '',
    meal_type: '',
    difficulty_level: ''
  });
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(0);
  const [quickSearch, setQuickSearch] = useState('');
  const [includePartial, setIncludePartial] = useState(true);
  const [relaxedMode, setRelaxedMode] = useState(false);
  const toast = useToast();

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  const micronutrientFilters = [
    { key: 'min_vitamin_d', name: 'Vitamin D', unit: 'mcg', description: 'Bone health and immune function' },
    { key: 'min_vitamin_b12', name: 'Vitamin B12', unit: 'mcg', description: 'Nerve function and red blood cells' },
    { key: 'min_iron', name: 'Iron', unit: 'mg', description: 'Oxygen transport in blood' },
    { key: 'min_calcium', name: 'Calcium', unit: 'mg', description: 'Bone and teeth health' },
    { key: 'min_magnesium', name: 'Magnesium', unit: 'mg', description: 'Muscle and nerve function' },
    { key: 'min_vitamin_c', name: 'Vitamin C', unit: 'mg', description: 'Immune system support' },
    { key: 'min_folate', name: 'Folate', unit: 'mcg', description: 'Cell division and DNA synthesis' },
    { key: 'min_zinc', name: 'Zinc', unit: 'mg', description: 'Immune function and healing' },
    { key: 'min_potassium', name: 'Potassium', unit: 'mg', description: 'Heart and muscle function' },
    { key: 'min_fiber', name: 'Fiber', unit: 'g', description: 'Digestive health and satiety' },
  ];

  const cuisines = [
    'Mediterranean', 'Asian', 'Indian', 'Mexican', 'Italian', 'American',
    'French', 'Thai', 'Chinese', 'Japanese', 'Middle Eastern', 'Other'
  ];

  const mealTypes = [
    'breakfast', 'lunch', 'dinner', 'snack', 'dessert', 'appetizer'
  ];

  const difficultyLevels = [
    'easy', 'medium', 'hard'
  ];

  const handleSearch = async () => {
    setLoading(true);
    try {
      // Filter out empty values
      const searchFilters = Object.fromEntries(
        Object.entries(filters).filter(([_, value]) => value !== '')
      );

      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        throw new Error('No valid session found');
      }

      const baseBody: any = { ...searchFilters, q: quickSearch || undefined, include_partial: includePartial };

      const fetchSearch = async (body: any) => fetch('http://localhost:8000/micronutrients/recipes/search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`
        },
        body: JSON.stringify(body)
      });

      // First attempt: strict search
      let response = await fetchSearch(baseBody);
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to search recipes');
      }
      let data = await response.json();

      // Detect “no data” case and relax filters
      const hasMicroFilters = Object.keys(searchFilters).some(k => k.startsWith('min_'));
      if ((data.total === 0 || !data.recipes?.length) && hasMicroFilters) {
        setRelaxedMode(true);
        // Retry without micronutrient mins, keep text/cuisine/type/difficulty
        const { cuisine, meal_type, difficulty_level } = filters as any;
        const relaxedBody = {
          q: quickSearch || undefined,
          cuisine: cuisine || undefined,
          meal_type: meal_type || undefined,
          difficulty_level: difficulty_level || undefined,
          include_partial: true
        };
        response = await fetchSearch(relaxedBody);
        if (response.ok) {
          data = await response.json();
          toast({
            title: 'Showing broader results',
            description: 'Very few recipes have full micronutrient data; filters were relaxed.',
            status: 'info',
            duration: 3500,
            isClosable: true,
          });
        }
      } else {
        setRelaxedMode(false);
      }

      setRecipes(data.recipes || []);
      setTotal(data.total || 0);
      if ((data.total || 0) > 0) {
        toast({
          title: 'Search Complete',
          description: `Found ${data.total} recipes`,
          status: 'success',
          duration: 2000,
          isClosable: true,
        });
      }
    } catch (error) {
      console.error('Error searching recipes:', error);
      
      // Set mock data for development/demo purposes
      const mockRecipes = [
        {
          id: '1',
          title: 'Spinach and Salmon Quinoa Bowl',
          cuisine: 'Mediterranean',
          meal_type: 'lunch',
          servings: 2,
          prep_time: 15,
          cook_time: 20,
          difficulty_level: 'easy',
          dietary_tags: ['gluten-free', 'high-protein'],
          per_serving_vitamin_d: 12.5,
          per_serving_vitamin_b12: 3.2,
          per_serving_iron: 4.8,
          per_serving_calcium: 180,
          per_serving_magnesium: 95,
          per_serving_vitamin_c: 45,
          per_serving_folate: 120,
          per_serving_zinc: 2.1,
          per_serving_potassium: 650,
          per_serving_fiber: 6.2
        },
        {
          id: '2',
          title: 'Fortified Oatmeal with Berries',
          cuisine: 'American',
          meal_type: 'breakfast',
          servings: 1,
          prep_time: 5,
          cook_time: 10,
          difficulty_level: 'easy',
          dietary_tags: ['vegetarian', 'high-fiber'],
          per_serving_vitamin_d: 8.0,
          per_serving_vitamin_b12: 1.8,
          per_serving_iron: 3.2,
          per_serving_calcium: 250,
          per_serving_magnesium: 85,
          per_serving_vitamin_c: 35,
          per_serving_folate: 80,
          per_serving_zinc: 1.5,
          per_serving_potassium: 420,
          per_serving_fiber: 8.5
        },
        {
          id: '3',
          title: 'Lentil and Vegetable Curry',
          cuisine: 'Indian',
          meal_type: 'dinner',
          servings: 4,
          prep_time: 20,
          cook_time: 30,
          difficulty_level: 'medium',
          dietary_tags: ['vegan', 'high-protein'],
          per_serving_vitamin_d: 2.5,
          per_serving_vitamin_b12: 0.8,
          per_serving_iron: 6.5,
          per_serving_calcium: 120,
          per_serving_magnesium: 75,
          per_serving_vitamin_c: 55,
          per_serving_folate: 150,
          per_serving_zinc: 2.8,
          per_serving_potassium: 580,
          per_serving_fiber: 12.3
        }
      ];
      
      setRecipes(mockRecipes);
      setTotal(mockRecipes.length);
      
      toast({
        title: 'Demo Mode',
        description: 'Showing sample recipes. Set up micronutrient search API for real results.',
        status: 'info',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClearFilters = () => {
    setFilters({
      min_vitamin_d: '',
      min_vitamin_b12: '',
      min_iron: '',
      min_calcium: '',
      min_magnesium: '',
      min_vitamin_c: '',
      min_folate: '',
      min_zinc: '',
      min_potassium: '',
      min_fiber: '',
      cuisine: '',
      meal_type: '',
      difficulty_level: ''
    });
    setRecipes([]);
    setTotal(0);
  };

  const getMicronutrientValue = (recipe: Recipe, micronutrient: string) => {
    const key = `per_serving_${micronutrient}` as keyof Recipe;
    return recipe[key] as number || 0;
  };

  const getMicronutrientColor = (value: number, threshold: number) => {
    if (value >= threshold * 1.5) return 'green';
    if (value >= threshold) return 'blue';
    if (value >= threshold * 0.5) return 'yellow';
    return 'red';
  };

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        <VStack align="start" spacing={2}>
          <Heading size="lg">Find Recipes by Micronutrient Content</Heading>
          <Text color="gray.600" fontSize="sm">
            Search for recipes based on specific vitamin and mineral content
          </Text>
        </VStack>
        
        {/* Quick Search */}
        <Card>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <Text fontWeight="semibold">Quick Search</Text>
              <HStack spacing={3}>
                <Input
                  placeholder="Search by recipe name, cuisine, or ingredients..."
                  value={quickSearch}
                  onChange={(e) => setQuickSearch(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                />
                <Button
                  leftIcon={<FiSearch />}
                  onClick={handleSearch}
                  isLoading={loading}
                  colorScheme="blue"
                >
                  Search
                </Button>
              </HStack>
            </VStack>
          </CardBody>
        </Card>
        
        {/* Search Filters */}
        <Card>
          <CardHeader>
            <HStack>
              <FiFilter />
              <Heading size="md">Search Filters</Heading>
            </HStack>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              {/* Partial data toggle */}
              <HStack>
                <FormControl display="flex" alignItems="center" w="auto">
                  <NumberInput display="none"><NumberInputField /></NumberInput>
                  <FormLabel mb="0" fontSize="sm">Include recipes with partial micronutrient data</FormLabel>
                </FormControl>
                <Button size="sm" variant={includePartial ? 'solid' : 'outline'} onClick={() => setIncludePartial(p => !p)}>
                  {includePartial ? 'On' : 'Off'}
                </Button>
              </HStack>
              {/* Micronutrient Filters */}
              <Box>
                <Text fontWeight="semibold" mb={3}>Micronutrient Content (per serving)</Text>
                <Grid templateColumns="repeat(2, 1fr)" gap={4}>
                  {micronutrientFilters.map((filter) => (
                    <GridItem key={filter.key}>
                      <FormControl>
                        <FormLabel fontSize="sm">{filter.name} ({filter.unit})</FormLabel>
                        <NumberInput
                          value={filters[filter.key as keyof typeof filters]}
                          onChange={(valueString, valueNumber) => {
                            if (!isNaN(valueNumber)) {
                              setFilters(prev => ({
                                ...prev,
                                [filter.key]: valueNumber
                              }));
                            }
                          }}
                          min={0}
                          precision={1}
                        >
                          <NumberInputField placeholder={`Min ${filter.unit}`} />
                          <NumberInputStepper>
                            <NumberIncrementStepper />
                            <NumberDecrementStepper />
                          </NumberInputStepper>
                        </NumberInput>
                        <Text fontSize="xs" color="gray.500">{filter.description}</Text>
                      </FormControl>
                    </GridItem>
                  ))}
                </Grid>
              </Box>

              <Divider />

              {/* Other Filters */}
              <Grid templateColumns="repeat(3, 1fr)" gap={4}>
                <GridItem>
                  <FormControl>
                    <FormLabel fontSize="sm">Cuisine</FormLabel>
                    <Select
                      value={filters.cuisine}
                      onChange={(e) => setFilters(prev => ({ ...prev, cuisine: e.target.value }))}
                      placeholder="Any cuisine"
                    >
                      {cuisines.map(cuisine => (
                        <option key={cuisine} value={cuisine}>{cuisine}</option>
                      ))}
                    </Select>
                  </FormControl>
                </GridItem>

                <GridItem>
                  <FormControl>
                    <FormLabel fontSize="sm">Meal Type</FormLabel>
                    <Select
                      value={filters.meal_type}
                      onChange={(e) => setFilters(prev => ({ ...prev, meal_type: e.target.value }))}
                      placeholder="Any meal"
                    >
                      {mealTypes.map(type => (
                        <option key={type} value={type}>{type}</option>
                      ))}
                    </Select>
                  </FormControl>
                </GridItem>

                <GridItem>
                  <FormControl>
                    <FormLabel fontSize="sm">Difficulty</FormLabel>
                    <Select
                      value={filters.difficulty_level}
                      onChange={(e) => setFilters(prev => ({ ...prev, difficulty_level: e.target.value }))}
                      placeholder="Any difficulty"
                    >
                      {difficultyLevels.map(level => (
                        <option key={level} value={level}>{level}</option>
                      ))}
                    </Select>
                  </FormControl>
                </GridItem>
              </Grid>

              {/* Preset Filters */}
              <Box>
                <Text fontWeight="semibold" mb={3}>Quick Presets</Text>
                <HStack spacing={2} wrap="wrap">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setFilters(prev => ({
                        ...prev,
                        min_iron: 5,
                        min_vitamin_c: 30,
                        min_folate: 100
                      }));
                    }}
                  >
                    Iron & Vitamin C
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setFilters(prev => ({
                        ...prev,
                        min_calcium: 200,
                        min_vitamin_d: 5,
                        min_magnesium: 50
                      }));
                    }}
                  >
                    Bone Health
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setFilters(prev => ({
                        ...prev,
                        min_fiber: 5,
                        min_potassium: 500,
                        min_vitamin_c: 25
                      }));
                    }}
                  >
                    Heart Health
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setFilters(prev => ({
                        ...prev,
                        min_vitamin_b12: 1,
                        min_folate: 150,
                        min_zinc: 2
                      }));
                    }}
                  >
                    Energy & Focus
                  </Button>
                </HStack>
              </Box>

              {/* Search Buttons */}
              <HStack spacing={3}>
                <Button
                  leftIcon={<FiSearch />}
                  onClick={handleSearch}
                  isLoading={loading}
                  loadingText="Searching..."
                  colorScheme="blue"
                >
                  Search Recipes
                </Button>
                <Button
                  variant="outline"
                  onClick={handleClearFilters}
                >
                  Clear Filters
                </Button>
              </HStack>
            </VStack>
          </CardBody>
        </Card>

        {relaxedMode && (
          <Alert status="info" variant="left-accent">
            <AlertIcon />
            Limited micronutrient data available. Showing broader matches and partial-data recipes.
          </Alert>
        )}

        {/* Results */}
        {loading && (
          <Center h="200px">
            <Spinner size="xl" />
          </Center>
        )}

        {!loading && recipes.length > 0 && (
          <Box>
            <HStack justify="space-between" mb={4}>
              <Heading size="md">Found {total} Recipes</Heading>
            </HStack>

            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
              {recipes.map((recipe) => (
                <Card key={recipe.id} bg={bgColor} borderColor={borderColor}>
                  <CardHeader>
                    <VStack align="start" spacing={2}>
                      <Heading size="sm">{recipe.title}</Heading>
                      <HStack spacing={2}>
                        <Badge colorScheme="blue">{recipe.cuisine}</Badge>
                        <Badge colorScheme="green">{recipe.meal_type}</Badge>
                        <Badge colorScheme="purple">{recipe.difficulty_level}</Badge>
                      </HStack>
                    </VStack>
                  </CardHeader>
                  <CardBody>
                    <VStack spacing={3} align="stretch">
                      <HStack justify="space-between">
                        <Text fontSize="sm" color="gray.600">
                          {recipe.servings} servings • {recipe.prep_time + recipe.cook_time} min
                        </Text>
                      </HStack>

                      {/* Micronutrient Highlights */}
                      <Box>
                        <Text fontSize="sm" fontWeight="semibold" mb={2}>
                          Micronutrient Content:
                        </Text>
                        <SimpleGrid columns={2} spacing={2}>
                          {micronutrientFilters.slice(0, 6).map((filter) => {
                            const value = getMicronutrientValue(recipe, filter.key.replace('min_', ''));
                            const threshold = parseFloat(filters[filter.key as keyof typeof filters]) || 0;
                            const color = threshold > 0 ? getMicronutrientColor(value, threshold) : 'gray';
                            
                            return (
                              <HStack key={filter.key} justify="space-between">
                                <Text fontSize="xs">{filter.name}:</Text>
                                <Badge colorScheme={color} fontSize="xs">
                                  {value.toFixed(1)} {filter.unit}
                                </Badge>
                              </HStack>
                            );
                          })}
                        </SimpleGrid>
                      </Box>

                      {onRecipeSelect && (
                        <Button
                          size="sm"
                          colorScheme="blue"
                          onClick={() => onRecipeSelect(recipe)}
                        >
                          Select Recipe
                        </Button>
                      )}
                    </VStack>
                  </CardBody>
                </Card>
              ))}
            </SimpleGrid>
          </Box>
        )}

        {!loading && recipes.length === 0 && total === 0 && (
          <Center h="200px">
            <VStack spacing={3}>
              <FiSearch size="48" color="gray" />
              <Text color="gray.600">No recipes found. Try adjusting your filters.</Text>
            </VStack>
          </Center>
        )}
      </VStack>
    </Box>
  );
};

export default MicronutrientRecipeSearch;


