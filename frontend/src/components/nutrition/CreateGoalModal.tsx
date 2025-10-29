import React, { useState, useEffect } from 'react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  VStack,
  HStack,
  Text,
  FormControl,
  FormLabel,
  Input,
  Textarea,
  Select,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  Button,
  useToast,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  SimpleGrid,
  Card,
  CardBody,
  CardHeader,
  Badge,
  Icon,
  useColorModeValue,
  Divider,
  Alert,
  AlertIcon,
  Spinner
} from '@chakra-ui/react';
import { 
  FiTarget, 
  FiPlus, 
  FiCalendar,
  FiTrendingUp,
  FiAward,
  FiInfo
} from 'react-icons/fi';
import nutritionGoalsService from '../../services/nutritionGoalsService';
import type { GoalTemplate } from '../../services/nutritionGoalsService';

interface CreateGoalModalProps {
  isOpen: boolean;
  onClose: () => void;
  onGoalCreated: () => void;
}

const CreateGoalModal: React.FC<CreateGoalModalProps> = ({ 
  isOpen, 
  onClose, 
  onGoalCreated 
}) => {
  const [activeTab, setActiveTab] = useState(0);
  const [templates, setTemplates] = useState<GoalTemplate[]>([]);
  const [loadingTemplates, setLoadingTemplates] = useState(false);
  const [creating, setCreating] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<GoalTemplate | null>(null);
  
  // Custom goal form state
  const [goalData, setGoalData] = useState({
    goal_name: '',
    description: '',
    goal_type: 'calories',
    target_value: 2000,
    unit: 'cal',
    frequency: 'daily',
    start_date: new Date().toISOString().split('T')[0],
    target_date: '',
    is_flexible: true,
    priority: 1,
    is_public: false
  });

  const toast = useToast();
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  useEffect(() => {
    if (isOpen) {
      loadTemplates();
    }
  }, [isOpen]);

  const loadTemplates = async () => {
    try {
      setLoadingTemplates(true);
      const data = await nutritionGoalsService.getGoalTemplates();
      setTemplates(data);
    } catch (error) {
      console.error('Error loading templates:', error);
    } finally {
      setLoadingTemplates(false);
    }
  };

  const handleTemplateSelect = (template: GoalTemplate) => {
    setSelectedTemplate(template);
    setGoalData({
      goal_name: template.name,
      description: template.description || '',
      goal_type: template.goal_type,
      target_value: template.default_target_value,
      unit: template.default_unit,
      frequency: template.default_frequency,
      start_date: new Date().toISOString().split('T')[0],
      target_date: template.default_duration_days 
        ? new Date(Date.now() + template.default_duration_days * 24 * 60 * 60 * 1000).toISOString().split('T')[0]
        : '',
      is_flexible: true,
      priority: 1,
      is_public: false
    });
    setActiveTab(1); // Switch to custom form tab
  };

  const handleInputChange = (field: string, value: any) => {
    setGoalData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleCreateGoal = async () => {
    try {
      setCreating(true);
      
      if (selectedTemplate) {
        // Create from template
        await nutritionGoalsService.createGoalFromTemplate(selectedTemplate.id, goalData);
      } else {
        // Create custom goal
        await nutritionGoalsService.createGoal(goalData);
      }
      
      toast({
        title: "Goal Created!",
        description: "Your nutrition goal has been created successfully.",
        status: "success",
        duration: 3000,
        isClosable: true,
      });
      
      onGoalCreated();
    } catch (error) {
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to create goal",
        status: "error",
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setCreating(false);
    }
  };

  const getGoalTypeIcon = (goalType: string) => {
    switch (goalType) {
      case 'calories':
        return <Icon as={FiTarget} color="orange.500" />;
      case 'protein':
        return <Icon as={FiTrendingUp} color="blue.500" />;
      case 'fiber':
        return <Icon as={FiTarget} color="green.500" />;
      case 'water':
        return <Icon as={FiTarget} color="cyan.500" />;
      case 'sodium':
        return <Icon as={FiTarget} color="purple.500" />;
      case 'weight_loss':
        return <Icon as={FiTrendingUp} color="red.500" />;
      case 'weight_gain':
        return <Icon as={FiTrendingUp} color="green.500" />;
      default:
        return <Icon as={FiTarget} color="gray.500" />;
    }
  };

  const getDifficultyColor = (level: number) => {
    switch (level) {
      case 1:
        return 'green';
      case 2:
        return 'blue';
      case 3:
        return 'yellow';
      case 4:
        return 'orange';
      case 5:
        return 'red';
      default:
        return 'gray';
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Create New Nutrition Goal</ModalHeader>
        <ModalCloseButton />
        
        <ModalBody>
          <Tabs index={activeTab} onChange={setActiveTab}>
            <TabList>
              <Tab>From Template</Tab>
              <Tab>Custom Goal</Tab>
            </TabList>

            <TabPanels>
              {/* Templates Tab */}
              <TabPanel px={0}>
                <VStack spacing={4} align="stretch">
                  <Text fontSize="sm" color="gray.600">
                    Choose from our pre-made goal templates to get started quickly
                  </Text>
                  
                  {loadingTemplates ? (
                    <HStack justify="center" py={8}>
                      <Spinner />
                      <Text>Loading templates...</Text>
                    </HStack>
                  ) : (
                    <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                      {templates.map((template) => (
                        <Card 
                          key={template.id} 
                          cursor="pointer" 
                          onClick={() => handleTemplateSelect(template)}
                          _hover={{ shadow: "md" }}
                          borderColor={selectedTemplate?.id === template.id ? "blue.500" : undefined}
                          borderWidth={selectedTemplate?.id === template.id ? 2 : 1}
                        >
                          <CardHeader pb={2}>
                            <HStack spacing={3}>
                              {getGoalTypeIcon(template.goal_type)}
                              <VStack align="start" spacing={1} flex="1">
                                <Text fontWeight="semibold" fontSize="md">
                                  {template.name}
                                </Text>
                                <HStack spacing={2}>
                                  <Badge 
                                    colorScheme={getDifficultyColor(template.difficulty_level)}
                                    size="sm"
                                  >
                                    Level {template.difficulty_level}
                                  </Badge>
                                  {template.category && (
                                    <Badge colorScheme="gray" size="sm">
                                      {template.category}
                                    </Badge>
                                  )}
                                </HStack>
                              </VStack>
                            </HStack>
                          </CardHeader>
                          
                          <CardBody pt={0}>
                            <VStack spacing={3} align="stretch">
                              <Text fontSize="sm" color="gray.600">
                                {template.description}
                              </Text>
                              
                              <HStack justify="space-between">
                                <Text fontSize="sm" fontWeight="semibold">
                                  Target: {template.default_target_value} {template.default_unit}
                                </Text>
                                <Text fontSize="sm" color="gray.500">
                                  {template.default_frequency}
                                </Text>
                              </HStack>
                              
                              {template.tips && (
                                <Alert status="info" size="sm">
                                  <AlertIcon />
                                  <Text fontSize="xs">{template.tips}</Text>
                                </Alert>
                              )}
                            </VStack>
                          </CardBody>
                        </Card>
                      ))}
                    </SimpleGrid>
                  )}
                </VStack>
              </TabPanel>

              {/* Custom Goal Tab */}
              <TabPanel px={0}>
                <VStack spacing={4} align="stretch">
                  <FormControl isRequired>
                    <FormLabel>Goal Name</FormLabel>
                    <Input
                      value={goalData.goal_name}
                      onChange={(e) => handleInputChange('goal_name', e.target.value)}
                      placeholder="e.g., Eat 100g Protein Daily"
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel>Description (Optional)</FormLabel>
                    <Textarea
                      value={goalData.description}
                      onChange={(e) => handleInputChange('description', e.target.value)}
                      placeholder="Describe your goal and why it's important to you"
                      rows={3}
                    />
                  </FormControl>

                  <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                    <FormControl isRequired>
                      <FormLabel>Goal Type</FormLabel>
                      <Select
                        value={goalData.goal_type}
                        onChange={(e) => handleInputChange('goal_type', e.target.value)}
                      >
                        <option value="calories">Calories</option>
                        <option value="protein">Protein</option>
                        <option value="carbs">Carbohydrates</option>
                        <option value="fat">Fat</option>
                        <option value="fiber">Fiber</option>
                        <option value="sodium">Sodium</option>
                        <option value="water">Water</option>
                        <option value="vitamin_c">Vitamin C</option>
                        <option value="calcium">Calcium</option>
                        <option value="iron">Iron</option>
                        <option value="weight_loss">Weight Loss</option>
                        <option value="weight_gain">Weight Gain</option>
                        <option value="weight_maintenance">Weight Maintenance</option>
                      </Select>
                    </FormControl>

                    <FormControl isRequired>
                      <FormLabel>Frequency</FormLabel>
                      <Select
                        value={goalData.frequency}
                        onChange={(e) => handleInputChange('frequency', e.target.value)}
                      >
                        <option value="daily">Daily</option>
                        <option value="weekly">Weekly</option>
                        <option value="monthly">Monthly</option>
                      </Select>
                    </FormControl>
                  </SimpleGrid>

                  <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                    <FormControl isRequired>
                      <FormLabel>Target Value</FormLabel>
                      <NumberInput
                        value={goalData.target_value}
                        onChange={(_, value) => handleInputChange('target_value', value)}
                        min={0}
                        precision={2}
                      >
                        <NumberInputField />
                        <NumberInputStepper>
                          <NumberIncrementStepper />
                          <NumberDecrementStepper />
                        </NumberInputStepper>
                      </NumberInput>
                    </FormControl>

                    <FormControl isRequired>
                      <FormLabel>Unit</FormLabel>
                      <Select
                        value={goalData.unit}
                        onChange={(e) => handleInputChange('unit', e.target.value)}
                      >
                        <option value="cal">Calories</option>
                        <option value="g">Grams</option>
                        <option value="mg">Milligrams</option>
                        <option value="oz">Ounces</option>
                        <option value="lbs">Pounds</option>
                        <option value="ml">Milliliters</option>
                        <option value="l">Liters</option>
                      </Select>
                    </FormControl>
                  </SimpleGrid>

                  <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                    <FormControl isRequired>
                      <FormLabel>Start Date</FormLabel>
                      <Input
                        type="date"
                        value={goalData.start_date}
                        onChange={(e) => handleInputChange('start_date', e.target.value)}
                      />
                    </FormControl>

                    <FormControl>
                      <FormLabel>Target Date (Optional)</FormLabel>
                      <Input
                        type="date"
                        value={goalData.target_date}
                        onChange={(e) => handleInputChange('target_date', e.target.value)}
                      />
                    </FormControl>
                  </SimpleGrid>

                  <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                    <FormControl>
                      <FormLabel>Priority (1-5)</FormLabel>
                      <NumberInput
                        value={goalData.priority}
                        onChange={(_, value) => handleInputChange('priority', value)}
                        min={1}
                        max={5}
                      >
                        <NumberInputField />
                        <NumberInputStepper>
                          <NumberIncrementStepper />
                          <NumberDecrementStepper />
                        </NumberInputStepper>
                      </NumberInput>
                    </FormControl>

                    <FormControl>
                      <FormLabel>Flexible Goal</FormLabel>
                      <Select
                        value={goalData.is_flexible ? 'true' : 'false'}
                        onChange={(e) => handleInputChange('is_flexible', e.target.value === 'true')}
                      >
                        <option value="true">Yes - Can be adjusted</option>
                        <option value="false">No - Fixed target</option>
                      </Select>
                    </FormControl>
                  </SimpleGrid>
                </VStack>
              </TabPanel>
            </TabPanels>
          </Tabs>
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose}>
            Cancel
          </Button>
          <Button
            colorScheme="blue"
            onClick={handleCreateGoal}
            isLoading={creating}
            loadingText="Creating..."
            isDisabled={!goalData.goal_name || !goalData.target_value}
          >
            Create Goal
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default CreateGoalModal;
