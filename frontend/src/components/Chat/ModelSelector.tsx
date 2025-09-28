import React from 'react'
import { useChatContext } from '@/context/ChatContext'
import { ChevronDown, Zap } from 'lucide-react'
import { cn } from '@/lib/utils'

const AVAILABLE_MODELS = [
  {
    id: 'gpt-4o',
    name: 'GPT-4o',
    provider: 'OpenAI',
    description: 'Most capable model, best for complex tasks'
  },
  {
    id: 'gpt-4o-mini',
    name: 'GPT-4o Mini',
    provider: 'OpenAI',
    description: 'Fast and efficient, good for most tasks'
  },
  {
    id: 'claude-3-5-sonnet',
    name: 'Claude 3.5 Sonnet',
    provider: 'Anthropic',
    description: 'Excellent reasoning and analysis capabilities'
  },
  {
    id: 'perplexity-sonar',
    name: 'Perplexity Sonar',
    provider: 'Perplexity',
    description: 'Real-time web search and research'
  }
]

export const ModelSelector: React.FC = () => {
  const { currentModel, setCurrentModel, currentAgent, agents } = useChatContext()
  const [isOpen, setIsOpen] = React.useState(false)
  
  const selectedModel = AVAILABLE_MODELS.find(m => m.id === currentModel)
  const currentAgentInfo = agents.find(a => a.id === currentAgent)
  
  // Filter models based on current agent's supported models
  const availableModels = AVAILABLE_MODELS.filter(model => 
    currentAgentInfo?.models.includes(model.id)
  )
  
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
        <Zap className="h-4 w-4 text-primary" />
        <span className="text-sm font-medium">
          {selectedModel?.name || 'Select Model'}
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
            {availableModels.map((model) => (
              <button
                key={model.id}
                onClick={() => {
                  setCurrentModel(model.id)
                  setIsOpen(false)
                }}
                className={cn(
                  "w-full p-3 text-left hover:bg-primary/10 transition-colors duration-200",
                  "border-b border-primary/10 last:border-b-0",
                  currentModel === model.id ? "bg-primary/10" : ""
                )}
              >
                <div className="flex items-start space-x-3">
                  <Zap className="h-5 w-5 text-primary mt-0.5" />
                  <div className="flex-1">
                    <div className="flex items-center space-x-2">
                      <span className="font-medium text-primary">{model.name}</span>
                      <span className="text-xs px-2 py-1 bg-primary/20 text-primary rounded">
                        {model.provider}
                      </span>
                    </div>
                    <div className="text-xs text-muted-foreground mt-1">
                      {model.description}
                    </div>
                  </div>
                </div>
              </button>
            ))}
            
            {availableModels.length === 0 && (
              <div className="p-3 text-center text-muted-foreground text-sm">
                No models available for {currentAgentInfo?.name}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  )
}