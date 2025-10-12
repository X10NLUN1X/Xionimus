import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } from './Modal'
import { Button } from './UI/Button'
import { Input } from './UI/Input'
import { Badge } from './UI/Badge'
import { useToast } from './UI/Toast'
import { getGitHubOAuthStatus, initiateGitHubOAuth } from '../services/githubOAuthService'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'

interface GitHubPushDialogProps {
  isOpen: boolean
  onClose: () => void
  sessionId?: string
}

interface FilePreview {
  path: string
  content: string
  size: number
  type: string
}

export const GitHubPushDialog: React.FC<GitHubPushDialogProps> = ({
  isOpen,
  onClose,
  sessionId
}) => {
  const [isPushing, setIsPushing] = useState(false)
  const [isCheckingConnection, setIsCheckingConnection] = useState(false)
  const [isConnected, setIsConnected] = useState(false)
  const [githubUsername, setGithubUsername] = useState('')
  
  const [repoName, setRepoName] = useState('')
  const [repoDescription, setRepoDescription] = useState('')
  const [isPrivate, setIsPrivate] = useState(false)
  const [resultUrl, setResultUrl] = useState('')
  
  const [isLoadingPreview, setIsLoadingPreview] = useState(false)
  const [filePreview, setFilePreview] = useState<FilePreview[]>([])
  const [selectedFiles, setSelectedFiles] = useState<Set<string>>(new Set())
  const [showPreview, setShowPreview] = useState(false)

  const { showToast } = useToast()

  useEffect(() => {
    if (isOpen) {
      checkGitHubConnection()
      generateDefaultRepoName()
    }
  }, [isOpen])

  const generateDefaultRepoName = () => {
    const date = new Date()
    const dateStr = date.toISOString().split('T')[0].replace(/-/g, '')
    setRepoName(`xionimus-session-${dateStr}`)
  }

  const checkGitHubConnection = async () => {
    setIsCheckingConnection(true)
    try {
      const token = localStorage.getItem('xionimus_token')
      if (!token) {
        setIsConnected(false)
        return
      }

      const status = await getGitHubOAuthStatus(token)
      setIsConnected(status.connected)
      if (status.connected) {
        setGithubUsername(status.github_username || '')
      }
    } catch (error) {
      console.error('Failed to check GitHub connection:', error)
      setIsConnected(false)
    } finally {
      setIsCheckingConnection(false)
    }
  }

  const handleConnectGitHub = async () => {
    try {
      const token = localStorage.getItem('xionimus_token')
      if (!token) {
        showToast({
          title: 'Nicht angemeldet',
          description: 'Bitte melden Sie sich zuerst an',
          status: 'error',
          duration: 3000
        })
        return
      }

      await initiateGitHubOAuth(token)
    } catch (error) {
      console.error('Failed to initiate GitHub OAuth:', error)
      showToast({
        title: 'Fehler',
        description: 'GitHub OAuth konnte nicht gestartet werden',
        status: 'error',
        duration: 3000
      })
    }
  }

  const loadFilePreview = async () => {
    if (!sessionId) return
    
    setIsLoadingPreview(true)
    try {
      const token = localStorage.getItem('xionimus_token')
      const response = await axios.post(
        `${BACKEND_URL}/api/v1/github-pat/preview-session-files`,
        { session_id: sessionId },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      )
      
      setFilePreview(response.data.files)
      setSelectedFiles(new Set(response.data.files.map((f: FilePreview) => f.path)))
      setShowPreview(true)
    } catch (error: any) {
      console.error('Failed to load file preview:', error)
      showToast({
        title: 'Fehler',
        description: 'Dateivorschau konnte nicht geladen werden',
        status: 'error',
        duration: 3000
      })
    } finally {
      setIsLoadingPreview(false)
    }
  }

  const toggleFileSelection = (path: string) => {
    const newSelected = new Set(selectedFiles)
    if (newSelected.has(path)) {
      newSelected.delete(path)
    } else {
      newSelected.add(path)
    }
    setSelectedFiles(newSelected)
  }

  const handlePush = async () => {
    if (!repoName.trim()) {
      showToast({
        title: 'Repository-Name erforderlich',
        status: 'warning',
        duration: 3000
      })
      return
    }

    setIsPushing(true)
    try {
      const token = localStorage.getItem('xionimus_token')
      const response = await axios.post(
        `${BACKEND_URL}/api/v1/github-pat/push-to-github`,
        {
          session_id: sessionId,
          repo_name: repoName,
          repo_description: repoDescription,
          is_private: isPrivate,
          selected_files: Array.from(selectedFiles)
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      )

      setResultUrl(response.data.repo_url)
      showToast({
        title: '✅ Erfolgreich zu GitHub gepusht!',
        description: response.data.message,
        status: 'success',
        duration: 5000
      })
    } catch (error: any) {
      console.error('GitHub push failed:', error)
      showToast({
        title: 'Push fehlgeschlagen',
        description: error.response?.data?.detail || 'Fehler beim Pushen zu GitHub',
        status: 'error',
        duration: 5000
      })
    } finally {
      setIsPushing(false)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="xl">
      <ModalContent>
        <ModalHeader onClose={onClose}>
          <div className="flex items-center gap-2">
            <span>🚀</span>
            <span>Push zu GitHub</span>
          </div>
        </ModalHeader>

        <ModalBody>
          <div className="space-y-4">
            {/* Connection Status */}
            {isCheckingConnection ? (
              <div className="glossy-card p-4 flex items-center gap-3">
                <div className="w-5 h-5 border-2 border-gold-500 border-t-transparent rounded-full animate-spin"></div>
                <span className="text-gray-300">Checking GitHub connection...</span>
              </div>
            ) : isConnected ? (
              <div className="glossy-card p-4 bg-green-500/10 border-green-500/30">
                <div className="flex items-start gap-3">
                  <span className="text-green-400 text-xl">✓</span>
                  <div>
                    <p className="font-semibold text-green-400">Mit GitHub verbunden</p>
                    <p className="text-sm text-gray-300">@{githubUsername}</p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="glossy-card p-4 bg-yellow-500/10 border-yellow-500/30">
                <div className="flex items-start gap-3">
                  <span className="text-yellow-400 text-xl">⚠️</span>
                  <div className="flex-1">
                    <p className="font-semibold text-yellow-400 mb-1">GitHub nicht verbunden</p>
                    <p className="text-sm text-gray-300 mb-3">
                      Verbinden Sie Ihr GitHub-Konto, um Code zu exportieren und Repositories zu erstellen
                    </p>
                    <Button
                      variant="primary"
                      size="sm"
                      onClick={handleConnectGitHub}
                      className="bg-gradient-to-r from-gold-500 to-gold-600 hover:from-gold-600 hover:to-gold-700"
                    >
                      🔗 Mit GitHub verbinden
                    </Button>
                  </div>
                </div>
              </div>
            )}

            {/* Result URL */}
            {resultUrl && (
              <div className="glossy-card p-4 bg-green-500/10 border-green-500/30">
                <div className="flex items-start gap-3">
                  <span className="text-green-400 text-xl">🎉</span>
                  <div className="flex-1">
                    <p className="font-semibold text-green-400 mb-2">Repository erstellt!</p>
                    <a
                      href={resultUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-400 hover:text-blue-300 underline break-all"
                    >
                      {resultUrl}
                    </a>
                  </div>
                </div>
              </div>
            )}

            {/* Repository Configuration */}
            <div className="space-y-3">
              <Input
                label="Repository-Name"
                value={repoName}
                onChange={(e) => setRepoName(e.target.value)}
                placeholder="my-awesome-project"
                required
              />

              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Beschreibung (optional)
                </label>
                <textarea
                  value={repoDescription}
                  onChange={(e) => setRepoDescription(e.target.value)}
                  placeholder="Eine kurze Beschreibung des Projekts..."
                  rows={3}
                  className="input-glossy w-full resize-none"
                />
              </div>

              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="private-repo"
                  checked={isPrivate}
                  onChange={(e) => setIsPrivate(e.target.checked)}
                  className="w-4 h-4 rounded border-gold-500/30 bg-primary-navy/50 text-gold-500 focus:ring-gold-500"
                />
                <label htmlFor="private-repo" className="text-sm text-gray-300 cursor-pointer">
                  Privates Repository
                </label>
              </div>
            </div>

            {/* File Preview */}
            {!showPreview ? (
              <Button
                variant="secondary"
                onClick={loadFilePreview}
                loading={isLoadingPreview}
                disabled={!sessionId}
                className="w-full"
              >
                Dateien anzeigen
              </Button>
            ) : (
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-semibold text-white">
                    Dateien ({selectedFiles.size}/{filePreview.length})
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setSelectedFiles(new Set(filePreview.map(f => f.path)))}
                      className="text-xs text-blue-400 hover:text-blue-300"
                    >
                      Alle auswählen
                    </button>
                    <button
                      onClick={() => setSelectedFiles(new Set())}
                      className="text-xs text-blue-400 hover:text-blue-300"
                    >
                      Keine
                    </button>
                  </div>
                </div>

                <div className="max-h-[300px] overflow-y-auto custom-scrollbar space-y-1">
                  {filePreview.map((file) => (
                    <label
                      key={file.path}
                      className={`
                        glossy-card p-3 flex items-center gap-3 cursor-pointer
                        transition-colors duration-200
                        ${selectedFiles.has(file.path) ? 'bg-gold-500/10 border-gold-500/30' : 'hover:bg-accent-blue/20'}
                      `}
                    >
                      <input
                        type="checkbox"
                        checked={selectedFiles.has(file.path)}
                        onChange={() => toggleFileSelection(file.path)}
                        className="w-4 h-4 rounded border-gold-500/30 bg-primary-navy/50 text-gold-500"
                      />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-white truncate">{file.path}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="info" className="text-xs">{file.type}</Badge>
                          <span className="text-xs text-gray-500">{formatFileSize(file.size)}</span>
                        </div>
                      </div>
                    </label>
                  ))}
                </div>
              </div>
            )}
          </div>
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" onClick={onClose} disabled={isPushing}>
            Abbrechen
          </Button>
          <Button
            variant="primary"
            onClick={handlePush}
            loading={isPushing}
            disabled={!isConnected || !repoName.trim() || selectedFiles.size === 0}
            leftIcon={<span>🚀</span>}
          >
            Zu GitHub pushen
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}
