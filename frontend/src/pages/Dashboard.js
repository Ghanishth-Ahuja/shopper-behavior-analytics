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
  const { data: metrics, isLoading: metricsLoading, error: metricsError } = useQuery(
    ['dashboardMetrics', dateRange],
    () => analyticsApi.getDashboardMetrics(),
    {
      refetchInterval: 30000,
    }
  );

  // Fetch conversion funnel
  const { data: funnelData, isLoading: funnelLoading } = useQuery(
    ['conversionFunnel', dateRange],
    () => analyticsApi.getConversionFunnel(),
    {
      refetchInterval: 60000,
    }
  );

  // Fetch segment distribution
  const { data: segmentData, isLoading: segmentsLoading } = useQuery(
    ['segments'],
    () => analyticsApi.getSegments(),
    {
      refetchInterval: 120000,
    }
  );

  // Fetch category affinity matrix for heatmap
  const { data: categoryData, isLoading: categoryLoading } = useQuery(
    ['affinityMatrix'],
    () => analyticsApi.getAffinityMatrix(),
    {
      refetchInterval: 120000,
    }
  );
  console.log("Dashboard rendered")

  const isLoading = metricsLoading || funnelLoading || segmentsLoading || categoryLoading;
  const error = metricsError;

  if (isLoading && !metrics && !segmentData) {
    return <LoadingSpinner fullScreen message="Syncing with Intelligence Engine..." />;
  }

  if (error) {
    return (
      <Box sx={{ p: 4 }}>
        <Alert severity="error" variant="filled" sx={{ borderRadius: 2 }}>
          <Typography variant="h6">Pipeline Interrupted</Typography>
          <Typography variant="body2">{error.message}</Typography>
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 1 }}>
      {console.log("Returning Dashboard JSX")}
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom weight="bold">
          🛍 Shopper Intelligence Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Real-time insights into customer behavior, preferences, and business opportunities
        </Typography>
      </Box>

      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Customers"
            value={metrics?.totalCustomers ?? 0}
            subtitle="Active users"
            trend="up"
            trendValue="+12.5%"
            color="primary"
            icon={<People />}
            loading={isLoading}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Active Segments"
            value={segmentData?.length ?? 0}
            subtitle="Customer segments"
            trend="up"
            trendValue="+2"
            color="secondary"
            icon={<Psychology />}
            loading={isLoading}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Conversion Rate"
            value={`${metrics?.conversionRate ?? 0}%`}
            subtitle="Purchase conversion"
            trend="up"
            trendValue="+3.2%"
            color="success"
            icon={<TrendingUp />}
            loading={isLoading}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Revenue"
            value={`$${(metrics?.totalRevenue ?? 0).toLocaleString()}`}
            subtitle="Total revenue"
            trend="up"
            trendValue="+18.7%"
            color="warning"
            icon={<AttachMoney />}
            loading={isLoading}
          />
        </Grid>
      </Grid>

      {/* Charts Row 1 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, height: 400, borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>
              📈 Revenue Trends
            </Typography>
            <RevenueTrendChart data={metrics?.revenueTrends} />
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3, height: 400, borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>
              🎯 Segment Distribution
            </Typography>
            <SegmentDistributionChart data={segmentData} />
          </Paper>
        </Grid>
      </Grid>

      {/* Charts Row 2 */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: 400, borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>
              🛒 Conversion Funnel
            </Typography>
            <ConversionFunnelChart data={funnelData} />
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, height: 400, borderRadius: 2 }}>
            <Typography variant="h6" gutterBottom>
              🔥 Category Performance Heatmap
            </Typography>
            <CategoryHeatmap data={categoryData} />
          </Paper>
        </Grid>
      </Grid>

      {/* Quick Insights */}
      <Paper sx={{ p: 3, mb: 4, borderRadius: 2 }}>
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
    </Box>
  );
};

export default Dashboard;
