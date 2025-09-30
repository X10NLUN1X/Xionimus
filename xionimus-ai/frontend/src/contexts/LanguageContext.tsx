import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'

export type Language = 'en' | 'de'

interface Translations {
  [key: string]: {
    en: string
    de: string
  }
}

const translations: Translations = {
  // Header
  'header.newChat': { en: 'New Chat', de: 'Neuer Chat' },
  'header.settings': { en: 'Settings', de: 'Einstellungen' },
  
  // Welcome Screen
  'welcome.title': { en: 'Welcome to Xionimus AI', de: 'Willkommen bei Xionimus AI' },
  'welcome.subtitle': { en: 'Your specialized Code Assistant', de: 'Ihr spezialisierter Code-Assistent' },
  'welcome.exampleTitle': { en: 'Example Queries:', de: 'Beispiel-Anfragen:' },
  'welcome.example1': { en: '🚀 Create a React Todo App with TypeScript', de: '🚀 Erstelle eine React Todo-App mit TypeScript' },
  'welcome.example2': { en: '🔧 Help me set up a Python FastAPI Server', de: '🔧 Hilf mir einen Python FastAPI Server aufzusetzen' },
  'welcome.example3': { en: '🎨 Build a responsive Dashboard with Tailwind CSS', de: '🎨 Baue ein responsives Dashboard mit Tailwind CSS' },
  
  // Chat Interface
  'chat.inputPlaceholder': { en: 'Describe your programming project...', de: 'Beschreiben Sie Ihr Programmier-Projekt...' },
  'chat.sendButton': { en: 'Send', de: 'Senden' },
  'chat.stopButton': { en: 'Stop', de: 'Stopp' },
  'chat.ultraThinking': { en: 'Ultra Thinking', de: 'Ultra Denken' },
  'chat.generating': { en: 'Generating...', de: 'Generiere...' },
  'chat.attachFile': { en: 'Attach File', de: 'Datei anhängen' },
  'chat.branch': { en: 'Branch', de: 'Branch' },
  'chat.fold': { en: 'Fold', de: 'Verzweigen' },
  'chat.gitHubPush': { en: 'GitHub Push', de: 'GitHub Push' },
  
  // Toasts
  'toast.generationStopped': { en: 'Generation stopped', de: 'Generierung gestoppt' },
  'toast.generationStoppedDesc': { en: 'AI generation was interrupted', de: 'Die KI-Generierung wurde unterbrochen' },
  'toast.newChatCreated': { en: 'New chat created', de: 'Neuer Chat erstellt' },
  'toast.copiedToClipboard': { en: 'Copied to clipboard', de: 'In Zwischenablage kopiert' },
  'toast.downloadStarted': { en: 'Download started', de: 'Download gestartet' },
  'toast.sessionDeleted': { en: 'Session deleted', de: 'Sitzung gelöscht' },
  'toast.sessionRenamed': { en: 'Session renamed', de: 'Sitzung umbenannt' },
  'toast.exportComplete': { en: 'Export complete', de: 'Export abgeschlossen' },
  
  // Settings
  'settings.title': { en: 'Settings', de: 'Einstellungen' },
  'settings.apiKeys': { en: 'API Keys', de: 'API-Schlüssel' },
  'settings.openai': { en: 'OpenAI API Key', de: 'OpenAI API-Schlüssel' },
  'settings.anthropic': { en: 'Anthropic API Key', de: 'Anthropic API-Schlüssel' },
  'settings.perplexity': { en: 'Perplexity API Key', de: 'Perplexity API-Schlüssel' },
  'settings.save': { en: 'Save API Keys', de: 'API-Schlüssel speichern' },
  'settings.saved': { en: 'Settings saved successfully', de: 'Einstellungen erfolgreich gespeichert' },
  'settings.language': { en: 'Language', de: 'Sprache' },
  'settings.theme': { en: 'Theme', de: 'Design' },
  'settings.lightMode': { en: 'Light Mode', de: 'Hell-Modus' },
  'settings.darkMode': { en: 'Dark Mode', de: 'Dunkel-Modus' },
  
  // Chat History
  'history.title': { en: 'Chat History', de: 'Chat-Verlauf' },
  'history.search': { en: 'Search chats...', de: 'Chats durchsuchen...' },
  'history.delete': { en: 'Delete', de: 'Löschen' },
  'history.rename': { en: 'Rename', de: 'Umbenennen' },
  'history.export': { en: 'Export', de: 'Exportieren' },
  'history.noChats': { en: 'No chat history', de: 'Kein Chat-Verlauf' },
  'history.deleteConfirm': { en: 'Delete this session?', de: 'Diese Sitzung löschen?' },
  
  // Code Actions
  'code.copy': { en: 'Copy', de: 'Kopieren' },
  'code.copied': { en: 'Copied!', de: 'Kopiert!' },
  'code.download': { en: 'Download', de: 'Herunterladen' },
  'code.lines': { en: 'lines', de: 'Zeilen' },
  
  // Misc
  'misc.loading': { en: 'Loading...', de: 'Lädt...' },
  'misc.error': { en: 'Error', de: 'Fehler' },
  'misc.retry': { en: 'Retry', de: 'Wiederholen' },
  'misc.cancel': { en: 'Cancel', de: 'Abbrechen' },
  'misc.confirm': { en: 'Confirm', de: 'Bestätigen' },
  'misc.close': { en: 'Close', de: 'Schließen' },
}

interface LanguageContextType {
  language: Language
  setLanguage: (lang: Language) => void
  t: (key: string) => string
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined)

export const LanguageProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [language, setLanguageState] = useState<Language>(() => {
    const saved = localStorage.getItem('xionimus-language')
    return (saved === 'en' || saved === 'de') ? saved : 'de'
  })

  const setLanguage = (lang: Language) => {
    setLanguageState(lang)
    localStorage.setItem('xionimus-language', lang)
  }

  const t = (key: string): string => {
    const translation = translations[key]
    if (!translation) {
      console.warn(`Translation missing for key: ${key}`)
      return key
    }
    return translation[language] || key
  }

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  )
}

export const useLanguage = () => {
  const context = useContext(LanguageContext)
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider')
  }
  return context
}
