// Utility function to safely extract error message from various error types
export const getErrorMessage = (error: any): string => {
  if (!error) return '';
  if (typeof error === 'string') return error;
  if (error.message) return error.message;
  if (error.msg) return error.msg;
  if (typeof error === 'object') {
    try {
      return JSON.stringify(error);
    } catch {
      return 'An error occurred';
    }
  }
  return String(error);
};
