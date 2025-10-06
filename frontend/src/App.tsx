import React, { Suspense, lazy } from 'react'
import { Routes, Route } from 'react-router-dom'
import { Box, Spinner, Center } from '@chakra-ui/react'
import { ErrorBoundary } from './components/ErrorBoundary/ErrorBoundary'
import { GitHubProvider } from './contexts/GitHubContext'
import { LanguageProvider } from './contexts/LanguageContext'
import { ThemeProvider } from './contexts/ThemeContext'
import { SkipLinks } from './components/SkipLink'

// Import accessibility styles
import './styles/accessibility.css'

// Lazy load pages for code splitting
const ChatPage = lazy(() => import('./pages/ChatPage').then(module => ({ default: module.ChatPage })))
const SettingsPage = lazy(() => import('./pages/SettingsPage').then(module => ({ default: module.SettingsPage })))
const LoginPage = lazy(() => import('./pages/LoginPage').then(module => ({ default: module.LoginPage })))
const GitHubCallbackPage = lazy(() => import('./pages/GitHubCallbackPage').then(module => ({ default: module.GitHubCallbackPage })))
const SessionSummaryPage = lazy(() => import('./pages/SessionSummaryPage').then(module => ({ default: module.SessionSummaryPage })))

// Loading component
const LoadingFallback = () => (
  <Center h="100vh" bg="#0a1628">
    <Spinner
      thickness="4px"
      speed="0.65s"
      emptyColor="gray.700"
      color="blue.500"
      size="xl"
    />
  </Center>
)

function App() {
  // Dark mode only - no light mode
  const bgColor = '#0a1628'
  
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <LanguageProvider>
          <GitHubProvider>
            <SkipLinks />
            <Box minH="100vh" bg={bgColor} id="app-root">
              <Suspense fallback={<LoadingFallback />}>
                <Box as="main" id="main-content" tabIndex={-1}>
                  <Routes>
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/github/callback" element={<GitHubCallbackPage />} />
                    <Route path="/" element={<ChatPage />} />
                    <Route path="/chat" element={<ChatPage />} />
                    <Route path="/settings" element={<SettingsPage />} />
                    <Route path="/agent" element={<AgentSettingsPage />} />
                    <Route path="/session-summary/:sessionId" element={<SessionSummaryPage />} />
                  </Routes>
                </Box>
              </Suspense>
            </Box>
          </GitHubProvider>
        </LanguageProvider>
      </ThemeProvider>
    </ErrorBoundary>
  )
}

export default App
