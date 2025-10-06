import React, { Suspense, lazy } from 'react'
import { Routes, Route } from 'react-router-dom'
import { ErrorBoundary } from './components/ErrorBoundary/ErrorBoundary'
import { GitHubProvider } from './contexts/GitHubContext'
import { LanguageProvider } from './contexts/LanguageContext'
import { ThemeProvider } from './contexts/ThemeContext'
import { SkipLinks } from './components/SkipLink'
import { Navigation } from './components/Navigation/Navigation'

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
  <div className="flex items-center justify-center min-h-screen bg-primary-dark">
    <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-gold-500"></div>
  </div>
)

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <LanguageProvider>
          <GitHubProvider>
            <SkipLinks />
            <div className="min-h-screen bg-primary-dark bg-geometric" id="app-root">
              <Navigation />
              <Suspense fallback={<LoadingFallback />}>
                <main id="main-content" tabIndex={-1}>
                  <Routes>
                    <Route path="/login" element={<LoginPage />} />
                    <Route path="/github/callback" element={<GitHubCallbackPage />} />
                    <Route path="/" element={<ChatPage />} />
                    <Route path="/chat" element={<ChatPage />} />
                    <Route path="/settings" element={<SettingsPage />} />
                    <Route path="/session-summary/:sessionId" element={<SessionSummaryPage />} />
                  </Routes>
                </main>
              </Suspense>
            </div>
          </GitHubProvider>
        </LanguageProvider>
      </ThemeProvider>
    </ErrorBoundary>
  )
}

export default App