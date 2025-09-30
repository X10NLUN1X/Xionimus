import { useEffect, useCallback } from 'react'

export type ShortcutKey = 'n' | 'k' | '/' | 'e' | 'r' | 's' | 'l' | 'Escape'

interface ShortcutHandler {
  key: ShortcutKey
  ctrl?: boolean
  shift?: boolean
  alt?: boolean
  handler: () => void
  description: string
}

// Platform detection
const isMac = typeof navigator !== 'undefined' && navigator.platform.toUpperCase().indexOf('MAC') >= 0

export const getModifierKey = () => isMac ? '⌘' : 'Ctrl'

export const useKeyboardShortcuts = (shortcuts: ShortcutHandler[]) => {
  const handleKeyPress = useCallback((event: KeyboardEvent) => {
    // Don't trigger shortcuts when typing in input/textarea
    const target = event.target as HTMLElement
    if (
      target.tagName === 'INPUT' ||
      target.tagName === 'TEXTAREA' ||
      target.isContentEditable
    ) {
      // Allow Escape to blur inputs
      if (event.key !== 'Escape') {
        return
      }
    }

    const matchingShortcut = shortcuts.find(shortcut => {
      const keyMatches = event.key.toLowerCase() === shortcut.key.toLowerCase()
      const ctrlMatches = shortcut.ctrl ? (isMac ? event.metaKey : event.ctrlKey) : true
      const shiftMatches = shortcut.shift ? event.shiftKey : !event.shiftKey
      const altMatches = shortcut.alt ? event.altKey : !event.altKey

      return keyMatches && ctrlMatches && shiftMatches && altMatches
    })

    if (matchingShortcut) {
      event.preventDefault()
      matchingShortcut.handler()
    }
  }, [shortcuts])

  useEffect(() => {
    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [handleKeyPress])
}

// Helper to format shortcut for display
export const formatShortcut = (shortcut: Pick<ShortcutHandler, 'key' | 'ctrl' | 'shift' | 'alt'>): string => {
  const parts: string[] = []
  
  if (shortcut.ctrl) parts.push(getModifierKey())
  if (shortcut.shift) parts.push('⇧')
  if (shortcut.alt) parts.push(isMac ? '⌥' : 'Alt')
  
  const keyMap: Record<string, string> = {
    'Escape': 'Esc',
    '/': '/',
    'n': 'N',
    'k': 'K',
    'e': 'E',
    'r': 'R',
    's': 'S',
    'l': 'L'
  }
  
  parts.push(keyMap[shortcut.key] || shortcut.key.toUpperCase())
  
  return parts.join(' + ')
}
