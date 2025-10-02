import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { useToast } from '@chakra-ui/react'
import axios from 'axios'

interface ChatMessage {
  id?: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: Date
  provider?: string
  model?: string
  usage?: any
  agent_results?: Array<{
    agent: string
    icon: string
    content: string
    summary: string
    data?: any
  }>
}

interface ChatSession {
  id: string
  session_id?: string  // Keep for backward compatibility
  name: string
  createdAt: string
  created_at?: Date  // Keep for backward compatibility
  updatedAt?: string
  updated_at?: Date  // Keep for backward compatibility
  messages: ChatMessage[]
  message_count?: number
  last_message?: string
}

interface User {
  user_id: string
  username: string
  email: string
  role?: string
}

interface AppContextType {
  // Authentication
  user: User | null
  isAuthenticated: boolean
  token: string | null
  login: (username: string, password: string) => Promise<void>
  register: (username: string, email: string, password: string) => Promise<void>
  logout: () => void
  
  // Chat State
  messages: ChatMessage[]
  currentSession: string | ChatSession | null
  sessions: ChatSession[]
  isLoading: boolean
  isStreaming: boolean  // New: Streaming state
  streamingText: string  // New: Current streaming text
  
  // AI Settings
  selectedProvider: string
  selectedModel: string
  availableProviders: Record<string, boolean>
  availableModels: Record<string, string[]>
  autoAgentSelection: boolean  // New: Intelligent agent selection
  useStreaming: boolean  // New: Toggle streaming on/off
  
  // API Keys
  apiKeys: {
    openai: string
    anthropic: string
    perplexity: string
  }
  
  // Actions
  sendMessage: (content: string, ultraThinking?: boolean) => Promise<void>
  stopGeneration: () => void
  loadSession: (sessionId: string) => Promise<void>
  createNewSession: () => void
  deleteSession: (sessionId: string) => Promise<void>
  switchSession: (sessionId: string) => void
  renameSession: (sessionId: string, newName: string) => void
  updateApiKeys: (keys: Partial<{openai: string, anthropic: string, perplexity: string}>) => void
  setSelectedProvider: (provider: string) => void
  setSelectedModel: (model: string) => void
  setAutoAgentSelection: (enabled: boolean) => void  // New: Toggle intelligent selection
  setUseStreaming: (enabled: boolean) => void  // New: Toggle streaming
  updateMessages: (newMessages: ChatMessage[]) => void  // New: Update messages directly
  
  // Data Loading
  loadSessions: () => Promise<void>
  loadProviders: () => Promise<void>
}

const AppContext = createContext<AppContextType | undefined>(undefined)

export const useApp = () => {
  const context = useContext(AppContext)
  if (context === undefined) {
    throw new Error('useApp must be used within an AppProvider')
  }
  return context
}

interface AppProviderProps {
  children: React.ReactNode
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  // Authentication State
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem('xionimus_token')
  })
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => {
    const savedToken = localStorage.getItem('xionimus_token')
    return Boolean(savedToken)
  })

  // Chat State
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [currentSession, setCurrentSession] = useState<string | null>(null)
  const [sessions, setSessions] = useState<ChatSession[]>(() => {
    // Load sessions from localStorage
    const saved = localStorage.getItem('xionimus_sessions')
    return saved ? JSON.parse(saved) : []
  })
  const [isLoading, setIsLoading] = useState(false)
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamingText, setStreamingText] = useState('')
  const [abortController, setAbortController] = useState<AbortController | null>(null)
  const [useStreaming, setUseStreaming] = useState(() => {
    const saved = localStorage.getItem('xionimus_use_streaming')
    return saved ? JSON.parse(saved) : true  // Streaming enabled by default
  })
  
  const [selectedProvider, setSelectedProvider] = useState('anthropic')  // Changed to Anthropic for Claude models
  
  // Auto-select appropriate model when provider changes
  const handleProviderChange = (provider: string) => {
    setSelectedProvider(provider)
    
    // Set default model based on provider
    const defaultModels = {
      openai: 'gpt-4.1',                              // GPT-4.1
      anthropic: 'claude-sonnet-4-5-20250514',        // Claude Sonnet 4.5 for coding
      perplexity: 'llama-3.1-sonar-large-128k-online'
    }
    
    setSelectedModel(defaultModels[provider as keyof typeof defaultModels] || 'claude-sonnet-4-5-20250514')
  }
  const [selectedModel, setSelectedModel] = useState('claude-sonnet-4-5-20250514')  // Default to Sonnet 4.5 for coding
  const [availableProviders, setAvailableProviders] = useState<Record<string, boolean>>({})
  const [availableModels, setAvailableModels] = useState<Record<string, string[]>>({})
  const [autoAgentSelection, setAutoAgentSelection] = useState(true)  // Enable by default
  const [apiKeys, setApiKeys] = useState({
    openai: '',
    anthropic: '',
    perplexity: ''
  })
  
  const toast = useToast()
  const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001'

  // Setup Axios Interceptor for automatic logout on 401
  React.useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      (error) => {
        // Check if error is 401 and we have a token (user thinks they're logged in)
        if (error.response?.status === 401 && token) {
          console.warn('⚠️ Token invalid or expired - logging out')
          
          // Clear token and user data
          setToken(null)
          setUser(null)
          setIsAuthenticated(false)
          localStorage.removeItem('xionimus_token')
          
          // Show toast
          toast({
            title: 'Sitzung abgelaufen',
            description: 'Bitte melden Sie sich erneut an.',
            status: 'warning',
            duration: 5000,
            isClosable: true,
            position: 'top'
          })
        }
        
        return Promise.reject(error)
      }
    )
    
    // Cleanup
    return () => {
      axios.interceptors.response.eject(interceptor)
    }
  }, [token, toast])

  // Authentication Functions
  const login = useCallback(async (username: string, password: string) => {
    try {
      const response = await axios.post(`${API_BASE}/api/auth/login`, {
        username,
        password
      })
      
      const { access_token, user_id, username: returnedUsername } = response.data
      
      // Store token
      setToken(access_token)
      localStorage.setItem('xionimus_token', access_token)
      
      // Store user data
      const userData: User = {
        user_id,
        username: returnedUsername,
        email: '', // Will be filled from /me endpoint
        role: 'user'
      }
      setUser(userData)
      setIsAuthenticated(true)
      
      toast({
        title: '✅ Login erfolgreich!',
        description: `Willkommen zurück, ${returnedUsername}!`,
        status: 'success',
        duration: 5000,
        isClosable: true,
        position: 'top'
      })
      
    } catch (error: any) {
      console.error('Login error:', error)
      toast({
        title: 'Login fehlgeschlagen',
        description: error.response?.data?.detail || 'Ungültige Anmeldedaten',
        status: 'error',
        duration: 5000
      })
      throw error
    }
  }, [API_BASE, toast])

  const register = useCallback(async (username: string, email: string, password: string) => {
    try {
      const response = await axios.post(`${API_BASE}/api/auth/register`, {
        username,
        email,
        password
      })
      
      const { access_token, user_id, username: returnedUsername } = response.data
      
      // Store token
      setToken(access_token)
      localStorage.setItem('xionimus_token', access_token)
      
      // Store user data
      const userData: User = {
        user_id,
        username: returnedUsername,
        email: email,
        role: 'user'
      }
      setUser(userData)
      setIsAuthenticated(true)
      
      toast({
        title: '✅ Account erstellt!',
        description: `Willkommen, ${returnedUsername}! Sie sind jetzt eingeloggt.`,
        status: 'success',
        duration: 5000,
        isClosable: true,
        position: 'top'
      })
      
    } catch (error: any) {
      console.error('Register error:', error)
      toast({
        title: 'Registrierung fehlgeschlagen',
        description: error.response?.data?.detail || 'Registrierung konnte nicht abgeschlossen werden',
        status: 'error',
        duration: 5000
      })
      throw error
    }
  }, [API_BASE, toast])

  const logout = useCallback(() => {
    setToken(null)
    setUser(null)
    setIsAuthenticated(false)
    localStorage.removeItem('xionimus_token')
    
    // Clear chat data
    setMessages([])
    setCurrentSession(null)
    setSessions([])
    
    toast({
      title: 'Abgemeldet',
      description: 'Sie wurden erfolgreich abgemeldet',
      status: 'info',
      duration: 3000
    })
  }, [toast])

  // Load API keys from localStorage
  useEffect(() => {
    const savedKeys = localStorage.getItem('xionimus_ai_api_keys')
    if (savedKeys) {
      try {
        setApiKeys(JSON.parse(savedKeys))
      } catch (error) {
        console.error('Failed to parse saved API keys:', error)
      }
    }
  }, [])

  const updateApiKeys = useCallback((keys: Partial<typeof apiKeys>) => {
    // Trim whitespace from API keys to prevent header errors
    const trimmedKeys = {
      openai: keys.openai?.trim() || apiKeys.openai,
      anthropic: keys.anthropic?.trim() || apiKeys.anthropic,
      perplexity: keys.perplexity?.trim() || apiKeys.perplexity
    }
    
    const newKeys = { ...apiKeys, ...trimmedKeys }
    setApiKeys(newKeys)
    localStorage.setItem('xionimus_ai_api_keys', JSON.stringify(newKeys))
    toast({
      title: 'API Keys Updated',
      description: 'Your API keys have been saved successfully.',
      status: 'success',
      duration: 3000,
    })
  }, [apiKeys, toast])

  // Streaming message handler
  const sendMessageStreaming = useCallback(async (content: string, ultraThinking: boolean = false) => {
    const userMessage: ChatMessage = {
      role: 'user',
      content: content.trim(),
      timestamp: new Date()
    }
    
    setMessages(prev => [...prev, userMessage])
    setIsStreaming(true)
    setStreamingText('')

    // Get session ID
    const sessionId = currentSession || `session_${Date.now()}`
    if (!currentSession) {
      setCurrentSession(sessionId)
    }

    // Create WebSocket connection
    const wsUrl = API_BASE.replace('http', 'ws') + `/api/ws/chat/${sessionId}`
    const ws = new WebSocket(wsUrl)

    let fullResponse = ''

    ws.onopen = () => {
      // Get current messages state
      setMessages(currentMessages => {
        // Prepare messages for API
        const messagesForAPI = [...currentMessages, userMessage].map(msg => ({
          role: msg.role,
          content: msg.content
        }))

        // Send message through WebSocket
        ws.send(JSON.stringify({
          type: 'chat',
          content: content.trim(),
          provider: selectedProvider,
          model: selectedModel,
          messages: messagesForAPI,
          ultra_thinking: ultraThinking,
          api_keys: apiKeys
        }))
        
        // Return unchanged state
        return currentMessages
      })
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)

      switch (data.type) {
        case 'chunk':
          fullResponse += data.content
          setStreamingText(fullResponse)
          break

        case 'complete':
          const aiMessage: ChatMessage = {
            role: 'assistant',
            content: data.full_content || fullResponse,
            timestamp: new Date(data.timestamp),
            provider: data.provider,
            model: data.model,
            agent_results: data.agent_results  // NEW: Include agent results from streaming
          }

          // Use functional update and get current state
          setMessages(prev => {
            const updatedMessages = [...prev, aiMessage]
            
            // Save to localStorage with current messages
            const sessionData: ChatSession = {
              id: sessionId,
              name: content.substring(0, 50) || 'New Chat',
              createdAt: sessions.find(s => s.id === sessionId)?.createdAt || new Date().toISOString(),
              updatedAt: new Date().toISOString(),
              messages: updatedMessages
            }

            const existingIndex = sessions.findIndex(s => s.id === sessionId)
            const updatedSessions = existingIndex >= 0
              ? sessions.map((s, i) => i === existingIndex ? sessionData : s)
              : [...sessions, sessionData]

            setSessions(updatedSessions)
            localStorage.setItem('xionimus_sessions', JSON.stringify(updatedSessions))
            
            return updatedMessages
          })
          
          setIsStreaming(false)
          setStreamingText('')
          ws.close()
          break

        case 'error':
          toast({
            title: 'Streaming Error',
            description: data.message,
            status: 'error',
            duration: 5000
          })
          setIsStreaming(false)
          setStreamingText('')
          ws.close()
          break
      }
    }

    ws.onerror = () => {
      // Don't recursively call sendMessage - just disable streaming for future
      console.error('WebSocket connection failed, switching to HTTP mode')
      toast({
        title: 'Connection Error',
        description: 'Streaming unavailable. Please try again.',
        status: 'warning',
        duration: 3000
      })
      setIsStreaming(false)
      setStreamingText('')
      setUseStreaming(false)
      ws.close()
    }

    ws.onclose = () => {
      setIsStreaming(false)
    }
  }, [messages, currentSession, sessions, selectedProvider, selectedModel, apiKeys, toast, API_BASE, setUseStreaming])

  const sendMessage = useCallback(async (content: string, ultraThinking: boolean = false) => {
    // Validate input
    if (!content || !content.trim()) {
      toast({
        title: 'Fehler',
        description: 'Bitte geben Sie eine Nachricht ein',
        status: 'error',
        duration: 3000,
      })
      return
    }
    
    // Check message length
    if (content.length > 100000) {
      toast({
        title: 'Fehler',
        description: 'Nachricht ist zu lang (max. 100.000 Zeichen)',
        status: 'error',
        duration: 3000,
      })
      return
    }

    // Use streaming if enabled
    if (useStreaming) {
      return sendMessageStreaming(content, ultraThinking)
    }
    
    // Create new AbortController for this request
    const controller = new AbortController()
    setAbortController(controller)
    setIsLoading(true)
    
    try {
      // Add user message immediately
      const userMessage: ChatMessage = {
        role: 'user',
        content: content.trim(),
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, userMessage])
      
      // Prepare messages for API
      const messagesForAPI = [...messages, userMessage].map(msg => ({
        role: msg.role,
        content: msg.content
      }))
      
      // Call AI API with intelligent agent selection and ultra thinking
      const response = await axios.post(`${API_BASE}/api/chat/`, {  // Added trailing slash
        messages: messagesForAPI,
        provider: selectedProvider,
        model: selectedModel,
        session_id: currentSession,
        api_keys: apiKeys,  // Send API keys with each request
        auto_agent_selection: autoAgentSelection,  // Enable intelligent selection
        ultra_thinking: ultraThinking  // Pass ultra thinking flag
      }, {
        signal: controller.signal,  // Add abort signal
        headers: token ? {
          'Authorization': `Bearer ${token}`
        } : {}
      })
      
      const aiMessage: ChatMessage = {
        role: 'assistant',
        content: response.data.content,
        timestamp: new Date(response.data.timestamp),
        provider: response.data.provider,
        model: response.data.model,
        usage: response.data.usage,
        agent_results: response.data.agent_results  // NEW: Include agent results
      }
      
      // Use functional update to avoid stale closure
      setMessages(prev => {
        const updatedMessages = [...prev, aiMessage]
        
        // Update or create session
        const sessionId = currentSession || `session_${Date.now()}`
        if (!currentSession) {
          setCurrentSession(sessionId)
        }
        
        // Save to localStorage
        const sessionData: ChatSession = {
          id: sessionId,
          name: prev[prev.length - 1]?.content.substring(0, 50) || 'New Chat',
          createdAt: sessions.find(s => s.id === sessionId)?.createdAt || new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          messages: updatedMessages
        }
        
        const existingIndex = sessions.findIndex(s => s.id === sessionId)
        const updatedSessions = existingIndex >= 0
          ? sessions.map((s, i) => i === existingIndex ? sessionData : s)
          : [...sessions, sessionData]
        
        setSessions(updatedSessions)
        localStorage.setItem('xionimus_sessions', JSON.stringify(updatedSessions))
        
        return updatedMessages
      })
      
    } catch (error: any) {
      // Check if error is from abort
      if (axios.isCancel(error) || error.name === 'CanceledError') {
        console.log('Request cancelled by user')
        toast({
          title: 'Generation gestoppt',
          description: 'Die KI-Generierung wurde vom Benutzer unterbrochen',
          status: 'warning',
          duration: 3000,
        })
      } else {
        console.error('Send message error:', error)
        toast({
          title: 'Error',
          description: error.response?.data?.detail || 'Failed to send message',
          status: 'error',
          duration: 5000,
        })
      }
    } finally {
      setIsLoading(false)
      setAbortController(null)
    }
  }, [messages, selectedProvider, selectedModel, currentSession, API_BASE, toast, apiKeys, autoAgentSelection])

  const stopGeneration = useCallback(() => {
    if (abortController) {
      abortController.abort()
      setAbortController(null)
      setIsLoading(false)
    }
  }, [abortController])

  const loadSession = useCallback(async (sessionId: string) => {
    try {
      const response = await axios.get(`${API_BASE}/api/chat/sessions/${sessionId}/messages`)
      
      const loadedMessages: ChatMessage[] = response.data.map((msg: any) => ({
        role: msg.role,
        content: msg.content,
        timestamp: new Date(msg.timestamp),
        provider: msg.provider,
        model: msg.model,
        usage: msg.usage
      }))
      
      setMessages(loadedMessages)
      setCurrentSession(sessionId)
      
    } catch (error) {
      console.error('Load session error:', error)
      toast({
        title: 'Error',
        description: 'Failed to load session',
        status: 'error',
        duration: 3000,
      })
    }
  }, [API_BASE, toast])

  const createNewSession = useCallback(() => {
    // Save current session if it has messages
    if (currentSession && messages.length > 0) {
      const existingSession = sessions.find(s => s.id === currentSession)
      if (existingSession) {
        const updatedSessions = sessions.map(s => 
          s.id === currentSession 
            ? { ...s, messages, updatedAt: new Date().toISOString() }
            : s
        )
        setSessions(updatedSessions)
        localStorage.setItem('xionimus_sessions', JSON.stringify(updatedSessions))
      } else {
        const newSession: ChatSession = {
          id: currentSession,
          name: messages[0]?.content.substring(0, 50) || 'New Chat',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
          messages
        }
        const updatedSessions = [...sessions, newSession]
        setSessions(updatedSessions)
        localStorage.setItem('xionimus_sessions', JSON.stringify(updatedSessions))
      }
    }
    
    // Create new empty session
    const newSessionId = `session_${Date.now()}`
    setMessages([])
    setCurrentSession(newSessionId)
    
    toast({
      title: 'New Session',
      description: 'Started a new chat session',
      status: 'info',
      duration: 2000,
    })
  }, [currentSession, messages, sessions, toast])

  const deleteSession = useCallback(async (sessionId: string) => {
    const updatedSessions = sessions.filter(s => s.id !== sessionId)
    setSessions(updatedSessions)
    localStorage.setItem('xionimus_sessions', JSON.stringify(updatedSessions))
    
    if (currentSession === sessionId) {
      setMessages([])
      setCurrentSession(null)
    }
    
    toast({
      title: 'Session Deleted',
      description: 'Chat session has been deleted',
      status: 'success',
      duration: 3000,
    })
  }, [currentSession, sessions, toast])

  const loadSessions = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/chat/sessions`)
      setSessions(response.data)
    } catch (error) {
      console.error('Load sessions error:', error)
    }
  }, [API_BASE])

  const loadProviders = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/chat/providers`)
      
      // Merge backend config with frontend API keys
      const backendProviders = response.data.providers
      const frontendProviders = {
        openai: !!apiKeys.openai,
        anthropic: !!apiKeys.anthropic,
        perplexity: !!apiKeys.perplexity
      }
      
      // Provider is available if configured in backend OR has frontend API key
      const mergedProviders = {
        openai: backendProviders.openai || frontendProviders.openai,
        anthropic: backendProviders.anthropic || frontendProviders.anthropic,
        perplexity: backendProviders.perplexity || frontendProviders.perplexity
      }
      
      setAvailableProviders(mergedProviders)
      setAvailableModels(response.data.models)
    } catch (error) {
      console.error('Load providers error:', error)
      
      // Fallback: use only frontend API keys
      setAvailableProviders({
        openai: !!apiKeys.openai,
        anthropic: !!apiKeys.anthropic,
        perplexity: !!apiKeys.perplexity
      })
    }
  }, [API_BASE, apiKeys])

  const switchSession = useCallback((sessionId: string) => {
    const session = sessions.find(s => s.id === sessionId)
    if (session) {
      setMessages(session.messages || [])
      setCurrentSession(sessionId)
    }
  }, [sessions])

  const renameSession = useCallback((sessionId: string, newName: string) => {
    const updatedSessions = sessions.map(session => 
      session.id === sessionId 
        ? { ...session, name: newName } 
        : session
    )
    setSessions(updatedSessions)
    localStorage.setItem('xionimus_sessions', JSON.stringify(updatedSessions))
  }, [sessions])

  const updateMessages = useCallback((newMessages: ChatMessage[]) => {
    setMessages(newMessages)
    
    // Update current session in storage if available
    if (currentSession) {
      const updatedSessions = sessions.map(session => 
        session.id === currentSession 
          ? { ...session, messages: newMessages } 
          : session
      )
      setSessions(updatedSessions)
      localStorage.setItem('xionimus_sessions', JSON.stringify(updatedSessions))
    }
  }, [currentSession, sessions])

  // Save streaming preference to localStorage
  useEffect(() => {
    localStorage.setItem('xionimus_use_streaming', JSON.stringify(useStreaming))
  }, [useStreaming])

  // Load initial data and reload when API keys change
  useEffect(() => {
    loadSessions()
    loadProviders()
    
    // Set initial model if not set - Default to Claude Sonnet 4.5 for coding
    if (!selectedModel) {
      setSelectedModel('claude-sonnet-4-5-20250514')
    }
  }, [loadSessions, loadProviders, selectedModel])

  const value: AppContextType = {
    // Authentication
    user,
    isAuthenticated,
    token,
    login,
    register,
    logout,
    
    // Chat State
    messages,
    currentSession,
    sessions,
    isLoading,
    isStreaming,
    streamingText,
    selectedProvider,
    selectedModel,
    availableProviders,
    availableModels,
    autoAgentSelection,
    useStreaming,
    apiKeys,
    sendMessage,
    stopGeneration,
    loadSession,
    createNewSession,
    deleteSession,
    switchSession,
    renameSession,
    updateApiKeys,
    setSelectedProvider: handleProviderChange,
    setSelectedModel,
    setAutoAgentSelection,
    setUseStreaming,
    updateMessages,
    loadSessions,
    loadProviders
  }

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  )
}