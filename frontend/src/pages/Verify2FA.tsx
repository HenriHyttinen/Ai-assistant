// @ts-nocheck
import React, { useEffect } from 'react';
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Heading,
  Input,
  Stack,
  Text,
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
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface Verify2FAFormValues {
  code: string;
}

const validationSchema = Yup.object({
  code: Yup.string()
    .required('Verification code is required')
    .matches(/^\d{6}$/, 'Code must be 6 digits'),
});

const Verify2FA = () => {
  const toast = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const { verify2FA, error, clearError } = useAuth();
  
  const email = location.state?.email;

  // Check if user should be on this page
  useEffect(() => {
    const tempToken = localStorage.getItem('temp_token');
    if (!tempToken || !email) {
      toast({
        title: 'Error',
        description: 'No 2FA verification required. Please login again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      navigate('/login');
    }
  }, [email, navigate, toast]);

  const formik = useFormik({
    initialValues: {
      code: '',
    } as Verify2FAFormValues,
    validationSchema,
    onSubmit: async (values: Verify2FAFormValues) => {
      try {
        if (!email) {
          toast({
            title: 'Error',
            description: 'Email not found. Please login again.',
            status: 'error',
            duration: 5000,
            isClosable: true,
          });
          navigate('/login');
          return;
        }
        
        await verify2FA(email, values.code);
        toast({
          title: 'Verification Successful',
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
                <Heading size="lg">Two-Factor Authentication</Heading>
                <Text color="gray.600">
                  Please enter the 6-digit code from your authenticator app
                </Text>
                
                {/* Development Helper */}
                <Alert status="info" borderRadius="md" maxW="md">
                  <AlertIcon />
                  <Box>
                    <Text fontWeight="bold" mb={1}>🔧 Development Mode</Text>
                    <Text fontSize="sm">
                      For testing, use verification code: <Text as="span" fontFamily="mono" fontWeight="bold" color="blue.600">123456</Text>
                    </Text>
                  </Box>
                </Alert>
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
                    <FormControl isInvalid={formik.touched.code && formik.errors.code}>
                      <FormLabel htmlFor="code">Verification Code</FormLabel>
                      <Input
                        id="code"
                        type="text"
                        maxLength={6}
                        {...formik.getFieldProps('code')}
                      />
                      {formik.touched.code && formik.errors.code && (
                        <Text color="red.500" fontSize="sm">{formik.errors.code}</Text>
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
                      Verify
                    </Button>
                  </Stack>
                </form>
              </Stack>
            </Stack>
          </CardBody>
        </Card>
      </Container>
    </Flex>
  );
};

export default Verify2FA; 