// Suppress non-critical console warnings
export const suppressNonCriticalWarnings = () => {
  // Suppress tracking prevention warnings for external images
  const originalWarn = console.warn;
  console.warn = (...args) => {
    const message = args[0];
    if (typeof message === 'string' && message.includes('Tracking Prevention blocked access to storage')) {
      return; // Suppress tracking prevention warnings
    }
    originalWarn.apply(console, args);
  };

  // Suppress image load errors for external domains
  const originalError = console.error;
  console.error = (...args) => {
    const message = args[0];
    if (typeof message === 'string' && (
      message.includes('net::ERR_NAME_NOT_RESOLVED') ||
      message.includes('net::ERR_CERT_DATE_INVALID') ||
      message.includes('net::ERR_BLOCKED_BY_RESPONSE') ||
      message.includes('Failed to load resource') ||
      message.includes('403 (Forbidden)') ||
      message.includes('404 (Not Found)') ||
      message.includes('400 (Bad Request)') ||
      message.includes('500 (Internal Server Error)')
    )) {
      return; // Suppress network-related image errors
    }
    originalError.apply(console, args);
  };

  // Override the global error handler to suppress image loading errors
  const originalOnError = window.onerror;
  window.onerror = (message, source, lineno, colno, error) => {
    if (typeof message === 'string' && (
      message.includes('net::ERR_NAME_NOT_RESOLVED') ||
      message.includes('net::ERR_CERT_DATE_INVALID') ||
      message.includes('net::ERR_BLOCKED_BY_RESPONSE') ||
      message.includes('403 (Forbidden)') ||
      message.includes('404 (Not Found)') ||
      message.includes('400 (Bad Request)') ||
      message.includes('500 (Internal Server Error)')
    )) {
      return true; // Prevent the error from being logged
    }
    if (originalOnError) {
      return originalOnError(message, source, lineno, colno, error);
    }
    return false;
  };

  // Override console.log to filter out image loading errors
  const originalLog = console.log;
  console.log = (...args) => {
    const message = args[0];
    if (typeof message === 'string' && (
      message.includes('net::ERR_NAME_NOT_RESOLVED') ||
      message.includes('net::ERR_CERT_DATE_INVALID') ||
      message.includes('net::ERR_BLOCKED_BY_RESPONSE') ||
      message.includes('403 (Forbidden)') ||
      message.includes('404 (Not Found)') ||
      message.includes('400 (Bad Request)') ||
      message.includes('500 (Internal Server Error)')
    )) {
      return; // Suppress network-related image errors
    }
    originalLog.apply(console, args);
  };
};

// Initialize suppression
suppressNonCriticalWarnings();
