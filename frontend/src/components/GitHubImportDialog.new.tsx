import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } from './Modal'
import { Button } from './UI/Button'
import { Input } from './UI/Input'
import { Badge } from './UI/Badge'
import { useToast } from './UI/Toast'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'

interface GitHubRepo {
  name: string
  full_name: string
  description: string | null
  private: boolean
  default_branch: string
}

interface GitHubImportDialogProps {
  isOpen: boolean
  onClose: () => void
  sessionId?: string | null
}

export const GitHubImportDialog: React.FC<GitHubImportDialogProps> = ({
  isOpen,
  onClose,
  sessionId
}) => {
  const [activeMode, setActiveMode] = useState<'auto' | 'manual'>('auto')
  
  // Auto mode
  const [repositories, setRepositories] = useState<GitHubRepo[]>([])
  const [selectedRepo, setSelectedRepo] = useState<string>('')
  const [selectedBranch, setSelectedBranch] = useState<string>('main')
  const [isLoadingRepos, setIsLoadingRepos] = useState(false)
  
  // Manual mode
  const [repoUrl, setRepoUrl] = useState('')
  const [branch, setBranch] = useState('main')
  
  // Common
  const [isImporting, setIsImporting] = useState(false)
  const [importResult, setImportResult] = useState<any>(null)

  const { showToast } = useToast()

  useEffect(() => {
    if (isOpen && activeMode === 'auto') {
      loadRepositories()
    }
  }, [isOpen, activeMode])

  const loadRepositories = async () => {
    setIsLoadingRepos(true)
    try {
      const token = localStorage.getItem('xionimus_token')
      const response = await axios.get(`${BACKEND_URL}/api/github-pat/repositories`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      setRepositories(response.data)
    } catch (error: any) {
      console.error('Failed to load repositories:', error)
      showToast({
        title: 'Fehler',
        description: 'Repositories konnten nicht geladen werden',
        status: 'error',
        duration: 3000
      })
    } finally {
      setIsLoadingRepos(false)
    }
  }

  const handleImport = async () => {
    setIsImporting(true)
    setImportResult(null)

    try {
      const token = localStorage.getItem('xionimus_token')
      
      const payload = activeMode === 'auto' 
        ? {
            repo_full_name: selectedRepo,
            branch: selectedBranch,
            session_id: sessionId
          }
        : {
            repo_url: repoUrl,
            branch: branch,
            session_id: sessionId
          }

      const endpoint = activeMode === 'auto' 
        ? '/api/github-pat/import-from-github'
        : '/api/github-pat/import-from-url'

      const response = await axios.post(
        `${BACKEND_URL}${endpoint}`,
        payload,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      )

      setImportResult(response.data)
      showToast({
        title: '✅ Repository importiert!',
        description: response.data.message,
        status: 'success',
        duration: 5000
      })
    } catch (error: any) {
      console.error('Import failed:', error)
      showToast({
        title: 'Import fehlgeschlagen',
        description: error.response?.data?.detail || 'Fehler beim Importieren',
        status: 'error',
        duration: 5000
      })
    } finally {
      setIsImporting(false)
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalContent>
        <ModalHeader onClose={onClose}>
          <div className="flex items-center gap-2">
            <span>📥</span>
            <span>GitHub Import</span>
          </div>
        </ModalHeader>

        <ModalBody>
          <div className="space-y-4">
            {/* Mode Toggle */}
            <div className="flex gap-2">
              <button
                onClick={() => setActiveMode('auto')}
                className={`
                  flex-1 py-2 px-4 rounded-lg font-semibold text-sm
                  transition-all duration-200
                  ${activeMode === 'auto'
                    ? 'bg-gold-500/20 border-2 border-gold-500 text-gold-400'
                    : 'bg-accent-blue/20 border-2 border-gold-500/20 text-gray-400 hover:border-gold-500/40'
                  }
                `}
              >
                🤖 Auto (Your Repos)
              </button>
              <button
                onClick={() => setActiveMode('manual')}
                className={`
                  flex-1 py-2 px-4 rounded-lg font-semibold text-sm
                  transition-all duration-200
                  ${activeMode === 'manual'
                    ? 'bg-gold-500/20 border-2 border-gold-500 text-gold-400'
                    : 'bg-accent-blue/20 border-2 border-gold-500/20 text-gray-400 hover:border-gold-500/40'
                  }
                `}
              >
                ✍️ Manual (Any URL)
              </button>
            </div>

            {/* Import Result */}
            {importResult && (
              <div className="glossy-card p-4 bg-green-500/10 border-green-500/30 animate-slide-in">
                <div className="flex items-start gap-3">
                  <span className="text-green-400 text-xl">✓</span>
                  <div className="flex-1">
                    <p className="font-semibold text-green-400 mb-1">Import erfolgreich!</p>
                    <p className="text-sm text-gray-300">{importResult.message}</p>
                    {importResult.project_path && (
                      <p className="text-xs text-gray-400 mt-2">📁 {importResult.project_path}</p>
                    )}
                  </div>
                </div>
              </div>
            )}

            {/* Auto Mode */}
            {activeMode === 'auto' && (
              <div className="space-y-3">
                {isLoadingRepos ? (
                  <div className="flex items-center justify-center py-8">
                    <div className="w-8 h-8 border-4 border-gold-500 border-t-transparent rounded-full animate-spin"></div>
                  </div>
                ) : repositories.length === 0 ? (
                  <div className="glossy-card p-6 text-center">
                    <p className="text-gray-400">Keine Repositories gefunden</p>
                    <Button
                      variant="secondary"
                      size="sm"
                      onClick={loadRepositories}
                      className="mt-3"
                    >
                      Neu laden
                    </Button>
                  </div>
                ) : (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Repository auswählen
                      </label>
                      <select
                        value={selectedRepo}
                        onChange={(e) => setSelectedRepo(e.target.value)}
                        className="input-glossy w-full"
                      >
                        <option value="">-- Wählen Sie ein Repository --</option>
                        {repositories.map((repo) => (
                          <option key={repo.full_name} value={repo.full_name}>
                            {repo.name} {repo.private && '🔒'}
                          </option>
                        ))}
                      </select>
                    </div>

                    <Input
                      label="Branch"
                      value={selectedBranch}
                      onChange={(e) => setSelectedBranch(e.target.value)}
                      placeholder="main"
                    />

                    {selectedRepo && (
                      <div className="glossy-card p-3 bg-blue-500/10 border-blue-500/30">
                        <p className="text-xs text-gray-400">
                          Selected: <span className="text-white font-mono">{selectedRepo}</span>
                        </p>
                      </div>
                    )}
                  </>
                )}
              </div>
            )}

            {/* Manual Mode */}
            {activeMode === 'manual' && (
              <div className="space-y-3">
                <Input
                  label="GitHub Repository URL"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  placeholder="https://github.com/username/repository"
                  helperText="Vollständige GitHub-URL des Repositories"
                />

                <Input
                  label="Branch"
                  value={branch}
                  onChange={(e) => setBranch(e.target.value)}
                  placeholder="main"
                />

                <div className="glossy-card p-3 bg-blue-500/10 border-blue-500/30">
                  <div className="flex items-start gap-2">
                    <span className="text-blue-400">ℹ️</span>
                    <p className="text-xs text-gray-300">
                      Sie können jedes öffentliche GitHub-Repository importieren, auch wenn es nicht Ihnen gehört.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </ModalBody>

        <ModalFooter>
          <Button variant="ghost" onClick={onClose} disabled={isImporting}>
            Abbrechen
          </Button>
          <Button
            variant="primary"
            onClick={handleImport}
            loading={isImporting}
            disabled={
              (activeMode === 'auto' && !selectedRepo) ||
              (activeMode === 'manual' && !repoUrl.trim())
            }
            leftIcon={<span>📥</span>}
          >
            Importieren
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}
