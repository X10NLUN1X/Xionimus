import React, { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import {
  Box,
  VStack,
  Text,
  useColorModeValue,
  Icon
} from '@chakra-ui/react'
import { AttachmentIcon } from '@chakra-ui/icons'

interface ChatDropZoneProps {
  onFilesAdded: (files: File[]) => void
  maxFiles?: number
  maxFileSize?: number
  acceptedFileTypes?: string[]
  children: React.ReactNode
}

export const ChatDropZone: React.FC<ChatDropZoneProps> = ({
  onFilesAdded,
  maxFiles = 5,
  maxFileSize = 25 * 1024 * 1024, // 25MB default
  acceptedFileTypes,
  children
}) => {
  const overlayBg = useColorModeValue(
    'rgba(0, 212, 255, 0.1)',
    'rgba(0, 212, 255, 0.2)'
  )
  const overlayBorder = useColorModeValue(
    '3px dashed rgba(0, 212, 255, 0.6)',
    '3px dashed rgba(0, 212, 255, 0.8)'
  )

  const onDrop = useCallback((acceptedFiles: File[]) => {
    // Filter files by size
    const validFiles = acceptedFiles.filter(file => file.size <= maxFileSize)
    
    if (validFiles.length < acceptedFiles.length) {
      console.warn('Some files exceeded the maximum file size and were not added')
    }
    
    onFilesAdded(validFiles.slice(0, maxFiles))
  }, [onFilesAdded, maxFiles, maxFileSize])

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    noClick: true,
    noKeyboard: true,
    maxFiles,
    maxSize: maxFileSize,
    accept: acceptedFileTypes ? acceptedFileTypes.reduce((acc, type) => {
      acc[type] = []
      return acc
    }, {} as Record<string, string[]>) : undefined
  })

  return (
    <Box 
      {...getRootProps()} 
      position="relative" 
      w="100%" 
      h="100%"
      sx={{
        '& > *:not(input)': {
          pointerEvents: isDragActive ? 'none' : 'auto'
        }
      }}
    >
      <input {...getInputProps()} />
      {children}
      
      {isDragActive && (
        <Box
          position="absolute"
          top={0}
          left={0}
          right={0}
          bottom={0}
          bg={overlayBg}
          backdropFilter="blur(4px)"
          border={overlayBorder}
          borderRadius="xl"
          display="flex"
          alignItems="center"
          justifyContent="center"
          zIndex={1000}
          pointerEvents="none"
        >
          <VStack spacing={4}>
            <Icon as={AttachmentIcon} boxSize={12} color="#00d4ff" />
            <Text fontSize="2xl" fontWeight="bold" color="#00d4ff">
              Drop files here to attach
            </Text>
            <Text fontSize="md" color="gray.400">
              Max {maxFiles} files, {(maxFileSize / (1024 * 1024)).toFixed(0)}MB each
            </Text>
          </VStack>
        </Box>
      )}
    </Box>
  )
}