import React, { useState } from 'react';
import { Box, Button, VStack, HStack, Text, useToast, Code as ChakraCode, Spinner, Textarea, Select, IconButton, Tooltip } from '@chakra-ui/react';
import { PlayIcon, StopCircleIcon } from '@heroicons/react/24/solid';
import { DocumentTextIcon } from '@heroicons/react/24/outline';

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
  const toast = useToast();

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
        toast({
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
        toast({
          title: 'Template geladen',
          description: `${type} Template für ${language}`,
          status: 'success',
          duration: 2000,
        });
      }
    } catch (error) {
      console.error('Template load error:', error);
      toast({
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
        toast({
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
        toast({
          title: 'Code erfolgreich ausgeführt',
          description: `Laufzeit: ${data.execution_time}s`,
          status: 'success',
          duration: 3000,
        });
      } else {
        toast({
          title: 'Code-Ausführung fehlgeschlagen',
          description: data.error || 'Siehe Fehlerausgabe',
          status: 'error',
          duration: 5000,
        });
      }
    } catch (error) {
      console.error('Code execution error:', error);
      toast({
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
    <VStack align="stretch" spacing={3} w="full">
      <HStack justify="space-between">
        <HStack>
          <Button
            leftIcon={isExecuting ? <Spinner size="sm" /> : <PlayIcon className="w-4 h-4" />}
            onClick={executeCode}
            isDisabled={isExecuting}
            colorScheme="green"
            size="sm"
          >
            {isExecuting ? 'Läuft...' : 'Code ausführen'}
          </Button>
          
          <Tooltip label="Stdin Input" placement="top">
            <IconButton
              aria-label="Stdin Input"
              icon={<DocumentTextIcon className="w-5 h-5" />}
              onClick={() => setShowStdin(!showStdin)}
              size="sm"
              variant={showStdin ? 'solid' : 'outline'}
              colorScheme="blue"
            />
          </Tooltip>
          
          {result && (
            <Text fontSize="xs" color="gray.500">
              {result.execution_time}s | Exit: {result.exit_code}
            </Text>
          )}
        </HStack>
        
        <HStack>
          <Select
            size="sm"
            placeholder="Template laden..."
            value={templateType}
            onChange={(e) => {
              setTemplateType(e.target.value);
              loadTemplate(e.target.value);
            }}
            isDisabled={isLoadingTemplate}
            width="200px"
          >
            <option value="hello_world">Hello World</option>
            <option value="fibonacci">Fibonacci</option>
            <option value="data_structures">Data Structures</option>
          </Select>
        </HStack>
      </HStack>

      {showStdin && (
        <Box>
          <Text fontSize="xs" fontWeight="bold" mb={1} color="blue.400">
            📝 Stdin Input:
          </Text>
          <Textarea
            placeholder="Eingabe für Ihr Programm (z.B. Namen, Zahlen)..."
            value={stdinInput}
            onChange={(e) => setStdinInput(e.target.value)}
            size="sm"
            rows={3}
            bg="gray.900"
            borderColor="blue.500"
          />
        </Box>
      )}

      {result && (
        <VStack align="stretch" spacing={2}>
          {result.stdout && (
            <Box>
              <Text fontSize="xs" fontWeight="bold" mb={1} color="green.400">
                ▶ Ausgabe:
              </Text>
              <ChakraCode
                p={3}
                bg="gray.900"
                color="green.300"
                fontSize="sm"
                borderRadius="md"
                whiteSpace="pre-wrap"
                display="block"
                fontFamily="monospace"
              >
                {result.stdout}
              </ChakraCode>
            </Box>
          )}

          {result.stderr && (
            <Box>
              <Text fontSize="xs" fontWeight="bold" mb={1} color="red.400">
                ▶ Fehler:
              </Text>
              <ChakraCode
                p={3}
                bg="gray.900"
                color="red.300"
                fontSize="sm"
                borderRadius="md"
                whiteSpace="pre-wrap"
                display="block"
                fontFamily="monospace"
              >
                {result.stderr}
              </ChakraCode>
            </Box>
          )}

          {result.timeout_occurred && (
            <Box bg="yellow.900" p={2} borderRadius="md">
              <Text fontSize="sm" color="yellow.200">
                ⏱️ Timeout: Code-Ausführung überschritt Zeitlimit
              </Text>
            </Box>
          )}
        </VStack>
      )}
    </VStack>
  );
};