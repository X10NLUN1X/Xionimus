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
  SimpleGrid
} from '@chakra-ui/react'
import { ViewIcon, ViewOffIcon, ExternalLinkIcon } from '@chakra-ui/icons'
import { useApp } from '../contexts/AppContext'

const apiProviders = [
  {
    key: 'openai' as const,
    name: 'OpenAI',
    description: 'Access to GPT-4o, GPT-4o-mini, and o1 models',
    website: 'https://platform.openai.com/api-keys',
    placeholder: 'sk-proj-...',
    models: ['gpt-4o', 'gpt-4o-mini', 'o1-preview', 'o1-mini']
  },
  {
    key: 'anthropic' as const,
    name: 'Anthropic',
    description: 'Access to Claude 3.5 Sonnet and Haiku models',
    website: 'https://console.anthropic.com/keys',
    placeholder: 'sk-ant-...',
    models: ['claude-3-5-sonnet-20241022', 'claude-3-5-haiku-20241022']
  },
  {
    key: 'perplexity' as const,
    name: 'Perplexity',
    description: 'Real-time web search and research capabilities',
    website: 'https://www.perplexity.ai/settings/api',
    placeholder: 'pplx-...',
    models: ['llama-3.1-sonar-large-128k-online', 'llama-3.1-sonar-small-128k-online']
  }
]

export const SettingsPage: React.FC = () => {
  const { apiKeys, updateApiKeys, availableProviders, loadProviders } = useApp()
  const [showKeys, setShowKeys] = useState({
    openai: false,
    anthropic: false,
    perplexity: false
  })
  const [tempKeys, setTempKeys] = useState(apiKeys)
  const [saving, setSaving] = useState(false)
  
  const cardBg = useColorModeValue('#111111', '#111111')
  
  React.useEffect(() => {
    setTempKeys(apiKeys)
  }, [apiKeys])
  
  const handleSave = async () => {
    setSaving(true)
    updateApiKeys(tempKeys)
    
    // Reload providers to check status
    setTimeout(() => {
      loadProviders()
      setSaving(false)
    }, 1000)
  }
  
  const toggleShowKey = (provider: keyof typeof showKeys) => {
    setShowKeys(prev => ({
      ...prev,
      [provider]: !prev[provider]
    }))
  }
  
  const configuredCount = Object.values(availableProviders).filter(Boolean).length
  
  return (
    <Box p={6} maxW="4xl" mx="auto">
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <VStack align="start" spacing={2}>
          <Heading size="lg">Settings</Heading>
          <Text color="gray.500">
            Configure your AI providers and platform preferences
          </Text>
        </VStack>
        
        {/* Status Overview */}
        <Card bg={cardBg}>
          <CardHeader>
            <Heading size="md">System Status</Heading>
          </CardHeader>
          <CardBody>
            <SimpleGrid columns={{ base: 1, md: 3 }} spacing={4}>
              <VStack>
                <Text fontSize="2xl" fontWeight="bold" color="primary.500">
                  {configuredCount}/3
                </Text>
                <Text fontSize="sm" color="gray.500" textAlign="center">
                  AI Providers Configured
                </Text>
              </VStack>
              <VStack>
                <Text fontSize="2xl" fontWeight="bold" color="green.500">
                  v1.0.0
                </Text>
                <Text fontSize="sm" color="gray.500" textAlign="center">
                  Platform Version
                </Text>
              </VStack>
              <VStack>
                <Text fontSize="2xl" fontWeight="bold" color="blue.500">
                  MVP
                </Text>
                <Text fontSize="sm" color="gray.500" textAlign="center">
                  Current Phase
                </Text>
              </VStack>
            </SimpleGrid>
          </CardBody>
        </Card>
        
        {/* API Keys Configuration */}
        <Card bg={cardBg}>
          <CardHeader>
            <Heading size="md">AI Provider API Keys</Heading>
            <Text color="gray.500" fontSize="sm" mt={2}>
              Add your API keys to enable AI chat functionality
            </Text>
          </CardHeader>
          <CardBody>
            <VStack spacing={6}>
              {apiProviders.map((provider) => (
                <Box key={provider.key} w="full">
                  <HStack justify="space-between" mb={2}>
                    <VStack align="start" spacing={1}>
                      <HStack>
                        <Text fontWeight="semibold">{provider.name}</Text>
                        <Badge
                          colorScheme={availableProviders[provider.key] ? 'green' : 'gray'}
                          size="sm"
                        >
                          {availableProviders[provider.key] ? 'Configured' : 'Not Set'}
                        </Badge>
                      </HStack>
                      <Text fontSize="sm" color="gray.500">
                        {provider.description}
                      </Text>
                    </VStack>
                    
                    <Link href={provider.website} isExternal>
                      <Button size="sm" variant="outline" rightIcon={<ExternalLinkIcon />}>
                        Get API Key
                      </Button>
                    </Link>
                  </HStack>
                  
                  <FormControl>
                    <InputGroup>
                      <Input
                        type={showKeys[provider.key] ? 'text' : 'password'}
                        value={tempKeys[provider.key]}
                        onChange={(e) => setTempKeys(prev => ({
                          ...prev,
                          [provider.key]: e.target.value
                        }))}
                        placeholder={provider.placeholder}
                        variant="filled"
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
                      Supported models: {provider.models.join(', ')}
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
                w="fit-content"
                alignSelf="flex-start"
              >
                Save API Keys
              </Button>
            </VStack>
          </CardBody>
        </Card>
        
        {/* Usage Guidelines */}
        <Alert status="info">
          <AlertIcon />
          <Box>
            <AlertTitle>Getting Started!</AlertTitle>
            <AlertDescription>
              Add your AI API keys above, then go to the Chat page to start conversations.
              Each provider offers different capabilities - OpenAI for general tasks,
              Anthropic for reasoning, and Perplexity for real-time research.
            </AlertDescription>
          </Box>
        </Alert>
        
        {/* Developer Info */}
        <Card bg={cardBg}>
          <CardHeader>
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
                <Code>MongoDB + WebSockets</Code>
              </VStack>
            </SimpleGrid>
          </CardBody>
        </Card>
      </VStack>
    </Box>
  )
}