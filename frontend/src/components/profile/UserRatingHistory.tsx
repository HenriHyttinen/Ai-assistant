import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Badge,
  Button,
  Icon,
  useColorModeValue,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  Divider,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Progress,
  Tooltip,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useDisclosure
} from '@chakra-ui/react';
import { 
  FiStar, 
  FiTrendingUp, 
  FiUsers, 
  FiCheck, 
  FiMoreVertical,
  FiEdit,
  FiTrash2,
  FiEye,
  FiHeart
} from 'react-icons/fi';
import StarRating from '../recipe/StarRating';
import RecipeStats from '../recipe/RecipeStats';
import RatingForm from '../recipe/RatingForm';
import ReviewCard from '../recipe/ReviewCard';
import recipeRatingService from '../../services/recipeRatingService';

interface UserRating {
  id: number;
  recipe_id: string;
  rating: number;
  review_text?: string;
  is_verified: boolean;
  difficulty_rating?: number;
  taste_rating?: number;
  would_make_again: boolean;
  created_at: string;
  updated_at: string;
  recipe?: {
    id: string;
    title: string;
    cuisine: string;
    meal_type: string;
    image_url?: string;
  };
}

interface UserReview {
  id: number;
  recipe_id: string;
  title?: string;
  content: string;
  is_helpful: boolean;
  cooking_tips?: string;
  modifications?: string;
  created_at: string;
  updated_at: string;
  helpful_count: number;
  not_helpful_count: number;
  recipe?: {
    id: string;
    title: string;
    cuisine: string;
    meal_type: string;
    image_url?: string;
  };
}

interface UserRatingSummary {
  total_ratings: number;
  total_reviews: number;
  average_rating_given?: number;
  most_rated_cuisine?: string;
  favorite_recipe?: string;
}

const UserRatingHistory: React.FC = () => {
  const [ratings, setRatings] = useState<UserRating[]>([]);
  const [reviews, setReviews] = useState<UserReview[]>([]);
  const [summary, setSummary] = useState<UserRatingSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'ratings' | 'reviews' | 'summary'>('summary');
  const [selectedRating, setSelectedRating] = useState<UserRating | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const { isOpen, onOpen, onClose } = useDisclosure();
  const toast = useToast();

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.400');

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      setLoading(true);
      
      // Load user rating summary
      const summaryData = await recipeRatingService.getUserRatingSummary();
      setSummary(summaryData);
      
      // Note: We would need additional endpoints to get user's ratings and reviews
      // For now, we'll show the summary and placeholder data
      
    } catch (error) {
      console.error('Error loading user data:', error);
      toast({
        title: 'Error',
        description: 'Failed to load your rating history',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleEditRating = (rating: UserRating) => {
    setSelectedRating(rating);
    setIsEditing(true);
    onOpen();
  };

  const handleDeleteRating = async (ratingId: number) => {
    try {
      await recipeRatingService.deleteRating(ratingId);
      setRatings(prev => prev.filter(r => r.id !== ratingId));
      toast({
        title: 'Rating Deleted',
        description: 'Your rating has been removed',
        status: 'success',
        duration: 3000,
        isClosable: true,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete rating',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    }
  };

  const handleRatingSubmit = async (ratingData: any) => {
    try {
      if (isEditing && selectedRating) {
        await recipeRatingService.updateRating(selectedRating.id, ratingData);
        toast({
          title: 'Rating Updated',
          description: 'Your rating has been updated successfully',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      } else {
        await recipeRatingService.createRating(ratingData);
        toast({
          title: 'Rating Submitted',
          description: 'Thank you for rating this recipe!',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
      }
      
      onClose();
      setIsEditing(false);
      setSelectedRating(null);
      loadUserData();
    } catch (error) {
      throw error; // Re-throw to be handled by the form
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <Box p={6}>
        <VStack spacing={4}>
          <Spinner size="lg" />
          <Text>Loading your rating history...</Text>
        </VStack>
      </Box>
    );
  }

  return (
    <Box>
      {/* Header */}
      <VStack spacing={4} align="stretch" mb={6}>
        <Heading size="md">Your Recipe Ratings & Reviews</Heading>
        <Text color={textColor}>
          Track your cooking experiences and help other users discover great recipes
        </Text>
      </VStack>

      {/* Tab Navigation */}
      <HStack spacing={4} mb={6}>
        <Button
          variant={activeTab === 'summary' ? 'solid' : 'outline'}
          colorScheme="blue"
          onClick={() => setActiveTab('summary')}
          leftIcon={<Icon as={FiTrendingUp} />}
        >
          Summary
        </Button>
        <Button
          variant={activeTab === 'ratings' ? 'solid' : 'outline'}
          colorScheme="yellow"
          onClick={() => setActiveTab('ratings')}
          leftIcon={<Icon as={FiStar} />}
        >
          Ratings ({summary?.total_ratings || 0})
        </Button>
        <Button
          variant={activeTab === 'reviews' ? 'solid' : 'outline'}
          colorScheme="green"
          onClick={() => setActiveTab('reviews')}
          leftIcon={<Icon as={FiUsers} />}
        >
          Reviews ({summary?.total_reviews || 0})
        </Button>
      </HStack>

      {/* Summary Tab */}
      {activeTab === 'summary' && summary && (
        <VStack spacing={6} align="stretch">
          {/* Key Statistics */}
          <SimpleGrid columns={{ base: 1, md: 2, lg: 4 }} spacing={4}>
            <Card>
              <CardBody textAlign="center">
                <Stat>
                  <StatLabel>Total Ratings</StatLabel>
                  <StatNumber>{summary.total_ratings}</StatNumber>
                  <StatHelpText>Recipes rated</StatHelpText>
                </Stat>
              </CardBody>
            </Card>
            
            <Card>
              <CardBody textAlign="center">
                <Stat>
                  <StatLabel>Total Reviews</StatLabel>
                  <StatNumber>{summary.total_reviews}</StatNumber>
                  <StatHelpText>Detailed reviews written</StatHelpText>
                </Stat>
              </CardBody>
            </Card>
            
            <Card>
              <CardBody textAlign="center">
                <Stat>
                  <StatLabel>Average Rating Given</StatLabel>
                  <StatNumber>
                    {summary.average_rating_given ? summary.average_rating_given.toFixed(1) : 'N/A'}
                  </StatNumber>
                  <StatHelpText>Your average rating</StatHelpText>
                </Stat>
              </CardBody>
            </Card>
            
            <Card>
              <CardBody textAlign="center">
                <Stat>
                  <StatLabel>Favorite Cuisine</StatLabel>
                  <StatNumber fontSize="lg">
                    {summary.most_rated_cuisine || 'N/A'}
                  </StatNumber>
                  <StatHelpText>Most rated cuisine</StatHelpText>
                </Stat>
              </CardBody>
            </Card>
          </SimpleGrid>

          {/* Favorite Recipe */}
          {summary.favorite_recipe && (
            <Card>
              <CardHeader>
                <Heading size="sm">Your Favorite Recipe</Heading>
              </CardHeader>
              <CardBody>
                <HStack spacing={4}>
                  <Icon as={FiHeart} color="red.500" />
                  <Text fontSize="lg" fontWeight="semibold">
                    {summary.favorite_recipe}
                  </Text>
                </HStack>
              </CardBody>
            </Card>
          )}

          {/* Rating Distribution */}
          <Card>
            <CardHeader>
              <Heading size="sm">Your Rating Distribution</Heading>
            </CardHeader>
            <CardBody>
              <VStack spacing={3} align="stretch">
                {[5, 4, 3, 2, 1].map((rating) => {
                  // This would need actual data from the backend
                  const count = Math.floor(Math.random() * 10); // Placeholder
                  const percentage = summary.total_ratings > 0 ? (count / summary.total_ratings) * 100 : 0;
                  
                  return (
                    <HStack key={rating} spacing={3}>
                      <Text minW="20px">{rating}</Text>
                      <Icon as={FiStar} color="yellow.400" />
                      <Progress value={percentage} colorScheme="yellow" flex="1" />
                      <Text minW="40px" fontSize="sm">
                        {count} ({percentage.toFixed(0)}%)
                      </Text>
                    </HStack>
                  );
                })}
              </VStack>
            </CardBody>
          </Card>
        </VStack>
      )}

      {/* Ratings Tab */}
      {activeTab === 'ratings' && (
        <VStack spacing={4} align="stretch">
          {ratings.length === 0 ? (
            <Alert status="info" borderRadius="lg">
              <AlertIcon />
              <VStack align="start" spacing={2}>
                <Text fontWeight="semibold">No ratings yet</Text>
                <Text fontSize="sm">
                  Start rating recipes to build your cooking history and help other users!
                </Text>
                <Button size="sm" colorScheme="blue" variant="outline">
                  Browse Recipes
                </Button>
              </VStack>
            </Alert>
          ) : (
            ratings.map((rating) => (
              <Card key={rating.id}>
                <CardBody>
                  <VStack spacing={3} align="stretch">
                    <HStack justify="space-between">
                      <VStack align="start" spacing={1}>
                        <Text fontWeight="semibold" fontSize="lg">
                          {rating.recipe?.title || 'Unknown Recipe'}
                        </Text>
                        <HStack spacing={2}>
                          <Badge colorScheme="purple" size="sm">
                            {rating.recipe?.cuisine || 'Unknown'}
                          </Badge>
                          <Badge colorScheme="blue" size="sm">
                            {rating.recipe?.meal_type?.replace('_', ' ').toUpperCase() || 'Unknown'}
                          </Badge>
                          {rating.is_verified && (
                            <Badge colorScheme="green" size="sm" leftIcon={<Icon as={FiCheck} />}>
                              Verified
                            </Badge>
                          )}
                        </HStack>
                      </VStack>
                      
                      <Menu>
                        <MenuButton as={Button} size="sm" variant="ghost">
                          <Icon as={FiMoreVertical} />
                        </MenuButton>
                        <MenuList>
                          <MenuItem icon={<Icon as={FiEdit} />} onClick={() => handleEditRating(rating)}>
                            Edit Rating
                          </MenuItem>
                          <MenuItem icon={<Icon as={FiEye} />} onClick={() => handleViewRecipe(rating.recipe_id)}>
                            View Recipe
                          </MenuItem>
                          <MenuItem 
                            icon={<Icon as={FiTrash2} />} 
                            onClick={() => handleDeleteRating(rating.id)}
                            color="red.500"
                          >
                            Delete Rating
                          </MenuItem>
                        </MenuList>
                      </Menu>
                    </HStack>

                    <HStack spacing={4}>
                      <VStack spacing={1}>
                        <Text fontSize="sm" fontWeight="medium">Overall</Text>
                        <StarRating rating={rating.rating} size="sm" showNumber={true} />
                      </VStack>
                      
                      {rating.difficulty_rating && (
                        <VStack spacing={1}>
                          <Text fontSize="sm" fontWeight="medium">Difficulty</Text>
                          <StarRating rating={rating.difficulty_rating} size="sm" showNumber={true} colorScheme="blue" />
                        </VStack>
                      )}
                      
                      {rating.taste_rating && (
                        <VStack spacing={1}>
                          <Text fontSize="sm" fontWeight="medium">Taste</Text>
                          <StarRating rating={rating.taste_rating} size="sm" showNumber={true} colorScheme="green" />
                        </VStack>
                      )}
                    </HStack>

                    {rating.review_text && (
                      <Box>
                        <Text fontSize="sm" color={textColor}>
                          "{rating.review_text}"
                        </Text>
                      </Box>
                    )}

                    <HStack justify="space-between" fontSize="xs" color={textColor}>
                      <Text>Rated on {formatDate(rating.created_at)}</Text>
                      {rating.would_make_again && (
                        <Badge colorScheme="purple" size="sm">
                          Would make again
                        </Badge>
                      )}
                    </HStack>
                  </VStack>
                </CardBody>
              </Card>
            ))
          )}
        </VStack>
      )}

      {/* Reviews Tab */}
      {activeTab === 'reviews' && (
        <VStack spacing={4} align="stretch">
          {reviews.length === 0 ? (
            <Alert status="info" borderRadius="lg">
              <AlertIcon />
              <VStack align="start" spacing={2}>
                <Text fontWeight="semibold">No reviews yet</Text>
                <Text fontSize="sm">
                  Write detailed reviews to help other users discover great recipes!
                </Text>
                <Button size="sm" colorScheme="green" variant="outline">
                  Browse Recipes
                </Button>
              </VStack>
            </Alert>
          ) : (
            reviews.map((review) => (
              <ReviewCard
                key={review.id}
                review={review}
                userRating={undefined} // Would need to fetch this
                onVoteHelpful={async () => {}} // Would implement this
                currentUserId="current-user" // Would get from auth
                isVoting={false}
              />
            ))
          )}
        </VStack>
      )}

      {/* Rating Form Modal */}
      {isOpen && selectedRating && (
        <RatingForm
          recipeId={selectedRating.recipe_id}
          recipeTitle={selectedRating.recipe?.title || 'Unknown Recipe'}
          existingRating={selectedRating}
          onRatingSubmit={handleRatingSubmit}
          onCancel={() => {
            onClose();
            setIsEditing(false);
            setSelectedRating(null);
          }}
        />
      )}
    </Box>
  );
};

export default UserRatingHistory;
