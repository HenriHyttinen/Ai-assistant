import React from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Progress,
  Badge,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  SimpleGrid,
  useColorModeValue,
  Tooltip
} from '@chakra-ui/react';
import { FiStar, FiUsers, FiCheck, FiTrendingUp } from 'react-icons/fi';
import StarRating from './StarRating';

interface RecipeStatsProps {
  stats: {
    recipe_id: string;
    average_rating: number;
    total_ratings: number;
    rating_distribution: { [key: string]: number };
    total_reviews: number;
    verified_cooks: number;
    would_make_again_percentage: number;
    average_difficulty_rating?: number;
    average_taste_rating?: number;
  };
  size?: 'sm' | 'md' | 'lg';
  showDistribution?: boolean;
}

const RecipeStats: React.FC<RecipeStatsProps> = ({
  stats,
  size = 'md',
  showDistribution = true
}) => {
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.400');

  const getRatingPercentage = (rating: number) => {
    const total = stats.total_ratings;
    if (total === 0) return 0;
    return (stats.rating_distribution[rating.toString()] || 0) / total * 100;
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

  const sizeMap = {
    sm: { spacing: 2, fontSize: 'sm', iconSize: '12px' },
    md: { spacing: 3, fontSize: 'md', iconSize: '16px' },
    lg: { spacing: 4, fontSize: 'lg', iconSize: '20px' }
  };

  const currentSize = sizeMap[size];

  return (
    <Box
      p={currentSize.spacing * 2}
      bg={bgColor}
      borderRadius="lg"
      border="1px"
      borderColor={borderColor}
      boxShadow="sm"
    >
      <VStack spacing={currentSize.spacing * 2} align="stretch">
        {/* Main Rating Display */}
        <VStack spacing={currentSize.spacing} align="center">
          <HStack spacing={2} align="center">
            <StarRating
              rating={stats.average_rating}
              size={size}
              showNumber={true}
            />
            <Badge colorScheme="blue" size="sm">
              {getRatingText(stats.average_rating)}
            </Badge>
          </HStack>
          
          <Text fontSize={currentSize.fontSize} color={textColor}>
            Based on {stats.total_ratings} rating{stats.total_ratings !== 1 ? 's' : ''}
          </Text>
        </VStack>

        {/* Key Statistics */}
        <SimpleGrid columns={2} spacing={currentSize.spacing}>
          <Stat textAlign="center">
            <StatLabel fontSize={currentSize.fontSize}>Reviews</StatLabel>
            <StatNumber fontSize={currentSize.fontSize}>
              {stats.total_reviews}
            </StatNumber>
          </Stat>
          
          <Stat textAlign="center">
            <StatLabel fontSize={currentSize.fontSize}>Verified Cooks</StatLabel>
            <StatNumber fontSize={currentSize.fontSize}>
              {stats.verified_cooks}
            </StatNumber>
          </Stat>
          
          <Stat textAlign="center">
            <StatLabel fontSize={currentSize.fontSize}>Would Make Again</StatLabel>
            <StatNumber fontSize={currentSize.fontSize}>
              {stats.would_make_again_percentage.toFixed(0)}%
            </StatNumber>
          </Stat>
          
          <Stat textAlign="center">
            <StatLabel fontSize={currentSize.fontSize}>Helpful Reviews</StatLabel>
            <StatNumber fontSize={currentSize.fontSize}>
              {stats.total_reviews > 0 ? Math.round((stats.total_reviews * 0.8)) : 0}
            </StatNumber>
          </Stat>
        </SimpleGrid>

        {/* Additional Ratings */}
        {(stats.average_difficulty_rating || stats.average_taste_rating) && (
          <VStack spacing={currentSize.spacing} align="stretch">
            <Text fontSize={currentSize.fontSize} fontWeight="semibold">
              Additional Ratings
            </Text>
            
            {stats.average_difficulty_rating && (
              <HStack justify="space-between">
                <Text fontSize={currentSize.fontSize}>Difficulty:</Text>
                <StarRating
                  rating={stats.average_difficulty_rating}
                  size="sm"
                  showNumber={true}
                  colorScheme="blue"
                />
              </HStack>
            )}
            
            {stats.average_taste_rating && (
              <HStack justify="space-between">
                <Text fontSize={currentSize.fontSize}>Taste:</Text>
                <StarRating
                  rating={stats.average_taste_rating}
                  size="sm"
                  showNumber={true}
                  colorScheme="green"
                />
              </HStack>
            )}
          </VStack>
        )}

        {/* Rating Distribution */}
        {showDistribution && stats.total_ratings > 0 && (
          <VStack spacing={currentSize.spacing} align="stretch">
            <Text fontSize={currentSize.fontSize} fontWeight="semibold">
              Rating Distribution
            </Text>
            
            {[5, 4, 3, 2, 1].map((rating) => {
              const percentage = getRatingPercentage(rating);
              const count = stats.rating_distribution[rating.toString()] || 0;
              
              return (
                <HStack key={rating} spacing={2}>
                  <Text fontSize={currentSize.fontSize} minW="20px">
                    {rating}
                  </Text>
                  <Icon as={FiStar} color="yellow.400" />
                  <Progress
                    value={percentage}
                    colorScheme="yellow"
                    size="sm"
                    flex="1"
                    borderRadius="md"
                  />
                  <Text fontSize={currentSize.fontSize} minW="40px" textAlign="right">
                    {count} ({percentage.toFixed(0)}%)
                  </Text>
                </HStack>
              );
            })}
          </VStack>
        )}

        {/* Quality Indicators */}
        <VStack spacing={currentSize.spacing} align="stretch">
          <Text fontSize={currentSize.fontSize} fontWeight="semibold">
            Quality Indicators
          </Text>
          
          <HStack justify="space-between">
            <HStack spacing={1}>
              <Icon as={FiCheck} color="green.500" />
              <Text fontSize={currentSize.fontSize}>
                {stats.verified_cooks} verified cooks
              </Text>
            </HStack>
          </HStack>
          
          <HStack justify="space-between">
            <HStack spacing={1}>
              <Icon as={FiTrendingUp} color="blue.500" />
              <Text fontSize={currentSize.fontSize}>
                {stats.would_make_again_percentage.toFixed(0)}% would make again
              </Text>
            </HStack>
          </HStack>
          
          <HStack justify="space-between">
            <HStack spacing={1}>
              <Icon as={FiUsers} color="purple.500" />
              <Text fontSize={currentSize.fontSize}>
                {stats.total_reviews} detailed reviews
              </Text>
            </HStack>
          </HStack>
        </VStack>
      </VStack>
    </Box>
  );
};

export default RecipeStats;


