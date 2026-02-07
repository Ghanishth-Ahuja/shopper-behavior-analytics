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
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// User API endpoints
export const userApi = {
  // User management
  getUsers: (params = {}) => api.get('/users', { params }).then(res => res.data),
  getUser: (userId) => api.get(`/users/${userId}`).then(res => res.data),
  createUser: (userData) => api.post('/users', userData).then(res => res.data),
  updateUser: (userId, userData) => api.put(`/users/${userId}`, userData).then(res => res.data),
  deleteUser: (userId) => api.delete(`/users/${userId}`).then(res => res.data),
  
  // User analytics
  getUserAnalytics: (userId) => api.get(`/users/${userId}/analytics`).then(res => res.data),
  getUserSegment: (userId) => api.get(`/users/${userId}/segment`).then(res => res.data),
  
  // User search
  searchUsers: (query, params = {}) => api.get('/users/search', { params: { q: query, ...params } }).then(res => res.data),
  getUsersBySegment: (segmentId, params = {}) => api.get(`/users/segment/${segmentId}`, { params }).then(res => res.data),
  
  // Authentication
  login: (credentials) => api.post('/auth/login', credentials).then(res => res.data),
  register: (userData) => api.post('/auth/register', userData).then(res => res.data),
  logout: () => api.post('/auth/logout').then(res => res.data),
  refreshToken: () => api.post('/auth/refresh').then(res => res.data),
};

export default api;
