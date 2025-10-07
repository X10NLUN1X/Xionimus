import React from 'react'

/**
 * Simplified Theme Indicator - Dark Mode Only
 * This component now just shows that dark mode is active
 * Glossy black-gold theme is always enabled
 */
export const ThemeSelector: React.FC = () => {
  return (
    <div className="group relative pointer-events-auto" style={{ pointerEvents: 'auto' }}>
      <div className="flex items-center gap-1 px-2 py-1 rounded-md bg-purple-500/20 border border-purple-500/30 pointer-events-auto" style={{ pointerEvents: 'auto' }}>
        <svg className="w-3 h-3 text-purple-400" fill="currentColor" viewBox="0 0 20 20">
          <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
        </svg>
        <span className="text-xs font-medium text-purple-400">Dark</span>
      </div>
      
      {/* Tooltip */}
      <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-50 animate-fade-in pointer-events-auto" style={{ pointerEvents: 'auto' }}>
        <div className="glossy-card px-2 py-1 text-xs text-gray-300 whitespace-nowrap">
          Dark Mode (immer aktiv)
        </div>
      </div>
    </div>
  )
}