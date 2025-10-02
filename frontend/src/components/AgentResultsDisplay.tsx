import React, { useState, useMemo, useCallback } from 'react'
import {
  Box,
  VStack,
  HStack,
  Text,
  Collapse,
  IconButton,
  useColorModeValue,
  Badge,
  Divider
} from '@chakra-ui/react'
import { ChevronDownIcon, ChevronUpIcon } from '@chakra-ui/icons'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface AgentResult {
  agent: string
  icon: string
  content: string
  summary: string
  data?: any
}

interface AgentResultsDisplayProps {
  agentResults: AgentResult[]
}

export const AgentResultsDisplay: React.FC<AgentResultsDisplayProps> = ({ agentResults }) => {
  const [expandedAgents, setExpandedAgents] = useState<Set<string>>(new Set())
  
  const bgColor = useColorModeValue('blue.50', 'rgba(0, 100, 200, 0.1)')
  const borderColor = useColorModeValue('blue.200', 'rgba(0, 212, 255, 0.3)')
  const summaryBg = useColorModeValue('white', 'rgba(15, 30, 50, 0.6)')
  const textColor = useColorModeValue('gray.800', 'white')
  
  // Memoize toggle function to prevent re-renders
  const toggleAgent = useCallback((agentName: string) => {
    setExpandedAgents(prev => {
      const newExpanded = new Set(prev)
      if (newExpanded.has(agentName)) {
        newExpanded.delete(agentName)
      } else {
        newExpanded.add(agentName)
      }
      return newExpanded
    })
  }, [])
  
  // Memoize deduplicated results to prevent duplicate rendering
  const uniqueResults = useMemo(() => {
    const seen = new Set<string>()
    return agentResults.filter(result => {
      const key = `${result.agent}-${result.summary}`
      if (seen.has(key)) {
        return false
      }
      seen.add(key)
      return true
    })
  }, [agentResults])
  
  if (!uniqueResults || uniqueResults.length === 0) {
    return null
  }
  
  return (
    <Box
      mt={4}
      p={4}
      bg={bgColor}
      borderRadius="lg"
      border="1px solid"
      borderColor={borderColor}
    >
      <Text fontSize="sm" fontWeight="bold" mb={3} color={textColor}>
        🤖 Automatische Verbesserungen ({agentResults.length} Agents)
      </Text>
      
      <VStack spacing={3} align="stretch">
        {agentResults.map((result, idx) => {
          const isExpanded = expandedAgents.has(result.agent)
          
          return (
            <Box
              key={idx}
              bg={summaryBg}
              borderRadius="md"
              border="1px solid"
              borderColor={borderColor}
              overflow="hidden"
            >
              {/* Zusammenfassung - Immer sichtbar */}
              <HStack
                p={3}
                spacing={3}
                cursor="pointer"
                onClick={() => toggleAgent(result.agent)}
                _hover={{ bg: useColorModeValue('gray.50', 'rgba(0, 212, 255, 0.05)') }}
                transition="background 0.2s"
              >
                <Text fontSize="lg">{result.icon}</Text>
                <VStack align="start" flex={1} spacing={1}>
                  <Text fontWeight="semibold" fontSize="sm" color={textColor}>
                    {result.agent}
                  </Text>
                  <Text fontSize="xs" color="gray.500">
                    {result.summary}
                  </Text>
                </VStack>
                <IconButton
                  aria-label={isExpanded ? "Collapse" : "Expand"}
                  icon={isExpanded ? <ChevronUpIcon /> : <ChevronDownIcon />}
                  size="sm"
                  variant="ghost"
                  colorScheme="blue"
                />
              </HStack>
              
              {/* Details - Zusammenklappbar */}
              <Collapse in={isExpanded} animateOpacity>
                <Box
                  p={4}
                  pt={0}
                  borderTop="1px solid"
                  borderColor={borderColor}
                  maxH="400px"
                  overflowY="auto"
                  sx={{
                    '&::-webkit-scrollbar': {
                      width: '8px',
                    },
                    '&::-webkit-scrollbar-track': {
                      background: 'transparent',
                    },
                    '&::-webkit-scrollbar-thumb': {
                      background: useColorModeValue('gray.300', 'rgba(0, 212, 255, 0.3)'),
                      borderRadius: '4px',
                    },
                  }}
                >
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={{
                      h1: ({ children }) => (
                        <Text fontSize="lg" fontWeight="bold" mt={2} mb={2} color={textColor}>
                          {children}
                        </Text>
                      ),
                      h2: ({ children }) => (
                        <Text fontSize="md" fontWeight="semibold" mt={2} mb={1} color={textColor}>
                          {children}
                        </Text>
                      ),
                      h3: ({ children }) => (
                        <Text fontSize="sm" fontWeight="semibold" mt={1} mb={1} color={textColor}>
                          {children}
                        </Text>
                      ),
                      p: ({ children }) => (
                        <Text fontSize="sm" mb={2} color={textColor}>
                          {children}
                        </Text>
                      ),
                      ul: ({ children }) => (
                        <Box as="ul" pl={4} mb={2} fontSize="sm" color={textColor}>
                          {children}
                        </Box>
                      ),
                      li: ({ children }) => (
                        <Box as="li" mb={1}>
                          {children}
                        </Box>
                      ),
                      code: ({ children }) => (
                        <Box
                          as="code"
                          bg={useColorModeValue('gray.100', 'rgba(0, 0, 0, 0.3)')}
                          px={1}
                          py={0.5}
                          borderRadius="sm"
                          fontSize="xs"
                          fontFamily="mono"
                        >
                          {children}
                        </Box>
                      ),
                    }}
                  >
                    {result.content}
                  </ReactMarkdown>
                </Box>
              </Collapse>
            </Box>
          )
        })}
      </VStack>
    </Box>
  )
}
