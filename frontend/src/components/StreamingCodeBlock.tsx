import React, { useEffect, useState } from 'react';
import { Box, Text, HStack, IconButton, useClipboard, useColorModeValue, Badge, VStack } from '@chakra-ui/react';
import { CopyIcon, CheckIcon } from '@chakra-ui/icons';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus, vs } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface StreamingCodeBlockProps {
  code: string;
  language?: string;
  isStreaming?: boolean;
  fileName?: string;
}

export const StreamingCodeBlock: React.FC<StreamingCodeBlockProps> = ({
  code,
  language = 'javascript',
  isStreaming = false,
  fileName
}) => {
  const { hasCopied, onCopy } = useClipboard(code);
  const [displayedCode, setDisplayedCode] = useState('');
  const [lineCount, setLineCount] = useState(0);
  
  const bgColor = useColorModeValue('gray.50', 'gray.900');
  const borderColor = useColorModeValue('gray.200', 'gray.700');
  const headerBg = useColorModeValue('gray.100', 'gray.800');
  const theme = useColorModeValue(vs, vscDarkPlus);

  // Simulate typing effect for streaming
  useEffect(() => {
    if (isStreaming && code.length > displayedCode.length) {
      const timer = setTimeout(() => {
        setDisplayedCode(code.slice(0, displayedCode.length + 5)); // Add 5 chars at a time
      }, 10);
      return () => clearTimeout(timer);
    } else {
      setDisplayedCode(code);
    }
  }, [code, displayedCode.length, isStreaming]);

  useEffect(() => {
    setLineCount(displayedCode.split('\n').length);
  }, [displayedCode]);

  return (
    <Box
      borderRadius="md"
      overflow="hidden"
      border="1px solid"
      borderColor={borderColor}
      my={3}
      boxShadow="sm"
    >
      {/* Header */}
      <HStack
        bg={headerBg}
        px={4}
        py={2}
        justify="space-between"
        borderBottom="1px solid"
        borderColor={borderColor}
      >
        <HStack spacing={3}>
          {fileName && (
            <Text fontSize="sm" fontWeight="600" color="blue.500">
              {fileName}
            </Text>
          )}
          <Badge colorScheme="purple" fontSize="xs">
            {language}
          </Badge>
          {isStreaming && (
            <Badge colorScheme="green" fontSize="xs" animation="pulse 2s infinite">
              ⚡ Streaming...
            </Badge>
          )}
          <Text fontSize="xs" color="gray.500">
            {lineCount} {lineCount === 1 ? 'line' : 'lines'}
          </Text>
        </HStack>
        <IconButton
          aria-label="Copy code"
          icon={hasCopied ? <CheckIcon /> : <CopyIcon />}
          size="sm"
          variant="ghost"
          onClick={onCopy}
          colorScheme={hasCopied ? 'green' : 'gray'}
        />
      </HStack>

      {/* Code Content */}
      <Box
        bg={bgColor}
        maxH="500px"
        overflowY="auto"
        position="relative"
      >
        <SyntaxHighlighter
          language={language}
          style={theme}
          showLineNumbers
          wrapLines
          customStyle={{
            margin: 0,
            padding: '1rem',
            background: 'transparent',
            fontSize: '14px',
            lineHeight: '1.6'
          }}
        >
          {displayedCode}
        </SyntaxHighlighter>
        
        {isStreaming && displayedCode.length < code.length && (
          <Box
            position="absolute"
            bottom={2}
            right={2}
            bg="blue.500"
            color="white"
            px={2}
            py={1}
            borderRadius="md"
            fontSize="xs"
            fontWeight="600"
          >
            Generating...
          </Box>
        )}
      </Box>
    </Box>
  );
};

// Component to extract and display code blocks from streaming markdown
export const StreamingMarkdownRenderer: React.FC<{ content: string; isStreaming?: boolean }> = ({
  content,
  isStreaming = false
}) => {
  const [codeBlocks, setCodeBlocks] = useState<Array<{ language: string; code: string; fileName?: string }>>([]);
  const [textParts, setTextParts] = useState<string[]>([]);

  useEffect(() => {
    // Parse markdown for code blocks
    const codeBlockRegex = /```(\w+)?\s*(?:\[(.+?)\])?\n([\s\S]*?)```/g;
    const blocks: Array<{ language: string; code: string; fileName?: string }> = [];
    const parts: string[] = [];
    
    let lastIndex = 0;
    let match;

    while ((match = codeBlockRegex.exec(content)) !== null) {
      // Add text before code block
      if (match.index > lastIndex) {
        parts.push(content.slice(lastIndex, match.index));
      }

      // Extract code block
      blocks.push({
        language: match[1] || 'plaintext',
        fileName: match[2],
        code: match[3].trim()
      });
      
      parts.push(''); // Placeholder for code block
      lastIndex = codeBlockRegex.lastIndex;
    }

    // Add remaining text
    if (lastIndex < content.length) {
      parts.push(content.slice(lastIndex));
    }

    setCodeBlocks(blocks);
    setTextParts(parts);
  }, [content]);

  return (
    <VStack align="stretch" spacing={2}>
      {textParts.map((text, index) => (
        <React.Fragment key={index}>
          {text && (
            <Text whiteSpace="pre-wrap" fontSize="15px" lineHeight="1.7">
              {text}
            </Text>
          )}
          {codeBlocks[index] && (
            <StreamingCodeBlock
              language={codeBlocks[index].language}
              code={codeBlocks[index].code}
              fileName={codeBlocks[index].fileName}
              isStreaming={isStreaming && index === codeBlocks.length - 1}
            />
          )}
        </React.Fragment>
      ))}
    </VStack>
  );
};
