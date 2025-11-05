// @ts-nocheck
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Spinner, Text, VStack, Button } from '@chakra-ui/react';
import { supabase } from '../lib/supabase';

const OAuthCallback = () => {
  const navigate = useNavigate();
  const [isProcessing, setIsProcessing] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [debugInfo, setDebugInfo] = useState<string>('');

  useEffect(() => {
    const handleOAuthCallback = async () => {
      try {
        console.log('Processing OAuth callback...');
        setDebugInfo('Processing OAuth callback...');
        
        // Wait a moment for the page to fully load and Supabase to process the OAuth
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Check if we have a session
        const { data: { session }, error: sessionError } = await supabase.auth.getSession();
        
        console.log('Session check:', { session: !!session, error: sessionError });
        setDebugInfo(`Session check: ${session ? 'Found' : 'Not found'}, Error: ${sessionError?.message || 'None'}`);
        
        if (sessionError) {
          console.error('Session error:', sessionError);
          setError(sessionError.message);
          setTimeout(() => {
            navigate('/login?error=oauth_failed');
          }, 3000);
          return;
        }

        if (session?.user) {
          console.log('User authenticated:', session.user.email);
          setDebugInfo(`User authenticated: ${session.user.email}`);
          navigate('/dashboard');
        } else {
          console.log('No session found, trying auth state listener...');
          setDebugInfo('No session found, trying auth state listener...');
          
          // Try to listen for auth state changes
          const { data: { subscription } } = supabase.auth.onAuthStateChange((event, session) => {
            console.log('Auth state change:', event, session?.user?.email);
            setDebugInfo(`Auth state change: ${event}, User: ${session?.user?.email || 'None'}`);
            if (session?.user) {
              navigate('/dashboard');
            }
          });

          // Wait a bit more for auth state to change
          setTimeout(() => {
            subscription.unsubscribe();
            console.log('Auth listener timeout');
            setDebugInfo('Auth listener timeout - redirecting to login');
            navigate('/login?error=oauth_timeout');
          }, 2000);
        }
      } catch (err) {
        console.error('OAuth callback error:', err);
        setError('Authentication failed');
        setDebugInfo(`Error: ${err}`);
        setTimeout(() => {
          navigate('/login?error=oauth_failed');
        }, 3000);
      } finally {
        setIsProcessing(false);
      }
    };

    handleOAuthCallback();
  }, [navigate]);

  const handleManualRedirect = () => {
    navigate('/dashboard');
  };

  return (
    <Box minH="100vh" display="flex" alignItems="center" justifyContent="center">
      <VStack spacing={4}>
        <Spinner size="xl" color="blue.500" />
        <Text>Completing login...</Text>
        <Text fontSize="sm" color="gray.500">
          Please wait while we authenticate your account
        </Text>
        {debugInfo && (
          <Text fontSize="xs" color="blue.500" textAlign="center" maxW="400px">
            Debug: {debugInfo}
          </Text>
        )}
        {error && (
          <Text fontSize="sm" color="red.500">
            Error: {error}
          </Text>
        )}
        {!isProcessing && (
          <Button onClick={handleManualRedirect} colorScheme="blue" size="sm">
            Continue to Dashboard
          </Button>
        )}
      </VStack>
    </Box>
  );
};

export default OAuthCallback;
