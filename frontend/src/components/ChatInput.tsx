import React, { useCallback, KeyboardEvent } from 'react'
import { Textarea, Box } from '@chakra-ui/react'

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
    <Textarea
      value={value}
      onChange={handleChange}
      onKeyDown={handleKeyDown}
      disabled={disabled}
      placeholder={placeholder}
      resize="none"
      minH="60px"
      maxH="200px"
      rows={2}
      fontSize="15px"
      lineHeight="1.6"
      _focus={{
        borderColor: '#0088cc',
        boxShadow: '0 0 0 1px #0088cc',
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
