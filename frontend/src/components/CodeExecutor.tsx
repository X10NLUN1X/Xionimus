import React, { useState } from 'react';
import { Box, Button, VStack, HStack, Text, useToast, Code as ChakraCode, Spinner } from '@chakra-ui/react';
import { PlayIcon, StopCircleIcon } from '@heroicons/react/24/solid';

interface CodeExecutorProps {
  code: string;
  language: string;
  onExecutionStart?: () => void;
  onExecutionComplete?: (result: ExecutionResult) => void;
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
  onExecutionComplete
}) => {
  const [isExecuting, setIsExecuting] = useState(false);
  const [result, setResult] = useState<ExecutionResult | null>(null);
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
      'py': 'python',
      'pl': 'perl'
    };
    const normalized = lang.toLowerCase();
    return langMap[normalized] || normalized;
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

      const response = await fetch(`${backendUrl}/api/sandbox/execute`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          code,
          language: language.toLowerCase()
        })
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
        {result && (
          <Text fontSize="xs" color="gray.500">
            {result.execution_time}s | Exit: {result.exit_code}
          </Text>
        )}
      </HStack>

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