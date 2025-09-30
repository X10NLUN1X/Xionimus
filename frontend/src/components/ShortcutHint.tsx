import React from 'react'
import { HStack, Text, Kbd, Tooltip, useColorModeValue } from '@chakra-ui/react'
import { getModifierKey } from '../hooks/useKeyboardShortcuts'

interface ShortcutHintProps {
  keys: string[]
  description: string
}

export const ShortcutHint: React.FC<ShortcutHintProps> = ({ keys, description }) => {
  const kbdBg = useColorModeValue('gray.100', 'whiteAlpha.200')
  
  return (
    <Tooltip label={description} placement="top" hasArrow>
      <HStack spacing={1} fontSize="xs">
        {keys.map((key, idx) => (
          <React.Fragment key={idx}>
            <Kbd bg={kbdBg} fontSize="xs">
              {key === 'mod' ? getModifierKey() : key}
            </Kbd>
            {idx < keys.length - 1 && <Text color="gray.500">+</Text>}
          </React.Fragment>
        ))}
      </HStack>
    </Tooltip>
  )
}
