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
  Checkbox,
  useToast,
  SimpleGrid,
  Icon,
  Flex,
  Spinner,
  Alert,
  AlertIcon,
  Divider,
} from '@chakra-ui/react';
import { FiShoppingCart, FiPlus, FiTrash2, FiCheck } from 'react-icons/fi';
import { t } from '../../utils/translations';

interface ShoppingListProps {
  shoppingLists?: any[];
  onUpdate?: () => void;
}

const ShoppingList: React.FC<ShoppingListProps> = ({
  shoppingLists = [],
  onUpdate = () => {},
}) => {
  const [generating, setGenerating] = useState(false);
  const [selectedList, setSelectedList] = useState<any>(null);
  const toast = useToast();

  const handleGenerateShoppingList = async () => {
    try {
      setGenerating(true);
      
      // Get Supabase session token
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      const response = await fetch('http://localhost:8000/nutrition/shopping-lists', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token || ''}`,
        },
        body: JSON.stringify({
          list_name: 'Weekly Shopping List',
          items: []
        }),
      });

      if (response.ok) {
        toast({
          title: 'Shopping list generated successfully!',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        onUpdate();
      } else {
        const errorText = await response.text();
        console.error('API Error:', response.status, errorText);
        throw new Error(`Failed to generate shopping list: ${response.status} ${errorText}`);
      }
    } catch (error) {
      console.error('Error generating shopping list:', error);
      
      // Add mock shopping list for demo purposes
      const mockList = {
        id: Date.now().toString(),
        name: 'Demo Shopping List',
        items: [
          { id: '1', name: 'Chicken Breast', quantity: '500g', category: 'Meat', purchased: false },
          { id: '2', name: 'Brown Rice', quantity: '1kg', category: 'Grains', purchased: false },
          { id: '3', name: 'Broccoli', quantity: '500g', category: 'Vegetables', purchased: false },
        ],
        created_at: new Date().toISOString(),
      };
      
      // Add to shopping lists (if we had state management)
      toast({
        title: 'Demo Mode',
        description: 'Shopping list generated in demo mode. Real functionality coming soon!',
        status: 'info',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setGenerating(false);
    }
  };

  const toggleItemPurchased = (itemId: string) => {
    // This would update the item's purchased status
    console.log('Toggle purchased for item:', itemId);
  };

  const removeItem = (itemId: string) => {
    // This would remove the item from the list
    console.log('Remove item:', itemId);
  };

  return (
    <VStack spacing={6} align="stretch">
      <Box>
        <Heading size="lg" mb={2}>
          {t('shoppingList', 'en')}
        </Heading>
        <Text color="gray.600">
          Generate and manage your shopping lists from meal plans
        </Text>
      </Box>

      {/* Generate Shopping List */}
      <Card>
        <CardHeader>
          <Heading size="md">Generate Shopping List</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={4}>
            <Text color="gray.600">
              Create a shopping list from your meal plans or add items manually
            </Text>
            
            <Button
              colorScheme="blue"
              size="lg"
              onClick={handleGenerateShoppingList}
              isLoading={generating}
              loadingText="Generating..."
              leftIcon={<Icon as={FiPlus} />}
            >
              {t('generateShoppingList', 'en')}
            </Button>
          </VStack>
        </CardBody>
      </Card>

      {/* Shopping Lists */}
      <Box>
        <HStack justify="space-between" mb={4}>
          <Heading size="md">Your Shopping Lists</Heading>
          <Text color="gray.600">{shoppingLists.length} lists</Text>
        </HStack>

        {shoppingLists.length === 0 ? (
          <Alert status="info" borderRadius="lg">
            <AlertIcon />
            <Box>
              <Text fontWeight="semibold">No shopping lists yet</Text>
              <Text>Generate your first shopping list to get started!</Text>
            </Box>
          </Alert>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
            {shoppingLists.map((list) => (
              <Card key={list.id} variant="outline">
                <CardHeader>
                  <HStack justify="space-between">
                    <Heading size="sm">{list.list_name}</Heading>
                    <Badge colorScheme={list.is_active ? 'green' : 'gray'} variant="subtle">
                      {list.is_active ? 'Active' : 'Inactive'}
                    </Badge>
                  </HStack>
                </CardHeader>
                <CardBody>
                  <VStack spacing={3} align="stretch">
                    <HStack justify="space-between">
                      <Text fontSize="sm" color="gray.600">
                        {list.total_items || 0} items
                      </Text>
                      <Text fontSize="sm" color="gray.600">
                        {list.purchased_items || 0} purchased
                      </Text>
                    </HStack>

                    <Divider />

                    {/* Sample items - in real implementation, these would come from the API */}
                    <VStack spacing={2} align="stretch">
                      <Text fontSize="sm" fontWeight="semibold">Sample Items:</Text>
                      <HStack>
                        <Checkbox size="sm" />
                        <Text fontSize="sm">Chicken breast (500g)</Text>
                        <Badge size="sm" colorScheme="blue">Protein</Badge>
                      </HStack>
                      <HStack>
                        <Checkbox size="sm" />
                        <Text fontSize="sm">Brown rice (1kg)</Text>
                        <Badge size="sm" colorScheme="green">Grains</Badge>
                      </HStack>
                      <HStack>
                        <Checkbox size="sm" defaultChecked />
                        <Text fontSize="sm" textDecoration="line-through" color="gray.500">
                          Olive oil (250ml)
                        </Text>
                        <Badge size="sm" colorScheme="orange">Fats</Badge>
                      </HStack>
                    </VStack>

                    <HStack justify="space-between">
                      <Button size="sm" variant="outline">
                        View Details
                      </Button>
                      <Button size="sm" colorScheme="red" variant="outline">
                        Delete
                      </Button>
                    </HStack>
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

export default ShoppingList;
