import axios from 'axios';

// API Configuration - Use current origin for production, localhost for development
const getApiBaseUrl = () => {
  // If we're in production (served from the same domain), use relative URLs
  if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    return window.location.origin;
  }
  // For local development, use the environment variable or default to localhost
  return process.env.REACT_APP_API_URL || 'http://localhost:8080';
};

const API_BASE_URL = getApiBaseUrl();

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000, // 2 minutes timeout for documentation generation
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to log requests (for debugging)
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor to handle common errors
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    if (error.response) {
      console.error(`API Error: ${error.response.status} ${error.response.config.url}`, error.response.data);
    } else if (error.request) {
      console.error('API Network Error:', error.message);
    } else {
      console.error('API Error:', error.message);
    }
    return Promise.reject(error);
  }
);

// API endpoints
export const endpoints = {
  health: '/health',
  generate: '/generate',
  status: (workflowId) => `/status/${workflowId}`,
  feedback: '/feedback',
  agentsStatus: '/agents/status',
  workflows: '/workflows',
  translationLanguages: '/translation/languages',
  translate: '/translation/translate',
  stopWorkflow: '/stop-workflow'
};

// API functions
export const apiService = {
  // Health check
  healthCheck: () => api.get(endpoints.health),
  
  // Generate documentation (with extended timeout)
  generateDocumentation: (data) => api.post(endpoints.generate, data, { timeout: 300000 }), // 5 minutes
  
  // Get workflow status
  getWorkflowStatus: (workflowId) => api.get(endpoints.status(workflowId)),
  
  // Submit feedback
  submitFeedback: (data) => api.post(endpoints.feedback, data),
  
  // Get agents status
  getAgentsStatus: () => api.get(endpoints.agentsStatus),
  
  // Get all workflows
  getWorkflows: () => api.get(endpoints.workflows),
  
  // Translation services
  getSupportedLanguages: () => api.get(endpoints.translationLanguages),
  translateDocumentation: (data) => api.post(endpoints.translate, data),
  
  // Stop workflow
  stopWorkflow: (workflowId) => api.post(endpoints.stopWorkflow, { workflow_id: workflowId })
};

export default api; 