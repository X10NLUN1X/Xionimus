import React, { useState, useEffect } from 'react'
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  Button,
  VStack,
  Text,
  useToast,
  Alert,
  AlertIcon,
  Box,
  HStack,
  Badge,
  Spinner,
  Divider
} from '@chakra-ui/react'
import axios from 'axios'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001'

interface ForkPreview {
  session_id: string
  session_name: string
  total_messages: number
  messages_to_summarize: number
  messages_to_keep_full: number
  estimated_summary_reduction: string
  preview: {
    first_message: string
    last_message: string
  }
}

interface SessionForkDialogProps {
  isOpen: boolean
  onClose: () => void
  sessionId: string | null
  onForkComplete: (newSessionId: string) => void
}

export const SessionForkDialog: React.FC<SessionForkDialogProps> = ({
  isOpen,
  onClose,
  sessionId,
  onForkComplete
}) => {
  const [isLoading, setIsLoading] = useState(false)
  const [preview, setPreview] = useState<ForkPreview | null>(null)
  const [isForkingprocess, setIsForkingProcess] = useState(false)
  const toast = useToast()

  useEffect(() => {
    if (isOpen && sessionId) {
      loadPreview()
    }
  }, [isOpen, sessionId])

  const loadPreview = async () => {
    if (!sessionId) return

    setIsLoading(true)
    try {
      const token = localStorage.getItem('xionimus_token')
      const response = await axios.get(
        `${BACKEND_URL}/api/session-fork/fork-preview/${sessionId}`,
        {
          headers: token ? {
            'Authorization': `Bearer ${token}`
          } : {}
        }
      )

      setPreview(response.data)
    } catch (error: any) {
      console.error('Failed to load fork preview:', error)
      toast({
        title: 'Fehler',
        description: 'Vorschau konnte nicht geladen werden',
        status: 'error',
        duration: 3000
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleFork = async () => {
    if (!sessionId) return

    setIsForkingProcess(true)
    try {
      const token = localStorage.getItem('xionimus_token')
      const response = await axios.post(
        `${BACKEND_URL}/api/session-fork/fork`,
        {
          session_id: sessionId,
          include_last_n_messages: 10
        },
        {
          headers: token ? {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          } : {
            'Content-Type': 'application/json'
          }
        }
      )

      const result = response.data

      toast({
        title: '✅ Session geforkt!',
        description: result.message,
        status: 'success',
        duration: 5000
      })

      onForkComplete(result.new_session_id)
      onClose()
    } catch (error: any) {
      console.error('Failed to fork session:', error)
      toast({
        title: 'Fork fehlgeschlagen',
        description: error.response?.data?.detail || 'Fehler beim Forken der Session',
        status: 'error',
        duration: 5000
      })
    } finally {
      setIsForkingProcess(false)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>🔀 Session forken</ModalHeader>
        <ModalCloseButton />

        <ModalBody>
          {isLoading ? (
            <VStack spacing={4} py={6}>
              <Spinner size="lg" color="blue.500" />
              <Text color="gray.600">Lade Vorschau...</Text>
            </VStack>
          ) : preview ? (
            <VStack align="stretch" spacing={4}>
              <Alert status="info" borderRadius="md">
                <AlertIcon />
                <Box>
                  <Text fontSize="sm" fontWeight="semibold">Was ist ein Fork?</Text>
                  <Text fontSize="sm">
                    Ein Fork erstellt eine neue Session mit einer kompakten Zusammenfassung der bisherigen Konversation. 
                    Die letzten 10 Nachrichten werden vollständig übernommen.
                  </Text>
                </Box>
              </Alert>

              <Box p={4} bg="gray.50" borderRadius="md">
                <VStack align="stretch" spacing={3}>
                  <HStack justify="space-between">
                    <Text fontSize="sm" fontWeight="semibold">Aktuelle Session:</Text>
                    <Badge colorScheme="purple">{preview.session_name}</Badge>
                  </HStack>

                  <Divider />

                  <HStack justify="space-between">
                    <Text fontSize="sm">Gesamt-Nachrichten:</Text>
                    <Badge colorScheme="blue">{preview.total_messages}</Badge>
                  </HStack>

                  <HStack justify="space-between">
                    <Text fontSize="sm">Werden zusammengefasst:</Text>
                    <Badge colorScheme="orange">{preview.messages_to_summarize}</Badge>
                  </HStack>

                  <HStack justify="space-between">
                    <Text fontSize="sm">Vollständig übernommen:</Text>
                    <Badge colorScheme="green">{preview.messages_to_keep_full}</Badge>
                  </HStack>

                  <HStack justify="space-between">
                    <Text fontSize="sm">Geschätzte Reduzierung:</Text>
                    <Badge colorScheme="cyan">{preview.estimated_summary_reduction}</Badge>
                  </HStack>
                </VStack>
              </Box>

              <Box>
                <Text fontSize="sm" fontWeight="semibold" mb={2}>📋 Kontext-Preview:</Text>
                <VStack align="stretch" spacing={2}>
                  <Box p={3} bg="blue.50" borderRadius="md" borderLeftWidth="3px" borderLeftColor="blue.500">
                    <Text fontSize="xs" color="gray.600" mb={1}>Erste Nachricht:</Text>
                    <Text fontSize="sm">{preview.preview.first_message}</Text>
                  </Box>
                  <Box p={3} bg="green.50" borderRadius="md" borderLeftWidth="3px" borderLeftColor="green.500">
                    <Text fontSize="xs" color="gray.600" mb={1}>Letzte Nachricht:</Text>
                    <Text fontSize="sm">{preview.preview.last_message}</Text>
                  </Box>
                </VStack>
              </Box>

              <Alert status="success" borderRadius="md" fontSize="sm">
                <AlertIcon />
                Nach dem Fork kannst du nahtlos in der neuen Session weiterarbeiten!
              </Alert>
            </VStack>
          ) : (
            <Text color="gray.600">Keine Vorschau verfügbar</Text>
          )}
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose} isDisabled={isForkingProcess}>
            Abbrechen
          </Button>
          <Button
            colorScheme="blue"
            onClick={handleFork}
            isLoading={isForkingProcess}
            loadingText="Forke Session..."
            leftIcon={<Text>🔀</Text>}
          >
            Jetzt forken
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}
