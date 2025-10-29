import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Card,
  CardBody,
  Heading,
  Badge,
  SimpleGrid,
  Spinner,
  Alert,
  AlertIcon,
  Icon,
  Link,
} from '@chakra-ui/react';
import { FiSettings, FiExternalLink } from 'react-icons/fi';

interface NutritionPreferencesSummaryProps {
  onLoad: () => Promise<any>;
}

const NutritionPreferencesSummary: React.FC<NutritionPreferencesSummaryProps> = ({
  onLoad,
}) => {
  const [preferences, setPreferences] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPreferences();
  }, []);

  const loadPreferences = async () => {
    setLoading(true);
    setError(null);
    try {
      const prefs = await onLoad();
      setPreferences(prefs);
    } catch (err) {
      setError('Failed to load nutrition preferences');
      console.error('Error loading nutrition preferences:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Card>
        <CardBody>
          <HStack justify="center">
            <Spinner size="sm" />
            <Text>Loading nutrition preferences...</Text>
          </HStack>
        </CardBody>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardBody>
          <Alert status="error">
            <AlertIcon />
            <Text>{error}</Text>
          </Alert>
        </CardBody>
      </Card>
    );
  }

  if (!preferences) {
    return (
      <Card>
        <CardBody>
          <VStack spacing={4}>
            <HStack>
              <Icon as={FiSettings} />
              <Heading size="md">Nutrition Preferences</Heading>
            </HStack>
            <Text color="gray.600" textAlign="center">
              No nutrition preferences configured yet.
            </Text>
            <Button
              as={Link}
              href="/nutrition"
              colorScheme="blue"
              variant="outline"
              rightIcon={<FiExternalLink />}
            >
              Set Up Nutrition Preferences
            </Button>
          </VStack>
        </CardBody>
      </Card>
    );
  }

  return (
    <Card>
      <CardBody>
        <VStack spacing={4} align="stretch">
          <HStack justify="space-between">
            <HStack>
              <Icon as={FiSettings} />
              <Heading size="md">Nutrition Preferences</Heading>
              <Badge colorScheme="green" variant="subtle">
                Configured
              </Badge>
            </HStack>
            <Button
              as={Link}
              href="/nutrition"
              size="sm"
              variant="outline"
              rightIcon={<FiExternalLink />}
            >
              Manage
            </Button>
          </HStack>

          <SimpleGrid columns={2} spacing={4}>
            <Box>
              <Text fontWeight="semibold" mb={2}>Daily Targets</Text>
              <VStack spacing={1} align="stretch">
                <Text fontSize="sm">
                  <Text as="span" fontWeight="medium">Calories:</Text> {preferences.daily_calorie_target || 'Not set'}
                </Text>
                <Text fontSize="sm">
                  <Text as="span" fontWeight="medium">Protein:</Text> {preferences.protein_target || 'Not set'}g
                </Text>
                <Text fontSize="sm">
                  <Text as="span" fontWeight="medium">Carbs:</Text> {preferences.carbs_target || 'Not set'}g
                </Text>
                <Text fontSize="sm">
                  <Text as="span" fontWeight="medium">Fats:</Text> {preferences.fats_target || 'Not set'}g
                </Text>
              </VStack>
            </Box>

            <Box>
              <Text fontWeight="semibold" mb={2}>Dietary Preferences</Text>
              <VStack spacing={1} align="stretch">
                {preferences.dietary_preferences && preferences.dietary_preferences.length > 0 ? (
                  <HStack wrap="wrap" spacing={1}>
                    {preferences.dietary_preferences.slice(0, 3).map((pref: string) => (
                      <Badge key={pref} colorScheme="blue" variant="subtle" fontSize="xs">
                        {pref.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </Badge>
                    ))}
                    {preferences.dietary_preferences.length > 3 && (
                      <Text fontSize="xs" color="gray.500">
                        +{preferences.dietary_preferences.length - 3} more
                      </Text>
                    )}
                  </HStack>
                ) : (
                  <Text fontSize="sm" color="gray.500">None selected</Text>
                )}
              </VStack>

              <Text fontWeight="semibold" mb={2} mt={3}>Allergies</Text>
              <VStack spacing={1} align="stretch">
                {preferences.allergies && preferences.allergies.length > 0 ? (
                  <HStack wrap="wrap" spacing={1}>
                    {preferences.allergies.slice(0, 3).map((allergy: string) => (
                      <Badge key={allergy} colorScheme="red" variant="subtle" fontSize="xs">
                        {allergy.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </Badge>
                    ))}
                    {preferences.allergies.length > 3 && (
                      <Text fontSize="xs" color="gray.500">
                        +{preferences.allergies.length - 3} more
                      </Text>
                    )}
                  </HStack>
                ) : (
                  <Text fontSize="sm" color="gray.500">None selected</Text>
                )}
              </VStack>
            </Box>
          </SimpleGrid>
        </VStack>
      </CardBody>
    </Card>
  );
};

export default NutritionPreferencesSummary;


