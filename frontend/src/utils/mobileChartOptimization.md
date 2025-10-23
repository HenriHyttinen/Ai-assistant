# Mobile Chart Optimization Guide

## Overview
This guide explains how to ensure charts resize without data loss on mobile devices in the Counting Calories health tracking app.

## Current Implementation
- **Chart Library**: Recharts (excellent for responsive charts)
- **Responsive Container**: Already implemented
- **Chakra UI**: Responsive design system

## Mobile Optimization Strategies

### 1. Responsive Breakpoints
```typescript
const isMobile = useBreakpointValue({ base: true, md: false });
const isTablet = useBreakpointValue({ base: false, md: true, lg: false });
const isDesktop = useBreakpointValue({ base: false, lg: true });
```

### 2. Dynamic Chart Heights
```typescript
const chartHeight = useBreakpointValue({
  base: 200,  // Mobile: smaller chart
  md: 250,    // Tablet: medium chart
  lg: 300     // Desktop: larger chart
});
```

### 3. Responsive Text Sizes
```typescript
const fontSize = useBreakpointValue({
  base: 10,  // Mobile: smaller text
  md: 12,    // Desktop: normal text
  lg: 14     // Large screens: larger text
});
```

### 4. Data Aggregation for Mobile
```typescript
// Show fewer data points on mobile
const getDataForScreen = (screenWidth: number) => {
  if (screenWidth < 768) {
    // Mobile: Show every 3rd data point
    return data.filter((_, index) => index % 3 === 0);
  }
  // Desktop: Show all data points
  return data;
};
```

### 5. Touch-Friendly Interactions
```typescript
// Larger touch targets on mobile
const touchTargetSize = useBreakpointValue({
  base: 44,  // iOS/Android minimum touch target
  md: 32,    // Desktop: smaller targets
  lg: 28     // Large screens: even smaller
});
```

## Implementation Examples

### Responsive Chart Component
```typescript
const ResponsiveChart = ({ data, dataKey, xAxisKey }) => {
  const chartHeight = useBreakpointValue({ 
    base: 200, md: 300, lg: 400 
  });
  
  const fontSize = useBreakpointValue({
    base: 10, md: 12, lg: 14
  });

  return (
    <Box width="100%" height={chartHeight}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <XAxis 
            dataKey={xAxisKey}
            fontSize={fontSize}
            angle={-45}  // Rotate labels on mobile
            textAnchor="end"
          />
          <YAxis fontSize={fontSize} />
          <Line dataKey={dataKey} strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
};
```

### Mobile-Optimized Grid
```typescript
const gridColumns = useBreakpointValue({ 
  base: 1,    // Mobile: single column
  md: 2,      // Tablet: two columns
  lg: 3       // Desktop: three columns
});

<SimpleGrid columns={gridColumns} spacing={4}>
  {/* Chart content */}
</SimpleGrid>
```

## Best Practices

### 1. Chart Sizing
- **Mobile**: 200-250px height
- **Tablet**: 250-300px height
- **Desktop**: 300-400px height

### 2. Text Sizing
- **Mobile**: 10-12px font size
- **Desktop**: 12-14px font size

### 3. Data Density
- **Mobile**: Show 5-7 data points
- **Desktop**: Show 10-15 data points

### 4. Touch Targets
- **Minimum**: 44px touch targets
- **Recommended**: 48px for better usability

### 5. Chart Types
- **Mobile**: Prefer bar charts (simpler)
- **Desktop**: Line charts (more detailed)

## Testing Checklist

### Mobile (375px - 768px)
- [ ] Charts fit within screen width
- [ ] Text is readable without zooming
- [ ] Touch targets are large enough
- [ ] Data points don't overlap
- [ ] Axes labels are visible

### Tablet (768px - 1024px)
- [ ] Charts use medium sizing
- [ ] Grid layouts work properly
- [ ] Touch interactions are smooth

### Desktop (1024px+)
- [ ] Charts use full available space
- [ ] All data points are visible
- [ ] Hover interactions work
- [ ] Tooltips are positioned correctly

## Common Issues & Solutions

### Issue: Text too small on mobile
**Solution**: Use responsive font sizes
```typescript
const fontSize = useBreakpointValue({ base: 10, md: 12, lg: 14 });
```

### Issue: Data points overlapping
**Solution**: Reduce data density on mobile
```typescript
const dataPoints = useBreakpointValue({ base: 5, md: 10, lg: 15 });
const filteredData = data.slice(-dataPoints);
```

### Issue: Chart too tall on mobile
**Solution**: Use responsive heights
```typescript
const height = useBreakpointValue({ base: 200, md: 300, lg: 400 });
```

### Issue: Touch targets too small
**Solution**: Increase touch target size
```typescript
const touchSize = useBreakpointValue({ base: 44, md: 32, lg: 28 });
```

## Performance Considerations

### 1. Data Limiting
- Limit data points on mobile to improve performance
- Use data aggregation for large datasets

### 2. Rendering Optimization
- Use `ResponsiveContainer` for automatic resizing
- Avoid re-rendering on every resize

### 3. Memory Management
- Clean up chart instances on component unmount
- Use React.memo for chart components

## Accessibility

### 1. Screen Readers
- Provide alt text for charts
- Use semantic HTML structure

### 2. Keyboard Navigation
- Ensure charts are keyboard accessible
- Provide keyboard shortcuts for interactions

### 3. Color Contrast
- Ensure sufficient color contrast
- Don't rely solely on color for information

## Conclusion

Mobile chart optimization is crucial for user experience. By implementing responsive design patterns, data aggregation, and touch-friendly interactions, charts can provide excellent user experience across all device sizes without data loss.
