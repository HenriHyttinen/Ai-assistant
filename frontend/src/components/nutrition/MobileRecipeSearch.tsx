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
  useDisclosure,
  SimpleGrid,
  InputGroup,
  InputLeftElement,
  Spinner,
  Center,
  Divider,
  Flex,
  IconButton,
} from '@chakra-ui/react';
import { FiSearch, FiFilter, FiChevronDown, FiChevronUp, FiClock, FiUsers, FiStar } from 'react-icons/fi';

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
}

const MobileRecipeSearch: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCuisine, setSelectedCuisine] = useState('');
  const [selectedMealType, setSelectedMealType] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('');
  const [recipes, setRecipes] = useState<Recipe[]>([]);
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  
  const isMobile = useBreakpointValue({ base: true, md: false });
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  const cuisines = [
    'Mediterranean', 'Asian', 'Indian', 'Mexican', 'Italian', 'American',
    'French', 'Thai', 'Chinese', 'Japanese', 'Middle Eastern'
  ];

  const mealTypes = [
    'breakfast', 'lunch', 'dinner', 'snack', 'dessert', 'appetizer'
  ];

  const difficultyLevels = ['easy', 'medium', 'hard'];

  const handleSearch = async () => {
    setLoading(true);
    // Simulate API call
    setTimeout(() => {
      setRecipes([
        {
          id: '1',
          title: 'Mediterranean Quinoa Bowl',
          cuisine: 'Mediterranean',
          meal_type: 'lunch',
          servings: 2,
          prep_time: 15,
          cook_time: 20,
          difficulty_level: 'easy',
          dietary_tags: ['vegetarian', 'gluten-free'],
          rating: 4.5,
          calories_per_serving: 350,
        },
        {
          id: '2',
          title: 'Asian Stir-Fry',
          cuisine: 'Asian',
          meal_type: 'dinner',
          servings: 4,
          prep_time: 10,
          cook_time: 15,
          difficulty_level: 'easy',
          dietary_tags: ['low-carb', 'high-protein'],
          rating: 4.2,
          calories_per_serving: 280,
        },
        {
          id: '3',
          title: 'Italian Pasta Primavera',
          cuisine: 'Italian',
          meal_type: 'dinner',
          servings: 3,
          prep_time: 20,
          cook_time: 25,
          difficulty_level: 'medium',
          dietary_tags: ['vegetarian'],
          rating: 4.7,
          calories_per_serving: 420,
        },
      ]);
      setLoading(false);
    }, 1000);
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
        <Text fontSize="xl" fontWeight="bold">
          Recipe Search
        </Text>
        <Button
          size="sm"
          variant="outline"
          leftIcon={<FiFilter />}
          onClick={() => setShowFilters(!showFilters)}
        >
          Filters
        </Button>
      </HStack>

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
          </Text>
          
          {recipes.map((recipe) => (
            <Card key={recipe.id} bg={bgColor} borderColor={borderColor}>
              <CardBody p={4}>
                <VStack spacing={3} align="stretch">
                  {/* Recipe Header */}
                  <HStack justify="space-between" align="start">
                    <VStack align="start" spacing={1} flex={1}>
                      <Text fontWeight="semibold" fontSize="md" noOfLines={2}>
                        {recipe.title}
                      </Text>
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
              Try adjusting your search terms or filters
            </Text>
          </VStack>
        </Center>
      )}
    </VStack>
  );
};

export default MobileRecipeSearch;


