/**
 * Extract code blocks from markdown text
 */

interface ExtractedCode {
  id: string
  name: string
  language: string
  content: string
  lineNumber: number
}

export const extractCodeFromMarkdown = (markdown: string): ExtractedCode[] => {
  const codeBlocks: ExtractedCode[] = []
  const codeBlockRegex = /```(\w+)?\n([\s\S]*?)```/g
  
  let match
  let blockIndex = 0
  let lineNumber = 0
  
  while ((match = codeBlockRegex.exec(markdown)) !== null) {
    const language = match[1] || 'text'
    const content = match[2].trim()
    
    // Count line number
    lineNumber = markdown.substring(0, match.index).split('\n').length
    
    // Generate filename based on language
    const extension = getFileExtension(language)
    const name = `code_${blockIndex + 1}.${extension}`
    
    codeBlocks.push({
      id: `code-${blockIndex}-${Date.now()}`,
      name,
      language: language.toLowerCase(),
      content,
      lineNumber
    })
    
    blockIndex++
  }
  
  return codeBlocks
}

/**
 * Extract code from multiple chat messages
 */
export const extractCodeFromMessages = (messages: any[]): ExtractedCode[] => {
  const allCodeBlocks: ExtractedCode[] = []
  
  messages.forEach((message, msgIndex) => {
    if (message.role === 'assistant' && message.content) {
      const blocks = extractCodeFromMarkdown(message.content)
      
      // Add message context to each block
      blocks.forEach(block => {
        block.id = `msg-${msgIndex}-${block.id}`
        block.name = `message_${msgIndex + 1}_${block.name}`
      })
      
      allCodeBlocks.push(...blocks)
    }
  })
  
  return allCodeBlocks
}

/**
 * Get file extension for language
 */
const getFileExtension = (language: string): string => {
  const extensionMap: Record<string, string> = {
    javascript: 'js',
    typescript: 'ts',
    python: 'py',
    java: 'java',
    c: 'c',
    cpp: 'cpp',
    csharp: 'cs',
    go: 'go',
    rust: 'rs',
    ruby: 'rb',
    php: 'php',
    sql: 'sql',
    html: 'html',
    css: 'css',
    json: 'json',
    xml: 'xml',
    yaml: 'yaml',
    markdown: 'md',
    bash: 'sh',
    shell: 'sh',
    text: 'txt'
  }
  
  return extensionMap[language.toLowerCase()] || 'txt'
}

/**
 * Format code with language-specific formatters (placeholder)
 */
export const formatCode = async (code: string, language: string): Promise<string> => {
  // TODO: Integrate with Prettier for JavaScript/TypeScript
  // TODO: Integrate with Black for Python
  // For now, just return the original code
  console.log(`Formatting ${language} code...`)
  return code
}

/**
 * Compare two code snippets (for diff view)
 */
export const generateDiff = (oldCode: string, newCode: string): string => {
  // TODO: Implement proper diff algorithm
  // For now, return a simple comparison
  const oldLines = oldCode.split('\n')
  const newLines = newCode.split('\n')
  
  let diff = ''
  const maxLength = Math.max(oldLines.length, newLines.length)
  
  for (let i = 0; i < maxLength; i++) {
    const oldLine = oldLines[i] || ''
    const newLine = newLines[i] || ''
    
    if (oldLine !== newLine) {
      if (oldLine) diff += `- ${oldLine}\n`
      if (newLine) diff += `+ ${newLine}\n`
    } else {
      diff += `  ${oldLine}\n`
    }
  }
  
  return diff
}

/**
 * Highlight search term in code
 */
export const highlightSearchTerm = (code: string, searchTerm: string): string => {
  if (!searchTerm) return code
  
  const regex = new RegExp(`(${searchTerm})`, 'gi')
  return code.replace(regex, '<mark class="bg-yellow-300 text-black">$1</mark>')
}
