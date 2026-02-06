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

function App() {
  return (
    <AppProvider>
      <Box sx={{ display: 'flex' }}>
        <Navbar />
        <Sidebar />
        <Box
          component="main"
          sx={{
            flexGrow: 1,
            p: 3,
            mt: 8, // navbar height
            ml: 240, // sidebar width
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
    </AppProvider>
  );
}

export default App;
