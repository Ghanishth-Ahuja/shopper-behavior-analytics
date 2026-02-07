import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Box } from '@mui/material';
import Navbar from './components/layout/Navbar';
import Sidebar from './components/layout/Sidebar';
import Dashboard from './pages/Dashboard';
import SegmentExplorer from './pages/SegmentExplorer';
import SegmentDetail from './pages/SegmentDetail';
import ProductAffinity from './pages/ProductAffinity';
import RecommendationIntelligence from './pages/RecommendationIntelligence';
import ReviewIntelligence from './pages/ReviewIntelligence';
import UserExplorer from './pages/UserExplorer';
import DataManagement from './pages/DataManagement';
import Settings from './pages/Settings';
import Profile from './pages/Profile';
import Login from './pages/Login';
import Register from './pages/Register';
import { AppProvider, useApp } from './context/AppContext';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import LoadingSpinner from './components/common/LoadingSpinner';

const ProtectedRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  if (loading) return <LoadingSpinner fullScreen message="Checking authorization..." />;
  return isAuthenticated ? children : <Navigate to="/login" replace />;
};

function ThemeWrapper({ children }) {
  const { theme: currentTheme } = useApp();
  
  const muiTheme = React.useMemo(() => createTheme({
    palette: {
      mode: currentTheme || 'light',
      primary: {
        main: '#1976d2',
        light: '#42a5f5',
        dark: '#1565c0',
      },
      secondary: {
        main: '#dc004e',
      },
      background: {
        default: currentTheme === 'dark' ? '#121212' : '#f5f5f5',
        paper: currentTheme === 'dark' ? '#1e1e1e' : '#ffffff',
      },
    },
    typography: {
      fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
      h4: { fontWeight: 600 },
      h5: { fontWeight: 600 },
      h6: { fontWeight: 600 },
    },
    shape: {
      borderRadius: 12,
    },
    components: {
      MuiCard: {
        styleOverrides: {
          root: {
            boxShadow: currentTheme === 'dark' ? '0 4px 20px rgba(0,0,0,0.5)' : '0 2px 8px rgba(0,0,0,0.1)',
          },
        },
      },
      MuiButton: {
        styleOverrides: {
          root: {
            textTransform: 'none',
            borderRadius: 8,
          },
        },
      },
    },
  }), [currentTheme]);

  return (
    <ThemeProvider theme={muiTheme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
}

function AuthenticatedApp() {
  return (
    <ProtectedRoute>
      <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: 'background.default' }}>
        <Navbar />
        <Sidebar />
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: 3,
            mt: 8, // navbar height
            overflowX: 'hidden',
            minHeight: 'calc(100vh - 64px)',
            display: 'block'
          }}
        >
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/segments" element={<SegmentExplorer />} />
            <Route path="/segments/:segmentId" element={<SegmentDetail />} />
            <Route path="/affinity" element={<ProductAffinity />} />
            <Route path="/recommendations" element={<RecommendationIntelligence />} />
            <Route path="/reviews" element={<ReviewIntelligence />} />
            <Route path="/users" element={<UserExplorer />} />
            <Route path="/data" element={<DataManagement />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/profile" element={<Profile />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Box>
      </Box>
    </ProtectedRoute>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppProvider>
        <ThemeWrapper>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/*" element={<AuthenticatedApp />} />
          </Routes>
        </ThemeWrapper>
      </AppProvider>
    </AuthProvider>
  );
}

export default App;
