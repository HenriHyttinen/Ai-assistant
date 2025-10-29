import React from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Slider,
  SliderTrack,
  SliderFilledTrack,
  SliderThumb,
  Checkbox,
  CheckboxGroup,
  Stack,
  Divider,
  useColorModeValue,
  Badge,
  Icon
} from '@chakra-ui/react';
import { FiStar, FiFilter, FiCheck } from 'react-icons/fi';

interface RatingFiltersProps {
  minRating: number;
  maxRating: number;
  verifiedOnly: boolean;
  wouldMakeAgain: boolean | null;
  minReviews: number;
  onMinRatingChange: (value: number) => void;
  onMaxRatingChange: (value: number) => void;
  onVerifiedOnlyChange: (checked: boolean) => void;
  onWouldMakeAgainChange: (value: boolean | null) => void;
  onMinReviewsChange: (value: number) => void;
  onReset: () => void;
}

const RatingFilters: React.FC<RatingFiltersProps> = ({
  minRating,
  maxRating,
  verifiedOnly,
  wouldMakeAgain,
  minReviews,
  onMinRatingChange,
  onMaxRatingChange,
  onVerifiedOnlyChange,
  onWouldMakeAgainChange,
  onMinReviewsChange,
  onReset
}) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.400');

  const hasActiveFilters = minRating > 1 || maxRating < 5 || verifiedOnly || wouldMakeAgain !== null || minReviews > 0;

  return (
    <Box
      p={4}
      bg={bgColor}
      borderRadius="lg"
      border="1px"
      borderColor={borderColor}
      boxShadow="sm"
    >
      <VStack spacing={4} align="stretch">
        {/* Header */}
        <HStack justify="space-between" align="center">
          <HStack spacing={2}>
            <Icon as={FiFilter} color="blue.500" />
            <Text fontSize="md" fontWeight="semibold">
              Rating Filters
            </Text>
          </HStack>
          {hasActiveFilters && (
            <Badge colorScheme="blue" variant="solid">
              Active
            </Badge>
          )}
        </HStack>

        <Divider />

        {/* Rating Range */}
        <VStack spacing={3} align="stretch">
          <Text fontSize="sm" fontWeight="semibold">
            Rating Range
          </Text>
          
          <VStack spacing={2}>
            <HStack justify="space-between" w="full">
              <Text fontSize="sm" color={textColor}>
                Min: {minRating} stars
              </Text>
              <Text fontSize="sm" color={textColor}>
                Max: {maxRating} stars
              </Text>
            </HStack>
            
            <HStack spacing={4} w="full">
              <VStack spacing={1} flex={1}>
                <Text fontSize="xs" color={textColor}>
                  Minimum Rating
                </Text>
                <Slider
                  value={minRating}
                  onChange={onMinRatingChange}
                  min={1}
                  max={5}
                  step={0.5}
                  colorScheme="yellow"
                >
                  <SliderTrack>
                    <SliderFilledTrack />
                  </SliderTrack>
                  <SliderThumb boxSize={4}>
                    <Icon as={FiStar} color="yellow.400" />
                  </SliderThumb>
                </Slider>
              </VStack>
              
              <VStack spacing={1} flex={1}>
                <Text fontSize="xs" color={textColor}>
                  Maximum Rating
                </Text>
                <Slider
                  value={maxRating}
                  onChange={onMaxRatingChange}
                  min={1}
                  max={5}
                  step={0.5}
                  colorScheme="yellow"
                >
                  <SliderTrack>
                    <SliderFilledTrack />
                  </SliderTrack>
                  <SliderThumb boxSize={4}>
                    <Icon as={FiStar} color="yellow.400" />
                  </SliderThumb>
                </Slider>
              </VStack>
            </HStack>
          </VStack>
        </VStack>

        <Divider />

        {/* Quality Filters */}
        <VStack spacing={3} align="stretch">
          <Text fontSize="sm" fontWeight="semibold">
            Quality Filters
          </Text>
          
          <CheckboxGroup>
            <Stack spacing={2}>
              <Checkbox
                isChecked={verifiedOnly}
                onChange={(e) => onVerifiedOnlyChange(e.target.checked)}
                colorScheme="blue"
              >
                <HStack spacing={2}>
                  <Text fontSize="sm">Verified cooks only</Text>
                  <Badge colorScheme="blue" size="sm">
                    <Icon as={FiCheck} mr={1} />
                    Verified
                  </Badge>
                </HStack>
              </Checkbox>
              
              <Checkbox
                isChecked={wouldMakeAgain === true}
                onChange={(e) => onWouldMakeAgainChange(e.target.checked ? true : null)}
                colorScheme="purple"
              >
                <Text fontSize="sm">Would make again</Text>
              </Checkbox>
            </Stack>
          </CheckboxGroup>
        </VStack>

        <Divider />

        {/* Review Count */}
        <VStack spacing={3} align="stretch">
          <Text fontSize="sm" fontWeight="semibold">
            Minimum Reviews
          </Text>
          
          <VStack spacing={2}>
            <HStack justify="space-between" w="full">
              <Text fontSize="sm" color={textColor}>
                At least {minReviews} reviews
              </Text>
            </HStack>
            
            <Slider
              value={minReviews}
              onChange={onMinReviewsChange}
              min={0}
              max={50}
              step={5}
              colorScheme="green"
            >
              <SliderTrack>
                <SliderFilledTrack />
              </SliderTrack>
              <SliderThumb boxSize={4}>
                <Box color="green.500">📝</Box>
              </SliderThumb>
            </Slider>
          </VStack>
        </VStack>

        {/* Reset Button */}
        {hasActiveFilters && (
          <>
            <Divider />
            <HStack justify="center">
              <Button
                size="sm"
                variant="outline"
                onClick={onReset}
                colorScheme="gray"
              >
                Reset Filters
              </Button>
            </HStack>
          </>
        )}

        {/* Filter Summary */}
        {hasActiveFilters && (
          <Box p={3} bg={useColorModeValue('blue.50', 'blue.900')} borderRadius="md">
            <Text fontSize="xs" color="blue.600" fontWeight="medium" mb={2}>
              Active Filters:
            </Text>
            <VStack spacing={1} align="start">
              {minRating > 1 && (
                <Text fontSize="xs" color="blue.600">
                  • Min rating: {minRating} stars
                </Text>
              )}
              {maxRating < 5 && (
                <Text fontSize="xs" color="blue.600">
                  • Max rating: {maxRating} stars
                </Text>
              )}
              {verifiedOnly && (
                <Text fontSize="xs" color="blue.600">
                  • Verified cooks only
                </Text>
              )}
              {wouldMakeAgain === true && (
                <Text fontSize="xs" color="blue.600">
                  • Would make again
                </Text>
              )}
              {minReviews > 0 && (
                <Text fontSize="xs" color="blue.600">
                  • Min {minReviews} reviews
                </Text>
              )}
            </VStack>
          </Box>
        )}
      </VStack>
    </Box>
  );
};

export default RatingFilters;


