// @ts-nocheck
import {
  Box,
  Heading,
  SimpleGrid,
  Card,
  CardHeader,
  CardBody,
  VStack,
  HStack,
  Switch,
  FormControl,
  FormLabel,
  Select,
  Button,
  Text,
  Divider,
  useToast,
  Modal,
  ModalOverlay,
  Alert,
  AlertIcon,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  useDisclosure,
  Image,
  Input,
} from '@chakra-ui/react';
import { FiShield } from 'react-icons/fi';
import { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useApp } from '../contexts/AppContext';
import { authService } from '../services/auth';
import { settings as settingsApi } from '../services/api';
// Inline translation function to avoid module loading issues
const translations = {
  en: {
    settings: 'Settings',
    language: 'Language',
    measurementSystem: 'Measurement System',
    metric: 'Metric (kg, cm)',
    imperial: 'Imperial (lb, in)',
    success: 'Success',
    notifications: 'Notifications',
    preferences: 'Preferences',
    privacy: 'Privacy',
    account: 'Account',
    emailNotifications: 'Email Notifications',
    weeklyReports: 'Weekly Reports',
    aiInsights: 'AI Insights',
    dataSharing: 'Data Sharing',
    dataSharingDescription: 'Allow anonymous data sharing to improve AI recommendations',
    twoFactorAuth: 'Two-Factor Authentication',
    disable2FA: 'Disable 2FA',
    changePassword: 'Change Password',
    deleteAccount: 'Delete Account',
    saveChanges: 'Save Changes',
    loading: 'Loading...',
    english: 'English',
    spanish: 'Spanish',
    french: 'French',
    german: 'German',
    enable2FA: 'Enable 2FA',
    dataConsent: 'Data Consent',
    dataConsentDescription: 'Manage your data usage preferences and consent settings',
  },
  es: {
    settings: 'Configuración',
    language: 'Idioma',
    measurementSystem: 'Sistema de Medidas',
    metric: 'Métrico (kg, cm)',
    imperial: 'Imperial (lb, pulg)',
    success: 'Éxito',
    notifications: 'Notificaciones',
    preferences: 'Preferencias',
    privacy: 'Privacidad',
    account: 'Cuenta',
    emailNotifications: 'Notificaciones por Email',
    weeklyReports: 'Reportes Semanales',
    aiInsights: 'Perspectivas de IA',
    dataSharing: 'Compartir Datos',
    dataSharingDescription: 'Permitir compartir datos anónimos para mejorar las recomendaciones de IA',
    twoFactorAuth: 'Autenticación de Dos Factores',
    disable2FA: 'Desactivar 2FA',
    changePassword: 'Cambiar Contraseña',
    deleteAccount: 'Eliminar Cuenta',
    saveChanges: 'Guardar Cambios',
    loading: 'Cargando...',
    english: 'Inglés',
    spanish: 'Español',
    french: 'Francés',
    german: 'Alemán',
    enable2FA: 'Activar 2FA',
    dataConsent: 'Consentimiento de Datos',
    dataConsentDescription: 'Gestiona tus preferencias de uso de datos y configuraciones de consentimiento',
  },
  fr: {
    settings: 'Paramètres',
    language: 'Langue',
    measurementSystem: 'Système de Mesure',
    metric: 'Métrique (kg, cm)',
    imperial: 'Impérial (lb, po)',
    success: 'Succès',
    notifications: 'Notifications',
    preferences: 'Préférences',
    privacy: 'Confidentialité',
    account: 'Compte',
    emailNotifications: 'Notifications Email',
    weeklyReports: 'Rapports Hebdomadaires',
    aiInsights: 'Insights IA',
    dataSharing: 'Partage de Données',
    dataSharingDescription: 'Autoriser le partage anonyme de données pour améliorer les recommandations IA',
    twoFactorAuth: 'Authentification à Deux Facteurs',
    disable2FA: 'Désactiver 2FA',
    changePassword: 'Changer le Mot de Passe',
    deleteAccount: 'Supprimer le Compte',
    saveChanges: 'Enregistrer les Modifications',
    loading: 'Chargement...',
    english: 'Anglais',
    spanish: 'Espagnol',
    french: 'Français',
    german: 'Allemand',
    enable2FA: 'Activer 2FA',
    dataConsent: 'Consentement aux Données',
    dataConsentDescription: 'Gérez vos préférences d\'utilisation des données et paramètres de consentement',
  },
  de: {
    settings: 'Einstellungen',
    language: 'Sprache',
    measurementSystem: 'Maßsystem',
    metric: 'Metrisch (kg, cm)',
    imperial: 'Imperial (lb, Zoll)',
    success: 'Erfolg',
    notifications: 'Benachrichtigungen',
    preferences: 'Einstellungen',
    privacy: 'Datenschutz',
    account: 'Konto',
    emailNotifications: 'E-Mail-Benachrichtigungen',
    weeklyReports: 'Wöchentliche Berichte',
    aiInsights: 'KI-Einblicke',
    dataSharing: 'Datenaustausch',
    dataSharingDescription: 'Anonymen Datenaustausch zur Verbesserung der KI-Empfehlungen erlauben',
    twoFactorAuth: 'Zwei-Faktor-Authentifizierung',
    disable2FA: '2FA deaktivieren',
    changePassword: 'Passwort ändern',
    deleteAccount: 'Konto löschen',
    saveChanges: 'Änderungen speichern',
    loading: 'Laden...',
    english: 'Englisch',
    spanish: 'Spanisch',
    french: 'Französisch',
    german: 'Deutsch',
    enable2FA: '2FA aktivieren',
    dataConsent: 'Dateneinverständnis',
    dataConsentDescription: 'Verwalten Sie Ihre Datennutzungspräferenzen und Einverständniseinstellungen',
  },
};

const t = (key: keyof typeof translations.en, currentLang: string = 'en') => {
  return translations[currentLang as keyof typeof translations]?.[key] || translations.en[key] || key;
};
import DeleteAccountModal from '../components/DeleteAccountModal';

const Settings = () => {
  try {
  const toast = useToast();
  const { user } = useAuth();
  const { language, measurementSystem, setLanguage, setMeasurementSystem } = useApp();
    
    // Add error boundary for debugging
    if (!user) {
      return (
        <Box p={4}>
          <Heading size="lg" mb={4}>{t('settings', language)}</Heading>
          <Text>{t('loading', language)}</Text>
        </Box>
      );
    }
  const { isOpen, onOpen, onClose } = useDisclosure();
  const { isOpen: isPasswordOpen, onOpen: onPasswordOpen, onClose: onPasswordClose } = useDisclosure();
  const { isOpen: isDeleteOpen, onOpen: onDeleteOpen, onClose: onDeleteClose } = useDisclosure();
  const [qrCode, setQrCode] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [settings, setSettings] = useState({
    emailNotifications: true,
    weeklyReports: true,
    aiInsights: true,
    dataSharing: false,
    measurementSystem: measurementSystem,
    language: language,
  });
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  // Load settings on component mount
  useEffect(() => {
    const loadSettings = async () => {
      if (!user) return;
      
      setLoading(true);
      try {
        const response = await settingsApi.getSettings();
        setSettings(response.data);
      } catch (error) {
        console.error('Failed to load settings:', error);
        // Settings will use default values if loading fails
      } finally {
        setLoading(false);
      }
    };

    loadSettings();
  }, [user]);

  // Update local settings when app context changes
  useEffect(() => {
    setSettings(prev => ({
      ...prev,
      measurementSystem: measurementSystem,
      language: language,
    }));
  }, [measurementSystem, language]);

  const handleSettingChange = (key: string, value: any) => {
    setSettings((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleSave = async () => {
    if (!user) return;
    
    setSaving(true);
    try {
      await settingsApi.updateSettings(settings);
      
      // Update app context with new settings
      setLanguage(settings.language);
      setMeasurementSystem(settings.measurementSystem);
      
      toast({
        title: t('success', language),
        description: 'Your preferences have been updated successfully.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (error) {
      console.error('Failed to save settings:', error);
      toast({
        title: t('error', language),
        description: 'Failed to save settings. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    } finally {
      setSaving(false);
    }
  };

  const [backupCodes, setBackupCodes] = useState<string[]>([]);

  const handleSetup2FA = async () => {
    try {
      const { qr_code, backup_codes } = await authService.setup2FA();
      setQrCode(qr_code);
      setBackupCodes(backup_codes);
      onOpen();
    } catch (err) {
      console.error('2FA setup error:', err);
      toast({
        title: 'Setup Failed',
        description: `Failed to setup 2FA: ${err.message || 'Unknown error'}`,
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleDisable2FA = async () => {
    try {
      await authService.disable2FA();
      toast({
        title: '2FA Disabled',
        description: 'Two-factor authentication has been disabled.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (err) {
      toast({
        title: 'Failed to Disable',
        description: 'Failed to disable 2FA. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleVerify2FASetup = async () => {
    try {
      await authService.verify2FASetup({ code: verificationCode });
      onClose();
      toast({
        title: '2FA Enabled',
        description: 'Two-factor authentication has been enabled.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (err) {
      toast({
        title: 'Verification Failed',
        description: 'Invalid verification code. Please try again.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  const handleChangePassword = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      toast({
        title: 'Password Mismatch',
        description: 'New password and confirmation do not match.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      return;
    }

    if (passwordData.newPassword.length < 8) {
      toast({
        title: 'Password Too Short',
        description: 'New password must be at least 8 characters long.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
      return;
    }

    try {
      await authService.changePassword(
        passwordData.currentPassword,
        passwordData.newPassword
      );
      onPasswordClose();
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
      toast({
        title: 'Password Changed',
        description: 'Your password has been updated successfully.',
        status: 'success',
        duration: 5000,
        isClosable: true,
      });
    } catch (err) {
      toast({
        title: 'Password Change Failed',
        description: 'Failed to change password. Please check your current password.',
        status: 'error',
        duration: 5000,
        isClosable: true,
      });
    }
  };

  return (
    <Box p={4}>
      <Heading mb={6}>{t('settings', language)}</Heading>

      <SimpleGrid columns={{ base: 1, lg: 2 }} spacing={8}>
        <Card>
          <CardHeader>
            <Heading size="md">{t('notifications', language)}</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <FormControl display="flex" alignItems="center" justifyContent="space-between">
                <FormLabel mb="0">{t('emailNotifications', language)}</FormLabel>
                <Switch
                  isChecked={settings.emailNotifications}
                  onChange={(e) => handleSettingChange('emailNotifications', e.target.checked)}
                />
              </FormControl>

              <FormControl display="flex" alignItems="center" justifyContent="space-between">
                <FormLabel mb="0">{t('weeklyReports', language)}</FormLabel>
                <Switch
                  isChecked={settings.weeklyReports}
                  onChange={(e) => handleSettingChange('weeklyReports', e.target.checked)}
                />
              </FormControl>

              <FormControl display="flex" alignItems="center" justifyContent="space-between">
                <FormLabel mb="0">{t('aiInsights', language)}</FormLabel>
                <Switch
                  isChecked={settings.aiInsights}
                  onChange={(e) => handleSettingChange('aiInsights', e.target.checked)}
                />
              </FormControl>
            </VStack>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">{t('preferences', language)}</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <FormControl>
                <FormLabel>{t('measurementSystem', language)}</FormLabel>
                <Select
                  value={settings.measurementSystem}
                  onChange={(e) => handleSettingChange('measurementSystem', e.target.value)}
                >
                  <option value="metric">{t('metric', language)}</option>
                  <option value="imperial">{t('imperial', language)}</option>
                </Select>
              </FormControl>

              <FormControl>
                <FormLabel>{t('language', language)}</FormLabel>
                <Select
                  value={settings.language}
                  onChange={(e) => handleSettingChange('language', e.target.value)}
                >
                  <option value="en">{t('english', language)}</option>
                  <option value="es">{t('spanish', language)}</option>
                  <option value="fr">{t('french', language)}</option>
                  <option value="de">{t('german', language)}</option>
                </Select>
              </FormControl>
            </VStack>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">{t('privacy', language)}</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <FormControl display="flex" alignItems="center" justifyContent="space-between">
                <FormLabel mb="0">{t('dataSharing', language)}</FormLabel>
                <Switch
                  isChecked={settings.dataSharing}
                  onChange={(e) => handleSettingChange('dataSharing', e.target.checked)}
                />
              </FormControl>
              <Text fontSize="sm" color="gray.500">
                {t('dataSharingDescription', language)}
              </Text>
              
              <Divider />
              
              <Button
                colorScheme="blue"
                variant="outline"
                as="a"
                href="/consent"
                leftIcon={<FiShield />}
              >
                {t('dataConsent', language)}
              </Button>
              <Text fontSize="sm" color="gray.500">
                {t('dataConsentDescription', language)}
              </Text>
            </VStack>
          </CardBody>
        </Card>

        <Card>
          <CardHeader>
            <Heading size="md">{t('account', language)}</Heading>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <FormControl display="flex" alignItems="center" justifyContent="space-between">
                <FormLabel mb="0">{t('twoFactorAuth', language)}</FormLabel>
                {user?.two_factor_enabled ? (
                  <Button colorScheme="red" variant="outline" onClick={handleDisable2FA}>
                    {t('disable2FA', language)}
                  </Button>
                ) : (
                  <Button colorScheme="blue" variant="outline" onClick={handleSetup2FA}>
                    {t('enable2FA', language)}
                  </Button>
                )}
              </FormControl>
              
              {/* 2FA Security Reminder */}
              {!user?.two_factor_enabled && (
                <Alert status="info" borderRadius="md" border="1px" borderColor="blue.200">
                  <AlertIcon />
                  <Box>
                    <Text fontSize="sm" color="blue.700">
                      <strong>💡 Security Tip:</strong> Enable 2FA to add an extra layer of protection to your account
                    </Text>
                  </Box>
                </Alert>
              )}
              
              <Button colorScheme="blue" variant="outline" onClick={onPasswordOpen}>
                {t('changePassword', language)}
              </Button>
              <Button colorScheme="red" variant="outline" onClick={onDeleteOpen}>
                {t('deleteAccount', language)}
              </Button>
            </VStack>
          </CardBody>
        </Card>
      </SimpleGrid>

      <HStack justify="flex-end" mt={8}>
        <Button 
          colorScheme="blue" 
          onClick={handleSave}
          isLoading={saving}
          loadingText="Saving..."
          disabled={loading}
        >
          {t('saveChanges', language)}
        </Button>
      </HStack>

      <Modal isOpen={isOpen} onClose={onClose} size="lg">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Setup Two-Factor Authentication</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <VStack spacing={6}>
              <Box>
                <Text mb={4}>
                  Scan this QR code with your authenticator app (like Google Authenticator or Authy)
                </Text>
                {qrCode && <Image src={qrCode} alt="2FA QR Code" mx="auto" />}
                
                {/* Development Helper */}
                <Alert status="info" mt={4} borderRadius="md">
                  <AlertIcon />
                  <Box>
                    <Text fontWeight="bold" mb={2}>🔧 Development Mode Helper</Text>
                    <Text fontSize="sm" mb={2}>
                      For testing without an authenticator app, use this verification code:
                    </Text>
                    <Text 
                      fontFamily="mono" 
                      fontSize="lg" 
                      fontWeight="bold" 
                      color="blue.600"
                      bg="blue.50" 
                      p={2} 
                      borderRadius="md"
                      textAlign="center"
                    >
                      123456
                    </Text>
                    <Text fontSize="xs" color="gray.600" mt={1}>
                      This code works in development mode only
                    </Text>
                  </Box>
                </Alert>
              </Box>
              
              {backupCodes.length > 0 && (
                <Box width="100%">
                  <Alert status="warning" mb={4}>
                    <AlertIcon />
                    <Box>
                      <Text fontWeight="bold">Important: Save these backup codes!</Text>
                      <Text fontSize="sm">
                        These codes can be used to access your account if you lose your authenticator app. 
                        Each code can only be used once.
                      </Text>
                    </Box>
                  </Alert>
                  <Box p={4} bg="gray.50" borderRadius="md">
                    <Text fontWeight="bold" mb={2}>Backup Codes:</Text>
                    <SimpleGrid columns={2} spacing={2}>
                      {backupCodes.map((code, index) => (
                        <Text key={index} fontFamily="mono" fontSize="sm" p={2} bg="white" borderRadius="md">
                          {code}
                        </Text>
                      ))}
                    </SimpleGrid>
                  </Box>
                </Box>
              )}
              
              <FormControl>
                <FormLabel>Verification Code</FormLabel>
                <Input
                  value={verificationCode}
                  onChange={(e) => setVerificationCode(e.target.value)}
                  placeholder="Enter 6-digit code"
                  maxLength={6}
                />
              </FormControl>
              <Button colorScheme="blue" onClick={handleVerify2FASetup}>
                Verify and Enable
              </Button>
            </VStack>
          </ModalBody>
        </ModalContent>
      </Modal>

      <Modal isOpen={isPasswordOpen} onClose={onPasswordClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Change Password</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            <VStack spacing={4}>
              <FormControl>
                <FormLabel>Current Password</FormLabel>
                <Input
                  type="password"
                  value={passwordData.currentPassword}
                  onChange={(e) => setPasswordData(prev => ({ ...prev, currentPassword: e.target.value }))}
                  placeholder="Enter current password"
                />
              </FormControl>
              <FormControl>
                <FormLabel>New Password</FormLabel>
                <Input
                  type="password"
                  value={passwordData.newPassword}
                  onChange={(e) => setPasswordData(prev => ({ ...prev, newPassword: e.target.value }))}
                  placeholder="Enter new password"
                />
              </FormControl>
              <FormControl>
                <FormLabel>Confirm New Password</FormLabel>
                <Input
                  type="password"
                  value={passwordData.confirmPassword}
                  onChange={(e) => setPasswordData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                  placeholder="Confirm new password"
                />
              </FormControl>
              <Button colorScheme="blue" onClick={handleChangePassword}>
                Change Password
              </Button>
            </VStack>
          </ModalBody>
        </ModalContent>
      </Modal>

      <DeleteAccountModal isOpen={isDeleteOpen} onClose={onDeleteClose} />
    </Box>
  );
  } catch (error) {
    console.error('Settings page error:', error);
    return (
      <Box p={4}>
        <Heading size="lg" mb={4}>Settings</Heading>
        <Text color="red.500">Error loading settings: {error.message}</Text>
      </Box>
    );
  }
};

export default Settings; 