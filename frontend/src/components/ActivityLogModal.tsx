import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  FormControl,
  FormLabel,
  Input,
  Select,
  Textarea,
  VStack,
  useToast,
} from '@chakra-ui/react';
import { useFormik } from 'formik';
import * as Yup from 'yup';
import { analytics } from '../services/api';

interface ActivityLogModalProps {
  isOpen: boolean;
  onClose: () => void;
  onActivityLogged?: () => void;
}

interface ActivityFormValues {
  activity_type: string;
  duration: number;
  intensity: string;
  notes: string;
}

const validationSchema = Yup.object({
  activity_type: Yup.string().required('Activity type is required'),
  duration: Yup.number()
    .min(1, 'Duration must be at least 1 minute')
    .max(480, 'Duration cannot exceed 8 hours')
    .required('Duration is required'),
  intensity: Yup.string().required('Intensity is required'),
  notes: Yup.string().max(500, 'Notes cannot exceed 500 characters'),
});

const ActivityLogModal = ({ isOpen, onClose, onActivityLogged }: ActivityLogModalProps) => {
  const toast = useToast();

  const formik = useFormik<ActivityFormValues>({
    initialValues: {
      activity_type: '',
      duration: 30,
      intensity: 'moderate',
      notes: '',
    },
    validationSchema,
    onSubmit: async (values, { setSubmitting, resetForm }) => {
      try {
        await analytics.createActivity({
          activity_type: values.activity_type,
          duration: values.duration,
          intensity: values.intensity,
          notes: values.notes,
        });

        toast({
          title: 'Activity Logged!',
          description: 'Your activity has been successfully recorded.',
          status: 'success',
          duration: 3000,
          isClosable: true,
        });

        resetForm();
        onClose();
        onActivityLogged?.();
      } catch (error: any) {
        toast({
          title: 'Error',
          description: error.response?.data?.detail || 'Failed to log activity',
          status: 'error',
          duration: 5000,
          isClosable: true,
        });
      } finally {
        setSubmitting(false);
      }
    },
  });

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="md">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>Log Today's Activity</ModalHeader>
        <ModalCloseButton />
        <form onSubmit={formik.handleSubmit}>
          <ModalBody>
            <VStack spacing={4}>
              <FormControl isInvalid={formik.touched.activity_type && !!formik.errors.activity_type}>
                <FormLabel>Activity Type</FormLabel>
                <Select
                  placeholder="Select activity type"
                  {...formik.getFieldProps('activity_type')}
                >
                  <option value="running">Running</option>
                  <option value="walking">Walking</option>
                  <option value="cycling">Cycling</option>
                  <option value="swimming">Swimming</option>
                  <option value="weight_training">Weight Training</option>
                  <option value="yoga">Yoga</option>
                  <option value="dancing">Dancing</option>
                  <option value="sports">Sports</option>
                  <option value="other">Other</option>
                </Select>
                {formik.touched.activity_type && formik.errors.activity_type && (
                  <div style={{ color: 'red', fontSize: 'sm' }}>
                    {formik.errors.activity_type}
                  </div>
                )}
              </FormControl>

              <FormControl isInvalid={formik.touched.duration && !!formik.errors.duration}>
                <FormLabel>Duration (minutes)</FormLabel>
                <Input
                  type="number"
                  min="1"
                  max="480"
                  {...formik.getFieldProps('duration')}
                />
                {formik.touched.duration && formik.errors.duration && (
                  <div style={{ color: 'red', fontSize: 'sm' }}>
                    {formik.errors.duration}
                  </div>
                )}
              </FormControl>

              <FormControl isInvalid={formik.touched.intensity && !!formik.errors.intensity}>
                <FormLabel>Intensity</FormLabel>
                <Select {...formik.getFieldProps('intensity')}>
                  <option value="low">Low</option>
                  <option value="moderate">Moderate</option>
                  <option value="high">High</option>
                  <option value="very_high">Very High</option>
                </Select>
                {formik.touched.intensity && formik.errors.intensity && (
                  <div style={{ color: 'red', fontSize: 'sm' }}>
                    {formik.errors.intensity}
                  </div>
                )}
              </FormControl>

              <FormControl isInvalid={formik.touched.notes && !!formik.errors.notes}>
                <FormLabel>Notes (optional)</FormLabel>
                <Textarea
                  placeholder="Any additional notes about your activity..."
                  rows={3}
                  {...formik.getFieldProps('notes')}
                />
                {formik.touched.notes && formik.errors.notes && (
                  <div style={{ color: 'red', fontSize: 'sm' }}>
                    {formik.errors.notes}
                  </div>
                )}
              </FormControl>
            </VStack>
          </ModalBody>

          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onClose}>
              Cancel
            </Button>
            <Button
              colorScheme="blue"
              type="submit"
              isLoading={formik.isSubmitting}
            >
              Log Activity
            </Button>
          </ModalFooter>
        </form>
      </ModalContent>
    </Modal>
  );
};

export default ActivityLogModal;
