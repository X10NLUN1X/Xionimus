import React, { useState } from 'react'
import { Box, Button, HStack, Text, useClipboard, useToast, IconButton } from '@chakra-ui/react'
import { CopyIcon, CheckIcon, DownloadIcon } from '@chakra-ui/icons'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { useLanguage } from '../contexts/LanguageContext'
import { CodeExecutor } from './CodeExecutor'

interface CodeBlockProps {
  language: string
  code: string
}

export const CodeBlock: React.FC<CodeBlockProps> = ({ language, code }) => {
  const { onCopy, hasCopied } = useClipboard(code)
  const toast = useToast()
  const { t } = useLanguage()
  const [isHovered, setIsHovered] = useState(false)
  const [showExecutor, setShowExecutor] = useState(false)
  
  // Check if language is executable
  const isExecutable = ['python', 'javascript', 'js', 'bash', 'shell'].includes(language.toLowerCase())

  const handleDownload = () => {
    const extension = getFileExtension(language)
    const filename = `code.${extension}`
    const blob = new Blob([code], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    toast({
      title: t('toast.downloadStarted'),
      status: 'success',
      duration: 2000,
      isClosable: true,
    })
  }

  const getFileExtension = (lang: string): string => {
    const extensions: { [key: string]: string } = {
      javascript: 'js',
      typescript: 'ts',
      python: 'py',
      java: 'java',
      cpp: 'cpp',
      c: 'c',
      csharp: 'cs',
      go: 'go',
      rust: 'rs',
      php: 'php',
      ruby: 'rb',
      swift: 'swift',
      kotlin: 'kt',
      html: 'html',
      css: 'css',
      json: 'json',
      yaml: 'yaml',
      yml: 'yml',
      xml: 'xml',
      sql: 'sql',
      bash: 'sh',
      shell: 'sh',
      powershell: 'ps1',
      markdown: 'md',
      jsx: 'jsx',
      tsx: 'tsx',
    }
    return extensions[lang.toLowerCase()] || 'txt'
  }

  const lineCount = code.split('\n').length

  return (
    <Box
      position="relative"
      borderRadius="md"
      overflow="hidden"
      my={3}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Header with language and actions */}
      <HStack
        justify="space-between"
        px={4}
        py={2}
        bg="rgba(30, 30, 30, 0.95)"
        borderBottom="1px solid"
        borderColor="rgba(255, 255, 255, 0.1)"
      >
        <HStack spacing={3}>
          <Text
            fontSize="xs"
            fontWeight="600"
            color="rgba(0, 212, 255, 0.9)"
            textTransform="uppercase"
            letterSpacing="wide"
          >
            {language || 'code'}
          </Text>
          <Text fontSize="xs" color="gray.500">
            {lineCount} {t('code.lines')}
          </Text>
        </HStack>
        
        <HStack spacing={2} opacity={isHovered ? 1 : 0.6} transition="opacity 0.2s">
          <Button
            size="xs"
            leftIcon={hasCopied ? <CheckIcon /> : <CopyIcon />}
            onClick={onCopy}
            colorScheme={hasCopied ? 'green' : 'cyan'}
            variant="solid"
          >
            {hasCopied ? t('code.copied') : t('code.copy')}
          </Button>
          <IconButton
            size="xs"
            icon={<DownloadIcon />}
            onClick={handleDownload}
            colorScheme="cyan"
            variant="outline"
            aria-label={t('code.download')}
          />
        </HStack>
      </HStack>

      {/* Code content */}
      <Box maxH="600px" overflowY="auto">
        {/* @ts-ignore - react-syntax-highlighter type mismatch */}
        <SyntaxHighlighter
          language={language}
          style={vscDarkPlus as any}
          showLineNumbers
          customStyle={{
            margin: 0,
            padding: '1rem',
            fontSize: '0.875rem',
            background: '#1e1e1e',
          }}
          lineNumberStyle={{
            minWidth: '3em',
            paddingRight: '1em',
            color: '#858585',
            userSelect: 'none',
          }}
        >
          {code}
        </SyntaxHighlighter>
      </Box>
      
      {/* Code Executor - Phase 4: Cloud Sandbox */}
      {isExecutable && (
        <Box px={4} py={3} bg="rgba(30, 30, 30, 0.95)" borderTop="1px solid" borderColor="rgba(255, 255, 255, 0.1)">
          <CodeExecutor 
            code={code} 
            language={language.toLowerCase()} 
          />
        </Box>
      )}
    </Box>
  )
}
