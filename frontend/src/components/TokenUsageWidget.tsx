import React, { useEffect, useState } from 'react'
import axios from 'axios'
import { Button } from './UI/Button'
import { Badge } from './UI/Badge'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'

interface TokenUsageWidgetProps {
  tokenUsage?: any
  onForkRecommended?: () => void
}

export const TokenUsageWidget: React.FC<TokenUsageWidgetProps> = ({ 
  tokenUsage: propTokenUsage,
  onForkRecommended 
}) => {
  const [tokenUsage, setTokenUsage] = useState<any>(propTokenUsage || null)
  const [isExpanded, setIsExpanded] = useState(false)
  const [isLoading, setIsLoading] = useState(!propTokenUsage)

  useEffect(() => {
    if (propTokenUsage) {
      setTokenUsage(propTokenUsage)
      setIsLoading(false)
    } else {
      fetchTokenUsage()
    }
  }, [propTokenUsage])

  const fetchTokenUsage = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/v1/tokens/stats`)
      setTokenUsage(response.data)
      setIsLoading(false)
    } catch (error) {
      console.error('Failed to fetch token usage:', error)
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return null
  }
  
  // Show widget even without usage data (with defaults)
  if (!tokenUsage) {
    return (
      <div className="fixed bottom-4 right-4 z-50 max-w-[350px] animate-fade-in">
        <div className="glossy-card p-3">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-xs font-semibold text-white">Token Usage</span>
            <Badge variant="success">0</Badge>
          </div>
          <div className="w-full h-2 bg-primary-navy rounded-full overflow-hidden">
            <div className="h-full bg-green-500 transition-all duration-300" style={{ width: '0%' }}></div>
          </div>
          <p className="text-xs text-gray-500 mt-1">0.0% of limit (No messages yet)</p>
        </div>
      </div>
    )
  }

  const currentSession = tokenUsage.current_session || {}
  const recommendation = tokenUsage.recommendation || {}
  const percentages = tokenUsage.percentages || {}
  const limits = tokenUsage.limits || {}

  // Determine color based on usage
  const getColorScheme = () => {
    if (recommendation.level === 'critical') return 'error'
    if (recommendation.level === 'high') return 'warning'
    if (recommendation.level === 'warning') return 'warning'
    return 'success'
  }

  const colorScheme = getColorScheme()
  const percentage = percentages.hard_limit_percentage || 0

  const getProgressColor = () => {
    if (recommendation.level === 'critical') return 'bg-red-500'
    if (recommendation.level === 'high') return 'bg-orange-500'
    if (recommendation.level === 'warning') return 'bg-yellow-500'
    return 'bg-green-500'
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 max-w-[350px] animate-fade-in">
      <div className="glossy-card overflow-hidden">
        {/* Compact View */}
        <div
          className="p-3 cursor-pointer hover:bg-accent-blue/30 transition-colors duration-200"
          onClick={() => setIsExpanded(!isExpanded)}
        >
          <div className="flex items-center justify-between gap-3">
            <div className="flex-1">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-semibold text-white">Token Usage</span>
                <Badge variant={colorScheme}>
                  {currentSession.total_tokens?.toLocaleString() || 0}
                </Badge>
              </div>
              <div className="w-full h-2 bg-primary-navy rounded-full overflow-hidden">
                <div 
                  className={`h-full transition-all duration-300 ${getProgressColor()}`}
                  style={{ width: `${Math.min(percentage, 100)}%` }}
                ></div>
              </div>
              <p className="text-xs text-gray-500 mt-1">
                {percentage.toFixed(1)}% of limit
              </p>
            </div>
            <button className="p-1 hover:bg-accent-blue rounded transition-colors">
              <svg 
                className={`w-5 h-5 text-gray-400 transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>
        </div>

        {/* Expanded View */}
        {isExpanded && (
          <div className="p-3 pt-0 space-y-3 border-t border-gold-500/20 animate-slide-in">
            {/* Recommendation Alert */}
            {recommendation.level !== 'ok' && (
              <div className={`glossy-card p-3 ${
                recommendation.level === 'critical' ? 'border-red-500/50 bg-red-500/10' :
                'border-yellow-500/50 bg-yellow-500/10'
              }`}>
                <div className="flex items-start gap-2">
                  <span className="text-xl">
                    {recommendation.level === 'critical' ? '🚨' : '⚠️'}
                  </span>
                  <div className="flex-1">
                    <p className={`text-xs ${
                      recommendation.level === 'critical' ? 'text-red-400' : 'text-yellow-400'
                    }`}>
                      {recommendation.message}
                    </p>
                    {recommendation.details && (
                      <p className="text-xs text-gray-400 mt-1 opacity-80">
                        {recommendation.details}
                      </p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Stats Grid */}
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-400">Current Session:</span>
                <span className="font-semibold text-white">
                  {currentSession.total_tokens?.toLocaleString() || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Messages:</span>
                <span className="font-semibold text-white">
                  {currentSession.messages_count || 0}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Soft Limit:</span>
                <span className="font-semibold text-white">
                  {limits.soft_limit?.toLocaleString() || 50000}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Hard Limit:</span>
                <span className="font-semibold text-white">
                  {limits.hard_limit?.toLocaleString() || 100000}
                </span>
              </div>
            </div>

            {/* Fork Button (if recommended) */}
            {recommendation.action && recommendation.action !== 'fork_soon' && onForkRecommended && (
              <Button
                variant={recommendation.level === 'critical' ? 'danger' : 'secondary'}
                size="sm"
                onClick={() => {
                  onForkRecommended()
                  setIsExpanded(false)
                }}
                leftIcon={
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                }
                className="w-full"
              >
                {recommendation.level === 'critical' ? 'Fork Now!' : 'Create Fork'}
              </Button>
            )}

            {/* Tips */}
            <div className="p-3 bg-accent-blue/20 rounded-lg">
              <p className="text-xs font-semibold mb-2 text-gold-400">
                💡 Wann Fork/Summary?
              </p>
              <div className="space-y-1 text-xs text-gray-400">
                <p>• &lt;50k tokens: Alles gut ✅</p>
                <p>• 50-100k: Bald forken ⚠️</p>
                <p>• 100k+: Jetzt forken! 🚨</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}