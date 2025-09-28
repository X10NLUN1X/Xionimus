import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Toaster } from 'sonner'
import { ChatProvider } from './context/ChatContext'
import { Layout } from './components/Layout'
import { ChatInterface } from './components/Chat/ChatInterface'
import { AgentManagement } from './components/Agents/AgentManagement'
import { FileManager } from './components/Files/FileManager'
import { SessionManager } from './components/Sessions/SessionManager'
import { Settings } from './components/Settings/Settings'

function App() {
  return (
    <ChatProvider>
      <Router>
        <div className="min-h-screen bg-background text-foreground">
          <Layout>
            <Routes>
              <Route path="/" element={<ChatInterface />} />
              <Route path="/agents" element={<AgentManagement />} />
              <Route path="/files" element={<FileManager />} />
              <Route path="/sessions" element={<SessionManager />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Layout>
          <Toaster
            theme="dark"
            position="top-right"
            toastOptions={{
              style: {
                background: 'rgb(30 41 59)',
                border: '1px solid rgb(245 158 11 / 0.2)',
                color: 'rgb(245 158 11)',
              },
            }}
          />
        </div>
      </Router>
    </ChatProvider>
  )
}

export default App