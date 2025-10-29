import React, { useState } from 'react';
import {
  Box,
  Flex,
  useDisclosure,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  IconButton,
  useBreakpointValue,
  VStack,
  Text,
  Divider,
  useColorModeValue,
  Container,
} from '@chakra-ui/react';
import { HamburgerIcon } from '@chakra-ui/icons';
import { Outlet, useLocation } from 'react-router-dom';
import Navbar from './Navbar';
import Sidebar from './Sidebar';
import AchievementNotification from './AchievementNotification';

const MobileLayout: React.FC = () => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const location = useLocation();
  const isMobile = useBreakpointValue({ base: true, md: false });
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const sidebarBg = useColorModeValue('white', 'gray.900');
  const borderColor = useColorModeValue('gray.200', 'gray.700');

  // Close drawer when route changes
  React.useEffect(() => {
    onClose();
  }, [location.pathname, onClose]);

  return (
    <Box minH="100vh" bg={bgColor}>
      <Navbar />
      
      <Flex pt="60px">
        {/* Desktop Sidebar */}
        {!isMobile && (
          <Box
            w="250px"
            h="calc(100vh - 60px)"
            bg={sidebarBg}
            borderRight="1px"
            borderRightColor={borderColor}
            position="fixed"
            left={0}
            top="60px"
            zIndex={1}
          >
            <Sidebar />
          </Box>
        )}

        {/* Mobile Drawer */}
        {isMobile && (
          <Drawer isOpen={isOpen} onClose={onClose} placement="left" size="xs">
            <DrawerOverlay />
            <DrawerContent>
              <DrawerCloseButton />
              <DrawerHeader>
                <Text fontSize="lg" fontWeight="bold">
                  Navigation
                </Text>
              </DrawerHeader>
              <DrawerBody p={0}>
                <Sidebar />
              </DrawerBody>
            </DrawerContent>
          </Drawer>
        )}

        {/* Main Content */}
        <Box
          flex="1"
          ml={{ base: 0, md: '250px' }}
          minH="calc(100vh - 60px)"
          bg={bgColor}
        >
          <Container 
            maxW="container.xl" 
            py={{ base: 4, md: 8 }} 
            px={{ base: 2, md: 8 }}
          >
            <Outlet />
          </Container>
        </Box>
      </Flex>

      <AchievementNotification />
    </Box>
  );
};

export default MobileLayout;


