import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  useColorModeValue,
  useBreakpointValue,
  Spinner,
  Center,
  Text,
  VStack,
} from '@chakra-ui/react';
import { useResponsive } from '../../hooks/useResponsive';

interface MobileChartProps {
  children: React.ReactNode;
  height?: number;
  width?: number | string;
  loading?: boolean;
  error?: string;
  title?: string;
  showLegend?: boolean;
  legendPosition?: 'top' | 'bottom' | 'left' | 'right';
  className?: string;
}

const MobileChart: React.FC<MobileChartProps> = ({
  children,
  height,
  width,
  loading = false,
  error,
  title,
  showLegend = true,
  legendPosition = 'bottom',
  className,
}) => {
  const responsive = useResponsive();
  const chartRef = useRef<HTMLDivElement>(null);
  const [chartDimensions, setChartDimensions] = useState({
    width: 0,
    height: 0,
  });

  // Calculate responsive dimensions
  const chartHeight = height || (responsive.isMobile ? 200 : 300);
  const chartWidth = width || '100%';

  // Handle resize for responsive charts
  useEffect(() => {
    const handleResize = () => {
      if (chartRef.current) {
        const rect = chartRef.current.getBoundingClientRect();
        setChartDimensions({
          width: rect.width,
          height: rect.height,
        });
      }
    };

    handleResize();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');

  if (loading) {
    return (
      <Box
        ref={chartRef}
        bg={bgColor}
        borderWidth={1}
        borderColor={borderColor}
        borderRadius="md"
        p={4}
        minH={chartHeight}
        display="flex"
        alignItems="center"
        justifyContent="center"
        className={className}
      >
        <VStack spacing={3}>
          <Spinner size="lg" />
          <Text fontSize="sm" color="gray.500">
            Loading chart...
          </Text>
        </VStack>
      </Box>
    );
  }

  if (error) {
    return (
      <Box
        ref={chartRef}
        bg={bgColor}
        borderWidth={1}
        borderColor={borderColor}
        borderRadius="md"
        p={4}
        minH={chartHeight}
        display="flex"
        alignItems="center"
        justifyContent="center"
        className={className}
      >
        <VStack spacing={3}>
          <Text fontSize="sm" color="red.500">
            Error loading chart
          </Text>
          <Text fontSize="xs" color="gray.500">
            {error}
          </Text>
        </VStack>
      </Box>
    );
  }

  return (
    <Box
      ref={chartRef}
      bg={bgColor}
      borderWidth={1}
      borderColor={borderColor}
      borderRadius="md"
      p={responsive.isMobile ? 2 : 4}
      className={className}
    >
      {title && (
        <Text
          fontSize={responsive.isMobile ? 'sm' : 'md'}
          fontWeight="semibold"
          mb={3}
          textAlign="center"
        >
          {title}
        </Text>
      )}
      
      <Box
        width={chartWidth}
        height={chartHeight}
        position="relative"
        overflow="hidden"
      >
        {React.cloneElement(children as React.ReactElement, {
          width: chartDimensions.width || '100%',
          height: chartHeight,
          // Mobile-specific chart props
          margin: responsive.isMobile ? { top: 10, right: 10, bottom: 30, left: 10 } : { top: 20, right: 20, bottom: 40, left: 20 },
          // Responsive font sizes
          fontSize: responsive.isMobile ? 10 : 12,
          // Touch-friendly interactions
          isAnimationActive: !responsive.isMobile,
        })}
      </Box>
    </Box>
  );
};

export default MobileChart;


