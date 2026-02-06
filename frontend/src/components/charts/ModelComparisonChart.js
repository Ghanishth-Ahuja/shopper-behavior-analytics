import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
} from '@mui/material';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';

const ModelComparisonChart = ({ data }) => {
  // Default data if none provided
  const defaultData = {
    variants: {
      'collaborative': {
        impressions: 1000,
        clicks: 150,
        conversions: 30,
        ctr: 15.0,
        conversion_rate: 3.0,
      },
      'content_based': {
        impressions: 1000,
        clicks: 120,
        conversions: 25,
        ctr: 12.0,
        conversion_rate: 2.5,
      },
      'hybrid': {
        impressions: 1000,
        clicks: 180,
        conversions: 45,
        ctr: 25.0,
        conversion_rate: 4.5,
      },
    },
    winner: 'hybrid',
    confidence: 0.95,
  };

  const chartData = data || defaultData;

  const barData = Object.entries(chartData.variants).map(([name, metrics]) => ({
    model: name,
    impressions: metrics.impressions,
    clicks: metrics.clicks,
    conversions: metrics.conversions,
    ctr: metrics.ctr,
    conversion_rate: metrics.conversion_rate,
    fill: name === chartData.winner ? '#4caf50' : name === 'collaborative' ? '#2196f3' : '#ff9800',
  }));

  return (
    <Box sx={{ width: '100%', height: 300 }}>
      <ResponsiveContainer>
        <Typography variant="h6" gutterBottom>
          🧪 A/B Test Results
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
          Comparing recommendation algorithms to find the optimal approach
        </Typography>
        
        <BarChart
          data={barData}
          margin={{
            top: 20,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="model" tick={{ fontSize: 12 }} />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                return (
                  <Box sx={{ p: 1, bgcolor: 'background.paper', border: '1px solid #ccc' }}>
                    <Typography variant="subtitle2">
                      {data.model}
                    </Typography>
                    <Typography variant="body2">
                      Impressions: {data.impressions.toLocaleString()}
                    </Typography>
                    <Typography variant="body2">
                      Clicks: {data.clicks.toLocaleString()}
                    </Typography>
                    <Typography variant="body2">
                      Conversions: {data.conversions.toLocaleString()}
                    </Typography>
                    <Typography variant="body2">
                      CTR: {data.ctr.toFixed(1)}%
                    </Typography>
                    <Typography variant="body2">
                      Conv Rate: {data.conversion_rate.toFixed(1)}%
                    </Typography>
                  </Box>
                );
              }
              return null;
            }}
          />
          <Legend />
          <Bar dataKey="impressions" fill="#8884d8" />
          <Bar dataKey="clicks" fill="#82ca9d" />
          <Bar dataKey="conversions" fill="#ffc658" />
        </BarChart>
      </ResponsiveContainer>
      
      {/* Winner Announcement */}
      <Box sx={{ mt: 2, textAlign: 'center' }}>
        <Chip
          label={`Winner: ${chartData.winner.toUpperCase()}`}
          color="success"
          variant="outlined"
          sx={{ mb: 1 }}
        />
        <Typography variant="body2" color="text.secondary">
          Confidence: {chartData.confidence * 100}%
        </Typography>
      </Box>
    </Box>
  );
};

export default ModelComparisonChart;
