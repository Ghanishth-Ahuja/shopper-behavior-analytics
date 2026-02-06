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
  Bar,
  BarChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';

const SegmentBehaviorChart = ({ data }) => {
  // Default data if none provided
  const defaultData = {
    categories: ['Purchase Frequency', 'Avg Order Value', 'Session Duration', 'Cart Abandonment', 'Search Activity', 'Weekend Preference'],
    values: [85, 72, 45, 23, 67, 89],
  };

  const chartData = data || defaultData;

  // Transform data for radar chart
  const radarData = chartData.categories.map((category, index) => ({
    category,
    value: chartData.values[index],
    fullMark: 100,
  }));

  return (
    <Box sx={{ width: '100%', height: 300 }}>
      <ResponsiveContainer>
        <RadarChart cx="50%" cy="50%" outerRadius={80} innerRadius={40}>
            <PolarGrid>
              <PolarAngleAxis
                type="category"
                dataKey="category"
                tick={{ fontSize: 10 }}
              />
              <PolarRadiusAxis
                angleAxisId={0}
                domain={[0, 100]}
                tick={{ fontSize: 10 }}
              />
            </PolarGrid>
            <Radar
              name="Behavior Score"
              dataKey="value"
              stroke="#8884d8"
              fill="#8884d8"
              fillOpacity={0.6}
            >
              {radarData.map((entry, index) => (
                <PolarAngleAxis
                  key={`angle-${index}`}
                  angleAxisId={0}
                  angle={entry.category}
                  domain={[0, 100]}
                />
              ))}
            </Radar>
          </RadarChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default SegmentBehaviorChart;
