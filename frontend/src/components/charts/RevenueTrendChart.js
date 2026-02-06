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
} from 'recharts';

const RevenueTrendChart = ({ data }) => {
  // Transform or validate data
  const chartData = React.useMemo(() => {
    if (!data || !Array.isArray(data) || data.length === 0) {
      return [
        { date: '2024-01-01', revenue: 12500, orders: 234 },
        { date: '2024-01-02', revenue: 13200, orders: 256 },
        { date: '2024-01-03', revenue: 11800, orders: 198 },
        { date: '2024-01-04', revenue: 14500, orders: 312 },
        { date: '2024-01-05', revenue: 15200, orders: 345 },
        { date: '2024-01-06', revenue: 13900, orders: 289 },
        { date: '2024-01-07', revenue: 16800, orders: 398 },
      ];
    }
    return data;
  }, [data]);

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
              if (!value) return '';
              const date = new Date(value);
              return isNaN(date.getTime()) ? value : date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            }}
          />
          <YAxis 
            yAxisId="left"
            tick={{ fontSize: 12 }}
            tickFormatter={(value) => `$${((value || 0) / 1000).toFixed(1)}k`}
          />
          <YAxis 
            yAxisId="right"
            orientation="right"
            tick={{ fontSize: 12 }}
          />
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const item = payload[0].payload;
                const revenue = item?.revenue ?? 0;
                const orders = item?.orders ?? 0;
                
                return (
                  <Box sx={{ p: 1, bgcolor: 'background.paper', border: '1px solid #ccc', boxShadow: 1 }}>
                    <Typography variant="subtitle2">
                      {item?.date ? new Date(item.date).toLocaleDateString() : 'Unknown Date'}
                    </Typography>
                    <Typography variant="body2">
                      Revenue: ${revenue.toLocaleString()}
                    </Typography>
                    {orders > 0 && (
                      <>
                        <Typography variant="body2">
                          Orders: {orders.toLocaleString()}
                        </Typography>
                        <Typography variant="body2">
                          Avg Order: ${(revenue / orders).toFixed(2)}
                        </Typography>
                      </>
                    )}
                  </Box>
                );
              }
              return null;
            }}
          />
          <Legend />
          <Line
            yAxisId="left"
            type="monotone"
            dataKey="revenue"
            stroke="#8884d8"
            strokeWidth={2}
            dot={{ fill: '#8884d8', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6 }}
            name="Revenue"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="orders"
            stroke="#82ca9d"
            strokeWidth={2}
            dot={{ fill: '#82ca9d', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6 }}
            name="Orders"
          />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default RevenueTrendChart;
