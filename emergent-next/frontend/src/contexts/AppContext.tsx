import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { useToast } from '@chakra-ui/react'
import axios from 'axios'

interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: Date
  provider?: string
  model?: string
  usage?: any
}

interface ChatSession {
  session_id: string
  name: string
  created_at: Date
  updated_at: Date
  message_count: number
  last_message?: string
}

interface AppContextType {
  // Chat State
  messages: ChatMessage[]
  currentSession: string | null
  sessions: ChatSession[]
  isLoading: boolean
  
  // AI Settings
  selectedProvider: string
  selectedModel: string
  availableProviders: Record<string, boolean>
  availableModels: Record<string, string[]>
  
  // API Keys
  apiKeys: {
    openai: string
    anthropic: string
    perplexity: string
  }
  
  // Actions
  sendMessage: (content: string) => Promise<void>
  loadSession: (sessionId: string) => Promise<void>
  createNewSession: () => void
  deleteSession: (sessionId: string) => Promise<void>
  updateApiKeys: (keys: Partial<typeof apiKeys>) => void
  setSelectedProvider: (provider: string) => void
  setSelectedModel: (model: string) => void
  
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
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [currentSession, setCurrentSession] = useState<string | null>(null)
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [isLoading, setIsLoading] = useState(false)
  
  const [selectedProvider, setSelectedProvider] = useState('openai')
  
  // Auto-select appropriate model when provider changes
  const handleProviderChange = (provider: string) => {
    setSelectedProvider(provider)
    
    // Set default model based on provider
    const defaultModels = {
      openai: 'gpt-4o-mini',
      anthropic: 'claude-3-5-sonnet-20241022', 
      perplexity: 'llama-3.1-sonar-large-128k-online'
    }
    
    setSelectedModel(defaultModels[provider as keyof typeof defaultModels] || 'gpt-4o-mini')
  }
  const [selectedModel, setSelectedModel] = useState('')
  const [availableProviders, setAvailableProviders] = useState<Record<string, boolean>>({})
  const [availableModels, setAvailableModels] = useState<Record<string, string[]>>({})
  
  const [apiKeys, setApiKeys] = useState({
    openai: '',
    anthropic: '',
    perplexity: ''
  })
  
  const toast = useToast()
  const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8002'

  // Load API keys from localStorage
  useEffect(() => {
    const savedKeys = localStorage.getItem('emergent_api_keys')
    if (savedKeys) {
      try {
        setApiKeys(JSON.parse(savedKeys))
      } catch (error) {
        console.error('Failed to parse saved API keys:', error)
      }
    }
  }, [])

  const updateApiKeys = useCallback((keys: Partial<typeof apiKeys>) => {
    const newKeys = { ...apiKeys, ...keys }
    setApiKeys(newKeys)
    localStorage.setItem('emergent_api_keys', JSON.stringify(newKeys))
    toast({
      title: 'API Keys Updated',
      description: 'Your API keys have been saved successfully.',
      status: 'success',
      duration: 3000,
    })
  }, [apiKeys, toast])

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim()) return
    
    setIsLoading(true)
    
    try {
      // Add user message immediately
      const userMessage: ChatMessage = {
        role: 'user',
        content,
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, userMessage])
      
      // Prepare messages for API
      const messagesForAPI = [...messages, userMessage].map(msg => ({
        role: msg.role,
        content: msg.content
      }))
      
      // Call AI API with dynamic keys
      const response = await axios.post(`${API_BASE}/api/chat`, {
        messages: messagesForAPI,
        provider: selectedProvider,
        model: selectedModel,
        session_id: currentSession,
        api_keys: apiKeys  // Send API keys with each request
      })
      
      const aiMessage: ChatMessage = {
        role: 'assistant',
        content: response.data.content,
        timestamp: new Date(response.data.timestamp),
        provider: response.data.provider,
        model: response.data.model,
        usage: response.data.usage
      }
      
      setMessages(prev => [...prev, aiMessage])
      
      // Update session if new
      if (response.data.session_id && !currentSession) {
        setCurrentSession(response.data.session_id)
        await loadSessions()
      }
      
    } catch (error: any) {
      console.error('Send message error:', error)
      toast({
        title: 'Error',
        description: error.response?.data?.detail || 'Failed to send message',
        status: 'error',
        duration: 5000,
      })
    } finally {
      setIsLoading(false)
    }
  }, [messages, selectedProvider, selectedModel, currentSession, API_BASE, toast])

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
    setMessages([])
    setCurrentSession(null)
    toast({
      title: 'New Session',
      description: 'Started a new chat session',
      status: 'info',
      duration: 2000,
    })
  }, [toast])

  const deleteSession = useCallback(async (sessionId: string) => {
    try {
      await axios.delete(`${API_BASE}/api/chat/sessions/${sessionId}`)
      
      if (currentSession === sessionId) {
        createNewSession()
      }
      
      await loadSessions()
      
      toast({
        title: 'Session Deleted',
        description: 'Chat session has been deleted',
        status: 'success',
        duration: 3000,
      })
      
    } catch (error) {
      console.error('Delete session error:', error)
      toast({
        title: 'Error',
        description: 'Failed to delete session',
        status: 'error',
        duration: 3000,
      })
    }
  }, [currentSession, createNewSession, API_BASE, toast])

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

  // Load initial data and reload when API keys change
  useEffect(() => {
    loadSessions()
    loadProviders()
  }, [loadSessions, loadProviders])

  const value: AppContextType = {
    messages,
    currentSession,
    sessions,
    isLoading,
    selectedProvider,
    selectedModel,
    availableProviders,
    availableModels,
    apiKeys,
    sendMessage,
    loadSession,
    createNewSession,
    deleteSession,
    updateApiKeys,
    setSelectedProvider,
    setSelectedModel,
    loadSessions,
    loadProviders
  }

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  )
}