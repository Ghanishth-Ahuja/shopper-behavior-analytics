import React from 'react';
import {
  Grid,
  Box,
  Typography,
  Card,
  CardContent,
  Paper,
  Alert,
} from '@mui/material';
import {
  People,
  ShoppingCart,
  TrendingUp,
  AttachMoney,
  Category,
  Psychology,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';

import { useApp } from '../context/AppContext';
import { analyticsApi } from '../api/analyticsApi';
import MetricCard from '../components/common/MetricCard';
import LoadingSpinner from '../components/common/LoadingSpinner';
import ConversionFunnelChart from '../components/charts/ConversionFunnelChart';
import CategoryHeatmap from '../components/charts/CategoryHeatmap';
import SegmentDistributionChart from '../components/charts/SegmentDistributionChart';
import RevenueTrendChart from '../components/charts/RevenueTrendChart';

const Dashboard = () => {
  const { dateRange, setSelectedSegment } = useApp();

  // Fetch dashboard metrics
  const { data: metrics, isLoading, error } = useQuery(
    ['dashboardMetrics', dateRange],
    () => analyticsApi.getDashboardMetrics(),
    {
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  );

  // Fetch conversion funnel
  const { data: funnelData } = useQuery(
    ['conversionFunnel', dateRange],
    () => analyticsApi.getConversionFunnel(),
    {
      refetchInterval: 60000, // Refresh every minute
    }
  );

  // Fetch segment distribution
  const { data: segmentData } = useQuery(
    ['segments'],
    () => analyticsApi.getSegments(),
    {
      refetchInterval: 120000, // Refresh every 2 minutes
    }
  );

  // Fetch category performance
  const { data: categoryData } = useQuery(
    ['categoryPerformance', dateRange],
    () => analyticsApi.getProductPerformance({ limit: 10 }),
    {
      refetchInterval: 60000,
    }
  );

  if (isLoading && !metrics) {
    return <LoadingSpinner fullScreen message="Loading dashboard..." />;
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ m: 2 }}>
        Error loading dashboard: {error.message}
      </Alert>
    );
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          🛍 Shopper Intelligence Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Real-time insights into customer behavior, preferences, and business opportunities
        </Typography>
      </Box>

      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
          >
            <MetricCard
              title="Total Customers"
              value={metrics?.totalCustomers || 0}
              subtitle="Active users"
              trend="up"
              trendValue="+12.5%"
              color="primary"
              icon={<People />}
            />
          </motion.div>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            <MetricCard
              title="Active Segments"
              value={segmentData?.length || 0}
              subtitle="Customer segments"
              trend="up"
              trendValue="+2"
              color="secondary"
              icon={<Psychology />}
            />
          </motion.div>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            <MetricCard
              title="Conversion Rate"
              value={`${metrics?.conversionRate || 0}%`}
              subtitle="Purchase conversion"
              trend="up"
              trendValue="+3.2%"
              color="success"
              icon={<TrendingUp />}
            />
          </motion.div>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <MetricCard
              title="Revenue"
              value={`$${(metrics?.totalRevenue || 0).toLocaleString()}`}
              subtitle="Total revenue"
              trend="up"
              trendValue="+18.7%"
              color="warning"
              icon={<AttachMoney />}
            />
          </motion.div>
        </Grid>
      </Grid>

      {/* Charts Row 1 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5 }}
          >
            <Paper sx={{ p: 3, height: 400 }}>
              <Typography variant="h6" gutterBottom>
                📈 Revenue Trends
              </Typography>
              <RevenueTrendChart data={metrics?.revenueTrends} />
            </Paper>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={4}>
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6 }}
          >
            <Paper sx={{ p: 3, height: 400 }}>
              <Typography variant="h6" gutterBottom>
                🎯 Segment Distribution
              </Typography>
              <SegmentDistributionChart data={segmentData} />
            </Paper>
          </motion.div>
        </Grid>
      </Grid>

      {/* Charts Row 2 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
          >
            <Paper sx={{ p: 3, height: 400 }}>
              <Typography variant="h6" gutterBottom>
                🛒 Conversion Funnel
              </Typography>
              <ConversionFunnelChart data={funnelData} />
            </Paper>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
          >
            <Paper sx={{ p: 3, height: 400 }}>
              <Typography variant="h6" gutterBottom>
                🔥 Category Performance Heatmap
              </Typography>
              <CategoryHeatmap data={categoryData} />
            </Paper>
          </motion.div>
        </Grid>
      </Grid>

      {/* Quick Insights */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.9 }}
      >
        <Paper sx={{ p: 3, mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            💡 Quick Insights
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Alert severity="success" icon={<Category />}>
                <Typography variant="body2">
                  <strong>Electronics</strong> category shows 23% higher conversion rate
                </Typography>
              </Alert>
            </Grid>
            <Grid item xs={12} md={4}>
              <Alert severity="info" icon={<People />}>
                <Typography variant="body2">
                  <strong>Tech Enthusiasts</strong> segment has highest average order value
                </Typography>
              </Alert>
            </Grid>
            <Grid item xs={12} md={4}>
              <Alert severity="warning" icon={<ShoppingCart />}>
                <Typography variant="body2">
                  Cart abandonment rate increased by 5% this week
                </Typography>
              </Alert>
            </Grid>
          </Grid>
        </Paper>
      </motion.div>
    </Box>
  );
};

export default Dashboard;
