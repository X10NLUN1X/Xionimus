import React, { useState, useEffect } from 'react';
import { Button } from '../components/UI/Button';
import { Input } from '../components/UI/Input';
import { Card, CardHeader, CardBody } from '../components/UI/Card';
import { Badge } from '../components/UI/Badge';
import { useToast } from '../components/UI/Toast';

interface ApiKey {
  provider: string;
  masked_key: string;
  is_active: boolean;
  last_test_status?: string;
  last_test_at?: string;
  created_at: string;
  updated_at: string;
}

interface ProviderConfig {
  name: string;
  key: string;
  label: string;
  description: string;
  placeholder: string;
  docsUrl: string;
}

const PROVIDERS: ProviderConfig[] = [
  {
    name: 'Anthropic (Claude)',
    key: 'anthropic',
    label: 'Anthropic API Key',
    description: 'For Claude Models (Sonnet, Opus, Haiku)',
    placeholder: 'sk-ant-api03-...',
    docsUrl: 'https://console.anthropic.com/settings/keys'
  },
  {
    name: 'OpenAI (ChatGPT)',
    key: 'openai',
    label: 'OpenAI API Key',
    description: 'For GPT-4, GPT-5 and DALL-E Models',
    placeholder: 'sk-proj-...',
    docsUrl: 'https://platform.openai.com/api-keys'
  },
  {
    name: 'Perplexity',
    key: 'perplexity',
    label: 'Perplexity API Key',
    description: 'For Deep Research and Sonar Models',
    placeholder: 'pplx-...',
    docsUrl: 'https://www.perplexity.ai/settings/api'
  },
  {
    name: 'GitHub',
    key: 'github',
    label: 'GitHub Personal Access Token',
    description: 'For Repository Access and Code Export',
    placeholder: 'ghp_...',
    docsUrl: 'https://github.com/settings/tokens'
  }
];

export const SettingsPage: React.FC = () => {
  const [apiKeys, setApiKeys] = useState<Record<string, ApiKey>>({});
  const [inputValues, setInputValues] = useState<Record<string, string>>({});
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<Record<string, boolean>>({});
  const [testing, setTesting] = useState<Record<string, boolean>>({});
  const { showToast } = useToast();

  const backendUrl = import.meta.env.VITE_BACKEND_URL || 
                     import.meta.env.REACT_APP_BACKEND_URL || 
                     'http://localhost:8001';

  useEffect(() => {
    loadApiKeys();
  }, []);

  const loadApiKeys = async () => {
    try {
      const token = localStorage.getItem('xionimus_token');
      if (!token) {
        showToast({
          title: 'Not logged in',
          description: 'Please log in first',
          status: 'warning',
          duration: 3000,
        });
        return;
      }

      const response = await fetch(`${backendUrl}/api/api-keys/list`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        const keysMap: Record<string, ApiKey> = {};
        data.api_keys?.forEach((key: ApiKey) => {
          keysMap[key.provider] = key;
        });
        setApiKeys(keysMap);
      }
    } catch (error) {
      console.error('Failed to load API keys:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveApiKey = async (provider: string) => {
    const apiKey = inputValues[provider];
    if (!apiKey || apiKey.length < 10) {
      showToast({
        title: 'Invalid API Key',
        description: 'Please enter a valid API key',
        status: 'error',
        duration: 3000,
      });
      return;
    }

    setSaving({ ...saving, [provider]: true });

    try {
      const token = localStorage.getItem('xionimus_token');
      const response = await fetch(`${backendUrl}/api/api-keys/save`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          provider,
          api_key: apiKey
        })
      });

      if (response.ok) {
        const data = await response.json();
        setApiKeys({ ...apiKeys, [provider]: data });
        setInputValues({ ...inputValues, [provider]: '' });
        showToast({
          title: 'API Key Saved',
          description: `${PROVIDERS.find(p => p.key === provider)?.name} key saved successfully`,
          status: 'success',
          duration: 3000,
        });
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Save error');
      }
    } catch (error) {
      showToast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Could not save API key',
        status: 'error',
        duration: 5000,
      });
    } finally {
      setSaving({ ...saving, [provider]: false });
    }
  };

  const deleteApiKey = async (provider: string) => {
    if (!window.confirm(`Do you really want to delete the ${PROVIDERS.find(p => p.key === provider)?.name} API Key?`)) {
      return;
    }

    try {
      const token = localStorage.getItem('xionimus_token');
      const response = await fetch(`${backendUrl}/api/api-keys/${provider}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const newApiKeys = { ...apiKeys };
        delete newApiKeys[provider];
        setApiKeys(newApiKeys);
        showToast({
          title: 'API Key Deleted',
          description: `${PROVIDERS.find(p => p.key === provider)?.name} key removed`,
          status: 'info',
          duration: 3000,
        });
      }
    } catch (error) {
      showToast({
        title: 'Error',
        description: 'Could not delete API key',
        status: 'error',
        duration: 3000,
      });
    }
  };

  const testConnection = async (provider: string) => {
    setTesting({ ...testing, [provider]: true });

    try {
      const token = localStorage.getItem('xionimus_token');
      const response = await fetch(`${backendUrl}/api/api-keys/test-connection`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ provider })
      });

      if (response.ok) {
        const data = await response.json();
        
        if (apiKeys[provider]) {
          setApiKeys({
            ...apiKeys,
            [provider]: {
              ...apiKeys[provider],
              last_test_status: data.success ? 'success' : 'failed',
              last_test_at: data.tested_at
            }
          });
        }

        showToast({
          title: data.success ? 'Connection Successful' : 'Connection Failed',
          description: data.message,
          status: data.success ? 'success' : 'error',
          duration: 5000,
        });
      }
    } catch (error) {
      showToast({
        title: 'Connection Test Failed',
        description: error instanceof Error ? error.message : 'Unknown error',
        status: 'error',
        duration: 5000,
      });
    } finally {
      setTesting({ ...testing, [provider]: false });
    }
  };

  const toggleShowKey = (provider: string) => {
    setShowKeys({ ...showKeys, [provider]: !showKeys[provider] });
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="flex flex-col items-center justify-center space-y-4 min-h-[400px]">
          <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-gold-500"></div>
          <p className="text-gray-300">Loading API Keys...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl animate-fade-in">
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-gold-400 via-gold-500 to-gold-400 bg-clip-text text-transparent mb-3 text-glow">
            ⚙️ Settings
          </h1>
          <p className="text-gray-400 text-lg">
            Manage your API keys for various AI providers
          </p>
        </div>

        {/* Info Alert */}
        <Card className="border-blue-500/30 bg-blue-500/5">
          <div className="flex items-start">
            <span className="text-3xl mr-4">🔒</span>
            <div>
              <h3 className="font-semibold text-blue-400 mb-1">Secure Storage</h3>
              <p className="text-gray-300 text-sm">
                All API keys are encrypted (AES-128) in the database.
                They are never displayed or logged in plain text.
              </p>
            </div>
          </div>
        </Card>

        {/* API Key Cards */}
        {PROVIDERS.map((provider) => {
          const existingKey = apiKeys[provider.key];
          const isSaving = saving[provider.key];
          const isTesting = testing[provider.key];

          return (
            <Card key={provider.key} hover>
              <CardHeader>
                <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex flex-wrap items-center gap-2 mb-2">
                      <h2 className="text-2xl font-bold text-white">{provider.name}</h2>
                      {existingKey && (
                        <Badge variant="success">
                          <span className="flex items-center gap-1">
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                            Configured
                          </span>
                        </Badge>
                      )}
                      {existingKey?.last_test_status === 'success' && (
                        <Badge variant="info">Connection OK</Badge>
                      )}
                      {existingKey?.last_test_status === 'failed' && (
                        <Badge variant="error">
                          <span className="flex items-center gap-1">
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                            </svg>
                            Connection Failed
                          </span>
                        </Badge>
                      )}
                    </div>
                    <p className="text-gray-400">
                      {provider.description}
                    </p>
                  </div>
                  <a
                    href={provider.docsUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-gold-400 hover:text-gold-300 text-sm font-medium transition-colors whitespace-nowrap"
                  >
                    Get API Key →
                  </a>
                </div>
              </CardHeader>

              <CardBody>
                <div className="space-y-4">
                  {/* Existing Key Display */}
                  {existingKey && (
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Current API Key
                      </label>
                      <div className="flex gap-2">
                        <input
                          value={existingKey.masked_key}
                          readOnly
                          className="input-glossy flex-1 font-mono text-sm"
                        />
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => testConnection(provider.key)}
                          loading={isTesting}
                          leftIcon={
                            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                          }
                        >
                          Test
                        </Button>
                        <Button
                          size="sm"
                          variant="danger"
                          onClick={() => deleteApiKey(provider.key)}
                        >
                          Delete
                        </Button>
                      </div>
                      <p className="text-xs text-gray-500 mt-2">
                        Last updated: {new Date(existingKey.updated_at).toLocaleString()}
                      </p>
                    </div>
                  )}

                  {existingKey && <div className="h-px bg-gold-500/20 my-4"></div>}

                  {/* New Key Input */}
                  <div>
                    <Input
                      label={`${existingKey ? 'New ' : ''}${provider.label}`}
                      type={showKeys[provider.key] ? 'text' : 'password'}
                      placeholder={provider.placeholder}
                      value={inputValues[provider.key] || ''}
                      onChange={(e) => setInputValues({ ...inputValues, [provider.key]: e.target.value })}
                      className="font-mono"
                      helperText="Your API key will be encrypted and only visible to you"
                      rightIcon={
                        <button
                          onClick={() => toggleShowKey(provider.key)}
                          className="text-gray-400 hover:text-gold-400 transition-colors"
                          type="button"
                        >
                          {showKeys[provider.key] ? (
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                            </svg>
                          ) : (
                            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                            </svg>
                          )}
                        </button>
                      }
                    />
                  </div>

                  <Button
                    variant="primary"
                    onClick={() => saveApiKey(provider.key)}
                    loading={isSaving}
                    disabled={!inputValues[provider.key] || inputValues[provider.key].length < 10}
                    leftIcon={
                      <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    }
                    className="w-full md:w-auto"
                  >
                    {existingKey ? 'Update' : 'Save'}
                  </Button>
                </div>
              </CardBody>
            </Card>
          );
        })}

        {/* Footer Info */}
        <Card className="bg-accent-blue/30">
          <div className="flex items-start">
            <span className="text-2xl mr-3">💡</span>
            <p className="text-sm text-gray-300">
              <strong className="text-gold-400">Tip:</strong> You can configure multiple providers and switch between them.
              API keys are only used for your requests and never shared.
            </p>
          </div>
        </Card>
      </div>
    </div>
  );
};
