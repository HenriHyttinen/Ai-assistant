// @ts-nocheck
import { Navigate, useLocation } from 'react-router-dom';
import { useSupabaseAuth } from '../contexts/SupabaseAuthContext';
import { Spinner, Center } from '@chakra-ui/react';
import { useEffect, useState } from 'react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  require2FA?: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, require2FA = false }) => {
  const { user, loading, session } = useSupabaseAuth();
  const location = useLocation();
  const [hasToken, setHasToken] = useState(false);

  // Check for stored token as fallback
  useEffect(() => {
    const token = localStorage.getItem('token');
    const supabaseSession = sessionStorage.getItem('supabase.auth.token');
    setHasToken(!!(token || supabaseSession));
  }, [session]);

  if (loading) {
    return (
      <Center h="100vh">
        <Spinner
          thickness="4px"
          speed="0.65s"
          emptyColor="gray.200"
          color="blue.500"
          size="xl"
        />
      </Center>
    );
  }

  // Allow access if user exists OR if we have a token (backend auth might still be valid)
  // Only redirect if both user and session are null AND no token exists
  if (!user && !session && !hasToken) {
    // Redirect to login page but save the attempted url
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check if email is verified (Supabase handles this automatically)
  // Only check if user exists
  if (user && !user.email_confirmed_at) {
    return <Navigate to="/verify-email" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute; 