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
  Input,
  Select,
  InputGroup,
  InputLeftElement,
  SimpleGrid,
  useToast,
  Spinner,
  Center,
  Link,
  Flex,
  Collapse,
  Divider,
} from '@chakra-ui/react';
import {
  FiSearch, FiFilter, FiClock, FiStar, FiBookOpen, FiEye,
  FiChevronDown, FiChevronUp, FiArrowRight, FiBookmark
} from 'react-icons/fi';
import { useNavigate } from 'react-router-dom';

interface Article {
  id: number;
  title: string;
  slug: string;
  summary: string;
  content: string;
  content_type: string;
  category: string;
  difficulty_level: string;
  reading_time_minutes: number;
  featured_image_url?: string;
  tags: string[];
  author?: string;
  view_count: number;
  like_count: number;
  bookmark_count: number;
  is_featured: boolean;
  created_at: string;
  updated_at: string;
}

const NutritionArticles: React.FC = () => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedDifficulty, setSelectedDifficulty] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  
  const navigate = useNavigate();
  const toast = useToast();
  const isMobile = useBreakpointValue({ base: true, md: false });
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  const categories = [
    'macronutrients', 'micronutrients', 'weight_management', 'sports_nutrition',
    'medical_nutrition', 'cooking_tips', 'meal_planning', 'food_safety',
    'sustainable_eating', 'cultural_nutrition'
  ];

  const difficultyLevels = ['beginner', 'intermediate', 'advanced'];

  useEffect(() => {
    loadArticles();
  }, [searchTerm, selectedCategory, selectedDifficulty, page]);

  const loadArticles = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        limit: '20',
        offset: ((page - 1) * 20).toString(),
      });

      if (searchTerm) params.append('query', searchTerm);
      if (selectedCategory) params.append('category', selectedCategory);
      if (selectedDifficulty) params.append('difficulty_level', selectedDifficulty);

      const response = await fetch(`/api/nutrition-education/articles?${params}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('supabase_token')}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (page === 1) {
          setArticles(data);
        } else {
          setArticles(prev => [...prev, ...data]);
        }
        setHasMore(data.length === 20);
      } else {
        throw new Error('Failed to load articles');
      }
    } catch (error) {
      console.error('Error loading articles:', error);
      toast({
        title: 'Error',
        description: 'Failed to load articles',
        status: 'error',
        duration: 3000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setPage(1);
    loadArticles();
  };

  const handleLoadMore = () => {
    setPage(prev => prev + 1);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'green';
      case 'intermediate': return 'yellow';
      case 'advanced': return 'red';
      default: return 'gray';
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

  return (
    <VStack spacing={6} align="stretch" p={4}>
      {/* Header */}
      <HStack justify="space-between" align="center">
        <Text fontSize="2xl" fontWeight="bold">
          Nutrition Articles
        </Text>
        <Button
          size="sm"
          variant="outline"
          leftIcon={<FiFilter />}
          onClick={() => setShowFilters(!showFilters)}
        >
          Filters
        </Button>
      </HStack>

      {/* Search and Filters */}
      <VStack spacing={4} align="stretch">
        <InputGroup>
          <InputLeftElement>
            <Icon as={FiSearch} color="gray.400" />
          </InputLeftElement>
          <Input
            placeholder="Search articles..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
        </InputGroup>

        <Collapse in={showFilters}>
          <Card bg={bgColor} borderColor={borderColor}>
            <CardBody>
              <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
                <Select
                  placeholder="Select category"
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                >
                  {categories.map(category => (
                    <option key={category} value={category}>
                      {category.replace('_', ' ').toUpperCase()}
                    </option>
                  ))}
                </Select>

                <Select
                  placeholder="Select difficulty"
                  value={selectedDifficulty}
                  onChange={(e) => setSelectedDifficulty(e.target.value)}
                >
                  {difficultyLevels.map(level => (
                    <option key={level} value={level}>
                      {level.charAt(0).toUpperCase() + level.slice(1)}
                    </option>
                  ))}
                </Select>
              </SimpleGrid>
            </CardBody>
          </Card>
        </Collapse>

        <Button
          colorScheme="blue"
          onClick={handleSearch}
          isLoading={loading}
          loadingText="Searching..."
        >
          Search Articles
        </Button>
      </VStack>

      {/* Articles List */}
      {loading && articles.length === 0 ? (
        <Center h="400px">
          <Spinner size="xl" />
        </Center>
      ) : (
        <VStack spacing={4} align="stretch">
          {articles.map((article) => (
            <Card
              key={article.id}
              bg={bgColor}
              borderColor={borderColor}
              _hover={{ transform: 'translateY(-2px)', boxShadow: 'lg' }}
              transition="all 0.2s"
            >
              <CardBody p={6}>
                <VStack spacing={4} align="stretch">
                  {/* Article Header */}
                  <HStack justify="space-between" align="start">
                    <VStack align="start" spacing={2} flex={1}>
                      <HStack spacing={2}>
                        <Text fontSize="xl" fontWeight="bold" noOfLines={2}>
                          {article.title}
                        </Text>
                        {article.is_featured && (
                          <Badge colorScheme="yellow" variant="solid">
                            Featured
                          </Badge>
                        )}
                      </HStack>
                      <Text fontSize="md" color={textColor} noOfLines={3}>
                        {article.summary}
                      </Text>
                    </VStack>
                    {article.featured_image_url && (
                      <Image
                        src={article.featured_image_url}
                        alt={article.title}
                        boxSize="120px"
                        objectFit="cover"
                        borderRadius="md"
                        ml={4}
                      />
                    )}
                  </HStack>

                  {/* Article Metadata */}
                  <HStack spacing={4} flexWrap="wrap">
                    <Badge
                      colorScheme={getCategoryColor(article.category)}
                      variant="subtle"
                    >
                      {article.category.replace('_', ' ').toUpperCase()}
                    </Badge>
                    <Badge
                      colorScheme={getDifficultyColor(article.difficulty_level)}
                      variant="subtle"
                    >
                      {article.difficulty_level.toUpperCase()}
                    </Badge>
                    <HStack spacing={1}>
                      <Icon as={FiClock} boxSize={4} color={textColor} />
                      <Text fontSize="sm" color={textColor}>
                        {article.reading_time_minutes} min read
                      </Text>
                    </HStack>
                    <HStack spacing={1}>
                      <Icon as={FiEye} boxSize={4} color={textColor} />
                      <Text fontSize="sm" color={textColor}>
                        {article.view_count} views
                      </Text>
                    </HStack>
                  </HStack>

                  {/* Tags */}
                  {article.tags && article.tags.length > 0 && (
                    <HStack spacing={2} flexWrap="wrap">
                      {article.tags.slice(0, 5).map((tag) => (
                        <Badge key={tag} size="sm" variant="outline">
                          {tag}
                        </Badge>
                      ))}
                      {article.tags.length > 5 && (
                        <Text fontSize="sm" color={textColor}>
                          +{article.tags.length - 5} more
                        </Text>
                      )}
                    </HStack>
                  )}

                  {/* Article Stats */}
                  <HStack justify="space-between" align="center">
                    <HStack spacing={4}>
                      <HStack spacing={1}>
                        <Icon as={FiStar} boxSize={4} color="yellow.500" />
                        <Text fontSize="sm" color={textColor}>
                          {article.like_count}
                        </Text>
                      </HStack>
                      <HStack spacing={1}>
                        <Icon as={FiBookmark} boxSize={4} color="blue.500" />
                        <Text fontSize="sm" color={textColor}>
                          {article.bookmark_count}
                        </Text>
                      </HStack>
                    </HStack>

                    <HStack spacing={2}>
                      <Button
                        size="sm"
                        variant="outline"
                        leftIcon={<Icon as={FiBookmark} />}
                      >
                        Save
                      </Button>
                      <Button
                        size="sm"
                        colorScheme="blue"
                        rightIcon={<Icon as={FiArrowRight} />}
                        onClick={() => navigate(`/nutrition/education/articles/${article.slug}`)}
                      >
                        Read Article
                      </Button>
                    </HStack>
                  </HStack>

                  {/* Author and Date */}
                  {(article.author || article.created_at) && (
                    <HStack justify="space-between" align="center" pt={2} borderTop="1px" borderColor={borderColor}>
                      {article.author && (
                        <Text fontSize="sm" color={textColor}>
                          By {article.author}
                        </Text>
                      )}
                      <Text fontSize="sm" color={textColor}>
                        {new Date(article.created_at).toLocaleDateString()}
                      </Text>
                    </HStack>
                  )}
                </VStack>
              </CardBody>
            </Card>
          ))}

          {/* Load More Button */}
          {hasMore && (
            <Center pt={4}>
              <Button
                onClick={handleLoadMore}
                isLoading={loading}
                loadingText="Loading more..."
                variant="outline"
              >
                Load More Articles
              </Button>
            </Center>
          )}

          {/* No Articles Message */}
          {!loading && articles.length === 0 && (
            <Center h="200px">
              <VStack spacing={3}>
                <Icon as={FiBookOpen} boxSize={12} color="gray.400" />
                <Text color={textColor}>No articles found</Text>
                <Text fontSize="sm" color={textColor}>
                  Try adjusting your search terms or filters
                </Text>
              </VStack>
            </Center>
          )}
        </VStack>
      )}
    </VStack>
  );
};

export default NutritionArticles;







