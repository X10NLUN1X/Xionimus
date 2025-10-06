import React, { Component, ErrorInfo, ReactNode } from 'react'
import { Button } from './UI/Button'
import { Card } from './UI/Card'

interface Props {
  children: ReactNode
}

interface State {
  hasError: boolean
  error: Error | null
  errorInfo: ErrorInfo | null
}

class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null
    }
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null
    }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
    
    this.setState({
      error,
      errorInfo
    })
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null
    })
    
    window.location.href = '/'
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-primary-dark bg-geometric flex items-center justify-center p-4">
          <Card className="max-w-2xl w-full">
            <div className="space-y-6 text-center">
              {/* Error Icon & Title */}
              <div className="space-y-3">
                <div className="text-6xl">⚠️</div>
                <h1 className="text-3xl font-bold bg-gradient-to-r from-red-400 via-red-500 to-red-400 bg-clip-text text-transparent">
                  Oops! Something went wrong
                </h1>
                <p className="text-gray-400 text-lg">
                  An unexpected error occurred. We've logged the issue and will look into it.
                </p>
              </div>

              {/* Error Details (Development Only) */}
              {import.meta.env.DEV && this.state.error && (
                <div className="glossy-card border-red-500/50 bg-red-500/10 p-4 text-left max-h-[300px] overflow-auto">
                  <p className="font-bold text-red-400 mb-2">
                    Error Details (Development Only):
                  </p>
                  <pre className="text-sm text-red-300 whitespace-pre-wrap font-mono">
                    {this.state.error.toString()}
                  </pre>
                  
                  {this.state.errorInfo && (
                    <>
                      <p className="font-bold text-red-400 mt-4 mb-2">
                        Component Stack:
                      </p>
                      <pre className="text-xs text-gray-400 whitespace-pre-wrap font-mono">
                        {this.state.errorInfo.componentStack}
                      </pre>
                    </>
                  )}
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <Button
                  variant="primary"
                  size="lg"
                  onClick={this.handleReset}
                  leftIcon={
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  }
                >
                  Reload Application
                </Button>
                
                <Button
                  variant="ghost"
                  onClick={() => window.history.back()}
                  leftIcon={
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                    </svg>
                  }
                >
                  Go Back
                </Button>
              </div>

              {/* Support Message */}
              <p className="text-sm text-gray-500 mt-4">
                If this problem persists, please contact support.
              </p>
            </div>
          </Card>
        </div>
      )
    }

    return this.props.children
  }
}

export default ErrorBoundary
