import React, { useState } from 'react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  Text,
  Input,
  VStack,
  Alert,
  AlertIcon,
  useToast,
  useDisclosure,
} from '@chakra-ui/react';
import { authService } from '../services/auth';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

interface DeleteAccountModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const DeleteAccountModal: React.FC<DeleteAccountModalProps> = ({ isOpen, onClose }) => {
  const [confirmationText, setConfirmationText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  const { logout } = useAuth();
  const navigate = useNavigate();
  const toast = useToast();

  const handleDeleteAccount = async () => {
    if (confirmationText !== 'DELETE') {
      toast({
        title: 'Invalid Confirmation',
        description: 'Please type DELETE in capital letters to confirm.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      return;
    }

    setIsDeleting(true);
    try {
      await authService.deleteAccount();
      
      toast({
        title: 'Account Deleted',
        description: 'Your account and all data have been permanently deleted.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });

      // Logout and redirect to login
      logout();
      navigate('/login');
    } catch (error: any) {
      console.error('Error deleting account:', error);
      toast({
        title: 'Deletion Failed',
        description: error.response?.data?.detail || 'Failed to delete account. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setIsDeleting(false);
    }
  };

  const handleClose = () => {
    setConfirmationText('');
    onClose();
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} isCentered>
      <ModalOverlay />
      <ModalContent maxW="md">
        <ModalHeader color="red.500">Delete Account</ModalHeader>
        <ModalBody>
          <VStack spacing={4} align="stretch">
            <Alert status="error">
              <AlertIcon />
              <Text fontSize="sm">
                <strong>Warning:</strong> This action cannot be undone. All your data will be permanently deleted.
              </Text>
            </Alert>

            <Text>
              Deleting your account will permanently remove:
            </Text>
            <VStack align="start" spacing={1} pl={4}>
              <Text fontSize="sm">• Your profile and personal information</Text>
              <Text fontSize="sm">• All health data and metrics</Text>
              <Text fontSize="sm">• Activity logs and progress</Text>
              <Text fontSize="sm">• Goals and achievements</Text>
              <Text fontSize="sm">• All settings and preferences</Text>
            </VStack>

            <Text fontWeight="bold" color="red.500">
              To confirm deletion, type <strong>DELETE</strong> in the box below:
            </Text>

            <Input
              value={confirmationText}
              onChange={(e) => setConfirmationText(e.target.value)}
              placeholder="Type DELETE to confirm"
              borderColor={confirmationText === 'DELETE' ? 'green.300' : 'red.300'}
              focusBorderColor={confirmationText === 'DELETE' ? 'green.400' : 'red.400'}
            />

            {confirmationText && confirmationText !== 'DELETE' && (
              <Text fontSize="sm" color="red.500">
                Please type exactly "DELETE" to confirm
              </Text>
            )}
          </VStack>
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" onClick={handleClose} isDisabled={isDeleting}>
            Cancel
          </Button>
          <Button
            colorScheme="red"
            ml={3}
            onClick={handleDeleteAccount}
            isLoading={isDeleting}
            loadingText="Deleting..."
            isDisabled={confirmationText !== 'DELETE'}
          >
            Delete Account Permanently
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  );
};

export default DeleteAccountModal;
