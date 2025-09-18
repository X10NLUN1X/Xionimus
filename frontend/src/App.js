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
  Copy,
  Mic,
  MicOff
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
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState(null);
  
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

  // Initialize speech recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = false;
      rec.lang = 'de-DE';
      
      rec.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setCurrentMessage(transcript);
        setIsListening(false);
      };
      
      rec.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };
      
      rec.onend = () => {
        setIsListening(false);
      };
      
      setRecognition(rec);
    }
  }, []);

  const toggleVoiceRecognition = () => {
    if (!recognition) {
      alert('Speech recognition is not supported in your browser');
      return;
    }
    
    if (isListening) {
      recognition.stop();
      setIsListening(false);
    } else {
      recognition.start();
      setIsListening(true);
    }
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
              className="cyberpunk-button"
            >
              ERSTELLEN
            </Button>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  );

  return (
    <div className="App">
      <Toaster />
      <ApiKeyDialog />
      <NewProjectDialog />
      
      {/* Header */}
      <div className="header">
        <div className="logo">XIONIMUS AI</div>
        <div className="flex items-center gap-4">
          <div className="status-indicator">
            <div className="status-dot"></div>
            <span>Neural Network Online</span>
          </div>
          <button
            onClick={() => setShowApiKeyDialog(true)}
            className="settings-button"
            title="API Settings"
          >
            <Settings />
          </button>
        </div>
      </div>

      {/* Main Container */}
      <div className="main-container">
        {/* Sidebar */}
        <div className="sidebar">
          {/* Navigation Tabs */}
          <div className="nav-tabs">
            <div 
              className={`nav-tab ${activeTab === 'chat' ? 'active' : ''}`}
              onClick={() => setActiveTab('chat')}
            >
              <MessageSquare />
              <span>CHAT</span>
            </div>
            <div 
              className={`nav-tab ${activeTab === 'code' ? 'active' : ''}`}
              onClick={() => setActiveTab('code')}
            >
              <Code />
              <span>CODE</span>
            </div>
            <div 
              className={`nav-tab ${activeTab === 'projects' ? 'active' : ''}`}
              onClick={() => setActiveTab('projects')}
            >
              <FolderOpen />
              <span>PROJ</span>
            </div>
            <div 
              className={`nav-tab ${activeTab === 'github' ? 'active' : ''}`}
              onClick={() => setActiveTab('github')}
            >
              <Terminal />
              <span>GIT</span>
            </div>
            <div 
              className={`nav-tab ${activeTab === 'files' ? 'active' : ''}`}
              onClick={() => setActiveTab('files')}
            >
              <FileText />
              <span>FILES</span>
            </div>
            <div 
              className={`nav-tab ${activeTab === 'sessions' ? 'active' : ''}`}
              onClick={() => setActiveTab('sessions')}
            >
              <Save />
              <span>FORK</span>
            </div>
          </div>

          {/* Chat Settings */}
          {activeTab === 'chat' && (
            <div className="glass-card">
              <div className="section-title">
                <Bot />
                AI Model
              </div>
              <select 
                className="model-select"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
              >
                <option value="claude">Claude (Anthropic)</option>
                <option value="perplexity">Perplexity</option>
              </select>

              <div className="agents-section">
                <div className="section-title">
                  <Brain />
                  Available Agents
                </div>
                {availableAgents.map((agent, index) => (
                  <div key={index} className="agent-card">
                    <div className="agent-name">{agent.name}</div>
                    <div className="agent-description">{agent.capabilities}</div>
                  </div>
                ))}
              </div>

              <Button
                onClick={() => {
                  setMessages([]);
                  setProcessingSteps([]);
                  setCurrentTaskId(null);
                }}
                className="w-full send-button"
              >
                <Plus className="w-4 h-4 mr-2" />
                New Chat
              </Button>
            </div>
          )}

          {/* Project Settings */}
          {activeTab === 'projects' && (
            <div className="glass-card">
              <div className="section-title">
                <FolderOpen />
                Projects
              </div>
              <Button
                onClick={() => setShowNewProjectDialog(true)}
                className="w-full send-button mb-4"
              >
                <Plus className="w-4 h-4 mr-2" />
                New Project
              </Button>
              
              <ScrollArea className="h-64">
                <div className="space-y-2">
                  {projects.map((project) => (
                    <div
                      key={project.id}
                      className={`agent-card ${selectedProject?.id === project.id ? 'active' : ''}`}
                      onClick={() => selectProject(project)}
                    >
                      <div className="agent-name">{project.name}</div>
                      <div className="agent-description">{project.description}</div>
                    </div>
                  ))}
                </div>
              </ScrollArea>
            </div>
          )}
        </div>

        {/* Content Area */}
        <div className="content-area">
          <div className="glass-card chat-container">
            {/* Messages Area */}
            <div className="messages-area">
              {messages.length === 0 ? (
                <div className="welcome-message">
                  <div className="welcome-title">XIONIMUS AI</div>
                  <div className="welcome-subtitle">Your Advanced AI Assistant</div>
                  <div className="welcome-description">
                    Powered by state-of-the-art language models, I'm here to help you with coding, research, writing, and complex problem-solving tasks.
                  </div>
                </div>
              ) : (
                messages.map((message) => (
                  <div key={message.id} className={`message ${message.role}`}>
                    <div className={`message-avatar ${message.role}`}>
                      {message.role === 'user' ? <User /> : <Bot />}
                    </div>
                    <div className="message-content">
                      {message.content}
                    </div>
                  </div>
                ))
              )}
              
              {isLoading && (
                <div className="message ai">
                  <div className="message-avatar ai">
                    <Bot />
                  </div>
                  <div className="message-content">
                    <div className="loading">
                      <span>Processing</span>
                      <div className="loading-dots">
                        <div className="loading-dot"></div>
                        <div className="loading-dot"></div>
                        <div className="loading-dot"></div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="input-area">
              <div className="input-container">
                <textarea
                  className="message-input"
                  value={currentMessage}
                  onChange={(e) => setCurrentMessage(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Type your message..."
                  disabled={isLoading}
                />
                <button
                  className="send-button"
                  onClick={sendMessage}
                  disabled={isLoading || !currentMessage.trim()}
                >
                  <Send />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;