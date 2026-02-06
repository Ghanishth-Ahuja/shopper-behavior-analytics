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
import { AppProvider } from './context/AppContext';

function MainLayout() {

  return (
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
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Box>
    </Box>
  );
}

function App() {
  return (
    <AppProvider>
      <MainLayout />
    </AppProvider>
  );
}

export default App;
