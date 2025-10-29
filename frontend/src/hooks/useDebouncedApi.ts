import { useState, useEffect, useRef, useCallback } from 'react';

interface UseDebouncedApiOptions {
  delay?: number;
  immediate?: boolean;
  onSuccess?: (data: any) => void;
  onError?: (error: any) => void;
}

export function useDebouncedApi<T>(
  apiFunction: (...args: any[]) => Promise<T>,
  dependencies: any[],
  options: UseDebouncedApiOptions = {}
) {
  const {
    delay = 300,
    immediate = false,
    onSuccess,
    onError
  } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const timeoutRef = useRef<NodeJS.Timeout>();
  const requestIdRef = useRef<number>(0);

  const executeApi = useCallback(async (...args: any[]) => {
    const currentRequestId = ++requestIdRef.current;
    
    try {
      setLoading(true);
      setError(null);
      
      const result = await apiFunction(...args);
      
      // Only update if this is still the latest request
      if (currentRequestId === requestIdRef.current) {
        setData(result);
        onSuccess?.(result);
      }
      
    } catch (err: any) {
      // Only update if this is still the latest request
      if (currentRequestId === requestIdRef.current) {
        const errorMessage = err.message || 'An error occurred';
        setError(errorMessage);
        onError?.(err);
      }
    } finally {
      // Only update if this is still the latest request
      if (currentRequestId === requestIdRef.current) {
        setLoading(false);
      }
    }
  }, [apiFunction, onSuccess, onError]);

  const debouncedExecute = useCallback((...args: any[]) => {
    // Clear existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Set new timeout
    timeoutRef.current = setTimeout(() => {
      executeApi(...args);
    }, delay);
  }, [executeApi, delay]);

  // Execute immediately if requested
  useEffect(() => {
    if (immediate) {
      executeApi();
    }
  }, [immediate, executeApi]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  return {
    data,
    loading,
    error,
    execute: debouncedExecute,
    executeImmediate: executeApi,
    reset: () => {
      setData(null);
      setError(null);
      setLoading(false);
    }
  };
}




