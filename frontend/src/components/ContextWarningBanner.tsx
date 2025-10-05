import React, { useState, useEffect } from 'react'
import {
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Box,
  Button,
  HStack,
  Progress,
  Text,
  useToast,
  VStack
} from '@chakra-ui/react'
import { WarningIcon } from '@chakra-ui/icons'
import axios from 'axios'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001'

interface ContextStatus {
  session_id: string
  total_messages: number
  estimated_tokens: number
  context_limit: number
  usage_percentage: number
  should_fork: boolean
  warning_message: string | null
}

interface ContextWarningBannerProps {
  sessionId: string | null
  onForkClick: () => void
}

export const ContextWarningBanner: React.FC<ContextWarningBannerProps> = ({
  sessionId,
  onForkClick
}) => {
  const [contextStatus, setContextStatus] = useState<ContextStatus | null>(null)
  const [isVisible, setIsVisible] = useState(false)
  const toast = useToast()

  useEffect(() => {
    if (!sessionId) {
      setIsVisible(false)
      return
    }

    const checkContext = async () => {
      try {
        const token = localStorage.getItem('xionimus_token')
        const response = await axios.get(
          `${BACKEND_URL}/api/session-fork/context-status/${sessionId}`,
          {
            headers: token ? {
              'Authorization': `Bearer ${token}`
            } : {}
          }
        )

        const status: ContextStatus = response.data
        setContextStatus(status)
        setIsVisible(status.should_fork)
      } catch (error) {
        console.error('Failed to check context status:', error)
      }
    }

    // Check immediately
    checkContext()

    // Check every 30 seconds
    const interval = setInterval(checkContext, 30000)

    return () => clearInterval(interval)
  }, [sessionId])

  if (!isVisible || !contextStatus) {
    return null
  }

  const getAlertStatus = () => {
    if (contextStatus.usage_percentage >= 95) return 'error'
    if (contextStatus.usage_percentage >= 80) return 'warning'
    return 'info'
  }

  const getProgressColorScheme = () => {
    if (contextStatus.usage_percentage >= 95) return 'red'
    if (contextStatus.usage_percentage >= 80) return 'orange'
    return 'blue'
  }

  return (
    <Alert
      status={getAlertStatus()}
      variant="left-accent"
      borderRadius="md"
      mb={4}
      flexDirection="column"
      alignItems="start"
    >
      <HStack spacing={2} mb={2} width="100%">
        <AlertIcon />
        <VStack align="start" flex={1} spacing={0}>
          <AlertTitle fontSize="md">
            ⚠️ Context-Auslastung hoch
          </AlertTitle>
          <AlertDescription fontSize="sm">
            {contextStatus.warning_message}
          </AlertDescription>
        </VStack>
      </HStack>

      <Box width="100%" mt={2}>
        <HStack justify="space-between" mb={1}>
          <Text fontSize="xs" color="gray.600">
            {contextStatus.estimated_tokens.toLocaleString()} / {contextStatus.context_limit.toLocaleString()} Tokens
          </Text>
          <Text fontSize="xs" fontWeight="bold" color={getAlertStatus() === 'error' ? 'red.600' : 'orange.600'}>
            {contextStatus.usage_percentage.toFixed(1)}%
          </Text>
        </HStack>
        <Progress
          value={contextStatus.usage_percentage}
          size="sm"
          colorScheme={getProgressColorScheme()}
          borderRadius="full"
        />
      </Box>

      <HStack mt={3} spacing={3} width="100%">
        <Button
          size="sm"
          colorScheme="blue"
          onClick={onForkClick}
          leftIcon={<Text>🔀</Text>}
        >
          Session forken
        </Button>
        <Button
          size="sm"
          variant="ghost"
          onClick={() => setIsVisible(false)}
        >
          Später
        </Button>
      </HStack>

      <Text fontSize="xs" color="gray.600" mt={2}>
        💡 Ein Fork erstellt eine neue Session mit kompakter Zusammenfassung - ideal für lange Gespräche!
      </Text>
    </Alert>
  )
}
