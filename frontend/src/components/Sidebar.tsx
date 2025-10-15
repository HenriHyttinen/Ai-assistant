import {
  Box,
  CloseButton,
  Flex,
  Icon,
  useColorModeValue,
  Text,
  VStack,
} from '@chakra-ui/react';
import type { IconType } from 'react-icons';
import {
  FiHome,
  FiTrendingUp,
  FiCompass,
  FiStar,
  FiSettings,
} from 'react-icons/fi';
import { Link as RouterLink } from 'react-router-dom';
import { useApp } from '../contexts/AppContext';

// Inline translation function to avoid module loading issues
const translations = {
  en: {
    dashboard: 'Dashboard',
    healthProfile: 'Health Profile',
    analytics: 'Analytics',
    goals: 'Goals',
    settings: 'Settings',
  },
  es: {
    dashboard: 'Panel de Control',
    healthProfile: 'Perfil de Salud',
    analytics: 'Analíticas',
    goals: 'Objetivos',
    settings: 'Configuración',
  },
  fr: {
    dashboard: 'Tableau de Bord',
    healthProfile: 'Profil de Santé',
    analytics: 'Analytiques',
    goals: 'Objectifs',
    settings: 'Paramètres',
  },
  de: {
    dashboard: 'Übersicht',
    healthProfile: 'Gesundheitsprofil',
    analytics: 'Analytik',
    goals: 'Ziele',
    settings: 'Einstellungen',
  },
};

const t = (key: keyof typeof translations.en, currentLang: string = 'en') => {
  return translations[currentLang as keyof typeof translations]?.[key] || translations.en[key] || key;
};

interface LinkItemProps {
  nameKey: string;
  icon: IconType;
  path: string;
}

const LinkItems: Array<LinkItemProps> = [
  { nameKey: 'dashboard', icon: FiHome, path: '/dashboard' },
  { nameKey: 'healthProfile', icon: FiTrendingUp, path: '/profile' },
  { nameKey: 'analytics', icon: FiCompass, path: '/analytics' },
  { nameKey: 'goals', icon: FiStar, path: '/goals' },
  { nameKey: 'settings', icon: FiSettings, path: '/settings' },
];

export default function Sidebar() {
  const { language } = useApp();
  
  return (
    <Box
      bg={useColorModeValue('white', 'gray.900')}
      borderRight="1px"
      borderRightColor={useColorModeValue('gray.200', 'gray.700')}
      w={{ base: 'full', md: 60 }}
      pos="fixed"
      h="calc(100vh - 60px)"
      top="60px"
      display={{ base: 'none', md: 'block' }}
      shadow="sm"
    >
      <Flex h="20" alignItems="center" mx="8" justifyContent="space-between">
        <Text fontSize="2xl" fontFamily="monospace" fontWeight="bold">
          NDL
        </Text>
        <CloseButton display={{ base: 'flex', md: 'none' }} />
      </Flex>
      <VStack spacing={2} align="stretch" px={4}>
        {LinkItems.map((link) => (
          <NavItem key={link.nameKey} icon={link.icon} path={link.path}>
            {t(link.nameKey as keyof typeof translations.en, language)}
          </NavItem>
        ))}
      </VStack>
    </Box>
  );
}

interface NavItemProps {
  icon: IconType;
  children: React.ReactNode;
  path: string;
}

const NavItem = ({ icon, children, path, ...rest }: NavItemProps) => {
  return (
    <RouterLink to={path} style={{ textDecoration: 'none' }}>
      <Flex
        align="center"
        p="4"
        mx="2"
        borderRadius="lg"
        role="group"
        cursor="pointer"
        _hover={{
          bg: 'cyan.400',
          color: 'white',
        }}
        {...rest}
      >
        {icon && (
          <Icon
            mr="4"
            fontSize="16"
            as={icon}
          />
        )}
        {children}
      </Flex>
    </RouterLink>
  );
}; 