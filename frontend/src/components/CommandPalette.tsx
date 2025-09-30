import React, { useState, useEffect, useRef } from 'react'
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalBody,
  Input,
  VStack,
  HStack,
  Text,
  Box,
  useColorModeValue,
  Badge,
  Kbd
} from '@chakra-ui/react'
import {
  AddIcon,
  SearchIcon,
  SettingsIcon,
  MoonIcon,
  SunIcon,
  ChatIcon,
  EditIcon,
  RepeatIcon,
  DeleteIcon
} from '@chakra-ui/icons'
import { useNavigate } from 'react-router-dom'
import { useApp } from '../contexts/AppContext'
import { useTheme } from '../contexts/ThemeContext'
import { useLanguage } from '../contexts/LanguageContext'
import { formatShortcut } from '../hooks/useKeyboardShortcuts'

interface Command {
  id: string
  label: string
  description?: string
  icon: JSX.Element
  shortcut?: string
  action: () => void
  category?: string
}

interface CommandPaletteProps {
  isOpen: boolean
  onClose: () => void
}

export const CommandPalette: React.FC<CommandPaletteProps> = ({ isOpen, onClose }) => {
  const [search, setSearch] = useState('')
  const [selectedIndex, setSelectedIndex] = useState(0)
  const inputRef = useRef<HTMLInputElement>(null)
  const navigate = useNavigate()
  const { createNewSession, messages } = useApp()
  const { themeMode, setThemeMode } = useTheme()
  const { language, setLanguage, t } = useLanguage()

  const bgColor = useColorModeValue('white', 'rgba(10, 22, 40, 0.98)')
  const borderColor = useColorModeValue('gray.200', 'rgba(0, 212, 255, 0.3)')
  const itemHoverBg = useColorModeValue('gray.100', 'rgba(0, 212, 255, 0.1)')
  const itemSelectedBg = useColorModeValue('blue.50', 'rgba(0, 212, 255, 0.2)')

  const commands: Command[] = [
    {
      id: 'new-chat',
      label: t('header.newChat'),
      description: 'Start a new conversation',
      icon: <AddIcon />,
      shortcut: formatShortcut({ key: 'n', ctrl: true }),
      action: () => {
        createNewSession()
        onClose()
      },
      category: 'Chat'
    },
    {
      id: 'settings',
      label: t('header.settings'),
      description: 'Open settings',
      icon: <SettingsIcon />,
      action: () => {
        navigate('/settings')
        onClose()
      },
      category: 'Navigation'
    },
    {
      id: 'toggle-theme-dark',
      label: 'Dark Mode',
      description: 'Switch to dark theme',
      icon: <MoonIcon />,
      action: () => {
        setThemeMode('dark')
        onClose()
      },
      category: 'Theme'
    },
    {
      id: 'toggle-theme-light',
      label: 'Light Mode',
      description: 'Switch to light theme',
      icon: <SunIcon />,
      action: () => {
        setThemeMode('light')
        onClose()
      },
      category: 'Theme'
    },
    {
      id: 'toggle-theme-auto',
      label: 'Auto Theme',
      description: 'Follow system theme',
      icon: <SettingsIcon />,
      action: () => {
        setThemeMode('auto')
        onClose()
      },
      category: 'Theme'
    },
    {
      id: 'language-en',
      label: 'English',
      description: 'Switch to English',
      icon: <Text fontSize="lg">🇬🇧</Text>,
      action: () => {
        setLanguage('en')
        onClose()
      },
      category: 'Language'
    },
    {
      id: 'language-de',
      label: 'Deutsch',
      description: 'Switch to German',
      icon: <Text fontSize="lg">🇩🇪</Text>,
      action: () => {
        setLanguage('de')
        onClose()
      },
      category: 'Language'
    },
    {
      id: 'chat-page',
      label: 'Go to Chat',
      description: 'Navigate to chat page',
      icon: <ChatIcon />,
      action: () => {
        navigate('/chat')
        onClose()
      },
      category: 'Navigation'
    }
  ]

  // Filter commands based on search
  const filteredCommands = commands.filter(cmd =>
    cmd.label.toLowerCase().includes(search.toLowerCase()) ||
    cmd.description?.toLowerCase().includes(search.toLowerCase()) ||
    cmd.category?.toLowerCase().includes(search.toLowerCase())
  )

  // Reset selection when search changes
  useEffect(() => {
    setSelectedIndex(0)
  }, [search])

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setSearch('')
      setSelectedIndex(0)
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }, [isOpen])

  // Handle keyboard navigation
  useEffect(() => {
    if (!isOpen) return

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedIndex(prev => Math.min(prev + 1, filteredCommands.length - 1))
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedIndex(prev => Math.max(prev - 1, 0))
      } else if (e.key === 'Enter') {
        e.preventDefault()
        if (filteredCommands[selectedIndex]) {
          filteredCommands[selectedIndex].action()
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, filteredCommands, selectedIndex])

  // Group commands by category
  const groupedCommands = filteredCommands.reduce((acc, cmd) => {
    const category = cmd.category || 'Other'
    if (!acc[category]) acc[category] = []
    acc[category].push(cmd)
    return acc
  }, {} as Record<string, Command[]>)

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl" isCentered>
      <ModalOverlay bg="blackAlpha.700" backdropFilter="blur(10px)" />
      <ModalContent
        bg={bgColor}
        border="1px solid"
        borderColor={borderColor}
        boxShadow="0 20px 60px rgba(0, 212, 255, 0.3)"
        maxH="600px"
      >
        <ModalBody p={0}>
          <VStack spacing={0} align="stretch">
            {/* Search Input */}
            <HStack p={4} borderBottom="1px solid" borderColor={borderColor}>
              <SearchIcon color="gray.500" />
              <Input
                ref={inputRef}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Type a command or search..."
                variant="unstyled"
                fontSize="lg"
                _placeholder={{ color: 'gray.500' }}
              />
              <Badge colorScheme="cyan" fontSize="xs">
                <Kbd>Esc</Kbd> to close
              </Badge>
            </HStack>

            {/* Commands List */}
            <Box maxH="400px" overflowY="auto">
              {Object.entries(groupedCommands).map(([category, cmds]) => (
                <Box key={category}>
                  {/* Category Header */}
                  <Text
                    px={4}
                    py={2}
                    fontSize="xs"
                    fontWeight="bold"
                    color="gray.500"
                    textTransform="uppercase"
                    letterSpacing="wide"
                  >
                    {category}
                  </Text>

                  {/* Commands in Category */}
                  {cmds.map((cmd, idx) => {
                    const globalIndex = filteredCommands.indexOf(cmd)
                    const isSelected = globalIndex === selectedIndex

                    return (
                      <HStack
                        key={cmd.id}
                        px={4}
                        py={3}
                        cursor="pointer"
                        bg={isSelected ? itemSelectedBg : 'transparent'}
                        _hover={{ bg: itemHoverBg }}
                        onClick={cmd.action}
                        borderLeft="3px solid"
                        borderLeftColor={isSelected ? 'cyan.400' : 'transparent'}
                        transition="all 0.15s"
                      >
                        <Box color={isSelected ? 'cyan.400' : 'gray.400'}>
                          {cmd.icon}
                        </Box>
                        <VStack flex={1} align="start" spacing={0}>
                          <Text fontWeight={isSelected ? '600' : '400'}>
                            {cmd.label}
                          </Text>
                          {cmd.description && (
                            <Text fontSize="xs" color="gray.500">
                              {cmd.description}
                            </Text>
                          )}
                        </VStack>
                        {cmd.shortcut && (
                          <Badge
                            variant="subtle"
                            colorScheme="gray"
                            fontSize="xs"
                          >
                            {cmd.shortcut}
                          </Badge>
                        )}
                      </HStack>
                    )
                  })}
                </Box>
              ))}

              {filteredCommands.length === 0 && (
                <Box p={8} textAlign="center">
                  <Text color="gray.500">No commands found</Text>
                  <Text fontSize="sm" color="gray.400" mt={2}>
                    Try a different search term
                  </Text>
                </Box>
              )}
            </Box>

            {/* Footer */}
            <HStack
              px={4}
              py={2}
              borderTop="1px solid"
              borderColor={borderColor}
              justify="space-between"
              fontSize="xs"
              color="gray.500"
            >
              <HStack spacing={4}>
                <HStack>
                  <Kbd>↑</Kbd>
                  <Kbd>↓</Kbd>
                  <Text>Navigate</Text>
                </HStack>
                <HStack>
                  <Kbd>Enter</Kbd>
                  <Text>Select</Text>
                </HStack>
              </HStack>
              <Text>{filteredCommands.length} commands</Text>
            </HStack>
          </VStack>
        </ModalBody>
      </ModalContent>
    </Modal>
  )
}
