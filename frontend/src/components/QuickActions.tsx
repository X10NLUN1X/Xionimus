import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Badge } from './UI/Badge'

interface QuickAction {
  id: string
  title: string
  description: string
  action: string
  icon?: string
  duration?: string
  provider?: string
  model?: string
}

interface QuickActionsProps {
  message: string
  options: QuickAction[]
  onSelect: (action: QuickAction) => void
  isDisabled?: boolean
}

export const QuickActions: React.FC<QuickActionsProps> = ({
  message,
  options,
  onSelect,
  isDisabled = false
}) => {
  return (
    <div className="glossy-card p-6 mb-4 border-blue-500/30 bg-blue-500/5 animate-fade-in">
      <div className="space-y-4">
        {/* Message/Question */}
        <div className="prose prose-sm prose-invert max-w-none">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {message}
          </ReactMarkdown>
        </div>

        <div className="h-px bg-gold-500/20"></div>

        {/* Options as clickable cards */}
        <div className="space-y-3">
          {options.map((option) => (
            <button
              key={option.id}
              onClick={() => !isDisabled && onSelect(option)}
              disabled={isDisabled}
              className={`
                w-full glossy-card p-5 text-left
                transition-all duration-200
                ${isDisabled 
                  ? 'opacity-50 cursor-not-allowed' 
                  : 'hover:border-blue-500 hover:-translate-y-1 hover:shadow-lg cursor-pointer'
                }
              `}
            >
              <div className="flex items-start gap-4">
                {/* Icon */}
                {option.icon && (
                  <span className="text-2xl flex-shrink-0">
                    {option.icon}
                  </span>
                )}

                {/* Content */}
                <div className="flex-1 space-y-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h4 className="font-bold text-white text-base">
                      {option.title}
                    </h4>
                    {option.duration && (
                      <Badge variant="info" className="text-xs">
                        {option.duration}
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm text-gray-400">
                    {option.description}
                  </p>
                  {option.model && (
                    <Badge variant="default" className="text-xs mt-1">
                      {option.model}
                    </Badge>
                  )}
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}