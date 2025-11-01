import { useBreakpointValue, useMediaQuery } from '@chakra-ui/react';
import { useState, useEffect } from 'react';

interface ResponsiveConfig {
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  isSmallScreen: boolean;
  isLargeScreen: boolean;
  screenWidth: number;
  screenHeight: number;
  orientation: 'portrait' | 'landscape';
}

export const useResponsive = (): ResponsiveConfig => {
  const [screenSize, setScreenSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 0,
    height: typeof window !== 'undefined' ? window.innerHeight : 0,
  });

  const isMobile = useBreakpointValue({ base: true, md: false }) || screenSize.width < 768;
  const isTablet = useBreakpointValue({ base: false, md: true, lg: false }) || (screenSize.width >= 768 && screenSize.width < 1024);
  const isDesktop = useBreakpointValue({ base: false, lg: true }) || screenSize.width >= 1024;
  const isSmallScreen = screenSize.width < 480;
  const isLargeScreen = screenSize.width >= 1200;
  const orientation = screenSize.width > screenSize.height ? 'landscape' : 'portrait';

  useEffect(() => {
    const handleResize = () => {
      setScreenSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return {
    isMobile,
    isTablet,
    isDesktop,
    isSmallScreen,
    isLargeScreen,
    screenWidth: screenSize.width,
    screenHeight: screenSize.height,
    orientation,
  };
};

export const useMobileOptimization = () => {
  const responsive = useResponsive();
  
  return {
    ...responsive,
    // Mobile-specific optimizations
    cardPadding: responsive.isMobile ? 3 : 6,
    buttonSize: responsive.isMobile ? 'sm' : 'md',
    textSize: responsive.isMobile ? 'sm' : 'md',
    spacing: responsive.isMobile ? 3 : 6,
    // Touch-friendly sizing
    touchTargetSize: responsive.isMobile ? 44 : 32,
    // Layout adjustments
    showSidebar: !responsive.isMobile,
    useDrawer: responsive.isMobile,
    // Chart sizing
    chartHeight: responsive.isMobile ? 200 : 300,
    chartWidth: responsive.isMobile ? '100%' : '100%',
  };
};

export const useTouchOptimization = () => {
  const [isTouchDevice, setIsTouchDevice] = useState(false);

  useEffect(() => {
    const checkTouch = () => {
      setIsTouchDevice(
        'ontouchstart' in window ||
        navigator.maxTouchPoints > 0 ||
        // @ts-ignore
        navigator.msMaxTouchPoints > 0
      );
    };

    checkTouch();
    window.addEventListener('touchstart', checkTouch);
    return () => window.removeEventListener('touchstart', checkTouch);
  }, []);

  return {
    isTouchDevice,
    // Touch-optimized values
    minTouchTarget: 44, // iOS/Android minimum touch target
    touchSpacing: 8, // Minimum spacing between touch targets
    swipeThreshold: 50, // Minimum distance for swipe gestures
  };
};







