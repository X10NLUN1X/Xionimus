# Klickbare Quick Actions - Vollständige Implementation

## ✅ Implementiert

### Backend (100% Komplett)

#### 1. Progress-Leiste nur bei Coding-Aufgaben
**Problem:** Progress-Leiste erschien bei "hallo" (Small Talk)
**Lösung:**
```python
# Prüfe ob es eine Coding-Aufgabe ist
is_coding_task = coding_prompt_manager.is_coding_related(last_user_msg["content"])

if not request.stream and is_coding_task:
    progress_tracker = get_progress_tracker("chat")
    # Nur bei echten Coding-Aufgaben
```

**Ergebnis:**
- ✅ Kein Progress bei "hallo", "wie geht's", etc.
- ✅ Progress nur bei "erstelle App", "programmiere", etc.

#### 2. Research-Optionen (Klickbar)
```python
# chat.py
if coding_prompt_manager.should_offer_research(messages_dict):
    research_options = coding_prompt_manager.generate_research_question(language)
    return ChatResponse(
        content=research_options["message"],
        quick_actions=research_options  # Strukturierte Daten
    )
```

**Datenstruktur:**
```json
{
  "message": "🔍 Recherche-Optionen\n\nMöchten Sie...",
  "options": [
    {
      "id": "klein",
      "title": "🟢 Klein",
      "description": "5-10 Sek - Schnelle Übersicht",
      "action": "research_small",
      "duration": "5-10 Sek",
      "icon": "🟢"
    }
  ]
}
```

#### 3. Post-Code Optionen (Klickbar)
```python
# Nach Code-Generierung
if coding_prompt_manager.should_offer_post_code_options(messages_dict):
    post_code_options = coding_prompt_manager.generate_post_code_options(language)
    return ChatResponse(
        content=response["content"],
        quick_actions=post_code_options
    )
```

**Optionen:**
- 🐛 **Debugging** (Claude Opus 4.1) - Detaillierte Analyse
- ⚡ **Verbesserungsvorschläge** (Sonnet 4.5) - Optimierungen
- 💡 **Weitere Schritte** (Sonnet 4.5) - Testing, Docs, Deployment

### Frontend (100% Komplett)

#### 1. QuickActions Komponente
**Datei:** `/app/frontend/src/components/QuickActions.tsx`

**Features:**
- Klickbare Button-Cards mit Hover-Effekten
- Icons und Badges (Zeitangaben, Models)
- Markdown-Support für Nachrichten
- Responsive Design
- Dark/Light Mode Support

```tsx
<QuickActions
  message="🔍 Recherche-Optionen..."
  options={[...]}
  onSelect={(action) => sendMessage(action.title)}
  isDisabled={isLoading}
/>
```

#### 2. ChatMessage Interface erweitert
**Datei:** `/app/frontend/src/contexts/AppContext.tsx`

```typescript
interface ChatMessage {
  // ... existing fields
  quick_actions?: {
    message: string
    options: Array<{
      id: string
      title: string
      description: string
      action: string
      icon?: string
      duration?: string
      provider?: string
      model?: string
    }>
  }
}
```

#### 3. ChatPage Integration
**Datei:** `/app/frontend/src/pages/ChatPage.tsx`

```tsx
{/* Quick Actions nach Messages */}
{messages.length > 0 && messages[messages.length - 1]?.quick_actions && (
  <QuickActions
    message={messages[messages.length - 1].quick_actions.message}
    options={messages[messages.length - 1].quick_actions.options}
    onSelect={(action) => {
      const optionText = action.title.replace(/[🟢🟡🔴❌🐛⚡💡]/g, '').trim()
      sendMessage(optionText)
    }}
    isDisabled={isLoading || isStreaming}
  />
)}
```

## 🎯 Kompletter Workflow

### Szenario 1: Small Talk
```
User: "hallo"
  ↓
System: "Hallo! Wie kann ich helfen?"
  ❌ Kein Progress
  ❌ Keine Quick Actions
```

### Szenario 2: Erste Coding-Anfrage
```
User: "Erstelle eine Todo-App"
  ↓
System zeigt Quick Actions:
┌────────────────────────────────────────┐
│ 🔍 Recherche-Optionen                  │
│                                        │
│ [🟢 Klein]        5-10 Sek            │
│ Schnelle Übersicht, grundlegende...   │
│                                        │
│ [🟡 Mittel]       15-30 Sek           │
│ Standard-Recherche mit Details...     │
│                                        │
│ [🔴 Groß]         10-15 Min           │
│ Tiefgehende Analyse mit Trends...    │
│                                        │
│ [❌ Keine Recherche]                   │
│ Direkt mit Coding beginnen            │
└────────────────────────────────────────┘
  ↓ User klickt [🟡 Mittel]
  ↓
System: "Mittel" wird als Message gesendet
  ↓
Backend erkennt Research-Choice
  ↓
Perplexity Research wird durchgeführt
  ↓ ✅ Progress-Leiste erscheint
  ↓
Code wird mit Research generiert
  ↓
System zeigt Post-Code Quick Actions:
┌────────────────────────────────────────┐
│ ✅ Code-Generierung abgeschlossen!     │
│                                        │
│ [🐛 Debugging]                         │
│ Detaillierte Code-Analyse              │
│ claude-opus-4-20250514                 │
│                                        │
│ [⚡ Verbesserungsvorschläge]           │
│ Optimierungen für Performance...      │
│ claude-sonnet-4-5-20250929            │
│                                        │
│ [💡 Weitere Schritte]                  │
│ Testing, Dokumentation oder...        │
│ claude-sonnet-4-5-20250929            │
└────────────────────────────────────────┘
  ↓ User klickt [🐛 Debugging]
  ↓
System: "Debugging" wird als Message gesendet
  ↓
Claude Opus 4.1 analysiert den generierten Code
  ↓ ✅ Progress-Leiste erscheint
  ↓
Detaillierter Debugging-Report
```

### Szenario 3: Direkt Coding (ohne Research)
```
User: "Erstelle eine Todo-App"
  ↓
System zeigt Quick Actions: [Klein] [Mittel] [Groß] [Keine]
  ↓ User klickt [❌ Keine Recherche]
  ↓
System geht direkt zu Klärungsfragen
  ↓ ✅ Progress-Leiste erscheint
  ↓
Code wird generiert
  ↓
Post-Code Quick Actions erscheinen
```

## 🎨 Design & UX

### Quick Actions Styling
```css
Button Cards:
- Border: 2px solid (blue theme)
- Hover: Transform + Box Shadow
- Active: Background color change
- Disabled: Gray out
- Transition: 0.2s smooth

Icons: 2xl size, prominent
Badges: Small, colored (blue/purple)
Text: Bold titles, gray descriptions
```

### Responsive Behavior
- Full width on mobile
- Stacked vertically
- Touch-friendly (min 44px height)
- Smooth animations

## 📊 Backend Detection Logic

### Coding Task Detection
```python
coding_keywords = [
    "erstelle", "programmiere", "code", "app", "website",
    "create", "build", "develop", "implement",
    "python", "javascript", "react", ...
]
```

### Research Detection
```python
def should_offer_research(messages):
    # 1. Is it a coding request?
    # 2. No research choice made yet?
    # 3. First message in conversation?
    return all_conditions_met
```

### Post-Code Detection
```python
def should_offer_post_code_options(messages):
    # 1. Last message from assistant?
    # 2. Contains code blocks (```)?
    # 3. Substantial length (>500 chars)?
    return all_conditions_met
```

## ✅ Testing Checklist

- [x] Backend: Research-Optionen generieren
- [x] Backend: Post-Code Optionen generieren
- [x] Backend: Progress nur bei Coding
- [x] Backend: quick_actions in Response
- [x] Frontend: QuickActions Komponente
- [x] Frontend: ChatMessage Interface
- [x] Frontend: ChatPage Integration
- [x] Frontend: onClick Handler
- [x] E2E: Research-Workflow
- [ ] E2E: Post-Code Workflow (Testing benötigt)
- [ ] E2E: Small Talk (kein Progress)

## 📝 Files Modified

### Backend
1. `/app/backend/app/core/coding_prompt.py`
   - `should_offer_research(self, messages)`
   - `generate_research_question(self, language)`
   - `generate_post_code_options(self, language)`
   - `detect_post_code_choice(self, user_input)`
   - `should_offer_post_code_options(self, messages)`

2. `/app/backend/app/api/chat.py`
   - Progress nur bei `is_coding_task`
   - Research quick_actions in Response
   - Post-Code quick_actions in Response
   - ChatResponse Model erweitert

### Frontend
1. `/app/frontend/src/components/QuickActions.tsx` (NEU)
2. `/app/frontend/src/contexts/AppContext.tsx`
   - ChatMessage interface + quick_actions
3. `/app/frontend/src/pages/ChatPage.tsx`
   - QuickActions Import
   - QuickActions Rendering
   - onClick Handler

## 🚀 Nächste Schritte

1. ✅ Backend komplett
2. ✅ Frontend komplett
3. ⏳ E2E Testing mit echten Requests
4. ⏳ User Feedback sammeln
5. ⏳ Eventuell: Animation Tweaks

## 💡 Hinweise

**Für User:**
- Klicke auf die Buttons anstatt zu tippen
- Icons helfen bei visueller Unterscheidung
- Zeitangaben geben Orientierung
- Model-Badges zeigen welche AI verwendet wird

**Für Entwickler:**
- quick_actions ist optional in ChatResponse
- Nur wenn should_offer_* true zurückgibt
- Frontend prüft messages[last].quick_actions
- onClick sendet title ohne Emojis
