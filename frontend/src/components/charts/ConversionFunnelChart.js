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
  // Default data if none provided
  const defaultData = [
    { stage: 'Sessions', value: 1000, fill: '#8884d8' },
    { stage: 'Product Views', value: 750, fill: '#82ca9d' },
    { stage: 'Cart Additions', value: 300, fill: '#ffc658' },
    { stage: 'Purchases', value: 150, fill: '#ff7c7c' },
  ];

  const chartData = data || defaultData;

  // Calculate conversion rates
  const conversionRates = [];
  for (let i = 1; i < chartData.length; i++) {
    const rate = ((chartData[i].value / chartData[i-1].value) * 100).toFixed(1);
    conversionRates.push(rate);
  }

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
              const { x, y, width, height } = props;
              const index = chartData.findIndex(item => item.stage === props.payload.stage);
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
                    {props.payload.stage}
                  </text>
                  <text
                    x={x + width / 2}
                    y={y + height / 2 + 15}
                    fill="#fff"
                    textAnchor="middle"
                    dominantBaseline="middle"
                    fontSize={10}
                  >
                    {props.payload.value.toLocaleString()}
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
