import React, { useRef, useEffect, useState } from 'react'
import { Editor, OnMount, OnChange } from '@monaco-editor/react'
import { 
  Box, 
  useColorModeValue, 
  Spinner, 
  VStack, 
  Text,
  useToast,
  HStack,
  Badge,
  Button
} from '@chakra-ui/react'
import { editor } from 'monaco-editor'

interface MonacoEditorProps {
  value: string
  onChange: (value: string | undefined) => void
  onSave?: (value: string) => void
  language?: string
  path?: string
  readOnly?: boolean
  height?: string | number
  options?: editor.IStandaloneEditorConstructionOptions
}

export const MonacoEditor: React.FC<MonacoEditorProps> = ({
  value,
  onChange,
  onSave,
  language = 'typescript',
  path,
  readOnly = false,
  height = '100%',
  options = {}
}) => {
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false)
  const [lastSaved, setLastSaved] = useState<Date | null>(null)
  const toast = useToast()

  const theme = useColorModeValue('vs-light', 'vs-dark')
  const bg = useColorModeValue('white', 'gray.900')

  const defaultOptions: editor.IStandaloneEditorConstructionOptions = {
    readOnly,
    minimap: { enabled: true },
    scrollBeyondLastLine: false,
    automaticLayout: true,
    fontSize: 14,
    lineNumbers: 'on',
    wordWrap: 'on',
    tabSize: 2,
    insertSpaces: true,
    detectIndentation: true,
    folding: true,
    renderLineHighlight: 'line',
    cursorBlinking: 'blink',
    formatOnPaste: true,
    formatOnType: true,
    suggestOnTriggerCharacters: true,
    acceptSuggestionOnEnter: 'on',
    ...options
  }

  const handleEditorDidMount: OnMount = (editor, monaco) => {
    editorRef.current = editor
    setIsLoading(false)

    // Add keyboard shortcuts
    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
      handleSave()
    })

    // Focus the editor
    editor.focus()

    // Configure language features
    monaco.languages.typescript.typescriptDefaults.setCompilerOptions({
      target: monaco.languages.typescript.ScriptTarget.Latest,
      allowNonTsExtensions: true,
      moduleResolution: monaco.languages.typescript.ModuleResolutionKind.NodeJs,
      module: monaco.languages.typescript.ModuleKind.CommonJS,
      noEmit: true,
      esModuleInterop: true,
      jsx: monaco.languages.typescript.JsxEmit.React,
      allowSyntheticDefaultImports: true,
      skipLibCheck: true,
    })
  }

  const handleEditorChange: OnChange = (newValue) => {
    onChange(newValue)
    setHasUnsavedChanges(true)
  }

  const handleSave = () => {
    if (onSave && hasUnsavedChanges) {
      onSave(value)
      setHasUnsavedChanges(false)
      setLastSaved(new Date())
      toast({
        title: 'File saved',
        description: path ? `Saved ${path}` : 'File saved successfully',
        status: 'success',
        duration: 2000,
        isClosable: true,
      })
    }
  }

  // Auto-save functionality
  useEffect(() => {
    if (!hasUnsavedChanges) return
    
    const autoSaveTimer = setTimeout(() => {
      if (onSave) {
        handleSave()
      }
    }, 2000) // Auto-save after 2 seconds of inactivity

    return () => clearTimeout(autoSaveTimer)
  }, [value, hasUnsavedChanges])

  const getLanguageFromPath = (filePath: string): string => {
    const ext = filePath.split('.').pop()?.toLowerCase()
    
    const languageMap: Record<string, string> = {
      'js': 'javascript',
      'jsx': 'javascript',
      'ts': 'typescript',
      'tsx': 'typescript',
      'py': 'python',
      'html': 'html',
      'css': 'css',
      'scss': 'scss',
      'json': 'json',
      'md': 'markdown',
      'yaml': 'yaml',
      'yml': 'yaml',
      'xml': 'xml',
      'php': 'php',
      'java': 'java',
      'cpp': 'cpp',
      'c': 'c',
      'cs': 'csharp',
      'go': 'go',
      'rust': 'rust',
      'sql': 'sql',
      'sh': 'shell',
      'bash': 'shell',
      'dockerfile': 'dockerfile',
    }
    
    return languageMap[ext || ''] || 'plaintext'
  }

  const currentLanguage = path ? getLanguageFromPath(path) : language

  // Optimize editor for welcome content
  const isWelcomeFile = path === 'welcome.md'
  const editorOptions = {
    ...defaultOptions,
    ...(isWelcomeFile && {
      readOnly: false,
      wordWrap: 'on' as const,
      lineNumbers: 'on' as const,
      minimap: { enabled: false }, // Disable minimap for welcome file
      scrollBeyondLastLine: false,
      renderLineHighlight: 'gutter' as const,
    })
  }

  if (isLoading) {
    return (
      <Box 
        h={height} 
        bg={bg} 
        display="flex" 
        alignItems="center" 
        justifyContent="center"
        border="1px solid"
        borderColor={useColorModeValue('gray.200', 'gray.700')}
        borderRadius="md"
      >
        <VStack spacing={4}>
          <Spinner size="lg" />
          <Text>Loading Monaco Editor...</Text>
        </VStack>
      </Box>
    )
  }

  return (
    <Box position="relative" h={height}>
      {/* Status bar */}
      <HStack 
        px={4} 
        py={2} 
        bg={useColorModeValue('gray.50', 'gray.800')} 
        borderBottom="1px solid"
        borderColor={useColorModeValue('gray.200', 'gray.700')}
        fontSize="sm"
        spacing={4}
      >
        <Text fontWeight="medium">{path || 'Untitled'}</Text>
        <Badge colorScheme={currentLanguage === 'plaintext' ? 'gray' : 'blue'}>
          {currentLanguage}
        </Badge>
        {hasUnsavedChanges && (
          <Badge 
            bg="linear-gradient(135deg, #0088cc, #0066aa)"
            color="white"
            boxShadow="0 2px 10px rgba(0, 212, 255, 0.4)"
          >
            Unsaved changes
          </Badge>
        )}
        {lastSaved && (
          <Text color="gray.500" fontSize="xs">
            Last saved: {lastSaved.toLocaleTimeString()}
          </Text>
        )}
        {onSave && hasUnsavedChanges && (
          <Button size="xs" colorScheme="blue" onClick={handleSave}>
            Save (Ctrl+S)
          </Button>
        )}
      </HStack>

      {/* Editor */}
      <Box h="calc(100% - 60px)">
        <Editor
          height="100%"
          language={currentLanguage}
          value={value}
          onChange={handleEditorChange}
          onMount={handleEditorDidMount}
          theme={theme}
          options={editorOptions}
          loading={<Spinner size="lg" />}
        />
      </Box>
    </Box>
  )
}