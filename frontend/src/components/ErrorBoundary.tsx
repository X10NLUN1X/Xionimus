import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Box, Heading, Text, Button, VStack, Code } from '@chakra-ui/react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * Error Boundary Component
 * Catches JavaScript errors anywhere in child component tree
 * and displays fallback UI instead of crashing
 */
class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    };
  }

  static getDerivedStateFromError(error: Error): State {
    // Update state so the next render shows the fallback UI
    return {
      hasError: true,
      error,
      errorInfo: null
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Log the error to an error reporting service
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    
    this.setState({
      error,
      errorInfo
    });
    
    // TODO: Send to error tracking service (Sentry, LogRocket, etc.)
    // logErrorToService(error, errorInfo);
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    });
  };

  render() {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <Box
          minH="100vh"
          display="flex"
          alignItems="center"
          justifyContent="center"
          bg="gray.900"
          color="white"
          p={8}
        >
          <VStack spacing={6} maxW="2xl" textAlign="center">
            <Heading size="2xl" bgGradient="linear(to-r, red.400, orange.400)" bgClip="text">
              Oops! Something went wrong
            </Heading>
            
            <Text fontSize="lg" color="gray.400">
              We're sorry for the inconvenience. The application encountered an unexpected error.
            </Text>

            <Button
              onClick={this.handleReset}
              colorScheme="orange"
              size="lg"
              _hover={{ transform: 'translateY(-2px)', boxShadow: 'lg' }}
              transition="all 0.2s"
            >
              Try Again
            </Button>

            <Button
              onClick={() => window.location.href = '/'}
              variant="ghost"
              size="md"
            >
              Return to Home
            </Button>

            {/* Error details (development only) */}
            {process.env.NODE_ENV === 'development' && this.state.error && (
              <Box mt={8} w="full" textAlign="left">
                <Text fontWeight="bold" mb={2}>Error Details:</Text>
                <Code
                  p={4}
                  borderRadius="md"
                  display="block"
                  whiteSpace="pre-wrap"
                  bg="gray.800"
                  color="red.300"
                  fontSize="sm"
                >
                  {this.state.error.toString()}
                  {this.state.errorInfo?.componentStack}
                </Code>
              </Box>
            )}
          </VStack>
        </Box>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;