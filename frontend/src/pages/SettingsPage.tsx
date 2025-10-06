import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  VStack,
  HStack,
  Text,
  Input,
  Button,
  FormControl,
  FormLabel,
  FormHelperText,
  InputGroup,
  InputRightElement,
  IconButton,
  useToast,
  Card,
  CardHeader,
  CardBody,
  Badge,
  Divider,
  Spinner,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
} from '@chakra-ui/react';
import { ViewIcon, ViewOffIcon, CheckCircleIcon, WarningIcon } from '@chakra-ui/icons';

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
    description: 'Für Claude Modelle (Sonnet, Opus, Haiku)',
    placeholder: 'sk-ant-api03-...',
    docsUrl: 'https://console.anthropic.com/settings/keys'
  },
  {
    name: 'OpenAI (ChatGPT)',
    key: 'openai',
    label: 'OpenAI API Key',
    description: 'Für GPT-4, GPT-5 und DALL-E Modelle',
    placeholder: 'sk-proj-...',
    docsUrl: 'https://platform.openai.com/api-keys'
  },
  {
    name: 'Perplexity',
    key: 'perplexity',
    label: 'Perplexity API Key',
    description: 'Für Deep Research und Sonar Modelle',
    placeholder: 'pplx-...',
    docsUrl: 'https://www.perplexity.ai/settings/api'
  },
  {
    name: 'GitHub',
    key: 'github',
    label: 'GitHub Personal Access Token',
    description: 'Für Repository-Zugriff und Code-Export',
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
  const toast = useToast();

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
        toast({
          title: 'Nicht angemeldet',
          description: 'Bitte melden Sie sich an',
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
      toast({
        title: 'Ungültiger API Key',
        description: 'Bitte geben Sie einen gültigen API Key ein',
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
        toast({
          title: 'API Key gespeichert',
          description: `${PROVIDERS.find(p => p.key === provider)?.name} Key erfolgreich gespeichert`,
          status: 'success',
          duration: 3000,
        });
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Fehler beim Speichern');
      }
    } catch (error) {
      toast({
        title: 'Fehler',
        description: error instanceof Error ? error.message : 'API Key konnte nicht gespeichert werden',
        status: 'error',
        duration: 5000,
      });
    } finally {
      setSaving({ ...saving, [provider]: false });
    }
  };

  const deleteApiKey = async (provider: string) => {
    if (!window.confirm(`Möchten Sie den ${PROVIDERS.find(p => p.key === provider)?.name} API Key wirklich löschen?`)) {
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
        toast({
          title: 'API Key gelöscht',
          description: `${PROVIDERS.find(p => p.key === provider)?.name} Key wurde entfernt`,
          status: 'info',
          duration: 3000,
        });
      }
    } catch (error) {
      toast({
        title: 'Fehler',
        description: 'API Key konnte nicht gelöscht werden',
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
        
        // Update key with test result
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

        toast({
          title: data.success ? 'Verbindung erfolgreich' : 'Verbindung fehlgeschlagen',
          description: data.message,
          status: data.success ? 'success' : 'error',
          duration: 5000,
        });
      }
    } catch (error) {
      toast({
        title: 'Verbindungstest fehlgeschlagen',
        description: error instanceof Error ? error.message : 'Unbekannter Fehler',
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
      <Container maxW="container.xl" py={8}>
        <VStack spacing={4}>
          <Spinner size="xl" />
          <Text>Lade API Keys...</Text>
        </VStack>
      </Container>
    );
  }

  return (
    <Container maxW="container.xl" py={8}>
      <VStack spacing={8} align="stretch">
        {/* Header */}
        <Box>
          <Heading size="lg" mb={2}>⚙️ Einstellungen</Heading>
          <Text color="gray.400">
            Verwalten Sie Ihre API Keys für verschiedene KI-Provider
          </Text>
        </Box>

        {/* Info Alert */}
        <Alert status="info" variant="left-accent" borderRadius="md">
          <AlertIcon />
          <Box>
            <AlertTitle>Sichere Speicherung</AlertTitle>
            <AlertDescription>
              Alle API Keys werden verschlüsselt (AES-128) in der Datenbank gespeichert.
              Sie werden niemals im Klartext angezeigt oder protokolliert.
            </AlertDescription>
          </Box>
        </Alert>

        {/* API Key Cards */}
        {PROVIDERS.map((provider) => {
          const existingKey = apiKeys[provider.key];
          const isSaving = saving[provider.key];
          const isTesting = testing[provider.key];

          return (
            <Card key={provider.key} variant="outline" bg="rgba(255, 255, 255, 0.02)">
              <CardHeader>
                <HStack justify="space-between">
                  <Box>
                    <HStack>
                      <Heading size="md">{provider.name}</Heading>
                      {existingKey && (
                        <Badge colorScheme="green">
                          <HStack spacing={1}>
                            <CheckCircleIcon />
                            <Text>Konfiguriert</Text>
                          </HStack>
                        </Badge>
                      )}
                      {existingKey?.last_test_status === 'success' && (
                        <Badge colorScheme="blue">Verbindung OK</Badge>
                      )}
                      {existingKey?.last_test_status === 'failed' && (
                        <Badge colorScheme="red">
                          <HStack spacing={1}>
                            <WarningIcon />
                            <Text>Verbindung fehlgeschlagen</Text>
                          </HStack>
                        </Badge>
                      )}
                    </HStack>
                    <Text fontSize="sm" color="gray.400" mt={1}>
                      {provider.description}
                    </Text>
                  </Box>
                  <Button
                    as="a"
                    href={provider.docsUrl}
                    target="_blank"
                    size="sm"
                    variant="ghost"
                    colorScheme="blue"
                  >
                    API Key erhalten →
                  </Button>
                </HStack>
              </CardHeader>

              <CardBody>
                <VStack spacing={4} align="stretch">
                  {/* Existing Key Display */}
                  {existingKey && (
                    <Box>
                      <FormLabel fontSize="sm">Aktueller API Key</FormLabel>
                      <HStack>
                        <Input
                          value={existingKey.masked_key}
                          isReadOnly
                          bg="gray.900"
                          fontFamily="monospace"
                          size="sm"
                        />
                        <Button
                          size="sm"
                          colorScheme="blue"
                          onClick={() => testConnection(provider.key)}
                          isLoading={isTesting}
                          leftIcon={<CheckCircleIcon />}
                        >
                          Testen
                        </Button>
                        <Button
                          size="sm"
                          colorScheme="red"
                          variant="outline"
                          onClick={() => deleteApiKey(provider.key)}
                        >
                          Löschen
                        </Button>
                      </HStack>
                      <Text fontSize="xs" color="gray.500" mt={1}>
                        Zuletzt aktualisiert: {new Date(existingKey.updated_at).toLocaleString('de-DE')}
                      </Text>
                    </Box>
                  )}

                  <Divider />

                  {/* New Key Input */}
                  <FormControl>
                    <FormLabel>{existingKey ? 'Neuen' : ''} {provider.label} eingeben</FormLabel>
                    <InputGroup size="md">
                      <Input
                        type={showKeys[provider.key] ? 'text' : 'password'}
                        placeholder={provider.placeholder}
                        value={inputValues[provider.key] || ''}
                        onChange={(e) => setInputValues({ ...inputValues, [provider.key]: e.target.value })}
                        fontFamily="monospace"
                      />
                      <InputRightElement>
                        <IconButton
                          aria-label={showKeys[provider.key] ? 'Key verbergen' : 'Key anzeigen'}
                          icon={showKeys[provider.key] ? <ViewOffIcon /> : <ViewIcon />}
                          onClick={() => toggleShowKey(provider.key)}
                          size="sm"
                          variant="ghost"
                        />
                      </InputRightElement>
                    </InputGroup>
                    <FormHelperText>
                      Ihr API Key wird verschlüsselt gespeichert und ist nur für Sie sichtbar
                    </FormHelperText>
                  </FormControl>

                  <Button
                    colorScheme="green"
                    onClick={() => saveApiKey(provider.key)}
                    isLoading={isSaving}
                    isDisabled={!inputValues[provider.key] || inputValues[provider.key].length < 10}
                    leftIcon={<CheckCircleIcon />}
                  >
                    {existingKey ? 'Aktualisieren' : 'Speichern'}
                  </Button>
                </VStack>
              </CardBody>
            </Card>
          );
        })}

        {/* Footer Info */}
        <Box p={4} bg="rgba(255, 255, 255, 0.02)" borderRadius="md">
          <Text fontSize="sm" color="gray.400">
            💡 <strong>Tipp:</strong> Sie können mehrere Provider konfigurieren und zwischen ihnen wechseln.
            Die API Keys werden nur für Ihre Anfragen verwendet und niemals geteilt.
          </Text>
        </Box>
      </VStack>
    </Container>
  );
};