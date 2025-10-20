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
import { useApp } from '../contexts/AppContext';
import { t } from '../utils/translations';

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
  performed_at: string; // ISO datetime-local string
}

const ActivityLogModal = ({ isOpen, onClose, onActivityLogged }: ActivityLogModalProps) => {
  const { language } = useApp();
  const toast = useToast();

  const getValidationSchema = (language: string) => Yup.object({
    activity_type: Yup.string().required(t('activityTypeRequired' as any, language)),
    duration: Yup.number()
      .min(1, t('durationMin' as any, language))
      .max(480, t('durationMax' as any, language))
      .required(t('durationRequired' as any, language)),
    intensity: Yup.string().required(t('intensityRequired' as any, language)),
    notes: Yup.string().max(500, t('notesMaxLength' as any, language)),
  });

  const formik = useFormik<ActivityFormValues>({
    initialValues: {
      activity_type: '',
      duration: 30,
      intensity: 'moderate',
      notes: '',
      performed_at: new Date().toISOString().slice(0,16),
    },
    validationSchema: getValidationSchema(language),
    onSubmit: async (values, { setSubmitting, resetForm }) => {
      try {
        await analytics.createActivity({
          activity_type: values.activity_type,
          duration: values.duration,
          intensity: values.intensity,
          notes: values.notes,
          performed_at: values.performed_at ? new Date(values.performed_at).toISOString() : undefined,
        });

        toast({
          title: t('activityLoggedSuccess' as any, language),
          description: t('activityLoggedSuccess' as any, language),
          status: 'success',
          duration: 3000,
          isClosable: true,
        });

        resetForm();
        onClose();
        onActivityLogged?.();
      } catch (error: any) {
        toast({
          title: t('error' as any, language),
          description: error.response?.data?.detail || t('activityLoggedError' as any, language),
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
        <ModalHeader>{t('logTodaysActivity' as any, language)}</ModalHeader>
        <ModalCloseButton />
        <form onSubmit={formik.handleSubmit}>
          <ModalBody>
            <VStack spacing={4}>
              <FormControl isInvalid={formik.touched.activity_type && !!formik.errors.activity_type}>
                <FormLabel>{t('activityType' as any, language)}</FormLabel>
                <Select
                  placeholder={t('selectActivity' as any, language)}
                  {...formik.getFieldProps('activity_type')}
                >
                  <option value="running">{t('running' as any, language)}</option>
                  <option value="walking">{t('walking' as any, language)}</option>
                  <option value="cycling">{t('cycling' as any, language)}</option>
                  <option value="swimming">{t('swimming' as any, language)}</option>
                  <option value="weight_training">{t('weightTraining' as any, language)}</option>
                  <option value="yoga">{t('yoga' as any, language)}</option>
                  <option value="dancing">{t('dancing' as any, language)}</option>
                  <option value="sports">{t('sports' as any, language)}</option>
                  <option value="other">{t('other' as any, language)}</option>
                </Select>
                {formik.touched.activity_type && formik.errors.activity_type && (
                  <div style={{ color: 'red', fontSize: 'sm' }}>
                    {formik.errors.activity_type}
                  </div>
                )}
              </FormControl>

              <FormControl>
                <FormLabel>{t('performedAt' as any, language)}</FormLabel>
                <Input
                  type="datetime-local"
                  {...formik.getFieldProps('performed_at')}
                />
              </FormControl>

              <FormControl isInvalid={formik.touched.duration && !!formik.errors.duration}>
                <FormLabel>{t('duration' as any, language)}</FormLabel>
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
                <FormLabel>{t('intensity' as any, language)}</FormLabel>
                <Select {...formik.getFieldProps('intensity')}>
                  <option value="low">{t('low' as any, language)}</option>
                  <option value="moderate">{t('moderate' as any, language)}</option>
                  <option value="high">{t('high' as any, language)}</option>
                  <option value="very_high">{t('veryHigh' as any, language)}</option>
                </Select>
                {formik.touched.intensity && formik.errors.intensity && (
                  <div style={{ color: 'red', fontSize: 'sm' }}>
                    {formik.errors.intensity}
                  </div>
                )}
              </FormControl>

              <FormControl isInvalid={formik.touched.notes && !!formik.errors.notes}>
                <FormLabel>{t('notes' as any, language)}</FormLabel>
                <Textarea
                  placeholder={t('notesPlaceholder' as any, language)}
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
              {t('cancel' as any, language)}
            </Button>
            <Button
              colorScheme="blue"
              type="submit"
              isLoading={formik.isSubmitting}
            >
              {t('logActivity' as any, language)}
            </Button>
          </ModalFooter>
        </form>
      </ModalContent>
    </Modal>
  );
};

export default ActivityLogModal;
