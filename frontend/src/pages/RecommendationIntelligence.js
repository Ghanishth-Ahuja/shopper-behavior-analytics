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
  Button,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Tabs,
  Tab,
  LinearProgress,
  Tooltip,
} from '@mui/material';
import {
  TrendingUp,
  Psychology,
  Person,
  Category,
  BarChart,
  Lightbulb,
  Refresh,
  Info,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';

import { useApp } from '../context/AppContext';
import { recommendationApi } from '../api/recommendationApi';
import { analyticsApi } from '../api/analyticsApi';
import RecommendationList from '../components/recommendations/RecommendationList';
import RecommendationPerformanceChart from '../components/charts/RecommendationPerformanceChart';
import ModelComparisonChart from '../components/charts/ModelComparisonChart';

const TabPanel = ({ children, value, index, ...other }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`recommendation-tabpanel-${index}`}
      aria-labelledby={`recommendation-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
};

const RecommendationIntelligence = () => {
  const { selectedSegment: appSelectedSegment, segments } = useApp();
  const [tabValue, setTabValue] = React.useState(0);
  const [selectedModel, setSelectedModel] = useState('hybrid');
  const [selectedSegment, setSelectedSegment] = useState('');

  // Fetch segment recommendations
  const { data: segmentRecommendations, isLoading: segmentLoading } = useQuery(
    ['segmentRecommendations', selectedSegment, selectedModel],
    () => recommendationApi.getSegmentRecommendations(selectedSegment, { 
      limit: 20,
      algorithm: selectedModel 
    }),
    {
      enabled: !!selectedSegment,
      refetchInterval: 60000, // Refresh every minute
    }
  );

  // Fetch performance metrics
  const { data: performanceMetrics, isLoading: performanceLoading } = useQuery(
    ['recommendationPerformance'],
    () => recommendationApi.getPerformanceMetrics(),
    {
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  );

  // Fetch analytics data
  const { data: analyticsData, isLoading: analyticsLoading } = useQuery(
    ['recommendationAnalytics'],
    () => recommendationApi.getRecommendationAnalytics(),
    {
      refetchInterval: 120000, // Refresh every 2 minutes
    }
  );

  // Fetch A/B test results
  const { data: abTestResults, isLoading: abTestLoading } = useQuery(
    ['abTestResults'],
    () => recommendationApi.getABTestResults('rec_algo_v2'),
    {
      refetchInterval: 300000, // Refresh every 5 minutes
    }
  );

  // Handle model refresh
  const handleRefreshModels = async () => {
    try {
      await recommendationApi.refreshModels();
      // Refresh data
      window.location.reload();
    } catch (error) {
      console.error('Error refreshing models:', error);
    }
  };

  // Calculate key metrics
  const keyMetrics = React.useMemo(() => {
    if (!performanceMetrics) return {
      totalRecommendations: 0,
      clickRate: 0,
      conversionRate: 0,
      avgPosition: 0,
    };

    return {
      totalRecommendations: performanceMetrics.total_recommendations || 0,
      clickRate: performanceMetrics.click_rate || 0,
      conversionRate: performanceMetrics.conversion_rate || 0,
      avgPosition: performanceMetrics.avg_position || 0,
    };
  }, [performanceMetrics]);

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          🎯 Recommendation Intelligence
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Analyze and optimize ML-powered product recommendations across customer segments
        </Typography>
      </Box>

      {/* Performance Overview */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <BarChart color="primary" />
                <Typography variant="subtitle2">Total Recommendations</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {keyMetrics.totalRecommendations.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Last 30 days
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <TrendingUp color="success" />
                <Typography variant="subtitle2">Click Rate</Typography>
              </Box>
              <Typography variant="h4" color="success">
                {keyMetrics.clickRate.toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Engagement rate
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Category color="warning" />
                <Typography variant="subtitle2">Conversion Rate</Typography>
              </Box>
              <Typography variant="h4" color="warning">
                {keyMetrics.conversionRate.toFixed(1)}%
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Purchase rate
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Psychology color="info" />
                <Typography variant="subtitle2">Avg Position</Typography>
              </Box>
              <Typography variant="h4" color="info">
                {keyMetrics.avgPosition.toFixed(1)}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Recommendation position
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Controls */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Select Segment</InputLabel>
              <Select
                value={selectedSegment}
                label="Select Segment"
                onChange={(e) => setSelectedSegment(e.target.value)}
              >
                <MenuItem value="">All Segments</MenuItem>
                {segments?.map(segment => (
                  <MenuItem key={segment.segment_id} value={segment.segment_id}>
                    {segment.segment_name} ({segment.size} users)
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Recommendation Model</InputLabel>
              <Select
                value={selectedModel}
                label="Recommendation Model"
                onChange={(e) => setSelectedModel(e.target.value)}
              >
                <MenuItem value="hybrid">Hybrid Model</MenuItem>
                <MenuItem value="collaborative">Collaborative Filtering</MenuItem>
                <MenuItem value="content">Content-Based</MenuItem>
                <MenuItem value="segment">Segment-Based</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={3}>
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={handleRefreshModels}
              fullWidth
            >
              Refresh Models
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* Tabs */}
      <Paper sx={{ mb: 4 }}>
        <Tabs
          value={tabValue}
          onChange={(e, newValue) => setTabValue(newValue)}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="🎯 Recommendations" />
          <Tab label="📊 Performance" />
          <Tab label="🧪 A/B Testing" />
          <Tab label="⚙️ Models" />
        </Tabs>

        {/* Recommendations Tab */}
        <TabPanel value={tabValue} index={0}>
          <Box>
            {selectedSegment ? (
              <>
                <Typography variant="h6" gutterBottom>
                  🎯 Recommendations for {segments?.find(s => s.segment_id === selectedSegment)?.segment_name}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  Using {selectedModel} model • {segmentRecommendations?.length || 0} recommendations
                </Typography>
                <RecommendationList 
                  recommendations={segmentRecommendations} 
                  loading={segmentLoading}
                  showReasoning={true}
                  showPerformance={true}
                />
              </>
            ) : (
              <Alert severity="info">
                <Typography variant="body2">
                  Please select a segment to view personalized recommendations.
                </Typography>
              </Alert>
            )}
          </Box>
        </TabPanel>

        {/* Performance Tab */}
        <TabPanel value={tabValue} index={1}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Typography variant="h6" gutterBottom>
                📈 Performance Trends
              </Typography>
              <RecommendationPerformanceChart data={analyticsData} />
            </Grid>

            <Grid item xs={12} md={4}>
              <Typography variant="h6" gutterBottom>
                📊 Performance Metrics
              </Typography>
              <TableContainer>
                <Table>
                  <TableBody>
                    <TableRow>
                      <TableCell component="th" scope="row">Click Rate</TableCell>
                      <TableCell align="right">
                        <Chip 
                          label={`${keyMetrics.clickRate.toFixed(1)}%`}
                          color={keyMetrics.clickRate > 15 ? 'success' : keyMetrics.clickRate > 10 ? 'warning' : 'error'}
                        />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell component="th" scope="row">Conversion Rate</TableCell>
                      <TableCell align="right">
                        <Chip 
                          label={`${keyMetrics.conversionRate.toFixed(1)}%`}
                          color={keyMetrics.conversionRate > 3 ? 'success' : keyMetrics.conversionRate > 2 ? 'warning' : 'error'}
                        />
                      </TableCell>
                    </TableRow>
                    <TableRow>
                      <TableCell component="th" scope="row">Avg Position</TableCell>
                      <TableCell align="right">
                        <Chip 
                          label={keyMetrics.avgPosition.toFixed(1)}
                          color={keyMetrics.avgPosition < 5 ? 'success' : keyMetrics.avgPosition < 10 ? 'warning' : 'error'}
                        />
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </TableContainer>
            </Grid>
          </Grid>
        </TabPanel>

        {/* A/B Testing Tab */}
        <TabPanel value={tabValue} index={2}>
          <Typography variant="h6" gutterBottom>
            🧪 A/B Test Results
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
            Comparing different recommendation algorithms to find the optimal approach
          </Typography>
          <ModelComparisonChart data={abTestResults} />
        </TabPanel>

        {/* Models Tab */}
        <TabPanel value={tabValue} index={3}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                🤖 Model Performance
              </Typography>
              <Alert severity="info" icon={<Info />}>
                <Typography variant="body2" paragraph>
                  <strong>Hybrid Model:</strong> Combines collaborative filtering, content-based filtering, and segment-based recommendations for optimal performance.
                </Typography>
                <Typography variant="body2">
                  <strong>Collaborative Filtering:</strong> Uses user-item interaction patterns to recommend products similar users liked.
                </Typography>
                <Typography variant="body2">
                  <strong>Content-Based:</strong> Recommends products based on item attributes and user preferences.
                </Typography>
                <Typography variant="body2">
                  <strong>Segment-Based:</strong> Leverages customer segment characteristics for targeted recommendations.
                </Typography>
              </Alert>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                💡 Model Insights
              </Typography>
              <Box>
                <Alert severity="success" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2">Hybrid Model Leading</Typography>
                  <Typography variant="body2">
                    32% higher conversion rate compared to individual models
                  </Typography>
                </Alert>
                
                <Alert severity="warning" sx={{ mb: 2 }}>
                  <Typography variant="subtitle2">Segment Performance Varies</Typography>
                  <Typography variant="body2">
                    Some segments respond better to content-based recommendations
                  </Typography>
                </Alert>
                
                <Alert severity="info">
                  <Typography variant="subtitle2">Real-Time Boost Effective</Typography>
                  <Typography variant="body2">
                    Session-based improvements increase engagement by 18%
                  </Typography>
                </Alert>
              </Box>
            </Grid>
          </Grid>
        </TabPanel>
      </Paper>
    </Box>
  );
};

export default RecommendationIntelligence;
