/**
 * Local Error Logger for Crash Recovery
 * Stores errors in localStorage for debugging and recovery
 */

interface ErrorLog {
  timestamp: string
  message: string
  stack?: string
  componentStack?: string
  userAgent: string
  url: string
  sessionId?: string
}

const ERROR_LOG_KEY = 'xionimus_error_logs'
const MAX_LOGS = 50 // Keep last 50 errors

export class ErrorLogger {
  /**
   * Log an error to localStorage
   */
  static logError(error: Error, componentStack?: string, additionalInfo?: Record<string, any>) {
    try {
      const errorLog: ErrorLog = {
        timestamp: new Date().toISOString(),
        message: error.message,
        stack: error.stack,
        componentStack,
        userAgent: navigator.userAgent,
        url: window.location.href,
        ...additionalInfo
      }

      // Get existing logs
      const logs = this.getErrorLogs()
      
      // Add new log
      logs.unshift(errorLog)
      
      // Keep only MAX_LOGS
      const trimmedLogs = logs.slice(0, MAX_LOGS)
      
      // Save to localStorage
      localStorage.setItem(ERROR_LOG_KEY, JSON.stringify(trimmedLogs))
      
      // Also log to console for development
      console.error('[ErrorLogger]', errorLog)
    } catch (e) {
      console.error('Failed to log error:', e)
    }
  }

  /**
   * Get all error logs
   */
  static getErrorLogs(): ErrorLog[] {
    try {
      const logs = localStorage.getItem(ERROR_LOG_KEY)
      return logs ? JSON.parse(logs) : []
    } catch (e) {
      console.error('Failed to retrieve error logs:', e)
      return []
    }
  }

  /**
   * Clear all error logs
   */
  static clearErrorLogs() {
    try {
      localStorage.removeItem(ERROR_LOG_KEY)
    } catch (e) {
      console.error('Failed to clear error logs:', e)
    }
  }

  /**
   * Get recent errors (last 24 hours)
   */
  static getRecentErrors(): ErrorLog[] {
    const logs = this.getErrorLogs()
    const oneDayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)
    
    return logs.filter(log => new Date(log.timestamp) > oneDayAgo)
  }

  /**
   * Export logs as JSON for debugging
   */
  static exportLogs(): string {
    const logs = this.getErrorLogs()
    return JSON.stringify(logs, null, 2)
  }

  /**
   * Check if there was a recent crash
   */
  static hadRecentCrash(): boolean {
    const recentErrors = this.getRecentErrors()
    return recentErrors.length > 0
  }

  /**
   * Get crash recovery data
   */
  static getCrashRecoveryData(): { hasCrash: boolean; errorCount: number; lastError?: ErrorLog } {
    const recentErrors = this.getRecentErrors()
    return {
      hasCrash: recentErrors.length > 0,
      errorCount: recentErrors.length,
      lastError: recentErrors[0]
    }
  }
}

/**
 * Setup global error handlers
 */
export const setupGlobalErrorHandlers = () => {
  // Catch unhandled promise rejections
  window.addEventListener('unhandledrejection', (event) => {
    ErrorLogger.logError(
      new Error(`Unhandled Promise Rejection: ${event.reason}`),
      undefined,
      { type: 'unhandledRejection' }
    )
  })

  // Catch global errors
  window.addEventListener('error', (event) => {
    ErrorLogger.logError(
      event.error || new Error(event.message),
      undefined,
      { 
        type: 'globalError',
        filename: event.filename,
        lineno: event.lineno,
        colno: event.colno
      }
    )
  })
}
