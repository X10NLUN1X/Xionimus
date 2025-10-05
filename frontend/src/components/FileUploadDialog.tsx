import React, { useState, useRef } from 'react'
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  Button,
  VStack,
  Text,
  useToast,
  Box,
  HStack,
  Badge,
  IconButton,
  Progress,
  Alert,
  AlertIcon,
  List,
  ListItem,
  ListIcon
} from '@chakra-ui/react'
import { AttachmentIcon, CheckCircleIcon, DeleteIcon, WarningIcon } from '@chakra-ui/icons'
import axios from 'axios'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001'
const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB

interface FileUploadDialogProps {
  isOpen: boolean
  onClose: () => void
  sessionId: string | null
  activeProject: string | null
}

interface FileToUpload {
  file: File
  id: string
}

export const FileUploadDialog: React.FC<FileUploadDialogProps> = ({
  isOpen,
  onClose,
  sessionId,
  activeProject
}) => {
  const [files, setFiles] = useState<FileToUpload[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const toast = useToast()

  const handleFileSelect = (selectedFiles: FileList | null) => {
    if (!selectedFiles) return

    const newFiles: FileToUpload[] = []
    const errors: string[] = []

    Array.from(selectedFiles).forEach(file => {
      if (file.size > MAX_FILE_SIZE) {
        errors.push(`${file.name} ist zu groß (${(file.size / (1024 * 1024)).toFixed(1)}MB > 50MB)`)
      } else {
        newFiles.push({
          file,
          id: `${Date.now()}_${file.name}`
        })
      }
    })

    if (errors.length > 0) {
      toast({
        title: 'Einige Dateien wurden übersprungen',
        description: errors.join(', '),
        status: 'warning',
        duration: 5000
      })
    }

    setFiles(prev => [...prev, ...newFiles])
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)

    handleFileSelect(e.dataTransfer.files)
  }

  const removeFile = (id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id))
  }

  const handleUpload = async () => {
    if (files.length === 0) return

    setIsUploading(true)
    setUploadProgress(0)

    try {
      const formData = new FormData()
      
      files.forEach(({ file }) => {
        formData.append('files', file)
      })

      if (sessionId) {
        formData.append('session_id', sessionId)
      }

      const token = localStorage.getItem('xionimus_token')
      
      const response = await axios.post(
        `${BACKEND_URL}/api/file-upload/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
          },
          onUploadProgress: (progressEvent) => {
            const progress = progressEvent.total
              ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
              : 0
            setUploadProgress(progress)
          }
        }
      )

      const result = response.data

      toast({
        title: '✅ Upload erfolgreich!',
        description: result.message,
        status: 'success',
        duration: 5000
      })

      setFiles([])
      onClose()
    } catch (error: any) {
      console.error('Upload failed:', error)
      const errorMsg = error.response?.data?.detail || 'Upload fehlgeschlagen'
      
      toast({
        title: 'Upload fehlgeschlagen',
        description: errorMsg,
        status: 'error',
        duration: 5000
      })
    } finally {
      setIsUploading(false)
      setUploadProgress(0)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const totalSize = files.reduce((sum, { file }) => sum + file.size, 0)

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>📤 Dateien hochladen</ModalHeader>
        <ModalCloseButton />

        <ModalBody>
          <VStack align="stretch" spacing={4}>
            {/* Target Info */}
            <Alert status="info" borderRadius="md">
              <AlertIcon />
              <Box>
                <Text fontSize="sm" fontWeight="semibold">Upload-Ziel:</Text>
                <Text fontSize="sm">
                  {activeProject 
                    ? `📁 Aktives Projekt: ${activeProject}`
                    : '📁 Uploads-Verzeichnis'}
                </Text>
              </Box>
            </Alert>

            {/* Drag & Drop Area */}
            <Box
              border="2px dashed"
              borderColor={isDragging ? 'blue.500' : 'gray.300'}
              borderRadius="md"
              p={8}
              textAlign="center"
              bg={isDragging ? 'blue.50' : 'gray.50'}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              cursor="pointer"
              onClick={() => fileInputRef.current?.click()}
              transition="all 0.2s"
              _hover={{
                borderColor: 'blue.400',
                bg: 'blue.50'
              }}
            >
              <VStack spacing={2}>
                <AttachmentIcon boxSize={8} color="gray.400" />
                <Text fontWeight="semibold" color="gray.700">
                  Dateien hier ablegen
                </Text>
                <Text fontSize="sm" color="gray.600">
                  oder klicken zum Auswählen
                </Text>
                <Text fontSize="xs" color="gray.500">
                  Max. 50MB pro Datei
                </Text>
              </VStack>
            </Box>

            <input
              ref={fileInputRef}
              type="file"
              multiple
              style={{ display: 'none' }}
              onChange={(e) => handleFileSelect(e.target.files)}
            />

            {/* Selected Files List */}
            {files.length > 0 && (
              <Box>
                <HStack justify="space-between" mb={2}>
                  <Text fontWeight="semibold" fontSize="sm">
                    Ausgewählte Dateien ({files.length})
                  </Text>
                  <Badge colorScheme="blue">
                    {formatFileSize(totalSize)}
                  </Badge>
                </HStack>

                <List spacing={2}>
                  {files.map(({ file, id }) => (
                    <ListItem
                      key={id}
                      p={2}
                      bg="white"
                      borderRadius="md"
                      borderWidth="1px"
                    >
                      <HStack justify="space-between">
                        <HStack flex={1} spacing={2}>
                          <ListIcon as={CheckCircleIcon} color="green.500" />
                          <VStack align="start" spacing={0} flex={1}>
                            <Text fontSize="sm" fontWeight="medium" noOfLines={1}>
                              {file.name}
                            </Text>
                            <Text fontSize="xs" color="gray.600">
                              {formatFileSize(file.size)}
                            </Text>
                          </VStack>
                        </HStack>
                        <IconButton
                          aria-label="Entfernen"
                          icon={<DeleteIcon />}
                          size="sm"
                          variant="ghost"
                          colorScheme="red"
                          onClick={() => removeFile(id)}
                          isDisabled={isUploading}
                        />
                      </HStack>
                    </ListItem>
                  ))}
                </List>
              </Box>
            )}

            {/* Upload Progress */}
            {isUploading && (
              <Box>
                <HStack justify="space-between" mb={1}>
                  <Text fontSize="sm" fontWeight="semibold">
                    Wird hochgeladen...
                  </Text>
                  <Text fontSize="sm" color="blue.600">
                    {uploadProgress}%
                  </Text>
                </HStack>
                <Progress
                  value={uploadProgress}
                  size="sm"
                  colorScheme="blue"
                  borderRadius="full"
                />
              </Box>
            )}
          </VStack>
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" mr={3} onClick={onClose} isDisabled={isUploading}>
            Abbrechen
          </Button>
          <Button
            colorScheme="blue"
            onClick={handleUpload}
            isLoading={isUploading}
            isDisabled={files.length === 0}
            leftIcon={<AttachmentIcon />}
          >
            {files.length > 0 ? `${files.length} Datei(en) hochladen` : 'Hochladen'}
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}
