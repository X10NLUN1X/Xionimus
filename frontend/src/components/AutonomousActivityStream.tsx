import React, { useState, useEffect } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  Divider,
  Icon,
  Collapse,
  IconButton,
  Code,
  useColorModeValue,
} from '@chakra-ui/react';
import {
  FiFile,
  FiTerminal,
  FiPackage,
  FiRefreshCw,
  FiGitBranch,
  FiCheck,
  FiX,
  FiLoader,
  FiChevronDown,
  FiChevronUp,
} from 'react-icons/fi';

interface AutonomousAction {
  id: number;
  tool: string;
  arguments: any;
  success?: boolean;
  result?: string;
  error?: string;
  executionTime?: number;
  status: 'pending' | 'executing' | 'completed' | 'failed';
  timestamp: Date;
}

interface AutonomousActivityStreamProps {
  actions: AutonomousAction[];
}

const AutonomousActivityStream: React.FC<AutonomousActivityStreamProps> = ({ actions }) => {
  const [expandedActions, setExpandedActions] = useState<Set<number>>(new Set());
  
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  const toggleExpand = (actionId: number) => {
    const newExpanded = new Set(expandedActions);
    if (newExpanded.has(actionId)) {
      newExpanded.delete(actionId);
    } else {
      newExpanded.add(actionId);
    }
    setExpandedActions(newExpanded);
  };
  
  const getToolIcon = (tool: string) => {
    if (tool.includes('file')) return FiFile;
    if (tool.includes('bash') || tool.includes('execute')) return FiTerminal;
    if (tool.includes('install')) return FiPackage;
    if (tool.includes('restart') || tool.includes('service')) return FiRefreshCw;
    if (tool.includes('git')) return FiGitBranch;
    return FiTerminal;
  };
  
  const getStatusBadge = (status: string, success?: boolean) => {
    if (status === 'pending') {
      return <Badge colorScheme="gray" fontSize="xs">⏳ Wartend</Badge>;
    }
    if (status === 'executing') {
      return <Badge colorScheme="blue" fontSize="xs">🔵 Ausführung...</Badge>;
    }
    if (status === 'completed' && success) {
      return <Badge colorScheme="green" fontSize="xs">✅ Erfolgreich</Badge>;
    }
    if (status === 'completed' && !success) {
      return <Badge colorScheme="orange" fontSize="xs">⚠️ Warnung</Badge>;
    }
    if (status === 'failed') {
      return <Badge colorScheme="red" fontSize="xs">❌ Fehler</Badge>;
    }
    return <Badge fontSize="xs">{status}</Badge>;
  };
  
  const formatArguments = (args: any): string => {
    if (typeof args === 'string') return args;
    if (typeof args === 'object') {
      const entries = Object.entries(args);
      if (entries.length === 0) return 'Keine Parameter';
      return entries.map(([key, value]) => `${key}: ${JSON.stringify(value)}`).join(', ');
    }
    return JSON.stringify(args);
  };

  if (actions.length === 0) {
    return (
      <Box p={4} bg={bgColor} borderRadius="md" borderWidth="1px" borderColor={borderColor}>
        <Text color="gray.500" fontSize="sm" textAlign="center">
          🤖 Warte auf autonome Aktionen...
        </Text>
      </Box>
    );
  }

  return (
    <VStack align="stretch" spacing={2} w="100%">
      {actions.map((action) => {
        const ToolIcon = getToolIcon(action.tool);
        const isExpanded = expandedActions.has(action.id);
        
        return (
          <Box
            key={action.id}
            p={3}
            bg={bgColor}
            borderRadius="md"
            borderWidth="1px"
            borderColor={borderColor}
            transition="all 0.2s"
            _hover={{ borderColor: 'blue.400' }}
          >
            <HStack justify="space-between" align="start">
              <HStack spacing={3} flex={1}>
                <Icon
                  as={ToolIcon}
                  boxSize={5}
                  color={
                    action.status === 'completed' && action.success
                      ? 'green.500'
                      : action.status === 'failed'
                      ? 'red.500'
                      : action.status === 'executing'
                      ? 'blue.500'
                      : 'gray.500'
                  }
                />
                <VStack align="start" spacing={1} flex={1}>
                  <HStack>
                    <Text fontWeight="bold" fontSize="sm">
                      {action.tool}
                    </Text>
                    {getStatusBadge(action.status, action.success)}
                  </HStack>
                  <Text fontSize="xs" color="gray.500">
                    {formatArguments(action.arguments)}
                  </Text>
                  {action.executionTime && action.status === 'completed' && (
                    <Text fontSize="xs" color="gray.400">
                      ⏱️ {action.executionTime.toFixed(2)}s
                    </Text>
                  )}
                </VStack>
              </HStack>
              
              {(action.result || action.error) && (
                <IconButton
                  aria-label="Toggle details"
                  icon={isExpanded ? <FiChevronUp /> : <FiChevronDown />}
                  size="sm"
                  variant="ghost"
                  onClick={() => toggleExpand(action.id)}
                />
              )}
            </HStack>
            
            <Collapse in={isExpanded}>
              <Box mt={3} pt={3} borderTopWidth="1px" borderColor={borderColor}>
                {action.result && (
                  <Box>
                    <Text fontSize="xs" fontWeight="bold" mb={1} color="green.500">
                      ✅ Ergebnis:
                    </Text>
                    <Code
                      display="block"
                      whiteSpace="pre-wrap"
                      fontSize="xs"
                      p={2}
                      borderRadius="md"
                      maxH="200px"
                      overflowY="auto"
                    >
                      {action.result}
                    </Code>
                  </Box>
                )}
                {action.error && (
                  <Box mt={action.result ? 2 : 0}>
                    <Text fontSize="xs" fontWeight="bold" mb={1} color="red.500">
                      ❌ Fehler:
                    </Text>
                    <Code
                      display="block"
                      whiteSpace="pre-wrap"
                      fontSize="xs"
                      p={2}
                      borderRadius="md"
                      colorScheme="red"
                    >
                      {action.error}
                    </Code>
                  </Box>
                )}
              </Box>
            </Collapse>
          </Box>
        );
      })}
    </VStack>
  );
};

export default AutonomousActivityStream;