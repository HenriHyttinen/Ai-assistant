// @ts-nocheck
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Heading,
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
} from '@chakra-ui/react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { Link as RouterLink } from 'react-router-dom';
import { FaGoogle, FaGithub } from 'react-icons/fa';
import { useAuth } from '../contexts/AuthContext';
import { authService } from '../services/auth';

interface LoginFormValues {
  email: string;
  password: string;
}

const validationSchema = Yup.object({
  email: Yup.string()
    .email('Invalid email address')
    .required('Email is required'),
  password: Yup.string()
    .min(8, 'Password must be at least 8 characters')
    .required('Password is required'),
});

const Login = () => {
  const toast = useToast();
  const { login, error, clearError } = useAuth();

  const formik = useFormik({
    initialValues: {
      email: '',
      password: '',
    } as LoginFormValues,
    validationSchema,
    onSubmit: async (values: LoginFormValues) => {
      try {
        await login(values.email, values.password);
        toast({
          title: 'Login Successful',
          description: 'Welcome back!',
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
      } catch (err) {
        // Error is handled by AuthContext
      }
    },
  });

  const handleOAuthLogin = async (provider: 'google' | 'github') => {
    try {
      const response = await authService.loginWithOAuth(provider);
      // Redirect to the OAuth URL
      window.location.href = response.url;
    } catch (err) {
      toast({
        title: 'Login Failed',
        description: 'Failed to login with ' + provider,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  return (
    <Flex 
      minH="100vh" 
      align="center" 
      justify="center" 
      bg="gray.50"
      w="100%"
      h="100vh"
    >
      <Container
        maxW="lg"
        py={{ base: '12', md: '24' }}
        px={{ base: '0', sm: '8' }}
        w="100%"
      >
        <Card boxShadow="lg" rounded="lg">
          <CardBody p={{ base: '4', md: '8' }}>
            <Stack spacing="8">
              <Stack spacing="6" align="center">
                <Heading size="lg">Welcome Back</Heading>
                <Text color="gray.600">
                  Don't have an account?{' '}
                  <Link as={RouterLink} to="/register" color="blue.500">
                    Sign up
                  </Link>
                </Text>
              </Stack>

              {error && (
                <Alert status="error" onClose={clearError}>
                  <AlertIcon />
                  {error}
                </Alert>
              )}

              <Stack spacing="6">
                <form onSubmit={formik.handleSubmit}>
                  <Stack spacing="5">
                    <FormControl isInvalid={formik.touched.email && formik.errors.email}>
                      <FormLabel htmlFor="email">Email</FormLabel>
                      <Input
                        id="email"
                        type="email"
                        {...formik.getFieldProps('email')}
                      />
                      {formik.touched.email && formik.errors.email && (
                        <Text color="red.500" fontSize="sm">{formik.errors.email}</Text>
                      )}
                    </FormControl>

                    <FormControl isInvalid={formik.touched.password && formik.errors.password}>
                      <FormLabel htmlFor="password">Password</FormLabel>
                      <Input
                        id="password"
                        type="password"
                        {...formik.getFieldProps('password')}
                      />
                      {formik.touched.password && formik.errors.password && (
                        <Text color="red.500" fontSize="sm">{formik.errors.password}</Text>
                      )}
                    </FormControl>
                  </Stack>

                  <Stack spacing="6" mt={6}>
                    <Button
                      type="submit"
                      colorScheme="blue"
                      size="lg"
                      fontSize="md"
                      isLoading={formik.isSubmitting}
                    >
                      Sign in
                    </Button>
                    
                    <Text align="center">
                      <Link as={RouterLink} to="/forgot-password" color="blue.500" fontSize="sm">
                        Forgot your password?
                      </Link>
                    </Text>
                  </Stack>
                </form>

                <HStack>
                  <Divider />
                  <Text fontSize="sm" whiteSpace="nowrap" color="gray.500">
                    or continue with
                  </Text>
                  <Divider />
                </HStack>

                <Stack spacing="3">
                  <Button
                    variant="outline"
                    leftIcon={<FaGoogle />}
                    onClick={() => handleOAuthLogin('google')}
                  >
                    Sign in with Google
                  </Button>
                  <Button
                    variant="outline"
                    leftIcon={<FaGithub />}
                    onClick={() => handleOAuthLogin('github')}
                  >
                    Sign in with GitHub
                  </Button>
                </Stack>
              </Stack>
            </Stack>
          </CardBody>
        </Card>
      </Container>
    </Flex>
  );
};

export default Login; 