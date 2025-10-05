import React from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { CodeBlock } from './CodeBlock'

interface MemoizedMarkdownProps {
  content: string
  isUserMessage?: boolean
}

/**
 * Memoized ReactMarkdown Component
 * Prevents re-parsing markdown when parent components re-render
 * Only re-renders when content actually changes
 */
export const MemoizedMarkdown = React.memo<MemoizedMarkdownProps>(({ content, isUserMessage = false }) => {
  const markdownComponents = React.useMemo(() => ({
    code: ({ node, inline, className, children, ...props }: any) => {
      const match = /language-(\w+)/.exec(className || '')
      const language = match ? match[1] : ''
      
      return !inline && language ? (
        <CodeBlock
          code={String(children).replace(/\n$/, '')}
          language={language}
        />
      ) : (
        <code
          style={{
            background: isUserMessage 
              ? 'rgba(255, 255, 255, 0.15)' 
              : 'rgba(0, 212, 255, 0.12)',
            padding: '3px 8px',
            borderRadius: '5px',
            fontSize: '14px',
            fontWeight: '500',
            fontFamily: "'JetBrains Mono', 'Fira Code', 'Consolas', 'Monaco', monospace",
            border: '1px solid',
            borderColor: isUserMessage
              ? 'rgba(255, 255, 255, 0.2)'
              : 'rgba(0, 212, 255, 0.2)',
            letterSpacing: '0.02em',
          }}
          {...props}
        >
          {children}
        </code>
      )
    },
  }), [isUserMessage])

  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={markdownComponents}
    >
      {content}
    </ReactMarkdown>
  )
}, (prevProps, nextProps) => {
  // Only re-render if content changes
  return prevProps.content === nextProps.content && 
         prevProps.isUserMessage === nextProps.isUserMessage
})

MemoizedMarkdown.displayName = 'MemoizedMarkdown'