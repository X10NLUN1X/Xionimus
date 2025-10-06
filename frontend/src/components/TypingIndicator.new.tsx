import React from 'react'

interface TypingIndicatorProps {
  streamingText?: string
  showDots?: boolean
}

export const TypingIndicator: React.FC<TypingIndicatorProps> = ({ 
  streamingText, 
  showDots = true 
}) => {
  return (
    <div className="flex gap-3 mb-4">
      {/* Avatar */}
      <div className="w-8 h-8 rounded-full bg-glossy-gold flex items-center justify-center shadow-gold-glow flex-shrink-0">
        <span className="text-primary-dark font-bold text-sm">X</span>
      </div>
      
      {/* Content */}
      <div className="flex-1 flex flex-col items-start gap-1">
        <div className="glossy-card px-4 py-3 min-h-[50px] max-w-[85%] relative">
          {streamingText ? (
            <p className="whitespace-pre-wrap text-gray-100">
              {streamingText}
              <span className="inline-block w-0.5 h-[1em] bg-cyan-400 ml-0.5 animate-pulse" />
            </p>
          ) : showDots && (
            <div className="flex items-center gap-1">
              <div className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: '0s' }} />
              <div className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: '0.16s' }} />
              <div className="w-2 h-2 rounded-full bg-cyan-400 animate-bounce" style={{ animationDelay: '0.32s' }} />
            </div>
          )}
        </div>
        
        {streamingText && (
          <span className="text-xs text-gray-500">Streaming...</span>
        )}
      </div>
    </div>
  )
}