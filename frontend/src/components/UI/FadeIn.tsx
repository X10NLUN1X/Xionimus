import React from 'react'

interface FadeInProps {
  children: React.ReactNode
  delay?: number
  direction?: 'up' | 'down' | 'left' | 'right' | 'none'
  duration?: number
  className?: string
}

export const FadeIn: React.FC<FadeInProps> = ({
  children,
  delay = 0,
  direction = 'up',
  duration = 0.6,
  className = ''
}) => {
  const animationClasses = {
    up: 'animate-fade-in-up',
    down: 'animate-fade-in-down',
    left: 'animate-slide-in-left',
    right: 'animate-slide-in-right',
    none: 'animate-fade-in'
  }

  return (
    <div
      className={`${animationClasses[direction]} ${className}`}
      style={{
        animationDelay: `${delay}s`,
        animationDuration: `${duration}s`,
        animationFillMode: 'both'
      }}
    >
      {children}
    </div>
  )
}