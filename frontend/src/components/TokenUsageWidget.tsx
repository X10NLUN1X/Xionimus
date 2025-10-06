import React, { useEffect, useState } from 'react'
import {
  Box,
  VStack,
  HStack,
  Text,
  Progress,
  Badge,
  Tooltip,
  IconButton,
  useColorModeValue,
  Collapse,
  Alert,
  AlertIcon,
  AlertDescription,
  Button
} from '@chakra-ui/react'
import { InfoIcon, ChevronDownIcon, ChevronUpIcon, WarningIcon } from '@chakra-ui/icons'
import axios from 'axios'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'

interface TokenUsageWidgetProps {
  tokenUsage?: any
  onForkRecommended?: () => void
}

export const TokenUsageWidget: React.FC<TokenUsageWidgetProps> = ({ 
  tokenUsage: propTokenUsage,
  onForkRecommended 
}) => {
  const [tokenUsage, setTokenUsage] = useState<any>(propTokenUsage || null)
  const [isExpanded, setIsExpanded] = useState(false)
  const [isLoading, setIsLoading] = useState(!propTokenUsage)

  const bgColor = useColorModeValue('white', 'rgba(15, 30, 50, 0.8)')
  const borderColor = useColorModeValue('gray.200', 'rgba(0, 212, 255, 0.3)')
  const textColor = useColorModeValue('gray.800', 'white')
  const hoverBgColor = useColorModeValue('gray.50', 'rgba(0, 212, 255, 0.05)')
  const expandedBorderColor = useColorModeValue('gray.50', 'rgba(0, 0, 0, 0.2)')

  useEffect(() => {
    if (propTokenUsage) {
      setTokenUsage(propTokenUsage)
      setIsLoading(false)
    } else {
      fetchTokenUsage()
    }
  }, [propTokenUsage])

  const fetchTokenUsage = async () => {
    try {
      const response = await axios.get(`${BACKEND_URL}/api/tokens/stats`)
      setTokenUsage(response.data)
      setIsLoading(false)
    } catch (error) {
      console.error('Failed to fetch token usage:', error)
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return null
  }
  
  // Show widget even without usage data (with defaults)
  if (!tokenUsage) {
    return (
      <Box
        position="fixed"
        bottom={4}
        right={4}
        bg={bgColor}
        borderRadius="lg"
        border="1px solid"
        borderColor={borderColor}
        boxShadow="lg"
        maxW="350px"
        zIndex={1000}
        p={3}
      >
        <HStack spacing={2}>
          <Text fontSize="xs" fontWeight="semibold" color={textColor}>
            Token Usage
          </Text>
          <Badge colorScheme="green" fontSize="xx-small">
            0
          </Badge>
        </HStack>
        <Progress
          value={0}
          colorScheme="green"
          size="sm"
          borderRadius="full"
          mt={2}
        />
        <Text fontSize="xx-small" color="gray.500" mt={1}>
          0.0% of limit (No messages yet)
        </Text>
      </Box>
    )
  }

  const currentSession = tokenUsage.current_session || {}
  const recommendation = tokenUsage.recommendation || {}
  const percentages = tokenUsage.percentages || {}
  const limits = tokenUsage.limits || {}

  // Determine color based on usage
  const getColorScheme = () => {
    if (recommendation.level === 'critical') return 'red'
    if (recommendation.level === 'high') return 'orange'
    if (recommendation.level === 'warning') return 'yellow'
    return 'green'
  }

  const colorScheme = getColorScheme()
  const percentage = percentages.hard_limit_percentage || 0

  return (
    <Box
      position="fixed"
      bottom={4}
      right={4}
      bg={bgColor}
      borderRadius="lg"
      border="1px solid"
      borderColor={borderColor}
      boxShadow="lg"
      maxW="350px"
      zIndex={1000}
    >
      {/* Compact View */}
      <HStack
        p={3}
        spacing={3}
        cursor="pointer"
        onClick={() => setIsExpanded(!isExpanded)}
        _hover={{ bg: hoverBgColor }}
        transition="background 0.2s"
      >
        <Box flex={1}>
          <HStack spacing={2} mb={1}>
            <Text fontSize="xs" fontWeight="semibold" color={textColor}>
              Token Usage
            </Text>
            <Badge colorScheme={colorScheme} fontSize="xx-small">
              {currentSession.total_tokens?.toLocaleString() || 0}
            </Badge>
          </HStack>
          <Progress
            value={percentage}
            colorScheme={colorScheme}
            size="sm"
            borderRadius="full"
          />
          <Text fontSize="xx-small" color="gray.500" mt={1}>
            {percentage.toFixed(1)}% of limit
          </Text>
        </Box>
        <IconButton
          aria-label={isExpanded ? "Collapse" : "Expand"}
          icon={isExpanded ? <ChevronDownIcon /> : <ChevronUpIcon />}
          size="sm"
          variant="ghost"
        />
      </HStack>

      {/* Expanded View */}
      <Collapse in={isExpanded} animateOpacity>
        <VStack align="stretch" p={3} pt={0} spacing={3} borderTop="1px solid" borderColor={borderColor}>
          {/* Recommendation Alert */}
          {recommendation.level !== 'ok' && (
            <Alert status={recommendation.level === 'critical' ? 'error' : 'warning'} borderRadius="md" fontSize="xs">
              <AlertIcon />
              <Box flex={1}>
                <AlertDescription>
                  {recommendation.message}
                </AlertDescription>
                {recommendation.details && (
                  <Text fontSize="xx-small" mt={1} opacity={0.8}>
                    {recommendation.details}
                  </Text>
                )}
              </Box>
            </Alert>
          )}

          {/* Stats Grid */}
          <VStack align="stretch" spacing={2} fontSize="xs">
            <HStack justify="space-between">
              <Text color="gray.500">Current Session:</Text>
              <Text fontWeight="semibold" color={textColor}>
                {currentSession.total_tokens?.toLocaleString() || 0}
              </Text>
            </HStack>
            <HStack justify="space-between">
              <Text color="gray.500">Messages:</Text>
              <Text fontWeight="semibold" color={textColor}>
                {currentSession.messages_count || 0}
              </Text>
            </HStack>
            <HStack justify="space-between">
              <Text color="gray.500">Soft Limit:</Text>
              <Text fontWeight="semibold" color={textColor}>
                {limits.soft_limit?.toLocaleString() || 50000}
              </Text>
            </HStack>
            <HStack justify="space-between">
              <Text color="gray.500">Hard Limit:</Text>
              <Text fontWeight="semibold" color={textColor}>
                {limits.hard_limit?.toLocaleString() || 100000}
              </Text>
            </HStack>
          </VStack>

          {/* Fork Button (if recommended) */}
          {recommendation.action && recommendation.action !== 'fork_soon' && onForkRecommended && (
            <Button
              size="sm"
              colorScheme={recommendation.level === 'critical' ? 'red' : 'orange'}
              onClick={() => {
                onForkRecommended()
                setIsExpanded(false)
              }}
              leftIcon={<WarningIcon />}
            >
              {recommendation.level === 'critical' ? 'Fork Now!' : 'Create Fork'}
            </Button>
          )}

          {/* Tips */}
          <Box p={2} bg={useColorModeValue('gray.50', 'rgba(0, 0, 0, 0.2)')} borderRadius="md">
            <Text fontSize="xx-small" fontWeight="semibold" mb={1} color={textColor}>
              💡 Wann Fork/Summary?
            </Text>
            <VStack align="stretch" spacing={1} fontSize="xx-small" color="gray.500">
              <Text>• &lt;50k tokens: Alles gut ✅</Text>
              <Text>• 50-100k: Bald forken ⚠️</Text>
              <Text>• 100k+: Jetzt forken! 🚨</Text>
            </VStack>
          </Box>
        </VStack>
      </Collapse>
    </Box>
  )
}
