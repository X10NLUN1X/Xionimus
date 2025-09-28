import React, { createContext, useContext, useState, useEffect } from 'react'
import { toast } from 'sonner'

interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  agent: string
  model: string
  timestamp: Date
  usage?: any
}

interface ChatSession {
  id: string
  name: string
  description?: string
  created_at: Date
  message_count: number
}

interface Agent {
  id: string
  name: string
  description: string
  capabilities: string[]
  models: string[]
  icon: string
}

interface ChatContextType {
  // Messages
  messages: Message[]
  addMessage: (message: Message) => void
  clearMessages: () => void
  
  // Current chat state
  currentAgent: string
  currentModel: string
  currentSession: string | null
  isLoading: boolean
  
  // Setters
  setCurrentAgent: (agent: string) => void
  setCurrentModel: (model: string) => void
  setCurrentSession: (sessionId: string | null) => void
  setIsLoading: (loading: boolean) => void
  
  // API methods
  sendMessage: (content: string) => Promise<void>
  loadChatHistory: (sessionId: string) => Promise<void>
  
  // Agents and sessions
  agents: Agent[]
  sessions: ChatSession[]
  loadAgents: () => Promise<void>
  loadSessions: () => Promise<void>
  
  // API keys
  apiKeys: {
    openai: string
    anthropic: string
    perplexity: string
  }
  updateApiKeys: (keys: Partial<typeof apiKeys>) => void
}

const ChatContext = createContext<ChatContextType | undefined>(undefined)

export const useChatContext = () => {
  const context = useContext(ChatContext)
  if (context === undefined) {
    throw new Error('useChatContext must be used within a ChatProvider')
  }
  return context
}

interface ChatProviderProps {
  children: React.ReactNode
}

export const ChatProvider: React.FC<ChatProviderProps> = ({ children }) => {
  const [messages, setMessages] = useState<Message[]>([])
  const [currentAgent, setCurrentAgent] = useState('code')
  const [currentModel, setCurrentModel] = useState('gpt-4o-mini')
  const [currentSession, setCurrentSession] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [agents, setAgents] = useState<Agent[]>([])
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [apiKeys, setApiKeys] = useState({
    openai: '',
    anthropic: '',
    perplexity: ''
  })

  const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001'

  const addMessage = (message: Message) => {
    setMessages(prev => [...prev, message])
  }

  const clearMessages = () => {
    setMessages([])
  }

  const sendMessage = async (content: string) => {
    if (!content.trim()) return
    
    setIsLoading(true)
    
    try {
      // Add user message
      const userMessage: Message = {
        id: Date.now().toString(),
        content,
        role: 'user',
        agent: currentAgent,
        model: currentModel,
        timestamp: new Date()
      }
      addMessage(userMessage)
      
      // Send to API
      const response = await fetch(`${API_BASE}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          agent: currentAgent,
          model: currentModel,
          session_id: currentSession
        })
      })
      
      if (!response.ok) {
        const error = await response.json()
        throw new Error(error.detail || 'API request failed')
      }
      
      const data = await response.json()
      
      // Add AI response
      const aiMessage: Message = {
        id: data.message_id,
        content: data.response,
        role: 'assistant',
        agent: data.agent,
        model: data.model,
        timestamp: new Date(data.timestamp),
        usage: data.usage
      }
      addMessage(aiMessage)
      
      // Update current session if created
      if (data.session_id && !currentSession) {
        setCurrentSession(data.session_id)
        await loadSessions()
      }
      
    } catch (error) {
      console.error('Send message error:', error)
      toast.error(`Error: ${error.message}`)
    } finally {
      setIsLoading(false)
    }
  }

  const loadChatHistory = async (sessionId: string) => {
    try {
      const response = await fetch(`${API_BASE}/api/chat/history/${sessionId}`)
      if (!response.ok) throw new Error('Failed to load chat history')
      
      const data = await response.json()
      const loadedMessages: Message[] = data.map((msg: any) => ({
        id: msg.message_id,
        content: msg.user_message,
        role: 'user' as const,
        agent: msg.agent,
        model: msg.model,
        timestamp: new Date(msg.timestamp)
      })).concat(data.map((msg: any) => ({
        id: msg.message_id + '_ai',
        content: msg.ai_response,
        role: 'assistant' as const,
        agent: msg.agent,
        model: msg.model,
        timestamp: new Date(msg.timestamp),
        usage: msg.usage
      })))
      
      setMessages(loadedMessages)
      setCurrentSession(sessionId)
      
    } catch (error) {
      console.error('Load chat history error:', error)
      toast.error('Failed to load chat history')
    }
  }

  const loadAgents = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/agents`)
      if (!response.ok) throw new Error('Failed to load agents')
      
      const data = await response.json()
      setAgents(data.agents)
      
    } catch (error) {
      console.error('Load agents error:', error)
      toast.error('Failed to load agents')
    }
  }

  const loadSessions = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/sessions`)
      if (!response.ok) throw new Error('Failed to load sessions')
      
      const data = await response.json()
      setSessions(data)
      
    } catch (error) {
      console.error('Load sessions error:', error)
      toast.error('Failed to load sessions')
    }
  }

  const updateApiKeys = (keys: Partial<typeof apiKeys>) => {
    setApiKeys(prev => ({ ...prev, ...keys }))
    // Save to localStorage
    localStorage.setItem('xionimus_api_keys', JSON.stringify({ ...apiKeys, ...keys }))
  }

  // Load initial data
  useEffect(() => {
    loadAgents()
    loadSessions()
    
    // Load API keys from localStorage
    const savedKeys = localStorage.getItem('xionimus_api_keys')
    if (savedKeys) {
      try {
        setApiKeys(JSON.parse(savedKeys))
      } catch (error) {
        console.error('Failed to parse saved API keys:', error)
      }
    }
  }, [])

  const value: ChatContextType = {
    messages,
    addMessage,
    clearMessages,
    currentAgent,
    currentModel,
    currentSession,
    isLoading,
    setCurrentAgent,
    setCurrentModel,
    setCurrentSession,
    setIsLoading,
    sendMessage,
    loadChatHistory,
    agents,
    sessions,
    loadAgents,
    loadSessions,
    apiKeys,
    updateApiKeys
  }

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  )
}