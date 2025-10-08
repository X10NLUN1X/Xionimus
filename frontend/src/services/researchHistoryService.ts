/**
 * Research History API Service
 * Communicates with backend for research history management and PDF export
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

export interface TokenUsage {
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
}

export interface ResearchResult {
  content: string;
  citations: string[];
  sources_count: number;
  related_questions?: string[];
  model_used?: string;
}

export interface ResearchHistoryItem {
  id: string;
  user_id: string;
  timestamp: Date;
  query: string;
  result: ResearchResult;
  duration_seconds?: number;
  token_usage?: TokenUsage;
  is_favorite: boolean;
}

export interface ResearchHistoryCreate {
  query: string;
  result: ResearchResult;
  duration_seconds?: number;
  token_usage?: TokenUsage;
}

/**
 * Get authorization token from localStorage
 */
const getAuthToken = (): string | null => {
  return localStorage.getItem('xionimus_token');
};

/**
 * Get auth headers
 */
const getAuthHeaders = (): HeadersInit => {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
};

/**
 * Save research to backend (MongoDB)
 */
export const saveResearchToBackend = async (
  research: ResearchHistoryCreate
): Promise<ResearchHistoryItem> => {
  const response = await fetch(`${API_URL}/api/research/save`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify(research)
  });

  if (!response.ok) {
    throw new Error('Failed to save research to backend');
  }

  const data = await response.json();
  return {
    ...data,
    timestamp: new Date(data.timestamp)
  };
};

/**
 * Get research history from backend
 */
export const getResearchHistoryFromBackend = async (
  limit: number = 50,
  skip: number = 0,
  favoritesOnly: boolean = false
): Promise<ResearchHistoryItem[]> => {
  const params = new URLSearchParams({
    limit: limit.toString(),
    skip: skip.toString(),
    favorites_only: favoritesOnly.toString()
  });

  const response = await fetch(
    `${API_URL}/api/research/history?${params}`,
    {
      headers: getAuthHeaders()
    }
  );

  if (!response.ok) {
    throw new Error('Failed to fetch research history');
  }

  const data = await response.json();
  return data.map((item: any) => ({
    ...item,
    timestamp: new Date(item.timestamp)
  }));
};

/**
 * Delete research from backend
 */
export const deleteResearchFromBackend = async (
  researchId: string
): Promise<void> => {
  const response = await fetch(
    `${API_URL}/api/research/history/${researchId}`,
    {
      method: 'DELETE',
      headers: getAuthHeaders()
    }
  );

  if (!response.ok) {
    throw new Error('Failed to delete research');
  }
};

/**
 * Toggle favorite status
 */
export const toggleFavoriteBackend = async (
  researchId: string
): Promise<boolean> => {
  const response = await fetch(
    `${API_URL}/api/research/history/${researchId}/favorite`,
    {
      method: 'PATCH',
      headers: getAuthHeaders()
    }
  );

  if (!response.ok) {
    throw new Error('Failed to toggle favorite');
  }

  const data = await response.json();
  return data.is_favorite;
};

/**
 * Export single research as PDF
 */
export const exportResearchPDF = async (researchId: string): Promise<void> => {
  const response = await fetch(
    `${API_URL}/api/research/history/${researchId}/export-pdf`,
    {
      headers: getAuthHeaders()
    }
  );

  if (!response.ok) {
    throw new Error('Failed to export PDF');
  }

  // Download the PDF
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `research-${researchId.substring(0, 8)}.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
};

/**
 * Export multiple research items as bulk PDF
 */
export const exportBulkPDF = async (
  researchIds: string[],
  title: string = 'Research Export',
  includeSources: boolean = true,
  includeMetadata: boolean = true
): Promise<void> => {
  const response = await fetch(`${API_URL}/api/research/export-bulk-pdf`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: JSON.stringify({
      research_ids: researchIds,
      title,
      include_sources: includeSources,
      include_metadata: includeMetadata
    })
  });

  if (!response.ok) {
    throw new Error('Failed to export bulk PDF');
  }

  // Download the PDF
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  
  const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
  a.download = `research-export-${timestamp}.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
};

/**
 * Get research statistics
 */
export const getResearchStats = async (): Promise<{
  total_queries: number;
  favorites: number;
  total_sources: number;
  total_tokens: number;
  average_sources_per_query: number;
}> => {
  const response = await fetch(`${API_URL}/api/research/stats`, {
    headers: getAuthHeaders()
  });

  if (!response.ok) {
    throw new Error('Failed to fetch stats');
  }

  return await response.json();
};
