import React, { useState, useEffect } from 'react';
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
  Checkbox,
  useToast,
  SimpleGrid,
  Icon,
  Flex,
  Spinner,
  Alert,
  AlertIcon,
  Divider,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  IconButton,
  Input,
  Select,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Progress,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Tooltip,
  Collapse,
  useColorModeValue
} from '@chakra-ui/react';
import { 
  FiShoppingCart, 
  FiPlus, 
  FiTrash2, 
  FiCheck, 
  FiEye, 
  FiEdit, 
  FiSave, 
  FiX,
  FiChevronDown,
  FiChevronUp,
  FiFilter,
  FiDownload,
  FiShare,
  FiZap,
  FiTarget,
  FiCalendar,
  FiUsers,
  FiPackage
} from 'react-icons/fi';

interface MealPlan {
  id: string;
  plan_type: string;
  start_date: string;
  end_date: string;
  meals: any[];
}

interface ShoppingListSummary {
  shopping_list_id: string;
  list_name: string;
  meal_plan_id: string;
  total_items: number;
  purchased_items: number;
  completion_percentage: number;
  categories: Record<string, any[]>;
  created_at: string;
  updated_at: string;
}

interface EnhancedShoppingListGeneratorProps {
  mealPlans: MealPlan[];
  onUpdate: () => void;
}

const EnhancedShoppingListGenerator: React.FC<EnhancedShoppingListGeneratorProps> = ({
  mealPlans,
  onUpdate
}) => {
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [selectedMealPlan, setSelectedMealPlan] = useState<MealPlan | null>(null);
  const [selectedMealTypes, setSelectedMealTypes] = useState<string[]>([]);
  const [shoppingListSummary, setShoppingListSummary] = useState<ShoppingListSummary | null>(null);
  const [customListName, setCustomListName] = useState('');
  const [showAdvancedOptions, setShowAdvancedOptions] = useState(false);
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'category' | 'name' | 'quantity'>('category');
  
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();
  
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  const mealTypes = [
    { value: 'breakfast', label: 'Breakfast', icon: FiCalendar },
    { value: 'lunch', label: 'Lunch', icon: FiTarget },
    { value: 'dinner', label: 'Dinner', icon: FiUsers },
    { value: 'snacks', label: 'Snacks', icon: FiPackage }
  ];

  const categories = [
    'protein', 'dairy', 'vegetables', 'fruits', 'grains', 
    'nuts_seeds', 'oils_fats', 'herbs_spices', 'condiments', 'other'
  ];

  const generateShoppingList = async (type: 'full' | 'filtered' | 'custom') => {
    if (!selectedMealPlan) return;

    try {
      setGenerating(true);
      
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session?.access_token) {
        toast({
          title: 'Authentication required',
          description: 'Please log in to generate shopping lists',
          status: 'error',
          duration: 3000,
          isClosable: true,
        });
        return;
      }

      let endpoint = '';
      let body: any = {};

      switch (type) {
        case 'full':
          endpoint = `/nutrition/meal-plans/${selectedMealPlan.id}/generate-shopping-list`;
          if (customListName) {
            body = { list_name: customListName };
          }
          break;
        case 'filtered':
          endpoint = `/nutrition/meal-plans/${selectedMealPlan.id}/generate-shopping-list-by-types`;
          body = {
            meal_types: selectedMealTypes,
            list_name: customListName || `Shopping List - ${selectedMealTypes.join(', ')}`
          };
          break;
        case 'custom':
          // For custom lists, we'll create an empty list that users can populate
          endpoint = '/nutrition/shopping-lists';
          body = {
            list_name: customListName || 'Custom Shopping List',
            items: []
          };
          break;
      }

      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session.access_token}`,
        },
        body: Object.keys(body).length > 0 ? JSON.stringify(body) : undefined,
      });

      if (response.ok) {
        const result = await response.json();
        console.log('✅ Shopping list generated successfully:', result);
        
        toast({
          title: 'Shopping list generated!',
          description: `Created "${result.list_name}" with ${result.total_items || 0} items`,
          status: 'success',
          duration: 3000,
          isClosable: true,
        });

        // Load the summary of the generated list
        await loadShoppingListSummary(result.id);
        onUpdate();
      } else {
        const errorText = await response.text();
        throw new Error(`Failed to generate shopping list: ${response.status} ${errorText}`);
      }
    } catch (error) {
      console.error('Error generating shopping list:', error);
      toast({
        title: 'Error generating shopping list',
        description: error instanceof Error ? error.message : 'Please try again',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setGenerating(false);
    }
  };

  const loadShoppingListSummary = async (shoppingListId: string) => {
    try {
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      const response = await fetch(`http://localhost:8000/nutrition/shopping-lists/${shoppingListId}/summary`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${session?.access_token || ''}`,
        },
      });

      if (response.ok) {
        const summary = await response.json();
        setShoppingListSummary(summary);
        onOpen();
      }
    } catch (error) {
      console.error('Error loading shopping list summary:', error);
    }
  };

  const getCategoryIcon = (category: string) => {
    const categoryIcons: Record<string, any> = {
      protein: FiTarget,
      dairy: FiPackage,
      vegetables: FiZap,
      fruits: FiZap,
      grains: FiPackage,
      nuts_seeds: FiPackage,
      oils_fats: FiPackage,
      herbs_spices: FiZap,
      condiments: FiPackage,
      other: FiPackage
    };
    return categoryIcons[category] || FiPackage;
  };

  const getCategoryColor = (category: string) => {
    const categoryColors: Record<string, string> = {
      protein: 'red',
      dairy: 'blue',
      vegetables: 'green',
      fruits: 'orange',
      grains: 'yellow',
      nuts_seeds: 'purple',
      oils_fats: 'pink',
      herbs_spices: 'teal',
      condiments: 'gray',
      other: 'gray'
    };
    return categoryColors[category] || 'gray';
  };

  const formatCategoryName = (category: string) => {
    return category.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const filteredCategories = shoppingListSummary?.categories 
    ? Object.entries(shoppingListSummary.categories).filter(([category]) => 
        filterCategory === 'all' || category === filterCategory
      )
    : [];

  return (
    <VStack spacing={6} align="stretch">
      <Box>
        <Heading size="lg" mb={2}>
          Smart Shopping List Generator
        </Heading>
        <Text color="gray.600">
          Generate intelligent shopping lists from your meal plans with advanced filtering and customization
        </Text>
      </Box>

      {/* Meal Plan Selection */}
      <Card bg={cardBg} borderColor={borderColor}>
        <CardHeader>
          <Heading size="md">Select Meal Plan</Heading>
        </CardHeader>
        <CardBody>
          {mealPlans.length === 0 ? (
            <Alert status="info">
              <AlertIcon />
              <Text>No meal plans available. Create a meal plan first to generate shopping lists.</Text>
            </Alert>
          ) : (
            <SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} spacing={4}>
              {mealPlans.map((plan) => (
                <Card
                  key={plan.id}
                  cursor="pointer"
                  borderColor={selectedMealPlan?.id === plan.id ? 'blue.500' : borderColor}
                  borderWidth={selectedMealPlan?.id === plan.id ? 2 : 1}
                  onClick={() => setSelectedMealPlan(plan)}
                  _hover={{ borderColor: 'blue.300' }}
                >
                  <CardBody>
                    <VStack align="stretch" spacing={2}>
                      <HStack justify="space-between">
                        <Text fontWeight="semibold" fontSize="sm">
                          {plan.plan_type.charAt(0).toUpperCase() + plan.plan_type.slice(1)} Plan
                        </Text>
                        <Badge colorScheme="blue" size="sm">
                          {plan.meals?.length || 0} meals
                        </Badge>
                      </HStack>
                      <Text fontSize="sm" color="gray.600">
                        {new Date(plan.start_date).toLocaleDateString()}
                        {plan.end_date && plan.end_date !== plan.start_date && 
                          ` - ${new Date(plan.end_date).toLocaleDateString()}`
                        }
                      </Text>
                      <HStack spacing={1} wrap="wrap">
                        {mealTypes.map((type) => {
                          const count = plan.meals?.filter((meal: any) => meal.meal_type === type.value).length || 0;
                          return count > 0 ? (
                            <Badge key={type.value} size="xs" colorScheme="green">
                              {type.label}: {count}
                            </Badge>
                          ) : null;
                        })}
                      </HStack>
                    </VStack>
                  </CardBody>
                </Card>
              ))}
            </SimpleGrid>
          )}
        </CardBody>
      </Card>

      {/* Generation Options */}
      {selectedMealPlan && (
        <Card bg={cardBg} borderColor={borderColor}>
          <CardHeader>
            <HStack justify="space-between">
              <Heading size="md">Generation Options</Heading>
              <Button
                size="sm"
                variant="outline"
                onClick={() => setShowAdvancedOptions(!showAdvancedOptions)}
                leftIcon={<Icon as={showAdvancedOptions ? FiChevronUp : FiChevronDown} />}
              >
                {showAdvancedOptions ? 'Hide' : 'Show'} Advanced
              </Button>
            </HStack>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              {/* Custom List Name */}
              <Box>
                <Text fontWeight="semibold" mb={2}>Custom List Name (Optional)</Text>
                <Input
                  placeholder="e.g., Weekly Groceries, Dinner Party Shopping"
                  value={customListName}
                  onChange={(e) => setCustomListName(e.target.value)}
                />
              </Box>

              {/* Advanced Options */}
              <Collapse in={showAdvancedOptions}>
                <VStack spacing={4} align="stretch">
                  <Divider />
                  
                  {/* Meal Type Filtering */}
                  <Box>
                    <Text fontWeight="semibold" mb={2}>Filter by Meal Types</Text>
                    <SimpleGrid columns={{ base: 2, md: 4 }} spacing={2}>
                      {mealTypes.map((type) => (
                        <Button
                          key={type.value}
                          size="sm"
                          variant={selectedMealTypes.includes(type.value) ? 'solid' : 'outline'}
                          colorScheme={selectedMealTypes.includes(type.value) ? 'blue' : 'gray'}
                          leftIcon={<Icon as={type.icon} />}
                          onClick={() => {
                            if (selectedMealTypes.includes(type.value)) {
                              setSelectedMealTypes(selectedMealTypes.filter(t => t !== type.value));
                            } else {
                              setSelectedMealTypes([...selectedMealTypes, type.value]);
                            }
                          }}
                        >
                          {type.label}
                        </Button>
                      ))}
                    </SimpleGrid>
                  </Box>
                </VStack>
              </Collapse>

              {/* Generation Buttons */}
              <HStack spacing={4} wrap="wrap">
                <Button
                  colorScheme="blue"
                  onClick={() => generateShoppingList('full')}
                  isLoading={generating}
                  loadingText="Generating..."
                  leftIcon={<Icon as={FiShoppingCart} />}
                >
                  Generate Full List
                </Button>
                
                {selectedMealTypes.length > 0 && (
                  <Button
                    colorScheme="green"
                    onClick={() => generateShoppingList('filtered')}
                    isLoading={generating}
                    loadingText="Generating..."
                    leftIcon={<Icon as={FiFilter} />}
                  >
                    Generate Filtered List
                  </Button>
                )}
                
                <Button
                  colorScheme="purple"
                  onClick={() => generateShoppingList('custom')}
                  isLoading={generating}
                  loadingText="Creating..."
                  leftIcon={<Icon as={FiPlus} />}
                >
                  Create Custom List
                </Button>
              </HStack>
            </VStack>
          </CardBody>
        </Card>
      )}

      {/* Shopping List Summary Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent maxW="4xl">
          <ModalHeader>
            <HStack justify="space-between">
              <Text>{shoppingListSummary?.list_name}</Text>
              <HStack spacing={2}>
                <Button size="sm" leftIcon={<Icon as={FiDownload} />}>
                  Export
                </Button>
                <Button size="sm" leftIcon={<Icon as={FiShare} />}>
                  Share
                </Button>
              </HStack>
            </HStack>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            {shoppingListSummary && (
              <VStack spacing={6} align="stretch">
                {/* Summary Stats */}
                <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
                  <Stat textAlign="center">
                    <StatLabel>Total Items</StatLabel>
                    <StatNumber color="blue.500">{shoppingListSummary.total_items}</StatNumber>
                  </Stat>
                  <Stat textAlign="center">
                    <StatLabel>Purchased</StatLabel>
                    <StatNumber color="green.500">{shoppingListSummary.purchased_items}</StatNumber>
                  </Stat>
                  <Stat textAlign="center">
                    <StatLabel>Remaining</StatLabel>
                    <StatNumber color="orange.500">
                      {shoppingListSummary.total_items - shoppingListSummary.purchased_items}
                    </StatNumber>
                  </Stat>
                  <Stat textAlign="center">
                    <StatLabel>Progress</StatLabel>
                    <StatNumber color="purple.500">
                      {shoppingListSummary.completion_percentage.toFixed(1)}%
                    </StatNumber>
                  </Stat>
                </SimpleGrid>

                <Progress
                  value={shoppingListSummary.completion_percentage}
                  colorScheme="green"
                  size="lg"
                  borderRadius="md"
                />

                {/* Filters and Sorting */}
                <HStack spacing={4} wrap="wrap">
                  <Select
                    placeholder="Filter by category"
                    value={filterCategory}
                    onChange={(e) => setFilterCategory(e.target.value)}
                    width="200px"
                  >
                    <option value="all">All Categories</option>
                    {categories.map(category => (
                      <option key={category} value={category}>
                        {formatCategoryName(category)}
                      </option>
                    ))}
                  </Select>
                  
                  <Select
                    placeholder="Sort by"
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as any)}
                    width="150px"
                  >
                    <option value="category">Category</option>
                    <option value="name">Name</option>
                    <option value="quantity">Quantity</option>
                  </Select>
                </HStack>

                {/* Categorized Items */}
                <VStack spacing={4} align="stretch">
                  {filteredCategories.map(([category, items]) => (
                    <Card key={category} bg={cardBg} borderColor={borderColor}>
                      <CardHeader pb={2}>
                        <HStack justify="space-between">
                          <HStack spacing={2}>
                            <Icon as={getCategoryIcon(category)} color={`${getCategoryColor(category)}.500`} />
                            <Text fontWeight="semibold">
                              {formatCategoryName(category)}
                            </Text>
                            <Badge colorScheme={getCategoryColor(category)}>
                              {items.length} items
                            </Badge>
                          </HStack>
                        </HStack>
                      </CardHeader>
                      <CardBody pt={0}>
                        <VStack spacing={2} align="stretch">
                          {items.map((item, index) => (
                            <HStack key={index} justify="space-between" p={2} bg="gray.50" borderRadius="md">
                              <HStack spacing={3}>
                                <Checkbox isChecked={item.is_purchased} />
                                <VStack align="start" spacing={0}>
                                  <Text fontWeight="medium">{item.ingredient_id}</Text>
                                  {item.notes && (
                                    <Text fontSize="xs" color="gray.500">
                                      {item.notes}
                                    </Text>
                                  )}
                                </VStack>
                              </HStack>
                              <HStack spacing={2}>
                                <Text fontSize="sm" fontWeight="semibold">
                                  {item.quantity} {item.unit}
                                </Text>
                                <IconButton
                                  size="xs"
                                  icon={<Icon as={FiEdit} />}
                                  aria-label="Edit item"
                                />
                                <IconButton
                                  size="xs"
                                  icon={<Icon as={FiTrash2} />}
                                  aria-label="Remove item"
                                  colorScheme="red"
                                  variant="ghost"
                                />
                              </HStack>
                            </HStack>
                          ))}
                        </VStack>
                      </CardBody>
                    </Card>
                  ))}
                </VStack>
              </VStack>
            )}
          </ModalBody>
        </ModalContent>
      </Modal>
    </VStack>
  );
};

export default EnhancedShoppingListGenerator;







