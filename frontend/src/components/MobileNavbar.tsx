import React from 'react';
import {
  Box,
  Flex,
  Text,
  IconButton,
  Button,
  useColorModeValue,
  useBreakpointValue,
  Avatar,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  MenuDivider,
  HStack,
  VStack,
  Badge,
  useDisclosure,
} from '@chakra-ui/react';
import { HamburgerIcon } from '@chakra-ui/icons';
import { FiActivity, FiList, FiCoffee, FiStar, FiSettings, FiAward, FiHome, FiTrendingUp } from 'react-icons/fi';
import { useSupabaseAuth } from '../contexts/SupabaseAuthContext';
import { useApp } from '../contexts/AppContext';
import { t } from '../utils/translations';
import { useNavigate } from 'react-router-dom';

interface MobileNavbarProps {
  onMenuOpen: () => void;
}

const MobileNavbar: React.FC<MobileNavbarProps> = ({ onMenuOpen }) => {
  const { user, signOut } = useSupabaseAuth();
  const { language } = useApp();
  const navigate = useNavigate();
  const isMobile = useBreakpointValue({ base: true, md: false });
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  const handleLogout = async () => {
    try {
      const { error } = await signOut();
      if (error) {
        console.error('Logout error:', error);
      }
      // Navigate to login page
      navigate('/login');
      // Force page reload to clear any cached state
      window.location.href = '/login';
    } catch (err) {
      console.error('Logout failed:', err);
      // Still navigate to login even if there's an error
      navigate('/login');
      window.location.href = '/login';
    }
  };

  if (!isMobile) return null;

  return (
    <Box
      bg={bgColor}
      px={4}
      py={3}
      borderBottom="1px"
      borderBottomColor={borderColor}
      position="fixed"
      top={0}
      left={0}
      right={0}
      zIndex={1000}
    >
      <Flex justify="space-between" align="center">
        {/* Left side - Menu button and title */}
        <HStack spacing={3}>
          <IconButton
            aria-label="Open menu"
            icon={<HamburgerIcon />}
            variant="ghost"
            size="sm"
            onClick={onMenuOpen}
          />
          <Text fontSize="lg" fontWeight="bold" color={textColor}>
            Numbers Don't Lie
          </Text>
        </HStack>

        {/* Right side - User menu */}
        <HStack spacing={2}>
          {user && (
            <Menu>
              <MenuButton
                as={Button}
                variant="ghost"
                size="sm"
                p={0}
                minW="auto"
              >
                <Avatar
                  size="sm"
                  name={user.email}
                  src={user.user_metadata?.avatar_url}
                />
              </MenuButton>
              <MenuList>
                <VStack align="start" p={3} spacing={1}>
                  <Text fontSize="sm" fontWeight="bold">
                    {user.user_metadata?.full_name || user.email}
                  </Text>
                  <Text fontSize="xs" color="gray.500">
                    {user.email}
                  </Text>
                </VStack>
                <MenuDivider />
                <MenuItem icon={<FiHome />}>
                  {t('dashboard', language)}
                </MenuItem>
                <MenuItem icon={<FiTrendingUp />}>
                  {t('healthProfile', language)}
                </MenuItem>
                <MenuItem icon={<FiActivity />}>
                  {t('analytics', language)}
                </MenuItem>
                <MenuItem icon={<FiList />}>
                  {t('activityHistory', language)}
                </MenuItem>
                <MenuItem icon={<FiCoffee />}>
                  {t('nutrition', language)}
                </MenuItem>
                <MenuItem icon={<FiStar />}>
                  {t('goals', language)}
                </MenuItem>
                <MenuItem icon={<FiAward />}>
                  {t('achievements', language)}
                </MenuItem>
                <MenuItem icon={<FiSettings />}>
                  {t('settings', language)}
                </MenuItem>
                <MenuDivider />
                <MenuItem onClick={handleLogout} color="red.500">
                  {t('signOut', language)}
                </MenuItem>
              </MenuList>
            </Menu>
          )}
        </HStack>
      </Flex>
    </Box>
  );
};

export default MobileNavbar;







