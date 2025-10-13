import React, { useState } from 'react'
import {
  Box,
  VStack,
  HStack,
  Text,
  Input,
  Button,
  Card,
  CardBody,
  Heading,
  FormControl,
  FormLabel,
  useColorModeValue,
  Alert,
  AlertIcon,
  Center,
  Spinner
} from '@chakra-ui/react'
import { useNavigate } from 'react-router-dom'

export const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('demo')
  const [password, setPassword] = useState('demo')
  const [isLoading, setIsLoading] = useState(false)
  const navigate = useNavigate()
  
  const cardBg = useColorModeValue('white', 'gray.800')
  
  const handleLogin = async () => {
    setIsLoading(true)
    
    // For MVP, just simulate login
    setTimeout(() => {
      setIsLoading(false)
      navigate('/chat')
    }, 1000)
  }
  
  return (
    <Center minH="100vh" bg={useColorModeValue('gray.50', 'gray.900')}>
      <Card bg={cardBg} w="full" maxW="md" shadow="xl">
        <CardBody p={8}>
          <VStack spacing={6}>
            {/* Header */}
            <VStack spacing={2} textAlign="center">
              <Box
                w={12}
                h={12}
                bg="primary.500"
                rounded="xl"
                display="flex"
                alignItems="center"
                justifyContent="center"
              >
                <Text color="white" fontWeight="bold" fontSize="xl">
                  EN
                </Text>
              </Box>
              <Heading size="lg">Xionimus AI</Heading>
              <Text color="gray.500" fontSize="sm">
                Modern Development Platform
              </Text>
            </VStack>
            
            {/* Demo Notice */}
            <Alert status="info" rounded="lg">
              <AlertIcon />
              <Box>
                <Text fontSize="sm">
                  <strong>MVP Demo Mode:</strong> Authentication is simplified for demonstration.
                  Full user management will be available in Phase 3.
                </Text>
              </Box>
            </Alert>
            
            {/* Login Form */}
            <VStack spacing={4} w="full">
              <FormControl>
                <FormLabel>Username</FormLabel>
                <Input
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Enter username"
                  variant="filled"
                />
              </FormControl>
              
              <FormControl>
                <FormLabel>Password</FormLabel>
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter password"
                  variant="filled"
                />
              </FormControl>
              
              <Button
                colorScheme="primary"
                size="lg"
                w="full"
                onClick={handleLogin}
                isLoading={isLoading}
                loadingText="Signing in..."
              >
                {isLoading ? <Spinner size="sm" /> : 'Sign In'}
              </Button>
            </VStack>
            
            {/* Footer */}
            <VStack spacing={2} textAlign="center">
              <Text fontSize="xs" color="gray.500">
                Full authentication coming in Phase 3
              </Text>
            </VStack>
          </VStack>
        </CardBody>
      </Card>
    </Center>
  )
}

export default LoginPage