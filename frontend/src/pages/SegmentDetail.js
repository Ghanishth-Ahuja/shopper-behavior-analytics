import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Paper,
  Chip,
  Button,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Alert,
  Tabs,
  Tab,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  ArrowBack,
  People,
  ShoppingCart,
  AttachMoney,
  TrendingUp,
  Psychology,
  Schedule,
  ThumbUp,
  ThumbDown,
  Campaign,
  Lightbulb,
  Star,
  Timeline,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';

import { useApp } from '../context/AppContext';
import { analyticsApi } from '../api/analyticsApi';
import { recommendationApi } from '../api/recommendationApi';
import MetricCard from '../components/common/MetricCard';
import LoadingSpinner from '../components/common/LoadingSpinner';
import SegmentBehaviorChart from '../components/charts/SegmentBehaviorChart';
import CategoryAffinityRadar from '../components/charts/CategoryAffinityRadar';
import RecommendationList from '../components/recommendations/RecommendationList';

const TabPanel = ({ children, value, index, ...other }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`segment-tabpanel-${index}`}
      aria-labelledby={`segment-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
};

const SegmentDetail = () => {
  const { segmentId } = useParams();
  const navigate = useNavigate();
  const { selectedSegment, setSelectedSegment } = useApp();
  const [tabValue, setTabValue] = React.useState(0);

  // Fetch segment details
  const { data: segment, isLoading: segmentLoading } = useQuery(
    ['segment', segmentId],
    () => analyticsApi.getSegment(segmentId),
    {
      enabled: !!segmentId,
      onSuccess: (data) => setSelectedSegment(data),
    }
  );

  // Fetch segment insights
  const { data: insights, isLoading: insightsLoading } = useQuery(
    ['segmentInsights', segmentId],
    () => analyticsApi.getSegmentInsights(segmentId),
    {
      enabled: !!segmentId,
    }
  );

  // Fetch segment recommendations
  const { data: recommendations, isLoading: recommendationsLoading } = useQuery(
    ['segmentRecommendations', segmentId],
    () => recommendationApi.getSegmentRecommendations(segmentId, { limit: 10 }),
    {
      enabled: !!segmentId,
    }
  );

  // Fetch segment users
  const { data: users, isLoading: usersLoading } = useQuery(
    ['segmentUsers', segmentId],
    () => analyticsApi.getSegmentUsers(segmentId, { limit: 20 }),
    {
      enabled: !!segmentId,
    }
  );

  if (segmentLoading || !segment) {
    return <LoadingSpinner fullScreen message="Loading segment details..." />;
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4, display: 'flex', alignItems: 'center', gap: 2 }}>
        <Button
          startIcon={<ArrowBack />}
          onClick={() => navigate('/segments')}
        >
          Back to Segments
        </Button>
        <Box sx={{ flex: 1 }}>
          <Typography variant="h4" gutterBottom>
            {segment.segment_name}
          </Typography>
          <Typography variant="body1" color="text.secondary">
            {segment.description || 'Customer segment with behavioral patterns and preferences'}
          </Typography>
        </Box>
        <Chip
          label={`${segment.size} users`}
          color="primary"
          variant="outlined"
          size="medium"
        />
      </Box>

      {/* Key Metrics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Segment Size"
            value={segment.size.toLocaleString()}
            subtitle="Total customers"
            color="primary"
            icon={<People />}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Avg Order Value"
            value={`$${(insights?.avg_order_value || 0).toFixed(2)}`}
            subtitle="Per transaction"
            color="success"
            icon={<AttachMoney />}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Conversion Rate"
            value={`${(insights?.conversion_rate || 0).toFixed(1)}%`}
            subtitle="Purchase conversion"
            color="warning"
            icon={<TrendingUp />}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Churn Risk"
            value={insights?.churn_risk || 'medium'}
            subtitle="Risk level"
            color={insights?.churn_risk === 'high' ? 'error' : insights?.churn_risk === 'low' ? 'success' : 'warning'}
            icon={<Psychology />}
          />
        </Grid>
      </Grid>

      {/* Tabs */}
      <Paper sx={{ mb: 4 }}>
        <Tabs
          value={tabValue}
          onChange={(e, newValue) => setTabValue(newValue)}
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab label="🎯 Overview" />
          <Tab label="📊 Behavior" />
          <Tab label="🛍 Preferences" />
          <Tab label="💬 Insights" />
          <Tab label="🎯 Recommendations" />
          <Tab label="👥 Users" />
        </Tabs>

        {/* Overview Tab */}
        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                🎯 Key Characteristics
              </Typography>
              <List>
                {insights?.key_behaviors?.map((behavior, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <Star color="primary" />
                    </ListItemIcon>
                    <ListItemText primary={behavior} />
                  </ListItem>
                ))}
              </List>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                💡 Marketing Insights
              </Typography>
              <List>
                {insights?.recommendations?.map((recommendation, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <Lightbulb color="warning" />
                    </ListItemIcon>
                    <ListItemText primary={recommendation} />
                  </ListItem>
                ))}
              </List>
            </Grid>
          </Grid>

          <Divider sx={{ my: 3 }} />

          <Typography variant="h6" gutterBottom>
            📈 Performance Metrics
          </Typography>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    Price Sensitivity
                  </Typography>
                  <Chip
                    label={segment.price_sensitivity}
                    color={segment.price_sensitivity === 'high' ? 'error' : segment.price_sensitivity === 'low' ? 'success' : 'warning'}
                  />
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    {segment.price_sensitivity === 'high' && 'Responds well to discounts and promotions'}
                    {segment.price_sensitivity === 'low' && 'Premium-focused, less price-sensitive'}
                    {segment.price_sensitivity === 'medium' && 'Balanced price sensitivity'}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="subtitle1" gutterBottom>
                    Top Categories
                  </Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {segment.top_categories?.slice(0, 5).map((category, index) => (
                      <Chip key={index} label={category} variant="outlined" size="small" />
                    ))}
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Behavior Tab */}
        <TabPanel value={tabValue} index={1}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                📊 Behavioral Patterns
              </Typography>
              <SegmentBehaviorChart data={insights} />
            </Grid>
          </Grid>
        </TabPanel>

        {/* Preferences Tab */}
        <TabPanel value={tabValue} index={2}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                🎯 Category Affinity
              </Typography>
              <CategoryAffinityRadar data={insights?.preferences} />
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                😊 Sentiment Analysis
              </Typography>
              <Box>
                {insights?.preferences && Object.entries(insights.preferences).map(([category, data]) => (
                  <Card key={category} sx={{ mb: 2 }}>
                    <CardContent>
                      <Typography variant="subtitle2">{category}</Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mt: 1 }}>
                        <Typography variant="body2" color="text.secondary">
                          Sentiment:
                        </Typography>
                        <Chip
                          label={data.sentiment_label}
                          size="small"
                          color={data.sentiment_label === 'positive' ? 'success' : data.sentiment_label === 'negative' ? 'error' : 'default'}
                        />
                      </Box>
                    </CardContent>
                  </Card>
                ))}
              </Box>
            </Grid>
          </Grid>
        </TabPanel>

        {/* Insights Tab */}
        <TabPanel value={tabValue} index={3}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                👍 Positive Aspects
              </Typography>
              <List>
                {insights?.preferences && Object.entries(insights.preferences)
                  .filter(([_, data]) => data.sentiment_label === 'positive')
                  .map(([category, data]) => (
                    <ListItem key={category}>
                      <ListItemIcon>
                        <ThumbUp color="success" />
                      </ListItemIcon>
                      <ListItemText 
                        primary={category}
                        secondary={`Confidence: ${(data.importance * 100).toFixed(1)}%`}
                      />
                    </ListItem>
                  ))}
              </List>
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="h6" gutterBottom>
                👎 Pain Points
              </Typography>
              <List>
                {insights?.pain_points?.map((painPoint, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <ThumbDown color="error" />
                    </ListItemIcon>
                    <ListItemText primary={painPoint} />
                  </ListItem>
                ))}
              </List>
            </Grid>
          </Grid>

          <Alert severity="info" sx={{ mt: 3 }}>
            <Typography variant="subtitle2" gutterBottom>
              🎯 Actionable Insights
            </Typography>
            <Typography variant="body2">
              Based on the analysis, this segment {insights?.churn_risk === 'high' ? 'shows signs of potential churn' : 'appears stable'} 
              and would benefit from {insights?.recommendations?.[0]?.toLowerCase() || 'targeted marketing campaigns'}.
            </Typography>
          </Alert>
        </TabPanel>

        {/* Recommendations Tab */}
        <TabPanel value={tabValue} index={4}>
          <Typography variant="h6" gutterBottom>
            🎯 Recommended Products for this Segment
          </Typography>
          <RecommendationList 
            recommendations={recommendations} 
            loading={recommendationsLoading}
            showReasoning={true}
          />
        </TabPanel>

        {/* Users Tab */}
        <TabPanel value={tabValue} index={5}>
          <Typography variant="h6" gutterBottom>
            👥 Sample Users in this Segment
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>User ID</TableCell>
                  <TableCell>Signup Date</TableCell>
                  <TableCell>Lifetime Value</TableCell>
                  <TableCell>Acquisition</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users?.map((user) => (
                  <TableRow key={user.user_id}>
                    <TableCell>{user.user_id}</TableCell>
                    <TableCell>{new Date(user.signup_date).toLocaleDateString()}</TableCell>
                    <TableCell>${user.lifetime_value.toFixed(2)}</TableCell>
                    <TableCell>{user.acquisition_channel}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </TabPanel>
      </Paper>
    </Box>
  );
};

export default SegmentDetail;
