// @ts-nocheck
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  Stack,
  Text,
  Link,
  useToast,
  Container,
  Card,
  CardBody,
  Divider,
  HStack,
  Alert,
  AlertIcon,
  Flex,
  Heading,
} from '@chakra-ui/react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
import { FaGithub, FaGoogle, FaFacebook, FaApple, FaDiscord } from 'react-icons/fa';
import { useSupabaseAuth } from '../contexts/SupabaseAuthContext';
import { getErrorMessage } from '../utils/errorUtils';

interface LoginFormValues {
  email: string;
  password: string;
}

const validationSchema = Yup.object({
  email: Yup.string().email('Invalid email address').required('Email is required'),
  password: Yup.string().required('Password is required'),
});

const SupabaseLogin = () => {
  const { signIn, signInWithGitHub, signInWithGoogle, signInWithFacebook, signInWithApple, signInWithDiscord, loading, error, clearError } = useSupabaseAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const formik = useFormik<LoginFormValues>({
    initialValues: {
      email: '',
      password: '',
    },
    validationSchema,
    onSubmit: async (values, { setSubmitting }) => {
      try {
        const { user, error } = await signIn(values.email, values.password);
        
        if (error) {
          toast({
            title: 'Login Failed',
            description: error.message,
            status: 'error',
            duration: 5000,
            isClosable: true,
          });
        } else if (user) {
          toast({
            title: 'Login Successful',
            description: 'Welcome back!',
            status: 'success',
            duration: 3000,
            isClosable: true,
          });
          navigate('/dashboard');
        }
      } catch (err: any) {
        toast({
          title: 'Login Failed',
          description: err.message || 'An unexpected error occurred',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setSubmitting(false);
      }
    },
  });

  const handleGitHubLogin = async () => {
    try {
      const { user, error } = await signInWithGitHub();
      
      if (error) {
        toast({
          title: 'GitHub Login Failed',
          description: error.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } else if (user) {
        toast({
          title: 'GitHub Login Successful',
          description: 'Welcome!',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        navigate('/dashboard');
      }
    } catch (err: any) {
      toast({
        title: 'GitHub Login Failed',
        description: err.message || 'An unexpected error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleGoogleLogin = async () => {
    try {
      const { user, error } = await signInWithGoogle();
      
      if (error) {
        toast({
          title: 'Google Login Failed',
          description: error.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } else if (user) {
        toast({
          title: 'Google Login Successful',
          description: 'Welcome!',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        navigate('/dashboard');
      }
    } catch (err: any) {
      toast({
        title: 'Google Login Failed',
        description: err.message || 'An unexpected error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleFacebookLogin = async () => {
    try {
      const { user, error } = await signInWithFacebook();
      
      if (error) {
        toast({
          title: 'Facebook Login Failed',
          description: error.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } else if (user) {
        toast({
          title: 'Facebook Login Successful',
          description: 'Welcome!',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        navigate('/dashboard');
      }
    } catch (err: any) {
      toast({
        title: 'Facebook Login Failed',
        description: err.message || 'An unexpected error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleAppleLogin = async () => {
    try {
      const { user, error } = await signInWithApple();
      
      if (error) {
        toast({
          title: 'Apple Login Failed',
          description: error.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } else if (user) {
        toast({
          title: 'Apple Login Successful',
          description: 'Welcome!',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        navigate('/dashboard');
      }
    } catch (err: any) {
      toast({
        title: 'Apple Login Failed',
        description: err.message || 'An unexpected error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleDiscordLogin = async () => {
    try {
      const { user, error } = await signInWithDiscord();
      
      if (error) {
        toast({
          title: 'Discord Login Failed',
          description: error.message,
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } else if (user) {
        toast({
          title: 'Discord Login Successful',
          description: 'Welcome!',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });
        navigate('/dashboard');
      }
    } catch (err: any) {
      toast({
        title: 'Discord Login Failed',
        description: err.message || 'An unexpected error occurred',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  return (
    <Container maxW="md" py={12}>
      <Card>
        <CardBody p={8}>
          <Box textAlign="center" mb={8}>
            <Heading size="lg" mb={2}>Welcome Back</Heading>
            <Text color="gray.600">Sign in to your health tracking account</Text>
          </Box>

          {error && (
            <Alert status="error" mb={4} onClose={clearError}>
              <AlertIcon />
              {getErrorMessage(error)}
            </Alert>
          )}

          <form onSubmit={formik.handleSubmit}>
            <Stack spacing={4}>
              <FormControl isInvalid={formik.touched.email && !!formik.errors.email}>
                <FormLabel>Email</FormLabel>
                <Input
                  type="email"
                  name="email"
                  value={formik.values.email}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  placeholder="Enter your email"
                />
                {formik.touched.email && formik.errors.email && (
                  <Text color="red.500" fontSize="sm" mt={1}>
                    {formik.errors.email}
                  </Text>
                )}
              </FormControl>

              <FormControl isInvalid={formik.touched.password && !!formik.errors.password}>
                <FormLabel>Password</FormLabel>
                <Input
                  type="password"
                  name="password"
                  value={formik.values.password}
                  onChange={formik.handleChange}
                  onBlur={formik.handleBlur}
                  placeholder="Enter your password"
                />
                {formik.touched.password && formik.errors.password && (
                  <Text color="red.500" fontSize="sm" mt={1}>
                    {formik.errors.password}
                  </Text>
                )}
              </FormControl>

              <Button
                type="submit"
                colorScheme="blue"
                size="lg"
                isLoading={formik.isSubmitting || loading}
                loadingText="Signing in..."
              >
                Sign In
              </Button>
            </Stack>
          </form>

          <Divider my={6} />

          <Stack spacing={3}>
            <Button
              leftIcon={<FaGithub />}
              variant="outline"
              onClick={handleGitHubLogin}
              isLoading={loading}
              loadingText="Connecting..."
            >
              Continue with GitHub
            </Button>
            
            <Button
              leftIcon={<FaGoogle />}
              variant="outline"
              onClick={handleGoogleLogin}
              isLoading={loading}
              loadingText="Connecting..."
              colorScheme="red"
            >
              Continue with Google
            </Button>
            
            <Button
              leftIcon={<FaFacebook />}
              variant="outline"
              onClick={handleFacebookLogin}
              isLoading={loading}
              loadingText="Connecting..."
              colorScheme="blue"
            >
              Continue with Facebook
            </Button>
            
            <Button
              leftIcon={<FaApple />}
              variant="outline"
              onClick={handleAppleLogin}
              isLoading={loading}
              loadingText="Connecting..."
              colorScheme="gray"
            >
              Continue with Apple
            </Button>
            
            <Button
              leftIcon={<FaDiscord />}
              variant="outline"
              onClick={handleDiscordLogin}
              isLoading={loading}
              loadingText="Connecting..."
              colorScheme="purple"
            >
              Continue with Discord
            </Button>
          </Stack>

          <Flex justify="center" mt={6}>
            <HStack spacing={1}>
              <Text>Don't have an account?</Text>
              <Link as={RouterLink} to="/register" color="blue.500" fontWeight="medium">
                Sign up
              </Link>
            </HStack>
          </Flex>
        </CardBody>
      </Card>
    </Container>
  );
};

export default SupabaseLogin;
