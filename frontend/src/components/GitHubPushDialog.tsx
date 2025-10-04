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
  Link,
  Checkbox,
  Code,
  Divider,
  Badge,
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon
} from '@chakra-ui/react'
import axios from 'axios'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001'

interface GitHubPushDialogProps {
  isOpen: boolean
  onClose: () => void
  sessionId?: string
}

interface FilePreview {
  path: string
  content: string
  size: number
  type: string
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
  
  // File preview and selection
  const [isLoadingPreview, setIsLoadingPreview] = useState(false)
  const [filePreview, setFilePreview] = useState<FilePreview[]>([])
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set())
  const [showPreview, setShowPreview] = useState(false)

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

  const loadFilePreview = async () => {
    if (!sessionId) return
    
    setIsLoadingPreview(true)
    try {
      const token = localStorage.getItem('token')
      const response = await axios.post(
        `${BACKEND_URL}/api/github-pat/preview-session-files`,
        { session_id: sessionId },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      )
      
      setFilePreview(response.data.files)
      // Select all files by default
      setSelectedFiles(new Set(response.data.files.map((f: FilePreview) => f.path)))
      setShowPreview(true)
    } catch (error: any) {
      console.error('Failed to load file preview:', error)
      toast({
        title: 'Fehler',
        description: 'Dateivorschau konnte nicht geladen werden',
        status: 'error',
        duration: 3000
      })
    } finally {
      setIsLoadingPreview(false)
    }
  }

  const toggleFileSelection = (path: string) => {
    const newSelected = new Set(selectedFiles)
    if (newSelected.has(path)) {
      newSelected.delete(path)
    } else {
      newSelected.add(path)
    }
    setSelectedFiles(newSelected)
  }

  const selectAllFiles = () => {
    setSelectedFiles(new Set(filePreview.map(f => f.path)))
  }

  const deselectAllFiles = () => {
    setSelectedFiles(new Set())
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

    if (selectedFiles.size === 0) {
      toast({
        title: 'Fehler',
        description: 'Bitte wählen Sie mindestens eine Datei aus',
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
          is_private: isPrivate,
          selected_files: Array.from(selectedFiles)
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
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalOverlay />
      <ModalContent maxW="800px">
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

                <Divider />

                {/* File Preview Section */}
                <Box>
                  <HStack justify="space-between" mb={2}>
                    <Text fontWeight="600">📋 Dateivorschau & Auswahl</Text>
                    {!showPreview && (
                      <Button
                        size="sm"
                        colorScheme="blue"
                        onClick={loadFilePreview}
                        isLoading={isLoadingPreview}
                        loadingText="Lade..."
                      >
                        Vorschau laden
                      </Button>
                    )}
                  </HStack>

                  {showPreview && filePreview.length > 0 ? (
                    <>
                      <HStack justify="space-between" mb={2}>
                        <Text fontSize="sm" color="gray.600">
                          {selectedFiles.size} von {filePreview.length} Dateien ausgewählt
                        </Text>
                        <HStack spacing={2}>
                          <Button size="xs" onClick={selectAllFiles} variant="ghost">
                            Alle auswählen
                          </Button>
                          <Button size="xs" onClick={deselectAllFiles} variant="ghost">
                            Alle abwählen
                          </Button>
                        </HStack>
                      </HStack>

                      <Box
                        maxH="300px"
                        overflowY="auto"
                        border="1px solid"
                        borderColor="gray.200"
                        borderRadius="md"
                        p={2}
                      >
                        <VStack align="stretch" spacing={2}>
                          {filePreview.map((file) => (
                            <Box
                              key={file.path}
                              p={3}
                              bg={selectedFiles.has(file.path) ? 'blue.50' : 'white'}
                              borderRadius="md"
                              border="1px solid"
                              borderColor={selectedFiles.has(file.path) ? 'blue.300' : 'gray.200'}
                            >
                              <HStack justify="space-between" mb={2}>
                                <HStack flex={1}>
                                  <Checkbox
                                    isChecked={selectedFiles.has(file.path)}
                                    onChange={() => toggleFileSelection(file.path)}
                                    colorScheme="blue"
                                  />
                                  <VStack align="start" spacing={0}>
                                    <Text fontSize="sm" fontWeight="600">
                                      {file.path}
                                    </Text>
                                    <HStack spacing={2}>
                                      <Badge colorScheme={
                                        file.type === 'readme' ? 'purple' :
                                        file.type === 'messages' ? 'green' :
                                        'blue'
                                      }>
                                        {file.type}
                                      </Badge>
                                      <Text fontSize="xs" color="gray.500">
                                        {(file.size / 1024).toFixed(1)} KB
                                      </Text>
                                    </HStack>
                                  </VStack>
                                </HStack>
                              </HStack>
                              
                              {/* Content preview */}
                              <Accordion allowToggle>
                                <AccordionItem border="none">
                                  <AccordionButton px={0} py={1}>
                                    <Box flex="1" textAlign="left">
                                      <Text fontSize="xs" color="gray.600">Vorschau anzeigen</Text>
                                    </Box>
                                    <AccordionIcon />
                                  </AccordionButton>
                                  <AccordionPanel px={0} pb={2}>
                                    <Code
                                      display="block"
                                      whiteSpace="pre-wrap"
                                      p={2}
                                      fontSize="xs"
                                      maxH="150px"
                                      overflowY="auto"
                                      bg="gray.50"
                                    >
                                      {file.content}
                                    </Code>
                                  </AccordionPanel>
                                </AccordionItem>
                              </Accordion>
                            </Box>
                          ))}
                        </VStack>
                      </Box>
                    </>
                  ) : !showPreview ? (
                    <Alert status="info" fontSize="sm">
                      <AlertIcon />
                      Klicken Sie auf "Vorschau laden", um alle Dateien anzusehen
                    </Alert>
                  ) : null}
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
                isDisabled={!repoName.trim() || selectedFiles.size === 0}
                _hover={{
                  bg: "linear-gradient(135deg, #0066aa, #0088cc)",
                  boxShadow: "0 0 25px rgba(0, 212, 255, 0.6)"
                }}
                boxShadow="0 2px 15px rgba(0, 212, 255, 0.4)"
              >
                📤 {selectedFiles.size} Datei(en) pushen
              </Button>
            )}
          </HStack>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}
