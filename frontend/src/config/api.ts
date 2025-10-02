/**
 * Centralized API Configuration
 * Single source of truth for backend URLs and API settings
 */

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
  
  // API Endpoints
  ENDPOINTS: {
    // Auth
    AUTH: '/api/auth',
    LOGIN: '/api/auth/login',
    REGISTER: '/api/auth/register',
    
    // Chat
    CHAT: '/api/chat',
    CHAT_STREAM: '/api/chat/stream',
    CHAT_WS: '/ws/chat',
    
    // Sessions
    SESSIONS: '/api/sessions',
    
    // Files
    FILES: '/api/files',
    UPLOAD: '/api/files/upload',
    
    // Workspace
    WORKSPACE: '/api/workspace',
    
    // GitHub
    GITHUB: '/api/github',
    GITHUB_OAUTH: '/api/github/oauth/url',
    GITHUB_TOKEN: '/api/github/oauth/token',
    GITHUB_PUSH: '/api/github/push',
    
    // RAG
    RAG: '/api/rag',
    
    // Multimodal
    MULTIMODAL: '/api/multimodal',
  },
  
  // Request settings
  TIMEOUT: 30000, // 30 seconds
  
  // Headers
  getHeaders: (includeAuth = true): HeadersInit => {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    if (includeAuth) {
      const token = localStorage.getItem('auth_token');
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
