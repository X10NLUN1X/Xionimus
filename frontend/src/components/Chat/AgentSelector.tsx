import React from 'react'
import { useChatContext } from '@/context/ChatContext'
import { ChevronDown, Bot } from 'lucide-react'
import { cn } from '@/lib/utils'

export const AgentSelector: React.FC = () => {
  const { agents, currentAgent, setCurrentAgent } = useChatContext()
  const [isOpen, setIsOpen] = React.useState(false)
  
  const selectedAgent = agents.find(a => a.id === currentAgent)
  
  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          "flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors duration-200",
          "bg-secondary border border-primary/20 text-foreground",
          "hover:bg-secondary/80 focus:outline-none focus:ring-2 focus:ring-primary/50"
        )}
      >
        <Bot className="h-4 w-4 text-primary" />
        <span className="text-sm font-medium">
          {selectedAgent?.name || 'Select Agent'}
        </span>
        <ChevronDown className={cn(
          "h-4 w-4 transition-transform duration-200",
          isOpen ? "transform rotate-180" : ""
        )} />
      </button>
      
      {isOpen && (
        <>
          <div 
            className="fixed inset-0 z-10" 
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute top-full left-0 mt-1 w-80 z-20 bg-secondary border border-primary/20 rounded-lg shadow-lg max-h-96 overflow-y-auto">
            {agents.map((agent) => (
              <button
                key={agent.id}
                onClick={() => {
                  setCurrentAgent(agent.id)
                  setIsOpen(false)
                }}
                className={cn(
                  "w-full p-3 text-left hover:bg-primary/10 transition-colors duration-200",
                  "border-b border-primary/10 last:border-b-0",
                  currentAgent === agent.id ? "bg-primary/10" : ""
                )}
              >
                <div className="flex items-start space-x-3">
                  <Bot className="h-5 w-5 text-primary mt-0.5" />
                  <div className="flex-1">
                    <div className="font-medium text-primary">{agent.name}</div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {agent.description}
                    </div>
                    <div className="flex flex-wrap gap-1 mt-2">
                      {agent.capabilities.slice(0, 3).map((cap) => (
                        <span
                          key={cap}
                          className="text-xs px-2 py-1 bg-primary/20 text-primary rounded"
                        >
                          {cap}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}