import React, { useCallback, KeyboardEvent } from 'react'

interface ChatInputProps {
  value: string
  onChange: (value: string) => void
  onSubmit: () => void
  disabled?: boolean
  placeholder?: string
  onKeyDown?: (e: KeyboardEvent<HTMLTextAreaElement>) => void
}

/**
 * Isolated Chat Input Component
 * Prevents re-renders of entire ChatPage when user types
 * Memoized to only re-render when props change
 */
export const ChatInput = React.memo<ChatInputProps>(({ 
  value, 
  onChange, 
  onSubmit, 
  disabled = false,
  placeholder = 'Nachricht eingeben...',
  onKeyDown
}) => {
  const handleChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    onChange(e.target.value)
  }, [onChange])

  const handleKeyDown = useCallback((e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (onKeyDown) {
      onKeyDown(e)
    }
    
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      onSubmit()
    }
  }, [onKeyDown, onSubmit])

  return (
    <textarea
      value={value}
      onChange={handleChange}
      onKeyDown={handleKeyDown}
      disabled={disabled}
      placeholder={placeholder}
      rows={2}
      className={`
        w-full min-h-[60px] max-h-[200px]
        px-4 py-3 rounded-xl
        bg-primary-navy/50 backdrop-blur-md
        border border-gold-500/20
        text-white placeholder-gray-400
        text-[15px] leading-relaxed
        resize-none
        focus:outline-none focus:border-gold-500/60 focus:shadow-gold-glow
        disabled:opacity-50 disabled:cursor-not-allowed
        transition-all duration-300
        custom-scrollbar
        pointer-events-auto
      `}
      style={{
        lineHeight: '1.6',
        pointerEvents: 'auto'
      }}
    />
  )
}, (prevProps, nextProps) => {
  // Only re-render if value, disabled, or placeholder changes
  return (
    prevProps.value === nextProps.value &&
    prevProps.disabled === nextProps.disabled &&
    prevProps.placeholder === nextProps.placeholder
  )
})

ChatInput.displayName = 'ChatInput'