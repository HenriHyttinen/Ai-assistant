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
  useDisclosure,
} from '@chakra-ui/react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { Link as RouterLink } from 'react-router-dom';
import { useState } from 'react';
import { FaCode } from 'react-icons/fa';
import { authService } from '../services/auth';
import DevHelper from '../components/DevHelper';

interface ForgotPasswordFormValues {
  email: string;
  backup_code?: string;
  new_password?: string;
  confirm_password?: string;
}

const validationSchema = Yup.object({
  email: Yup.string()
    .email('Invalid email address')
    .required('Email is required'),
  backup_code: Yup.string().when('resetMethod', {
    is: '2fa',
    then: (schema) => schema.required('Backup code is required'),
    otherwise: (schema) => schema.notRequired(),
  }),
  new_password: Yup.string().when('resetMethod', {
    is: '2fa',
    then: (schema) => schema.min(8, 'Password must be at least 8 characters').required('New password is required'),
    otherwise: (schema) => schema.notRequired(),
  }),
  confirm_password: Yup.string().when('resetMethod', {
    is: '2fa',
    then: (schema) => schema.oneOf([Yup.ref('new_password')], 'Passwords must match').required('Please confirm your password'),
    otherwise: (schema) => schema.notRequired(),
  }),
});

const ForgotPassword = () => {
  const toast = useToast();
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [resetLink, setResetLink] = useState<string>('');
  const [resetMethod, setResetMethod] = useState<'email' | '2fa'>('email');
  const { isOpen: isDevHelperOpen, onOpen: onDevHelperOpen, onClose: onDevHelperClose } = useDisclosure();

  const formik = useFormik({
    initialValues: {
      email: '',
      backup_code: '',
      new_password: '',
      confirm_password: '',
    } as ForgotPasswordFormValues,
    validationSchema,
    onSubmit: async (values: ForgotPasswordFormValues) => {
      try {
        setIsLoading(true);
        
        if (resetMethod === 'email') {
          const response = await authService.requestPasswordReset(values.email);
          setIsSubmitted(true);
          
          // In development mode, show the reset link if provided
          if (response.reset_link) {
            setResetLink(response.reset_link);
          }
          
          toast({
            title: 'Reset Link Sent',
            description: 'If an account with that email exists, we\'ve sent a password reset link.',
            status: 'success',
            duration: 5000,
            isClosable: true,
          });
        } else if (resetMethod === '2fa') {
          // Handle 2FA backup code password reset
          const response = await authService.resetPasswordWith2FA(
            values.email,
            values.backup_code!,
            values.new_password!
          );
          
          toast({
            title: 'Password Reset Successful',
            description: 'Your password has been reset using your 2FA backup code.',
            status: 'success',
            duration: 5000,
            isClosable: true,
          });
          
          // Redirect to login after successful reset
          setTimeout(() => {
            window.location.href = '/login';
          }, 2000);
        }
      } catch (err: any) {
        toast({
          title: 'Request Failed',
          description: err.response?.data?.detail || 'Failed to reset password. Please try again.',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setIsLoading(false);
      }
    },
  });

  if (isSubmitted) {
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
                <Heading size="lg" color="green.600">Check Your Email</Heading>
                
                <Alert status="success" borderRadius="md">
                  <AlertIcon />
                  <Box>
                    <Text fontWeight="bold">Password reset link sent!</Text>
                    <Text fontSize="sm">
                      If an account with that email exists, we've sent a password reset link to your email address.
                    </Text>
                  </Box>
                </Alert>

                <Text color="gray.600" textAlign="center">
                  Didn't receive the email? Check your spam folder or try again.
                </Text>

                {/* Development Mode - Show Reset Link */}
                {resetLink && (
                  <Box p={4} bg="blue.50" borderRadius="md" border="1px" borderColor="blue.200">
                    <Text fontWeight="bold" color="blue.800" mb={2}>
                      🔗 Development Mode - Reset Link:
                    </Text>
                    <Text fontSize="sm" color="blue.600" mb={3}>
                      Click the link below to reset your password:
                    </Text>
                    <Button
                      as="a"
                      href={resetLink}
                      target="_blank"
                      colorScheme="blue"
                      size="sm"
                      width="full"
                    >
                      Reset Password
                    </Button>
                    <Text fontSize="xs" color="gray.500" mt={2} textAlign="center">
                      This link expires in 1 hour
                    </Text>
                  </Box>
                )}

                <Stack spacing="4" w="full">
                  {resetLink && (
                    <Button
                      colorScheme="green"
                      onClick={onDevHelperOpen}
                      leftIcon={<FaCode />}
                    >
                      Development Helper - View Reset Link
                    </Button>
                  )}
                  
                  <Button
                    colorScheme="blue"
                    onClick={() => setIsSubmitted(false)}
                    variant="outline"
                  >
                    Try Again
                  </Button>
                  
                  <Text align="center">
                    <Link as={RouterLink} to="/login" color="blue.500">
                      Back to Login
                    </Link>
                  </Text>
                </Stack>
              </Stack>
            </CardBody>
          </Card>
        </Container>
        
        {/* Development Helper Modal */}
        <DevHelper
          title="Password Reset"
          links={resetLink ? [{
            label: "Password Reset Link",
            url: resetLink,
            description: "Click to reset your password (expires in 1 hour)"
          }] : []}
          isOpen={isDevHelperOpen}
          onClose={onDevHelperClose}
        />
      </Flex>
    );
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
                <Heading size="lg">Forgot Password?</Heading>
                <Text color="gray.600" textAlign="center">
                  Choose how you'd like to reset your password:
                </Text>
                
                {/* Method Selection */}
                <Stack direction="row" spacing={4} align="center">
                  <Button
                    variant={resetMethod === 'email' ? 'solid' : 'outline'}
                    colorScheme="blue"
                    onClick={() => setResetMethod('email')}
                    size="sm"
                  >
                    Email Reset
                  </Button>
                  <Button
                    variant={resetMethod === '2fa' ? 'solid' : 'outline'}
                    colorScheme="green"
                    onClick={() => setResetMethod('2fa')}
                    size="sm"
                    leftIcon={<FaCode />}
                  >
                    2FA Backup Code
                  </Button>
                </Stack>
                
                <Text color="gray.500" fontSize="sm" textAlign="center">
                  {resetMethod === 'email' 
                    ? "We'll send you a reset link via email"
                    : "Use one of your 2FA backup codes to reset your password"
                  }
                </Text>
              </Stack>

              <form onSubmit={formik.handleSubmit}>
                <Stack spacing="5">
                  <FormControl isInvalid={formik.touched.email && formik.errors.email}>
                    <FormLabel htmlFor="email">Email Address</FormLabel>
                    <Input
                      id="email"
                      type="email"
                      placeholder="Enter your email address"
                      {...formik.getFieldProps('email')}
                    />
                    {formik.touched.email && formik.errors.email && (
                      <Text color="red.500" fontSize="sm">{formik.errors.email}</Text>
                    )}
                  </FormControl>

                  {/* 2FA Backup Code Fields */}
                  {resetMethod === '2fa' && (
                    <>
                      <FormControl isInvalid={formik.touched.backup_code && formik.errors.backup_code}>
                        <FormLabel htmlFor="backup_code">2FA Backup Code</FormLabel>
                        <Input
                          id="backup_code"
                          type="text"
                          placeholder="Enter your backup code"
                          {...formik.getFieldProps('backup_code')}
                        />
                        {formik.touched.backup_code && formik.errors.backup_code && (
                          <Text color="red.500" fontSize="sm">{formik.errors.backup_code}</Text>
                        )}
                        <Text fontSize="xs" color="gray.500" mt={1}>
                          Enter one of your 8-digit backup codes from when you set up 2FA
                        </Text>
                      </FormControl>

                      <FormControl isInvalid={formik.touched.new_password && formik.errors.new_password}>
                        <FormLabel htmlFor="new_password">New Password</FormLabel>
                        <Input
                          id="new_password"
                          type="password"
                          placeholder="Enter new password"
                          {...formik.getFieldProps('new_password')}
                        />
                        {formik.touched.new_password && formik.errors.new_password && (
                          <Text color="red.500" fontSize="sm">{formik.errors.new_password}</Text>
                        )}
                      </FormControl>

                      <FormControl isInvalid={formik.touched.confirm_password && formik.errors.confirm_password}>
                        <FormLabel htmlFor="confirm_password">Confirm New Password</FormLabel>
                        <Input
                          id="confirm_password"
                          type="password"
                          placeholder="Confirm new password"
                          {...formik.getFieldProps('confirm_password')}
                        />
                        {formik.touched.confirm_password && formik.errors.confirm_password && (
                          <Text color="red.500" fontSize="sm">{formik.errors.confirm_password}</Text>
                        )}
                      </FormControl>
                    </>
                  )}
                </Stack>

                <Stack spacing="6" mt={6}>
                  <Button
                    type="submit"
                    colorScheme={resetMethod === 'email' ? 'blue' : 'green'}
                    size="lg"
                    fontSize="md"
                    isLoading={isLoading}
                    loadingText={resetMethod === 'email' ? 'Sending...' : 'Resetting...'}
                  >
                    {resetMethod === 'email' ? 'Send Reset Link' : 'Reset Password with 2FA'}
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
      
      {/* Development Helper Modal */}
      <DevHelper
        title="Password Reset"
        links={resetLink ? [{
          label: "Password Reset Link",
          url: resetLink,
          description: "Click to reset your password (expires in 1 hour)"
        }] : []}
        isOpen={isDevHelperOpen}
        onClose={onDevHelperClose}
      />
    </Flex>
  );
};

export default ForgotPassword;
