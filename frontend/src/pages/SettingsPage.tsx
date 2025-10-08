import React, { useState, useEffect } from 'react';
import { Button } from '../components/UI/Button';
import { Input } from '../components/UI/Input';
import { Card, CardHeader, CardBody } from '../components/UI/Card';
import { Badge } from '../components/UI/Badge';
import { useToast } from '../components/UI/Toast';
import { getGitHubOAuthStatus, initiateGitHubOAuth } from '../services/githubOAuthService';

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
  }
];

export const SettingsPage: React.FC = () => {
  const [apiKeys, setApiKeys] = useState<Record<string, ApiKey>>({});
  const [inputValues, setInputValues] = useState<Record<string, string>>({});
  const [showKeys, setShowKeys] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState<Record<string, boolean>>({});
  const [testing, setTesting] = useState<Record<string, boolean>>({});
  
  // GitHub OAuth state
  const [githubConnected, setGithubConnected] = useState(false);
  const [githubUsername, setGithubUsername] = useState<string | null>(null);
  const [checkingGitHub, setCheckingGitHub] = useState(true);
  
  // GitHub OAuth Credentials Configuration
  const [oauthClientId, setOauthClientId] = useState('');
  const [oauthClientSecret, setOauthClientSecret] = useState('');
  const [oauthCallbackUrl, setOauthCallbackUrl] = useState('http://localhost:3000/github/callback');
  const [oauthConfigured, setOauthConfigured] = useState(false);
  const [savingOauth, setSavingOauth] = useState(false);
  const [showOauthConfig, setShowOauthConfig] = useState(false);
  
  const { showToast } = useToast();

  const backendUrl = import.meta.env.VITE_BACKEND_URL || 
                     import.meta.env.REACT_APP_BACKEND_URL || 
                     'http://localhost:8001';

  useEffect(() => {
    loadApiKeys();
    checkGitHubOAuth();
    loadOAuthConfig();
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

  const checkGitHubOAuth = async () => {
    setCheckingGitHub(true);
    try {
      const token = localStorage.getItem('xionimus_token');
      if (!token) {
        setGithubConnected(false);
        return;
      }

      const status = await getGitHubOAuthStatus(token);
      setGithubConnected(status.connected);
      setGithubUsername(status.github_username);
    } catch (error) {
      console.error('Failed to check GitHub OAuth status:', error);
      setGithubConnected(false);
    } finally {
      setCheckingGitHub(false);
    }
  };

  const handleConnectGitHub = async () => {
    try {
      const token = localStorage.getItem('xionimus_token');
      if (!token) {
        showToast({
          title: 'Not Logged In',
          description: 'Please log in first',
          status: 'error',
          duration: 3000
        });
        return;
      }

      // Check GitHub status first
      const response = await fetch(`${backendUrl}/api/v1/github/oauth/status`);
      const status = await response.json();
      
      if (status.mode === 'pat' && status.configured) {
        // PAT mode - GitHub is already configured
        showToast({
          title: 'GitHub Already Connected',
          description: 'GitHub is configured with Personal Access Token and ready to use',
          status: 'success',
          duration: 3000
        });
        
        // Refresh OAuth status
        await checkGitHubOAuth();
        return;
      }

      await initiateGitHubOAuth(token);
    } catch (error: any) {
      console.error('Failed to initiate GitHub OAuth:', error);
      
      // Extract detailed error message if available
      let errorMessage = 'Could not start GitHub OAuth';
      
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (typeof detail === 'object' && detail.message) {
          errorMessage = detail.message;
        } else if (typeof detail === 'string') {
          errorMessage = detail;
        }
      }
      
      // Check for authentication errors
      if (error.response?.status === 401) {
        errorMessage = 'Authentication failed. Please log in again.';
      } else if (error.response?.status === 503) {
        errorMessage = 'GitHub OAuth is not configured. Please contact your administrator.';
      }
      
      showToast({
        title: 'GitHub OAuth Error',
        description: errorMessage,
        status: 'error',
        duration: 5000
      });
    }
  };

  const loadOAuthConfig = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/v1/github/admin/github-oauth/status`);
      const data = await response.json();
      
      if (data.configured) {
        setOauthConfigured(true);
        setOauthClientId(data.client_id || '');
        setOauthCallbackUrl(data.callback_url || 'http://localhost:3000/github/callback');
      }
    } catch (error) {
      console.error('Failed to load OAuth config:', error);
    }
  };

  const saveOAuthCredentials = async () => {
    if (!oauthClientId.trim() || !oauthClientSecret.trim()) {
      showToast({
        title: 'Validation Error',
        description: 'Please enter both Client ID and Client Secret',
        status: 'error',
        duration: 3000
      });
      return;
    }

    setSavingOauth(true);
    try {
      const response = await fetch(`${backendUrl}/api/v1/github/admin/github-oauth/store`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          client_id: oauthClientId,
          client_secret: oauthClientSecret,
          callback_url: oauthCallbackUrl
        })
      });

      const data = await response.json();

      if (data.success) {
        setOauthConfigured(true);
        setOauthClientSecret(''); // Clear secret from state
        setShowOauthConfig(false);
        
        showToast({
          title: 'Success',
          description: 'GitHub OAuth credentials saved securely',
          status: 'success',
          duration: 3000
        });
      } else {
        throw new Error(data.message || 'Failed to save credentials');
      }
    } catch (error: any) {
      showToast({
        title: 'Error',
        description: error.message || 'Failed to save OAuth credentials',
        status: 'error',
        duration: 5000
      });
    } finally {
      setSavingOauth(false);
    }
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

        {/* GitHub OAuth Section */}
        <Card hover>
          <CardHeader>
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <div className="flex-1">
                <div className="flex flex-wrap items-center gap-2 mb-2">
                  <h2 className="text-2xl font-bold text-white">GitHub</h2>
                  {checkingGitHub ? (
                    <Badge variant="info">
                      <span className="flex items-center gap-1">
                        <svg className="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Checking...
                      </span>
                    </Badge>
                  ) : githubConnected ? (
                    <Badge variant="success">
                      <span className="flex items-center gap-1">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        Connected
                      </span>
                    </Badge>
                  ) : (
                    <Badge variant="warning">Not Connected</Badge>
                  )}
                </div>
                <p className="text-gray-400">
                  OAuth Integration for Repository Access and Code Export
                </p>
              </div>
              <a
                href="https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gold-400 hover:text-gold-300 text-sm font-medium transition-colors whitespace-nowrap"
              >
                Learn More →
              </a>
            </div>
          </CardHeader>

          <CardBody>
            {/* OAuth Configuration Section */}
            <div className="mb-6 pb-6 border-b border-gray-700">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <h4 className="text-lg font-semibold text-white">OAuth Configuration</h4>
                  {oauthConfigured && (
                    <Badge variant="success">
                      <span className="flex items-center gap-1">
                        <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        Configured
                      </span>
                    </Badge>
                  )}
                </div>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => setShowOauthConfig(!showOauthConfig)}
                  leftIcon={
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={showOauthConfig ? "M19 9l-7 7-7-7" : "M9 5l7 7-7 7"} />
                    </svg>
                  }
                >
                  {showOauthConfig ? 'Hide' : oauthConfigured ? 'Update' : 'Configure'}
                </Button>
              </div>

              {showOauthConfig && (
                <div className="space-y-4 glossy-card p-4 bg-gray-800/50 border border-gray-700 rounded-lg">
                  <div className="glossy-card p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                    <p className="text-sm text-gray-300">
                      <strong className="text-blue-400">Setup Instructions:</strong>
                    </p>
                    <ol className="mt-2 space-y-1 text-sm text-gray-400 ml-4 list-decimal">
                      <li>Go to <a href="https://github.com/settings/developers" target="_blank" rel="noopener noreferrer" className="text-gold-400 hover:underline">GitHub Developer Settings</a></li>
                      <li>Click "New OAuth App"</li>
                      <li>Set Homepage URL to your application URL</li>
                      <li>Set Authorization callback URL (e.g., http://localhost:3000/github/callback)</li>
                      <li>Copy Client ID and Client Secret below</li>
                    </ol>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Client ID
                    </label>
                    <Input
                      type="text"
                      value={oauthClientId}
                      onChange={(e) => setOauthClientId(e.target.value)}
                      placeholder="Ov23liXXXXXXXXXXXXXX"
                      className="w-full"
                    />
                    <p className="text-xs text-gray-500 mt-1">Starts with "Ov"</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Client Secret
                    </label>
                    <Input
                      type="password"
                      value={oauthClientSecret}
                      onChange={(e) => setOauthClientSecret(e.target.value)}
                      placeholder="Enter your OAuth Client Secret"
                      className="w-full"
                    />
                    <p className="text-xs text-gray-500 mt-1">This will be encrypted and stored securely</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Callback URL
                    </label>
                    <Input
                      type="text"
                      value={oauthCallbackUrl}
                      onChange={(e) => setOauthCallbackUrl(e.target.value)}
                      placeholder="http://localhost:3000/github/callback"
                      className="w-full"
                    />
                    <p className="text-xs text-gray-500 mt-1">Must match your GitHub OAuth App settings</p>
                  </div>

                  <div className="flex gap-2">
                    <Button
                      variant="primary"
                      onClick={saveOAuthCredentials}
                      disabled={savingOauth}
                      leftIcon={
                        savingOauth ? (
                          <svg className="w-5 h-5 animate-spin" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                          </svg>
                        ) : (
                          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                        )
                      }
                    >
                      {savingOauth ? 'Saving...' : 'Save Credentials'}
                    </Button>
                    <Button
                      variant="secondary"
                      onClick={() => setShowOauthConfig(false)}
                      disabled={savingOauth}
                    >
                      Cancel
                    </Button>
                  </div>
                </div>
              )}

              {oauthConfigured && !showOauthConfig && (
                <div className="glossy-card p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
                  <div className="flex items-start gap-2">
                    <svg className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div className="text-sm">
                      <p className="text-green-400 font-medium">OAuth credentials configured</p>
                      <p className="text-gray-400 mt-1">Client ID: <span className="font-mono text-gray-300">{oauthClientId}</span></p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* GitHub Connection Status */}
            {githubConnected ? (
              <div className="space-y-4">
                <div className="glossy-card p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
                  <div className="flex items-center gap-3">
                    <svg className="w-6 h-6 text-green-400" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                    </svg>
                    <div>
                      <p className="font-semibold text-green-400">Connected as {githubUsername}</p>
                      <p className="text-sm text-gray-400">You can now import and export repositories</p>
                    </div>
                  </div>
                </div>
                
                <Button
                  variant="secondary"
                  onClick={checkGitHubOAuth}
                  leftIcon={
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                  }
                >
                  Refresh Connection Status
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="glossy-card p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                  <div className="flex items-start gap-3">
                    <svg className="w-6 h-6 text-yellow-400 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    <div>
                      <p className="font-semibold text-yellow-400 mb-1">GitHub Not Connected</p>
                      <p className="text-sm text-gray-300">
                        Connect your GitHub account to import repositories, export code, and manage your projects directly from Xionimus AI.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="glossy-card p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                  <h4 className="font-semibold text-blue-400 mb-2">What you get with GitHub OAuth:</h4>
                  <ul className="space-y-2 text-sm text-gray-300">
                    <li className="flex items-start gap-2">
                      <svg className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span>Access your repositories without managing tokens</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <svg className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span>Import code directly from GitHub</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <svg className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span>Export and push code to your repositories</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <svg className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span>Secure OAuth 2.0 authentication</span>
                    </li>
                  </ul>
                </div>

                <Button
                  variant="primary"
                  onClick={handleConnectGitHub}
                  leftIcon={
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                    </svg>
                  }
                  className="w-full md:w-auto"
                >
                  Connect with GitHub
                </Button>
              </div>
            )}
          </CardBody>
        </Card>

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
