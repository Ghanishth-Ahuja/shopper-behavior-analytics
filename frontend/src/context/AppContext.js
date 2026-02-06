import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { analyticsApi } from '../api/analyticsApi';

// Initial state
const initialState = {
  // Global UI state
  loading: false,
  error: null,
  
  // Dashboard filters
  dateRange: {
    start: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), // 30 days ago
    end: new Date(),
  },
  selectedSegment: null,
  selectedCategory: null,
  
  // Data cache
  segments: [],
  metrics: {},
  affinityData: {},
  recommendations: {},
  reviewData: {},
  
  // User preferences
  sidebarOpen: true,
  theme: 'light',
};

// Action types
const actionTypes = {
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  CLEAR_ERROR: 'CLEAR_ERROR',
  
  SET_DATE_RANGE: 'SET_DATE_RANGE',
  SET_SELECTED_SEGMENT: 'SET_SELECTED_SEGMENT',
  SET_SELECTED_CATEGORY: 'SET_SELECTED_CATEGORY',
  
  SET_SEGMENTS: 'SET_SEGMENTS',
  SET_METRICS: 'SET_METRICS',
  SET_AFFINITY_DATA: 'SET_AFFINITY_DATA',
  SET_RECOMMENDATIONS: 'SET_RECOMMENDATIONS',
  SET_REVIEW_DATA: 'SET_REVIEW_DATA',
  
  TOGGLE_SIDEBAR: 'TOGGLE_SIDEBAR',
  SET_THEME: 'SET_THEME',
};

// Reducer
function appReducer(state, action) {
  switch (action.type) {
    case actionTypes.SET_LOADING:
      return {
        ...state,
        loading: action.payload,
      };
    
    case actionTypes.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        loading: false,
      };
    
    case actionTypes.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      };
    
    case actionTypes.SET_DATE_RANGE:
      return {
        ...state,
        dateRange: action.payload,
      };
    
    case actionTypes.SET_SELECTED_SEGMENT:
      return {
        ...state,
        selectedSegment: action.payload,
      };
    
    case actionTypes.SET_SELECTED_CATEGORY:
      return {
        ...state,
        selectedCategory: action.payload,
      };
    
    case actionTypes.SET_SEGMENTS:
      return {
        ...state,
        segments: action.payload,
      };
    
    case actionTypes.SET_METRICS:
      return {
        ...state,
        metrics: { ...state.metrics, ...action.payload },
      };
    
    case actionTypes.SET_AFFINITY_DATA:
      return {
        ...state,
        affinityData: { ...state.affinityData, ...action.payload },
      };
    
    case actionTypes.SET_RECOMMENDATIONS:
      return {
        ...state,
        recommendations: { ...state.recommendations, ...action.payload },
      };
    
    case actionTypes.SET_REVIEW_DATA:
      return {
        ...state,
        reviewData: { ...state.reviewData, ...action.payload },
      };
    
    case actionTypes.TOGGLE_SIDEBAR:
      return {
        ...state,
        sidebarOpen: !state.sidebarOpen,
      };
    
    case actionTypes.SET_THEME:
      return {
        ...state,
        theme: action.payload,
      };
    
    default:
      return state;
  }
}

// Create context
const AppContext = createContext();

// Provider component
export function AppProvider({ children }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Action creators
  const actions = {
    setLoading: (loading) => dispatch({ type: actionTypes.SET_LOADING, payload: loading }),
    setError: (error) => dispatch({ type: actionTypes.SET_ERROR, payload: error }),
    clearError: () => dispatch({ type: actionTypes.CLEAR_ERROR }),
    
    setDateRange: (dateRange) => dispatch({ type: actionTypes.SET_DATE_RANGE, payload: dateRange }),
    setSelectedSegment: (segment) => dispatch({ type: actionTypes.SET_SELECTED_SEGMENT, payload: segment }),
    setSelectedCategory: (category) => dispatch({ type: actionTypes.SET_SELECTED_CATEGORY, payload: category }),
    
    setSegments: (segments) => dispatch({ type: actionTypes.SET_SEGMENTS, payload: segments }),
    setMetrics: (metrics) => dispatch({ type: actionTypes.SET_METRICS, payload: metrics }),
    setAffinityData: (data) => dispatch({ type: actionTypes.SET_AFFINITY_DATA, payload: data }),
    setRecommendations: (recommendations) => dispatch({ type: actionTypes.SET_RECOMMENDATIONS, payload: recommendations }),
    setReviewData: (reviewData) => dispatch({ type: actionTypes.SET_REVIEW_DATA, payload: reviewData }),
    
    toggleSidebar: () => dispatch({ type: actionTypes.TOGGLE_SIDEBAR }),
    setTheme: (theme) => dispatch({ type: actionTypes.SET_THEME, payload: theme }),
  };

  // Load initial data
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        actions.setLoading(true);
        
        // Load segments
        const segments = await analyticsApi.getSegments();
        actions.setSegments(segments);
        
        // Load dashboard metrics
        const metrics = await analyticsApi.getDashboardMetrics();
        actions.setMetrics(metrics);
        
      } catch (error) {
        actions.setError(error.message);
      } finally {
        actions.setLoading(false);
      }
    };

    loadInitialData();
  }, []);

  const value = {
    ...state,
    ...actions,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

// Hook to use the context
export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
}

export default AppContext;
