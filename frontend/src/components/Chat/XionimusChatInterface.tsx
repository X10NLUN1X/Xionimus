import React, { useState, useRef, useEffect } from 'react'
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Input,
  Textarea,
  IconButton,
  Flex,
  useColorModeValue,
  Avatar,
  Badge,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Divider,
  Spinner,
  useToast,
  Tooltip,
  Card,
  CardBody
} from '@chakra-ui/react'
import {
  ArrowUpIcon,
  ChevronDownIcon,
  CopyIcon,
  DeleteIcon,
  AttachmentIcon,
  SettingsIcon
} from '@chakra-ui/icons'
import { useApp } from '../../contexts/AppContext'
import ReactMarkdown from 'react-markdown'

interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  timestamp: Date
  provider?: string
  model?: string
}

export const XionimusChatInterface: React.FC = () => {
  const {
    messages,
    isLoading,
    sendMessage,
    selectedProvider,
    setSelectedProvider,
    selectedModel,
    setSelectedModel,
    availableProviders,
    availableModels
  } = useApp()

  const [inputValue, setInputValue] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const toast = useToast()

  // Luxury theme colors
  const chatBg = useColorModeValue('rgba(10, 10, 10, 0.98)', 'rgba(0, 0, 0, 0.98)')
  const messageBg = useColorModeValue('rgba(17, 17, 17, 0.95)', 'rgba(17, 17, 17, 0.95)')
  const userMessageBg = useColorModeValue('linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(0, 148, 255, 0.1))', 'linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 148, 255, 0.15))')
  const assistantMessageBg = useColorModeValue('rgba(30, 30, 30, 0.8)', 'rgba(30, 30, 30, 0.8)')
  const inputBg = useColorModeValue('rgba(17, 17, 17, 0.95)', 'rgba(17, 17, 17, 0.95)')
  const borderColor = useColorModeValue('rgba(0, 212, 255, 0.2)', 'rgba(0, 212, 255, 0.3)')
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return
    
    try {
      await sendMessage(inputValue.trim())
      setInputValue('')
    } catch (error) {
      toast({
        title: 'Error sending message',
        description: 'Please try again or check your API configuration',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const getProviderColor = (provider: string) => {
    const colors = {
      openai: '#00D9FF',
      anthropic: '#FF6B35',
      perplexity: '#6366F1'
    }
    return colors[provider as keyof typeof colors] || '#00d4ff'
  }

  const getModelDisplayName = (model: string) => {
    const modelNames: Record<string, string> = {
      'gpt-4o': 'GPT-4o',
      'gpt-4o-mini': 'GPT-4o Mini',
      'claude-3-5-sonnet-20241022': 'Claude 3.5 Sonnet',
      'claude-3-5-haiku-20241022': 'Claude 3.5 Haiku',
      'llama-3.1-sonar-large-128k-online': 'Llama 3.1 Sonar Large',
      'llama-3.1-sonar-small-128k-online': 'Llama 3.1 Sonar Small'
    }
    return modelNames[model] || model
  }

  const availableProvidersList = Object.entries(availableProviders)
    .filter(([, available]) => available)
    .map(([provider]) => provider)

  return (
    <Flex direction="column" h="100vh" bg={chatBg} data-testid="chat-interface">
      {/* Header */}
      <Box
        p={4}
        borderBottom="1px solid"
        borderColor={borderColor}
        bg={messageBg}
        backdropFilter="blur(20px)"
        data-testid="chat-header"
      >
        <HStack justify="space-between" data-testid="chat-header-content">
          <VStack align="start" spacing={1}>
            <Text
              fontSize="xl"
              fontWeight="700"
              color="#00d4ff"
              fontFamily="'Inter', sans-serif"
            >
              AI Chat
            </Text>
            <Text fontSize="sm" color="rgba(255, 255, 255, 0.6)">
              Powered by {selectedProvider}
            </Text>
          </VStack>
          
          <HStack spacing={2}>
            {/* Provider Selection */}
            <Menu>
              <MenuButton
                as={Button}
                rightIcon={<ChevronDownIcon />}
                size="sm"
                bg="rgba(0, 212, 255, 0.1)"
                color="#00d4ff"
                border="1px solid"
                borderColor="rgba(0, 212, 255, 0.3)"
                _hover={{
                  bg: "rgba(0, 212, 255, 0.2)",
                  borderColor: "#00d4ff"
                }}
                data-testid="provider-selector"
              >
                <HStack spacing={2}>
                  <Box
                    w="8px"
                    h="8px"
                    borderRadius="50%"
                    bg={getProviderColor(selectedProvider)}
                  />
                  <Text>{selectedProvider.toUpperCase()}</Text>
                </HStack>
              </MenuButton>
              <MenuList
                bg={messageBg}
                borderColor={borderColor}
                shadow="xl"
              >
                {availableProvidersList.map((provider) => (
                  <MenuItem
                    key={provider}
                    onClick={() => setSelectedProvider(provider)}
                    bg="transparent"
                    _hover={{ bg: "rgba(0, 212, 255, 0.1)" }}
                    color={provider === selectedProvider ? "#00d4ff" : "rgba(255, 255, 255, 0.8)"}
                  >
                    <HStack spacing={2}>
                      <Box
                        w="8px"
                        h="8px"
                        borderRadius="50%"
                        bg={getProviderColor(provider)}
                      />
                      <Text>{provider.toUpperCase()}</Text>
                    </HStack>
                  </MenuItem>
                ))}
              </MenuList>
            </Menu>
          </HStack>
        </HStack>
      </Box>

      {/* Messages Area */}
      <Box flex={1} overflowY="auto" p={4} data-testid="messages-area">
        {messages.length === 0 ? (
          <VStack
            spacing={6}
            justify="center"
            h="100%"
            textAlign="center"
            color="rgba(255, 255, 255, 0.6)"
            data-testid="empty-state"
          >
            <Box
              w="80px"
              h="80px"
              bg="linear-gradient(135deg, rgba(0, 212, 255, 0.2), rgba(0, 148, 255, 0.1))"
              borderRadius="xl"
              display="flex"
              alignItems="center"
              justifyContent="center"
              border="2px solid"
              borderColor="rgba(0, 212, 255, 0.3)"
            >
              <Text fontSize="2xl" fontWeight="bold" color="#00d4ff" textShadow="0 0 15px rgba(0, 212, 255, 0.5)">
                X
              </Text>
            </Box>
            
            <VStack spacing={2}>
              <Text fontSize="xl" fontWeight="600" color="#00d4ff" textShadow="0 0 10px rgba(0, 212, 255, 0.4)">
                Welcome to Xionimus AI
              </Text>
              <Text fontSize="md" maxW="md">
                Start a conversation with our advanced AI models. Choose your preferred provider and model from the options above.
              </Text>
            </VStack>

            <VStack spacing={2}>
              <Text fontSize="sm" fontWeight="500" color="#00d4ff">
                Quick Start:
              </Text>
              <HStack spacing={4} wrap="wrap" justify="center">
                <Button
                  size="sm"
                  variant="outline"
                  borderColor="rgba(0, 212, 255, 0.3)"
                  color="rgba(255, 255, 255, 0.8)"
                  _hover={{ borderColor: "#00d4ff", color: "#00d4ff" }}
                  onClick={() => setInputValue("Explain quantum computing in simple terms")}
                >
                  Ask about Science
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  borderColor="rgba(0, 212, 255, 0.3)"
                  color="rgba(255, 255, 255, 0.8)"
                  _hover={{ borderColor: "#00d4ff", color: "#00d4ff" }}
                  onClick={() => setInputValue("Write a Python function to sort a list")}
                >
                  Code Help
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  borderColor="rgba(0, 212, 255, 0.3)"
                  color="rgba(255, 255, 255, 0.8)"
                  _hover={{ borderColor: "#00d4ff", color: "#00d4ff" }}
                  onClick={() => setInputValue("What's trending in AI today?")}
                >
                  Current Events
                </Button>
              </HStack>
            </VStack>
          </VStack>
        ) : (
          <VStack spacing={4} align="stretch" data-testid="messages-list">
            {messages.map((message) => (
              <Card
                key={message.id}
                bg={message.role === 'user' ? userMessageBg : assistantMessageBg}
                border="1px solid"
                borderColor={message.role === 'user' ? "rgba(0, 212, 255, 0.3)" : "rgba(255, 255, 255, 0.1)"}
                borderRadius="xl"
                overflow="hidden"
                backdropFilter="blur(10px)"
                data-testid={`message-${message.role}`}
              >
                <CardBody p={4}>
                  <VStack align="stretch" spacing={3}>
                    {/* Message Header */}
                    <HStack justify="space-between">
                      <HStack spacing={3}>
                        <Avatar
                          size="sm"
                          bg={message.role === 'user' ? "linear-gradient(135deg, #00d4ff, #0094ff)" : "linear-gradient(135deg, #666, #999)"}
                          color={message.role === 'user' ? "#000" : "#FFF"}
                          name={message.role === 'user' ? 'You' : 'AI'}
                        />
                        <VStack align="start" spacing={0}>
                          <Text
                            fontSize="sm"
                            fontWeight="600"
                            color={message.role === 'user' ? "#00d4ff" : "#FFF"}
                          >
                            {message.role === 'user' ? 'You' : 'AI Assistant'}
                          </Text>
                          {message.provider && (
                            <HStack spacing={2}>
                              <Badge
                                size="xs"
                                bg={getProviderColor(message.provider)}
                                color="#000"
                              >
                                {message.provider}
                              </Badge>
                              {message.model && (
                                <Text fontSize="xs" color="rgba(255, 255, 255, 0.5)">
                                  {getModelDisplayName(message.model)}
                                </Text>
                              )}
                            </HStack>
                          )}
                        </VStack>
                      </HStack>
                      
                      <HStack spacing={1}>
                        <Tooltip label="Copy message">
                          <IconButton
                            aria-label="Copy"
                            icon={<CopyIcon />}
                            size="xs"
                            variant="ghost"
                            color="rgba(255, 255, 255, 0.5)"
                            _hover={{ color: "#00d4ff" }}
                            onClick={() => {
                              navigator.clipboard.writeText(message.content)
                              toast({
                                title: 'Copied to clipboard',
                                status: 'success',
                                duration: 2000,
                              })
                            }}
                          />
                        </Tooltip>
                      </HStack>
                    </HStack>

                    {/* Message Content */}
                    <Box
                      color={message.role === 'user' ? "#FFF" : "rgba(255, 255, 255, 0.9)"}
                      fontSize="sm"
                      lineHeight="1.6"
                    >
                      {message.role === 'assistant' ? (
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                      ) : (
                        <Text whiteSpace="pre-wrap">{message.content}</Text>
                      )}
                    </Box>
                  </VStack>
                </CardBody>
              </Card>
            ))}

            {isLoading && (
              <Card
                bg={assistantMessageBg}
                border="1px solid"
                borderColor="rgba(255, 255, 255, 0.1)"
                borderRadius="xl"
                data-testid="loading-indicator"
              >
                <CardBody p={4}>
                  <HStack spacing={3}>
                    <Avatar
                      size="sm"
                      bg="linear-gradient(135deg, #666, #999)"
                      color="#FFF"
                      name="AI"
                    />
                    <HStack spacing={2}>
                      <Spinner size="sm" color="#00d4ff" />
                      <Text fontSize="sm" color="rgba(255, 255, 255, 0.7)">
                        AI is thinking...
                      </Text>
                    </HStack>
                  </HStack>
                </CardBody>
              </Card>
            )}

            <div ref={messagesEndRef} />
          </VStack>
        )}
      </Box>

      {/* Input Area */}
      <Box
        p={4}
        borderTop="1px solid"
        borderColor={borderColor}
        bg={messageBg}
        backdropFilter="blur(20px)"
      >
        <HStack spacing={3}>
          <Box flex={1} position="relative">
            <Textarea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Type your message..."
              bg={inputBg}
              border="1px solid"
              borderColor="rgba(0, 212, 255, 0.2)"
              color="#FFF"
              _placeholder={{ color: "rgba(255, 255, 255, 0.4)" }}
              _focus={{
                borderColor: "#00d4ff",
                boxShadow: "0 0 0 1px #00d4ff, 0 0 20px rgba(0, 212, 255, 0.3)",
                bg: inputBg
              }}
              resize="none"
              maxH="120px"
              minH="48px"
              borderRadius="xl"
              pr="50px"
            />
            
            <IconButton
              aria-label="Send message"
              icon={<ArrowUpIcon />}
              size="sm"
              position="absolute"
              right="8px"
              bottom="8px"
              bg="linear-gradient(135deg, #00d4ff, #0094ff)"
              color="#000"
              _hover={{
                bg: "linear-gradient(135deg, #0094ff, #00d4ff)",
                transform: "scale(1.05)"
              }}
              _active={{ transform: "scale(0.95)" }}
              isDisabled={!inputValue.trim() || isLoading}
              onClick={handleSend}
              borderRadius="lg"
            />
          </Box>
        </HStack>
        
        <HStack
          spacing={2}
          mt={2}
          fontSize="xs"
          color="rgba(255, 255, 255, 0.5)"
          justify="center"
        >
          <Text>Press Enter to send • Shift+Enter for new line</Text>
        </HStack>
      </Box>
    </Flex>
  )
}