/**
 * API client for TRIDENT backend
 * Uses Axios for HTTP requests
 */

import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Handle common errors
    if (error.response) {
      // Server responded with error status
      const status = error.response.status
      const message = error.response.data?.detail || error.response.data?.message || 'An error occurred'
      
      switch (status) {
        case 401:
          // Unauthorized - clear token
          localStorage.removeItem('auth_token')
          // Could redirect to login here if needed
          break
        case 403:
          // Forbidden
          console.error('Access forbidden:', message)
          break
        case 404:
          // Not found
          console.error('Resource not found:', message)
          break
        case 429:
          // Rate limited
          console.error('Rate limit exceeded:', message)
          break
        case 500:
          // Server error
          console.error('Server error:', message)
          break
        default:
          console.error(`API error (${status}):`, message)
      }
    } else if (error.request) {
      // Request made but no response received
      console.error('Network error: No response from server')
    } else {
      // Error setting up request
      console.error('Request error:', error.message)
    }
    
    return Promise.reject(error)
  }
)

// API endpoint functions
export const healthCheck = () => api.get('/health')

// Traffic API endpoints
export const getTrafficLogs = (params = {}) => api.get('/api/v1/traffic', { params })
export const getTrafficLog = (id) => api.get(`/api/v1/traffic/${id}`)
export const createTrafficLog = (data) => api.post('/api/v1/traffic', data)
export const createTrafficLogsBatch = (data) => api.post('/api/v1/traffic/batch', data)

// Alerts API endpoints
export const getAlerts = (params = {}) => api.get('/api/v1/alerts', { params })
export const getAlert = (id) => api.get(`/api/v1/alerts/${id}`)
export const updateAlert = (id, data) => api.put(`/api/v1/alerts/${id}`, data)

// Recommendations API endpoints
export const getRecommendations = (params = {}) => api.get('/api/v1/recommendations', { params })
export const getRecommendation = (id) => api.get(`/api/v1/recommendations/${id}`)
export const approveRecommendation = (id, data) => api.post(`/api/v1/recommendations/${id}/approve`, data)
export const rejectRecommendation = (id, data) => api.post(`/api/v1/recommendations/${id}/reject`, data)

// Baseline API endpoints
export const getBaselines = (params = {}) => api.get('/api/v1/baseline', { params })
export const getBaselineByIP = (ip) => api.get(`/api/v1/baseline/ip/${ip}`)
export const getBaselineByEndpoint = (endpoint) => api.get(`/api/v1/baseline/endpoint/${endpoint}`)
export const updateBaseline = (data) => api.post('/api/v1/baseline/update', data)

// Detection API endpoints
export const detectAnomaly = (data) => api.post('/api/v1/detection/detect', data)
export const detectAnomaliesBatch = (data) => api.post('/api/v1/detection/batch', data)

// Metrics API endpoints
export const getMetrics = () => api.get('/api/v1/metrics')
export const getLatencyMetrics = () => api.get('/api/v1/metrics/latency')
export const getThroughputMetrics = () => api.get('/api/v1/metrics/throughput')
export const getErrorMetrics = () => api.get('/api/v1/metrics/errors')
export const getModelMetrics = () => api.get('/api/v1/metrics/model')

// Feedback API endpoints
export const submitFeedback = (data) => api.post('/api/v1/feedback', data)
export const getFeedback = (params = {}) => api.get('/api/v1/feedback', { params })
export const getFeedbackById = (id) => api.get(`/api/v1/feedback/${id}`)
export const getFeedbackForAlert = (alertId, params = {}) => api.get(`/api/v1/feedback/alert/${alertId}`, { params })
export const getFeedbackStats = () => api.get('/api/v1/feedback/stats')

export default api

