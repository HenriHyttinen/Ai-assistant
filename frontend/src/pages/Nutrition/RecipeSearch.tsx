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
import { useTranslation } from 'react-i18next';
import { 
  FiSearch, 
  FiFilter, 
  FiClock, 
  FiTarget,
  FiChefHat,
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
  mealType: string;
  calories: number;
  protein: number;
  carbs: number;
  fats: number;
  prepTime: number;
  cookTime: number;
  difficulty: 'easy' | 'medium' | 'hard';
  dietaryTags: string[];
  ingredients: string[];
  instructions: string[];
  rating: number;
  image?: string;
}

interface RecipeSearchProps {
  user?: any;
}

const RecipeSearch: React.FC<RecipeSearchProps> = ({ user }) => {
  const { t } = useTranslation();
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
  const [selectedRecipe, setSelectedRecipe] = useState<Recipe | null>(null);
  const { isOpen, onOpen, onClose } = useDisclosure();

  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  useEffect(() => {
    loadRecipes();
  }, []);

  const loadRecipes = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock data
      setRecipes([
        {
          id: 'r1',
          title: 'Mediterranean Omelet',
          cuisine: 'Mediterranean',
          mealType: 'breakfast',
          calories: 400,
          protein: 28,
          carbs: 15,
          fats: 25,
          prepTime: 10,
          cookTime: 15,
          difficulty: 'easy',
          dietaryTags: ['vegetarian', 'high-protein'],
          ingredients: ['eggs', 'tomatoes', 'spinach', 'olive oil', 'cheese'],
          instructions: [
            'Heat olive oil in a non-stick pan over medium heat.',
            'Beat eggs in a bowl and season with salt and pepper.',
            'Add tomatoes and spinach to the pan, cook for 2 minutes.',
            'Pour beaten eggs over vegetables and cook until set.',
            'Sprinkle cheese on top and fold omelet in half.'
          ],
          rating: 4.5
        },
        {
          id: 'r2',
          title: 'Quinoa Buddha Bowl',
          cuisine: 'International',
          mealType: 'lunch',
          calories: 420,
          protein: 18,
          carbs: 50,
          fats: 15,
          prepTime: 15,
          cookTime: 20,
          difficulty: 'medium',
          dietaryTags: ['vegetarian', 'vegan', 'gluten-free'],
          ingredients: ['quinoa', 'broccoli', 'avocado', 'olive oil'],
          instructions: [
            'Cook quinoa according to package instructions.',
            'Steam broccoli until tender.',
            'Slice avocado and prepare vegetables.',
            'Arrange all ingredients in a bowl.',
            'Drizzle with olive oil and season to taste.'
          ],
          rating: 4.8
        },
        {
          id: 'r3',
          title: 'Baked Salmon with Vegetables',
          cuisine: 'International',
          mealType: 'dinner',
          calories: 550,
          protein: 40,
          carbs: 25,
          fats: 30,
          prepTime: 15,
          cookTime: 25,
          difficulty: 'medium',
          dietaryTags: ['gluten-free', 'high-protein', 'omega-3'],
          ingredients: ['salmon fillet', 'broccoli', 'olive oil'],
          instructions: [
            'Preheat oven to 400°F (200°C).',
            'Season salmon with salt, pepper, and olive oil.',
            'Toss broccoli with olive oil and seasonings.',
            'Place salmon and vegetables on a baking sheet.',
            'Bake for 20-25 minutes until salmon is flaky.'
          ],
          rating: 4.7
        },
        {
          id: 'r4',
          title: 'Vegetarian Stir-Fry',
          cuisine: 'Asian',
          mealType: 'dinner',
          calories: 320,
          protein: 15,
          carbs: 40,
          fats: 12,
          prepTime: 20,
          cookTime: 15,
          difficulty: 'easy',
          dietaryTags: ['vegetarian', 'vegan', 'quick'],
          ingredients: ['tofu', 'bell peppers', 'broccoli', 'soy sauce'],
          instructions: [
            'Cut tofu into cubes and vegetables into bite-sized pieces.',
            'Heat oil in a large wok or pan.',
            'Stir-fry tofu and vegetables for 10-12 minutes.',
            'Add soy sauce and seasonings.',
            'Serve over rice or noodles.'
          ],
          rating: 4.3
        }
      ]);
    } catch (err) {
      setError('Failed to load recipes');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Simulate API call with search query and filters
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Filter recipes based on search query and filters
      let filteredRecipes = recipes;
      
      if (searchQuery) {
        filteredRecipes = filteredRecipes.filter(recipe =>
          recipe.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
          recipe.ingredients.some(ingredient =>
            ingredient.toLowerCase().includes(searchQuery.toLowerCase())
          )
        );
      }
      
      if (filters.cuisine) {
        filteredRecipes = filteredRecipes.filter(recipe => recipe.cuisine === filters.cuisine);
      }
      
      if (filters.mealType) {
        filteredRecipes = filteredRecipes.filter(recipe => recipe.mealType === filters.mealType);
      }
      
      if (filters.difficulty) {
        filteredRecipes = filteredRecipes.filter(recipe => recipe.difficulty === filters.difficulty);
      }
      
      if (filters.maxCalories) {
        filteredRecipes = filteredRecipes.filter(recipe => recipe.calories <= parseInt(filters.maxCalories));
      }
      
      if (filters.dietaryTags.length > 0) {
        filteredRecipes = filteredRecipes.filter(recipe =>
          filters.dietaryTags.some(tag => recipe.dietaryTags.includes(tag))
        );
      }
      
      if (filters.maxPrepTime) {
        filteredRecipes = filteredRecipes.filter(recipe => 
          recipe.prepTime <= parseInt(filters.maxPrepTime)
        );
      }
      
      setRecipes(filteredRecipes);
    } catch (err) {
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
          <Text>{t('nutrition.loading')}</Text>
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
            {t('nutrition.recipeSearch.title')}
          </Heading>
          <Text color="gray.600">
            {t('nutrition.recipeSearch.subtitle')}
          </Text>
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
                  placeholder={t('nutrition.searchRecipes')}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                />
              </InputGroup>

              {/* Filters */}
              <Grid templateColumns={{ base: '1fr', md: 'repeat(3, 1fr)' }} gap={4}>
                <FormControl>
                  <FormLabel>{t('nutrition.cuisine')}</FormLabel>
                  <Select
                    value={filters.cuisine}
                    onChange={(e) => setFilters({...filters, cuisine: e.target.value})}
                  >
                    <option value="">{t('nutrition.allCuisines')}</option>
                    <option value="Mediterranean">Mediterranean</option>
                    <option value="Asian">Asian</option>
                    <option value="International">International</option>
                    <option value="Italian">Italian</option>
                    <option value="Mexican">Mexican</option>
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel>{t('nutrition.mealType')}</FormLabel>
                  <Select
                    value={filters.mealType}
                    onChange={(e) => setFilters({...filters, mealType: e.target.value})}
                  >
                    <option value="">{t('nutrition.allMealTypes')}</option>
                    <option value="breakfast">{t('nutrition.breakfast')}</option>
                    <option value="lunch">{t('nutrition.lunch')}</option>
                    <option value="dinner">{t('nutrition.dinner')}</option>
                    <option value="snack">{t('nutrition.snack')}</option>
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel>{t('nutrition.difficulty')}</FormLabel>
                  <Select
                    value={filters.difficulty}
                    onChange={(e) => setFilters({...filters, difficulty: e.target.value})}
                  >
                    <option value="">{t('nutrition.allDifficulties')}</option>
                    <option value="easy">{t('nutrition.easy')}</option>
                    <option value="medium">{t('nutrition.medium')}</option>
                    <option value="hard">{t('nutrition.hard')}</option>
                  </Select>
                </FormControl>

                <FormControl>
                  <FormLabel>{t('nutrition.maxCalories')}</FormLabel>
                  <Input
                    type="number"
                    placeholder="e.g. 500"
                    value={filters.maxCalories}
                    onChange={(e) => setFilters({...filters, maxCalories: e.target.value})}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>{t('nutrition.maxPrepTime')}</FormLabel>
                  <Input
                    type="number"
                    placeholder="e.g. 30"
                    value={filters.maxPrepTime}
                    onChange={(e) => setFilters({...filters, maxPrepTime: e.target.value})}
                  />
                </FormControl>

                <FormControl>
                  <FormLabel>{t('nutrition.dietaryTags')}</FormLabel>
                  <CheckboxGroup
                    value={filters.dietaryTags}
                    onChange={(values) => setFilters({...filters, dietaryTags: values as string[]})}
                  >
                    <Stack direction="row" wrap="wrap">
                      <Checkbox value="vegetarian">Vegetarian</Checkbox>
                      <Checkbox value="vegan">Vegan</Checkbox>
                      <Checkbox value="gluten-free">Gluten-free</Checkbox>
                      <Checkbox value="high-protein">High-protein</Checkbox>
                    </Stack>
                  </CheckboxGroup>
                </FormControl>
              </Grid>

              <Button colorScheme="blue" onClick={handleSearch} isLoading={loading}>
                <FiSearch />
                {t('nutrition.search')}
              </Button>
            </VStack>
          </CardBody>
        </Card>

        {error && (
          <Alert status="error">
            <AlertIcon />
            {error}
          </Alert>
        )}

        {/* Recipe Results */}
        <Grid templateColumns={{ base: '1fr', md: 'repeat(2, 1fr)', lg: 'repeat(3, 1fr)' }} gap={4}>
          {recipes.map((recipe) => (
            <Card key={recipe.id} bg={cardBg} borderColor={borderColor}>
              <CardHeader>
                <HStack justify="space-between">
                  <VStack align="start" spacing={1}>
                    <Heading size="sm">{recipe.title}</Heading>
                    <HStack spacing={2}>
                      <Badge colorScheme="blue" size="sm">{recipe.cuisine}</Badge>
                      <Badge colorScheme="purple" size="sm">{recipe.mealType}</Badge>
                    </HStack>
                  </VStack>
                  <Menu>
                    <MenuButton as={IconButton} icon={<FiMoreVertical />} size="sm" variant="ghost" />
                    <MenuList>
                      <MenuItem icon={<FiEye />} onClick={() => handleRecipeView(recipe)}>
                        {t('nutrition.viewRecipe')}
                      </MenuItem>
                      <MenuItem icon={<FiPlus />}>
                        {t('nutrition.addToMealPlan')}
                      </MenuItem>
                      <MenuItem icon={<FiHeart />}>
                        {t('nutrition.saveRecipe')}
                      </MenuItem>
                    </MenuList>
                  </Menu>
                </HStack>
              </CardHeader>
              <CardBody>
                <VStack spacing={3} align="stretch">
                  {/* Nutritional Info */}
                  <HStack justify="space-between" fontSize="sm">
                    <Text>{recipe.calories} {t('nutrition.calories')}</Text>
                    <Text>{recipe.protein}g {t('nutrition.protein')}</Text>
                  </HStack>
                  <HStack justify="space-between" fontSize="sm">
                    <Text>{recipe.carbs}g {t('nutrition.carbs')}</Text>
                    <Text>{recipe.fats}g {t('nutrition.fats')}</Text>
                  </HStack>

                  <Divider />

                  {/* Recipe Details */}
                  <HStack justify="space-between" fontSize="sm">
                    <HStack>
                      <FiClock />
                      <Text>{recipe.prepTime + recipe.cookTime} min</Text>
                    </HStack>
                    <HStack>
                      <FiStar />
                      <Text>{recipe.rating}</Text>
                    </HStack>
                    <Badge colorScheme={getDifficultyColor(recipe.difficulty)} size="sm">
                      {recipe.difficulty}
                    </Badge>
                  </HStack>

                  {/* Dietary Tags */}
                  <HStack wrap="wrap" spacing={1}>
                    {recipe.dietaryTags.map((tag) => (
                      <Badge key={tag} size="sm" colorScheme="green" variant="subtle">
                        {tag}
                      </Badge>
                    ))}
                  </HStack>

                  {/* Actions */}
                  <HStack spacing={2}>
                    <Button size="sm" colorScheme="blue" flex={1} onClick={() => handleRecipeView(recipe)}>
                      {t('nutrition.viewRecipe')}
                    </Button>
                    <Button size="sm" variant="outline" flex={1}>
                      {t('nutrition.addToMealPlan')}
                    </Button>
                  </HStack>
                </VStack>
              </CardBody>
            </Card>
          ))}
        </Grid>

        {recipes.length === 0 && !loading && (
          <Center h="200px">
            <VStack spacing={4}>
              <FiChefHat size={48} color="gray" />
              <Text color="gray.600">{t('nutrition.noRecipesFound')}</Text>
              <Button colorScheme="blue" onClick={loadRecipes}>
                {t('nutrition.loadAllRecipes')}
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
                      <Text fontSize="sm">{selectedRecipe.calories} {t('nutrition.calories')}</Text>
                      <Text fontSize="sm">{selectedRecipe.protein}g {t('nutrition.protein')}</Text>
                      <Text fontSize="sm">{selectedRecipe.carbs}g {t('nutrition.carbs')}</Text>
                      <Text fontSize="sm">{selectedRecipe.fats}g {t('nutrition.fats')}</Text>
                    </HStack>
                    <HStack spacing={2}>
                      <FiClock />
                      <Text fontSize="sm">{selectedRecipe.prepTime + selectedRecipe.cookTime} min</Text>
                      <FiStar />
                      <Text fontSize="sm">{selectedRecipe.rating}</Text>
                    </HStack>
                  </HStack>

                  {/* Dietary Tags */}
                  <HStack wrap="wrap" spacing={1}>
                    {selectedRecipe.dietaryTags.map((tag) => (
                      <Badge key={tag} size="sm" colorScheme="green" variant="subtle">
                        {tag}
                      </Badge>
                    ))}
                  </HStack>

                  <Divider />

                  {/* Ingredients */}
                  <Box>
                    <Heading size="sm" mb={2}>{t('nutrition.ingredients')}</Heading>
                    <Text fontSize="sm">{selectedRecipe.ingredients.join(', ')}</Text>
                  </Box>

                  {/* Instructions */}
                  <Box>
                    <Heading size="sm" mb={2}>{t('nutrition.instructions')}</Heading>
                    <VStack spacing={2} align="stretch">
                      {selectedRecipe.instructions.map((instruction, index) => (
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
                {t('common.close')}
              </Button>
              <Button colorScheme="blue">
                {t('nutrition.addToMealPlan')}
              </Button>
            </ModalFooter>
          </ModalContent>
        </Modal>
      </VStack>
    </Box>
  );
};

export default RecipeSearch;
