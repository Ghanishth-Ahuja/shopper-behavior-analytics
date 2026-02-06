import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  Tabs,
  Tab,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
} from '@mui/material';
import {
  SentimentVerySatisfied,
  SentimentVeryDissatisfied,
  SentimentNeutral,
  TrendingUp,
  TrendingDown,
  Psychology,
  Comment,
  Topic,
  Refresh,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';

import { useApp } from '../context/AppContext';
import { analyticsApi } from '../api/analyticsApi';
import SentimentTrendChart from '../components/charts/SentimentTrendChart';
import AspectSentimentChart from '../components/charts/AspectSentimentChart';
import TopicWordCloud from '../components/charts/TopicWordCloud';
import ReviewClusterChart from '../components/charts/ReviewClusterChart';

const TabPanel = ({ children, value, index, ...other }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`review-tabpanel-${index}`}
      aria-labelledby={`review-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
};

const ReviewIntelligence = () => {
  const { dateRange } = useApp();
  const [tabValue, setTabValue] = React.useState(0);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [selectedTimeRange, setSelectedTimeRange] = useState('30');

  // Fetch sentiment analysis
  const { data: sentimentData, isLoading: sentimentLoading } = useQuery(
    ['sentimentAnalysis', selectedCategory],
    () => analyticsApi.getSentimentAnalysis(selectedCategory),
    {
      refetchInterval: 120000, // Refresh every 2 minutes
    }
  );

  // Fetch sentiment trends
  const { data: sentimentTrends, isLoading: trendsLoading } = useQuery(
    ['sentimentTrends', selectedCategory, selectedTimeRange],
    () => analyticsApi.getSentimentTrends(selectedCategory, selectedTimeRange),
    {
      refetchInterval: 300000, // Refresh every 5 minutes
    }
  );

  // Fetch categories for filter
  const { data: categories, isLoading: categoriesLoading } = useQuery(
    ['categories'],
    async () => {
      // This would come from your API
      return ['Electronics', 'Clothing', 'Home', 'Books', 'Sports', 'Beauty', 'Toys'];
    }
  );

  // Calculate sentiment metrics
  const sentimentMetrics = React.useMemo(() => {
    if (!sentimentData) return {
      total: 0,
      positive: 0,
      negative: 0,
      neutral: 0,
      positivePercentage: 0,
      negativePercentage: 0,
      avgRating: 0,
    };

    const total = sentimentData.total_reviews || 0;
    const positive = sentimentData.sentiment_distribution?.positive || 0;
    const negative = sentimentData.sentiment_distribution?.negative || 0;
    const neutral = sentimentData.sentiment_distribution?.neutral || 0;

    return {
      total,
      positive,
      negative,
      neutral,
      positivePercentage: total > 0 ? (positive / total * 100) : 0,
      negativePercentage: total > 0 ? (negative / total * 100) : 0,
      avgRating: sentimentData.avg_rating || 0,
    };
  }, [sentimentData]);

  // Get sentiment trend
  const sentimentTrend = React.useMemo(() => {
    if (!sentimentTrends || !sentimentTrends.sentiment_trends) return 'stable';
    
    const trends = sentimentTrends.sentiment_trends;
    const recentTrend = Object.values(trends).slice(-3); // Last 3 data points
    
    if (recentTrend.length < 2) return 'stable';
    
    const first = recentTrend[0].avg_sentiment;
    const last = recentTrend[recentTrend.length - 1].avg_sentiment;
    
    if (last > first + 0.1) return 'improving';
    if (last < first - 0.1) return 'declining';
    return 'stable';
  }, [sentimentTrends]);

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          💬 Review Intelligence
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Analyze customer sentiment, extract insights from reviews, and understand customer voice patterns
        </Typography>
      </Box>

      {/* Sentiment Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Comment color="primary" />
                <Typography variant="subtitle2">Total Reviews</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {sentimentMetrics.total.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                All time
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <SentimentVerySatisfied color="success" />
                <Typography variant="subtitle2">Positive</Typography>
              </Box>
              <Typography variant="h4" color="success">
                {sentimentMetrics.positivePercentage.toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {sentimentMetrics.positive.toLocaleString()} reviews
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <SentimentVeryDissatisfied color="error" />
                <Typography variant="subtitle2">Negative</Typography>
              </Box>
              <Typography variant="h4" color="error">
                {sentimentMetrics.negativePercentage.toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {sentimentMetrics.negative.toLocaleString()} reviews
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <SentimentNeutral color="warning" />
                <Typography variant="subtitle2">Avg Rating</Typography>
              </Box>
              <Typography variant="h4" color="warning">
                {sentimentMetrics.avgRating.toFixed(1)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Out of 5 stars
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Controls */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Filter by Category</InputLabel>
              <Select
                value={selectedCategory}
                label="Filter by Category"
                onChange={(e) => setSelectedCategory(e.target.value)}
              >
                <MenuItem value="">All Categories</MenuItem>
                {categories?.map(category => (
                  <MenuItem key={category} value={category}>
                    {category}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Time Range</InputLabel>
              <Select
                value={selectedTimeRange}
                label="Time Range"
                onChange={(e) => setSelectedTimeRange(e.target.value)}
              >
                <MenuItem value="7">Last 7 days</MenuItem>
                <MenuItem value="30">Last 30 days</MenuItem>
                <MenuItem value="90">Last 90 days</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      {/* Sentiment Trend Indicator */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
      >
        <Alert 
          severity={sentimentTrend === 'improving' ? 'success' : sentimentTrend === 'declining' ? 'error' : 'info'}
          sx={{ mb: 4 }}
          icon={sentimentTrend === 'improving' ? <TrendingUp /> : sentimentTrend === 'declining' ? <TrendingDown /> : <SentimentNeutral />}
        >
          <Typography variant="subtitle2" gutterBottom>
            Sentiment is {sentimentTrend}
          </Typography>
          <Typography variant="body2">
            {sentimentTrend === 'improving' && 'Customer sentiment has been improving over the selected period.'}
            {sentimentTrend === 'declining' && 'Customer sentiment has been declining. Consider investigating recent changes.'}
            {sentimentTrend === 'stable' && 'Customer sentiment remains stable over the selected period.'}
          </Typography>
        </Alert>
      </motion.div>

      {/* Tabs */}
      <Paper sx={{ mb: 4 }}>
        <Tabs
          value={tabValue}
          onChange={(e, newValue) => setTabValue(newValue)}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="📈 Sentiment Trends" />
          <Tab label="🎯 Aspect Analysis" />
          <Tab label="🏷️ Topic Modeling" />
          <Tab label="🔍 Review Clusters" />
        </Tabs>

        {/* Sentiment Trends Tab */}
        <TabPanel value={tabValue} index={0}>
          <Typography variant="h6" gutterBottom>
            📈 Sentiment Trends Over Time
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Track how customer sentiment changes over time for different categories and products.
          </Typography>
          <SentimentTrendChart data={sentimentTrends} />
        </TabPanel>

        {/* Aspect Analysis Tab */}
        <TabPanel value={tabValue} index={1}>
          <Typography variant="h6" gutterBottom>
            🎯 Aspect-Based Sentiment Analysis
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Understand what specific aspects of products customers are happy or unhappy about.
          </Typography>
          <AspectSentimentChart data={sentimentData} />
        </TabPanel>

        {/* Topic Modeling Tab */}
        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            🏷️ Topic Modeling
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Discover the main topics and themes emerging from customer reviews.
          </Typography>
          <TopicWordCloud />
        </TabPanel>

        {/* Review Clusters Tab */}
        <TabPanel value={tabValue} index={3}>
          <Typography variant="h6" gutterBottom>
            🔍 Review Clustering
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Group similar reviews together to identify patterns and common themes.
          </Typography>
          <ReviewClusterChart />
        </TabPanel>
      </Paper>

      {/* Key Insights */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
      >
        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            💡 Key Insights from Review Analysis
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <List>
                <ListItem>
                  <ListItemIcon>
                    <Psychology color="primary" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Aspect Performance"
                    secondary="Customers are most satisfied with product quality and most concerned about pricing"
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemIcon>
                    <Topic color="secondary" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Emerging Topics"
                    secondary="Customer service and shipping are the most frequently mentioned topics"
                  />
                </ListItem>
              </List>
            </Grid>
            
            <Grid item xs={12} md={6}>
              <List>
                <ListItem>
                  <ListItemIcon>
                    <TrendingUp color="success" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Improvement Areas"
                    secondary="Focus on reducing negative mentions about delivery times and product packaging"
                  />
                </ListItem>
                <Divider />
                <ListItem>
                  <ListItemIcon>
                    <Comment color="warning" />
                  </ListItemIcon>
                  <ListItemText 
                    primary="Review Patterns"
                    secondary="Detailed reviews correlate with higher customer satisfaction scores"
                  />
                </ListItem>
              </List>
            </Grid>
          </Grid>
        </Paper>
      </motion.div>
    </Box>
  );
};

export default ReviewIntelligence;
