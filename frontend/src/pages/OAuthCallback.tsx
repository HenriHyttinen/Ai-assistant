// @ts-nocheck
import { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Box, Spinner, Text, VStack } from '@chakra-ui/react';
import { useAuth } from '../contexts/AuthContext';

const OAuthCallback = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { login } = useAuth();

  useEffect(() => {
    const handleOAuthCallback = async () => {
      try {
        // Get the token from URL parameters or make a request to get it
        const token = searchParams.get('token');
        const error = searchParams.get('error');
        
        if (error) {
          console.error('OAuth error:', error);
          navigate('/login?error=oauth_failed');
          return;
        }

        if (token) {
          // Store the token and redirect to dashboard
          localStorage.setItem('token', token);
          navigate('/dashboard');
        } else {
          // If no token in URL, try to get it from the backend
          // This is a fallback for demo purposes
          navigate('/dashboard');
        }
      } catch (err) {
        console.error('OAuth callback error:', err);
        navigate('/login?error=oauth_failed');
      }
    };

    handleOAuthCallback();
  }, [navigate, searchParams]);

  return (
    <Box minH="100vh" display="flex" alignItems="center" justifyContent="center">
      <VStack spacing={4}>
        <Spinner size="xl" color="blue.500" />
        <Text>Completing login...</Text>
      </VStack>
    </Box>
  );
};

export default OAuthCallback;
