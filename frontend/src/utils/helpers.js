import { format } from 'date-fns';
import { CHART_COLORS, DATE_FORMATS, NUMBER_FORMATS } from './constants';

// Format currency
export const formatCurrency = (amount, currency = 'USD') => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency,
  }).format(amount);
};

// Format percentage
export const formatPercentage = (value, decimals = 1) => {
  return `${value.toFixed(decimals)}%`;
};

// Format date
export const formatDate = (date, format = DATE_FORMATS.MEDIUM) => {
  if (!date) return 'N/A';
  
  const dateObj = new Date(date);
  if (isNaN(dateObj.getTime())) return 'Invalid Date';
  
  switch (format) {
    case DATE_FORMATS.SHORT:
      return format(dateObj, 'MM/dd/yyyy');
    case DATE_FORMATS.MEDIUM:
      return format(dateObj, 'MMM dd, yyyy');
    case DATE_FORMATS.LONG:
      return format(dateObj, 'MMMM dd, yyyy');
    case DATE_FORMATS.TIME:
      return format(dateObj, 'h:mm a');
    case DATE_FORMATS.DATETIME:
      return format(dateObj, 'MMM dd, yyyy h:mm a');
    default:
      return dateObj.toLocaleDateString();
  }
};

// Format relative time
export const formatRelativeTime = (date) => {
  if (!date) return 'N/A';
  
  const now = new Date();
  const dateObj = new Date(date);
  const diffInSeconds = Math.floor((now - dateObj) / 1000);
  
  if (diffInSeconds < 60) {
    return 'Just now';
  } else if (diffInSeconds < 3600) {
    const minutes = Math.floor(diffInSeconds / 60);
    return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
  } else if (diffInSeconds < 86400) {
    const hours = Math.floor(diffInSeconds / 3600);
    return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  } else if (diffInSeconds < 2592000) {
    const days = Math.floor(diffInSeconds / 86400);
    return `${days} day${days > 1 ? 's' : ''} ago`;
  } else {
    return formatDate(date, DATE_FORMATS.MEDIUM);
  }
};

// Format number with commas
export const formatNumber = (num, decimals = 0) => {
  if (num === null || num === undefined) return 'N/A';
  
  return num.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
};

// Format file size
export const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// Calculate percentage change
export const calculatePercentageChange = (current, previous) => {
  if (previous === 0) return current > 0 ? 100 : 0;
  
  return ((current - previous) / previous) * 100;
};

// Get trend direction
export const getTrendDirection = (current, previous) => {
  if (previous === 0) return 'stable';
  
  const change = calculatePercentageChange(current, previous);
  
  if (change > 5) return 'up';
  if (change < -5) return 'down';
  return 'stable';
};

// Get trend color
export const getTrendColor = (trend) => {
  switch (trend) {
    case 'up': return CHART_COLORS.SUCCESS;
    case 'down': return CHART_COLORS.ERROR;
    default: return CHART_COLORS.GREY;
  }
};

// Get sentiment color
export const getSentimentColor = (sentiment) => {
  switch (sentiment) {
    case 'positive': return CHART_COLORS.POSITIVE;
    case 'negative': return CHART_COLORS.NEGATIVE;
    default: return CHART_COLORS.NEUTRAL;
  }
};

// Get sentiment label
export const getSentimentLabel = (score) => {
  if (score > 0.05) return 'positive';
  if (score < -0.05) return 'negative';
  return 'neutral';
};

// Truncate text
export const truncateText = (text, maxLength = 50) => {
  if (!text || text.length <= maxLength) return text;
  
  return text.substring(0, maxLength) + '...';
};

// Capitalize first letter
export const capitalizeFirst = (str) => {
  if (!str) return '';
  
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

// Convert to title case
export const toTitleCase = (str) => {
  if (!str) return '';
  
  return str.replace(/\w\S*/g, (txt) => 
    txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
  );
};

// Generate random color
export const generateRandomColor = () => {
  const colors = Object.values(CHART_COLORS);
  return colors[Math.floor(Math.random() * colors.length)];
};

// Generate color based on value
export const generateColorByValue = (value, max = 100) => {
  const percentage = (value / max) * 100;
  
  if (percentage >= 80) return CHART_COLORS.SUCCESS;
  if (percentage >= 60) return CHART_COLORS.WARNING;
  if (percentage >= 40) return CHART_COLORS.INFO;
  return CHART_COLORS.ERROR;
};

// Deep clone object
export const deepClone = (obj) => {
  if (obj === null || typeof obj !== 'object') return obj;
  
  if (obj instanceof Date) return new Date(obj.getTime());
  if (obj instanceof Array) return obj.map(item => deepClone(item));
  
  const cloned = {};
  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      cloned[key] = deepClone(obj[key]);
    }
  }
  
  return cloned;
};

// Debounce function
export const debounce = (func, wait) => {
  let timeout;
  
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

// Throttle function
export const throttle = (func, limit) => {
  let inThrottle;
  
  return function() {
    const args = arguments;
    const context = this;
    
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

// Check if object is empty
export const isEmpty = (obj) => {
  if (obj == null) return true;
  
  if (Array.isArray(obj) || typeof obj === 'string') return obj.length === 0;
  
  return Object.keys(obj).length === 0;
};

// Check if value is null or undefined
export const isNil = (value) => {
  return value === null || value === undefined;
};

// Get nested object property safely
export const getNestedProperty = (obj, path, defaultValue = null) => {
  const keys = path.split('.');
  let result = obj;
  
  for (const key of keys) {
    if (result == null || typeof result !== 'object') {
      return defaultValue;
    }
    
    result = result[key];
  }
  
  return result !== undefined ? result : defaultValue;
};

// Set nested object property
export const setNestedProperty = (obj, path, value) => {
  const keys = path.split('.');
  const lastKey = keys.pop();
  
  let current = obj;
  for (const key of keys) {
    if (!(key in current) || typeof current[key] !== 'object') {
      current[key] = {};
    }
    current = current[key];
  }
  
  current[lastKey] = value;
};

// Remove null and undefined values from object
export const removeNulls = (obj) => {
  if (obj == null) return obj;
  
  if (Array.isArray(obj)) {
    return obj.filter(item => item != null).map(item => removeNulls(item));
  }
  
  if (typeof obj === 'object') {
    const result = {};
    for (const key in obj) {
      if (obj[key] != null) {
        result[key] = removeNulls(obj[key]);
      }
    }
    return result;
  }
  
  return obj;
};

// Group array of objects by key
export const groupBy = (array, key) => {
  return array.reduce((groups, item) => {
    const group = item[key];
    groups[group] = groups[group] || [];
    groups[group].push(item);
    return groups;
  }, {});
};

// Sort array of objects by key
export const sortBy = (array, key, direction = 'asc') => {
  return [...array].sort((a, b) => {
    const aVal = a[key];
    const bVal = b[key];
    
    if (aVal < bVal) return direction === 'asc' ? -1 : 1;
    if (aVal > bVal) return direction === 'asc' ? 1 : -1;
    return 0;
  });
};

// Calculate average
export const calculateAverage = (numbers) => {
  if (!numbers || numbers.length === 0) return 0;
  
  const sum = numbers.reduce((acc, num) => acc + num, 0);
  return sum / numbers.length;
};

// Calculate median
export const calculateMedian = (numbers) => {
  if (!numbers || numbers.length === 0) return 0;
  
  const sorted = [...numbers].sort((a, b) => a - b);
  const middle = Math.floor(sorted.length / 2);
  
  return sorted.length % 2 === 0
    ? (sorted[middle - 1] + sorted[middle]) / 2
    : sorted[middle];
};

// Calculate percentile
export const calculatePercentile = (numbers, percentile) => {
  if (!numbers || numbers.length === 0) return 0;
  
  const sorted = [...numbers].sort((a, b) => a - b);
  const index = (percentile / 100) * (sorted.length - 1);
  
  if (index === Math.floor(index)) {
    return sorted[index];
  }
  
  const lower = sorted[Math.floor(index)];
  const upper = sorted[Math.ceil(index)];
  const fraction = index - Math.floor(index);
  
  return lower + (upper - lower) * fraction;
};

export default {
  formatCurrency,
  formatPercentage,
  formatDate,
  formatRelativeTime,
  formatNumber,
  formatFileSize,
  calculatePercentageChange,
  getTrendDirection,
  getTrendColor,
  getSentimentColor,
  getSentimentLabel,
  truncateText,
  capitalizeFirst,
  toTitleCase,
  generateRandomColor,
  generateColorByValue,
  deepClone,
  debounce,
  throttle,
  isEmpty,
  isNil,
  getNestedProperty,
  setNestedProperty,
  removeNulls,
  groupBy,
  sortBy,
  calculateAverage,
  calculateMedian,
  calculatePercentile,
};
