import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } from './Modal'
import { Button } from './UI/Button'
import { Badge } from './UI/Badge'
import { useToast } from './UI/Toast'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'

interface ForkPreview {
  session_id: string
  session_name: string
  total_messages: number
  messages_to_summarize: number
  messages_to_keep_full: number
  estimated_summary_reduction: string
  preview: {
    first_message: string
    last_message: string
  }
}

interface SessionForkDialogProps {
  isOpen: boolean
  onClose: () => void
  sessionId: string | null
  onForkComplete: (newSessionId: string) => void
}

export const SessionForkDialog: React.FC<SessionForkDialogProps> = ({
  isOpen,
  onClose,
  sessionId,
  onForkComplete
}) => {
  const [isLoading, setIsLoading] = useState(false)
  const [preview, setPreview] = useState<ForkPreview | null>(null)
  const [isForkingProcess, setIsForkingProcess] = useState(false)
  const { showToast } = useToast()

  useEffect(() => {
    if (isOpen && sessionId) {
      loadPreview()
    }
  }, [isOpen, sessionId])

  const loadPreview = async () => {
    if (!sessionId) return

    setIsLoading(true)
    try {
      const token = localStorage.getItem('xionimus_token')
      const response = await axios.get(
        `${BACKEND_URL}/api/v1/session-fork/fork-preview/${sessionId}`,
        {
          headers: token ? {
            'Authorization': `Bearer ${token}`
          } : {}
        }
      )

      setPreview(response.data)
    } catch (error: any) {
      console.error('Failed to load fork preview:', error)
      showToast({
        title: 'Fehler',
        description: 'Vorschau konnte nicht geladen werden',
        status: 'error',
        duration: 3000
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleFork = async () => {
    if (!sessionId) return

    setIsForkingProcess(true)
    try {
      const token = localStorage.getItem('xionimus_token')
      const response = await axios.post(
        `${BACKEND_URL}/api/v1/session-fork/fork`,
        {
          session_id: sessionId,
          include_last_n_messages: 10
        },
        {
          headers: token ? {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          } : {
            'Content-Type': 'application/json'
          }
        }
      )

      const result = response.data

      showToast({
        title: '✅ Session geforkt!',
        description: result.message,
        status: 'success',
        duration: 5000
      })

      onForkComplete(result.new_session_id)
      onClose()
    } catch (error: any) {
      console.error('Failed to fork session:', error)
      showToast({
        title: 'Fork fehlgeschlagen',
        description: error.response?.data?.detail || 'Fehler beim Forken der Session',
        status: 'error',
        duration: 5000
      })
    } finally {
      setIsForkingProcess(false)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalContent>
        <ModalHeader onClose={onClose}>🔀 Session forken</ModalHeader>

        <ModalBody>
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-8 space-y-4">
              <div className="w-12 h-12 border-4 border-gold-500 border-t-transparent rounded-full animate-spin"></div>
              <p className="text-gray-400">Lade Vorschau...</p>
            </div>
          ) : preview ? (
            <div className="space-y-4">
              {/* Info Alert */}
              <div className="glossy-card p-4 bg-blue-500/10 border-blue-500/30">
                <div className="flex items-start gap-3">
                  <span className="text-blue-400 text-xl">ℹ️</span>
                  <div>
                    <p className="text-sm font-semibold text-blue-400 mb-1">Was ist ein Fork?</p>
                    <p className="text-sm text-gray-300">
                      Ein Fork erstellt eine neue Session mit einer kompakten Zusammenfassung der bisherigen Konversation. 
                      Die letzten 10 Nachrichten werden vollständig übernommen.
                    </p>
                  </div>
                </div>
              </div>

              {/* Stats Box */}
              <div className="glossy-card p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-semibold text-gray-300">Aktuelle Session:</span>
                  <Badge variant="default">{preview.session_name}</Badge>
                </div>

                <div className="h-px bg-gold-500/20"></div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">Gesamt-Nachrichten:</span>
                  <Badge variant="info">{preview.total_messages}</Badge>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">Werden zusammengefasst:</span>
                  <Badge variant="warning">{preview.messages_to_summarize}</Badge>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">Vollständig übernommen:</span>
                  <Badge variant="success">{preview.messages_to_keep_full}</Badge>
                </div>

                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-400">Geschätzte Reduzierung:</span>
                  <Badge variant="info">{preview.estimated_summary_reduction}</Badge>
                </div>
              </div>

              {/* Preview Box */}
              <div>
                <p className="text-sm font-semibold text-white mb-2">📋 Kontext-Preview:</p>
                <div className="space-y-2">
                  <div className="glossy-card p-3 bg-blue-500/10 border-l-4 border-blue-500">
                    <p className="text-xs text-gray-500 mb-1">Erste Nachricht:</p>
                    <p className="text-sm text-gray-200">{preview.preview.first_message}</p>
                  </div>
                  <div className="glossy-card p-3 bg-green-500/10 border-l-4 border-green-500">
                    <p className="text-xs text-gray-500 mb-1">Letzte Nachricht:</p>
                    <p className="text-sm text-gray-200">{preview.preview.last_message}</p>
                  </div>
                </div>
              </div>

              {/* Success Alert */}
              <div className="glossy-card p-4 bg-green-500/10 border-green-500/30">
                <div className="flex items-center gap-2">
                  <span className="text-green-400">✓</span>
                  <p className="text-sm text-gray-300">
                    Nach dem Fork kannst du nahtlos in der neuen Session weiterarbeiten!
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <p className="text-gray-400 text-center py-6">Keine Vorschau verfügbar</p>
          )}
        </ModalBody>

        <ModalFooter>
          <Button 
            variant="ghost" 
            onClick={onClose} 
            disabled={isForkingProcess}
          >
            Abbrechen
          </Button>
          <Button
            variant="primary"
            onClick={handleFork}
            loading={isForkingProcess}
            disabled={!preview}
            leftIcon={<span>🔀</span>}
          >
            Jetzt forken
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}
