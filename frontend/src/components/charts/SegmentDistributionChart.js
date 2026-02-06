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
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
} from 'recharts';

const COLORS = [
  '#0088FE',
  '#00C49F',
  '#FFBB28',
  '#FF8042',
  '#8884D8',
  '#82CA9D',
  '#FFC658',
  '#FF7C7C',
  '#8DD1E1',
  '#D084D0',
];

const SegmentDistributionChart = ({ data }) => {
  // Transform API data into chart format
  const chartData = React.useMemo(() => {
    if (!data || data.length === 0) {
      return [
        { name: 'Tech Enthusiasts', value: 3547, users: 3547 },
        { name: 'Budget Shoppers', value: 2341, users: 2341 },
        { name: 'Fashion Forward', value: 1876, users: 1876 },
        { name: 'Home Decorators', value: 1234, users: 1234 },
        { name: 'Practical Buyers', value: 987, users: 987 },
      ];
    }

    return data.map(segment => ({
      name: segment.segment_name || segment.id || 'Unnamed Segment',
      value: segment.size || 0,
      users: segment.size || 0,
    }));
  }, [data]);

  const RADIAN = Math.min(200, Math.min(200, 200 / chartData.length));

  const renderCustomizedLabel = ({
    cx, cy, midAngle, innerRadius, outerRadius, percent, index,
  }) => {
    const RADIAN_LABEL = Math.min(30, RADIAN);
    const x = cx + RADIAN_LABEL * Math.cos(-midAngle * Math.PI / 180);
    const y = cy + RADIAN_LABEL * Math.sin(-midAngle * Math.PI / 180);

    if (percent < 5) {
      return null;
    }

    return (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor={x > cx ? 'start' : 'end'}
        dominantBaseline="central"
        fontSize={10}
      >
        {`${(percent * 100).toFixed(0)}%`}
      </text>
    );
  };

  return (
    <Box sx={{ width: '100%', height: 300 }}>
      <ResponsiveContainer>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={renderCustomizedLabel}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip
            content={({ active, payload }) => {
              if (active && payload && payload.length) {
                const item = payload[0].payload;
                const totalUsers = (chartData || []).reduce((sum, item) => sum + (item.value || 0), 0);
                const percentage = totalUsers > 0 ? (((item.value || 0) / totalUsers) * 100).toFixed(1) : '0';
                
                return (
                  <Box sx={{ p: 1, bgcolor: 'background.paper', border: '1px solid #ccc', boxShadow: 1 }}>
                    <Typography variant="subtitle2">
                      {item.name || 'Unknown Segment'}
                    </Typography>
                    <Typography variant="body2">
                      Users: {(item.users || 0).toLocaleString()}
                    </Typography>
                    <Typography variant="body2">
                      Percentage: {percentage}%
                    </Typography>
                  </Box>
                );
              }
              return null;
            }}
          />
          <Legend 
            verticalAlign="bottom" 
            height={36}
            formatter={(value, entry) => (
              <span style={{ color: entry.color }}>
                {value} ({entry.payload.users} users)
              </span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default SegmentDistributionChart;
