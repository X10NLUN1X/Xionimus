import React from 'react'
import { clsx } from 'clsx'

interface BadgeProps {
  children: React.ReactNode
  variant?: 'success' | 'warning' | 'error' | 'info' | 'default'
  className?: string
}

export const Badge: React.FC<BadgeProps> = ({ 
  children, 
  variant = 'default',
  className 
}) => {
  const variantClasses = {
    success: 'bg-green-500/20 text-green-400 border-green-500/40',
    warning: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/40',
    error: 'bg-red-500/20 text-red-400 border-red-500/40',
    info: 'bg-blue-500/20 text-blue-400 border-blue-500/40',
    default: 'bg-gold-500/20 text-gold-400 border-gold-500/40',
  }

  return (
    <span
      className={clsx(
        'inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border',
        variantClasses[variant],
        className
      )}
    >
      {children}
    </span>
  )
}