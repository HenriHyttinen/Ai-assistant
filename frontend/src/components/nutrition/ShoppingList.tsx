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
} from '@chakra-ui/react';
import { FiShoppingCart, FiPlus, FiTrash2, FiCheck, FiEye } from 'react-icons/fi';
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
  const [lists, setLists] = useState<any[]>(shoppingLists);
  const [loading, setLoading] = useState(false);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  // Load shopping lists on component mount
  useEffect(() => {
    loadShoppingLists();
  }, []);

  const loadShoppingLists = async () => {
    try {
      setLoading(true);
      
      // Get Supabase session token
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      const response = await fetch('http://localhost:8000/nutrition/shopping-lists', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token || ''}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setLists(data);
      } else {
        console.error('Failed to load shopping lists:', response.status);
      }
    } catch (error) {
      console.error('Error loading shopping lists:', error);
    } finally {
      setLoading(false);
    }
  };

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
        // Reload the shopping lists to show the new one
        await loadShoppingLists();
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
          { id: '4', name: 'Olive Oil', quantity: '30ml', category: 'Fats', purchased: false },
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

  const handleViewDetails = (list: any) => {
    setSelectedList(list);
    onOpen();
  };

  const handleDeleteList = async (listId: string) => {
    try {
      // Get Supabase session token
      const { supabase } = await import('../../lib/supabase');
      const { data: { session } } = await supabase.auth.getSession();
      
      const response = await fetch(`http://localhost:8000/nutrition/shopping-lists/${listId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session?.access_token || ''}`,
        },
      });

      if (response.ok) {
        setLists(prev => prev.filter(list => list.id !== listId));
        toast({
          title: 'Shopping list deleted!',
          status: 'success',
          duration: 3000,
        });
        onUpdate();
      } else {
        throw new Error('Failed to delete shopping list');
      }
    } catch (error) {
      console.error('Error deleting shopping list:', error);
      toast({
        title: 'Error deleting shopping list',
        description: 'Please try again later.',
        status: 'error',
        duration: 5000,
      });
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
          {t('shoppingList.title')}
        </Heading>
        <Text color="gray.600">
          {t('shoppingList.subtitle')}
        </Text>
      </Box>

      {/* Generate Shopping List */}
      <Card>
        <CardHeader>
          <Heading size="md">{t('shoppingList.generateNew')}</Heading>
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
              {t('shoppingList.generateNew')}
            </Button>
          </VStack>
        </CardBody>
      </Card>

      {/* Shopping Lists */}
      <Box>
        <HStack justify="space-between" mb={4}>
          <Heading size="md">{t('shoppingList.title')}</Heading>
          <Text color="gray.600">{lists.length} lists</Text>
        </HStack>

        {loading ? (
          <Flex justify="center" py={8}>
            <Spinner size="lg" />
          </Flex>
        ) : lists.length === 0 ? (
          <Alert status="info" borderRadius="lg">
            <AlertIcon />
            <Box>
              <Text fontWeight="semibold">No shopping lists yet</Text>
              <Text>Generate your first shopping list to get started!</Text>
            </Box>
          </Alert>
        ) : (
          <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
            {lists.map((list) => (
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
                        <Checkbox size="sm" />
                        <Text fontSize="sm">Olive oil (30ml)</Text>
                        <Badge size="sm" colorScheme="orange">Fats</Badge>
                      </HStack>
                    </VStack>

                    <HStack justify="space-between">
                      <Button 
                        size="sm" 
                        variant="outline" 
                        leftIcon={<FiEye />}
                        onClick={() => handleViewDetails(list)}
                      >
                        View Details
                      </Button>
                      <Button 
                        size="sm" 
                        colorScheme="red" 
                        variant="outline"
                        leftIcon={<FiTrash2 />}
                        onClick={() => handleDeleteList(list.id)}
                      >
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

      {/* Shopping List Details Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            <HStack>
              <FiShoppingCart />
              <Text>{selectedList?.name || 'Shopping List Details'}</Text>
            </HStack>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            {selectedList && (
              <VStack spacing={4} align="stretch">
                <HStack justify="space-between">
                  <Text fontWeight="semibold">Total Items: {selectedList.total_items || 0}</Text>
                  <Text fontWeight="semibold">Purchased: {selectedList.purchased_items || 0}</Text>
                </HStack>
                
                <Divider />
                
                <VStack spacing={3} align="stretch">
                  <Text fontWeight="semibold">Items:</Text>
                  {selectedList.items?.map((item: any) => (
                    <HStack key={item.id} justify="space-between" p={2} bg="gray.50" borderRadius="md">
                      <HStack>
                        <Checkbox 
                          isChecked={item.purchased} 
                          onChange={() => toggleItemPurchased(item.id)}
                        />
                        <Text>{item.name}</Text>
                        <Badge size="sm" colorScheme="blue">{item.category}</Badge>
                      </HStack>
                      <Text fontSize="sm" color="gray.600">{item.quantity}</Text>
                    </HStack>
                  )) || (
                    <Text color="gray.500" fontStyle="italic">No items in this list</Text>
                  )}
                </VStack>
              </VStack>
            )}
          </ModalBody>
        </ModalContent>
      </Modal>
    </VStack>
  );
};

export default ShoppingList;
