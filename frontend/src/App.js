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
  MicOff,
  Upload,
  Download,
  Eye,
  GitBranch
} from 'lucide-react';
import Editor from '@monaco-editor/react';
import ReactMarkdown from 'react-markdown';
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
    anthropic: false,
    openai: false
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
  const [codeRequest, setCodeRequest] = useState('');
  const [codeResult, setCodeResult] = useState('');
  const [githubUrl, setGithubUrl] = useState('');
  const [repoAnalysis, setRepoAnalysis] = useState('');
  const [files, setFiles] = useState([]);
  const [sessions, setSessions] = useState([]);
  
  const messagesEndRef = useRef(null);
  const editorRef = useRef(null);
  const chatContainerRef = useRef(null);

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

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: currentMessage.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');
    setIsLoading(true);
    
    // Zeige intelligente Verarbeitung
    setProcessingSteps([
      { icon: '🧠', text: 'Analysiere Anfrage...', status: 'active' }
    ]);

    try {
      const response = await axios.post(`${API}/chat`, {
        message: userMessage.content,
        conversation_history: messages.slice(-6), // Letzte 6 Nachrichten als Kontext
        conversation_id: null,
        use_agent: true
      });

      // Simuliere Verarbeitungsschritte basierend auf verwendeten Services
      const servicesUsed = response.data.processing_info?.services_used || [];
      const steps = [];
      
      if (servicesUsed.includes('research')) {
        steps.push({ icon: '🔍', text: 'Führe umfassende Recherche durch...', status: 'completed' });
      }
      if (servicesUsed.includes('technical')) {
        steps.push({ icon: '⚙️', text: 'Analysiere technische Aspekte...', status: 'completed' });
      }
      steps.push({ icon: '✨', text: 'Erstelle finale Antwort...', status: 'completed' });
      
      setProcessingSteps(steps);

      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.data.content,
        timestamp: new Date().toISOString(),
        processing_info: response.data.processing_info
      };

      setMessages(prev => [...prev, aiMessage]);
      scrollToBottom();
      
    } catch (error) {
      console.error('Chat error:', error);
      
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Entschuldigung, ich konnte Ihre Anfrage nicht verarbeiten. Bitte stellen Sie sicher, dass die API-Schlüssel konfiguriert sind.',
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    }
    
    setIsLoading(false);
    setProcessingSteps([]);
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

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Additional functions for new tabs
  const generateCodeFromRequest = async () => {
    if (!codeRequest.trim()) return;
    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/chat`, {
        message: `Generate ${selectedLanguage} code: ${codeRequest}`,
        model: 'claude',
        use_agent: true
      });
      setCodeResult(response.data.content);
      toast.success('Code generated');
    } catch (error) {
      console.error('Error generating code:', error);
      toast.error('Error generating code');
    } finally {
      setIsLoading(false);
    }
  };

  const createNewProject = () => {
    setShowNewProjectDialog(true);
  };

  const openProject = (projectId) => {
    const project = projects.find(p => p.id === projectId);
    if (project) {
      setSelectedProject(project);
      loadProjectFiles(projectId);
    }
  };

  const deleteProject = async (projectId) => {
    try {
      await axios.delete(`${API}/projects/${projectId}`);
      await loadProjects();
      toast.success('Project deleted');
    } catch (error) {
      console.error('Error deleting project:', error);
      toast.error('Error deleting project');
    }
  };

  const analyzeRepository = async () => {
    if (!githubUrl.trim()) return;
    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/analyze-repo`, {
        url: githubUrl,
        model: selectedModel
      });
      setRepoAnalysis(response.data.analysis);
      toast.success('Repository analyzed');
    } catch (error) {
      console.error('Error analyzing repository:', error);
      toast.error('Error analyzing repository');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = (event) => {
    const uploadedFiles = Array.from(event.target.files);
    const newFiles = uploadedFiles.map(file => ({
      id: Date.now() + Math.random(),
      name: file.name,
      size: file.size,
      file: file
    }));
    setFiles(prev => [...prev, ...newFiles]);
    toast.success(`${uploadedFiles.length} files uploaded`);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const viewFile = (fileId) => {
    const file = files.find(f => f.id === fileId);
    if (file) {
      toast.info(`Viewing ${file.name}`);
    }
  };

  const downloadFile = (fileId) => {
    const file = files.find(f => f.id === fileId);
    if (file && file.file) {
      const url = URL.createObjectURL(file.file);
      const a = document.createElement('a');
      a.href = url;
      a.download = file.name;
      a.click();
      URL.revokeObjectURL(url);
    }
  };

  const deleteFile = (fileId) => {
    setFiles(prev => prev.filter(f => f.id !== fileId));
    toast.success('File deleted');
  };

  const saveCurrentSession = () => {
    const session = {
      id: Date.now(),
      name: `Session ${new Date().toLocaleString()}`,
      messages: messages,
      created: new Date(),
      messageCount: messages.length
    };
    setSessions(prev => [...prev, session]);
    toast.success('Session saved');
  };

  const loadSession = (sessionId) => {
    const session = sessions.find(s => s.id === sessionId);
    if (session) {
      setMessages(session.messages);
      toast.success('Session loaded');
    }
  };

  const forkSession = (sessionId) => {
    const session = sessions.find(s => s.id === sessionId);
    if (session) {
      const forkedSession = {
        ...session,
        id: Date.now(),
        name: `Fork of ${session.name}`,
        created: new Date()
      };
      setSessions(prev => [...prev, forkedSession]);
      toast.success('Session forked');
    }
  };

  const deleteSession = (sessionId) => {
    setSessions(prev => prev.filter(s => s.id !== sessionId));
    toast.success('Session deleted');
  };

  const ApiKeyDialog = () => {
    const [perplexityKey, setPerplexityKey] = useState('');
    const [anthropicKey, setAnthropicKey] = useState('');
    const [openaiKey, setOpenaiKey] = useState('');

    return (
      <Dialog open={showApiKeyDialog} onOpenChange={setShowApiKeyDialog}>
        <DialogContent className="bg-gray-900 border-gray-700 max-w-md mx-auto">
          <DialogHeader>
            <DialogTitle className="text-white text-lg font-semibold">AI Service Configuration</DialogTitle>
          </DialogHeader>
          <div className="space-y-6 py-4">
            <div>
              <label className="text-sm text-gray-300 mb-3 block font-medium">Perplexity API-Schlüssel (Deep Research)</label>
              <div className="flex gap-3">
                <input
                  type="password"
                  value={perplexityKey}
                  onChange={(e) => setPerplexityKey(e.target.value)}
                  placeholder="pplx-..."
                  className="dialog-input flex-1"
                />
                <button
                  onClick={() => saveApiKey('perplexity', perplexityKey)}
                  disabled={!perplexityKey}
                  className="dialog-button px-3"
                  title="Speichern"
                >
                  <Save className="w-4 h-4" />
                </button>
              </div>
              <div className="flex items-center gap-2 mt-2">
                <div className={`w-3 h-3 rounded-full ${apiKeys.perplexity ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-xs text-gray-400">
                  {apiKeys.perplexity ? 'Konfiguriert' : 'Nicht konfiguriert'}
                </span>
              </div>
            </div>
            
            <div>
              <label className="text-sm text-gray-300 mb-3 block font-medium">Anthropic API-Schlüssel (Claude Sonnet 4)</label>
              <div className="flex gap-3">
                <input
                  type="password"
                  value={anthropicKey}
                  onChange={(e) => setAnthropicKey(e.target.value)}
                  placeholder="sk-ant-..."
                  className="dialog-input flex-1"
                />
                <button
                  onClick={() => saveApiKey('anthropic', anthropicKey)}
                  disabled={!anthropicKey}
                  className="dialog-button px-3"
                  title="Speichern"
                >
                  <Save className="w-4 h-4" />
                </button>
              </div>
              <div className="flex items-center gap-2 mt-2">
                <div className={`w-3 h-3 rounded-full ${apiKeys.anthropic ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-xs text-gray-400">
                  {apiKeys.anthropic ? 'Konfiguriert' : 'Nicht konfiguriert'}
                </span>
              </div>
            </div>

            <div>
              <label className="text-sm text-gray-300 mb-3 block font-medium">OpenAI API-Schlüssel (GPT-5)</label>
              <div className="flex gap-3">
                <input
                  type="password"
                  value={openaiKey}
                  onChange={(e) => setOpenaiKey(e.target.value)}
                  placeholder="sk-..."
                  className="dialog-input flex-1"
                />
                <button
                  onClick={() => saveApiKey('openai', openaiKey)}
                  disabled={!openaiKey}
                  className="dialog-button px-3"
                  title="Speichern"
                >
                  <Save className="w-4 h-4" />
                </button>
              </div>
              <div className="flex items-center gap-2 mt-2">
                <div className={`w-3 h-3 rounded-full ${apiKeys.openai ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-xs text-gray-400">
                  {apiKeys.openai ? 'Konfiguriert' : 'Nicht konfiguriert'}
                </span>
              </div>
            </div>
            
            <div className="pt-4 border-t border-gray-700">
              <p className="text-xs text-gray-500 leading-relaxed">
                Ihre API-Schlüssel werden lokal gespeichert und direkt an die jeweiligen Anbieter gesendet. 
                Wir haben keinen Zugriff auf Ihre Schlüssel.
              </p>
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
                <option value="claude">Claude Opus 4 (Anthropic)</option>
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
          {/* Chat Tab Content */}
          {activeTab === 'chat' && (
            <div className="glass-card chat-container">
              {/* Messages Area */}
              <div className="messages-area">
                {messages.length === 0 ? (
                  <div className="welcome-message">
                    <div className="welcome-title">XIONIMUS AI</div>
                    <div className="welcome-subtitle">Your Advanced AI Assistant</div>
                    <div className="welcome-description">
                      Powered by cutting-edge AI models, I intelligently use Claude Sonnet 4 for technical tasks, 
                      Perplexity for research, and GPT-5 for natural conversations - all seamlessly integrated.
                    </div>
                  </div>
                ) : (
                  messages.map((message) => (
                    <div key={message.id} className={`message ${message.role}`}>
                      <div className={`message-avatar ${message.role}`}>
                        {message.role === 'user' ? <User /> : <Bot />}
                      </div>
                      <div className="message-content">
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                        {message.timestamp && (
                          <div className="message-timestamp">
                            {new Date(message.timestamp).toLocaleTimeString()}
                          </div>
                        )}
                        {message.processing_info && (
                          <div className="processing-info">
                            <div className="models-used">
                              {message.processing_info.models_involved?.map((model, idx) => (
                                <span key={idx} className="model-badge">{model}</span>
                              ))}
                            </div>
                          </div>
                        )}
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
                      <div className="intelligent-processing">
                        {processingSteps.map((step, idx) => (
                          <div key={idx} className={`processing-step ${step.status}`}>
                            <span className="step-icon">{step.icon}</span>
                            <span className="step-text">{step.text}</span>
                            {step.status === 'active' && (
                              <div className="loading-dots">
                                <div className="loading-dot"></div>
                                <div className="loading-dot"></div>
                                <div className="loading-dot"></div>
                              </div>
                            )}
                          </div>
                        ))}
                        {processingSteps.length === 0 && (
                          <div className="processing-step active">
                            <span className="step-icon">🧠</span>
                            <span className="step-text">Analysiere Anfrage und wähle optimale KI-Services...</span>
                            <div className="loading-dots">
                              <div className="loading-dot"></div>
                              <div className="loading-dot"></div>
                              <div className="loading-dot"></div>
                            </div>
                          </div>
                        )}
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
                    placeholder="Fragen Sie mich alles - ich wähle automatisch die beste KI für Ihre Anfrage..."
                    disabled={isLoading}
                  />
                  <button
                    className={`voice-button ${isListening ? 'listening' : ''}`}
                    onClick={toggleVoiceRecognition}
                    disabled={isLoading}
                    title={isListening ? "Stop listening" : "Start voice input"}
                  >
                    {isListening ? <MicOff /> : <Mic />}
                  </button>
                  <button
                    className="send-button"
                    onClick={sendMessage}
                    disabled={isLoading || !currentMessage.trim()}
                  >
                    <Send />
                  </button>
                </div>
                
                {/* AI Status Indicator */}
                <div className="ai-status">
                  <div className="ai-models">
                    <div className="model-status">
                      <span className="model-name">Claude Sonnet 4</span>
                      <span className={`status-dot ${apiKeys.anthropic ? 'active' : 'inactive'}`}></span>
                      <span className="model-purpose">Technical & Code</span>
                    </div>
                    <div className="model-status">
                      <span className="model-name">Perplexity Deep Research</span>
                      <span className={`status-dot ${apiKeys.perplexity ? 'active' : 'inactive'}`}></span>
                      <span className="model-purpose">Research & Facts</span>
                    </div>
                    <div className="model-status">
                      <span className="model-name">GPT-5</span>
                      <span className={`status-dot ${apiKeys.openai ? 'active' : 'inactive'}`}></span>
                      <span className="model-purpose">Natural Conversation</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Code Tab Content */}
          {activeTab === 'code' && (
            <div className="code-tab">
              <div className="code-header">
                <h2>Code Assistant</h2>
                <p>Generate, analyze, and debug code with AI assistance</p>
              </div>
              <div className="code-workspace">
                <div className="code-input-section">
                  <label>Code Request:</label>
                  <textarea
                    className="code-input"
                    value={codeRequest}
                    onChange={(e) => setCodeRequest(e.target.value)}
                    placeholder="Describe what code you need or paste code for analysis..."
                    rows={6}
                  />
                  <div className="code-actions">
                    <select 
                      className="language-select"
                      value={selectedLanguage}
                      onChange={(e) => setSelectedLanguage(e.target.value)}
                    >
                      <option value="python">Python</option>
                      <option value="javascript">JavaScript</option>
                      <option value="react">React</option>
                      <option value="html">HTML</option>
                      <option value="css">CSS</option>
                      <option value="sql">SQL</option>
                    </select>
                    <button 
                      className="generate-code-btn"
                      onClick={generateCodeFromRequest}
                      disabled={!codeRequest.trim()}
                    >
                      <Code /> Generate Code
                    </button>
                  </div>
                </div>
                {codeResult && (
                  <div className="code-result">
                    <div className="code-result-header">
                      <h3>Generated Code:</h3>
                      <button 
                        className="copy-code-btn"
                        onClick={() => copyToClipboard(codeResult)}
                      >
                        Copy
                      </button>
                    </div>
                    <pre className="code-block">
                      <code>{codeResult}</code>
                    </pre>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Projects Tab Content */}
          {activeTab === 'projects' && (
            <div className="projects-tab">
              <div className="projects-header">
                <h2>Project Management</h2>
                <button className="create-project-btn" onClick={createNewProject}>
                  <Plus /> New Project
                </button>
              </div>
              <div className="projects-grid">
                {projects.map((project) => (
                  <div key={project.id} className="project-card">
                    <div className="project-header">
                      <h3>{project.name}</h3>
                      <div className="project-actions">
                        <button onClick={() => openProject(project.id)}>
                          <FolderOpen />
                        </button>
                        <button onClick={() => deleteProject(project.id)}>
                          <Trash2 />
                        </button>
                      </div>
                    </div>
                    <p className="project-description">{project.description}</p>
                    <div className="project-meta">
                      <span>Files: {project.fileCount || 0}</span>
                      <span>Modified: {new Date(project.lastModified).toLocaleDateString()}</span>
                    </div>
                  </div>
                ))}
                {projects.length === 0 && (
                  <div className="no-projects">
                    <FolderOpen size={48} />
                    <p>No projects yet. Create your first project!</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* GitHub Tab Content */}
          {activeTab === 'github' && (
            <div className="github-tab">
              <div className="github-header">
                <h2>GitHub Integration</h2>
                <p>Connect and manage your GitHub repositories</p>
              </div>
              <div className="github-workspace">
                <div className="github-auth">
                  <h3>Repository URL:</h3>
                  <div className="github-input-group">
                    <input
                      type="text"
                      className="github-input"
                      value={githubUrl}
                      onChange={(e) => setGithubUrl(e.target.value)}
                      placeholder="https://github.com/username/repository"
                    />
                    <button 
                      className="analyze-repo-btn"
                      onClick={analyzeRepository}
                      disabled={!githubUrl.trim()}
                    >
                      <Terminal /> Analyze Repo
                    </button>
                  </div>
                </div>
                {repoAnalysis && (
                  <div className="repo-analysis">
                    <h3>Repository Analysis:</h3>
                    <div className="analysis-content">
                      <ReactMarkdown>{repoAnalysis}</ReactMarkdown>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Files Tab Content */}
          {activeTab === 'files' && (
            <div className="files-tab">
              <div className="files-header">
                <h2>File Management</h2>
                <div className="file-actions">
                  <input
                    type="file"
                    id="file-upload"
                    multiple
                    onChange={handleFileUpload}
                    style={{ display: 'none' }}
                  />
                  <button 
                    className="upload-btn"
                    onClick={() => document.getElementById('file-upload').click()}
                  >
                    <Upload /> Upload Files
                  </button>
                </div>
              </div>
              <div className="files-list">
                {files.map((file) => (
                  <div key={file.id} className="file-item">
                    <div className="file-info">
                      <FileText />
                      <div className="file-details">
                        <span className="file-name">{file.name}</span>
                        <span className="file-size">{formatFileSize(file.size)}</span>
                      </div>
                    </div>
                    <div className="file-actions">
                      <button onClick={() => viewFile(file.id)}>
                        <Eye />
                      </button>
                      <button onClick={() => downloadFile(file.id)}>
                        <Download />
                      </button>
                      <button onClick={() => deleteFile(file.id)}>
                        <Trash2 />
                      </button>
                    </div>
                  </div>
                ))}
                {files.length === 0 && (
                  <div className="no-files">
                    <FileText size={48} />
                    <p>No files uploaded yet. Upload some files to get started!</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Sessions Tab Content */}
          {activeTab === 'sessions' && (
            <div className="sessions-tab">
              <div className="sessions-header">
                <h2>Session Management</h2>
                <button className="save-session-btn" onClick={saveCurrentSession}>
                  <Save /> Save Current Session
                </button>
              </div>
              <div className="sessions-list">
                {sessions.map((session) => (
                  <div key={session.id} className="session-item">
                    <div className="session-info">
                      <Save />
                      <div className="session-details">
                        <span className="session-name">{session.name}</span>
                        <span className="session-date">{new Date(session.created).toLocaleString()}</span>
                        <span className="session-messages">{session.messageCount} messages</span>
                      </div>
                    </div>
                    <div className="session-actions">
                      <button onClick={() => loadSession(session.id)}>
                        <Download /> Load
                      </button>
                      <button onClick={() => forkSession(session.id)}>
                        <GitBranch /> Fork
                      </button>
                      <button onClick={() => deleteSession(session.id)}>
                        <Trash2 />
                      </button>
                    </div>
                  </div>
                ))}
                {sessions.length === 0 && (
                  <div className="no-sessions">
                    <Save size={48} />
                    <p>No saved sessions yet. Save your current conversation!</p>
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