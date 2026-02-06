import axios from 'axios';

// Create axios instance
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Analytics API endpoints
export const analyticsApi = {
  // Dashboard
  getDashboardMetrics: () => api.get('/analytics/dashboard').then(res => res.data),
  
  // Segments
  getSegments: () => api.get('/segmentation').then(res => res.data),
  getSegment: (segmentId) => api.get(`/segmentation/${segmentId}`).then(res => res.data),
  getSegmentInsights: (segmentId) => api.get(`/segmentation/${segmentId}/insights`).then(res => res.data),
  getSegmentUsers: (segmentId, params = {}) => api.get(`/segmentation/${segmentId}/users`, { params }).then(res => res.data),
  
  // Affinity
  getAffinityMatrix: () => api.get('/analytics/affinity-matrix').then(res => res.data),
  getCategoryLift: () => api.get('/analytics/category-lift').then(res => res.data),
  getCustomerPersonas: () => api.get('/analytics/customer-personas').then(res => res.data),
  
  // RFM Analysis
  getRFMAnalysis: () => api.get('/analytics/rfm-analysis').then(res => res.data),
  getCohortAnalysis: () => api.get('/analytics/cohort-analysis').then(res => res.data),
  getConversionFunnel: () => api.get('/analytics/conversion-funnel').then(res => res.data),
  
  // Product Performance
  getProductPerformance: (params = {}) => api.get('/analytics/product-performance', { params }).then(res => res.data),
  getSegmentPerformance: (segmentId) => api.get(`/analytics/segment-performance/${segmentId}`).then(res => res.data),
  
  // Sentiment
  getSentimentAnalysis: (params = {}) => api.get('/analytics/sentiment-analysis', { params }).then(res => res.data),
  getPriceSensitivity: () => api.get('/analytics/price-sensitivity').then(res => res.data),
  getBehavioralPatterns: () => api.get('/analytics/behavioral-patterns').then(res => res.data),
  
  // Events
  getEventAnalytics: (params = {}) => api.get('/analytics/events', { params }).then(res => res.data),
  getEventHeatmap: (params = {}) => api.get('/analytics/heatmap', { params }).then(res => res.data),
};

export default api;
