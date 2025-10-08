import React, { useState } from 'react'
import { Button } from './UI/Button'
import { Input } from './UI/Input'
import { Card } from './UI/Card'

interface RegisterFormProps {
  onRegister: (username: string, password: string, email: string) => Promise<void>
  onSwitchToLogin: () => void
}

export const RegisterForm: React.FC<RegisterFormProps> = ({ onRegister, onSwitchToLogin }) => {
  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    // Validation
    if (password !== confirmPassword) {
      setError('Passwörter stimmen nicht überein')
      return
    }

    if (password.length < 6) {
      setError('Passwort muss mindestens 6 Zeichen lang sein')
      return
    }

    setIsLoading(true)
    
    try {
      await onRegister(username.trim(), password.trim(), email.trim())
    } catch (error) {
      setError('Registrierung fehlgeschlagen. Bitte versuchen Sie es erneut.')
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
                Konto erstellen
              </h1>
              <p className="text-gray-400">
                Registrieren Sie sich bei Xionimus AI
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

          {/* Register Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Benutzername"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Wählen Sie einen Benutzernamen"
              required
              leftIcon={
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              }
            />

            <Input
              label="E-Mail"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="ihre@email.com"
              required
              leftIcon={
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              }
            />

            <Input
              label="Passwort"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Mindestens 6 Zeichen"
              required
              leftIcon={
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              }
            />

            <Input
              label="Passwort bestätigen"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Passwort wiederholen"
              required
              leftIcon={
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
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
              Registrieren
            </Button>
          </form>

          {/* Login Link */}
          <div className="pt-4 border-t border-gold-500/20">
            <div className="flex items-center justify-center gap-2 text-sm">
              <span className="text-gray-400">Bereits ein Konto?</span>
              <button
                onClick={onSwitchToLogin}
                className="text-gold-400 font-semibold hover:text-gold-300 transition-colors"
              >
                Jetzt anmelden
              </button>
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}