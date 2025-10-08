import React, { useState } from 'react'
import {
  HStack,
  IconButton,
  Tooltip,
  useToast,
  useClipboard,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  AlertDialog,
  AlertDialogBody,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogContent,
  AlertDialogOverlay,
  Button,
  useDisclosure,
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalFooter,
  ModalCloseButton,
  Textarea,
  useColorModeValue
} from '@chakra-ui/react'
import {
  CopyIcon,
  EditIcon,
  RepeatIcon,
  DeleteIcon,
  ChevronDownIcon,
  CheckIcon
} from '@chakra-ui/icons'
import { useLanguage } from '../contexts/LanguageContext'

interface MessageActionsProps {
  messageId: string
  content: string
  role: 'user' | 'assistant'
  onEdit?: (messageId: string, newContent: string) => void
  onRegenerate?: (messageId: string) => void
  onDelete?: (messageId: string) => void
  isVisible?: boolean
}

export const MessageActions: React.FC<MessageActionsProps> = ({
  messageId,
  content,
  role,
  onEdit,
  onRegenerate,
  onDelete,
  isVisible = true
}) => {
  const { t } = useLanguage()
  const toast = useToast()
  const { onCopy, hasCopied } = useClipboard(content)
  
  const [editContent, setEditContent] = useState(content)
  const { isOpen: isEditOpen, onOpen: onEditOpen, onClose: onEditClose } = useDisclosure()
  const { isOpen: isDeleteOpen, onOpen: onDeleteOpen, onClose: onDeleteClose } = useDisclosure()
  const cancelRef = React.useRef<HTMLButtonElement>(null)
  
  const bgColor = useColorModeValue('white', 'rgba(10, 22, 40, 0.95)')
  const borderColor = useColorModeValue('gray.200', 'rgba(0, 212, 255, 0.3)')

  const handleCopy = () => {
    onCopy()
    if (toast) {
      toast({
        title: t('toast.copiedToClipboard'),
        status: 'success',
        duration: 2000,
        isClosable: true,
      })
    }
  }

  const handleEdit = () => {
    if (onEdit && editContent.trim() !== content) {
      onEdit(messageId, editContent.trim())
      toast({
        title: 'Message edited',
        status: 'success',
        duration: 2000,
      })
    }
    onEditClose()
  }

  const handleRegenerate = () => {
    if (onRegenerate) {
      onRegenerate(messageId)
      toast({
        title: 'Regenerating response...',
        status: 'info',
        duration: 2000,
      })
    }
  }

  const handleDelete = () => {
    if (onDelete) {
      onDelete(messageId)
      toast({
        title: t('toast.sessionDeleted'),
        status: 'success',
        duration: 2000,
      })
    }
    onDeleteClose()
  }

  if (!isVisible) return null

  return (
    <>
      <HStack 
        spacing={1} 
        opacity={0.7}
        _hover={{ opacity: 1 }}
        transition="opacity 0.2s"
      >
        {/* Copy */}
        <Tooltip label={hasCopied ? t('code.copied') : t('code.copy')} placement="top">
          <IconButton
            icon={hasCopied ? <CheckIcon /> : <CopyIcon />}
            aria-label="Copy message"
            size="sm"
            variant="ghost"
            onClick={handleCopy}
            colorScheme={hasCopied ? 'green' : 'gray'}
          />
        </Tooltip>

        {/* Edit (only for user messages) */}
        {role === 'user' && onEdit && (
          <Tooltip label="Edit message" placement="top">
            <IconButton
              icon={<EditIcon />}
              aria-label="Edit message"
              size="sm"
              variant="ghost"
              onClick={onEditOpen}
            />
          </Tooltip>
        )}

        {/* Regenerate (only for assistant messages) */}
        {role === 'assistant' && onRegenerate && (
          <Tooltip label="Regenerate response" placement="top">
            <IconButton
              icon={<RepeatIcon />}
              aria-label="Regenerate"
              size="sm"
              variant="ghost"
              onClick={handleRegenerate}
            />
          </Tooltip>
        )}

        {/* More Actions Menu */}
        <Menu>
          <MenuButton
            as={IconButton}
            icon={<ChevronDownIcon />}
            aria-label="More actions"
            size="sm"
            variant="ghost"
          />
          <MenuList>
            {onDelete && (
              <MenuItem icon={<DeleteIcon />} onClick={onDeleteOpen} color="red.500">
                🗑️ Delete message
              </MenuItem>
            )}
          </MenuList>
        </Menu>
      </HStack>

      {/* Edit Modal */}
      <Modal isOpen={isEditOpen} onClose={onEditClose} size="xl">
        <ModalOverlay />
        <ModalContent bg={bgColor}>
          <ModalHeader>Edit Message</ModalHeader>
          <ModalCloseButton />
          <ModalBody>
            <Textarea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              placeholder="Edit your message..."
              minH="150px"
              autoFocus
            />
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" mr={3} onClick={onEditClose}>
              Cancel
            </Button>
            <Button 
              colorScheme="cyan" 
              onClick={handleEdit}
              isDisabled={!editContent.trim() || editContent === content}
            >
              Save Changes
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Delete Confirmation Dialog */}
      <AlertDialog
        isOpen={isDeleteOpen}
        leastDestructiveRef={cancelRef}
        onClose={onDeleteClose}
      >
        <AlertDialogOverlay>
          <AlertDialogContent bg={bgColor} borderColor={borderColor} borderWidth="1px">
            <AlertDialogHeader fontSize="lg" fontWeight="bold">
              Delete Message
            </AlertDialogHeader>

            <AlertDialogBody>
              Are you sure? This will delete this message and all messages after it.
              This action cannot be undone.
            </AlertDialogBody>

            <AlertDialogFooter>
              <Button ref={cancelRef} onClick={onDeleteClose}>
                Cancel
              </Button>
              <Button colorScheme="red" onClick={handleDelete} ml={3}>
                Delete
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialogOverlay>
      </AlertDialog>
    </>
  )
}
