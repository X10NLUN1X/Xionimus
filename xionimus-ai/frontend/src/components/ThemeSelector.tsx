import React from 'react'
import {
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  IconButton,
  HStack,
  Text,
  useColorModeValue
} from '@chakra-ui/react'
import { SunIcon, MoonIcon, SettingsIcon } from '@chakra-ui/icons'
import { useTheme } from '../contexts/ThemeContext'
import { useLanguage } from '../contexts/LanguageContext'

export const ThemeSelector: React.FC = () => {
  const { themeMode, setThemeMode, effectiveTheme } = useTheme()
  const { t } = useLanguage()

  const getCurrentIcon = () => {
    if (themeMode === 'auto') {
      return <SettingsIcon />
    }
    return effectiveTheme === 'dark' ? <MoonIcon /> : <SunIcon />
  }

  const modes: Array<{ value: 'light' | 'dark' | 'auto'; icon: JSX.Element; label: string }> = [
    { value: 'light', icon: <SunIcon />, label: t('settings.lightMode') },
    { value: 'dark', icon: <MoonIcon />, label: t('settings.darkMode') },
    { value: 'auto', icon: <SettingsIcon />, label: 'Auto' }
  ]

  return (
    <Menu>
      <MenuButton
        as={IconButton}
        icon={getCurrentIcon()}
        variant="ghost"
        aria-label="Theme selector"
        size="sm"
      />
      <MenuList>
        {modes.map(mode => (
          <MenuItem
            key={mode.value}
            onClick={() => setThemeMode(mode.value)}
            bg={themeMode === mode.value ? 'rgba(0, 212, 255, 0.1)' : undefined}
            _hover={{ bg: 'rgba(0, 212, 255, 0.2)' }}
          >
            <HStack spacing={3}>
              {mode.icon}
              <Text>{mode.label}</Text>
              {themeMode === mode.value && (
                <Text fontSize="xs" color="cyan.400">✓</Text>
              )}
            </HStack>
          </MenuItem>
        ))}
      </MenuList>
    </Menu>
  )
}
