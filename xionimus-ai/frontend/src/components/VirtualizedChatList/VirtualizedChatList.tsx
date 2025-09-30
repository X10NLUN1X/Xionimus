import React, { useRef, useEffect } from 'react'
import { FixedSizeList as List } from 'react-window'
import AutoSizer from 'react-virtualized-auto-sizer'
import { Box, useColorModeValue } from '@chakra-ui/react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp?: string
  [key: string]: any
}

interface VirtualizedChatListProps {
  messages: Message[]
  renderMessage: (message: Message, index: number) => React.ReactNode
  itemSize?: number
  overscanCount?: number
}

export const VirtualizedChatList: React.FC<VirtualizedChatListProps> = ({
  messages,
  renderMessage,
  itemSize = 150, // Estimated height per message
  overscanCount = 5
}) => {
  const listRef = useRef<List>(null)
  const bgColor = useColorModeValue('gray.50', '#0a1628')

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (listRef.current && messages.length > 0) {
      listRef.current.scrollToItem(messages.length - 1, 'end')
    }
  }, [messages.length])

  const Row = ({ index, style }: { index: number; style: React.CSSProperties }) => {
    const message = messages[index]
    
    return (
      <Box style={style} px={4}>
        {renderMessage(message, index)}
      </Box>
    )
  }

  if (messages.length === 0) {
    return null
  }

  // Use virtualization only for large message lists (>50 messages)
  if (messages.length < 50) {
    return (
      <Box w="100%" h="100%" overflowY="auto" bg={bgColor} px={4}>
        {messages.map((message, index) => (
          <Box key={message.id || index}>
            {renderMessage(message, index)}
          </Box>
        ))}
      </Box>
    )
  }

  return (
    <Box w="100%" h="100%" bg={bgColor}>
      <AutoSizer>
        {({ height, width }) => (
          <List
            ref={listRef}
            height={height}
            width={width}
            itemCount={messages.length}
            itemSize={itemSize}
            overscanCount={overscanCount}
          >
            {Row}
          </List>
        )}
      </AutoSizer>
    </Box>
  )
}
