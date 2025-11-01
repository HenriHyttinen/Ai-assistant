import React from 'react';
import {
  HStack,
  Icon,
  Text,
  Box,
  Tooltip,
  useColorModeValue
} from '@chakra-ui/react';
import { FiStar } from 'react-icons/fi';

interface StarRatingProps {
  rating: number;
  maxRating?: number;
  size?: 'sm' | 'md' | 'lg';
  showNumber?: boolean;
  interactive?: boolean;
  onRatingChange?: (rating: number) => void;
  colorScheme?: 'yellow' | 'blue' | 'green' | 'purple';
}

const StarRating: React.FC<StarRatingProps> = ({
  rating,
  maxRating = 5,
  size = 'md',
  showNumber = true,
  interactive = false,
  onRatingChange,
  colorScheme = 'yellow'
}) => {
  const filledColor = useColorModeValue(
    colorScheme === 'yellow' ? 'yellow.400' : 
    colorScheme === 'blue' ? 'blue.400' :
    colorScheme === 'green' ? 'green.400' :
    'purple.400',
    colorScheme === 'yellow' ? 'yellow.300' : 
    colorScheme === 'blue' ? 'blue.300' :
    colorScheme === 'green' ? 'green.300' :
    'purple.300'
  );
  
  const emptyColor = useColorModeValue('gray.300', 'gray.600');
  const hoverColor = useColorModeValue('gray.400', 'gray.500');

  const sizeMap = {
    sm: '12px',
    md: '16px',
    lg: '20px'
  };

  const iconSize = sizeMap[size];

  const handleStarClick = (starRating: number) => {
    if (interactive && onRatingChange) {
      onRatingChange(starRating);
    }
  };

  const getRatingText = (rating: number) => {
    if (rating >= 4.5) return 'Excellent';
    if (rating >= 4.0) return 'Very Good';
    if (rating >= 3.5) return 'Good';
    if (rating >= 3.0) return 'Average';
    if (rating >= 2.5) return 'Below Average';
    if (rating >= 2.0) return 'Poor';
    return 'Very Poor';
  };

  return (
    <HStack spacing={1} align="center">
      {Array.from({ length: maxRating }, (_, index) => {
        const starRating = index + 1;
        const isFilled = starRating <= Math.round(rating);
        const isHalfFilled = starRating === Math.ceil(rating) && rating % 1 !== 0;
        
        return (
          <Tooltip
            key={index}
            label={`${starRating} star${starRating > 1 ? 's' : ''}`}
            placement="top"
            hasArrow
          >
            <Box
              cursor={interactive ? 'pointer' : 'default'}
              onClick={() => handleStarClick(starRating)}
              _hover={interactive ? { transform: 'scale(1.1)' } : {}}
              transition="all 0.2s"
            >
              <Icon
                as={FiStar}
                w={iconSize}
                h={iconSize}
                color={isFilled ? filledColor : emptyColor}
                fill={isFilled ? filledColor : 'none'}
                stroke={isFilled ? filledColor : emptyColor}
                _hover={interactive ? { color: hoverColor } : {}}
              />
            </Box>
          </Tooltip>
        );
      })}
      
      {showNumber && (
        <Text
          fontSize={size === 'sm' ? 'sm' : size === 'lg' ? 'lg' : 'md'}
          fontWeight="semibold"
          color={useColorModeValue('gray.700', 'gray.300')}
          ml={1}
        >
          {rating.toFixed(1)}
        </Text>
      )}
      
      {rating > 0 && (
        <Text
          fontSize="xs"
          color={useColorModeValue('gray.500', 'gray.400')}
          ml={1}
        >
          ({getRatingText(rating)})
        </Text>
      )}
    </HStack>
  );
};

export default StarRating;







