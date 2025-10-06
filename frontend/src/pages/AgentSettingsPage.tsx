import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Heading,
  VStack,
  Text,
  Button,
  Input,
  FormControl,
  FormLabel,
  Switch,
  Select,
  useToast,
  Card,
  CardHeader,
  CardBody,
  Stack,
  Badge,
  List,
  ListItem,
  ListIcon,
  Divider,
  Alert,
  AlertIcon,
  AlertTitle,
  AlertDescription,
  Code,
  Textarea
} from '@chakra-ui/react';
import { FiCheckCircle, FiCircle, FiFolderPlus, FiTrash2 } from 'react-icons/fi';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001';

interface AgentSettings {
  watch_directories: string[];
  sonnet_enabled: boolean;
  opus_enabled: boolean;
  auto_analysis_enabled: boolean;
  suggestions_enabled: boolean;
  notification_level: string;
}

interface AgentStatus {
  connected: boolean;
  agent_count: number;
  last_activity: string | null;
  last_connection: string | null;
}

const AgentSettingsPage: React.FC = () => {
  const [settings, setSettings] = useState<AgentSettings>({
    watch_directories: [],
    sonnet_enabled: true,
    opus_enabled: true,
    auto_analysis_enabled: true,
    suggestions_enabled: true,
    notification_level: 'all'
  });
  
  const [status, setStatus] = useState<AgentStatus>({
    connected: false,
    agent_count: 0,
    last_activity: null,
    last_connection: null
  });
  
  const [claudeApiKey, setClaudeApiKey] = useState('');
  const [newDirectory, setNewDirectory] = useState('');
  const [loading, setLoading] = useState(false);
  const toast = useToast();

  useEffect(() => {
    loadSettings();
    loadStatus();
    
    // Poll status every 10 seconds
    const interval = setInterval(loadStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadSettings = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/agent/settings`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setSettings(data);
      }
    } catch (error) {
      console.error('Failed to load settings:', error);
    }
  };

  const loadStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/agent/status`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
      }
    } catch (error) {
      console.error('Failed to load status:', error);
    }
  };

  const saveSettings = async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${BACKEND_URL}/api/agent/settings`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          ...settings,
          claude_api_key: claudeApiKey || undefined
        })
      });
      
      if (response.ok) {
        toast({
          title: 'Einstellungen gespeichert',
          description: 'Agent-Einstellungen wurden erfolgreich aktualisiert.',
          status: 'success',
          duration: 3000,
          isClosable: true
        });
        setClaudeApiKey(''); // Clear API key input
      } else {
        throw new Error('Failed to save settings');
      }
    } catch (error) {
      toast({
        title: 'Fehler',
        description: 'Einstellungen konnten nicht gespeichert werden.',
        status: 'error',
        duration: 3000,
        isClosable: true
      });
    } finally {
      setLoading(false);
    }
  };

  const addDirectory = () => {
    if (newDirectory && !settings.watch_directories.includes(newDirectory)) {
      setSettings({
        ...settings,
        watch_directories: [...settings.watch_directories, newDirectory]
      });
      setNewDirectory('');
    }
  };

  const removeDirectory = (dir: string) => {
    setSettings({
      ...settings,
      watch_directories: settings.watch_directories.filter(d => d !== dir)
    });
  };

  return (
    <Container maxW="container.lg" py={8}>
      <VStack spacing={6} align="stretch">
        {/* Header */}
        <Box>
          <Heading size="lg" mb={2}>🤖 Autonomous Agent</Heading>
          <Text color="gray.600">
            Konfiguriere den lokalen Windows-Agent für automatische Code-Analyse
          </Text>
        </Box>

        {/* Status Card */}
        <Card>
          <CardHeader>
            <Heading size="md">Agent Status</Heading>
          </CardHeader>
          <CardBody>
            <Stack spacing={4}>
              <Box display="flex" alignItems="center" gap={3}>
                <Badge
                  colorScheme={status.connected ? 'green' : 'gray'}
                  fontSize="md"
                  px={3}
                  py={2}
                  borderRadius="md"
                >
                  {status.connected ? '🟢 Verbunden' : '⚫ Nicht verbunden'}
                </Badge>
                {status.connected && (
                  <Text fontSize="sm" color="gray.600">
                    {status.agent_count} Agent(s) aktiv
                  </Text>
                )}
              </Box>
              
              {status.last_activity && (
                <Text fontSize="sm" color="gray.500">
                  Letzte Aktivität: {new Date(status.last_activity).toLocaleString('de-DE')}
                </Text>
              )}
              
              {!status.connected && (
                <Alert status="info">
                  <AlertIcon />
                  <Box>
                    <AlertTitle>Agent nicht verbunden</AlertTitle>
                    <AlertDescription>
                      Starte den lokalen Agent auf deinem Windows-PC:
                      <Code mt={2} display="block" p={2}>
                        python agent/main.py --config config.json
                      </Code>
                    </AlertDescription>
                  </Box>
                </Alert>
              )}
            </Stack>
          </CardBody>
        </Card>

        {/* Watch Directories */}
        <Card>
          <CardHeader>
            <Heading size="md">Überwachte Verzeichnisse</Heading>
            <Text fontSize="sm" color="gray.600" mt={2}>
              Windows-Pfade, die der Agent überwachen soll (z.B. C:\Users\YourName\Projects)
            </Text>
          </CardHeader>
          <CardBody>
            <VStack spacing={4} align="stretch">
              <Box display="flex" gap={2}>
                <Input
                  placeholder="C:\Users\YourName\Projects"
                  value={newDirectory}
                  onChange={(e) => setNewDirectory(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addDirectory()}
                />
                <Button
                  leftIcon={<FiFolderPlus />}
                  colorScheme="blue"
                  onClick={addDirectory}
                >
                  Hinzufügen
                </Button>
              </Box>
              
              <List spacing={2}>
                {settings.watch_directories.map((dir, index) => (
                  <ListItem
                    key={index}
                    display="flex"
                    alignItems="center"
                    justifyContent="space-between"
                    p={2}
                    bg="gray.50"
                    borderRadius="md"
                  >
                    <Box display="flex" alignItems="center" gap={2}>
                      <ListIcon as={FiCheckCircle} color="green.500" />
                      <Code fontSize="sm">{dir}</Code>
                    </Box>
                    <Button
                      size="sm"
                      variant="ghost"
                      colorScheme="red"
                      leftIcon={<FiTrash2 />}
                      onClick={() => removeDirectory(dir)}
                    >
                      Entfernen
                    </Button>
                  </ListItem>
                ))}
                {settings.watch_directories.length === 0 && (
                  <Text color="gray.500" fontSize="sm">
                    Keine Verzeichnisse konfiguriert
                  </Text>
                )}
              </List>
            </VStack>
          </CardBody>
        </Card>

        {/* Claude API Key */}
        <Card>
          <CardHeader>
            <Heading size="md">Claude API Schlüssel</Heading>
            <Text fontSize="sm" color="gray.600" mt={2}>
              Optional: Eigener Claude API Schlüssel für Code-Analyse
            </Text>
          </CardHeader>
          <CardBody>
            <FormControl>
              <FormLabel>Claude API Key</FormLabel>
              <Textarea
                placeholder="sk-ant-api03-..."
                value={claudeApiKey}
                onChange={(e) => setClaudeApiKey(e.target.value)}
                fontFamily="monospace"
                fontSize="sm"
                rows={3}
              />
              <Text fontSize="xs" color="gray.500" mt={2}>
                Wird verschlüsselt gespeichert. Leer lassen für Server-API-Key.
              </Text>
            </FormControl>
          </CardBody>
        </Card>

        {/* AI Models */}
        <Card>
          <CardHeader>
            <Heading size="md">AI Modelle</Heading>
          </CardHeader>
          <CardBody>
            <Stack spacing={4}>
              <FormControl display="flex" alignItems="center">
                <FormLabel mb={0}>Claude Sonnet 4.5</FormLabel>
                <Switch
                  isChecked={settings.sonnet_enabled}
                  onChange={(e) => setSettings({ ...settings, sonnet_enabled: e.target.checked })}
                  colorScheme="blue"
                />
                <Text ml={3} fontSize="sm" color="gray.600">
                  Für Debugging und Code-Analyse
                </Text>
              </FormControl>
              
              <FormControl display="flex" alignItems="center">
                <FormLabel mb={0}>Claude Opus 4.1</FormLabel>
                <Switch
                  isChecked={settings.opus_enabled}
                  onChange={(e) => setSettings({ ...settings, opus_enabled: e.target.checked })}
                  colorScheme="blue"
                />
                <Text ml={3} fontSize="sm" color="gray.600">
                  Für komplexe Analysen
                </Text>
              </FormControl>
            </Stack>
          </CardBody>
        </Card>

        {/* Features */}
        <Card>
          <CardHeader>
            <Heading size="md">Features</Heading>
          </CardHeader>
          <CardBody>
            <Stack spacing={4}>
              <FormControl display="flex" alignItems="center">
                <FormLabel mb={0}>Automatische Analyse</FormLabel>
                <Switch
                  isChecked={settings.auto_analysis_enabled}
                  onChange={(e) => setSettings({ ...settings, auto_analysis_enabled: e.target.checked })}
                  colorScheme="blue"
                />
              </FormControl>
              
              <FormControl display="flex" alignItems="center">
                <FormLabel mb={0}>Vorschläge aktiviert</FormLabel>
                <Switch
                  isChecked={settings.suggestions_enabled}
                  onChange={(e) => setSettings({ ...settings, suggestions_enabled: e.target.checked })}
                  colorScheme="blue"
                />
              </FormControl>
              
              <FormControl>
                <FormLabel>Benachrichtigungslevel</FormLabel>
                <Select
                  value={settings.notification_level}
                  onChange={(e) => setSettings({ ...settings, notification_level: e.target.value })}
                >
                  <option value="all">Alle</option>
                  <option value="errors">Nur Fehler</option>
                  <option value="none">Keine</option>
                </Select>
              </FormControl>
            </Stack>
          </CardBody>
        </Card>

        {/* Save Button */}
        <Button
          colorScheme="blue"
          size="lg"
          onClick={saveSettings}
          isLoading={loading}
        >
          Einstellungen speichern
        </Button>

        {/* Instructions */}
        <Card>
          <CardHeader>
            <Heading size="md">Installation & Nutzung</Heading>
          </CardHeader>
          <CardBody>
            <VStack align="stretch" spacing={3}>
              <Box>
                <Text fontWeight="bold" mb={2}>1. Agent installieren:</Text>
                <Code display="block" p={3} bg="gray.50" borderRadius="md">
                  cd agent{'\n'}
                  pip install -r requirements.txt
                </Code>
              </Box>
              
              <Box>
                <Text fontWeight="bold" mb={2}>2. Konfiguration erstellen:</Text>
                <Code display="block" p={3} bg="gray.50" borderRadius="md" whiteSpace="pre">
                  {`{
  "backend_url": "${BACKEND_URL}",
  "watch_directories": [
    "C:\\\\Users\\\\YourName\\\\Projects"
  ]
}`}
                </Code>
              </Box>
              
              <Box>
                <Text fontWeight="bold" mb={2}>3. Agent starten:</Text>
                <Code display="block" p={3} bg="gray.50" borderRadius="md">
                  python main.py --config config.json
                </Code>
              </Box>
              
              <Alert status="info">
                <AlertIcon />
                <Text fontSize="sm">
                  Der Agent läuft lokal auf deinem Windows-PC und sendet Dateiänderungen an dieses Backend zur Analyse.
                </Text>
              </Alert>
            </VStack>
          </CardBody>
        </Card>
      </VStack>
    </Container>
  );
};

export default AgentSettingsPage;
