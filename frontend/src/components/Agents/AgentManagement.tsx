import React from 'react'
import { useChatContext } from '@/context/ChatContext'
import { Button } from '@/components/ui/Button'
import { Bot, Users, Zap, Code, Search, Edit, BarChart, CheckCircle, GitBranch, FileText, MessageSquare } from 'lucide-react'
import { cn } from '@/lib/utils'

const iconMap = {
  Bot,
  Users,
  Zap,
  Code,
  Search,
  Edit,
  BarChart,
  CheckCircle,
  GitBranch,
  FileText,
  MessageSquare
}

export const AgentManagement: React.FC = () => {
  const { agents, currentAgent, setCurrentAgent, loadAgents } = useChatContext()
  const [selectedAgent, setSelectedAgent] = React.useState<string | null>(null)

  React.useEffect(() => {
    loadAgents()
  }, [])

  const handleAgentSelect = (agentId: string) => {
    setCurrentAgent(agentId)
    setSelectedAgent(agentId)
  }

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-primary mb-2">AI Agents</h1>
        <p className="text-muted-foreground">
          Choose from 9 specialized AI agents, each optimized for different tasks.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map((agent) => {
          const IconComponent = iconMap[agent.icon as keyof typeof iconMap] || Bot
          const isSelected = currentAgent === agent.id
          const isDetailSelected = selectedAgent === agent.id
          
          return (
            <div
              key={agent.id}
              className={cn(
                "p-6 rounded-lg border transition-all duration-200 cursor-pointer",
                "bg-secondary border-primary/20",
                isSelected
                  ? "ring-2 ring-primary/50 xionimus-glow"
                  : "hover:border-primary/40 hover:bg-secondary/80"
              )}
              onClick={() => handleAgentSelect(agent.id)}
            >
              <div className="flex items-start space-x-4">
                <div className={cn(
                  "flex-shrink-0 w-12 h-12 rounded-lg flex items-center justify-center",
                  "bg-primary/10 border border-primary/20"
                )}>
                  <IconComponent className="h-6 w-6 text-primary" />
                </div>
                
                <div className="flex-1">
                  <h3 className="font-semibold text-primary mb-1">{agent.name}</h3>
                  <p className="text-sm text-muted-foreground mb-3">
                    {agent.description}
                  </p>
                  
                  <div className="flex flex-wrap gap-1 mb-3">
                    {agent.capabilities.slice(0, 3).map((capability) => (
                      <span
                        key={capability}
                        className="text-xs px-2 py-1 bg-primary/20 text-primary rounded"
                      >
                        {capability}
                      </span>
                    ))}
                  </div>
                  
                  <div className="text-xs text-muted-foreground">
                    Models: {agent.models.join(', ')}
                  </div>
                </div>
              </div>
              
              {isSelected && (
                <div className="mt-4 pt-4 border-t border-primary/20">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-primary">Currently Active</span>
                    <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {agents.length === 0 && (
        <div className="text-center py-12">
          <Bot className="h-16 w-16 text-primary/50 mx-auto mb-4" />
          <h3 className="text-xl font-semibold text-primary mb-2">No Agents Found</h3>
          <p className="text-muted-foreground mb-4">
            Unable to load AI agents. Please check your backend connection.
          </p>
          <Button onClick={loadAgents} variant="outline">
            Retry Loading
          </Button>
        </div>
      )}
    </div>
  )
}