import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  IconButton,
  Tooltip,
  LinearProgress,
} from '@mui/material';
import {
  People,
  ShoppingCart,
  AttachMoney,
  TrendingUp,
  Info,
  ArrowForward,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

const SegmentCard = ({ segment, insights, onSelect }) => {
  const getConversionColor = (rate) => {
    if (rate >= 5) return 'success';
    if (rate >= 3) return 'warning';
    return 'error';
  };

  const getChurnColor = (risk) => {
    switch (risk) {
      case 'low': return 'success';
      case 'medium': return 'warning';
      case 'high': return 'error';
      default: return 'default';
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
          cursor: 'pointer',
          position: 'relative',
          overflow: 'visible',
          '&:hover': {
            boxShadow: 4,
            transform: 'translateY(-2px)',
          },
        }}
        onClick={() => onSelect && onSelect(segment)}
      >
        <CardContent sx={{ p: 2 }}>
          {/* Header */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
            <Box sx={{ flex: 1 }}>
              <Typography variant="h6" gutterBottom>
                {segment.segment_name}
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                {segment.description || 'Customer segment with unique behavioral patterns'}
              </Typography>
              
              {/* Top Categories */}
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
                {segment.top_categories?.slice(0, 3).map((category, index) => (
                  <Chip
                    key={index}
                    label={category}
                    variant="outlined"
                    size="small"
                    color="primary"
                  />
                ))}
              </Box>
            </Box>
            
            <IconButton
              size="small"
              onClick={(e) => {
                e.stopPropagation();
                onSelect && onSelect(segment);
              }}
            >
              <Info />
            </IconButton>
          </Box>

          {/* Key Metrics */}
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={6}>
              <Box sx={{ textAlign: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
                  <People fontSize="small" color="primary" />
                  <Typography variant="caption" color="text.secondary">
                    Users
                  </Typography>
                </Box>
                <Typography variant="h6" color="primary">
                  {segment.size.toLocaleString()}
                </Typography>
              </Box>
            </Grid>

            <Grid item xs={6}>
              <Box sx={{ textAlign: 'center' }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 1 }}>
                  <AttachMoney fontSize="small" color="success" />
                  <Typography variant="caption" color="text.secondary">
                    LTV
                  </Typography>
                </Box>
                <Typography variant="h6" color="success">
                  ${(segment.avg_lifetime_value || 0).toFixed(0)}
                </Typography>
              </Box>
            </Grid>
          </Grid>

          {/* Behavioral Traits */}
          {insights && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                🎯 Behavioral Traits
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {insights.key_behaviors?.slice(0, 3).map((behavior, index) => (
                  <Chip
                    key={index}
                    label={behavior}
                    variant="outlined"
                    size="small"
                    color="secondary"
                  />
                ))}
              </Box>
            </Box>
          )}

          {/* Performance Indicators */}
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
              📊 Performance
            </Typography>
            
            {/* Conversion Rate */}
            <Box sx={{ mb: 1 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                <Typography variant="body2" color="text.secondary">
                  Conversion Rate
                </Typography>
                <Typography variant="body2" fontWeight={600}>
                  {insights?.conversion_rate?.toFixed(1) || 0}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={insights?.conversion_rate || 0}
                color={getConversionColor(insights?.conversion_rate)}
                sx={{ height: 6 }}
              />
            </Box>

            {/* Churn Risk */}
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Typography variant="body2" color="text.secondary">
                Churn Risk
              </Typography>
              <Chip
                label={insights?.churn_risk || 'medium'}
                size="small"
                color={getChurnColor(insights?.churn_risk)}
              />
            </Box>
          </Box>

          {/* Price Sensitivity */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              Price Sensitivity
            </Typography>
            <Chip
              label={segment.price_sensitivity}
              size="small"
              color={segment.price_sensitivity === 'high' ? 'error' : segment.price_sensitivity === 'low' ? 'success' : 'warning'}
            />
          </Box>

          {/* Action Button */}
          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Button
              variant="contained"
              endIcon={<ArrowForward />}
              onClick={() => onSelect && onSelect(segment)}
              fullWidth
            >
              View Details
            </Button>
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default SegmentCard;
