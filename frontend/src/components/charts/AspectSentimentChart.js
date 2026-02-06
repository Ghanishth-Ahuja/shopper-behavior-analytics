import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';

const AspectSentimentChart = ({ data }) => {
  // Default data if none provided
  const defaultData = {
    aspects: [
      { aspect: 'Price', positive: 0.3, negative: 0.4, neutral: 0.3 },
      { aspect: 'Quality', positive: 0.7, negative: 0.1, neutral: 0.2 },
      { aspect: 'Service', positive: 0.6, negative: 0.2, neutral: 0.2 },
      { aspect: 'Shipping', positive: 0.4, negative: 0.3, neutral: 0.3 },
      { aspect: 'Features', positive: 0.8, negative: 0.1, neutral: 0.1 },
    ],
  };

  const chartData = data || defaultData;

  const getColor = (positive, negative) => {
    if (positive > negative + 0.1) return 'success';
    if (negative > positive + 0.1) return 'error';
    return 'warning';
  };

  return (
    <Box sx={{ width: '100%', height: 300 }}>
      <Typography variant="h6" gutterBottom>
        🎯 Aspect-Based Sentiment Analysis
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Understanding what specific aspects customers are happy or unhappy about
      </Typography>
      
      <ResponsiveContainer>
        <BarChart
          data={chartData.aspects}
          layout="horizontal"
          margin={{
            top: 20,
            right: 30,
            left: 20,
            bottom: 5,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="aspect" 
            tick={{ fontSize: 12 }}
          />
          <YAxis 
            tick={{ fontSize: 12 }}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const data = payload[0].payload;
                const sentiment = getColor(data.positive, data.negative);
                
                return (
                  <Box sx={{ p: 1, bgcolor: 'background.paper', border: '1px solid #ccc' }}>
                    <Typography variant="subtitle2">
                      {data.aspect}
                    </Typography>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 2, mb: 1 }}>
                      <Box sx={{ textAlign: 'center' }}>
                        <Typography variant="caption" color={sentiment === 'success' ? 'success.main' : sentiment === 'error' ? 'error.main' : 'warning.main'}>
                          {sentiment === 'success' ? 'Positive' : sentiment === 'error' ? 'Negative' : 'Neutral'}
                        </Typography>
                        <Typography variant="h6" color={sentiment === 'success' ? 'success.main' : sentiment === 'error' ? 'error.main' : 'warning.main'}>
                          {sentiment === 'success' ? data.positive.toFixed(2) : sentiment === 'error' ? data.negative.toFixed(2) : '0.0'}
                        </Typography>
                      </Box>
                    </Box>
                    <Box sx={{ textAlign: 'center' }}>
                      <Typography variant="caption" color="text.secondary">
                        Positive: {data.positive.toFixed(2)} | Negative: {data.negative.toFixed(2)}
                      </Typography>
                    </Box>
                  </Box>
                );
              }
              return null;
            }}
          />
          <Bar dataKey="positive" fill="#22c55e" />
          <Bar dataKey="negative" fill="#ef5350" />
          <Bar dataKey="neutral" fill="#9e9e9e" />
        </BarChart>
      </ResponsiveContainer>
      
      {/* Aspect Insights */}
      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          💡 Key Insights
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {chartData.aspects.map((aspect, index) => (
            <Box key={index} sx={{ minWidth: 200, mb: 1 }}>
              <Typography variant="subtitle2">
                {aspect.aspect}
              </Typography>
              <LinearProgress
                variant="determinate"
                value={aspect.positive / (aspect.positive + aspect.negative + aspect.neutral) * 100}
                color={getColor(aspect.positive, aspect.negative)}
                sx={{ height: 4 }}
              />
              <Typography variant="caption" color="text.secondary">
                {aspect.positive > aspect.negative ? 'Positive majority' : aspect.negative > aspect.positive ? 'Negative majority' : 'Mixed sentiment'}
              </Typography>
            </Box>
          ))}
        </Box>
      </Box>
    </Box>
  );
};

export default AspectSentimentChart;
