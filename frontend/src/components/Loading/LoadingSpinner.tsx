import React from 'react'
import {
  Box,
  Spinner,
  VStack,
  Text,
  useColorModeValue
} from '@chakra-ui/react'

interface LoadingSpinnerProps {
  message?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  fullScreen?: boolean
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  message = 'Loading...',
  size = 'lg',
  fullScreen = false
}) => {
  const content = (
    <VStack spacing={4}>
      <Spinner
        size={size}
        thickness="4px"
        speed="0.65s"
        color="primary.500"
      />
      {message && (
        <Text color={useColorModeValue('gray.600', 'gray.400')} fontSize="sm">
          {message}
        </Text>
      )}
    </VStack>
  )

  if (fullScreen) {
    return (
      <Box
        position="fixed"
        top={0}
        left={0}
        right={0}
        bottom={0}
        display="flex"
        alignItems="center"
        justifyContent="center"
        bg={useColorModeValue('whiteAlpha.800', 'blackAlpha.800')}
        zIndex={9999}
        backdropFilter="blur(4px)"
      >
        {content}
      </Box>
    )
  }

  return (
    <Box
      display="flex"
      alignItems="center"
      justifyContent="center"
      py={8}
    >
      {content}
    </Box>
  )
}