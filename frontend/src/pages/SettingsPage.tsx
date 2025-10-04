import React, { useState } from 'react'
import {
  Box,
  VStack,
  HStack,
  Text,
  Input,
  Button,
  Card,
  CardBody,
  CardHeader,
  Heading,
  FormControl,
  FormLabel,
  FormHelperText,
  InputGroup,
  InputRightElement,
  IconButton,
  Divider,
  Badge,
  useColorModeValue,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Code,
  Link,
  SimpleGrid,
  Switch,
  useBreakpointValue,
  useToast,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  useDisclosure
} from '@chakra-ui/react'
import { ViewIcon, ViewOffIcon, ExternalLinkIcon, ArrowBackIcon } from '@chakra-ui/icons'
import { useApp } from '../contexts/AppContext'
import { useNavigate } from 'react-router-dom'

const apiProviders = [
  {
    key: 'openai' as const,
    name: 'OpenAI',
    description: 'Advanced AI for general conversation and complex tasks',
    website: 'https://platform.openai.com/api-keys',
    placeholder: 'sk-proj-...',
    models: [],
    recommended: '',
    useCase: 'Complex conversations, coding, general intelligence'
  },
  {
    key: 'anthropic' as const,
    name: 'Anthropic',
    description: 'Advanced AI for reasoning and deep analysis',
    website: 'https://console.anthropic.com/keys',
    placeholder: 'sk-ant-...',
    models: [],
    recommended: '',
    useCase: 'Complex reasoning, analysis, research workflows'
  },
  {
    key: 'perplexity' as const,
    name: 'Perplexity',
    description: 'Real-time web search and research capabilities',
    website: 'https://www.perplexity.ai/settings/api',
    placeholder: 'pplx-...',
    models: [],
    recommended: '',
    useCase: 'Real-time research, web search, current information'
  }
]

export const SettingsPage: React.FC = () => {
  const { apiKeys, updateApiKeys, availableProviders, loadProviders, autoAgentSelection, setAutoAgentSelection } = useApp()
  const navigate = useNavigate()
  const toast = useToast()
  const { isOpen: isForkOpen, onOpen: onForkOpen, onClose: onForkClose } = useDisclosure()
  const [showKeys, setShowKeys] = useState({
    openai: false,
    anthropic: false,
    perplexity: false
  })
  const [tempKeys, setTempKeys] = useState(apiKeys)
  const [saving, setSaving] = useState(false)
  const [githubConnected, setGithubConnected] = useState(false)
  const [githubUsername, setGithubUsername] = useState<string | null>(null)
  const [githubToken, setGithubToken] = useState('')
  const [showGithubToken, setShowGithubToken] = useState(false)
  const [savingGithubToken, setSavingGithubToken] = useState(false)
  const [testingConnection, setTestingConnection] = useState(false)
  const [forkSummary, setForkSummary] = useState<any>(null)
  const [loadingSummary, setLoadingSummary] = useState(false)
  const [pushing, setPushing] = useState(false)
  
  const cardBg = useColorModeValue('#111111', '#111111')
  const isMobile = useBreakpointValue({ base: true, md: false })
  
  React.useEffect(() => {
    setTempKeys(apiKeys)
  }, [apiKeys])
  
  // Check GitHub PAT connection status on mount
  React.useEffect(() => {
    checkGithubConnection()
  }, [])
  
  const checkGithubConnection = async () => {
    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      const token = localStorage.getItem('xionimus_token')
      
      if (!token) return
      
      const response = await fetch(`${backendUrl}/api/github-pat/verify-token`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      const data = await response.json();
      
      if (data.connected) {
        setGithubConnected(true)
        setGithubUsername(data.github_username)
      } else {
        setGithubConnected(false)
        setGithubUsername(null)
      }
    } catch (error) {
      console.error('Failed to check GitHub connection:', error);
    }
  }
  
  const handleSaveGithubToken = async () => {
    if (!githubToken.trim()) {
      toast({
        title: 'Token Required',
        description: 'Please enter your GitHub Personal Access Token',
        status: 'warning',
        duration: 3000,
      });
      return;
    }
    
    setSavingGithubToken(true);
    
    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      const authToken = localStorage.getItem('xionimus_token')
      
      const response = await fetch(`${backendUrl}/api/github-pat/save-token`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authToken}`
        },
        body: JSON.stringify({
          token: githubToken
        })
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setGithubConnected(true)
        setGithubUsername(data.github_username)
        setGithubToken('')
        toast({
          title: 'GitHub Connected! ✅',
          description: `Successfully connected as ${data.github_username}`,
          status: 'success',
          duration: 5000,
        });
      } else {
        toast({
          title: 'Connection Failed',
          description: data.detail || 'Failed to connect GitHub',
          status: 'error',
          duration: 5000,
        });
      }
    } catch (error: any) {
      console.error('Save GitHub token error:', error);
      toast({
        title: 'Connection Error',
        description: error.message || 'Could not connect to backend',
        status: 'error',
        duration: 5000,
      });
    } finally {
      setSavingGithubToken(false);
    }
  }
  
  const handleRemoveGithubToken = async () => {
    setTestingConnection(true);
    
    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      const authToken = localStorage.getItem('xionimus_token')
      
      const response = await fetch(`${backendUrl}/api/github-pat/remove-token`, {
        method: 'DELETE',
        headers: { 
          'Authorization': `Bearer ${authToken}`
        }
      });
      
      const data = await response.json();
      
      if (response.ok) {
        setGithubConnected(false)
        setGithubUsername(null)
        setGithubToken('')
        toast({
          title: 'Disconnected',
          description: 'GitHub connection removed',
          status: 'info',
          duration: 3000,
        });
      }
    } catch (error: any) {
      console.error('Remove GitHub token error:', error);
      toast({
        title: 'Error',
        description: 'Failed to disconnect GitHub',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setTestingConnection(false);
    }
  }
  
  const handleSave = async () => {
    setSaving(true)
    updateApiKeys(tempKeys)
    
    // Reload providers to check status
    setTimeout(() => {
      loadProviders()
      setSaving(false)
    }, 1000)
  }
  
  const handleForkSummary = async () => {
    setLoadingSummary(true)
    onForkOpen()
    
    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      
      const response = await fetch(`${backendUrl}/api/github/fork-summary`);
      const data = await response.json();
      
      if (response.ok) {
        setForkSummary(data)
      } else {
        toast({
          title: 'Failed to Load Summary',
          description: data.detail || 'Could not generate fork summary',
          status: 'error',
          duration: 5000,
        });
      }
    } catch (error) {
      console.error('Fork summary error:', error);
      toast({
        title: 'Connection Error',
        description: 'Could not connect to backend',
        status: 'error',
        duration: 5000,
      });
    } finally {
      setLoadingSummary(false)
    }
  }
  
  const toggleShowKey = (provider: keyof typeof showKeys) => {
    setShowKeys(prev => ({
      ...prev,
      [provider]: !prev[provider]
    }))
  }
  
  const handlePushToGithub = async () => {
    const username = githubUsername;
    
    if (!token || !username) {
      toast({
        title: 'Not Connected',
        description: 'Please connect to GitHub first.',
        status: 'warning',
        duration: 3000,
      });
      return;
    }
    
    // Prompt for repository name
    const repoName = prompt('Enter repository name:', 'xionimus-ai-project');
    
    if (!repoName) {
      return; // User cancelled
    }
    
    // Prompt for branch name
    const branchName = prompt('Enter branch name:', 'main');
    
    if (!branchName) {
      return; // User cancelled
    }
    
    setPushing(true);
    
    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
      
      // First, try to create the repository
      try {
        await fetch(`${backendUrl}/api/github/repositories?access_token=${token}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: repoName,
            description: 'Xionimus AI - Advanced local-first AI assistant',
            private: false
          })
        });
        
        toast({
          title: 'Repository Created',
          description: `Repository ${repoName} created successfully`,
          status: 'success',
          duration: 3000,
        });
      } catch (repoError) {
        // Repository might already exist, continue with push
        console.log('Repository might already exist, continuing with push');
      }
      
      // Push entire project to specified branch
      const response = await fetch(
        `${backendUrl}/api/github/push-project?owner=${username}&repo=${repoName}&access_token=${token}&commit_message=Update from Xionimus AI&branch=${encodeURIComponent(branchName)}`,
        {
          method: 'POST'
        }
      );
      
      const result = await response.json();
      
      if (response.ok) {
        toast({
          title: 'Push Successful! 🎉',
          description: `Pushed ${result.files_pushed} files to ${result.repository} on branch ${branchName}`,
          status: 'success',
          duration: 5000,
        });
        
        // Show repository URL
        setTimeout(() => {
          toast({
            title: 'View on GitHub',
            description: result.repository_url,
            status: 'info',
            duration: 8000,
            isClosable: true,
          });
        }, 1000);
      } else {
        toast({
          title: 'Push Failed',
          description: result.detail || 'Failed to push to GitHub',
          status: 'error',
          duration: 5000,
        });
      }
    } catch (error: any) {
      console.error('Push error:', error);
      toast({
        title: 'Push Failed',
        description: error.message || 'An error occurred while pushing to GitHub',
        status: 'error',
        duration: 5000,
      });
    } finally {
      setPushing(false);
    }
  };
  
  const configuredCount = Object.values(availableProviders).filter(Boolean).length
  
  return (
    <Box p={{ base: 4, md: 6 }} maxW="4xl" mx="auto" data-testid="settings-page">
      <VStack spacing={{ base: 6, md: 8 }} align="stretch">
        {/* Header with Back Button */}
        <HStack justify="space-between" align="start">
          <VStack align="start" spacing={2} flex={1}>
            <HStack>
              <IconButton
                aria-label="Zurück"
                icon={<ArrowBackIcon />}
                onClick={() => navigate(-1)}
                variant="ghost"
                size="sm"
              />
              <Heading size={{ base: 'md', md: 'lg' }}>Settings</Heading>
            </HStack>
            <Text color="gray.400" fontSize={{ base: 'xs', md: 'sm' }}>
              Configure your AI providers and platform preferences
            </Text>
          </VStack>
          
          {/* Quick Action Buttons */}
          <HStack spacing={2}>
            <Button
              leftIcon={<ExternalLinkIcon />}
              size="sm"
              colorScheme="purple"
              variant="outline"
              onClick={handleForkSummary}
              isLoading={loadingSummary}
              data-testid="fork-summary-button"
            >
              Fork Summary
            </Button>
          </HStack>
        </HStack>
        
        {/* Status Overview */}
        <Card bg={cardBg}>
          <CardHeader pb={3}>
            <Heading size={{ base: 'sm', md: 'md' }}>System Status</Heading>
          </CardHeader>
          <CardBody>
            <SimpleGrid columns={{ base: 1, sm: 3 }} spacing={4}>
              <VStack>
                <Text fontSize={{ base: 'xl', md: '2xl' }} fontWeight="bold" color="primary.500">
                  {configuredCount}/3
                </Text>
                <Text fontSize={{ base: 'xs', md: 'sm' }} color="gray.500" textAlign="center">
                  AI Providers Configured
                </Text>
              </VStack>
              <VStack>
                <Text fontSize={{ base: 'xl', md: '2xl' }} fontWeight="bold" color="green.500">
                  v1.0.0
                </Text>
                <Text fontSize={{ base: 'xs', md: 'sm' }} color="gray.500" textAlign="center">
                  Platform Version
                </Text>
              </VStack>
              <VStack>
                <Text fontSize={{ base: 'xl', md: '2xl' }} fontWeight="bold" color="blue.500">
                  MVP
                </Text>
                <Text fontSize={{ base: 'xs', md: 'sm' }} color="gray.500" textAlign="center">
                  Current Phase
                </Text>
              </VStack>
            </SimpleGrid>
          </CardBody>
        </Card>
        
        {/* API Keys Configuration */}
        <Card bg={cardBg} data-testid="api-keys-card">
          <CardHeader pb={3}>
            <Heading size={{ base: 'sm', md: 'md' }}>AI Provider API Keys</Heading>
            <Text color="gray.500" fontSize={{ base: 'xs', md: 'sm' }} mt={2}>
              Add your API keys to enable AI chat functionality
            </Text>
          </CardHeader>
          <CardBody>
            <VStack spacing={6}>
              {/* Intelligent Agent Selection Toggle */}
              <Box w="full" p={{ base: 3, md: 4 }} border="1px solid" borderColor="primary.500" borderRadius="md">
                <VStack align="start" spacing={3}>
                  <HStack justify="space-between" w="full" flexWrap={{ base: 'wrap', md: 'nowrap' }}>
                    <VStack align="start" spacing={1} flex={1} minW={{ base: 'full', md: 'auto' }}>
                      <Text fontWeight="semibold" color="primary.500" fontSize={{ base: 'sm', md: 'md' }}>
                        🤖 Intelligent Agent Selection
                      </Text>
                      <Text fontSize={{ base: 'xs', md: 'sm' }} color="gray.500">
                        Automatically select the best AI model based on your message content
                      </Text>
                    </VStack>
                    <FormControl display="flex" alignItems="center" w="auto">
                      <Switch
                        colorScheme="cyan"
                        isChecked={autoAgentSelection}
                        onChange={(e) => setAutoAgentSelection(e.target.checked)}
                      />
                    </FormControl>
                  </HStack>
                  
                  {autoAgentSelection && (
                    <Box mt={2} p={3} bg="rgba(0, 212, 255, 0.1)" borderRadius="md" w="full">
                      <Text fontSize={{ base: '2xs', md: 'xs' }} color="gray.400">
                        ✨ Enabled: GPT-5 for conversations • Claude Opus 4.1 for analysis • Perplexity for research
                      </Text>
                    </Box>
                  )}
                </VStack>
              </Box>
              
              {apiProviders.map((provider) => (
                <Box key={provider.key} w="full">
                  <HStack justify="space-between" mb={2} flexWrap={{ base: 'wrap', md: 'nowrap' }}>
                    <VStack align="start" spacing={1} flex={1}>
                      <HStack>
                        <Text fontWeight="semibold" fontSize={{ base: 'sm', md: 'md' }}>{provider.name}</Text>
                        <Badge
                          colorScheme={availableProviders[provider.key] ? 'green' : 'gray'}
                          size="sm"
                          fontSize={{ base: '2xs', md: 'xs' }}
                        >
                          {availableProviders[provider.key] ? 'Configured' : 'Not Set'}
                        </Badge>
                      </HStack>
                      <Text fontSize={{ base: 'xs', md: 'sm' }} color="gray.500">
                        {provider.description}
                      </Text>
                    </VStack>
                    
                    <Link href={provider.website} isExternal>
                      <Button 
                        size="sm" 
                        variant="outline" 
                        rightIcon={!isMobile ? <ExternalLinkIcon /> : undefined}
                        fontSize={{ base: 'xs', md: 'sm' }}
                      >
                        {isMobile ? 'Get Key' : 'Get API Key'}
                      </Button>
                    </Link>
                  </HStack>
                  
                  <FormControl>
                    <InputGroup size={{ base: 'sm', md: 'md' }}>
                      <Input
                        type={showKeys[provider.key] ? 'text' : 'password'}
                        value={tempKeys[provider.key]}
                        onChange={(e) => setTempKeys(prev => ({
                          ...prev,
                          [provider.key]: e.target.value
                        }))}
                        placeholder={provider.placeholder}
                        variant="filled"
                        fontSize={{ base: 'xs', md: 'sm' }}
                        data-testid={`api-key-input-${provider.key}`}
                      />
                      <InputRightElement>
                        <IconButton
                          aria-label={showKeys[provider.key] ? 'Hide key' : 'Show key'}
                          icon={showKeys[provider.key] ? <ViewOffIcon /> : <ViewIcon />}
                          size="sm"
                          variant="ghost"
                          onClick={() => toggleShowKey(provider.key)}
                        />
                      </InputRightElement>
                    </InputGroup>
                    <FormHelperText>
                      <VStack align="start" spacing={1}>
                        <Text fontSize={{ base: '2xs', md: 'xs' }}>
                          Recommended: <Code fontSize={{ base: '2xs', md: 'xs' }}>{provider.recommended}</Code>
                        </Text>
                        <Text fontSize={{ base: '2xs', md: 'xs' }}>Use case: {provider.useCase}</Text>
                        <Text fontSize={{ base: '2xs', md: 'xs' }} display={{ base: 'none', md: 'block' }}>
                          Models: {provider.models.join(', ')}
                        </Text>
                      </VStack>
                    </FormHelperText>
                  </FormControl>
                  
                  {provider.key !== 'perplexity' && <Divider mt={4} />}
                </Box>
              ))}
              
              <Button
                colorScheme="primary"
                onClick={handleSave}
                isLoading={saving}
                loadingText="Saving..."
                w={{ base: 'full', md: 'fit-content' }}
                alignSelf={{ base: 'stretch', md: 'flex-start' }}
                size={{ base: 'sm', md: 'md' }}
                data-testid="save-api-keys-button"
              >
                Save API Keys
              </Button>
            </VStack>
          </CardBody>
        </Card>
        
        {/* GitHub Integration - Personal Access Token */}
        <Card bg={cardBg} data-testid="github-integration-card">
          <CardHeader pb={3}>
            <Heading size={{ base: 'sm', md: 'md' }}>GitHub Integration</Heading>
            <Text color="gray.500" fontSize={{ base: 'xs', md: 'sm' }} mt={2}>
              Connect using Personal Access Token for repository access
            </Text>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              {/* Connection Status */}
              <HStack justify="space-between" p={4} border="1px solid" borderColor="gray.700" borderRadius="md">
                <VStack align="start" spacing={1}>
                  <HStack>
                    <Text fontWeight="semibold">GitHub Status</Text>
                    <Badge colorScheme={githubConnected ? 'green' : 'gray'}>
                      {githubConnected ? 'Connected' : 'Not Connected'}
                    </Badge>
                  </HStack>
                  <Text fontSize="xs" color="gray.500">
                    {githubConnected && githubUsername 
                      ? `Connected as ${githubUsername}` 
                      : 'Add your Personal Access Token to connect'}
                  </Text>
                </VStack>
                {githubConnected && (
                  <Button
                    colorScheme="red"
                    size="sm"
                    onClick={handleRemoveGithubToken}
                    isLoading={testingConnection}
                    data-testid="github-disconnect-button"
                  >
                    Disconnect
                  </Button>
                )}
              </HStack>
              
              {/* Token Input (only show if not connected) */}
              {!githubConnected && (
                <Box p={4} bg="rgba(66, 153, 225, 0.1)" borderRadius="md" border="1px solid" borderColor="blue.500">
                  <VStack align="stretch" spacing={3}>
                    <Text fontWeight="semibold" color="blue.400">🔑 Add GitHub Personal Access Token</Text>
                    <Text fontSize="xs" color="gray.400">
                      How to get your token:
                    </Text>
                    <VStack align="start" spacing={1} fontSize="xs" color="gray.500" pl={2}>
                      <Text>1. Go to: <Link href="https://github.com/settings/tokens" isExternal color="blue.400">github.com/settings/tokens</Link></Text>
                      <Text>2. Click "Generate new token" → "Generate new token (classic)"</Text>
                      <Text>3. Select scopes: <Code fontSize="xs">repo</Code> (Full repository access)</Text>
                      <Text>4. Generate and copy the token</Text>
                      <Text>5. Paste it below</Text>
                    </VStack>
                    
                    <FormControl>
                      <FormLabel fontSize="sm">Personal Access Token</FormLabel>
                      <InputGroup size="sm">
                        <Input
                          value={githubToken}
                          onChange={(e) => setGithubToken(e.target.value)}
                          placeholder="ghp_..."
                          type={showGithubToken ? 'text' : 'password'}
                          variant="filled"
                        />
                        <InputRightElement>
                          <IconButton
                            aria-label={showGithubToken ? 'Hide token' : 'Show token'}
                            icon={showGithubToken ? <ViewOffIcon /> : <ViewIcon />}
                            size="xs"
                            variant="ghost"
                            onClick={() => setShowGithubToken(!showGithubToken)}
                          />
                        </InputRightElement>
                      </InputGroup>
                      <FormHelperText fontSize="xs">
                        Token is securely stored and never shared
                      </FormHelperText>
                    </FormControl>
                    
                    <Button
                      colorScheme="blue"
                      size="sm"
                      onClick={handleSaveGithubToken}
                      isLoading={savingGithubToken}
                      loadingText="Connecting..."
                      isDisabled={!githubToken.trim()}
                    >
                      Connect GitHub
                    </Button>
                  </VStack>
                </Box>
              )}
              
              {/* Connected Features */}
              {githubConnected && (
                <Alert status="success" borderRadius="md">
                  <AlertIcon />
                  <Box flex="1">
                    <AlertTitle fontSize="sm">Connected!</AlertTitle>
                    <AlertDescription fontSize="xs">
                      You can now import repositories and push code to GitHub
                    </AlertDescription>
                  </Box>
                </Alert>
              )}
            </VStack>
          </CardBody>
        </Card>
        
        {/* Usage Guidelines */}
        <Alert status="info" borderRadius="md">
          <AlertIcon />
          <Box>
            <AlertTitle fontSize={{ base: 'sm', md: 'md' }}>Intelligente Modellauswahl</AlertTitle>
            <AlertDescription fontSize={{ base: 'xs', md: 'sm' }}>
              Xionimus AI wählt automatisch das beste Modell für Ihre Anfrage aus.
              GPT-5 für Konversationen • Claude Opus 4.1 für Analysen • Perplexity für Recherche.
              Sie müssen kein Modell manuell auswählen!
            </AlertDescription>
          </Box>
        </Alert>
        
        {/* Developer Info */}
        <Card bg={cardBg} display={{ base: 'none', md: 'block' }}>
          <CardHeader pb={3}>
            <Heading size="md">Developer Information</Heading>
          </CardHeader>
          <CardBody>
            <SimpleGrid columns={{ base: 1, md: 2 }} spacing={4}>
              <VStack align="start" spacing={2}>
                <Text fontWeight="semibold">Frontend</Text>
                <Code>React 18 + Chakra UI + Vite</Code>
                <Code>TypeScript + Framer Motion</Code>
              </VStack>
              <VStack align="start" spacing={2}>
                <Text fontWeight="semibold">Backend</Text>
                <Code>FastAPI + Python 3.10+</Code>
                <Code>SQLite + WebSockets</Code>
              </VStack>
            </SimpleGrid>
          </CardBody>
        </Card>
      </VStack>
      
      {/* Fork Summary Modal */}
      <Modal isOpen={isForkOpen} onClose={onForkClose} size="xl">
        <ModalOverlay />
        <ModalContent bg={cardBg}>
          <ModalHeader>Fork Summary - {forkSummary?.project_name || 'Loading...'}</ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            {loadingSummary ? (
              <VStack spacing={4} py={8}>
                <Text>Loading project summary...</Text>
              </VStack>
            ) : forkSummary ? (
              <VStack align="stretch" spacing={4}>
                <Box p={4} bg="rgba(0, 212, 255, 0.1)" borderRadius="md">
                  <Text fontWeight="semibold" mb={2}>{forkSummary.description}</Text>
                  <VStack align="start" spacing={2} fontSize="sm">
                    <HStack>
                      <Badge colorScheme="blue">v1.0.0</Badge>
                      <Text color="gray.400">
                        Generated: {new Date(forkSummary.timestamp).toLocaleString()}
                      </Text>
                    </HStack>
                  </VStack>
                </Box>
                
                <Box p={4} border="1px solid" borderColor="gray.700" borderRadius="md">
                  <Text fontWeight="semibold" mb={3}>📊 Project Statistics</Text>
                  <SimpleGrid columns={2} spacing={3} fontSize="sm">
                    <VStack align="start">
                      <Text color="gray.400">Total Files</Text>
                      <Text fontWeight="bold" fontSize="lg">{forkSummary.statistics.total_files}</Text>
                    </VStack>
                    <VStack align="start">
                      <Text color="gray.400">Lines of Code</Text>
                      <Text fontWeight="bold" fontSize="lg">{forkSummary.statistics.total_lines_of_code.toLocaleString()}</Text>
                    </VStack>
                    <VStack align="start">
                      <Text color="gray.400">Total Size</Text>
                      <Text fontWeight="bold" fontSize="lg">{forkSummary.statistics.total_size_mb} MB</Text>
                    </VStack>
                    <VStack align="start">
                      <Text color="gray.400">Key Files</Text>
                      <Text fontWeight="bold" fontSize="lg">{forkSummary.statistics.key_files_count}</Text>
                    </VStack>
                  </SimpleGrid>
                </Box>
                
                <Box p={4} border="1px solid" borderColor="gray.700" borderRadius="md">
                  <Text fontWeight="semibold" mb={2}>💻 Languages</Text>
                  <VStack align="start" spacing={1} fontSize="sm">
                    {Object.entries(forkSummary.statistics.languages).map(([lang, stats]: [string, any]) => (
                      <HStack key={lang} justify="space-between" w="full">
                        <Text>{lang}</Text>
                        <HStack>
                          <Badge>{stats.files} files</Badge>
                          <Badge colorScheme="green">{stats.lines.toLocaleString()} lines</Badge>
                        </HStack>
                      </HStack>
                    ))}
                  </VStack>
                </Box>
                
                <Box p={4} border="1px solid" borderColor="gray.700" borderRadius="md">
                  <Text fontWeight="semibold" mb={2}>🏗️ Project Structure</Text>
                  <VStack align="start" spacing={2} fontSize="sm">
                    <Box>
                      <Text fontWeight="semibold" color="primary.400">Backend</Text>
                      <Text color="gray.400">{forkSummary.structure.backend.description}</Text>
                      <VStack align="start" mt={1} pl={4}>
                        {forkSummary.structure.backend.key_features.map((feature: string, i: number) => (
                          <Text key={i} fontSize="xs">• {feature}</Text>
                        ))}
                      </VStack>
                    </Box>
                    <Box>
                      <Text fontWeight="semibold" color="primary.400">Frontend</Text>
                      <Text color="gray.400">{forkSummary.structure.frontend.description}</Text>
                      <VStack align="start" mt={1} pl={4}>
                        {forkSummary.structure.frontend.key_features.map((feature: string, i: number) => (
                          <Text key={i} fontSize="xs">• {feature}</Text>
                        ))}
                      </VStack>
                    </Box>
                  </VStack>
                </Box>
                
                <Box p={4} border="1px solid" borderColor="gray.700" borderRadius="md">
                  <Text fontWeight="semibold" mb={2}>🔧 Technology Stack</Text>
                  <VStack align="start" spacing={2} fontSize="xs">
                    <Box>
                      <Text fontWeight="semibold">Backend:</Text>
                      <Text color="gray.400">{forkSummary.technology_stack.backend.join(', ')}</Text>
                    </Box>
                    <Box>
                      <Text fontWeight="semibold">Frontend:</Text>
                      <Text color="gray.400">{forkSummary.technology_stack.frontend.join(', ')}</Text>
                    </Box>
                    <Box>
                      <Text fontWeight="semibold">AI/ML:</Text>
                      <Text color="gray.400">{forkSummary.technology_stack.ai_ml.join(', ')}</Text>
                    </Box>
                  </VStack>
                </Box>
                
                {githubConnected && (
                  <Alert status="success" fontSize="sm">
                    <AlertIcon />
                    <Text>
                      Ready to push! Click "Push to GitHub" to deploy this project.
                    </Text>
                  </Alert>
                )}
              </VStack>
            ) : (
              <Alert status="info" fontSize="sm">
                <AlertIcon />
                <Text>
                  Failed to load summary. Please try again.
                </Text>
              </Alert>
            )}
          </ModalBody>
        </ModalContent>
      </Modal>
    </Box>
  )
}