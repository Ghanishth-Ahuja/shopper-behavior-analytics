import { VALIDATION_PATTERNS } from './constants';

// Email validation
export const validateEmail = (email) => {
  if (!email) return false;
  
  return VALIDATION_PATTERNS.EMAIL.test(email);
};

// User ID validation
export const validateUserId = (userId) => {
  if (!userId) return false;
  
  return VALIDATION_PATTERNS.USER_ID.test(userId);
};

// Product ID validation
export const validateProductId = (productId) => {
  if (!productId) return false;
  
  return VALIDATION_PATTERNS.PRODUCT_ID.test(productId);
};

// Phone validation
export const validatePhone = (phone) => {
  if (!phone) return false;
  
  return VALIDATION_PATTERNS.PHONE.test(phone);
};

// Required field validation
export const validateRequired = (value) => {
  return value !== null && value !== undefined && value !== '';
};

// Length validation
export const validateLength = (value, minLength, maxLength) => {
  if (!value) return true;
  
  const length = value.length;
  return length >= minLength && length <= maxLength;
};

// Number range validation
export const validateRange = (value, min, max) => {
  if (value === null || value === undefined) return false;
  
  return value >= min && value <= max;
};

// Rating validation
export const validateRating = (rating) => {
  if (rating === null || rating === undefined) return false;
  
  return Number.isInteger(rating) && rating >= 1 && rating <= 5;
};

// Price validation
export const validatePrice = (price) => {
  if (price === null || price === undefined) return false;
  
  return Number.isFinite(price) && price >= 0;
};

// Date validation
export const validateDate = (date) => {
  if (!date) return false;
  
  const dateObj = new Date(date);
  return !isNaN(dateObj.getTime());
};

// Date range validation
export const validateDateRange = (startDate, endDate) => {
  if (!startDate || !endDate) return false;
  
  const start = new Date(startDate);
  const end = new Date(endDate);
  
  return start <= end;
};

// URL validation
export const validateUrl = (url) => {
  if (!url) return false;
  
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

// Password validation
export const validatePassword = (password) => {
  if (!password) return false;
  
  // At least 8 characters, one uppercase, one lowercase, one number, one special character
  const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
  
  return passwordRegex.test(password);
};

// Credit card validation
export const validateCreditCard = (cardNumber) => {
  if (!cardNumber) return false;
  
  // Remove spaces and dashes
  const cleanNumber = cardNumber.replace(/[\s-]/g, '');
  
  // Check if it's all digits and has correct length
  if (!/^\d+$/.test(cleanNumber) || cleanNumber.length < 13 || cleanNumber.length > 19) {
    return false;
  }
  
  // Luhn algorithm
  let sum = 0;
  let isEven = false;
  
  for (let i = cleanNumber.length - 1; i >= 0; i--) {
    let digit = parseInt(cleanNumber[i], 10);
    
    if (isEven) {
      digit *= 2;
      if (digit > 9) {
        digit -= 9;
      }
    }
    
    sum += digit;
    isEven = !isEven;
  }
  
  return sum % 10 === 0;
};

// Form validation
export const validateForm = (formData, validationRules) => {
  const errors = {};
  let isValid = true;
  
  for (const [field, rules] of Object.entries(validationRules)) {
    const value = formData[field];
    const fieldErrors = [];
    
    // Check if required
    if (rules.required && !validateRequired(value)) {
      fieldErrors.push('This field is required');
      isValid = false;
    }
    
    // Skip other validations if field is empty and not required
    if (!value && !rules.required) {
      continue;
    }
    
    // Check email
    if (rules.email && !validateEmail(value)) {
      fieldErrors.push('Please enter a valid email address');
      isValid = false;
    }
    
    // Check user ID
    if (rules.userId && !validateUserId(value)) {
      fieldErrors.push('Please enter a valid user ID');
      isValid = false;
    }
    
    // Check product ID
    if (rules.productId && !validateProductId(value)) {
      fieldErrors.push('Please enter a valid product ID');
      isValid = false;
    }
    
    // Check phone
    if (rules.phone && !validatePhone(value)) {
      fieldErrors.push('Please enter a valid phone number');
      isValid = false;
    }
    
    // Check length
    if (rules.minLength || rules.maxLength) {
      const minLength = rules.minLength || 0;
      const maxLength = rules.maxLength || Infinity;
      
      if (!validateLength(value, minLength, maxLength)) {
        fieldErrors.push(`Must be between ${minLength} and ${maxLength} characters`);
        isValid = false;
      }
    }
    
    // Check range
    if (rules.min !== undefined || rules.max !== undefined) {
      const min = rules.min !== undefined ? rules.min : -Infinity;
      const max = rules.max !== undefined ? rules.max : Infinity;
      
      if (!validateRange(value, min, max)) {
        fieldErrors.push(`Must be between ${min} and ${max}`);
        isValid = false;
      }
    }
    
    // Check rating
    if (rules.rating && !validateRating(value)) {
      fieldErrors.push('Rating must be between 1 and 5');
      isValid = false;
    }
    
    // Check price
    if (rules.price && !validatePrice(value)) {
      fieldErrors.push('Please enter a valid price');
      isValid = false;
    }
    
    // Check date
    if (rules.date && !validateDate(value)) {
      fieldErrors.push('Please enter a valid date');
      isValid = false;
    }
    
    // Check URL
    if (rules.url && !validateUrl(value)) {
      fieldErrors.push('Please enter a valid URL');
      isValid = false;
    }
    
    // Check password
    if (rules.password && !validatePassword(value)) {
      fieldErrors.push('Password must be at least 8 characters with uppercase, lowercase, number, and special character');
      isValid = false;
    }
    
    // Check custom validation
    if (rules.custom && typeof rules.custom === 'function') {
      const customResult = rules.custom(value);
      if (customResult !== true) {
        fieldErrors.push(customResult);
        isValid = false;
      }
    }
    
    if (fieldErrors.length > 0) {
      errors[field] = fieldErrors;
    }
  }
  
  return { isValid, errors };
};

// Sanitize input
export const sanitizeInput = (input, maxLength = 1000) => {
  if (!input) return '';
  
  // Remove potentially dangerous characters
  const dangerousChars = ['<', '>', '&', '"', "'", '/', '\\', '(', ')', '{', '}'];
  let sanitized = input;
  
  for (const char of dangerousChars) {
    sanitized = sanitized.replace(new RegExp(`\\${char}`, 'g'), '');
  }
  
  // Truncate to max length
  return sanitized.substring(0, maxLength);
};

// Sanitize HTML
export const sanitizeHtml = (html) => {
  if (!html) return '';
  
  // Basic HTML sanitization (in production, use a library like DOMPurify)
  return html
    .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
    .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '')
    .replace(/<object\b[^<]*(?:(?!<\/object>)<[^<]*)*<\/object>/gi, '')
    .replace(/<embed\b[^<]*(?:(?!<\/embed>)<[^<]*)*<\/embed>/gi, '');
};

// Validate file type
export const validateFileType = (file, allowedTypes) => {
  if (!file || !file.type) return false;
  
  return allowedTypes.includes(file.type);
};

// Validate file size
export const validateFileSize = (file, maxSizeInMB) => {
  if (!file || !file.size) return false;
  
  const maxSizeInBytes = maxSizeInMB * 1024 * 1024;
  return file.size <= maxSizeInBytes;
};

// Validate image file
export const validateImageFile = (file) => {
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
  return validateFileType(file, allowedTypes);
};

// Validate CSV file
export const validateCsvFile = (file) => {
  const allowedTypes = ['text/csv', 'application/vnd.ms-excel'];
  return validateFileType(file, allowedTypes);
};

export default {
  validateEmail,
  validateUserId,
  validateProductId,
  validatePhone,
  validateRequired,
  validateLength,
  validateRange,
  validateRating,
  validatePrice,
  validateDate,
  validateDateRange,
  validateUrl,
  validatePassword,
  validateCreditCard,
  validateForm,
  sanitizeInput,
  sanitizeHtml,
  validateFileType,
  validateFileSize,
  validateImageFile,
  validateCsvFile,
};
