import React, { useEffect, useState } from 'react'
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } from './Modal'
import { Button } from './UI/Button'
import { Badge } from './UI/Badge'
import { ErrorLogger } from '../utils/errorLogger'

export const CrashRecovery: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false)
  const [crashData, setCrashData] = useState<ReturnType<typeof ErrorLogger.getCrashRecoveryData> | null>(null)

  useEffect(() => {
    // Check for recent crashes on mount
    const data = ErrorLogger.getCrashRecoveryData()
    if (data.hasCrash && data.errorCount > 0) {
      setCrashData(data)
      setIsOpen(true)
    }
  }, [])

  const handleDismiss = () => {
    setIsOpen(false)
  }

  const handleClearLogs = () => {
    ErrorLogger.clearErrorLogs()
    setIsOpen(false)
  }

  if (!crashData || !crashData.hasCrash) return null

  return (
    <Modal isOpen={isOpen} onClose={handleDismiss} size="lg">
      <ModalContent className="border-red-500/50 bg-red-500/5">
        <ModalHeader>
          <div className="flex items-center gap-3">
            <svg className="w-6 h-6 text-orange-400" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            <div className="space-y-1">
              <h2 className="text-lg font-semibold text-white">
                App Recovered from Crash
              </h2>
              <Badge variant="warning" className="text-xs">
                {crashData.errorCount} error{crashData.errorCount > 1 ? 's' : ''} detected
              </Badge>
            </div>
          </div>
        </ModalHeader>

        <ModalBody>
          <div className="space-y-4">
            {/* Alert Message */}
            <div className="glossy-card p-4 bg-orange-500/10 border-orange-500/30">
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-orange-400 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                <div>
                  <h3 className="font-semibold text-orange-400 mb-1">
                    The app encountered an error
                  </h3>
                  <p className="text-sm text-gray-300">
                    The application has automatically recovered. Your data should be safe, but you may want to refresh the page.
                  </p>
                </div>
              </div>
            </div>

            {/* Error Details */}
            {crashData.lastError && (
              <div>
                <p className="text-sm font-semibold text-gray-300 mb-2">Last Error:</p>
                <div className="glossy-card p-3 bg-red-500/10 border-red-500/30">
                  <code className="text-xs text-red-300 font-mono break-words">
                    {typeof crashData.lastError === 'string' 
                      ? crashData.lastError 
                      : crashData.lastError.message || JSON.stringify(crashData.lastError, null, 2)
                    }
                  </code>
                </div>
              </div>
            )}

            {/* Timestamp */}
            {crashData.timestamp && (
              <p className="text-xs text-gray-500">
                Occurred at: {new Date(crashData.timestamp).toLocaleString()}
              </p>
            )}

            {/* Recovery Info */}
            <div className="glossy-card p-4 bg-green-500/10 border-green-500/30">
              <div className="flex items-start gap-3">
                <svg className="w-5 h-5 text-green-400 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <div>
                  <h4 className="font-semibold text-green-400 mb-1">
                    Recovery Successful
                  </h4>
                  <p className="text-sm text-gray-300">
                    The app is now stable. Error logs have been saved for debugging.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </ModalBody>

        <ModalFooter>
          <Button 
            variant="ghost" 
            onClick={handleDismiss}
            size="sm"
          >
            Continue
          </Button>
          <Button 
            variant="secondary" 
            onClick={handleClearLogs}
            size="sm"
          >
            Clear Logs & Dismiss
          </Button>
          <Button
            variant="primary"
            onClick={() => window.location.reload()}
            size="sm"
            leftIcon={
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            }
          >
            Refresh Page
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}