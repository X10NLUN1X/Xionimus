import React, { useState, useRef, useEffect } from 'react'
import { useChatContext } from '@/context/ChatContext'
import { Button } from '@/components/ui/Button'
import { MessageList } from './MessageList'
import { AgentSelector } from './AgentSelector'
import { ModelSelector } from './ModelSelector'
import { 
  Send, 
  Loader2,
  Mic,
  MicOff,
  Plus
} from 'lucide-react'
import { cn } from '@/lib/utils'

export const ChatInterface: React.FC = () => {
  const {
    messages,
    sendMessage,
    isLoading,
    currentAgent,
    currentModel,
    clearMessages,
    agents
  } = useChatContext()
  
  const [inputMessage, setInputMessage] = useState('')
  const [isListening, setIsListening] = useState(false)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [inputMessage])

  const handleSend = async () => {
    if (!inputMessage.trim() || isLoading) return
    
    const message = inputMessage.trim()
    setInputMessage('')
    await sendMessage(message)
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const currentAgentInfo = agents.find(a => a.id === currentAgent)

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Header */}
      <div className="border-b border-primary/20 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <h1 className="text-2xl font-bold text-primary">XIONIMUS AI</h1>
            <div className="flex items-center space-x-2">
              <AgentSelector />
              <ModelSelector />
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={clearMessages}
              disabled={messages.length === 0}
            >
              <Plus className="h-4 w-4 mr-2" />
              New Chat
            </Button>
          </div>
        </div>
        
        {currentAgentInfo && (
          <div className="mt-2 text-sm text-muted-foreground">
            <span className="font-medium text-primary">{currentAgentInfo.name}:</span> {currentAgentInfo.description}
          </div>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-auto p-4">
        <MessageList messages={messages} />
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-primary/20 p-4">
        <div className="flex items-end space-x-2">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={`Message ${currentAgentInfo?.name || 'AI Agent'}...`}
              className={
                cn(
                  "w-full min-h-[44px] max-h-32 px-3 py-2 rounded-lg resize-none",
                  "bg-secondary border border-primary/20 text-foreground",
                  "placeholder:text-muted-foreground",
                  "focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50",
                  "transition-colors duration-200"
                )
              }
              disabled={isLoading}
              rows={1}
            />
          </div>
          
          <Button
            onClick={() => setIsListening(!isListening)}
            variant={isListening ? "default" : "outline"}
            size="icon"
            disabled={isLoading}
            className="shrink-0"
          >
            {isListening ? <MicOff className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
          </Button>
          
          <Button
            onClick={handleSend}
            disabled={!inputMessage.trim() || isLoading}
            className="shrink-0"
          >
            {isLoading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}
          </Button>
        </div>
        
        {isLoading && (
          <div className="mt-2 flex items-center text-sm text-muted-foreground">
            <Loader2 className="h-3 w-3 animate-spin mr-2" />
            {currentAgentInfo?.name || 'AI Agent'} is thinking...
          </div>
        )}
      </div>
    </div>
  )
}