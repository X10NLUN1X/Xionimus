import React from 'react'
import ReactDOM from 'react-dom/client'
import { ChakraProvider } from '@chakra-ui/react'
import { BrowserRouter } from 'react-router-dom'
import App from './App.tsx'
import theme from './theme/index.ts'
import { AppProvider } from './contexts/AppContext.tsx'
import { CrashRecovery } from './components/CrashRecovery.tsx'
import ErrorBoundary from './components/ErrorBoundary.tsx'
import { setupGlobalErrorHandlers } from './utils/errorLogger.ts'

// Setup global error handlers for crash recovery
setupGlobalErrorHandlers()

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <ChakraProvider theme={theme}>
        <BrowserRouter
          future={{
            v7_startTransition: true,
            v7_relativeSplatPath: true,
          }}
        >
          <AppProvider>
            <CrashRecovery />
            <App />
          </AppProvider>
        </BrowserRouter>
      </ChakraProvider>
    </ErrorBoundary>
  </React.StrictMode>,
)