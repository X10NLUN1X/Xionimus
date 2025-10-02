import React, { useMemo } from 'react'
import { Box, HStack, Text, useColorModeValue } from '@chakra-ui/react'
import { AgentResultsDisplay } from './AgentResultsDisplay'
import { MemoizedMarkdown } from './MemoizedMarkdown'

interface ChatMessage {
  id?: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: Date
  provider?: string
  model?: string
  agent_results?: Array<{
    agent: string
    icon: string
    content: string
    summary: string
    data?: any
  }>
}

interface ChatMessageProps {
  message: ChatMessage
  index: number
}

/**
 * Memoized Chat Message Component
 * Only re-renders when message content actually changes
 * Prevents expensive ReactMarkdown re-parsing on every parent render
 */
export const MemoizedChatMessage = React.memo<ChatMessageProps>(({ message, index }) => {
  const userBg = 'linear-gradient(135deg, #00d4ff, #0094ff)'
  const assistantBg = useColorModeValue('white', 'rgba(15, 30, 50, 0.8)')
  const textColor = message.role === 'user' 
    ? 'white' 
    : useColorModeValue('gray.900', '#E8E8E8')
  const borderColor = message.role === 'user' 
    ? 'rgba(0, 212, 255, 0.5)' 
    : useColorModeValue('gray.200', 'rgba(0, 212, 255, 0.2)')

  // No need to recreate components anymore - using MemoizedMarkdown

  return (
    <HStack
      align="start"
      justify={message.role === 'user' ? 'flex-end' : 'flex-start'}
      w="full"
      mb={4}
    >
      <Box
        bg={message.role === 'user' ? userBg : assistantBg}
        color={textColor}
        px={5}
        py={4}
        borderRadius="lg"
        maxW="85%"
        boxShadow={
          message.role === 'user' 
            ? "0 4px 15px rgba(0, 212, 255, 0.3)" 
            : useColorModeValue("0 2px 8px rgba(0, 0, 0, 0.1)", "0 4px 15px rgba(0, 0, 0, 0.3)")
        }
        border="1px solid"
        borderColor={borderColor}
        sx={{
          fontSize: '15px',
          lineHeight: '1.7',
          letterSpacing: '0.01em',
          WebkitFontSmoothing: 'antialiased',
          MozOsxFontSmoothing: 'grayscale',
          
          '& p': {
            marginBottom: '1em',
            lineHeight: '1.7',
            color: textColor,
          },
          '& h1, & h2, & h3': {
            fontWeight: '600',
            marginTop: '0.75em',
            marginBottom: '0.5em',
          },
          '& ul, & ol': {
            marginLeft: '1.5em',
            marginBottom: '1em',
            lineHeight: '1.7',
          },
          '& li': {
            marginBottom: '0.5em',
            paddingLeft: '0.25em',
          },
        }}
      >
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          components={markdownComponents}
        >
          {message.content}
        </ReactMarkdown>
        
        {message.agent_results && message.agent_results.length > 0 && (
          <AgentResultsDisplay agentResults={message.agent_results} />
        )}
      </Box>
    </HStack>
  )
}, (prevProps, nextProps) => {
  // Custom comparison: only re-render if message actually changed
  const prevMsg = prevProps.message
  const nextMsg = nextProps.message
  
  return (
    prevMsg.id === nextMsg.id &&
    prevMsg.content === nextMsg.content &&
    prevMsg.role === nextMsg.role &&
    JSON.stringify(prevMsg.agent_results) === JSON.stringify(nextMsg.agent_results)
  )
})

MemoizedChatMessage.displayName = 'MemoizedChatMessage'
