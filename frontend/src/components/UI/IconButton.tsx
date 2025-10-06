import React from 'react'

interface IconButtonProps {
  'aria-label': string
  icon: React.ReactNode
  onClick?: () => void
  variant?: 'ghost' | 'solid' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  colorScheme?: 'blue' | 'red' | 'green' | 'purple' | 'cyan' | 'gray'
  isDisabled?: boolean
  isLoading?: boolean
  className?: string
}

export const IconButton: React.FC<IconButtonProps> = ({
  'aria-label': ariaLabel,
  icon,
  onClick,
  variant = 'ghost',
  size = 'md',
  colorScheme = 'blue',
  isDisabled = false,
  isLoading = false,
  className = ''
}) => {
  const sizeClasses = {
    sm: 'p-1.5 text-sm',
    md: 'p-2 text-base',
    lg: 'p-3 text-lg'
  }

  const colorClasses = {
    blue: 'text-blue-400 hover:bg-blue-500/20 hover:border-blue-500/50',
    red: 'text-red-400 hover:bg-red-500/20 hover:border-red-500/50',
    green: 'text-green-400 hover:bg-green-500/20 hover:border-green-500/50',
    purple: 'text-purple-400 hover:bg-purple-500/20 hover:border-purple-500/50',
    cyan: 'text-cyan-400 hover:bg-cyan-500/20 hover:border-cyan-500/50',
    gray: 'text-gray-400 hover:bg-gray-500/20 hover:border-gray-500/50'
  }

  const variantClasses = {
    ghost: 'bg-transparent border border-transparent',
    solid: 'bg-gold-500/20 border border-gold-500/50',
    outline: 'bg-transparent border border-gold-500/50'
  }

  return (
    <button
      aria-label={ariaLabel}
      onClick={onClick}
      disabled={isDisabled || isLoading}
      className={`
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${colorClasses[colorScheme]}
        rounded-lg
        transition-all duration-200
        hover:scale-105 active:scale-95
        disabled:opacity-50 disabled:cursor-not-allowed
        flex items-center justify-center
        ${className}
      `}
    >
      {isLoading ? (
        <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      ) : (
        icon
      )}
    </button>
  )
}