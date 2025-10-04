import React, { useState } from 'react'
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Text,
  useToast,
  Alert,
  AlertIcon,
  AlertDescription,
  Box,
  HStack,
  Badge,
  List,
  ListItem,
  ListIcon,
  Code,
  Spinner
} from '@chakra-ui/react'
import { CheckCircleIcon, WarningIcon } from '@chakra-ui/icons'
import { useGitHub } from '../contexts/GitHubContext'

interface GitHubImportDialogProps {
  isOpen: boolean
  onClose: () => void
}

export const GitHubImportDialog: React.FC<GitHubImportDialogProps> = ({
  isOpen,
  onClose
}) => {
  const [repoUrl, setRepoUrl] = useState('')
  const [branch, setBranch] = useState('main')
  const [targetDirectory, setTargetDirectory] = useState('')
  const [isImporting, setIsImporting] = useState(false)
  const [importResult, setImportResult] = useState<any>(null)
  
  const github = useGitHub()
  const toast = useToast()

  const handleImport = async () => {
    if (!repoUrl.trim()) {
      toast({
        title: 'Repository URL erforderlich',
        description: 'Bitte gib eine GitHub Repository URL ein',
        status: 'warning',
        duration: 3000
      })
      return
    }

    // Validate URL format
    if (!repoUrl.includes('github.com')) {
      toast({
        title: 'Ungültige URL',
        description: 'Bitte gib eine gültige GitHub Repository URL ein',
        status: 'error',
        duration: 3000
      })
      return
    }

    setIsImporting(true)
    setImportResult(null)

    try {
      // Use direct API call with JWT token to access user's GitHub PAT
      const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001'
      const jwtToken = localStorage.getItem('xionimus_token')
      
      const headers: any = {
        'Content-Type': 'application/json'
      }
      
      // Add JWT token if available (backend will use it to fetch user's GitHub PAT)
      if (jwtToken) {
        headers['Authorization'] = `Bearer ${jwtToken}`
      }
      
      const response = await fetch(`${BACKEND_URL}/api/github/import`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
          repo_url: repoUrl.trim(),
          branch: branch.trim() || 'main',
          target_directory: targetDirectory.trim() || undefined
        })
      })
      
      const result = await response.json()
      
      if (!response.ok) {
        throw new Error(result.detail || 'Import fehlgeschlagen')
      }

      setImportResult(result)
      
      toast({
        title: '✅ Repository erfolgreich importiert!',
        description: `${result.repository.name} wurde in deinen Workspace importiert`,
        status: 'success',
        duration: 5000
      })

    } catch (error: any) {
      console.error('Import error:', error)
      
      toast({
        title: 'Import fehlgeschlagen',
        description: error.message || 'Fehler beim Importieren des Repositories',
        status: 'error',
        duration: 7000,
        isClosable: true
      })
    } finally {
      setIsImporting(false)
    }
  }

  const handleClose = () => {
    setRepoUrl('')
    setBranch('main')
    setTargetDirectory('')
    setImportResult(null)
    onClose()
  }

  return (
    <Modal isOpen={isOpen} onClose={handleClose} size="xl">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>📥 Projekt von GitHub importieren</ModalHeader>
        <ModalCloseButton />
        
        <ModalBody>
          {!importResult ? (
            <VStack spacing={4} align="stretch">
              <Alert status="info" borderRadius="md">
                <AlertIcon />
                <Box>
                  <AlertDescription fontSize="sm">
                    Importiere ein bestehendes GitHub-Projekt in deinen Xionimus Workspace, 
                    um es weiterzuentwickeln.
                  </AlertDescription>
                </Box>
              </Alert>

              <FormControl isRequired>
                <FormLabel fontSize="sm">Repository URL</FormLabel>
                <Input
                  placeholder="https://github.com/username/repository"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  size="md"
                  isDisabled={isImporting}
                />
                <Text fontSize="xs" color="gray.500" mt={1}>
                  Beispiel: https://github.com/vercel/next.js
                </Text>
              </FormControl>

              <FormControl>
                <FormLabel fontSize="sm">Branch (optional)</FormLabel>
                <Input
                  placeholder="main"
                  value={branch}
                  onChange={(e) => setBranch(e.target.value)}
                  size="md"
                  isDisabled={isImporting}
                />
                <Text fontSize="xs" color="gray.500" mt={1}>
                  Standard: main (oder master für ältere Repos)
                </Text>
              </FormControl>

              <FormControl>
                <FormLabel fontSize="sm">Zielverzeichnis (optional)</FormLabel>
                <Input
                  placeholder="Automatisch: Repository-Name"
                  value={targetDirectory}
                  onChange={(e) => setTargetDirectory(e.target.value)}
                  size="md"
                  isDisabled={isImporting}
                />
                <Text fontSize="xs" color="gray.500" mt={1}>
                  Leer lassen, um Repository-Namen zu verwenden
                </Text>
              </FormControl>

              <Alert status="warning" borderRadius="md" fontSize="sm">
                <AlertIcon />
                <Box>
                  <Text fontWeight="semibold" mb={1}>Hinweise:</Text>
                  <List spacing={1} fontSize="xs">
                    <ListItem>
                      <ListIcon as={CheckCircleIcon} color="green.500" />
                      Öffentliche Repositories: Kein Token erforderlich
                    </ListItem>
                    <ListItem>
                      <ListIcon as={CheckCircleIcon} color="green.500" />
                      Private Repositories: GitHub Login erforderlich
                    </ListItem>
                    <ListItem>
                      <ListIcon as={WarningIcon} color="orange.500" />
                      Große Repositories (&gt;100MB) können länger dauern
                    </ListItem>
                  </List>
                </Box>
              </Alert>
            </VStack>
          ) : (
            <VStack spacing={4} align="stretch">
              <Alert status="success" borderRadius="md">
                <AlertIcon />
                <Box>
                  <Text fontWeight="semibold">Import erfolgreich!</Text>
                  <Text fontSize="sm">
                    Repository wurde in deinen Workspace importiert
                  </Text>
                </Box>
              </Alert>

              <Box p={4} bg="gray.50" borderRadius="md" borderWidth="1px">
                <VStack align="stretch" spacing={2}>
                  <HStack>
                    <Text fontSize="sm" fontWeight="semibold">Repository:</Text>
                    <Badge colorScheme="blue">
                      {importResult.repository.owner}/{importResult.repository.name}
                    </Badge>
                  </HStack>
                  
                  <HStack>
                    <Text fontSize="sm" fontWeight="semibold">Branch:</Text>
                    <Code fontSize="xs">{importResult.repository.branch}</Code>
                  </HStack>
                  
                  <HStack>
                    <Text fontSize="sm" fontWeight="semibold">Verzeichnis:</Text>
                    <Code fontSize="xs">{importResult.import_details.target_directory}</Code>
                  </HStack>
                  
                  <HStack>
                    <Text fontSize="sm" fontWeight="semibold">Dateien:</Text>
                    <Badge colorScheme="green">{importResult.import_details.total_files}</Badge>
                  </HStack>
                </VStack>
              </Box>

              <Alert status="info" borderRadius="md" fontSize="sm">
                <AlertIcon />
                <Text>
                  Du kannst jetzt mit der Weiterentwicklung beginnen! 
                  Die Dateien sind im Workspace verfügbar.
                </Text>
              </Alert>
            </VStack>
          )}
        </ModalBody>

        <ModalFooter>
          {!importResult ? (
            <>
              <Button variant="ghost" mr={3} onClick={handleClose} isDisabled={isImporting}>
                Abbrechen
              </Button>
              <Button
                colorScheme="blue"
                onClick={handleImport}
                isLoading={isImporting}
                loadingText="Importiere..."
                leftIcon={isImporting ? <Spinner size="sm" /> : undefined}
              >
                {isImporting ? 'Importiere...' : 'Importieren'}
              </Button>
            </>
          ) : (
            <Button colorScheme="blue" onClick={handleClose}>
              Fertig
            </Button>
          )}
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}
