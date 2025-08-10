// API Endpoints
export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/api/v1/auth/login',
    REGISTER: '/api/v1/auth/register',
    REFRESH: '/api/v1/auth/refresh',
    LOGOUT: '/api/v1/auth/logout',
  },
  USERS: {
    ME: '/api/v1/users/me',
    UPDATE_PROFILE: '/api/v1/users/me',
    STATS: '/api/v1/users/me/stats',
    DELETE_ACCOUNT: '/api/v1/users/me',
  },
  BOOKINGS: {
    LIST: '/api/v1/bookings',
    CREATE: '/api/v1/bookings',
    GET: (id: string) => `/api/v1/bookings/${id}`,
    CANCEL: (id: string) => `/api/v1/bookings/${id}/cancel`,
    UPDATE: (id: string) => `/api/v1/bookings/${id}`,
  },
  CABS: {
    LIST: '/api/v1/cabs',
    AVAILABILITY: '/api/v1/cabs/availability',
  },
} as const;

// Route Paths
export const ROUTES = {
  HOME: '/',
  SIGNIN: '/signin',
  SIGNUP: '/signup',
  PROFILE: '/profile',
  BOOKINGS: '/bookings',
  SERVICES: '/services',
  FLEET: '/fleet',
  PRICING: '/pricing',
  ABOUT: '/about',
  CONTACT: '/contact',
  PRIVACY: '/privacy',
  HELP: '/help',
} as const;

// Time Constants (in milliseconds)
export const TIME = {
  SECOND: 1000,
  MINUTE: 60 * 1000,
  HOUR: 60 * 60 * 1000,
  DAY: 24 * 60 * 60 * 1000,
} as const;

// Session & Auth Constants
export const AUTH = {
  SESSION_TIMEOUT: 30 * TIME.MINUTE, // 30 minutes
  ACTIVITY_CHECK_INTERVAL: TIME.MINUTE, // Check every minute
  TOKEN_REFRESH_THRESHOLD: 5 * TIME.MINUTE, // Refresh if expires in 5 minutes
  MAX_LOGIN_ATTEMPTS: 5,
  LOGIN_LOCKOUT_DURATION: 15 * TIME.MINUTE, // 15 minutes
} as const;

// Booking Status
export enum BookingStatus {
  PENDING = 'pending',
  CONFIRMED = 'confirmed',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
}

// User Roles
export enum UserRole {
  CUSTOMER = 'customer',
  DRIVER = 'driver',
  ADMIN = 'admin',
}

// Payment Status
export enum PaymentStatus {
  PENDING = 'pending',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
  REFUNDED = 'refunded',
}

// Trip Types
export enum TripType {
  ONE_WAY = 'one-way',
  ROUND_TRIP = 'round-trip',
}

// Validation Rules
export const VALIDATION = {
  PASSWORD: {
    MIN_LENGTH: 8,
    MAX_LENGTH: 128,
    PATTERN: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
    MESSAGE: 'Password must be at least 8 characters with uppercase, lowercase, number, and special character',
  },
  PHONE: {
    PATTERN: /^(\+?91)?[6-9]\d{9}$/,
    MESSAGE: 'Please enter a valid Indian phone number',
  },
  EMAIL: {
    PATTERN: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    MESSAGE: 'Please enter a valid email address',
  },
  OTP: {
    LENGTH: 6,
    EXPIRY: 10 * TIME.MINUTE, // 10 minutes
  },
} as const;

// Pagination
export const PAGINATION = {
  DEFAULT_PAGE: 1,
  DEFAULT_LIMIT: 10,
  MAX_LIMIT: 100,
} as const;

// Price Constants
export const PRICING = {
  GST_RATE: 0.05, // 5%
  CONVENIENCE_FEE: 50, // ₹50
  CANCELLATION_CHARGE: 100, // ₹100
  NIGHT_CHARGE_MULTIPLIER: 1.2, // 20% extra
  PEAK_HOUR_MULTIPLIER: 1.5, // 50% extra
  MINIMUM_FARE: 100, // ₹100
} as const;

// Distance Constants
export const DISTANCE = {
  MIN_BOOKING_KM: 10, // Minimum 10 km
  MAX_BOOKING_KM: 3000, // Maximum 3000 km
  FREE_WAITING_MINUTES: 15, // 15 minutes free waiting
  WAITING_CHARGE_PER_MINUTE: 2, // ₹2 per minute after free time
} as const;

// UI Constants
export const UI = {
  TOAST_DURATION: 5000, // 5 seconds
  DEBOUNCE_DELAY: 300, // 300ms
  ANIMATION_DURATION: 200, // 200ms
  MAX_FILE_SIZE: 5 * 1024 * 1024, // 5MB
  ALLOWED_IMAGE_TYPES: ['image/jpeg', 'image/png', 'image/webp'],
} as const;

// Error Messages
export const ERROR_MESSAGES = {
  GENERIC: 'Something went wrong. Please try again.',
  NETWORK: 'Network connection failed. Please check your internet connection.',
  TIMEOUT: 'Request timed out. Please try again.',
  UNAUTHORIZED: 'You are not authorized to perform this action.',
  FORBIDDEN: 'Access denied.',
  NOT_FOUND: 'The requested resource was not found.',
  VALIDATION: 'Please check your input and try again.',
  SERVER: 'Server error. Please try again later.',
} as const;

// Success Messages
export const SUCCESS_MESSAGES = {
  LOGIN: 'Welcome back! You have successfully signed in.',
  REGISTER: 'Account created successfully!',
  LOGOUT: 'You have been signed out successfully.',
  BOOKING_CREATED: 'Your booking has been confirmed!',
  BOOKING_CANCELLED: 'Your booking has been cancelled.',
  PROFILE_UPDATED: 'Your profile has been updated successfully.',
  PASSWORD_CHANGED: 'Your password has been changed successfully.',
} as const;

// Local Storage Keys
export const STORAGE_KEYS = {
  AUTH_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER_PREFERENCES: 'user_preferences',
  RECENT_SEARCHES: 'recent_searches',
  THEME: 'theme',
} as const;

// Environment Variables
export const ENV = {
  API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  APP_URL: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
  IS_PRODUCTION: process.env.NODE_ENV === 'production',
  IS_DEVELOPMENT: process.env.NODE_ENV === 'development',
} as const;
