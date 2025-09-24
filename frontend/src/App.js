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

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API = `${BACKEND_URL}/api`;

  // Helper function to ensure content is always a string for ReactMarkdown
  const ensureStringContent = (content) => {
    if (typeof content === 'string') {
      return content;
    }
    
    if (Array.isArray(content)) {
      // Handle array of content blocks (e.g., from Anthropic API)
      return content.map(item => {
        if (typeof item === 'object' && item !== null) {
          // Try to extract text property
          if (item.text) {
            return item.text;
          }
          // Try to extract content property
          if (item.content) {
            return item.content;
          }
          // Fallback: JSON stringify
          return JSON.stringify(item);
        }
        return String(item);
      }).join('');
    }
    
    if (typeof content === 'object' && content !== null) {
      // Handle single content object
      if (content.text) {
        return content.text;
      }
      if (content.content) {
        return content.content;
      }
      // Fallback: JSON stringify
      return JSON.stringify(content);
    }
    
    // Fallback: convert to string
    return String(content);
  };
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

  const testBackendConnection = async () => {
    try {
      console.log('🔄 Testing backend connection...');
      const response = await axios.get(`${API}/health`);
      console.log('✅ Backend connection successful:', response.data);
      toast.success('✅ Backend-Verbindung erfolgreich!');
      return true;
    } catch (error) {
      console.error('❌ Backend connection failed:', error);
      if (error.code === 'ERR_NETWORK' || error.message.includes('Network Error')) {
        toast.error('🔌 Backend-Server ist nicht erreichbar. Bitte starten Sie den Backend-Server (http://localhost:8001).');
      } else {
        toast.error(`❌ Verbindungsfehler: ${error.message}`);
      }
      return false;
    }
  };

  const loadApiKeysStatus = async () => {
    try {
      console.log('🔄 Loading API keys status from MongoDB backend...');
      const startTime = performance.now();
      
      const response = await axios.get(`${API}/api-keys/status`);
      const endTime = performance.now();
      
      console.log(`✅ API keys status loaded in ${Math.round(endTime - startTime)}ms`);
      console.log('📊 Raw response data:', response.data);
      
      // Handle MongoDB-enhanced format
      if (response.data.status && response.data.details) {
        // New MongoDB format with detailed information
        setApiKeys(response.data.status);
        
        // Store additional details for debugging
        console.log('📋 MongoDB info:', response.data.mongodb_info);
        console.log('📈 Configuration status:', {
          total_configured: response.data.total_configured,
          total_services: response.data.total_services,
          mongodb_connection: response.data.mongodb_connection
        });
        
        // Update UI state with additional information
        if (response.data.details) {
          Object.keys(response.data.details).forEach(service => {
            const details = response.data.details[service];
            console.log(`🔑 ${service}: MongoDB=${details.mongodb_stored}, Env=${details.environment_available}, Preview=${details.preview}`);
          });
        }
        
        console.log('✅ API keys state updated from MongoDB backend');
        
      } else {
        // Fallback for old format
        console.log('⚠️ Using fallback format (old API response)');
        setApiKeys(response.data);
      }
      
      // Show user feedback
      const configuredCount = Object.values(response.data.status || response.data).filter(Boolean).length;
      if (configuredCount > 0) {
        console.log(`🎉 ${configuredCount} API key(s) configured and ready`);
      } else {
        console.log('⚠️ No API keys configured - Please add API keys');
      }
      
    } catch (error) {
      console.error('❌ Error loading API keys status:', error);
      
      if (error.response?.status === 500 && error.response?.data?.detail?.includes('MongoDB')) {
        console.error('🗄️ MongoDB connection issue detected');
        toast.error('MongoDB Verbindungsfehler - Bitte Administrator kontaktieren');
      } else if (error.response?.status === 404) {
        console.error('🔗 API endpoint not found');
        toast.error('API-Endpoint nicht gefunden');
      } else {
        toast.error('Fehler beim Laden der API-Schlüssel Status');
      }
      
      // Set fallback state
      setApiKeys({
        perplexity: false,
        anthropic: false,
        openai: false
      });
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

      // Ensure content is always a string
      let content = ensureStringContent(response.data.message?.content || response.data.content || 'Keine Antwort erhalten');

      const aiMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: content,
        timestamp: new Date().toISOString(),
        processing_info: response.data.processing_info
      };

      setMessages(prev => [...prev, aiMessage]);
      scrollToBottom();
      
    } catch (error) {
      console.error('Chat error:', error);
      
      // Try to get error message from response
      let errorContent = 'Entschuldigung, ich konnte Ihre Anfrage nicht verarbeiten. Bitte stellen Sie sicher, dass die API-Schlüssel konfiguriert sind.';
      
      if (error.response?.data?.detail) {
        errorContent = error.response.data.detail;
      } else if (error.response?.data?.message?.content) {
        // Fix: Ensure error content is also converted to string
        errorContent = ensureStringContent(error.response.data.message.content);
      } else if (error.message) {
        if (error.message.includes('Network Error') || error.code === 'ERR_NETWORK') {
          errorContent = '🔌 Verbindung zum Backend fehlgeschlagen. Bitte stellen Sie sicher, dass der Backend-Server läuft (http://localhost:8001). Verwenden Sie die Einstellungen → "Backend testen" um die Verbindung zu prüfen.';
        } else if (error.message.includes('CORS')) {
          errorContent = '🚫 CORS-Fehler: Frontend kann nicht mit Backend kommunizieren. Überprüfen Sie die Server-Konfiguration.';
        }
      }
      
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: errorContent,
        timestamp: new Date().toISOString()
      };
      
      setMessages(prev => [...prev, errorMessage]);
    }
    
    setIsLoading(false);
    setProcessingSteps([]);
  };

  const saveApiKey = async (service, key) => {
    if (!key || key.trim().length < 8) {
      toast.error('API-Schlüssel ist zu kurz oder ungültig');
      return;
    }

    try {
      console.log(`🔄 Saving ${service} API key...`);
      
      const response = await axios.post(`${API}/api-keys`, {
        service,
        key: key.trim(),
        is_active: true
      });
      
      console.log(`✅ ${service} API key saved:`, response.data);
      
      // Reload API keys status from backend to ensure sync
      await loadApiKeysStatus();
      
      toast.success(`${service} API-Schlüssel erfolgreich gespeichert`);
      
      // Close dialog only after successful save and reload
      setTimeout(() => {
        setShowApiKeyDialog(false);
      }, 1000);
      
    } catch (error) {
      console.error(`❌ Error saving ${service} API key:`, error);
      
      if (error.response?.data?.detail) {
        toast.error(`Fehler: ${error.response.data.detail}`);
      } else {
        toast.error(`Fehler beim Speichern des ${service} API-Schlüssels`);
      }
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
      // Fix: Ensure repoAnalysis is always a string
      let analysis = ensureStringContent(response.data.analysis);
      setRepoAnalysis(analysis);
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
    const [isSaving, setIsSaving] = useState(false);
    
    const handleSaveKeys = async () => {
      const keysToSave = [];
      
      if (perplexityKey.trim()) keysToSave.push({ service: 'perplexity', key: perplexityKey.trim() });
      if (anthropicKey.trim()) keysToSave.push({ service: 'anthropic', key: anthropicKey.trim() });
      if (openaiKey.trim()) keysToSave.push({ service: 'openai', key: openaiKey.trim() });
      
      if (keysToSave.length === 0) {
        toast.error('Bitte geben Sie mindestens einen API-Schlüssel ein');
        return;
      }
      
      setIsSaving(true);
      
      try {
        console.log(`🔄 Saving ${keysToSave.length} API keys...`);
        
        for (const { service, key } of keysToSave) {
          await saveApiKey(service, key);
          // Small delay between saves
          await new Promise(resolve => setTimeout(resolve, 200));
        }
        
        // Clear input fields after successful save
        setPerplexityKey('');
        setAnthropicKey('');
        setOpenaiKey('');
        
        console.log('✅ All API keys saved successfully');
        
      } catch (error) {
        console.error('❌ Error in bulk API key save:', error);
      } finally {
        setIsSaving(false);
      }
    };

    // Validate API key format
    const validateApiKey = (key, service) => {
      if (!key) return '';
      
      switch (service) {
        case 'perplexity':
          return key.startsWith('pplx-') ? '' : 'Format: pplx-...';
        case 'anthropic':
          return key.startsWith('sk-ant-') ? '' : 'Format: sk-ant-...';
        case 'openai':
          return key.startsWith('sk-') ? '' : 'Format: sk-...';
        default:
          return '';
      }
    };

    return (
      <Dialog open={showApiKeyDialog} onOpenChange={setShowApiKeyDialog}>
        <DialogContent className="bg-gray-900 border-gray-700 max-w-md mx-auto">
          <DialogHeader>
            <DialogTitle className="text-white text-lg font-semibold">🔑 AI Service Configuration</DialogTitle>
          </DialogHeader>
          <div className="space-y-6 py-4">
            <div>
              <label className="text-sm text-gray-300 mb-3 block font-medium">🔍 Perplexity API-Schlüssel (Deep Research):</label>
              <div className="flex gap-3">
                <input
                  type="password"
                  value={perplexityKey}
                  onChange={(e) => setPerplexityKey(e.target.value)}
                  placeholder="pplx-..."
                  className="dialog-input flex-1"
                  disabled={isSaving}
                />
                <button
                  onClick={() => saveApiKey('perplexity', perplexityKey)}
                  disabled={!perplexityKey || isSaving}
                  className="dialog-button px-3"
                  title="Speichern"
                >
                  <Save className="w-4 h-4" />
                </button>
              </div>
              {validateApiKey(perplexityKey, 'perplexity') && (
                <div className="text-xs text-red-400 mt-1">{validateApiKey(perplexityKey, 'perplexity')}</div>
              )}
              <div className="flex items-center gap-2 mt-2">
                <div className={`w-3 h-3 rounded-full ${apiKeys.perplexity ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-xs text-gray-400">
                  {apiKeys.perplexity ? '✅ Konfiguriert' : '❌ Nicht konfiguriert'}
                </span>
              </div>
              <div className="text-xs text-blue-400 mt-1">
                <a href="https://www.perplexity.ai/settings/api" target="_blank" rel="noopener noreferrer">
                  → API-Schlüssel erhalten
                </a>
              </div>
            </div>
            
            <div>
              <label className="text-sm text-gray-300 mb-3 block font-medium">🧠 Anthropic API-Schlüssel (Claude Sonnet 4):</label>
              <div className="flex gap-3">
                <input
                  type="password"
                  value={anthropicKey}
                  onChange={(e) => setAnthropicKey(e.target.value)}
                  placeholder="sk-ant-..."
                  className="dialog-input flex-1"
                  disabled={isSaving}
                />
                <button
                  onClick={() => saveApiKey('anthropic', anthropicKey)}
                  disabled={!anthropicKey || isSaving}
                  className="dialog-button px-3"
                  title="Speichern"
                >
                  <Save className="w-4 h-4" />
                </button>
              </div>
              {validateApiKey(anthropicKey, 'anthropic') && (
                <div className="text-xs text-red-400 mt-1">{validateApiKey(anthropicKey, 'anthropic')}</div>
              )}
              <div className="flex items-center gap-2 mt-2">
                <div className={`w-3 h-3 rounded-full ${apiKeys.anthropic ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-xs text-gray-400">
                  {apiKeys.anthropic ? '✅ Konfiguriert' : '❌ Nicht konfiguriert'}
                </span>
              </div>
              <div className="text-xs text-blue-400 mt-1">
                <a href="https://console.anthropic.com/" target="_blank" rel="noopener noreferrer">
                  → API-Schlüssel erhalten
                </a>
              </div>
            </div>

            <div>
              <label className="text-sm text-gray-300 mb-3 block font-medium">⚡ OpenAI API-Schlüssel (GPT-5):</label>
              <div className="flex gap-3">
                <input
                  type="password"
                  value={openaiKey}
                  onChange={(e) => setOpenaiKey(e.target.value)}
                  placeholder="sk-..."
                  className="dialog-input flex-1"
                  disabled={isSaving}
                />
                <button
                  onClick={() => saveApiKey('openai', openaiKey)}
                  disabled={!openaiKey || isSaving}
                  className="dialog-button px-3"
                  title="Speichern"
                >
                  <Save className="w-4 h-4" />
                </button>
              </div>
              {validateApiKey(openaiKey, 'openai') && (
                <div className="text-xs text-red-400 mt-1">{validateApiKey(openaiKey, 'openai')}</div>
              )}
              <div className="flex items-center gap-2 mt-2">
                <div className={`w-3 h-3 rounded-full ${apiKeys.openai ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-xs text-gray-400">
                  {apiKeys.openai ? '✅ Konfiguriert' : '❌ Nicht konfiguriert'}
                </span>
              </div>
              <div className="text-xs text-blue-400 mt-1">
                <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer">
                  → API-Schlüssel erhalten
                </a>
              </div>
            </div>
            
            <div className="pt-4 border-t border-gray-700">
              <div className="flex justify-between items-center">
                <button
                  onClick={testBackendConnection}
                  className="px-3 py-2 text-sm bg-gray-700 text-gray-300 rounded hover:bg-gray-600"
                >
                  🔧 Backend testen
                </button>
                <div className="flex gap-2">
                  <button
                    onClick={() => setShowApiKeyDialog(false)}
                    disabled={isSaving}
                    className="px-4 py-2 text-gray-300 border border-gray-600 rounded hover:bg-gray-800 disabled:opacity-50"
                  >
                    Abbrechen
                  </button>
                  <button
                    onClick={handleSaveKeys}
                    disabled={isSaving}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
                  >
                    {isSaving ? '🔄 Speichere...' : '💾 Alle Speichern'}
                  </button>
                </div>
              </div>
              <p className="text-xs text-gray-500 leading-relaxed mt-4">
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
    <div className="app">
      <Toaster />
      <NewProjectDialog />
      
      {/* Pure Chat Interface */}
      <div className="chat-interface">
        {/* Header */}
        <div className="chat-header">
          <h1 className="app-title">XIONIMUS AI</h1>
          <div className="header-status">
            <span className="status-indicator">Neural Network Online</span>
          </div>
        </div>

        {/* Chat Messages */}
        <div className="chat-messages" ref={chatContainerRef}>
          {messages.length === 0 ? (
            <div className="welcome-message">
              <div className="welcome-title">XIONIMUS AI</div>
              <div className="welcome-subtitle">Your Advanced AI Assistant</div>
              <div className="welcome-description">
                Ask me anything - I'll intelligently handle your request using the most suitable AI capabilities.
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
                <div className="processing-indicator">
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
                      <span className="step-text">Verarbeite Ihre Anfrage...</span>
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
        <div className="input-section">
          <div className="input-container">
            <textarea
              className="message-input"
              value={currentMessage}
              onChange={(e) => setCurrentMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask me anything..."
              disabled={isLoading}
              rows={1}
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
          
          {/* Compact Function Toolbar */}
          <div className="function-toolbar">
            <div className="toolbar-section">
              <button 
                className={`toolbar-btn ${activeTab === 'code' ? 'active' : ''}`}
                onClick={() => setActiveTab('code')}
                title="Code Generation"
              >
                <Code size={16} />
              </button>
              <button 
                className={`toolbar-btn ${activeTab === 'projects' ? 'active' : ''}`}
                onClick={() => setActiveTab('projects')}
                title="Projects"
              >
                <FolderOpen size={16} />
              </button>
              <button 
                className={`toolbar-btn ${activeTab === 'github' ? 'active' : ''}`}
                onClick={() => setActiveTab('github')}
                title="GitHub Integration"
              >
                <Terminal size={16} />
              </button>
              <button 
                className={`toolbar-btn ${activeTab === 'files' ? 'active' : ''}`}
                onClick={() => setActiveTab('files')}
                title="File Management"
              >
                <FileText size={16} />
              </button>
              <button 
                className={`toolbar-btn ${activeTab === 'sessions' ? 'active' : ''}`}
                onClick={() => setActiveTab('sessions')}
                title="Session Management"
              >
                <Save size={16} />
              </button>
            </div>
            
            <div className="toolbar-section">
              <input
                type="file"
                id="file-upload-toolbar"
                multiple
                onChange={handleFileUpload}
                style={{ display: 'none' }}
              />
              <button 
                className="toolbar-btn"
                onClick={() => document.getElementById('file-upload-toolbar').click()}
                title="Upload Files"
              >
                <Upload size={16} />
              </button>
              <button 
                className="toolbar-btn"
                onClick={() => setShowApiKeyDialog(true)}
                title="AI Configuration"
              >
                <Settings size={16} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Hidden Function Panels (shown as overlay when toolbar buttons clicked) */}
      {activeTab !== 'chat' && (
        <div className="function-overlay">
          <div className="overlay-header">
            <h3>{activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}</h3>
            <button 
              className="close-overlay"
              onClick={() => setActiveTab('chat')}
            >
              ×
            </button>
          </div>
          
          <div className="overlay-content">
            {activeTab === 'code' && (
              <div className="code-panel">
                <div className="code-input-area">
                  <textarea
                    className="code-request-input"
                    value={codeRequest}
                    onChange={(e) => setCodeRequest(e.target.value)}
                    placeholder="Describe the code you need..."
                    rows={4}
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
                      className="generate-btn"
                      onClick={generateCodeFromRequest}
                      disabled={!codeRequest.trim()}
                    >
                      Generate Code
                    </button>
                  </div>
                </div>
                
                {codeResult && (
                  <div className="code-result">
                    <div className="result-header">
                      <span>Generated Code:</span>
                      <button onClick={() => copyToClipboard(codeResult)}>
                        Copy
                      </button>
                    </div>
                    <pre className="code-block">
                      <code>{codeResult}</code>
                    </pre>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'projects' && (
              <div className="projects-panel">
                <div className="panel-actions">
                  <button className="action-btn" onClick={createNewProject}>
                    <Plus size={16} /> New Project
                  </button>
                </div>
                <div className="projects-list">
                  {projects.map((project) => (
                    <div key={project.id} className="project-item">
                      <div className="project-info">
                        <h4>{project.name}</h4>
                        <p>{project.description}</p>
                      </div>
                      <div className="project-actions">
                        <button onClick={() => openProject(project.id)}>
                          <FolderOpen size={14} />
                        </button>
                        <button onClick={() => deleteProject(project.id)}>
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </div>
                  ))}
                  {projects.length === 0 && (
                    <div className="empty-state">
                      <FolderOpen size={32} />
                      <p>No projects yet</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'github' && (
              <div className="github-panel">
                <div className="github-input">
                  <input
                    type="text"
                    className="repo-input"
                    value={githubUrl}
                    onChange={(e) => setGithubUrl(e.target.value)}
                    placeholder="https://github.com/username/repository"
                  />
                  <button 
                    className="analyze-btn"
                    onClick={analyzeRepository}
                    disabled={!githubUrl.trim()}
                  >
                    Analyze
                  </button>
                </div>
                {repoAnalysis && (
                  <div className="analysis-result">
                    <ReactMarkdown>{repoAnalysis}</ReactMarkdown>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'files' && (
              <div className="files-panel">
                <div className="files-list">
                  {files.map((file) => (
                    <div key={file.id} className="file-item">
                      <div className="file-info">
                        <FileText size={16} />
                        <span className="file-name">{file.name}</span>
                        <span className="file-size">{formatFileSize(file.size)}</span>
                      </div>
                      <div className="file-actions">
                        <button onClick={() => viewFile(file.id)}>
                          <Eye size={14} />
                        </button>
                        <button onClick={() => downloadFile(file.id)}>
                          <Download size={14} />
                        </button>
                        <button onClick={() => deleteFile(file.id)}>
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </div>
                  ))}
                  {files.length === 0 && (
                    <div className="empty-state">
                      <FileText size={32} />
                      <p>No files uploaded</p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'sessions' && (
              <div className="sessions-panel">
                <div className="panel-actions">
                  <button className="action-btn" onClick={saveCurrentSession}>
                    <Save size={16} /> Save Session
                  </button>
                </div>
                <div className="sessions-list">
                  {sessions.map((session) => (
                    <div key={session.id} className="session-item">
                      <div className="session-info">
                        <h4>{session.name}</h4>
                        <span>{session.messageCount} messages</span>
                        <span>{new Date(session.created).toLocaleDateString()}</span>
                      </div>
                      <div className="session-actions">
                        <button onClick={() => loadSession(session.id)}>
                          <Download size={14} />
                        </button>
                        <button onClick={() => forkSession(session.id)}>
                          <GitBranch size={14} />
                        </button>
                        <button onClick={() => deleteSession(session.id)}>
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </div>
                  ))}
                  {sessions.length === 0 && (
                    <div className="empty-state">
                      <Save size={32} />
                      <p>No saved sessions</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* API Key Dialog */}
      <ApiKeyDialog />
    </div>
  );
}

export default App;