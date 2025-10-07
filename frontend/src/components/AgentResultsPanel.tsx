/**
 * Agent Results Panel Component
 * Generic component for displaying results from any agent
 */
import React from 'react';
import { AgentType, AgentExecutionResult } from '../services/agentService';
import { ResearchResultsPanel } from './ResearchResultsPanel';

interface AgentResultsPanelProps {
  result: AgentExecutionResult;
  isLoading?: boolean;
  className?: string;
}

const AGENT_ICONS: Record<AgentType, string> = {
  research: '🔍',
  code_review: '👁️',
  testing: '🧪',
  documentation: '📝',
  debugging: '🐛',
  security: '🔒',
  performance: '⚡',
  fork: '🔀',
};

const AGENT_LABELS: Record<AgentType, string> = {
  research: 'Research Results',
  code_review: 'Code Review',
  testing: 'Test Results',
  documentation: 'Documentation',
  debugging: 'Debugging Analysis',
  security: 'Security Analysis',
  performance: 'Performance Analysis',
  fork: 'Fork Results',
};

export const AgentResultsPanel: React.FC<AgentResultsPanelProps> = ({
  result,
  isLoading = false,
  className = '',
}) => {
  // Special handling for research agent
  if (result.agent_type === 'research' && result.output_data) {
    return (
      <ResearchResultsPanel
        result={result.output_data as any}
        isLoading={isLoading}
        className={className}
      />
    );
  }

  // Generic display for other agents
  const icon = AGENT_ICONS[result.agent_type];
  const label = AGENT_LABELS[result.agent_type];

  return (
    <div className={`bg-gradient-to-br from-black/60 to-black/40 border border-amber-500/30 rounded-lg overflow-hidden backdrop-blur-sm ${className}`}>
      {/* Header */}
      <div className="px-4 py-3 border-b border-amber-500/20 bg-black/30">
        <div className="flex items-center gap-2">
          <span className="text-xl">{icon}</span>
          <h3 className="text-amber-100 font-semibold">{label}</h3>
          {result.model && (
            <span className="ml-auto text-xs text-amber-300/50 px-2 py-1 bg-amber-500/10 rounded">
              {result.model}
            </span>
          )}
        </div>
        {result.duration_seconds && (
          <div className="text-xs text-amber-200/50 mt-1">
            Completed in {result.duration_seconds.toFixed(2)}s
          </div>
        )}
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="px-4 py-8 text-center">
          <div className="inline-block w-8 h-8 border-3 border-amber-500/30 border-t-amber-500 rounded-full animate-spin" />
          <p className="text-amber-200/60 mt-3">Processing...</p>
        </div>
      )}

      {/* Error State */}
      {result.status === 'failed' && result.error_message && (
        <div className="p-4">
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <span className="text-xl">⚠️</span>
              <div>
                <div className="text-red-400 font-medium text-sm">Error</div>
                <div className="text-red-300/80 text-xs mt-1">{result.error_message}</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Success Content */}
      {result.status === 'completed' && result.output_data && !isLoading && (
        <div className="p-4">
          {/* Code Review */}
          {result.agent_type === 'code_review' && result.output_data.review && (
            <div className="prose prose-invert prose-amber max-w-none">
              <div className="text-sm text-amber-100/90 leading-relaxed whitespace-pre-wrap">
                {result.output_data.review}
              </div>
            </div>
          )}

          {/* Testing */}
          {result.agent_type === 'testing' && result.output_data.tests && (
            <div className="space-y-3">
              <div className="text-xs text-amber-200/60 mb-2">
                Framework: {result.output_data.test_framework || 'pytest'}
              </div>
              <pre className="bg-black/50 border border-amber-500/20 rounded p-3 text-xs text-amber-100 overflow-x-auto">
                {result.output_data.tests}
              </pre>
            </div>
          )}

          {/* Documentation */}
          {result.agent_type === 'documentation' && result.output_data.documentation && (
            <div className="prose prose-invert prose-amber max-w-none">
              <div className="text-sm text-amber-100/90 leading-relaxed whitespace-pre-wrap">
                {result.output_data.documentation}
              </div>
            </div>
          )}

          {/* Debugging */}
          {result.agent_type === 'debugging' && result.output_data.analysis && (
            <div className="prose prose-invert prose-amber max-w-none">
              <div className="text-sm text-amber-100/90 leading-relaxed whitespace-pre-wrap">
                {result.output_data.analysis}
              </div>
            </div>
          )}

          {/* Security */}
          {result.agent_type === 'security' && result.output_data.security_analysis && (
            <div className="prose prose-invert prose-amber max-w-none">
              <div className="text-sm text-amber-100/90 leading-relaxed whitespace-pre-wrap">
                {result.output_data.security_analysis}
              </div>
            </div>
          )}

          {/* Performance */}
          {result.agent_type === 'performance' && result.output_data.performance_analysis && (
            <div className="prose prose-invert prose-amber max-w-none">
              <div className="text-sm text-amber-100/90 leading-relaxed whitespace-pre-wrap">
                {result.output_data.performance_analysis}
              </div>
            </div>
          )}

          {/* Fork */}
          {result.agent_type === 'fork' && (
            <div className="space-y-2 text-sm">
              {result.output_data.success && (
                <div className="flex items-center gap-2 text-green-400">
                  <span>✓</span>
                  <span>Operation successful</span>
                </div>
              )}
              <pre className="bg-black/50 border border-amber-500/20 rounded p-3 text-xs text-amber-100 overflow-x-auto">
                {JSON.stringify(result.output_data, null, 2)}
              </pre>
            </div>
          )}

          {/* Token Usage */}
          {result.token_usage && (
            <div className="mt-4 pt-4 border-t border-amber-500/10">
              <div className="flex items-center gap-4 text-xs text-amber-200/50">
                <div>
                  Input: {result.token_usage.input_tokens} tokens
                </div>
                <div>
                  Output: {result.token_usage.output_tokens} tokens
                </div>
                <div>
                  Total: {result.token_usage.total_tokens} tokens
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
