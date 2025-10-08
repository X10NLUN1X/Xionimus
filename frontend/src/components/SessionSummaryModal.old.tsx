import React, { useState } from 'react'
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalFooter,
  ModalBody,
  ModalCloseButton,
  Button,
  VStack,
  HStack,
  Text,
  Box,
  Spinner,
  useColorModeValue,
  Badge,
  Divider,
  useToast,
  Icon
} from '@chakra-ui/react'
import { CheckCircleIcon, InfoIcon, WarningIcon } from '@chakra-ui/icons'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface SessionSummaryModalProps {
  isOpen: boolean
  onClose: () => void
  sessionId: string | null
  apiKeys: {
    openai: string
    anthropic: string
    perplexity: string
  }
  onSwitchSession: (sessionId: string) => void
}

interface SummaryData {
  session_id: string
  new_session_id: string
  summary: string
  context_transfer: string
  next_steps: Array<{
    title: string
    description: string
    action: string
  }>
  old_session_tokens: number
  timestamp: string
}

export const SessionSummaryModal: React.FC<SessionSummaryModalProps> = ({
  isOpen,
  onClose,
  sessionId,
  apiKeys,
  onSwitchSession
}) => {
  const [isLoading, setIsLoading] = useState(false)
  const [summaryData, setSummaryData] = useState<SummaryData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [selectedOption, setSelectedOption] = useState<number | null>(null)
  const toast = useToast()
  
  const bgColor = useColorModeValue('white', '#0a1628')
  const borderColor = useColorModeValue('gray.200', 'rgba(0, 212, 255, 0.3)')
  const cardBg = useColorModeValue('gray.50', 'rgba(15, 30, 50, 0.6)')
  const hoverBg = useColorModeValue('blue.50', 'rgba(0, 136, 204, 0.2)')
  
  const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001'

  // Generate summary when modal opens
  React.useEffect(() => {
    if (isOpen && sessionId && !summaryData && !isLoading) {
      handleGenerateSummary()
    }
  }, [isOpen, sessionId])

  const handleGenerateSummary = async () => {
    if (!sessionId) {
      setError('Keine aktive Session')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const token = localStorage.getItem('xionimus_token')
      const response = await fetch(
        `${API_BASE}/api/session-management/summarize-and-fork`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify({
            session_id: sessionId,
            api_keys: apiKeys
          })
        }
      )

      if (!response.ok) {
        throw new Error('Zusammenfassung fehlgeschlagen')
      }

      const data: SummaryData = await response.json()
      setSummaryData(data)
      
      toast({
        title: '✅ Session zusammengefasst',
        description: 'Neue Session wurde erstellt',
        status: 'success',
        duration: 3000
      })
    } catch (err: any) {
      console.error('Summary generation error:', err)
      setError(err.message || 'Fehler beim Generieren der Zusammenfassung')
      toast({
        title: 'Fehler',
        description: err.message,
        status: 'error',
        duration: 5000
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleSelectOption = async (optionIndex: number) => {
    if (!summaryData) return

    setSelectedOption(optionIndex)
    const selectedAction = summaryData.next_steps[optionIndex]

    try {
      const token = localStorage.getItem('xionimus_token')
      await fetch(`${API_BASE}/api/session-management/continue-with-option`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          session_id: summaryData.new_session_id,
          option_action: selectedAction.action,
          api_keys: apiKeys
        })
      })

      // Switch to the new session
      onSwitchSession(summaryData.new_session_id)
      
      toast({
        title: '✅ Neue Session gestartet',
        description: `"${selectedAction.title}" wird fortgesetzt`,
        status: 'success',
        duration: 3000
      })
      
      // Close modal
      onClose()
      
      // Reset state for next time
      setTimeout(() => {
        setSummaryData(null)
        setSelectedOption(null)
        setError(null)
      }, 500)
    } catch (err: any) {
      console.error('Option selection error:', err)
      toast({
        title: 'Fehler',
        description: 'Option konnte nicht ausgewählt werden',
        status: 'error',
        duration: 3000
      })
      setSelectedOption(null)
    }
  }

  const handleClose = () => {
    onClose()
    // Reset state
    setTimeout(() => {
      setSummaryData(null)
      setSelectedOption(null)
      setError(null)
    }, 300)
  }

  return (
    <Modal isOpen={isOpen} onClose={handleClose} size="2xl" scrollBehavior="inside">
      <ModalOverlay backdropFilter="blur(4px)" />
      <ModalContent bg={bgColor} borderColor={borderColor} maxH="85vh">
        <ModalHeader borderBottom="1px solid" borderColor={borderColor}>
          <HStack spacing={2}>
            <Icon as={InfoIcon} color="blue.400" />
            <Text>Session Zusammenfassung</Text>
          </HStack>
        </ModalHeader>
        <ModalCloseButton />
        
        <ModalBody py={6}>
          {isLoading && (
            <VStack spacing={4} py={8}>
              <Spinner size="xl" color="blue.400" thickness="4px" />
              <Text color="gray.500">
                KI erstellt Zusammenfassung...
              </Text>
              <Text fontSize="sm" color="gray.400">
                Dies kann 10-30 Sekunden dauern
              </Text>
            </VStack>
          )}

          {error && (
            <Box
              p={4}
              bg="red.50"
              borderRadius="lg"
              borderLeft="4px solid"
              borderColor="red.400"
            >
              <HStack spacing={2}>
                <Icon as={WarningIcon} color="red.400" />
                <Text color="red.700">{error}</Text>
              </HStack>
            </Box>
          )}

          {summaryData && !isLoading && (
            <VStack spacing={6} align="stretch">
              {/* Token Savings Info */}
              <Box
                p={4}
                bg={cardBg}
                borderRadius="lg"
                borderLeft="4px solid"
                borderColor="green.400"
              >
                <HStack justify="space-between">
                  <HStack spacing={2}>
                    <Icon as={CheckCircleIcon} color="green.400" />
                    <Text fontWeight="600">Session gespeichert</Text>
                  </HStack>
                  <Badge colorScheme="green" fontSize="sm">
                    {summaryData.old_session_tokens.toLocaleString()} Tokens
                  </Badge>
                </HStack>
                <Text fontSize="sm" color="gray.500" mt={2}>
                  Neue Session mit komprimiertem Kontext erstellt
                </Text>
              </Box>

              <Divider />

              {/* Summary Section */}
              <Box>
                <Text fontWeight="700" fontSize="lg" mb={3} color="blue.400">
                  📋 Zusammenfassung
                </Text>
                <Box
                  p={4}
                  bg={cardBg}
                  borderRadius="lg"
                  fontSize="sm"
                  lineHeight="1.7"
                  sx={{
                    '& h1, & h2, & h3': {
                      fontWeight: 'bold',
                      marginTop: '1em',
                      marginBottom: '0.5em'
                    },
                    '& p': {
                      marginBottom: '0.8em'
                    },
                    '& ul, & ol': {
                      paddingLeft: '1.5em',
                      marginBottom: '0.8em'
                    }
                  }}
                >
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {summaryData.summary}
                  </ReactMarkdown>
                </Box>
              </Box>

              <Divider />

              {/* Next Steps Options */}
              <Box>
                <Text fontWeight="700" fontSize="lg" mb={3} color="blue.400">
                  🎯 Wie möchtest du fortfahren?
                </Text>
                <VStack spacing={3} align="stretch">
                  {summaryData.next_steps.map((option, index) => (
                    <Box
                      key={index}
                      p={4}
                      bg={cardBg}
                      borderRadius="lg"
                      borderWidth="2px"
                      borderColor={selectedOption === index ? 'blue.400' : borderColor}
                      cursor="pointer"
                      transition="all 0.2s"
                      _hover={{
                        bg: hoverBg,
                        borderColor: 'blue.400',
                        transform: 'translateY(-2px)'
                      }}
                      onClick={() => handleSelectOption(index)}
                    >
                      <HStack justify="space-between" align="start">
                        <VStack align="start" spacing={1} flex={1}>
                          <HStack>
                            <Badge colorScheme="blue" fontSize="xs">
                              Option {index + 1}
                            </Badge>
                            <Text fontWeight="600" fontSize="md">
                              {option.title}
                            </Text>
                          </HStack>
                          <Text fontSize="sm" color="gray.500">
                            {option.description}
                          </Text>
                        </VStack>
                        {selectedOption === index && (
                          <Spinner size="sm" color="blue.400" />
                        )}
                      </HStack>
                    </Box>
                  ))}
                </VStack>
              </Box>

              <Box
                p={3}
                bg="blue.50"
                borderRadius="lg"
                fontSize="sm"
                color="blue.700"
              >
                <Text>
                  💡 <strong>Tipp:</strong> Wähle eine Option, um mit der neuen Session fortzufahren.
                  Deine alte Session bleibt erhalten.
                </Text>
              </Box>
            </VStack>
          )}
        </ModalBody>

        <ModalFooter borderTop="1px solid" borderColor={borderColor}>
          <Button variant="ghost" onClick={handleClose}>
            Schließen
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}
