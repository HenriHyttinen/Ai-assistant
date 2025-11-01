import React from 'react';
import { useResponsive } from '../hooks/useResponsive';
import MainLayout from '../layouts/MainLayout';
import MobileLayout from './MobileLayout';
import MobileBottomNav from './MobileBottomNav';

interface ResponsiveLayoutProps {
  children: React.ReactNode;
}

const ResponsiveLayout: React.FC<ResponsiveLayoutProps> = ({ children }) => {
  const { isMobile } = useResponsive();

  if (isMobile) {
    return (
      <>
        <MobileLayout>
          {children}
        </MobileLayout>
        <MobileBottomNav />
      </>
    );
  }

  return (
    <MainLayout>
      {children}
    </MainLayout>
  );
};

export default ResponsiveLayout;







