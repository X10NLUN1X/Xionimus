import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Button } from './UI/Button'
import { useToast } from './UI/Toast'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'

interface ContextStatus {
  session_id: string
  total_messages: number
  estimated_tokens: number
  context_limit: number
  usage_percentage: number
  should_fork: boolean
  warning_message: string | null
}

interface ContextWarningBannerProps {
  sessionId: string | null
  onForkClick: () => void
}

export const ContextWarningBanner: React.FC<ContextWarningBannerProps> = ({
  sessionId,
  onForkClick
}) => {
  const [contextStatus, setContextStatus] = useState<ContextStatus | null>(null)
  const [isVisible, setIsVisible] = useState(false)
  const { showToast } = useToast()

  useEffect(() => {
    if (!sessionId) {
      setIsVisible(false)
      return
    }

    const checkContext = async () => {
      try {
        const token = localStorage.getItem('xionimus_token')
        const response = await axios.get(
          `${BACKEND_URL}/api/session-fork/context-status/${sessionId}`,
          {
            headers: token ? {
              'Authorization': `Bearer ${token}`
            } : {}
          }
        )

        const status: ContextStatus = response.data
        setContextStatus(status)
        setIsVisible(status.should_fork)
      } catch (error) {
        console.debug('Context status check unavailable:', error)
        setIsVisible(false)
      }
    }

    checkContext()
    const interval = setInterval(checkContext, 30000)
    return () => clearInterval(interval)
  }, [sessionId])

  if (!isVisible || !contextStatus) {
    return null
  }

  const getAlertVariant = (): 'error' | 'warning' | 'info' => {
    if (contextStatus.usage_percentage >= 95) return 'error'
    if (contextStatus.usage_percentage >= 80) return 'warning'
    return 'info'
  }

  const getProgressColor = () => {
    if (contextStatus.usage_percentage >= 95) return 'bg-red-500'
    if (contextStatus.usage_percentage >= 80) return 'bg-orange-500'
    return 'bg-blue-500'
  }

  const getBorderColor = () => {
    if (contextStatus.usage_percentage >= 95) return 'border-red-500/50'
    if (contextStatus.usage_percentage >= 80) return 'border-orange-500/50'
    return 'border-blue-500/50'
  }

  const getBackgroundColor = () => {
    if (contextStatus.usage_percentage >= 95) return 'bg-red-500/10'
    if (contextStatus.usage_percentage >= 80) return 'bg-orange-500/10'
    return 'bg-blue-500/10'
  }

  const getIconColor = () => {
    if (contextStatus.usage_percentage >= 95) return 'text-red-400'
    if (contextStatus.usage_percentage >= 80) return 'text-orange-400'
    return 'text-blue-400'
  }

  const alertVariant = getAlertVariant()

  return (
    <div className={`glossy-card ${getBorderColor()} ${getBackgroundColor()} mb-4 p-4 space-y-3 animate-slide-in`}>
      <div className="flex items-start gap-3">
        <div className={`text-2xl ${getIconColor()} mt-0.5`}>
          {alertVariant === 'error' ? '🚨' : alertVariant === 'warning' ? '⚠️' : 'ℹ️'}
        </div>
        <div className="flex-1">
          <h3 className={`text-base font-semibold ${getIconColor()} mb-1`}>
            ⚠️ Context-Auslastung hoch
          </h3>
          <p className="text-sm text-gray-300">
            {contextStatus.warning_message}
          </p>
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between text-xs">
          <span className="text-gray-400">
            {contextStatus.estimated_tokens.toLocaleString()} / {contextStatus.context_limit.toLocaleString()} Tokens
          </span>
          <span className={`font-bold ${
            alertVariant === 'error' ? 'text-red-400' : 
            alertVariant === 'warning' ? 'text-orange-400' : 
            'text-blue-400'
          }`}>
            {contextStatus.usage_percentage.toFixed(1)}%
          </span>
        </div>
        
        <div className="w-full h-2 bg-primary-navy/50 rounded-full overflow-hidden">
          <div 
            className={`h-full transition-all duration-500 ${getProgressColor()}`}
            style={{ width: `${Math.min(contextStatus.usage_percentage, 100)}%` }}
          />
        </div>
      </div>

      <div className="flex items-center gap-3">
        <Button
          size="sm"
          variant="primary"
          onClick={onForkClick}
          leftIcon={<span>🔀</span>}
        >
          Session forken
        </Button>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => setIsVisible(false)}
        >
          Später
        </Button>
      </div>

      <div className="flex items-start gap-2 pt-2 border-t border-gold-500/20">
        <span className="text-sm">💡</span>
        <p className="text-xs text-gray-400">
          Ein Fork erstellt eine neue Session mit kompakter Zusammenfassung - ideal für lange Gespräche!
        </p>
      </div>
    </div>
  )
}
