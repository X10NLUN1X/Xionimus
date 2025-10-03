import React from 'react'
import {
  Box,
  VStack,
  HStack,
  Text,
  Button,
  useColorModeValue,
  Icon,
  Badge,
  Divider
} from '@chakra-ui/react'
import ReactMarkdown from 'react-markdown'

interface QuickAction {
  id: string
  title: string
  description: string
  action: string
  icon?: string
  duration?: string
  provider?: string
  model?: string
}

interface QuickActionsProps {
  message: string
  options: QuickAction[]
  onSelect: (action: QuickAction) => void
  isDisabled?: boolean
}

export const QuickActions: React.FC<QuickActionsProps> = ({
  message,
  options,
  onSelect,
  isDisabled = false
}) => {
  const bgColor = useColorModeValue('white', 'rgba(15, 30, 50, 0.8)')
  const borderColor = useColorModeValue('gray.200', 'rgba(0, 212, 255, 0.3)')
  const hoverBg = useColorModeValue('blue.50', 'rgba(0, 212, 255, 0.1)')
  const activeBg = useColorModeValue('blue.100', 'rgba(0, 212, 255, 0.2)')

  return (
    <Box
      bg={bgColor}
      borderWidth="2px"
      borderColor={borderColor}
      borderRadius="xl"
      p={6}
      mb={4}
      boxShadow="lg"
    >
      <VStack align="stretch" spacing={4}>
        {/* Message/Question */}
        <Box>
          <ReactMarkdown>{message}</ReactMarkdown>
        </Box>

        <Divider />

        {/* Options as clickable cards */}
        <VStack align="stretch" spacing={3}>
          {options.map((option) => (
            <Button
              key={option.id}
              onClick={() => onSelect(option)}
              isDisabled={isDisabled}
              size="lg"
              height="auto"
              py={4}
              px={5}
              variant="outline"
              borderWidth="2px"
              borderColor={borderColor}
              bg={bgColor}
              _hover={{
                bg: hoverBg,
                borderColor: 'blue.400',
                transform: 'translateY(-2px)',
                boxShadow: 'lg'
              }}
              _active={{
                bg: activeBg,
                transform: 'translateY(0)'
              }}
              transition="all 0.2s"
              textAlign="left"
              whiteSpace="normal"
              justifyContent="flex-start"
            >
              <HStack spacing={4} align="start" width="100%">
                {/* Icon */}
                {option.icon && (
                  <Text fontSize="2xl" flexShrink={0}>
                    {option.icon}
                  </Text>
                )}

                {/* Content */}
                <VStack align="start" spacing={1} flex={1}>
                  <HStack>
                    <Text fontWeight="bold" fontSize="md">
                      {option.title}
                    </Text>
                    {option.duration && (
                      <Badge colorScheme="blue" fontSize="xs">
                        {option.duration}
                      </Badge>
                    )}
                  </HStack>
                  <Text fontSize="sm" color="gray.500" fontWeight="normal">
                    {option.description}
                  </Text>
                  {option.model && (
                    <Badge colorScheme="purple" fontSize="xs" mt={1}>
                      {option.model}
                    </Badge>
                  )}
                </VStack>
              </HStack>
            </Button>
          ))}
        </VStack>
      </VStack>
    </Box>
  )
}
