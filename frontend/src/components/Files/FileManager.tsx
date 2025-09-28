import React from 'react'
import { useChatContext } from '@/context/ChatContext'
import { Button } from '@/components/ui/Button'
import { Upload, FileText, Trash2, Download, Eye } from 'lucide-react'
import { toast } from 'sonner'
import { format } from 'date-fns'

export const FileManager: React.FC = () => {
  const [files, setFiles] = React.useState<any[]>([])
  const [uploading, setUploading] = React.useState(false)
  const fileInputRef = React.useRef<HTMLInputElement>(null)

  const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001'

  const loadFiles = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/files`)
      if (!response.ok) throw new Error('Failed to load files')
      
      const data = await response.json()
      setFiles(data)
    } catch (error) {
      console.error('Load files error:', error)
      toast.error('Failed to load files')
    }
  }

  const uploadFile = async (file: File) => {
    setUploading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await fetch(`${API_BASE}/api/files/upload`, {
        method: 'POST',
        body: formData
      })
      
      if (!response.ok) throw new Error('Upload failed')
      
      const data = await response.json()
      toast.success(`File uploaded: ${data.filename}`)
      loadFiles()
    } catch (error) {
      console.error('Upload error:', error)
      toast.error('Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const deleteFile = async (fileId: string) => {
    try {
      const response = await fetch(`${API_BASE}/api/files/${fileId}`, {
        method: 'DELETE'
      })
      
      if (!response.ok) throw new Error('Delete failed')
      
      toast.success('File deleted')
      loadFiles()
    } catch (error) {
      console.error('Delete error:', error)
      toast.error('Delete failed')
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      uploadFile(file)
    }
  }

  React.useEffect(() => {
    loadFiles()
  }, [])

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-primary mb-2">File Manager</h1>
        <p className="text-muted-foreground">
          Upload and manage files for AI agent processing.
        </p>
      </div>

      {/* Upload area */}
      <div className="mb-6">
        <div 
          className="border-2 border-dashed border-primary/30 rounded-lg p-8 text-center hover:border-primary/50 transition-colors duration-200 cursor-pointer"
          onClick={() => fileInputRef.current?.click()}
        >
          <Upload className="h-12 w-12 text-primary mx-auto mb-4" />
          <h3 className="text-lg font-semibold text-primary mb-2">Upload Files</h3>
          <p className="text-muted-foreground mb-4">
            Click to browse or drag and drop files here
          </p>
          <Button disabled={uploading}>
            {uploading ? 'Uploading...' : 'Choose Files'}
          </Button>
        </div>
        
        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileSelect}
          className="hidden"
          multiple
        />
      </div>

      {/* Files list */}
      <div className="space-y-4">
        {files.map((file) => (
          <div
            key={file.file_id}
            className="p-4 bg-secondary rounded-lg border border-primary/20 hover:border-primary/40 transition-colors duration-200"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <FileText className="h-8 w-8 text-primary" />
                <div>
                  <h3 className="font-medium text-primary">{file.original_filename}</h3>
                  <p className="text-sm text-muted-foreground">
                    {(file.file_size / 1024).toFixed(1)} KB • {format(new Date(file.uploaded_at), 'MMM dd, yyyy HH:mm')}
                  </p>
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <Button variant="outline" size="sm">
                  <Eye className="h-4 w-4" />
                </Button>
                <Button variant="outline" size="sm">
                  <Download className="h-4 w-4" />
                </Button>
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => deleteFile(file.file_id)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        ))}
        
        {files.length === 0 && (
          <div className="text-center py-12">
            <FileText className="h-16 w-16 text-primary/50 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-primary mb-2">No Files Uploaded</h3>
            <p className="text-muted-foreground">
              Upload files to get started with AI-powered file processing.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}