import { useState, useCallback } from 'react';

interface UseFormSubmitState {
  loading: boolean;
  error: string | null;
  success: boolean;
}

interface UseFormSubmitResult extends UseFormSubmitState {
  submit: (data: any) => Promise<void>;
  reset: () => void;
}

export function useFormSubmit<T>(
  submitFunction: (data: T) => Promise<any>
): UseFormSubmitResult {
  const [state, setState] = useState<UseFormSubmitState>({
    loading: false,
    error: null,
    success: false,
  });

  const submit = useCallback(
    async (data: T) => {
      try {
        setState({ loading: true, error: null, success: false });
        await submitFunction(data);
        setState({ loading: false, error: null, success: true });
      } catch (error: any) {
        setState({
          loading: false,
          error: error.response?.data?.message || 'An error occurred',
          success: false,
        });
        throw error;
      }
    },
    [submitFunction]
  );

  const reset = useCallback(() => {
    setState({ loading: false, error: null, success: false });
  }, []);

  return {
    ...state,
    submit,
    reset,
  };
}

export default useFormSubmit; 