import React, { useState } from 'react'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism'
import { useLanguage } from '../contexts/LanguageContext'
import { CodeExecutor } from './CodeExecutor'
import { useToast } from './UI/Toast'

interface CodeBlockProps {
  language: string
  code: string
}

export const CodeBlock: React.FC<CodeBlockProps> = ({ language, code }) => {
  const [hasCopied, setHasCopied] = useState(false)
  const { showToast } = useToast()
  const { t } = useLanguage()
  const [isHovered, setIsHovered] = useState(false)
  
  // Check if language is executable
  const isExecutable = [
    'python', 'py',
    'javascript', 'js',
    'typescript', 'ts',
    'bash', 'shell', 'sh',
    'cpp', 'c++',
    'c',
    'csharp', 'c#', 'cs',
    'java',
    'go', 'golang',
    'php',
    'ruby', 'rb',
    'perl', 'pl'
  ].includes(language.toLowerCase())

  const handleCopy = () => {
    navigator.clipboard.writeText(code)
    setHasCopied(true)
    setTimeout(() => setHasCopied(false), 2000)
    
    showToast({
      title: 'Code copied!',
      status: 'success',
      duration: 2000,
    })
  }

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
    
    showToast({
      title: t('toast.downloadStarted'),
      status: 'success',
      duration: 2000,
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
    <div
      className="relative rounded-xl overflow-hidden my-3 glossy-card border-gold-500/10"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Header with language and actions */}
      <div className="flex items-center justify-between px-4 py-2 bg-primary-darker border-b border-gold-500/20">
        <div className="flex items-center gap-3">
          <span className="text-xs font-semibold text-gold-400 uppercase tracking-wide">
            {language || 'code'}
          </span>
          <span className="text-xs text-gray-500">
            {lineCount} {t('code.lines')}
          </span>
        </div>
        
        <div className={`flex items-center gap-2 transition-opacity duration-200 ${isHovered ? 'opacity-100' : 'opacity-60'}`}>
          <button
            onClick={handleCopy}
            className={`
              px-3 py-1.5 rounded-lg text-xs font-semibold
              flex items-center gap-1.5
              transition-all duration-200
              ${hasCopied
                ? 'bg-green-500/20 text-green-400 border border-green-500/50'
                : 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50 hover:bg-cyan-500/30'
              }
            `}
          >
            {hasCopied ? (
              <>
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                {t('code.copied')}
              </>
            ) : (
              <>
                <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                {t('code.copy')}
              </>
            )}
          </button>
          <button
            onClick={handleDownload}
            className="p-1.5 rounded-lg text-cyan-400 border border-cyan-500/50 hover:bg-cyan-500/20 transition-all duration-200"
            aria-label={t('code.download')}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
          </button>
        </div>
      </div>

      {/* Code content */}
      <div className="max-h-[600px] overflow-y-auto custom-scrollbar">
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
      </div>
      
      {/* Code Executor */}
      {isExecutable && (
        <div className="px-4 py-3 bg-primary-darker border-t border-gold-500/20">
          <CodeExecutor 
            code={code} 
            language={language.toLowerCase()} 
          />
        </div>
      )}
    </div>
  )
}
