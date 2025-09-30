import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  Progress,
  Alert,
  AlertIcon,
  useColorModeValue,
  useToast,
  Badge,
  IconButton,
  List,
  ListItem,
  Flex,
  Spinner,
  Icon
} from '@chakra-ui/react'
import {
  AttachmentIcon,
  CheckCircleIcon,
  DeleteIcon,
  WarningIcon,
  AddIcon  // Using AddIcon instead of UploadIcon
} from '@chakra-ui/icons'
import axios from 'axios'

interface UploadFile {
  file: File
  id: string
  progress: number
  status: 'pending' | 'uploading' | 'success' | 'error'
  error?: string
  response?: any
}

interface FileUploadZoneProps {
  onUploadComplete?: (files: any[]) => void
  maxFiles?: number
  maxFileSize?: number // in bytes
  acceptedFileTypes?: string[]
  className?: string
}

export const FileUploadZone: React.FC<FileUploadZoneProps> = ({
  onUploadComplete,
  maxFiles = 10,
  maxFileSize = 250 * 1024 * 1024, // 250MB default
  acceptedFileTypes,
  className
}) => {
  const [uploadFiles, setUploadFiles] = useState<UploadFile[]>([])
  const [isDragActive, setIsDragActive] = useState(false)
  
  const toast = useToast()
  const backendUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'
  
  // Theme colors
  const borderColor = useColorModeValue('gray.300', 'gray.600')
  const activeBorderColor = useColorModeValue('blue.400', 'blue.300')
  const bgColor = useColorModeValue('gray.50', 'gray.700')
  const activeBgColor = useColorModeValue('blue.50', 'blue.900')
  const textColor = useColorModeValue('gray.600', 'gray.300')

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const validateFile = (file: File): string | null => {
    if (file.size > maxFileSize) {
      return `File too large. Maximum size: ${formatFileSize(maxFileSize)}`
    }
    
    if (acceptedFileTypes && acceptedFileTypes.length > 0) {
      const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase()
      if (!acceptedFileTypes.includes(fileExtension) && !acceptedFileTypes.includes(file.type)) {
        return `File type not supported. Accepted types: ${acceptedFileTypes.join(', ')}`
      }
    }
    
    return null
  }

  const uploadSingleFile = async (uploadFile: UploadFile) => {
    const formData = new FormData()
    formData.append('file', uploadFile.file)
    formData.append('description', `Uploaded via drag-drop: ${uploadFile.file.name}`)

    try {
      setUploadFiles(prev => 
        prev.map(f => f.id === uploadFile.id ? { ...f, status: 'uploading' } : f)
      )

      const response = await axios.post(`${backendUrl}/api/files/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round(
            (progressEvent.loaded * 100) / (progressEvent.total || progressEvent.loaded)
          )
          
          setUploadFiles(prev =>
            prev.map(f => f.id === uploadFile.id ? { ...f, progress } : f)
          )
        }
      })

      // Success
      setUploadFiles(prev =>
        prev.map(f => f.id === uploadFile.id ? 
          { ...f, status: 'success', progress: 100, response: response.data } : f
        )
      )

      toast({
        title: 'Upload successful',
        description: `${uploadFile.file.name} uploaded successfully`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      })

    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Upload failed'
      
      setUploadFiles(prev =>
        prev.map(f => f.id === uploadFile.id ? 
          { ...f, status: 'error', error: errorMessage } : f
        )
      )

      toast({
        title: 'Upload failed',
        description: `${uploadFile.file.name}: ${errorMessage}`,
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    }
  }

  const onDrop = useCallback((acceptedFiles: File[]) => {
    setIsDragActive(false)
    
    if (uploadFiles.length + acceptedFiles.length > maxFiles) {
      toast({
        title: 'Too many files',
        description: `Maximum ${maxFiles} files allowed`,
        status: 'warning',
        duration: 3000,
        isClosable: true,
      })
      return
    }

    const newUploadFiles: UploadFile[] = acceptedFiles.map(file => {
      const validation = validateFile(file)
      return {
        file,
        id: Math.random().toString(36).substr(2, 9),
        progress: 0,
        status: validation ? 'error' : 'pending',
        error: validation || undefined
      }
    })

    setUploadFiles(prev => [...prev, ...newUploadFiles])

    // Start uploading valid files
    newUploadFiles.forEach(uploadFileItem => {
      if (uploadFileItem.status === 'pending') {
        handleUpload(uploadFileItem)
      }
    })
  }, [uploadFiles, maxFiles, maxFileSize, acceptedFileTypes, toast])

  const { getRootProps, getInputProps, isDragActive: dropzoneActive } = useDropzone({
    onDrop,
    multiple: true,
    onDragEnter: () => setIsDragActive(true),
    onDragLeave: () => setIsDragActive(false)
  })

  const removeFile = (id: string) => {
    setUploadFiles(prev => prev.filter(f => f.id !== id))
  }

  const retryUpload = (uploadFile: UploadFile) => {
    setUploadFiles(prev =>
      prev.map(f => f.id === uploadFile.id ? 
        { ...f, status: 'pending', progress: 0, error: undefined } : f
      )
    )
    handleUpload(uploadFile)
  }

  const clearAll = () => {
    setUploadFiles([])
  }

  const getStatusIcon = (status: UploadFile['status']) => {
    switch (status) {
      case 'uploading':
        return <Spinner size="sm" color="blue.500" />
      case 'success':
        return <CheckCircleIcon color="green.500" />
      case 'error':
        return <WarningIcon color="red.500" />
      default:
        return <AttachmentIcon color="gray.400" />
    }
  }

  const getStatusColor = (status: UploadFile['status']) => {
    switch (status) {
      case 'uploading':
        return 'blue'
      case 'success':
        return 'green'
      case 'error':
        return 'red'
      default:
        return 'gray'
    }
  }

  const successfulUploads = uploadFiles.filter(f => f.status === 'success')
  const isUploading = uploadFiles.some(f => f.status === 'uploading')

  // Notify parent when uploads complete
  React.useEffect(() => {
    if (onUploadComplete && successfulUploads.length > 0) {
      const completedFiles = successfulUploads.map(f => f.response)
      onUploadComplete(completedFiles)
    }
  }, [successfulUploads.length, onUploadComplete])

  return (
    <VStack spacing={4} align="stretch" className={className}>
      {/* Drop Zone */}
      <Box
        {...getRootProps()}
        border="2px dashed"
        borderColor={isDragActive || dropzoneActive ? activeBorderColor : borderColor}
        bg={isDragActive || dropzoneActive ? activeBgColor : bgColor}
        borderRadius="lg"
        p={8}
        textAlign="center"
        cursor="pointer"
        transition="all 0.2s"
        _hover={{
          borderColor: activeBorderColor,
          bg: activeBgColor
        }}
      >
        <input {...getInputProps()} />
        <VStack spacing={4}>
          <Icon as={AddIcon} w={12} h={12} color={textColor} />
          
          {isDragActive || dropzoneActive ? (
            <Text fontSize="lg" fontWeight="medium" color="blue.500">
              Drop files here to upload
            </Text>
          ) : (
            <VStack spacing={2}>
              <Text fontSize="lg" fontWeight="medium">
                Drag & drop files here
              </Text>
              <Text fontSize="sm" color={textColor}>
                or click to browse
              </Text>
              <HStack spacing={4} fontSize="xs" color={textColor}>
                <Text>Max {maxFiles} files</Text>
                <Text>•</Text>
                <Text>Up to {formatFileSize(maxFileSize)} each</Text>
              </HStack>
            </VStack>
          )}
        </VStack>
      </Box>

      {/* Upload Progress List */}
      {uploadFiles.length > 0 && (
        <VStack spacing={3} align="stretch">
          <HStack justify="space-between">
            <Text fontWeight="medium">
              Upload Progress ({uploadFiles.length} files)
            </Text>
            {!isUploading && (
              <Button size="sm" variant="ghost" onClick={clearAll}>
                Clear All
              </Button>
            )}
          </HStack>

          <List spacing={2}>
            {uploadFiles.map((uploadFile) => (
              <ListItem key={uploadFile.id}>
                <Box
                  p={3}
                  border="1px"
                  borderColor={borderColor}
                  borderRadius="md"
                  bg={useColorModeValue('white', 'gray.800')}
                >
                  <Flex align="center" gap={3}>
                    {getStatusIcon(uploadFile.status)}
                    
                    <VStack align="start" spacing={1} flex={1}>
                      <HStack justify="space-between" w="100%">
                        <Text fontSize="sm" fontWeight="medium" isTruncated>
                          {uploadFile.file.name}
                        </Text>
                        <HStack spacing={2}>
                          <Badge colorScheme={getStatusColor(uploadFile.status)}>
                            {uploadFile.status}
                          </Badge>
                          <Text fontSize="xs" color={textColor}>
                            {formatFileSize(uploadFile.file.size)}
                          </Text>
                        </HStack>
                      </HStack>
                      
                      {uploadFile.status === 'uploading' && (
                        <Progress
                          value={uploadFile.progress}
                          size="sm"
                          colorScheme="blue"
                          w="100%"
                        />
                      )}
                      
                      {uploadFile.error && (
                        <Text fontSize="xs" color="red.500">
                          {uploadFile.error}
                        </Text>
                      )}
                    </VStack>

                    <HStack>
                      {uploadFile.status === 'error' && (
                        <Button
                          size="xs"
                          colorScheme="blue"
                          variant="outline"
                          onClick={() => retryUpload(uploadFile)}
                        >
                          Retry
                        </Button>
                      )}
                      <IconButton
                        aria-label="Remove file"
                        icon={<DeleteIcon />}
                        size="xs"
                        variant="ghost"
                        colorScheme="red"
                        onClick={() => removeFile(uploadFile.id)}
                        isDisabled={uploadFile.status === 'uploading'}
                      />
                    </HStack>
                  </Flex>
                </Box>
              </ListItem>
            ))}
          </List>

          {/* Summary */}
          {successfulUploads.length > 0 && (
            <Alert status="success" borderRadius="md">
              <AlertIcon />
              <Text fontSize="sm">
                {successfulUploads.length} file{successfulUploads.length !== 1 ? 's' : ''} uploaded successfully
              </Text>
            </Alert>
          )}
        </VStack>
      )}
    </VStack>
  )
}