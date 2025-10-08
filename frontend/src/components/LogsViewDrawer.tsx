import React, { useState, useEffect, useRef } from 'react'
import { FadeIn } from './UI/FadeIn'

interface LogEntry {
  id: string
  timestamp: Date
  level: 'info' | 'warning' | 'error' | 'success'
  message: string
  source?: 'stdout' | 'stderr'
}

interface LogsViewDrawerProps {
  isOpen: boolean
  onClose: () => void
  logs: LogEntry[]
  metrics?: {
    executionTime?: number
    exitCode?: number
    memoryUsage?: number
  }
}

export const LogsViewDrawer: React.FC<LogsViewDrawerProps> = ({
  isOpen,
  onClose,
  logs,
  metrics
}) => {
  const [filterLevel, setFilterLevel] = useState<string>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [autoScroll, setAutoScroll] = useState(true)
  const logsEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (autoScroll && logsEndRef.current) {
      logsEndRef.current.scrollIntoView({ behavior: 'smooth' })
    }
  }, [logs, autoScroll])

  const getLevelColor = (level: string) => {
    switch (level) {
      case 'error': return 'text-red-400 bg-red-500/10 border-red-500/30'
      case 'warning': return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/30'
      case 'success': return 'text-green-400 bg-green-500/10 border-green-500/30'
      default: return 'text-blue-400 bg-blue-500/10 border-blue-500/30'
    }
  }

  const filteredLogs = logs.filter(log => {
    const matchesLevel = filterLevel === 'all' || log.level === filterLevel
    const matchesSearch = searchTerm === '' || log.message.toLowerCase().includes(searchTerm.toLowerCase())
    return matchesLevel && matchesSearch
  })

  const handleClearLogs = () => {
    // TODO: Clear logs functionality
    console.log('Clear logs')
  }

  const handleDownloadLogs = () => {
    const logText = logs.map(log => 
      `[${log.timestamp.toISOString()}] [${log.level.toUpperCase()}] ${log.message}`
    ).join('\n')
    
    const blob = new Blob([logText], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `xionimus-logs-${Date.now()}.txt`
    a.click()
    URL.revokeObjectURL(url)
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
                <span className="text-primary-dark font-black text-lg">📊</span>
              </div>
              <h2 className="text-xl font-bold bg-gradient-to-r from-gold-400 via-gold-500 to-gold-400 bg-clip-text text-transparent">
                Logs View
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

          {/* Metrics Bar */}
          {metrics && (
            <div className="px-4 py-3 border-b border-gold-500/10 bg-primary-navy/50 flex gap-4 flex-wrap">
              {metrics.executionTime !== undefined && (
                <div className="flex items-center gap-2 px-3 py-1 bg-blue-500/20 rounded-lg border border-blue-500/30">
                  <span className="text-blue-400 text-xs">⏱️</span>
                  <span className="text-sm text-blue-300">{metrics.executionTime}ms</span>
                </div>
              )}
              {metrics.exitCode !== undefined && (
                <div className={`flex items-center gap-2 px-3 py-1 rounded-lg border ${
                  metrics.exitCode === 0 
                    ? 'bg-green-500/20 border-green-500/30' 
                    : 'bg-red-500/20 border-red-500/30'
                }`}>
                  <span className={metrics.exitCode === 0 ? 'text-green-400 text-xs' : 'text-red-400 text-xs'}>
                    {metrics.exitCode === 0 ? '✅' : '❌'}
                  </span>
                  <span className={`text-sm ${metrics.exitCode === 0 ? 'text-green-300' : 'text-red-300'}`}>
                    Exit: {metrics.exitCode}
                  </span>
                </div>
              )}
              {metrics.memoryUsage !== undefined && (
                <div className="flex items-center gap-2 px-3 py-1 bg-purple-500/20 rounded-lg border border-purple-500/30">
                  <span className="text-purple-400 text-xs">💾</span>
                  <span className="text-sm text-purple-300">{metrics.memoryUsage}MB</span>
                </div>
              )}
            </div>
          )}

          {/* Toolbar */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-gold-500/10 bg-primary-navy/30 flex-wrap gap-2">
            <div className="flex items-center gap-2">
              {/* Level Filter */}
              <select
                value={filterLevel}
                onChange={(e) => setFilterLevel(e.target.value)}
                className="px-3 py-1.5 text-sm bg-primary-navy/50 border border-gold-500/20 rounded-lg text-white focus:outline-none focus:border-gold-500/50"
              >
                <option value="all">All Levels</option>
                <option value="info">Info</option>
                <option value="warning">Warning</option>
                <option value="error">Error</option>
                <option value="success">Success</option>
              </select>

              {/* Search */}
              <input
                type="text"
                placeholder="Search logs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="px-3 py-1.5 text-sm bg-primary-navy/50 border border-gold-500/20 rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-gold-500/50"
              />
            </div>

            <div className="flex items-center gap-2">
              {/* Auto-scroll Toggle */}
              <button
                onClick={() => setAutoScroll(!autoScroll)}
                className={`px-3 py-1.5 text-xs rounded-lg transition-colors ${
                  autoScroll 
                    ? 'bg-green-500/20 text-green-300 border border-green-500/30' 
                    : 'bg-gray-500/20 text-gray-400 border border-gray-500/30'
                }`}
                title="Auto-scroll"
              >
                📜 {autoScroll ? 'ON' : 'OFF'}
              </button>

              {/* Clear */}
              <button
                onClick={handleClearLogs}
                className="p-2 hover:bg-red-500/20 rounded-lg transition-colors group"
                title="Clear Logs"
              >
                <span className="text-gray-400 group-hover:text-red-400">🗑️</span>
              </button>

              {/* Download */}
              <button
                onClick={handleDownloadLogs}
                className="p-2 hover:bg-gold-500/20 rounded-lg transition-colors group"
                title="Download Logs"
              >
                <span className="text-gray-400 group-hover:text-gold-400">💾</span>
              </button>
            </div>
          </div>

          {/* Logs Content */}
          <div className="flex-1 overflow-auto p-4">
            <div className="space-y-2 font-mono text-sm">
              {filteredLogs.length > 0 ? (
                filteredLogs.map(log => (
                  <div
                    key={log.id}
                    className={`p-3 rounded-lg border ${getLevelColor(log.level)} transition-all duration-200 hover:scale-[1.01]`}
                  >
                    <div className="flex items-start gap-3">
                      <span className="text-xs text-gray-500 whitespace-nowrap">
                        {log.timestamp.toLocaleTimeString()}
                      </span>
                      <span className="text-xs font-semibold uppercase whitespace-nowrap">
                        [{log.level}]
                      </span>
                      <span className="flex-1 break-words">{log.message}</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="flex items-center justify-center h-full text-gray-500">
                  <p>No logs available</p>
                </div>
              )}
              <div ref={logsEndRef} />
            </div>
          </div>

          {/* Footer */}
          <div className="h-12 px-4 border-t border-gold-500/20 flex items-center justify-between bg-primary-navy/50 text-xs text-gray-400">
            <span>Total Logs: {logs.length}</span>
            <span>Filtered: {filteredLogs.length}</span>
          </div>
        </div>
      </FadeIn>
    </>
  )
}