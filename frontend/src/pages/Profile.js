import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Avatar,
  Grid,
  TextField,
  Button,
  Divider,
  Chip,
} from '@mui/material';
import {
  Email,
  Phone,
  LocationOn,
  Business,
  AdminPanelSettings,
} from '@mui/icons-material';

const Profile = () => {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        👤 User Profile
      </Typography>
      
      <Grid container spacing={4} sx={{ mt: 2 }}>
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 4, textAlign: 'center', borderRadius: 4 }}>
            <Avatar 
              sx={{ width: 120, height: 120, mx: 'auto', mb: 2, bgcolor: 'primary.main', fontSize: 40 }}
            >
              JD
            </Avatar>
            <Typography variant="h5" gutterBottom>John Doe</Typography>
            <Typography variant="body2" color="text.secondary" gutterBottom>Senior Merchandising Manager</Typography>
            <Chip label="Administrator" color="primary" size="small" icon={<AdminPanelSettings />} sx={{ mt: 1 }} />
            
            <Divider sx={{ my: 3 }} />
            
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              <Email fontSize="small" color="action" />
              <Typography variant="body2">john.doe@shoppers-intel.com</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              <Phone fontSize="small" color="action" />
              <Typography variant="body2">+1 (555) 123-4567</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 1 }}>
              <LocationOn fontSize="small" color="action" />
              <Typography variant="body2">San Francisco, CA</Typography>
            </Box>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Business fontSize="small" color="action" />
              <Typography variant="body2">Headquarters</Typography>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 4, borderRadius: 4 }}>
            <Typography variant="h6" gutterBottom>Account Details</Typography>
            <Grid container spacing={3}>
              <Grid item xs={12} sm={6}>
                <TextField fullWidth label="First Name" defaultValue="John" />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField fullWidth label="Last Name" defaultValue="Doe" />
              </Grid>
              <Grid item xs={12}>
                <TextField fullWidth label="Email Address" defaultValue="john.doe@shoppers-intel.com" />
              </Grid>
              <Grid item xs={12}>
                <TextField fullWidth label="Company" defaultValue="Shopper Intelligence Dashboard" />
              </Grid>
              <Grid item xs={12}>
                <Divider sx={{ my: 2 }} />
                <Typography variant="h6" gutterBottom>Change Password</Typography>
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField fullWidth type="password" label="New Password" />
              </Grid>
              <Grid item xs={12} sm={6}>
                <TextField fullWidth type="password" label="Confirm Password" />
              </Grid>
              <Grid item xs={12} sx={{ textAlign: 'right', mt: 2 }}>
                <Button variant="contained" size="large">Update Profile</Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Profile;
