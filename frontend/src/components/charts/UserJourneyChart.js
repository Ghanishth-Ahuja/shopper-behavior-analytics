import React from 'react';
import {
  Box,
  Typography,
  Chip,
} from '@mui/material';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
} from '@mui/lab';
import {
  ShoppingCart,
  Visibility,
  Search,
  Favorite,
  LocalOffer,
  Payment,
} from '@mui/icons-material';

const UserJourneyChart = ({ userId }) => {
  // Default data if none provided
  const defaultData = {
    events: [
      {
        timestamp: '2024-01-15T10:30:00Z',
        type: 'search',
        description: 'Searched for "wireless headphones"',
        duration: 45,
      },
      {
        timestamp: '2024-01-15T10:35:00Z',
        type: 'view',
        description: 'Viewed product: Sony WH-1000XM4',
        duration: 120,
      },
      {
        timestamp: '2024-01-15T10:37:00Z',
        type: 'view',
        description: 'Viewed product: Bose QuietComfort 45',
        duration: 90,
      },
      {
        timestamp: '2024-01-15T10:39:00Z',
        type: 'add_to_cart',
        description: 'Added Sony WH-1000XM4 to cart',
        duration: 30,
      },
      {
        timestamp: '2024-01-15T10:40:00Z',
        type: 'view',
        description: 'Viewed cart',
        duration: 60,
      },
      {
        timestamp: '2024-01-15T10:41:00Z',
        type: 'purchase',
        description: 'Completed purchase',
        duration: 180,
      },
    ],
  };

  const chartData = defaultData; // In real app, this would use userId to fetch data

  const getEventIcon = (type) => {
    switch (type) {
      case 'search': return <Search />;
      case 'view': return <Visibility />;
      case 'add_to_cart': return <ShoppingCart />;
      case 'favorite': return <Favorite />;
      case 'coupon': return <LocalOffer />;
      case 'purchase': return <Payment />;
      default: return <Visibility />;
    }
  };

  const getEventColor = (type) => {
    switch (type) {
      case 'search': return 'primary';
      case 'view': return 'info';
      case 'add_to_cart': return 'warning';
      case 'favorite': return 'secondary';
      case 'coupon': return 'success';
      case 'purchase': return 'success';
      default: return 'default';
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: true 
    });
  };

  return (
    <Box sx={{ width: '100%', height: 300 }}>
      <Typography variant="h6" gutterBottom>
        📊 User Journey Timeline
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Track the complete user journey from search to purchase
      </Typography>
      
      <Box sx={{ maxHeight: 250, overflowY: 'auto' }}>
        <Timeline>
          {chartData.events.map((event, index) => (
            <TimelineItem key={index}>
              <TimelineSeparator>
                <TimelineConnector />
              </TimelineSeparator>
              <TimelineDot color={getEventColor(event.type)}>
                {getEventIcon(event.type)}
              </TimelineDot>
              <TimelineContent sx={{ py: '12px', px: 2 }}>
                <Box>
                  <Typography variant="subtitle2" component="span">
                    {event.description}
                  </Typography>
                  <Chip
                    label={`${formatTime(event.timestamp)} • ${event.duration}s`}
                    size="small"
                    variant="outlined"
                    sx={{ ml: 1 }}
                  />
                </Box>
                <Typography variant="body2" color="text.secondary">
                  {event.type === 'search' && 'User searched for products'}
                  {event.type === 'view' && 'User viewed product details'}
                  {event.type === 'add_to_cart' && 'User added item to cart'}
                  {event.type === 'favorite' && 'User favorited item'}
                  {event.type === 'coupon' && 'User applied coupon'}
                  {event.type === 'purchase' && 'User completed purchase'}
                </Typography>
              </TimelineContent>
            </TimelineItem>
          ))}
        </Timeline>
      </Box>
      
      {/* Journey Insights */}
      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          💡 Journey Insights
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          <Chip
            label="Search to Purchase: 11 min"
            size="small"
            color="primary"
            variant="outlined"
          />
          <Chip
            label="3 products viewed"
            size="small"
            color="info"
            variant="outlined"
          />
          <Chip
            label="1 cart addition"
            size="small"
            color="warning"
            variant="outlined"
          />
          <Chip
            label="Conversion: 100%"
            size="small"
            color="success"
            variant="outlined"
          />
        </Box>
      </Box>
    </Box>
  );
};

export default UserJourneyChart;
