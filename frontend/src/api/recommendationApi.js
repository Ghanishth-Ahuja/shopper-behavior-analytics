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
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Recommendation API endpoints
export const recommendationApi = {
  // User recommendations
  getUserRecommendations: (userId, params = {}) => 
    api.get(`/recommendations/user/${userId}`, { params }).then(res => res.data),
  
  // Segment recommendations
  getSegmentRecommendations: (segmentId, params = {}) => 
    api.get(`/recommendations/segment/${segmentId}`, { params }).then(res => res.data),
  
  // Similar products
  getSimilarProducts: (productId, params = {}) => 
    api.get(`/recommendations/similar/${productId}`, { params }).then(res => res.data),
  
  // Trending products
  getTrendingProducts: (params = {}) => 
    api.get('/recommendations/trending', { params }).then(res => res.data),
  
  // Frequently bought together
  getFrequentlyBoughtTogether: (productId, params = {}) => 
    api.get(`/recommendations/frequently-bought-together/${productId}`, { params }).then(res => res.data),
  
  // Recommendation explanation
  explainRecommendation: (userId, productId) => 
    api.get(`/recommendations/explain/${userId}/${productId}`).then(res => res.data),
  
  // Feedback
  recordFeedback: (userId, productId, feedback, position) => 
    api.post('/recommendations/feedback', { userId, productId, feedback, position }).then(res => res.data),
  
  // Performance metrics
  getPerformanceMetrics: () => 
    api.get('/recommendations/performance').then(res => res.data),
  
  // Analytics
  getRecommendationAnalytics: (params = {}) => 
    api.get('/recommendations/analytics', { params }).then(res => res.data),
  
  // A/B testing
  getABTestResults: (testId) => 
    api.get(`/recommendations/ab-test/${testId}`).then(res => res.data),
  
  // Model management
  refreshModels: () => 
    api.post('/recommendations/refresh-models').then(res => res.data),
};

export default api;
