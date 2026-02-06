import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardMedia,
  Chip,
  Button,
  IconButton,
  Tooltip,
  Rating,
  LinearProgress,
  Alert,
} from '@mui/material';
import {
  ShoppingCart,
  Visibility,
  ThumbUp,
  ThumbDown,
  Info,
  Refresh,
} from '@mui/icons-material';
import { motion } from 'framer-motion';

const RecommendationList = ({ 
  recommendations, 
  loading = false, 
  showReasoning = false, 
  showPerformance = false 
}) => {
  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
        <Typography variant="body2" sx={{ mt: 2 }} textAlign="center">
          Loading recommendations...
        </Typography>
      </Box>
    );
  }

  if (!recommendations || recommendations.length === 0) {
    return (
      <Alert severity="info" sx={{ m: 2 }}>
        <Typography variant="body2">
          No recommendations available. Try adjusting your filters or check back later.
        </Typography>
      </Alert>
    );
  }

  const handleFeedback = (recommendationId, feedback) => {
    // This would call your API to record feedback
    console.log(`Feedback recorded for ${recommendationId}: ${feedback}`);
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom sx={{ mb: 3 }}>
        🎯 Recommended Products ({recommendations.length})
      </Typography>
      
      <Box sx={{ display: 'grid', gap: 3 }}>
        {recommendations.map((recommendation, index) => (
          <motion.div
            key={recommendation.product_id}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              {/* Product Image */}
              <CardMedia
                component="div"
                sx={{
                  height: 140,
                  backgroundColor: 'grey.200',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <ShoppingCart sx={{ fontSize: 48, color: 'text.secondary' }} />
              </CardMedia>

              <CardContent sx={{ flex: 1, p: 2 }}>
                {/* Product Info */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    {recommendation.product_details?.product_id || recommendation.product_id}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                    {recommendation.product_details?.category || 'Unknown Category'}
                  </Typography>
                  {recommendation.product_details?.brand && (
                    <Typography variant="caption" color="text.secondary">
                      Brand: {recommendation.product_details.brand}
                    </Typography>
                  )}
                </Box>

                {/* Score and Reasoning */}
                <Box sx={{ mb: 2 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography variant="subtitle2" color="primary">
                      Score: {recommendation.score.toFixed(2)}
                    </Typography>
                    {showPerformance && (
                      <Chip
                        label={`${(100 - recommendation.position)}%`}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    )}
                  </Box>
                  
                  {showReasoning && recommendation.reason && (
                    <Alert severity="info" sx={{ mb: 1 }}>
                      <Typography variant="caption">
                        {recommendation.reason}
                      </Typography>
                    </Alert>
                  )}
                </Box>

                {/* Additional Metrics */}
                <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                  {recommendation.segment_boost && (
                    <Chip
                      label={`Segment: +${(recommendation.segment_boost * 100).toFixed(0)}%`}
                      size="small"
                      color="secondary"
                      variant="outlined"
                    />
                  )}
                  {recommendation.real_time_boost && (
                    <Chip
                      label={`Real-time: +${(recommendation.real_time_boost * 100).toFixed(0)}%`}
                      size="small"
                      color="success"
                      variant="outlined"
                    />
                  )}
                </Box>

                {/* Rating */}
                {recommendation.product_details?.rating && (
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                    <Rating
                      value={recommendation.product_details.rating}
                      readOnly
                      size="small"
                      precision={0.5}
                    />
                    <Typography variant="body2" color="text.secondary">
                      ({recommendation.product_details.rating.toFixed(1)})
                    </Typography>
                  </Box>
                )}

                {/* Price */}
                {recommendation.product_details?.price_history && (
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="body2" color="text.secondary">
                      Price: ${recommendation.product_details.price_history[recommendation.product_details.price_history.length - 1]?.price || 'N/A'}
                    </Typography>
                  </Box>
                )}

                {/* Action Buttons */}
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Button
                    variant="contained"
                    size="small"
                    startIcon={<ShoppingCart />}
                    fullWidth
                  >
                    View Product
                  </Button>
                  
                  <Tooltip title="Explain recommendation">
                    <IconButton size="small">
                      <Info />
                    </IconButton>
                  </Tooltip>
                </Box>

                {/* Feedback Buttons */}
                <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
                  <Tooltip title="This recommendation was helpful">
                    <IconButton
                      size="small"
                      color="success"
                      onClick={() => handleFeedback(recommendation.product_id, 'click')}
                    >
                      <ThumbUp />
                    </IconButton>
                  </Tooltip>
                  
                  <Tooltip title="This recommendation was not helpful">
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleFeedback(recommendation.product_id, 'ignore')}
                    >
                      <ThumbDown />
                    </IconButton>
                  </Tooltip>
                  
                  <Tooltip title="I purchased this">
                    <IconButton
                      size="small"
                      color="primary"
                      onClick={() => handleFeedback(recommendation.product_id, 'purchase')}
                    >
                      <Visibility />
                    </IconButton>
                  </Tooltip>
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </Box>
    </Box>
  );
};

export default RecommendationList;
