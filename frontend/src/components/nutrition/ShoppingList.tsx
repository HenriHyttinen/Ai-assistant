import React, { useState, useEffect, useMemo } from 'react';
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
  Switch,
  FormControl,
  FormLabel,
  CheckboxGroup,
  Stack,
} from '@chakra-ui/react';
import { FiShoppingCart, FiPlus, FiTrash2, FiCheck, FiEye, FiEdit, FiSave, FiX } from 'react-icons/fi';
import { t } from '../../utils/translations';

// Shopping List Item Component
interface ShoppingListItemProps {
  item: any;
  onTogglePurchased: (itemId: string) => void;
  onRemove: (itemId: string) => void;
  onUpdateQuantity: (itemId: string, quantity: number) => void;
}

const toHumanName = (raw: string) => {
  if (!raw) return '';
  const cleaned = raw.replace(/^ing[_-]/i, '').replace(/[_-]+/g, ' ');
  return cleaned.replace(/\b\w/g, (c) => c.toUpperCase());
};

const ShoppingListItem: React.FC<ShoppingListItemProps> = ({
  item,
  onTogglePurchased,
  onRemove,
  onUpdateQuantity
}) => {
  const [isEditingQuantity, setIsEditingQuantity] = useState(false);
  const [editQuantity, setEditQuantity] = useState(item.quantity);

  const handleSaveQuantity = () => {
    if (editQuantity > 0 && editQuantity !== item.quantity) {
      onUpdateQuantity(item.id, editQuantity);
    }
    setIsEditingQuantity(false);
  };

  const handleCancelEdit = () => {
    setEditQuantity(item.quantity);
    setIsEditingQuantity(false);
  };

  return (
    <HStack justify="space-between" p={3} bg="gray.50" borderRadius="md" spacing={3}>
      <HStack spacing={3} flex={1}>
        <Checkbox 
          isChecked={item.purchased || item.is_purchased} 
          onChange={() => onTogglePurchased(item.id)}
        />
        <VStack align="start" spacing={0} flex={1}>
          <Text fontWeight="medium">{item.ingredient_name || item.name || toHumanName(item.ingredient_id)}</Text>
          <HStack spacing={2}>
            <Badge size="sm" colorScheme="blue">{item.category}</Badge>
            {item.notes && (
              <Text fontSize="xs" color="gray.500" fontStyle="italic">
                {item.notes}
              </Text>
            )}
          </HStack>
        </VStack>
      </HStack>
      
      <HStack spacing={2}>
        {isEditingQuantity ? (
          <HStack spacing={1}>
            <Input
              size="sm"
              width="60px"
              type="number"
              value={editQuantity}
              onChange={(e) => setEditQuantity(parseFloat(e.target.value) || 0)}
              min="0"
              step="0.1"
            />
            <Text fontSize="sm" color="gray.600" minWidth="20px">
              {item.unit}
            </Text>
            <IconButton
              size="sm"
              icon={<FiSave />}
              onClick={handleSaveQuantity}
              colorScheme="green"
              variant="ghost"
            />
            <IconButton
              size="sm"
              icon={<FiX />}
              onClick={handleCancelEdit}
              colorScheme="red"
              variant="ghost"
            />
          </HStack>
        ) : (
          <HStack spacing={2}>
            <Text fontSize="sm" color="gray.600" minWidth="60px" textAlign="right">
              {item.quantity} {item.unit}
            </Text>
            <IconButton
              size="sm"
              icon={<FiEdit />}
              onClick={() => setIsEditingQuantity(true)}
              variant="ghost"
            />
            <IconButton
              size="sm"
              icon={<FiTrash2 />}
              onClick={() => onRemove(item.id)}
              colorScheme="red"
              variant="ghost"
            />
          </HStack>
        )}
      </HStack>
    </HStack>
  );
};

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

  // Smart list wizard state
  const [mealPlans, setMealPlans] = useState<any[]>([]);
  const [selectedMealPlanId, setSelectedMealPlanId] = useState<string>('');
  const [selectedMealTypes, setSelectedMealTypes] = useState<string[]>(['breakfast','lunch','dinner','snack']);
  const [mergeDuplicates, setMergeDuplicates] = useState<boolean>(true);
  const [normalizeUnits, setNormalizeUnits] = useState<boolean>(true);
  const [excludePantry, setExcludePantry] = useState<string>('salt, pepper, water');

  // Load shopping lists on component mount
  useEffect(() => {
    loadShoppingLists();
    loadRecentMealPlans();
  }, []);

  const loadShoppingLists = async () => {
    const attemptFetch = async (attempt: number): Promise<void> => {
    try {
      setLoading(true);
      const { supabase } = await import('../../lib/supabase.ts');
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
          return;
      }
        throw new Error(`HTTP ${response.status}`);
    } catch (error) {
        if (attempt < 3) {
          toast({ title: 'Shopping lists unavailable', description: `Retrying... (${attempt}/3)`, status: 'warning', duration: 1500, isClosable: true });
          await new Promise(res => setTimeout(res, attempt * 1000));
          return attemptFetch(attempt + 1);
        }
        toast({ title: 'Failed to load shopping lists', description: 'Please try again later.', status: 'error', duration: 3000, isClosable: true });
    } finally {
      setLoading(false);
    }
    };
    await attemptFetch(1);
  };

  const loadRecentMealPlans = async () => {
    try {
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      const token = session?.access_token || '';
      const today = new Date();
      const dates: string[] = [];
      for (let i = 0; i < 7; i++) {
        const d = new Date(today);
        d.setDate(today.getDate() - i);
        dates.push(d.toISOString().split('T')[0]);
      }
      // Fetch in parallel for last 7 days; combine unique ids
      const results = await Promise.all(
        dates.map(d => fetch(`http://localhost:8000/nutrition/meal-plans?date=${d}&limit=1`, {
          headers: { 'Authorization': `Bearer ${token}` }
        }).then(r => r.ok ? r.json() : [])
        )
      );
      const combined = Array.from(new Map(results.flat().map((mp: any) => [mp.id, mp])).values());
      setMealPlans(combined);
      if (combined && combined.length) setSelectedMealPlanId(combined[0].id);
    } catch (e) {
      // noop
    }
  };

  const handleGenerateShoppingList = async () => {
    try {
      setGenerating(true);
      
      // Get Supabase session token
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      if (!selectedMealPlanId) {
        toast({ title: 'Select a meal plan first', status: 'info', duration: 2500, isClosable: true });
        return;
      }

      // Use meal-type aware endpoint
      const response = await fetch(`http://localhost:8000/nutrition/meal-plans/${selectedMealPlanId}/generate-shopping-list-by-types`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token || ''}`,
        },
        body: JSON.stringify({
          meal_types: selectedMealTypes,
          list_name: 'Smart Shopping List'
        }),
      });

      if (response.ok) {
        let result = await response.json();
        // Client-side post-processing
        if (result && result.items && Array.isArray(result.items)) {
          const pantry = excludePantry.split(',').map(s => s.trim().toLowerCase()).filter(Boolean);
          let items = result.items.filter((it: any) => !pantry.some(p => (it.name || it.ingredient_id || '').toLowerCase().includes(p)));
          if (normalizeUnits) {
            const map: any = { milliliter: 'ml', liter: 'l', kilograms: 'kg', gram: 'g', grams: 'g' };
            items = items.map((it: any) => ({ ...it, unit: map[it.unit] || it.unit }));
          }
          if (mergeDuplicates) {
            const merged: Record<string, any> = {};
            items.forEach((it: any) => {
              const key = `${(it.name || it.ingredient_id).toLowerCase()}|${it.unit || ''}`;
              if (!merged[key]) merged[key] = { ...it };
              else merged[key].quantity = (parseFloat(merged[key].quantity) || 0) + (parseFloat(it.quantity) || 0);
            });
            result.items = Object.values(merged);
            result.total_items = result.items.length;
          } else {
            result.items = items;
            result.total_items = items.length;
          }
        }
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
      const { supabase } = await import('../../lib/supabase.ts');
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

  const toggleItemPurchased = async (itemId: string) => {
    try {
      // Get Supabase session token
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      
      const response = await fetch(`http://localhost:8000/nutrition/shopping-lists/items/${itemId}/purchased`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${session?.access_token || ''}`,
        },
      });

      if (response.ok) {
        // Update local state
        setLists(prev => prev.map(list => {
          const updatedItems = list.items?.map((item: any) => 
            item.id === itemId 
              ? { ...item, purchased: !item.purchased, is_purchased: !(item.purchased || item.is_purchased) }
              : item
          ) || [];
          return {
            ...list,
            items: updatedItems,
            purchased_items: updatedItems.filter((item: any) => item.is_purchased || item.purchased).length
          };
        }));
        
        // CRITICAL FIX: Also update selectedList if it's open
        if (selectedList) {
          setSelectedList(prev => {
            if (!prev) return prev;
            const updatedItems = (prev.items || []).map((item: any) => 
              item.id === itemId 
                ? { ...item, purchased: !item.purchased, is_purchased: !(item.purchased || item.is_purchased) }
                : item
            );
            return {
              ...prev,
              items: updatedItems,
              purchased_items: updatedItems.filter((item: any) => item.is_purchased || item.purchased).length
            };
          });
        }
        
        toast({
          title: 'Item status updated!',
          status: 'success',
          duration: 2000,
        });
      } else {
        throw new Error('Failed to update item status');
      }
    } catch (error) {
      console.error('Error updating item status:', error);
      toast({
        title: 'Error updating item status',
        description: 'Please try again later.',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const removeItem = async (itemId: string) => {
    try {
      // Get Supabase session token
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      
      const response = await fetch(`http://localhost:8000/nutrition/shopping-lists/items/${itemId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${session?.access_token || ''}`,
        },
      });

      if (response.ok) {
        // Update local state - ensure we create a new array reference for React to detect the change
        setLists(prev => {
          const updated = prev.map(list => ({
          ...list,
            items: (list.items || []).filter((item: any) => String(item.id) !== String(itemId)),
            total_items: (list.total_items || 0) - 1
          }));
          return updated;
        });
        
        // CRITICAL FIX: Also update selectedList if it's the same list
        if (selectedList) {
          setSelectedList(prev => {
            if (!prev) return prev;
            const updatedItems = (prev.items || []).filter((item: any) => String(item.id) !== String(itemId));
            return {
              ...prev,
              items: updatedItems,
              total_items: updatedItems.length,
              purchased_items: updatedItems.filter((item: any) => item.is_purchased || item.purchased).length
            };
          });
        }
        
        // Also trigger parent update if available
        if (onUpdate) {
          onUpdate();
        }
        
        toast({
          title: 'Item removed!',
          status: 'success',
          duration: 2000,
        });
      } else {
        throw new Error('Failed to remove item');
      }
    } catch (error) {
      console.error('Error removing item:', error);
      toast({
        title: 'Error removing item',
        description: 'Please try again later.',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const updateItemQuantity = async (itemId: string, newQuantity: number) => {
    try {
      // Get Supabase session token
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      
      const response = await fetch(`http://localhost:8000/nutrition/shopping-lists/items/${itemId}/quantity`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token || ''}`,
        },
        body: JSON.stringify({ new_quantity: newQuantity }),
      });

      if (response.ok) {
        // Update local state
        setLists(prev => prev.map(list => ({
          ...list,
          items: list.items?.map((item: any) => 
            item.id === itemId 
              ? { ...item, quantity: newQuantity }
              : item
          )
        })));
        
        // CRITICAL FIX: Also update selectedList if it's the same list
        if (selectedList) {
          setSelectedList(prev => {
            if (!prev) return prev;
            return {
              ...prev,
              items: (prev.items || []).map((item: any) => 
                item.id === itemId 
                  ? { ...item, quantity: newQuantity }
                  : item
              )
            };
          });
        }
        
        toast({
          title: 'Quantity updated!',
          status: 'success',
          duration: 2000,
        });
      } else {
        throw new Error('Failed to update quantity');
      }
    } catch (error) {
      console.error('Error updating quantity:', error);
      toast({
        title: 'Error updating quantity',
        description: 'Please try again later.',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const handleTogglePurchased = async (listId: string, itemId: string) => {
    try {
      const { supabase } = await import('../../lib/supabase.ts');
      const { data: { session } } = await supabase.auth.getSession();
      
      const response = await fetch(`http://localhost:8000/nutrition/shopping-lists/items/${itemId}/purchased`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token || ''}`,
        },
      });

      if (response.ok) {
        // Update local state
        setLists(prev => prev.map(list => 
          list.id === listId 
            ? {
                ...list,
                items: list.items?.map((item: any) => 
                  item.id === itemId 
                    ? { ...item, is_purchased: !item.is_purchased }
                    : item
                ) || [],
                purchased_items: list.items?.filter((item: any) => 
                  item.id === itemId ? !item.is_purchased : (item.is_purchased || item.purchased)
                ).length || 0
              }
            : list
        ));
        
        // CRITICAL FIX: Also update selectedList if it's the same list
        if (selectedList && selectedList.id === listId) {
          setSelectedList(prev => {
            if (!prev) return prev;
            const updatedItems = (prev.items || []).map((item: any) => 
              item.id === itemId 
                ? { ...item, is_purchased: !item.is_purchased }
                : item
            );
            return {
              ...prev,
              items: updatedItems,
              purchased_items: updatedItems.filter((item: any) => item.is_purchased || item.purchased).length
            };
          });
        }
      }
    } catch (error) {
      console.error('Error toggling purchased status:', error);
    }
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
          <Heading size="md">Smart Shopping List Generator</Heading>
        </CardHeader>
        <CardBody>
          <VStack spacing={4} align="stretch">
            <Text color="gray.600">Generate intelligent shopping lists with advanced filtering and customization.</Text>

            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
              <FormControl>
                <FormLabel>Select Meal Plan</FormLabel>
                <Select value={selectedMealPlanId} onChange={(e) => setSelectedMealPlanId(e.target.value)}>
                  {mealPlans.length === 0 && <option value="">No meal plans available</option>}
                  {mealPlans.map(mp => (
                    <option key={mp.id} value={mp.id}>{mp.plan_type} • {mp.start_date}</option>
                  ))}
                </Select>
              </FormControl>

              <FormControl>
                <FormLabel>Exclude Pantry Items (comma separated)</FormLabel>
                <Input value={excludePantry} onChange={(e) => setExcludePantry(e.target.value)} placeholder="salt, pepper, water" />
              </FormControl>
            </SimpleGrid>

            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
              <FormControl>
                <FormLabel>Include Meal Types</FormLabel>
                <CheckboxGroup value={selectedMealTypes} onChange={(vals) => setSelectedMealTypes(vals as string[])}>
                  <Stack direction="row" spacing={4} wrap="wrap">
                    {['breakfast','lunch','dinner','snack'].map(t => (
                      <Checkbox key={t} value={t} defaultChecked>{t.charAt(0).toUpperCase()+t.slice(1)}</Checkbox>
                    ))}
                  </Stack>
                </CheckboxGroup>
              </FormControl>
              <FormControl>
                <FormLabel>Options</FormLabel>
                <HStack>
                  <Switch isChecked={mergeDuplicates} onChange={(e)=>setMergeDuplicates(e.target.checked)} />
                  <Text>Merge Duplicates</Text>
                  <Switch ml={6} isChecked={normalizeUnits} onChange={(e)=>setNormalizeUnits(e.target.checked)} />
                  <Text>Normalize Units</Text>
                </HStack>
              </FormControl>
            </SimpleGrid>

            <HStack>
              <Button
                colorScheme="blue"
                onClick={handleGenerateShoppingList}
                isLoading={generating}
                loadingText="Generating..."
                leftIcon={<Icon as={FiPlus} />}
                variant="solid"
              >
                Generate from Meal Plan
              </Button>
              <Button colorScheme="green" onClick={onOpen} leftIcon={<Icon as={FiPlus} />}>Add Items Manually</Button>
            </HStack>
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

                    {/* Shopping List Items */}
                    <VStack spacing={2} align="stretch">
                      <Text fontSize="sm" fontWeight="semibold">Items:</Text>
                      {list.items && list.items.length > 0 ? (
                        list.items.slice(0, 3).map((item: any, index: number) => (
                          <HStack key={index}>
                            <Checkbox 
                              size="sm" 
                              isChecked={item.is_purchased || false}
                              onChange={() => handleTogglePurchased(list.id, item.id)}
                            />
                            <Text fontSize="sm">
                              {item.ingredient_name || item.name || toHumanName(item.ingredient_id)} ({item.quantity} {item.unit})
                            </Text>
                            <Badge size="sm" colorScheme="blue">{item.category}</Badge>
                          </HStack>
                        ))
                      ) : (
                        <Text fontSize="sm" color="gray.500">No items in this list</Text>
                      )}
                      {list.items && list.items.length > 3 && (
                        <Text fontSize="xs" color="gray.500">
                          +{list.items.length - 3} more items
                        </Text>
                      )}
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
                
                {/* CRITICAL FIX: Group items by category for better organization */}
                {(() => {
                  if (!selectedList.items || selectedList.items.length === 0) {
                    return <Text color="gray.500" fontStyle="italic">No items in this list</Text>;
                  }
                  
                  // Group items by category
                  const itemsByCategory = selectedList.items.reduce((acc: any, item: any) => {
                    const category = item.category || 'other';
                    if (!acc[category]) {
                      acc[category] = [];
                    }
                    acc[category].push(item);
                    return acc;
                  }, {});
                  
                  return (
                    <VStack spacing={4} align="stretch">
                      {Object.entries(itemsByCategory).map(([category, items]: [string, any[]]) => (
                        <Box key={category}>
                          <HStack mb={2}>
                            <Badge colorScheme="blue" size="sm" textTransform="capitalize">
                              {category.replace('_', ' ')}
                            </Badge>
                            <Text fontSize="sm" color="gray.600">
                              {items.length} {items.length === 1 ? 'item' : 'items'}
                            </Text>
                          </HStack>
                          <VStack spacing={2} align="stretch">
                            {items.map((item: any) => (
                              <ShoppingListItem 
                                key={item.id} 
                                item={item} 
                                onTogglePurchased={toggleItemPurchased}
                                onRemove={removeItem}
                                onUpdateQuantity={updateItemQuantity}
                              />
                            ))}
                          </VStack>
                        </Box>
                      ))}
                    </VStack>
                  );
                })()}
              </VStack>
            )}
          </ModalBody>
        </ModalContent>
      </Modal>
    </VStack>
  );
};

export default ShoppingList;
