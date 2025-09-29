import React, { useState, useEffect, useCallback } from 'react'
import {
  Box,
  Text,
  Heading,
  VStack,
  HStack,
  Card,
  CardBody,
  Badge,
  useColorModeValue,
  Button,
  IconButton,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  TableContainer,
  useToast,
  Spinner,
  Alert,
  AlertIcon,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
  Image,
  Flex,
  SimpleGrid,
  useBreakpointValue
} from '@chakra-ui/react'
import {
  AttachmentIcon,
  DownloadIcon,
  DeleteIcon,
  ViewIcon,
  ChevronDownIcon,
  RepeatIcon,
  AddIcon
} from '@chakra-ui/icons'
import axios from 'axios'
import { FileUploadZone } from '../components/FileUpload/FileUploadZone'
import { LoadingSpinner } from '../components/Loading/LoadingSpinner'

interface UploadedFile {
  file_id: string
  original_filename: string
  stored_filename: string
  file_size: number
  content_type: string
  description?: string
  uploaded_at: string
  download_url: string
}

export const FilesPage: React.FC = () => {
  const [files, setFiles] = useState<UploadedFile[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedFile, setSelectedFile] = useState<UploadedFile | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  
  const { isOpen, onOpen, onClose } = useDisclosure()
  const toast = useToast()
  
  const cardBg = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.700')
  const backendUrl = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString()
  }

  const getFileIcon = (contentType: string) => {
    if (contentType.startsWith('image/')) return '🖼️'
    if (contentType.startsWith('video/')) return '🎥'
    if (contentType.startsWith('audio/')) return '🎵'
    if (contentType.includes('pdf')) return '📄'
    if (contentType.includes('text')) return '📝'
    if (contentType.includes('json')) return '📋'
    if (contentType.includes('zip') || contentType.includes('tar')) return '📦'
    return '📎'
  }

  const loadFiles = useCallback(async () => {
    try {
      setLoading(true)
      const response = await axios.get(`${backendUrl}/api/files`)
      setFiles(response.data)
    } catch (error: any) {
      console.error('Load files error:', error)
      toast({
        title: 'Error loading files',
        description: error.response?.data?.detail || 'Failed to load files',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    } finally {
      setLoading(false)
    }
  }, [backendUrl, toast])

  const handleUploadComplete = useCallback((uploadedFiles: any[]) => {
    toast({
      title: 'Upload complete',
      description: `${uploadedFiles.length} file(s) uploaded successfully`,
      status: 'success',
      duration: 3000,
      isClosable: true,
    })
    loadFiles() // Refresh file list
  }, [loadFiles, toast])

  const downloadFile = (file: UploadedFile) => {
    const link = document.createElement('a')
    link.href = `${backendUrl}${file.download_url}`
    link.download = file.original_filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const deleteFile = async (file: UploadedFile) => {
    try {
      await axios.delete(`${backendUrl}/api/files/${file.file_id}`)
      toast({
        title: 'File deleted',
        description: `${file.original_filename} has been deleted`,
        status: 'success',
        duration: 3000,
        isClosable: true,
      })
      loadFiles() // Refresh file list
    } catch (error: any) {
      toast({
        title: 'Error deleting file',
        description: error.response?.data?.detail || 'Failed to delete file',
        status: 'error',
        duration: 5000,
        isClosable: true,
      })
    }
  }

  const viewFile = (file: UploadedFile) => {
    setSelectedFile(file)
    onOpen()
  }

  useEffect(() => {
    loadFiles()
  }, [loadFiles])

  return (
    <Box p={6}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <VStack align="start" spacing={2}>
          <HStack justify="space-between" w="100%">
            <VStack align="start" spacing={1}>
              <Heading size="lg">Files</Heading>
              <Text color="gray.500">
                Upload, manage, and organize your files
              </Text>
            </VStack>
            <HStack>
              <Button
                leftIcon={<RepeatIcon />}
                variant="outline"
                size="sm"
                onClick={loadFiles}
                isLoading={loading}
              >
                Refresh
              </Button>
            </HStack>
          </HStack>
        </VStack>

        {/* File Upload Zone */}
        <Card bg={cardBg}>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <HStack justify="space-between">
                <HStack>
                  <AddIcon />
                  <Text fontWeight="medium">Upload Files</Text>
                </HStack>
                <Badge colorScheme="green">250MB Max</Badge>
              </HStack>
              
              <FileUploadZone
                onUploadComplete={handleUploadComplete}
                maxFiles={10}
                maxFileSize={250 * 1024 * 1024} // 250MB
              />
            </VStack>
          </CardBody>
        </Card>

        {/* Files List */}
        <Card bg={cardBg}>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <HStack justify="space-between">
                <HStack>
                  <AttachmentIcon />
                  <Text fontWeight="medium">Your Files</Text>
                  <Badge>{files.length}</Badge>
                </HStack>
              </HStack>

              {loading ? (
                <Flex justify="center" py={8}>
                  <Spinner size="lg" />
                </Flex>
              ) : files.length === 0 ? (
                <Alert status="info">
                  <AlertIcon />
                  No files uploaded yet. Use the upload zone above to get started.
                </Alert>
              ) : (
                <TableContainer>
                  <Table variant="simple">
                    <Thead>
                      <Tr>
                        <Th>File</Th>
                        <Th>Type</Th>
                        <Th>Size</Th>
                        <Th>Uploaded</Th>
                        <Th>Actions</Th>
                      </Tr>
                    </Thead>
                    <Tbody>
                      {files.map((file) => (
                        <Tr key={file.file_id}>
                          <Td>
                            <HStack>
                              <Text fontSize="lg">{getFileIcon(file.content_type)}</Text>
                              <VStack align="start" spacing={0}>
                                <Text fontWeight="medium" isTruncated maxW="200px">
                                  {file.original_filename}
                                </Text>
                                {file.description && (
                                  <Text fontSize="sm" color="gray.500" isTruncated maxW="200px">
                                    {file.description}
                                  </Text>
                                )}
                              </VStack>
                            </HStack>
                          </Td>
                          <Td>
                            <Badge colorScheme="blue" fontSize="xs">
                              {file.content_type.split('/')[1]?.toUpperCase() || 'FILE'}
                            </Badge>
                          </Td>
                          <Td>{formatFileSize(file.file_size)}</Td>
                          <Td>
                            <Text fontSize="sm" color="gray.600">
                              {formatDate(file.uploaded_at)}
                            </Text>
                          </Td>
                          <Td>
                            <HStack spacing={1}>
                              <IconButton
                                aria-label="View file"
                                icon={<ViewIcon />}
                                size="sm"
                                variant="ghost"
                                onClick={() => viewFile(file)}
                              />
                              <IconButton
                                aria-label="Download file"
                                icon={<DownloadIcon />}
                                size="sm"
                                variant="ghost"
                                onClick={() => downloadFile(file)}
                              />
                              <IconButton
                                aria-label="Delete file"
                                icon={<DeleteIcon />}
                                size="sm"
                                variant="ghost"
                                colorScheme="red"
                                onClick={() => deleteFile(file)}
                              />
                            </HStack>
                          </Td>
                        </Tr>
                      ))}
                    </Tbody>
                  </Table>
                </TableContainer>
              )}
            </VStack>
          </CardBody>
        </Card>
      </VStack>

      {/* File Preview Modal */}
      <Modal isOpen={isOpen} onClose={onClose} size="xl">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>
            <HStack>
              <Text fontSize="lg">{selectedFile && getFileIcon(selectedFile.content_type)}</Text>
              <Text isTruncated>{selectedFile?.original_filename}</Text>
            </HStack>
          </ModalHeader>
          <ModalCloseButton />
          <ModalBody pb={6}>
            {selectedFile && (
              <VStack spacing={4} align="stretch">
                <HStack justify="space-between">
                  <VStack align="start" spacing={1}>
                    <Text fontSize="sm" color="gray.500">File Information</Text>
                    <Text>Type: {selectedFile.content_type}</Text>
                    <Text>Size: {formatFileSize(selectedFile.file_size)}</Text>
                    <Text>Uploaded: {formatDate(selectedFile.uploaded_at)}</Text>
                  </VStack>
                  <VStack>
                    <Button
                      leftIcon={<DownloadIcon />}
                      colorScheme="blue"
                      size="sm"
                      onClick={() => downloadFile(selectedFile)}
                    >
                      Download
                    </Button>
                  </VStack>
                </HStack>

                {/* Image Preview */}
                {selectedFile.content_type.startsWith('image/') && (
                  <Box>
                    <Text fontSize="sm" color="gray.500" mb={2}>Preview</Text>
                    <Image
                      src={`${backendUrl}${selectedFile.download_url}`}
                      alt={selectedFile.original_filename}
                      maxH="400px"
                      objectFit="contain"
                      border="1px"
                      borderColor={borderColor}
                      borderRadius="md"
                    />
                  </Box>
                )}

                {/* Text Preview */}
                {selectedFile.content_type.startsWith('text/') && selectedFile.file_size < 1024 * 100 && (
                  <Box>
                    <Text fontSize="sm" color="gray.500" mb={2}>Preview</Text>
                    <Box
                      p={4}
                      bg={useColorModeValue('gray.50', 'gray.700')}
                      borderRadius="md"
                      maxH="300px"
                      overflowY="auto"
                    >
                      <Text fontSize="sm" fontFamily="mono" whiteSpace="pre-wrap">
                        {/* Text content would be loaded here */}
                        Preview not available yet...
                      </Text>
                    </Box>
                  </Box>
                )}
              </VStack>
            )}
          </ModalBody>
        </ModalContent>
      </Modal>
    </Box>
  )
}