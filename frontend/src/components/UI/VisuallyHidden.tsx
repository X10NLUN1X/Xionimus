import React from 'react'

interface VisuallyHiddenProps {
  children: React.ReactNode
}

/**
 * VisuallyHidden component hides content visually but keeps it accessible to screen readers
 * Used for improved accessibility without cluttering the UI
 */
export const VisuallyHidden: React.FC<VisuallyHiddenProps> = ({ children }) => {
  return (
    <span
      className="absolute w-px h-px p-0 -m-px overflow-hidden whitespace-nowrap border-0"
      style={{
        clip: 'rect(0, 0, 0, 0)',
        clipPath: 'inset(50%)'
      }}
    >
      {children}
    </span>
  )
}