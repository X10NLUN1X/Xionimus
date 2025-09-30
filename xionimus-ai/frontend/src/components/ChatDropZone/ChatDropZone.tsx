import React, { useState, useCallback, useRef, useEffect } from 'react'
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
  const [isDragActive, setIsDragActive] = useState(false)
  const dragCounter = useRef(0)
  
  const overlayBg = useColorModeValue(
    'rgba(0, 212, 255, 0.1)',
    'rgba(0, 212, 255, 0.2)'
  )
  const overlayBorder = useColorModeValue(
    '3px dashed rgba(0, 212, 255, 0.6)',
    '3px dashed rgba(0, 212, 255, 0.8)'
  )

  const handleDrag = useCallback((e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
  }, [])

  const handleDragIn = useCallback((e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    dragCounter.current++
    
    if (e.dataTransfer?.items && e.dataTransfer.items.length > 0) {
      setIsDragActive(true)
    }
  }, [])

  const handleDragOut = useCallback((e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    dragCounter.current--
    
    if (dragCounter.current === 0) {
      setIsDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragActive(false)
    dragCounter.current = 0
    
    if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
      const files = Array.from(e.dataTransfer.files)
      
      // Filter files by size
      const validFiles = files.filter(file => file.size <= maxFileSize)
      
      if (validFiles.length < files.length) {
        console.warn('Some files exceeded the maximum file size and were not added')
      }
      
      onFilesAdded(validFiles.slice(0, maxFiles))
    }
  }, [onFilesAdded, maxFiles, maxFileSize])

  useEffect(() => {
    const div = document.body
    
    div.addEventListener('dragenter', handleDragIn)
    div.addEventListener('dragleave', handleDragOut)
    div.addEventListener('dragover', handleDrag)
    div.addEventListener('drop', handleDrop)
    
    return () => {
      div.removeEventListener('dragenter', handleDragIn)
      div.removeEventListener('dragleave', handleDragOut)
      div.removeEventListener('dragover', handleDrag)
      div.removeEventListener('drop', handleDrop)
    }
  }, [handleDrag, handleDragIn, handleDragOut, handleDrop])

  return (
    <>
      {children}
      
      {isDragActive && (
        <Box
          position="fixed"
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
          zIndex={9999}
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
    </>
  )
}