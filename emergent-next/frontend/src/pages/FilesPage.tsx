import React from 'react'
import {
  Box,
  Text,
  Heading,
  VStack,
  Card,
  CardBody,
  Badge,
  useColorModeValue
} from '@chakra-ui/react'
import { AttachmentIcon } from '@chakra-ui/icons'

export const FilesPage: React.FC = () => {
  const cardBg = useColorModeValue('white', 'gray.800')
  
  return (
    <Box p={6}>
      <VStack spacing={8} align="stretch">
        <VStack align="start" spacing={2}>
          <Heading size="lg">Files</Heading>
          <Text color="gray.500">
            File upload and management system (Coming in Phase 2)
          </Text>
        </VStack>
        
        <Card bg={cardBg}>
          <CardBody>
            <VStack spacing={6} align="center" py={12}>
              <AttachmentIcon w={16} h={16} color="gray.400" />
              <VStack spacing={2} textAlign="center">
                <Heading size="md" color="gray.600">
                  File Management System
                </Heading>
                <Text color="gray.500" maxW="md">
                  Upload, organize, and manage files for AI processing.
                  Includes drag-and-drop, preview, and sharing features.
                </Text>
                <Badge colorScheme="blue" mt={2}>
                  Coming Soon
                </Badge>
              </VStack>
            </VStack>
          </CardBody>
        </Card>
      </VStack>
    </Box>
  )
}