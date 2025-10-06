import React from 'react'
import { Button } from './Button'

interface EmptyStateProps {
  icon?: React.ReactNode
  title: string
  description?: string
  action?: {
    label: string
    onClick: () => void
  }
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action
}) => {
  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] text-center p-8">
      {icon && (
        <div className="text-6xl mb-4 opacity-50 animate-bounce-in">
          {icon}
        </div>
      )}
      <h3 className="text-xl font-bold text-gray-200 mb-2 animate-fade-in-up">
        {title}
      </h3>
      {description && (
        <p className="text-gray-400 mb-6 max-w-md animate-fade-in-up animation-delay-100">
          {description}
        </p>
      )}
      {action && (
        <Button
          variant="primary"
          onClick={action.onClick}
          className="animate-fade-in-up animation-delay-200"
        >
          {action.label}
        </Button>
      )}
    </div>
  )
}