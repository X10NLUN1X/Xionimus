import React from 'react'
import { useChatContext } from '@/context/ChatContext'
import { Button } from '@/components/ui/Button'
import { FolderOpen, Trash2, MessageSquare, Plus } from 'lucide-react'
import { toast } from 'sonner'
import { format } from 'date-fns'

export const SessionManager: React.FC = () => {
  const { sessions, loadSessions, loadChatHistory, currentSession, setCurrentSession } = useChatContext()
  const [creatingSession, setCreatingSession] = React.useState(false)

  const API_BASE = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001'

  const createNewSession = async () => {
    setCreatingSession(true)
    try {
      const response = await fetch(`${API_BASE}/api/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: `Session ${format(new Date(), 'MMM dd, HH:mm')}`
        })
      })
      
      if (!response.ok) throw new Error('Failed to create session')
      
      const data = await response.json()
      toast.success('New session created')
      loadSessions()
      setCurrentSession(data.session_id)
    } catch (error) {
      console.error('Create session error:', error)
      toast.error('Failed to create session')
    } finally {
      setCreatingSession(false)
    }
  }

  const deleteSession = async (sessionId: string) => {
    try {
      const response = await fetch(`${API_BASE}/api/sessions/${sessionId}`, {
        method: 'DELETE'
      })
      
      if (!response.ok) throw new Error('Delete failed')
      
      toast.success('Session deleted')
      if (currentSession === sessionId) {
        setCurrentSession(null)
      }
      loadSessions()
    } catch (error) {
      console.error('Delete session error:', error)
      toast.error('Delete failed')
    }
  }

  const loadSession = async (sessionId: string) => {
    await loadChatHistory(sessionId)
    toast.success('Session loaded')
  }

  React.useEffect(() => {
    loadSessions()
  }, [])

  return (
    <div className="p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-primary mb-2">Chat Sessions</h1>
            <p className="text-muted-foreground">
              Manage your conversation history and create new chat sessions.
            </p>
          </div>
          
          <Button onClick={createNewSession} disabled={creatingSession}>
            <Plus className="h-4 w-4 mr-2" />
            {creatingSession ? 'Creating...' : 'New Session'}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {sessions.map((session) => (
          <div
            key={session.id}
            className={
              `p-4 bg-secondary rounded-lg border transition-all duration-200 cursor-pointer ${
                currentSession === session.id
                  ? "border-primary/50 ring-2 ring-primary/30 xionimus-glow"
                  : "border-primary/20 hover:border-primary/40"
              }`
            }
            onClick={() => loadSession(session.id)}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-2">
                <FolderOpen className="h-5 w-5 text-primary" />
                <h3 className="font-semibold text-primary truncate">{session.name}</h3>
              </div>
              
              <Button
                variant="ghost"
                size="sm"
                onClick={(e) => {
                  e.stopPropagation()
                  deleteSession(session.id)
                }}
                className="h-6 w-6 p-0 hover:bg-destructive/20 hover:text-destructive"
              >
                <Trash2 className="h-3 w-3" />
              </Button>
            </div>
            
            {session.description && (
              <p className="text-sm text-muted-foreground mb-3">
                {session.description}
              </p>
            )}
            
            <div className="flex items-center justify-between text-xs text-muted-foreground">
              <div className="flex items-center space-x-1">
                <MessageSquare className="h-3 w-3" />
                <span>{session.message_count} messages</span>
              </div>
              <span>{format(session.created_at, 'MMM dd, yyyy')}</span>
            </div>
            
            {currentSession === session.id && (
              <div className="mt-3 pt-3 border-t border-primary/20">
                <div className="flex items-center space-x-2">
                  <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                  <span className="text-xs font-medium text-primary">Active Session</span>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {sessions.length === 0 && (
        <div className="text-center py-12">
          <FolderOpen className="h-16 w-16 text-primary/50 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-primary mb-2">No Sessions Found</h3>
          <p className="text-muted-foreground mb-4">
            Create your first chat session to start organizing your conversations.
          </p>
          <Button onClick={createNewSession} disabled={creatingSession}>
            <Plus className="h-4 w-4 mr-2" />
            Create First Session
          </Button>
        </div>
      )}
    </div>
  )
}