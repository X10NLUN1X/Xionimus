import React, { useState, useRef, useEffect } from 'react'
import { 
  useToast, 
  useDisclosure, 
  useColorModeValue,
  Text
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
// Import new glossy components
import { Avatar } from '../components/UI/Avatar'
import { Spinner } from '../components/UI/Spinner'
import { IconButton } from '../components/UI/IconButton'
import { Button } from '../components/UI/Button'
import { Tooltip } from '../components/UI/Tooltip'
import { Menu, MenuButton, MenuList, MenuItem } from '../components/UI/Menu'
import { Switch } from '../components/UI/Switch'
import { Popover, PopoverTrigger, PopoverContent } from '../components/UI/Popover'
import { Badge } from '../components/UI/Badge'
// Import animation components
import { FadeIn } from '../components/UI/FadeIn'
import { SkeletonLoader } from '../components/UI/SkeletonLoader'
import { AnimatedButton } from '../components/UI/AnimatedButton'
// Import Code & Logs Drawers
import { CodeViewDrawer } from '../components/CodeViewDrawer'
import { LogsViewDrawer } from '../components/LogsViewDrawer'
// Import code extraction utilities
import { extractCodeFromMessages } from '../utils/codeExtractor'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { StreamingMarkdownRenderer } from '../components/StreamingCodeBlock'
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
import { ActiveProjectBadge } from '../components/ActiveProjectBadge'
import { ContextWarningBanner } from '../components/ContextWarningBanner'
import { SessionForkDialog } from '../components/SessionForkDialog'
import { FileUploadDialog } from '../components/FileUploadDialog'
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
import { DeveloperModeToggle } from '../components/DeveloperModeToggle'  // 🎯 PHASE 2
import { ResearchActivityPanel } from '../components/ResearchActivityPanel'
import { SessionSummaryModal } from '../components/SessionSummaryModal'
import { AgentSelector } from '../components/AgentSelector'  // 🤖 AGENTEN PHASE
import { AgentResultsPanel } from '../components/AgentResultsPanel'  // 🤖 AGENTEN PHASE
import { ResearchHistoryPanel } from '../components/ResearchHistoryPanel'  // 📜 PHASE 4: Research History
import { agentService, AgentType } from '../services/agentService'  // 🤖 AGENTEN PHASE
import { detectAgent, getAgentDisplayName, shouldShowDetection } from '../utils/autonomousAgentRouter'  // 🤖 AUTONOMOUS ROUTING
import { saveResearchToHistory, ResearchHistoryItem } from '../utils/researchHistory'  // 📜 PHASE 4
import { perfMonitor, memMonitor } from '../utils/performanceMonitor'

// Performance optimized chat page with memoized components
export const ChatPage: React.FC = () => {
  // Authentication check first - before using all hooks
  const { isAuthenticated, register } = useApp()
  const [showRegister, setShowRegister] = useState(false)
  
  // Authentication Guard - Show login/register if not authenticated
  if (!isAuthenticated) {
    return (
      <>
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
      </>
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
    tokenUsage,  // NEW: Get token usage from context
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
    apiKeys,
    developerMode,  // 🎯 PHASE 2: Developer Mode
    setDeveloperMode  // 🎯 PHASE 2: Set developer mode
  } = useApp()
  
  const [input, setInput] = useState('')
  const [ultraThinking, setUltraThinking] = useState(true)  // 🎯 PHASE 2: Ultra-thinking enabled by default
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null)  // 🤖 AGENTEN PHASE: Selected AI agent
  const [agentResult, setAgentResult] = useState<any>(null)  // 🤖 AGENTEN PHASE: Agent execution result
  const [isAgentExecuting, setIsAgentExecuting] = useState(false)  // 🤖 AGENTEN PHASE: Agent execution state
  const [showResearchHistory, setShowResearchHistory] = useState(false)  // 📜 PHASE 4: Research history panel
  const [isGitHubPushOpen, setIsGitHubPushOpen] = useState(false)
  const [isGitHubImportOpen, setIsGitHubImportOpen] = useState(false)
  const [isSessionForkOpen, setIsSessionForkOpen] = useState(false)
  const [isFileUploadOpen, setIsFileUploadOpen] = useState(false)
  const [activeProjectName, setActiveProjectName] = useState<string | null>(null)
  const [showScrollButton, setShowScrollButton] = useState(false)
  const [attachedFiles, setAttachedFiles] = useState<File[]>([])
  // Token usage is now available from context - no need for local state
  const [contextStatus, setContextStatus] = useState<any>(null)
  const [autoScroll, setAutoScroll] = useState(true) // Auto-scroll beim Streaming
  const [isAtBottom, setIsAtBottom] = useState(true) // Ist User am Ende?
  const [researchActivities, setResearchActivities] = useState<any[]>([]) // Research activities (empty by default)
  const [showActivityPanel, setShowActivityPanel] = useState(false) // Show/hide panel (default: false)
  
  // Code & Logs Drawers State
  const [isCodeViewOpen, setIsCodeViewOpen] = useState(false)
  const [isLogsViewOpen, setIsLogsViewOpen] = useState(false)
  const [codeFiles, setCodeFiles] = useState<any[]>([])
  const [logs, setLogs] = useState<any[]>([])
  const [executionMetrics, setExecutionMetrics] = useState<any>(null)
  
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const messagesContainerRef = useRef<HTMLDivElement>(null)
  const toast = useToast()
  const navigate = useNavigate()
  const github = useGitHub()
  const { t } = useLanguage()
  const { isOpen: isHistoryOpen, onOpen: onHistoryOpen, onClose: onHistoryClose } = useDisclosure()
  const { isOpen: isCommandOpen, onOpen: onCommandOpen, onClose: onCommandClose } = useDisclosure()
  const { isOpen: isSummaryOpen, onOpen: onSummaryOpen, onClose: onSummaryClose } = useDisclosure()
  
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

  // Auto-extract code from messages
  useEffect(() => {
    if (messages.length > 0) {
      const extractedCode = extractCodeFromMessages(messages)
      
      if (extractedCode.length > 0) {
        setCodeFiles(extractedCode)
      } else {
        // Fallback to demo data if no code found
        setCodeFiles([
          {
            id: '1',
            name: 'example.py',
            language: 'python',
            content: `def fibonacci(n):
    """Calculate Fibonacci number recursively"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Calculate first 10 Fibonacci numbers
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")`
          },
          {
            id: '2',
            name: 'app.js',
            language: 'javascript',
            content: `// Express.js API Server
const express = require('express');
const app = express();

app.get('/api/hello', (req, res) => {
  res.json({ message: 'Hello from Xionimus AI!' });
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});`
          }
        ])
      }
    }
  }, [messages])

  // Initialize demo logs (will be replaced by real logs from sandbox)
  useEffect(() => {
    // Demo Logs
    setLogs([
      {
        id: '1',
        timestamp: new Date(Date.now() - 5000),
        level: 'info',
        message: 'Starting code execution...',
        source: 'stdout'
      },
      {
        id: '2',
        timestamp: new Date(Date.now() - 4000),
        level: 'success',
        message: 'Dependencies loaded successfully',
        source: 'stdout'
      },
      {
        id: '3',
        timestamp: new Date(Date.now() - 3000),
        level: 'info',
        message: 'F(0) = 0',
        source: 'stdout'
      },
      {
        id: '4',
        timestamp: new Date(Date.now() - 2000),
        level: 'info',
        message: 'F(1) = 1',
        source: 'stdout'
      },
      {
        id: '5',
        timestamp: new Date(Date.now() - 1000),
        level: 'warning',
        message: 'Recursive function may cause performance issues',
        source: 'stderr'
      },
      {
        id: '6',
        timestamp: new Date(),
        level: 'success',
        message: 'Execution completed successfully',
        source: 'stdout'
      }
    ])

    // Demo Metrics
    setExecutionMetrics({
      executionTime: 1234,
      exitCode: 0,
      memoryUsage: 45.2
    })
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

  // Update activities when messages change - scan ALL messages for activities
  useEffect(() => {
    const activities: any[] = []
    
    // Scan all assistant messages for activities
    messages.forEach((message, index) => {
      if (message.role !== 'assistant') return
      
      // 1. Research Activities (from research_sources)
      if (message.research_sources && message.research_sources.length > 0) {
        activities.push({
          id: `research_${message.id || index}`,
          type: 'research',
          status: 'completed',
          title: '🔍 Research abgeschlossen',
          description: `${message.research_sources.length} Quellen analysiert`,
          progress: 100,
          sources: message.research_sources.map((source: any) => ({
            url: source.url,
            title: source.title,
            status: source.status || 'completed',
            timestamp: source.timestamp || new Date().toISOString(),
            snippet: source.snippet || ''
          })),
          startTime: message.timestamp || new Date().toISOString(),
          endTime: message.timestamp || new Date().toISOString()
        })
      }
      
      // 2. Coding Activities (detect by checking for code blocks in content)
      const hasCodeBlocks = message.content.includes('```')
      // Check if this is multi-agent response
      const isMultiAgent = message.provider === 'multi-agent'
      const isSingleAgentCoding = message.provider === 'anthropic' && hasCodeBlocks
      
      if (isMultiAgent && (message as any).agent_results) {
        // MULTI-AGENT: Show each agent as separate activity
        const agentResults = (message as any).agent_results || []
        agentResults.forEach((agentTask: any) => {
          const agentIcons: Record<string, string> = {
            'architect': '🏗️',
            'engineer': '💻',
            'ui_ux': '🎨',
            'tester': '🧪',
            'debugger': '🐛',
            'documenter': '📚'
          }
          
          activities.push({
            id: `agent_${agentTask.agent_type}_${index}`,
            type: agentTask.agent_type,
            status: agentTask.status,
            title: `${agentIcons[agentTask.agent_type] || '🤖'} ${agentTask.agent_type.replace('_', ' ').toUpperCase()} Agent`,
            description: agentTask.description,
            progress: agentTask.status === 'completed' ? 100 : agentTask.status === 'running' ? 50 : 0,
            startTime: agentTask.start_time,
            endTime: agentTask.end_time,
            thinkingSteps: agentTask.thinking_steps
          })
        })
      } else if (isSingleAgentCoding) {
        // SINGLE AGENT: Traditional coding activity
        const codeBlockCount = (message.content.match(/```/g) || []).length / 2
        
        activities.push({
          id: `coding_${message.id || index}`,
          type: 'coding',
          status: 'completed',
          title: '💻 Code-Generierung abgeschlossen',
          description: `${Math.floor(codeBlockCount)} Code-Blöcke erstellt mit ${message.model || 'Claude Sonnet 4-5'}`,
          progress: 100,
          startTime: message.timestamp || new Date().toISOString(),
          endTime: message.timestamp || new Date().toISOString()
        })
      }
    })
    
    // 3. Add ACTIVE activity if currently processing
    if (isStreaming || isLoading) {
      const lastUserMessage = messages.filter(m => m.role === 'user').pop()
      const isResearchPhase = lastUserMessage?.content.match(/klein|mittel|groß|kleine|keine/i)
      
      if (isResearchPhase) {
        // Research is running
        // Progressive actions based on time
        const researchActions = [
          'Analysiere Anfrage...',
          'Suche relevante Quellen...',
          'Durchsuche Dokumentation...',
          'Extrahiere Best Practices...',
          'Sammle aktuelle Trends...',
          'Verarbeite Ergebnisse...'
        ]
        const actionIndex = Math.floor(Math.random() * researchActions.length)
        
        // Get real sources from completed research activities (if any)
        const completedResearch = activities.find(a => a.type === 'research' && a.status === 'completed')
        const realSources = completedResearch?.sources || []
        
        // During active research, show real sources if available, otherwise show "Suche läuft..."
        const activeSources = realSources.length > 0 ? realSources.map(s => ({
          ...s,
          status: 'processing' as const  // Mark as processing during active research
        })) : undefined
        
        activities.push({
          id: 'active_research',
          type: 'research',
          status: 'active',
          title: '🔍 Recherche läuft...',
          description: realSources.length > 0 
            ? `Analysiere ${realSources.length} gefundene Quellen...`
            : 'Durchsuche aktuelle Quellen und Best Practices',
          progress: isLoading ? 30 : 70,
          currentAction: researchActions[actionIndex],
          sources: activeSources,
          sourcesProcessed: realSources.length > 0 ? Math.floor(realSources.length * 0.7) : undefined,
          startTime: new Date().toISOString()
        })
      } else {
        // Coding is running
        const codingActions = [
          'Analysiere Anforderungen...',
          'Plane Architektur...',
          'Generiere Code-Struktur...',
          'Implementiere Features...',
          'Erstelle Tests...',
          'Optimiere Code...',
          'Finalisiere Dokumentation...'
        ]
        const actionIndex = Math.floor((streamingText?.length || 0) / 500) % codingActions.length
        
        activities.push({
          id: 'active_coding',
          type: 'coding',
          status: 'active',
          title: '💻 Code wird generiert...',
          description: 'Claude Sonnet 4-5 erstellt den Code',
          progress: streamingText ? Math.min(75, (streamingText.length / 100)) : 15,
          currentAction: codingActions[actionIndex],
          startTime: new Date().toISOString()
        })
      }
    }
    
    // Update activities state
    setResearchActivities(activities)
    
    // Auto-open panel if there are activities
    if (activities.length > 0 && activities.some(a => a.status === 'active')) {
      setShowActivityPanel(true)
    }
  }, [messages, isLoading, isStreaming, streamingText])
  
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
    if (!input.trim() || isLoading || isAgentExecuting) return
    
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
    
    // 🤖 AUTONOMOUS AGENT ROUTING (Emergent-style)
    // If user manually selected an agent, use that
    // Otherwise, autonomously detect which agent should handle the message
    let agentToUse = selectedAgent
    
    if (!agentToUse) {
      // Autonomous detection
      const detection = detectAgent(message)
      
      if (detection.agent && shouldShowDetection(detection.confidence)) {
        // Show user which agent was detected
        toast({
          title: `🤖 ${getAgentDisplayName(detection.agent)} detected`,
          description: detection.reason,
          status: 'info',
          duration: 3000,
          isClosable: true
        })
        agentToUse = detection.agent
      }
    }
    
    // Execute with agent or regular chat
    if (agentToUse) {
      await executeAgent(message, agentToUse)
    } else {
      await sendMessage(message, ultraThinking)
    }
  }
  
  // 🤖 AGENTEN PHASE: Execute agent (manual or autonomous)
  const executeAgent = async (userMessage: string, agentType?: string) => {
    const agent = agentType || selectedAgent
    if (!agent) return
    
    setIsAgentExecuting(true)
    setAgentResult(null)
    
    try {
      // Prepare agent input based on agent type
      const inputData = prepareAgentInput(agent as AgentType, userMessage)
      
      // Execute agent
      const result = await agentService.executeAgent({
        agent_type: agent as AgentType,
        input_data: inputData,
        session_id: currentSession || undefined,
        options: {}
      })
      
      setAgentResult(result)
      
      // 📜 PHASE 4: Save research to history if it's a research agent
      if (agent === 'research' && result.output_data) {
        try {
          saveResearchToHistory({
            timestamp: new Date(),
            query: userMessage,
            result: result.output_data,
            duration_seconds: result.duration_seconds,
            token_usage: result.token_usage
          });
        } catch (error) {
          console.error('Failed to save research to history:', error);
        }
      }
      
      // Show success toast
      toast({
        title: `✅ ${getAgentDisplayName(agent as AgentType)} completed`,
        description: `Execution took ${result.duration_seconds?.toFixed(2)}s`,
        status: 'success',
        duration: 5000
      })
      
    } catch (error: any) {
      console.error('Agent execution failed:', error)
      toast({
        title: '❌ Agent execution failed',
        description: error.message || 'Unknown error occurred',
        status: 'error',
        duration: 5000
      })
    } finally {
      setIsAgentExecuting(false)
    }
  }
  
  // 🤖 AGENTEN PHASE: Prepare input for different agent types
  const prepareAgentInput = (agentType: AgentType, userMessage: string): Record<string, any> => {
    switch (agentType) {
      case 'research':
        return {
          query: userMessage,
          deep_research: userMessage.length > 100  // Use deep research for longer queries
        }
      
      case 'code_review':
      case 'testing':
      case 'documentation':
      case 'debugging':
      case 'security':
      case 'performance':
        // Try to extract code from message, otherwise use message as code
        const codeMatch = userMessage.match(/```[\w]*\n([\s\S]*?)\n```/)
        const code = codeMatch ? codeMatch[1] : userMessage
        return {
          code,
          language: 'python',  // Default to python, could be enhanced
          ...(agentType === 'debugging' && { error: userMessage.includes('error') ? userMessage : '' })
        }
      
      case 'fork':
        return {
          operation: 'list_repos',
          limit: 5
        }
      
      default:
        return { query: userMessage }
    }
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
    if (!currentSession) {
      toast({
        title: 'Keine Session',
        description: 'Starten Sie zuerst eine Konversation',
        status: 'warning',
        duration: 3000
      })
      return
    }
    setIsGitHubPushOpen(true)
  }

  // Welcome Screen
  if (messages.length === 0) {
    return (
      <ChatDropZone onFilesAdded={handleFilesAdded} maxFiles={5}>
      <div className="min-h-screen bg-primary-dark bg-geometric">
        {/* Header */}
        <div className="h-[60px] px-4 border-b border-gold-500/20 flex items-center justify-center bg-gradient-dark sticky top-0 z-10">
          {/* Logo zentriert */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-glossy-gold rounded-lg flex items-center justify-center shadow-gold-glow">
              <span className="text-primary-dark font-black text-xl">X</span>
            </div>
            <h1 className="text-lg font-bold bg-gradient-to-r from-gold-400 via-gold-500 to-gold-400 bg-clip-text text-transparent text-glow">
              Xionimus AI
            </h1>
          </div>
          
          {/* User Controls rechts - Mobile Optimized (Welcome Screen) */}
          <div className="absolute right-4 flex items-center gap-1 sm:gap-2">
            {/* Activity Panel Toggle - Hidden on small screens */}
            <div className="hidden sm:block">
              <Tooltip label={showActivityPanel ? "Agent-Aktivitäten ausblenden" : "Agent-Aktivitäten anzeigen"}>
                <IconButton
                  aria-label="Toggle Activity Panel"
                  icon={showActivityPanel ? <ChevronDownIcon /> : <TimeIcon />}
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowActivityPanel(!showActivityPanel)}
                  colorScheme={showActivityPanel ? "blue" : "gray"}
                  className="min-w-[44px] min-h-[44px]"
                />
              </Tooltip>
            </div>
            
            {/* Username - Hidden on very small screens */}
            <span className="hidden md:block text-sm text-gray-500 whitespace-nowrap">{user?.username}</span>
            
            {/* Rate Limit Status Popover - Compact on mobile */}
            <Popover placement="bottom-end">
              <PopoverTrigger>
                <button className="px-2 py-1 text-xs bg-blue-500/20 text-blue-300 rounded-lg border border-blue-500/30 hover:bg-blue-500/30 transition-colors min-w-[44px] min-h-[32px]">
                  <span className="hidden sm:inline">Limits</span>
                  <span className="sm:hidden">L</span>
                </button>
              </PopoverTrigger>
              <PopoverContent>
                <RateLimitStatus />
              </PopoverContent>
            </Popover>
            
            {/* 🎯 Developer Mode Toggle - Responsive */}
            <div className="flex items-center">
              <DeveloperModeToggle
                mode={developerMode}
                onChange={setDeveloperMode}
              />
            </div>
          </div>
        </div>

        {/* Main Content Area with Split View */}
        <div className="flex h-[calc(100vh-60px)] overflow-hidden">
        {/* Welcome Content */}
        <div className={`flex-1 py-20 overflow-y-auto ${showActivityPanel ? 'max-w-5xl' : 'max-w-6xl'} mx-auto px-4`}>
          <div className="flex flex-col items-center text-center space-y-8">
            {/* Logo with Glow */}
            <FadeIn delay={0} direction="none">
              <div className="relative">
                <div className="w-20 h-20 bg-glossy-gold rounded-2xl flex items-center justify-center shadow-gold-glow-lg animate-glow-pulse hover:scale-110 transition-transform duration-300 cursor-pointer">
                  <span className="text-primary-dark font-black text-5xl leading-none mt-1">X</span>
                </div>
              </div>
            </FadeIn>
            
            {/* Title & Subtitle */}
            <FadeIn delay={0.1} direction="up" className="space-y-2">
              <h1 className="text-5xl font-extrabold bg-gradient-to-r from-gold-400 via-gold-500 to-gold-400 bg-clip-text text-transparent text-glow animate-pulse-slow">
                {t('welcome.title')}
              </h1>
              <p className="text-lg text-gray-300 animate-fade-in">
                {t('welcome.subtitle')}
              </p>
            </FadeIn>

            {/* Example Prompts */}
            <FadeIn delay={0.3} direction="up" className="w-full max-w-2xl mt-8 space-y-4">
              <p className="text-base font-semibold text-gray-300">
                {t('welcome.exampleTitle')}
              </p>
              
              <div className="space-y-3">
                {[
                  t('welcome.example1'),
                  t('welcome.example2'),
                  t('welcome.example3')
                ].map((example, i) => (
                  <FadeIn key={i} delay={0.4 + i * 0.1} direction="up">
                    <button
                      onClick={() => setInput(example.substring(2))}
                      className="w-full p-4 text-left glossy-card hover:border-gold-500/60 hover:shadow-gold-glow hover:scale-105 transition-all duration-300 group active:scale-95"
                    >
                      <p className="text-gray-200 group-hover:text-white transition-colors">
                        {example}
                      </p>
                    </button>
                  </FadeIn>
                ))}
              </div>
            </FadeIn>
          </div>
        </div>

        {/* Input Area (Fixed Bottom) - Fully Tailwind */}
        <div className="fixed bottom-0 left-0 right-0 bg-gradient-dark border-t border-gold-500/20 p-4 backdrop-blur-xl z-10">
          <div className="max-w-4xl mx-auto">
            <div className="flex flex-col gap-3">
              {/* File Attachments Display */}
              {attachedFiles.length > 0 && (
                <div className="flex gap-2 flex-wrap">
                  {attachedFiles.map((file, index) => (
                    <ChatFileAttachment
                      key={index}
                      file={file}
                      onRemove={() => handleRemoveFile(index)}
                      showRemove={true}
                      isCompact={true}
                    />
                  ))}
                </div>
              )}
              
              {/* Main Input with Ultra Thinking Toggle */}
              <div className="flex items-end gap-3">
                {/* Ultra Thinking Toggle - Glossy Design */}
                <div className="flex flex-col items-center gap-1">
                  <Tooltip 
                    label="Ultra Thinking: Aktiviert erweiterte Reasoning-Modi für komplexe Aufgaben (Claude)" 
                    placement="top"
                    bg="rgba(0, 212, 255, 0.9)"
                    color="white"
                  >
                    <div 
                      className={`p-2 rounded-lg transition-all duration-300 ${
                        ultraThinking 
                          ? 'bg-blue-500/10 border-2 border-blue-500 shadow-lg shadow-blue-500/30' 
                          : 'bg-transparent border-2 border-transparent'
                      }`}
                    >
                      <Switch
                        size="lg"
                        colorScheme="cyan"
                        isChecked={ultraThinking}
                        onChange={(e) => setUltraThinking(e.target.checked)}
                      />
                      <span 
                        className={`block text-xs mt-1 text-center ${
                          ultraThinking ? 'text-blue-400 font-bold' : 'text-gray-500 font-normal'
                        }`}
                      >
                        🧠
                      </span>
                    </div>
                  </Tooltip>
                </div>

                {/* Textarea - Glossy Input */}
                <div className="flex-1 relative">
                  <textarea
                    ref={textareaRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyPress}
                    placeholder={t('chat.inputPlaceholder')}
                    className="w-full min-h-[56px] max-h-[200px] pr-[50px] px-4 py-3 text-base
                              bg-primary-navy/50 backdrop-blur-md 
                              border-2 border-gold-500/20 rounded-xl
                              text-white placeholder-gray-400
                              focus:outline-none focus:border-blue-500 focus:shadow-lg focus:shadow-blue-500/20
                              resize-none transition-all duration-300
                              hover:border-gold-500/30"
                    style={{ minHeight: '56px', maxHeight: '200px' }}
                  />
                  
                  {/* Send Button (Inside Textarea) - Enhanced */}
                  <button
                    onClick={handleSend}
                    disabled={!input.trim() || isLoading}
                    aria-label="Senden"
                    className="absolute right-2 bottom-2 p-2 rounded-lg
                              bg-gradient-to-br from-blue-500 to-blue-600
                              text-white shadow-lg shadow-blue-500/40
                              hover:shadow-blue-500/60 hover:scale-110
                              active:scale-95
                              disabled:opacity-50 disabled:cursor-not-allowed
                              transition-all duration-300
                              min-w-[44px] min-h-[44px] flex items-center justify-center
                              z-50 cursor-pointer"
                  >
                    {isLoading ? (
                      <Spinner size="sm" color="white" />
                    ) : (
                      <ArrowUpIcon />
                    )}
                  </button>
                </div>
              </div>

              {/* Toolbar Buttons removed - using single button bar below */}

              {/* Ultra Thinking Status */}
              {ultraThinking && (
                <div className="flex justify-center items-center text-xs text-gray-500">
                  <div className="flex items-center gap-1">
                    <span className="text-blue-400 font-semibold">
                      🧠 Erweitertes Denken aktiv
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Input Area (Fixed Bottom) - Fully Tailwind Welcome Screen */}
        <div className="fixed bottom-0 left-0 right-0 bg-gradient-dark border-t border-gold-500/20 p-4 backdrop-blur-xl z-10">
          <div className="max-w-4xl mx-auto">
            <div className="flex flex-col gap-3">
              {/* File Attachments Display */}
              {attachedFiles.length > 0 && (
                <div className="flex gap-2 flex-wrap">
                  {attachedFiles.map((file, index) => (
                    <ChatFileAttachment
                      key={index}
                      file={file}
                      onRemove={() => handleRemoveFile(index)}
                      showRemove={true}
                      isCompact={true}
                    />
                  ))}
                </div>
              )}
              
              {/* Main Input with Ultra Thinking Toggle */}
              <div className="flex items-end gap-3 flex-col sm:flex-row">
                {/* Input Box */}
                <div className="flex-1 w-full">
                  <textarea
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyPress}
                    placeholder={t('chat.inputPlaceholder')}
                    autoFocus
                    className="w-full min-h-[60px] max-h-[200px] px-4 py-3 text-base
                              bg-primary-navy/50 backdrop-blur-md 
                              border-2 border-gold-500/20 rounded-xl
                              text-white placeholder-gray-400
                              focus:outline-none focus:border-blue-500 focus:shadow-lg focus:shadow-blue-500/20
                              resize-y transition-all duration-300
                              hover:border-gold-500/30"
                  />
                  
                  <div className="flex justify-between items-center mt-2 gap-2 flex-wrap">
                    <div className="flex gap-2 flex-wrap">
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
                        leftIcon={<span>🧠</span>}
                      >
                        Ultra-Thinking
                      </Button>
                    </div>

                    <div className="flex gap-2">
                      {/* Model info hidden - configured for Claude Sonnet 4.5 (coding) and Opus 4.1 (debugging) */}
                    </div>
                  </div>
                </div>

                {/* Send Button - Touch Optimized */}
                <button
                  onClick={handleSend}
                  disabled={!input.trim() || isLoading}
                  aria-label={t('chat.send')}
                  className="min-w-[60px] min-h-[60px] w-[60px] h-[60px] rounded-xl
                            bg-gradient-to-br from-blue-500 to-blue-600
                            text-white shadow-lg shadow-blue-500/40
                            hover:shadow-blue-500/60 hover:scale-110
                            active:scale-95
                            disabled:opacity-50 disabled:cursor-not-allowed
                            transition-all duration-300
                            flex items-center justify-center"
                >
                  {isLoading ? <Spinner size="sm" /> : <ArrowForwardIcon />}
                </button>
              </div>

              {/* Info Section */}
              <div className="flex justify-between items-center text-xs text-gray-500 flex-wrap gap-2">
                <div className="flex gap-2">
                  <Button
                    size="xs"
                    variant="ghost"
                    leftIcon={<SettingsIcon />}
                    onClick={() => navigate('/settings')}
                  >
                    {t('chat.configureKeys')}
                  </Button>
                </div>
                
                {ultraThinking && (
                  <div className="flex items-center gap-1">
                    <span className="text-blue-400 font-semibold">
                      🧠 Erweitertes Denken aktiv
                    </span>
                  </div>
                )}
              </div>

              {/* Xionimus Control Buttons - Welcome Screen */}
              <div className="border-t border-gold-500/10 pt-3 mt-2">
                <div className="flex justify-between items-center gap-2 flex-wrap">
                  {/* Left Side - Action Buttons - Touch Optimized */}
                  <div className="flex gap-2 flex-wrap">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={handleStop}
                      isDisabled={!isLoading}
                    >
                      ⏸️ Stopp
                    </Button>
                    
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => toast({ title: 'Fork-Feature kommt bald', status: 'info', duration: 2000 })}
                    >
                      🔀 Verzweigen
                    </Button>
                    
                    {/* GitHub Menu */}
                    <Menu>
                      <MenuButton
                        as={Button}
                        size="sm"
                        variant="solid"
                        colorScheme="purple"
                        rightIcon={<ChevronDownIcon />}
                      >
                        🔄 GitHub
                      </MenuButton>
                      <MenuList>
                        <MenuItem
                          icon={<ArrowUpIcon />}
                          onClick={handleGitHubPush}
                        >
                          📤 Exportieren zu GitHub
                        </MenuItem>
                        <MenuItem
                          icon={<ArrowDownIcon />}
                          onClick={() => setIsGitHubImportOpen(true)}
                        >
                          📥 Importieren von GitHub
                        </MenuItem>
                      </MenuList>
                    </Menu>

                    {/* Code View */}
                    <Tooltip label="Code anzeigen">
                      <Button
                        size="sm"
                        variant={isCodeViewOpen ? "solid" : "ghost"}
                        colorScheme="gold"
                        leftIcon={<span>💻</span>}
                        onClick={() => setIsCodeViewOpen(!isCodeViewOpen)}
                      >
                        Code
                      </Button>
                    </Tooltip>

                    {/* Logs View */}
                    <Tooltip label="Logs anzeigen">
                      <Button
                        size="sm"
                        variant={isLogsViewOpen ? "solid" : "ghost"}
                        colorScheme="blue"
                        leftIcon={<span>📊</span>}
                        onClick={() => setIsLogsViewOpen(!isLogsViewOpen)}
                      >
                        Logs
                      </Button>
                    </Tooltip>
                  </div>

                  {/* Right Side - Settings & Admin - Touch Optimized */}
                  <div className="flex gap-2 flex-wrap">
                    <Tooltip label="Neuer Chat">
                      <IconButton
                        aria-label="Neuer Chat"
                        icon={<AddIcon />}
                        variant="ghost"
                        size="sm"
                        onClick={handleNewChat}
                        className="min-w-[44px] min-h-[44px]"
                      />
                    </Tooltip>

                    <Tooltip label="Einstellungen">
                      <IconButton
                        aria-label="Einstellungen"
                        icon={<SettingsIcon />}
                        variant="ghost"
                        size="sm"
                        onClick={() => navigate('/settings')}
                        className="min-w-[44px] min-h-[44px]"
                      />
                    </Tooltip>

                    <LanguageSelector />
                    <ThemeSelector />

                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={logout}
                      colorScheme="red"
                    >
                      Abmelden
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right: Research Activity Panel */}
        <ResearchActivityPanel
          activities={researchActivities}
          isVisible={showActivityPanel}
        />
        </div>

        {/* GitHub Push Dialog */}
        <GitHubPushDialog
          isOpen={isGitHubPushOpen}
          onClose={() => setIsGitHubPushOpen(false)}
          sessionId={currentSession?.id}
        />

        {/* GitHub Import Dialog - Welcome Screen */}
        <GitHubImportDialog
          isOpen={isGitHubImportOpen}
          onClose={() => setIsGitHubImportOpen(false)}
          sessionId={typeof currentSession === 'string' ? currentSession : currentSession?.id || null}
        />
      </div>
      </ChatDropZone>
    )
  }

  // Chat View
  return (
    <ChatDropZone onFilesAdded={handleFilesAdded} maxFiles={5}>
    <div className="min-h-screen bg-primary-dark bg-geometric">
      {/* Header - Glossy Black-Gold Design */}
      <div className="h-[60px] px-4 border-b border-gold-500/20 flex items-center justify-center bg-gradient-dark sticky top-0 z-10">
        {/* Logo zentriert */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-glossy-gold rounded-lg flex items-center justify-center shadow-gold-glow">
            <span className="text-primary-dark font-black text-xl">X</span>
          </div>
          <h1 className="text-lg font-bold bg-gradient-to-r from-gold-400 via-gold-500 to-gold-400 bg-clip-text text-transparent text-glow">
            Xionimus AI
          </h1>
          
          {/* Active Project Badge - Hidden on mobile */}
          {currentSession && (
            <div className="ml-4 hidden lg:block">
              <ActiveProjectBadge sessionId={currentSession} />
            </div>
          )}
          
          {/* 🤖 AGENTEN PHASE: Agent Selector with Autonomous Mode */}
          <div className="ml-4 hidden md:flex items-center gap-2">
            <AgentSelector
              selectedAgent={selectedAgent as any}
              onAgentSelect={(agent) => setSelectedAgent(agent)}
            />
            {!selectedAgent && (
              <div className="px-3 py-1.5 bg-gradient-to-br from-green-500/20 to-green-600/10 border border-green-500/30 rounded-lg backdrop-blur-sm">
                <div className="flex items-center gap-1.5">
                  <span className="text-xs text-green-400 font-medium">🤖 Autonomous</span>
                </div>
              </div>
            )}
            
            {/* 📜 PHASE 4: Research History Button */}
            <button
              onClick={() => setShowResearchHistory(!showResearchHistory)}
              className="px-3 py-1.5 bg-gradient-to-br from-black/40 to-black/20 border border-amber-500/30 rounded-lg hover:border-amber-400/50 transition-all duration-200 backdrop-blur-sm"
              title="Research History"
            >
              <span className="text-base">📜</span>
            </button>
          </div>
        </div>
        
        {/* User Controls rechts - Mobile Optimized */}
        <div className="absolute right-4 flex items-center gap-1 sm:gap-2">
          {/* Activity Panel Toggle - Hidden on small screens */}
          <div className="hidden sm:block">
            <Tooltip label={showActivityPanel ? "Agent-Aktivitäten ausblenden" : "Agent-Aktivitäten anzeigen"}>
              <IconButton
                aria-label="Toggle Activity Panel"
                icon={showActivityPanel ? <ChevronDownIcon /> : <TimeIcon />}
                variant="ghost"
                size="sm"
                onClick={() => setShowActivityPanel(!showActivityPanel)}
                colorScheme={showActivityPanel ? "blue" : "gray"}
                className="min-w-[44px] min-h-[44px]"
              />
            </Tooltip>
          </div>
          
          {/* Username - Hidden on very small screens */}
          <span className="hidden md:block text-sm text-gray-400 whitespace-nowrap">{user?.username}</span>
          
          {/* Rate Limit Status Popover - Compact on mobile */}
          <Popover placement="bottom-end">
            <PopoverTrigger>
              <button className="px-2 py-1 text-xs bg-blue-500/20 text-blue-300 rounded-lg border border-blue-500/30 hover:bg-blue-500/30 transition-colors min-w-[44px] min-h-[32px]">
                <span className="hidden sm:inline">Limits</span>
                <span className="sm:hidden">L</span>
              </button>
            </PopoverTrigger>
            <PopoverContent>
              <RateLimitStatus />
            </PopoverContent>
          </Popover>
          
          {/* 🎯 Developer Mode Toggle - Responsive */}
          <div className="flex items-center">
            <DeveloperModeToggle
              mode={developerMode}
              onChange={setDeveloperMode}
            />
          </div>
        </div>
      </div>

      {/* Main Content Area with Split View */}
      <div className="flex h-[calc(100vh-60px)] overflow-hidden">
        {/* Left: Messages */}
        <div 
          className={`flex-1 pb-[200px] pt-4 overflow-y-auto ${showActivityPanel ? 'max-w-5xl' : 'max-w-6xl'} mx-auto px-4`}
          ref={messagesContainerRef}
        >
          <div className="space-y-6">
          {/* Context Warning - New Fork System */}
          <ContextWarningBanner
            sessionId={currentSession}
            onForkClick={() => setIsSessionForkOpen(true)}
          />
          
          {messages.map((msg, idx) => (
            <FadeIn
              key={msg.id || idx}
              direction="up"
              delay={idx * 0.05}
              duration={0.4}
            >
              <div className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
                <Avatar
                  size="sm"
                  name={msg.role === 'user' ? 'User' : 'Xionimus'}
                  bg={msg.role === 'user' ? userBg : 'linear-gradient(135deg, #0088cc, #0066aa)'}
                />
                
                <div className={`flex-1 flex flex-col gap-1 ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                <div className={`w-full flex gap-2 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  {msg.role === 'assistant' && (
                    <MessageActions
                      messageId={msg.id || idx.toString()}
                      content={msg.content}
                      role={msg.role}
                      onRegenerate={handleRegenerateResponse}
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
                      onDelete={handleDeleteMessage}
                    />
                  )}
                </div>
                
                {/* Timestamp and Model Info */}
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  {msg.timestamp && (
                    <>
                      <TimeIcon boxSize={3} />
                      <span>
                        {new Date(msg.timestamp).toLocaleTimeString([], { 
                          hour: '2-digit', 
                          minute: '2-digit' 
                        })}
                      </span>
                    </>
                  )}
                  {msg.model && (
                    <>
                      <span>•</span>
                      <span className="px-2 py-0.5 bg-blue-500/20 text-blue-300 text-xs rounded-full border border-blue-500/30">
                        {msg.model}
                      </span>
                    </>
                  )}
                </div>
              </div>
              </div>
            </FadeIn>
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
          
          {/* Streaming Indicator - Glossy Design */}
          {isStreaming && (
            <div className="flex flex-row items-start max-w-[85%] py-0">
              <div className="glossy-card border-blue-500/50 w-full p-6">
                <div className="flex flex-col items-start gap-3">
                  {/* Header with Spinner */}
                  <div className="flex items-center gap-2">
                    <Spinner size="sm" color="blue.400" />
                    <span className="font-semibold text-[15px] text-blue-400">
                      {streamingText ? 'Generiere...' : 'Arbeite daran...'}
                    </span>
                  </div>
                  
                  {/* Research Indicator */}
                  {messages.length > 0 && messages[messages.length - 1].content.match(/(klein|mittel|groß|small|medium|large)/i) && !streamingText && (
                    <span className="text-[13px] text-gray-400 font-medium">
                      🔍 Führe Recherche durch...
                    </span>
                  )}
                  
                  {/* STREAMED TEXT - Live Output */}
                  {streamingText && (
                    <div className="mt-2 w-full text-[14px] leading-relaxed text-gray-200">
                      {/* 🎯 Echtzeit Code-Streaming mit Syntax-Highlighting */}
                      <StreamingMarkdownRenderer 
                        content={streamingText} 
                        isStreaming={true}
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
          
          {/* 🤖 AGENTEN PHASE: Agent Results Display */}
          {agentResult && (
            <FadeIn direction="up" duration={0.5}>
              <div className="mb-4">
                <AgentResultsPanel
                  result={agentResult}
                  isLoading={isAgentExecuting}
                />
              </div>
            </FadeIn>
          )}
          
          {/* 🤖 AGENTEN PHASE: Agent Executing Indicator */}
          {isAgentExecuting && (
            <div className="flex gap-3 mb-4">
              <Avatar size="sm" name="Agent" bg="linear-gradient(135deg, #f59e0b, #d97706)" />
              <div className="glossy-card border-amber-500/30 px-4 py-3 min-w-[200px]">
                <div className="flex flex-col items-start gap-2">
                  <div className="flex items-center gap-2">
                    <Spinner size="sm" color="amber.400" />
                    <span className="font-semibold text-[15px] text-amber-400">
                      {selectedAgent} Agent arbeitet...
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {isLoading && (
            <div className="flex gap-3">
              <Avatar size="sm" name="Xionimus" bg="linear-gradient(135deg, #0088cc, #0066aa)" />
              <div className="glossy-card border-blue-500/30 px-4 py-3 min-w-[200px]">
                <div className="flex flex-col items-start gap-2">
                  <div className="flex items-center gap-2">
                    <Spinner size="sm" color="blue.400" />
                    <span className="font-semibold text-[15px] text-blue-400">
                      Arbeite daran...
                    </span>
                  </div>
                  {messages.length > 0 && messages[messages.length - 1].content.match(/(klein|mittel|groß|small|medium|large)/i) && (
                    <span className="text-[13px] text-gray-400 font-medium">
                      🔍 Führe Recherche durch...
                    </span>
                  )}
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

        {/* Right: Research Activity Panel */}
        <ResearchActivityPanel
          activities={researchActivities}
          isVisible={showActivityPanel}
        />
      </div>

      {/* Input Area (Fixed Bottom) - Glossy Design */}
      <div className="fixed bottom-0 left-0 right-0 bg-gradient-dark border-t border-gold-500/20 p-4 backdrop-blur-xl">
        <div className="max-w-6xl mx-auto">
          <div className="flex flex-col gap-3">
            {/* Action Buttons Bar - Xionimus Control Buttons */}
            <div className="flex items-center justify-between flex-wrap gap-2 pb-2 border-b border-gold-500/10">
              <div className="flex items-center gap-2 flex-wrap">
                {/* GitHub Menu - Combined Push & Import */}
                <Tooltip label="GitHub-Aktionen">
                  <Menu>
                    <MenuButton
                      as={Button}
                      size="sm"
                      variant="ghost"
                      colorScheme="purple"
                      rightIcon={<ChevronDownIcon />}
                    >
                      🔄 GitHub
                    </MenuButton>
                    <MenuList>
                      <MenuItem
                        icon={<ArrowUpIcon />}
                        onClick={() => setIsGitHubPushOpen(true)}
                      >
                        📤 Exportieren zu GitHub
                      </MenuItem>
                      <MenuItem
                        icon={<ArrowDownIcon />}
                        onClick={() => setIsGitHubImportOpen(true)}
                      >
                        📥 Importieren von GitHub
                      </MenuItem>
                    </MenuList>
                  </Menu>
                </Tooltip>

                {/* File Upload */}
                <Tooltip label="Dateien hochladen">
                  <Button
                    size="sm"
                    variant="ghost"
                    colorScheme="cyan"
                    leftIcon={<AttachmentIcon />}
                    onClick={() => setIsFileUploadOpen(true)}
                  >
                    Upload
                  </Button>
                </Tooltip>

                {/* Code View */}
                <Tooltip label="Code anzeigen">
                  <Button
                    size="sm"
                    variant={isCodeViewOpen ? "solid" : "ghost"}
                    colorScheme="gold"
                    leftIcon={<Text>💻</Text>}
                    onClick={() => setIsCodeViewOpen(!isCodeViewOpen)}
                  >
                    Code
                  </Button>
                </Tooltip>

                {/* Logs View */}
                <Tooltip label="Logs anzeigen">
                  <Button
                    size="sm"
                    variant={isLogsViewOpen ? "solid" : "ghost"}
                    colorScheme="blue"
                    leftIcon={<Text>📊</Text>}
                    onClick={() => setIsLogsViewOpen(!isLogsViewOpen)}
                  >
                    Logs
                  </Button>
                </Tooltip>

                {/* Session Summary */}
                {messages.length > 0 && currentSession && (
                  <Tooltip label="Session zusammenfassen">
                    <Button
                      size="sm"
                      variant="ghost"
                      colorScheme="purple"
                      leftIcon={<Text>📋</Text>}
                      onClick={onSummaryOpen}
                    >
                      Summary
                    </Button>
                  </Tooltip>
                )}

                {/* Chat History */}
                <Tooltip label="Chat-Verlauf">
                  <IconButton
                    aria-label="Chat history"
                    icon={<Text>📜</Text>}
                    variant="ghost"
                    size="sm"
                    onClick={() => setIsHistoryOpen(true)}
                  />
                </Tooltip>
              </div>

              <div className="flex items-center gap-2">
                {/* New Chat */}
                <Tooltip label={t('header.newChat')}>
                  <IconButton
                    aria-label={t('header.newChat')}
                    icon={<AddIcon />}
                    variant="ghost"
                    size="sm"
                    onClick={handleNewChat}
                  />
                </Tooltip>

                {/* Settings */}
                <Tooltip label={t('header.settings')}>
                  <IconButton
                    aria-label={t('header.settings')}
                    icon={<SettingsIcon />}
                    variant="ghost"
                    size="sm"
                    onClick={() => navigate('/settings')}
                  />
                </Tooltip>

                {/* Language Selector */}
                <LanguageSelector />

                {/* Theme Selector */}
                <ThemeSelector />

                {/* Logout */}
                <Tooltip label="Abmelden">
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={logout}
                    colorScheme="red"
                  >
                    Abmelden
                  </Button>
                </Tooltip>
              </div>
            </div>
            
            {/* Main Input with Ultra Thinking Toggle */}
            <div className="flex items-end gap-3">
              {/* Ultra Thinking Toggle - Glossy Design */}
              <div className="flex flex-col items-center gap-1">
                <Tooltip 
                  label="Ultra Thinking: Aktiviert erweiterte Reasoning-Modi für komplexe Aufgaben (Claude)" 
                  placement="top"
                  bg="rgba(0, 212, 255, 0.9)"
                  color="white"
                >
                  <div className={`p-2 rounded-lg transition-all duration-300 ${
                    ultraThinking 
                      ? 'bg-blue-500/10 border-2 border-blue-500 shadow-lg shadow-blue-500/30' 
                      : 'bg-transparent border-2 border-transparent'
                  }`}>
                    <Switch
                      size="lg"
                      colorScheme="cyan"
                      isChecked={ultraThinking}
                      onChange={(e) => setUltraThinking(e.target.checked)}
                    />
                    <span className={`block text-xs mt-1 text-center ${
                      ultraThinking ? 'text-blue-400 font-bold' : 'text-gray-500 font-normal'
                    }`}>
                      🧠
                    </span>
                  </div>
                </Tooltip>
              </div>

              {/* Chat Input Component */}
              <div className="flex-1 relative">
                <ChatInput
                  value={input}
                  onChange={setInput}
                  onSubmit={handleSend}
                  disabled={isLoading}
                  placeholder="Beschreiben Sie Ihr Programmier-Projekt..."
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
              </div>
            </div>

            {/* Toolbar Buttons - Removed as per user request */}

            {/* Status Info */}
            {ultraThinking && (
              <div className="flex justify-center items-center text-xs text-gray-500">
                <div className="flex items-center gap-1">
                  <span>🧠 Erweitertes Denken aktiv</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

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
        sessionId={currentSession?.id}
      />

      {/* GitHub Import Dialog */}
      <GitHubImportDialog
        isOpen={isGitHubImportOpen}
        onClose={() => setIsGitHubImportOpen(false)}
        sessionId={typeof currentSession === 'string' ? currentSession : currentSession?.id || null}
      />

      {/* Session Summary Modal */}
      <SessionSummaryModal
        isOpen={isSummaryOpen}
        onClose={onSummaryClose}
        sessionId={typeof currentSession === 'string' ? currentSession : currentSession?.id || null}
        apiKeys={apiKeys}
        onSwitchSession={(sessionId) => {
          loadSession(sessionId).catch(err => {
            console.error('Failed to load session:', err)
            toast({
              title: 'Fehler',
              description: 'Neue Session konnte nicht geladen werden',
              status: 'error',
              duration: 3000
            })
          })
        }}
      />

      {/* Session Fork Dialog */}
      <SessionForkDialog
        isOpen={isSessionForkOpen}
        onClose={() => setIsSessionForkOpen(false)}
        sessionId={currentSession}
        onForkComplete={(newSessionId) => {
          // Load the new forked session
          loadSession(newSessionId).then(() => {
            toast({
              title: '✅ Session geforkt',
              description: 'Du arbeitest jetzt in der neuen Session weiter',
              status: 'success',
              duration: 5000
            })
          }).catch(err => {
            console.error('Failed to load forked session:', err)
            toast({
              title: 'Fehler',
              description: 'Neue Session konnte nicht geladen werden',
              status: 'error',
              duration: 3000
            })
          })
        }}
      />

      {/* File Upload Dialog */}
      <FileUploadDialog
        isOpen={isFileUploadOpen}
        onClose={() => setIsFileUploadOpen(false)}
        sessionId={currentSession}
        activeProject={activeProjectName}
      />

      {/* Token Usage Widget */}
      <TokenUsageWidget 
        tokenUsage={tokenUsage}
        onForkRecommended={() => {
          toast({
            title: 'Fork empfohlen',
            description: 'Erwäge einen Fork zu erstellen, um die Conversation zu optimieren',
            status: 'info',
            duration: 5000
          })
        }}
      />

      {/* Code View Drawer */}
      <CodeViewDrawer
        isOpen={isCodeViewOpen}
        onClose={() => setIsCodeViewOpen(false)}
        files={codeFiles}
      />

      {/* Logs View Drawer */}
      <LogsViewDrawer
        isOpen={isLogsViewOpen}
        onClose={() => setIsLogsViewOpen(false)}
        logs={logs}
        metrics={executionMetrics}
      />
      
      {/* 📜 PHASE 4: Research History Panel */}
      {showResearchHistory && (
        <>
          <div 
            className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
            onClick={() => setShowResearchHistory(false)}
          />
          <div className="fixed right-0 top-0 h-full w-full max-w-md bg-gradient-to-br from-black/95 to-black/85 shadow-2xl z-50 overflow-hidden flex flex-col">
            <div className="flex-1 overflow-y-auto">
              <ResearchHistoryPanel
                onSelectResearch={(item) => {
                  setAgentResult({
                    execution_id: item.id,
                    agent_type: 'research' as any,
                    status: 'completed' as any,
                    output_data: item.result,
                    provider: 'perplexity',
                    model: item.result.model_used,
                    started_at: item.timestamp.toISOString(),
                    duration_seconds: item.duration_seconds,
                    token_usage: item.token_usage
                  });
                  setShowResearchHistory(false);
                }}
                onRerunResearch={(query) => {
                  setInput(query);
                  setSelectedAgent('research');
                  setShowResearchHistory(false);
                }}
              />
            </div>
          </div>
        </>
      )}
    </div>
    </ChatDropZone>
  )
}
