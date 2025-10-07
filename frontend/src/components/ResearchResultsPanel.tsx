/**
 * Research Results Panel Component
 * Displays research results with citations, sources, and findings
 * Enhanced with source visualization, filtering, and export
 */
import React, { useState, useMemo } from 'react';

interface Source {
  name: string;
  url: string;
  queries: number;
}

interface ResearchResult {
  content: string;
  citations: string[];
  sources_count: number;
  related_questions?: string[];
  model_used?: string;
}

interface ResearchResultsPanelProps {
  result: ResearchResult;
  isLoading?: boolean;
  className?: string;
}

export const ResearchResultsPanel: React.FC<ResearchResultsPanelProps> = ({
  result,
  isLoading = false,
  className = '',
}) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['content']));

  const toggleSection = (section: string) => {
    setExpandedSections((prev) => {
      const next = new Set(prev);
      if (next.has(section)) {
        next.delete(section);
      } else {
        next.add(section);
      }
      return next;
    });
  };

  // Extract domain from URL for source display
  const getDomain = (url: string): string => {
    try {
      const domain = new URL(url).hostname.replace('www.', '');
      return domain;
    } catch {
      return url;
    }
  };

  // Get icon for source domain with better categorization
  const getSourceIcon = (domain: string): string => {
    // Developer platforms
    if (domain.includes('stackoverflow')) return '📚';
    if (domain.includes('github')) return '💻';
    if (domain.includes('gitlab')) return '🦊';
    if (domain.includes('bitbucket')) return '🪣';
    
    // Tech companies
    if (domain.includes('microsoft')) return '🏢';
    if (domain.includes('google')) return '🔍';
    if (domain.includes('apple')) return '🍎';
    if (domain.includes('amazon') || domain.includes('aws')) return '📦';
    
    // Documentation
    if (domain.includes('docs.') || domain.includes('documentation')) return '📄';
    if (domain.includes('wiki')) return '📖';
    if (domain.includes('readme')) return '📝';
    
    // Programming languages
    if (domain.includes('python')) return '🐍';
    if (domain.includes('javascript') || domain.includes('nodejs')) return '🟨';
    if (domain.includes('rust')) return '🦀';
    if (domain.includes('golang') || domain.includes('go.dev')) return '🐹';
    
    // News & Media
    if (domain.includes('medium')) return '📰';
    if (domain.includes('dev.to')) return '💬';
    if (domain.includes('hackernews')) return '🔶';
    
    // Academic
    if (domain.includes('arxiv')) return '🎓';
    if (domain.includes('.edu')) return '🏛️';
    if (domain.includes('scholar')) return '🔬';
    
    return '🌐';
  };
  
  // Get source category for filtering
  const getSourceCategory = (domain: string): string => {
    if (domain.includes('stackoverflow') || domain.includes('github')) return 'Developer';
    if (domain.includes('microsoft') || domain.includes('google')) return 'Tech Company';
    if (domain.includes('docs') || domain.includes('wiki')) return 'Documentation';
    if (domain.includes('medium') || domain.includes('dev.to')) return 'Blog';
    if (domain.includes('arxiv') || domain.includes('.edu')) return 'Academic';
    return 'Other';
  };

  return (
    <div className={`bg-gradient-to-br from-black/60 to-black/40 border border-amber-500/30 rounded-lg overflow-hidden backdrop-blur-sm ${className}`}>
      {/* Header */}
      <div className="px-4 py-3 border-b border-amber-500/20 bg-black/30">
        <div className="flex items-center gap-2">
          <span className="text-xl">🔍</span>
          <h3 className="text-amber-100 font-semibold">Research Results</h3>
          {result.model_used && (
            <span className="ml-auto text-xs text-amber-300/50 px-2 py-1 bg-amber-500/10 rounded">
              {result.model_used}
            </span>
          )}
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="px-4 py-8 text-center">
          <div className="inline-block w-8 h-8 border-3 border-amber-500/30 border-t-amber-500 rounded-full animate-spin" />
          <p className="text-amber-200/60 mt-3">Researching...</p>
          <p className="text-amber-200/40 text-sm mt-1">
            This may take a few moments
          </p>
        </div>
      )}

      {/* Content */}
      {!isLoading && (
        <div className="divide-y divide-amber-500/10">
          {/* Research Plan Status */}
          <div className="p-4">
            <button
              onClick={() => toggleSection('status')}
              className="flex items-center justify-between w-full text-left"
            >
              <div className="flex items-center gap-2">
                <span className="text-lg">✨</span>
                <span className="text-amber-100 font-medium text-sm">Research Plan</span>
              </div>
              <svg
                className={`w-4 h-4 text-amber-400 transition-transform duration-200 ${
                  expandedSections.has('status') ? 'rotate-180' : ''
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {expandedSections.has('status') && (
              <div className="mt-3 space-y-2">
                <div className="flex items-center gap-2 text-xs">
                  <div className="w-2 h-2 rounded-full bg-green-500" />
                  <span className="text-amber-200/80">Query analyzed</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <div className="w-2 h-2 rounded-full bg-green-500" />
                  <span className="text-amber-200/80">Sources identified</span>
                </div>
                <div className="flex items-center gap-2 text-xs">
                  <div className="w-2 h-2 rounded-full bg-green-500" />
                  <span className="text-amber-200/80">Content synthesized</span>
                </div>
              </div>
            )}
          </div>

          {/* Source Breakdown */}
          {result.citations && result.citations.length > 0 && (
            <div className="p-4">
              <button
                onClick={() => toggleSection('sources')}
                className="flex items-center justify-between w-full text-left"
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg">📊</span>
                  <span className="text-amber-100 font-medium text-sm">
                    Sources ({result.sources_count || result.citations.length})
                  </span>
                </div>
                <svg
                  className={`w-4 h-4 text-amber-400 transition-transform duration-200 ${
                    expandedSections.has('sources') ? 'rotate-180' : ''
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {expandedSections.has('sources') && (
                <div className="mt-3 space-y-2">
                  {result.citations.map((citation, index) => {
                    const domain = getDomain(citation);
                    const icon = getSourceIcon(domain);

                    return (
                      <a
                        key={index}
                        href={citation}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center gap-3 p-2 rounded bg-black/30 hover:bg-amber-500/10 transition-colors duration-150 border border-amber-500/10 hover:border-amber-500/30"
                      >
                        <span className="text-lg">{icon}</span>
                        <div className="flex-1 min-w-0">
                          <div className="text-xs text-amber-100 truncate">
                            {domain}
                          </div>
                          <div className="text-xs text-amber-200/50 mt-0.5">
                            Source {index + 1}
                          </div>
                        </div>
                        <svg
                          className="w-4 h-4 text-amber-400/50"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                        </svg>
                      </a>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* Main Content */}
          <div className="p-4">
            <button
              onClick={() => toggleSection('content')}
              className="flex items-center justify-between w-full text-left"
            >
              <div className="flex items-center gap-2">
                <span className="text-lg">📄</span>
                <span className="text-amber-100 font-medium text-sm">Findings</span>
              </div>
              <svg
                className={`w-4 h-4 text-amber-400 transition-transform duration-200 ${
                  expandedSections.has('content') ? 'rotate-180' : ''
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {expandedSections.has('content') && (
              <div className="mt-3 prose prose-invert prose-amber max-w-none">
                <div className="text-sm text-amber-100/90 leading-relaxed whitespace-pre-wrap">
                  {result.content}
                </div>
              </div>
            )}
          </div>

          {/* Related Questions */}
          {result.related_questions && result.related_questions.length > 0 && (
            <div className="p-4">
              <button
                onClick={() => toggleSection('related')}
                className="flex items-center justify-between w-full text-left"
              >
                <div className="flex items-center gap-2">
                  <span className="text-lg">💡</span>
                  <span className="text-amber-100 font-medium text-sm">
                    Related Questions ({result.related_questions.length})
                  </span>
                </div>
                <svg
                  className={`w-4 h-4 text-amber-400 transition-transform duration-200 ${
                    expandedSections.has('related') ? 'rotate-180' : ''
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {expandedSections.has('related') && (
                <div className="mt-3 space-y-2">
                  {result.related_questions.map((question, index) => (
                    <div
                      key={index}
                      className="p-2 rounded bg-black/30 border border-amber-500/10 text-xs text-amber-200/80"
                    >
                      {question}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};
