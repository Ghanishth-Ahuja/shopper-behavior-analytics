import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Typography,
  Divider,
  Box,
  Chip,
} from '@mui/material';
import {
  Dashboard,
  People,
  Category,
  TrendingUp,
  Psychology,
  RateReview,
  PersonSearch,
  Analytics,
  Settings,
} from '@mui/icons-material';
import { useApp } from '../../context/AppContext';

const menuItems = [
  { text: 'Dashboard', icon: <Dashboard />, path: '/dashboard' },
  { text: 'Segment Explorer', icon: <People />, path: '/segments' },
  { text: 'Product Affinity', icon: <Category />, path: '/affinity' },
  { text: 'Recommendations', icon: <TrendingUp />, path: '/recommendations' },
  { text: 'Review Intelligence', icon: <RateReview />, path: '/reviews' },
  { text: 'User Explorer', icon: <PersonSearch />, path: '/users' },
  { text: 'Analytics', icon: <Analytics />, path: '/analytics' },
];

const Sidebar = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { sidebarOpen, selectedSegment } = useApp();

  const handleNavigation = (path) => {
    navigate(path);
  };

  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={sidebarOpen}
      sx={{
        width: 240,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: 240,
          boxSizing: 'border-box',
          top: 64, // navbar height
          height: 'calc(100% - 64px)',
        },
      }}
    >
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" color="primary" gutterBottom>
          Navigation
        </Typography>
        
        {selectedSegment && (
          <Box sx={{ mb: 2 }}>
            <Chip
              label={`Selected: ${selectedSegment.segment_name}`}
              color="primary"
              variant="outlined"
              size="small"
              sx={{ mb: 1 }}
            />
            <Typography variant="caption" display="block" color="text.secondary">
              {selectedSegment.size} users
            </Typography>
          </Box>
        )}
      </Box>

      <Divider />

      <List sx={{ p: 1 }}>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
            <ListItemButton
              selected={location.pathname === item.path}
              onClick={() => handleNavigation(item.path)}
              sx={{
                borderRadius: 1,
                '&.Mui-selected': {
                  backgroundColor: 'primary.main',
                  color: 'primary.contrastText',
                  '&:hover': {
                    backgroundColor: 'primary.dark',
                  },
                  '& .MuiListItemIcon-root': {
                    color: 'primary.contrastText',
                  },
                },
              }}
            >
              <ListItemIcon sx={{ minWidth: 40 }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText 
                primary={item.text}
                primaryTypographyProps={{
                  fontSize: '0.9rem',
                  fontWeight: location.pathname === item.path ? 600 : 400,
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      <Divider sx={{ mt: 'auto' }} />

      <Box sx={{ p: 2 }}>
        <Typography variant="caption" color="text.secondary" display="block" gutterBottom>
          Quick Actions
        </Typography>
        <List dense>
          <ListItem disablePadding>
            <ListItemButton sx={{ borderRadius: 1 }}>
              <ListItemIcon sx={{ minWidth: 32 }}>
                <Psychology fontSize="small" />
              </ListItemIcon>
              <ListItemText 
                primary="Train Models" 
                primaryTypographyProps={{ fontSize: '0.8rem' }}
              />
            </ListItemButton>
          </ListItem>
          <ListItem disablePadding>
            <ListItemButton sx={{ borderRadius: 1 }}>
              <ListItemIcon sx={{ minWidth: 32 }}>
                <Settings fontSize="small" />
              </ListItemIcon>
              <ListItemText 
                primary="Settings" 
                primaryTypographyProps={{ fontSize: '0.8rem' }}
              />
            </ListItemButton>
          </ListItem>
        </List>
      </Box>
    </Drawer>
  );
};

export default Sidebar;
