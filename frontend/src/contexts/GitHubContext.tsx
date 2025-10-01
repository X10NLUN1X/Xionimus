import React, { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

interface GitHubUser {
  login: string
  name: string
  avatar_url: string
}

interface GitHubRepository {
  id: number
  name: string
  full_name: string
  private: boolean
  description: string
}

interface GitHubBranch {
  name: string
  commit: {
    sha: string
  }
}

interface GitHubContextType {
  isConnected: boolean
  user: GitHubUser | null
  accessToken: string | null
  repositories: GitHubRepository[]
  branches: GitHubBranch[]
  selectedRepo: string | null
  selectedBranch: string
  connectGitHub: () => Promise<void>
  disconnectGitHub: () => void
  fetchRepositories: () => Promise<void>
  fetchBranches: (owner: string, repo: string) => Promise<void>
  setSelectedRepo: (repo: string) => void
  setSelectedBranch: (branch: string) => void
  pushToGitHub: (files: Array<{path: string, content: string}>, commitMessage: string) => Promise<any>
  createRepository: (name: string, description: string, isPrivate: boolean) => Promise<any>
}

const GitHubContext = createContext<GitHubContextType | undefined>(undefined)

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'

export const GitHubProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [accessToken, setAccessToken] = useState<string | null>(
    localStorage.getItem('github_access_token')
  )
  const [user, setUser] = useState<GitHubUser | null>(
    JSON.parse(localStorage.getItem('github_user') || 'null')
  )
  const [repositories, setRepositories] = useState<GitHubRepository[]>([])
  const [branches, setBranches] = useState<GitHubBranch[]>([])
  const [selectedRepo, setSelectedRepo] = useState<string | null>(
    localStorage.getItem('github_selected_repo')
  )
  const [selectedBranch, setSelectedBranch] = useState<string>(
    localStorage.getItem('github_selected_branch') || 'main'
  )

  const isConnected = !!accessToken && !!user

  // Save to localStorage when state changes
  useEffect(() => {
    if (accessToken) {
      localStorage.setItem('github_access_token', accessToken)
    } else {
      localStorage.removeItem('github_access_token')
    }
  }, [accessToken])

  useEffect(() => {
    if (user) {
      localStorage.setItem('github_user', JSON.stringify(user))
    } else {
      localStorage.removeItem('github_user')
    }
  }, [user])

  useEffect(() => {
    if (selectedRepo) {
      localStorage.setItem('github_selected_repo', selectedRepo)
    }
  }, [selectedRepo])

  useEffect(() => {
    localStorage.setItem('github_selected_branch', selectedBranch)
  }, [selectedBranch])

  const connectGitHub = async () => {
    try {
      // Get OAuth URL from backend
      const response = await axios.get(`${BACKEND_URL}/api/github/oauth/url`)
      const { oauth_url } = response.data
      
      // Redirect to GitHub OAuth
      window.location.href = oauth_url
    } catch (error: any) {
      console.error('Failed to get GitHub OAuth URL:', error)
      
      // Show user-friendly error message for configuration issues
      if (error.response?.status === 400) {
        const errorMsg = error.response?.data?.detail || 'GitHub OAuth ist nicht konfiguriert'
        throw new Error(errorMsg)
      }
      
      throw error
    }
  }

  const disconnectGitHub = () => {
    setAccessToken(null)
    setUser(null)
    setRepositories([])
    setBranches([])
    setSelectedRepo(null)
    setSelectedBranch('main')
    localStorage.removeItem('github_access_token')
    localStorage.removeItem('github_user')
    localStorage.removeItem('github_selected_repo')
    localStorage.removeItem('github_selected_branch')
  }

  const fetchRepositories = async () => {
    if (!accessToken) return
    
    try {
      const response = await axios.get(`${BACKEND_URL}/api/github/repositories`, {
        headers: { 
          'Authorization': `Bearer ${accessToken}`
        }
      })
      setRepositories(response.data)
    } catch (error) {
      console.error('Failed to fetch repositories:', error)
      throw error
    }
  }

  const fetchBranches = async (owner: string, repo: string) => {
    if (!accessToken) return
    
    try {
      const response = await axios.get(
        `${BACKEND_URL}/api/github/repositories/${owner}/${repo}/branches`,
        { 
          headers: { 
            'Authorization': `Bearer ${accessToken}`
          }
        }
      )
      setBranches(response.data)
    } catch (error) {
      console.error('Failed to fetch branches:', error)
      throw error
    }
  }

  const pushToGitHub = async (
    files: Array<{path: string, content: string}>,
    commitMessage: string
  ) => {
    if (!accessToken || !selectedRepo) {
      throw new Error('GitHub not connected or no repository selected')
    }

    const [owner, repo] = selectedRepo.split('/')

    try {
      const response = await axios.post(`${BACKEND_URL}/api/github/push`, {
        owner,
        repo,
        files,
        commit_message: commitMessage,
        branch: selectedBranch
      }, {
        headers: { 
          'Authorization': `Bearer ${accessToken}`
        }
      })
      return response.data
    } catch (error) {
      console.error('Failed to push to GitHub:', error)
      throw error
    }
  }

  const createRepository = async (name: string, description: string, isPrivate: boolean) => {
    if (!accessToken) {
      throw new Error('GitHub not connected')
    }

    try {
      const response = await axios.post(
        `${BACKEND_URL}/api/github/repositories`,
        { name, description, private: isPrivate },
        { 
          headers: { 
            'Authorization': `Bearer ${accessToken}`
          }
        }
      )
      
      // Refresh repositories list
      await fetchRepositories()
      
      return response.data
    } catch (error) {
      console.error('Failed to create repository:', error)
      throw error
    }
  }

  const value: GitHubContextType = {
    isConnected,
    user,
    accessToken,
    repositories,
    branches,
    selectedRepo,
    selectedBranch,
    connectGitHub,
    disconnectGitHub,
    fetchRepositories,
    fetchBranches,
    setSelectedRepo,
    setSelectedBranch,
    pushToGitHub,
    createRepository
  }

  return <GitHubContext.Provider value={value}>{children}</GitHubContext.Provider>
}

export const useGitHub = () => {
  const context = useContext(GitHubContext)
  if (context === undefined) {
    throw new Error('useGitHub must be used within a GitHubProvider')
  }
  return context
}
