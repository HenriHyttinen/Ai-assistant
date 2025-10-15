import { useState, useCallback } from 'react';
import type { AxiosError } from 'axios';

interface UseApiState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

interface UseApiResult<T> extends UseApiState<T> {
  execute: (...args: any[]) => Promise<void>;
  reset: () => void;
}

export function useApi<T>(
  apiFunction: (...args: any[]) => Promise<{ data: T }>
): UseApiResult<T> {
  const [state, setState] = useState<UseApiState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const execute = useCallback(
    async (...args: any[]) => {
      try {
        setState((prev) => ({ ...prev, loading: true, error: null }));
        const response = await apiFunction(...args);
        setState({ data: response.data, loading: false, error: null });
      } catch (error) {
        const axiosError = error as AxiosError;
        setState({
          data: null,
          loading: false,
          error: axiosError.response?.data?.message || 'An error occurred',
        });
        throw error;
      }
    },
    [apiFunction]
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return {
    ...state,
    execute,
    reset,
  };
}

export default useApi; 