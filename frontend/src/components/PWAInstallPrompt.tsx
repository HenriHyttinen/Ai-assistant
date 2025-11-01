import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Text,
  HStack,
  VStack,
  Icon,
  useColorModeValue,
  useBreakpointValue,
  Collapse,
  IconButton,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
} from '@chakra-ui/react';
import { FiDownload, FiX, FiSmartphone, FiMonitor } from 'react-icons/fi';

interface BeforeInstallPromptEvent extends Event {
  prompt(): Promise<void>;
  userChoice: Promise<{ outcome: 'accepted' | 'dismissed' }>;
}

const PWAInstallPrompt: React.FC = () => {
  const [deferredPrompt, setDeferredPrompt] = useState<BeforeInstallPromptEvent | null>(null);
  const [showInstallPrompt, setShowInstallPrompt] = useState(false);
  const [isInstalled, setIsInstalled] = useState(false);
  const [isIOS, setIsIOS] = useState(false);
  const [isStandalone, setIsStandalone] = useState(false);

  const isMobile = useBreakpointValue({ base: true, md: false });
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.600', 'gray.300');

  useEffect(() => {
    // Check if app is already installed
    const checkInstallStatus = () => {
      // Check if running in standalone mode
      const isStandaloneMode = window.matchMedia('(display-mode: standalone)').matches ||
                              (window.navigator as any).standalone ||
                              document.referrer.includes('android-app://');
      setIsStandalone(isStandaloneMode);

      // Check if it's iOS
      const iOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
      setIsIOS(iOS);

      // Check if already installed
      if (isStandaloneMode) {
        setIsInstalled(true);
        setShowInstallPrompt(false);
      }
    };

    checkInstallStatus();

    // Listen for beforeinstallprompt event
    const handleBeforeInstallPrompt = (e: Event) => {
      e.preventDefault();
      setDeferredPrompt(e as BeforeInstallPromptEvent);
      setShowInstallPrompt(true);
    };

    // Listen for appinstalled event
    const handleAppInstalled = () => {
      setIsInstalled(true);
      setShowInstallPrompt(false);
      setDeferredPrompt(null);
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    window.addEventListener('appinstalled', handleAppInstalled);

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
      window.removeEventListener('appinstalled', handleAppInstalled);
    };
  }, []);

  const handleInstallClick = async () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      
      if (outcome === 'accepted') {
        console.log('User accepted the install prompt');
      } else {
        console.log('User dismissed the install prompt');
      }
      
      setDeferredPrompt(null);
      setShowInstallPrompt(false);
    }
  };

  const handleDismiss = () => {
    setShowInstallPrompt(false);
    // Store dismissal in localStorage to avoid showing again for a while
    localStorage.setItem('pwa-install-dismissed', Date.now().toString());
  };

  // Don't show if already installed or if user recently dismissed
  if (isInstalled || isStandalone) {
    return null;
  }

  // Check if user recently dismissed
  const dismissedTime = localStorage.getItem('pwa-install-dismissed');
  if (dismissedTime) {
    const daysSinceDismissed = (Date.now() - parseInt(dismissedTime)) / (1000 * 60 * 60 * 24);
    if (daysSinceDismissed < 7) { // Don't show for 7 days
      return null;
    }
  }

  // Don't show on iOS if no deferred prompt (iOS doesn't support beforeinstallprompt)
  if (isIOS && !deferredPrompt) {
    return null;
  }

  return (
    <Collapse in={showInstallPrompt}>
      <Box
        position="fixed"
        bottom={isMobile ? 20 : 4}
        left={isMobile ? 4 : 4}
        right={isMobile ? 4 : 'auto'}
        maxW={isMobile ? 'full' : '400px'}
        bg={bgColor}
        border="1px"
        borderColor={borderColor}
        borderRadius="lg"
        boxShadow="lg"
        zIndex={1000}
        p={4}
      >
        <VStack spacing={3} align="stretch">
          <HStack justify="space-between" align="start">
            <HStack spacing={3}>
              <Icon
                as={isMobile ? FiSmartphone : FiMonitor}
                boxSize={6}
                color="blue.500"
              />
              <VStack align="start" spacing={1}>
                <Text fontWeight="semibold" fontSize="md">
                  Install App
                </Text>
                <Text fontSize="sm" color={textColor}>
                  {isMobile 
                    ? 'Add to home screen for quick access'
                    : 'Install for better experience'
                  }
                </Text>
              </VStack>
            </HStack>
            <IconButton
              aria-label="Dismiss install prompt"
              icon={<FiX />}
              size="sm"
              variant="ghost"
              onClick={handleDismiss}
            />
          </HStack>

          {isIOS && !deferredPrompt && (
            <Alert status="info" size="sm" borderRadius="md">
              <AlertIcon />
              <Box>
                <AlertTitle fontSize="sm">iOS Installation</AlertTitle>
                <AlertDescription fontSize="xs">
                  Tap the share button and select "Add to Home Screen"
                </AlertDescription>
              </Box>
            </Alert>
          )}

          <HStack spacing={2}>
            <Button
              size="sm"
              colorScheme="blue"
              leftIcon={<FiDownload />}
              onClick={handleInstallClick}
              flex={1}
            >
              Install
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={handleDismiss}
            >
              Maybe Later
            </Button>
          </HStack>
        </VStack>
      </Box>
    </Collapse>
  );
};

export default PWAInstallPrompt;







