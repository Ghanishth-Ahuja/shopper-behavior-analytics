import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Alert,
  Tooltip,
} from '@mui/material';
import {
  Category,
  Timeline,
  Share,
  TrendingUp,
  NetworkCheck,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';

import { useApp } from '../context/AppContext';
import { analyticsApi } from '../api/analyticsApi';
import CategoryHeatmap from '../components/charts/CategoryHeatmap';
import AffinityNetworkGraph from '../components/charts/AffinityNetworkGraph';
import CrossSellTable from '../components/affinity/CrossSellTable';
import CoPurchaseAnalysis from '../components/affinity/CoPurchaseAnalysis';

const ProductAffinity = () => {
  const { selectedSegment, dateRange } = useApp();
  const [selectedSegmentFilter, setSelectedSegmentFilter] = useState('');
  const [viewMode, setViewMode] = useState('heatmap');

  // Fetch affinity matrix
  const { data: affinityData, isLoading: affinityLoading } = useQuery(
    ['affinityMatrix', selectedSegmentFilter],
    () => analyticsApi.getAffinityMatrix(),
    {
      refetchInterval: 120000, // Refresh every 2 minutes
    }
  );

  // Fetch category lift
  const { data: categoryLift, isLoading: liftLoading } = useQuery(
    ['categoryLift', selectedSegmentFilter],
    () => analyticsApi.getCategoryLift(),
    {
      refetchInterval: 120000,
    }
  );

  // Fetch customer personas
  const { data: personas, isLoading: personasLoading } = useQuery(
    ['customerPersonas'],
    () => analyticsApi.getCustomerPersonas(),
    {
      refetchInterval: 300000, // Refresh every 5 minutes
    }
  );

  // Fetch behavioral patterns
  const { data: behavioralPatterns, isLoading: patternsLoading } = useQuery(
    ['behavioralPatterns'],
    () => analyticsApi.getBehavioralPatterns(),
    {
      refetchInterval: 300000,
    }
  );

  // Get unique segments for filter
  const availableSegments = React.useMemo(() => {
    if (!affinityData) return [];
    return affinityData.map(item => ({
      id: item.segment_id,
      name: item.segment_name,
      size: item.total_users,
    }));
  }, [affinityData]);

  // Calculate key insights
  const keyInsights = React.useMemo(() => {
    if (!categoryLift || categoryLift.length === 0) return [];

    const insights = [];
    
    // Find highest lift
    const highestLift = categoryLift.reduce((max, item) => 
      item.lift_score > max.lift_score ? item : max, categoryLift[0]
    );
    
    insights.push({
      type: 'highest_lift',
      title: 'Strongest Cross-Category Relationship',
      description: `${highestLift.category} shows ${highestLift.lift_score.toFixed(1)}x higher purchase rate`,
      value: `${highestLift.lift_score.toFixed(1)}x`,
    });

    // Find lowest lift
    const lowestLift = categoryLift.reduce((min, item) => 
      item.lift_score < min.lift_score ? item : min, categoryLift[0]
    );
    
    insights.push({
      type: 'lowest_lift',
      title: 'Weakest Cross-Category Relationship',
      description: `${lowestLift.category} shows only ${lowestLift.lift_score.toFixed(1)}x higher purchase rate`,
      value: `${lowestLift.lift_score.toFixed(1)}x`,
    });

    return insights;
  }, [categoryLift]);

  if (affinityLoading && !affinityData) {
    return <Box sx={{ p: 3 }}>
      <Typography>Loading affinity data...</Typography>
    </Box>;
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          🔗 Product Affinity Analysis
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Discover relationships between products and categories to optimize cross-selling and bundling strategies
        </Typography>
      </Box>

      {/* Filters */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>Filter by Segment</InputLabel>
              <Select
                value={selectedSegmentFilter}
                label="Filter by Segment"
                onChange={(e) => setSelectedSegmentFilter(e.target.value)}
              >
                <MenuItem value="">All Segments</MenuItem>
                {availableSegments.map(segment => (
                  <MenuItem key={segment.id} value={segment.id}>
                    {segment.name} ({segment.size} users)
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={4}>
            <FormControl fullWidth>
              <InputLabel>View Mode</InputLabel>
              <Select
                value={viewMode}
                label="View Mode"
                onChange={(e) => setViewMode(e.target.value)}
              >
                <MenuItem value="heatmap">Heatmap View</MenuItem>
                <MenuItem value="network">Network Graph</MenuItem>
                <MenuItem value="table">Table View</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      {/* Key Insights */}
      <Grid container spacing={2} sx={{ mb: 4 }}>
        {keyInsights.map((insight, index) => (
          <Grid item xs={12} md={4} key={index}>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Alert 
                severity={insight.type === 'highest_lift' ? 'success' : 'warning'}
                icon={insight.type === 'highest_lift' ? <TrendingUp /> : <Timeline />}
              >
                <Typography variant="subtitle2" gutterBottom>
                  {insight.title}
                </Typography>
                <Typography variant="body2">
                  {insight.description}
                </Typography>
                <Chip 
                  label={insight.value} 
                  size="small" 
                  sx={{ mt: 1 }}
                  color={insight.type === 'highest_lift' ? 'success' : 'warning'}
                />
              </Alert>
            </motion.div>
          </Grid>
        ))}
      </Grid>

      {/* Main Content */}
      {viewMode === 'heatmap' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <Paper sx={{ p: 3, mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              📊 Category Affinity Heatmap
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Shows how strongly each segment prefers different categories. Darker colors indicate stronger affinity.
            </Typography>
            <CategoryHeatmap data={affinityData} />
          </Paper>
        </motion.div>
      )}

      {viewMode === 'network' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <Paper sx={{ p: 3, mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              🕸️ Product Relationship Network
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Visualizes how products and categories are connected through customer behavior patterns.
            </Typography>
            <AffinityNetworkGraph data={categoryLift} />
          </Paper>
        </motion.div>
      )}

      {viewMode === 'table' && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3 }}
        >
          <Paper sx={{ p: 3, mb: 4 }}>
            <Typography variant="h6" gutterBottom>
              📋 Category Lift Analysis Table
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Detailed analysis of how categories influence each other's purchase rates.
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Category</TableCell>
                    <TableCell>Lift Score</TableCell>
                    <TableCell>Baseline Conversion</TableCell>
                    <TableCell>Segment Conversion</TableCell>
                    <TableCell>Segment</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {categoryLift?.map((item, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <Chip label={item.category} variant="outlined" size="small" />
                      </TableCell>
                      <TableCell>
                        <Tooltip title={`${item.lift_score.toFixed(2)}x higher purchase rate`}>
                          <Chip 
                            label={`${item.lift_score.toFixed(1)}x`} 
                            color={item.lift_score > 2 ? 'success' : item.lift_score > 1.5 ? 'warning' : 'default'}
                            size="small"
                          />
                        </Tooltip>
                      </TableCell>
                      <TableCell>{(item.baseline_conversion * 100).toFixed(1)}%</TableCell>
                      <TableCell>{(item.segment_conversion * 100).toFixed(1)}%</TableCell>
                      <TableCell>{item.segment_name}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </motion.div>
      )}

      {/* Cross-Sell Analysis */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                🔄 Cross-Sell Opportunities
              </Typography>
              <CrossSellTable data={categoryLift} />
            </Paper>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={6}>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
          >
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                🛒 Co-Purchase Analysis
              </Typography>
              <CoPurchaseAnalysis />
            </Paper>
          </motion.div>
        </Grid>
      </Grid>

      {/* Behavioral Patterns */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.6 }}
      >
        <Paper sx={{ p: 3, mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            🧠 Behavioral Patterns Impact
          </Typography>
          <Grid container spacing={2}>
            {behavioralPatterns?.cross_category_rate && (
              <Grid item xs={12} md={4}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                      <NetworkCheck color="primary" />
                      <Typography variant="subtitle2">
                        Cross-Category Rate
                      </Typography>
                    </Box>
                    <Typography variant="h4" color="primary">
                      {(behavioralPatterns.cross_category_rate * 100).toFixed(1)}%
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      of customers purchase from multiple categories
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            )}
            
            {behavioralPatterns?.top_cross_categories && (
              <Grid item xs={12} md={8}>
                <Card>
                  <CardContent>
                    <Typography variant="subtitle2" gutterBottom>
                      <Share color="secondary" sx={{ mr: 1, verticalAlign: 'middle' }} />
                      Top Cross-Category Paths
                    </Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                      {behavioralPatterns.top_cross_categories.map((path, index) => (
                        <Chip 
                          key={index}
                          label={path}
                          variant="outlined"
                          size="small"
                          color="secondary"
                        />
                      ))}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            )}
          </Grid>
        </Paper>
      </motion.div>
    </Box>
  );
};

export default ProductAffinity;
