import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Tabs,
  Tab,
  TextField,
  Button,
  Divider,
  Alert,
  Snackbar,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Card,
  CardContent,
} from '@mui/material';
import {
  CloudUpload,
  AddCircle,
  FilePresent,
  CheckCircle,
  Inventory,
  Person,
  Receipt,
  RateReview,
} from '@mui/icons-material';
import { analyticsApi } from '../api/analyticsApi';

const DataManagement = () => {
  const [tab, setTab] = useState(0);
  const [loading, setLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({ open: false, message: '', severity: 'success' });
  const [productData, setProductData] = useState({
    product_id: '',
    category: '',
    brand: '',
    price: '',
  });

  const handleTabChange = (event, newValue) => {
    setTab(newValue);
  };

  const handleProductSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      // In a real app, we would have a dedicated API for this
      // For now, let's pretend we're sending it
      console.log('Submitting product:', productData);
      await new Promise(resolve => setTimeout(resolve, 1000));
      setSnackbar({ open: true, message: 'Product added successfully!', severity: 'success' });
      setProductData({ product_id: '', category: '', brand: '', price: '' });
    } catch (error) {
      setSnackbar({ open: true, message: 'Error adding product.', severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (type) => {
    setLoading(true);
    try {
      // Simulate CSV processing
      await new Promise(resolve => setTimeout(resolve, 2000));
      setSnackbar({ open: true, message: `${type} CSV processed successfully!`, severity: 'success' });
    } catch (error) {
      setSnackbar({ open: true, message: 'Error processing file.', severity: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        📁 Data Management
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Import your business data via CSV or manual entry to power the intelligence engine.
      </Typography>

      <Paper sx={{ width: '100%', mb: 4 }}>
        <Tabs value={tab} onChange={handleTabChange} sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tab icon={<CloudUpload />} label="Bulk Import (CSV)" iconPosition="start" />
          <Tab icon={<AddCircle />} label="Manual Entry" iconPosition="start" />
        </Tabs>

        <Box sx={{ p: 4 }}>
          {tab === 0 ? (
            <Grid container spacing={4}>
              <Grid item xs={12} md={6}>
                <Typography variant="h6" gutterBottom>
                  Import Datasets
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
                  Supported formats: .csv, .json
                </Typography>
                
                <List sx={{ bgcolor: 'background.paper', borderRadius: 2 }}>
                  {[
                    { name: 'Product Catalog', icon: <Inventory />, type: 'Catalog' },
                    { name: 'User Profiles', icon: <Person />, type: 'Users' },
                    { name: 'Transactions', icon: <Receipt />, type: 'Transactions' },
                    { name: 'User Reviews', icon: <RateReview />, type: 'Reviews' },
                  ].map((item) => (
                    <ListItem
                      key={item.name}
                      secondaryAction={
                        <Button
                          variant="outlined"
                          size="small"
                          startIcon={<CloudUpload />}
                          onClick={() => handleFileUpload(item.type)}
                          disabled={loading}
                        >
                          Upload
                        </Button>
                      }
                      sx={{ border: '1px solid #eee', mb: 1, borderRadius: 2 }}
                    >
                      <ListItemIcon color="primary">
                        {item.icon}
                      </ListItemIcon>
                      <ListItemText primary={item.name} secondary={`Upload ${item.name.toLowerCase()} for analysis`} />
                    </ListItem>
                  ))}
                </List>
              </Grid>
              
              <Grid item xs={12} md={6}>
                <Card variant="outlined" sx={{ height: '100%', bgcolor: 'rgba(25, 118, 210, 0.05)' }}>
                  <CardContent>
                    <Typography variant="h6" gutterBottom color="primary">
                      Import Guidelines
                    </Typography>
                    <Typography variant="body2" paragraph>
                      1. Ensure your CSV files have a header row matching the schema.
                    </Typography>
                    <Typography variant="body2" paragraph>
                      2. Use UTC ISO-8601 format for all timestamps.
                    </Typography>
                    <Typography variant="body2" paragraph>
                      3. Maximum file size is 50MB per upload.
                    </Typography>
                    <Box sx={{ mt: 4, textAlign: 'center' }}>
                      <FilePresent sx={{ fontSize: 60, color: 'primary.light', mb: 1 }} />
                      <Typography variant="caption" display="block">
                        Download Sample Templates
                      </Typography>
                      <Button size="small" sx={{ mt: 1 }}>Download .zip</Button>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          ) : (
            <Box component="form" onSubmit={handleProductSubmit} sx={{ maxWidth: 600 }}>
              <Typography variant="h6" gutterBottom>
                Add New Product
              </Typography>
              <Grid container spacing={3}>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Product ID"
                    required
                    value={productData.product_id}
                    onChange={(e) => setProductData({ ...productData, product_id: e.target.value })}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Category"
                    required
                    value={productData.category}
                    onChange={(e) => setProductData({ ...productData, category: e.target.value })}
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Brand"
                    value={productData.brand}
                    onChange={(e) => setProductData({ ...productData, brand: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Price"
                    type="number"
                    value={productData.price}
                    onChange={(e) => setProductData({ ...productData, price: e.target.value })}
                  />
                </Grid>
                <Grid item xs={12}>
                  <Button
                    type="submit"
                    variant="contained"
                    size="large"
                    disabled={loading}
                    startIcon={loading ? <CircularProgress size={20} /> : <CheckCircle />}
                  >
                    Save Product
                  </Button>
                </Grid>
              </Grid>
            </Box>
          )}
        </Box>
      </Paper>

      <Snackbar
        open={snackbar.open}
        autoHideDuration={4000}
        onClose={() => setSnackbar({ ...snackbar, open: false })}
      >
        <Alert severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default DataManagement;
