import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
} from '@mui/material';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Area,
  AreaChart,
} from 'recharts';

const RecommendationPerformanceChart = ({ data }) => {
  // Default data if none provided
  const defaultData = [
    { date: '2024-01-01', clickRate: 12.5, conversionRate: 3.2, totalRecommendations: 1000 },
    { date: '2024-01-02', clickRate: 13.2, conversionRate: 3.5, totalRecommendations: 1200 },
    { date: '2024-01-03', clickRate: 11.8, conversionRate: 2.9, totalRecommendations: 980 },
    { date: '2024-01-04', clickRate: 14.1, conversionRate: 3.8, totalRecommendations: 1350 },
    { date: '2024-01-05', clickRate: 15.3, conversionRate: 4.1, totalRecommendations: 1420 },
    { date: '2024-01-06', clickRate: 13.9, conversionRate: 3.7, totalRecommendations: 1380 },
    { date: '2024-01-07', clickRate: 16.2, conversionRate: 4.5, totalRecommendations: 1560 },
  ];

  const chartData = data || defaultData;

  return (
    <Box sx={{ width: '100%', height: 300 }}>
      <ResponsiveContainer>
        <LineChart
          data={chartData}
          margin={{
            top: 5,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="date" 
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => {
              const date = new Date(value);
              return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            }}
          />
          <YAxis 
            yAxisId="left"
            tick={{ fontSize: 12 }}
          />
          <YAxis 
            yAxisId="right"
            orientation="right"
            tick={{ fontSize: 12 }}
          />
          <Tooltip
            content={({ active, payload, label }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                return (
                  <Box sx={{ p: 1, bgcolor: 'background.paper', border: '1px solid #ccc' }}>
                    <Typography variant="subtitle2">
                      {new Date(data.date).toLocaleDateString()}
                    </Typography>
                    <Typography variant="body2">
                      Click Rate: {data.clickRate}%
                    </Typography>
                    <Typography variant="body2">
                      Conversion Rate: {data.conversionRate}%
                    </Typography>
                    <Typography variant="body2">
                      Total Recs: {data.totalRecommendations}
                    </Typography>
                  </Box>
                );
              }
              return null;
            }}
          />
          <Legend />
          <Area
            yAxisId="left"
            type="monotone"
            dataKey="clickRate"
            stroke="#8884d8"
            fill="#8884d8"
            fillOpacity={0.3}
          />
          <Area
            yAxisId="right"
            type="monotone"
            dataKey="conversionRate"
            stroke="#82ca9d"
            fill="#82ca9d"
            fillOpacity={0.3}
          />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="clickRate"
            stroke="#8884d8"
            strokeWidth={2}
            dot={{ fill: '#8884d8', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6 }}
            name="Click Rate"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="conversionRate"
            stroke="#82ca9d"
            strokeWidth={2}
            dot={{ fill: '#82ca9d', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6 }}
            name="Conversion Rate"
          />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default RecommendationPerformanceChart;
