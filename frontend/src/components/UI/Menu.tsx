import React, { useState, useRef, useEffect } from 'react'

interface MenuProps {
  children: React.ReactNode
}

interface MenuButtonProps {
  children: React.ReactNode
  as?: React.ElementType
  size?: 'sm' | 'md' | 'lg'
  variant?: 'ghost' | 'solid' | 'outline'
  colorScheme?: string
  rightIcon?: React.ReactNode
  className?: string
}

interface MenuListProps {
  children: React.ReactNode
}

interface MenuItemProps {
  icon?: React.ReactNode
  onClick?: () => void
  children: React.ReactNode
}

const MenuContext = React.createContext<{
  isOpen: boolean
  setIsOpen: (open: boolean) => void
}>({ isOpen: false, setIsOpen: () => {} })

export const Menu: React.FC<MenuProps> = ({ children }) => {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <MenuContext.Provider value={{ isOpen, setIsOpen }}>
      <div className="relative inline-block">
        {children}
      </div>
    </MenuContext.Provider>
  )
}

export const MenuButton: React.FC<MenuButtonProps> = ({ 
  children, 
  as: Component = 'button',
  size = 'sm',
  variant = 'ghost',
  colorScheme = 'purple',
  rightIcon,
  className = ''
}) => {
  const { isOpen, setIsOpen } = React.useContext(MenuContext)

  const sizeClasses = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-5 py-2.5 text-lg'
  }

  const colorSchemeMap: Record<string, string> = {
    purple: 'text-purple-400 hover:bg-purple-500/20',
    blue: 'text-blue-400 hover:bg-blue-500/20',
    cyan: 'text-cyan-400 hover:bg-cyan-500/20'
  }

  return (
    <Component
      onClick={() => setIsOpen(!isOpen)}
      className={`
        ${sizeClasses[size]}
        ${colorSchemeMap[colorScheme] || colorSchemeMap.purple}
        rounded-lg
        transition-all duration-200
        hover:scale-105 active:scale-95
        flex items-center gap-2
        ${className}
      `}
    >
      {children}
      {rightIcon}
    </Component>
  )
}

export const MenuList: React.FC<MenuListProps> = ({ children }) => {
  const { isOpen, setIsOpen } = React.useContext(MenuContext)
  const menuRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false)
      }
    }

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside)
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [isOpen, setIsOpen])

  if (!isOpen) return null

  return (
    <div 
      ref={menuRef}
      className="absolute top-full left-0 mt-2 min-w-[200px] glossy-card border-gold-500/30 shadow-xl z-50 animate-fade-in"
    >
      <div className="py-1">
        {children}
      </div>
    </div>
  )
}

export const MenuItem: React.FC<MenuItemProps> = ({ icon, onClick, children }) => {
  const { setIsOpen } = React.useContext(MenuContext)

  const handleClick = () => {
    onClick?.()
    setIsOpen(false)
  }

  return (
    <button
      onClick={handleClick}
      className="w-full px-4 py-2 text-left text-gray-300 hover:bg-gold-500/10 hover:text-gold-400 transition-colors duration-200 flex items-center gap-3"
    >
      {icon}
      {children}
    </button>
  )
}