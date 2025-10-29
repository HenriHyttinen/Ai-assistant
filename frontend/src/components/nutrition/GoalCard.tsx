import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Card,
  CardBody,
  CardHeader,
  Badge,
  Icon,
  Progress,
  Button,
  useColorModeValue,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useDisclosure,
  Tooltip,
  Divider
} from '@chakra-ui/react';
import { 
  FiTarget, 
  FiMoreVertical, 
  FiEdit, 
  FiPause, 
  FiPlay, 
  FiTrash2,
  FiTrendingUp,
  FiCalendar,
  FiAward,
  FiCheck
} from 'react-icons/fi';
import type { GoalProgressSummary } from '../../services/nutritionGoalsService';
import LogProgressModal from './LogProgressModal';
import GoalDetailsModal from './GoalDetailsModal';

interface GoalCardProps {
  goal: GoalProgressSummary;
  onUpdate: () => void;
}

const GoalCard: React.FC<GoalCardProps> = ({ goal, onUpdate }) => {
  const [isLoggingProgress, setIsLoggingProgress] = useState(false);
  const { isOpen: isDetailsOpen, onOpen: onDetailsOpen, onClose: onDetailsClose } = useDisclosure();
  const { isOpen: isLogOpen, onOpen: onLogOpen, onClose: onLogClose } = useDisclosure();

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.400');

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'green';
      case 'paused':
        return 'yellow';
      case 'completed':
        return 'blue';
      case 'cancelled':
        return 'red';
      default:
        return 'gray';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <Icon as={FiTarget} color="green.500" />;
      case 'paused':
        return <Icon as={FiPause} color="yellow.500" />;
      case 'completed':
        return <Icon as={FiCheck} color="blue.500" />;
      case 'cancelled':
        return <Icon as={FiTarget} color="red.500" />;
      default:
        return <Icon as={FiTarget} color="gray.500" />;
    }
  };

  const getGoalTypeIcon = (goalType: string) => {
    switch (goalType) {
      case 'calories':
        return <Icon as={FiTarget} color="orange.500" />;
      case 'protein':
        return <Icon as={FiTrendingUp} color="blue.500" />;
      case 'fiber':
        return <Icon as={FiTarget} color="green.500" />;
      case 'water':
        return <Icon as={FiTarget} color="cyan.500" />;
      case 'sodium':
        return <Icon as={FiTarget} color="purple.500" />;
      default:
        return <Icon as={FiTarget} color="gray.500" />;
    }
  };

  const getUnitDisplay = (unit: string) => {
    switch (unit) {
      case 'cal':
        return 'calories';
      case 'g':
        return 'grams';
      case 'mg':
        return 'milligrams';
      case 'oz':
        return 'ounces';
      case 'lbs':
        return 'pounds';
      default:
        return unit;
    }
  };

  const handleLogProgress = async () => {
    setIsLoggingProgress(true);
    onLogOpen();
  };

  const handleProgressLogged = () => {
    onLogClose();
    onUpdate();
  };

  const handleEdit = () => {
    onDetailsOpen();
  };

  const handlePause = () => {
    // TODO: Implement pause functionality
    console.log('Pause goal:', goal.goal_id);
  };

  const handleResume = () => {
    // TODO: Implement resume functionality
    console.log('Resume goal:', goal.goal_id);
  };

  const handleDelete = () => {
    // TODO: Implement delete functionality
    console.log('Delete goal:', goal.goal_id);
  };

  return (
    <>
      <Card bg={bgColor} borderColor={borderColor} position="relative">
        <CardHeader pb={2}>
          <HStack justify="space-between" align="start">
            <HStack spacing={3} flex="1">
              {getGoalTypeIcon(goal.goal_type)}
              <VStack align="start" spacing={1} flex="1">
                <Text fontWeight="semibold" fontSize="lg" noOfLines={1}>
                  {goal.goal_name}
                </Text>
                <HStack spacing={2}>
                  <Badge colorScheme={getStatusColor(goal.status)} size="sm">
                    {goal.status.toUpperCase()}
                  </Badge>
                  <Text fontSize="sm" color={textColor} textTransform="capitalize">
                    {goal.goal_type.replace('_', ' ')}
                  </Text>
                </HStack>
              </VStack>
            </HStack>
            
            <Menu>
              <MenuButton as={Button} variant="ghost" size="sm">
                <Icon as={FiMoreVertical} />
              </MenuButton>
              <MenuList>
                <MenuItem icon={<Icon as={FiEdit} />} onClick={handleEdit}>
                  Edit Goal
                </MenuItem>
                {goal.status === 'active' ? (
                  <MenuItem icon={<Icon as={FiPause} />} onClick={handlePause}>
                    Pause Goal
                  </MenuItem>
                ) : goal.status === 'paused' ? (
                  <MenuItem icon={<Icon as={FiPlay} />} onClick={handleResume}>
                    Resume Goal
                  </MenuItem>
                ) : null}
                <MenuItem icon={<Icon as={FiTrash2} />} onClick={handleDelete} color="red.500">
                  Delete Goal
                </MenuItem>
              </MenuList>
            </Menu>
          </HStack>
        </CardHeader>

        <CardBody pt={0}>
          <VStack spacing={4} align="stretch">
            {/* Progress Section */}
            <Box>
              <HStack justify="space-between" mb={2}>
                <Text fontSize="sm" fontWeight="semibold">Progress</Text>
                <Text fontSize="sm" color={textColor}>
                  {goal.progress_percentage.toFixed(0)}%
                </Text>
              </HStack>
              
              <Progress 
                value={goal.progress_percentage} 
                colorScheme={goal.is_on_track ? 'green' : 'yellow'}
                size="lg"
                borderRadius="full"
              />
              
              <HStack justify="space-between" mt={2}>
                <Text fontSize="sm" color={textColor}>
                  {goal.current_value.toFixed(0)} / {goal.target_value.toFixed(0)} {getUnitDisplay(goal.unit)}
                </Text>
                <HStack spacing={1}>
                  {goal.is_on_track ? (
                    <Tooltip label="On track">
                      <Icon as={FiCheck} color="green.500" />
                    </Tooltip>
                  ) : (
                    <Tooltip label="Behind schedule">
                      <Icon as={FiTarget} color="yellow.500" />
                    </Tooltip>
                  )}
                </HStack>
              </HStack>
            </Box>

            <Divider />

            {/* Stats Section */}
            <SimpleGrid columns={2} spacing={4}>
              <VStack spacing={1} align="center">
                <Text fontSize="sm" color={textColor}>Streak</Text>
                <Text fontWeight="bold" fontSize="lg">
                  {goal.streak_days}
                </Text>
                <Text fontSize="xs" color={textColor}>days</Text>
              </VStack>
              
              <VStack spacing={1} align="center">
                <Text fontSize="sm" color={textColor}>Days Left</Text>
                <Text fontWeight="bold" fontSize="lg">
                  {goal.days_remaining || '∞'}
                </Text>
                <Text fontSize="xs" color={textColor}>
                  {goal.days_remaining ? 'days' : 'ongoing'}
                </Text>
              </VStack>
            </SimpleGrid>

            {/* Next Milestone */}
            {goal.next_milestone && (
              <Box p={3} bg={useColorModeValue('gray.50', 'gray.700')} borderRadius="md">
                <HStack spacing={2} mb={1}>
                  <Icon as={FiAward} color="purple.500" />
                  <Text fontSize="sm" fontWeight="semibold">Next Milestone</Text>
                </HStack>
                <Text fontSize="sm" color={textColor}>
                  {goal.next_milestone.milestone_name}
                </Text>
                <Progress 
                  value={(goal.current_value / goal.next_milestone.target_value) * 100}
                  size="sm"
                  colorScheme="purple"
                  mt={2}
                />
              </Box>
            )}

            {/* Last Achieved */}
            {goal.last_achieved && (
              <HStack spacing={2}>
                <Icon as={FiCalendar} color="green.500" />
                <Text fontSize="sm" color={textColor}>
                  Last achieved: {new Date(goal.last_achieved).toLocaleDateString()}
                </Text>
              </HStack>
            )}

            {/* Action Buttons */}
            <HStack spacing={2}>
              <Button
                size="sm"
                colorScheme="blue"
                onClick={handleLogProgress}
                isLoading={isLoggingProgress}
                flex="1"
              >
                Log Progress
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={onDetailsOpen}
              >
                View Details
              </Button>
            </HStack>
          </VStack>
        </CardBody>
      </Card>

      {/* Modals */}
      <GoalDetailsModal
        isOpen={isDetailsOpen}
        onClose={onDetailsClose}
        goalId={goal.goal_id}
        onUpdate={onUpdate}
      />
      
      <LogProgressModal
        isOpen={isLogOpen}
        onClose={onLogClose}
        goalId={goal.goal_id}
        goalName={goal.goal_name}
        targetValue={goal.target_value}
        unit={goal.unit}
        onProgressLogged={handleProgressLogged}
      />
    </>
  );
};

export default GoalCard;
