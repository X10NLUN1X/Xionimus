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
import { EditIcon } from '@chakra-ui/icons'

export const WorkspacePage: React.FC = () => {
  const cardBg = useColorModeValue('white', 'gray.800')
  
  return (
    <Box p={6}>
      <VStack spacing={8} align="stretch">
        <VStack align="start" spacing={2}>
          <Heading size="lg">Workspace</Heading>
          <Text color="gray.500">
            Code editor and file management (Coming in Phase 2)
          </Text>
        </VStack>
        
        <Card bg={cardBg}>
          <CardBody>
            <VStack spacing={6} align="center" py={12}>
              <EditIcon w={16} h={16} color="gray.400" />
              <VStack spacing={2} textAlign="center">
                <Heading size="md" color="gray.600">
                  Code Editor & File Management
                </Heading>
                <Text color="gray.500" maxW="md">
                  The workspace will include Monaco Editor, file tree navigation,
                  and Git integration. This feature is planned for Phase 2.
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