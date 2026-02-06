import React, { useState } from 'react';
import {
  Grid,
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  Tooltip,
  Paper,
} from '@mui/material';
import {
  Search,
  FilterList,
  People,
  ShoppingCart,
  AttachMoney,
  TrendingUp,
  Psychology,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';

import { useApp } from '../context/AppContext';
import { analyticsApi } from '../api/analyticsApi';
import MetricCard from '../components/common/MetricCard';
import LoadingSpinner from '../components/common/LoadingSpinner';
import SegmentCard from '../components/segments/SegmentCard';
import SegmentComparisonChart from '../components/charts/SegmentComparisonChart';

const SegmentExplorer = () => {
  const { segments, setSelectedSegment, dateRange } = useApp();
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('size');
  const [filterCategory, setFilterCategory] = useState('');

  // Fetch segment insights for all segments
  const { data: segmentInsights, isLoading } = useQuery(
    ['segmentInsights', segments],
    async () => {
      if (!segments || segments.length === 0) return [];
      
      const insightsPromises = segments.map(async (segment) => {
        try {
          const insights = await analyticsApi.getSegmentInsights(segment.segment_id);
          return { ...segment, insights };
        } catch (error) {
          console.error(`Error fetching insights for segment ${segment.segment_id}:`, error);
          return { ...segment, insights: null };
        }
      });

      return Promise.all(insightsPromises);
    },
    {
      enabled: segments && segments.length > 0,
      refetchInterval: 120000, // Refresh every 2 minutes
    }
  );

  // Filter and sort segments
  const filteredSegments = React.useMemo(() => {
    if (!segmentInsights) return [];

    let filtered = segmentInsights.filter(segment => {
      const matchesSearch = segment.segment_name.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = !filterCategory || segment.top_categories?.includes(filterCategory);
      return matchesSearch && matchesCategory;
    });

    // Sort segments
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'size':
          return b.size - a.size;
        case 'name':
          return a.segment_name.localeCompare(b.segment_name);
        case 'ltv':
          return (b.insights?.avg_order_value || 0) - (a.insights?.avg_order_value || 0);
        case 'conversion':
          return (b.insights?.conversion_rate || 0) - (a.insights?.conversion_rate || 0);
        default:
          return 0;
      }
    });

    return filtered;
  }, [segmentInsights, searchTerm, sortBy, filterCategory]);

  // Get all unique categories for filter
  const allCategories = React.useMemo(() => {
    if (!segments) return [];
    const categories = new Set();
    segments.forEach(segment => {
      segment.top_categories?.forEach(cat => categories.add(cat));
    });
    return Array.from(categories).sort();
  }, [segments]);

  // Calculate segment statistics
  const segmentStats = React.useMemo(() => {
    if (!filteredSegments) return {};

    const totalUsers = filteredSegments.reduce((sum, seg) => sum + seg.size, 0);
    const avgLTV = filteredSegments.reduce((sum, seg) => sum + (seg.insights?.avg_order_value || 0), 0) / filteredSegments.length;
    const avgConversion = filteredSegments.reduce((sum, seg) => sum + (seg.insights?.conversion_rate || 0), 0) / filteredSegments.length;

    return {
      totalUsers,
      avgLTV,
      avgConversion,
      totalSegments: filteredSegments.length,
    };
  }, [filteredSegments]);

  if (isLoading && !segmentInsights) {
    return <LoadingSpinner fullScreen message="Loading segments..." />;
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          👥 Segment Explorer
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Discover and analyze customer segments to understand behavioral patterns and preferences
        </Typography>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Segments"
            value={segmentStats.totalSegments}
            subtitle="Active segments"
            color="primary"
            icon={<Psychology />}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Total Customers"
            value={segmentStats.totalUsers?.toLocaleString() || 0}
            subtitle="Segmented users"
            color="secondary"
            icon={<People />}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Avg Order Value"
            value={`$${(segmentStats.avgLTV || 0).toFixed(2)}`}
            subtitle="Across all segments"
            color="success"
            icon={<AttachMoney />}
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Avg Conversion"
            value={`${(segmentStats.avgConversion || 0).toFixed(1)}%`}
            subtitle="Purchase rate"
            color="warning"
            icon={<TrendingUp />}
          />
        </Grid>
      </Grid>

      {/* Filters and Search */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="Search segments..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
            />
          </Grid>

          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Sort By</InputLabel>
              <Select
                value={sortBy}
                label="Sort By"
                onChange={(e) => setSortBy(e.target.value)}
              >
                <MenuItem value="size">Size</MenuItem>
                <MenuItem value="name">Name</MenuItem>
                <MenuItem value="ltv">Avg Order Value</MenuItem>
                <MenuItem value="conversion">Conversion Rate</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Filter by Category</InputLabel>
              <Select
                value={filterCategory}
                label="Filter by Category"
                onChange={(e) => setFilterCategory(e.target.value)}
              >
                <MenuItem value="">All Categories</MenuItem>
                {allCategories.map(category => (
                  <MenuItem key={category} value={category}>
                    {category}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={2}>
            <Tooltip title="Clear filters">
              <IconButton onClick={() => {
                setSearchTerm('');
                setFilterCategory('');
                setSortBy('size');
              }}>
                <FilterList />
              </IconButton>
            </Tooltip>
          </Grid>
        </Grid>
      </Paper>

      {/* Segment Comparison Chart */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          📊 Segment Comparison
        </Typography>
        <SegmentComparisonChart data={filteredSegments} />
      </Paper>

      {/* Segment Cards Grid */}
      <Grid container spacing={3}>
        {filteredSegments.map((segment, index) => (
          <Grid item xs={12} sm={6} md={4} lg={3} key={segment.segment_id}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <SegmentCard
                segment={segment}
                insights={segment.insights}
                onSelect={() => setSelectedSegment(segment)}
              />
            </motion.div>
          </Grid>
        ))}
      </Grid>

      {filteredSegments.length === 0 && (
        <Box sx={{ textAlign: 'center', py: 8 }}>
          <Typography variant="h6" color="text.secondary">
            No segments found matching your criteria
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            Try adjusting your filters or search terms
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default SegmentExplorer;
