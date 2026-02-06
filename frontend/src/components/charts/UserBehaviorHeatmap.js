import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
} from '@mui/material';

const UserBehaviorHeatmap = ({ userId }) => {
  // Default data if none provided
  const defaultData = {
    heatmap: {
      'Monday': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      'Tuesday': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      'Wednesday': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      'Thursday': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      'Friday': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      'Saturday': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      'Sunday': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    },
    maxActivity: 10,
  };

  const chartData = defaultData; // In real app, this would use userId to fetch data

  const getHeatmapColor = (value) => {
    if (value === 0) return '#f5f5f5';
    if (value <= 2) return '#fff3e0';
    if (value <= 4) return '#ffe0b2';
    if (value <= 6) return '#ffcc80';
    if (value <= 8) return '#ffb74d';
    return '#ff9800';
  };

  const hours = Array.from({ length: 24 }, (_, i) => i);

  return (
    <Box sx={{ width: '100%', height: 300 }}>
      <Typography variant="h6" gutterBottom>
        🔥 Activity Heatmap
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        User activity patterns throughout the week
      </Typography>
      
      <Box sx={{ overflowX: 'auto' }}>
        <Grid container spacing={0.5} sx={{ minWidth: 600 }}>
          {/* Hour labels */}
          <Grid item xs={1}>
            <Box sx={{ height: 30 }} />
          </Grid>
          {hours.map((hour) => (
            <Grid item xs={0.5} key={hour}>
              <Typography variant="caption" sx={{ fontSize: '0.6rem', textAlign: 'center' }}>
                {hour}
              </Typography>
            </Grid>
          ))}
          
          {/* Heatmap rows */}
          {Object.entries(chartData.heatmap).map(([day, hourData]) => (
            <Grid container item spacing={0.5} key={day}>
              <Grid item xs={1}>
                <Typography variant="caption" sx={{ fontSize: '0.7rem', pt: 1 }}>
                  {day.slice(0, 3)}
                </Typography>
              </Grid>
              {hourData.map((value, hourIndex) => (
                <Grid item xs={0.5} key={hourIndex}>
                  <Box
                    sx={{
                      width: '100%',
                      height: 20,
                      backgroundColor: getHeatmapColor(value),
                      border: '1px solid #e0e0e0',
                      borderRadius: 1,
                      cursor: 'pointer',
                      '&:hover': {
                        border: '1px solid #666',
                      },
                    }}
                    title={`${day} ${hourIndex}:00 - ${value} activities`}
                  />
                </Grid>
              ))}
            </Grid>
          ))}
        </Grid>
      </Box>
      
      {/* Legend */}
      <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
        <Typography variant="caption" color="text.secondary">
          Activity Level:
        </Typography>
        {[0, 2, 4, 6, 8, 10].map((value) => (
          <Box
            key={value}
            sx={{
              width: 20,
              height: 12,
              backgroundColor: getHeatmapColor(value),
              border: '1px solid #e0e0e0',
              borderRadius: 1,
            }}
          />
        ))}
        <Typography variant="caption" color="text.secondary">
          High
        </Typography>
      </Box>
      
      {/* Insights */}
      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          💡 Activity Insights
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          <Chip
            label="Most Active: Friday 7-9 PM"
            size="small"
            color="primary"
            variant="outlined"
          />
          <Chip
            label="Peak Hours: 6-9 PM"
            size="small"
            color="info"
            variant="outlined"
          />
          <Chip
            label="Weekend Activity: Moderate"
            size="small"
            color="warning"
            variant="outlined"
          />
        </Box>
      </Box>
    </Box>
  );
};

export default UserBehaviorHeatmap;
