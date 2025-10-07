import React, { useState } from 'react'
import { FadeIn } from './UI/FadeIn'

interface CodeFile {
  id: string
  name: string
  language: string
  content: string
}

interface CodeViewDrawerProps {
  isOpen: boolean
  onClose: () => void
  files: CodeFile[]
}

export const CodeViewDrawer: React.FC<CodeViewDrawerProps> = ({
  isOpen,
  onClose,
  files
}) => {
  const [activeFileId, setActiveFileId] = useState<string>(files[0]?.id || '')
  const [searchTerm, setSearchTerm] = useState('')
  const [viewMode, setViewMode] = useState<'single' | 'diff'>('single')

  const activeFile = files.find(f => f.id === activeFileId)

  const handleCopyCode = () => {
    if (activeFile) {
      navigator.clipboard.writeText(activeFile.content)
      // TODO: Show toast notification
    }
  }

  const handleDownloadCode = () => {
    if (activeFile) {
      const blob = new Blob([activeFile.content], { type: 'text/plain' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = activeFile.name
      a.click()
      URL.revokeObjectURL(url)
    }
  }

  const handleFormatCode = async () => {
    // TODO: Implement code formatting
    console.log('Format code:', activeFile?.language)
  }

  if (!isOpen) return null

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40"
        onClick={onClose}
      />
      
      {/* Drawer */}
      <FadeIn direction="right" duration={0.3}>
        <div className="fixed right-0 top-0 h-full w-full md:w-[600px] lg:w-[800px] bg-gradient-dark border-l border-gold-500/20 shadow-2xl z-50 flex flex-col">
          {/* Header */}
          <div className="h-16 px-4 border-b border-gold-500/20 flex items-center justify-between bg-primary-navy/80 backdrop-blur-xl">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-glossy-gold rounded-lg flex items-center justify-center shadow-gold-glow">
                <span className="text-primary-dark font-black text-lg">💻</span>
              </div>
              <h2 className="text-xl font-bold bg-gradient-to-r from-gold-400 via-gold-500 to-gold-400 bg-clip-text text-transparent">
                Code View
              </h2>
            </div>
            
            <button
              onClick={onClose}
              className="p-2 hover:bg-red-500/20 rounded-lg transition-colors"
              aria-label="Close"
            >
              <span className="text-2xl text-gray-400 hover:text-red-400">×</span>
            </button>
          </div>

          {/* Tabs */}
          {files.length > 0 && (
            <div className="flex items-center gap-2 px-4 py-2 border-b border-gold-500/10 bg-primary-navy/50 overflow-x-auto">
              {files.map(file => (
                <button
                  key={file.id}
                  onClick={() => setActiveFileId(file.id)}
                  className={`
                    px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all duration-200
                    ${activeFileId === file.id
                      ? 'bg-gold-500/20 text-gold-400 border border-gold-500/50'
                      : 'bg-transparent text-gray-400 hover:bg-gold-500/10 hover:text-gold-300'
                    }
                  `}
                >
                  {file.name}
                </button>
              ))}
            </div>
          )}

          {/* Toolbar */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-gold-500/10 bg-primary-navy/30">
            <div className="flex items-center gap-2">
              {/* View Mode Toggle */}
              <button
                onClick={() => setViewMode(viewMode === 'single' ? 'diff' : 'single')}
                className="px-3 py-1.5 text-xs bg-blue-500/20 text-blue-300 rounded-lg border border-blue-500/30 hover:bg-blue-500/30 transition-colors"
              >
                {viewMode === 'single' ? '📄 Single' : '🔀 Diff'}
              </button>

              {/* Search */}
              <input
                type="text"
                placeholder="Search in code..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="px-3 py-1.5 text-sm bg-primary-navy/50 border border-gold-500/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-gold-500/50"
              />
            </div>

            <div className="flex items-center gap-2">
              {/* Format */}
              <button
                onClick={handleFormatCode}
                className="p-2 hover:bg-gold-500/20 rounded-lg transition-colors group"
                title="Format Code"
              >
                <span className="text-gray-400 group-hover:text-gold-400">✨</span>
              </button>

              {/* Copy */}
              <button
                onClick={handleCopyCode}
                className="p-2 hover:bg-gold-500/20 rounded-lg transition-colors group"
                title="Copy Code"
              >
                <span className="text-gray-400 group-hover:text-gold-400">📋</span>
              </button>

              {/* Download */}
              <button
                onClick={handleDownloadCode}
                className="p-2 hover:bg-gold-500/20 rounded-lg transition-colors group"
                title="Download Code"
              >
                <span className="text-gray-400 group-hover:text-gold-400">💾</span>
              </button>
            </div>
          </div>

          {/* Code Content */}
          <div className="flex-1 overflow-auto p-4">
            {activeFile ? (
              <div className="glossy-card p-4">
                <pre className="text-sm text-gray-300 font-mono overflow-x-auto">
                  <code className={`language-${activeFile.language}`}>
                    {activeFile.content}
                  </code>
                </pre>
              </div>
            ) : (
              <div className="flex items-center justify-center h-full text-gray-500">
                <p>No code files available</p>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="h-12 px-4 border-t border-gold-500/20 flex items-center justify-between bg-primary-navy/50 text-xs text-gray-400">
            <span>Language: {activeFile?.language || 'N/A'}</span>
            <span>Lines: {activeFile?.content.split('\n').length || 0}</span>
          </div>
        </div>
      </FadeIn>
    </>
  )
}