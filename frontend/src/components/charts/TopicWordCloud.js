import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
} from '@mui/material';

const TopicWordCloud = ({ data }) => {
  // Default data if none provided
  const defaultData = {
    topics: [
      { word: 'quality', weight: 85, sentiment: 'positive' },
      { word: 'price', weight: 72, sentiment: 'negative' },
      { word: 'service', weight: 68, sentiment: 'positive' },
      { word: 'shipping', weight: 45, sentiment: 'negative' },
      { word: 'features', weight: 91, sentiment: 'positive' },
      { word: 'design', weight: 58, sentiment: 'positive' },
      { word: 'battery', weight: 34, sentiment: 'negative' },
      { word: 'packaging', weight: 29, sentiment: 'negative' },
      { word: 'support', weight: 76, sentiment: 'positive' },
      { word: 'delivery', weight: 41, sentiment: 'negative' },
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

  const getFontSize = (weight) => {
    // Scale weight to font size (12px to 48px)
    const minSize = 12;
    const maxSize = 48;
    const minWeight = 20;
    const maxWeight = 100;
    
    const scaledSize = minSize + ((weight - minWeight) / (maxWeight - minWeight)) * (maxSize - minSize);
    return Math.round(scaledSize);
  };

  return (
    <Box sx={{ width: '100%', height: 300 }}>
      <Typography variant="h6" gutterBottom>
        🏷️ Topic Modeling - Key Themes
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Discover the main topics and themes emerging from customer reviews
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
        borderRadius: 1
      }}>
        {chartData.topics.map((topic, index) => (
          <Chip
            key={index}
            label={topic.word}
            sx={{
              fontSize: `${getFontSize(topic.weight)}px`,
              fontWeight: topic.weight > 70 ? 600 : topic.weight > 50 ? 500 : 400,
              color: getSentimentColor(topic.sentiment),
              backgroundColor: `${getSentimentColor(topic.sentiment)}15`,
              border: `1px solid ${getSentimentColor(topic.sentiment)}30`,
              cursor: 'pointer',
              '&:hover': {
                backgroundColor: `${getSentimentColor(topic.sentiment)}25`,
                transform: 'scale(1.05)',
              },
              transition: 'all 0.2s ease-in-out',
            }}
            title={`${topic.word}: ${topic.weight} mentions, ${topic.sentiment} sentiment`}
          />
        ))}
      </Box>
      
      {/* Topic Insights */}
      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          💡 Topic Insights
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {chartData.topics.slice(0, 5).map((topic, index) => (
            <Box key={index} sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Chip
                label={topic.word}
                size="small"
                color={topic.sentiment === 'positive' ? 'success' : topic.sentiment === 'negative' ? 'error' : 'default'}
                variant="outlined"
              />
              <Typography variant="caption" color="text.secondary">
                ({topic.weight})
              </Typography>
            </Box>
          ))}
        </Box>
      </Box>
    </Box>
  );
};

export default TopicWordCloud;
