/**
 * Agent Service - API calls for multi-agent system
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

export type AgentType = 
  | 'research'
  | 'code_review'
  | 'testing'
  | 'documentation'
  | 'debugging'
  | 'security'
  | 'performance'
  | 'fork';

export interface AgentExecutionRequest {
  agent_type: AgentType;
  input_data: Record<string, any>;
  session_id?: string;
  user_id?: string;
  parent_execution_id?: string;
  options?: Record<string, any>;
  api_keys?: Record<string, string>;
}

export interface AgentExecutionResult {
  execution_id: string;
  agent_type: AgentType;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  output_data?: Record<string, any>;
  error_message?: string;
  provider: string;
  model?: string;
  started_at: string;
  completed_at?: string;
  duration_seconds?: number;
  token_usage?: {
    input_tokens: number;
    output_tokens: number;
    total_tokens: number;
  };
  metadata?: Record<string, any>;
}

export interface AgentInfo {
  type: AgentType;
  provider: string;
  model: string | null;
  timeout: number;
  description: string;
}

export interface AgentHealth {
  agent_type: AgentType;
  is_healthy: boolean;
  provider: string;
  model?: string;
  last_check: string;
  response_time_ms?: number;
  error_message?: string;
  success_rate_24h?: number;
}

class AgentService {
  private getAuthToken(): string | null {
    // FIX: Use correct token key 'xionimus_token' instead of 'token'
    return localStorage.getItem('xionimus_token');
  }

  private getHeaders(): HeadersInit {
    const token = this.getAuthToken();
    return {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    };
  }

  /**
   * Execute an agent
   */
  async executeAgent(request: AgentExecutionRequest): Promise<AgentExecutionResult> {
    // FIX: Use versioned API endpoint /api/v1/
    const response = await fetch(`${API_BASE_URL}/api/v1/multi-agents/execute`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Agent execution failed');
    }

    return response.json();
  }

  /**
   * Execute agent with streaming (SSE)
   */
  async executeAgentStreaming(
    request: AgentExecutionRequest,
    onChunk: (chunk: any) => void,
    onError: (error: string) => void,
    onComplete: () => void
  ): Promise<void> {
    const token = this.getAuthToken();
    
    // FIX: Use versioned API endpoint /api/v1/
    const response = await fetch(`${API_BASE_URL}/api/v1/multi-agents/execute/stream`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(request),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Streaming failed');
    }

    const reader = response.body?.getReader();
    const decoder = new TextDecoder();

    if (!reader) {
      throw new Error('Response body is not readable');
    }

    try {
      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          onComplete();
          break;
        }

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              onChunk(data);
            } catch (e) {
              console.error('Failed to parse SSE data:', e);
            }
          } else if (line.startsWith('event: error')) {
            onError('Streaming error occurred');
          }
        }
      }
    } catch (error) {
      onError(error instanceof Error ? error.message : 'Unknown streaming error');
    }
  }

  /**
   * Get all available agent types
   */
  async getAgentTypes(): Promise<{ total_agents: number; agents: AgentInfo[] }> {
    // FIX: Use versioned API endpoint /api/v1/
    const response = await fetch(`${API_BASE_URL}/api/v1/multi-agents/types`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch agent types');
    }

    return response.json();
  }

  /**
   * Get health status of all agents
   */
  async getAgentsHealth(): Promise<{
    overall_healthy: boolean;
    agents: Record<string, AgentHealth>;
    total_agents: number;
    healthy_agents: number;
  }> {
    // FIX: Use versioned API endpoint /api/v1/
    const response = await fetch(`${API_BASE_URL}/api/v1/multi-agents/health`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error('Failed to fetch agent health');
    }

    return response.json();
  }

  /**
   * Get health status of a specific agent
   */
  async getAgentHealth(agentType: AgentType): Promise<AgentHealth> {
    const response = await fetch(`${API_BASE_URL}/api/multi-agents/health/${agentType}`, {
      headers: this.getHeaders(),
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch health for ${agentType}`);
    }

    return response.json();
  }

  /**
   * Execute collaborative agents
   */
  async executeCollaborative(
    primaryRequest: AgentExecutionRequest,
    strategy: 'sequential' | 'parallel' | 'conditional' = 'sequential'
  ): Promise<any> {
    const response = await fetch(
      `${API_BASE_URL}/api/multi-agents/collaborative?strategy=${strategy}`,
      {
        method: 'POST',
        headers: this.getHeaders(),
        body: JSON.stringify(primaryRequest),
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Collaborative execution failed');
    }

    return response.json();
  }
}

export const agentService = new AgentService();
