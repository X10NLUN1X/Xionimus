/**
 * Centralized API Configuration
 * Single source of truth for backend URLs and API settings
 */

// Global constants
export const AUTH_TOKEN_KEY = 'xionimus_token'; // Single source of truth for token storage

// Get backend URL from environment variables
const getBackendUrl = (): string => {
  // Try Vite env vars first, then React env vars, then fallback
  const url = 
    import.meta.env.VITE_BACKEND_URL || 
    'http://localhost:8001';
  
  // Remove trailing slash if present
  return url.endsWith('/') ? url.slice(0, -1) : url;
};

export const API_CONFIG = {
  // Base URL for all API calls
  BASE_URL: getBackendUrl(),
  
  // WebSocket URL (derived from BASE_URL)
  WS_URL: getBackendUrl().replace('http:', 'ws:').replace('https:', 'wss:'),
  
  // API Version
  VERSION: '/api/v1',
  
  // API Endpoints (versioned)
  ENDPOINTS: {
    // Auth
    AUTH: '/api/auth',
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    
    // Chat (versioned)
    CHAT: '/api/v1/chat',
    CHAT_STREAM: '/api/v1/chat/stream',
    CHAT_WS: '/ws/chat',
    
    // Sessions (versioned)
    SESSIONS: '/api/v1/sessions',
    
    // Files (versioned)
    FILES: '/api/v1/files',
    UPLOAD: '/api/v1/files/upload',
    
    // Workspace (versioned)
    WORKSPACE: '/api/v1/workspace',
    
    // GitHub (versioned)
    GITHUB: '/api/v1/github',
    GITHUB_OAUTH: '/api/v1/github/oauth/url',
    GITHUB_TOKEN: '/api/v1/github/oauth/token',
    GITHUB_PUSH: '/api/v1/github/push',
    
    // RAG (versioned)
    RAG: '/api/v1/rag',
    
    // Multimodal (versioned)
    MULTIMODAL: '/api/v1/multimodal',
  },
  
  // Request settings
  TIMEOUT: 30000, // 30 seconds
  
  // Headers
  getHeaders: (includeAuth = true): HeadersInit => {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    if (includeAuth) {
      const token = localStorage.getItem(AUTH_TOKEN_KEY); // Use global constant
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }
    
    return headers;
  },
  
  // Build full URL
  url: (endpoint: string): string => {
    return `${API_CONFIG.BASE_URL}${endpoint}`;
  },
};

// Helper function for API calls
export const apiCall = async <T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> => {
  const url = API_CONFIG.url(endpoint);
  
  const response = await fetch(url, {
    ...options,
    headers: {
      ...API_CONFIG.getHeaders(),
      ...options.headers,
    },
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ 
      message: 'Request failed' 
    }));
    throw new Error(error.message || `HTTP ${response.status}`);
  }
  
  return response.json();
};

export default API_CONFIG;
