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
  Alert,
  AlertIcon,
  Flex,
} from '@chakra-ui/react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { Link as RouterLink, useSearchParams, useNavigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { authService } from '../services/auth';

interface ResetPasswordFormValues {
  password: string;
  confirmPassword: string;
}

const validationSchema = Yup.object({
  password: Yup.string()
    .min(8, 'Password must be at least 8 characters')
    .required('Password is required'),
  confirmPassword: Yup.string()
    .oneOf([Yup.ref('password')], 'Passwords must match')
    .required('Please confirm your password'),
});

const ResetPassword = () => {
  const toast = useToast();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const tokenParam = searchParams.get('token');
    if (!tokenParam) {
      toast({
        title: 'Invalid Link',
        description: 'This password reset link is invalid or has expired.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      navigate('/forgot-password');
    } else {
      setToken(tokenParam);
    }
  }, [searchParams, navigate, toast]);

  const formik = useFormik({
    initialValues: {
      password: '',
      confirmPassword: '',
    } as ResetPasswordFormValues,
    validationSchema,
    onSubmit: async (values: ResetPasswordFormValues) => {
      if (!token) return;
      
      try {
        setIsLoading(true);
        await authService.resetPassword(token, values.password);
        setIsSuccess(true);
        toast({
          title: 'Password Reset Successful',
          description: 'Your password has been updated successfully.',
          status: 'success',
          duration: 5000,
          isClosable: true,
        });
      } catch (err: any) {
        toast({
          title: 'Reset Failed',
          description: err.response?.data?.detail || 'Failed to reset password. The link may have expired.',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setIsLoading(false);
      }
    },
  });

  if (isSuccess) {
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
              <Stack spacing="8" align="center">
                <Heading size="lg" color="green.600">Password Reset Complete!</Heading>
                
                <Alert status="success" borderRadius="md">
                  <AlertIcon />
                  <Box>
                    <Text fontWeight="bold">Your password has been updated successfully.</Text>
                    <Text fontSize="sm">
                      You can now log in with your new password.
                    </Text>
                  </Box>
                </Alert>

                <Button
                  colorScheme="blue"
                  size="lg"
                  onClick={() => navigate('/login')}
                >
                  Go to Login
                </Button>
              </Stack>
            </CardBody>
          </Card>
        </Container>
      </Flex>
    );
  }

  if (!token) {
    return null; // Will redirect in useEffect
  }

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
                <Heading size="lg">Reset Your Password</Heading>
                <Text color="gray.600" textAlign="center">
                  Enter your new password below.
                </Text>
              </Stack>

              <form onSubmit={formik.handleSubmit}>
                <Stack spacing="5">
                  <FormControl isInvalid={formik.touched.password && formik.errors.password}>
                    <FormLabel htmlFor="password">New Password</FormLabel>
                    <Input
                      id="password"
                      type="password"
                      placeholder="Enter your new password"
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
                      placeholder="Confirm your new password"
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
                    isLoading={isLoading}
                    loadingText="Resetting..."
                  >
                    Reset Password
                  </Button>
                  
                  <Text align="center">
                    <Link as={RouterLink} to="/login" color="blue.500">
                      Back to Login
                    </Link>
                  </Text>
                </Stack>
              </form>
            </Stack>
          </CardBody>
        </Card>
      </Container>
    </Flex>
  );
};

export default ResetPassword;
