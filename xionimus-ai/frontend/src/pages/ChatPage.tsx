import React, { useState, useRef, useEffect } from 'react'
import {
  Box,
  VStack,
  HStack,
  Text,
  Textarea,
  Button,
  IconButton,
  Flex,
  useColorModeValue,
  Spinner,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useToast,
  Switch,
  Tooltip,
  Avatar,
  Container,
  Divider
} from '@chakra-ui/react'
import {
  ChatIcon,
  ArrowUpIcon,
  SettingsIcon,
  AddIcon,
  AttachmentIcon,
  ChevronDownIcon
} from '@chakra-ui/icons'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { useApp } from '../contexts/AppContext'
import { useGitHub } from '../contexts/GitHubContext'
import { useNavigate } from 'react-router-dom'
import { GitHubPushDialog } from '../components/GitHubPushDialog'

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
    currentSession,
    stopGeneration
  } = useApp()
  
  const [input, setInput] = useState('')
  const [ultraThinking, setUltraThinking] = useState(false)
  const [isGitHubPushOpen, setIsGitHubPushOpen] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const toast = useToast()
  const navigate = useNavigate()
  const github = useGitHub()
  
  const bgColor = useColorModeValue('#f7fafc', '#0a1628')
  const borderColor = useColorModeValue('gray.200', 'rgba(0, 212, 255, 0.3)')
  const userBg = 'linear-gradient(135deg, #00d4ff, #0094ff)'
  const assistantBg = useColorModeValue('gray.50', 'rgba(15, 30, 50, 0.8)')
  const inputBg = useColorModeValue('white', 'rgba(15, 30, 50, 0.6)')
  const headerBg = useColorModeValue('white', 'rgba(10, 22, 40, 0.95)')
  
  // Auto-scroll
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])
  
  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`
    }
  }, [input])
  
  const handleSend = async () => {
    if (!input.trim() || isLoading) return
    
    const message = input.trim()
    setInput('')
    await sendMessage(message, ultraThinking)
  }
  
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleStop = () => {
    if (stopGeneration) {
      stopGeneration()
      toast({
        title: 'Generation gestoppt',
        description: 'Die KI-Generierung wurde unterbrochen',
        status: 'warning',
        duration: 3000
      })
    }
  }

  const handleNewChat = () => {
    createNewSession()
    toast({
      title: 'Neuer Chat erstellt',
      status: 'success',
      duration: 2000
    })
  }

  const handleGitHubPush = () => {
    // Extract generated code from last assistant message
    const lastAssistantMsg = messages.filter(m => m.role === 'assistant').pop()
    const generatedCode = lastAssistantMsg?.content || ''
    
    setIsGitHubPushOpen(true)
  }

  // Welcome Screen
  if (messages.length === 0) {
    return (
      <Box minH="100vh" bg={bgColor}>
        {/* Header */}
        <Flex
          h="60px"
          px={4}
          borderBottom="1px solid"
          borderColor={borderColor}
          align="center"
          justify="space-between"
          bg={headerBg}
          position="sticky"
          top={0}
          zIndex={10}
        >
          <HStack spacing={3}>
            <Box
              w="32px"
              h="32px"
              bg="linear-gradient(135deg, #00d4ff, #0094ff)"
              borderRadius="lg"
              display="flex"
              alignItems="center"
              justifyContent="center"
              boxShadow="0 4px 15px rgba(0, 212, 255, 0.4)"
            >
              <Text color="white" fontWeight="900" fontSize="sm" textShadow="0 0 10px rgba(255, 255, 255, 0.5)">X</Text>
            </Box>
            <Text fontWeight="700" fontSize="lg" color={useColorModeValue('#0094ff', '#00d4ff')} textShadow={useColorModeValue('none', '0 0 15px rgba(0, 212, 255, 0.5)')}>Xionimus AI</Text>
          </HStack>
          
          <HStack spacing={2}>
            <IconButton
              aria-label="Neuer Chat"
              icon={<AddIcon />}
              variant="ghost"
              onClick={handleNewChat}
            />
            <IconButton
              aria-label="Einstellungen"
              icon={<SettingsIcon />}
              variant="ghost"
              onClick={() => navigate('/settings')}
            />
          </HStack>
        </Flex>

        {/* Welcome Content */}
        <Container maxW="4xl" py={20}>
          <VStack spacing={8} align="center" textAlign="center">
            <Box
              w="80px"
              h="80px"
              bg="linear-gradient(135deg, #00d4ff, #0094ff)"
              borderRadius="2xl"
              display="flex"
              alignItems="center"
              justifyContent="center"
              boxShadow="0 10px 40px rgba(0, 212, 255, 0.5), 0 0 60px rgba(0, 148, 255, 0.3)"
              position="relative"
              _before={{
                content: '""',
                position: 'absolute',
                inset: '-3px',
                borderRadius: '2xl',
                background: 'linear-gradient(135deg, #00d4ff, #0094ff)',
                zIndex: -1,
                filter: 'blur(10px)',
                opacity: 0.7,
              }}
            >
              <Text color="white" fontWeight="900" fontSize="3xl" textShadow="0 0 15px rgba(255, 255, 255, 0.8)">X</Text>
            </Box>
            
            <VStack spacing={2}>
              <Text 
                fontSize="4xl" 
                fontWeight="800" 
                color={useColorModeValue('#0094ff', '#00d4ff')} 
                textShadow={useColorModeValue('none', '0 0 30px rgba(0, 212, 255, 0.5)')}
              >
                Willkommen bei Xionimus AI
              </Text>
              <Text fontSize="lg" color={useColorModeValue('gray.600', 'rgba(0, 212, 255, 0.7)')}>
                Ihr spezialisierter Code-Assistent
              </Text>
            </VStack>

            <VStack spacing={4} w="100%" maxW="2xl" mt={8}>
              <Text fontSize="md" fontWeight="600" color={useColorModeValue('gray.700', 'rgba(0, 212, 255, 0.8)')}>
                Beispiel-Anfragen:
              </Text>
              
              {[
                '🚀 Erstelle eine React Todo-App mit TypeScript',
                '🔧 Hilf mir einen Python FastAPI Server aufzusetzen',
                '🎨 Baue ein responsives Dashboard mit Tailwind CSS'
              ].map((example, i) => (
                <Button
                  key={i}
                  w="100%"
                  h="auto"
                  py={4}
                  justifyContent="flex-start"
                  variant="outline"
                  borderColor={useColorModeValue('gray.300', 'rgba(0, 212, 255, 0.3)')}
                  color={useColorModeValue('gray.700', 'rgba(0, 212, 255, 0.9)')}
                  onClick={() => setInput(example.substring(2))}
                  _hover={{ 
                    bg: assistantBg,
                    borderColor: useColorModeValue('#0094ff', '#00d4ff'),
                    boxShadow: useColorModeValue('0 0 10px rgba(0, 148, 255, 0.2)', '0 0 20px rgba(0, 212, 255, 0.3)')
                  }}
                >
                  <Text textAlign="left">{example}</Text>
                </Button>
              ))}
            </VStack>
          </VStack>
        </Container>

        {/* Input Area (Fixed Bottom) */}
        <Box
          position="fixed"
          bottom={0}
          left={0}
          right={0}
          bg={bgColor}
          borderTop="1px solid"
          borderColor={borderColor}
          p={4}
        >
          <Container maxW="4xl">
            <VStack spacing={3} align="stretch">
              {/* Main Input with Ultra Thinking Toggle */}
              <HStack align="flex-end" spacing={3}>
                {/* Ultra Thinking Toggle */}
                <VStack spacing={1} align="center">
                  <Tooltip 
                    label="Ultra Thinking: Aktiviert erweiterte Reasoning-Modi für komplexe Aufgaben (Claude)" 
                    placement="top"
                    bg="rgba(0, 212, 255, 0.9)"
                    color="white"
                  >
                    <Box 
                      p={2} 
                      borderRadius="md" 
                      bg={ultraThinking ? "rgba(0, 212, 255, 0.1)" : "transparent"}
                      border="2px solid"
                      borderColor={ultraThinking ? (useColorModeValue('#0094ff', '#00d4ff')) : "transparent"}
                      transition="all 0.3s ease"
                      boxShadow={ultraThinking ? "0 0 20px rgba(0, 212, 255, 0.4)" : "none"}
                    >
                      <Switch
                        size="lg"
                        colorScheme="cyan"
                        isChecked={ultraThinking}
                        onChange={(e) => setUltraThinking(e.target.checked)}
                      />
                      <Text 
                        fontSize="xs" 
                        mt={1} 
                        color={ultraThinking ? (useColorModeValue('#0094ff', '#00d4ff')) : 'gray.500'}
                        textAlign="center"
                        fontWeight={ultraThinking ? "bold" : "normal"}
                      >
                        🧠
                      </Text>
                    </Box>
                  </Tooltip>
                </VStack>

                {/* Textarea */}
                <Box flex={1} position="relative">
                  <Textarea
                    ref={textareaRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Beschreiben Sie Ihr Programmier-Projekt..."
                    bg={inputBg}
                    border="2px solid"
                    borderColor={borderColor}
                    _focus={{
                      borderColor: '#00d4ff',
                      boxShadow: '0 0 0 1px #00d4ff, 0 0 20px rgba(0, 212, 255, 0.3)'
                    }}
                    resize="none"
                    minH="56px"
                    maxH="200px"
                    pr="50px"
                    fontSize="md"
                  />
                  
                  {/* Send Button (Inside Textarea) */}
                  <IconButton
                    aria-label="Senden"
                    icon={<ArrowUpIcon />}
                    position="absolute"
                    right="8px"
                    bottom="8px"
                    size="sm"
                    bg="linear-gradient(135deg, #00d4ff, #0094ff)"
                    color="white"
                    borderRadius="md"
                    onClick={handleSend}
                    isLoading={isLoading}
                    isDisabled={!input.trim() || isLoading}
                    _hover={{
                      bg: "linear-gradient(135deg, #0094ff, #00d4ff)",
                      boxShadow: "0 0 20px rgba(0, 212, 255, 0.6)"
                    }}
                    boxShadow="0 2px 10px rgba(0, 212, 255, 0.4)"
                  />
                </Box>
              </HStack>

              {/* Toolbar Buttons */}
              <Flex
                wrap="wrap"
                gap={2}
                justify="space-between"
                align="center"
              >
                <HStack spacing={2}>
                  <Button
                    size="sm"
                    variant="ghost"
                    leftIcon={<AttachmentIcon />}
                    onClick={() => toast({ title: 'Anhang-Feature kommt bald', status: 'info', duration: 2000 })}
                  >
                    📎 Anhang
                  </Button>
                  
                  <Button
                    size="sm"
                    variant="ghost"
                    isDisabled={!isLoading}
                    onClick={handleStop}
                  >
                    ⏸️ Stopp
                  </Button>
                  
                  <Menu>
                    <MenuButton as={Button} size="sm" variant="ghost" rightIcon={<ChevronDownIcon />}>
                      🌿 Branch: main
                    </MenuButton>
                    <MenuList>
                      <MenuItem>main</MenuItem>
                      <MenuItem>develop</MenuItem>
                      <MenuItem>+ Neuer Branch</MenuItem>
                    </MenuList>
                  </Menu>
                </HStack>

                <HStack spacing={2}>
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => toast({ title: 'Fork-Feature kommt bald', status: 'info', duration: 2000 })}
                  >
                    🔀 Verzweigen
                  </Button>
                  
                  <Button
                    size="sm"
                    variant="solid"
                    colorScheme="green"
                    onClick={handleGitHubPush}
                  >
                    📤 GitHub Push
                  </Button>
                </HStack>
              </Flex>

              {/* Model Selector & Info */}
              <Flex justify="space-between" align="center" fontSize="xs" color="gray.500">
                <HStack spacing={2}>
                  <Text>Modell:</Text>
                  <Menu>
                    <MenuButton as={Button} size="xs" variant="link" rightIcon={<ChevronDownIcon />}>
                      {selectedProvider}/{selectedModel}
                    </MenuButton>
                    <MenuList>
                      {Object.entries(availableModels).map(([provider, models]) => (
                        <Box key={provider}>
                          <Text px={3} py={1} fontSize="xs" fontWeight="bold" color="gray.500">
                            {provider.toUpperCase()}
                          </Text>
                          {models.map((model: string) => (
                            <MenuItem
                              key={model}
                              onClick={() => {
                                setSelectedProvider(provider)
                                setSelectedModel(model)
                              }}
                              fontSize="sm"
                            >
                              {model}
                            </MenuItem>
                          ))}
                        </Box>
                      ))}
                    </MenuList>
                  </Menu>
                </HStack>
                
                {ultraThinking && (
                  <HStack spacing={1}>
                    <Text>🧠 Erweitertes Denken aktiv</Text>
                  </HStack>
                )}
              </Flex>
            </VStack>
          </Container>
        </Box>

        {/* GitHub Push Dialog */}
        <GitHubPushDialog
          isOpen={isGitHubPushOpen}
          onClose={() => setIsGitHubPushOpen(false)}
          generatedCode={messages.filter(m => m.role === 'assistant').pop()?.content}
        />
      </Box>
    )
  }

  // Chat View
  return (
    <Box minH="100vh" bg={bgColor}>
      {/* Header */}
      <Flex
        h="60px"
        px={4}
        borderBottom="1px solid"
        borderColor={borderColor}
        align="center"
        justify="space-between"
        bg={headerBg}
        position="sticky"
        top={0}
        zIndex={10}
      >
        <HStack spacing={3}>
          <Box
            w="32px"
            h="32px"
            bg="linear-gradient(135deg, #FFD700, #FFA500)"
            borderRadius="lg"
            display="flex"
            alignItems="center"
            justifyContent="center"
          >
            <Text color="#000" fontWeight="900" fontSize="sm">X</Text>
          </Box>
          <Text fontWeight="700" fontSize="lg">Xionimus AI</Text>
        </HStack>
        
        <HStack spacing={2}>
          <IconButton
            aria-label="Neuer Chat"
            icon={<AddIcon />}
            variant="ghost"
            onClick={handleNewChat}
          />
          <IconButton
            aria-label="Einstellungen"
            icon={<SettingsIcon />}
            variant="ghost"
            onClick={() => navigate('/settings')}
          />
        </HStack>
      </Flex>

      {/* Messages */}
      <Container maxW="4xl" pb="200px" pt={4}>
        <VStack spacing={6} align="stretch">
          {messages.map((msg, idx) => (
            <Flex
              key={idx}
              gap={3}
              flexDirection={msg.role === 'user' ? 'row-reverse' : 'row'}
            >
              <Avatar
                size="sm"
                name={msg.role === 'user' ? 'User' : 'Xionimus'}
                bg={msg.role === 'user' ? userBg : 'linear-gradient(135deg, #00d4ff, #0094ff)'}
              />
              
              <Box
                flex={1}
                bg={msg.role === 'user' ? userBg : assistantBg}
                color={msg.role === 'user' ? 'white' : useColorModeValue('gray.800', 'white')}
                px={4}
                py={3}
                borderRadius="lg"
                maxW="85%"
                boxShadow={msg.role === 'user' ? "0 4px 15px rgba(0, 212, 255, 0.3)" : useColorModeValue("0 2px 8px rgba(0, 0, 0, 0.1)", "0 4px 15px rgba(0, 0, 0, 0.3)")}
                border="1px solid"
                borderColor={msg.role === 'user' ? "rgba(0, 212, 255, 0.5)" : useColorModeValue("gray.200", "rgba(0, 212, 255, 0.2)")}
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
                  {msg.content}
                </ReactMarkdown>
              </Box>
            </Flex>
          ))}
          
          {isLoading && (
            <Flex gap={3}>
              <Avatar size="sm" name="Xionimus" bg="linear-gradient(135deg, #00d4ff, #0094ff)" />
              <Box 
                bg={assistantBg} 
                px={4} 
                py={3} 
                borderRadius="lg" 
                minW="200px"
                boxShadow="0 4px 15px rgba(0, 212, 255, 0.2)"
                border="1px solid"
                borderColor="rgba(0, 212, 255, 0.2)"
              >
                <VStack align="start" spacing={2}>
                  <HStack spacing={2}>
                    <Spinner size="sm" color={useColorModeValue('#0094ff', '#00d4ff')} />
                    <Text fontWeight="600" color={useColorModeValue('#0094ff', '#00d4ff')}>Arbeite daran...</Text>
                  </HStack>
                  {messages.length > 0 && messages[messages.length - 1].content.match(/(klein|mittel|groß|small|medium|large)/i) && (
                    <Text fontSize="xs" color="gray.500">
                      🔍 Führe Recherche durch...
                    </Text>
                  )}
                </VStack>
              </Box>
            </Flex>
          )}
          
          <div ref={messagesEndRef} />
        </VStack>
      </Container>

      {/* Input Area (Fixed Bottom) */}
      <Box
        position="fixed"
        bottom={0}
        left={0}
        right={0}
        bg={bgColor}
        borderTop="1px solid"
        borderColor={borderColor}
        p={4}
      >
        <Container maxW="4xl">
          <VStack spacing={3} align="stretch">
            {/* Main Input with Ultra Thinking Toggle */}
            <HStack align="flex-end" spacing={3}>
              {/* Ultra Thinking Toggle */}
              <VStack spacing={1} align="center">
                <Tooltip 
                  label="Ultra Thinking: Aktiviert erweiterte Reasoning-Modi für komplexe Aufgaben (Claude)" 
                  placement="top"
                  bg="rgba(0, 212, 255, 0.9)"
                  color="white"
                >
                  <Box 
                    p={2} 
                    borderRadius="md" 
                    bg={ultraThinking ? "rgba(0, 212, 255, 0.1)" : "transparent"}
                    border="2px solid"
                    borderColor={ultraThinking ? "#00d4ff" : "transparent"}
                    transition="all 0.3s ease"
                    boxShadow={ultraThinking ? "0 0 20px rgba(0, 212, 255, 0.4)" : "none"}
                  >
                    <Switch
                      size="lg"
                      colorScheme="cyan"
                      isChecked={ultraThinking}
                      onChange={(e) => setUltraThinking(e.target.checked)}
                    />
                    <Text 
                      fontSize="xs" 
                      mt={1} 
                      color={ultraThinking ? (useColorModeValue('#0094ff', '#00d4ff')) : 'gray.500'}
                      textAlign="center"
                      fontWeight={ultraThinking ? "bold" : "normal"}
                    >
                      🧠
                    </Text>
                  </Box>
                </Tooltip>
              </VStack>

              {/* Textarea */}
              <Box flex={1} position="relative">
                <Textarea
                  ref={textareaRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Beschreiben Sie Ihr Programmier-Projekt..."
                  bg={inputBg}
                  border="2px solid"
                  borderColor={borderColor}
                  _focus={{
                    borderColor: 'blue.400',
                    boxShadow: '0 0 0 1px var(--chakra-colors-blue-400)'
                  }}
                  resize="none"
                  minH="56px"
                  maxH="200px"
                  pr="50px"
                  fontSize="md"
                />
                
                {/* Send Button (Inside Textarea) */}
                <IconButton
                  aria-label="Senden"
                  icon={<ArrowUpIcon />}
                  position="absolute"
                  right="8px"
                  bottom="8px"
                  size="sm"
                  colorScheme="blue"
                  borderRadius="md"
                  onClick={handleSend}
                  isLoading={isLoading}
                  isDisabled={!input.trim() || isLoading}
                />
              </Box>
            </HStack>

            {/* Toolbar Buttons */}
            <Flex
              wrap="wrap"
              gap={2}
              justify="space-between"
              align="center"
            >
              <HStack spacing={2}>
                <Button
                  size="sm"
                  variant="ghost"
                  leftIcon={<AttachmentIcon />}
                  onClick={() => toast({ title: 'Anhang-Feature kommt bald', status: 'info', duration: 2000 })}
                >
                  📎 Anhang
                </Button>
                
                <Button
                  size="sm"
                  variant="solid"
                  bg={isLoading ? "linear-gradient(135deg, #ff4444, #cc0000)" : "gray.600"}
                  color="white"
                  isDisabled={!isLoading}
                  onClick={handleStop}
                  _hover={{
                    bg: isLoading ? "linear-gradient(135deg, #cc0000, #ff4444)" : "gray.600",
                    boxShadow: isLoading ? "0 0 20px rgba(255, 68, 68, 0.6)" : "none"
                  }}
                  boxShadow={isLoading ? "0 2px 10px rgba(255, 68, 68, 0.4)" : "none"}
                >
                  ⏸️ Stopp
                </Button>
                
                <Menu>
                  <MenuButton as={Button} size="sm" variant="ghost" rightIcon={<ChevronDownIcon />}>
                    🌿 Branch: main
                  </MenuButton>
                  <MenuList>
                    <MenuItem>main</MenuItem>
                    <MenuItem>develop</MenuItem>
                    <MenuItem>+ Neuer Branch</MenuItem>
                  </MenuList>
                </Menu>
              </HStack>

              <HStack spacing={2}>
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => toast({ title: 'Fork-Feature kommt bald', status: 'info', duration: 2000 })}
                >
                  🔀 Verzweigen
                </Button>
                
                <Button
                  size="sm"
                  variant="solid"
                  bg="linear-gradient(135deg, #00d4ff, #0094ff)"
                  color="white"
                  onClick={handleGitHubPush}
                  _hover={{
                    bg: "linear-gradient(135deg, #0094ff, #00d4ff)",
                    boxShadow: "0 0 25px rgba(0, 212, 255, 0.6)"
                  }}
                  boxShadow="0 2px 15px rgba(0, 212, 255, 0.4)"
                >
                  📤 GitHub Push
                </Button>
              </HStack>
            </Flex>

            {/* Model Selector & Info */}
            <Flex justify="space-between" align="center" fontSize="xs" color="gray.500">
              <HStack spacing={2}>
                <Text>Modell:</Text>
                <Menu>
                  <MenuButton as={Button} size="xs" variant="link" rightIcon={<ChevronDownIcon />}>
                    {selectedProvider}/{selectedModel}
                  </MenuButton>
                  <MenuList>
                    {Object.entries(availableModels).map(([provider, models]) => (
                      <Box key={provider}>
                        <Text px={3} py={1} fontSize="xs" fontWeight="bold" color="gray.500">
                          {provider.toUpperCase()}
                        </Text>
                        {models.map((model: string) => (
                          <MenuItem
                            key={model}
                            onClick={() => {
                              setSelectedProvider(provider)
                              setSelectedModel(model)
                            }}
                            fontSize="sm"
                          >
                            {model}
                          </MenuItem>
                        ))}
                      </Box>
                    ))}
                  </MenuList>
                </Menu>
              </HStack>
              
              {ultraThinking && (
                <HStack spacing={1}>
                  <Text>🧠 Erweitertes Denken aktiv</Text>
                </HStack>
              )}
            </Flex>
          </VStack>
        </Container>
      </Box>
    </Box>
  )
}
