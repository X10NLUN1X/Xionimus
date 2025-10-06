import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react'
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
  research_sources?: Array<{
    url: string
    title: string
    status: string
    timestamp: string
    snippet?: string
  }>
  quick_actions?: {
    message: string
    options: Array<{
      id: string
      title: string
      description: string
      action: string
      icon?: string
      duration?: string
      provider?: string
      model?: string
    }>
  }
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
  tokenUsage: any  // NEW: Token usage data
  
  // AI Settings
  selectedProvider: string
  selectedModel: string
  availableProviders: Record<string, boolean>
  availableModels: Record<string, string[]>
  autoAgentSelection: boolean  // New: Intelligent agent selection
  useStreaming: boolean  // New: Toggle streaming on/off
  developerMode: 'junior' | 'senior'  // PHASE 2: Developer Mode
  
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
  setDeveloperMode: (mode: 'junior' | 'senior') => void  // PHASE 2: Set developer mode
  
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
  const [user, setUser] = useState<User | null>(() => {
    // Load user data from localStorage on startup
    const savedUser = localStorage.getItem('xionimus_user')
    if (savedUser) {
      try {
        return JSON.parse(savedUser)
      } catch (error) {
        console.error('Failed to parse saved user data:', error)
        return null
      }
    }
    return null
  })
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
  const [tokenUsage, setTokenUsage] = useState<any>(null)  // NEW: Token usage tracking
  const [useStreaming, setUseStreaming] = useState(() => {
    const saved = localStorage.getItem('xionimus_use_streaming')
    return saved ? JSON.parse(saved) : true  // Streaming enabled by default
  })
  
  const [selectedProvider, setSelectedProvider] = useState('anthropic')  // 🎯 PHASE 2: Claude as primary AI
  
  // Auto-select appropriate model when provider changes
  const handleProviderChange = (provider: string) => {
    setSelectedProvider(provider)
    
    // Set default model based on provider
    const defaultModels = {
      openai: 'gpt-4o-mini',                          // ChatGPT-4o-mini - Cost-effective chatbot
      anthropic: 'claude-sonnet-4-5-20250929',        // 🎯 PHASE 2: Claude Sonnet 4.5 as default
      perplexity: 'sonar-pro'                         // Perplexity Pro for research
    }
    
    setSelectedModel(defaultModels[provider as keyof typeof defaultModels] || 'claude-sonnet-4-5-20250929')
  }
  const [selectedModel, setSelectedModel] = useState('claude-sonnet-4-5-20250929')  // 🎯 PHASE 2: Claude Sonnet 4.5 as default
  const [availableProviders, setAvailableProviders] = useState<Record<string, boolean>>({})
  const [availableModels, setAvailableModels] = useState<Record<string, string[]>>({})
  const [autoAgentSelection, setAutoAgentSelection] = useState(true)  // Enable by default
  const [developerMode, setDeveloperMode] = useState<'junior' | 'senior'>('senior')  // 🎯 PHASE 2: Senior mode as default
  const [apiKeys, setApiKeys] = useState({
    openai: '',
    anthropic: '',
    perplexity: ''
  })
  
  const toast = useToast()
  const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001'

  // Setup Axios Request Interceptor to add token to all requests
  React.useEffect(() => {
    const requestInterceptor = axios.interceptors.request.use(
      (config) => {
        // Add Authorization header if token exists
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )
    
    // Cleanup
    return () => {
      axios.interceptors.request.eject(requestInterceptor)
    }
  }, [token])

  // Setup Axios Response Interceptor for automatic logout on 401
  React.useEffect(() => {
    const interceptor = axios.interceptors.response.use(
      (response) => response,
      (error) => {
        // Check if error is 401 and we have a token (user thinks they're logged in)
        // BUT: Don't logout for GitHub PAT endpoints - just show error
        const isGitHubEndpoint = error.config?.url?.includes('/api/github-pat/')
        
        if (error.response?.status === 401 && token && !isGitHubEndpoint) {
          console.warn('⚠️ Token invalid or expired - logging out')
          
          // Clear token and user data
          setToken(null)
          setUser(null)
          setIsAuthenticated(false)
          
          // Remove all auth data from localStorage
          localStorage.removeItem('xionimus_token')
          localStorage.removeItem('xionimus_user')
          
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
      
      // Store user data in localStorage for persistence across page reloads
      localStorage.setItem('xionimus_user', JSON.stringify(userData))
      
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
      
      // Store user data in localStorage for persistence across page reloads
      localStorage.setItem('xionimus_user', JSON.stringify(userData))
      
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
    
    // Remove all auth data from localStorage
    localStorage.removeItem('xionimus_token')
    localStorage.removeItem('xionimus_user')
    
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

  // Load user sessions from backend on login
  const loadUserSessions = useCallback(async () => {
    if (!token) {
      console.log('⏸️ Skipping session load - no auth token')
      return
    }
    
    try {
      console.log('📋 Loading sessions from backend...')
      const response = await axios.get(`${API_BASE}/api/sessions/list`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      
      if (response.data && Array.isArray(response.data)) {
        setSessions(response.data)
        console.log(`✅ Loaded ${response.data.length} sessions from backend`)
      }
    } catch (error) {
      console.error('❌ Failed to load sessions:', error)
    }
  }, [token, API_BASE])

  // Auto-save session to backend after each message
  // Track which messages have been saved to avoid duplicates
  const savedMessagesRef = useRef<Set<string>>(new Set())

  const saveSessionToBackend = useCallback(async (sessionData: ChatSession) => {
    if (!token) return
    
    try {
      // Check if session exists
      const sessionExists = sessions.find(s => s.id === sessionData.id)
      
      let backendSessionId = sessionData.id
      
      if (!sessionExists) {
        // Create new session
        const response = await axios.post(`${API_BASE}/api/sessions/`, {
          name: sessionData.name
        }, {
          headers: { Authorization: `Bearer ${token}` }
        })
        
        // Use backend-generated session ID
        backendSessionId = response.data.id
        console.log(`✅ Created session: ${backendSessionId} (frontend: ${sessionData.id})`)
      }
      
      // Only save NEW messages (not already saved)
      const sessionKey = backendSessionId
      if (!savedMessagesRef.current.has(sessionKey)) {
        savedMessagesRef.current.add(sessionKey)
      }
      
      // Save only the last message (the new one) to avoid duplicates
      const lastMessage = sessionData.messages[sessionData.messages.length - 1]
      if (lastMessage) {
        await axios.post(`${API_BASE}/api/sessions/messages`, {
          session_id: backendSessionId,
          role: lastMessage.role,
          content: lastMessage.content,
          provider: lastMessage.provider,
          model: lastMessage.model,
          usage: lastMessage.usage
        }, {
          headers: { Authorization: `Bearer ${token}` }
        })
        console.log(`💾 Saved new message to session ${sessionData.id}`)
      }
    } catch (error) {
      console.error('Failed to save session:', error)
    }
  }, [token, API_BASE, sessions])

  // Load sessions on authentication
  useEffect(() => {
    if (isAuthenticated && token) {
      loadUserSessions()
    }
  }, [isAuthenticated, token]) // eslint-disable-line react-hooks/exhaustive-deps

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
    
    // Add user message to state
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
      // Prepare messages for API - use the messages state + userMessage
      // We already added userMessage to state above, so we need to get current state
      setMessages(currentMessages => {
        // currentMessages now includes the userMessage we just added
        const messagesForAPI = currentMessages.map(msg => ({
          role: msg.role,
          content: msg.content
        }))

        // Send message through WebSocket
        ws.send(JSON.stringify({
          type: 'chat',
          session_id: sessionId,
          content: content.trim(),
          developer_mode: developerMode,  // 🎯 PHASE 2: Send developer mode
          provider: selectedProvider,
          model: selectedModel,
          messages: messagesForAPI,
          ultra_thinking: ultraThinking,
          api_keys: apiKeys
        }))
        
        // Return unchanged state (no modification needed)
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
          // Update token usage if available
          if (data.token_usage) {
            setTokenUsage(data.token_usage)
          }
          
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
            // Deduplicate before adding - check if aiMessage already exists
            const isDuplicate = prev.some(m => 
              m.content === aiMessage.content && 
              m.role === aiMessage.role &&
              Math.abs(new Date(m.timestamp).getTime() - new Date(aiMessage.timestamp).getTime()) < 1000
            )
            
            const updatedMessages = isDuplicate ? prev : [...prev, aiMessage]
            
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
            
            // Auto-save to backend
            if (token) {
              saveSessionToBackend(sessionData).catch(err => 
                console.error('Background session save failed:', err)
              )
            }
            
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
        developer_mode: developerMode,  // 🎯 PHASE 2: Send developer mode
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
      
      // Update token usage from response
      if (response.data.token_usage) {
        setTokenUsage(response.data.token_usage)
      }
      
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
        // Deduplicate before adding - check if aiMessage already exists
        const isDuplicate = prev.some(m => 
          m.content === aiMessage.content && 
          m.role === aiMessage.role &&
          Math.abs(new Date(m.timestamp).getTime() - new Date(aiMessage.timestamp).getTime()) < 1000
        )
        
        const updatedMessages = isDuplicate ? prev : [...prev, aiMessage]
        
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
        
        // Auto-save to backend
        if (token) {
          saveSessionToBackend(sessionData).catch(err => 
            console.error('Background session save failed:', err)
          )
        }
        
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
      console.log('📥 Loading session:', sessionId)
      const response = await axios.get(`${API_BASE}/api/sessions/${sessionId}`)
      
      // Check if session has messages
      if (response.data && response.data.message_count > 0) {
        // Load messages from backend
        const messagesResponse = await axios.get(`${API_BASE}/api/sessions/${sessionId}/messages`)
        
        const loadedMessages: ChatMessage[] = messagesResponse.data.map((msg: any) => ({
          role: msg.role,
          content: msg.content,
          timestamp: new Date(msg.timestamp),
          provider: msg.provider,
          model: msg.model,
          usage: msg.usage,
          id: msg.id
        }))
        
        console.log(`✅ Loaded ${loadedMessages.length} messages from session ${sessionId}`)
        setMessages(loadedMessages)
      } else {
        console.log('ℹ️ Session has no messages, starting fresh')
        setMessages([])
      }
      
      setCurrentSession(sessionId)
      
    } catch (error: any) {
      console.error('Load session error:', error)
      
      // If session not found in backend, try localStorage backup
      const localSessions = localStorage.getItem('xionimus_sessions')
      if (localSessions) {
        const parsedSessions = JSON.parse(localSessions)
        const localSession = parsedSessions.find((s: any) => s.id === sessionId)
        
        if (localSession && localSession.messages) {
          console.log('📦 Restored session from localStorage backup')
          setMessages(localSession.messages)
          setCurrentSession(sessionId)
          return
        }
      }
      
      toast({
        title: 'Session Load Error',
        description: 'Could not load session. Starting fresh.',
        status: 'warning',
        duration: 3000,
      })
      
      // Create new session as fallback
      const newSessionId = `session_${Date.now()}`
      setMessages([])
      setCurrentSession(newSessionId)
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
      // Deduplicate messages when switching
      const messages = session.messages || []
      const uniqueMessages = messages.filter((msg, index, self) => {
        if (msg.id) {
          return self.findIndex(m => m.id === msg.id) === index
        }
        return self.findIndex(m => 
          m.content === msg.content && 
          m.role === msg.role &&
          Math.abs(new Date(m.timestamp).getTime() - new Date(msg.timestamp).getTime()) < 1000
        ) === index
      })
      
      setMessages(uniqueMessages)
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
    // Deduplicate messages based on content + timestamp + role
    const uniqueMessages = newMessages.filter((msg, index, self) => {
      // If message has an ID, use that for uniqueness
      if (msg.id) {
        return self.findIndex(m => m.id === msg.id) === index
      }
      // Otherwise use content + timestamp combination
      return self.findIndex(m => 
        m.content === msg.content && 
        m.role === msg.role &&
        new Date(m.timestamp).getTime() === new Date(msg.timestamp).getTime()
      ) === index
    })
    
    setMessages(uniqueMessages)
    
    // Update current session in storage if available
    if (currentSession) {
      const updatedSessions = sessions.map(session => 
        session.id === currentSession 
          ? { ...session, messages: uniqueMessages } 
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

  // 🎯 Save current session ID for reload persistence
  useEffect(() => {
    if (currentSession) {
      localStorage.setItem('xionimus_last_session', currentSession)
      console.log('💾 Saved last session:', currentSession)
    }
  }, [currentSession])

  // Load initial data and reload when API keys change
  useEffect(() => {
    const initializeApp = async () => {
      // Load sessions from backend
      await loadSessions()
      await loadProviders()
      
      // Set initial model if not set - Default to ChatGPT-4o-mini
      if (!selectedModel) {
        setSelectedModel('gpt-4o-mini')
      }
      
      // 🎯 Auto-restore last session after reload
      const lastSessionId = localStorage.getItem('xionimus_last_session')
      if (lastSessionId && !currentSession) {
        console.log('🔄 Restoring last session:', lastSessionId)
        try {
          await loadSession(lastSessionId)
        } catch (error) {
          console.error('Failed to restore last session:', error)
          // If restore fails, create new session
          createNewSession()
        }
      } else if (!currentSession && sessions.length === 0) {
        // No sessions exist, create new one
        createNewSession()
      }
    }
    
    initializeApp()
  }, []) // Only run once on mount

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
    tokenUsage,  // NEW: Add token usage to context
    selectedProvider,
    selectedModel,
    availableProviders,
    availableModels,
    autoAgentSelection,
    useStreaming,
    developerMode,  // 🎯 PHASE 2: Developer Mode
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