import React, { useState } from 'react'
import {
  Box,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Button,
  Progress,
  VStack,
  HStack,
  Text,
  useToast,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  useDisclosure,
  Badge,
  Divider
} from '@chakra-ui/react'
import { WarningIcon } from '@chakra-ui/icons'
import axios from 'axios'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001'

interface ContextWarningProps {
  sessionId: string
  currentTokens: number
  limit: number
  percentage: number
  recommendation: 'ok' | 'warning' | 'critical'
  onSessionForked: (newSessionId: string) => void
  apiKeys?: Record<string, string>
}

export const ContextWarning: React.FC<ContextWarningProps> = ({
  sessionId,
  currentTokens,
  limit,
  percentage,
  recommendation,
  onSessionForked,
  apiKeys
}) => {
  const { isOpen, onOpen, onClose } = useDisclosure()
  const [isProcessing, setIsProcessing] = useState(false)
  const [summary, setSummary] = useState<any>(null)
  const toast = useToast()

  // Don't show if context is ok
  if (recommendation === 'ok') {
    return null
  }

  const handleSummarizeAndFork = async () => {
    setIsProcessing(true)
    
    try {
      const token = localStorage.getItem('xionimus_token')
      
      const response = await axios.post(
        `${BACKEND_URL}/api/session-management/summarize-and-fork`,
        {
          session_id: sessionId,
          api_keys: apiKeys || {}
        },
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )
      
      setSummary(response.data)
      onOpen() // Show options modal
      
      toast({
        title: '✅ Session zusammengefasst',
        description: 'Neue Session wurde erstellt',
        status: 'success',
        duration: 3000
      })
      
    } catch (error) {
      console.error('Session fork error:', error)
      toast({
        title: '❌ Fehler',
        description: 'Session konnte nicht zusammengefasst werden',
        status: 'error',
        duration: 5000
      })
    } finally {
      setIsProcessing(false)
    }
  }

  const handleSelectOption = async (option: any) => {
    try {
      const token = localStorage.getItem('xionimus_token')
      
      await axios.post(
        `${BACKEND_URL}/api/session-management/continue-with-option`,
        {
          session_id: summary.new_session_id,
          option_action: option.action,
          api_keys: apiKeys || {}
        },
        {
          headers: {
            Authorization: `Bearer ${token}`
          },
          params: {
            session_id: summary.new_session_id,
            option_action: option.action
          }
        }
      )
      
      // Navigate to new session
      onSessionForked(summary.new_session_id)
      onClose()
      
      toast({
        title: '🚀 Weiter geht\'s',
        description: option.title,
        status: 'success',
        duration: 3000
      })
      
    } catch (error) {
      console.error('Option selection error:', error)
      toast({
        title: '❌ Fehler',
        description: 'Option konnte nicht ausgewählt werden',
        status: 'error',
        duration: 5000
      })
    }
  }

  const getAlertStatus = () => {
    if (recommendation === 'critical') return 'error'
    if (recommendation === 'warning') return 'warning'
    return 'info'
  }

  const getAlertMessage = () => {
    if (recommendation === 'critical') {
      return 'Context-Limit fast erreicht! Bitte Session zusammenfassen, um fortzufahren.'
    }
    return 'Context wird bald voll. Wir empfehlen eine Zusammenfassung.'
  }

  return (
    <>
      <Alert
        status={getAlertStatus()}
        variant="left-accent"
        borderRadius="md"
        mb={4}
      >
        <AlertIcon />
        <Box flex="1">
          <AlertTitle display="flex" alignItems="center" gap={2}>
            <WarningIcon />
            Context-Warnung
            <Badge colorScheme={recommendation === 'critical' ? 'red' : 'orange'}>
              {percentage.toFixed(1)}%
            </Badge>
          </AlertTitle>
          <AlertDescription mt={2}>
            <VStack align="stretch" spacing={2}>
              <Text fontSize="sm">
                {getAlertMessage()}
              </Text>
              
              <Progress
                value={percentage}
                colorScheme={recommendation === 'critical' ? 'red' : 'orange'}
                size="sm"
                borderRadius="full"
              />
              
              <HStack spacing={2} fontSize="xs" color="gray.600">
                <Text>{currentTokens.toLocaleString()} / {limit.toLocaleString()} Tokens</Text>
              </HStack>
              
              <Button
                size="sm"
                colorScheme={recommendation === 'critical' ? 'red' : 'orange'}
                onClick={handleSummarizeAndFork}
                isLoading={isProcessing}
                loadingText="Zusammenfassen..."
                leftIcon={<WarningIcon />}
                mt={2}
              >
                Session zusammenfassen & fortsetzen
              </Button>
            </VStack>
          </AlertDescription>
        </Box>
      </Alert>

      {/* Options Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            <VStack align="start" spacing={1}>
              <Text>📋 Neue Session erstellt</Text>
              <Text fontSize="sm" fontWeight="normal" color="gray.500">
                Wie möchtest du fortfahren?
              </Text>
            </VStack>
          </ModalHeader>
          <ModalCloseButton />
          
          <ModalBody>
            {summary && (
              <VStack align="stretch" spacing={4}>
                {/* Summary Preview */}
                <Box
                  p={4}
                  bg="gray.50"
                  borderRadius="md"
                  fontSize="sm"
                  maxH="200px"
                  overflowY="auto"
                >
                  <Text whiteSpace="pre-wrap">
                    {summary.summary.substring(0, 500)}
                    {summary.summary.length > 500 ? '...' : ''}
                  </Text>
                </Box>
                
                <Divider />
                
                {/* Next Steps Options */}
                <Text fontWeight="semibold">🎯 Nächste Schritte:</Text>
                
                <VStack align="stretch" spacing={3}>
                  {summary.next_steps.map((option: any, index: number) => (
                    <Button
                      key={index}
                      size="lg"
                      variant="outline"
                      height="auto"
                      py={4}
                      onClick={() => handleSelectOption(option)}
                      textAlign="left"
                      whiteSpace="normal"
                      justifyContent="flex-start"
                      _hover={{
                        bg: 'blue.50',
                        borderColor: 'blue.400'
                      }}
                    >
                      <VStack align="start" spacing={1} flex={1}>
                        <HStack>
                          <Badge colorScheme="blue">{index + 1}</Badge>
                          <Text fontWeight="semibold" fontSize="md">
                            {option.title}
                          </Text>
                        </HStack>
                        <Text fontSize="sm" color="gray.600" fontWeight="normal">
                          {option.description}
                        </Text>
                      </VStack>
                    </Button>
                  ))}
                </VStack>
              </VStack>
            )}
          </ModalBody>
          
          <ModalFooter>
            <Button variant="ghost" onClick={onClose}>
              Abbrechen
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  )
}
