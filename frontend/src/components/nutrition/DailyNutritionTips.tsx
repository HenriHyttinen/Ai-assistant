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
  Badge,
  Image,
  useColorModeValue,
  useBreakpointValue,
  Icon,
  SimpleGrid,
  useToast,
  Spinner,
  Center,
  Flex,
  Divider,
  IconButton,
} from '@chakra-ui/react';
import {
  FiLightbulb, FiStar, FiHeart, FiShare2, FiBookmark,
  FiArrowLeft, FiArrowRight, FiRefreshCw, FiTarget
} from 'react-icons/fi';

interface NutritionTip {
  id: number;
  title: string;
  content: string;
  category: string;
  difficulty_level: string;
  tip_type?: string;
  target_goals?: string[];
  target_dietary_restrictions?: string[];
  image_url?: string;
  icon_name?: string;
  view_count: number;
  like_count: number;
  is_featured: boolean;
  created_at: string;
  updated_at: string;
}

const DailyNutritionTips: React.FC = () => {
  const [dailyTip, setDailyTip] = useState<NutritionTip | null>(null);
  const [allTips, setAllTips] = useState<NutritionTip[]>([]);
  const [loading, setLoading] = useState(true);
  const [currentTipIndex, setCurrentTipIndex] = useState(0);
  const [likedTips, setLikedTips] = useState<Set<number>>(new Set());
  const [bookmarkedTips, setBookmarkedTips] = useState<Set<number>>(new Set());
  
  const toast = useToast();
  const isMobile = useBreakpointValue({ base: true, md: false });
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  useEffect(() => {
    loadDailyTip();
    loadAllTips();
  }, []);

  const loadDailyTip = async () => {
    try {
      const response = await fetch('/api/nutrition-education/tips/daily', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDailyTip(data);
      } else {
        throw new Error('Failed to load daily tip');
      }
    } catch (error) {
      console.error('Error loading daily tip:', error);
    }
  };

  const loadAllTips = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/nutrition-education/tips?limit=50', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setAllTips(data);
      } else {
        throw new Error('Failed to load tips');
      }
    } catch (error) {
      console.error('Error loading tips:', error);
      toast({
        title: 'Error',
        description: 'Failed to load nutrition tips',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleLike = async (tipId: number) => {
    const isLiked = likedTips.has(tipId);
    const newLikedTips = new Set(likedTips);
    
    if (isLiked) {
      newLikedTips.delete(tipId);
    } else {
      newLikedTips.add(tipId);
    }
    
    setLikedTips(newLikedTips);
    
    // Update the tip's like count
    setAllTips(prev => prev.map(tip => 
      tip.id === tipId 
        ? { ...tip, like_count: tip.like_count + (isLiked ? -1 : 1) }
        : tip
    ));
    
    toast({
      title: isLiked ? 'Tip unliked' : 'Tip liked!',
      status: 'success',
      duration: 2000,
      isClosable: true,
    });
  };

  const handleBookmark = async (tipId: number) => {
    const isBookmarked = bookmarkedTips.has(tipId);
    const newBookmarkedTips = new Set(bookmarkedTips);
    
    if (isBookmarked) {
      newBookmarkedTips.delete(tipId);
    } else {
      newBookmarkedTips.add(tipId);
    }
    
    setBookmarkedTips(newBookmarkedTips);
    
    toast({
      title: isBookmarked ? 'Removed from bookmarks' : 'Added to bookmarks!',
      status: 'success',
      duration: 2000,
      isClosable: true,
    });
  };

  const handleShare = (tip: NutritionTip) => {
    if (navigator.share) {
      navigator.share({
        title: tip.title,
        text: tip.content,
        url: window.location.href,
      });
    } else {
      // Fallback to copying to clipboard
      navigator.clipboard.writeText(`${tip.title}\n\n${tip.content}`);
      toast({
        title: 'Tip copied to clipboard',
        status: 'success',
        duration: 2000,
        isClosable: true,
      });
    }
  };

  const getCategoryColor = (category: string) => {
    const colors = {
      macronutrients: 'blue',
      micronutrients: 'purple',
      weight_management: 'orange',
      sports_nutrition: 'green',
      medical_nutrition: 'red',
      cooking_tips: 'pink',
      meal_planning: 'teal',
      food_safety: 'yellow',
      sustainable_eating: 'cyan',
      cultural_nutrition: 'indigo',
    };
    return colors[category as keyof typeof colors] || 'gray';
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'green';
      case 'intermediate': return 'yellow';
      case 'advanced': return 'red';
      default: return 'gray';
    }
  };

  const currentTip = allTips[currentTipIndex];

  if (loading) {
    return (
      <Center h="400px">
        <Spinner size="xl" />
      </Center>
    );
  }

  return (
    <VStack spacing={6} align="stretch" p={4}>
      {/* Header */}
      <HStack justify="space-between" align="center">
        <Text fontSize="2xl" fontWeight="bold">
          Nutrition Tips
        </Text>
        <Button
          size="sm"
          variant="outline"
          leftIcon={<Icon as={FiRefreshCw} />}
          onClick={loadAllTips}
        >
          Refresh
        </Button>
      </HStack>

      {/* Daily Tip */}
      {dailyTip && (
        <Card bg={bgColor} borderColor={borderColor} borderWidth={2}>
          <CardHeader>
            <HStack>
              <Icon as={FiLightbulb} color="yellow.500" boxSize={6} />
              <Text fontWeight="bold" fontSize="lg">
                Today's Tip
              </Text>
              <Badge colorScheme="yellow" variant="solid">
                Daily
              </Badge>
            </HStack>
          </CardHeader>
          <CardBody pt={0}>
            <VStack spacing={4} align="stretch">
              <Text fontSize="xl" fontWeight="semibold">
                {dailyTip.title}
              </Text>
              <Text fontSize="md" color={textColor} lineHeight="1.6">
                {dailyTip.content}
              </Text>
              
              <HStack spacing={2} flexWrap="wrap">
                <Badge
                  colorScheme={getCategoryColor(dailyTip.category)}
                  variant="subtle"
                >
                  {dailyTip.category.replace('_', ' ').toUpperCase()}
                </Badge>
                <Badge
                  colorScheme={getDifficultyColor(dailyTip.difficulty_level)}
                  variant="subtle"
                >
                  {dailyTip.difficulty_level.toUpperCase()}
                </Badge>
                {dailyTip.tip_type && (
                  <Badge colorScheme="blue" variant="outline">
                    {dailyTip.tip_type}
                  </Badge>
                )}
              </HStack>

              <HStack justify="space-between" align="center">
                <HStack spacing={4}>
                  <HStack spacing={1}>
                    <Icon as={FiStar} boxSize={4} color="yellow.500" />
                    <Text fontSize="sm" color={textColor}>
                      {dailyTip.like_count}
                    </Text>
                  </HStack>
                  <HStack spacing={1}>
                    <Icon as={FiTarget} boxSize={4} color="blue.500" />
                    <Text fontSize="sm" color={textColor}>
                      {dailyTip.view_count} views
                    </Text>
                  </HStack>
                </HStack>

                <HStack spacing={2}>
                  <IconButton
                    aria-label="Like tip"
                    icon={<Icon as={FiHeart} />}
                    size="sm"
                    variant="ghost"
                    colorScheme="red"
                    onClick={() => handleLike(dailyTip.id)}
                  />
                  <IconButton
                    aria-label="Bookmark tip"
                    icon={<Icon as={FiBookmark} />}
                    size="sm"
                    variant="ghost"
                    colorScheme="blue"
                    onClick={() => handleBookmark(dailyTip.id)}
                  />
                  <IconButton
                    aria-label="Share tip"
                    icon={<Icon as={FiShare2} />}
                    size="sm"
                    variant="ghost"
                    colorScheme="green"
                    onClick={() => handleShare(dailyTip)}
                  />
                </HStack>
              </HStack>
            </VStack>
          </CardBody>
        </Card>
      )}

      {/* All Tips */}
      {allTips.length > 0 && (
        <Card bg={bgColor} borderColor={borderColor}>
          <CardHeader>
            <HStack justify="space-between">
              <Text fontWeight="semibold">
                More Tips ({allTips.length})
              </Text>
              <HStack spacing={2}>
                <IconButton
                  aria-label="Previous tip"
                  icon={<Icon as={FiArrowLeft} />}
                  size="sm"
                  variant="outline"
                  isDisabled={currentTipIndex === 0}
                  onClick={() => setCurrentTipIndex(prev => Math.max(0, prev - 1))}
                />
                <Text fontSize="sm" color={textColor}>
                  {currentTipIndex + 1} of {allTips.length}
                </Text>
                <IconButton
                  aria-label="Next tip"
                  icon={<Icon as={FiArrowRight} />}
                  size="sm"
                  variant="outline"
                  isDisabled={currentTipIndex === allTips.length - 1}
                  onClick={() => setCurrentTipIndex(prev => Math.min(allTips.length - 1, prev + 1))}
                />
              </HStack>
            </HStack>
          </CardHeader>
          <CardBody pt={0}>
            {currentTip && (
              <VStack spacing={4} align="stretch">
                <HStack justify="space-between" align="start">
                  <VStack align="start" spacing={2} flex={1}>
                    <Text fontSize="lg" fontWeight="semibold">
                      {currentTip.title}
                    </Text>
                    <Text fontSize="md" color={textColor} lineHeight="1.6">
                      {currentTip.content}
                    </Text>
                  </VStack>
                  {currentTip.image_url && (
                    <Image
                      src={currentTip.image_url}
                      alt={currentTip.title}
                      boxSize="100px"
                      objectFit="cover"
                      borderRadius="md"
                      ml={4}
                    />
                  )}
                </HStack>

                <HStack spacing={2} flexWrap="wrap">
                  <Badge
                    colorScheme={getCategoryColor(currentTip.category)}
                    variant="subtle"
                  >
                    {currentTip.category.replace('_', ' ').toUpperCase()}
                  </Badge>
                  <Badge
                    colorScheme={getDifficultyColor(currentTip.difficulty_level)}
                    variant="subtle"
                  >
                    {currentTip.difficulty_level.toUpperCase()}
                  </Badge>
                  {currentTip.tip_type && (
                    <Badge colorScheme="blue" variant="outline">
                      {currentTip.tip_type}
                    </Badge>
                  )}
                  {currentTip.is_featured && (
                    <Badge colorScheme="yellow" variant="solid">
                      Featured
                    </Badge>
                  )}
                </HStack>

                <HStack justify="space-between" align="center">
                  <HStack spacing={4}>
                    <HStack spacing={1}>
                      <Icon as={FiStar} boxSize={4} color="yellow.500" />
                      <Text fontSize="sm" color={textColor}>
                        {currentTip.like_count}
                      </Text>
                    </HStack>
                    <HStack spacing={1}>
                      <Icon as={FiTarget} boxSize={4} color="blue.500" />
                      <Text fontSize="sm" color={textColor}>
                        {currentTip.view_count} views
                      </Text>
                    </HStack>
                  </HStack>

                  <HStack spacing={2}>
                    <IconButton
                      aria-label="Like tip"
                      icon={<Icon as={FiHeart} />}
                      size="sm"
                      variant="ghost"
                      colorScheme="red"
                      color={likedTips.has(currentTip.id) ? 'red.500' : undefined}
                      onClick={() => handleLike(currentTip.id)}
                    />
                    <IconButton
                      aria-label="Bookmark tip"
                      icon={<Icon as={FiBookmark} />}
                      size="sm"
                      variant="ghost"
                      colorScheme="blue"
                      color={bookmarkedTips.has(currentTip.id) ? 'blue.500' : undefined}
                      onClick={() => handleBookmark(currentTip.id)}
                    />
                    <IconButton
                      aria-label="Share tip"
                      icon={<Icon as={FiShare2} />}
                      size="sm"
                      variant="ghost"
                      colorScheme="green"
                      onClick={() => handleShare(currentTip)}
                    />
                  </HStack>
                </HStack>
              </VStack>
            )}
          </CardBody>
        </Card>
      )}

      {/* No Tips Message */}
      {!loading && allTips.length === 0 && (
        <Center h="200px">
          <VStack spacing={3}>
            <Icon as={FiLightbulb} boxSize={12} color="gray.400" />
            <Text color={textColor}>No tips available</Text>
            <Text fontSize="sm" color={textColor}>
              Check back later for new nutrition tips
            </Text>
          </VStack>
        </Center>
      )}
    </VStack>
  );
};

export default DailyNutritionTips;







