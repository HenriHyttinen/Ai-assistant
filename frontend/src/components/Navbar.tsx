import {
  Box,
  Flex,
  Text,
  IconButton,
  Button,
  Stack,
  Collapse,
  Icon,
  Link,
  useColorModeValue,
  useBreakpointValue,
  useDisclosure,
  Avatar,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  MenuDivider,
  VStack,
} from '@chakra-ui/react';
import {
  HamburgerIcon,
  CloseIcon,
  ViewIcon,
  ArrowUpIcon,
  StarIcon,
  TriangleUpIcon,
  SettingsIcon,
} from '@chakra-ui/icons';
import { FiActivity, FiList, FiCoffee } from 'react-icons/fi';
import { useSupabaseAuth } from '../contexts/SupabaseAuthContext';
import { useApp, AppContext } from '../contexts/AppContext';
import { t } from '../utils/translations';
import { useContext } from 'react';

// Navigation items - same as in Sidebar
const LinkItems = [
  { nameKey: 'dashboard', icon: ViewIcon, path: '/dashboard' },
  { nameKey: 'healthProfile', icon: ArrowUpIcon, path: '/profile' },
  { nameKey: 'analytics', icon: FiActivity, path: '/analytics' },
  { nameKey: 'activityHistory', icon: FiList, path: '/activities' },
  { nameKey: 'nutrition', icon: FiCoffee, path: '/nutrition' },
  { nameKey: 'goals', icon: StarIcon, path: '/goals' },
  { nameKey: 'achievements', icon: TriangleUpIcon, path: '/achievements' },
  { nameKey: 'settings', icon: SettingsIcon, path: '/settings' },
];

export default function Navbar() {
  const { isOpen, onToggle } = useDisclosure();
  const { user, signOut } = useSupabaseAuth();
  const appContext = useContext(AppContext);
  
  // Safety check to prevent context errors during hot reload
  if (!appContext) {
    return null;
  }

  return (
    <Box position="fixed" w="full" zIndex={1000}>
      <Flex
        bg={useColorModeValue('white', 'gray.800')}
        color={useColorModeValue('gray.600', 'white')}
        minH={'60px'}
        py={{ base: 2 }}
        px={{ base: 4 }}
        borderBottom={1}
        borderStyle={'solid'}
        borderColor={useColorModeValue('gray.200', 'gray.900')}
        align={'center'}
        shadow="sm"
      >
        <Flex
          flex={{ base: 1, md: 'auto' }}
          ml={{ base: -2 }}
          display={{ base: 'flex', md: 'none' }}
        >
          <IconButton
            onClick={onToggle}
            icon={
              isOpen ? <CloseIcon w={3} h={3} /> : <HamburgerIcon w={5} h={5} />
            }
            variant={'ghost'}
            aria-label={'Toggle Navigation'}
          />
        </Flex>
        <Flex flex={{ base: 1 }} justify={{ base: 'center', md: 'start' }}>
          <Text
            textAlign={useBreakpointValue({ base: 'center', md: 'left' })}
            fontFamily={'heading'}
            color={useColorModeValue('gray.800', 'white')}
            fontWeight="bold"
            fontSize="xl"
          >
            Counting Calories
          </Text>

          <Flex display={{ base: 'none', md: 'flex' }} ml={10}>
            <DesktopNav />
          </Flex>
        </Flex>

        <Stack
          flex={{ base: 1, md: 0 }}
          justify={'flex-end'}
          direction={'row'}
          spacing={6}
        >
          <Menu>
            <MenuButton
              as={Button}
              rounded={'full'}
              variant={'link'}
              cursor={'pointer'}
              minW={0}
            >
              <Avatar
                size={'sm'}
                name={user?.email}
                src={user?.profile_picture}
              />
            </MenuButton>
            <MenuList zIndex={1001}>
              <MenuItem as={Link} href="/profile">
                Profile
              </MenuItem>
              <MenuItem as={Link} href="/settings">
                Settings
              </MenuItem>
              <MenuDivider />
              <MenuItem onClick={() => signOut()}>Logout</MenuItem>
            </MenuList>
          </Menu>
        </Stack>
      </Flex>

      <Collapse in={isOpen} animateOpacity>
        <Box
          bg={useColorModeValue('white', 'gray.800')}
          p={4}
          display={{ md: 'none' }}
          shadow="md"
        >
          <MobileNav />
        </Box>
      </Collapse>
    </Box>
  );
}

const DesktopNav = () => {
  // Desktop navigation is handled by the Sidebar component
  // This is just a placeholder for the navbar
  return null;
};


const MobileNav = () => {
  const appContext = useContext(AppContext);
  
  // Safety check to prevent context errors during hot reload
  if (!appContext) {
    return null;
  }
  
  const { language } = appContext;
  
  return (
    <VStack
      bg={useColorModeValue('white', 'gray.800')}
      p={4}
      display={{ md: 'none' }}
      spacing={2}
      align="stretch"
    >
      {LinkItems.map((link) => (
        <MobileNavItem 
          key={link.nameKey} 
          icon={link.icon} 
          path={link.path}
          label={t(link.nameKey as any, language)}
        />
      ))}
    </VStack>
  );
};

const MobileNavItem = ({ label, icon, path }: { label: string; icon: any; path: string }) => {
  return (
    <Flex
      py={2}
      as={Link}
      href={path}
      justify={'flex-start'}
      align={'center'}
      _hover={{
        textDecoration: 'none',
        bg: useColorModeValue('gray.100', 'gray.700'),
      }}
      px={3}
      borderRadius="md"
    >
      <Icon
        as={icon}
        w={5}
        h={5}
        mr={3}
        color={useColorModeValue('gray.600', 'gray.200')}
      />
      <Text
        fontWeight={600}
        color={useColorModeValue('gray.600', 'gray.200')}
      >
        {label}
      </Text>
    </Flex>
  );
};
