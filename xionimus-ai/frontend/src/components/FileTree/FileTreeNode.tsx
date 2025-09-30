import React, { useState } from 'react'
import {
  Box,
  HStack,
  VStack,
  Text,
  Icon,
  Collapse,
  useColorModeValue,
  IconButton,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useDisclosure,
} from '@chakra-ui/react'
import {
  ChevronRightIcon,
  ChevronDownIcon,
  AddIcon,
  DeleteIcon,
  EditIcon,
} from '@chakra-ui/icons'
import {
  FaFile,
  FaFolder,
  FaFolderOpen,
  FaJs,
  FaPython,
  FaHtml5,
  FaCss3,
  FaMarkdown,
  FaImage,
  FaCode,
  FaFileCode,
} from 'react-icons/fa'

export interface FileTreeItem {
  name: string
  path: string
  type: 'file' | 'directory'
  size?: number
  modified: string
  extension?: string
  children?: FileTreeItem[]
}

interface FileTreeNodeProps {
  item: FileTreeItem
  level: number
  isSelected: boolean
  onSelect: (item: FileTreeItem) => void
  onCreateFile?: (parentPath: string) => void
  onCreateFolder?: (parentPath: string) => void
  onDelete?: (path: string) => void
  onRename?: (path: string, newName: string) => void
  isExpanded?: boolean
  onToggleExpand?: (path: string) => void
}

export const FileTreeNode: React.FC<FileTreeNodeProps> = ({
  item,
  level,
  isSelected,
  onSelect,
  onCreateFile,
  onCreateFolder,
  onDelete,
  onRename,
  isExpanded = false,
  onToggleExpand,
}) => {
  const [isEditing, setIsEditing] = useState(false)
  const [editName, setEditName] = useState(item.name)
  const { isOpen, onOpen, onClose } = useDisclosure()

  const hoverBg = useColorModeValue('gray.100', 'gray.700')
  const selectedBg = useColorModeValue('blue.100', 'blue.900')
  const textColor = useColorModeValue('gray.800', 'gray.100')

  const getFileIcon = (item: FileTreeItem) => {
    if (item.type === 'directory') {
      return isExpanded ? FaFolderOpen : FaFolder
    }

    const ext = item.extension?.toLowerCase()
    switch (ext) {
      case '.js':
      case '.jsx':
        return FaJs
      case '.ts':
      case '.tsx':
        return FaJs
      case '.py':
        return FaPython
      case '.html':
        return FaHtml5
      case '.css':
      case '.scss':
        return FaCss3
      case '.md':
        return FaMarkdown
      case '.png':
      case '.jpg':
      case '.jpeg':
      case '.gif':
      case '.svg':
        return FaImage
      case '.json':
      case '.yaml':
      case '.yml':
        return FaFileCode
      default:
        return item.extension ? FaCode : FaFile
    }
  }

  const getFileColor = (item: FileTreeItem) => {
    if (item.type === 'directory') {
      return 'blue.500'
    }

    const ext = item.extension?.toLowerCase()
    switch (ext) {
      case '.js':
      case '.jsx':
        return 'cyan.500'
      case '.ts':
      case '.tsx':
        return 'blue.600'
      case '.py':
        return 'teal.500'
      case '.html':
        return 'cyan.600'
      case '.css':
      case '.scss':
        return 'purple.500'
      case '.md':
        return 'gray.600'
      case '.png':
      case '.jpg':
      case '.jpeg':
      case '.gif':
      case '.svg':
        return 'pink.500'
      case '.json':
        return 'orange.400'
      default:
        return 'gray.500'
    }
  }

  const handleToggle = () => {
    if (item.type === 'directory') {
      onToggleExpand?.(item.path)
    }
  }

  const handleSelect = () => {
    onSelect(item)
    if (item.type === 'directory') {
      handleToggle()
    }
  }

  const handleRename = () => {
    if (editName !== item.name && editName.trim()) {
      onRename?.(item.path, editName.trim())
    }
    setIsEditing(false)
  }

  const formatFileSize = (bytes?: number) => {
    if (!bytes) return ''
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const FileIcon = getFileIcon(item)

  return (
    <VStack spacing={0} align="stretch">
      <HStack
        spacing={1}
        pl={level * 4}
        pr={2}
        py={1}
        bg={isSelected ? selectedBg : 'transparent'}
        _hover={{ bg: isSelected ? selectedBg : hoverBg }}
        cursor="pointer"
        borderRadius="sm"
        position="relative"
        onMouseEnter={onOpen}
        onMouseLeave={onClose}
      >
        {/* Expand/Collapse Button */}
        {item.type === 'directory' && (
          <IconButton
            aria-label="toggle"
            icon={isExpanded ? <ChevronDownIcon /> : <ChevronRightIcon />}
            size="xs"
            variant="ghost"
            onClick={handleToggle}
            minW="auto"
            h="auto"
            p={0}
          />
        )}
        {item.type === 'file' && <Box w={4} />}

        {/* File/Folder Icon */}
        <Icon as={FileIcon} color={getFileColor(item)} boxSize={4} />

        {/* File/Folder Name */}
        <Box flex={1} onClick={handleSelect}>
          {isEditing ? (
            <input
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              onBlur={handleRename}
              onKeyPress={(e) => e.key === 'Enter' && handleRename()}
              autoFocus
              style={{
                background: 'transparent',
                border: 'none',
                outline: 'none',
                width: '100%',
                color: textColor,
              }}
            />
          ) : (
            <HStack spacing={2} justify="space-between">
              <Text
                fontSize="sm"
                color={textColor}
                isTruncated
                maxW="150px"
              >
                {item.name}
              </Text>
              {item.type === 'file' && item.size && (
                <Text fontSize="xs" color="gray.500">
                  {formatFileSize(item.size)}
                </Text>
              )}
            </HStack>
          )}
        </Box>

        {/* Context Menu */}
        {isOpen && (
          <Menu>
            <MenuButton
              as={IconButton}
              aria-label="options"
              icon={<Icon as={FaCode} />}
              size="xs"
              variant="ghost"
            />
            <MenuList>
              {item.type === 'directory' && (
                <>
                  <MenuItem
                    icon={<AddIcon />}
                    onClick={() => onCreateFile?.(item.path)}
                  >
                    New File
                  </MenuItem>
                  <MenuItem
                    icon={<AddIcon />}
                    onClick={() => onCreateFolder?.(item.path)}
                  >
                    New Folder
                  </MenuItem>
                </>
              )}
              <MenuItem
                icon={<EditIcon />}
                onClick={() => setIsEditing(true)}
              >
                Rename
              </MenuItem>
              <MenuItem
                icon={<DeleteIcon />}
                onClick={() => onDelete?.(item.path)}
                color="red.500"
              >
                Delete
              </MenuItem>
            </MenuList>
          </Menu>
        )}
      </HStack>

      {/* Children */}
      {item.type === 'directory' && item.children && (
        <Collapse in={isExpanded}>
          <VStack spacing={0} align="stretch">
            {item.children.map((child) => (
              <FileTreeNode
                key={child.path}
                item={child}
                level={level + 1}
                isSelected={false} // Child selection logic would go here
                onSelect={onSelect}
                onCreateFile={onCreateFile}
                onCreateFolder={onCreateFolder}
                onDelete={onDelete}
                onRename={onRename}
                isExpanded={false} // Child expansion logic would go here
                onToggleExpand={onToggleExpand}
              />
            ))}
          </VStack>
        </Collapse>
      )}
    </VStack>
  )
}