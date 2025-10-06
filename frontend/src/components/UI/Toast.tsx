import React, { createContext, useContext, useState, useCallback } from 'react'
import { clsx } from 'clsx'

interface Toast {
  id: string
  title: string
  description?: string
  status: 'success' | 'error' | 'warning' | 'info'
  duration?: number
}

interface ToastContextType {
  showToast: (toast: Omit<Toast, 'id'>) => void
}

const ToastContext = createContext<ToastContextType | undefined>(undefined)

export const useToast = () => {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within ToastProvider')
  }
  return context
}

export const ToastProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [toasts, setToasts] = useState<Toast[]>([])

  const showToast = useCallback((toast: Omit<Toast, 'id'>) => {
    const id = Math.random().toString(36).substr(2, 9)
    const newToast = { ...toast, id }
    setToasts((prev) => [...prev, newToast])

    setTimeout(() => {
      setToasts((prev) => prev.filter((t) => t.id !== id))
    }, toast.duration || 5000)
  }, [])

  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ',
  }

  const statusClasses = {
    success: 'border-green-500/50 bg-green-500/10',
    error: 'border-red-500/50 bg-red-500/10',
    warning: 'border-yellow-500/50 bg-yellow-500/10',
    info: 'border-blue-500/50 bg-blue-500/10',
  }

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            className={clsx(
              'glossy-card p-4 min-w-[300px] animate-slide-in',
              statusClasses[toast.status]
            )}
          >
            <div className="flex items-start">
              <span className="text-2xl mr-3">{icons[toast.status]}</span>
              <div className="flex-1">
                <h4 className="font-semibold text-white">{toast.title}</h4>
                {toast.description && (
                  <p className="text-sm text-gray-300 mt-1">{toast.description}</p>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}