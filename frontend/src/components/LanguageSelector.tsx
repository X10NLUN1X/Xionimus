import React, { useState } from 'react'
import { useLanguage, Language } from '../contexts/LanguageContext'

export const LanguageSelector: React.FC = () => {
  const { language, setLanguage } = useLanguage()
  const [isOpen, setIsOpen] = useState(false)

  const languages: { code: Language; name: string; flag: string }[] = [
    { code: 'en', name: 'English', flag: '🇬🇧' },
    { code: 'de', name: 'Deutsch', flag: '🇩🇪' },
  ]

  const currentLang = languages.find(l => l.code === language) || languages[1]

  return (
    <div className="relative pointer-events-auto">
      {/* Menu Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 rounded-lg hover:bg-accent-blue transition-colors flex items-center gap-1 pointer-events-auto"
        style={{ pointerEvents: 'auto' }}
        aria-label="Select language"
      >
        <span className="text-lg">{currentLang.flag}</span>
        <svg 
          className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill="none" 
          viewBox="0 0 24 24" 
          stroke="currentColor"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {/* Dropdown Menu */}
      {isOpen && (
        <>
          {/* Backdrop */}
          <div 
            className="fixed inset-0 z-40 pointer-events-auto" 
            onClick={() => setIsOpen(false)}
            style={{ pointerEvents: 'auto' }}
          />
          
          {/* Menu Items */}
          <div className="absolute right-0 bottom-full mb-2 glossy-card py-1 z-50 min-w-[150px] animate-slide-in pointer-events-auto" style={{ pointerEvents: 'auto' }}>
            {languages.map(lang => (
              <button
                key={lang.code}
                onClick={() => {
                  setLanguage(lang.code)
                  setIsOpen(false)
                }}
                className={`
                  w-full px-4 py-2 flex items-center gap-2
                  transition-colors duration-200 pointer-events-auto
                  ${language === lang.code 
                    ? 'bg-gold-500/20 text-gold-400' 
                    : 'text-gray-300 hover:bg-accent-blue/30'
                  }
                `}
                style={{ pointerEvents: 'auto' }}
              >
                <span className="text-lg">{lang.flag}</span>
                <span className="text-sm">{lang.name}</span>
              </button>
            ))}
          </div>
        </>
      )}
    </div>
  )
}