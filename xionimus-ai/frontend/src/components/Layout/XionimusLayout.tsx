import React, { useState } from 'react'
import {
  Box,
  Flex,
  VStack,
  HStack,
  IconButton,
  Text,
  useColorMode,
  useColorModeValue,
  useDisclosure,
  Drawer,
  DrawerBody,
  DrawerOverlay,
  DrawerContent,
  useBreakpointValue,
  Avatar,
  Button,
  Divider,
  Tooltip,
  Badge,
  Switch,
  FormControl,
  FormLabel
} from '@chakra-ui/react'
import { Outlet, useNavigate, useLocation } from 'react-router-dom'
import {
  HamburgerIcon,
  ChatIcon,
  SettingsIcon,
  AttachmentIcon,
  EditIcon,
  SunIcon,
  MoonIcon,
  AddIcon,
  ExternalLinkIcon
} from '@chakra-ui/icons'
import { useApp } from '../../contexts/AppContext'

const navigationItems = [
  { 
    path: '/chat', 
    label: 'Chat', 
    icon: ChatIcon, 
    badge: null,
    description: 'Code-Assistent' 
  },
  { 
    path: '/settings', 
    label: 'Einstellungen', 
    icon: SettingsIcon, 
    badge: null,
    description: 'Konfiguration' 
  },
]

export const XionimusLayout: React.FC = () => {
  const { isOpen, onOpen, onClose } = useDisclosure()
  const { colorMode, toggleColorMode } = useColorMode()
  const navigate = useNavigate()
  const location = useLocation()
  const { sessions, availableProviders, createNewSession } = useApp()
  
  const isMobile = useBreakpointValue({ base: true, lg: false })
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  
  // Luxury Black & Gold Theme Colors
  const sidebarBg = useColorModeValue('rgba(10, 10, 10, 0.98)', 'rgba(0, 0, 0, 0.98)')
  const sidebarBorder = useColorModeValue('rgba(255, 215, 0, 0.2)', 'rgba(255, 215, 0, 0.3)')
  const activeBg = useColorModeValue('linear-gradient(135deg, rgba(255, 215, 0, 0.15), rgba(255, 165, 0, 0.1))', 'linear-gradient(135deg, rgba(255, 215, 0, 0.2), rgba(255, 165, 0, 0.15))')
  const activeColor = useColorModeValue('#FFD700', '#FFA500')
  const hoverBg = useColorModeValue('rgba(255, 215, 0, 0.08)', 'rgba(255, 215, 0, 0.12)')
  const mainBg = useColorModeValue('#0A0A0A', '#000000')
  const contentBg = useColorModeValue('rgba(17, 17, 17, 0.95)', 'rgba(17, 17, 17, 0.95)')
  
  const isActive = (path: string) => location.pathname === path
  
  const handleNewChat = () => {
    createNewSession()
    if (location.pathname !== '/chat') {
      navigate('/chat')
    }
  }

  const SidebarContent = () => (
    <VStack spacing={0} align="stretch" h="100%">
      {/* Header */}
      <Box p={6} borderBottom="1px solid" borderColor={sidebarBorder}>
        <HStack spacing={3} justify={sidebarCollapsed ? 'center' : 'flex-start'}>
          {/* Logo */}
          <Box
            w={sidebarCollapsed ? "32px" : "40px"}
            h={sidebarCollapsed ? "32px" : "40px"}
            bg="linear-gradient(135deg, #FFD700, #FFA500)"
            borderRadius="lg"
            display="flex"
            alignItems="center"
            justifyContent="center"
            border="2px solid"
            borderColor="#B8860B"
            boxShadow="0 4px 20px rgba(255, 215, 0, 0.3)"
            position="relative"
            _before={{
              content: '""',
              position: 'absolute',
              inset: '-2px',
              borderRadius: 'lg',
              background: 'linear-gradient(135deg, #FFD700, #FFA500)',
              zIndex: -1,
              filter: 'blur(4px)',
              opacity: 0.7,
            }}
          >
            <Text 
              color="#000" 
              fontWeight="900" 
              fontSize={sidebarCollapsed ? "sm" : "md"}
              fontFamily="'Inter', sans-serif"
              letterSpacing="-0.5px"
            >
              X
            </Text>
          </Box>

          {/* Brand Name */}
          {!sidebarCollapsed && (
            <VStack align="start" spacing={0}>
              <Text 
                fontWeight="800" 
                fontSize="lg" 
                color="#FFD700"
                fontFamily="'Inter', sans-serif"
                letterSpacing="-0.5px"
              >
                Xionimus AI
              </Text>
              <Text 
                fontSize="xs" 
                color="rgba(255, 215, 0, 0.7)"
                fontFamily="'Inter', sans-serif"
                letterSpacing="0.5px"
                textTransform="uppercase"
              >
                Code-Spezialist
              </Text>
            </VStack>
          )}
        </HStack>

        {/* New Chat Button */}
        {!sidebarCollapsed && (
          <Button
            mt={4}
            w="100%"
            size="sm"
            bg="linear-gradient(135deg, #FFD700, #FFA500)"
            color="#000"
            fontWeight="600"
            leftIcon={<AddIcon />}
            onClick={handleNewChat}
            _hover={{
              bg: "linear-gradient(135deg, #FFA500, #FFD700)",
              transform: "translateY(-1px)",
              boxShadow: "0 6px 25px rgba(255, 215, 0, 0.4)"
            }}
            _active={{
              transform: "translateY(0)"
            }}
            transition="all 0.2s ease"
            borderRadius="md"
          >
            New Chat
          </Button>
        )}
      </Box>

      {/* Navigation */}
      <VStack spacing={1} align="stretch" p={3} flex={1}>
        {navigationItems.map((item) => {
          const isCurrentActive = isActive(item.path)
          
          return (
            <Tooltip
              key={item.path}
              label={sidebarCollapsed ? item.label : ''}
              placement="right"
              isDisabled={!sidebarCollapsed}
            >
              <Button
                variant="ghost"
                justifyContent={sidebarCollapsed ? 'center' : 'flex-start'}
                leftIcon={sidebarCollapsed ? undefined : <item.icon />}
                onClick={() => navigate(item.path)}
                bg={isCurrentActive ? activeBg : 'transparent'}
                color={isCurrentActive ? activeColor : 'rgba(255, 255, 255, 0.8)'}
                _hover={{
                  bg: isCurrentActive ? activeBg : hoverBg,
                  color: isCurrentActive ? activeColor : '#FFD700',
                  transform: 'translateX(4px)'
                }}
                _active={{
                  transform: isCurrentActive ? 'translateX(4px)' : 'translateX(2px)'
                }}
                transition="all 0.2s ease"
                borderRadius="lg"
                h="48px"
                fontWeight="500"
                fontSize="sm"
                position="relative"
                border={isCurrentActive ? '1px solid rgba(255, 215, 0, 0.3)' : '1px solid transparent'}
              >
                {sidebarCollapsed ? (
                  <item.icon />
                ) : (
                  <HStack justify="space-between" w="100%">
                    <HStack spacing={3}>
                      <item.icon />
                      <Text>{item.label}</Text>
                    </HStack>
                    {item.badge && (
                      <Badge 
                        size="sm" 
                        bg="linear-gradient(135deg, #FFD700, #FFA500)"
                        color="#000"
                        fontWeight="600"
                      >
                        {item.badge}
                      </Badge>
                    )}
                  </HStack>
                )}
                
                {/* Active indicator */}
                {isCurrentActive && (
                  <Box
                    position="absolute"
                    left="0"
                    top="50%"
                    transform="translateY(-50%)"
                    w="3px"
                    h="24px"
                    bg="linear-gradient(135deg, #FFD700, #FFA500)"
                    borderRadius="0 2px 2px 0"
                    boxShadow="0 0 10px rgba(255, 215, 0, 0.5)"
                  />
                )}
              </Button>
            </Tooltip>
          )
        })}
      </VStack>

      {/* Footer */}
      <Box p={3} borderTop="1px solid" borderColor={sidebarBorder}>
        {/* Theme Toggle - Always Visible */}
        <FormControl display="flex" alignItems="center" mb={3}>
          {sidebarCollapsed ? (
            <Tooltip label={colorMode === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'} placement="right">
              <IconButton
                aria-label="Toggle theme"
                icon={colorMode === 'dark' ? <SunIcon /> : <MoonIcon />}
                variant="ghost"
                size="sm"
                color="rgba(255, 215, 0, 0.8)"
                _hover={{ 
                  bg: hoverBg,
                  color: '#FFD700'
                }}
                onClick={toggleColorMode}
                w="100%"
              />
            </Tooltip>
          ) : (
            <HStack spacing={2} w="100%" justify="space-between">
              <HStack spacing={2}>
                <SunIcon color="rgba(255, 215, 0, 0.7)" />
                <Switch
                  colorScheme="yellow"
                  size="sm"
                  isChecked={colorMode === 'dark'}
                  onChange={toggleColorMode}
                />
                <MoonIcon color="rgba(255, 215, 0, 0.7)" />
              </HStack>
              <Text fontSize="xs" color="rgba(255, 215, 0, 0.7)">
                {colorMode === 'dark' ? 'Dark' : 'Light'}
              </Text>
            </HStack>
          )}
        </FormControl>

        {/* Collapse Toggle */}
        <Tooltip label={sidebarCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'} placement="right">
          <IconButton
            aria-label="Toggle sidebar"
            icon={<HamburgerIcon />}
            variant="ghost"
            size="sm"
            color="rgba(255, 215, 0, 0.8)"
            _hover={{ 
              bg: hoverBg,
              color: '#FFD700'
            }}
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            w="100%"
          />
        </Tooltip>

        {/* Status Indicator */}
        {!sidebarCollapsed && (
          <HStack spacing={2} mt={3} justify="center">
            <Box
              w="8px"
              h="8px"
              borderRadius="50%"
              bg="#00FF87"
              boxShadow="0 0 8px #00FF87"
            />
            <Text fontSize="xs" color="rgba(255, 255, 255, 0.6)">
              Online
            </Text>
          </HStack>
        )}
      </Box>
    </VStack>
  )

  return (
    <Box minH="100vh" bg={mainBg}>
      <Flex>
        {/* Desktop Sidebar */}
        {!isMobile && (
          <Box
            w={sidebarCollapsed ? "80px" : "280px"}
            h="100vh"
            bg={sidebarBg}
            borderRight="1px solid"
            borderColor={sidebarBorder}
            position="fixed"
            left={0}
            top={0}
            zIndex={100}
            transition="width 0.3s ease"
            backdropFilter="blur(20px)"
            boxShadow="4px 0 20px rgba(0, 0, 0, 0.5)"
          >
            <SidebarContent />
          </Box>
        )}

        {/* Mobile Drawer */}
        <Drawer isOpen={isOpen} placement="left" onClose={onClose}>
          <DrawerOverlay bg="rgba(0, 0, 0, 0.8)" />
          <DrawerContent 
            bg={sidebarBg} 
            borderRight="1px solid" 
            borderColor={sidebarBorder}
            maxW="280px"
          >
            <DrawerBody p={0}>
              <SidebarContent />
            </DrawerBody>
          </DrawerContent>
        </Drawer>

        {/* Main Content */}
        <Box
          flex={1}
          ml={isMobile ? 0 : sidebarCollapsed ? "80px" : "280px"}
          transition="margin-left 0.3s ease"
          minH="100vh"
        >
          {/* Mobile Header */}
          {isMobile && (
            <Flex
              h="60px"
              bg={sidebarBg}
              borderBottom="1px solid"
              borderColor={sidebarBorder}
              align="center"
              px={4}
              position="sticky"
              top={0}
              zIndex={50}
              backdropFilter="blur(20px)"
              justify="space-between"
            >
              <HStack>
                <IconButton
                  aria-label="Open menu"
                  icon={<HamburgerIcon />}
                  variant="ghost"
                  color="#FFD700"
                  onClick={onOpen}
                  _hover={{ bg: hoverBg }}
                />
                <Text
                  ml={4}
                  fontWeight="800"
                  fontSize="lg"
                  color="#FFD700"
                  fontFamily="'Inter', sans-serif"
                >
                  Xionimus AI
                </Text>
              </HStack>
              
              {/* Mobile Theme Toggle */}
              <Tooltip label={colorMode === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}>
                <IconButton
                  aria-label="Toggle theme"
                  icon={colorMode === 'dark' ? <SunIcon /> : <MoonIcon />}
                  variant="ghost"
                  size="sm"
                  color="rgba(255, 215, 0, 0.8)"
                  _hover={{ 
                    bg: hoverBg,
                    color: '#FFD700'
                  }}
                  onClick={toggleColorMode}
                />
              </Tooltip>
            </Flex>
          )}

          {/* Page Content */}
          <Box
            bg={contentBg}
            minH={isMobile ? "calc(100vh - 60px)" : "100vh"}
            backdropFilter="blur(10px)"
            position="relative"
            _before={{
              content: '""',
              position: 'absolute',
              inset: 0,
              background: 'radial-gradient(ellipse at top right, rgba(255, 215, 0, 0.03), transparent 50%), radial-gradient(ellipse at bottom left, rgba(255, 165, 0, 0.02), transparent 50%)',
              pointerEvents: 'none'
            }}
          >
            <Box position="relative" zIndex={1}>
              <Outlet />
            </Box>
          </Box>
        </Box>
      </Flex>
    </Box>
  )
}