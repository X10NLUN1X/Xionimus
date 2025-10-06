import React, { useState } from 'react';
import { PlayIcon, StopCircleIcon } from '@heroicons/react/24/solid';
import { DocumentTextIcon } from '@heroicons/react/24/outline';
import { Button } from './UI/Button';
import { useToast } from './UI/Toast';

interface CodeExecutorProps {
  code: string;
  language: string;
  onExecutionStart?: () => void;
  onExecutionComplete?: (result: ExecutionResult) => void;
  onCodeChange?: (code: string) => void;
}

interface ExecutionResult {
  success: boolean;
  stdout?: string;
  stderr?: string;
  exit_code?: number;
  execution_time?: number;
  execution_id?: string;
  timeout_occurred?: boolean;
  error?: string;
}

export const CodeExecutor: React.FC<CodeExecutorProps> = ({
  code,
  language,
  onExecutionStart,
  onExecutionComplete,
  onCodeChange
}) => {
  const [isExecuting, setIsExecuting] = useState(false);
  const [result, setResult] = useState<ExecutionResult | null>(null);
  const [stdinInput, setStdinInput] = useState('');
  const [showStdin, setShowStdin] = useState(false);
  const [templateType, setTemplateType] = useState<string>('');
  const [isLoadingTemplate, setIsLoadingTemplate] = useState(false);
  const { showToast } = useToast();

  // Map common language names to sandbox API names
  const mapLanguage = (lang: string): string => {
    const langMap: { [key: string]: string } = {
      'c++': 'cpp',
      'c#': 'csharp',
      'cs': 'csharp',
      'sh': 'bash',
      'shell': 'bash',
      'js': 'javascript',
      'ts': 'typescript',
      'py': 'python',
      'pl': 'perl',
      'rb': 'ruby',
      'golang': 'go'
    };
    const normalized = lang.toLowerCase();
    return langMap[normalized] || normalized;
  };

  const loadTemplate = async (type: string) => {
    if (!type) return;
    
    setIsLoadingTemplate(true);
    try {
      const token = localStorage.getItem('xionimus_token');
      if (!token) {
        showToast({
          title: 'Authentifizierung erforderlich',
          status: 'error',
          duration: 3000,
        });
        return;
      }

      const backendUrl = import.meta.env.VITE_BACKEND_URL || 
                        import.meta.env.REACT_APP_BACKEND_URL || 
                        'http://localhost:8001';

      const mappedLang = mapLanguage(language);
      const response = await fetch(`${backendUrl}/api/sandbox/templates/template/${mappedLang}/${type}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      if (onCodeChange && data.code) {
        onCodeChange(data.code);
        showToast({
          title: 'Template geladen',
          description: `${type} Template für ${language}`,
          status: 'success',
          duration: 2000,
        });
      }
    } catch (error) {
      console.error('Template load error:', error);
      showToast({
        title: 'Template-Ladefehler',
        description: error instanceof Error ? error.message : 'Unbekannter Fehler',
        status: 'error',
        duration: 3000,
      });
    } finally {
      setIsLoadingTemplate(false);
      setTemplateType('');
    }
  };

  const executeCode = async () => {
    try {
      setIsExecuting(true);
      setResult(null);
      onExecutionStart?.();

      const token = localStorage.getItem('xionimus_token');
      if (!token) {
        showToast({
          title: 'Authentifizierung erforderlich',
          description: 'Bitte melden Sie sich an',
          status: 'error',
          duration: 3000,
        });
        return;
      }

      const backendUrl = import.meta.env.VITE_BACKEND_URL || 
                        import.meta.env.REACT_APP_BACKEND_URL || 
                        'http://localhost:8001';

      const requestBody: any = {
        code,
        language: mapLanguage(language)
      };

      if (stdinInput.trim()) {
        requestBody.stdin = stdinInput;
      }

      const response = await fetch(`${backendUrl}/api/sandbox/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(requestBody)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data: ExecutionResult = await response.json();
      setResult(data);
      onExecutionComplete?.(data);

      if (data.success) {
        showToast({
          title: 'Code erfolgreich ausgeführt',
          description: `Laufzeit: ${data.execution_time}s`,
          status: 'success',
          duration: 3000,
        });
      } else {
        showToast({
          title: 'Code-Ausführung fehlgeschlagen',
          description: data.error || 'Siehe Fehlerausgabe',
          status: 'error',
          duration: 5000,
        });
      }
    } catch (error) {
      console.error('Code execution error:', error);
      showToast({
        title: 'Ausführungsfehler',
        description: error instanceof Error ? error.message : 'Unbekannter Fehler',
        status: 'error',
        duration: 5000,
      });
    } finally {
      setIsExecuting(false);
    }
  };

  return (
    <div className="space-y-3 w-full">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Button
            onClick={executeCode}
            disabled={isExecuting}
            variant="primary"
            size="sm"
            loading={isExecuting}
            leftIcon={<PlayIcon className="w-4 h-4" />}
          >
            {isExecuting ? 'Läuft...' : 'Code ausführen'}
          </Button>
          
          <div className="relative group">
            <button
              onClick={() => setShowStdin(!showStdin)}
              className={`
                p-2 rounded-lg transition-all duration-200
                ${showStdin 
                  ? 'bg-blue-500/20 border-blue-500 text-blue-400' 
                  : 'bg-transparent border-blue-500/50 text-blue-400/70 hover:bg-blue-500/10 hover:border-blue-500'
                }
                border
              `}
            >
              <DocumentTextIcon className="w-5 h-5" />
            </button>
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-50">
              <div className="glossy-card px-2 py-1 text-xs text-gray-300 whitespace-nowrap">
                Stdin Input
              </div>
            </div>
          </div>
          
          {result && (
            <span className="text-xs text-gray-500">
              {result.execution_time}s | Exit: {result.exit_code}
            </span>
          )}
        </div>
        
        <div>
          <select
            value={templateType}
            onChange={(e) => {
              setTemplateType(e.target.value);
              loadTemplate(e.target.value);
            }}
            disabled={isLoadingTemplate}
            className="input-glossy text-sm py-2 px-3 w-[200px]"
          >
            <option value="">Template laden...</option>
            <option value="hello_world">Hello World</option>
            <option value="fibonacci">Fibonacci</option>
            <option value="data_structures">Data Structures</option>
          </select>
        </div>
      </div>

      {showStdin && (
        <div className="animate-slide-in">
          <p className="text-xs font-bold mb-1 text-blue-400">
            📝 Stdin Input:
          </p>
          <textarea
            placeholder="Eingabe für Ihr Programm (z.B. Namen, Zahlen)..."
            value={stdinInput}
            onChange={(e) => setStdinInput(e.target.value)}
            rows={3}
            className="input-glossy w-full text-sm resize-none"
          />
        </div>
      )}

      {result && (
        <div className="space-y-2 animate-fade-in">
          {result.stdout && (
            <div>
              <p className="text-xs font-bold mb-1 text-green-400">
                ▶ Ausgabe:
              </p>
              <pre className="glossy-card p-3 text-green-300 text-sm whitespace-pre-wrap font-mono overflow-x-auto custom-scrollbar">
                {result.stdout}
              </pre>
            </div>
          )}

          {result.stderr && (
            <div>
              <p className="text-xs font-bold mb-1 text-red-400">
                ▶ Fehler:
              </p>
              <pre className="glossy-card p-3 text-red-300 text-sm whitespace-pre-wrap font-mono overflow-x-auto custom-scrollbar border-red-500/30">
                {result.stderr}
              </pre>
            </div>
          )}

          {result.timeout_occurred && (
            <div className="glossy-card p-3 bg-yellow-500/10 border-yellow-500/30">
              <p className="text-sm text-yellow-200">
                ⏱️ Timeout: Code-Ausführung überschritt Zeitlimit
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
