import React, { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { clsx } from 'clsx'

export const Navigation: React.FC = () => {
  const location = useLocation()
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  const navLinks = [
    { path: '/', label: 'Home' },
    { path: '/chat', label: 'Chat' },
    { path: '/settings', label: 'Settings' },
  ]

  const isActive = (path: string) => {
    if (path === '/' && location.pathname === '/') return true
    if (path !== '/' && location.pathname.startsWith(path)) return true
    return false
  }

  return (
    <nav className="sticky top-0 z-50 bg-gradient-dark backdrop-blur-xl border-b border-gold-500/20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          {/* Logo/Brand - Centered on Mobile, Left on Desktop */}
          <div className="flex-1 flex justify-start">
            <Link 
              to="/" 
              className="flex items-center space-x-3 group"
            >
              <div className="w-10 h-10 bg-glossy-gold rounded-lg flex items-center justify-center shadow-gold-glow group-hover:shadow-gold-glow-lg transition-all duration-300">
                <span className="text-primary-dark font-bold text-xl">X</span>
              </div>
            </Link>
          </div>

          {/* Center - Brand Name */}
          <div className="absolute left-1/2 transform -translate-x-1/2">
            <Link to="/" className="flex items-center">
              <h1 className="text-2xl md:text-3xl font-bold bg-gradient-to-r from-gold-400 via-gold-500 to-gold-400 bg-clip-text text-transparent hover:scale-105 transition-transform duration-300 text-glow">
                Xionimus AI
              </h1>
            </Link>
          </div>

          {/* Desktop Navigation - Right */}
          <div className="hidden md:flex flex-1 justify-end items-center space-x-8">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                className={clsx(
                  'nav-link',
                  isActive(link.path) && 'active text-gold-400'
                )}
              >
                {link.label}
              </Link>
            ))}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex-1 flex justify-end">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-lg text-gold-400 hover:bg-accent-blue transition-colors duration-300"
              aria-expanded={isMenuOpen}
              aria-label="Toggle navigation menu"
            >
              {/* Hamburger Icon */}
              <svg
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                {isMenuOpen ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="md:hidden bg-primary-navy/95 backdrop-blur-xl border-t border-gold-500/20 animate-slide-in">
          <div className="px-4 pt-2 pb-4 space-y-2">
            {navLinks.map((link) => (
              <Link
                key={link.path}
                to={link.path}
                onClick={() => setIsMenuOpen(false)}
                className={clsx(
                  'block px-4 py-3 rounded-lg text-base font-medium transition-all duration-300',
                  isActive(link.path)
                    ? 'bg-gradient-gold text-primary-dark shadow-gold-glow'
                    : 'text-gray-300 hover:bg-accent-blue hover:text-gold-400'
                )}
              >
                {link.label}
              </Link>
            ))}
          </div>
        </div>
      )}
    </nav>
  )
}