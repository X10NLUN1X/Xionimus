import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Textarea } from './components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from './components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';
import { Badge } from './components/ui/badge';
import { ScrollArea } from './components/ui/scroll-area';
import { Separator } from './components/ui/separator';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './components/ui/select';
import { toast } from 'sonner';
import { Toaster } from './components/ui/sonner';
import { 
  MessageSquare, 
  Code, 
  FolderOpen, 
  Settings, 
  Send, 
  Plus, 
  Search,
  Terminal,
  Brain,
  Key,
  Save,
  Trash2,
  Edit,
  FileText,
  Zap,
  Bot,
  User,
  Copy
} from 'lucide-react';
import Editor from '@monaco-editor/react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  // State management
  const [activeTab, setActiveTab] = useState('chat');
  const [messages, setMessages] = useState([]);
  const [currentMessage, setCurrentMessage] = useState('');
  const [selectedModel, setSelectedModel] = useState('claude');
  const [isLoading, setIsLoading] = useState(false);
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectFiles, setProjectFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [apiKeys, setApiKeys] = useState({
    perplexity: false,
    anthropic: false
  });
  const [showApiKeyDialog, setShowApiKeyDialog] = useState(false);
  const [newProject, setNewProject] = useState({ name: '', description: '' });
  const [showNewProjectDialog, setShowNewProjectDialog] = useState(false);
  const [codeGenPrompt, setCodeGenPrompt] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('python');
  const [availableAgents, setAvailableAgents] = useState([]);
  const [useAgents, setUseAgents] = useState(true);
  const [currentTaskId, setCurrentTaskId] = useState(null);
  const [processingSteps, setProcessingSteps] = useState([]);
  const [detectedLanguage, setDetectedLanguage] = useState(null);
  
  const messagesEndRef = useRef(null);
  const editorRef = useRef(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load initial data
  useEffect(() => {
    loadApiKeysStatus();
    loadProjects();
    loadAvailableAgents();
  }, []);

  const loadApiKeysStatus = async () => {
    try {
      const response = await axios.get(`${API}/api-keys/status`);
      setApiKeys(response.data);
    } catch (error) {
      console.error('Error loading API keys status:', error);
    }
  };

  const loadProjects = async () => {
    try {
      const response = await axios.get(`${API}/projects`);
      setProjects(response.data);
    } catch (error) {
      console.error('Error loading projects:', error);
      toast.error('Fehler beim Laden der Projekte');
    }
  };

  const loadProjectFiles = async (projectId) => {
    try {
      const response = await axios.get(`${API}/files/${projectId}`);
      setProjectFiles(response.data);
    } catch (error) {
      console.error('Error loading project files:', error);
      toast.error('Fehler beim Laden der Dateien');
    }
  };

  const loadAvailableAgents = async () => {
    try {
      const response = await axios.get(`${API}/agents`);
      setAvailableAgents(response.data);
    } catch (error) {
      console.error('Error loading agents:', error);
    }
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() || isLoading) return;

    // Check if API key is configured
    if ((selectedModel === 'perplexity' && !apiKeys.perplexity) || 
        (selectedModel === 'claude' && !apiKeys.anthropic)) {
      toast.error(`Bitte konfigurieren Sie zuerst den ${selectedModel} API-Schlüssel`);
      setShowApiKeyDialog(true);
      return;
    }

    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: currentMessage,
      timestamp: new Date(),
      model: selectedModel
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API}/chat`, {
        message: currentMessage,
        model: selectedModel,
        use_agent: useAgents,
        context: {
          project_type: selectedProject?.name,
          language: detectedLanguage
        }
      });

      const assistantMessage = {
        ...response.data.message,
        sources: response.data.sources,
        agent_used: response.data.agent_used,
        language_detected: response.data.language_detected
      };

      setMessages(prev => [...prev, assistantMessage]);
      
      // Update detected language
      if (response.data.language_detected) {
        setDetectedLanguage(response.data.language_detected);
      }
      
      // Show processing steps if available
      if (response.data.processing_steps && response.data.processing_steps.length > 0) {
        setProcessingSteps(response.data.processing_steps);
      }
      
      // Show success message based on type of response
      if (response.data.agent_used) {
        toast.success(`Antwort von ${response.data.agent_used} erhalten`);
      } else if (response.data.sources && response.data.sources.length > 0) {
        toast.success(`Antwort erhalten mit ${response.data.sources.length} Quellen`);
      } else {
        toast.success('Antwort erhalten');
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      if (error.response?.status === 400) {
        toast.error(error.response.data.detail || 'Bitte konfigurieren Sie zuerst die API-Schlüssel');
      } else {
        toast.error('Fehler beim Senden der Nachricht');
      }
      
      // Add error message
      const errorMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Entschuldigung, es gab einen Fehler bei der Verarbeitung Ihrer Anfrage.',
        timestamp: new Date(),
        model: selectedModel
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const saveApiKey = async (service, key) => {
    try {
      await axios.post(`${API}/api-keys`, {
        service,
        key,
        is_active: true
      });
      
      setApiKeys(prev => ({ ...prev, [service]: true }));
      toast.success(`${service} API-Schlüssel gespeichert`);
      setShowApiKeyDialog(false);
    } catch (error) {
      console.error('Error saving API key:', error);
      toast.error('Fehler beim Speichern des API-Schlüssels');
    }
  };

  const createProject = async () => {
    if (!newProject.name.trim()) {
      toast.error('Projektname ist erforderlich');
      return;
    }

    try {
      const response = await axios.post(`${API}/projects`, newProject);
      // Reload projects to ensure we get the latest list
      await loadProjects();
      setNewProject({ name: '', description: '' });
      setShowNewProjectDialog(false);
      toast.success('Projekt erstellt');
    } catch (error) {
      console.error('Error creating project:', error);
      toast.error('Fehler beim Erstellen des Projekts');
    }
  };

  const selectProject = async (project) => {
    setSelectedProject(project);
    await loadProjectFiles(project.id);
    setActiveTab('code');
  };

  const generateCode = async () => {
    if (!codeGenPrompt.trim()) {
      toast.error('Bitte geben Sie eine Beschreibung ein');
      return;
    }

    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/generate-code`, {
        prompt: codeGenPrompt,
        language: selectedLanguage,
        model: selectedModel
      });

      const newFile = {
        id: Date.now().toString(),
        name: `generated_${selectedLanguage}_${Date.now()}.${getFileExtension(selectedLanguage)}`,
        content: response.data.code,
        language: selectedLanguage
      };

      if (selectedProject) {
        // Save to project
        await axios.post(`${API}/files`, {
          project_id: selectedProject.id,
          ...newFile
        });
        await loadProjectFiles(selectedProject.id);
      }

      setSelectedFile(newFile);
      setCodeGenPrompt('');
      toast.success('Code generiert');
    } catch (error) {
      console.error('Error generating code:', error);
      if (error.response?.status === 400) {
        toast.error(error.response.data.detail || 'Bitte konfigurieren Sie zuerst die API-Schlüssel');
      } else {
        toast.error('Fehler bei der Code-Generierung');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const getFileExtension = (language) => {
    const extensions = {
      javascript: 'js',
      python: 'py',
      typescript: 'ts',
      java: 'java',
      cpp: 'cpp',
      html: 'html',
      css: 'css'
    };
    return extensions[language] || 'txt';
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success('In Zwischenablage kopiert');
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('de-DE', {
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const ApiKeyDialog = () => {
    const [perplexityKey, setPerplexityKey] = useState('');
    const [anthropicKey, setAnthropicKey] = useState('');

    return (
      <Dialog open={showApiKeyDialog} onOpenChange={setShowApiKeyDialog}>
        <DialogContent className="bg-gray-900 border-gray-700">
          <DialogHeader>
            <DialogTitle className="text-white">API-Schlüssel konfigurieren</DialogTitle>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm text-gray-300 mb-2 block">Perplexity API-Schlüssel</label>
              <div className="flex gap-2">
                <Input
                  type="password"
                  value={perplexityKey}
                  onChange={(e) => setPerplexityKey(e.target.value)}
                  placeholder="pplx-..."
                  className="bg-gray-800 border-gray-600 text-white"
                />
                <Button
                  onClick={() => saveApiKey('perplexity', perplexityKey)}
                  disabled={!perplexityKey}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  <Save className="w-4 h-4" />
                </Button>
              </div>
              <div className="flex items-center gap-2 mt-1">
                <div className={`w-2 h-2 rounded-full ${apiKeys.perplexity ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-xs text-gray-400">
                  {apiKeys.perplexity ? 'Konfiguriert' : 'Nicht konfiguriert'}
                </span>
              </div>
            </div>
            
            <div>
              <label className="text-sm text-gray-300 mb-2 block">Anthropic API-Schlüssel</label>
              <div className="flex gap-2">
                <Input
                  type="password"
                  value={anthropicKey}
                  onChange={(e) => setAnthropicKey(e.target.value)}
                  placeholder="sk-ant-..."
                  className="bg-gray-800 border-gray-600 text-white"
                />
                <Button
                  onClick={() => saveApiKey('anthropic', anthropicKey)}
                  disabled={!anthropicKey}
                  className="bg-purple-600 hover:bg-purple-700"
                >
                  <Save className="w-4 h-4" />
                </Button>
              </div>
              <div className="flex items-center gap-2 mt-1">
                <div className={`w-2 h-2 rounded-full ${apiKeys.anthropic ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-xs text-gray-400">
                  {apiKeys.anthropic ? 'Konfiguriert' : 'Nicht konfiguriert'}
                </span>
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    );
  };

  const NewProjectDialog = () => (
    <Dialog open={showNewProjectDialog} onOpenChange={setShowNewProjectDialog}>
      <DialogContent className="bg-gray-900 border-gray-700">
        <DialogHeader>
          <DialogTitle className="text-white">Neues Projekt erstellen</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <label className="text-sm text-gray-300 mb-2 block">Projektname</label>
            <Input
              value={newProject.name}
              onChange={(e) => setNewProject(prev => ({ ...prev, name: e.target.value }))}
              placeholder="Mein Projekt"
              className="bg-gray-800 border-gray-600 text-white"
            />
          </div>
          <div>
            <label className="text-sm text-gray-300 mb-2 block">Beschreibung</label>
            <Textarea
              value={newProject.description}
              onChange={(e) => setNewProject(prev => ({ ...prev, description: e.target.value }))}
              placeholder="Projektbeschreibung..."
              className="bg-gray-800 border-gray-600 text-white resize-none"
              rows={3}
            />
          </div>
          <div className="flex gap-2 justify-end">
            <Button
              variant="outline"
              onClick={() => setShowNewProjectDialog(false)}
              className="border-gray-600 text-gray-300 hover:bg-gray-800"
            >
              Abbrechen
            </Button>
            <Button
              onClick={createProject}
              className="bg-blue-600 hover:bg-blue-700"
            >
              Erstellen
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );

  return (
    <div className="h-screen bg-gray-950 text-white overflow-hidden">
      <Toaster />
      <ApiKeyDialog />
      <NewProjectDialog />
      
      {/* Header */}
      <div className="h-16 bg-gray-900 border-b border-gray-800 flex items-center justify-between px-6">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-gradient-to-br from-cyan-400 to-teal-500 rounded-lg flex items-center justify-center shadow-lg shadow-cyan-500/25">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-xl font-semibold tracking-wider text-cyan-100">XIONIMUS AI</h1>
          <Badge variant="outline" className="text-xs border-cyan-500 text-cyan-400 bg-cyan-500/10">
            Autonomous Intelligence
          </Badge>
        </div>
        
        <div className="flex items-center gap-3">
          <div className="flex gap-1">
            <div className={`w-2 h-2 rounded-full ${apiKeys.perplexity ? 'bg-green-500' : 'bg-gray-600'}`} />
            <div className={`w-2 h-2 rounded-full ${apiKeys.anthropic ? 'bg-green-500' : 'bg-gray-600'}`} />
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowApiKeyDialog(true)}
            className="text-gray-400 hover:text-white hover:bg-gray-800"
          >
            <Settings className="w-4 h-4" />
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex h-[calc(100vh-4rem)]">
        {/* Sidebar */}
        <div className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
            <TabsList className="grid w-full grid-cols-3 bg-gray-800 mx-4 mt-4">
              <TabsTrigger value="chat" className="data-[state=active]:bg-gray-700">
                <MessageSquare className="w-4 h-4 mr-1" />
                Chat
              </TabsTrigger>
              <TabsTrigger value="code" className="data-[state=active]:bg-gray-700">
                <Code className="w-4 h-4 mr-1" />
                Code
              </TabsTrigger>
              <TabsTrigger value="projects" className="data-[state=active]:bg-gray-700">
                <FolderOpen className="w-4 h-4 mr-1" />
                Projekte
              </TabsTrigger>
            </TabsList>

            <div className="flex-1 p-4">
              <TabsContent value="chat" className="mt-0">
                <div className="space-y-3">
                  <div>
                    <label className="text-sm text-gray-400 mb-2 block">AI-Modell</label>
                    <Select value={selectedModel} onValueChange={setSelectedModel}>
                      <SelectTrigger className="bg-gray-800 border-gray-700">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent className="bg-gray-800 border-gray-700">
                        <SelectItem value="claude">
                          <div className="flex items-center gap-2">
                            <Bot className="w-4 h-4" />
                            Claude (Anthropic)
                          </div>
                        </SelectItem>
                        <SelectItem value="perplexity">
                          <div className="flex items-center gap-2">
                            <Search className="w-4 h-4" />
                            Perplexity
                          </div>
                        </SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  
                  <div className="flex items-center gap-2 p-2 bg-gray-800 rounded-lg">
                    <input
                      type="checkbox"
                      id="useAgents"
                      checked={useAgents}
                      onChange={(e) => setUseAgents(e.target.checked)}
                      className="rounded"
                    />
                    <label htmlFor="useAgents" className="text-sm text-gray-300">
                      Agenten verwenden
                    </label>
                  </div>
                  
                  {detectedLanguage && (
                    <div className="p-2 bg-gray-800 rounded-lg">
                      <div className="text-xs text-gray-400">Erkannte Sprache:</div>
                      <div className="text-sm text-white capitalize">{detectedLanguage}</div>
                    </div>
                  )}
                  
                  {availableAgents.length > 0 && (
                    <div>
                      <label className="text-sm text-gray-400 mb-2 block">Verfügbare Agenten</label>
                      <div className="space-y-1 max-h-32 overflow-y-auto">
                        {availableAgents.map((agent, index) => (
                          <div key={index} className="p-2 bg-gray-800 rounded text-xs">
                            <div className="font-medium text-white">{agent.name}</div>
                            <div className="text-gray-400">{agent.capabilities}</div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  <Button
                    onClick={() => {
                      setMessages([]);
                      setProcessingSteps([]);
                      setCurrentTaskId(null);
                    }}
                    variant="outline"
                    className="w-full border-gray-700 text-gray-300 hover:bg-gray-800"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Neuer Chat
                  </Button>
                </div>
              </TabsContent>

              <TabsContent value="projects" className="mt-0">
                <div className="space-y-3">
                  <Button
                    onClick={() => setShowNewProjectDialog(true)}
                    className="w-full bg-blue-600 hover:bg-blue-700"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Neues Projekt
                  </Button>
                  
                  <ScrollArea className="h-96">
                    <div className="space-y-2">
                      {projects.map((project) => (
                        <Card
                          key={project.id}
                          className={`cursor-pointer transition-colors bg-gray-800 border-gray-700 hover:bg-gray-750 ${
                            selectedProject?.id === project.id ? 'ring-2 ring-blue-500' : ''
                          }`}
                          onClick={() => selectProject(project)}
                        >
                          <CardContent className="p-3">
                            <h4 className="font-medium text-white">{project.name}</h4>
                            <p className="text-xs text-gray-400 mt-1 line-clamp-2">
                              {project.description}
                            </p>
                            <div className="flex items-center gap-2 mt-2">
                              <FileText className="w-3 h-3 text-gray-500" />
                              <span className="text-xs text-gray-500">
                                {project.files?.length || 0} Dateien
                              </span>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </ScrollArea>
                </div>
              </TabsContent>

              <TabsContent value="code" className="mt-0">
                <div className="space-y-3">
                  {selectedProject && (
                    <div className="p-3 bg-gray-800 rounded-lg">
                      <h4 className="font-medium text-white">{selectedProject.name}</h4>
                      <p className="text-xs text-gray-400 mt-1">{selectedProject.description}</p>
                    </div>
                  )}
                  
                  <div>
                    <label className="text-sm text-gray-400 mb-2 block">Code generieren</label>
                    <div className="space-y-2">
                      <Select value={selectedLanguage} onValueChange={setSelectedLanguage}>
                        <SelectTrigger className="bg-gray-800 border-gray-700">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent className="bg-gray-800 border-gray-700">
                          <SelectItem value="python">Python</SelectItem>
                          <SelectItem value="javascript">JavaScript</SelectItem>
                          <SelectItem value="typescript">TypeScript</SelectItem>
                          <SelectItem value="java">Java</SelectItem>
                          <SelectItem value="cpp">C++</SelectItem>
                          <SelectItem value="html">HTML</SelectItem>
                          <SelectItem value="css">CSS</SelectItem>
                        </SelectContent>
                      </Select>
                      
                      <Textarea
                        value={codeGenPrompt}
                        onChange={(e) => setCodeGenPrompt(e.target.value)}
                        placeholder="Beschreiben Sie den Code, den Sie generieren möchten..."
                        className="bg-gray-800 border-gray-700 text-white resize-none"
                        rows={3}
                      />
                      
                      <Button
                        onClick={generateCode}
                        disabled={isLoading || !codeGenPrompt.trim()}
                        className="w-full xionimus-button text-white font-medium"
                      >
                        <Zap className="w-4 h-4 mr-2" />
                        Code generieren
                      </Button>
                    </div>
                  </div>

                  {projectFiles.length > 0 && (
                    <div>
                      <label className="text-sm text-gray-400 mb-2 block">Projektdateien</label>
                      <ScrollArea className="h-48">
                        <div className="space-y-1">
                          {projectFiles.map((file) => (
                            <div
                              key={file.id}
                              className={`p-2 rounded cursor-pointer hover:bg-gray-800 ${
                                selectedFile?.id === file.id ? 'bg-gray-800' : ''
                              }`}
                              onClick={() => setSelectedFile(file)}
                            >
                              <div className="flex items-center gap-2">
                                <FileText className="w-4 h-4 text-gray-500" />
                                <span className="text-sm text-white truncate">{file.name}</span>
                              </div>
                              <span className="text-xs text-gray-500">{file.language}</span>
                            </div>
                          ))}
                        </div>
                      </ScrollArea>
                    </div>
                  )}
                </div>
              </TabsContent>
            </div>
          </Tabs>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col">
          {activeTab === 'chat' && (
            <div className="flex-1 flex flex-col">
              {/* Messages Area */}
              <ScrollArea className="flex-1 p-6">
                <div className="space-y-4 max-w-4xl mx-auto">
                  {messages.length === 0 ? (
                    <div className="text-center py-12">
                      <div className="relative mb-6">
                        <div className="w-20 h-20 bg-gradient-to-br from-cyan-400 to-teal-500 rounded-full mx-auto flex items-center justify-center shadow-2xl shadow-cyan-500/50 animate-pulse">
                          <Brain className="w-10 h-10 text-white" />
                        </div>
                        <div className="absolute inset-0 w-20 h-20 bg-gradient-to-br from-cyan-400 to-teal-500 rounded-full mx-auto opacity-20 animate-ping"></div>
                      </div>
                      <h3 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-teal-300 mb-3 tracking-wider">
                        XIONIMUS AI
                      </h3>
                      <p className="text-cyan-300/80 mb-2 text-lg">
                        An autonomous artificial intelligence
                      </p>
                      <p className="text-gray-400">
                        Wählen Sie einen spezialisierten Agenten oder starten Sie eine Unterhaltung
                      </p>
                    </div>
                  ) : (
                    messages.map((message) => (
                      <div
                        key={message.id}
                        className={`flex gap-3 ${
                          message.role === 'user' ? 'justify-end' : 'justify-start'
                        }`}
                      >
                        <div
                          className={`max-w-3xl rounded-2xl px-4 py-3 ${
                            message.role === 'user'
                              ? 'bg-blue-600 text-white'
                              : 'bg-gray-800 text-gray-100'
                          }`}
                        >
                          <div className="flex items-center gap-2 mb-2">
                            {message.role === 'user' ? (
                              <User className="w-4 h-4" />
                            ) : (
                              <Bot className="w-4 h-4" />
                            )}
                            <span className="text-sm font-medium">
                              {message.role === 'user' ? 'Sie' : (message.agent_used ? `${message.agent_used}` : message.model || 'AI')}
                            </span>
                            {message.agent_used && (
                              <Badge variant="outline" className="text-xs border-blue-500 text-blue-400">
                                Agent
                              </Badge>
                            )}
                            {message.language_detected && message.role === 'user' && (
                              <Badge variant="outline" className="text-xs border-green-500 text-green-400">
                                {message.language_detected}
                              </Badge>
                            )}
                            <span className="text-xs opacity-70">
                              {formatTimestamp(message.timestamp)}
                            </span>
                          </div>
                          
                          <div className="whitespace-pre-wrap">{message.content}</div>
                          
                          {message.sources && message.sources.length > 0 && (
                            <div className="mt-3 pt-3 border-t border-gray-700">
                              <div className="text-sm font-medium mb-2">Quellen:</div>
                              <div className="space-y-1">
                                {message.sources.map((source, index) => (
                                  <div key={index} className="text-xs">
                                    <a
                                      href={source.url}
                                      target="_blank"
                                      rel="noopener noreferrer"
                                      className="text-blue-400 hover:underline"
                                    >
                                      {source.title}
                                    </a>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                          
                          <div className="flex items-center gap-2 mt-2">
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => copyToClipboard(message.content)}
                              className="text-xs opacity-70 hover:opacity-100"
                            >
                              <Copy className="w-3 h-3 mr-1" />
                              Kopieren
                            </Button>
                            {message.tokens_used && (
                              <span className="text-xs opacity-50">
                                {message.tokens_used} Tokens
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                  <div ref={messagesEndRef} />
                </div>
              </ScrollArea>

              {/* Input Area */}
              <div className="border-t border-gray-800 p-4">
                <div className="max-w-4xl mx-auto">
                  <div className="flex gap-3">
                    <Textarea
                      value={currentMessage}
                      onChange={(e) => setCurrentMessage(e.target.value)}
                      placeholder="Stellen Sie Ihre Frage..."
                      className="flex-1 bg-gray-800 border-gray-700 text-white resize-none min-h-[60px]"
                      rows={2}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          sendMessage();
                        }
                      }}
                    />
                    <Button
                      onClick={sendMessage}
                      disabled={isLoading || !currentMessage.trim()}
                      className="xionimus-button px-6 text-white font-medium"
                    >
                      {isLoading ? (
                        <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <Send className="w-4 h-4" />
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'code' && (
            <div className="flex-1">
              {selectedFile ? (
                <div className="h-full flex flex-col">
                  <div className="bg-gray-900 border-b border-gray-800 p-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <FileText className="w-5 h-5 text-gray-400" />
                      <span className="font-medium">{selectedFile.name}</span>
                      <Badge variant="outline" className="text-xs border-gray-600">
                        {selectedFile.language}
                      </Badge>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => copyToClipboard(selectedFile.content)}
                      >
                        <Copy className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                  <div className="flex-1">
                    <Editor
                      ref={editorRef}
                      height="100%"
                      language={selectedFile.language}
                      value={selectedFile.content}
                      theme="vs-dark"
                      options={{
                        readOnly: false,
                        minimap: { enabled: false },
                        scrollBeyondLastLine: false,
                        fontSize: 14,
                        lineHeight: 1.5,
                        padding: { top: 16, bottom: 16 }
                      }}
                    />
                  </div>
                </div>
              ) : (
                <div className="flex-1 flex items-center justify-center">
                  <div className="text-center">
                    <div className="relative mb-4">
                      <div className="w-16 h-16 bg-gradient-to-br from-cyan-500 to-teal-400 rounded-xl mx-auto flex items-center justify-center shadow-xl shadow-cyan-500/25">
                        <Code className="w-8 h-8 text-white" />
                      </div>
                    </div>
                    <h3 className="text-xl font-medium text-cyan-300 mb-2 tracking-wide">
                      Code Generator
                    </h3>
                    <p className="text-cyan-400/70">
                      Wählen Sie eine Datei aus oder lassen Sie Code generieren
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'projects' && (
            <div className="flex-1 p-6">
              <div className="max-w-4xl mx-auto">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold">Projekte</h2>
                  <Button
                    onClick={() => setShowNewProjectDialog(true)}
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Neues Projekt
                  </Button>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {projects.map((project) => (
                    <Card
                      key={project.id}
                      className="bg-gray-800 border-gray-700 hover:bg-gray-750 cursor-pointer transition-colors"
                      onClick={() => selectProject(project)}
                    >
                      <CardHeader>
                        <CardTitle className="text-white">{project.name}</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <p className="text-gray-400 text-sm mb-4">{project.description}</p>
                        <div className="flex items-center justify-between text-xs text-gray-500">
                          <span>{project.files?.length || 0} Dateien</span>
                          <span>{new Date(project.updated_at).toLocaleDateString('de-DE')}</span>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
                
                {projects.length === 0 && (
                  <div className="text-center py-12">
                    <div className="relative mb-6">
                      <div className="w-16 h-16 bg-gradient-to-br from-cyan-500 to-teal-400 rounded-xl mx-auto flex items-center justify-center shadow-xl shadow-cyan-500/25">
                        <FolderOpen className="w-8 h-8 text-white" />
                      </div>
                    </div>
                    <h3 className="text-xl font-medium text-cyan-300 mb-2 tracking-wide">
                      Keine Projekte vorhanden
                    </h3>
                    <p className="text-cyan-400/70 mb-4">
                      Erstellen Sie Ihr erstes Projekt, um zu beginnen
                    </p>
                    <Button
                      onClick={() => setShowNewProjectDialog(true)}
                      className="bg-gradient-to-r from-cyan-500 to-teal-500 hover:from-cyan-600 hover:to-teal-600 shadow-lg shadow-cyan-500/25 border-0"
                    >
                      <Plus className="w-4 h-4 mr-2" />
                      Projekt erstellen
                    </Button>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;