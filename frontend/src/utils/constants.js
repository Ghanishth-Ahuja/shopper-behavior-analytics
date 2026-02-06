// API endpoints
export const API_ENDPOINTS = {
  BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1',
  
  // Analytics endpoints
  ANALYTICS: {
    DASHBOARD: '/analytics/dashboard',
    AFFINITY_MATRIX: '/analytics/affinity-matrix',
    CATEGORY_LIFT: '/analytics/category-lift',
    CUSTOMER_PERSONAS: '/analytics/customer-personas',
    RFM_ANALYSIS: '/analytics/rfm-analysis',
    COHORT_ANALYSIS: '/analytics/cohort-analysis',
    CONVERSION_FUNNEL: '/analytics/conversion-funnel',
    PRODUCT_PERFORMANCE: '/analytics/product-performance',
    SEGMENT_PERFORMANCE: '/analytics/segment-performance',
    SENTIMENT_ANALYSIS: '/analytics/sentiment-analysis',
    PRICE_SENSITIVITY: '/analytics/price-sensitivity',
    BEHAVIORAL_PATTERNS: '/analytics/behavioral-patterns',
    EVENTS: '/analytics/events',
    HEATMAP: '/analytics/heatmap',
  },
  
  // Segmentation endpoints
  SEGMENTATION: {
    SEGMENTS: '/segmentation',
    SEGMENT: (id) => `/segmentation/${id}`,
    SEGMENT_INSIGHTS: (id) => `/segmentation/${id}/insights`,
    SEGMENT_USERS: (id) => `/segmentation/${id}/users`,
    TRAIN: '/segmentation/train',
  },
  
  // Recommendations endpoints
  RECOMMENDATIONS: {
    USER_RECOMMENDATIONS: (userId) => `/recommendations/user/${userId}`,
    SEGMENT_RECOMMENDATIONS: (segmentId) => `/recommendations/segment/${segmentId}`,
    SIMILAR_PRODUCTS: (productId) => `/recommendations/similar/${productId}`,
    TRENDING: '/recommendations/trending',
    FREQUENTLY_BOUGHT_TOGETHER: (productId) => `/recommendations/frequently-bought-together/${productId}`,
    EXPLAIN: (userId, productId) => `/recommendations/explain/${userId}/${productId}`,
    FEEDBACK: '/recommendations/feedback',
    PERFORMANCE: '/recommendations/performance',
    ANALYTICS: '/recommendations/analytics',
    AB_TEST: (testId) => `/recommendations/ab-test/${testId}`,
    REFRESH_MODELS: '/recommendations/refresh-models',
  },
  
  // User endpoints
  USERS: {
    USERS: '/users',
    USER: (id) => `/users/${id}`,
    USER_ANALYTICS: (id) => `/users/${id}/analytics`,
    USER_SEGMENT: (id) => `/users/${id}/segment`,
    SEARCH: '/users/search',
    SEGMENT_USERS: (segmentId) => `/users/segment/${segmentId}`,
  },
  
  // Auth endpoints
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
  },
};

// Chart colors
export const CHART_COLORS = {
  PRIMARY: '#1976d2',
  SECONDARY: '#dc004e',
  SUCCESS: '#22c55e',
  WARNING: '#ff9800',
  ERROR: '#ef5350',
  INFO: '#2196f3',
  GREY: '#9e9e9e',
  
  // Chart-specific colors
  POSITIVE: '#22c55e',
  NEGATIVE: '#ef5350',
  NEUTRAL: '#9e9e9e',
  
  // Gradient colors
  GRADIENTS: {
    PRIMARY: ['#1976d2', '#42a5f5'],
    SECONDARY: ['#dc004e', '#f06292'],
    SUCCESS: ['#22c55e', '#4caf50'],
    WARNING: ['#ff9800', '#ffa726'],
  },
};

// Segment colors
export const SEGMENT_COLORS = [
  '#0088FE',
  '#00C49F',
  '#FFBB28',
  '#FF8042',
  '#8884D8',
  '#82CA9D',
  '#FFC658',
  '#FF7C7C',
  '#8DD1E1',
  '#D084D0',
];

// Sentiment colors
export const SENTIMENT_COLORS = {
  POSITIVE: '#22c55e',
  NEGATIVE: '#ef5350',
  NEUTRAL: '#9e9e9e',
};

// Time ranges
export const TIME_RANGES = {
  LAST_7_DAYS: 7,
  LAST_30_DAYS: 30,
  LAST_90_DAYS: 90,
  LAST_365_DAYS: 365,
};

// Sort options
export const SORT_OPTIONS = {
  RECENT: 'recent',
  NAME: 'name',
  VALUE: 'value',
  ACTIVITY: 'activity',
  SIZE: 'size',
  CONVERSION: 'conversion',
};

// Filter options
export const FILTER_OPTIONS = {
  ALL: 'all',
  POSITIVE: 'positive',
  NEGATIVE: 'negative',
  NEUTRAL: 'neutral',
  HIGH: 'high',
  MEDIUM: 'medium',
  LOW: 'low',
};

// Pagination defaults
export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 20,
  DEFAULT_PAGE: 1,
  MAX_PAGE_SIZE: 100,
};

// Chart dimensions
export const CHART_DIMENSIONS = {
  SMALL: { width: '100%', height: 200 },
  MEDIUM: { width: '100%', height: 300 },
  LARGE: { width: '100%', height: 400 },
  EXTRA_LARGE: { width: '100%', height: 500 },
};

// Animation durations
export const ANIMATIONS = {
  FAST: 200,
  NORMAL: 300,
  SLOW: 500,
  EXTRA_SLOW: 1000,
};

// Breakpoints
export const BREAKPOINTS = {
  XS: 0,
  SM: 600,
  MD: 960,
  LG: 1280,
  XL: 1920,
};

// Error messages
export const ERROR_MESSAGES = {
  NETWORK_ERROR: 'Network error. Please check your connection.',
  SERVER_ERROR: 'Server error. Please try again later.',
  NOT_FOUND: 'Data not found.',
  UNAUTHORIZED: 'Unauthorized access.',
  FORBIDDEN: 'Access forbidden.',
  VALIDATION_ERROR: 'Invalid data provided.',
  UNKNOWN_ERROR: 'An unexpected error occurred.',
};

// Success messages
export const SUCCESS_MESSAGES = {
  DATA_LOADED: 'Data loaded successfully.',
  DATA_SAVED: 'Data saved successfully.',
  DATA_DELETED: 'Data deleted successfully.',
  OPERATION_SUCCESSFUL: 'Operation completed successfully.',
};

// Loading messages
export const LOADING_MESSAGES = {
  LOADING: 'Loading...',
  SAVING: 'Saving...',
  DELETING: 'Deleting...',
  PROCESSING: 'Processing...',
  FETCHING: 'Fetching data...',
  UPDATING: 'Updating...',
};

// Empty state messages
export const EMPTY_STATE_MESSAGES = {
  NO_DATA: 'No data available.',
  NO_RESULTS: 'No results found.',
  NO_SEGMENTS: 'No segments found.',
  NO_RECOMMENDATIONS: 'No recommendations available.',
  NO_USERS: 'No users found.',
  NO_PRODUCTS: 'No products found.',
  NO_REVIEWS: 'No reviews found.',
};

// Validation patterns
export const VALIDATION_PATTERNS = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  USER_ID: /^[a-zA-Z0-9_]+$/,
  PRODUCT_ID: /^[a-zA-Z0-9_-]+$/,
  PHONE: /^\+?[\d\s-()]+$/,
};

// Date formats
export const DATE_FORMATS = {
  SHORT: 'MM/dd/yyyy',
  MEDIUM: 'MMM dd, yyyy',
  LONG: 'MMMM dd, yyyy',
  TIME: 'h:mm a',
  DATETIME: 'MMM dd, yyyy h:mm a',
  ISO: 'yyyy-MM-ddTHH:mm:ssZ',
};

// Currency formats
export const CURRENCY_FORMATS = {
  USD: { style: 'currency', currency: 'USD' },
  EUR: { style: 'currency', currency: 'EUR' },
  GBP: { style: 'currency', currency: 'GBP' },
};

// Number formats
export const NUMBER_FORMATS = {
  DECIMAL: { minimumFractionDigits: 2, maximumFractionDigits: 2 },
  INTEGER: { maximumFractionDigits: 0 },
  PERCENTAGE: { style: 'percent', minimumFractionDigits: 1, maximumFractionDigits: 1 },
};

export default {
  API_ENDPOINTS,
  CHART_COLORS,
  SEGMENT_COLORS,
  SENTIMENT_COLORS,
  TIME_RANGES,
  SORT_OPTIONS,
  FILTER_OPTIONS,
  PAGINATION,
  CHART_DIMENSIONS,
  ANIMATIONS,
  BREAKPOINTS,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES,
  LOADING_MESSAGES,
  EMPTY_STATE_MESSAGES,
  VALIDATION_PATTERNS,
  DATE_FORMATS,
  CURRENCY_FORMATS,
  NUMBER_FORMATS,
};
