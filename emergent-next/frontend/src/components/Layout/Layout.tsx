import React from 'react'
import {
  Box,
  Flex,
  VStack,
  HStack,
  IconButton,
  Text,
  useColorModeValue,
  useDisclosure,
  Drawer,
  DrawerBody,
  DrawerHeader,
  DrawerOverlay,
  DrawerContent,
  DrawerCloseButton,
  useBreakpointValue,
  Avatar,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  Badge
} from '@chakra-ui/react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import {
  HamburgerIcon,
  ChatIcon,
  SettingsIcon,
  AttachmentIcon,
  EditIcon,
  ChevronDownIcon
} from '@chakra-ui/icons'
import { useApp } from '../../contexts/AppContext'

const navigationItems = [
  { path: '/chat', label: 'AI Chat', icon: ChatIcon, badge: null },
  { path: '/workspace', label: 'Workspace', icon: EditIcon, badge: 'Beta' },
  { path: '/files', label: 'Files', icon: AttachmentIcon, badge: null },
  { path: '/settings', label: 'Settings', icon: SettingsIcon, badge: null },
]

export const Layout: React.FC = () => {
  const { isOpen, onOpen, onClose } = useDisclosure()
  const navigate = useNavigate()
  const location = useLocation()
  const { sessions, availableProviders } = useApp()
  
  const sidebarBg = useColorModeValue('#111111', '#000000')
  const sidebarBorder = useColorModeValue('#333333', '#444444')
  const activeBg = useColorModeValue('rgba(255, 179, 0, 0.15)', 'rgba(255, 179, 0, 0.2)')
  const activeColor = useColorModeValue('primary.500', 'primary.400')
  
  const isMobile = useBreakpointValue({ base: true, md: false })
  
  // Count configured providers
  const configuredProviders = Object.values(availableProviders).filter(Boolean).length
  
  const sidebarContent = (
    <VStack spacing={0} align="stretch" h="full">
      {/* Header */}
      <Box p={6} borderBottom="1px" borderColor={sidebarBorder}>
        <HStack spacing={3}>
          <Box
            w={10}
            h={10}
            bg="primary.500"
            rounded="lg"
            display="flex"
            alignItems="center"
            justifyContent="center"
            border="2px solid"
            borderColor="primary.600"
          >
            <Text color="#000000" fontWeight="bold" fontSize="lg">
              EN
            </Text>
          </Box>
          <VStack align="start" spacing={0}>
            <Text fontWeight="bold" fontSize="lg">
              Emergent-Next
            </Text>
            <Text fontSize="sm" color="gray.500">
              Development Platform
            </Text>
          </VStack>
        </HStack>
      </Box>
      
      {/* Navigation */}
      <VStack spacing={1} align="stretch" p={4} flex={1}>
        {navigationItems.map((item) => {
          const Icon = item.icon
          const isActive = location.pathname === item.path || 
                          (item.path === '/chat' && location.pathname === '/')
          
          return (
            <Box
              key={item.path}
              p={3}
              rounded="lg"
              bg={isActive ? activeBg : 'transparent'}
              color={isActive ? activeColor : 'inherit'}
              cursor="pointer"
              transition="all 0.2s"
              _hover={{
                bg: isActive ? activeBg : useColorModeValue('gray.50', 'gray.700')
              }}
              onClick={() => {
                navigate(item.path)
                if (isMobile) onClose()
              }}
            >
              <HStack spacing={3}>
                <Icon />
                <Text fontWeight={isActive ? 'semibold' : 'normal'}>
                  {item.label}
                </Text>
                {item.badge && (
                  <Badge size="sm" colorScheme="primary">
                    {item.badge}
                  </Badge>
                )}
              </HStack>
            </Box>
          )
        })}
      </VStack>
      
      {/* Footer */}
      <Box p={4} borderTop="1px" borderColor={sidebarBorder}>
        <Menu>
          <MenuButton
            as={Box}
            cursor="pointer"
            p={3}
            rounded="lg"
            _hover={{ bg: useColorModeValue('gray.50', 'gray.700') }}
            transition="all 0.2s"
          >
            <HStack spacing={3}>
              <Avatar size="sm" name="Demo User" />
              <VStack align="start" spacing={0} flex={1}>
                <Text fontSize="sm" fontWeight="medium">
                  Demo User
                </Text>
                <HStack spacing={1}>
                  <Text fontSize="xs" color="gray.500">
                    {configuredProviders}/3 AI providers
                  </Text>
                  <Box
                    w={2}
                    h={2}
                    rounded="full"
                    bg={configuredProviders > 0 ? 'green.400' : 'gray.400'}
                  />
                </HStack>
              </VStack>
              <ChevronDownIcon />
            </HStack>
          </MenuButton>
          <MenuList>
            <MenuItem onClick={() => navigate('/settings')}>
              <SettingsIcon mr={3} />
              Settings
            </MenuItem>
          </MenuList>
        </Menu>
      </Box>
    </VStack>
  )

  return (
    <Flex h="100vh">
      {/* Desktop Sidebar */}
      {!isMobile && (
        <Box
          w={72}
          bg={sidebarBg}
          borderRight="1px"
          borderColor={sidebarBorder}
          flexShrink={0}
        >
          {sidebarContent}
        </Box>
      )}
      
      {/* Mobile Drawer */}
      <Drawer isOpen={isOpen} placement="left" onClose={onClose}>
        <DrawerOverlay />
        <DrawerContent bg={sidebarBg}>
          <DrawerCloseButton />
          <DrawerHeader borderBottomWidth="1px">
            Emergent-Next
          </DrawerHeader>
          <DrawerBody p={0}>
            {sidebarContent}
          </DrawerBody>
        </DrawerContent>
      </Drawer>
      
      {/* Main Content */}
      <Flex direction="column" flex={1} overflow="hidden">
        {/* Mobile Header */}
        {isMobile && (
          <Flex
            as="header"
            align="center"
            justify="space-between"
            p={4}
            bg={sidebarBg}
            borderBottom="1px"
            borderColor={sidebarBorder}
          >
            <IconButton
              aria-label="Open menu"
              icon={<HamburgerIcon />}
              variant="ghost"
              onClick={onOpen}
            />
            <Text fontWeight="bold" fontSize="lg">
              Emergent-Next
            </Text>
            <Box w={10} /> {/* Spacer */}
          </Flex>
        )}
        
        {/* Content */}
        <Box flex={1} overflow="auto">
          <Outlet />
        </Box>
      </Flex>
    </Flex>
  )
}