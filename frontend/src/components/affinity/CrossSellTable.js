import React from 'react';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  TrendingUp,
  ShoppingCart,
} from '@mui/icons-material';

const CrossSellTable = ({ data }) => {
  // Default data if none provided
  const defaultData = [
    {
      category: 'Electronics',
      crossSellCategory: 'Accessories',
      liftScore: 2.3,
      confidence: 0.85,
      opportunity: 'High',
      examples: ['Phone cases', 'Screen protectors', 'Chargers'],
    },
    {
      category: 'Clothing',
      crossSellCategory: 'Shoes',
      liftScore: 1.8,
      confidence: 0.72,
      opportunity: 'Medium',
      examples: ['Sneakers', 'Boots', 'Sandals'],
    },
    {
      category: 'Home',
      crossSellCategory: 'Furniture',
      liftScore: 1.5,
      confidence: 0.68,
      opportunity: 'Medium',
      examples: ['Tables', 'Chairs', 'Storage'],
    },
    {
      category: 'Books',
      crossSellCategory: 'Stationery',
      liftScore: 2.1,
      confidence: 0.79,
      opportunity: 'High',
      examples: ['Notebooks', 'Pens', 'Markers'],
    },
  ];

  const tableData = data || defaultData;

  const getLiftColor = (score) => {
    if (score >= 2.0) return 'success';
    if (score >= 1.5) return 'warning';
    return 'error';
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'error';
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        🔄 Cross-Sell Opportunities
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
        Identify products frequently purchased together for cross-selling strategies
      </Typography>
      
      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Category</TableCell>
              <TableCell>Cross-Sell Category</TableCell>
              <TableCell>Lift Score</TableCell>
              <TableCell>Confidence</TableCell>
              <TableCell>Opportunity</TableCell>
              <TableCell>Examples</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tableData.map((row, index) => (
              <TableRow key={index}>
                <TableCell>
                  <Chip
                    label={row.category}
                    variant="outlined"
                    size="small"
                    color="primary"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={row.crossSellCategory}
                    variant="outlined"
                    size="small"
                    color="secondary"
                  />
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <TrendingUp
                      fontSize="small"
                      color={getLiftColor(row.liftScore) === 'success' ? 'success' : getLiftColor(row.liftScore) === 'warning' ? 'warning' : 'error'}
                    />
                    <Typography variant="body2" fontWeight={600}>
                      {row.liftScore.toFixed(1)}x
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={Math.min((row.liftScore / 3) * 100, 100)}
                    color={getLiftColor(row.liftScore)}
                    sx={{ height: 4, mt: 1 }}
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={`${(row.confidence * 100).toFixed(0)}%`}
                    size="small"
                    color={getConfidenceColor(row.confidence)}
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={row.opportunity}
                    size="small"
                    color={row.opportunity === 'High' ? 'success' : row.opportunity === 'Medium' ? 'warning' : 'error'}
                    variant="outlined"
                  />
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {row.examples.slice(0, 2).map((example, i) => (
                      <Chip
                        key={i}
                        label={example}
                        size="small"
                        variant="outlined"
                      />
                    ))}
                    {row.examples.length > 2 && (
                      <Chip
                        label={`+${row.examples.length - 2} more`}
                        size="small"
                        variant="outlined"
                        color="default"
                      />
                    )}
                  </Box>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      
      {/* Insights */}
      <Box sx={{ mt: 2 }}>
        <Typography variant="subtitle2" gutterBottom>
          💡 Cross-Sell Insights
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          <Chip
            label="Electronics + Accessories: 2.3x lift"
            size="small"
            color="success"
            variant="outlined"
          />
          <Chip
            label="Books + Stationery: 2.1x lift"
            size="small"
            color="success"
            variant="outlined"
          />
          <Chip
            label="Avg confidence: 76%"
            size="small"
            color="info"
            variant="outlined"
          />
        </Box>
      </Box>
    </Box>
  );
};

export default CrossSellTable;
