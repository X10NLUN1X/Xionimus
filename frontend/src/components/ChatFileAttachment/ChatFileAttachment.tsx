import React from 'react'
import {
  Box,
  HStack,
  VStack,
  Text,
  IconButton,
  useColorModeValue,
  Badge,
  Flex
} from '@chakra-ui/react'
import {
  DeleteIcon,
  AttachmentIcon,
  DownloadIcon
} from '@chakra-ui/icons'

interface ChatFileAttachmentProps {
  file: File | { name: string; size: number; type: string }
  onRemove?: () => void
  showRemove?: boolean
  isCompact?: boolean
}

export const ChatFileAttachment: React.FC<ChatFileAttachmentProps> = ({
  file,
  onRemove,
  showRemove = true,
  isCompact = false
}) => {
  const bgColor = useColorModeValue('gray.100', 'rgba(15, 30, 50, 0.6)')
  const borderColor = useColorModeValue('gray.300', 'rgba(0, 212, 255, 0.3)')
  const textColor = useColorModeValue('gray.700', 'gray.300')

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const getFileIcon = (type: string): string => {
    if (type.startsWith('image/')) return '🖼️'
    if (type.startsWith('video/')) return '🎥'
    if (type.startsWith('audio/')) return '🎵'
    if (type.includes('pdf')) return '📄'
    if (type.includes('zip') || type.includes('rar')) return '📦'
    if (type.includes('text') || type.includes('code')) return '📝'
    return '📎'
  }

  if (isCompact) {
    return (
      <HStack
        spacing={2}
        p={2}
        bg={bgColor}
        borderRadius="md"
        border="1px solid"
        borderColor={borderColor}
        maxW="200px"
      >
        <Text fontSize="lg">{getFileIcon(file.type)}</Text>
        <VStack align="start" spacing={0} flex={1} minW={0}>
          <Text fontSize="xs" fontWeight="medium" color={textColor} isTruncated maxW="100%">
            {file.name}
          </Text>
          <Text fontSize="xs" color="gray.500">
            {formatFileSize(file.size)}
          </Text>
        </VStack>
        {showRemove && onRemove && (
          <IconButton
            aria-label="Remove file"
            icon={<DeleteIcon />}
            size="xs"
            variant="ghost"
            colorScheme="red"
            onClick={onRemove}
          />
        )}
      </HStack>
    )
  }

  return (
    <Box
      p={3}
      bg={bgColor}
      borderRadius="lg"
      border="2px solid"
      borderColor={borderColor}
      _hover={{ borderColor: '#0088cc' }}
      transition="all 0.2s"
    >
      <Flex justify="space-between" align="start">
        <HStack spacing={3} flex={1} minW={0}>
          <Text fontSize="2xl">{getFileIcon(file.type)}</Text>
          <VStack align="start" spacing={1} flex={1} minW={0}>
            <Text fontSize="sm" fontWeight="medium" color={textColor} isTruncated maxW="100%">
              {file.name}
            </Text>
            <HStack spacing={2}>
              <Badge colorScheme="cyan" fontSize="xs">
                {formatFileSize(file.size)}
              </Badge>
              {file.type && (
                <Badge colorScheme="blue" fontSize="xs">
                  {file.type.split('/')[1]?.toUpperCase() || 'FILE'}
                </Badge>
              )}
            </HStack>
          </VStack>
        </HStack>
        {showRemove && onRemove && (
          <IconButton
            aria-label="Remove file"
            icon={<DeleteIcon />}
            size="sm"
            variant="ghost"
            colorScheme="red"
            onClick={onRemove}
          />
        )}
      </Flex>
    </Box>
  )
}