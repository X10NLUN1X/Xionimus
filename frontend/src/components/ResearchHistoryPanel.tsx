/**
 * Research History Panel Component
 * Displays past research queries with ability to view, re-run, and manage
 */
import React, { useState, useEffect } from 'react';
import {
  ResearchHistoryItem,
  getResearchHistory,
  deleteResearchFromHistory,
  toggleResearchFavorite,
  clearResearchHistory,
  searchResearchHistory,
  getFavoriteResearch,
  getResearchStats,
  isItemSynced
} from '../utils/researchHistory';
import { exportResearchPDF, exportBulkPDF } from '../services/researchHistoryService';

interface ResearchHistoryPanelProps {
  onSelectResearch: (item: ResearchHistoryItem) => void;
  onRerunResearch: (query: string) => void;
  className?: string;
}

export const ResearchHistoryPanel: React.FC<ResearchHistoryPanelProps> = ({
  onSelectResearch,
  onRerunResearch,
  className = ''
}) => {
  const [history, setHistory] = useState<ResearchHistoryItem[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filter, setFilter] = useState<'all' | 'favorites'>('all');
  const [showStats, setShowStats] = useState(false);
  const [selectedItems, setSelectedItems] = useState<Set<string>>(new Set());
  const [isExporting, setIsExporting] = useState(false);

  useEffect(() => {
    loadHistory();
  }, [filter, searchTerm]);

  const loadHistory = () => {
    if (searchTerm) {
      setHistory(searchResearchHistory(searchTerm));
    } else if (filter === 'favorites') {
      setHistory(getFavoriteResearch());
    } else {
      setHistory(getResearchHistory());
    }
  };

  const handleDelete = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (confirm('Delete this research from history?')) {
      deleteResearchFromHistory(id);
      loadHistory();
    }
  };

  const handleToggleFavorite = (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    toggleResearchFavorite(id);
    loadHistory();
  };

  const handleClearAll = () => {
    if (confirm('Clear all research history? This cannot be undone.')) {
      clearResearchHistory();
      loadHistory();
    }
  };

  const formatDate = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) {
      const hours = Math.floor(diff / (1000 * 60 * 60));
      if (hours === 0) {
        const minutes = Math.floor(diff / (1000 * 60));
        return minutes === 0 ? 'Just now' : `${minutes}m ago`;
      }
      return `${hours}h ago`;
    } else if (days === 1) {
      return 'Yesterday';
    } else if (days < 7) {
      return `${days}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const stats = getResearchStats();

  return (
    <div className={`bg-gradient-to-br from-black/60 to-black/40 border border-amber-500/30 rounded-lg overflow-hidden backdrop-blur-sm ${className}`}>
      {/* Header */}
      <div className="px-4 py-3 border-b border-amber-500/20 bg-black/30">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-xl">📜</span>
            <h3 className="text-amber-100 font-semibold">Research History</h3>
            <span className="text-xs text-amber-300/50 px-2 py-1 bg-amber-500/10 rounded">
              {history.length}
            </span>
          </div>
          
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowStats(!showStats)}
              className="p-1.5 hover:bg-amber-500/10 rounded transition-colors"
              title="Statistics"
            >
              <svg className="w-4 h-4 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </button>
            {history.length > 0 && (
              <button
                onClick={handleClearAll}
                className="p-1.5 hover:bg-red-500/10 rounded transition-colors"
                title="Clear all"
              >
                <svg className="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                </svg>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Stats Panel */}
      {showStats && (
        <div className="px-4 py-3 border-b border-amber-500/20 bg-black/20">
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div>
              <div className="text-amber-200/60 text-xs">Total Queries</div>
              <div className="text-amber-100 font-semibold">{stats.totalQueries}</div>
            </div>
            <div>
              <div className="text-amber-200/60 text-xs">Favorites</div>
              <div className="text-amber-100 font-semibold">{stats.favorites}</div>
            </div>
            <div>
              <div className="text-amber-200/60 text-xs">Total Sources</div>
              <div className="text-amber-100 font-semibold">{stats.totalSources}</div>
            </div>
            <div>
              <div className="text-amber-200/60 text-xs">Avg Sources/Query</div>
              <div className="text-amber-100 font-semibold">{stats.averageSourcesPerQuery.toFixed(1)}</div>
            </div>
          </div>
        </div>
      )}

      {/* Search & Filters */}
      <div className="px-4 py-3 border-b border-amber-500/20 space-y-2">
        <input
          type="text"
          placeholder="Search history..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full px-3 py-2 bg-black/30 border border-amber-500/20 rounded text-amber-100 text-sm placeholder-amber-200/40 focus:outline-none focus:border-amber-500/50"
        />
        
        <div className="flex gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`flex-1 px-3 py-1.5 text-xs rounded transition-colors ${
              filter === 'all'
                ? 'bg-amber-500/30 text-amber-100 border border-amber-500/50'
                : 'bg-black/30 text-amber-200/60 border border-amber-500/10 hover:border-amber-500/30'
            }`}
          >
            All
          </button>
          <button
            onClick={() => setFilter('favorites')}
            className={`flex-1 px-3 py-1.5 text-xs rounded transition-colors ${
              filter === 'favorites'
                ? 'bg-amber-500/30 text-amber-100 border border-amber-500/50'
                : 'bg-black/30 text-amber-200/60 border border-amber-500/10 hover:border-amber-500/30'
            }`}
          >
            ⭐ Favorites
          </button>
        </div>
      </div>

      {/* History List */}
      <div className="max-h-[600px] overflow-y-auto">
        {history.length === 0 ? (
          <div className="px-4 py-8 text-center text-amber-200/40 text-sm">
            {searchTerm ? 'No matching research found' : 
             filter === 'favorites' ? 'No favorites yet' : 
             'No research history yet'}
          </div>
        ) : (
          <div className="divide-y divide-amber-500/10">
            {history.map((item) => (
              <div
                key={item.id}
                className="px-4 py-3 hover:bg-amber-500/5 transition-colors cursor-pointer group"
                onClick={() => onSelectResearch(item)}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <div className="text-sm text-amber-100 font-medium truncate">
                        {item.query}
                      </div>
                      {item.isFavorite && (
                        <span className="text-sm">⭐</span>
                      )}
                    </div>
                    
                    <div className="flex items-center gap-2 mt-1 text-xs text-amber-200/50">
                      <span>{formatDate(item.timestamp)}</span>
                      <span>•</span>
                      <span>{item.result.sources_count} sources</span>
                      {item.duration_seconds && (
                        <>
                          <span>•</span>
                          <span>{item.duration_seconds.toFixed(1)}s</span>
                        </>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                      onClick={(e) => handleToggleFavorite(item.id, e)}
                      className="p-1.5 hover:bg-amber-500/20 rounded transition-colors"
                      title={item.isFavorite ? 'Remove from favorites' : 'Add to favorites'}
                    >
                      <span className="text-base">{item.isFavorite ? '⭐' : '☆'}</span>
                    </button>
                    
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onRerunResearch(item.query);
                      }}
                      className="p-1.5 hover:bg-amber-500/20 rounded transition-colors"
                      title="Re-run research"
                    >
                      <svg className="w-4 h-4 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                    </button>
                    
                    <button
                      onClick={(e) => handleDelete(item.id, e)}
                      className="p-1.5 hover:bg-red-500/20 rounded transition-colors"
                      title="Delete"
                    >
                      <svg className="w-4 h-4 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
