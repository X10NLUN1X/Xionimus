import React, { useState, useEffect } from 'react'
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Card,
  CardBody,
  CardHeader,
  Heading,
  Badge,
  useColorModeValue,
  useToast,
  IconButton,
  Divider,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  SimpleGrid,
  Stat,
  StatLabel,
  StatNumber,
  StatHelpText,
  Spinner,
  Center,
  Alert,
  AlertIcon,
  AlertDescription,
  Code,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Tag,
} from '@chakra-ui/react'
import { ArrowBackIcon, DownloadIcon, CopyIcon, CheckIcon } from '@chakra-ui/icons'
import { useNavigate, useParams } from 'react-router-dom'

interface Message {
  role: string
  content: string
  timestamp: string
}

interface Finding {
  type: string
  severity: string
  message: string
  line_number?: number
}

interface Review {
  id: string
  title: string
  language: string
  status: string
  total_issues: number
  critical_issues: number
  findings: Finding[]
  created_at: string
}

interface SessionSummary {
  session_id: string
  title: string
  created_at: string
  updated_at: string
  conversation: {
    total_messages: number
    messages: Message[]
  }
  code_reviews: {
    total_reviews: number
    reviews: Review[]
  }
  statistics: {
    total_user_messages: number
    total_assistant_messages: number
    total_code_issues_found: number
    total_critical_issues: number
  }
}

export const SessionSummaryPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>()
  const navigate = useNavigate()
  const toast = useToast()
  const cardBg = useColorModeValue('#111111', '#111111')
  
  const [loading, setLoading] = useState(true)
  const [summary, setSummary] = useState<SessionSummary | null>(null)
  const [copied, setCopied] = useState(false)
  
  useEffect(() => {
    if (sessionId) {
      fetchSessionSummary()
    }
  }, [sessionId])
  
  const fetchSessionSummary = async () => {
    try {
      setLoading(true)
      const backendUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'
      
      const response = await fetch(`${backendUrl}/api/settings/session-summary`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ session_id: sessionId })
      })
      
      if (!response.ok) {
        throw new Error('Failed to fetch session summary')
      }
      
      const data = await response.json()
      setSummary(data)
    } catch (error: any) {
      console.error('Failed to fetch summary:', error)
      toast({
        title: 'Failed to Load Summary',
        description: error.message || 'Could not load session summary',
        status: 'error',
        duration: 5000,
      })
    } finally {
      setLoading(false)
    }
  }
  
  const handleCopy = () => {
    if (!summary) return
    
    const summaryText = generateMarkdownSummary(summary)
    navigator.clipboard.writeText(summaryText)
    
    setCopied(true)
    toast({
      title: 'Copied to Clipboard!',
      status: 'success',
      duration: 2000,
    })
    
    setTimeout(() => setCopied(false), 2000)
  }
  
  const handleDownload = () => {
    if (!summary) return
    
    const summaryText = generateMarkdownSummary(summary)
    const blob = new Blob([summaryText], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `session-summary-${sessionId}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    toast({
      title: 'Download Started',
      description: 'Session summary downloaded as Markdown file',
      status: 'success',
      duration: 3000,
    })
  }
  
  const generateMarkdownSummary = (data: SessionSummary): string => {
    let markdown = `# Session Summary: ${data.title}\n\n`
    markdown += `**Session ID:** ${data.session_id}\n`
    markdown += `**Created:** ${new Date(data.created_at).toLocaleString()}\n`
    markdown += `**Last Updated:** ${new Date(data.updated_at).toLocaleString()}\n\n`
    
    markdown += `## Statistics\n\n`
    markdown += `- **Total Messages:** ${data.conversation.total_messages}\n`
    markdown += `- **User Messages:** ${data.statistics.total_user_messages}\n`
    markdown += `- **Assistant Messages:** ${data.statistics.total_assistant_messages}\n`
    markdown += `- **Code Reviews:** ${data.code_reviews.total_reviews}\n`
    markdown += `- **Total Issues Found:** ${data.statistics.total_code_issues_found}\n`
    markdown += `- **Critical Issues:** ${data.statistics.total_critical_issues}\n\n`
    
    markdown += `## Conversation History\n\n`
    data.conversation.messages.forEach((msg, idx) => {
      markdown += `### Message ${idx + 1} (${msg.role})\n`
      markdown += `*${new Date(msg.timestamp).toLocaleString()}*\n\n`
      markdown += `${msg.content}\n\n`
      markdown += `---\n\n`
    })
    
    if (data.code_reviews.total_reviews > 0) {
      markdown += `## Code Reviews\n\n`
      data.code_reviews.reviews.forEach((review, idx) => {
        markdown += `### Review ${idx + 1}: ${review.title}\n\n`
        markdown += `- **Language:** ${review.language}\n`
        markdown += `- **Status:** ${review.status}\n`
        markdown += `- **Total Issues:** ${review.total_issues}\n`
        markdown += `- **Critical Issues:** ${review.critical_issues}\n\n`
        
        if (review.findings.length > 0) {
          markdown += `#### Findings\n\n`
          review.findings.forEach((finding, fIdx) => {
            markdown += `${fIdx + 1}. **[${finding.severity}]** ${finding.type}\n`
            markdown += `   ${finding.message}\n`
            if (finding.line_number) {
              markdown += `   *Line ${finding.line_number}*\n`
            }
            markdown += `\n`
          })
        }
        
        markdown += `\n---\n\n`
      })
    }
    
    return markdown
  }
  
  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'red'
      case 'high':
        return 'orange'
      case 'medium':
        return 'yellow'
      case 'low':
        return 'blue'
      default:
        return 'gray'
    }
  }
  
  if (loading) {
    return (
      <Center h="100vh">
        <VStack spacing={4}>
          <Spinner size="xl" color="blue.500" />
          <Text>Loading session summary...</Text>
        </VStack>
      </Center>
    )
  }
  
  if (!summary) {
    return (
      <Box p={6} maxW="4xl" mx="auto">
        <Alert status="error">
          <AlertIcon />
          <AlertDescription>Session summary not found</AlertDescription>
        </Alert>
        <Button mt={4} leftIcon={<ArrowBackIcon />} onClick={() => navigate('/chat')}>
          Back to Chat
        </Button>
      </Box>
    )
  }
  
  return (
    <Box p={{ base: 4, md: 6 }} maxW="6xl" mx="auto">
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <HStack justify="space-between" align="start">
          <VStack align="start" spacing={2} flex={1}>
            <HStack>
              <IconButton
                aria-label="Back"
                icon={<ArrowBackIcon />}
                onClick={() => navigate('/chat')}
                variant="ghost"
                size="sm"
              />
              <Heading size={{ base: 'md', md: 'lg' }}>Session Summary</Heading>
            </HStack>
            <Text color="gray.400" fontSize={{ base: 'xs', md: 'sm' }}>
              {summary.title}
            </Text>
          </VStack>
          
          <HStack spacing={2}>
            <Button
              leftIcon={copied ? <CheckIcon /> : <CopyIcon />}
              size="sm"
              colorScheme={copied ? 'green' : 'blue'}
              variant="outline"
              onClick={handleCopy}
            >
              {copied ? 'Copied!' : 'Copy'}
            </Button>
            <Button
              leftIcon={<DownloadIcon />}
              size="sm"
              colorScheme="purple"
              onClick={handleDownload}
            >
              Download
            </Button>
          </HStack>
        </HStack>
        
        {/* Session Info */}
        <Card bg={cardBg}>
          <CardBody>
            <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
              <VStack align="start" spacing={1}>
                <Text fontSize="xs" color="gray.500">Session ID</Text>
                <Code fontSize="xs">{summary.session_id.slice(0, 8)}...</Code>
              </VStack>
              <VStack align="start" spacing={1}>
                <Text fontSize="xs" color="gray.500">Created</Text>
                <Text fontSize="sm">{new Date(summary.created_at).toLocaleDateString()}</Text>
              </VStack>
              <VStack align="start" spacing={1}>
                <Text fontSize="xs" color="gray.500">Last Updated</Text>
                <Text fontSize="sm">{new Date(summary.updated_at).toLocaleDateString()}</Text>
              </VStack>
              <VStack align="start" spacing={1}>
                <Text fontSize="xs" color="gray.500">Status</Text>
                <Badge colorScheme="green">Active</Badge>
              </VStack>
            </SimpleGrid>
          </CardBody>
        </Card>
        
        {/* Statistics */}
        <SimpleGrid columns={{ base: 2, md: 4 }} spacing={4}>
          <Card bg={cardBg}>
            <CardBody>
              <Stat>
                <StatLabel fontSize="xs">Total Messages</StatLabel>
                <StatNumber fontSize="2xl">{summary.conversation.total_messages}</StatNumber>
                <StatHelpText fontSize="xs">
                  {summary.statistics.total_user_messages} user / {summary.statistics.total_assistant_messages} assistant
                </StatHelpText>
              </Stat>
            </CardBody>
          </Card>
          
          <Card bg={cardBg}>
            <CardBody>
              <Stat>
                <StatLabel fontSize="xs">Code Reviews</StatLabel>
                <StatNumber fontSize="2xl">{summary.code_reviews.total_reviews}</StatNumber>
                <StatHelpText fontSize="xs">Completed</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
          
          <Card bg={cardBg}>
            <CardBody>
              <Stat>
                <StatLabel fontSize="xs">Issues Found</StatLabel>
                <StatNumber fontSize="2xl">{summary.statistics.total_code_issues_found}</StatNumber>
                <StatHelpText fontSize="xs">Total across all reviews</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
          
          <Card bg={cardBg}>
            <CardBody>
              <Stat>
                <StatLabel fontSize="xs">Critical Issues</StatLabel>
                <StatNumber fontSize="2xl" color="red.500">{summary.statistics.total_critical_issues}</StatNumber>
                <StatHelpText fontSize="xs">Requiring immediate attention</StatHelpText>
              </Stat>
            </CardBody>
          </Card>
        </SimpleGrid>
        
        {/* Content Tabs */}
        <Card bg={cardBg}>
          <CardBody>
            <Tabs colorScheme="blue" isLazy>
              <TabList>
                <Tab>Conversation ({summary.conversation.total_messages})</Tab>
                <Tab>Code Reviews ({summary.code_reviews.total_reviews})</Tab>
              </TabList>
              
              <TabPanels>
                {/* Conversation Tab */}
                <TabPanel px={0}>
                  <VStack spacing={4} align="stretch">
                    {summary.conversation.messages.map((msg, idx) => (
                      <Box
                        key={idx}
                        p={4}
                        bg={msg.role === 'user' ? 'rgba(66, 153, 225, 0.1)' : 'rgba(0, 0, 0, 0.2)'}
                        borderRadius="md"
                        borderLeft="4px solid"
                        borderLeftColor={msg.role === 'user' ? 'blue.500' : 'green.500'}
                      >
                        <HStack justify="space-between" mb={2}>
                          <Badge colorScheme={msg.role === 'user' ? 'blue' : 'green'}>
                            {msg.role}
                          </Badge>
                          <Text fontSize="xs" color="gray.500">
                            {new Date(msg.timestamp).toLocaleString()}
                          </Text>
                        </HStack>
                        <Text fontSize="sm" whiteSpace="pre-wrap">{msg.content}</Text>
                      </Box>
                    ))}
                  </VStack>
                </TabPanel>
                
                {/* Code Reviews Tab */}
                <TabPanel px={0}>
                  {summary.code_reviews.total_reviews === 0 ? (
                    <Center py={8}>
                      <Text color="gray.500">No code reviews in this session</Text>
                    </Center>
                  ) : (
                    <Accordion allowMultiple>
                      {summary.code_reviews.reviews.map((review, idx) => (
                        <AccordionItem key={idx} border="1px solid" borderColor="gray.700" borderRadius="md" mb={4}>
                          <h2>
                            <AccordionButton>
                              <Box flex="1" textAlign="left">
                                <HStack justify="space-between" w="full" pr={4}>
                                  <VStack align="start" spacing={1}>
                                    <Text fontWeight="semibold">{review.title}</Text>
                                    <HStack spacing={2} fontSize="xs">
                                      <Tag size="sm" colorScheme="blue">{review.language}</Tag>
                                      <Tag size="sm" colorScheme={review.status === 'completed' ? 'green' : 'yellow'}>
                                        {review.status}
                                      </Tag>
                                      <Text color="gray.500">
                                        {review.total_issues} issues ({review.critical_issues} critical)
                                      </Text>
                                    </HStack>
                                  </VStack>
                                </HStack>
                              </Box>
                              <AccordionIcon />
                            </AccordionButton>
                          </h2>
                          <AccordionPanel pb={4}>
                            <VStack spacing={3} align="stretch">
                              <Divider />
                              <Text fontSize="sm" fontWeight="semibold" color="gray.400">
                                Findings ({review.findings.length})
                              </Text>
                              {review.findings.map((finding, fIdx) => (
                                <Box
                                  key={fIdx}
                                  p={3}
                                  bg="rgba(0, 0, 0, 0.3)"
                                  borderRadius="md"
                                  borderLeft="3px solid"
                                  borderLeftColor={`${getSeverityColor(finding.severity)}.500`}
                                >
                                  <HStack justify="space-between" mb={2}>
                                    <HStack spacing={2}>
                                      <Badge colorScheme={getSeverityColor(finding.severity)}>
                                        {finding.severity}
                                      </Badge>
                                      <Text fontSize="sm" fontWeight="semibold">{finding.type}</Text>
                                    </HStack>
                                    {finding.line_number && (
                                      <Text fontSize="xs" color="gray.500">Line {finding.line_number}</Text>
                                    )}
                                  </HStack>
                                  <Text fontSize="sm">{finding.message}</Text>
                                </Box>
                              ))}
                            </VStack>
                          </AccordionPanel>
                        </AccordionItem>
                      ))}
                    </Accordion>
                  )}
                </TabPanel>
              </TabPanels>
            </Tabs>
          </CardBody>
        </Card>
      </VStack>
    </Box>
  )
}

export default SessionSummaryPage
