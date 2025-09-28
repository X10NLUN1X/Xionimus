import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  MessageSquare, 
  Bot, 
  FileText, 
  FolderOpen, 
  Settings, 
  Zap,
  Menu,
  X
} from 'lucide-react'
import { Button } from './ui/Button'
import { cn } from '@/lib/utils'

interface LayoutProps {
  children: React.ReactNode
}

const navigationItems = [
  { path: '/', label: 'Chat', icon: MessageSquare },
  { path: '/agents', label: 'Agents', icon: Bot },
  { path: '/files', label: 'Files', icon: FileText },
  { path: '/sessions', label: 'Sessions', icon: FolderOpen },
  { path: '/settings', label: 'Settings', icon: Settings },
]

export const Layout: React.FC<LayoutProps> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = React.useState(false)
  const location = useLocation()

  return (
    <div className="flex h-screen bg-background">
      {/* Sidebar */}
      <div className={cn(
        "fixed inset-y-0 left-0 z-50 w-64 bg-secondary border-r border-primary/20 transition-transform duration-300 ease-in-out lg:translate-x-0 lg:static lg:inset-0",
        sidebarOpen ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between p-6 border-b border-primary/20">
            <div className="flex items-center space-x-2">
              <Zap className="h-8 w-8 text-primary" />
              <span className="text-xl font-bold text-primary">XIONIMUS AI</span>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
          
          {/* Navigation */}
          <nav className="flex-1 p-4">
            <ul className="space-y-2">
              {navigationItems.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.path
                
                return (
                  <li key={item.path}>
                    <Link
                      to={item.path}
                      className={cn(
                        "flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors duration-200",
                        isActive
                          ? "bg-primary/10 text-primary border border-primary/20"
                          : "text-muted-foreground hover:text-primary hover:bg-primary/5"
                      )}
                      onClick={() => setSidebarOpen(false)}
                    >
                      <Icon className="h-5 w-5" />
                      <span className="font-medium">{item.label}</span>
                    </Link>
                  </li>
                )
              })}
            </ul>
          </nav>
          
          {/* Footer */}
          <div className="p-4 border-t border-primary/20">
            <div className="text-xs text-muted-foreground text-center">
              XIONIMUS AI v3.0.0
            </div>
          </div>
        </div>
      </div>
      
      {/* Overlay */}
      {sidebarOpen && (
        <div 
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      
      {/* Main content */}
      <div className="flex-1 flex flex-col lg:ml-0">
        {/* Header */}
        <header className="flex items-center justify-between p-4 border-b border-primary/20 lg:hidden">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu className="h-5 w-5" />
          </Button>
          <div className="flex items-center space-x-2">
            <Zap className="h-6 w-6 text-primary" />
            <span className="font-bold text-primary">XIONIMUS AI</span>
          </div>
        </header>
        
        {/* Content */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  )
}