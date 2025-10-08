import React from 'react'

interface AvatarProps {
  size?: 'sm' | 'md' | 'lg'
  name?: string
  bg?: string
  src?: string
  className?: string
}

export const Avatar: React.FC<AvatarProps> = ({ 
  size = 'md', 
  name = 'User', 
  bg = 'linear-gradient(135deg, #d4af37, #f4d03f)',
  src,
  className = ''
}) => {
  const sizeClasses = {
    sm: 'w-8 h-8 text-xs',
    md: 'w-10 h-10 text-sm',
    lg: 'w-12 h-12 text-base'
  }

  const getInitials = (name: string) => {
    return name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  return (
    <div 
      className={`${sizeClasses[size]} rounded-full flex items-center justify-center font-bold text-white shadow-lg border-2 border-gold-500/30 ${className}`}
      style={{ background: bg }}
    >
      {src ? (
        <img src={src} alt={name} className="w-full h-full rounded-full object-cover" />
      ) : (
        <span>{getInitials(name)}</span>
      )}
    </div>
  )
}