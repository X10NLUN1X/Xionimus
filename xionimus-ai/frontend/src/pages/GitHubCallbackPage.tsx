import React, { useEffect, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Box, VStack, Spinner, Text, useToast } from '@chakra-ui/react'
import axios from 'axios'

const BACKEND_URL = import.meta.env.REACT_APP_BACKEND_URL || process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'

export const GitHubCallbackPage: React.FC = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const toast = useToast()
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code')
      const error = searchParams.get('error')

      if (error) {
        setStatus('error')
        toast({
          title: 'GitHub Autorisierung fehlgeschlagen',
          description: error,
          status: 'error',
          duration: 5000
        })
        setTimeout(() => navigate('/'), 2000)
        return
      }

      if (!code) {
        setStatus('error')
        toast({
          title: 'Fehler',
          description: 'Kein OAuth Code erhalten',
          status: 'error',
          duration: 5000
        })
        setTimeout(() => navigate('/'), 2000)
        return
      }

      try {
        // Exchange code for token
        const response = await axios.post(`${BACKEND_URL}/api/github/oauth/token`, {
          code
        })

        const { access_token, user } = response.data

        // Save to localStorage
        localStorage.setItem('github_access_token', access_token)
        localStorage.setItem('github_user', JSON.stringify(user))

        setStatus('success')
        toast({
          title: 'GitHub verbunden!',
          description: `Willkommen, ${user.name || user.login}!`,
          status: 'success',
          duration: 3000
        })

        // Redirect to chat
        setTimeout(() => navigate('/'), 1000)
      } catch (error) {
        console.error('OAuth exchange failed:', error)
        setStatus('error')
        toast({
          title: 'Fehler beim Verbinden',
          description: 'GitHub Autorisierung fehlgeschlagen',
          status: 'error',
          duration: 5000
        })
        setTimeout(() => navigate('/'), 2000)
      }
    }

    handleCallback()
  }, [searchParams, navigate, toast])

  return (
    <Box
      minH="100vh"
      display="flex"
      alignItems="center"
      justifyContent="center"
      bg="gray.50"
    >
      <VStack spacing={4}>
        {status === 'loading' && (
          <>
            <Spinner size="xl" color="blue.500" thickness="4px" />
            <Text fontSize="lg" fontWeight="600">
              Verbinde mit GitHub...
            </Text>
            <Text fontSize="sm" color="gray.500">
              Einen Moment bitte
            </Text>
          </>
        )}

        {status === 'success' && (
          <>
            <Box
              w="60px"
              h="60px"
              bg="green.500"
              borderRadius="full"
              display="flex"
              alignItems="center"
              justifyContent="center"
            >
              <Text fontSize="3xl">✓</Text>
            </Box>
            <Text fontSize="lg" fontWeight="600" color="green.600">
              Erfolgreich verbunden!
            </Text>
            <Text fontSize="sm" color="gray.500">
              Leite weiter...
            </Text>
          </>
        )}

        {status === 'error' && (
          <>
            <Box
              w="60px"
              h="60px"
              bg="red.500"
              borderRadius="full"
              display="flex"
              alignItems="center"
              justifyContent="center"
            >
              <Text fontSize="3xl">✕</Text>
            </Box>
            <Text fontSize="lg" fontWeight="600" color="red.600">
              Verbindung fehlgeschlagen
            </Text>
            <Text fontSize="sm" color="gray.500">
              Leite zurück...
            </Text>
          </>
        )}
      </VStack>
    </Box>
  )
}
