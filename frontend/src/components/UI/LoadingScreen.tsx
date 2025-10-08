import React from 'react'
import { Spinner } from './Spinner'
import { SkeletonLoader } from './SkeletonLoader'

interface LoadingScreenProps {
  message?: string
  type?: 'spinner' | 'skeleton'
  count?: number
}

export const LoadingScreen: React.FC<LoadingScreenProps> = ({
  message = 'Laden...',
  type = 'spinner',
  count = 3
}) => {
  if (type === 'skeleton') {
    return (
      <div className="w-full space-y-4 p-6" role="status" aria-label={message}>
        <SkeletonLoader height="h-12" count={count} />
        <span className="sr-only">{message}</span>
      </div>
    )
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-[200px] gap-4" role="status">
      <Spinner size="lg" />
      <p className="text-gray-400 text-sm">{message}</p>
    </div>
  )
}