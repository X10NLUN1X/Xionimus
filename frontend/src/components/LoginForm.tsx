import React, { useState } from 'react'
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Text,
  useColorModeValue,
  Alert,
  AlertIcon,
  Link,
  Divider,
  HStack,
  Container
} from '@chakra-ui/react'
import { useApp } from '../contexts/AppContext'

interface LoginFormProps {
  onRegisterClick?: () => void
}

export const LoginForm: React.FC<LoginFormProps> = ({ onRegisterClick }) => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const { login } = useApp()
  
  const bgColor = useColorModeValue('white', 'rgba(15, 30, 50, 0.8)')
  const borderColor = useColorModeValue('gray.200', 'rgba(0, 212, 255, 0.3)')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)
    
    try {
      await login(username.trim(), password.trim())
    } catch (error) {
      setError('Login fehlgeschlagen. Bitte überprüfen Sie Ihre Eingaben.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Container maxW="md" centerContent>
      <Box
        w="full"
        maxW="400px"
        bg={bgColor}
        p={8}
        borderRadius="xl"
        border="1px solid"
        borderColor={borderColor}
        boxShadow="0 10px 40px rgba(0, 212, 255, 0.2)"
      >
        <VStack spacing={6} align="stretch">
          {/* Header */}
          <VStack spacing={2}>
            <Box
              w="60px"
              h="60px"
              bg="linear-gradient(135deg, #0088cc, #0094ff)"
              borderRadius="xl"
              display="flex"
              alignItems="center"
              justifyContent="center"
              boxShadow="0 4px 20px rgba(0, 212, 255, 0.4)"
            >
              <Text color="white" fontWeight="900" fontSize="2xl" textShadow="0 0 10px rgba(255, 255, 255, 0.8)">X</Text>
            </Box>
            <Text fontSize="2xl" fontWeight="700" color={useColorModeValue('#0094ff', '#0088cc')}>
              Xionimus AI
            </Text>
            <Text fontSize="md" color="gray.500">
              Melden Sie sich an, um fortzufahren
            </Text>
          </VStack>

          {/* Error Alert */}
          {error && (
            <Alert status="error" borderRadius="md">
              <AlertIcon />
              {error}
            </Alert>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit}>
            <VStack spacing={4}>
              <FormControl isRequired>
                <FormLabel>Benutzername</FormLabel>
                <Input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Ihr Benutzername"
                  bg={useColorModeValue('gray.50', 'rgba(0, 0, 0, 0.2)')}
                  border="2px solid"
                  borderColor={borderColor}
                  _focus={{
                    borderColor: '#0088cc',
                    boxShadow: '0 0 0 1px #0088cc'
                  }}
                />
              </FormControl>

              <FormControl isRequired>
                <FormLabel>Passwort</FormLabel>
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Ihr Passwort"
                  bg={useColorModeValue('gray.50', 'rgba(0, 0, 0, 0.2)')}
                  border="2px solid"
                  borderColor={borderColor}
                  _focus={{
                    borderColor: '#0088cc',
                    boxShadow: '0 0 0 1px #0088cc'
                  }}
                />
              </FormControl>

              <Button
                type="submit"
                w="full"
                bg="linear-gradient(135deg, #0088cc, #0094ff)"
                color="white"
                size="lg"
                isLoading={isLoading}
                loadingText="Anmeldung..."
                _hover={{
                  bg: "linear-gradient(135deg, #0094ff, #0088cc)",
                  boxShadow: "0 0 20px rgba(0, 212, 255, 0.6)"
                }}
                boxShadow="0 4px 15px rgba(0, 212, 255, 0.4)"
              >
                Anmelden
              </Button>
            </VStack>
          </form>

          {/* Register Link */}
          <Divider />
          <HStack justify="center" spacing={2}>
            <Text color="gray.500" fontSize="sm">
              Noch kein Konto?
            </Text>
            <Link
              color={useColorModeValue('#0094ff', '#0088cc')}
              fontSize="sm"
              fontWeight="600"
              onClick={onRegisterClick}
              cursor="pointer"
              _hover={{ textDecoration: 'underline' }}
            >
              Jetzt registrieren
            </Link>
          </HStack>

          {/* Demo Account Info */}
          <Box
            bg={useColorModeValue('blue.50', 'rgba(0, 212, 255, 0.1)')}
            p={3}
            borderRadius="md"
            fontSize="sm"
          >
            <Text fontWeight="600" color={useColorModeValue('#0094ff', '#0088cc')} mb={1}>
              Demo-Zugang:
            </Text>
            <Text color="gray.600">
              <strong>Benutzername:</strong> demo<br />
              <strong>Passwort:</strong> demo123
            </Text>
          </Box>
        </VStack>
      </Box>
    </Container>
  )
}