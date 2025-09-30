import React, { Component, ErrorInfo, ReactNode } from 'react'
import {
  Box,
  VStack,
  Text,
  Button,
  Heading,
  Code,
  useColorModeValue,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Collapse,
  HStack,
  Badge
} from '@chakra-ui/react'
import { WarningIcon, DownloadIcon } from '@chakra-ui/icons'
import { ErrorLogger } from '../../utils/errorLogger'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
  showDetails: boolean
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      showDetails: false
    }
  }

  static getDerivedStateFromError(error: Error): Partial<State> {
    return { hasError: true }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo)
    this.setState({
      error,
      errorInfo
    })
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      showDetails: false
    })
  }

  toggleDetails = () => {
    this.setState(prev => ({ showDetails: !prev.showDetails }))
  }

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) {
        return this.props.fallback
      }

      return (
        <Box
          minH="100vh"
          display="flex"
          alignItems="center"
          justifyContent="center"
          bg={useColorModeValue('gray.50', 'gray.900')}
          p={6}
        >
          <VStack
            spacing={6}
            maxW="600px"
            w="100%"
            bg={useColorModeValue('white', 'gray.800')}
            p={8}
            borderRadius="xl"
            boxShadow="xl"
          >
            <WarningIcon boxSize={16} color="red.500" />
            
            <VStack spacing={2}>
              <Heading size="lg" textAlign="center">
                Something went wrong
              </Heading>
              <Text color="gray.500" textAlign="center">
                We encountered an unexpected error. Please try refreshing the page.
              </Text>
            </VStack>

            {this.state.error && (
              <Alert status="error" borderRadius="md">
                <AlertIcon />
                <VStack align="start" spacing={1} flex={1}>
                  <AlertTitle fontSize="sm">Error Message</AlertTitle>
                  <AlertDescription fontSize="xs">
                    {this.state.error.message}
                  </AlertDescription>
                </VStack>
              </Alert>
            )}

            <VStack spacing={3} w="100%">
              <Button
                colorScheme="blue"
                onClick={this.handleReset}
                w="100%"
              >
                Try Again
              </Button>
              
              <Button
                variant="outline"
                onClick={() => window.location.reload()}
                w="100%"
              >
                Reload Page
              </Button>

              {this.state.error && (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={this.toggleDetails}
                  w="100%"
                >
                  {this.state.showDetails ? 'Hide' : 'Show'} Technical Details
                </Button>
              )}
            </VStack>

            <Collapse in={this.state.showDetails} style={{ width: '100%' }}>
              <VStack
                spacing={3}
                w="100%"
                align="stretch"
                bg={useColorModeValue('gray.50', 'gray.700')}
                p={4}
                borderRadius="md"
              >
                {this.state.error && (
                  <Box>
                    <Text fontSize="xs" fontWeight="bold" mb={2}>
                      Error Stack:
                    </Text>
                    <Code
                      display="block"
                      whiteSpace="pre-wrap"
                      fontSize="xs"
                      p={3}
                      borderRadius="md"
                      overflow="auto"
                      maxH="200px"
                    >
                      {this.state.error.stack}
                    </Code>
                  </Box>
                )}

                {this.state.errorInfo && (
                  <Box>
                    <Text fontSize="xs" fontWeight="bold" mb={2}>
                      Component Stack:
                    </Text>
                    <Code
                      display="block"
                      whiteSpace="pre-wrap"
                      fontSize="xs"
                      p={3}
                      borderRadius="md"
                      overflow="auto"
                      maxH="200px"
                    >
                      {this.state.errorInfo.componentStack}
                    </Code>
                  </Box>
                )}
              </VStack>
            </Collapse>
          </VStack>
        </Box>
      )
    }

    return this.props.children
  }
}