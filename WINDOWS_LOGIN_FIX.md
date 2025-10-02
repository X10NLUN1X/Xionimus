# 🔧 WINDOWS LOGIN FIX - SCHRITT FÜR SCHRITT

## Das Problem
Sie arbeiten auf **Windows**, aber die Datenbank und Konfiguration wurden für Linux erstellt.
Deshalb:
- ❌ SECRET_KEY wird nicht gefunden
- ❌ Demo-User existiert nicht in Ihrer Windows-Datenbank

## ✅ LÖSUNG - Folgen Sie diesen Schritten:

### Schritt 1: Backend stoppen
Stoppen Sie den laufenden Backend-Server (Strg+C im Terminal)

### Schritt 2: .env Datei erstellen
Im Verzeichnis `C:\AI\Xionimus-Genesis\backend\` erstellen Sie eine Datei namens `.env` mit folgendem Inhalt:

```
SECRET_KEY=628942e396b7cd9bda2e74c1f110adc767d2b07c33cd634d61dd3b0629b10158
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=1440
MONGO_URL=mongodb://localhost:27017/
LOG_LEVEL=INFO
```

**WICHTIG:** Die Datei muss `.env` heißen (nicht `.env.txt`!)

### Schritt 3: Demo-User erstellen

#### Option A: Automatisches Script (empfohlen)
1. Kopieren Sie die Datei `create_demo_user_windows.py` in Ihr Backend-Verzeichnis
2. Öffnen Sie ein Terminal/CMD im Backend-Verzeichnis
3. Führen Sie aus:
```bash
cd C:\AI\Xionimus-Genesis\backend
python create_demo_user_windows.py
```

#### Option B: Manuell mit Python
Öffnen Sie ein Python-Terminal im Backend-Verzeichnis und führen Sie aus:

```python
import sys
sys.path.insert(0, '.')

from app.models.user_models import User
from app.core.database import engine, Base
from sqlalchemy.orm import Session
import bcrypt

# Create tables
Base.metadata.create_all(bind=engine)
print("Tables created")

# Create demo user
with Session(engine) as session:
    # Check if exists
    existing = session.query(User).filter(User.username == "demo").first()
    if existing:
        print("Demo user already exists")
    else:
        hashed_pw = bcrypt.hashpw("demo123".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        demo_user = User(
            username="demo",
            email="demo@xionimus.ai",
            hashed_password=hashed_pw,
            role="user",
            is_active=True
        )
        session.add(demo_user)
        session.commit()
        print("✅ Demo user created!")
```

### Schritt 4: Backend neu starten
```bash
cd C:\AI\Xionimus-Genesis\backend
python main.py
```

Sie sollten NICHT mehr diese Warnung sehen:
```
🔴 SECRET_KEY not set! Using temporary key for this session.
```

### Schritt 5: Browser-Cache leeren
1. Browser DevTools öffnen (F12)
2. Application Tab → Local Storage → http://localhost:3000
3. Alle Einträge löschen
4. Seite neu laden (Strg+Shift+R)

### Schritt 6: Login testen
- **Username:** demo
- **Password:** demo123

## ✅ Erfolgs-Prüfung

Beim Backend-Start sollten Sie sehen:
```
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**OHNE** diese Warnung:
```
🔴 SECRET_KEY not set!
```

Beim Login sollten Sie im Backend-Log sehen:
```
✅ User found: demo
✅ Password verified successfully
✅ Login successful
```

## 📁 Datei-Standorte

### .env Datei:
`C:\AI\Xionimus-Genesis\backend\.env`

### Datenbank:
Windows speichert die DB unter:
`C:\Users\<IhrUsername>\.xionimus_ai\xionimus.db`

## 🆘 Wenn es immer noch nicht funktioniert

Senden Sie mir:
1. Den kompletten Backend-Start-Log
2. Den Login-Versuch-Log
3. Bestätigung, dass die `.env` Datei existiert

## 🔍 Debug-Befehle

Prüfen Sie ob die .env geladen wird:
```python
import os
from dotenv import load_dotenv
load_dotenv()
print("SECRET_KEY:", os.getenv("SECRET_KEY", "NOT FOUND"))
```

Prüfen Sie die Datenbank:
```python
from app.core.database import DATABASE_PATH
print(f"Database: {DATABASE_PATH}")
print(f"Exists: {DATABASE_PATH.exists()}")
```

---

**Zusammenfassung:**
1. ✅ `.env` Datei mit SECRET_KEY erstellen
2. ✅ Demo-User in Windows-Datenbank erstellen
3. ✅ Backend neu starten
4. ✅ Browser-Cache leeren
5. ✅ Mit demo/demo123 einloggen
