import React, { useState } from 'react'
import {
  Box,
  VStack,
  HStack,
  Text,
  Input,
  IconButton,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  useColorModeValue,
  useToast,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  Button,
  useDisclosure,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
} from '@chakra-ui/react'
import {
  SearchIcon,
  DeleteIcon,
  EditIcon,
  DownloadIcon,
  ChatIcon,
  HamburgerIcon,
} from '@chakra-ui/icons'
import { useLanguage } from '../contexts/LanguageContext'
import { useApp } from '../contexts/AppContext'

interface ChatHistoryProps {
  isOpen: boolean
  onClose: () => void
}

export const ChatHistory: React.FC<ChatHistoryProps> = ({ isOpen, onClose }) => {
  const { t } = useLanguage()
  const { sessions, currentSession, switchSession, deleteSession, renameSession } = useApp()
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null)
  const [newName, setNewName] = useState('')
  const { isOpen: isRenameOpen, onOpen: onRenameOpen, onClose: onRenameClose } = useDisclosure()
  const { isOpen: isDeleteOpen, onOpen: onDeleteOpen, onClose: onDeleteClose } = useDisclosure()
  const toast = useToast()
  
  const bgColor = useColorModeValue('white', 'rgba(10, 22, 40, 0.95)')
  const borderColor = useColorModeValue('gray.200', 'rgba(0, 212, 255, 0.3)')
  const hoverBg = useColorModeValue('gray.50', 'rgba(0, 212, 255, 0.1)')
  const activeBg = useColorModeValue('blue.50', 'rgba(0, 212, 255, 0.2)')

  const filteredSessions = sessions.filter(session => {
    // Safe access to messages array with optional chaining and default
    const firstMessage = session?.messages?.[0]?.content?.toLowerCase() || ''
    return firstMessage.includes(searchQuery.toLowerCase())
  })

  const handleRename = () => {
    if (selectedSessionId && newName.trim()) {
      renameSession(selectedSessionId, newName.trim())
      toast({
        title: t('toast.sessionRenamed'),
        status: 'success',
        duration: 2000,
      })
      onRenameClose()
      setNewName('')
    }
  }

  const handleDelete = () => {
    if (selectedSessionId) {
      deleteSession(selectedSessionId)
      toast({
        title: t('toast.sessionDeleted'),
        status: 'success',
        duration: 2000,
      })
      onDeleteClose()
    }
  }

  const handleExport = (sessionId: string) => {
    const session = sessions.find(s => s.id === sessionId)
    if (!session) return

    const markdown = generateMarkdown(session)
    const blob = new Blob([markdown], { type: 'text/markdown' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `chat-${session.name || sessionId}-${new Date().toISOString().split('T')[0]}.md`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    toast({
      title: t('toast.exportComplete'),
      status: 'success',
      duration: 2000,
    })
  }

  const generateMarkdown = (session: any): string => {
    let md = `# ${session.name || 'Chat Session'}\n\n`
    md += `**Date**: ${new Date(session.createdAt).toLocaleString()}\n\n`
    md += `---\n\n`

    session.messages.forEach((msg: any, idx: number) => {
      const role = msg.role === 'user' ? '👤 User' : '🤖 Assistant'
      md += `## ${role}\n\n${msg.content}\n\n`
      if (idx < session.messages.length - 1) {
        md += `---\n\n`
      }
    })

    return md
  }

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    const diffHours = Math.floor(diffMs / 3600000)
    const diffDays = Math.floor(diffMs / 86400000)

    if (diffMins < 60) return `${diffMins}m ago`
    if (diffHours < 24) return `${diffHours}h ago`
    if (diffDays < 7) return `${diffDays}d ago`
    return date.toLocaleDateString()
  }

  return (
    <>
      <Drawer isOpen={isOpen} placement="left" onClose={onClose} size="md">
        <DrawerOverlay />
        <DrawerContent bg={bgColor}>
          <DrawerCloseButton />
          <DrawerHeader borderBottomWidth="1px" borderColor={borderColor}>
            <HStack spacing={2}>
              <ChatIcon color="cyan.400" />
              <Text>{t('history.title')}</Text>
            </HStack>
          </DrawerHeader>

          <DrawerBody p={0}>
            <VStack spacing={0} align="stretch">
              {/* Search */}
              <Box p={4} borderBottom="1px solid" borderColor={borderColor}>
                <HStack spacing={2}>
                  <SearchIcon color="gray.400" />
                  <Input
                    placeholder={t('history.search')}
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    size="sm"
                    flex={1}
                  />
                </HStack>
              </Box>

              {/* Sessions List */}
              <VStack spacing={0} align="stretch" overflowY="auto" maxH="calc(100vh - 180px)">
                {filteredSessions.length === 0 ? (
                  <Box p={8} textAlign="center">
                    <Text color="gray.500">{t('history.noChats')}</Text>
                  </Box>
                ) : (
                  filteredSessions.map((session) => {
                    const firstMessage = session.messages[0]?.content || 'New Chat'
                    const preview = firstMessage.length > 60 
                      ? firstMessage.substring(0, 60) + '...' 
                      : firstMessage
                    const isActive = (typeof currentSession === 'string' ? currentSession : currentSession?.id) === session.id

                    return (
                      <HStack
                        key={session.id}
                        p={4}
                        spacing={3}
                        cursor="pointer"
                        bg={isActive ? activeBg : 'transparent'}
                        _hover={{ bg: hoverBg }}
                        borderBottom="1px solid"
                        borderColor={borderColor}
                        onClick={() => {
                          switchSession(session.id)
                          onClose()
                        }}
                      >
                        <ChatIcon color={isActive ? 'cyan.400' : 'gray.400'} />
                        <VStack flex={1} align="start" spacing={1}>
                          <Text fontSize="sm" fontWeight={isActive ? '600' : '400'} noOfLines={1}>
                            {session.name || preview}
                          </Text>
                          <Text fontSize="xs" color="gray.500">
                            {formatDate(session.createdAt)} · {session.messages.length} msgs
                          </Text>
                        </VStack>
                        
                        <Menu>
                          <MenuButton
                            as={IconButton}
                            icon={<HamburgerIcon />}
                            size="xs"
                            variant="ghost"
                            onClick={(e) => {
                              e.stopPropagation()
                            }}
                          />
                          <MenuList>
                            <MenuItem
                              icon={<EditIcon />}
                              onClick={(e) => {
                                e.stopPropagation()
                                setSelectedSessionId(session.id)
                                setNewName(session.name || '')
                                onRenameOpen()
                              }}
                            >
                              {t('history.rename')}
                            </MenuItem>
                            <MenuItem
                              icon={<DownloadIcon />}
                              onClick={(e) => {
                                e.stopPropagation()
                                handleExport(session.id)
                              }}
                            >
                              {t('history.export')}
                            </MenuItem>
                            <MenuItem
                              icon={<DeleteIcon />}
                              color="red.500"
                              onClick={(e) => {
                                e.stopPropagation()
                                setSelectedSessionId(session.id)
                                onDeleteOpen()
                              }}
                            >
                              {t('history.delete')}
                            </MenuItem>
                          </MenuList>
                        </Menu>
                      </HStack>
                    )
                  })
                )}
              </VStack>
            </VStack>
          </DrawerBody>
        </DrawerContent>
      </Drawer>

      {/* Rename Modal */}
      <Modal isOpen={isRenameOpen} onClose={onRenameClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{t('history.rename')}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Input
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="Enter new name"
              autoFocus
            />
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onRenameClose}>
              {t('misc.cancel')}
            </Button>
            <Button colorScheme="cyan" onClick={handleRename}>
              {t('misc.confirm')}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal isOpen={isDeleteOpen} onClose={onDeleteClose}>
        <ModalOverlay />
        <ModalContent>
          <ModalHeader>{t('history.delete')}</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Text>{t('history.deleteConfirm')}</Text>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onDeleteClose}>
              {t('misc.cancel')}
            </Button>
            <Button colorScheme="red" onClick={handleDelete}>
              {t('misc.confirm')}
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  )
}
