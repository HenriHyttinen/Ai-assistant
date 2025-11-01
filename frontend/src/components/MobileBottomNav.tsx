import React from 'react';
import {
  Box,
  HStack,
  IconButton,
  Text,
  useColorModeValue,
  useBreakpointValue,
  Badge,
} from '@chakra-ui/react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  FiHome,
  FiTrendingUp,
  FiActivity,
  FiCoffee,
  FiStar,
  FiAward,
  FiList,
  FiSettings,
} from 'react-icons/fi';

interface NavItem {
  key: string;
  icon: React.ElementType;
  label: string;
  path: string;
  badge?: number;
}

const MobileBottomNav: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const isMobile = useBreakpointValue({ base: true, md: false });
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const activeColor = useColorModeValue('blue.500', 'blue.300');
  const inactiveColor = useColorModeValue('gray.500', 'gray.400');

  const navItems: NavItem[] = [
    { key: 'dashboard', icon: FiHome, label: 'Dashboard', path: '/dashboard' },
    { key: 'nutrition', icon: FiCoffee, label: 'Nutrition', path: '/nutrition' },
    { key: 'goals', icon: FiStar, label: 'Goals', path: '/goals' },
    { key: 'activities', icon: FiActivity, label: 'Activities', path: '/activities' },
    { key: 'achievements', icon: FiAward, label: 'Achievements', path: '/achievements' },
  ];

  if (!isMobile) return null;

  return (
    <Box
      position="fixed"
      bottom={0}
      left={0}
      right={0}
      bg={bgColor}
      borderTop="1px"
      borderTopColor={borderColor}
      zIndex={1000}
      px={2}
      py={1}
    >
      <HStack justify="space-around" spacing={0}>
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;
          
          return (
            <Box key={item.key} position="relative">
              <IconButton
                aria-label={item.label}
                icon={<Icon />}
                variant="ghost"
                size="lg"
                color={isActive ? activeColor : inactiveColor}
                onClick={() => navigate(item.path)}
                _hover={{
                  bg: isActive ? 'blue.50' : 'gray.50',
                }}
                _active={{
                  bg: isActive ? 'blue.100' : 'gray.100',
                }}
              />
              <Text
                fontSize="xs"
                color={isActive ? activeColor : inactiveColor}
                textAlign="center"
                mt={1}
                fontWeight={isActive ? 'semibold' : 'normal'}
              >
                {item.label}
              </Text>
              {item.badge && item.badge > 0 && (
                <Badge
                  position="absolute"
                  top={1}
                  right={1}
                  colorScheme="red"
                  borderRadius="full"
                  fontSize="xs"
                  minW={5}
                  h={5}
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                >
                  {item.badge}
                </Badge>
              )}
            </Box>
          );
        })}
      </HStack>
    </Box>
  );
};

export default MobileBottomNav;







