// Service Worker registration and management

interface ServiceWorkerConfig {
  onUpdate?: (registration: ServiceWorkerRegistration) => void;
  onSuccess?: (registration: ServiceWorkerRegistration) => void;
  onOfflineReady?: () => void;
}

export const registerServiceWorker = (config: ServiceWorkerConfig = {}) => {
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker
        .register('/sw.js')
        .then((registration) => {
          console.log('Service Worker registered successfully:', registration.scope);
          config.onSuccess?.(registration);

          // Check for updates
          registration.addEventListener('updatefound', () => {
            const newWorker = registration.installing;
            if (newWorker) {
              newWorker.addEventListener('statechange', () => {
                if (newWorker.state === 'installed') {
                  if (navigator.serviceWorker.controller) {
                    // New content is available
                    config.onUpdate?.(registration);
                  } else {
                    // Content is cached for offline use
                    config.onOfflineReady?.();
                  }
                }
              });
            }
          });
        })
        .catch((error) => {
          console.error('Service Worker registration failed:', error);
        });
    });
  }
};

export const unregisterServiceWorker = () => {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready.then((registration) => {
      registration.unregister();
    });
  }
};

export const checkForUpdates = () => {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready.then((registration) => {
      registration.update();
    });
  }
};

export const getServiceWorkerRegistration = (): Promise<ServiceWorkerRegistration | null> => {
  if ('serviceWorker' in navigator) {
    return navigator.serviceWorker.ready;
  }
  return Promise.resolve(null);
};

export const isServiceWorkerSupported = (): boolean => {
  return 'serviceWorker' in navigator;
};

export const isServiceWorkerActive = (): boolean => {
  return 'serviceWorker' in navigator && navigator.serviceWorker.controller !== null;
};

export const getServiceWorkerState = (): string | null => {
  if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
    return navigator.serviceWorker.controller.state;
  }
  return null;
};

export const sendMessageToServiceWorker = (message: any) => {
  if ('serviceWorker' in navigator && navigator.serviceWorker.controller) {
    navigator.serviceWorker.controller.postMessage(message);
  }
};

export const addServiceWorkerEventListener = (event: string, callback: (event: any) => void) => {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.addEventListener(event, callback);
  }
};

export const removeServiceWorkerEventListener = (event: string, callback: (event: any) => void) => {
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.removeEventListener(event, callback);
  }
};


