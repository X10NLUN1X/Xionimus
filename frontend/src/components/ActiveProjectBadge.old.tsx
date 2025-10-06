import React, { useState, useEffect } from 'react'
import {
  Box,
  HStack,
  Badge,
  Text,
  Menu,
  MenuButton,
  MenuList,
  MenuItem,
  IconButton,
  Spinner,
  useToast,
  Tooltip
} from '@chakra-ui/react'
import { ChevronDownIcon, CloseIcon } from '@chakra-ui/icons'
import axios from 'axios'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8001'

interface ActiveProjectInfo {
  project_name: string | null
  project_path: string | null
  branch: string | null
  file_count: number | null
  size_mb: number | null
  exists: boolean
}

interface ActiveProjectBadgeProps {
  sessionId: string | null
}

export const ActiveProjectBadge: React.FC<ActiveProjectBadgeProps> = ({ sessionId }) => {
  const [activeProject, setActiveProject] = useState<ActiveProjectInfo | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [availableProjects, setAvailableProjects] = useState<string[]>([])
  const toast = useToast()

  // Load active project when session changes
  useEffect(() => {
    if (sessionId) {
      loadActiveProject()
    } else {
      setActiveProject(null)
    }
  }, [sessionId])

  const loadActiveProject = async () => {
    if (!sessionId) return
    
    setIsLoading(true)
    try {
      const token = localStorage.getItem('xionimus_token')
      const response = await axios.get(
        `${BACKEND_URL}/api/workspace/active-project/${sessionId}`,
        {
          headers: token ? {
            'Authorization': `Bearer ${token}`
          } : {}
        }
      )
      
      if (response.data && response.data.exists) {
        setActiveProject(response.data)
      } else {
        setActiveProject(null)
      }
    } catch (error: any) {
      console.error('Failed to load active project:', error)
      setActiveProject(null)
    } finally {
      setIsLoading(false)
    }
  }

  const loadAvailableProjects = async () => {
    try {
      const token = localStorage.getItem('xionimus_token')
      const response = await axios.get(
        `${BACKEND_URL}/api/github/import/status`,
        {
          headers: token ? {
            'Authorization': `Bearer ${token}`
          } : {}
        }
      )
      
      const projects = response.data.existing_projects || []
      setAvailableProjects(projects.map((p: any) => p.name))
    } catch (error) {
      console.error('Failed to load available projects:', error)
    }
  }

  const setActiveProjectForSession = async (projectName: string, branch: string | null = null) => {
    if (!sessionId) return
    
    try {
      const token = localStorage.getItem('xionimus_token')
      const response = await axios.post(
        `${BACKEND_URL}/api/workspace/active-project`,
        {
          session_id: sessionId,
          project_name: projectName,
          branch: branch
        },
        {
          headers: token ? {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          } : {
            'Content-Type': 'application/json'
          }
        }
      )
      
      toast({
        title: '✅ Projekt aktiviert',
        description: response.data.message,
        status: 'success',
        duration: 3000
      })
      
      await loadActiveProject()
    } catch (error: any) {
      console.error('Failed to set active project:', error)
      toast({
        title: 'Fehler',
        description: error.response?.data?.detail || 'Projekt konnte nicht aktiviert werden',
        status: 'error',
        duration: 5000
      })
    }
  }

  const clearActiveProject = async () => {
    if (!sessionId) return
    
    try {
      const token = localStorage.getItem('xionimus_token')
      await axios.delete(
        `${BACKEND_URL}/api/workspace/active-project/${sessionId}`,
        {
          headers: token ? {
            'Authorization': `Bearer ${token}`
          } : {}
        }
      )
      
      setActiveProject(null)
      
      toast({
        title: 'Projekt entfernt',
        description: 'Kein aktives Projekt mehr gesetzt',
        status: 'info',
        duration: 3000
      })
    } catch (error: any) {
      console.error('Failed to clear active project:', error)
      toast({
        title: 'Fehler',
        description: 'Projekt konnte nicht entfernt werden',
        status: 'error',
        duration: 3000
      })
    }
  }

  if (isLoading) {
    return (
      <HStack spacing={2} px={3} py={1} bg="gray.100" borderRadius="md">
        <Spinner size="xs" />
        <Text fontSize="xs" color="gray.600">Lade...</Text>
      </HStack>
    )
  }

  if (!activeProject || !activeProject.exists) {
    return (
      <Menu onOpen={loadAvailableProjects}>
        <MenuButton
          as={Box}
          cursor="pointer"
          px={3}
          py={1}
          bg="gray.100"
          borderRadius="md"
          _hover={{ bg: 'gray.200' }}
        >
          <HStack spacing={2}>
            <Text fontSize="xs" color="gray.600" fontWeight="medium">
              📂 Kein Projekt aktiv
            </Text>
            <ChevronDownIcon color="gray.600" />
          </HStack>
        </MenuButton>
        <MenuList maxH="300px" overflowY="auto">
          {availableProjects.length === 0 ? (
            <MenuItem isDisabled>
              <Text fontSize="sm" color="gray.500">Keine Projekte verfügbar</Text>
            </MenuItem>
          ) : (
            availableProjects.map((projectName) => (
              <MenuItem
                key={projectName}
                onClick={() => setActiveProjectForSession(projectName)}
                fontSize="sm"
              >
                📁 {projectName}
              </MenuItem>
            ))
          )}
        </MenuList>
      </Menu>
    )
  }

  return (
    <Menu onOpen={loadAvailableProjects}>
      <Tooltip 
        label={`${activeProject.file_count} Dateien • ${activeProject.size_mb} MB`}
        placement="bottom"
      >
        <MenuButton
          as={Box}
          cursor="pointer"
          px={3}
          py={1.5}
          bg="purple.50"
          borderRadius="md"
          borderWidth="1px"
          borderColor="purple.200"
          _hover={{ bg: 'purple.100', borderColor: 'purple.300' }}
        >
          <HStack spacing={2}>
            <Text fontSize="xs" fontWeight="bold" color="purple.700">
              📁 {activeProject.project_name}
            </Text>
            {activeProject.branch && (
              <Badge colorScheme="green" fontSize="xs">
                {activeProject.branch}
              </Badge>
            )}
            <ChevronDownIcon color="purple.600" />
          </HStack>
        </MenuButton>
      </Tooltip>
      <MenuList>
        <Box px={3} py={2} borderBottomWidth="1px">
          <Text fontSize="xs" fontWeight="semibold" color="gray.700">
            Aktives Projekt
          </Text>
          <Text fontSize="xs" color="gray.500" mt={1}>
            {activeProject.file_count} Dateien • {activeProject.size_mb} MB
          </Text>
        </Box>
        
        <MenuItem
          icon={<CloseIcon boxSize={3} />}
          onClick={clearActiveProject}
          fontSize="sm"
          color="red.600"
        >
          Projekt entfernen
        </MenuItem>
        
        {availableProjects.length > 0 && (
          <>
            <Box px={3} py={2} borderTopWidth="1px" borderBottomWidth="1px">
              <Text fontSize="xs" fontWeight="semibold" color="gray.700">
                Wechseln zu:
              </Text>
            </Box>
            {availableProjects
              .filter(p => p !== activeProject.project_name)
              .map((projectName) => (
                <MenuItem
                  key={projectName}
                  onClick={() => setActiveProjectForSession(projectName)}
                  fontSize="sm"
                >
                  📁 {projectName}
                </MenuItem>
              ))}
          </>
        )}
      </MenuList>
    </Menu>
  )
}
