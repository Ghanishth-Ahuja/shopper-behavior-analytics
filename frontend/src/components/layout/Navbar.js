import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Box,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  Tooltip,
  Divider,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import {
  Menu as MenuIcon,
  Notifications,
  AccountCircle,
  Settings,
  Logout,
  Refresh,
} from '@mui/icons-material';
import { useApp } from '../../context/AppContext';

const Navbar = () => {
  const navigate = useNavigate();
  const { sidebarOpen, toggleSidebar, theme, setTheme } = useApp();
  const [anchorEl, setAnchorEl] = useState(null);
  const [notificationAnchorEl, setNotificationAnchorEl] = useState(null);

  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleProfileMenuClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationMenuOpen = (event) => {
    setNotificationAnchorEl(event.currentTarget);
  };

  const handleNotificationMenuClose = () => {
    setNotificationAnchorEl(null);
  };

  const handleThemeToggle = () => {
    setTheme(theme === 'light' ? 'dark' : 'light');
  };

  const handleRefresh = () => {
    window.location.reload();
  };

  return (
    <AppBar position="fixed" sx={{ zIndex: 1200 }}>
      <Toolbar>
        <IconButton
          color="inherit"
          aria-label="open drawer"
          onClick={toggleSidebar}
          edge="start"
          sx={{ mr: 2 }}
        >
          <MenuIcon />
        </IconButton>

        <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
          🛍 Shopper Intelligence Dashboard
        </Typography>

        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Tooltip title="Refresh Data">
            <IconButton color="inherit" onClick={handleRefresh}>
              <Refresh />
            </IconButton>
          </Tooltip>

          <Tooltip title="Notifications">
            <IconButton color="inherit" onClick={handleNotificationMenuOpen}>
              <Badge badgeContent={3} color="error">
                <Notifications />
              </Badge>
            </IconButton>
          </Tooltip>

          <Menu
            anchorEl={notificationAnchorEl}
            open={Boolean(notificationAnchorEl)}
            onClose={handleNotificationMenuClose}
            PaperProps={{
              elevation: 3,
              sx: { mt: 2, minWidth: 300 },
            }}
          >
            <MenuItem onClick={handleNotificationMenuClose}>
              <Typography variant="body2">New segment created: "Tech Enthusiasts"</Typography>
            </MenuItem>
            <MenuItem onClick={handleNotificationMenuClose}>
              <Typography variant="body2">Recommendation accuracy improved by 12%</Typography>
            </MenuItem>
            <MenuItem onClick={handleNotificationMenuClose}>
              <Typography variant="body2">Weekly report is ready</Typography>
            </MenuItem>
          </Menu>

          <Tooltip title="Account">
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleProfileMenuOpen}
              color="inherit"
            >
              <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
                <AccountCircle />
              </Avatar>
            </IconButton>
          </Tooltip>

          <Menu
            id="menu-appbar"
            anchorEl={anchorEl}
            anchorOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            keepMounted
            transformOrigin={{
              vertical: 'top',
              horizontal: 'right',
            }}
            open={Boolean(anchorEl)}
            onClose={handleProfileMenuClose}
            PaperProps={{
              elevation: 3,
              sx: { mt: 2, minWidth: 200 },
            }}
          >
            <MenuItem onClick={() => { handleProfileMenuClose(); navigate('/profile'); }}>
              <Avatar sx={{ width: 24, height: 24, mr: 2 }} />
              Profile
            </MenuItem>
            <MenuItem onClick={() => { handleProfileMenuClose(); navigate('/settings'); }}>
              <Settings sx={{ mr: 2 }} />
              Settings
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleThemeToggle}>
              <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                <Box sx={{ flexGrow: 1 }}>{theme === 'light' ? 'Dark Mode' : 'Light Mode'}</Box>
                {theme === 'light' ? '🌙' : '☀️'}
              </Box>
            </MenuItem>
            <Divider />
            <MenuItem onClick={handleProfileMenuClose}>
              <Logout sx={{ mr: 2 }} color="error" />
              <Typography color="error">Logout</Typography>
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
