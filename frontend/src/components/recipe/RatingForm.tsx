import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Textarea,
  FormControl,
  FormLabel,
  Switch,
  Divider,
  useToast,
  Alert,
  AlertIcon,
  Spinner,
  useColorModeValue
} from '@chakra-ui/react';
import StarRating from './StarRating';
import { FiStar, FiCheck } from 'react-icons/fi';

interface RatingFormProps {
  recipeId: string;
  recipeTitle: string;
  existingRating?: {
    rating: number;
    review_text?: string;
    is_verified: boolean;
    difficulty_rating?: number;
    taste_rating?: number;
    would_make_again: boolean;
  };
  onRatingSubmit: (ratingData: any) => Promise<void>;
  onCancel: () => void;
  isSubmitting?: boolean;
}

const RatingForm: React.FC<RatingFormProps> = ({
  recipeId,
  recipeTitle,
  existingRating,
  onRatingSubmit,
  onCancel,
  isSubmitting = false
}) => {
  const [rating, setRating] = useState(existingRating?.rating || 0);
  const [difficultyRating, setDifficultyRating] = useState(existingRating?.difficulty_rating || 0);
  const [tasteRating, setTasteRating] = useState(existingRating?.taste_rating || 0);
  const [reviewText, setReviewText] = useState(existingRating?.review_text || '');
  const [isVerified, setIsVerified] = useState(existingRating?.is_verified || false);
  const [wouldMakeAgain, setWouldMakeAgain] = useState(existingRating?.would_make_again ?? true);
  
  const toast = useToast();

  const handleSubmit = async () => {
    if (rating === 0) {
      toast({
        title: 'Rating Required',
        description: 'Please provide a star rating for this recipe.',
        status: 'warning',
        duration: 3000,
        isClosable: true,
      });
      return;
    }

    try {
      const ratingData = {
        recipe_id: recipeId,
        rating,
        review_text: reviewText.trim() || null,
        is_verified: isVerified,
        difficulty_rating: difficultyRating || null,
        taste_rating: tasteRating || null,
        would_make_again: wouldMakeAgain
      };

      await onRatingSubmit(ratingData);
      
      toast({
        title: 'Rating Submitted',
        description: `Thank you for rating "${recipeTitle}"!`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to submit rating. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const isFormValid = rating > 0;

  return (
    <Box p={6} bg={useColorModeValue('white', 'gray.800')} borderRadius="lg" boxShadow="md">
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <Box>
          <Text fontSize="lg" fontWeight="semibold" mb={2}>
            {existingRating ? 'Update Your Rating' : 'Rate This Recipe'}
          </Text>
          <Text fontSize="sm" color="gray.600">
            {recipeTitle}
          </Text>
        </Box>

        {/* Overall Rating */}
        <FormControl>
          <FormLabel fontSize="md" fontWeight="semibold">
            Overall Rating *
          </FormLabel>
          <StarRating
            rating={rating}
            interactive={true}
            onRatingChange={setRating}
            size="lg"
            showNumber={true}
          />
          <Text fontSize="xs" color="gray.500" mt={1}>
            How would you rate this recipe overall?
          </Text>
        </FormControl>

        {/* Difficulty Rating */}
        <FormControl>
          <FormLabel fontSize="md" fontWeight="semibold">
            Difficulty Level
          </FormLabel>
          <StarRating
            rating={difficultyRating}
            interactive={true}
            onRatingChange={setDifficultyRating}
            size="md"
            showNumber={true}
            colorScheme="blue"
          />
          <Text fontSize="xs" color="gray.500" mt={1}>
            How difficult was this recipe to make? (Optional)
          </Text>
        </FormControl>

        {/* Taste Rating */}
        <FormControl>
          <FormLabel fontSize="md" fontWeight="semibold">
            Taste Rating
          </FormLabel>
          <StarRating
            rating={tasteRating}
            interactive={true}
            onRatingChange={setTasteRating}
            size="md"
            showNumber={true}
            colorScheme="green"
          />
          <Text fontSize="xs" color="gray.500" mt={1}>
            How did this recipe taste? (Optional)
          </Text>
        </FormControl>

        <Divider />

        {/* Verification and Preferences */}
        <VStack spacing={4} align="stretch">
          <HStack justify="space-between">
            <Box>
              <Text fontSize="md" fontWeight="semibold">
                I actually cooked this recipe
              </Text>
              <Text fontSize="xs" color="gray.500">
                Mark as verified to help other users
              </Text>
            </Box>
            <Switch
              isChecked={isVerified}
              onChange={(e) => setIsVerified(e.target.checked)}
              colorScheme="green"
            />
          </HStack>

          <HStack justify="space-between">
            <Box>
              <Text fontSize="md" fontWeight="semibold">
                I would make this again
              </Text>
              <Text fontSize="xs" color="gray.500">
                Would you cook this recipe again?
              </Text>
            </Box>
            <Switch
              isChecked={wouldMakeAgain}
              onChange={(e) => setWouldMakeAgain(e.target.checked)}
              colorScheme="blue"
            />
          </HStack>
        </VStack>

        {/* Review Text */}
        <FormControl>
          <FormLabel fontSize="md" fontWeight="semibold">
            Written Review (Optional)
          </FormLabel>
          <Textarea
            value={reviewText}
            onChange={(e) => setReviewText(e.target.value)}
            placeholder="Share your thoughts about this recipe... What did you like? Any tips or modifications?"
            rows={4}
            resize="vertical"
            maxLength={2000}
          />
          <Text fontSize="xs" color="gray.500" textAlign="right">
            {reviewText.length}/2000 characters
          </Text>
        </FormControl>

        {/* Action Buttons */}
        <HStack spacing={3} justify="flex-end">
          <Button
            variant="outline"
            onClick={onCancel}
            isDisabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button
            colorScheme="blue"
            onClick={handleSubmit}
            isDisabled={!isFormValid || isSubmitting}
            leftIcon={isSubmitting ? <Spinner size="sm" /> : <FiCheck />}
          >
            {isSubmitting ? 'Submitting...' : existingRating ? 'Update Rating' : 'Submit Rating'}
          </Button>
        </HStack>
      </VStack>
    </Box>
  );
};

export default RatingForm;
