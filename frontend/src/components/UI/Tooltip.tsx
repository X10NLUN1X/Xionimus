import React, { useState } from 'react'

interface TooltipProps {
  label: string
  placement?: 'top' | 'bottom' | 'left' | 'right'
  children: React.ReactElement
  bg?: string
  color?: string
}

export const Tooltip: React.FC<TooltipProps> = ({ 
  label, 
  placement = 'top',
  children,
  bg = 'rgba(0, 0, 0, 0.9)',
  color = 'white'
}) => {
  const [isVisible, setIsVisible] = useState(false)

  const placementClasses = {
    top: 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    bottom: 'top-full left-1/2 -translate-x-1/2 mt-2',
    left: 'right-full top-1/2 -translate-y-1/2 mr-2',
    right: 'left-full top-1/2 -translate-y-1/2 ml-2'
  }

  return (
    <div 
      className="relative inline-block"
      onMouseEnter={() => setIsVisible(true)}
      onMouseLeave={() => setIsVisible(false)}
    >
      {children}
      {isVisible && (
        <div 
          className={`absolute z-50 px-3 py-2 text-sm rounded-lg shadow-lg backdrop-blur-sm border border-gold-500/20 whitespace-nowrap animate-fade-in ${placementClasses[placement]}`}
          style={{ background: bg, color }}
        >
          {label}
        </div>
      )}
    </div>
  )
}