import React from 'react'
import { useChatContext } from '@/context/ChatContext'
import ReactMarkdown from 'react-markdown'
import { User, Bot, Copy, Check } from 'lucide-react'
import { Button } from '@/components/ui/Button'
import { cn } from '@/lib/utils'
import { format } from 'date-fns'

interface Message {
  id: string
  content: string
  role: 'user' | 'assistant'
  agent: string
  model: string
  timestamp: Date
  usage?: any
}

interface MessageListProps {
  messages: Message[]
}

export const MessageList: React.FC<MessageListProps> = ({ messages }) => {
  const { agents } = useChatContext()
  const [copiedId, setCopiedId] = React.useState<string | null>(null)

  const copyToClipboard = async (text: string, id: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedId(id)
      setTimeout(() => setCopiedId(null), 2000)
    } catch (error) {
      console.error('Failed to copy:', error)
    }
  }

  if (messages.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-center">
        <Bot className="h-16 w-16 text-primary/50 mb-4" />
        <h3 className="text-xl font-semibold text-primary mb-2">
          Welcome to XIONIMUS AI
        </h3>
        <p className="text-muted-foreground max-w-md">
          Start a conversation with any of our 9 specialized AI agents. 
          Choose an agent and model, then send your first message.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {messages.map((message) => {
        const isUser = message.role === 'user'
        const agent = agents.find(a => a.id === message.agent)
        
        return (
          <div
            key={message.id}
            className={cn(
              "flex items-start space-x-3",
              isUser ? "justify-end" : "justify-start"
            )}
          >
            {!isUser && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center border border-primary/20">
                <Bot className="h-4 w-4 text-primary" />
              </div>
            )}
            
            <div className={cn(
              "flex-1 max-w-3xl",
              isUser ? "order-first" : ""
            )}>
              <div className={cn(
                "rounded-lg p-4 shadow-sm",
                isUser
                  ? "bg-primary text-primary-foreground ml-auto max-w-lg"
                  : "bg-secondary border border-primary/20 xionimus-glow"
              )}>
                {!isUser && (
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center space-x-2">
                      <span className="text-xs font-medium text-primary">
                        {agent?.name || message.agent}
                      </span>
                      <span className="text-xs text-muted-foreground">
                        {message.model}
                      </span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => copyToClipboard(message.content, message.id)}
                      className="h-6 w-6 p-0"
                    >
                      {copiedId === message.id ? (
                        <Check className="h-3 w-3" />
                      ) : (
                        <Copy className="h-3 w-3" />
                      )}
                    </Button>
                  </div>
                )}
                
                <div className={cn(
                  "prose prose-sm max-w-none",
                  isUser
                    ? "prose-invert"
                    : "prose-slate prose-headings:text-primary prose-a:text-primary"
                )}>
                  {isUser ? (
                    <p className="mb-0">{message.content}</p>
                  ) : (
                    <ReactMarkdown>{message.content}</ReactMarkdown>
                  )}
                </div>
                
                <div className="mt-2 text-xs text-muted-foreground">
                  {format(message.timestamp, 'HH:mm')}
                  {message.usage && (
                    <span className="ml-2">
                      • {message.usage.input_tokens || message.usage.prompt_tokens || 0} in, 
                      {message.usage.output_tokens || message.usage.completion_tokens || 0} out
                    </span>
                  )}
                </div>
              </div>
            </div>
            
            {isUser && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary flex items-center justify-center">
                <User className="h-4 w-4 text-primary-foreground" />
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}