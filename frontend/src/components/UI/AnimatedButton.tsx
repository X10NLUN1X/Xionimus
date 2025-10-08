import React from 'react'
import { RippleEffect } from './RippleEffect'

interface AnimatedButtonProps {
  children: React.ReactNode
  onClick?: () => void
  variant?: 'primary' | 'secondary' | 'danger' | 'ghost'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  disabled?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
  className?: string
  ripple?: boolean
  glow?: boolean
}

export const AnimatedButton: React.FC<AnimatedButtonProps> = ({
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  leftIcon,
  rightIcon,
  className = '',
  ripple = true,
  glow = false
}) => {
  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg'
  }

  const variantClasses = {
    primary: 'btn-gold',
    secondary: 'btn-dark',
    danger: 'bg-gradient-to-br from-red-600 to-red-800 text-white',
    ghost: 'bg-transparent text-gold-400 hover:bg-gold-500/10 border border-gold-500/30'
  }

  const baseClasses = `
    inline-flex items-center justify-center gap-2
    font-semibold rounded-lg
    transition-all duration-300
    focus:outline-none focus:ring-2 focus:ring-gold-500 focus:ring-offset-2 focus:ring-offset-primary-dark
    disabled:opacity-50 disabled:cursor-not-allowed
    hover:scale-105 active:scale-95
    ${glow ? 'hover:shadow-gold-glow-lg' : ''}
  `

  const ButtonContent = (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      className={`
        ${baseClasses}
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        ${className}
      `}
    >
      {loading && (
        <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
      )}
      {!loading && leftIcon && <span>{leftIcon}</span>}
      {children}
      {!loading && rightIcon && <span>{rightIcon}</span>}
    </button>
  )

  if (ripple && !disabled && !loading) {
    return (
      <RippleEffect className="inline-block rounded-lg">
        {ButtonContent}
      </RippleEffect>
    )
  }

  return ButtonContent
}