import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  Button,
  Icon,
  useToast,
  useColorModeValue,
  Collapse,
  Divider,
  Avatar,
  Tooltip
} from '@chakra-ui/react';
import { FiThumbsUp, FiThumbsDown, FiChevronDown, FiChevronUp, FiUser, FiCheck } from 'react-icons/fi';
import StarRating from './StarRating';

interface ReviewCardProps {
  review: {
    id: number;
    user_id: string;
    recipe_id: string;
    title?: string;
    content: string;
    is_helpful: boolean;
    cooking_tips?: string;
    modifications?: string;
    created_at: string;
    helpful_count: number;
    not_helpful_count: number;
    user?: {
      email: string;
      profile_picture?: string;
    };
  };
  userRating?: {
    rating: number;
    difficulty_rating?: number;
    taste_rating?: number;
    is_verified: boolean;
    would_make_again: boolean;
  };
  onVoteHelpful: (reviewId: number, isHelpful: boolean) => Promise<void>;
  currentUserId?: string;
  isVoting?: boolean;
}

const ReviewCard: React.FC<ReviewCardProps> = ({
  review,
  userRating,
  onVoteHelpful,
  currentUserId,
  isVoting = false
}) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [hasVoted, setHasVoted] = useState(false);
  const toast = useToast();

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.400');

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const handleVote = async (isHelpful: boolean) => {
    if (hasVoted) return;
    
    try {
      await onVoteHelpful(review.id, isHelpful);
      setHasVoted(true);
      toast({
        title: 'Vote Recorded',
        description: `Thank you for your feedback!`,
        status: 'success',
        duration: 2000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to record vote. Please try again.',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const shouldShowExpandedContent = review.cooking_tips || review.modifications;

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
        <HStack justify="space-between" align="start">
          <HStack spacing={3}>
            <Avatar
              size="sm"
              src={review.user?.profile_picture}
              icon={<Icon as={FiUser} />}
              name={review.user?.email}
            />
            <VStack align="start" spacing={0}>
              <Text fontSize="sm" fontWeight="semibold">
                {review.user?.email || 'Anonymous User'}
              </Text>
              <Text fontSize="xs" color={textColor}>
                {formatDate(review.created_at)}
              </Text>
            </VStack>
          </HStack>
          
          <HStack spacing={2}>
            {review.is_helpful && (
              <Badge colorScheme="green" size="sm">
                Helpful
              </Badge>
            )}
            {userRating?.is_verified && (
              <Tooltip label="Verified Cook">
                <Badge colorScheme="blue" size="sm" leftIcon={<Icon as={FiCheck} />}>
                  Verified
                </Badge>
              </Tooltip>
            )}
          </HStack>
        </HStack>

        {/* User Rating Display */}
        {userRating && (
          <HStack spacing={4} wrap="wrap">
            <HStack spacing={1}>
              <Text fontSize="sm" fontWeight="medium">Overall:</Text>
              <StarRating rating={userRating.rating} size="sm" showNumber={false} />
            </HStack>
            {userRating.difficulty_rating && (
              <HStack spacing={1}>
                <Text fontSize="sm" fontWeight="medium">Difficulty:</Text>
                <StarRating rating={userRating.difficulty_rating} size="sm" showNumber={false} colorScheme="blue" />
              </HStack>
            )}
            {userRating.taste_rating && (
              <HStack spacing={1}>
                <Text fontSize="sm" fontWeight="medium">Taste:</Text>
                <StarRating rating={userRating.taste_rating} size="sm" showNumber={false} colorScheme="green" />
              </HStack>
            )}
            {userRating.would_make_again && (
              <Badge colorScheme="purple" size="sm">
                Would make again
              </Badge>
            )}
          </HStack>
        )}

        {/* Review Title */}
        {review.title && (
          <Text fontSize="md" fontWeight="semibold" color={useColorModeValue('gray.800', 'white')}>
            {review.title}
          </Text>
        )}

        {/* Review Content */}
        <Text fontSize="sm" lineHeight="1.6">
          {review.content}
        </Text>

        {/* Expandable Content */}
        {shouldShowExpandedContent && (
          <>
            <Button
              size="sm"
              variant="ghost"
              onClick={() => setIsExpanded(!isExpanded)}
              rightIcon={<Icon as={isExpanded ? FiChevronUp : FiChevronDown} />}
            >
              {isExpanded ? 'Show Less' : 'Show More Details'}
            </Button>
            
            <Collapse in={isExpanded}>
              <VStack spacing={3} align="stretch">
                {review.cooking_tips && (
                  <Box>
                    <Text fontSize="sm" fontWeight="semibold" color="green.600" mb={1}>
                      Cooking Tips:
                    </Text>
                    <Text fontSize="sm" color={textColor}>
                      {review.cooking_tips}
                    </Text>
                  </Box>
                )}
                
                {review.modifications && (
                  <Box>
                    <Text fontSize="sm" fontWeight="semibold" color="blue.600" mb={1}>
                      Modifications:
                    </Text>
                    <Text fontSize="sm" color={textColor}>
                      {review.modifications}
                    </Text>
                  </Box>
                )}
              </VStack>
            </Collapse>
          </>
        )}

        <Divider />

        {/* Action Buttons */}
        <HStack justify="space-between">
          <HStack spacing={2}>
            <Button
              size="sm"
              variant="outline"
              leftIcon={<Icon as={FiThumbsUp} />}
              onClick={() => handleVote(true)}
              isDisabled={hasVoted || isVoting}
              colorScheme="green"
            >
              Helpful ({review.helpful_count})
            </Button>
            <Button
              size="sm"
              variant="outline"
              leftIcon={<Icon as={FiThumbsDown} />}
              onClick={() => handleVote(false)}
              isDisabled={hasVoted || isVoting}
              colorScheme="red"
            >
              Not Helpful ({review.not_helpful_count})
            </Button>
          </HStack>
        </HStack>
      </VStack>
    </Box>
  );
};

export default ReviewCard;







