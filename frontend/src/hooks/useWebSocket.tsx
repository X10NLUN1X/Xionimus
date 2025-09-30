import { useEffect, useRef, useState, useCallback } from 'react'

export interface WebSocketMessage {
  type: 'start' | 'chunk' | 'complete' | 'error' | 'pong'
  content?: string
  full_content?: string
  model?: string
  provider?: string
  timestamp?: string
  message?: string
  chunk_id?: number
}

interface UseWebSocketOptions {
  url: string
  onMessage?: (message: WebSocketMessage) => void
  onOpen?: () => void
  onClose?: () => void
  onError?: (error: Event) => void
  autoConnect?: boolean
}

export const useWebSocket = ({
  url,
  onMessage,
  onOpen,
  onClose,
  onError,
  autoConnect = false
}: UseWebSocketOptions) => {
  const wsRef = useRef<WebSocket | null>(null)
  const [isConnected, setIsConnected] = useState(false)
  const [isConnecting, setIsConnecting] = useState(false)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const reconnectAttemptsRef = useRef(0)
  const maxReconnectAttempts = 5

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log('WebSocket already connected')
      return
    }

    if (wsRef.current?.readyState === WebSocket.CONNECTING) {
      console.log('WebSocket already connecting')
      return
    }

    setIsConnecting(true)

    try {
      const ws = new WebSocket(url)

      ws.onopen = () => {
        console.log('✅ WebSocket connected')
        setIsConnected(true)
        setIsConnecting(false)
        reconnectAttemptsRef.current = 0
        onOpen?.()
      }

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data)
          onMessage?.(message)
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error)
        }
      }

      ws.onclose = () => {
        console.log('❌ WebSocket disconnected')
        setIsConnected(false)
        setIsConnecting(false)
        wsRef.current = null
        onClose?.()

        // Auto-reconnect with exponential backoff
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 10000)
          console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current + 1}/${maxReconnectAttempts})`)
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current++
            connect()
          }, delay)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setIsConnecting(false)
        onError?.(error)
      }

      wsRef.current = ws
    } catch (error) {
      console.error('Failed to create WebSocket:', error)
      setIsConnecting(false)
    }
  }, [url, onMessage, onOpen, onClose, onError])

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current)
      reconnectTimeoutRef.current = null
    }

    if (wsRef.current) {
      wsRef.current.close()
      wsRef.current = null
      setIsConnected(false)
    }
  }, [])

  const send = useCallback((data: any) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(typeof data === 'string' ? data : JSON.stringify(data))
      return true
    } else {
      console.warn('WebSocket not connected, cannot send message')
      return false
    }
  }, [])

  // Auto-connect on mount if enabled
  useEffect(() => {
    if (autoConnect) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [autoConnect, connect, disconnect])

  // Heartbeat to keep connection alive
  useEffect(() => {
    if (!isConnected) return

    const interval = setInterval(() => {
      send({ type: 'ping' })
    }, 30000) // Ping every 30 seconds

    return () => clearInterval(interval)
  }, [isConnected, send])

  return {
    isConnected,
    isConnecting,
    connect,
    disconnect,
    send
  }
}
