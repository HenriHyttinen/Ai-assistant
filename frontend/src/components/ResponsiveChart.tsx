import React from 'react';
import { Box, useBreakpointValue } from '@chakra-ui/react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface ResponsiveChartProps {
  data: any[];
  dataKey: string;
  xAxisKey: string;
  height?: number;
  showGrid?: boolean;
  showTooltip?: boolean;
  strokeColor?: string;
  strokeWidth?: number;
}

const ResponsiveChart: React.FC<ResponsiveChartProps> = ({
  data,
  dataKey,
  xAxisKey,
  height,
  showGrid = true,
  showTooltip = true,
  strokeColor = '#3182ce',
  strokeWidth = 2
}) => {
  // Get responsive values based on screen size
  const chartHeight = useBreakpointValue({ 
    base: height || 200,  // Mobile: smaller height
    md: height || 300,   // Desktop: larger height
    lg: height || 400    // Large screens: even larger
  });

  const fontSize = useBreakpointValue({
    base: 10,  // Mobile: smaller text
    md: 12,    // Desktop: normal text
    lg: 14     // Large screens: larger text
  });

  const tickCount = useBreakpointValue({
    base: 3,   // Mobile: fewer ticks
    md: 5,     // Desktop: more ticks
    lg: 7      // Large screens: most ticks
  });

  const margin = useBreakpointValue({
    base: { top: 5, right: 5, left: 5, bottom: 5 },    // Mobile: minimal margins
    md: { top: 10, right: 10, left: 10, bottom: 10 },  // Desktop: normal margins
    lg: { top: 20, right: 20, left: 20, bottom: 20 }  // Large screens: more margins
  });

  return (
    <Box width="100%" height={chartHeight}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart 
          data={data} 
          margin={margin}
        >
          {showGrid && (
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke="#e2e8f0" 
              strokeOpacity={0.3}
            />
          )}
          <XAxis 
            dataKey={xAxisKey}
            stroke="#718096"
            fontSize={fontSize}
            tickCount={tickCount}
            angle={-45}  // Rotate labels on mobile
            textAnchor="end"
            height={60}
            interval="preserveStartEnd"
          />
          <YAxis 
            stroke="#718096"
            fontSize={fontSize}
            tickCount={4}
            width={60}
          />
          {showTooltip && (
            <Tooltip 
              contentStyle={{
                backgroundColor: 'white',
                border: '1px solid #e2e8f0',
                borderRadius: '6px',
                fontSize: fontSize
              }}
              labelStyle={{
                fontSize: fontSize,
                fontWeight: 'bold'
              }}
            />
          )}
          <Line 
            type="monotone" 
            dataKey={dataKey} 
            stroke={strokeColor}
            strokeWidth={strokeWidth}
            dot={{ r: 4, strokeWidth: 2, fill: strokeColor }}
            activeDot={{ r: 6, strokeWidth: 2, fill: strokeColor }}
          />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default ResponsiveChart;
