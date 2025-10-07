/**
 * Research History Manager
 * Stores and retrieves research queries and results
 */

export interface ResearchHistoryItem {
  id: string;
  timestamp: Date;
  query: string;
  result: {
    content: string;
    citations: string[];
    sources_count: number;
    related_questions?: string[];
    model_used?: string;
  };
  duration_seconds?: number;
  token_usage?: {
    input_tokens: number;
    output_tokens: number;
    total_tokens: number;
  };
  isFavorite?: boolean;
}

const STORAGE_KEY = 'xionimus_research_history';
const MAX_HISTORY_ITEMS = 50; // Limit to prevent localStorage overflow

/**
 * Get all research history
 */
export const getResearchHistory = (): ResearchHistoryItem[] => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return [];
    
    const items = JSON.parse(stored);
    // Convert timestamp strings back to Date objects
    return items.map((item: any) => ({
      ...item,
      timestamp: new Date(item.timestamp)
    }));
  } catch (error) {
    console.error('Failed to load research history:', error);
    return [];
  }
};

/**
 * Save a research query to history
 */
export const saveResearchToHistory = (item: Omit<ResearchHistoryItem, 'id'>): ResearchHistoryItem => {
  try {
    const history = getResearchHistory();
    
    const newItem: ResearchHistoryItem = {
      ...item,
      id: `research_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    };
    
    // Add to beginning of array
    history.unshift(newItem);
    
    // Limit history size
    const limitedHistory = history.slice(0, MAX_HISTORY_ITEMS);
    
    localStorage.setItem(STORAGE_KEY, JSON.stringify(limitedHistory));
    
    return newItem;
  } catch (error) {
    console.error('Failed to save research to history:', error);
    throw error;
  }
};

/**
 * Delete a research item from history
 */
export const deleteResearchFromHistory = (id: string): void => {
  try {
    const history = getResearchHistory();
    const filtered = history.filter(item => item.id !== id);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(filtered));
  } catch (error) {
    console.error('Failed to delete research from history:', error);
    throw error;
  }
};

/**
 * Toggle favorite status
 */
export const toggleResearchFavorite = (id: string): void => {
  try {
    const history = getResearchHistory();
    const updated = history.map(item => 
      item.id === id ? { ...item, isFavorite: !item.isFavorite } : item
    );
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
  } catch (error) {
    console.error('Failed to toggle favorite:', error);
    throw error;
  }
};

/**
 * Clear all history
 */
export const clearResearchHistory = (): void => {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch (error) {
    console.error('Failed to clear history:', error);
    throw error;
  }
};

/**
 * Search history by query text
 */
export const searchResearchHistory = (searchTerm: string): ResearchHistoryItem[] => {
  const history = getResearchHistory();
  const lowerSearch = searchTerm.toLowerCase();
  
  return history.filter(item => 
    item.query.toLowerCase().includes(lowerSearch) ||
    item.result.content.toLowerCase().includes(lowerSearch)
  );
};

/**
 * Get favorite research items
 */
export const getFavoriteResearch = (): ResearchHistoryItem[] => {
  return getResearchHistory().filter(item => item.isFavorite);
};

/**
 * Get research statistics
 */
export const getResearchStats = () => {
  const history = getResearchHistory();
  
  const totalQueries = history.length;
  const totalTokens = history.reduce((sum, item) => 
    sum + (item.token_usage?.total_tokens || 0), 0
  );
  const totalSources = history.reduce((sum, item) => 
    sum + item.result.sources_count, 0
  );
  const favorites = history.filter(item => item.isFavorite).length;
  
  // Most used sources
  const sourceDomains: Record<string, number> = {};
  history.forEach(item => {
    item.result.citations?.forEach(citation => {
      try {
        const domain = new URL(citation).hostname.replace('www.', '');
        sourceDomains[domain] = (sourceDomains[domain] || 0) + 1;
      } catch (e) {
        // Invalid URL, skip
      }
    });
  });
  
  const topSources = Object.entries(sourceDomains)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([domain, count]) => ({ domain, count }));
  
  return {
    totalQueries,
    totalTokens,
    totalSources,
    favorites,
    topSources,
    averageSourcesPerQuery: totalQueries > 0 ? totalSources / totalQueries : 0
  };
};

/**
 * Export history as JSON
 */
export const exportResearchHistory = (): string => {
  const history = getResearchHistory();
  return JSON.stringify(history, null, 2);
};

/**
 * Import history from JSON
 */
export const importResearchHistory = (jsonString: string): void => {
  try {
    const imported = JSON.parse(jsonString);
    if (!Array.isArray(imported)) {
      throw new Error('Invalid history format');
    }
    
    const existing = getResearchHistory();
    const combined = [...imported, ...existing];
    
    // Remove duplicates based on query and timestamp
    const unique = combined.filter((item, index, self) => 
      index === self.findIndex(t => 
        t.query === item.query && 
        new Date(t.timestamp).getTime() === new Date(item.timestamp).getTime()
      )
    );
    
    const limited = unique.slice(0, MAX_HISTORY_ITEMS);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(limited));
  } catch (error) {
    console.error('Failed to import history:', error);
    throw error;
  }
};
