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

// Version 2.1 "Core Enhancements" Components
import EnhancedSearchComponent from './components/EnhancedSearchComponent';
import AutoTestingComponent from './components/AutoTestingComponent';
import CodeReviewComponent from './components/CodeReviewComponent';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
const API = `${BACKEND_URL}/api`;

function App() {
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
  const [selectedLanguage, setSelectedLanguage] = useState('python');
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
  const [availableAgents, setAvailableAgents] = useState([]);
  const [suggestedAgent, setSuggestedAgent] = useState(null);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [agentProcessingInfo, setAgentProcessingInfo] = useState(null);
  const [showAgentSelector, setShowAgentSelector] = useState(false);
  const [useAgents, setUseAgents] = useState(true);
  const [currentTaskId, setCurrentTaskId] = useState(null);
  const [processingSteps, setProcessingSteps] = useState([]);
  const [detectedLanguage, setDetectedLanguage] = useState(null);
  const [pendingCodeRequest, setPendingCodeRequest] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState(null);
  const [githubUrl, setGithubUrl] = useState('');
  const [repoAnalysis, setRepoAnalysis] = useState('');
  const [files, setFiles] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [conversationId, setConversationId] = useState(() => generateUUID());
  
  // Generate a UUID for conversation ID
  function generateUUID() {
    return 'conversation-' + Math.random().toString(36).substr(2, 9) + '-' + Date.now();
  }
  
  // New streaming and GitHub functionality state
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingProgress, setStreamingProgress] = useState(null);
  const [githubToken, setGithubToken] = useState('');
  const [githubRepo, setGithubRepo] = useState('');
  const [showGithubDialog, setShowGithubDialog] = useState(false);
  const [generatedCode, setGeneratedCode] = useState('');
  const [codeLanguage, setCodeLanguage] = useState('python');
  const [downloadReady, setDownloadReady] = useState(false);
  
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
      console.log('📊 Available agents loaded:', response.data);
      setAvailableAgents(response.data.agents || response.data);
      
      // Also load XIONIMUS status
      try {
        const xionimusResponse = await axios.get(`${API}/xionimus/status`);
        console.log('🚀 XIONIMUS AI status:', xionimusResponse.data);
        // Store XIONIMUS status in state if needed
      } catch (xionimusError) {
        console.log('XIONIMUS AI not available:', xionimusError.message);
      }
      
    } catch (error) {
      console.error('Error loading agents:', error);
      // Set fallback agents if API fails
      setAvailableAgents([
        { name: 'Code Agent', description: 'Code Generation, Analysis, Debugging', ai_model: 'claude' },
        { name: 'Research Agent', description: 'Web research and information gathering', ai_model: 'perplexity' },
        { name: 'Writing Agent', description: 'Content creation and documentation', ai_model: 'claude' }
      ]);
    }
  };

  // Agent suggestion function
  const suggestAgentForQuery = async (query) => {
    if (!query || query.length < 10) return null;
    
    try {
      const response = await axios.get(`${API}/agents/suggest`, {
        params: { query }
      });
      console.log('🤖 Agent suggestion:', response.data);
      
      // Handle XIONIMUS AI enhancement
      if (response.data.xionimus_analysis) {
        const analysis = response.data.xionimus_analysis;
        console.log('🚀 XIONIMUS complexity analysis:', analysis);
        
        // Store complexity analysis for UI display
        setAgentProcessingInfo({
          complexity_level: analysis.complexity_level,
          complexity_score: analysis.complexity_score,
          xionimus_ai_properties: analysis.xionimus_ai_properties
        });
      }
      
      return response.data.suggested_agent;
    } catch (error) {
      console.error('Error getting agent suggestion:', error);
      return null;
    }
  };

  // Language detection function
  const detectProgrammingLanguage = (message) => {
    const text = message.toLowerCase();
    
    // Programming language patterns with weighted scoring
    const patterns = {
      'python': ['python', 'django', 'flask', 'pandas', 'numpy', 'def ', 'import ', 'print(', '__init__', 'class ', '.py'],
      'javascript': ['javascript', 'js', 'node.js', 'npm', 'console.log', 'function(', 'const ', 'let ', 'var ', '.js', 'react', 'vue', 'angular'],
      'java': ['java', 'spring', 'junit', 'public class', 'private ', 'public ', 'static ', 'void main', '.java'],
      'c++': ['c++', 'cpp', 'iostream', '#include', 'std::', 'cout', 'cin', 'class ', 'public:', 'private:', '.cpp'],
      'c': ['#include', 'stdio.h', 'printf', 'scanf', 'int main', '.c file'],
      'php': ['php', 'laravel', '<?php', '$_GET', '$_POST', 'echo ', 'mysql', '.php'],
      'ruby': ['ruby', 'rails', 'def ', 'puts ', 'class ', 'end', '.rb'],
      'go': ['golang', 'go lang', 'fmt.', 'func main', 'package main', '.go'],
      'rust': ['rust', 'cargo', 'fn main', 'let mut', 'println!', '.rs'],
      'swift': ['swift', 'ios', 'xcode', 'var ', 'let ', 'func ', 'class ', '.swift'],
      'kotlin': ['kotlin', 'android', 'fun main', 'val ', 'var ', '.kt'],
      'typescript': ['typescript', 'ts', 'interface', 'type ', '.ts', '.tsx'],
      'sql': ['select ', 'insert ', 'update ', 'delete ', 'create table', 'drop table', 'join ', 'where '],
      'html': ['html', '<div', '<span', '<html>', '<!doctype', '<head>', '<body>', '.html'],
      'css': ['css', 'stylesheet', 'color:', 'background:', 'margin:', 'padding:', '.css', 'flex', 'grid'],
      'react': ['react', 'jsx', 'usestate', 'useeffect', 'component', 'props', 'setstate'],
      'bash': ['bash', 'shell', 'chmod', 'ls -', 'cd ', 'mkdir', 'rm -', 'sudo ', '.sh'],
      'powershell': ['powershell', 'get-', 'set-', 'new-', '$_', '.ps1']
    };

    // Code-related keywords that strongly suggest programming intent
    const codeKeywords = [
      'write code', 'create code', 'generate code', 'build a script', 'develop a',
      'program that', 'write a function', 'create a class', 'implement algorithm',
      'code for', 'script to', 'function to', 'method that', 'class that',
      'api that', 'database query', 'web app', 'mobile app', 'software',
      'debug this', 'fix code', 'optimize code', 'refactor code', 'implement',
      'programming', 'coding', 'application', 'system', 'framework',
      'library', 'module', 'package', 'compile', 'execute', 'run code', 'test code'
    ];

    // Non-programming indicators (to avoid false positives)
    const nonCodeIndicators = [
      'what is', 'who is', 'when was', 'where is', 'how to cook', 'recipe for',
      'history of', 'definition of', 'capital of', 'explain', 'tell me about',
      'weather', 'news', 'translate', 'convert currency', 'math problem',
      'calculate', 'solve equation', 'homework help', 'study guide'
    ];

    // Check for non-programming indicators first
    const hasNonCodeIndicator = nonCodeIndicators.some(indicator => text.includes(indicator));
    if (hasNonCodeIndicator) {
      return null; // Likely not a programming request
    }

    // Check for specific language mentions with higher threshold
    for (const [language, keywords] of Object.entries(patterns)) {
      const matches = keywords.filter(keyword => text.includes(keyword)).length;
      // Require at least 2 matches or 1 strong match (longer keywords)
      if (matches >= 2 || (matches >= 1 && keywords.some(k => text.includes(k) && k.length > 6))) {
        return language;
      }
    }

    // Check for strong coding intent with higher threshold
    const codeMatches = codeKeywords.filter(keyword => text.includes(keyword)).length;
    if (codeMatches >= 1) {
      return 'general'; // General programming request
    }

    return null;
  };

  // Handle code generation confirmation
  const handleCodeConfirmation = async (confirmed) => {
    if (!pendingCodeRequest || !detectedLanguage) return;

    const confirmationResponse = {
      id: Date.now(),
      role: 'user',
      content: confirmed ? 'Yes, generate the code' : 'No, just answer normally',
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, confirmationResponse]);
    setIsLoading(true);

    try {
      if (confirmed) {
        // Use streaming code generation
        await generateCodeWithStreaming(pendingCodeRequest, detectedLanguage, selectedModel);
        
        const aiMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: `✅ ${detectedLanguage} code generated with real-time streaming! Check the code panel for live updates.`,
          model: selectedModel || 'AI',
          timestamp: new Date().toISOString(),
          hasGeneratedCode: true,
          generatedLanguage: detectedLanguage
        };

        setMessages(prev => [...prev, aiMessage]);
        toast.success(`${detectedLanguage} code generated with streaming!`);
      } else {
        // Process as normal chat
        const response = await axios.post(`${API}/chat`, {
          message: pendingCodeRequest,
          conversation_history: messages.slice(-6),
          conversation_id: conversationId,
          use_agent: true
        });

        const aiMessage = {
          id: Date.now() + 1,
          role: 'assistant',
          content: response.data.content,
          model: response.data.model || 'AI',
          timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, aiMessage]);
      }
    } catch (error) {
      console.error('Error processing request:', error);
      toast.error('Error processing your request');
      
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: 'Sorry, I encountered an error while processing your request. Please try again.',
        timestamp: new Date().toISOString(),
        isError: true
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
      setProcessingSteps([]);
      setPendingCodeRequest(null);
      setDetectedLanguage(null);
    }
  };

  const sendMessage = async () => {
    if (!currentMessage.trim() || isLoading) return;

    // Check for programming language detection
    const detectedLang = detectProgrammingLanguage(currentMessage);
    
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: currentMessage.trim(),
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setCurrentMessage('');

    // If programming language detected, show confirmation
    if (detectedLang && detectedLang !== 'general') {
      const confirmationMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: `I detected you want ${detectedLang.charAt(0).toUpperCase() + detectedLang.slice(1)} code. Should I generate it?`,
        timestamp: new Date().toISOString(),
        isConfirmation: true,
        detectedLanguage: detectedLang,
        originalRequest: userMessage.content
      };
      
      setMessages(prev => [...prev, confirmationMessage]);
      setPendingCodeRequest(userMessage.content);
      setDetectedLanguage(detectedLang);
      return;
    }

    setIsLoading(true);
    
    // Get agent suggestion for better user experience
    const suggestedAgent = await suggestAgentForQuery(userMessage.content);
    if (suggestedAgent) {
      setSuggestedAgent(suggestedAgent);
      setAgentProcessingInfo({
        suggested: suggestedAgent.name,
        confidence: suggestedAgent.confidence
      });
    }
    
    // Zeige intelligente Verarbeitung
    const initialSteps = [
      { icon: '🧠', text: 'Analysiere Anfrage...', status: 'active' }
    ];
    
    if (suggestedAgent) {
      initialSteps.push({ 
        icon: '🤖', 
        text: `${suggestedAgent.name} wird empfohlen...`, 
        status: 'pending' 
      });
    }
    
    setProcessingSteps(initialSteps);

    try {
      const response = await axios.post(`${API}/chat`, {
        message: userMessage.content,
        conversation_history: messages.slice(-6), // Letzte 6 Nachrichten als Kontext
        conversation_id: conversationId,
        use_agent: true
      });

      // Enhanced processing steps with agent information
      const servicesUsed = response.data.processing_info?.services_used || [];
      const agentUsed = response.data.agent_used;
      const steps = [];
      
      // Show agent routing step
      if (agentUsed) {
        steps.push({ 
          icon: '🤖', 
          text: `${agentUsed} wurde verwendet`, 
          status: 'completed' 
        });
      }
      
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
        processing_info: response.data.processing_info,
        agent_used: response.data.agent_used,
        agent_result: response.data.agent_result,
        language_detected: response.data.language_detected
      };

      setMessages(prev => [...prev, aiMessage]);
      scrollToBottom();
      
    } catch (error) {
      console.error('Chat error:', error);
      
      // Try to get error message from response
      let errorContent = 'Entschuldigung, ich konnte Ihre Anfrage nicht verarbeiten. Bitte stellen Sie sicher, dass die API-Schlüssel konfiguriert sind.';
      
      if (error.response?.data?.detail) {
        errorContent = ensureStringContent(error.response.data.detail);
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

  // Streaming code generation function
  const generateCodeWithStreaming = async (prompt, language = 'python', model = 'claude') => {
    setIsStreaming(true);
    setStreamingProgress({ stage: 'starting', progress: 0, current_code: '', message: 'Starting code generation...' });
    
    try {
      const response = await fetch(`${API}/stream-code-generation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt: prompt,
          language: language,
          model: model,
          stream_updates: true
        })
      });

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              setStreamingProgress(data);
              
              // Update generated code
              if (data.stage === 'complete') {
                setGeneratedCode(data.current_code);
                setCodeLanguage(language);
                setDownloadReady(true);
              }
            } catch (e) {
              console.error('Error parsing streaming data:', e);
            }
          }
        }
      }
    } catch (error) {
      console.error('Streaming error:', error);
      toast.error('Streaming error: ' + error.message);
      setStreamingProgress({
        stage: 'error',
        progress: 0,
        current_code: '',
        message: 'Error occurred during code generation'
      });
    } finally {
      setIsStreaming(false);
    }
  };

  // Push code to GitHub function
  const pushToGithub = async () => {
    if (!githubToken || !githubRepo || !generatedCode) {
      toast.error('GitHub token, repository, and generated code are required');
      return;
    }

    try {
      const files = [{
        path: `generated_code.${getFileExtension(codeLanguage)}`,
        content: generatedCode
      }];

      const response = await axios.post(`${API}/github-push`, {
        repository: githubRepo,
        branch: 'main',
        files: files,
        commit_message: `Add generated ${codeLanguage} code`,
        github_token: githubToken
      });

      if (response.data.success) {
        toast.success(`✅ Code pushed to ${githubRepo} successfully!`);
        setShowGithubDialog(false);
      } else {
        toast.error('Failed to push to GitHub');
      }
    } catch (error) {
      console.error('GitHub push error:', error);
      toast.error('GitHub push failed: ' + (error.response?.data?.detail || error.message));
    }
  };

  // Download code as RAR/ZIP function
  const downloadAsRar = async () => {
    if (!generatedCode) {
      toast.error('No code available for download');
      return;
    }

    try {
      const files = [{
        name: `generated_code.${getFileExtension(codeLanguage)}`,
        content: generatedCode
      }];

      const response = await axios.post(`${API}/download-code-rar`, {
        files: files,
        project_name: 'generated_code_project'
      }, {
        responseType: 'blob'
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'generated_code_project.zip');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      toast.success('✅ Code downloaded successfully!');
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Download failed: ' + (error.response?.data?.detail || error.message));
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
        model: selectedModel,
        conversation_id: conversationId
      });
      
      // Fix: Ensure repoAnalysis is always a string
      let analysis = ensureStringContent(response.data.analysis);
      setRepoAnalysis(analysis);
      
      // Add repository analysis to message history for context
      const analysisMessage = {
        id: Date.now(),
        role: 'assistant',
        content: `📊 **Repository Analysis Complete**\n\n**Repository:** ${githubUrl}\n\n${analysis}`,
        model: response.data.model_used || 'GitHub Agent',
        timestamp: new Date().toISOString(),
        agent_used: response.data.agent_used,
        repository_url: response.data.repository_url
      };
      
      setMessages(prev => [...prev, analysisMessage]);
      toast.success('Repository analyzed and saved to conversation');
    } catch (error) {
      console.error('Error analyzing repository:', error);
      toast.error('Error analyzing repository');
    } finally {
      setIsLoading(false);
    }
  };

  // Start a new conversation
  const startNewConversation = () => {
    setConversationId(generateUUID());
    setMessages([]);
    setRepoAnalysis('');
    toast.success('New conversation started');
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
          return !key.startsWith('pplx-') ? 'Perplexity keys should start with "pplx-"' : '';
        case 'anthropic':
          return !key.startsWith('sk-ant-') ? 'Anthropic keys should start with "sk-ant-"' : '';
        case 'openai':
          return !key.startsWith('sk-') ? 'OpenAI keys should start with "sk-"' : '';
        default:
          return '';
      }
    };

    return (
      <Dialog open={showApiKeyDialog} onOpenChange={setShowApiKeyDialog}>
        <DialogContent className="bg-black border-2 border-[#f4d03f] max-w-md mx-auto shadow-2xl shadow-[#f4d03f]/20">
          <DialogHeader className="border-b border-[#f4d03f]/20 pb-4">
            <DialogTitle className="text-[#f4d03f] text-xl font-bold flex items-center gap-2">
              🔑 AI Service Configuration
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-6 py-6">
            {/* Perplexity Section */}
            <div className="space-y-3">
              <label className="text-[#f4d03f] text-sm font-semibold flex items-center gap-2">
                🔍 Perplexity API-Schlüssel (Deep Research):
              </label>
              <div className="flex gap-3">
                <input
                  type="password"
                  value={perplexityKey}
                  onChange={(e) => setPerplexityKey(e.target.value)}
                  placeholder="pplx-..."
                  className="flex-1 bg-black border-2 border-[#f4d03f]/30 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:border-[#f4d03f] focus:outline-none focus:ring-2 focus:ring-[#f4d03f]/20"
                  disabled={isSaving}
                />
              </div>
              {validateApiKey(perplexityKey, 'perplexity') && (
                <div className="text-xs text-red-400 mt-1">{validateApiKey(perplexityKey, 'perplexity')}</div>
              )}
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${apiKeys.perplexity ? 'bg-[#f4d03f]' : 'bg-red-500'}`} />
                <span className="text-xs text-gray-300">
                  {apiKeys.perplexity ? '✅ Konfiguriert' : '❌ Nicht konfiguriert'}
                </span>
              </div>
              <div className="text-xs text-[#f4d03f] hover:text-[#f9e79f] transition-colors">
                <a href="https://www.perplexity.ai/settings/api" target="_blank" rel="noopener noreferrer">
                  → API-Schlüssel erhalten
                </a>
              </div>
            </div>
            
            {/* Anthropic Section */}
            <div className="space-y-3">
              <label className="text-[#f4d03f] text-sm font-semibold flex items-center gap-2">
                🧠 Anthropic API-Schlüssel (Claude Sonnet 4):
              </label>
              <div className="flex gap-3">
                <input
                  type="password"
                  value={anthropicKey}
                  onChange={(e) => setAnthropicKey(e.target.value)}
                  placeholder="sk-ant-..."
                  className="flex-1 bg-black border-2 border-[#f4d03f]/30 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:border-[#f4d03f] focus:outline-none focus:ring-2 focus:ring-[#f4d03f]/20"
                  disabled={isSaving}
                />
              </div>
              {validateApiKey(anthropicKey, 'anthropic') && (
                <div className="text-xs text-red-400 mt-1">{validateApiKey(anthropicKey, 'anthropic')}</div>
              )}
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${apiKeys.anthropic ? 'bg-[#f4d03f]' : 'bg-red-500'}`} />
                <span className="text-xs text-gray-300">
                  {apiKeys.anthropic ? '✅ Konfiguriert' : '❌ Nicht konfiguriert'}
                </span>
              </div>
              <div className="text-xs text-[#f4d03f] hover:text-[#f9e79f] transition-colors">
                <a href="https://console.anthropic.com" target="_blank" rel="noopener noreferrer">
                  → API-Schlüssel erhalten
                </a>
              </div>
            </div>

            {/* OpenAI Section */}
            <div className="space-y-3">
              <label className="text-[#f4d03f] text-sm font-semibold flex items-center gap-2">
                ⚡ OpenAI API-Schlüssel (GPT-5):
              </label>
              <div className="flex gap-3">
                <input
                  type="password"
                  value={openaiKey}
                  onChange={(e) => setOpenaiKey(e.target.value)}
                  placeholder="sk-..."
                  className="flex-1 bg-black border-2 border-[#f4d03f]/30 rounded-lg px-3 py-2 text-white placeholder-gray-500 focus:border-[#f4d03f] focus:outline-none focus:ring-2 focus:ring-[#f4d03f]/20"
                  disabled={isSaving}
                />
              </div>
              {validateApiKey(openaiKey, 'openai') && (
                <div className="text-xs text-red-400 mt-1">{validateApiKey(openaiKey, 'openai')}</div>
              )}
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${apiKeys.openai ? 'bg-[#f4d03f]' : 'bg-red-500'}`} />
                <span className="text-xs text-gray-300">
                  {apiKeys.openai ? '✅ Konfiguriert' : '❌ Nicht konfiguriert'}
                </span>
              </div>
              <div className="text-xs text-[#f4d03f] hover:text-[#f9e79f] transition-colors">
                <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer">
                  → API-Schlüssel erhalten
                </a>
              </div>
            </div>
          </div>

          {/* Footer with Info and Buttons */}
          <div className="border-t border-[#f4d03f]/20 pt-4 space-y-4">
            <div className="text-xs text-gray-400 bg-black/50 p-3 rounded-lg border border-[#f4d03f]/10">
              Ihre API-Schlüssel werden lokal gespeichert und direkt an die jeweiligen Anbieter gesendet. Wir haben keinen Zugriff auf Ihre Schlüssel.
            </div>
            
            {/* Action Buttons */}
            <div className="flex gap-3">
              <button
                onClick={testBackendConnection}
                disabled={isSaving}
                className="flex-1 bg-black border border-[#f4d03f] text-[#f4d03f] px-4 py-2 rounded-lg hover:bg-[#f4d03f]/10 transition-colors disabled:opacity-50 font-medium"
              >
                🔧 Backend testen
              </button>
            </div>
            
            <div className="flex gap-3">
              <button
                onClick={() => setShowApiKeyDialog(false)}
                disabled={isSaving}
                className="flex-1 bg-black border border-gray-600 text-gray-300 px-4 py-2 rounded-lg hover:bg-gray-800 transition-colors disabled:opacity-50"
              >
                Abbrechen
              </button>
              <button
                onClick={handleSaveKeys}
                disabled={isSaving || (!perplexityKey && !anthropicKey && !openaiKey)}
                className="flex-1 bg-gradient-to-r from-[#f4d03f] to-[#d4af37] text-black px-4 py-2 rounded-lg hover:from-[#f9e79f] hover:to-[#f4d03f] transition-all disabled:opacity-50 font-semibold shadow-lg shadow-[#f4d03f]/20"
              >
                {isSaving ? 'Speichere...' : '💾 Alle Speichern'}
              </button>
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

  const GitHubDialog = () => (
    <Dialog open={showGithubDialog} onOpenChange={setShowGithubDialog}>
      <DialogContent className="bg-gray-900 border-gray-700">
        <DialogHeader>
          <DialogTitle className="text-white">Push Code to GitHub</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <div>
            <label className="text-sm text-gray-300 mb-2 block">GitHub Personal Access Token</label>
            <Input
              type="password"
              value={githubToken}
              onChange={(e) => setGithubToken(e.target.value)}
              placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
              className="bg-gray-800 border-gray-600 text-white"
            />
            <p className="text-xs text-gray-400 mt-1">
              Create a token at: GitHub Settings → Developer settings → Personal access tokens
            </p>
          </div>
          <div>
            <label className="text-sm text-gray-300 mb-2 block">Repository (owner/repo)</label>
            <Input
              value={githubRepo}
              onChange={(e) => setGithubRepo(e.target.value)}
              placeholder="username/repository-name"
              className="bg-gray-800 border-gray-600 text-white"
            />
          </div>
          {generatedCode && (
            <div>
              <label className="text-sm text-gray-300 mb-2 block">Code Preview</label>
              <div className="bg-gray-800 border border-gray-600 rounded p-3 max-h-40 overflow-y-auto">
                <code className="text-green-400 text-xs">
                  {generatedCode.substring(0, 200)}
                  {generatedCode.length > 200 && '...'}
                </code>
              </div>
            </div>
          )}
        </div>
        <div className="flex justify-end space-x-2 mt-6">
          <Button
            variant="outline"
            onClick={() => setShowGithubDialog(false)}
            className="border-gray-600 text-gray-300 hover:bg-gray-800"
          >
            Cancel
          </Button>
          <Button
            onClick={pushToGithub}
            className="cyberpunk-button"
            disabled={!githubToken || !githubRepo}
          >
            <GitBranch size={16} className="mr-2" />
            PUSH TO GITHUB
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );

  return (
    <div className="App">
      <Toaster />
      <NewProjectDialog />
      <GitHubDialog />
      
      {/* Main Dark Interface */}
      <div className="main-container">
        <div className="app-header">
          <div className="header-content">
            <div>
              <h1 className="app-title">XIONIMUS AI</h1>
              <div className="app-subtitle">v2.1 - Core Enhancements</div>
            </div>
            <div className="header-controls">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowApiKeyDialog(true)}
                className="bg-black border-[#f4d03f] text-[#f4d03f] hover:bg-[#f4d03f] hover:text-black"
              >
                <Settings className="h-4 w-4 mr-2" />
                API Configuration
              </Button>
              <div className="status-indicator">
                <span className="text-[#f4d03f]">AI Services</span>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Dark Navigation Tabs */}
        <div className="nav-tabs">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="tab-list bg-black">
              <TabsTrigger value="chat" className="tab-trigger bg-black text-[#c0c0c0] hover:text-[#f4d03f] data-[state=active]:bg-[#f4d03f] data-[state=active]:text-black">
                <MessageSquare className="h-4 w-4" />
                <span>Chat</span>
              </TabsTrigger>
              <TabsTrigger value="search" className="tab-trigger bg-black text-[#c0c0c0] hover:text-[#f4d03f] data-[state=active]:bg-[#f4d03f] data-[state=active]:text-black">
                <Search className="h-4 w-4" />
                <span>🔍 Search</span>
              </TabsTrigger>
              <TabsTrigger value="testing" className="tab-trigger bg-black text-[#c0c0c0] hover:text-[#f4d03f] data-[state=active]:bg-[#f4d03f] data-[state=active]:text-black">
                <Zap className="h-4 w-4" />
                <span>🤖 Auto-Test</span>
              </TabsTrigger>
              <TabsTrigger value="review" className="tab-trigger bg-black text-[#c0c0c0] hover:text-[#f4d03f] data-[state=active]:bg-[#f4d03f] data-[state=active]:text-black">
                <FileText className="h-4 w-4" />
                <span>📝 Code Review</span>
              </TabsTrigger>
              <TabsTrigger value="projects" className="tab-trigger bg-black text-[#c0c0c0] hover:text-[#f4d03f] data-[state=active]:bg-[#f4d03f] data-[state=active]:text-black">
                <FolderOpen className="h-4 w-4" />
                <span>Projects</span>
              </TabsTrigger>
            </TabsList>

            <div className="mt-6">
              <TabsContent value="search">
                <EnhancedSearchComponent />
              </TabsContent>

              <TabsContent value="testing">
                <AutoTestingComponent />
              </TabsContent>

              <TabsContent value="review">
                <CodeReviewComponent />
              </TabsContent>

              <TabsContent value="projects">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center space-x-2">
                      <FolderOpen className="h-5 w-5" />
                      <span>Projekte verwalten</span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <Button onClick={() => setShowNewProjectDialog(true)} className="w-full">
                        <Plus className="h-4 w-4 mr-2" />
                        Neues Projekt erstellen
                      </Button>
                      
                      {projects.length === 0 ? (
                        <div className="text-center py-8 text-gray-500">
                          <FolderOpen className="h-12 w-12 mx-auto mb-4 opacity-50" />
                          <p>Keine Projekte vorhanden.</p>
                          <p className="text-sm">Erstellen Sie Ihr erstes Projekt!</p>
                        </div>
                      ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                          {projects.map((project) => (
                            <Card key={project.id} className="cursor-pointer hover:shadow-md transition-shadow">
                              <CardContent className="p-4">
                                <h3 className="font-semibold mb-2">{project.name}</h3>
                                <p className="text-sm text-gray-600 mb-3">{project.description}</p>
                                <div className="flex space-x-2">
                                  <Button size="sm" variant="outline">
                                    <Eye className="h-3 w-3 mr-1" />
                                    Öffnen
                                  </Button>
                                  <Button size="sm" variant="outline">
                                    <Edit className="h-3 w-3 mr-1" />
                                    Bearbeiten
                                  </Button>
                                </div>
                              </CardContent>
                            </Card>
                          ))}
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </div>
          </Tabs>
        </div>

        {/* Main Chat Container - The lower chat window */}
        <div className="chat-container">
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
                    {message.isConfirmation && (
                      <div className="confirmation-buttons">
                        <button 
                          className="confirm-btn yes"
                          onClick={() => handleCodeConfirmation(true)}
                          disabled={isLoading}
                        >
                          ✅ Yes, generate code
                        </button>
                        <button 
                          className="confirm-btn no"
                          onClick={() => handleCodeConfirmation(false)}
                          disabled={isLoading}
                        >
                          ❌ No, just answer normally
                        </button>
                      </div>
                    )}
                    {message.timestamp && (
                      <div className="message-timestamp">
                        {new Date(message.timestamp).toLocaleTimeString()}
                        {message.model && ` • ${message.model}`}
                        {message.agent_used && (
                          <span className="agent-indicator">
                            • 🤖 {message.agent_used}
                            {message.agent_used === 'XIONIMUS AI Orchestrator' && (
                              <span className="xionimus-badge">✨ XIONIMUS AI</span>
                            )}
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
            
            {isLoading && (
              <div className="loading-container">
                <div className="processing-indicator">
                  {processingSteps.map((step, index) => (
                    <div 
                      key={index} 
                      className={`processing-step ${step.active ? 'active' : step.completed ? 'completed' : ''}`}
                    >
                      <div className="step-icon">{step.icon}</div>
                      <div className="step-text">{step.text}</div>
                      {step.active && (
                        <div className="loading-dots">
                          <div className="loading-dot"></div>
                          <div className="loading-dot"></div>
                          <div className="loading-dot"></div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
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
                className={`toolbar-btn ${showAgentSelector ? 'active' : ''}`}
                onClick={() => setShowAgentSelector(!showAgentSelector)}
                title="AI-Agenten"
              >
                <Bot size={16} />
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
      </div>

      {/* API Key Dialog */}
      <ApiKeyDialog />
    </div>
  );
}

export default App;