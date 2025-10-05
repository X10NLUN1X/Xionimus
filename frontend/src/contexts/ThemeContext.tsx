import React, { createContext, useContext, useEffect, ReactNode } from 'react'
import { useColorMode } from '@chakra-ui/react'

/**
 * Simplified Theme Context - Dark Mode Only
 * Light mode and auto-mode have been removed
 */
interface ThemeContextType {
  effectiveTheme: 'dark'
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export const ThemeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { setColorMode } = useColorMode()

  // Force dark mode on mount
  useEffect(() => {
    setColorMode('dark')
    // Clean up old theme settings from localStorage
    localStorage.removeItem('xionimus-theme-mode')
  }, [setColorMode])

  return (
    <ThemeContext.Provider value={{ effectiveTheme: 'dark' }}>
      {children}
    </ThemeContext.Provider>
  )
}

export const useTheme = () => {
  const context = useContext(ThemeContext)
  if (!context) {
    throw new Error('useTheme must be used within ThemeProvider')
  }
  return context
}
