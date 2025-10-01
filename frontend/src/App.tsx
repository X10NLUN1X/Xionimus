import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Box, useColorModeValue } from '@chakra-ui/react'
import { ChatPage } from './pages/ChatPage'
import { SettingsPage } from './pages/SettingsPage'
import { CodeReviewPage } from './pages/CodeReviewPage'
import { LoginPage } from './pages/LoginPage'
import { GitHubCallbackPage } from './pages/GitHubCallbackPage'
import { ErrorBoundary } from './components/ErrorBoundary/ErrorBoundary'
import { GitHubProvider } from './contexts/GitHubContext'
import { LanguageProvider } from './contexts/LanguageContext'
import { ThemeProvider } from './contexts/ThemeContext'

function App() {
  const bgColor = useColorModeValue('gray.50', '#0a1628')
  
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <LanguageProvider>
          <GitHubProvider>
            <Box minH="100vh" bg={bgColor}>
              <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route path="/github/callback" element={<GitHubCallbackPage />} />
                <Route path="/" element={<ChatPage />} />
                <Route path="/chat" element={<ChatPage />} />
                <Route path="/settings" element={<SettingsPage />} />
                <Route path="/code-review" element={<CodeReviewPage />} />
              </Routes>
            </Box>
          </GitHubProvider>
        </LanguageProvider>
      </ThemeProvider>
    </ErrorBoundary>
  )
}

export default App
