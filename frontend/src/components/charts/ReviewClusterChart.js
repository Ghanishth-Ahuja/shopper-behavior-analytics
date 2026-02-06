import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
} from '@mui/material';

const ReviewClusterChart = ({ data }) => {
  // Default data if none provided
  const defaultData = {
    clusters: [
      {
        name: 'Quality Enthusiasts',
        size: 245,
        keywords: ['quality', 'excellent', 'perfect', 'premium'],
        avgRating: 4.8,
        sentiment: 'positive',
      },
      {
        name: 'Price Conscious',
        size: 189,
        keywords: ['price', 'expensive', 'cheap', 'value'],
        avgRating: 3.2,
        sentiment: 'negative',
      },
      {
        name: 'Service Focused',
        size: 156,
        keywords: ['service', 'support', 'helpful', 'responsive'],
        avgRating: 4.5,
        sentiment: 'positive',
      },
      {
        name: 'Shipping Issues',
        size: 98,
        keywords: ['shipping', 'delivery', 'late', 'damaged'],
        avgRating: 2.1,
        sentiment: 'negative',
      },
      {
        name: 'Feature Seekers',
        size: 134,
        keywords: ['features', 'functionality', 'options', 'versatile'],
        avgRating: 4.2,
        sentiment: 'positive',
      },
    ],
  };

  const chartData = data || defaultData;

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'positive': return '#22c55e';
      case 'negative': return '#ef5350';
      case 'neutral': return '#9e9e9e';
      default: return '#9e9e9e';
    }
  };

  const getClusterSize = (size) => {
    // Scale size to visual representation
    const minSize = 60;
    const maxSize = 200;
    const minCount = 50;
    const maxCount = 300;
    
    const scaledSize = minSize + ((size - minCount) / (maxCount - minCount)) * (maxSize - minSize);
    return Math.round(scaledSize);
  };

  return (
    <Box sx={{ width: '100%', height: 300 }}>
      <Typography variant="h6" gutterBottom>
        🔍 Review Clustering
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Group similar reviews together to identify patterns and common themes
      </Typography>
      
      <Box sx={{ 
        display: 'flex', 
        flexWrap: 'wrap', 
        gap: 2, 
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: 200,
        p: 2,
        border: '1px dashed #ccc',
        borderRadius: 1,
        position: 'relative'
      }}>
        {chartData.clusters.map((cluster, index) => (
          <Box
            key={index}
            sx={{
              width: `${getClusterSize(cluster.size)}px`,
              height: `${getClusterSize(cluster.size)}px`,
              borderRadius: '50%',
              backgroundColor: `${getSentimentColor(cluster.sentiment)}15`,
              border: `2px solid ${getSentimentColor(cluster.sentiment)}50`,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              '&:hover': {
                backgroundColor: `${getSentimentColor(cluster.sentiment)}25`,
                transform: 'scale(1.05)',
              },
              transition: 'all 0.2s ease-in-out',
              p: 1,
            }}
            title={`${cluster.name}: ${cluster.size} reviews, ${cluster.avgRating} avg rating`}
          >
            <Typography 
              variant="subtitle2" 
              sx={{ 
                fontSize: cluster.size > 200 ? '0.9rem' : cluster.size > 150 ? '0.8rem' : '0.7rem',
                fontWeight: 600,
                color: getSentimentColor(cluster.sentiment),
                textAlign: 'center',
                mb: 0.5
              }}
            >
              {cluster.name}
            </Typography>
            <Typography 
              variant="caption" 
              sx={{ 
                fontSize: '0.6rem',
                color: 'text.secondary',
                textAlign: 'center'
              }}
            >
              {cluster.size} reviews
            </Typography>
            <Typography 
              variant="caption" 
              sx={{ 
                fontSize: '0.6rem',
                color: getSentimentColor(cluster.sentiment),
                fontWeight: 500
              }}
            >
              ⭐ {cluster.avgRating}
            </Typography>
          </Box>
        ))}
      </Box>
      
      {/* Cluster Details */}
      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          📊 Cluster Analysis
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2 }}>
          {chartData.clusters.map((cluster, index) => (
            <Card key={index} sx={{ minWidth: 200, p: 1 }}>
              <CardContent sx={{ p: 1, '&:last-child': { pb: 1 } }}>
                <Typography variant="subtitle2" gutterBottom>
                  {cluster.name}
                </Typography>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Size: {cluster.size}
                  </Typography>
                  <Chip
                    label={`${cluster.avgRating} ⭐`}
                    size="small"
                    color={cluster.sentiment === 'positive' ? 'success' : cluster.sentiment === 'negative' ? 'error' : 'default'}
                    variant="outlined"
                  />
                </Box>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                  {cluster.keywords.slice(0, 3).map((keyword, kIndex) => (
                    <Chip
                      key={kIndex}
                      label={keyword}
                      size="small"
                      variant="outlined"
                    />
                  ))}
                </Box>
              </CardContent>
            </Card>
          ))}
        </Box>
      </Box>
    </Box>
  );
};

export default ReviewClusterChart;
