import React, { useState, useEffect, useCallback } from 'react'
import {
  Box,
  VStack,
  HStack,
  Text,
  IconButton,
  Input,
  Button,
  useColorModeValue,
  Spinner,
  Alert,
  AlertIcon,
  useToast,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
} from '@chakra-ui/react'
import {
  AddIcon,
  RefreshIcon,
  ChevronRightIcon,
} from '@chakra-ui/icons'
import { FaFolder } from 'react-icons/fa'
import { FileTreeNode, FileTreeItem } from './FileTreeNode'
import axios from 'axios'

interface FileTreeProps {
  onFileSelect: (file: FileTreeItem) => void
  selectedFile?: FileTreeItem
  className?: string
}

export const FileTree: React.FC<FileTreeProps> = ({
  onFileSelect,
  selectedFile,
  className,
}) => {
  const [files, setFiles] = useState<FileTreeItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [expandedPaths, setExpandedPaths] = useState<Set<string>>(new Set())
  const [currentPath, setCurrentPath] = useState('')
  const [isCreatingFile, setIsCreatingFile] = useState(false)
  const [isCreatingFolder, setIsCreatingFolder] = useState(false)
  const [newItemName, setNewItemName] = useState('')
  const [newItemParent, setNewItemParent] = useState('')

  const toast = useToast()
  const borderColor = useColorModeValue('gray.200', 'gray.700')
  const bg = useColorModeValue('white', 'gray.800')

  const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8002'

  const fetchWorkspaceTree = useCallback(async (path: string = '') => {
    try {
      setLoading(true)
      setError(null)
      
      const response = await axios.get(`${backendUrl}/api/workspace/tree`, {
        params: { path },
      })
      
      const items: FileTreeItem[] = response.data.map((item: any) => ({
        name: item.name,
        path: item.path,
        type: item.type,
        size: item.size,
        modified: item.modified,
        extension: item.extension,
      }))
      
      setFiles(items)
    } catch (err: any) {
      console.error('Failed to fetch workspace tree:', err)
      setError(err.response?.data?.detail || 'Failed to load workspace')
    } finally {
      setLoading(false)
    }
  }, [backendUrl])

  const loadDirectoryChildren = async (dirPath: string): Promise<FileTreeItem[]> => {
    try {
      const response = await axios.get(`${backendUrl}/api/workspace/tree`, {
        params: { path: dirPath },
      })
      
      return response.data.map((item: any) => ({
        name: item.name,
        path: item.path,
        type: item.type,
        size: item.size,
        modified: item.modified,
        extension: item.extension,
      }))
    } catch (err) {
      console.error('Failed to load directory children:', err)
      return []
    }
  }

  useEffect(() => {
    fetchWorkspaceTree(currentPath)
  }, [fetchWorkspaceTree, currentPath])

  const handleFileSelect = async (item: FileTreeItem) => {
    if (item.type === 'file') {
      onFileSelect(item)
    } else {
      // Load children for directory if not already loaded
      if (!item.children) {
        const children = await loadDirectoryChildren(item.path)
        item.children = children
      }
    }
  }

  const handleToggleExpand = async (path: string) => {
    const newExpandedPaths = new Set(expandedPaths)
    
    if (expandedPaths.has(path)) {
      newExpandedPaths.delete(path)
    } else {
      newExpandedPaths.add(path)
      
      // Load children if not loaded
      const targetItem = findItemByPath(files, path)
      if (targetItem && targetItem.type === 'directory' && !targetItem.children) {
        const children = await loadDirectoryChildren(path)
        targetItem.children = children
        setFiles([...files]) // Trigger re-render
      }
    }
    
    setExpandedPaths(newExpandedPaths)
  }

  const findItemByPath = (items: FileTreeItem[], path: string): FileTreeItem | null => {
    for (const item of items) {
      if (item.path === path) return item
      if (item.children) {
        const found = findItemByPath(item.children, path)
        if (found) return found
      }
    }
    return null
  }

  const handleCreateFile = (parentPath: string) => {
    setNewItemParent(parentPath)
    setIsCreatingFile(true)
    setNewItemName('')
  }

  const handleCreateFolder = (parentPath: string) => {
    setNewItemParent(parentPath)
    setIsCreatingFolder(true)
    setNewItemName('')
  }

  const confirmCreateFile = async () => {
    if (!newItemName.trim()) return

    try {
      const filePath = newItemParent ? `${newItemParent}/${newItemName}` : newItemName
      
      await axios.post(`${backendUrl}/api/workspace/file/${filePath}`, {
        content: ''
      })
      
      toast({
        title: 'File created',
        description: `Created ${newItemName}`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
      
      fetchWorkspaceTree(currentPath)
    } catch (err: any) {
      toast({
        title: 'Error creating file',
        description: err.response?.data?.detail || 'Failed to create file',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setIsCreatingFile(false)
      setNewItemName('')
    }
  }

  const confirmCreateFolder = async () => {
    if (!newItemName.trim()) return

    try {
      const folderPath = newItemParent ? `${newItemParent}/${newItemName}` : newItemName
      
      await axios.post(`${backendUrl}/api/workspace/directory`, {
        path: folderPath
      })
      
      toast({
        title: 'Folder created',
        description: `Created ${newItemName}`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
      
      fetchWorkspaceTree(currentPath)
    } catch (err: any) {
      toast({
        title: 'Error creating folder',
        description: err.response?.data?.detail || 'Failed to create folder',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setIsCreatingFolder(false)
      setNewItemName('')
    }
  }

  const handleDelete = async (path: string) => {
    try {
      await axios.delete(`${backendUrl}/api/workspace/file/${path}`)
      
      toast({
        title: 'Deleted',
        description: `Deleted ${path}`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
      
      fetchWorkspaceTree(currentPath)
    } catch (err: any) {
      toast({
        title: 'Error deleting',
        description: err.response?.data?.detail || 'Failed to delete',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    }
  }

  const handleRename = async (path: string, newName: string) => {
    // This would require a rename endpoint in the backend
    toast({
      title: 'Rename not implemented',
      description: 'File rename functionality coming soon',
      status: 'info',
      duration: 3000,
      isClosable: true,
    })
  }

  const pathSegments = currentPath.split('/').filter(Boolean)

  return (
    <Box
      className={className}
      bg={bg}
      border="1px solid"
      borderColor={borderColor}
      borderRadius="md"
      overflow="hidden"
      h="100%"
    >
      {/* Header */}
      <VStack spacing={0} align="stretch">
        <HStack p={3} borderBottom="1px solid" borderColor={borderColor}>
          <Text fontSize="sm" fontWeight="bold" flex={1}>
            Workspace
          </Text>
          <Menu>
            <MenuButton
              as={IconButton}
              aria-label="New"
              icon={<AddIcon />}
              size="sm"
              variant="ghost"
            />
            <MenuList>
              <MenuItem onClick={() => handleCreateFile('')}>
                New File
              </MenuItem>
              <MenuItem onClick={() => handleCreateFolder('')}>
                New Folder
              </MenuItem>
            </MenuList>
          </Menu>
          <IconButton
            aria-label="Refresh"
            icon={<RefreshIcon />}
            size="sm"
            variant="ghost"
            onClick={() => fetchWorkspaceTree(currentPath)}
          />
        </HStack>

        {/* Breadcrumb */}
        {pathSegments.length > 0 && (
          <Box p={2} borderBottom="1px solid" borderColor={borderColor}>
            <Breadcrumb
              spacing="8px"
              separator={<ChevronRightIcon color="gray.500" />}
              fontSize="xs"
            >
              <BreadcrumbItem>
                <BreadcrumbLink onClick={() => setCurrentPath('')}>
                  <FolderIcon />
                </BreadcrumbLink>
              </BreadcrumbItem>
              {pathSegments.map((segment, index) => (
                <BreadcrumbItem key={index}>
                  <BreadcrumbLink
                    onClick={() => setCurrentPath(pathSegments.slice(0, index + 1).join('/'))}
                  >
                    {segment}
                  </BreadcrumbLink>
                </BreadcrumbItem>
              ))}
            </Breadcrumb>
          </Box>
        )}

        {/* New Item Forms */}
        {(isCreatingFile || isCreatingFolder) && (
          <Box p={3} borderBottom="1px solid" borderColor={borderColor}>
            <VStack spacing={2}>
              <Input
                placeholder={isCreatingFile ? 'File name' : 'Folder name'}
                value={newItemName}
                onChange={(e) => setNewItemName(e.target.value)}
                size="sm"
                onKeyPress={(e) => {
                  if (e.key === 'Enter') {
                    isCreatingFile ? confirmCreateFile() : confirmCreateFolder()
                  }
                }}
                autoFocus
              />
              <HStack spacing={2}>
                <Button
                  size="xs"
                  colorScheme="blue"
                  onClick={isCreatingFile ? confirmCreateFile : confirmCreateFolder}
                >
                  Create
                </Button>
                <Button
                  size="xs"
                  variant="ghost"
                  onClick={() => {
                    setIsCreatingFile(false)
                    setIsCreatingFolder(false)
                    setNewItemName('')
                  }}
                >
                  Cancel
                </Button>
              </HStack>
            </VStack>
          </Box>
        )}
      </VStack>

      {/* File Tree Content */}
      <Box flex={1} overflowY="auto" p={2}>
        {loading ? (
          <Box display="flex" justifyContent="center" py={8}>
            <Spinner />
          </Box>
        ) : error ? (
          <Alert status="error" size="sm">
            <AlertIcon />
            {error}
          </Alert>
        ) : files.length === 0 ? (
          <Box textAlign="center" py={8} color="gray.500">
            <Text fontSize="sm">No files in workspace</Text>
            <Text fontSize="xs">Create a new file or folder to get started</Text>
          </Box>
        ) : (
          <VStack spacing={0} align="stretch">
            {files.map((file) => (
              <FileTreeNode
                key={file.path}
                item={file}
                level={0}
                isSelected={selectedFile?.path === file.path}
                onSelect={handleFileSelect}
                onCreateFile={handleCreateFile}
                onCreateFolder={handleCreateFolder}
                onDelete={handleDelete}
                onRename={handleRename}
                isExpanded={expandedPaths.has(file.path)}
                onToggleExpand={handleToggleExpand}
              />
            ))}
          </VStack>
        )}
      </Box>
    </Box>
  )
}