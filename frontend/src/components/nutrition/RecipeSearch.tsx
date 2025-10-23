import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Badge,
  Input,
  Select,
  useToast,
  SimpleGrid,
  Icon,
  Flex,
  Spinner,
  Alert,
  AlertIcon,
} from '@chakra-ui/react';
import { FiSearch, FiPlus, FiBookOpen, FiClock, FiUsers } from 'react-icons/fi';
import { t } from '../../utils/translations';

interface RecipeSearchProps {
  recipes: any[];
  onUpdate: () => void;
}

const RecipeSearch: React.FC<RecipeSearchProps> = ({
  recipes,
  onUpdate,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [cuisine, setCuisine] = useState('');
  const [mealType, setMealType] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [searching, setSearching] = useState(false);
  const [generating, setGenerating] = useState(false);
  const toast = useToast();

  const handleSearch = async () => {
    try {
      setSearching(true);
      
      const searchParams = new URLSearchParams();
      if (searchQuery) searchParams.append('query', searchQuery);
      if (cuisine) searchParams.append('cuisine', cuisine);
      if (mealType) searchParams.append('meal_type', mealType);
      if (difficulty) searchParams.append('difficulty_level', difficulty);
      
      const response = await fetch(`http://localhost:8000/nutrition/recipes/search?${searchParams}`);
      
      if (response.ok) {
        const results = await response.json();
        toast({
          title: `Found ${results.length} recipes`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        onUpdate();
      } else {
        throw new Error('Search failed');
      }
    } catch (error) {
      console.error('Error searching recipes:', error);
      toast({
        title: 'Search failed',
        description: 'Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setSearching(false);
    }
  };

  const handleGenerateRecipe = async () => {
    try {
      setGenerating(true);
      
      const response = await fetch('http://localhost:8000/nutrition/recipes/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: searchQuery }),
      });

      if (response.ok) {
        toast({
          title: 'Recipe generated successfully!',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        onUpdate();
      } else {
        throw new Error('Failed to generate recipe');
      }
    } catch (error) {
      console.error('Error generating recipe:', error);
      toast({
        title: 'Error generating recipe',
        description: 'Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setGenerating(false);
    }
  };

  return (
    <VStack spacing={6} align="stretch">
      <Box>
        <Heading size="lg" mb={2}>
          {t('recipes', 'en')}
        </Heading>
        <Text color="gray.600">
          Search existing recipes or generate new ones with AI
        </Text>
      </Box>

      {/* Search & Generate */}
      <Card>
        <CardHeader>
          <Heading size="md">Search & Generate Recipes</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={4}>
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4} w="full">
              <Box>
                <Text mb={2} fontWeight="semibold">Search Query</Text>
                <Input
                  placeholder="Search for recipes..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </Box>

              <Box>
                <Text mb={2} fontWeight="semibold">Cuisine</Text>
                <Select
                  placeholder="Any cuisine"
                  value={cuisine}
                  onChange={(e) => setCuisine(e.target.value)}
                >
                  <option value="italian">Italian</option>
                  <option value="mexican">Mexican</option>
                  <option value="asian">Asian</option>
                  <option value="mediterranean">Mediterranean</option>
                  <option value="indian">Indian</option>
                </Select>
              </Box>

              <Box>
                <Text mb={2} fontWeight="semibold">Meal Type</Text>
                <Select
                  placeholder="Any meal"
                  value={mealType}
                  onChange={(e) => setMealType(e.target.value)}
                >
                  <option value="breakfast">Breakfast</option>
                  <option value="lunch">Lunch</option>
                  <option value="dinner">Dinner</option>
                  <option value="snack">Snack</option>
                </Select>
              </Box>

              <Box>
                <Text mb={2} fontWeight="semibold">Difficulty</Text>
                <Select
                  placeholder="Any difficulty"
                  value={difficulty}
                  onChange={(e) => setDifficulty(e.target.value)}
                >
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </Select>
              </Box>
            </SimpleGrid>

            <HStack spacing={4}>
              <Button
                colorScheme="blue"
                onClick={handleSearch}
                isLoading={searching}
                loadingText="Searching..."
                leftIcon={<Icon as={FiSearch} />}
              >
                Search Recipes
              </Button>
              
              <Button
                colorScheme="green"
                variant="outline"
                onClick={handleGenerateRecipe}
                isLoading={generating}
                loadingText="Generating..."
                leftIcon={<Icon as={FiPlus} />}
              >
                Generate Recipe
              </Button>
            </HStack>
          </VStack>
        </CardBody>
      </Card>

      {/* Recipe Results */}
      <Box>
        <HStack justify="space-between" mb={4}>
          <Heading size="md">Recipe Results</Heading>
          <Text color="gray.600">{recipes.length} recipes found</Text>
        </HStack>

        {recipes.length === 0 ? (
          <Alert status="info" borderRadius="lg">
            <AlertIcon />
            <Box>
              <Text fontWeight="semibold">No recipes found</Text>
              <Text>Try searching or generating a new recipe!</Text>
            </Box>
          </Alert>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
            {recipes.map((recipe) => (
              <Card key={recipe.id} variant="outline">
                <CardHeader>
                  <HStack justify="space-between">
                    <Heading size="sm">{recipe.title}</Heading>
                    <Badge colorScheme="blue" variant="subtle">
                      {recipe.cuisine}
                    </Badge>
                  </HStack>
                </CardHeader>
                <CardBody>
                  <VStack spacing={3} align="stretch">
                    <Text fontSize="sm" color="gray.600" noOfLines={2}>
                      {recipe.summary}
                    </Text>

                    <HStack spacing={4}>
                      <HStack>
                        <Icon as={FiClock} color="gray.500" />
                        <Text fontSize="sm">{recipe.prep_time + recipe.cook_time} min</Text>
                      </HStack>
                      <HStack>
                        <Icon as={FiUsers} color="gray.500" />
                        <Text fontSize="sm">{recipe.servings} servings</Text>
                      </HStack>
                    </HStack>

                    <HStack>
                      <Badge colorScheme="green" variant="subtle">
                        {recipe.difficulty_level}
                      </Badge>
                      <Badge colorScheme="purple" variant="subtle">
                        {recipe.meal_type}
                      </Badge>
                    </HStack>

                    <Button size="sm" colorScheme="blue">
                      View Recipe
                    </Button>
                  </VStack>
                </CardBody>
              </Card>
            ))}
          </SimpleGrid>
        )}
      </Box>
    </VStack>
  );
};

export default RecipeSearch;
