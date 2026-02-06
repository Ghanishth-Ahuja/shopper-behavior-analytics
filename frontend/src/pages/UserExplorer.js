import React, { useState } from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  Paper,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Avatar,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Search,
  Person,
  Timeline,
  ShoppingCart,
  AttachMoney,
  TrendingUp,
  Visibility,
  Info,
  Refresh,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useQuery } from 'react-query';

import { useApp } from '../context/AppContext';
import { userApi } from '../api/userApi';
import { analyticsApi } from '../api/analyticsApi';
import UserJourneyChart from '../components/charts/UserJourneyChart';
import UserBehaviorHeatmap from '../components/charts/UserBehaviorHeatmap';

const UserExplorer = () => {
  const { selectedSegment } = useApp();
  const [searchTerm, setSearchTerm] = useState('');
  const [sortBy, setSortBy] = useState('recent');
  const [selectedUser, setSelectedUser] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  // Fetch users
  const { data: users, isLoading: usersLoading } = useQuery(
    ['users', searchTerm, sortBy],
    () => userApi.getUsers({ search: searchTerm, sort: sortBy }),
    {
      refetchInterval: 60000, // Refresh every minute
    }
  );

  // Fetch user analytics for selected user
  const { data: userAnalytics, isLoading: analyticsLoading } = useQuery(
    ['userAnalytics', selectedUser],
    () => analyticsApi.getUserAnalytics(selectedUser),
    {
      enabled: !!selectedUser,
      refetchInterval: 30000, // Refresh every 30 seconds
    }
  );

  // Handle user selection
  const handleUserClick = (user) => {
    setSelectedUser(user);
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedUser(null);
  };

  // Filter and sort users
  const filteredUsers = React.useMemo(() => {
    if (!users) return [];

    let filtered = users.filter(user => 
      user.user_id.toLowerCase().includes(searchTerm.toLowerCase())
    );

    // Sort users
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'recent':
          return new Date(b.signup_date) - new Date(a.signup_date);
        case 'value':
          return b.lifetime_value - a.lifetime_value;
        case 'activity':
          return (b.recent_activity || 0) - (a.recent_activity || 0);
        case 'name':
          return a.user_id.localeCompare(b.user_id);
        default:
          return 0;
      }
    });

    return filtered;
  }, [users, searchTerm, sortBy]);

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          👤 User Explorer
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Deep dive into individual customer behavior patterns and journey analysis
        </Typography>
      </Box>

      {/* Search and Filters */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="Search users by ID..."
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
                <MenuItem value="recent">Most Recent</MenuItem>
                <MenuItem value="value">Highest Value</MenuItem>
                <MenuItem value="activity">Most Active</MenuItem>
                <MenuItem value="name">User ID</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={3}>
            <Button
              variant="outlined"
              startIcon={<Refresh />}
              onClick={() => window.location.reload()}
            >
              Refresh
            </Button>
          </Grid>
        </Grid>
      </Paper>

      {/* User Statistics */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <Person color="primary" />
                <Typography variant="subtitle2">Total Users</Typography>
              </Box>
              <Typography variant="h4" color="primary">
                {users?.length || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Registered users
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <AttachMoney color="success" />
                <Typography variant="subtitle2">Avg LTV</Typography>
              </Box>
              <Typography variant="h4" color="success">
                ${users?.reduce((sum, user) => sum + user.lifetime_value, 0) / (users?.length || 1) || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Per user
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <ShoppingCart color="warning" />
                <Typography variant="subtitle2">Avg Orders</Typography>
              </Box>
              <Typography variant="h4" color="warning">
                {users?.reduce((sum, user) => sum + (user.total_transactions || 0), 0) / (users?.length || 1) || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Per user
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                <TrendingUp color="info" />
                <Typography variant="subtitle2">Active Today</Typography>
              </Box>
              <Typography variant="h4" color="info">
                {users?.filter(user => user.recent_activity > 0).length || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Users
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Users Table */}
      <Paper sx={{ mb: 4 }}>
        <Typography variant="h6" gutterBottom sx={{ p: 2 }}>
          👥 User Directory ({filteredUsers.length} users)
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>User</TableCell>
                <TableCell>Segment</TableCell>
                <TableCell>LTV</TableCell>
                <TableCell>Orders</TableCell>
                <TableCell>Activity</TableCell>
                <TableCell>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredUsers.map((user, index) => (
                <motion.tr
                  key={user.user_id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: index * 0.05 }}
                  sx={{ '&:hover': { backgroundColor: 'action.hover' } }}
                >
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Avatar sx={{ bgcolor: 'primary.main' }}>
                        {user.user_id.charAt(0).toUpperCase()}
                      </Avatar>
                      <Box>
                        <Typography variant="body2" fontWeight={500}>
                          {user.user_id}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Joined {new Date(user.signup_date).toLocaleDateString()}
                        </Typography>
                      </Box>
                    </Box>
                  </TableCell>
                  <TableCell>
                    {user.segment_id ? (
                      <Chip 
                        label={user.segment_id} 
                        variant="outlined" 
                        size="small" 
                        color="primary"
                      />
                    ) : (
                      <Chip 
                        label="Unassigned" 
                        variant="outlined" 
                        size="small" 
                        color="default"
                      />
                    )}
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      ${user.lifetime_value.toFixed(2)}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {user.total_transactions || 0}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Visibility 
                        sx={{ 
                          fontSize: 16, 
                          color: user.recent_activity > 0 ? 'success.main' : 'text.secondary' 
                        }} 
                      />
                      <Typography variant="body2">
                        {user.recent_activity || 0}
                      </Typography>
                    </Box>
                  </TableCell>
                  <TableCell>
                    <Tooltip title="View detailed analytics">
                      <IconButton
                        size="small"
                        onClick={() => handleUserClick(user)}
                      >
                        <Info />
                      </IconButton>
                    </Tooltip>
                  </TableCell>
                </motion.tr>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* User Detail Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          👤 User Analytics: {selectedUser?.user_id}
        </DialogTitle>
        <DialogContent>
          {analyticsLoading ? (
            <Box sx={{ p: 3, textAlign: 'center' }}>
              <Typography>Loading analytics...</Typography>
            </Box>
          ) : userAnalytics ? (
            <Box sx={{ p: 2 }}>
              {/* User Overview */}
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Lifetime Value
                  </Typography>
                  <Typography variant="h6">
                    ${userAnalytics.user_info?.lifetime_value?.toFixed(2) || '0.00'}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Total Transactions
                  </Typography>
                  <Typography variant="h6">
                    {userAnalytics.transaction_summary?.total_transactions || 0}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Avg Order Value
                  </Typography>
                  <Typography variant="h6">
                    ${userAnalytics.transaction_summary?.avg_order_value?.toFixed(2) || '0.00'}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Total Reviews
                  </Typography>
                  <Typography variant="h6">
                    {userAnalytics.review_summary?.total_reviews || 0}
                  </Typography>
                </Grid>
              </Grid>

              {/* Charts */}
              <Grid container spacing={3}>
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>
                    📊 User Journey
                  </Typography>
                  <UserJourneyChart userId={selectedUser?.user_id} />
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="h6" gutterBottom>
                    🔥 Activity Heatmap
                  </Typography>
                  <UserBehaviorHeatmap userId={selectedUser?.user_id} />
                </Grid>
              </Grid>

              {/* Recent Activity */}
              <Box sx={{ mt: 3 }}>
                <Typography variant="h6" gutterBottom>
                  📈 Recent Activity
                </Typography>
                <TableContainer size="small">
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Type</TableCell>
                        <TableCell>Count</TableCell>
                        <TableCell>Details</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      <TableRow>
                        <TableCell>Sessions</TableCell>
                        <TableCell>{userAnalytics.session_summary?.total_sessions || 0}</TableCell>
                        <TableCell>Avg duration: {userAnalytics.session_summary?.avg_session_duration?.toFixed(1) || 0} min</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Page Views</TableCell>
                        <TableCell>{userAnalytics.session_summary?.avg_pages_per_session?.toFixed(1) || 0}</TableCell>
                        <TableCell>Per session</TableCell>
                      </TableRow>
                      <TableRow>
                        <TableCell>Cart Additions</TableCell>
                        <TableCell>{userAnalytics.session_summary?.cart_additions || 0}</TableCell>
                        <TableCell>Total events</TableCell>
                      </TableRow>
                    </TableBody>
                  </Table>
                </TableContainer>
              </Box>
            </Box>
          ) : null}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default UserExplorer;
