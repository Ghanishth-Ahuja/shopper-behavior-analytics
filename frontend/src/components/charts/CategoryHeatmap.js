import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
} from '@mui/material';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from 'recharts';

const CategoryHeatmap = ({ data }) => {
  // Transform API data for heatmap
  const heatmapData = React.useMemo(() => {
    if (!data || data.length === 0) {
      const defaultData = [
        { category: 'Electronics', segments: ['Tech Enthusiasts', 'Budget Shoppers'], values: [85, 45] },
        { category: 'Clothing', segments: ['Fashion Forward', 'Value Seekers'], values: [72, 68] },
        { category: 'Home', segments: ['Home Decorators', 'Practical Buyers'], values: [58, 82] },
        { category: 'Books', segments: ['Tech Enthusiasts', 'Value Seekers'], values: [91, 23] },
        { category: 'Sports', segments: ['Active Lifestyle', 'Weekend Warriors'], values: [67, 34] },
      ];
      
      const flat = [];
      defaultData.forEach((item) => {
        item.segments.forEach((segment, index) => {
          flat.push({
            category: item.category,
            segment: segment,
            value: item.values[index],
          });
        });
      });
      return flat;
    }

    const flat = [];
    data.forEach((segment) => {
      Object.entries(segment.category_affinities || {}).forEach(([category, score]) => {
        flat.push({
          category,
          segment: segment.segment_name,
          value: Math.round(score * 100), // Scale to 0-100 for color scale
        });
      });
    });
    return flat;
  }, [data]);

  // Color scale
  const getColor = (value) => {
    if (value >= 80) return '#22c55e'; // green
    if (value >= 60) return '#2e7d32'; // light green
    if (value >= 40) return '#ff9800'; // orange
    if (value >= 20) return '#ff5722'; // red orange
    return '#f44336'; // red
  };

  return (
    <Box sx={{ width: '100%', height: 300 }}>
      <ResponsiveContainer>
        <BarChart
          data={heatmapData}
          margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="category" 
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={80}
          />
          <YAxis 
            dataKey="segment" 
            type="category"
            tick={{ fontSize: 12 }}
            width={100}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                return (
                  <Box sx={{ p: 1, bgcolor: 'background.paper', border: '1px solid #ccc' }}>
                    <Typography variant="subtitle2">
                      {data.category} - {data.segment}
                    </Typography>
                    <Typography variant="body2">
                      Affinity Score: {data.value}
                    </Typography>
                  </Box>
                );
              }
              return null;
            }}
          />
          <Bar dataKey="value" fill="#8884d8">
            {heatmapData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getColor(entry.value)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default CategoryHeatmap;
