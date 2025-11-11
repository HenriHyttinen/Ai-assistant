/**
 * VisualizationChart component for displaying charts in AI assistant responses.
 * Supports line, bar, and pie charts based on chart configuration from backend.
 */
import React, { useMemo } from 'react';
import {
  Box,
  Card,
  CardBody,
  CardHeader,
  Heading,
  useColorModeValue,
  Text
} from '@chakra-ui/react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';

interface ChartData {
  x?: string | number;
  y?: number;
  name?: string;
  value?: number;
  current?: number;
  target?: number;
  color?: string;
  [key: string]: any;
}

interface ChartConfig {
  type: 'line' | 'bar' | 'pie';
  title: string;
  data: ChartData[];
  xAxis?: {
    label: string;
  };
  yAxis?: {
    label: string;
  };
  config?: {
    strokeWidth?: number;
    dot?: boolean;
    grid?: boolean;
    barRadius?: number;
    innerRadius?: number | string;
    outerRadius?: number | string;
    label?: boolean;
    stacked?: boolean;
    showTarget?: boolean;
  };
}

interface VisualizationChartProps {
  chartConfig: ChartConfig;
}

const VisualizationChart: React.FC<VisualizationChartProps> = ({ chartConfig }) => {
  const cardBg = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.600');
  const textColor = useColorModeValue('gray.600', 'gray.300');
  
  // Color palette for charts
  const colors = [
    '#3182ce', // Blue
    '#38a169', // Green
    '#d69e2e', // Yellow
    '#e53e3e', // Red
    '#805ad5', // Purple
    '#dd6b20', // Orange
  ];
  
  // Prepare data based on chart type
  const preparedData = useMemo(() => {
    if (chartConfig.type === 'pie') {
      return chartConfig.data.map((item, index) => ({
        ...item,
        color: item.color || colors[index % colors.length]
      }));
    }
    return chartConfig.data;
  }, [chartConfig.data, chartConfig.type]);
  
  const renderChart = () => {
    switch (chartConfig.type) {
      case 'line':
        return (
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={preparedData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
              {chartConfig.config?.grid && <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />}
              <XAxis 
                dataKey="x" 
                stroke={textColor}
                label={chartConfig.xAxis?.label ? { value: chartConfig.xAxis.label, position: 'insideBottom', offset: -5 } : undefined}
              />
              <YAxis 
                stroke={textColor}
                label={chartConfig.yAxis?.label ? { value: chartConfig.yAxis.label, angle: -90, position: 'insideLeft' } : undefined}
              />
              <RechartsTooltip 
                contentStyle={{ 
                  backgroundColor: cardBg, 
                  border: `1px solid ${borderColor}`,
                  borderRadius: '8px'
                }}
              />
              <Line 
                type="monotone" 
                dataKey="y" 
                stroke={colors[0]} 
                strokeWidth={chartConfig.config?.strokeWidth || 2}
                dot={chartConfig.config?.dot !== false}
              />
            </LineChart>
          </ResponsiveContainer>
        );
      
      case 'bar':
        // Check if we have current/target data (for comparison charts)
        const hasComparison = preparedData.some(item => 'current' in item && 'target' in item);
        
        if (hasComparison) {
          return (
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={preparedData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                {chartConfig.config?.grid && <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />}
                <XAxis 
                  dataKey="x" 
                  stroke={textColor}
                  label={chartConfig.xAxis?.label ? { value: chartConfig.xAxis.label, position: 'insideBottom', offset: -5 } : undefined}
                />
                <YAxis 
                  stroke={textColor}
                  label={chartConfig.yAxis?.label ? { value: chartConfig.yAxis.label, angle: -90, position: 'insideLeft' } : undefined}
                />
                <RechartsTooltip 
                  contentStyle={{ 
                    backgroundColor: cardBg, 
                    border: `1px solid ${borderColor}`,
                    borderRadius: '8px'
                  }}
                />
                <Legend />
                <Bar 
                  dataKey="current" 
                  fill={colors[0]} 
                  radius={chartConfig.config?.barRadius || 4}
                  name="Current"
                />
                {chartConfig.config?.showTarget && (
                  <Bar 
                    dataKey="target" 
                    fill={colors[1]} 
                    radius={chartConfig.config?.barRadius || 4}
                    opacity={0.5}
                    name="Target"
                  />
                )}
              </BarChart>
            </ResponsiveContainer>
          );
        }
        
        // Simple bar chart
        return (
          <ResponsiveContainer width="100%" height={350}>
            <BarChart data={preparedData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
              {chartConfig.config?.grid && <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />}
              <XAxis 
                dataKey="x" 
                stroke={textColor}
                label={chartConfig.xAxis?.label ? { value: chartConfig.xAxis.label, position: 'insideBottom', offset: -5 } : undefined}
              />
              <YAxis 
                stroke={textColor}
                label={chartConfig.yAxis?.label ? { value: chartConfig.yAxis.label, angle: -90, position: 'insideLeft' } : undefined}
              />
              <RechartsTooltip 
                contentStyle={{ 
                  backgroundColor: cardBg, 
                  border: `1px solid ${borderColor}`,
                  borderRadius: '8px'
                }}
              />
              <Bar 
                dataKey="y" 
                fill={colors[0]} 
                radius={chartConfig.config?.barRadius || 4}
              />
            </BarChart>
          </ResponsiveContainer>
        );
      
      case 'pie':
        return (
          <ResponsiveContainer width="100%" height={350}>
            <PieChart>
              <Pie
                data={preparedData}
                cx="50%"
                cy="50%"
                labelLine={chartConfig.config?.label !== false}
                label={chartConfig.config?.label !== false ? ({ name, value }) => `${name}: ${value}` : false}
                outerRadius={chartConfig.config?.outerRadius === 'string' ? 120 : (chartConfig.config?.outerRadius as number) || 120}
                innerRadius={chartConfig.config?.innerRadius as number || 0}
                fill="#8884d8"
                dataKey="value"
              >
                {preparedData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color || colors[index % colors.length]} />
                ))}
              </Pie>
              <RechartsTooltip 
                contentStyle={{ 
                  backgroundColor: cardBg, 
                  border: `1px solid ${borderColor}`,
                  borderRadius: '8px'
                }}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        );
      
      default:
        return (
          <Box p={4}>
            <Text color={textColor}>Unsupported chart type: {chartConfig.type}</Text>
          </Box>
        );
    }
  };
  
  return (
    <Card bg={cardBg} borderColor={borderColor} my={4}>
      <CardHeader>
        <Heading size="md">{chartConfig.title}</Heading>
      </CardHeader>
      <CardBody>
        <Box width="100%" minHeight="300px">
          {renderChart()}
        </Box>
      </CardBody>
    </Card>
  );
};

export default VisualizationChart;

