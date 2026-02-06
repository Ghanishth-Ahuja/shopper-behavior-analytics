import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
} from '@mui/material';
import {
  FunnelChart,
  Funnel,
  LabelList,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';

const ConversionFunnelChart = ({ data }) => {
  // Transform API data object into chart array format
  const chartData = React.useMemo(() => {
    if (!data || Object.keys(data).length === 0) {
      return [
        { stage: 'Sessions', value: 1000, fill: '#8884d8' },
        { stage: 'Product Views', value: 750, fill: '#82ca9d' },
        { stage: 'Cart Additions', value: 300, fill: '#ffc658' },
        { stage: 'Purchases', value: 150, fill: '#ff7c7c' },
      ];
    }

    return [
      { stage: 'Sessions', value: data.total_sessions || 0, fill: '#8884d8' },
      { stage: 'Product Views', value: data.view_sessions || 0, fill: '#82ca9d' },
      { stage: 'Cart Additions', value: data.cart_sessions || 0, fill: '#ffc658' },
      { stage: 'Purchases', value: data.purchase_sessions || 0, fill: '#ff7c7c' },
    ];
  }, [data]);

  // Calculate conversion rates
  const conversionRates = React.useMemo(() => {
    const rates = [];
    for (let i = 1; i < chartData.length; i++) {
      const prevValue = chartData[i - 1].value;
      const rate = prevValue > 0 ? ((chartData[i].value / prevValue) * 100).toFixed(1) : '0.0';
      rates.push(rate);
    }
    return rates;
  }, [chartData]);

  return (
    <Box sx={{ width: '100%', height: 300 }}>
      <ResponsiveContainer>
        <FunnelChart>
          <Tooltip />
          <Funnel
            data={chartData}
            dataKey="value"
            nameKey="stage"
            isAnimationActive={true}
            labelLine={false}
            label={(props) => {
              const { x, y, width, height, payload } = props;
              if (!payload || !payload.stage) return null;

              const index = chartData.findIndex(item => item.stage === payload.stage);
              const rate = conversionRates[index - 1];
              
              return (
                <g>
                  <text
                    x={x + width / 2}
                    y={y + height / 2}
                    fill="#fff"
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fontSize={12}
                    fontWeight={500}
                  >
                    {payload.stage}
                  </text>
                  <text
                    x={x + width / 2}
                    y={y + height / 2 + 15}
                    fill="#fff"
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fontSize={10}
                  >
                    {payload.value?.toLocaleString() || 0}
                  </text>
                  {rate && (
                    <text
                      x={x + width / 2}
                      y={y + height / 2 + 30}
                      fill="#fff"
                      textAnchor="middle"
                      dominantBaseline="middle"
                      fontSize={10}
                    >
                      {rate}% conv
                    </text>
                  )}
                </g>
              );
            }}
          />
        </FunnelChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default ConversionFunnelChart;
