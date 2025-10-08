import React, { useState, useCallback } from 'react'

interface Ripple {
  x: number
  y: number
  id: number
}

interface RippleEffectProps {
  children: React.ReactNode
  color?: string
  duration?: number
  className?: string
}

export const RippleEffect: React.FC<RippleEffectProps> = ({
  children,
  color = 'rgba(212, 175, 55, 0.4)',
  duration = 600,
  className = ''
}) => {
  const [ripples, setRipples] = useState<Ripple[]>([])

  const addRipple = useCallback((event: React.MouseEvent<HTMLDivElement>) => {
    const rippleContainer = event.currentTarget.getBoundingClientRect()
    const size = rippleContainer.width > rippleContainer.height 
      ? rippleContainer.width 
      : rippleContainer.height
    
    const x = event.clientX - rippleContainer.left - size / 2
    const y = event.clientY - rippleContainer.top - size / 2
    
    const newRipple: Ripple = {
      x,
      y,
      id: Date.now()
    }

    setRipples((prevRipples) => [...prevRipples, newRipple])

    setTimeout(() => {
      setRipples((prevRipples) =>
        prevRipples.filter((ripple) => ripple.id !== newRipple.id)
      )
    }, duration)
  }, [duration])

  return (
    <div
      className={`relative overflow-hidden ${className}`}
      onMouseDown={addRipple}
    >
      {children}
      {ripples.map((ripple) => (
        <span
          key={ripple.id}
          className="absolute rounded-full animate-ripple pointer-events-none"
          style={{
            left: ripple.x,
            top: ripple.y,
            width: '100px',
            height: '100px',
            background: color,
          }}
        />
      ))}
    </div>
  )
}