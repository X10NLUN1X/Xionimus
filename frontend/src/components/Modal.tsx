import React, { useEffect } from 'react'
import { createPortal } from 'react-dom'

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  children: React.ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl' | '2xl'
}

export const Modal: React.FC<ModalProps> = ({ 
  isOpen, 
  onClose, 
  children,
  size = 'md'
}) => {
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = 'unset'
    }
    return () => {
      document.body.style.overflow = 'unset'
    }
  }, [isOpen])

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose()
      }
    }
    window.addEventListener('keydown', handleEscape)
    return () => window.removeEventListener('keydown', handleEscape)
  }, [isOpen, onClose])

  if (!isOpen) return null

  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    '2xl': 'max-w-6xl'
  }

  return createPortal(
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 animate-fade-in"
      onClick={onClose}
    >
      {/* Overlay */}
      <div className="absolute inset-0 bg-black/70 backdrop-blur-sm" />
      
      {/* Modal Content */}
      <div 
        className={`relative w-full ${sizeClasses[size]} animate-slide-in`}
        onClick={(e) => e.stopPropagation()}
      >
        {children}
      </div>
    </div>,
    document.body
  )
}

interface ModalContentProps {
  children: React.ReactNode
  className?: string
}

export const ModalContent: React.FC<ModalContentProps> = ({ children, className = '' }) => {
  return (
    <div className={`glossy-card overflow-hidden ${className}`}>
      {children}
    </div>
  )
}

interface ModalHeaderProps {
  children: React.ReactNode
  onClose?: () => void
}

export const ModalHeader: React.FC<ModalHeaderProps> = ({ children, onClose }) => {
  return (
    <div className="flex items-center justify-between p-6 border-b border-gold-500/20">
      <h2 className="text-xl font-bold text-white">{children}</h2>
      {onClose && (
        <button
          onClick={onClose}
          className="p-2 hover:bg-accent-blue rounded-lg transition-colors"
          aria-label="Close modal"
        >
          <svg className="w-5 h-5 text-gray-400 hover:text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
    </div>
  )
}

interface ModalBodyProps {
  children: React.ReactNode
  className?: string
}

export const ModalBody: React.FC<ModalBodyProps> = ({ children, className = '' }) => {
  return (
    <div className={`p-6 max-h-[70vh] overflow-y-auto custom-scrollbar ${className}`}>
      {children}
    </div>
  )
}

interface ModalFooterProps {
  children: React.ReactNode
  className?: string
}

export const ModalFooter: React.FC<ModalFooterProps> = ({ children, className = '' }) => {
  return (
    <div className={`flex items-center justify-end gap-3 p-6 border-t border-gold-500/20 ${className}`}>
      {children}
    </div>
  )
}
