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
  Spinner,
  Select,
  Switch,
  FormHelperText,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  IconButton,
  Divider,
  useDisclosure,
  AlertDialog,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay
} from '@chakra-ui/react'
import { CheckCircleIcon, WarningIcon, DeleteIcon } from '@chakra-ui/icons'
import { useGitHub } from '../contexts/GitHubContext'
import axios from 'axios'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001'

interface GitHubRepo {
  name: string
  full_name: string
  description: string | null
  private: boolean
  url: string
  clone_url: string
  default_branch: string
}

interface GitHubBranch {
  name: string
  protected: boolean
}

interface ImportedProject {
  name: string
  path: string
  file_count: number
  size_bytes: number
  size_mb: number
  branch: string | null
  created_at: string | null
  modified_at: string | null
}

interface GitHubImportDialogProps {
  isOpen: boolean
  onClose: () => void
  sessionId?: string | null  // Pass session ID to auto-activate imported project
}

export const GitHubImportDialog: React.FC<GitHubImportDialogProps> = ({
  isOpen,
  onClose,
  sessionId
}) => {
  // Tab state
  const [activeTab, setActiveTab] = useState(0)
  
  // Mode selection
  const [useAutoMode, setUseAutoMode] = useState(true)
  
  // Auto mode state
  const [repositories, setRepositories] = useState<GitHubRepo[]>([])
  const [selectedRepo, setSelectedRepo] = useState<string>('')
  const [branches, setBranches] = useState<GitHubBranch[]>([])
  const [selectedBranch, setSelectedBranch] = useState<string>('')
  const [isLoadingRepos, setIsLoadingRepos] = useState(false)
  const [isLoadingBranches, setIsLoadingBranches] = useState(false)
  
  // Manual mode state
  const [repoUrl, setRepoUrl] = useState('')
  const [branch, setBranch] = useState('main')
  
  // Common state
  const [targetDirectory, setTargetDirectory] = useState('')
  const [isImporting, setIsImporting] = useState(false)
  const [importResult, setImportResult] = useState<any>(null)
  
  // Repository management state
  const [importedProjects, setImportedProjects] = useState<ImportedProject[]>([])
  const [isLoadingProjects, setIsLoadingProjects] = useState(false)
  const [isDeletingProject, setIsDeletingProject] = useState(false)
  const [projectToDelete, setProjectToDelete] = useState<string | null>(null)
  const [conflictingProject, setConflictingProject] = useState<string | null>(null)
  
  // Alert dialog for delete confirmation
  const { isOpen: isDeleteAlertOpen, onOpen: onDeleteAlertOpen, onClose: onDeleteAlertClose } = useDisclosure()
  const cancelRef = React.useRef<HTMLButtonElement>(null)
  
  const github = useGitHub()
  const toast = useToast()

  // Load repositories when dialog opens in auto mode
  useEffect(() => {
    if (isOpen && useAutoMode) {
      loadRepositories()
    }
  }, [isOpen, useAutoMode])

  // Load branches when repository is selected
  useEffect(() => {
    if (selectedRepo && useAutoMode) {
      loadBranches()
    }
  }, [selectedRepo])

  const loadRepositories = async () => {
    setIsLoadingRepos(true)
    try {
      const token = localStorage.getItem('xionimus_token')
      const response = await axios.get(`${BACKEND_URL}/api/github-pat/repositories`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      setRepositories(response.data)
    } catch (error: any) {
      console.error('Failed to load repositories:', error)
      // Don't close dialog on error - just show toast
      toast({
        title: 'GitHub nicht verbunden',
        description: 'Bitte konfigurieren Sie Ihren GitHub Personal Access Token in den Einstellungen.',
        status: 'warning',
        duration: 5000,
        isClosable: true
      })
      // Set empty array so dialog stays open
      setRepositories([])
    } finally {
      setIsLoadingRepos(false)
    }
  }

  const loadBranches = async () => {
    if (!selectedRepo) return
    
    setIsLoadingBranches(true)
    setBranches([])
    setSelectedBranch('')
    
    try {
      const token = localStorage.getItem('xionimus_token')
      const [owner, repo] = selectedRepo.split('/')
      const response = await axios.get(
        `${BACKEND_URL}/api/github-pat/repositories/${owner}/${repo}/branches`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      )
      setBranches(response.data)
      
      // Auto-select default branch if available
      const selectedRepoData = repositories.find(r => r.full_name === selectedRepo)
      if (selectedRepoData?.default_branch) {
        setSelectedBranch(selectedRepoData.default_branch)
      } else if (response.data.length > 0) {
        setSelectedBranch(response.data[0].name)
      }
    } catch (error: any) {
      console.error('Failed to load branches:', error)
      toast({
        title: 'Fehler beim Laden',
        description: 'Branches konnten nicht geladen werden',
        status: 'error',
        duration: 3000
      })
    } finally {
      setIsLoadingBranches(false)
    }
  }

  // Load imported projects
  const loadImportedProjects = async () => {
    setIsLoadingProjects(true)
    try {
      const response = await axios.get(`${BACKEND_URL}/api/github/import/status`)
      setImportedProjects(response.data.existing_projects || [])
    } catch (error: any) {
      console.error('Failed to load imported projects:', error)
      toast({
        title: 'Fehler beim Laden',
        description: 'Projekte konnten nicht geladen werden',
        status: 'error',
        duration: 3000
      })
    } finally {
      setIsLoadingProjects(false)
    }
  }

  // Delete project
  const handleDeleteProject = async (projectName: string) => {
    setIsDeletingProject(true)
    try {
      const token = localStorage.getItem('xionimus_token')
      const response = await axios.delete(
        `${BACKEND_URL}/api/github/import/${projectName}`,
        {
          headers: token ? {
            'Authorization': `Bearer ${token}`
          } : {}
        }
      )
      
      toast({
        title: '✅ Gelöscht',
        description: response.data.message || `Repository '${projectName}' wurde gelöscht`,
        status: 'success',
        duration: 5000
      })
      
      // Reload projects list
      await loadImportedProjects()
      
      // If this was the conflicting project, clear the conflict
      if (conflictingProject === projectName) {
        setConflictingProject(null)
      }
      
    } catch (error: any) {
      console.error('Failed to delete project:', error)
      const errorDetail = error.response?.data?.detail || 'Löschen fehlgeschlagen'
      
      toast({
        title: 'Löschen fehlgeschlagen',
        description: errorDetail,
        status: 'error',
        duration: 7000,
        isClosable: true
      })
    } finally {
      setIsDeletingProject(false)
      onDeleteAlertClose()
      setProjectToDelete(null)
    }
  }

  // Confirm delete
  const confirmDelete = (projectName: string) => {
    setProjectToDelete(projectName)
    onDeleteAlertOpen()
  }

  // Load projects when dialog opens or when switching to "Meine Repos" tab
  useEffect(() => {
    if (isOpen) {
      loadImportedProjects()
    }
  }, [isOpen, activeTab])

  const handleImport = async () => {
    // Determine repo URL and branch based on mode
    let finalRepoUrl: string
    let finalBranch: string
    
    if (useAutoMode) {
      if (!selectedRepo) {
        toast({
          title: 'Repository auswählen',
          description: 'Bitte wähle ein Repository aus',
          status: 'warning',
          duration: 3000
        })
        return
      }
      
      if (!selectedBranch) {
        toast({
          title: 'Branch auswählen',
          description: 'Bitte wähle einen Branch aus',
          status: 'warning',
          duration: 3000
        })
        return
      }
      
      // Construct repo URL from full_name
      finalRepoUrl = `https://github.com/${selectedRepo}`
      finalBranch = selectedBranch
    } else {
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
      
      finalRepoUrl = repoUrl.trim()
      finalBranch = branch.trim() || 'main'
    }

    setIsImporting(true)
    setImportResult(null)

    try {
      // Use direct API call (supports both authenticated and public repos)
      const token = localStorage.getItem('xionimus_token')
      const response = await axios.post(
        `${BACKEND_URL}/api/github/import`,
        {
          repo_url: finalRepoUrl,
          branch: finalBranch,
          target_directory: targetDirectory.trim() || undefined,
          session_id: sessionId || undefined  // Auto-activate project for current session
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

      setImportResult(result)
      
      // Show success message with project activation status
      const description = result.project_activated
        ? `${result.repository.name} wurde importiert und ist jetzt für KI-Agenten verfügbar! 🤖`
        : `${result.repository.name} wurde in deinen Workspace importiert`
      
      toast({
        title: '✅ Repository erfolgreich importiert!',
        description: description,
        status: 'success',
        duration: 6000
      })

    } catch (error: any) {
      console.error('Import error:', error)
      
      // Extract detailed error message from backend response
      const errorDetail = error.response?.data?.detail || error.message || 'Fehler beim Importieren des Repositories'
      
      // Check if it's a directory conflict error
      if (errorDetail.includes('existiert bereits')) {
        // Extract directory name from error message
        const match = errorDetail.match(/Verzeichnis '([^']+)' existiert bereits/)
        if (match && match[1]) {
          setConflictingProject(match[1])
        }
      }
      
      toast({
        title: 'Import fehlgeschlagen',
        description: errorDetail,
        status: 'error',
        duration: 9000,
        isClosable: true
      })
    } finally {
      setIsImporting(false)
      // Reload projects to show updated list
      await loadImportedProjects()
    }
  }

  const handleClose = () => {
    setRepoUrl('')
    setBranch('main')
    setTargetDirectory('')
    setImportResult(null)
    setSelectedRepo('')
    setSelectedBranch('')
    setRepositories([])
    setBranches([])
    setConflictingProject(null)
    setActiveTab(0)
    onClose()
  }
  
  // Handle delete conflicting project (local copy only)
  const handleDeleteConflictingProject = async () => {
    if (conflictingProject) {
      await handleDeleteProject(conflictingProject)
      setConflictingProject(null)
    }
  }

  return (
    <>
      {/* Delete Confirmation Dialog */}
      <AlertDialog
        isOpen={isDeleteAlertOpen}
        leastDestructiveRef={cancelRef}
        onClose={onDeleteAlertClose}
      >
        <AlertDialogOverlay>
          <AlertDialogContent>
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              🗑️ Lokale Kopie löschen
            </AlertDialogHeader>

            <AlertDialogBody>
              <VStack align="start" spacing={3}>
                <Text>
                  Möchtest du die lokale Kopie von <strong>{projectToDelete}</strong> aus dem Workspace löschen?
                </Text>
                <Alert status="info" fontSize="sm">
                  <AlertIcon />
                  <Box>
                    <Text fontWeight="semibold">⚠️ Goldene Regel:</Text>
                    <Text>Nur die lokale Kopie in Xionimus wird gelöscht. Dein Repository auf GitHub bleibt vollständig unberührt!</Text>
                  </Box>
                </Alert>
              </VStack>
            </AlertDialogBody>

            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onDeleteAlertClose}>
                Abbrechen
              </Button>
              <Button
                colorScheme="red"
                onClick={() => projectToDelete && handleDeleteProject(projectToDelete)}
                ml={3}
                isLoading={isDeletingProject}
              >
                Löschen
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>

      {/* Main Dialog */}
      <Modal isOpen={isOpen} onClose={handleClose} size="xl">
        <ModalOverlay />
        <ModalContent maxW="900px">
          <ModalHeader>
            <HStack justify="space-between">
              <Text>📥 GitHub Import & Verwaltung</Text>
              <Button 
                size="sm" 
                variant="ghost" 
                onClick={() => setActiveTab(activeTab === 0 ? 1 : 0)}
              >
                {activeTab === 0 ? '📦 Meine Repos' : '➕ Neues Repo'}
              </Button>
            </HStack>
          </ModalHeader>
          <ModalCloseButton />
          
          <ModalBody>
            {activeTab === 0 ? (
              // Tab 1: Import New Repo
              !importResult ? (
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

              {/* Mode Switch */}
              <FormControl display="flex" alignItems="center">
                <FormLabel htmlFor="auto-mode" mb="0" fontSize="sm">
                  Automatische Auswahl
                </FormLabel>
                <Switch 
                  id="auto-mode" 
                  isChecked={useAutoMode}
                  onChange={(e) => setUseAutoMode(e.target.checked)}
                  colorScheme="blue"
                />
                <FormHelperText ml={3} mt={0} fontSize="xs" color="gray.500">
                  {useAutoMode ? 'Repos aus GitHub laden' : 'Manuelle URL-Eingabe'}
                </FormHelperText>
              </FormControl>

              {/* Auto Mode - Repository & Branch Selection */}
              {useAutoMode ? (
                <>
                  <FormControl isRequired>
                    <FormLabel fontSize="sm">Repository auswählen</FormLabel>
                    {isLoadingRepos ? (
                      <HStack spacing={2} p={2} bg="gray.50" borderRadius="md">
                        <Spinner size="sm" />
                        <Text fontSize="sm" color="gray.600">Lade Repositories...</Text>
                      </HStack>
                    ) : repositories.length > 0 ? (
                      <Select
                        placeholder="Repository auswählen..."
                        value={selectedRepo}
                        onChange={(e) => setSelectedRepo(e.target.value)}
                        size="md"
                      >
                        {repositories.map((repo) => (
                          <option key={repo.full_name} value={repo.full_name}>
                            {repo.full_name} {repo.private ? '🔒' : '🌐'}
                          </option>
                        ))}
                      </Select>
                    ) : (
                      <Alert status="warning" fontSize="sm">
                        <AlertIcon />
                        Keine Repositories gefunden. Bitte GitHub PAT in Settings hinterlegen.
                      </Alert>
                    )}
                    {selectedRepo && (
                      <FormHelperText fontSize="xs">
                        {repositories.find(r => r.full_name === selectedRepo)?.description || 'Kein Beschreibung'}
                      </FormHelperText>
                    )}
                  </FormControl>

                  <FormControl isRequired isDisabled={!selectedRepo}>
                    <FormLabel fontSize="sm">Branch auswählen</FormLabel>
                    {isLoadingBranches ? (
                      <HStack spacing={2} p={2} bg="gray.50" borderRadius="md">
                        <Spinner size="sm" />
                        <Text fontSize="sm" color="gray.600">Lade Branches...</Text>
                      </HStack>
                    ) : branches.length > 0 ? (
                      <Select
                        placeholder="Branch auswählen..."
                        value={selectedBranch}
                        onChange={(e) => setSelectedBranch(e.target.value)}
                        size="md"
                      >
                        {branches.map((branch) => (
                          <option key={branch.name} value={branch.name}>
                            {branch.name} {branch.protected ? '🔐' : ''}
                          </option>
                        ))}
                      </Select>
                    ) : selectedRepo ? (
                      <Alert status="info" fontSize="sm">
                        <AlertIcon />
                        Wähle zuerst ein Repository aus
                      </Alert>
                    ) : (
                      <Select placeholder="Zuerst Repository wählen" isDisabled size="md" />
                    )}
                  </FormControl>
                </>
              ) : (
                /* Manual Mode - URL & Branch Input */
                <>
                  <FormControl isRequired>
                    <FormLabel fontSize="sm">Repository URL</FormLabel>
                    <Input
                      placeholder="https://github.com/username/repository"
                      value={repoUrl}
                      onChange={(e) => setRepoUrl(e.target.value)}
                      size="md"
                    />
                  </FormControl>

                  <FormControl>
                    <FormLabel fontSize="sm">Branch</FormLabel>
                    <Input
                      placeholder="main"
                      value={branch}
                      onChange={(e) => setBranch(e.target.value)}
                      size="md"
                    />
                  </FormControl>
                </>
              )}

              {/* Target Directory - Common for both modes */}
              <FormControl>
                <FormLabel fontSize="sm">Zielverzeichnis (optional)</FormLabel>
                <Input
                  placeholder="Leer lassen für Standard"
                  value={targetDirectory}
                  onChange={(e) => setTargetDirectory(e.target.value)}
                  size="md"
                />
              </FormControl>
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
                <VStack align="stretch" spacing={3}>
                  <HStack>
                    <Text fontSize="sm" fontWeight="semibold" color="gray.700">Repository:</Text>
                    <Badge colorScheme="purple" fontSize="sm" px={3} py={1}>
                      {importResult.repository.owner}/{importResult.repository.name}
                    </Badge>
                  </HStack>
                  
                  <HStack>
                    <Text fontSize="sm" fontWeight="semibold" color="gray.700">Branch:</Text>
                    <Badge colorScheme="green" fontSize="sm" px={3} py={1}>
                      {importResult.repository.branch}
                    </Badge>
                  </HStack>
                  
                  <HStack>
                    <Text fontSize="sm" fontWeight="semibold" color="gray.700">Verzeichnis:</Text>
                    <Badge colorScheme="orange" fontSize="sm" px={3} py={1}>
                      {importResult.import_details.target_directory}
                    </Badge>
                  </HStack>
                  
                  <HStack>
                    <Text fontSize="sm" fontWeight="semibold" color="gray.700">Dateien:</Text>
                    <Badge colorScheme="blue" fontSize="sm" px={3} py={1}>
                      {importResult.import_details.total_files}
                    </Badge>
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
          )
            ) : (
              // Tab 2: Manage Repositories
              <VStack spacing={4} align="stretch">
                <Alert status="info" borderRadius="md">
                  <AlertIcon />
                  <Box>
                    <AlertDescription fontSize="sm">
                      Verwalte deine importierten GitHub-Projekte im Workspace
                    </AlertDescription>
                  </Box>
                </Alert>

                {/* Conflicting Project Warning */}
                {conflictingProject && (
                  <Alert status="warning" borderRadius="md">
                    <AlertIcon />
                    <Box flex="1">
                      <Text fontSize="sm" fontWeight="semibold">⚠️ Import-Konflikt</Text>
                      <Text fontSize="sm">
                        Eine lokale Kopie von '{conflictingProject}' existiert bereits im Workspace.
                      </Text>
                      <Text fontSize="xs" color="gray.600" mt={1}>
                        Lösche die lokale Kopie, um erneut importieren zu können.
                      </Text>
                    </Box>
                    <Button
                      size="sm"
                      colorScheme="red"
                      onClick={() => confirmDelete(conflictingProject)}
                      leftIcon={<DeleteIcon />}
                    >
                      Lokale Kopie löschen
                    </Button>
                  </Alert>
                )}

                {/* Projects List */}
                <Box>
                  <HStack justify="space-between" mb={3}>
                    <Text fontWeight="semibold" fontSize="lg">
                      📦 Meine Repositories ({importedProjects.length})
                    </Text>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={loadImportedProjects}
                      isLoading={isLoadingProjects}
                    >
                      🔄 Aktualisieren
                    </Button>
                  </HStack>

                  {isLoadingProjects ? (
                    <HStack spacing={3} p={4} justify="center">
                      <Spinner size="md" color="blue.500" />
                      <Text color="gray.600">Lade Repositories...</Text>
                    </HStack>
                  ) : importedProjects.length === 0 ? (
                    <Box p={8} textAlign="center" bg="gray.50" borderRadius="md">
                      <Text fontSize="3xl" mb={2}>📭</Text>
                      <Text color="gray.600" fontSize="sm">
                        Keine Repositories gefunden
                      </Text>
                      <Button
                        size="sm"
                        colorScheme="blue"
                        mt={3}
                        onClick={() => setActiveTab(0)}
                      >
                        Erstes Repo importieren
                      </Button>
                    </Box>
                  ) : (
                    <VStack spacing={3} align="stretch">
                      {importedProjects.map((project) => (
                        <Box
                          key={project.name}
                          p={4}
                          bg="white"
                          borderRadius="md"
                          borderWidth="1px"
                          borderColor="gray.200"
                          _hover={{ borderColor: 'blue.300', boxShadow: 'sm' }}
                        >
                          <HStack justify="space-between" align="start">
                            <VStack align="start" spacing={2} flex={1}>
                              <HStack>
                                <Text fontWeight="bold" fontSize="md" color="purple.600">
                                  📁 {project.name}
                                </Text>
                                {project.branch && (
                                  <Badge colorScheme="green" fontSize="xs">
                                    {project.branch}
                                  </Badge>
                                )}
                              </HStack>
                              
                              <HStack spacing={4} fontSize="sm" color="gray.600">
                                <HStack>
                                  <Text>📄</Text>
                                  <Text>{project.file_count} Dateien</Text>
                                </HStack>
                                <HStack>
                                  <Text>💾</Text>
                                  <Text>{project.size_mb} MB</Text>
                                </HStack>
                              </HStack>
                              
                              {project.created_at && (
                                <Text fontSize="xs" color="gray.500">
                                  Importiert: {new Date(project.created_at).toLocaleString('de-DE')}
                                </Text>
                              )}
                            </VStack>
                            
                            <IconButton
                              aria-label="Lokale Kopie löschen"
                              icon={<DeleteIcon />}
                              colorScheme="red"
                              variant="ghost"
                              size="sm"
                              onClick={() => confirmDelete(project.name)}
                              isDisabled={isDeletingProject}
                            />
                          </HStack>
                        </Box>
                      ))}
                    </VStack>
                  )}
                </Box>
              </VStack>
            )}
          </ModalBody>

          <ModalFooter>
            {activeTab === 0 ? (
              !importResult ? (
                <>
                  {conflictingProject && (
                    <Button
                      colorScheme="red"
                      mr={3}
                      onClick={handleDeleteConflictingProject}
                      leftIcon={<DeleteIcon />}
                      isLoading={isDeletingProject}
                    >
                      Lokale Kopie löschen
                    </Button>
                  )}
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
                <>
                  <Button variant="ghost" mr={3} onClick={() => {
                    setImportResult(null)
                    setActiveTab(0)
                  }}>
                    Weiteres Repo importieren
                  </Button>
                  <Button colorScheme="blue" onClick={handleClose}>
                    Fertig
                  </Button>
                </>
              )
            ) : (
              <Button colorScheme="blue" onClick={handleClose}>
                Schließen
              </Button>
            )}
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  )
}
