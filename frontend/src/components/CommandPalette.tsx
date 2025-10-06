import React, { useState, useEffect, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Modal, ModalContent, ModalBody } from './Modal'
import { useApp } from '../contexts/AppContext'
import { useTheme } from '../contexts/ThemeContext'
import { useLanguage } from '../contexts/LanguageContext'
import { Badge } from './UI/Badge'

interface Command {
  id: string
  label: string
  description?: string
  icon: string
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
  const { createNewSession } = useApp()
  const { themeMode, setThemeMode } = useTheme()
  const { setLanguage, t } = useLanguage()

  const commands: Command[] = [
    {
      id: 'new-chat',
      label: t('header.newChat'),
      description: 'Start a new conversation',
      icon: '💬',
      shortcut: 'Ctrl+N',
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
      icon: '⚙️',
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
      icon: '🌙',
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
      icon: '☀️',
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
      icon: '🔄',
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
      icon: '🇬🇧',
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
      icon: '🇩🇪',
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
      icon: '💭',
      action: () => {
        navigate('/chat')
        onClose()
      },
      category: 'Navigation'
    },
  ]

  const filteredCommands = commands.filter(cmd =>
    cmd.label.toLowerCase().includes(search.toLowerCase()) ||
    cmd.description?.toLowerCase().includes(search.toLowerCase()) ||
    cmd.category?.toLowerCase().includes(search.toLowerCase())
  )

  useEffect(() => {
    if (isOpen && inputRef.current) {
      setTimeout(() => inputRef.current?.focus(), 100)
    }
  }, [isOpen])

  useEffect(() => {
    setSelectedIndex(0)
  }, [search])

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!isOpen) return

      if (e.key === 'ArrowDown') {
        e.preventDefault()
        setSelectedIndex(prev => 
          prev < filteredCommands.length - 1 ? prev + 1 : 0
        )
      } else if (e.key === 'ArrowUp') {
        e.preventDefault()
        setSelectedIndex(prev => 
          prev > 0 ? prev - 1 : filteredCommands.length - 1
        )
      } else if (e.key === 'Enter') {
        e.preventDefault()
        if (filteredCommands[selectedIndex]) {
          filteredCommands[selectedIndex].action()
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, selectedIndex, filteredCommands])

  // Group commands by category
  const groupedCommands = filteredCommands.reduce((acc, cmd) => {
    const category = cmd.category || 'Other'
    if (!acc[category]) acc[category] = []
    acc[category].push(cmd)
    return acc
  }, {} as Record<string, Command[]>)

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalContent className="mt-20">
        <ModalBody className="p-0">
          {/* Search Input */}
          <div className="p-4 border-b border-gold-500/20">
            <div className="relative">
              <svg 
                className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
                fill="none" 
                viewBox="0 0 24 24" 
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                ref={inputRef}
                type="text"
                placeholder="Type a command or search..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full pl-10 pr-4 py-3 bg-primary-navy/50 border border-gold-500/20 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-gold-500/60 focus:shadow-gold-glow transition-all"
              />
            </div>
          </div>

          {/* Commands List */}
          <div className="max-h-[400px] overflow-y-auto custom-scrollbar">
            {Object.entries(groupedCommands).length === 0 ? (
              <div className="p-8 text-center text-gray-400">
                No commands found
              </div>
            ) : (
              Object.entries(groupedCommands).map(([category, cmds]) => (
                <div key={category} className="py-2">
                  <div className="px-4 py-2">
                    <Badge variant="default" className="text-xs">
                      {category}
                    </Badge>
                  </div>
                  {cmds.map((cmd, index) => {
                    const globalIndex = filteredCommands.findIndex(c => c.id === cmd.id)
                    const isSelected = globalIndex === selectedIndex

                    return (
                      <button
                        key={cmd.id}
                        onClick={() => cmd.action()}
                        className={`
                          w-full px-4 py-3 flex items-center gap-3
                          transition-colors duration-150
                          ${isSelected 
                            ? 'bg-gold-500/20 border-l-4 border-gold-500' 
                            : 'border-l-4 border-transparent hover:bg-accent-blue/30'
                          }
                        `}
                      >
                        <span className="text-2xl">{cmd.icon}</span>
                        <div className="flex-1 text-left">
                          <p className="text-sm font-medium text-white">
                            {cmd.label}
                          </p>
                          {cmd.description && (
                            <p className="text-xs text-gray-400">
                              {cmd.description}
                            </p>
                          )}
                        </div>
                        {cmd.shortcut && (
                          <kbd className="px-2 py-1 text-xs font-mono bg-primary-navy/50 border border-gold-500/20 rounded">
                            {cmd.shortcut}
                          </kbd>
                        )}
                      </button>
                    )
                  })}
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          <div className="p-3 border-t border-gold-500/20 flex items-center justify-between text-xs text-gray-500">
            <div className="flex items-center gap-4">
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-primary-navy/50 border border-gold-500/20 rounded">↑↓</kbd>
                Navigate
              </span>
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-primary-navy/50 border border-gold-500/20 rounded">↵</kbd>
                Select
              </span>
              <span className="flex items-center gap-1">
                <kbd className="px-1.5 py-0.5 bg-primary-navy/50 border border-gold-500/20 rounded">ESC</kbd>
                Close
              </span>
            </div>
          </div>
        </ModalBody>
      </ModalContent>
    </Modal>
  )
}
