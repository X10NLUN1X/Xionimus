import React, { useState, useMemo, useCallback } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Badge } from './UI/Badge'

interface AgentResult {
  agent: string
  icon: string
  content: string
  summary: string
  data?: any
}

interface AgentResultsDisplayProps {
  agentResults: AgentResult[]
}

export const AgentResultsDisplay: React.FC<AgentResultsDisplayProps> = ({ agentResults }) => {
  const [expandedAgents, setExpandedAgents] = useState<Set<string>>(new Set())
  
  const toggleAgent = useCallback((agentName: string) => {
    setExpandedAgents(prev => {
      const newExpanded = new Set(prev)
      if (newExpanded.has(agentName)) {
        newExpanded.delete(agentName)
      } else {
        newExpanded.add(agentName)
      }
      return newExpanded
    })
  }, [])
  
  const uniqueResults = useMemo(() => {
    const seen = new Set<string>()
    return agentResults.filter(result => {
      const key = `${result.agent}-${result.summary}`
      if (seen.has(key)) {
        return false
      }
      seen.add(key)
      return true
    })
  }, [agentResults])
  
  if (!uniqueResults || uniqueResults.length === 0) {
    return null
  }
  
  return (
    <div className="mt-4 glossy-card p-4 border-blue-500/30 bg-blue-500/5">
      <div className="flex items-center gap-2 mb-3">
        <span className="text-sm font-bold text-white">
          🤖 Automatische Verbesserungen
        </span>
        <Badge variant="info" className="text-xs">
          {uniqueResults.length} Agent{uniqueResults.length !== 1 ? 's' : ''}
        </Badge>
      </div>
      
      <div className="space-y-3">
        {uniqueResults.map((result, idx) => {
          const isExpanded = expandedAgents.has(result.agent)
          
          return (
            <div
              key={idx}
              className="glossy-card border-blue-500/20 overflow-hidden"
            >
              <div
                className="p-3 cursor-pointer hover:bg-blue-500/10 transition-colors duration-200 flex items-center justify-between"
                onClick={() => toggleAgent(result.agent)}
              >
                <div className="flex items-center gap-3 flex-1">
                  <span className="text-xl">{result.icon}</span>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-semibold text-blue-400 text-sm">
                        {result.agent}
                      </span>
                    </div>
                    <p className="text-sm text-gray-300">
                      {result.summary}
                    </p>
                  </div>
                </div>
                <button className="p-1 hover:bg-blue-500/20 rounded transition-colors">
                  <svg 
                    className={`w-5 h-5 text-blue-400 transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}
                    fill="none" 
                    viewBox="0 0 24 24" 
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </div>
              
              {isExpanded && (
                <div className="p-3 pt-0 border-t border-blue-500/20 animate-slide-in">
                  <div className="prose prose-sm prose-invert max-w-none">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {result.content}
                    </ReactMarkdown>
                  </div>
                  
                  {result.data && (
                    <div className="mt-3 p-2 bg-primary-navy/50 rounded text-xs font-mono overflow-x-auto custom-scrollbar">
                      <pre className="text-gray-400">
                        {JSON.stringify(result.data, null, 2)}
                      </pre>
                    </div>
                  )}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
