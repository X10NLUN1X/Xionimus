/**
 * GitHub OAuth Service
 * Handles GitHub OAuth authentication flow
 */
import axios from 'axios'

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || import.meta.env.REACT_APP_BACKEND_URL || 'http://localhost:8001'

export interface GitHubOAuthStatus {
  connected: boolean
  github_username: string | null
  message: string
}

export interface GitHubOAuthUrl {
  authorization_url: string
  state: string
}

/**
 * Get GitHub OAuth authorization URL
 */
export const getGitHubOAuthUrl = async (token: string): Promise<GitHubOAuthUrl> => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/github/oauth/authorize-url`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    return response.data
  } catch (error) {
    console.error('Failed to get GitHub OAuth URL:', error)
    throw error
  }
}

/**
 * Check GitHub OAuth connection status
 */
export const getGitHubOAuthStatus = async (token: string): Promise<GitHubOAuthStatus> => {
  try {
    const response = await axios.get(`${BACKEND_URL}/api/github/oauth/status`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    return response.data
  } catch (error) {
    console.error('Failed to get GitHub OAuth status:', error)
    throw error
  }
}

/**
 * Initiate GitHub OAuth flow
 * Redirects user to GitHub authorization page or handles PAT mode
 */
export const initiateGitHubOAuth = async (token: string): Promise<void> => {
  try {
    const response = await getGitHubOAuthUrl(token)
    
    // Check if PAT mode
    if (response.mode === 'pat') {
      // PAT mode - GitHub is already configured
      console.log('GitHub PAT mode detected - authentication handled automatically')
      return
    }
    
    // OAuth mode - redirect to GitHub
    if (response.authorization_url) {
      window.location.href = response.authorization_url
    } else {
      throw new Error('No authorization URL received')
    }
  } catch (error) {
    console.error('Failed to initiate GitHub OAuth:', error)
    throw error
  }
}

/**
 * Exchange OAuth code for access token
 * This is called by the callback page
 */
export const exchangeOAuthCode = async (code: string, token: string): Promise<GitHubOAuthStatus> => {
  try {
    const response = await axios.post(
      `${BACKEND_URL}/api/github/oauth/callback`,
      { code },
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    )
    return response.data
  } catch (error) {
    console.error('Failed to exchange OAuth code:', error)
    throw error
  }
}
