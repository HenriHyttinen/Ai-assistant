import { useState, useEffect, useCallback } from 'react';
import { useToast } from '@chakra-ui/react';

interface OfflineStatus {
  isOffline: boolean;
  wasOffline: boolean;
  lastOnline: Date | null;
  lastOffline: Date | null;
  connectionType: string | null;
  isSlowConnection: boolean;
}

export const useOffline = () => {
  const [offlineStatus, setOfflineStatus] = useState<OfflineStatus>({
    isOffline: !navigator.onLine,
    wasOffline: false,
    lastOnline: null,
    lastOffline: null,
    connectionType: null,
    isSlowConnection: false,
  });

  const toast = useToast();

  // Check connection type and speed
  const checkConnectionInfo = useCallback(() => {
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      const connectionType = connection.effectiveType || connection.type || 'unknown';
      const isSlowConnection = connection.effectiveType === 'slow-2g' || 
                              connection.effectiveType === '2g' ||
                              connection.downlink < 1;

      setOfflineStatus(prev => ({
        ...prev,
        connectionType,
        isSlowConnection,
      }));
    }
  }, []);

  // Handle online event
  const handleOnline = useCallback(() => {
    const now = new Date();
    setOfflineStatus(prev => ({
      ...prev,
      isOffline: false,
      wasOffline: prev.isOffline,
      lastOnline: now,
    }));

    toast({
      title: 'Back Online',
      description: 'Your connection has been restored. Syncing data...',
      status: 'success',
      duration: 3000,
      isClosable: true,
    });

    // Trigger sync when back online
    if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
      navigator.serviceWorker.ready.then(registration => {
        registration.sync.register('sync-recipes');
        registration.sync.register('sync-meal-plans');
      });
    }
  }, [toast]);

  // Handle offline event
  const handleOffline = useCallback(() => {
    const now = new Date();
    setOfflineStatus(prev => ({
      ...prev,
      isOffline: true,
      wasOffline: false,
      lastOffline: now,
    }));

    toast({
      title: 'You\'re Offline',
      description: 'Some features may be limited. Your data will sync when you\'re back online.',
      status: 'warning',
      duration: 5000,
      isClosable: true,
    });
  }, [toast]);

  // Handle connection change
  const handleConnectionChange = useCallback(() => {
    checkConnectionInfo();
  }, [checkConnectionInfo]);

  useEffect(() => {
    // Initial connection check
    checkConnectionInfo();

    // Add event listeners
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      connection.addEventListener('change', handleConnectionChange);
    }

    // Cleanup
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
      
      if ('connection' in navigator) {
        const connection = (navigator as any).connection;
        connection.removeEventListener('change', handleConnectionChange);
      }
    };
  }, [handleOnline, handleOffline, handleConnectionChange, checkConnectionInfo]);

  return {
    ...offlineStatus,
    // Helper functions
    isOnline: !offlineStatus.isOffline,
    hasBeenOffline: offlineStatus.wasOffline,
    getConnectionStatus: () => {
      if (offlineStatus.isOffline) return 'offline';
      if (offlineStatus.isSlowConnection) return 'slow';
      return 'online';
    },
    getConnectionMessage: () => {
      if (offlineStatus.isOffline) {
        return 'You\'re currently offline. Some features may be limited.';
      }
      if (offlineStatus.isSlowConnection) {
        return 'Your connection is slow. Some features may take longer to load.';
      }
      return 'You\'re online with a good connection.';
    },
  };
};

export default useOffline;


