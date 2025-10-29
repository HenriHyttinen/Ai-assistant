import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Checkbox,
  useColorModeValue,
  Collapse,
  useDisclosure,
  Badge,
  Icon,
  Divider,
  RangeSlider,
  RangeSliderTrack,
  RangeSliderFilledTrack,
  RangeSliderThumb,
  NumberInput,
  NumberInputField,
  NumberInputStepper,
  NumberIncrementStepper,
  NumberDecrementStepper,
  FormControl,
  FormLabel,
} from '@chakra-ui/react';
import { FiChevronDown, FiChevronUp, FiTarget, FiZap, FiShield, FiHeart } from 'react-icons/fi';

interface MicronutrientFiltersProps {
  onFiltersChange: (filters: MicronutrientFilterState) => void;
  initialFilters?: MicronutrientFilterState;
}

interface MicronutrientFilterState {
  nutrients: string[];
  minValues: Record<string, number>;
  maxValues: Record<string, number>;
  categories: string[];
}

const MicronutrientFilters: React.FC<MicronutrientFiltersProps> = ({
  onFiltersChange,
  initialFilters = {
    nutrients: [],
    minValues: {},
    maxValues: {},
    categories: []
  }
}) => {
  const [filters, setFilters] = useState<MicronutrientFilterState>(initialFilters);
  const { isOpen: showFilters, onToggle: toggleFilters } = useDisclosure();
  
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  // Micronutrient categories
  const micronutrientCategories = {
    vitamins: {
      title: 'Vitamins',
      icon: FiZap,
      color: 'blue',
      nutrients: [
        { key: 'vitamin_d', name: 'Vitamin D', unit: 'IU', min: 0, max: 1000 },
        { key: 'vitamin_b12', name: 'Vitamin B12', unit: 'mcg', min: 0, max: 10 },
        { key: 'vitamin_c', name: 'Vitamin C', unit: 'mg', min: 0, max: 200 },
        { key: 'vitamin_a', name: 'Vitamin A', unit: 'IU', min: 0, max: 5000 },
        { key: 'vitamin_e', name: 'Vitamin E', unit: 'mg', min: 0, max: 20 },
        { key: 'vitamin_k', name: 'Vitamin K', unit: 'mcg', min: 0, max: 200 },
        { key: 'thiamine', name: 'Thiamine (B1)', unit: 'mg', min: 0, max: 2 },
        { key: 'riboflavin', name: 'Riboflavin (B2)', unit: 'mg', min: 0, max: 2 },
        { key: 'niacin', name: 'Niacin (B3)', unit: 'mg', min: 0, max: 30 },
        { key: 'folate', name: 'Folate (B9)', unit: 'mcg', min: 0, max: 800 }
      ]
    },
    minerals: {
      title: 'Minerals',
      icon: FiShield,
      color: 'green',
      nutrients: [
        { key: 'calcium', name: 'Calcium', unit: 'mg', min: 0, max: 1000 },
        { key: 'iron', name: 'Iron', unit: 'mg', min: 0, max: 20 },
        { key: 'magnesium', name: 'Magnesium', unit: 'mg', min: 0, max: 500 },
        { key: 'zinc', name: 'Zinc', unit: 'mg', min: 0, max: 15 },
        { key: 'selenium', name: 'Selenium', unit: 'mcg', min: 0, max: 100 },
        { key: 'potassium', name: 'Potassium', unit: 'mg', min: 0, max: 4000 },
        { key: 'phosphorus', name: 'Phosphorus', unit: 'mg', min: 0, max: 1000 }
      ]
    },
    fatty_acids: {
      title: 'Fatty Acids',
      icon: FiHeart,
      color: 'purple',
      nutrients: [
        { key: 'omega_3', name: 'Omega-3', unit: 'g', min: 0, max: 5 },
        { key: 'omega_6', name: 'Omega-6', unit: 'g', min: 0, max: 20 }
      ]
    }
  };

  const handleNutrientToggle = (nutrient: string) => {
    const newNutrients = filters.nutrients.includes(nutrient)
      ? filters.nutrients.filter(n => n !== nutrient)
      : [...filters.nutrients, nutrient];
    
    const newFilters = {
      ...filters,
      nutrients: newNutrients
    };
    
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handleMinValueChange = (nutrient: string, _: string, value: number) => {
    const newFilters = {
      ...filters,
      minValues: {
        ...filters.minValues,
        [nutrient]: value
      }
    };
    
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handleMaxValueChange = (nutrient: string, _: string, value: number) => {
    const newFilters = {
      ...filters,
      maxValues: {
        ...filters.maxValues,
        [nutrient]: value
      }
    };
    
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const handleCategoryToggle = (category: string) => {
    const newCategories = filters.categories.includes(category)
      ? filters.categories.filter(c => c !== category)
      : [...filters.categories, category];
    
    const newFilters = {
      ...filters,
      categories: newCategories
    };
    
    setFilters(newFilters);
    onFiltersChange(newFilters);
  };

  const clearAllFilters = () => {
    const clearedFilters = {
      nutrients: [],
      minValues: {},
      maxValues: {},
      categories: []
    };
    
    setFilters(clearedFilters);
    onFiltersChange(clearedFilters);
  };

  const getActiveFiltersCount = () => {
    return filters.nutrients.length + Object.keys(filters.minValues).length + Object.keys(filters.maxValues).length;
  };

  return (
    <Box>
      <Button
        onClick={toggleFilters}
        variant="outline"
        size="sm"
        rightIcon={showFilters ? <FiChevronUp /> : <FiChevronDown />}
        mb={4}
      >
        <Icon as={FiTarget} mr={2} />
        Micronutrient Filters
        {getActiveFiltersCount() > 0 && (
          <Badge ml={2} colorScheme="blue" variant="solid">
            {getActiveFiltersCount()}
          </Badge>
        )}
      </Button>

      <Collapse in={showFilters}>
        <Box p={4} bg={cardBg} borderRadius="md" border="1px" borderColor={borderColor}>
          <VStack spacing={4} align="stretch">
            {/* Category Selection */}
            <Box>
              <Text fontWeight="semibold" mb={3}>Categories</Text>
              <HStack spacing={4} wrap="wrap">
                {Object.entries(micronutrientCategories).map(([key, category]) => (
                  <Button
                    key={key}
                    size="sm"
                    variant={filters.categories.includes(key) ? 'solid' : 'outline'}
                    colorScheme={category.color}
                    leftIcon={<Icon as={category.icon} />}
                    onClick={() => handleCategoryToggle(key)}
                  >
                    {category.title}
                  </Button>
                ))}
              </HStack>
            </Box>

            <Divider />

            {/* Individual Nutrient Filters */}
            <Box>
              <HStack justify="space-between" mb={3}>
                <Text fontWeight="semibold">Specific Nutrients</Text>
                <Button size="xs" variant="ghost" onClick={clearAllFilters}>
                  Clear All
                </Button>
              </HStack>

              {Object.entries(micronutrientCategories).map(([categoryKey, category]) => (
                <Box key={categoryKey} mb={4}>
                  <HStack mb={2}>
                    <Icon as={category.icon} color={`${category.color}.500`} />
                    <Text fontWeight="medium" color={`${category.color}.600`}>
                      {category.title}
                    </Text>
                  </HStack>
                  
                  <VStack spacing={3} align="stretch" pl={4}>
                    {category.nutrients.map((nutrient) => {
                      const isSelected = filters.nutrients.includes(nutrient.key);
                      const minValue = filters.minValues[nutrient.key] || nutrient.min;
                      const maxValue = filters.maxValues[nutrient.key] || nutrient.max;
                      
                      return (
                        <Box key={nutrient.key} p={3} bg="gray.50" borderRadius="md">
                          <HStack justify="space-between" mb={2}>
                            <Checkbox
                              isChecked={isSelected}
                              onChange={() => handleNutrientToggle(nutrient.key)}
                            >
                              <Text fontSize="sm" fontWeight="medium">
                                {nutrient.name}
                              </Text>
                            </Checkbox>
                            <Text fontSize="xs" color="gray.500">
                              {nutrient.unit}
                            </Text>
                          </HStack>
                          
                          {isSelected && (
                            <VStack spacing={2} align="stretch">
                              <HStack spacing={2}>
                                <FormControl size="sm">
                                  <FormLabel fontSize="xs">Min</FormLabel>
                                  <NumberInput
                                    size="sm"
                                    value={minValue}
                                    min={nutrient.min}
                                    max={nutrient.max}
                                    onChange={(_, value) => handleMinValueChange(nutrient.key, '', value)}
                                  >
                                    <NumberInputField />
                                    <NumberInputStepper>
                                      <NumberIncrementStepper />
                                      <NumberDecrementStepper />
                                    </NumberInputStepper>
                                  </NumberInput>
                                </FormControl>
                                
                                <FormControl size="sm">
                                  <FormLabel fontSize="xs">Max</FormLabel>
                                  <NumberInput
                                    size="sm"
                                    value={maxValue}
                                    min={nutrient.min}
                                    max={nutrient.max}
                                    onChange={(_, value) => handleMaxValueChange(nutrient.key, '', value)}
                                  >
                                    <NumberInputField />
                                    <NumberInputStepper>
                                      <NumberIncrementStepper />
                                      <NumberDecrementStepper />
                                    </NumberInputStepper>
                                  </NumberInput>
                                </FormControl>
                              </HStack>
                              
                              <Box px={2}>
                                <RangeSlider
                                  value={[minValue, maxValue]}
                                  min={nutrient.min}
                                  max={nutrient.max}
                                  step={nutrient.max > 100 ? 10 : 1}
                                  onChange={(values: number[]) => {
                                    handleMinValueChange(nutrient.key, '', values[0]);
                                    handleMaxValueChange(nutrient.key, '', values[1]);
                                  }}
                                >
                                  <RangeSliderTrack>
                                    <RangeSliderFilledTrack />
                                  </RangeSliderTrack>
                                  <RangeSliderThumb index={0} />
                                  <RangeSliderThumb index={1} />
                                </RangeSlider>
                              </Box>
                            </VStack>
                          )}
                        </Box>
                      );
                    })}
                  </VStack>
                </Box>
              ))}
            </Box>

            {/* Quick Presets */}
            <Box>
              <Text fontWeight="semibold" mb={3}>Quick Presets</Text>
              <HStack spacing={2} wrap="wrap">
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    const presetFilters = {
                      nutrients: ['vitamin_d', 'iron', 'calcium'],
                      minValues: { vitamin_d: 100, iron: 5, calcium: 200 },
                      maxValues: { vitamin_d: 1000, iron: 20, calcium: 1000 },
                      categories: []
                    };
                    setFilters(presetFilters);
                    onFiltersChange(presetFilters);
                  }}
                >
                  Common Deficiencies
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    const presetFilters = {
                      nutrients: ['omega_3', 'vitamin_c', 'magnesium'],
                      minValues: { omega_3: 1, vitamin_c: 50, magnesium: 200 },
                      maxValues: { omega_3: 5, vitamin_c: 200, magnesium: 500 },
                      categories: []
                    };
                    setFilters(presetFilters);
                    onFiltersChange(presetFilters);
                  }}
                >
                  Anti-Inflammatory
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => {
                    const presetFilters = {
                      nutrients: ['vitamin_b12', 'folate', 'iron'],
                      minValues: { vitamin_b12: 2, folate: 400, iron: 10 },
                      maxValues: { vitamin_b12: 10, folate: 800, iron: 20 },
                      categories: []
                    };
                    setFilters(presetFilters);
                    onFiltersChange(presetFilters);
                  }}
                >
                  Energy & Focus
                </Button>
              </HStack>
            </Box>
          </VStack>
        </Box>
      </Collapse>
    </Box>
  );
};

export default MicronutrientFilters;
