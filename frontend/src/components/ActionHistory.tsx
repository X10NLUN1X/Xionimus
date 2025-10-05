import React, { useState } from 'react';
import {
  Box,
  VStack,
  HStack,
  Text,
  Badge,
  Button,
  IconButton,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  useDisclosure,
  useToast,
  Tabs,
  TabList,
  TabPanels,
  Tab,
  TabPanel,
  Code,
  useColorModeValue,
} from '@chakra-ui/react';
import { FiRotateCcw, FiDownload, FiFilter } from 'react-icons/fi';

interface ActionHistoryItem {
  id: string;
  tool_name: string;
  arguments: any;
  result: any;
  success: boolean;
  execution_time: string;
  created_at: string;
}

interface ActionHistoryProps {
  sessionId: string;
  onRollbackAction: () => void;
  onRollbackSession: () => void;
}

const ActionHistory: React.FC<ActionHistoryProps> = ({
  sessionId,
  onRollbackAction,
  onRollbackSession,
}) => {
  const { isOpen, onOpen, onClose } = useDisclosure();
  const [history, setHistory] = useState<ActionHistoryItem[]>([]);
  const [filter, setFilter] = useState<string>('all');
  const toast = useToast();
  
  const bgColor = useColorModeValue('white', 'gray.800');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  
  const loadHistory = async () => {
    try {
      // TODO: API call to fetch action history
      // const response = await fetch(`/api/autonomous/history/${sessionId}`);
      // const data = await response.json();
      // setHistory(data.history);
      
      toast({
        title: 'Verlauf geladen',
        status: 'success',
        duration: 2000,
      });
    } catch (error) {
      toast({
        title: 'Fehler beim Laden',
        description: 'Konnte Aktionsverlauf nicht laden',
        status: 'error',
        duration: 3000,
      });
    }
  };
  
  const exportHistory = () => {
    const dataStr = JSON.stringify(history, null, 2);
    const blob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `action-history-${sessionId}.json`;
    link.click();
    URL.revokeObjectURL(url);
    
    toast({
      title: 'Verlauf exportiert',
      status: 'success',
      duration: 2000,
    });
  };
  
  const handleRollbackAction = async () => {
    try {
      onRollbackAction();
      toast({
        title: 'Letzte Aktion rückgängig gemacht',
        status: 'success',
        duration: 2000,
      });
      await loadHistory(); // Reload history
    } catch (error) {
      toast({
        title: 'Rollback fehlgeschlagen',
        description: 'Konnte Aktion nicht rückgängig machen',
        status: 'error',
        duration: 3000,
      });
    }
  };
  
  const handleRollbackSession = async () => {
    const confirmed = window.confirm(
      'Möchten Sie wirklich ALLE Aktionen dieser Session rückgängig machen? Dies kann nicht rückgängig gemacht werden!'
    );
    
    if (confirmed) {
      try {
        onRollbackSession();
        toast({
          title: 'Session zurückgesetzt',
          description: 'Alle Aktionen wurden rückgängig gemacht',
          status: 'success',
          duration: 3000,
        });
        await loadHistory(); // Reload history
      } catch (error) {
        toast({
          title: 'Session-Rollback fehlgeschlagen',
          status: 'error',
          duration: 3000,
        });
      }
    }
  };
  
  const filteredHistory = filter === 'all'
    ? history
    : filter === 'success'
    ? history.filter((item) => item.success)
    : history.filter((item) => !item.success);
  
  return (
    <>
      <Button
        size="sm"
        leftIcon={<FiRotateCcw />}
        onClick={() => {
          loadHistory();
          onOpen();
        }}
        variant="outline"
      >
        Aktionsverlauf
      </Button>
      
      <Modal isOpen={isOpen} onClose={onClose} size="xl" scrollBehavior="inside">
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>Autonome Aktionsverlauf</ModalHeader>
          <ModalCloseButton />
          
          <ModalBody>
            <VStack align="stretch" spacing={4}>
              <HStack justify="space-between">
                <HStack>
                  <Button
                    size="xs"
                    variant={filter === 'all' ? 'solid' : 'outline'}
                    onClick={() => setFilter('all')}
                  >
                    Alle ({history.length})
                  </Button>
                  <Button
                    size="xs"
                    variant={filter === 'success' ? 'solid' : 'outline'}
                    colorScheme="green"
                    onClick={() => setFilter('success')}
                  >
                    Erfolge ({history.filter((h) => h.success).length})
                  </Button>
                  <Button
                    size="xs"
                    variant={filter === 'failed' ? 'solid' : 'outline'}
                    colorScheme="red"
                    onClick={() => setFilter('failed')}
                  >
                    Fehler ({history.filter((h) => !h.success).length})
                  </Button>
                </HStack>
                
                <IconButton
                  aria-label="Export history"
                  icon={<FiDownload />}
                  size="xs"
                  onClick={exportHistory}
                />
              </HStack>
              
              {filteredHistory.length === 0 ? (
                <Text color="gray.500" textAlign="center" py={8}>
                  Keine Aktionen gefunden
                </Text>
              ) : (
                <VStack align="stretch" spacing={2}>
                  {filteredHistory.map((item) => (
                    <Box
                      key={item.id}
                      p={3}
                      bg={bgColor}
                      borderRadius="md"
                      borderWidth="1px"
                      borderColor={borderColor}
                    >
                      <HStack justify="space-between" mb={2}>
                        <Text fontWeight="bold" fontSize="sm">
                          {item.tool_name}
                        </Text>
                        <Badge colorScheme={item.success ? 'green' : 'red'}>
                          {item.success ? '✅' : '❌'}
                        </Badge>
                      </HStack>
                      
                      <Text fontSize="xs" color="gray.500" mb={2}>
                        {new Date(item.created_at).toLocaleString('de-DE')} • {item.execution_time}
                      </Text>
                      
                      <Tabs size="sm">
                        <TabList>
                          <Tab>Parameter</Tab>
                          <Tab>Ergebnis</Tab>
                        </TabList>
                        <TabPanels>
                          <TabPanel p={2}>
                            <Code
                              display="block"
                              whiteSpace="pre-wrap"
                              fontSize="xs"
                              p={2}
                            >
                              {JSON.stringify(item.arguments, null, 2)}
                            </Code>
                          </TabPanel>
                          <TabPanel p={2}>
                            <Code
                              display="block"
                              whiteSpace="pre-wrap"
                              fontSize="xs"
                              p={2}
                              maxH="150px"
                              overflowY="auto"
                            >
                              {JSON.stringify(item.result, null, 2)}
                            </Code>
                          </TabPanel>
                        </TabPanels>
                      </Tabs>
                    </Box>
                  ))}
                </VStack>
              )}
              
              <Box pt={4} borderTopWidth="1px" borderColor={borderColor}>
                <Text fontSize="sm" fontWeight="bold" mb={3}>
                  🔄 Rollback-Optionen
                </Text>
                <VStack align="stretch" spacing={2}>
                  <Button
                    size="sm"
                    leftIcon={<FiRotateCcw />}
                    colorScheme="orange"
                    variant="outline"
                    onClick={handleRollbackAction}
                  >
                    Letzte Aktion rückgängig machen
                  </Button>
                  <Button
                    size="sm"
                    leftIcon={<FiRotateCcw />}
                    colorScheme="red"
                    variant="outline"
                    onClick={handleRollbackSession}
                  >
                    Gesamte Session zurücksetzen
                  </Button>
                </VStack>
              </Box>
            </VStack>
          </ModalBody>
          
          <ModalFooter>
            <Button size="sm" onClick={onClose}>
              Schließen
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  );
};

export default ActionHistory;