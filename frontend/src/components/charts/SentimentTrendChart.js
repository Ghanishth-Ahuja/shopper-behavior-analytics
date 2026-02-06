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

const SentimentTrendChart = ({ data }) => {
  // Default data if none provided
  const defaultData = [
    { date: '2024-01-01', positive: 450, negative: 120, neutral: 130, total: 700 },
    { date: '2024-01-02', positive: 480, negative: 110, neutral: 140, total: 730 },
    { date: '2024-01-03', positive: 420, negative: 135, neutral: 125, total: 680 },
    { date: '2024-01-04', positive: 510, negative: 95, neutral: 145, total: 750 },
    { date: '2024-01-05', positive: 490, negative: 85, neutral: 155, total: 730 },
    { date: '2024-01-06', positive: 520, negative: 75, neutral: 165, total: 760 },
    { date: '2024-01-07', positive: 580, negative: 65, neutral: 170, total: 815 },
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
            tick={{ fontSize: 12 }}
          />
          <Tooltip
            content={({ active, payload, label }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                const total = data.total;
                const positivePct = ((data.positive / total) * 100).toFixed(1);
                const negativePct = ((data.negative / total) * 100).toFixed(1);
                const neutralPct = ((data.neutral / total) * 100).toFixed(1);
                
                return (
                  <Box sx={{ p: 1, bgcolor: 'background.paper', border: '1px solid #ccc' }}>
                    <Typography variant="subtitle2">
                      {new Date(data.date).toLocaleDateString()}
                    </Typography>
                    <Box sx={{ display: 'flex', gap: 2, mb: 1 }}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="caption" color="success.main">
                          Positive
                        </Typography>
                        <Typography variant="h6" color="success.main">
                          {positivePct}%
                        </Typography>
                      </Box>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="caption" color="error.main">
                          Negative
                        </Typography>
                        <Typography variant="h6" color="error.main">
                          {negativePct}%
                        </Typography>
                      </Box>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="caption" color="text.secondary">
                          Neutral
                        </Typography>
                        <Typography variant="h6" color="text.secondary">
                          {neutralPct}%
                        </Typography>
                      </Box>
                    </Box>
                    <Typography variant="body2" color="text.secondary">
                      Total Reviews: {total}
                    </Typography>
                  </Box>
                );
              }
              return null;
            }}
          />
          <Legend />
          <Area
            type="monotone"
            dataKey="positive"
            stackId="1"
            stroke="#22c55e"
            fill="#22c55e"
            fillOpacity={0.6}
          />
          <Area
            type="monotone"
            dataKey="negative"
            stackId="2"
            stroke="#ef5350"
            fill="#ef5350"
            fillOpacity={0.6}
          />
          <Area
            type="monotone"
            dataKey="neutral"
            stackId="3"
            stroke="#9e9e9e"
            fill="#9e9e9e"
            fillOpacity={0.6}
          />
          <Line
            type="monotone"
            dataKey="positive"
            stroke="#22c55e"
            strokeWidth={2}
            stackId="1"
          />
          <Line
            type="monotone"
            dataKey="negative"
            stroke="#ef5350"
            strokeWidth={2}
            stackId="2"
          />
          <Line
            type="monotone"
            dataKey="neutral"
            stroke="#9e9e9e"
            strokeWidth={2}
            stackId="3"
          />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default SentimentTrendChart;
