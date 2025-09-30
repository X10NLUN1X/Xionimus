import { useState, useCallback } from 'react'
import { useWebSocket, WebSocketMessage } from './useWebSocket'

interface StreamingChatOptions {
  sessionId: string
  onChunk?: (chunk: string) => void
  onComplete?: (fullText: string, metadata: any) => void
  onError?: (error: string) => void
}

export const useStreamingChat = ({
  sessionId,
  onChunk,
  onComplete,
  onError
}: StreamingChatOptions) => {
  const [streamingText, setStreamingText] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)

  // Get backend URL from environment
  const backendUrl = import.meta.env.VITE_REACT_APP_BACKEND_URL || 
                     process.env.REACT_APP_BACKEND_URL || 
                     'http://localhost:8001'
  const wsUrl = backendUrl.replace('http', 'ws') + `/ws/chat/${sessionId}`

  const handleMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'start':
        setIsStreaming(true)
        setStreamingText('')
        break

      case 'chunk':
        if (message.content) {
          setStreamingText(prev => {
            const newText = prev + message.content
            onChunk?.(message.content)
            return newText
          })
        }
        break

      case 'complete':
        setIsStreaming(false)
        if (message.full_content) {
          onComplete?.(message.full_content, {
            model: message.model,
            provider: message.provider,
            timestamp: message.timestamp
          })
        }
        setStreamingText('')
        break

      case 'error':
        setIsStreaming(false)
        onError?.(message.message || 'Unknown error')
        setStreamingText('')
        break

      case 'pong':
        // Heartbeat response
        break
    }
  }, [onChunk, onComplete, onError])

  const {
    isConnected,
    isConnecting,
    connect,
    disconnect,
    send
  } = useWebSocket({
    url: wsUrl,
    onMessage: handleMessage,
    autoConnect: false
  })

  const sendMessage = useCallback((
    content: string,
    options: {
      provider?: string
      model?: string
      messages?: any[]
      ultraThinking?: boolean
      apiKeys?: Record<string, string>
    } = {}
  ) => {
    const success = send({
      type: 'chat',
      content,
      provider: options.provider || 'openai',
      model: options.model || 'gpt-4o',
      messages: options.messages || [],
      ultra_thinking: options.ultraThinking || false,
      api_keys: options.apiKeys || {}
    })

    if (!success) {
      onError?.('Failed to send message: Not connected')
    }

    return success
  }, [send, onError])

  return {
    isConnected,
    isConnecting,
    isStreaming,
    streamingText,
    connect,
    disconnect,
    sendMessage
  }
}
