import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  TrendingUp,
  TrendingDown,
  TrendingFlat,
} from '@mui/material';
import { motion } from 'framer-motion';

const MetricCard = ({ 
  title, 
  value, 
  subtitle, 
  trend, 
  trendValue, 
  color = 'primary',
  icon,
  loading = false,
  onClick,
}) => {
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp color="success" />;
      case 'down':
        return <TrendingDown color="error" />;
      default:
        return <TrendingFlat color="action" />;
    }
  };

  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return 'success.main';
      case 'down':
        return 'error.main';
      default:
        return 'text.secondary';
    }
  };

  return (
    <motion.div
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
    >
      <Card
        sx={{
          height: '100%',
          cursor: onClick ? 'pointer' : 'default',
          background: `linear-gradient(135deg, ${color === 'primary' ? '#1976d2' : color === 'secondary' ? '#dc004e' : '#2e7d32'}15, transparent)`,
          border: `1px solid ${color === 'primary' ? '#1976d230' : color === 'secondary' ? '#dc004e30' : '#2e7d3230'}`,
          '&:hover': {
            boxShadow: 3,
            background: `linear-gradient(135deg, ${color === 'primary' ? '#1976d2' : color === 'secondary' ? '#dc004e' : '#2e7d32'}25, transparent)`,
          },
        }}
        onClick={onClick}
      >
        <CardContent sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 2 }}>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                {title}
              </Typography>
              {loading ? (
                <Box sx={{ width: 60, height: 32, bgcolor: 'grey.200', borderRadius: 1 }} />
              ) : (
                <Typography variant="h4" component="div" color={color} fontWeight="bold">
                  {typeof value === 'number' ? value.toLocaleString() : value}
                </Typography>
              )}
            </Box>
            {icon && (
              <Box sx={{ ml: 2, color: `${color}.main`, opacity: 0.7 }}>
                {icon}
              </Box>
            )}
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Typography variant="body2" color="text.secondary">
              {subtitle}
            </Typography>
            
            {trend && (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                {getTrendIcon()}
                <Typography 
                  variant="body2" 
                  sx={{ color: getTrendColor(), fontWeight: 600 }}
                >
                  {trendValue}
                </Typography>
              </Box>
            )}
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default MetricCard;
