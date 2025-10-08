import React from 'react'

interface SwitchProps {
  isChecked: boolean
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void
  size?: 'sm' | 'md' | 'lg'
  colorScheme?: 'blue' | 'green' | 'purple' | 'cyan'
  className?: string
}

export const Switch: React.FC<SwitchProps> = ({ 
  isChecked, 
  onChange,
  size = 'md',
  colorScheme = 'cyan',
  className = ''
}) => {
  const sizeClasses = {
    sm: 'w-8 h-4',
    md: 'w-11 h-6',
    lg: 'w-14 h-7'
  }

  const thumbSizeClasses = {
    sm: 'w-3 h-3',
    md: 'w-5 h-5',
    lg: 'w-6 h-6'
  }

  const colorSchemes = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
    cyan: 'bg-cyan-500'
  }

  return (
    <label className={`relative inline-block ${className}`}>
      <input
        type="checkbox"
        checked={isChecked}
        onChange={onChange}
        className="sr-only peer"
      />
      <div 
        className={`
          ${sizeClasses[size]}
          ${isChecked ? colorSchemes[colorScheme] : 'bg-gray-600'}
          rounded-full
          transition-all duration-300
          cursor-pointer
          peer-focus:ring-4 peer-focus:ring-${colorScheme}-500/20
          shadow-lg
        `}
      >
        <div 
          className={`
            ${thumbSizeClasses[size]}
            bg-white
            rounded-full
            shadow-md
            transition-transform duration-300
            absolute top-1/2 -translate-y-1/2
            ${isChecked ? 'translate-x-[calc(100%+0.25rem)]' : 'translate-x-1'}
          `}
        />
      </div>
    </label>
  )
}