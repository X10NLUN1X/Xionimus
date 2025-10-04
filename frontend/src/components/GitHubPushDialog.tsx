import React, { useState, useEffect } from 'react'
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
  FormControl,
  FormLabel,
  Input,
  Textarea,
  HStack,
  Text,
  Alert,
  AlertIcon,
  Spinner,
  Box,
  useToast,
  Switch,
  Link
} from '@chakra-ui/react'
import axios from 'axios'

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001'

interface GitHubPushDialogProps {
  isOpen: boolean
  onClose: () => void
  sessionId?: string
}

export const GitHubPushDialog: React.FC<GitHubPushDialogProps> = ({
  isOpen,
  onClose,
  sessionId
}) => {
  const [isPushing, setIsPushing] = useState(false)
  const [isCheckingConnection, setIsCheckingConnection] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const [githubUsername, setGithubUsername] = useState('')
  
  // Repository configuration
  const [repoName, setRepoName] = useState('')
  const [repoDescription, setRepoDescription] = useState('')
  const [isPrivate, setIsPrivate] = useState(false)
  const [resultUrl, setResultUrl] = useState('')

  const toast = useToast()

  // Check GitHub connection status
  useEffect(() => {
    if (isOpen) {
      checkGitHubConnection()
      generateDefaultRepoName()
    }
  }, [isOpen])

  const generateDefaultRepoName = () => {
    const date = new Date()
    const dateStr = date.toISOString().split('T')[0].replace(/-/g, '')
    setRepoName(`xionimus-session-${dateStr}`)
  }

  const checkGitHubConnection = async () => {
    setIsCheckingConnection(true)
    try {
      const token = localStorage.getItem('token')
      const response = await axios.get(`${BACKEND_URL}/api/github-pat/verify-token`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      setIsConnected(response.data.connected)
      if (response.data.connected) {
        setGithubUsername(response.data.github_username || '')
      }
    } catch (error) {
      console.error('Failed to check GitHub connection:', error)
      setIsConnected(false)
    } finally {
      setIsCheckingConnection(false)
    }
  }

  const handlePush = async () => {
    if (!sessionId) {
      toast({
        title: 'Fehler',
        description: 'Keine Session gefunden',
        status: 'error',
        duration: 3000
      })
      return
    }

    if (!repoName.trim()) {
      toast({
        title: 'Fehler',
        description: 'Repository-Name ist erforderlich',
        status: 'error',
        duration: 3000
      })
      return
    }

    setIsPushing(true)
    setResultUrl('')
    
    try {
      const token = localStorage.getItem('token')
      const response = await axios.post(
        `${BACKEND_URL}/api/github-pat/push-session`,
        {
          session_id: sessionId,
          repo_name: repoName.trim(),
          repo_description: repoDescription.trim() || undefined,
          is_private: isPrivate
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      )

      if (response.data.success) {
        setResultUrl(response.data.repo_url)
        toast({
          title: 'Erfolgreich gepusht!',
          description: response.data.message,
          status: 'success',
          duration: 5000
        })
      }
    } catch (error: any) {
      console.error('Push failed:', error)
      toast({
        title: 'Push fehlgeschlagen',
        description: error.response?.data?.detail || 'Ein Fehler ist aufgetreten',
        status: 'error',
        duration: 5000
      })
    } finally {
      setIsPushing(false)
    }
  }

  // If still checking connection
  if (isCheckingConnection) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} size="md">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>GitHub Push</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4} py={8}>
              <Spinner size="xl" color="blue.500" />
              <Text>Überprüfe GitHub-Verbindung...</Text>
            </VStack>
          </ModalBody>
        </ModalContent>
      </Modal>
    )
  }

  // If not connected to GitHub
  if (!isConnected) {
    return (
      <Modal isOpen={isOpen} onClose={onClose} size="md">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>GitHub Verbindung erforderlich</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <VStack spacing={4} py={4}>
              <Box
                w="60px"
                h="60px"
                bg="gray.800"
                borderRadius="full"
                display="flex"
                alignItems="center"
                justifyContent="center"
              >
                <svg width="40" height="40" fill="white" viewBox="0 0 16 16">
                  <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/>
                </svg>
              </Box>
              <Text fontSize="lg" fontWeight="600">
                GitHub nicht verbunden
              </Text>
              <Text fontSize="sm" color="gray.500" textAlign="center">
                Bitte verbinden Sie Ihr GitHub-Konto in den Einstellungen, um Code zu pushen.
              </Text>
              <Alert status="info" fontSize="sm">
                <AlertIcon />
                Sie benötigen ein GitHub Personal Access Token (PAT) mit 'repo' Berechtigung.
              </Alert>
            </VStack>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" onClick={onClose}>
              Schließen
            </Button>
            <Button
              colorScheme="blue"
              onClick={() => {
                onClose()
                window.location.href = '/settings'
              }}
            >
              Zu Einstellungen
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    )
  }

  // Connected - show push dialog
  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>
          <HStack>
            <Text>📤 Session zu GitHub pushen</Text>
            {githubUsername && (
              <Text fontSize="sm" color="gray.500">
                (@{githubUsername})
              </Text>
            )}
          </HStack>
        </ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <VStack spacing={4} align="stretch">
            {resultUrl ? (
              // Success view
              <VStack spacing={4} py={4}>
                <Box
                  w="60px"
                  h="60px"
                  bg="green.500"
                  borderRadius="full"
                  display="flex"
                  alignItems="center"
                  justifyContent="center"
                >
                  <Text fontSize="3xl">✓</Text>
                </Box>
                <Text fontSize="lg" fontWeight="600" textAlign="center">
                  Erfolgreich gepusht!
                </Text>
                <Text fontSize="sm" color="gray.500" textAlign="center">
                  Ihre Session wurde erfolgreich zu GitHub gepusht.
                </Text>
                <Link href={resultUrl} isExternal color="blue.500" fontWeight="600">
                  🔗 Repository auf GitHub öffnen
                </Link>
              </VStack>
            ) : (
              // Configuration view
              <>
                <Alert status="info" fontSize="sm">
                  <AlertIcon />
                  Diese Session (alle Nachrichten und Code) wird zu GitHub gepusht.
                </Alert>

                <FormControl isRequired>
                  <FormLabel>Repository-Name</FormLabel>
                  <Input
                    value={repoName}
                    onChange={(e) => setRepoName(e.target.value)}
                    placeholder="xionimus-session-20250110"
                  />
                  <Text fontSize="xs" color="gray.500" mt={1}>
                    Der Name für das neue oder bestehende Repository
                  </Text>
                </FormControl>

                <FormControl>
                  <FormLabel>Beschreibung (optional)</FormLabel>
                  <Textarea
                    value={repoDescription}
                    onChange={(e) => setRepoDescription(e.target.value)}
                    placeholder="Xionimus AI Session - Conversation history and generated code"
                    rows={3}
                  />
                </FormControl>

                <FormControl display="flex" alignItems="center" justifyContent="space-between">
                  <FormLabel mb="0">Privates Repository</FormLabel>
                  <Switch
                    isChecked={isPrivate}
                    onChange={(e) => setIsPrivate(e.target.checked)}
                    colorScheme="purple"
                  />
                </FormControl>

                <Box bg="gray.50" p={4} borderRadius="md" fontSize="sm">
                  <Text fontWeight="600" mb={2}>📦 Was wird gepusht:</Text>
                  <VStack align="start" spacing={1} color="gray.600">
                    <Text>• README.md mit Session-Zusammenfassung</Text>
                    <Text>• messages.json mit vollständiger Konversation</Text>
                    <Text>• code/ Ordner mit extrahierten Code-Blöcken</Text>
                  </VStack>
                </Box>
              </>
            )}
          </VStack>
        </ModalBody>

        <ModalFooter>
          <HStack spacing={3}>
            <Button variant="ghost" onClick={onClose}>
              {resultUrl ? 'Schließen' : 'Abbrechen'}
            </Button>
            {!resultUrl && (
              <Button
                bg="linear-gradient(135deg, #0088cc, #0066aa)"
                color="white"
                onClick={handlePush}
                isLoading={isPushing}
                loadingText="Pushe zu GitHub..."
                isDisabled={!repoName.trim()}
                _hover={{
                  bg: "linear-gradient(135deg, #0066aa, #0088cc)",
                  boxShadow: "0 0 25px rgba(0, 212, 255, 0.6)"
                }}
                boxShadow="0 2px 15px rgba(0, 212, 255, 0.4)"
              >
                📤 Zu GitHub pushen
              </Button>
            )}
          </HStack>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}
