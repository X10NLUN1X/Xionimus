import React from 'react'
import { Badge, Tooltip } from '@chakra-ui/react'
import { MoonIcon } from '@chakra-ui/icons'

/**
 * Simplified Theme Indicator - Dark Mode Only
 * This component now just shows that dark mode is active
 * Light mode and theme switching have been removed
 */
export const ThemeSelector: React.FC = () => {
  return (
    <Tooltip label="Dark Mode (immer aktiv)" placement="bottom">
      <Badge
        colorScheme="purple"
        variant="subtle"
        px={2}
        py={1}
        borderRadius="md"
        fontSize="xs"
        display="flex"
        alignItems="center"
        gap={1}
      >
        <MoonIcon boxSize={3} />
        Dark
      </Badge>
    </Tooltip>
  )
}
