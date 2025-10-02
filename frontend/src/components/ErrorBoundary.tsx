import React, { Component, ErrorInfo, ReactNode } from 'react'
import { Box, Text, Button, VStack, Code, Heading } from '@chakra-ui/react'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    }
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    
    this.setState({
      error,
      errorInfo
    })
    
    // Send to monitoring service (Sentry, etc.)
    // if (window.Sentry) {
    //   window.Sentry.captureException(error, { extra: errorInfo })
    // }
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    })
    
    // Reload page or navigate to home
    window.location.href = '/'
  }

  render() {
    if (this.state.hasError) {
      return (
        <Box
          minH="100vh"
          bg="gray.900"
          color="white"
          display="flex"
          alignItems="center"
          justifyContent="center"
          p={8}
        >
          <VStack spacing={6} maxW="600px" textAlign="center">
            <Heading size="xl" color="red.400">
              ⚠️ Oops! Something went wrong
            </Heading>
            
            <Text fontSize="lg" color="gray.300">
              An unexpected error occurred. We've logged the issue and will look into it.
            </Text>
            
            {import.meta.env.DEV && this.state.error && (
              <Box
                w="full"
                bg="gray.800"
                p={4}
                borderRadius="md"
                border="1px solid"
                borderColor="red.600"
                textAlign="left"
                overflow="auto"
                maxH="300px"
              >
                <Text fontWeight="bold" color="red.400" mb={2}>
                  Error Details (Development Only):
                </Text>
                <Code
                  display="block"
                  whiteSpace="pre-wrap"
                  fontSize="sm"
                  bg="transparent"
                  color="red.300"
                >
                  {this.state.error.toString()}
                </Code>
                
                {this.state.errorInfo && (
                  <>
                    <Text fontWeight="bold" color="red.400" mt={4} mb={2}>
                      Component Stack:
                    </Text>
                    <Code
                      display="block"
                      whiteSpace="pre-wrap"
                      fontSize="xs"
                      bg="transparent"
                      color="gray.400"
                    >
                      {this.state.errorInfo.componentStack}
                    </Code>
                  </>
                )}
              </Box>
            )}
            
            <VStack spacing={3}>
              <Button
                colorScheme="blue"
                size="lg"
                onClick={this.handleReset}
              >
                🔄 Reload Application
              </Button>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={() => window.history.back()}
              >
                ← Go Back
              </Button>
            </VStack>
            
            <Text fontSize="sm" color="gray.500" mt={4}>
              If this problem persists, please contact support.
            </Text>
          </VStack>
        </Box>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
