import React, { useState, useRef, useEffect } from 'react'

interface PopoverProps {
  placement?: 'top' | 'bottom' | 'left' | 'right' | 'bottom-end'
  children: React.ReactNode
}

interface PopoverTriggerProps {
  children: React.ReactElement
}

interface PopoverContentProps {
  children: React.ReactNode
}

const PopoverContext = React.createContext<{
  isOpen: boolean
  setIsOpen: (open: boolean) => void
}>({ isOpen: false, setIsOpen: () => {} })

export const Popover: React.FC<PopoverProps> = ({ placement = 'bottom', children }) => {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <PopoverContext.Provider value={{ isOpen, setIsOpen }}>
      <div className="relative inline-block">
        {React.Children.map(children, child => 
          React.isValidElement(child) ? React.cloneElement(child, { placement } as any) : child
        )}
      </div>
    </PopoverContext.Provider>
  )
}

export const PopoverTrigger: React.FC<PopoverTriggerProps> = ({ children }) => {
  const { isOpen, setIsOpen } = React.useContext(PopoverContext)

  return React.cloneElement(children, {
    onClick: (e: React.MouseEvent) => {
      e.stopPropagation()
      setIsOpen(!isOpen)
      children.props.onClick?.(e)
    }
  })
}

export const PopoverContent: React.FC<PopoverContentProps & { placement?: string }> = ({ 
  children,
  placement = 'bottom'
}) => {
  const { isOpen, setIsOpen } = React.useContext(PopoverContext)
  const contentRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (contentRef.current && !contentRef.current.contains(event.target as Node)) {
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

  const placementClasses: Record<string, string> = {
    'top': 'bottom-full left-1/2 -translate-x-1/2 mb-2',
    'bottom': 'top-full left-1/2 -translate-x-1/2 mt-2',
    'bottom-end': 'top-full right-0 mt-2',
    'left': 'right-full top-1/2 -translate-y-1/2 mr-2',
    'right': 'left-full top-1/2 -translate-y-1/2 ml-2'
  }

  return (
    <div 
      ref={contentRef}
      className={`absolute z-50 glossy-card border-gold-500/30 shadow-xl min-w-[250px] animate-fade-in ${placementClasses[placement] || placementClasses.bottom}`}
    >
      {children}
    </div>
  )
}