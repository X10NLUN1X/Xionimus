# 🎯 SESSION ID FIX - KI-Agent erkennt Repository

## ❌ Problem (Root Cause):

Der KI-Agent erkannte importierte Repositories **NICHT**, weil:

1. **Frontend**: Erstellt eigene Session IDs mit `session_${Date.now()}`
2. **Backend Import**: Aktualisierte die **neueste Session** des Users
3. **Mismatch**: Frontend nutzt Session A, aber Import setzt `active_project` in Session B
4. **Resultat**: Agent sieht kein Repository, weil er die falsche Session verwendet

---

## ✅ Lösung:

### **1. Backend: `set_active_project_for_user()` erweitert**

**Datei:** `/app/backend/app/api/github_pat.py` (Zeile 483)

**Neue Signatur:**
```python
def set_active_project_for_user(
    db, 
    user_id: str, 
    repo_name: str, 
    branch_name: str = "main", 
    session_id: Optional[str] = None  # ← NEU
) -> bool:
```

**Logik:**
1. **Wenn `session_id` gegeben:**
   - Versuche diese spezifische Session zu aktualisieren
   - Falls nicht gefunden, nutze Fallback-Logik
   
2. **Fallback (keine session_id oder nicht gefunden):**
   - Suche neueste Session des Users
   - Falls keine existiert, erstelle neue mit gegebener `session_id` (oder UUID)

**Code-Änderungen:**
```python
# Priorität 1: Spezifische Session nutzen
if session_id:
    session = db.query(SessionModel).filter(
        SessionModel.id == session_id,
        SessionModel.user_id == user_id_str
    ).first()
    
    if session:
        # Update die richtige Session!
        session.active_project = repo_name
        session.active_project_branch = branch_name
        db.commit()
        return True

# Priorität 2: Neueste Session finden (Fallback)
# Priorität 3: Neue Session erstellen mit session_id
```

---

### **2. Import Endpoints: session_id übergeben**

#### **A) POST `/import-from-github`** (Zeile 1413)
```python
set_active_project_for_user(
    db=db,
    user_id=current_user.user_id,
    repo_name=repo.name,
    branch_name=branch,
    session_id=request.session_id  # ← Request-Feld
)
```

#### **B) POST `/import-from-url`** (Zeile 1586)
```python
set_active_project_for_user(
    db=db,
    user_id=current_user.user_id,
    repo_name=repo.name,
    branch_name=branch,
    session_id=request.session_id  # ← Request-Feld
)
```

#### **C) GET `/import-progress`** (Zeile 1628 + 1825)
```python
# Parameter hinzugefügt:
async def import_with_progress(
    repo_owner: str,
    repo_name: str,
    branch: str = "main",
    token: str = None,
    session_id: str = None  # ← NEU
):

# Funktionsaufruf:
set_active_project_for_user(
    db=db,
    user_id=user_id,
    repo_name=repo.name,
    branch_name=branch_name,
    session_id=session_id  # ← Query Parameter
)
```

---

### **3. Frontend: session_id mitsenden**

**Datei:** `/app/frontend/src/components/GitHubImportDialog.tsx` (Zeile 279)

**Vorher:**
```typescript
const sseUrl = `${BACKEND_URL}/api/v1/github-pat/import-progress/${repoOwner}/${repoName}?branch=${branchToUse}&token=${encodeURIComponent(token)}`
```

**Nachher:**
```typescript
const sseUrl = `${BACKEND_URL}/api/v1/github-pat/import-progress/${repoOwner}/${repoName}?branch=${branchToUse}&token=${encodeURIComponent(token)}${sessionId ? `&session_id=${encodeURIComponent(sessionId)}` : ''}`
```

**Komponente erhält bereits `sessionId` Prop:**
```typescript
export const GitHubImportDialog: React.FC<GitHubImportDialogProps> = ({
  isOpen,
  onClose,
  sessionId  // ← Bereits vorhanden
}) => {
```

**ChatPage übergibt korrekt:**
```typescript
<GitHubImportDialog
  isOpen={isGitHubImportOpen}
  onClose={() => setIsGitHubImportOpen(false)}
  sessionId={typeof currentSession === 'string' ? currentSession : currentSession?.id || null}
/>
```

---

## 📊 Flow nach Fix:

```
┌─────────────┐
│  Frontend   │
│ Session:    │
│ session_123 │
└──────┬──────┘
       │
       │ 1. Import Repository
       │    + session_id=session_123
       ▼
┌─────────────────┐
│   Backend       │
│ Import Endpoint │
└──────┬──────────┘
       │
       │ 2. set_active_project_for_user(
       │      user_id="user_xyz",
       │      repo_name="MyRepo",
       │      session_id="session_123"  ← WICHTIG!
       │    )
       ▼
┌──────────────────┐
│    Database      │
│ Session:         │
│ session_123      │ ← DIE RICHTIGE SESSION!
│ active_project=  │
│   "MyRepo"       │
└──────┬───────────┘
       │
       │ 3. WebSocket Chat
       │    zu session_123
       ▼
┌─────────────────┐
│   chat_stream   │
│ Lädt Session:   │
│ session_123     │
│                 │
│ ✅ active_project │
│    gefunden!     │
│ ✅ Repository    │
│    wird gescannt │
└─────────────────┘
```

---

## 🎯 Vorher vs. Nachher:

### ❌ **Vorher (Bug):**
```
Frontend: session_123
         ↓ Import
Backend:  Setzt active_project in session_456 (neueste)
         ↓ Chat
Frontend: Nutzt session_123
Agent:    ❌ Kein active_project → Kein Repository
```

### ✅ **Nachher (Fix):**
```
Frontend: session_123
         ↓ Import + session_id=session_123
Backend:  Setzt active_project in session_123 (die richtige!)
         ↓ Chat
Frontend: Nutzt session_123
Agent:    ✅ active_project gesetzt → Repository erkannt!
```

---

## ✅ Test-Checklist:

1. **Repository importieren:**
   - Frontend sendet `session_id` mit
   - Backend loggt: "✅ Active project set for specific session"

2. **Chat-Nachricht senden:**
   - Backend loggt: "✅ Active project from session: [repo_name]"
   - Backend loggt: "✅ Repository contains X files..."

3. **Agent-Antwort:**
   - Agent hat Zugriff auf Repository-Struktur
   - Kann Files lesen und bearbeiten

---

## 📁 Geänderte Dateien:

### Backend:
- ✅ `/app/backend/app/api/github_pat.py`
  - `set_active_project_for_user()` erweitert (Zeile 483)
  - `/import-from-github` aktualisiert (Zeile 1413)
  - `/import-from-url` aktualisiert (Zeile 1586)
  - `/import-progress` erweitert (Zeile 1628, 1825)

### Frontend:
- ✅ `/app/frontend/src/components/GitHubImportDialog.tsx`
  - SSE URL um `session_id` Parameter erweitert (Zeile 279)

---

## 🎉 Status:

**✅ SESSION ID MISMATCH BEHOBEN**

Der KI-Agent erkennt jetzt importierte Repositories korrekt, weil:
1. Frontend sendet die aktuelle `session_id` beim Import
2. Backend setzt `active_project` in der **richtigen Session**
3. Agent lädt diese Session beim Chat und findet das Repository

---

## 🔍 Debug-Logs (zum Verifizieren):

**Import erfolgreich:**
```
✅ Active project set for specific session: MyRepo (Session: session_1...)
```

**Chat lädt Repository:**
```
🔍 User ID from session: user_xyz
✅ Active project from session: MyRepo
✅ Repository path: /path/to/MyRepo
✅ Repository contains 1839 files in 460 directories
✅ Repository structure scanned successfully!
```
