import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Input,
  Button,
  Select,
  Card,
  CardBody,
  CardHeader,
  Badge,
  Image,
  useColorModeValue,
  useBreakpointValue,
  Icon,
  Collapse,
  SimpleGrid,
  InputGroup,
  InputLeftElement,
  Spinner,
  Center,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  useToast,
} from '@chakra-ui/react';
import { FiSearch, FiFilter, FiChevronDown, FiChevronUp, FiClock, FiUsers, FiStar, FiWifi, FiWifiOff } from 'react-icons/fi';
import { useOffline } from '../../hooks/useOffline';
import offlineApiService from '../../services/offlineApiService';

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
  image_url?: string;
  rating?: number;
  calories_per_serving?: number;
  last_updated?: string;
  fromCache?: boolean;
  offline?: boolean;
}

const OfflineRecipeSearch: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCuisine, setSelectedCuisine] = useState('');
  const [selectedMealType, setSelectedMealType] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('');
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [lastSync, setLastSync] = useState<Date | null>(null);
  
  const { isOffline, isSlowConnection } = useOffline();
  const isMobile = useBreakpointValue({ base: true, md: false });
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  const toast = useToast();

  const cuisines = [
    'Mediterranean', 'Asian', 'Indian', 'Mexican', 'Italian', 'American',
    'French', 'Thai', 'Chinese', 'Japanese', 'Middle Eastern'
  ];

  const mealTypes = [
    'breakfast', 'lunch', 'dinner', 'snack', 'dessert', 'appetizer'
  ];

  const difficultyLevels = ['easy', 'medium', 'hard'];

  // Load initial data
  useEffect(() => {
    loadRecipes();
  }, []);

  const loadRecipes = async () => {
    setLoading(true);
    try {
      const response = await offlineApiService.getRecipes({
        cuisine: selectedCuisine || undefined,
        meal_type: selectedMealType || undefined,
        difficulty: selectedDifficulty || undefined,
      });

      setRecipes(response.data);
      setLastSync(new Date());
      
      if (response.offline) {
        toast({
          title: 'Offline Mode',
          description: 'Showing cached recipes. Some features may be limited.',
          status: 'warning',
          duration: 3000,
          isClosable: true,
        });
      }
    } catch (error) {
      console.error('Error loading recipes:', error);
      toast({
        title: 'Error',
        description: 'Failed to load recipes',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    setLoading(true);
    try {
      const response = await offlineApiService.getRecipes({
        search: searchTerm,
        cuisine: selectedCuisine || undefined,
        meal_type: selectedMealType || undefined,
        difficulty: selectedDifficulty || undefined,
      });

      setRecipes(response.data);
      setLastSync(new Date());
    } catch (error) {
      console.error('Error searching recipes:', error);
      toast({
        title: 'Search Error',
        description: 'Failed to search recipes',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    if (isOffline) {
      toast({
        title: 'Cannot Sync',
        description: 'You need to be online to sync data',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    setLoading(true);
    try {
      await offlineApiService.syncOfflineData();
      await loadRecipes();
      
      toast({
        title: 'Sync Complete',
        description: 'Your data has been synced successfully',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Error syncing:', error);
      toast({
        title: 'Sync Failed',
        description: 'Failed to sync data',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return 'green';
      case 'medium': return 'yellow';
      case 'hard': return 'red';
      default: return 'gray';
    }
  };

  const getMealTypeColor = (mealType: string) => {
    switch (mealType) {
      case 'breakfast': return 'orange';
      case 'lunch': return 'blue';
      case 'dinner': return 'purple';
      case 'snack': return 'teal';
      case 'dessert': return 'pink';
      default: return 'gray';
    }
  };

  return (
    <VStack spacing={4} align="stretch" p={4}>
      {/* Header */}
      <HStack justify="space-between" align="center">
        <HStack>
          <Text fontSize="xl" fontWeight="bold">
            Recipe Search
          </Text>
          {isOffline && (
            <Badge colorScheme="red" variant="subtle">
              <Icon as={FiWifiOff} mr={1} />
              Offline
            </Badge>
          )}
          {isSlowConnection && (
            <Badge colorScheme="yellow" variant="subtle">
              <Icon as={FiWifi} mr={1} />
              Slow
            </Badge>
          )}
        </HStack>
        <HStack spacing={2}>
          <Button
            size="sm"
            variant="outline"
            leftIcon={<FiFilter />}
            onClick={() => setShowFilters(!showFilters)}
          >
            Filters
          </Button>
          <Button
            size="sm"
            colorScheme="blue"
            leftIcon={<Icon as={FiWifi} />}
            onClick={handleSync}
            isLoading={loading}
            isDisabled={isOffline}
          >
            Sync
          </Button>
        </HStack>
      </HStack>

      {/* Offline Alert */}
      {isOffline && (
        <Alert status="warning" borderRadius="md">
          <AlertIcon />
          <Box>
            <AlertTitle>Offline Mode</AlertTitle>
            <AlertDescription>
              You're viewing cached recipes. Some features may be limited.
            </AlertDescription>
          </Box>
        </Alert>
      )}

      {/* Last Sync Info */}
      {lastSync && (
        <Text fontSize="sm" color={textColor} textAlign="center">
          Last updated: {lastSync.toLocaleString()}
          {isOffline && ' (Offline)'}
        </Text>
      )}

      {/* Search Bar */}
      <InputGroup>
        <InputLeftElement>
          <Icon as={FiSearch} color="gray.400" />
        </InputLeftElement>
        <Input
          placeholder="Search recipes..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
      </InputGroup>

      {/* Filters */}
      <Collapse in={showFilters}>
        <Card bg={bgColor} borderColor={borderColor}>
          <CardBody>
            <VStack spacing={3}>
              <Select
                placeholder="Select cuisine"
                value={selectedCuisine}
                onChange={(e) => setSelectedCuisine(e.target.value)}
              >
                {cuisines.map(cuisine => (
                  <option key={cuisine} value={cuisine}>{cuisine}</option>
                ))}
              </Select>
              
              <Select
                placeholder="Select meal type"
                value={selectedMealType}
                onChange={(e) => setSelectedMealType(e.target.value)}
              >
                {mealTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </Select>
              
              <Select
                placeholder="Select difficulty"
                value={selectedDifficulty}
                onChange={(e) => setSelectedDifficulty(e.target.value)}
              >
                {difficultyLevels.map(level => (
                  <option key={level} value={level}>{level}</option>
                ))}
              </Select>
            </VStack>
          </CardBody>
        </Card>
      </Collapse>

      {/* Search Button */}
      <Button
        colorScheme="blue"
        onClick={handleSearch}
        isLoading={loading}
        loadingText="Searching..."
        leftIcon={<FiSearch />}
      >
        Search Recipes
      </Button>

      {/* Results */}
      {loading && (
        <Center h="200px">
          <Spinner size="xl" />
        </Center>
      )}

      {!loading && recipes.length > 0 && (
        <VStack spacing={3} align="stretch">
          <Text fontSize="sm" color={textColor}>
            Found {recipes.length} recipes
            {isOffline && ' (from cache)'}
          </Text>
          
          {recipes.map((recipe) => (
            <Card key={recipe.id} bg={bgColor} borderColor={borderColor}>
              <CardBody p={4}>
                <VStack spacing={3} align="stretch">
                  {/* Recipe Header */}
                  <HStack justify="space-between" align="start">
                    <VStack align="start" spacing={1} flex={1}>
                      <HStack>
                        <Text fontWeight="semibold" fontSize="md" noOfLines={2}>
                          {recipe.title}
                        </Text>
                        {recipe.fromCache && (
                          <Badge colorScheme="blue" size="sm" variant="subtle">
                            Cached
                          </Badge>
                        )}
                      </HStack>
                      <HStack spacing={2}>
                        <Badge colorScheme={getMealTypeColor(recipe.meal_type)} size="sm">
                          {recipe.meal_type}
                        </Badge>
                        <Badge colorScheme={getDifficultyColor(recipe.difficulty_level)} size="sm">
                          {recipe.difficulty_level}
                        </Badge>
                      </HStack>
                    </VStack>
                    {recipe.image_url && (
                      <Image
                        src={recipe.image_url}
                        alt={recipe.title}
                        boxSize="60px"
                        objectFit="cover"
                        borderRadius="md"
                      />
                    )}
                  </HStack>

                  {/* Recipe Info */}
                  <HStack spacing={4} fontSize="sm" color={textColor}>
                    <HStack>
                      <Icon as={FiClock} />
                      <Text>{recipe.prep_time + recipe.cook_time} min</Text>
                    </HStack>
                    <HStack>
                      <Icon as={FiUsers} />
                      <Text>{recipe.servings} servings</Text>
                    </HStack>
                    {recipe.rating && (
                      <HStack>
                        <Icon as={FiStar} color="yellow.400" />
                        <Text>{recipe.rating}</Text>
                      </HStack>
                    )}
                  </HStack>

                  {/* Dietary Tags */}
                  {recipe.dietary_tags.length > 0 && (
                    <HStack spacing={1} flexWrap="wrap">
                      {recipe.dietary_tags.slice(0, 3).map((tag) => (
                        <Badge key={tag} size="sm" variant="subtle" colorScheme="blue">
                          {tag}
                        </Badge>
                      ))}
                      {recipe.dietary_tags.length > 3 && (
                        <Text fontSize="xs" color={textColor}>
                          +{recipe.dietary_tags.length - 3} more
                        </Text>
                      )}
                    </HStack>
                  )}

                  {/* Calories */}
                  {recipe.calories_per_serving && (
                    <HStack justify="space-between">
                      <Text fontSize="sm" color={textColor}>
                        Calories per serving:
                      </Text>
                      <Text fontWeight="semibold" color="blue.500">
                        {recipe.calories_per_serving} cal
                      </Text>
                    </HStack>
                  )}

                  {/* Action Buttons */}
                  <HStack spacing={2} pt={2}>
                    <Button size="sm" colorScheme="blue" flex={1}>
                      View Recipe
                    </Button>
                    <Button size="sm" variant="outline" flex={1}>
                      Add to Meal Plan
                    </Button>
                  </HStack>
                </VStack>
              </CardBody>
            </Card>
          ))}
        </VStack>
      )}

      {!loading && recipes.length === 0 && searchTerm && (
        <Center h="200px">
          <VStack spacing={3}>
            <Icon as={FiSearch} boxSize={8} color="gray.400" />
            <Text color={textColor}>No recipes found</Text>
            <Text fontSize="sm" color={textColor}>
              {isOffline 
                ? 'Try searching with different terms or check your cache'
                : 'Try adjusting your search terms or filters'
              }
            </Text>
          </VStack>
        </Center>
      )}
    </VStack>
  );
};

export default OfflineRecipeSearch;


