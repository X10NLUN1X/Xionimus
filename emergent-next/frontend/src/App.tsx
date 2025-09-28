import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Box, useColorModeValue } from '@chakra-ui/react'
import { Layout } from './components/Layout/Layout'
import { ChatPage } from './pages/ChatPage'
import { WorkspacePage } from './pages/WorkspacePage'
import { FilesPage } from './pages/FilesPage'
import { SettingsPage } from './pages/SettingsPage'
import { LoginPage } from './pages/LoginPage'

function App() {
  const bgColor = useColorModeValue('gray.50', 'gray.900')
  
  return (
    <Box minH="100vh" bg={bgColor}>
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/" element={<Layout />}>
          <Route index element={<ChatPage />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="workspace" element={<WorkspacePage />} />
          <Route path="files" element={<FilesPage />} />
          <Route path="settings" element={<SettingsPage />} />
        </Route>
      </Routes>
    </Box>
  )
}

export default App