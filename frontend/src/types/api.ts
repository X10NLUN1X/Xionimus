/**
 * TypeScript Type Definitions for API Responses
 * Provides type safety across the entire frontend
 */

// ============================================================================
// Common Types
// ============================================================================

export interface APIResponse<T = any> {
  success: boolean;
  data?: T;
  message?: string;
  error?: APIError;
}

export interface APIError {
  code: string;
  message: string;
  field?: string;
  timestamp: string;
  details?: any[];
}

// ============================================================================
// Auth Types
// ============================================================================

export interface User {
  id: string;
  email: string;
  username: string;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
}

// ============================================================================
// Chat Types
// ============================================================================

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  provider?: string;
  model?: string;
  created_at: string;
}

export interface ChatSession {
  id: string;
  user_id?: string;
  title: string;
  created_at: string;
  updated_at: string;
  messages?: Message[];
}

export interface ChatRequest {
  message: string;
  session_id?: string;
  provider?: string;
  model?: string;
}

export interface ChatResponse {
  message: Message;
  session_id: string;
}

export interface StreamChunk {
  content: string;
  done: boolean;
  session_id?: string;
  message_id?: string;
}

// ============================================================================
// File Types
// ============================================================================

export interface FileInfo {
  id: string;
  name: string;
  path: string;
  size: number;
  type: string;
  uploaded_at: string;
  user_id?: string;
}

export interface UploadResponse {
  file_id: string;
  filename: string;
  path: string;
  size: number;
  url: string;
}

// ============================================================================
// GitHub Types
// ============================================================================

export interface GitHubUser {
  login: string;
  name?: string;
  avatar_url: string;
  email?: string;
}

export interface GitHubOAuthResponse {
  oauth_url: string;
  redirect_uri: string;
}

export interface GitHubTokenResponse {
  access_token: string;
  user: GitHubUser;
}

export interface GitHubRepository {
  id: number;
  name: string;
  full_name: string;
  description?: string;
  private: boolean;
  html_url: string;
  default_branch: string;
  updated_at: string;
}

export interface GitHubBranch {
  name: string;
  commit: {
    sha: string;
    url: string;
  };
  protected: boolean;
}

export interface PushRequest {
  owner: string;
  repo: string;
  files: Array<{
    path: string;
    content: string;
  }>;
  commit_message: string;
  branch?: string;
  access_token: string;
}

export interface PushResponse {
  success: boolean;
  commit_sha: string;
  files_pushed: number;
  repository: string;
  branch: string;
  message: string;
}

// ============================================================================
// Workspace Types
// ============================================================================

export interface WorkspaceFile {
  path: string;
  content: string;
  type: 'file' | 'directory';
  size?: number;
  modified_at?: string;
}

export interface Workspace {
  id: string;
  name: string;
  path: string;
  files: WorkspaceFile[];
  created_at: string;
  updated_at: string;
}

// ============================================================================
// RAG Types
// ============================================================================

export interface RAGDocument {
  id: string;
  content: string;
  metadata: Record<string, any>;
  embedding?: number[];
}

export interface RAGQuery {
  query: string;
  top_k?: number;
  filter?: Record<string, any>;
}

export interface RAGResult {
  documents: RAGDocument[];
  scores: number[];
}

// ============================================================================
// Multimodal Types
// ============================================================================

export interface MultimodalFile {
  file_id: string;
  type: 'image' | 'pdf' | 'document';
  url: string;
  processed: boolean;
}

export interface MultimodalRequest {
  file_id: string;
  prompt?: string;
  options?: Record<string, any>;
}

export interface MultimodalResponse {
  result: string;
  metadata: Record<string, any>;
}

// ============================================================================
// Settings Types
// ============================================================================

export interface APIKeys {
  openai?: string;
  anthropic?: string;
  perplexity?: string;
}

export interface ProviderConfig {
  enabled: boolean;
  default_model?: string;
  api_key_set: boolean;
}

export interface Providers {
  openai: ProviderConfig;
  anthropic: ProviderConfig;
  perplexity: ProviderConfig;
}

// ============================================================================
// WebSocket Types
// ============================================================================

export interface WSMessage {
  type: 'chat' | 'status' | 'error';
  session_id?: string;
  content?: string;
  data?: any;
}

export interface WSConnectionState {
  connected: boolean;
  session_id?: string;
  error?: string;
}
