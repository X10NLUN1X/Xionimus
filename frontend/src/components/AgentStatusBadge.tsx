import React from 'react';
import { Box, Badge, Tooltip } from '@chakra-ui/react';

interface AgentStatusBadgeProps {
  isConnected: boolean;
  agentCount?: number;
}

export const AgentStatusBadge: React.FC<AgentStatusBadgeProps> = ({
  isConnected,
  agentCount = 0
}) => {
  return (
    <Tooltip
      label={isConnected ? `Agent verbunden (${agentCount})` : 'Agent nicht verbunden'}
      placement="bottom"
    >
      <Box>
        <Badge
          colorScheme={isConnected ? 'green' : 'gray'}
          variant="solid"
          fontSize="xs"
          px={2}
          py={1}
          borderRadius="md"
          display="flex"
          alignItems="center"
          gap={1}
        >
          <Box
            as="span"
            w={2}
            h={2}
            borderRadius="full"
            bg={isConnected ? 'green.300' : 'gray.400'}
            animation={isConnected ? 'pulse 2s infinite' : 'none'}
          />
          {isConnected ? '🟢 AGENT' : '⚫ AGENT'}
        </Badge>
      </Box>
    </Tooltip>
  );
};

export default AgentStatusBadge;
