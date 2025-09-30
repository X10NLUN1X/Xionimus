import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useColorMode, useColorModeValue } from '@chakra-ui/react'

type ThemeMode = 'light' | 'dark' | 'auto'

interface ThemeContextType {
  themeMode: ThemeMode
  setThemeMode: (mode: ThemeMode) => void
  effectiveTheme: 'light' | 'dark'
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export const ThemeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const { colorMode, setColorMode } = useColorMode()
  const [themeMode, setThemeModeState] = useState<ThemeMode>(() => {
    const saved = localStorage.getItem('xionimus-theme-mode')
    return (saved === 'light' || saved === 'dark' || saved === 'auto') ? saved : 'dark'
  })

  // Detect system theme
  const getSystemTheme = (): 'light' | 'dark' => {
    if (typeof window !== 'undefined' && window.matchMedia) {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }
    return 'dark'
  }

  // Calculate effective theme
  const effectiveTheme: 'light' | 'dark' = themeMode === 'auto' ? getSystemTheme() : themeMode

  // Update Chakra UI color mode when effective theme changes
  useEffect(() => {
    if (effectiveTheme !== colorMode) {
      setColorMode(effectiveTheme)
    }
  }, [effectiveTheme, colorMode, setColorMode])

  // Listen to system theme changes when in auto mode
  useEffect(() => {
    if (themeMode !== 'auto') return

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handleChange = () => {
      const newTheme = getSystemTheme()
      if (newTheme !== colorMode) {
        setColorMode(newTheme)
      }
    }

    mediaQuery.addEventListener('change', handleChange)
    return () => mediaQuery.removeEventListener('change', handleChange)
  }, [themeMode, colorMode, setColorMode])

  const setThemeMode = (mode: ThemeMode) => {
    setThemeModeState(mode)
    localStorage.setItem('xionimus-theme-mode', mode)
  }

  return (
    <ThemeContext.Provider value={{ themeMode, setThemeMode, effectiveTheme }}>
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
