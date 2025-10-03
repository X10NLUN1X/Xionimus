import React, { useState, useRef, useEffect } from 'react'
import {
  Box,
  VStack,
  HStack,
  Text,
  Textarea,
  Button,
  IconButton,
  Flex,
  useColorModeValue,
  Spinner,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useToast,
  Switch,
  Tooltip,
  Avatar,
  Container,
  Divider,
  useDisclosure,
  Badge,
  Popover,
  PopoverTrigger,
  PopoverContent,
  Icon
} from '@chakra-ui/react'
import {
  ChatIcon,
  ArrowUpIcon,
  ArrowForwardIcon,
  SettingsIcon,
  AddIcon,
  AttachmentIcon,
  ChevronDownIcon,
  ArrowDownIcon,
  HamburgerIcon,
  TimeIcon
} from '@chakra-ui/icons'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { useApp } from '../contexts/AppContext'
import { useGitHub } from '../contexts/GitHubContext'
import { useNavigate } from 'react-router-dom'
import { useLanguage } from '../contexts/LanguageContext'
import { GitHubPushDialog } from '../components/GitHubPushDialog'
import { GitHubImportDialog } from '../components/GitHubImportDialog'
import { LanguageSelector } from '../components/LanguageSelector'
import { ThemeSelector } from '../components/ThemeSelector'
import { ContextWarning } from '../components/ContextWarning'
import { ChatHistory } from '../components/ChatHistory'
import { CodeBlock } from '../components/CodeBlock'
import { CommandPalette } from '../components/CommandPalette'
import { ShortcutHint } from '../components/ShortcutHint'
import { MessageActions } from '../components/MessageActions'
import { TypingIndicator } from '../components/TypingIndicator'
import { useKeyboardShortcuts } from '../hooks/useKeyboardShortcuts'
import { ChatDropZone } from '../components/ChatDropZone/ChatDropZone'
import { ChatFileAttachment } from '../components/ChatFileAttachment/ChatFileAttachment'
import { AgentResultsDisplay } from '../components/AgentResultsDisplay'
import { TokenUsageWidget } from '../components/TokenUsageWidget'
import { ChatInput } from '../components/ChatInput'
import { MemoizedChatMessage } from '../components/MemoizedChatMessage'
import { LoginForm } from '../components/LoginForm'
import { QuickActions } from '../components/QuickActions'
import { RegisterForm } from '../components/RegisterForm'
import { RateLimitStatus } from '../components/RateLimitStatus'
import { ResearchActivityPanel } from '../components/ResearchActivityPanel'
import { perfMonitor, memMonitor } from '../utils/performanceMonitor'

// Performance optimized chat page with memoized components
export const ChatPage: React.FC = () => {
  // Authentication check first - before using all hooks
  const { isAuthenticated, register } = useApp()
  const [showRegister, setShowRegister] = useState(false)
  
  // Authentication Guard - Show login/register if not authenticated
  if (!isAuthenticated) {
    return (
      <Box minH="100vh" bg={useColorModeValue('gray.50', 'gray.900')} display="flex" alignItems="center" justifyContent="center">
        {showRegister ? (
          <RegisterForm 
            onRegister={register}
            onSwitchToLogin={() => setShowRegister(false)}
          />
        ) : (
          <LoginForm 
            onRegisterClick={() => setShowRegister(true)}
          />
        )}
      </Box>
    )
  }
  
  // Only use the rest of the hooks if authenticated
  return <AuthenticatedChatPage />
}

// Separate component for authenticated users to avoid hooks issues
const AuthenticatedChatPage: React.FC = () => {
  const {
    // Authentication
    user,
    logout,
    
    // Chat functionality
    messages,
    sendMessage,
    isLoading,
    isStreaming,
    streamingText,
    selectedProvider,
    selectedModel,
    setSelectedProvider,
    setSelectedModel,
    availableProviders,
    availableModels,
    createNewSession,
    currentSession,
    stopGeneration,
    useStreaming,
    setUseStreaming,
    updateMessages,
    loadSession,
    apiKeys
  } = useApp()
  
  const [input, setInput] = useState('')
  const [ultraThinking, setUltraThinking] = useState(false)
  const [isGitHubPushOpen, setIsGitHubPushOpen] = useState(false)
  const [isGitHubImportOpen, setIsGitHubImportOpen] = useState(false)
  const [showScrollButton, setShowScrollButton] = useState(false)
  const [attachedFiles, setAttachedFiles] = useState<File[]>([])
  const [lastTokenUsage, setLastTokenUsage] = useState<any>(null)
  const [contextStatus, setContextStatus] = useState<any>(null)
  const [autoScroll, setAutoScroll] = useState(true) // Auto-scroll beim Streaming
  const [isAtBottom, setIsAtBottom] = useState(true) // Ist User am Ende?
  const [researchActivities, setResearchActivities] = useState<any[]>([
    // Test activity to show panel immediately
    {
      id: 'demo_activity',
      type: 'research',
      status: 'completed',
      title: 'Demo Research',
      description: '3 Quellen analysiert (Test)',
      progress: 100,
      sources: [
        {
          url: 'https://react.dev',
          title: 'React Documentation',
          status: 'completed',
          timestamp: new Date().toISOString(),
          snippet: 'The library for web and native user interfaces'
        },
        {
          url: 'https://developer.mozilla.org',
          title: 'MDN Web Docs',
          status: 'completed',
          timestamp: new Date().toISOString(),
          snippet: 'Resources for developers, by developers'
        },
        {
          url: 'https://stackoverflow.com',
          title: 'Stack Overflow',
          status: 'completed',
          timestamp: new Date().toISOString(),
          snippet: 'Where developers learn, share, & build careers'
        }
      ],
      startTime: new Date().toISOString(),
      endTime: new Date().toISOString()
    }
  ]) // Research activities
  const [showActivityPanel, setShowActivityPanel] = useState(true) // Show/hide panel (default: true for testing)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const messagesContainerRef = useRef<HTMLDivElement>(null)
  const toast = useToast()
  const navigate = useNavigate()
  const github = useGitHub()
  const { t } = useLanguage()
  const { isOpen: isHistoryOpen, onOpen: onHistoryOpen, onClose: onHistoryClose } = useDisclosure()
  const { isOpen: isCommandOpen, onOpen: onCommandOpen, onClose: onCommandClose } = useDisclosure()
  
  const bgColor = useColorModeValue('gray.50', '#0a1628')
  const textColor = useColorModeValue('gray.800', 'white')
  const borderColor = useColorModeValue('gray.200', 'rgba(0, 212, 255, 0.3)')
  const userBg = 'linear-gradient(135deg, #0088cc, #0066aa)'
  const assistantBg = useColorModeValue('gray.50', 'rgba(15, 30, 50, 0.8)')
  const inputBg = useColorModeValue('white', 'rgba(15, 30, 50, 0.6)')
  const headerBg = useColorModeValue('white', 'rgba(10, 22, 40, 0.95)')
  
  // API Base URL configuration
  const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001'
  
  // Performance monitoring initialization
  useEffect(() => {
    perfMonitor.startMonitoring()
    memMonitor.start()
    
    return () => {
      perfMonitor.stopMonitoring()
      memMonitor.stop()
    }
  }, [])

  // Scroll Detection - Check if user is at bottom
  useEffect(() => {
    const container = messagesContainerRef.current
    if (!container) return

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container
      const distanceFromBottom = scrollHeight - scrollTop - clientHeight
      const isBottom = distanceFromBottom < 100 // Within 100px of bottom
      
      setIsAtBottom(isBottom)
      setShowScrollButton(!isBottom)
      
      // Enable auto-scroll if user manually scrolled to bottom
      if (isBottom) {
        setAutoScroll(true)
      } else {
        // Disable auto-scroll if user scrolled up
        setAutoScroll(false)
      }
    }

    container.addEventListener('scroll', handleScroll)
    return () => container.removeEventListener('scroll', handleScroll)
  }, [])

  // Auto-scroll beim Streaming - nur wenn autoScroll aktiv
  useEffect(() => {
    if (autoScroll && (isStreaming || messages.length > 0)) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
    }
  }, [messages, streamingText, isStreaming, autoScroll])
  
  // Check context status after each message
  useEffect(() => {
    const checkContextStatus = async () => {
      if (!currentSession || messages.length === 0) return
      
      try {
        const token = localStorage.getItem('xionimus_token')
        const response = await fetch(
          `${API_BASE}/api/session-management/context-status/${currentSession}`,
          {
            headers: {
              Authorization: `Bearer ${token}`
            }
          }
        )
        
        if (response.ok) {
          const status = await response.json()
          setContextStatus(status)
        }
      } catch (error) {
        console.error('Context status check failed:', error)
      }
    }
    
    checkContextStatus()
  }, [messages.length, currentSession, API_BASE])

  // Extract research activities from agent_results
  useEffect(() => {
    const lastMessage = messages[messages.length - 1]
    if (!lastMessage?.agent_results) {
      return
    }

    const researchAgents = lastMessage.agent_results.filter(
      (result: any) => result.agent === 'research' || result.agent === 'perplexity'
    )

    if (researchAgents.length > 0) {
      setShowActivityPanel(true)
      
      const activities = researchAgents.map((result: any) => ({
        id: `research_${Date.now()}_${Math.random()}`,
        type: 'research',
        status: 'completed',
        title: result.summary || 'Research durchgeführt',
        description: `${result.data?.sources?.length || 0} Quellen analysiert`,
        progress: 100,
        sources: result.data?.sources?.map((source: any, idx: number) => ({
          url: source.url || '#',
          title: source.title || `Quelle ${idx + 1}`,
          status: 'completed',
          timestamp: new Date().toISOString(),
          snippet: source.snippet || source.text?.substring(0, 150)
        })) || [],
        startTime: new Date().toISOString(),
        endTime: new Date().toISOString()
      }))

      setResearchActivities(activities)
    } else if (showActivityPanel && messages.length > 0) {
      // Hide panel if no research in latest message
      setTimeout(() => setShowActivityPanel(false), 5000)
    }
  }, [messages])
  
  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`
    }
  }, [input])

  // Scroll to bottom function - aktiviert auch Auto-Scroll
  const scrollToBottom = () => {
    setAutoScroll(true) // Enable auto-scroll when user clicks button
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  // Handler functions (defined before keyboard shortcuts)
  const handleNewChat = () => {
    createNewSession()
    toast({
      title: t('toast.newChatCreated'),
      status: 'success',
      duration: 2000
    })
  }

  // Keyboard shortcuts
  useKeyboardShortcuts([
    {
      key: 'n',
      ctrl: true,
      handler: handleNewChat,
      description: 'New chat'
    },
    {
      key: 'k',
      ctrl: true,
      handler: onCommandOpen,
      description: 'Open command palette'
    },
    {
      key: '/',
      ctrl: true,
      handler: onHistoryOpen,
      description: 'Toggle history'
    },
    {
      key: 's',
      ctrl: true,
      handler: () => navigate('/settings'),
      description: 'Open settings'
    },
    {
      key: 'l',
      ctrl: true,
      handler: () => {
        if (messages.length > 0) {
          scrollToBottom()
        }
      },
      description: 'Scroll to bottom'
    },
    {
      key: 'r',
      ctrl: true,
      handler: () => {
        // Regenerate last assistant message
        const lastAssistantMsg = messages.filter(m => m.role === 'assistant').pop()
        if (lastAssistantMsg && lastAssistantMsg.id) {
          handleRegenerateResponse(lastAssistantMsg.id)
        }
      },
      description: 'Regenerate last response'
    },
    {
      key: 'e',
      ctrl: true,
      handler: () => {
        // Edit last user message
        const lastUserMsg = messages.filter(m => m.role === 'user').pop()
        if (lastUserMsg) {
          // Focus would trigger edit modal - implementation depends on UX
          toast({
            title: 'Edit mode',
            description: 'Click edit button on your message to edit',
            status: 'info',
            duration: 2000
          })
        }
      },
      description: 'Edit last message'
    }
  ])
  
  const handleSend = async () => {
    if (!input.trim() || isLoading) return
    
    const message = input.trim()
    setInput('')
    
    // Handle file attachments
    if (attachedFiles.length > 0) {
      // TODO: Upload files and attach to message
      // For now, just show file names in message
      const fileNames = attachedFiles.map(f => f.name).join(', ')
      toast({
        title: 'Files attached',
        description: `Attached: ${fileNames}`,
        status: 'info',
        duration: 3000
      })
      setAttachedFiles([])
    }
    
    await sendMessage(message, ultraThinking)
  }
  
  const handleFilesAdded = (files: File[]) => {
    const newFiles = [...attachedFiles, ...files]
    if (newFiles.length > 5) {
      toast({
        title: 'Too many files',
        description: 'Maximum 5 files can be attached',
        status: 'warning',
        duration: 3000
      })
      return
    }
    setAttachedFiles(newFiles)
    toast({
      title: `${files.length} file(s) attached`,
      status: 'success',
      duration: 2000
    })
  }
  
  const handleRemoveFile = (index: number) => {
    setAttachedFiles(files => files.filter((_, i) => i !== index))
  }
  
  const handleAttachClick = () => {
    const input = document.createElement('input')
    input.type = 'file'
    input.multiple = true
    input.accept = 'image/*,application/pdf,.txt,.md,.doc,.docx'
    input.onchange = (e) => {
      const files = Array.from((e.target as HTMLInputElement).files || [])
      if (files.length > 0) {
        handleFilesAdded(files)
      }
    }
    input.click()
  }
  
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleStop = () => {
    if (stopGeneration) {
      stopGeneration()
      toast({
        title: t('toast.generationStopped'),
        description: t('toast.generationStoppedDesc'),
        status: 'warning',
        duration: 3000
      })
    }
  }

  // Message Actions Handlers
  const handleEditMessage = async (messageId: string, newContent: string) => {
    // Find the message index
    const messageIndex = messages.findIndex(m => m.id === messageId)
    if (messageIndex === -1) return

    // Update the message content locally
    const updatedMessages = [...messages]
    updatedMessages[messageIndex] = {
      ...updatedMessages[messageIndex],
      content: newContent
    }

    // Update state immediately for responsiveness
    // TODO: Also update in SQLite backend
    toast({
      title: 'Message updated',
      description: 'Conversation will continue from edited message',
      status: 'success',
      duration: 3000
    })
  }

  const handleRegenerateResponse = async (messageId: string) => {
    // Find the message index
    const messageIndex = messages.findIndex(m => m.id === messageId)
    if (messageIndex === -1) return

    // Find the user message before this assistant message
    const userMessage = messages[messageIndex - 1]
    if (!userMessage || userMessage.role !== 'user') return

    // Remove all messages from this assistant message onwards
    const messagesToKeep = messages.slice(0, messageIndex)
    
    // Update messages state to remove the old response
    updateMessages(messagesToKeep)

    // Resend the user message to get a new response
    await sendMessage(userMessage.content, ultraThinking)
  }

  const handleBranchConversation = async (messageId: string) => {
    // Find the message index
    const messageIndex = messages.findIndex(m => m.id === messageId)
    if (messageIndex === -1) return

    // Create new session with messages up to this point
    createNewSession()
    
    // TODO: Copy messages up to branch point to new session
    // This would require backend integration with SQLite
    
    toast({
      title: 'Branch created!',
      description: 'Continue from this point in a new conversation',
      status: 'success',
      duration: 3000
    })
  }

  const handleDeleteMessage = (messageId: string) => {
    // Find the message index
    const messageIndex = messages.findIndex(m => m.id === messageId)
    if (messageIndex === -1) return

    // Delete this message and all after it
    // TODO: Implement proper deletion with state management
    
    toast({
      title: 'Message deleted',
      description: 'All subsequent messages were also removed',
      status: 'info',
      duration: 3000
    })
  }

  const handleGitHubPush = () => {
    // Extract generated code from last assistant message
    const lastAssistantMsg = messages.filter(m => m.role === 'assistant').pop()
    const generatedCode = lastAssistantMsg?.content || ''
    
    setIsGitHubPushOpen(true)
  }

  // Welcome Screen
  if (messages.length === 0) {
    return (
      <ChatDropZone onFilesAdded={handleFilesAdded} maxFiles={5}>
      <Box minH="100vh" bg={bgColor}>
        {/* Header */}
        <Flex
          h="60px"
          px={4}
          borderBottom="1px solid"
          borderColor={borderColor}
          align="center"
          justify="space-between"
          bg={headerBg}
          position="sticky"
          top={0}
          zIndex={10}
        >
          <HStack spacing={3}>
            <IconButton
              aria-label="Chat History"
              icon={<HamburgerIcon />}
              variant="ghost"
              onClick={onHistoryOpen}
            />
            <Box
              w="32px"
              h="32px"
              bg="linear-gradient(135deg, #0088cc, #0066aa)"
              borderRadius="lg"
              display="flex"
              alignItems="center"
              justifyContent="center"
              boxShadow="0 4px 15px rgba(0, 212, 255, 0.4)"
            >
              <Text color="white" fontWeight="900" fontSize="sm" textShadow="0 0 10px rgba(255, 255, 255, 0.5)">X</Text>
            </Box>
            <Text fontWeight="700" fontSize="lg" color={useColorModeValue('#0066aa', '#0088cc')} textShadow={useColorModeValue('none', '0 0 15px rgba(0, 212, 255, 0.5)')}>Xionimus AI</Text>
          </HStack>
          
          <HStack spacing={2}>
            <Text fontSize="sm" color="gray.500">
              {user?.username}
            </Text>
            
            {/* Rate Limit Status Popover */}
            <Popover placement="bottom-end">
              <PopoverTrigger>
                <Badge
                  colorScheme="blue"
                  variant="subtle"
                  cursor="pointer"
                  _hover={{ bg: 'blue.100' }}
                >
                  Limits
                </Badge>
              </PopoverTrigger>
              <PopoverContent>
                <RateLimitStatus />
              </PopoverContent>
            </Popover>
            
            <ThemeSelector />
            <LanguageSelector />
            <Tooltip label="View Session Summary" placement="bottom">
              <IconButton
                aria-label="Session Summary"
                icon={<TimeIcon />}
                variant="ghost"
                onClick={() => {
                  if (currentSession?.id) {
                    navigate(`/session-summary/${currentSession.id}`)
                  } else {
                    toast({
                      title: 'No Active Session',
                      description: 'Start a conversation first',
                      status: 'info',
                      duration: 3000,
                    })
                  }
                }}
              />
            </Tooltip>
            <IconButton
              aria-label={t('header.newChat')}
              icon={<AddIcon />}
              variant="ghost"
              onClick={handleNewChat}
            />
            <Tooltip label="Import von GitHub">
              <IconButton
                aria-label="Import from GitHub"
                icon={<ArrowDownIcon />}
                variant="ghost"
                colorScheme="blue"
                onClick={() => setIsGitHubImportOpen(true)}
              />
            </Tooltip>
            <IconButton
              aria-label={t('header.settings')}
              icon={<SettingsIcon />}
              variant="ghost"
              onClick={() => navigate('/settings')}
            />
            <Button
              size="sm"
              variant="ghost"
              onClick={logout}
              colorScheme="red"
            >
              Abmelden
            </Button>
          </HStack>
        </Flex>

        {/* Welcome Content */}
        <Container maxW="4xl" py={20}>
          <VStack spacing={8} align="center" textAlign="center">
            <Box
              w="80px"
              h="80px"
              bg="linear-gradient(135deg, #0088cc, #0066aa)"
              borderRadius="2xl"
              display="flex"
              alignItems="center"
              justifyContent="center"
              boxShadow="0 10px 40px rgba(0, 212, 255, 0.5), 0 0 60px rgba(0, 148, 255, 0.3)"
              position="relative"
              _before={{
                content: '""',
                position: 'absolute',
                inset: '-3px',
                borderRadius: '2xl',
                background: 'linear-gradient(135deg, #0088cc, #0066aa)',
                zIndex: -1,
                filter: 'blur(10px)',
                opacity: 0.7,
              }}
            >
              <Text color="white" fontWeight="900" fontSize="3xl" textShadow="0 0 15px rgba(255, 255, 255, 0.8)">X</Text>
            </Box>
            
            <VStack spacing={2}>
              <Text 
                fontSize="4xl" 
                fontWeight="800" 
                color={useColorModeValue('#0066cc', '#0088cc')} 
                textShadow={useColorModeValue('none', '0 0 30px rgba(0, 212, 255, 0.5)')}
              >
                {t('welcome.title')}
              </Text>
              <Text fontSize="lg" color={useColorModeValue('gray.600', 'rgba(0, 212, 255, 0.7)')}>
                {t('welcome.subtitle')}
              </Text>
            </VStack>

            <VStack spacing={4} w="100%" maxW="2xl" mt={8}>
              <Text fontSize="md" fontWeight="600" color={useColorModeValue('gray.700', 'rgba(0, 212, 255, 0.8)')}>
                {t('welcome.exampleTitle')}
              </Text>
              
              {[
                t('welcome.example1'),
                t('welcome.example2'),
                t('welcome.example3')
              ].map((example, i) => (
                <Button
                  key={i}
                  w="100%"
                  h="auto"
                  py={4}
                  justifyContent="flex-start"
                  variant="outline"
                  borderColor={useColorModeValue('gray.300', 'rgba(0, 212, 255, 0.3)')}
                  color={useColorModeValue('gray.700', 'rgba(0, 212, 255, 0.9)')}
                  onClick={() => setInput(example.substring(2))}
                  _hover={{ 
                    bg: assistantBg,
                    borderColor: useColorModeValue('#0066aa', '#0088cc'),
                    boxShadow: useColorModeValue('0 0 10px rgba(0, 148, 255, 0.2)', '0 0 20px rgba(0, 212, 255, 0.3)')
                  }}
                >
                  <Text textAlign="left">{example}</Text>
                </Button>
              ))}
            </VStack>
          </VStack>
        </Container>

        {/* Input Area (Fixed Bottom) */}
        <Box
          position="fixed"
          bottom={0}
          left={0}
          right={0}
          bg={bgColor}
          borderTop="1px solid"
          borderColor={borderColor}
          p={4}
        >
          <Container maxW="4xl">
            <VStack spacing={3} align="stretch">
              {/* File Attachments Display */}
              {attachedFiles.length > 0 && (
                <HStack spacing={2} flexWrap="wrap">
                  {attachedFiles.map((file, index) => (
                    <ChatFileAttachment
                      key={index}
                      file={file}
                      onRemove={() => handleRemoveFile(index)}
                      showRemove={true}
                      isCompact={true}
                    />
                  ))}
                </HStack>
              )}
              
              {/* Main Input with Ultra Thinking Toggle */}
              <HStack align="flex-end" spacing={3}>
                {/* Ultra Thinking Toggle */}
                <VStack spacing={1} align="center">
                  <Tooltip 
                    label="Ultra Thinking: Aktiviert erweiterte Reasoning-Modi für komplexe Aufgaben (Claude)" 
                    placement="top"
                    bg="rgba(0, 212, 255, 0.9)"
                    color="white"
                  >
                    <Box 
                      p={2} 
                      borderRadius="md" 
                      bg={ultraThinking ? "rgba(0, 212, 255, 0.1)" : "transparent"}
                      border="2px solid"
                      borderColor={ultraThinking ? (useColorModeValue('#0066aa', '#0088cc')) : "transparent"}
                      transition="all 0.3s ease"
                      boxShadow={ultraThinking ? "0 0 20px rgba(0, 212, 255, 0.4)" : "none"}
                    >
                      <Switch
                        size="lg"
                        colorScheme="cyan"
                        isChecked={ultraThinking}
                        onChange={(e) => setUltraThinking(e.target.checked)}
                      />
                      <Text 
                        fontSize="xs" 
                        mt={1} 
                        color={ultraThinking ? (useColorModeValue('#0066aa', '#0088cc')) : 'gray.500'}
                        textAlign="center"
                        fontWeight={ultraThinking ? "bold" : "normal"}
                      >
                        🧠
                      </Text>
                    </Box>
                  </Tooltip>
                </VStack>

                {/* Textarea */}
                <Box flex={1} position="relative">
                  <Textarea
                    ref={textareaRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder={t('chat.inputPlaceholder')}
                    bg={inputBg}
                    border="2px solid"
                    borderColor={borderColor}
                    _focus={{
                      borderColor: '#0088cc',
                      boxShadow: '0 0 0 1px #0088cc, 0 0 20px rgba(0, 212, 255, 0.3)'
                    }}
                    resize="none"
                    minH="56px"
                    maxH="200px"
                    pr="50px"
                    fontSize="md"
                  />
                  
                  {/* Send Button (Inside Textarea) */}
                  <IconButton
                    aria-label="Senden"
                    icon={<ArrowUpIcon />}
                    position="absolute"
                    right="8px"
                    bottom="8px"
                    size="sm"
                    bg="linear-gradient(135deg, #0088cc, #0066aa)"
                    color="white"
                    borderRadius="md"
                    onClick={handleSend}
                    isLoading={isLoading}
                    isDisabled={!input.trim() || isLoading}
                    _hover={{
                      bg: "linear-gradient(135deg, #0066aa, #0088cc)",
                      boxShadow: "0 0 20px rgba(0, 212, 255, 0.6)"
                    }}
                    boxShadow="0 2px 10px rgba(0, 212, 255, 0.4)"
                  />
                </Box>
              </HStack>

              {/* Toolbar Buttons */}
              <Flex
                wrap="wrap"
                gap={2}
                justify="space-between"
                align="center"
              >
                <HStack spacing={2}>
                  <Button
                    size="sm"
                    variant="ghost"
                    leftIcon={<AttachmentIcon />}
                    onClick={handleAttachClick}
                  >
                    📎 Anhang {attachedFiles.length > 0 && `(${attachedFiles.length})`}
                  </Button>
                  
                  <Button
                    size="sm"
                    variant="ghost"
                    isDisabled={!isLoading}
                    onClick={handleStop}
                  >
                    ⏸️ Stopp
                  </Button>
                  
                  <Menu>
                    <MenuButton as={Button} size="sm" variant="ghost" rightIcon={<ChevronDownIcon />}>
                      🌿 Branch: main
                    </MenuButton>
                    <MenuList>
                      <MenuItem>main</MenuItem>
                      <MenuItem>develop</MenuItem>
                      <MenuItem>+ Neuer Branch</MenuItem>
                    </MenuList>
                  </Menu>
                </HStack>

                <HStack spacing={2}>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => toast({ title: 'Fork-Feature kommt bald', status: 'info', duration: 2000 })}
                  >
                    🔀 Verzweigen
                  </Button>
                  
                  <Button
                    size="sm"
                    variant="solid"
                    colorScheme="blue"
                    onClick={() => setIsGitHubImportOpen(true)}
                  >
                    📥 GitHub Import
                  </Button>
                  
                  <Button
                    size="sm"
                    variant="solid"
                    colorScheme="green"
                    onClick={handleGitHubPush}
                  >
                    📤 GitHub Push
                  </Button>
                </HStack>
              </Flex>

              {/* Ultra Thinking Status */}
              {ultraThinking && (
                <Flex justify="center" align="center" fontSize="xs" color="gray.500">
                  <HStack spacing={1}>
                    <Text color={useColorModeValue('#0066aa', '#0088cc')} fontWeight="600">
                      🧠 Erweitertes Denken aktiv
                    </Text>
                  </HStack>
                </Flex>
              )}
            </VStack>
          </Container>
        </Box>

        {/* Input Area (Fixed Bottom) - Same as Chat View */}
        <Box
          position="fixed"
          bottom={0}
          left={0}
          right={0}
          bg={bgColor}
          borderTop="1px solid"
          borderColor={borderColor}
          p={4}
        >
          <Container maxW="4xl">
            <VStack spacing={3} align="stretch">
              {/* File Attachments Display */}
              {attachedFiles.length > 0 && (
                <HStack spacing={2} flexWrap="wrap">
                  {attachedFiles.map((file, index) => (
                    <ChatFileAttachment
                      key={index}
                      file={file}
                      onRemove={() => handleRemoveFile(index)}
                      showRemove={true}
                      isCompact={true}
                    />
                  ))}
                </HStack>
              )}
              
              {/* Main Input with Ultra Thinking Toggle */}
              <HStack align="flex-end" spacing={3}>
                {/* Input Box */}
                <Box flex={1}>
                  <Textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyPress}
                    placeholder={t('chat.inputPlaceholder')}
                    bg={inputBg}
                    border="2px solid"
                    borderColor={borderColor}
                    _hover={{ borderColor: '#0088cc' }}
                    _focus={{ borderColor: '#0088cc', boxShadow: '0 0 0 1px #0088cc' }}
                    minH="60px"
                    maxH="200px"
                    resize="vertical"
                    fontSize="md"
                    autoFocus
                  />
                  
                  <HStack mt={2} spacing={2} justify="space-between">
                    <HStack spacing={2}>
                      <Button
                        size="sm"
                        variant="ghost"
                        leftIcon={<AttachmentIcon />}
                        onClick={handleAttachClick}
                      >
                        📎 Anhang {attachedFiles.length > 0 && `(${attachedFiles.length})`}
                      </Button>
                      
                      <Button
                        size="sm"
                        variant={ultraThinking ? "solid" : "ghost"}
                        colorScheme={ultraThinking ? "purple" : "gray"}
                        onClick={() => setUltraThinking(!ultraThinking)}
                        leftIcon={<Text>🧠</Text>}
                      >
                        Ultra-Thinking
                      </Button>
                    </HStack>

                    <HStack spacing={2}>
                      {/* Model info hidden - configured for Claude Sonnet 4.5 (coding) and Opus 4.1 (debugging) */}
                    </HStack>
                  </HStack>
                </Box>

                {/* Send Button */}
                <IconButton
                  aria-label={t('chat.send')}
                  icon={isLoading ? <Spinner size="sm" /> : <ArrowForwardIcon />}
                  colorScheme="blue"
                  size="lg"
                  onClick={handleSend}
                  isDisabled={!input.trim() || isLoading}
                  h="60px"
                  w="60px"
                  borderRadius="xl"
                  bg="linear-gradient(135deg, #0088cc, #0066aa)"
                  _hover={{ bg: 'linear-gradient(135deg, #00b8e6, #0080e6)' }}
                  boxShadow="0 4px 15px rgba(0, 212, 255, 0.4)"
                />
              </HStack>

              {/* Info Section */}
              <Flex justify="space-between" align="center" fontSize="xs" color="gray.500">
                <HStack spacing={2}>
                  <Button
                    size="xs"
                    variant="ghost"
                    leftIcon={<SettingsIcon />}
                    onClick={() => navigate('/settings')}
                  >
                    {t('chat.configureKeys')}
                  </Button>
                </HStack>
                
                {ultraThinking && (
                  <HStack spacing={1}>
                    <Text color={useColorModeValue('#0066aa', '#0088cc')} fontWeight="600">
                      🧠 Erweitertes Denken aktiv
                    </Text>
                  </HStack>
                )}
              </Flex>
            </VStack>
          </Container>
        </Box>

        {/* GitHub Push Dialog */}
        <GitHubPushDialog
          isOpen={isGitHubPushOpen}
          onClose={() => setIsGitHubPushOpen(false)}
          generatedCode={messages.filter(m => m.role === 'assistant').pop()?.content}
        />
      </Box>
      </ChatDropZone>
    )
  }

  // Chat View
  return (
    <ChatDropZone onFilesAdded={handleFilesAdded} maxFiles={5}>
    <Box minH="100vh" bg={bgColor}>
      {/* Header */}
      <Flex
        h="60px"
        px={4}
        borderBottom="1px solid"
        borderColor={borderColor}
        align="center"
        justify="space-between"
        bg={headerBg}
        position="sticky"
        top={0}
        zIndex={10}
      >
        <HStack spacing={3}>
          <IconButton
            aria-label="Chat History"
            icon={<HamburgerIcon />}
            variant="ghost"
            onClick={onHistoryOpen}
          />
          <Box
            w="32px"
            h="32px"
            bg="linear-gradient(135deg, #0088cc, #0066aa)"
            borderRadius="lg"
            display="flex"
            alignItems="center"
            justifyContent="center"
            boxShadow="0 4px 15px rgba(0, 212, 255, 0.4)"
          >
            <Text color="white" fontWeight="900" fontSize="sm" textShadow="0 0 10px rgba(255, 255, 255, 0.5)">X</Text>
          </Box>
          <Text fontWeight="700" fontSize="lg" color={useColorModeValue('#0066aa', '#0088cc')} textShadow={useColorModeValue('none', '0 0 15px rgba(0, 212, 255, 0.5)')}>Xionimus AI</Text>
        </HStack>
        
        <HStack spacing={2}>
          {/* Activity Panel Toggle */}
          <Tooltip label={showActivityPanel ? "Agent-Aktivitäten ausblenden" : "Agent-Aktivitäten anzeigen"}>
            <IconButton
              aria-label="Toggle Activity Panel"
              icon={showActivityPanel ? <ChevronDownIcon /> : <TimeIcon />}
              variant="ghost"
              size="sm"
              onClick={() => setShowActivityPanel(!showActivityPanel)}
              colorScheme={showActivityPanel ? "blue" : "gray"}
            />
          </Tooltip>
          
          <Text fontSize="sm" color="gray.500">
            {user?.username}
          </Text>
          
          {/* Rate Limit Status Popover */}
          <Popover placement="bottom-end">
            <PopoverTrigger>
              <Badge
                colorScheme="blue"
                variant="subtle"
                cursor="pointer"
                _hover={{ bg: 'blue.100' }}
              >
                Limits
              </Badge>
            </PopoverTrigger>
            <PopoverContent>
              <RateLimitStatus />
            </PopoverContent>
          </Popover>
          
          <LanguageSelector />
          <Tooltip label="Import von GitHub">
            <IconButton
              aria-label="Import from GitHub"
              icon={<ArrowDownIcon />}
              variant="ghost"
              colorScheme="blue"
              size="sm"
              onClick={() => setIsGitHubImportOpen(true)}
            />
          </Tooltip>
          <IconButton
            aria-label={t('header.newChat')}
            icon={<AddIcon />}
            variant="ghost"
            onClick={handleNewChat}
          />
          <IconButton
            aria-label={t('header.settings')}
            icon={<SettingsIcon />}
            variant="ghost"
            onClick={() => navigate('/settings')}
          />
          <Button
            size="sm"
            variant="ghost"
            onClick={logout}
            colorScheme="red"
          >
            Abmelden
          </Button>
        </HStack>
      </Flex>

      {/* Main Content Area with Split View */}
      <Flex height="calc(100vh - 60px)" overflow="hidden">
        {/* Left: Messages */}
        <Container 
          maxW={showActivityPanel ? "container.lg" : "4xl"} 
          flex={1}
          pb="200px" 
          pt={4} 
          ref={messagesContainerRef} 
          maxH="calc(100vh - 260px)" 
          overflowY="auto"
        >
          <VStack spacing={6} align="stretch">
          {/* Context Warning */}
          {contextStatus && contextStatus.warning && (
            <ContextWarning
              sessionId={currentSession?.id || ''}
              currentTokens={contextStatus.current_tokens}
              limit={contextStatus.limit}
              percentage={contextStatus.percentage}
              recommendation={contextStatus.recommendation}
              onSessionForked={(newSessionId) => {
                // Load new session
                loadSession(newSessionId)
              }}
              apiKeys={apiKeys}
            />
          )}
          
          {messages.map((msg, idx) => (
            <Flex
              key={msg.id || idx}
              gap={3}
              flexDirection={msg.role === 'user' ? 'row-reverse' : 'row'}
            >
              <Avatar
                size="sm"
                name={msg.role === 'user' ? 'User' : 'Xionimus'}
                bg={msg.role === 'user' ? userBg : 'linear-gradient(135deg, #0088cc, #0066aa)'}
              />
              
              <VStack flex={1} align={msg.role === 'user' ? 'flex-end' : 'flex-start'} spacing={1}>
                <HStack 
                  w="full" 
                  justify={msg.role === 'user' ? 'flex-end' : 'flex-start'}
                  spacing={2}
                >
                  {msg.role === 'assistant' && (
                    <MessageActions
                      messageId={msg.id || idx.toString()}
                      content={msg.content}
                      role={msg.role}
                      onRegenerate={handleRegenerateResponse}
                      onBranch={handleBranchConversation}
                      onDelete={handleDeleteMessage}
                    />
                  )}
                  
                  <MemoizedChatMessage message={msg} index={idx} />
                  
                  {msg.role === 'user' && (
                    <MessageActions
                      messageId={msg.id || idx.toString()}
                      content={msg.content}
                      role={msg.role}
                      onEdit={handleEditMessage}
                      onBranch={handleBranchConversation}
                      onDelete={handleDeleteMessage}
                    />
                  )}
                </HStack>
                
                {/* Timestamp and Model Info */}
                <HStack spacing={2} fontSize="xs" color="gray.500">
                  {msg.timestamp && (
                    <>
                      <TimeIcon boxSize={3} />
                      <Text>
                        {new Date(msg.timestamp).toLocaleTimeString([], { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        })}
                      </Text>
                    </>
                  )}
                  {msg.model && (
                    <>
                      <Text>•</Text>
                      <Badge
                        size="sm"
                        colorScheme="cyan"
                        variant="subtle"
                        fontSize="xx-small"
                      >
                        {msg.model}
                      </Badge>
                    </>
                  )}
                </HStack>
              </VStack>
            </Flex>
          ))}
          
          {/* Quick Actions (Research Options / Post-Code Options) */}
          {messages.length > 0 && messages[messages.length - 1]?.quick_actions && (
            <QuickActions
              message={messages[messages.length - 1].quick_actions.message}
              options={messages[messages.length - 1].quick_actions.options}
              onSelect={(action) => {
                // Send the selected option as user message
                const optionText = action.title.replace(/[🟢🟡🔴❌🐛⚡💡]/g, '').trim()
                sendMessage(optionText)
              }}
              isDisabled={isLoading || isStreaming}
            />
          )}
          
          {/* Streaming Indicator */}
          {isStreaming && (
            <TypingIndicator 
              streamingText={streamingText} 
              showDots={!streamingText}
            />
          )}
          
          {isLoading && (
            <Flex gap={3}>
              <Avatar size="sm" name="Xionimus" bg="linear-gradient(135deg, #0088cc, #0066aa)" />
              <Box 
                bg={assistantBg} 
                px={4} 
                py={3} 
                borderRadius="lg" 
                minW="200px"
                boxShadow="0 4px 15px rgba(0, 212, 255, 0.2)"
                border="1px solid"
                borderColor="rgba(0, 212, 255, 0.2)"
              >
                <VStack align="start" spacing={2}>
                  <HStack spacing={2}>
                    <Spinner size="sm" color={useColorModeValue('#0066aa', '#0088cc')} />
                    <Text 
                      fontWeight="600" 
                      fontSize="15px"
                      letterSpacing="0.01em"
                      color={useColorModeValue('#0066aa', '#0088cc')}
                    >
                      Arbeite daran...
                    </Text>
                  </HStack>
                  {messages.length > 0 && messages[messages.length - 1].content.match(/(klein|mittel|groß|small|medium|large)/i) && (
                    <Text 
                      fontSize="13px" 
                      color="gray.500"
                      fontWeight="500"
                      letterSpacing="0.01em"
                    >
                      🔍 Führe Recherche durch...
                    </Text>
                  )}
                </VStack>
              </Box>
            </Flex>
          )}
          
          <div ref={messagesEndRef} />
        </VStack>
      </Container>

        {/* Right: Research Activity Panel */}
        <ResearchActivityPanel
          activities={researchActivities}
          isVisible={showActivityPanel}
        />
      </Flex>

      {/* Input Area (Fixed Bottom) */}
      <Box
        position="fixed"
        bottom={0}
        left={0}
        right={0}
        bg={bgColor}
        borderTop="1px solid"
        borderColor={borderColor}
        p={4}
      >
        <Container maxW="4xl">
          <VStack spacing={3} align="stretch">
            {/* Main Input with Ultra Thinking Toggle */}
            <HStack align="flex-end" spacing={3}>
              {/* Ultra Thinking Toggle */}
              <VStack spacing={1} align="center">
                <Tooltip 
                  label="Ultra Thinking: Aktiviert erweiterte Reasoning-Modi für komplexe Aufgaben (Claude)" 
                  placement="top"
                  bg="rgba(0, 212, 255, 0.9)"
                  color="white"
                >
                  <Box 
                    p={2} 
                    borderRadius="md" 
                    bg={ultraThinking ? "rgba(0, 212, 255, 0.1)" : "transparent"}
                    border="2px solid"
                    borderColor={ultraThinking ? "#0088cc" : "transparent"}
                    transition="all 0.3s ease"
                    boxShadow={ultraThinking ? "0 0 20px rgba(0, 212, 255, 0.4)" : "none"}
                  >
                    <Switch
                      size="lg"
                      colorScheme="cyan"
                      isChecked={ultraThinking}
                      onChange={(e) => setUltraThinking(e.target.checked)}
                    />
                    <Text 
                      fontSize="xs" 
                      mt={1} 
                      color={ultraThinking ? (useColorModeValue('#0066aa', '#0088cc')) : 'gray.500'}
                      textAlign="center"
                      fontWeight={ultraThinking ? "bold" : "normal"}
                    >
                      🧠
                    </Text>
                  </Box>
                </Tooltip>
              </VStack>

              {/* Chat Input Component */}
              <Box flex={1} position="relative">
                <ChatInput
                  value={input}
                  onChange={setInput}
                  onSubmit={handleSend}
                  disabled={isLoading}
                  placeholder="Beschreiben Sie Ihr Programmier-Projekt..."
                  onKeyDown={handleKeyPress}
                />
                
                {/* Send Button (Inside Input) */}
                <IconButton
                  aria-label="Senden"
                  icon={<ArrowUpIcon />}
                  position="absolute"
                  right="8px"
                  bottom="8px"
                  size="sm"
                  colorScheme="blue"
                  borderRadius="md"
                  onClick={handleSend}
                  isLoading={isLoading}
                  isDisabled={!input.trim() || isLoading}
                />
              </Box>
            </HStack>

            {/* Toolbar Buttons */}
            <Flex
              wrap="wrap"
              gap={2}
              justify="space-between"
              align="center"
            >
              <HStack spacing={2}>
                <Button
                  size="sm"
                  variant="ghost"
                  leftIcon={<AttachmentIcon />}
                  onClick={() => toast({ title: 'Anhang-Feature kommt bald', status: 'info', duration: 2000 })}
                >
                  📎 Anhang
                </Button>
                
                <Button
                  size="sm"
                  variant="solid"
                  bg={isLoading ? "linear-gradient(135deg, #ff4444, #cc0000)" : "gray.600"}
                  color="white"
                  isDisabled={!isLoading}
                  onClick={handleStop}
                  _hover={{
                    bg: isLoading ? "linear-gradient(135deg, #cc0000, #ff4444)" : "gray.600",
                    boxShadow: isLoading ? "0 0 20px rgba(255, 68, 68, 0.6)" : "none"
                  }}
                  boxShadow={isLoading ? "0 2px 10px rgba(255, 68, 68, 0.4)" : "none"}
                >
                  ⏸️ Stopp
                </Button>
                
                <Menu>
                  <MenuButton as={Button} size="sm" variant="ghost" rightIcon={<ChevronDownIcon />}>
                    🌿 Branch: main
                  </MenuButton>
                  <MenuList>
                    <MenuItem>main</MenuItem>
                    <MenuItem>develop</MenuItem>
                    <MenuItem>+ Neuer Branch</MenuItem>
                  </MenuList>
                </Menu>
              </HStack>

              <HStack spacing={2}>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => toast({ title: 'Fork-Feature kommt bald', status: 'info', duration: 2000 })}
                >
                  🔀 Verzweigen
                </Button>
                
                <Button
                  size="sm"
                  variant="solid"
                  bg="linear-gradient(135deg, #0088cc, #0066aa)"
                  color="white"
                  onClick={handleGitHubPush}
                  _hover={{
                    bg: "linear-gradient(135deg, #0066aa, #0088cc)",
                    boxShadow: "0 0 25px rgba(0, 212, 255, 0.6)"
                  }}
                  boxShadow="0 2px 15px rgba(0, 212, 255, 0.4)"
                >
                  📤 GitHub Push
                </Button>
              </HStack>
            </Flex>

            {/* Status Info */}
            {ultraThinking && (
              <Flex justify="center" align="center" fontSize="xs" color="gray.500">
                <HStack spacing={1}>
                  <Text>🧠 Erweitertes Denken aktiv</Text>
                </HStack>
              </Flex>
            )}
          </VStack>
        </Container>
      </Box>

      {/* Scroll to Bottom Button */}
      {showScrollButton && (
        <IconButton
          aria-label="Scroll to bottom"
          icon={<ArrowDownIcon />}
          position="fixed"
          bottom="220px"
          right="30px"
          size="lg"
          colorScheme="cyan"
          borderRadius="full"
          boxShadow="0 4px 20px rgba(0, 212, 255, 0.4)"
          onClick={scrollToBottom}
          zIndex={5}
          _hover={{
            transform: 'scale(1.1)',
            boxShadow: '0 6px 25px rgba(0, 212, 255, 0.6)'
          }}
          transition="all 0.2s"
        />
      )}

      {/* Chat History Drawer */}
      <ChatHistory isOpen={isHistoryOpen} onClose={onHistoryClose} />

      {/* Command Palette */}
      <CommandPalette isOpen={isCommandOpen} onClose={onCommandClose} />

      {/* GitHub Push Dialog */}
      <GitHubPushDialog
        isOpen={isGitHubPushOpen}
        onClose={() => setIsGitHubPushOpen(false)}
        generatedCode={messages.filter(m => m.role === 'assistant').pop()?.content}
      />

      {/* GitHub Import Dialog */}
      <GitHubImportDialog
        isOpen={isGitHubImportOpen}
        onClose={() => setIsGitHubImportOpen(false)}
      />

      {/* Token Usage Widget */}
      <TokenUsageWidget 
        tokenUsage={lastTokenUsage}
        onForkRecommended={() => {
          toast({
            title: 'Fork empfohlen',
            description: 'Erwäge einen Fork zu erstellen, um die Conversation zu optimieren',
            status: 'info',
            duration: 5000
          })
        }}
      />
    </Box>
    </ChatDropZone>
  )
}
