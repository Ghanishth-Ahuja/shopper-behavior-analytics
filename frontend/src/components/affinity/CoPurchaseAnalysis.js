import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  ShoppingCart,
  TrendingUp,
  People,
} from '@mui/icons-material';

const CoPurchaseAnalysis = () => {
  // Default data
  const defaultData = {
    topPairs: [
      {
        product1: 'Wireless Headphones',
        product2: 'Phone Case',
        frequency: 245,
        lift: 3.2,
        confidence: 0.89,
      },
      {
        product1: 'Laptop',
        product2: 'Mouse Pad',
        frequency: 189,
        lift: 2.8,
        confidence: 0.82,
      },
      {
        product1: 'Running Shoes',
        product2: 'Athletic Socks',
        frequency: 156,
        lift: 2.5,
        confidence: 0.76,
      },
      {
        product1: 'Coffee Maker',
        product2: 'Coffee Beans',
        frequency: 134,
        lift: 2.9,
        confidence: 0.84,
      },
    ],
    insights: {
      totalCoPurchases: 1247,
      avgLift: 2.8,
      topCategory: 'Electronics',
      seasonality: 'Higher during holidays',
    },
  };

  const data = defaultData;

  const getLiftColor = (lift) => {
    if (lift >= 3.0) return 'success';
    if (lift >= 2.0) return 'warning';
    return 'error';
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        🛒 Co-Purchase Analysis
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Products frequently bought together for bundling and recommendation strategies
      </Typography>
      
      {/* Top Co-Purchase Pairs */}
      <List>
        {data.topPairs.map((pair, index) => (
          <ListItem key={index} sx={{ mb: 1 }}>
            <ListItemIcon>
              <ShoppingCart color="primary" />
            </ListItemIcon>
            <ListItemText
              primary={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="subtitle2">
                    {pair.product1}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    + {pair.product2}
                  </Typography>
                </Box>
              }
              secondary={
                <Box sx={{ mt: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                    <TrendingUp
                      fontSize="small"
                      color={getLiftColor(pair.lift) === 'success' ? 'success' : getLiftColor(pair.lift) === 'warning' ? 'warning' : 'error'}
                    />
                    <Typography variant="body2" fontWeight={600}>
                      {pair.lift.toFixed(1)}x lift
                    </Typography>
                    <Chip
                      label={`${pair.frequency} purchases`}
                      size="small"
                      variant="outlined"
                    />
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={pair.confidence * 100}
                    color={pair.confidence >= 0.8 ? 'success' : pair.confidence >= 0.6 ? 'warning' : 'error'}
                    sx={{ height: 4 }}
                  />
                  <Typography variant="caption" color="text.secondary">
                    {pair.confidence >= 0.8 ? 'High confidence' : pair.confidence >= 0.6 ? 'Medium confidence' : 'Low confidence'}
                  </Typography>
                </Box>
              }
            />
          </ListItem>
        ))}
      </List>
      
      {/* Co-Purchase Insights */}
      <Card sx={{ mt: 2 }}>
        <CardContent>
          <Typography variant="subtitle2" gutterBottom>
            📊 Co-Purchase Insights
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h6" color="primary">
                  {data.insights.totalCoPurchases.toLocaleString()}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Total Co-Purchases
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h6" color="success">
                  {data.insights.avgLift.toFixed(1)}x
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Average Lift
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="body2">
                  <People sx={{ mr: 1, verticalAlign: 'middle' }} />
                  Top Category: {data.insights.topCategory}
                </Typography>
                <Typography variant="body2">
                  Seasonality: {data.insights.seasonality}
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
      
      {/* Recommendations */}
      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          💡 Bundle Recommendations
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          <Chip
            label="Electronics Bundle: Headphones + Case + Charger"
            size="small"
            color="success"
            variant="outlined"
          />
          <Chip
            label="Home Bundle: Coffee Maker + Beans + Filters"
            size="small"
            color="warning"
            variant="outlined"
          />
          <Chip
            label="Sports Bundle: Shoes + Socks + Accessories"
            size="small"
            color="info"
            variant="outlined"
          />
        </Box>
      </Box>
    </Box>
  );
};

export default CoPurchaseAnalysis;
