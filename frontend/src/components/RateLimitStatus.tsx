import React, { useState, useEffect } from 'react'
import {
  Box,
  Text,
  Progress,
  VStack,
  HStack,
  Badge,
  Tooltip,
  IconButton,
  useColorModeValue,
  Divider
} from '@chakra-ui/react'
import { InfoIcon, RefreshIcon } from '@chakra-ui/icons'
import { useApp } from '../contexts/AppContext'

interface QuotaData {
  requests: {
    used: number
    limit: number
    remaining: number
  }
  ai_calls: {
    used: number
    limit: number
    remaining: number
  }
  reset_in_seconds: number
  user_role: string
}

export const RateLimitStatus: React.FC = () => {
  const [quotaData, setQuotaData] = useState<QuotaData | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const { token, isAuthenticated } = useApp()
  
  const bgColor = useColorModeValue('white', 'gray.800')
  const borderColor = useColorModeValue('gray.200', 'gray.600')
  
  const API_BASE = import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'

  const fetchQuotaStatus = async () => {
    if (!isAuthenticated || !token) return
    
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`${API_BASE}/api/rate-limits/quota`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        setQuotaData(data)
      } else if (response.status === 429) {
        setError('Rate limit exceeded')
      } else {
        setError('Fehler beim Laden der Quota-Daten')
      }
    } catch (err) {
      setError('Netzwerkfehler')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (isAuthenticated) {
      fetchQuotaStatus()
      
      // Refresh every 30 seconds
      const interval = setInterval(fetchQuotaStatus, 30000)
      return () => clearInterval(interval)
    }
  }, [isAuthenticated, token])

  const formatTime = (seconds: number): string => {
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    
    if (minutes > 0) {
      return `${minutes}m ${remainingSeconds}s`
    }
    return `${remainingSeconds}s`
  }

  const getProgressColor = (used: number, limit: number): string => {
    const percentage = (used / limit) * 100
    if (percentage >= 90) return 'red'
    if (percentage >= 70) return 'yellow'
    return 'green'
  }

  if (!isAuthenticated) {
    return null
  }

  if (error) {
    return (
      <Box
        p={3}
        bg={bgColor}
        border="1px solid"
        borderColor={borderColor}
        borderRadius="md"
        fontSize="sm"
      >
        <HStack>
          <Text color="red.500">⚠️ {error}</Text>
          <IconButton
            aria-label="Refresh"
            icon={<RefreshIcon />}
            size="xs"
            variant="ghost"
            onClick={fetchQuotaStatus}
            isLoading={loading}
          />
        </HStack>
      </Box>
    )
  }

  if (!quotaData) {
    return (
      <Box
        p={3}
        bg={bgColor}
        border="1px solid"
        borderColor={borderColor}
        borderRadius="md"
        fontSize="sm"
      >
        <Text color="gray.500">Lade Rate Limit Status...</Text>
      </Box>
    )
  }

  return (
    <Box
      p={3}
      bg={bgColor}
      border="1px solid"
      borderColor={borderColor}
      borderRadius="md"
      fontSize="sm"
      minW="250px"
    >
      <VStack spacing={3} align="stretch">
        {/* Header */}
        <HStack justify="space-between">
          <HStack>
            <Text fontWeight="600" color="blue.500">
              Rate Limits
            </Text>
            <Badge colorScheme="blue" variant="subtle">
              {quotaData.user_role}
            </Badge>
          </HStack>
          <Tooltip label="Rate Limit Status aktualisieren">
            <IconButton
              aria-label="Refresh"
              icon={<RefreshIcon />}
              size="xs"
              variant="ghost"
              onClick={fetchQuotaStatus}
              isLoading={loading}
            />
          </Tooltip>
        </HStack>

        {/* API Requests */}
        <Box>
          <HStack justify="space-between" mb={1}>
            <Text fontSize="xs" color="gray.600">
              API Requests
            </Text>
            <Text fontSize="xs" color="gray.600">
              {quotaData.requests.used} / {quotaData.requests.limit}
            </Text>
          </HStack>
          <Progress
            value={(quotaData.requests.used / quotaData.requests.limit) * 100}
            colorScheme={getProgressColor(quotaData.requests.used, quotaData.requests.limit)}
            size="sm"
            borderRadius="md"
          />
        </Box>

        {/* AI Calls */}
        <Box>
          <HStack justify="space-between" mb={1}>
            <Text fontSize="xs" color="gray.600">
              AI Calls
            </Text>
            <Text fontSize="xs" color="gray.600">
              {quotaData.ai_calls.used} / {quotaData.ai_calls.limit}
            </Text>
          </HStack>
          <Progress
            value={(quotaData.ai_calls.used / quotaData.ai_calls.limit) * 100}
            colorScheme={getProgressColor(quotaData.ai_calls.used, quotaData.ai_calls.limit)}
            size="sm"
            borderRadius="md"
          />
        </Box>

        <Divider />

        {/* Reset Timer */}
        <HStack justify="space-between" fontSize="xs">
          <HStack>
            <InfoIcon color="gray.400" />
            <Text color="gray.600">Reset in:</Text>
          </HStack>
          <Text color="gray.600" fontWeight="600">
            {formatTime(quotaData.reset_in_seconds)}
          </Text>
        </HStack>

        {/* Warnings */}
        {quotaData.requests.remaining < 10 && (
          <Box p={2} bg="orange.50" borderRadius="md" border="1px solid" borderColor="orange.200">
            <Text fontSize="xs" color="orange.700">
              ⚠️ Nur noch {quotaData.requests.remaining} API Requests übrig
            </Text>
          </Box>
        )}

        {quotaData.ai_calls.remaining < 3 && (
          <Box p={2} bg="red.50" borderRadius="md" border="1px solid" borderColor="red.200">
            <Text fontSize="xs" color="red.700">
              🚨 Nur noch {quotaData.ai_calls.remaining} AI Calls übrig
            </Text>
          </Box>
        )}
      </VStack>
    </Box>
  )
}