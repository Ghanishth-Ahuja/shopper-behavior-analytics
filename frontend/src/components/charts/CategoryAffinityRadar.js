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
} from 'recharts';

const CategoryAffinityRadar = ({ data }) => {
  // Default data if none provided
  const defaultData = {
    categories: ['Electronics', 'Clothing', 'Home', 'Books', 'Sports'],
    affinities: [
      { category: 'Electronics', affinity: 0.85, fullMark: 1.0 },
      { category: 'Clothing', affinity: 0.72, fullMark: 1.0 },
      { category: 'Home', affinity: 0.45, fullMark: 1.0 },
      { category: 'Books', affinity: 0.91, fullMark: 1.0 },
      { category: 'Sports', affinity: 0.33, fullMark: 1.0 },
    ],
  };

  const chartData = data || defaultData;

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
              domain={[0, 1]}
              tick={{ fontSize: 10 }}
            />
          </PolarGrid>
          <Radar
            name="Category Affinity"
            dataKey="affinity"
            stroke="#8884d8"
            fill="#8884d8"
            fillOpacity={0.6}
          >
              {chartData.affinities.map((entry, index) => (
                <PolarAngleAxis
                  key={`angle-${index}`}
                  angleAxisId={0}
                  angle={entry.category}
                  domain={[0, 1]}
                />
              ))}
            </Radar>
          </RadarChart>
        </ResponsiveContainer>
      </Box>
  );
};

export default CategoryAffinityRadar;
