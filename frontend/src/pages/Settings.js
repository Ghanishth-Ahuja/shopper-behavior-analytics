import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Switch,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Button,
} from '@mui/material';
import {
  Notifications,
  Security,
  Language,
  Storage,
  Palette,
  Tune,
} from '@mui/icons-material';
import { useApp } from '../context/AppContext';

const Settings = () => {
  const { theme, setTheme } = useApp();

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        ⚙️ System Settings
      </Typography>
      <Typography variant="body1" color="text.secondary" sx={{ mb: 4 }}>
        Manage your platform preferences and intelligence engine configurations.
      </Typography>

      <Paper variant="outlined" sx={{ borderRadius: 2 }}>
        <List>
          <ListItem>
            <ListItemIcon>
              <Palette color="primary" />
            </ListItemIcon>
            <ListItemText 
              primary="Dark Mode" 
              secondary="Toggle between light and dark visual themes" 
            />
            <Switch 
              checked={theme === 'dark'} 
              onChange={() => setTheme(theme === 'dark' ? 'light' : 'dark')} 
            />
          </ListItem>
          <Divider variant="inset" component="li" />
          
          <ListItem>
            <ListItemIcon>
              <Notifications color="primary" />
            </ListItemIcon>
            <ListItemText 
              primary="Email Notifications" 
              secondary="Receive weekly intelligence reports via email" 
            />
            <Switch defaultChecked />
          </ListItem>
          <Divider variant="inset" component="li" />

          <ListItem>
            <ListItemIcon>
              <Security color="primary" />
            </ListItemIcon>
            <ListItemText 
              primary="Two-Factor Authentication" 
              secondary="Secure your account with an extra layer of protection" 
            />
            <Button variant="outlined" size="small">Enable</Button>
          </ListItem>
          <Divider variant="inset" component="li" />

          <ListItem>
            <ListItemIcon>
              <Language color="primary" />
            </ListItemIcon>
            <ListItemText 
              primary="Language" 
              secondary="Select your preferred display language" 
            />
            <Button size="small">English (US)</Button>
          </ListItem>
          <Divider variant="inset" component="li" />

          <ListItem>
            <ListItemIcon>
              <Storage color="primary" />
            </ListItemIcon>
            <ListItemText 
              primary="Data Retention" 
              secondary="History of user events to keep for training" 
            />
            <Typography variant="body2" color="text.secondary">90 Days</Typography>
          </ListItem>
          <Divider variant="inset" component="li" />

          <ListItem>
            <ListItemIcon>
              <Tune color="primary" />
            </ListItemIcon>
            <ListItemText 
              primary="ML Model Refresh Rate" 
              secondary="How often to retrain segmentation models" 
            />
            <Typography variant="body2" color="text.secondary">Daily</Typography>
          </ListItem>
        </List>
      </Paper>
      
      <Box sx={{ mt: 4, display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
        <Button>Reset to Defaults</Button>
        <Button variant="contained">Save All Changes</Button>
      </Box>
    </Box>
  );
};

export default Settings;
