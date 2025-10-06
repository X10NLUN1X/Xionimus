import React from 'react'
import { AgentResultsDisplay } from './AgentResultsDisplay'
import { MemoizedMarkdown } from './MemoizedMarkdown'

interface ChatMessage {
  id?: string
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: Date
  provider?: string
  model?: string
  agent_results?: Array<{
    agent: string
    icon: string
    content: string
    summary: string
    data?: any
  }>
}

interface ChatMessageProps {
  message: ChatMessage
  index: number
}

/**
 * Memoized Chat Message Component
 * Only re-renders when message content actually changes
 * Prevents expensive ReactMarkdown re-parsing on every parent render
 */
export const MemoizedChatMessage = React.memo<ChatMessageProps>(({ message, index }) => {
  const isUser = message.role === 'user'

  return (
    <div className={`flex w-full mb-4 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`
          px-5 py-4 rounded-xl max-w-[85%]
          border transition-all duration-300
          ${isUser
            ? 'bg-gradient-to-br from-blue-600 to-blue-800 text-white border-blue-500/50 shadow-lg shadow-blue-500/30'
            : 'glossy-card text-gray-100 border-gold-500/20'
          }
        `}
        style={{
          fontSize: '15px',
          lineHeight: '1.7',
          letterSpacing: '0.01em',
          WebkitFontSmoothing: 'antialiased',
        }}
      >
        <div className="prose prose-invert prose-sm max-w-none">
          <style>{`
            .prose p {
              margin-bottom: 1em;
              line-height: 1.7;
              ${isUser ? 'color: white;' : 'color: #E8E8E8;'}
            }
            .prose h1, .prose h2, .prose h3 {
              font-weight: 600;
              margin-top: 0.75em;
              margin-bottom: 0.5em;
              ${isUser ? 'color: white;' : 'color: #FFD700;'}
            }
            .prose ul, .prose ol {
              margin-left: 1.5em;
              margin-bottom: 1em;
              line-height: 1.7;
            }
            .prose li {
              margin-bottom: 0.5em;
              padding-left: 0.25em;
            }
            .prose code {
              ${isUser ? 'background-color: rgba(255, 255, 255, 0.2);' : 'background-color: rgba(212, 175, 55, 0.1);'}
              padding: 0.2em 0.4em;
              border-radius: 0.25em;
              font-size: 0.9em;
            }
            .prose a {
              color: ${isUser ? '#60a5fa' : '#d4af37'};
              text-decoration: underline;
            }
            .prose a:hover {
              color: ${isUser ? '#93c5fd' : '#f7cf3f'};
            }
            .prose strong {
              font-weight: 700;
              ${isUser ? 'color: white;' : 'color: #FFD700;'}
            }
            .prose blockquote {
              border-left: 4px solid ${isUser ? '#60a5fa' : '#d4af37'};
              padding-left: 1em;
              margin-left: 0;
              ${isUser ? 'color: rgba(255, 255, 255, 0.9);' : 'color: rgba(232, 232, 232, 0.9);'}
            }
            .prose table {
              border-collapse: collapse;
              width: 100%;
              margin: 1em 0;
            }
            .prose th, .prose td {
              border: 1px solid ${isUser ? 'rgba(255, 255, 255, 0.2)' : 'rgba(212, 175, 55, 0.2)'};
              padding: 0.5em;
              text-align: left;
            }
            .prose th {
              background-color: ${isUser ? 'rgba(255, 255, 255, 0.1)' : 'rgba(212, 175, 55, 0.1)'};
              font-weight: 600;
            }
          `}</style>
          
          <MemoizedMarkdown 
            content={message.content}
            isUserMessage={isUser}
          />
        </div>
        
        {message.agent_results && message.agent_results.length > 0 && (
          <div className="mt-4">
            <AgentResultsDisplay agentResults={message.agent_results} />
          </div>
        )}
      </div>
    </div>
  )
}, (prevProps, nextProps) => {
  // Custom comparison: only re-render if message actually changed
  const prevMsg = prevProps.message
  const nextMsg = nextProps.message
  
  return (
    prevMsg.id === nextMsg.id &&
    prevMsg.content === nextMsg.content &&
    prevMsg.role === nextMsg.role &&
    JSON.stringify(prevMsg.agent_results) === JSON.stringify(nextMsg.agent_results)
  )
})

MemoizedChatMessage.displayName = 'MemoizedChatMessage'
