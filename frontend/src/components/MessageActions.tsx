import React, { useState } from 'react'
import { Modal, ModalContent, ModalHeader, ModalBody, ModalFooter } from './Modal'
import { Button } from './UI/Button'
import { useToast } from './UI/Toast'
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
  const { showToast } = useToast()
  const [hasCopied, setHasCopied] = useState(false)
  
  const [editContent, setEditContent] = useState(content)
  const [isEditOpen, setIsEditOpen] = useState(false)
  const [isDeleteOpen, setIsDeleteOpen] = useState(false)
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content)
      setHasCopied(true)
      setTimeout(() => setHasCopied(false), 2000)
      showToast({
        title: t('toast.copiedToClipboard'),
        status: 'success',
        duration: 2000,
      })
    } catch (err) {
      showToast({
        title: 'Failed to copy',
        status: 'error',
        duration: 2000,
      })
    }
  }

  const handleEdit = () => {
    if (onEdit && editContent.trim() !== content) {
      onEdit(messageId, editContent.trim())
      showToast({
        title: 'Message edited',
        status: 'success',
        duration: 2000,
      })
    }
    setIsEditOpen(false)
  }

  const handleRegenerate = () => {
    if (onRegenerate) {
      onRegenerate(messageId)
      showToast({
        title: 'Regenerating response...',
        status: 'info',
        duration: 2000,
      })
    }
  }

  const handleDelete = () => {
    if (onDelete) {
      onDelete(messageId)
      showToast({
        title: 'Message deleted',
        status: 'success',
        duration: 2000,
      })
    }
    setIsDeleteOpen(false)
  }

  if (!isVisible) return null

  return (
    <>
      {/* Action Buttons */}
      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
        {/* Copy Button */}
        <button
          onClick={handleCopy}
          className="p-1.5 rounded hover:bg-accent-blue transition-colors"
          title="Copy"
        >
          {hasCopied ? (
            <svg className="w-4 h-4 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          ) : (
            <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          )}
        </button>

        {/* Edit Button (only for user messages) */}
        {role === 'user' && onEdit && (
          <button
            onClick={() => setIsEditOpen(true)}
            className="p-1.5 rounded hover:bg-accent-blue transition-colors"
            title="Edit"
          >
            <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
            </svg>
          </button>
        )}

        {/* Regenerate Button (only for assistant messages) */}
        {role === 'assistant' && onRegenerate && (
          <button
            onClick={handleRegenerate}
            className="p-1.5 rounded hover:bg-accent-blue transition-colors"
            title="Regenerate"
          >
            <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </button>
        )}

        {/* Delete Button */}
        {onDelete && (
          <button
            onClick={() => setIsDeleteOpen(true)}
            className="p-1.5 rounded hover:bg-red-500/20 transition-colors"
            title="Delete"
          >
            <svg className="w-4 h-4 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
          </button>
        )}
      </div>

      {/* Edit Modal */}
      <Modal isOpen={isEditOpen} onClose={() => setIsEditOpen(false)} size="lg">
        <ModalContent>
          <ModalHeader onClose={() => setIsEditOpen(false)}>
            Edit Message
          </ModalHeader>
          <ModalBody>
            <textarea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              rows={6}
              className="input-glossy w-full resize-none"
              placeholder="Edit your message..."
            />
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" onClick={() => setIsEditOpen(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleEdit}>
              Save Changes
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal isOpen={isDeleteOpen} onClose={() => setIsDeleteOpen(false)} size="md">
        <ModalContent className="border-red-500/50">
          <ModalHeader onClose={() => setIsDeleteOpen(false)}>
            Delete Message
          </ModalHeader>
          <ModalBody>
            <p className="text-gray-300">
              Are you sure you want to delete this message? This action cannot be undone.
            </p>
          </ModalBody>
          <ModalFooter>
            <Button variant="ghost" onClick={() => setIsDeleteOpen(false)}>
              Cancel
            </Button>
            <Button variant="danger" onClick={handleDelete}>
              Delete
            </Button>
          </ModalFooter>
        </ModalContent>
      </Modal>
    </>
  )
}