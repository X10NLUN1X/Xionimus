import React, { useState, useCallback, useEffect } from 'react'
import {
  Box,
  Text,
  Heading,
  VStack,
  HStack,
  useColorModeValue,
  Spinner,
  Alert,
  AlertIcon,
  Button,
  useToast,
  Divider,
  useBreakpointValue,
  IconButton,
  Drawer,
  DrawerBody,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  DrawerHeader,
  useDisclosure
} from '@chakra-ui/react'
import { HamburgerIcon } from '@chakra-ui/icons'
import { FileTree } from '../components/FileTree/FileTree'
import { MonacoEditor } from '../components/Editor/MonacoEditor'
import { FileTreeItem } from '../components/FileTree/FileTreeNode'
import { LoadingSpinner } from '../components/Loading/LoadingSpinner'
import axios from 'axios'

export const WorkspacePage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<FileTreeItem | null>(null)
  const [fileContent, setFileContent] = useState('')
  const [loading, setLoading] = useState(false)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [sidebarWidth, setSidebarWidth] = useState(300)
  
  // Mobile drawer state
  const { isOpen, onOpen, onClose } = useDisclosure()
  const isMobile = useBreakpointValue({ base: true, lg: false })

  const toast = useToast()
  const bg = useColorModeValue('#0A0A0A', '#000000')
  const borderColor = useColorModeValue('#333333', '#444444')
  const backendUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'

  const handleFileSelect = useCallback(async (file: FileTreeItem) => {
    if (file.type !== 'file') return

    // Check for unsaved changes
    if (hasUnsavedChanges) {
      const confirmDiscard = window.confirm(
        'You have unsaved changes. Do you want to discard them?'
      )
      if (!confirmDiscard) return
    }

    // Close mobile drawer when file is selected
    if (isMobile) {
      onClose()
    }

    setLoading(true)
    try {
      const response = await axios.get(
        `${backendUrl}/api/workspace/file/${file.path}`
      )
      
      setSelectedFile(file)
      setFileContent(response.data.content || '')
      setHasUnsavedChanges(false)
      
      toast({
        title: 'File loaded',
        description: `Opened ${file.name}`,
        status: 'success',
        duration: 2000,
        isClosable: true,
      })
    } catch (err: any) {
      toast({
        title: 'Error loading file',
        description: err.response?.data?.detail || 'Failed to load file',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setLoading(false)
    }
  }, [backendUrl, hasUnsavedChanges, toast, isMobile, onClose])

  const handleContentChange = useCallback((newContent: string | undefined) => {
    if (newContent !== undefined) {
      setFileContent(newContent)
      setHasUnsavedChanges(true)
    }
  }, [])

  const handleSaveFile = useCallback(async (content: string) => {
    if (!selectedFile) return

    try {
      await axios.post(`${backendUrl}/api/workspace/file/${selectedFile.path}`, {
        content
      })

      setHasUnsavedChanges(false)
      
      // Update file size in selected file info
      setSelectedFile({
        ...selectedFile,
        size: new Blob([content]).size,
        modified: new Date().toISOString()
      })
    } catch (err: any) {
      toast({
        title: 'Error saving file',
        description: err.response?.data?.detail || 'Failed to save file',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    }
  }, [selectedFile, backendUrl, toast])

  // Auto-load welcome file on component mount
  useEffect(() => {
    if (!selectedFile && !loading) {
      const welcomeFile = {
        name: 'welcome.md',
        path: 'welcome.md',
        type: 'file' as const,
        modified: new Date().toISOString(),
      }
      
      const welcomeContent = `# Welcome to Xionimus AI Workspace 🚀

## Getting Started
This is your development environment with Monaco Editor integration.

### Features Available:
- **Monaco Editor**: VS Code-like editing experience
- **File Tree**: Navigate and manage your workspace files
- **Multi-language Support**: JavaScript, TypeScript, Python, and more
- **Auto-save**: Your changes are automatically saved
- **Syntax Highlighting**: Full syntax support for 20+ languages

### Quick Actions:
- **Ctrl+S**: Manual save
- **Ctrl+N**: Create new file  
- **Select files** from the tree on the left to edit them

### Next Steps:
1. Explore the file tree on the left
2. Create new files and directories
3. Start coding with full IntelliSense support

---
*Happy coding with Xionimus AI! 💻*`

      setSelectedFile(welcomeFile)
      setFileContent(welcomeContent)
      setHasUnsavedChanges(false)
    }
  }, [selectedFile, loading])

  const handleCreateNewFile = () => {
    setSelectedFile({
      name: 'untitled.txt',
      path: 'untitled.txt',
      type: 'file',
      modified: new Date().toISOString(),
    })
    setFileContent('')
    setHasUnsavedChanges(true)
  }

  return (
    <Box h="100vh" bg={bg} overflow="hidden">
      <VStack spacing={0} align="stretch" h="100%">
        {/* Header */}
        <Box p={{ base: 3, md: 4 }} borderBottom="1px solid" borderColor={borderColor}>
          <HStack justify="space-between" align="center">
            <HStack spacing={3}>
              {isMobile && (
                <IconButton
                  aria-label="Open file tree"
                  icon={<HamburgerIcon />}
                  onClick={onOpen}
                  size="sm"
                  variant="ghost"
                />
              )}
              <VStack align="start" spacing={1}>
                <Heading size={{ base: 'md', md: 'lg' }}>Workspace</Heading>
                <Text color="gray.400" fontSize={{ base: 'xs', md: 'sm' }}>
                  Code editor with Monaco and file management
                </Text>
              </VStack>
            </HStack>
            <Button
              size="sm"
              colorScheme="blue"
              onClick={handleCreateNewFile}
            >
              New File
            </Button>
          </HStack>
        </Box>

        {/* Main Content */}
        <HStack spacing={0} flex={1} align="stretch">
          {/* Desktop Sidebar - File Tree */}
          {!isMobile && (
            <>
              <Box
                w={`${sidebarWidth}px`}
                borderRight="1px solid"
                borderColor={borderColor}
                overflowY="auto"
                flexShrink={0}
              >
                <FileTree
                  onFileSelect={handleFileSelect}
                  selectedFile={selectedFile || undefined}
                />
              </Box>

              {/* Resize Handle */}
              <Box
                w="4px"
                bg={borderColor}
                cursor="col-resize"
                _hover={{ bg: 'blue.500' }}
                onMouseDown={(e) => {
                  const startX = e.clientX
                  const startWidth = sidebarWidth

                  const handleMouseMove = (e: MouseEvent) => {
                    const newWidth = Math.max(200, Math.min(600, startWidth + (e.clientX - startX)))
                    setSidebarWidth(newWidth)
                  }

                  const handleMouseUp = () => {
                    document.removeEventListener('mousemove', handleMouseMove)
                    document.removeEventListener('mouseup', handleMouseUp)
                  }

                  document.addEventListener('mousemove', handleMouseMove)
                  document.addEventListener('mouseup', handleMouseUp)
                }}
              />
            </>
          )}

          {/* Mobile Drawer - File Tree */}
          <Drawer isOpen={isOpen} placement="left" onClose={onClose} size="full">
            <DrawerOverlay />
            <DrawerContent bg={bg}>
              <DrawerCloseButton />
              <DrawerHeader borderBottomWidth="1px" borderColor={borderColor}>
                File Tree
              </DrawerHeader>
              <DrawerBody p={0}>
                <FileTree
                  onFileSelect={handleFileSelect}
                  selectedFile={selectedFile || undefined}
                />
              </DrawerBody>
            </DrawerContent>
          </Drawer>

          {/* Editor Area */}
          <Box flex={1} overflow="hidden">
            {loading ? (
              <LoadingSpinner message="Loading file..." />
            ) : selectedFile ? (
              <MonacoEditor
                value={fileContent}
                onChange={handleContentChange}
                onSave={handleSaveFile}
                language="typescript"
                path={selectedFile.name}
                height="100%"
              />
            ) : (
              <Box
                display="flex"
                alignItems="center"
                justifyContent="center"
                h="100%"
                color="gray.500"
                p={{ base: 4, md: 0 }}
              >
                <VStack spacing={4} textAlign="center">
                  <Heading size={{ base: 'sm', md: 'md' }} color="gray.400">
                    Welcome to Workspace
                  </Heading>
                  <VStack spacing={2}>
                    <Text fontSize={{ base: 'sm', md: 'md' }}>
                      {isMobile ? 'Tap the menu icon to browse files' : 'Select a file from the sidebar to start editing'}
                    </Text>
                    <Text fontSize={{ base: 'xs', md: 'sm' }}>or create a new file to get started</Text>
                  </VStack>
                  <Button
                    colorScheme="blue"
                    variant="outline"
                    onClick={handleCreateNewFile}
                    size={{ base: 'sm', md: 'md' }}
                  >
                    Create New File
                  </Button>
                </VStack>
              </Box>
            )}
          </Box>
        </HStack>

        {/* Status Bar */}
        {selectedFile && (
          <Box
            p={2}
            borderTop="1px solid"
            borderColor={borderColor}
            bg={useColorModeValue('gray.100', 'gray.800')}
          >
            <HStack 
              spacing={{ base: 2, md: 4 }} 
              fontSize={{ base: 'xs', md: 'sm' }} 
              color="gray.600" 
              flexWrap="wrap"
            >
              <Text isTruncated maxW={{ base: '120px', md: 'none' }}>{selectedFile.name}</Text>
              <Divider orientation="vertical" h="4" display={{ base: 'none', md: 'block' }} />
              <Text>
                {selectedFile.size 
                  ? `${(selectedFile.size / 1024).toFixed(1)} KB`
                  : 'New file'
                }
              </Text>
              <Divider orientation="vertical" h="4" display={{ base: 'none', md: 'block' }} />
              <Text display={{ base: 'none', md: 'block' }}>
                {selectedFile.extension || 'Plain text'}
              </Text>
              {hasUnsavedChanges && (
                <>
                  <Divider orientation="vertical" h="4" />
                  <Text color={useColorModeValue('#0066aa', '#0088cc')}>● Unsaved changes</Text>
                </>
              )}
            </HStack>
          </Box>
        )}
      </VStack>
    </Box>
  )
}