import React, { useState } from 'react'
import { useApp } from '../contexts/AppContext'
import { Button } from './UI/Button'
import { Input } from './UI/Input'
import { Card } from './UI/Card'

interface LoginFormProps {
  onRegisterClick?: () => void
}

export const LoginForm: React.FC<LoginFormProps> = ({ onRegisterClick }) => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  const { login } = useApp()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setIsLoading(true)
    
    try {
      await login(username.trim(), password.trim())
    } catch (error) {
      setError('Login fehlgeschlagen. Bitte überprüfen Sie Ihre Eingaben.')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 bg-primary-dark bg-geometric">
      <Card className="w-full max-w-md animate-fade-in">
        <div className="space-y-6">
          {/* Header */}
          <div className="text-center space-y-4">
            <div className="flex justify-center">
              <div className="w-16 h-16 bg-glossy-gold rounded-2xl flex items-center justify-center shadow-gold-glow">
                <span className="text-primary-dark font-black text-3xl">X</span>
              </div>
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-gold-400 via-gold-500 to-gold-400 bg-clip-text text-transparent text-glow mb-2">
                Xionimus AI
              </h1>
              <p className="text-gray-400">
                Melden Sie sich an, um fortzufahren
              </p>
            </div>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="glossy-card border-red-500/50 bg-red-500/10 p-4">
              <div className="flex items-start">
                <span className="text-red-400 text-xl mr-3">⚠</span>
                <p className="text-red-400 text-sm">{error}</p>
              </div>
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Benutzername"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Ihr Benutzername"
              required
              leftIcon={
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              }
            />

            <Input
              label="Passwort"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Ihr Passwort"
              required
              leftIcon={
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              }
            />

            <Button
              type="submit"
              variant="primary"
              size="lg"
              loading={isLoading}
              className="w-full"
            >
              Anmelden
            </Button>
          </form>

          {/* Register Link */}
          <div className="pt-4 border-t border-gold-500/20">
            <div className="flex items-center justify-center gap-2 text-sm">
              <span className="text-gray-400">Noch kein Konto?</span>
              <button
                onClick={onRegisterClick}
                className="text-gold-400 font-semibold hover:text-gold-300 transition-colors"
              >
                Jetzt registrieren
              </button>
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}