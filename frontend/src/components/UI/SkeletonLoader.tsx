import React from 'react'

interface SkeletonLoaderProps {
  width?: string
  height?: string
  className?: string
  count?: number
  circle?: boolean
}

export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  width = 'w-full',
  height = 'h-4',
  className = '',
  count = 1,
  circle = false
}) => {
  const skeletons = Array.from({ length: count }, (_, i) => i)

  const shimmerClasses = `
    ${circle ? 'rounded-full' : 'rounded-lg'}
    ${width} ${height}
    bg-gradient-to-r from-gray-800 via-gray-700 to-gray-800
    bg-[length:1000px_100%]
    animate-shimmer
    ${className}
  `

  return (
    <>
      {skeletons.map((index) => (
        <div
          key={index}
          className={shimmerClasses}
          style={{
            animationDelay: `${index * 0.1}s`
          }}
        />
      ))}
    </>
  )
}