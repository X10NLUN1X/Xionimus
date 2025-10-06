import React from 'react'
import {
  Box,
  Button,
  HStack,
  Text,
  Tooltip,
  useColorModeValue
} from '@chakra-ui/react'

interface DeveloperModeToggleProps {
  mode: 'junior' | 'senior'
  onChange: (mode: 'junior' | 'senior') => void
}

export const DeveloperModeToggle: React.FC<DeveloperModeToggleProps> = ({
  mode,
  onChange
}) => {
  const juniorBg = useColorModeValue('green.50', 'green.900')
  const juniorBorder = useColorModeValue('green.400', 'green.600')
  const seniorBg = useColorModeValue('blue.50', 'blue.900')
  const seniorBorder = useColorModeValue('blue.400', 'blue.600')

  return (
    <HStack spacing={2} align="center">
      <Tooltip
        label="🌱 Junior Developer: Fast & Budget-Friendly (Claude Haiku) - 73% cheaper, perfect for learning and simple tasks"
        placement="top"
      >
        <Button
          size="sm"
          variant={mode === 'junior' ? 'solid' : 'outline'}
          colorScheme="green"
          onClick={() => onChange('junior')}
          bg={mode === 'junior' ? juniorBg : 'transparent'}
          borderColor={juniorBorder}
          borderWidth={2}
          leftIcon={<Text>🌱</Text>}
          _hover={{
            bg: juniorBg,
            transform: 'scale(1.05)'
          }}
          transition="all 0.2s"
        >
          Junior
        </Button>
      </Tooltip>

      <Tooltip
        label="🚀 Senior Developer: Premium Quality (Claude Sonnet 4.5 + Opus 4.1) - Best for production code, complex debugging, and architecture"
        placement="top"
      >
        <Button
          size="sm"
          variant={mode === 'senior' ? 'solid' : 'outline'}
          colorScheme="blue"
          onClick={() => onChange('senior')}
          bg={mode === 'senior' ? seniorBg : 'transparent'}
          borderColor={seniorBorder}
          borderWidth={2}
          leftIcon={<Text>🚀</Text>}
          _hover={{
            bg: seniorBg,
            transform: 'scale(1.05)'
          }}
          transition="all 0.2s"
        >
          Senior
        </Button>
      </Tooltip>
    </HStack>
  )
}
