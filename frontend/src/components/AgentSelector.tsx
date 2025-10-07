/**
 * Agent Selector Component
 * Dropdown selector for choosing which agent to use
 */
import React, { useState, useEffect } from 'react';
import { agentService, AgentType, AgentInfo } from '../services/agentService';

interface AgentSelectorProps {
  selectedAgent: AgentType | null;
  onAgentSelect: (agent: AgentType | null) => void;
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
  research: 'Research',
  code_review: 'Code Review',
  testing: 'Testing',
  documentation: 'Documentation',
  debugging: 'Debugging',
  security: 'Security',
  performance: 'Performance',
  fork: 'Fork',
};

const AGENT_DESCRIPTIONS: Record<AgentType, string> = {
  research: 'Web research with citations',
  code_review: 'Code quality analysis',
  testing: 'Generate unit tests',
  documentation: 'Create documentation',
  debugging: 'Debug and fix errors',
  security: 'Security vulnerability scan',
  performance: 'Performance optimization',
  fork: 'Repository operations',
};

export const AgentSelector: React.FC<AgentSelectorProps> = ({
  selectedAgent,
  onAgentSelect,
  className = '',
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [agents, setAgents] = useState<AgentInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await agentService.getAgentTypes();
      setAgents(data.agents);
    } catch (err) {
      setError('Failed to load agents');
      console.error('Failed to load agents:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAgentSelect = (agent: AgentType) => {
    onAgentSelect(agent);
    setIsOpen(false);
  };

  const handleClearSelection = () => {
    onAgentSelect(null);
    setIsOpen(false);
  };

  return (
    <div className={`relative ${className}`}>
      {/* Selector Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-4 py-2 bg-gradient-to-br from-black/40 to-black/20 border border-amber-500/30 rounded-lg hover:border-amber-400/50 transition-all duration-200 backdrop-blur-sm"
      >
        <span className="text-xl">
          {selectedAgent ? AGENT_ICONS[selectedAgent] : '🤖'}
        </span>
        <span className="text-amber-100 font-medium">
          {selectedAgent ? AGENT_LABELS[selectedAgent] : 'Select Agent'}
        </span>
        <svg
          className={`w-4 h-4 text-amber-400 transition-transform duration-200 ${
            isOpen ? 'rotate-180' : ''
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div
            className="fixed inset-0 z-40"
            onClick={() => setIsOpen(false)}
          />

          {/* Menu */}
          <div className="absolute right-0 mt-2 w-80 bg-gradient-to-br from-black/95 to-black/85 border border-amber-500/30 rounded-lg shadow-2xl backdrop-blur-xl z-50 overflow-hidden">
            {/* Header */}
            <div className="px-4 py-3 border-b border-amber-500/20 bg-black/30">
              <h3 className="text-amber-100 font-semibold flex items-center gap-2">
                <span className="text-xl">🤖</span>
                <span>AI Agents</span>
              </h3>
              <p className="text-xs text-amber-200/60 mt-1">
                Choose an agent for specialized tasks
              </p>
            </div>

            {/* Loading State */}
            {loading && (
              <div className="px-4 py-8 text-center">
                <div className="inline-block w-6 h-6 border-2 border-amber-500/30 border-t-amber-500 rounded-full animate-spin" />
                <p className="text-amber-200/60 text-sm mt-2">Loading agents...</p>
              </div>
            )}

            {/* Error State */}
            {error && (
              <div className="px-4 py-3 text-center">
                <p className="text-red-400 text-sm">{error}</p>
                <button
                  onClick={loadAgents}
                  className="mt-2 text-xs text-amber-400 hover:text-amber-300"
                >
                  Retry
                </button>
              </div>
            )}

            {/* Agent List */}
            {!loading && !error && (
              <div className="max-h-96 overflow-y-auto">
                {/* Clear Selection Option */}
                {selectedAgent && (
                  <button
                    onClick={handleClearSelection}
                    className="w-full px-4 py-3 text-left hover:bg-amber-500/10 transition-colors duration-150 border-b border-amber-500/10"
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-xl">❌</span>
                      <div className="flex-1">
                        <div className="text-amber-100 font-medium text-sm">
                          Clear Selection
                        </div>
                        <div className="text-amber-200/60 text-xs mt-0.5">
                          Return to normal chat mode
                        </div>
                      </div>
                    </div>
                  </button>
                )}

                {/* Agent Options */}
                {agents.map((agent) => {
                  const agentType = agent.type as AgentType;
                  const isSelected = selectedAgent === agentType;

                  return (
                    <button
                      key={agentType}
                      onClick={() => handleAgentSelect(agentType)}
                      className={`w-full px-4 py-3 text-left hover:bg-amber-500/10 transition-colors duration-150 border-b border-amber-500/10 ${
                        isSelected ? 'bg-amber-500/20' : ''
                      }`}
                    >
                      <div className="flex items-start gap-3">
                        <span className="text-xl">{AGENT_ICONS[agentType]}</span>
                        <div className="flex-1">
                          <div className="flex items-center gap-2">
                            <span className="text-amber-100 font-medium text-sm">
                              {AGENT_LABELS[agentType]}
                            </span>
                            {isSelected && (
                              <span className="text-xs text-amber-400">✓</span>
                            )}
                          </div>
                          <div className="text-amber-200/60 text-xs mt-0.5">
                            {AGENT_DESCRIPTIONS[agentType]}
                          </div>
                          <div className="flex items-center gap-2 mt-1">
                            <span className="text-xs text-amber-300/50">
                              {agent.provider}
                            </span>
                            {agent.model && (
                              <>
                                <span className="text-amber-500/30">•</span>
                                <span className="text-xs text-amber-300/50 truncate">
                                  {agent.model}
                                </span>
                              </>
                            )}
                          </div>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            )}

            {/* Footer */}
            <div className="px-4 py-2 border-t border-amber-500/20 bg-black/30">
              <p className="text-xs text-amber-200/40 text-center">
                {agents.length} agents available
              </p>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
