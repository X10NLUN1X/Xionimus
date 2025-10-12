import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Badge } from './UI/Badge'
import { useToast } from './UI/Toast'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'

interface ActiveProjectInfo {
  project_name: string | null
  project_path: string | null
  branch: string | null
  file_count: number | null
  size_mb: number | null
  exists: boolean
}

interface ActiveProjectBadgeProps {
  sessionId: string | null
}

export const ActiveProjectBadge: React.FC<ActiveProjectBadgeProps> = ({ sessionId }) => {
  const [activeProject, setActiveProject] = useState<ActiveProjectInfo | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const { showToast } = useToast()

  useEffect(() => {
    if (sessionId) {
      loadActiveProject()
    } else {
      setActiveProject(null)
    }
  }, [sessionId])

  const loadActiveProject = async () => {
    if (!sessionId) return
    
    setIsLoading(true)
    try {
      const token = localStorage.getItem('xionimus_token')
      const response = await axios.get(
        `${BACKEND_URL}/api/v1/workspace/active-project/${sessionId}`,
        {
          headers: token ? {
            'Authorization': `Bearer ${token}`
          } : {}
        }
      )
      
      if (response.data && response.data.exists) {
        setActiveProject(response.data)
      } else {
        setActiveProject(null)
      }
    } catch (error: any) {
      console.error('Failed to load active project:', error)
      setActiveProject(null)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center gap-2 px-3 py-1.5 bg-accent-blue/30 rounded-lg animate-pulse">
        <div className="w-3 h-3 border-2 border-gold-400 border-t-transparent rounded-full animate-spin"></div>
        <span className="text-xs text-gray-400">Loading project...</span>
      </div>
    )
  }

  if (!activeProject || !activeProject.exists) {
    return null
  }

  return (
    <div className="flex items-center gap-2 px-3 py-1.5 glossy-card animate-fade-in">
      <span className="text-lg">📁</span>
      <div className="flex flex-col">
        <div className="flex items-center gap-2">
          <span className="text-sm font-semibold text-white">
            {activeProject.project_name}
          </span>
          {activeProject.branch && (
            <Badge variant="info" className="text-xs">
              {activeProject.branch}
            </Badge>
          )}
        </div>
        {(activeProject.file_count || activeProject.size_mb) && (
          <div className="flex items-center gap-2 text-xs text-gray-400">
            {activeProject.file_count && (
              <span>{activeProject.file_count} files</span>
            )}
            {activeProject.size_mb && (
              <span>• {activeProject.size_mb.toFixed(1)} MB</span>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
