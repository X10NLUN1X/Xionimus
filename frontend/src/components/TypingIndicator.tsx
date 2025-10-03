import React from 'react'
import { Box, HStack, Text, Flex, Avatar, useColorModeValue } from '@chakra-ui/react'
import { keyframes } from '@emotion/react'

interface TypingIndicatorProps {
  streamingText?: string
  showDots?: boolean
}

const dotAnimation = keyframes`
  0%, 80%, 100% { transform: scale(0); opacity: 0.3; }
  40% { transform: scale(1); opacity: 1; }
`

export const TypingIndicator: React.FC<TypingIndicatorProps> = ({ 
  streamingText, 
  showDots = true 
}) => {
  const assistantBg = useColorModeValue('white', 'rgba(20, 30, 50, 0.7)')
  const borderColor = useColorModeValue('gray.200', 'rgba(0, 212, 255, 0.2)')

  return (
    <Flex gap={3}>
      <Avatar
        size="sm"
        name="Xionimus"
        bg="linear-gradient(135deg, #0088cc, #0066aa)"
      />
      
      <VStack flex={1} align="flex-start" spacing={1}>
        <Box
          bg={assistantBg}
          color={useColorModeValue('gray.800', 'white')}
          px={4}
          py={3}
          borderRadius="lg"
          maxW="85%"
          boxShadow={useColorModeValue("0 2px 8px rgba(0, 0, 0, 0.1)", "0 4px 15px rgba(0, 0, 0, 0.3)")}
          border="1px solid"
          borderColor={borderColor}
          minH="50px"
          position="relative"
        >
          {streamingText ? (
            <Text whiteSpace="pre-wrap">
              {streamingText}
              <Box
                as="span"
                display="inline-block"
                w="2px"
                h="1em"
                bg="cyan.400"
                ml="2px"
                animation="blink 1s infinite"
                sx={{
                  '@keyframes blink': {
                    '0%, 100%': { opacity: 1 },
                    '50%': { opacity: 0 }
                  }
                }}
              />
            </Text>
          ) : showDots && (
            <HStack spacing={1}>
              <Box
                w="8px"
                h="8px"
                borderRadius="full"
                bg="cyan.400"
                animation={`${dotAnimation} 1.4s infinite ease-in-out`}
                sx={{ animationDelay: '0s' }}
              />
              <Box
                w="8px"
                h="8px"
                borderRadius="full"
                bg="cyan.400"
                animation={`${dotAnimation} 1.4s infinite ease-in-out`}
                sx={{ animationDelay: '0.16s' }}
              />
              <Box
                w="8px"
                h="8px"
                borderRadius="full"
                bg="cyan.400"
                animation={`${dotAnimation} 1.4s infinite ease-in-out`}
                sx={{ animationDelay: '0.32s' }}
              />
            </HStack>
          )}
        </Box>
        
        {streamingText && (
          <Text fontSize="xs" color="gray.500">
            Streaming...
          </Text>
        )}
      </VStack>
    </Flex>
  )
}

// Fix missing import
import { VStack } from '@chakra-ui/react'
