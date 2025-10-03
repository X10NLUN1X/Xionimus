import React, { useState, useEffect } from 'react'
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  Progress,
  Icon,
  Divider,
  useColorModeValue,
  Collapse,
  IconButton,
  Spinner,
  Link,
  Tooltip
} from '@chakra-ui/react'
import { ChevronDownIcon, ChevronUpIcon, SearchIcon, CheckIcon, ExternalLinkIcon } from '@chakra-ui/icons'

interface ResearchSource {
  url: string
  title: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  timestamp: string
  snippet?: string
}

interface ResearchActivity {
  id: string
  type: 'research' | 'clarification' | 'coding'
  status: 'active' | 'completed' | 'failed'
  title: string
  description: string
  progress: number
  sources?: ResearchSource[]
  startTime: string
  endTime?: string
}

interface ResearchActivityPanelProps {
  activities: ResearchActivity[]
  isVisible: boolean
}

export const ResearchActivityPanel: React.FC<ResearchActivityPanelProps> = ({
  activities,
  isVisible
}) => {
  const [expandedActivities, setExpandedActivities] = useState<Set<string>>(new Set())
  
  const bgColor = useColorModeValue('white', 'rgba(10, 22, 40, 0.95)')
  const borderColor = useColorModeValue('gray.200', 'rgba(0, 212, 255, 0.3)')
  const headerBg = useColorModeValue('gray.50', 'rgba(15, 30, 50, 0.8)')
  const sourceBg = useColorModeValue('gray.50', 'rgba(20, 35, 60, 0.5)')
  const accentColor = useColorModeValue('#0094ff', '#0088cc')

  const toggleActivity = (id: string) => {
    const newExpanded = new Set(expandedActivities)
    if (newExpanded.has(id)) {
      newExpanded.delete(id)
    } else {
      newExpanded.add(id)
    }
    setExpandedActivities(newExpanded)
  }

  // Auto-expand active activities
  useEffect(() => {
    const activeActivities = activities.filter(a => a.status === 'active')
    if (activeActivities.length > 0) {
      setExpandedActivities(new Set(activeActivities.map(a => a.id)))
    }
  }, [activities])

  if (!isVisible || activities.length === 0) {
    return null
  }

  return (
    <Box
      width="400px"
      height="100%"
      bg={bgColor}
      borderLeft="2px solid"
      borderColor={borderColor}
      overflowY="auto"
      position="sticky"
      top={0}
    >
      {/* Header */}
      <Box
        p={4}
        bg={headerBg}
        borderBottom="2px solid"
        borderColor={borderColor}
        position="sticky"
        top={0}
        zIndex={10}
      >
        <HStack spacing={2}>
          <Icon as={SearchIcon} color={accentColor} />
          <Text fontWeight="bold" fontSize="lg">
            Agent Aktivitäten
          </Text>
          <Badge colorScheme="blue" ml="auto">
            {activities.filter(a => a.status === 'active').length} aktiv
          </Badge>
        </HStack>
      </Box>

      {/* Activities List */}
      <VStack spacing={0} align="stretch">
        {activities.map((activity) => (
          <Box
            key={activity.id}
            borderBottom="1px solid"
            borderColor={borderColor}
          >
            {/* Activity Header */}
            <HStack
              p={4}
              cursor="pointer"
              onClick={() => toggleActivity(activity.id)}
              _hover={{ bg: headerBg }}
              transition="all 0.2s"
            >
              <IconButton
                aria-label="Toggle"
                icon={expandedActivities.has(activity.id) ? <ChevronUpIcon /> : <ChevronDownIcon />}
                size="sm"
                variant="ghost"
              />

              <VStack align="start" flex={1} spacing={1}>
                <HStack>
                  <Text fontWeight="semibold" fontSize="md">
                    {activity.title}
                  </Text>
                  {activity.status === 'active' && (
                    <Spinner size="xs" color={accentColor} />
                  )}
                  {activity.status === 'completed' && (
                    <Icon as={CheckIcon} color="green.500" />
                  )}
                </HStack>
                <Text fontSize="sm" color="gray.500">
                  {activity.description}
                </Text>
              </VStack>

              {activity.sources && (
                <Badge colorScheme="purple">
                  {activity.sources.length} Quellen
                </Badge>
              )}
            </HStack>

            {/* Activity Details */}
            <Collapse in={expandedActivities.has(activity.id)}>
              <Box px={4} pb={4}>
                {/* Progress Bar */}
                {activity.status === 'active' && (
                  <Box mb={3}>
                    <HStack mb={1} justify="space-between">
                      <Text fontSize="xs" color="gray.500">
                        Fortschritt
                      </Text>
                      <Text fontSize="xs" fontWeight="bold" color={accentColor}>
                        {activity.progress}%
                      </Text>
                    </HStack>
                    <Progress
                      value={activity.progress}
                      size="sm"
                      colorScheme="blue"
                      borderRadius="full"
                      isAnimated
                      hasStripe={activity.status === 'active'}
                    />
                  </Box>
                )}

                {/* Sources List */}
                {activity.sources && activity.sources.length > 0 && (
                  <VStack align="stretch" spacing={2} mt={3}>
                    <Text fontSize="xs" fontWeight="bold" color="gray.500" textTransform="uppercase">
                      Durchsuchte Quellen
                    </Text>
                    {activity.sources.map((source, idx) => (
                      <Box
                        key={idx}
                        p={3}
                        bg={sourceBg}
                        borderRadius="md"
                        borderLeft="3px solid"
                        borderColor={
                          source.status === 'completed' ? 'green.500' :
                          source.status === 'processing' ? 'blue.500' :
                          source.status === 'failed' ? 'red.500' :
                          'gray.500'
                        }
                      >
                        <HStack spacing={2} align="start">
                          {source.status === 'processing' && (
                            <Spinner size="xs" color="blue.500" mt={1} />
                          )}
                          {source.status === 'completed' && (
                            <Icon as={CheckIcon} color="green.500" boxSize={3} mt={1} />
                          )}
                          
                          <VStack align="start" flex={1} spacing={1}>
                            <Link
                              href={source.url}
                              isExternal
                              fontSize="sm"
                              fontWeight="semibold"
                              color={accentColor}
                              _hover={{ textDecoration: 'underline' }}
                            >
                              <HStack spacing={1}>
                                <Text noOfLines={1}>{source.title}</Text>
                                <Icon as={ExternalLinkIcon} boxSize={3} />
                              </HStack>
                            </Link>
                            
                            {source.snippet && (
                              <Text fontSize="xs" color="gray.500" noOfLines={2}>
                                {source.snippet}
                              </Text>
                            )}
                            
                            <Text fontSize="xs" color="gray.400">
                              {new Date(source.timestamp).toLocaleTimeString('de-DE')}
                            </Text>
                          </VStack>

                          <Badge
                            size="sm"
                            colorScheme={
                              source.status === 'completed' ? 'green' :
                              source.status === 'processing' ? 'blue' :
                              source.status === 'failed' ? 'red' :
                              'gray'
                            }
                          >
                            {source.status === 'completed' ? '✓' :
                             source.status === 'processing' ? '...' :
                             source.status === 'failed' ? '✗' : '○'}
                          </Badge>
                        </HStack>
                      </Box>
                    ))}
                  </VStack>
                )}

                {/* Timing Info */}
                <HStack mt={3} fontSize="xs" color="gray.500">
                  <Text>Gestartet: {new Date(activity.startTime).toLocaleTimeString('de-DE')}</Text>
                  {activity.endTime && (
                    <>
                      <Text>•</Text>
                      <Text>Beendet: {new Date(activity.endTime).toLocaleTimeString('de-DE')}</Text>
                    </>
                  )}
                </HStack>
              </Box>
            </Collapse>
          </Box>
        ))}
      </VStack>
    </Box>
  )
}
