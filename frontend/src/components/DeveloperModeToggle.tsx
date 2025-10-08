import React, { useState } from 'react'

interface DeveloperModeToggleProps {
  mode: 'junior' | 'senior'
  onChange: (mode: 'junior' | 'senior') => void
}

export const DeveloperModeToggle: React.FC<DeveloperModeToggleProps> = ({
  mode,
  onChange
}) => {
  const [showTooltip, setShowTooltip] = useState<'junior' | 'senior' | null>(null)

  return (
    <div className="flex items-center gap-1 sm:gap-2">
      {/* Junior Mode Button - Responsive */}
      <div className="relative">
        <button
          onClick={() => onChange('junior')}
          onMouseEnter={() => setShowTooltip('junior')}
          onMouseLeave={() => setShowTooltip(null)}
          aria-label="Junior Developer Mode"
          className={`
            px-2 sm:px-4 py-2 rounded-full font-semibold text-sm
            border-2 transition-all duration-200
            flex items-center gap-1 sm:gap-2
            min-w-[44px] min-h-[44px]
            ${mode === 'junior'
              ? 'bg-green-500/20 border-green-500 text-green-400 shadow-lg shadow-green-500/30'
              : 'bg-transparent border-green-500/50 text-green-400/70 hover:bg-green-500/10 hover:border-green-500'
            }
            hover:scale-105 active:scale-95
          `}
        >
          <span className="text-base">🌱</span>
          <span className="hidden sm:inline">Junior</span>
        </button>
        
        {/* Tooltip */}
        {showTooltip === 'junior' && (
          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-50 animate-fade-in pointer-events-none">
            <div className="glossy-card max-w-xs p-3 text-xs text-gray-300 border-green-500/30 whitespace-nowrap sm:whitespace-normal">
              <p className="font-semibold text-green-400 mb-1">🌱 Junior Developer</p>
              <p className="hidden sm:block">Fast & Budget-Friendly (Claude Haiku) - 73% cheaper, perfect for learning and simple tasks</p>
              <p className="sm:hidden">Fast & Budget-Friendly</p>
            </div>
          </div>
        )}
      </div>

      {/* Senior Mode Button - Responsive */}
      <div className="relative">
        <button
          onClick={() => onChange('senior')}
          onMouseEnter={() => setShowTooltip('senior')}
          onMouseLeave={() => setShowTooltip(null)}
          aria-label="Senior Developer Mode"
          className={`
            px-2 sm:px-4 py-2 rounded-full font-semibold text-sm
            border-2 transition-all duration-200
            flex items-center gap-1 sm:gap-2
            min-w-[44px] min-h-[44px]
            ${mode === 'senior'
              ? 'bg-blue-500/20 border-blue-500 text-blue-400 shadow-lg shadow-blue-500/30'
              : 'bg-transparent border-blue-500/50 text-blue-400/70 hover:bg-blue-500/10 hover:border-blue-500'
            }
            hover:scale-105 active:scale-95
          `}
        >
          <span className="text-base">🚀</span>
          <span className="hidden sm:inline">Senior</span>
        </button>
        
        {/* Tooltip */}
        {showTooltip === 'senior' && (
          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 z-50 animate-fade-in pointer-events-none">
            <div className="glossy-card max-w-xs p-3 text-xs text-gray-300 border-blue-500/30 whitespace-nowrap sm:whitespace-normal">
              <p className="font-semibold text-blue-400 mb-1">🚀 Senior Developer</p>
              <p className="hidden sm:block">Premium Quality (Claude Sonnet 4.5 + Opus 4.1) - Best for production code, complex debugging, and architecture</p>
              <p className="sm:hidden">Premium Quality</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}