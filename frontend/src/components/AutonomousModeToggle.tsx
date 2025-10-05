import React from 'react';
import {
  HStack,
  Switch,
  Text,
  Tooltip,
  Icon,
  Badge,
  useColorModeValue,
} from '@chakra-ui/react';
import { FiZap } from 'react-icons/fi';

interface AutonomousModeToggleProps {
  isEnabled: boolean;
  onChange: (enabled: boolean) => void;
}

const AutonomousModeToggle: React.FC<AutonomousModeToggleProps> = ({
  isEnabled,
  onChange,
}) => {
  const bgColor = useColorModeValue('blue.50', 'blue.900');
  const borderColor = useColorModeValue('blue.200', 'blue.700');
  
  return (
    <Tooltip
      label={
        isEnabled
          ? 'AI führt Aktionen direkt aus (Dateien schreiben, Befehle ausführen, etc.)'
          : 'AI schlägt nur Aktionen vor, führt sie aber nicht aus'
      }
      placement="top"
      hasArrow
    >
      <HStack
        spacing={3}
        p={2}
        px={3}
        bg={isEnabled ? bgColor : 'transparent'}
        borderRadius="md"
        borderWidth={isEnabled ? '1px' : '0'}
        borderColor={isEnabled ? borderColor : 'transparent'}
        transition="all 0.2s"
        cursor="pointer"
        onClick={() => onChange(!isEnabled)}
      >
        <Icon
          as={FiZap}
          color={isEnabled ? 'blue.500' : 'gray.400'}
          boxSize={4}
        />
        <Text fontSize="sm" fontWeight={isEnabled ? 'bold' : 'normal'}>
          Autonomer Modus
        </Text>
        {isEnabled && (
          <Badge colorScheme="blue" fontSize="xs">
            AKTIV
          </Badge>
        )}
        <Switch
          size="md"
          colorScheme="blue"
          isChecked={isEnabled}
          onChange={(e) => onChange(e.target.checked)}
        />
      </HStack>
    </Tooltip>
  );
};

export default AutonomousModeToggle;