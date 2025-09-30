import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Box, useColorModeValue } from '@chakra-ui/react'
import { ChatPage } from './pages/ChatPage'
import { SettingsPage } from './pages/SettingsPage'
import { LoginPage } from './pages/LoginPage'
import { GitHubCallbackPage } from './pages/GitHubCallbackPage'
import { ErrorBoundary } from './components/ErrorBoundary/ErrorBoundary'
import { GitHubProvider } from './contexts/GitHubContext'
import { LanguageProvider } from './contexts/LanguageContext'

function App() {
  const bgColor = useColorModeValue('gray.50', 'gray.900')
  
  return (
    <ErrorBoundary>
      <LanguageProvider>
        <GitHubProvider>
          <Box minH="100vh" bg={bgColor}>
            <Routes>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/github/callback" element={<GitHubCallbackPage />} />
              <Route path="/" element={<ChatPage />} />
              <Route path="/chat" element={<ChatPage />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </Box>
        </GitHubProvider>
      </LanguageProvider>
    </ErrorBoundary>
  )
}

export default App
