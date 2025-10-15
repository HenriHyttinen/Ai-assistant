// @ts-nocheck
import {
  Box,
  Button,
  Heading,
  Text,
  VStack,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  Container,
  Card,
  CardBody,
} from '@chakra-ui/react';
import { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { authService } from '../services/auth';

const VerifyEmail = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const toast = useToast();
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<'verifying' | 'success' | 'error'>('verifying');
  const [message, setMessage] = useState('');

  const token = searchParams.get('token');

  useEffect(() => {
    if (token) {
      verifyEmail();
    } else {
      setStatus('error');
      setMessage('No verification token provided');
    }
  }, [token]);

  const verifyEmail = async () => {
    if (!token) return;

    try {
      setLoading(true);
      await authService.verifyEmail(token);
      setStatus('success');
      setMessage('Your email has been verified successfully!');
      
      toast({
        title: 'Email Verified',
        description: 'Your email has been verified successfully!',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

      // Redirect to login after 3 seconds
      setTimeout(() => {
        navigate('/login');
      }, 3000);
    } catch (err: any) {
      setStatus('error');
      setMessage(err.response?.data?.detail || 'Failed to verify email');
      
      toast({
        title: 'Verification Failed',
        description: err.response?.data?.detail || 'Failed to verify email',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  const resendVerification = async () => {
    try {
      setLoading(true);
      await authService.resendVerificationEmail();
      
      toast({
        title: 'Verification Email Sent',
        description: 'Please check your email for the verification link.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (err: any) {
      toast({
        title: 'Failed to Resend',
        description: err.response?.data?.detail || 'Failed to resend verification email',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxW="md" py={8}>
      <Card>
        <CardBody>
          <VStack spacing={6} align="center">
            <Heading size="lg">Email Verification</Heading>
            
            {status === 'verifying' && (
              <>
                <Spinner size="xl" />
                <Text>Verifying your email...</Text>
              </>
            )}

            {status === 'success' && (
              <>
                <Alert status="success">
                  <AlertIcon />
                  {message}
                </Alert>
                <Text>Redirecting to login page...</Text>
              </>
            )}

            {status === 'error' && (
              <>
                <Alert status="error">
                  <AlertIcon />
                  {message}
                </Alert>
                <VStack spacing={4}>
                  <Button
                    colorScheme="blue"
                    onClick={resendVerification}
                    isLoading={loading}
                    loadingText="Sending..."
                  >
                    Resend Verification Email
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => navigate('/login')}
                  >
                    Back to Login
                  </Button>
                </VStack>
              </>
            )}
          </VStack>
        </CardBody>
      </Card>
    </Container>
  );
};

export default VerifyEmail;

