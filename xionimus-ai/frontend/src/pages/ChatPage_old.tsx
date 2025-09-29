import React, { useState, useRef, useEffect } from 'react'
import {
  Box,
  VStack,
  HStack,
  Text,
  Textarea,
  Button,
  IconButton,
  Select,
  Badge,
  Flex,
  useColorModeValue,
  Spinner,
  Card,
  CardBody,
  Divider,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useToast,
  useBreakpointValue,
  Stack
} from '@chakra-ui/react'
import {
  ChatIcon,
  ArrowUpIcon,
  CopyIcon,
  DeleteIcon,
  ChevronDownIcon,
  AddIcon
} from '@chakra-ui/icons'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { useApp } from '../contexts/AppContext'
import { format } from 'date-fns'
import { LoadingSpinner } from '../components/Loading/LoadingSpinner'
import { SkeletonLoader } from '../components/Loading/SkeletonLoader'

export const ChatPage: React.FC = () => {
  const {
    messages,
    sendMessage,
    isLoading,
    selectedProvider,
    selectedModel,
    setSelectedProvider,
    setSelectedModel,
    availableProviders,
    availableModels,
    createNewSession,
    sessions,
    loadSession,
    deleteSession,
    currentSession
  } = useApp()
  
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const toast = useToast()
  
  // Responsive breakpoints
  const isMobile = useBreakpointValue({ base: true, md: false })
  const isTablet = useBreakpointValue({ base: false, md: true, lg: false })
  const headerDirection = useBreakpointValue<'column' | 'row'>({ base: 'column', md: 'row' })
  const selectWidth = useBreakpointValue({ base: '100%', md: 'auto' })
  const inputMinH = useBreakpointValue({ base: 10, md: 12 })
  
  const cardBg = useColorModeValue('white', 'gray.800')
  const userBg = useColorModeValue('primary.500', 'primary.600')
  const assistantBg = useColorModeValue('gray.50', 'gray.700')
  const activeBg = useColorModeValue('primary.50', 'primary.900')
  
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
  }, [input])
  
  const handleSend = async () => {
    if (!input.trim() || isLoading) return
    
    const message = input.trim()
    setInput('')
    await sendMessage(message)
  }
  
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }
  
  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text)
      toast({
        title: 'Copied!',
        status: 'success',
        duration: 2000,
      })
    } catch (error) {
      console.error('Copy failed:', error)
    }
  }
  
  const configuredProviders = Object.entries(availableProviders)
    .filter(([_, available]) => available)
    .map(([name]) => name)
  
  return (
    <Flex h="full" direction="column">
      {/* Header */}
      <Box p={{ base: 4, md: 6 }} borderBottom="1px" borderColor={useColorModeValue('gray.200', 'gray.700')}>
        <Stack direction={headerDirection} justify="space-between" spacing={4} w="100%">
          <VStack align="start" spacing={1}>
            <Text fontSize={{ base: 'xl', md: '2xl' }} fontWeight="bold">
              AI Chat
            </Text>
            <Text color="gray.500" fontSize={{ base: 'xs', md: 'sm' }}>
              Chat with advanced AI models
            </Text>
          </VStack>
          
          <Stack 
            direction={{ base: 'column', md: 'row' }} 
            spacing={3} 
            w={{ base: '100%', md: 'auto' }}
          >
            {/* Provider Selector */}
            <Select
              value={selectedProvider}
              onChange={(e) => setSelectedProvider(e.target.value)}
              size="sm"
              w={selectWidth}
              minW={{ md: 32 }}
            >
              {configuredProviders.map(provider => (
                <option key={provider} value={provider}>
                  {provider.charAt(0).toUpperCase() + provider.slice(1)}
                </option>
              ))}
            </Select>
            
            {/* Model Selector */}
            <Select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              size="sm"
              w={selectWidth}
              minW={{ md: 40 }}
            >
              {(availableModels[selectedProvider] || []).map(model => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))}
            </Select>
            
            {/* New Chat Button */}
            <Button
              leftIcon={<AddIcon />}
              size="sm"
              variant="outline"
              onClick={createNewSession}
              w={selectWidth}
            >
              New Chat
            </Button>
            
            {/* Sessions Menu */}
            <Menu>
              <MenuButton
                as={Button}
                rightIcon={<ChevronDownIcon />}
                size="sm"
                variant="ghost"
                w={selectWidth}
              >
                Sessions ({sessions.length})
              </MenuButton>
              <MenuList maxH="300px" overflowY="auto">
                {sessions.map((session) => (
                  <MenuItem
                    key={session.session_id}
                    onClick={() => loadSession(session.session_id)}
                    bg={currentSession === session.session_id ? activeBg : 'transparent'}
                  >
                    <VStack align="start" spacing={1} flex={1}>
                      <Text fontSize="sm" fontWeight="medium">
                        {session.name}
                      </Text>
                      <HStack justify="space-between" w="full">
                        <Text fontSize="xs" color="gray.500">
                          {session.message_count} messages
                        </Text>
                        <Text fontSize="xs" color="gray.500">
                          {format(session.created_at, 'MMM dd')}
                        </Text>
                      </HStack>
                    </VStack>
                  </MenuItem>
                ))}
                {sessions.length === 0 && (
                  <MenuItem isDisabled>
                    <Text fontSize="sm" color="gray.500">
                      No sessions yet
                    </Text>
                  </MenuItem>
                )}
              </MenuList>
            </Menu>
          </Stack>
        </Stack>
        
        {/* Status Indicators */}
        <HStack mt={4} spacing={2} flexWrap="wrap">
          <Badge colorScheme={configuredProviders.length > 0 ? 'green' : 'red'} fontSize={{ base: 'xs', md: 'sm' }}>
            {configuredProviders.length}/3 AI Providers
          </Badge>
          {currentSession && (
            <Badge colorScheme="blue" fontSize={{ base: 'xs', md: 'sm' }}>
              Session Active
            </Badge>
          )}
        </HStack>
      </Box>
      
      {/* Chat Messages */}
      <Box flex={1} overflowY="auto" p={{ base: 4, md: 6 }}>
        <VStack spacing={{ base: 4, md: 6 }} align="stretch">
          {messages.length === 0 ? (
            <Flex
              direction="column"
              align="center"
              justify="center"
              h="full"
              textAlign="center"
              py={{ base: 10, md: 20 }}
            >
              <ChatIcon w={{ base: 12, md: 16 }} h={{ base: 12, md: 16 }} color="gray.400" mb={4} />
              <Text fontSize={{ base: 'lg', md: 'xl' }} fontWeight="semibold" mb={2}>
                Welcome to Xionimus AI
              </Text>
              <Text color="gray.500" maxW="md" fontSize={{ base: 'sm', md: 'md' }} px={{ base: 4, md: 0 }}>
                Start a conversation with AI. Choose your preferred provider and model, 
                then send your first message below.
              </Text>
              {configuredProviders.length === 0 && (
                <Text color="red.500" mt={4} fontSize={{ base: 'xs', md: 'sm' }} px={{ base: 4, md: 0 }}>
                  ⚠️ Please configure API keys in Settings to enable AI chat
                </Text>
              )}
            </Flex>
          ) : (
            messages.map((message, index) => (
              <Card 
                key={index} 
                bg={message.role === 'user' ? userBg : assistantBg}
                size={{ base: 'sm', md: 'md' }}
              >
                <CardBody p={{ base: 3, md: 4 }}>
                  <HStack justify="space-between" mb={{ base: 2, md: 3 }} flexWrap="wrap">
                    <HStack spacing={2}>
                      <Text
                        fontSize={{ base: 'xs', md: 'sm' }}
                        fontWeight="bold"
                        color={message.role === 'user' ? 'white' : 'inherit'}
                      >
                        {message.role === 'user' ? 'You' : 'Assistant'}
                      </Text>
                      {message.provider && (
                        <Badge size="sm" colorScheme="purple" fontSize="xs">
                          {message.provider} {message.model}
                        </Badge>
                      )}
                    </HStack>
                    
                    <HStack spacing={1}>
                      <IconButton
                        aria-label="Copy message"
                        icon={<CopyIcon />}
                        size="xs"
                        variant="ghost"
                        onClick={() => copyToClipboard(message.content)}
                      />
                      {message.timestamp && (
                        <Text fontSize="xs" color={message.role === 'user' ? 'whiteAlpha.700' : 'gray.500'}>
                          {format(message.timestamp, 'HH:mm')}
                        </Text>
                      )}
                    </HStack>
                  </HStack>
                  
                  {message.role === 'user' ? (
                    <Text 
                      color="white" 
                      whiteSpace="pre-wrap" 
                      fontSize={{ base: 'sm', md: 'md' }}
                    >
                      {message.content}
                    </Text>
                  ) : (
                    <Box
                      fontSize={{ base: 'sm', md: 'md' }}
                      sx={{
                        '& pre': {
                          bg: useColorModeValue('gray.100', 'gray.800'),
                          p: { base: 2, md: 3 },
                          rounded: 'md',
                          fontSize: { base: 'xs', md: 'sm' },
                          overflowX: 'auto',
                        },
                        '& code': {
                          bg: useColorModeValue('gray.100', 'gray.800'),
                          px: 1,
                          py: 0.5,
                          rounded: 'sm',
                          fontSize: { base: 'xs', md: 'sm' },
                        },
                      }}
                    >
                      <ReactMarkdown
                        remarkPlugins={[remarkGfm]}
                        components={{
                          code({ node, inline, className, children, ...props }) {
                            const match = /language-(\w+)/.exec(className || '')
                            return !inline && match ? (
                              <SyntaxHighlighter
                                style={vscDarkPlus}
                                language={match[1]}
                                PreTag="div"
                                {...props}
                              >
                                {String(children).replace(/\n$/, '')}
                              </SyntaxHighlighter>
                            ) : (
                              <code className={className} {...props}>
                                {children}
                              </code>
                            )
                          }
                        }}
                      >
                        {message.content}
                      </ReactMarkdown>
                    </Box>
                  )}
                  
                  {message.usage && (
                    <Text fontSize="xs" color="gray.500" mt={2}>
                      {message.usage.prompt_tokens || 0} → {message.usage.completion_tokens || 0} tokens
                    </Text>
                  )}
                </CardBody>
              </Card>
            ))
          )}
          
          {isLoading && (
            <Card bg={assistantBg}>
              <CardBody p={{ base: 3, md: 4 }}>
                <HStack spacing={3}>
                  <Spinner size="sm" color="primary.500" />
                  <Text color="gray.500" fontSize={{ base: 'sm', md: 'md' }}>
                    AI is thinking...
                  </Text>
                </HStack>
              </CardBody>
            </Card>
          )}
          
          <div ref={messagesEndRef} />
        </VStack>
      </Box>
      
      {/* Input Area */}
      <Box p={{ base: 4, md: 6 }} borderTop="1px" borderColor={useColorModeValue('gray.200', 'gray.700')}>
        <Stack direction={{ base: 'column', md: 'row' }} spacing={3}>
          <Textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={`Message ${selectedProvider} ${selectedModel}...`}
            resize="none"
            minH={inputMinH}
            maxH={{ base: 24, md: 32 }}
            disabled={isLoading || configuredProviders.length === 0}
            fontSize={{ base: 'sm', md: 'md' }}
          />
          <IconButton
            aria-label="Send message"
            icon={isLoading ? <Spinner size="sm" /> : <ArrowUpIcon />}
            colorScheme="primary"
            onClick={handleSend}
            disabled={!input.trim() || isLoading || configuredProviders.length === 0}
            size={{ base: 'md', md: 'lg' }}
            w={{ base: '100%', md: 'auto' }}
          />
        </Stack>
        
        {configuredProviders.length === 0 && (
          <Text color="red.500" fontSize={{ base: 'xs', md: 'sm' }} mt={2}>
            ⚠️ Please configure API keys in Settings to enable chat
          </Text>
        )}
      </Box>
    </Flex>
  )
}