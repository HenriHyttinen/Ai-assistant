import { Box, Container, Flex, useColorModeValue } from '@chakra-ui/react';
import { Outlet } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import AchievementNotification from '../components/AchievementNotification';
const MainLayout = () => {
  const bgColor = useColorModeValue('gray.50', 'gray.900');

  return (
    <Box minH="100vh" bg={bgColor}>
        <Navbar />
        <Flex pt="60px">
          <Sidebar />
          <Box
            flex="1"
            ml={{ base: 0, md: 60 }}
            minH="calc(100vh - 60px)"
            bg={bgColor}
          >
            <Container maxW="container.xl" py={8} px={{ base: 4, md: 8 }}>
              <Outlet />
            </Container>
          </Box>
        </Flex>
        <AchievementNotification />
      </Box>
  );
};

export default MainLayout; 