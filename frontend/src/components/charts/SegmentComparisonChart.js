import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
} from '@mui/material';
import {
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Tooltip,
  Legend,
} from 'recharts';

const SegmentComparisonChart = ({ data }) => {
  // Default data if none provided
  const defaultData = [
    {
      segment: 'Tech Enthusiasts',
      purchaseFrequency: 85,
      avgOrderValue: 72,
      sessionDuration: 45,
      cartAbandonment: 23,
      searchActivity: 67,
      weekendPreference: 89,
    },
    {
      segment: 'Budget Shoppers',
      purchaseFrequency: 45,
      avgOrderValue: 35,
      sessionDuration: 78,
      cartAbandonment: 56,
      searchActivity: 89,
      weekendPreference: 67,
    },
    {
      segment: 'Fashion Forward',
      purchaseFrequency: 67,
      avgOrderValue: 58,
      sessionDuration: 92,
      cartAbandonment: 34,
      searchActivity: 45,
      weekendPreference: 78,
    },
  ];

  const chartData = data || defaultData;

  return (
    <Box sx={{ width: '100%', height: 300 }}>
      <Typography variant="h6" gutterBottom>
        📊 Segment Comparison
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Compare behavioral patterns across different customer segments
      </Typography>
      
      <ResponsiveContainer>
        <RadarChart cx="50%" cy="50%" outerRadius={80} innerRadius={40}>
          <PolarGrid>
            <PolarAngleAxis
              type="category"
              dataKey="segment"
              tick={{ fontSize: 10 }}
            />
            <PolarRadiusAxis
              angleAxisId={0}
              domain={[0, 100]}
              tick={{ fontSize: 10 }}
            />
          </PolarGrid>
          
          {/* Map each metric to a radar chart */}
          <Radar
            name="Purchase Frequency"
            dataKey="purchaseFrequency"
            stroke="#8884d8"
            fill="#8884d8"
            fillOpacity={0.3}
          />
          <Radar
            name="Avg Order Value"
            dataKey="avgOrderValue"
            stroke="#82ca9d"
            fill="#82ca9d"
            fillOpacity={0.3}
          />
          <Radar
            name="Session Duration"
            dataKey="sessionDuration"
            stroke="#ffc658"
            fill="#ffc658"
            fillOpacity={0.3}
          />
          
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                return (
                  <Box sx={{ p: 1, bgcolor: 'background.paper', border: '1px solid #ccc' }}>
                    <Typography variant="subtitle2">
                      {data.segment}
                    </Typography>
                    {payload.map((entry, index) => (
                      <Typography key={index} variant="body2">
                        {entry.name}: {entry.value}
                      </Typography>
                    ))}
                  </Box>
                );
              }
              return null;
            }}
          />
          <Legend />
        </RadarChart>
      </ResponsiveContainer>
      
      {/* Comparison Insights */}
      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          💡 Comparison Insights
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          <Typography variant="caption" color="text.secondary" sx={{ mr: 2 }}>
            • Tech Enthusiasts: High purchase frequency, low cart abandonment
          </Typography>
          <Typography variant="caption" color="text.secondary" sx={{ mr: 2 }}>
            • Budget Shoppers: High search activity, high cart abandonment
          </Typography>
          <Typography variant="caption" color="text.secondary">
            • Fashion Forward: Long sessions, moderate conversion
          </Typography>
        </Box>
      </Box>
    </Box>
  );
};

export default SegmentComparisonChart;
