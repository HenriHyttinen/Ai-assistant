// @ts-nocheck
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { Spinner, Center } from '@chakra-ui/react';

interface ProtectedRouteProps {
  children: React.ReactNode;
  require2FA?: boolean;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, require2FA = false }) => {
  const { user, loading } = useAuth();
  const location = useLocation();

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

  if (!user) {
    // Redirect to login page but save the attempted url
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  // Check if email is verified
  if (!user.is_verified) {
    return <Navigate to="/verify-email" state={{ from: location }} replace />;
  }

  if (require2FA && !user.two_factor_enabled) {
    // Redirect to 2FA setup if required but not enabled
    return <Navigate to="/settings" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute; 