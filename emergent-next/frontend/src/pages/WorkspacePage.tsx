import React, { useState, useCallback } from 'react'
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
  ResizeObserver,
} from '@chakra-ui/react'
import { FileTree } from '../components/FileTree/FileTree'
import { MonacoEditor } from '../components/Editor/MonacoEditor'
import { FileTreeItem } from '../components/FileTree/FileTreeNode'
import axios from 'axios'

export const WorkspacePage: React.FC = () => {
  const [selectedFile, setSelectedFile] = useState<FileTreeItem | null>(null)
  const [fileContent, setFileContent] = useState('')
  const [loading, setLoading] = useState(false)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [sidebarWidth, setSidebarWidth] = useState(300)

  const toast = useToast()
  const bg = useColorModeValue('#0A0A0A', '#000000')
  const borderColor = useColorModeValue('#333333', '#444444')
  const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8002'

  const handleFileSelect = useCallback(async (file: FileTreeItem) => {
    if (file.type !== 'file') return

    // Check for unsaved changes
    if (hasUnsavedChanges) {
      const confirmDiscard = window.confirm(
        'You have unsaved changes. Do you want to discard them?'
      )
      if (!confirmDiscard) return
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
  }, [backendUrl, hasUnsavedChanges, toast])

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
        <Box p={4} borderBottom="1px solid" borderColor={borderColor}>
          <HStack justify="space-between" align="center">
            <VStack align="start" spacing={1}>
              <Heading size="lg">Workspace</Heading>
              <Text color="gray.400" fontSize="sm">
                Code editor with Monaco and file management
              </Text>
            </VStack>
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
          {/* Sidebar - File Tree */}
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

          {/* Editor Area */}
          <Box flex={1} overflow="hidden">
            {loading ? (
              <Box
                display="flex"
                alignItems="center"
                justifyContent="center"
                h="100%"
              >
                <VStack spacing={4}>
                  <Spinner size="lg" />
                  <Text>Loading file...</Text>
                </VStack>
              </Box>
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
              >
                <VStack spacing={4} textAlign="center">
                  <Heading size="md" color="gray.400">
                    Welcome to Workspace
                  </Heading>
                  <VStack spacing={2}>
                    <Text>Select a file from the sidebar to start editing</Text>
                    <Text fontSize="sm">or create a new file to get started</Text>
                  </VStack>
                  <Button
                    colorScheme="blue"
                    variant="outline"
                    onClick={handleCreateNewFile}
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
            <HStack spacing={4} fontSize="sm" color="gray.600">
              <Text>{selectedFile.name}</Text>
              <Divider orientation="vertical" h="4" />
              <Text>
                {selectedFile.size 
                  ? `${(selectedFile.size / 1024).toFixed(1)} KB`
                  : 'New file'
                }
              </Text>
              <Divider orientation="vertical" h="4" />
              <Text>
                {selectedFile.extension || 'Plain text'}
              </Text>
              {hasUnsavedChanges && (
                <>
                  <Divider orientation="vertical" h="4" />
                  <Text color="orange.500">● Unsaved changes</Text>
                </>
              )}
            </HStack>
          </Box>
        )}
      </VStack>
    </Box>
  )
}