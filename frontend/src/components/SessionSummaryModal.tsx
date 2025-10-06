import React, { useState } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } from './Modal'
import { Button } from './UI/Button'
import { Badge } from './UI/Badge'
import { useToast } from './UI/Toast'

interface SessionSummaryModalProps {
  isOpen: boolean
  onClose: () => void
  sessionId: string | null
  apiKeys: {
    openai: string
    anthropic: string
    perplexity: string
  }
  onSwitchSession: (sessionId: string) => void
}

interface SummaryData {
  session_id: string
  new_session_id: string
  summary: string
  context_transfer: string
  next_steps: Array<{
    title: string
    description: string
    action: string
  }>
  old_session_tokens: number
  timestamp: string
}

export const SessionSummaryModal: React.FC<SessionSummaryModalProps> = ({
  isOpen,
  onClose,
  sessionId,
  apiKeys,
  onSwitchSession
}) => {
  const [isLoading, setIsLoading] = useState(false)
  const [summaryData, setSummaryData] = useState<SummaryData | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [selectedOption, setSelectedOption] = useState<number | null>(null)
  const { showToast } = useToast()
  
  const API_BASE = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'

  React.useEffect(() => {
    if (isOpen && sessionId && !summaryData && !isLoading) {
      handleGenerateSummary()
    }
  }, [isOpen, sessionId])

  const handleGenerateSummary = async () => {
    if (!sessionId) {
      setError('Keine aktive Session')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const token = localStorage.getItem('xionimus_token')
      const response = await fetch(
        `${API_BASE}/api/session-management/summarize-and-fork`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify({
            session_id: sessionId,
            api_keys: apiKeys
          })
        }
      )

      if (!response.ok) {
        throw new Error('Zusammenfassung fehlgeschlagen')
      }

      const data: SummaryData = await response.json()
      setSummaryData(data)
      
      showToast({
        title: '✅ Session zusammengefasst',
        description: 'Neue Session wurde erstellt',
        status: 'success',
        duration: 3000
      })
    } catch (err: any) {
      console.error('Summary generation error:', err)
      setError(err.message || 'Fehler beim Generieren der Zusammenfassung')
      showToast({
        title: 'Fehler',
        description: err.message,
        status: 'error',
        duration: 5000
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleSelectOption = async (optionIndex: number) => {
    if (!summaryData) return

    setSelectedOption(optionIndex)
    const selectedAction = summaryData.next_steps[optionIndex]

    try {
      const token = localStorage.getItem('xionimus_token')
      await fetch(`${API_BASE}/api/session-management/continue-with-option`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          session_id: summaryData.new_session_id,
          option_action: selectedAction.action,
          api_keys: apiKeys
        })
      })

      onSwitchSession(summaryData.new_session_id)
      
      showToast({
        title: '✅ Neue Session gestartet',
        description: `"${selectedAction.title}" wird fortgesetzt`,
        status: 'success',
        duration: 3000
      })
      
      onClose()
      
      setTimeout(() => {
        setSummaryData(null)
        setSelectedOption(null)
        setError(null)
      }, 500)
    } catch (err: any) {
      console.error('Option selection error:', err)
      showToast({
        title: 'Fehler',
        description: 'Option konnte nicht ausgewählt werden',
        status: 'error',
        duration: 3000
      })
      setSelectedOption(null)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalContent>
        <ModalHeader onClose={onClose}>
          📋 Session Zusammenfassung
        </ModalHeader>

        <ModalBody>
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-12 space-y-4">
              <div className="w-16 h-16 border-4 border-gold-500 border-t-transparent rounded-full animate-spin"></div>
              <p className="text-gray-300">AI generiert Zusammenfassung...</p>
              <p className="text-sm text-gray-500">Dies kann einen Moment dauern</p>
            </div>
          ) : error ? (
            <div className="glossy-card p-6 bg-red-500/10 border-red-500/30">
              <div className="flex items-start gap-3">
                <span className="text-red-400 text-2xl">⚠️</span>
                <div>
                  <h3 className="font-semibold text-red-400 mb-2">Fehler</h3>
                  <p className="text-gray-300">{error}</p>
                  <Button
                    variant="secondary"
                    size="sm"
                    onClick={handleGenerateSummary}
                    className="mt-4"
                  >
                    Erneut versuchen
                  </Button>
                </div>
              </div>
            </div>
          ) : summaryData ? (
            <div className="space-y-4">
              {/* Success Alert */}
              <div className="glossy-card p-4 bg-green-500/10 border-green-500/30">
                <div className="flex items-center gap-2">
                  <span className="text-green-400 text-xl">✓</span>
                  <div>
                    <p className="text-sm font-semibold text-green-400">Session erfolgreich zusammengefasst!</p>
                    <p className="text-xs text-gray-400 mt-1">
                      Tokens reduziert: {summaryData.old_session_tokens.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>

              {/* Summary Content */}
              <div className="glossy-card p-4">
                <h3 className="text-sm font-semibold text-gold-400 mb-3">📝 Zusammenfassung:</h3>
                <div className="prose prose-sm prose-invert max-w-none">
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {summaryData.summary}
                  </ReactMarkdown>
                </div>
              </div>

              {/* Context Transfer */}
              {summaryData.context_transfer && (
                <div className="glossy-card p-4 bg-blue-500/10 border-blue-500/30">
                  <h3 className="text-sm font-semibold text-blue-400 mb-2">🔄 Kontext-Übertragung:</h3>
                  <p className="text-sm text-gray-300">{summaryData.context_transfer}</p>
                </div>
              )}

              {/* Next Steps */}
              {summaryData.next_steps && summaryData.next_steps.length > 0 && (
                <div>
                  <h3 className="text-sm font-semibold text-white mb-3">🚀 Wie möchten Sie fortfahren?</h3>
                  <div className="space-y-2">
                    {summaryData.next_steps.map((step, index) => (
                      <button
                        key={index}
                        onClick={() => handleSelectOption(index)}
                        disabled={selectedOption !== null}
                        className={`
                          w-full glossy-card p-4 text-left
                          transition-all duration-200
                          ${selectedOption === index 
                            ? 'bg-gold-500/20 border-gold-500' 
                            : 'hover:bg-accent-blue/30 hover:border-gold-500/50'
                          }
                          disabled:opacity-50 disabled:cursor-not-allowed
                        `}
                      >
                        <div className="flex items-start gap-3">
                          <span className="text-2xl">{index === 0 ? '1️⃣' : index === 1 ? '2️⃣' : '3️⃣'}</span>
                          <div className="flex-1">
                            <h4 className="font-semibold text-white mb-1">{step.title}</h4>
                            <p className="text-sm text-gray-400">{step.description}</p>
                          </div>
                          {selectedOption === index && (
                            <Badge variant="success">Ausgewählt</Badge>
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Info */}
              <div className="glossy-card p-3 bg-blue-500/5 border-blue-500/20">
                <p className="text-xs text-gray-400">
                  💡 Die neue Session enthält die kompakte Zusammenfassung und ist bereit für Ihre Fortsetzung.
                </p>
              </div>
            </div>
          ) : null}
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" onClick={onClose}>
            Schließen
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}
