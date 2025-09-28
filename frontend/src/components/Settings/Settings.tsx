import React from 'react'
import { useChatContext } from '@/context/ChatContext'
import { Button } from '@/components/ui/Button'
import { Key, Save, Eye, EyeOff } from 'lucide-react'
import { toast } from 'sonner'

export const Settings: React.FC = () => {
  const { apiKeys, updateApiKeys } = useChatContext()
  const [formKeys, setFormKeys] = React.useState(apiKeys)
  const [showKeys, setShowKeys] = React.useState({
    openai: false,
    anthropic: false,
    perplexity: false
  })

  React.useEffect(() => {
    setFormKeys(apiKeys)
  }, [apiKeys])

  const handleSave = () => {
    updateApiKeys(formKeys)
    toast.success('API keys saved successfully')
  }

  const toggleShowKey = (provider: keyof typeof showKeys) => {
    setShowKeys(prev => ({
      ...prev,
      [provider]: !prev[provider]
    }))
  }

  const apiProviders = [
    {
      key: 'openai' as const,
      name: 'OpenAI',
      description: 'Required for GPT models (gpt-4o, gpt-4o-mini)',
      placeholder: 'sk-...'
    },
    {
      key: 'anthropic' as const,
      name: 'Anthropic',
      description: 'Required for Claude models (claude-3-5-sonnet)',
      placeholder: 'sk-ant-...'
    },
    {
      key: 'perplexity' as const,
      name: 'Perplexity',
      description: 'Required for research and web search capabilities',
      placeholder: 'pplx-...'
    }
  ]

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-primary mb-2">Settings</h1>
        <p className="text-muted-foreground">
          Configure your API keys and application preferences.
        </p>
      </div>

      {/* API Keys Section */}
      <div className="bg-secondary rounded-lg border border-primary/20 p-6 mb-6">
        <div className="flex items-center space-x-2 mb-4">
          <Key className="h-5 w-5 text-primary" />
          <h2 className="text-xl font-semibold text-primary">API Keys</h2>
        </div>
        
        <p className="text-muted-foreground mb-6">
          Add your AI service API keys to enable the full functionality of XIONIMUS AI.
        </p>

        <div className="space-y-6">
          {apiProviders.map((provider) => (
            <div key={provider.key} className="space-y-2">
              <label className="block text-sm font-medium text-primary">
                {provider.name} API Key
              </label>
              <p className="text-xs text-muted-foreground mb-2">
                {provider.description}
              </p>
              
              <div className="relative">
                <input
                  type={showKeys[provider.key] ? "text" : "password"}
                  value={formKeys[provider.key]}
                  onChange={(e) => setFormKeys(prev => ({
                    ...prev,
                    [provider.key]: e.target.value
                  }))}
                  placeholder={provider.placeholder}
                  className="w-full px-3 py-2 pr-10 bg-background border border-primary/20 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 transition-colors duration-200"
                />
                <button
                  type="button"
                  onClick={() => toggleShowKey(provider.key)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground hover:text-primary transition-colors duration-200"
                >
                  {showKeys[provider.key] ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </button>
              </div>
            </div>
          ))}
        </div>
        
        <div className="mt-6 pt-6 border-t border-primary/20">
          <Button onClick={handleSave}>
            <Save className="h-4 w-4 mr-2" />
            Save API Keys
          </Button>
        </div>
      </div>

      {/* System Information */}
      <div className="bg-secondary rounded-lg border border-primary/20 p-6">
        <h2 className="text-xl font-semibold text-primary mb-4">System Information</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
          <div>
            <span className="font-medium text-primary">Version:</span>
            <span className="ml-2 text-muted-foreground">3.0.0</span>
          </div>
          <div>
            <span className="font-medium text-primary">Frontend:</span>
            <span className="ml-2 text-muted-foreground">React 18 + Vite</span>
          </div>
          <div>
            <span className="font-medium text-primary">Backend:</span>
            <span className="ml-2 text-muted-foreground">FastAPI + MongoDB</span>
          </div>
          <div>
            <span className="font-medium text-primary">AI Agents:</span>
            <span className="ml-2 text-muted-foreground">9 Specialized Agents</span>
          </div>
        </div>
      </div>
    </div>
  )
}