import React, { useState, useRef } from 'react'
import axios from 'axios'
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } from './Modal'
import { Button } from './UI/Button'
import { Badge } from './UI/Badge'
import { useToast } from './UI/Toast'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'
const MAX_FILE_SIZE = 50 * 1024 * 1024 // 50MB

interface FileUploadDialogProps {
  isOpen: boolean
  onClose: () => void
  sessionId: string | null
  activeProject: string | null
}

interface FileToUpload {
  file: File
  id: string
}

export const FileUploadDialog: React.FC<FileUploadDialogProps> = ({
  isOpen,
  onClose,
  sessionId,
  activeProject
}) => {
  const [files, setFiles] = useState<FileToUpload[]>([])
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [isDragging, setIsDragging] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { showToast } = useToast()

  const handleFileSelect = (selectedFiles: FileList | null) => {
    if (!selectedFiles) return

    const newFiles: FileToUpload[] = []
    const errors: string[] = []

    Array.from(selectedFiles).forEach(file => {
      if (file.size > MAX_FILE_SIZE) {
        errors.push(`${file.name} ist zu groß (${(file.size / (1024 * 1024)).toFixed(1)}MB > 50MB)`)
      } else {
        newFiles.push({
          file,
          id: `${Date.now()}_${file.name}`
        })
      }
    })

    if (errors.length > 0) {
      showToast({
        title: 'Einige Dateien wurden übersprungen',
        description: errors.join(', '),
        status: 'warning',
        duration: 5000
      })
    }

    setFiles(prev => [...prev, ...newFiles])
  }

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
  }

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(false)
    handleFileSelect(e.dataTransfer.files)
  }

  const removeFile = (id: string) => {
    setFiles(prev => prev.filter(f => f.id !== id))
  }

  const handleUpload = async () => {
    if (files.length === 0) return

    setIsUploading(true)
    setUploadProgress(0)

    try {
      const formData = new FormData()
      
      files.forEach(({ file }) => {
        formData.append('files', file)
      })

      if (sessionId) {
        formData.append('session_id', sessionId)
      }

      const token = localStorage.getItem('xionimus_token')
      
      const response = await axios.post(
        `${BACKEND_URL}/api/v1/file-upload/upload`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
            ...(token ? { 'Authorization': `Bearer ${token}` } : {})
          },
          onUploadProgress: (progressEvent) => {
            const progress = progressEvent.total
              ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
              : 0
            setUploadProgress(progress)
          }
        }
      )

      const result = response.data

      showToast({
        title: '✅ Upload erfolgreich!',
        description: result.message,
        status: 'success',
        duration: 5000
      })

      setFiles([])
      onClose()
    } catch (error: any) {
      console.error('Upload failed:', error)
      const errorMsg = error.response?.data?.detail || 'Upload fehlgeschlagen'
      
      showToast({
        title: 'Upload fehlgeschlagen',
        description: errorMsg,
        status: 'error',
        duration: 5000
      })
    } finally {
      setIsUploading(false)
      setUploadProgress(0)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
  }

  const totalSize = files.reduce((sum, { file }) => sum + file.size, 0)

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <ModalContent>
        <ModalHeader onClose={onClose}>📤 Dateien hochladen</ModalHeader>

        <ModalBody>
          <div className="space-y-4">
            {/* Target Info */}
            <div className="glossy-card p-4 bg-blue-500/10 border-blue-500/30">
              <div className="flex items-start gap-3">
                <span className="text-blue-400 text-xl">ℹ️</span>
                <div>
                  <p className="text-sm font-semibold text-blue-400 mb-1">Upload-Ziel:</p>
                  <p className="text-sm text-gray-300">
                    {activeProject 
                      ? `📁 Aktives Projekt: ${activeProject}`
                      : '📁 Uploads-Verzeichnis'}
                  </p>
                </div>
              </div>
            </div>

            {/* Drag & Drop Area */}
            <div
              className={`
                border-2 border-dashed rounded-xl p-8 text-center
                transition-all duration-200 cursor-pointer
                ${isDragging 
                  ? 'border-blue-500 bg-blue-500/10' 
                  : 'border-gold-500/30 bg-accent-blue/20 hover:border-blue-500 hover:bg-blue-500/10'
                }
              `}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
            >
              <div className="space-y-2">
                <svg className="w-12 h-12 mx-auto text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                </svg>
                <p className="font-semibold text-white">
                  Dateien hier ablegen
                </p>
                <p className="text-sm text-gray-400">
                  oder klicken zum Auswählen
                </p>
                <p className="text-xs text-gray-500">
                  Max. 50MB pro Datei
                </p>
              </div>
            </div>

            <input
              ref={fileInputRef}
              type="file"
              multiple
              className="hidden"
              onChange={(e) => handleFileSelect(e.target.files)}
            />

            {/* Selected Files List */}
            {files.length > 0 && (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-semibold text-white">
                    Ausgewählte Dateien ({files.length})
                  </p>
                  <Badge variant="info">
                    {formatFileSize(totalSize)}
                  </Badge>
                </div>

                <div className="space-y-2">
                  {files.map(({ file, id }) => (
                    <div
                      key={id}
                      className="glossy-card p-3 flex items-center justify-between"
                    >
                      <div className="flex items-center gap-3 flex-1 min-w-0">
                        <svg className="w-5 h-5 text-green-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium text-white truncate">
                            {file.name}
                          </p>
                          <p className="text-xs text-gray-400">
                            {formatFileSize(file.size)}
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => removeFile(id)}
                        disabled={isUploading}
                        className="p-2 hover:bg-red-500/20 rounded-lg transition-colors disabled:opacity-50"
                      >
                        <svg className="w-4 h-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Upload Progress */}
            {isUploading && (
              <div>
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-semibold text-white">
                    Wird hochgeladen...
                  </p>
                  <p className="text-sm text-blue-400">
                    {uploadProgress}%
                  </p>
                </div>
                <div className="w-full h-2 bg-primary-navy/50 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-500 transition-all duration-300"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        </ModalBody>

        <ModalFooter>
          <Button 
            variant="ghost" 
            onClick={onClose} 
            disabled={isUploading}
          >
            Abbrechen
          </Button>
          <Button
            variant="primary"
            onClick={handleUpload}
            loading={isUploading}
            disabled={files.length === 0}
            leftIcon={
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
              </svg>
            }
          >
            {files.length > 0 ? `${files.length} Datei(en) hochladen` : 'Hochladen'}
          </Button>
        </ModalFooter>
      </ModalContent>
    </Modal>
  )
}
