import React from 'react'
import { clsx } from 'clsx'

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost' | 'solid' | 'outline'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  isLoading?: boolean // Chakra API compatibility
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  colorScheme?: 'blue' | 'red' | 'green' | 'purple' | 'cyan' | 'gray' | 'gold'
  isDisabled?: boolean // Chakra API compatibility
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  loading = false,
  isLoading = false,
  leftIcon,
  rightIcon,
  colorScheme,
  className,
  disabled,
  isDisabled = false,
  ...props
}) => {
  const isButtonLoading = loading || isLoading
  const isButtonDisabled = disabled || isDisabled
  
  const baseClasses = 'inline-flex items-center justify-center font-semibold rounded-lg transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-gold-500 focus:ring-offset-2 focus:ring-offset-primary-dark disabled:opacity-50 disabled:cursor-not-allowed hover:scale-105 active:scale-95'
  
  // Color scheme classes
  const colorClasses: Record<string, string> = {
    blue: 'text-blue-400 hover:bg-blue-500/20 border border-blue-500/50',
    red: 'text-red-400 hover:bg-red-500/20 border border-red-500/50',
    green: 'text-green-400 hover:bg-green-500/20 border border-green-500/50',
    purple: 'text-purple-400 hover:bg-purple-500/20 border border-purple-500/50',
    cyan: 'text-cyan-400 hover:bg-cyan-500/20 border border-cyan-500/50',
    gray: 'text-gray-400 hover:bg-gray-500/20 border border-gray-500/50',
    gold: 'text-gold-400 hover:bg-gold-500/20 border border-gold-500/50'
  }
  
  const variantClasses = {
    primary: 'btn-gold',
    secondary: 'btn-dark',
    danger: 'bg-gradient-to-br from-red-600 to-red-800 text-white hover:shadow-lg',
    ghost: 'bg-transparent text-gold-400 hover:bg-gold-500/10 border border-transparent',
    solid: colorScheme ? colorClasses[colorScheme] : 'btn-gold',
    outline: 'bg-transparent border border-gold-500/50 text-gold-400 hover:bg-gold-500/10'
  }
  
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  }

  return (
    <button
      className={clsx(
        baseClasses,
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
      disabled={isButtonDisabled || isButtonLoading}
      {...props}
    >
      {isButtonLoading && (
        <svg className="animate-spin -ml-1 mr-3 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
      )}
      {!isButtonLoading && leftIcon && <span className="mr-2">{leftIcon}</span>}
      {children}
      {!isButtonLoading && rightIcon && <span className="ml-2">{rightIcon}</span>}
    </button>
  )
}