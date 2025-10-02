import React, { useState } from 'react'
import {
  Box,
  Button,
  FormControl,
  FormLabel,
  Input,
  VStack,
  Text,
  useToast,
  Container,
  Heading,
  Link,
  FormErrorMessage,
  InputGroup,
  InputRightElement,
  IconButton,
} from '@chakra-ui/react'
import { ViewIcon, ViewOffIcon } from '@chakra-ui/icons'

interface RegisterFormProps {
  onRegister: (username: string, email: string, password: string) => Promise<void>
  onSwitchToLogin: () => void
}

export const RegisterForm: React.FC<RegisterFormProps> = ({ onRegister, onSwitchToLogin }) => {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const toast = useToast()

  // Validation
  const isUsernameValid = username.length >= 3
  const isEmailValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
  const isPasswordValid = password.length >= 6
  const doPasswordsMatch = password === confirmPassword && password.length > 0

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    // Validation
    if (!isUsernameValid) {
      setError('Benutzername muss mindestens 3 Zeichen lang sein.')
      return
    }

    if (!isEmailValid) {
      setError('Bitte geben Sie eine gültige E-Mail-Adresse ein.')
      return
    }

    if (!isPasswordValid) {
      setError('Passwort muss mindestens 6 Zeichen lang sein.')
      return
    }

    if (!doPasswordsMatch) {
      setError('Passwörter stimmen nicht überein.')
      return
    }

    setIsLoading(true)

    try {
      await onRegister(username.trim(), email.trim(), password)
      
      toast({
        title: '✅ Account erstellt!',
        description: 'Sie werden automatisch eingeloggt.',
        status: 'success',
        duration: 3000,
        isClosable: true,
        position: 'top',
      })
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Registrierung fehlgeschlagen. Bitte versuchen Sie es erneut.'
      setError(errorMessage)
      
      toast({
        title: 'Registrierung fehlgeschlagen',
        description: errorMessage,
        status: 'error',
        duration: 5000,
        isClosable: true,
        position: 'top',
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Container maxW="md" py={12}>
      <Box
        bg="rgba(26, 32, 44, 0.8)"
        backdropFilter="blur(10px)"
        p={8}
        borderRadius="xl"
        border="1px solid rgba(0, 212, 255, 0.2)"
        boxShadow="0 8px 32px rgba(0, 212, 255, 0.1)"
      >
        <VStack spacing={6} align="stretch">
          <Box textAlign="center">
            <Heading size="lg" mb={2} color="#00d4ff">
              Neuen Account erstellen
            </Heading>
            <Text fontSize="sm" color="gray.400">
              Erstellen Sie Ihren ersten Account für Xionimus AI
            </Text>
          </Box>

          <form onSubmit={handleSubmit}>
            <VStack spacing={4}>
              {/* Username */}
              <FormControl isInvalid={username.length > 0 && !isUsernameValid} isRequired>
                <FormLabel color="gray.300">Benutzername</FormLabel>
                <Input
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="Mindestens 3 Zeichen"
                  bg="rgba(0, 0, 0, 0.3)"
                  border="1px solid rgba(255, 255, 255, 0.1)"
                  _hover={{ borderColor: '#00d4ff' }}
                  _focus={{ borderColor: '#00d4ff', boxShadow: '0 0 0 1px #00d4ff' }}
                  autoFocus
                />
                {username.length > 0 && !isUsernameValid && (
                  <FormErrorMessage>Mindestens 3 Zeichen erforderlich</FormErrorMessage>
                )}
              </FormControl>

              {/* Email */}
              <FormControl isInvalid={email.length > 0 && !isEmailValid} isRequired>
                <FormLabel color="gray.300">E-Mail</FormLabel>
                <Input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="ihre@email.com"
                  bg="rgba(0, 0, 0, 0.3)"
                  border="1px solid rgba(255, 255, 255, 0.1)"
                  _hover={{ borderColor: '#00d4ff' }}
                  _focus={{ borderColor: '#00d4ff', boxShadow: '0 0 0 1px #00d4ff' }}
                />
                {email.length > 0 && !isEmailValid && (
                  <FormErrorMessage>Ungültige E-Mail-Adresse</FormErrorMessage>
                )}
              </FormControl>

              {/* Password */}
              <FormControl isInvalid={password.length > 0 && !isPasswordValid} isRequired>
                <FormLabel color="gray.300">Passwort</FormLabel>
                <InputGroup>
                  <Input
                    type={showPassword ? 'text' : 'password'}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Mindestens 6 Zeichen"
                    bg="rgba(0, 0, 0, 0.3)"
                    border="1px solid rgba(255, 255, 255, 0.1)"
                    _hover={{ borderColor: '#00d4ff' }}
                    _focus={{ borderColor: '#00d4ff', boxShadow: '0 0 0 1px #00d4ff' }}
                  />
                  <InputRightElement>
                    <IconButton
                      aria-label={showPassword ? 'Passwort verbergen' : 'Passwort anzeigen'}
                      icon={showPassword ? <ViewOffIcon /> : <ViewIcon />}
                      onClick={() => setShowPassword(!showPassword)}
                      variant="ghost"
                      size="sm"
                    />
                  </InputRightElement>
                </InputGroup>
                {password.length > 0 && !isPasswordValid && (
                  <FormErrorMessage>Mindestens 6 Zeichen erforderlich</FormErrorMessage>
                )}
              </FormControl>

              {/* Confirm Password */}
              <FormControl isInvalid={confirmPassword.length > 0 && !doPasswordsMatch} isRequired>
                <FormLabel color="gray.300">Passwort bestätigen</FormLabel>
                <InputGroup>
                  <Input
                    type={showConfirmPassword ? 'text' : 'password'}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Passwort wiederholen"
                    bg="rgba(0, 0, 0, 0.3)"
                    border="1px solid rgba(255, 255, 255, 0.1)"
                    _hover={{ borderColor: '#00d4ff' }}
                    _focus={{ borderColor: '#00d4ff', boxShadow: '0 0 0 1px #00d4ff' }}
                  />
                  <InputRightElement>
                    <IconButton
                      aria-label={showConfirmPassword ? 'Passwort verbergen' : 'Passwort anzeigen'}
                      icon={showConfirmPassword ? <ViewOffIcon /> : <ViewIcon />}
                      onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      variant="ghost"
                      size="sm"
                    />
                  </InputRightElement>
                </InputGroup>
                {confirmPassword.length > 0 && !doPasswordsMatch && (
                  <FormErrorMessage>Passwörter stimmen nicht überein</FormErrorMessage>
                )}
              </FormControl>

              {/* Error Message */}
              {error && (
                <Box
                  bg="rgba(229, 62, 62, 0.1)"
                  border="1px solid rgba(229, 62, 62, 0.3)"
                  borderRadius="md"
                  p={3}
                  w="100%"
                >
                  <Text color="red.300" fontSize="sm">
                    {error}
                  </Text>
                </Box>
              )}

              {/* Submit Button */}
              <Button
                type="submit"
                colorScheme="blue"
                bg="#00d4ff"
                color="black"
                w="100%"
                size="lg"
                isLoading={isLoading}
                loadingText="Account wird erstellt..."
                isDisabled={
                  !isUsernameValid ||
                  !isEmailValid ||
                  !isPasswordValid ||
                  !doPasswordsMatch ||
                  isLoading
                }
                _hover={{ bg: '#00b8e6' }}
                _active={{ bg: '#009cc7' }}
              >
                Account erstellen
              </Button>
            </VStack>
          </form>

          {/* Switch to Login */}
          <Box textAlign="center" pt={4} borderTop="1px solid rgba(255, 255, 255, 0.1)">
            <Text fontSize="sm" color="gray.400">
              Haben Sie bereits einen Account?{' '}
              <Link
                color="#00d4ff"
                onClick={onSwitchToLogin}
                fontWeight="bold"
                _hover={{ textDecoration: 'underline' }}
              >
                Jetzt anmelden
              </Link>
            </Text>
          </Box>
        </VStack>
      </Box>
    </Container>
  )
}
