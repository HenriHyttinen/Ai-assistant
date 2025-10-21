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
import { FaGoogle, FaGithub, FaFacebook, FaApple, FaDiscord } from 'react-icons/fa';
import { useSupabaseAuth } from '../contexts/SupabaseAuthContext';
import { authService } from '../services/auth';
import { getErrorMessage } from '../utils/errorUtils';

interface RegisterFormValues {
  email: string;
  password: string;
  confirmPassword: string;
}

const validationSchema = Yup.object({
  email: Yup.string()
    .email('Invalid email address')
    .required('Email is required'),
  password: Yup.string()
    .min(8, 'Password must be at least 8 characters')
    .required('Password is required'),
  confirmPassword: Yup.string()
    .oneOf([Yup.ref('password')], 'Passwords must match')
    .required('Please confirm your password'),
});

const Register = () => {
  const toast = useToast();
  const { signUp, signInWithGitHub, signInWithGoogle, signInWithFacebook, signInWithApple, signInWithDiscord, error, clearError } = useSupabaseAuth();

  const formik = useFormik({
    initialValues: {
      email: '',
      password: '',
      confirmPassword: '',
    } as RegisterFormValues,
    validationSchema,
    onSubmit: async (values: RegisterFormValues) => {
      try {
        const { user, error } = await signUp(values.email, values.password);
        
        if (error) {
          throw new Error(error.message);
        }
        
        if (user) {
          toast({
            title: 'Registration Successful',
            description: 'Please check your email for verification link.',
            status: 'success',
            duration: 5000,
            isClosable: true,
          });
        }
      } catch (err: any) {
        toast({
          title: 'Registration Failed',
          description: err.message || 'An error occurred during registration',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      }
    },
  });

  const handleOAuthLogin = async (provider: 'google' | 'github') => {
    try {
      const response = await authService.loginWithOAuth(provider);
      if (response.requires_2fa) {
        // Handle 2FA if needed
        return;
      }
      localStorage.setItem('token', response.access_token);
      window.location.href = '/dashboard';
    } catch (err) {
      toast({
        title: 'Registration Failed',
        description: 'Failed to register with ' + provider,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  return (
    <Flex minH="100vh" align="center" justify="center" bg="gray.50">
      <Container
        maxW="lg"
        py={{ base: '12', md: '24' }}
        px={{ base: '0', sm: '8' }}
      >
        <Card boxShadow="lg" rounded="lg">
          <CardBody p={{ base: '4', md: '8' }}>
            <Stack spacing="8">
              <Stack spacing="6" align="center">
                <Heading size="lg">Create an Account</Heading>
                <Text color="gray.600">
                  Already have an account?{' '}
                  <Link as={RouterLink} to="/login" color="blue.500">
                    Sign in
                  </Link>
                </Text>
              </Stack>

              {error && (
                <Alert status="error" onClose={clearError}>
                  <AlertIcon />
                  {getErrorMessage(error)}
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

                    <FormControl isInvalid={formik.touched.confirmPassword && formik.errors.confirmPassword}>
                      <FormLabel htmlFor="confirmPassword">Confirm Password</FormLabel>
                      <Input
                        id="confirmPassword"
                        type="password"
                        {...formik.getFieldProps('confirmPassword')}
                      />
                      {formik.touched.confirmPassword && formik.errors.confirmPassword && (
                        <Text color="red.500" fontSize="sm">{formik.errors.confirmPassword}</Text>
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
                      Create Account
                    </Button>
                  </Stack>
                </form>

                <HStack>
                  <Divider />
                  <Text fontSize="sm" whiteSpace="nowrap" color="gray.500">
                    or sign up with
                  </Text>
                  <Divider />
                </HStack>

                <Stack spacing="4">
                  <Button
                    variant="outline"
                    leftIcon={<FaGoogle />}
                    onClick={() => handleOAuthLogin('google')}
                  >
                    Continue with Google
                  </Button>
                  <Button
                    variant="outline"
                    leftIcon={<FaGithub />}
                    onClick={() => handleOAuthLogin('github')}
                  >
                    Continue with GitHub
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

export default Register; 