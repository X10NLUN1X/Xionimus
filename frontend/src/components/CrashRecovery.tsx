import React, { useEffect, useState } from 'react'
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  Button,
  VStack,
  Text,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Code,
  useColorModeValue,
  HStack,
  Badge
} from '@chakra-ui/react'
import { WarningIcon, CheckIcon } from '@chakra-ui/icons'
import { ErrorLogger } from '../utils/errorLogger'

export const CrashRecovery: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [crashData, setCrashData] = useState<ReturnType<typeof ErrorLogger.getCrashRecoveryData> | null>(null)
  
  const bgColor = useColorModeValue('white', 'rgba(10, 22, 40, 0.98)')
  const borderColor = useColorModeValue('gray.200', 'rgba(0, 212, 255, 0.3)')

  useEffect(() => {
    // Check for recent crashes on mount
    const data = ErrorLogger.getCrashRecoveryData()
    if (data.hasCrash && data.errorCount > 0) {
      setCrashData(data)
      setIsOpen(true)
    }
  }, [])

  const handleDismiss = () => {
    setIsOpen(false)
  }

  const handleClearLogs = () => {
    ErrorLogger.clearErrorLogs()
    setIsOpen(false)
  }

  if (!crashData || !crashData.hasCrash) return null

  return (
    <Modal isOpen={isOpen} onClose={handleDismiss} size="lg" isCentered>
      <ModalOverlay bg="blackAlpha.700" backdropFilter="blur(10px)" />
      <ModalContent
        bg={bgColor}
        border="1px solid"
        borderColor={borderColor}
        boxShadow="0 20px 60px rgba(255, 100, 100, 0.3)"
      >
        <ModalHeader>
          <HStack spacing={3}>
            <WarningIcon color="orange.400" boxSize={6} />
            <VStack align="start" spacing={0}>
              <Text>App Recovered from Crash</Text>
              <Badge colorScheme="orange" fontSize="xs">
                {crashData.errorCount} error{crashData.errorCount > 1 ? 's' : ''} detected
              </Badge>
            </VStack>
          </HStack>
        </ModalHeader>

        <ModalBody>
          <VStack spacing={4} align="stretch">
            <Alert status="warning" borderRadius="md">
              <AlertIcon />
              <VStack align="start" spacing={1} flex={1}>
                <AlertTitle fontSize="sm">Session Recovered</AlertTitle>
                <AlertDescription fontSize="xs">
                  The app encountered errors in your last session. Your data should be safe.
                </AlertDescription>
              </VStack>
            </Alert>

            {crashData.lastError && (
              <VStack align="stretch" spacing={2}>
                <Text fontSize="sm" fontWeight="bold" color="gray.500">
                  Last Error:
                </Text>
                <Code
                  p={3}
                  borderRadius="md"
                  fontSize="xs"
                  display="block"
                  whiteSpace="pre-wrap"
                  maxH="150px"
                  overflowY="auto"
                >
                  {crashData.lastError.message}
                </Code>
                <Text fontSize="xs" color="gray.500">
                  Occurred: {new Date(crashData.lastError.timestamp).toLocaleString()}
                </Text>
              </VStack>
            )}

            <Alert status="info" borderRadius="md" size="sm">
              <AlertIcon />
              <AlertDescription fontSize="xs">
                Error logs are stored locally for debugging. You can clear them once everything works normally.
              </AlertDescription>
            </Alert>
          </VStack>
        </ModalBody>

        <ModalFooter>
          <HStack spacing={2}>
            <Button
              variant="ghost"
              onClick={handleClearLogs}
              size="sm"
            >
              Clear Logs
            </Button>
            <Button
              colorScheme="cyan"
              onClick={handleDismiss}
              leftIcon={<CheckIcon />}
              size="sm"
            >
              Continue
            </Button>
          </HStack>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}
