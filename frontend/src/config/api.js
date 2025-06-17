import axios from 'axios';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

// Create axios instance with base configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
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
  workflows: '/workflows'
};

// API functions
export const apiService = {
  // Health check
  healthCheck: () => api.get(endpoints.health),
  
  // Generate documentation
  generateDocumentation: (data) => api.post(endpoints.generate, data),
  
  // Get workflow status
  getWorkflowStatus: (workflowId) => api.get(endpoints.status(workflowId)),
  
  // Submit feedback
  submitFeedback: (data) => api.post(endpoints.feedback, data),
  
  // Get agents status
  getAgentsStatus: () => api.get(endpoints.agentsStatus),
  
  // Get all workflows
  getWorkflows: () => api.get(endpoints.workflows)
};

export default api; 