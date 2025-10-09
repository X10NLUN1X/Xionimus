# 🪟 Xionimus AI - Windows Setup Anleitung

## 🚀 Schnellstart

### Option 1: Automatisches Setup (EMPFOHLEN)

```cmd
# Einfach starten - .env wird automatisch erstellt:
start.bat
```

Das war's! Die `start.bat` prüft automatisch ob `.env` existiert und erstellt sie bei Bedarf.

---

### Option 2: Manuelles .env Setup (falls gewünscht)

```cmd
# Nur .env erstellen ohne zu starten:
setup-env.bat
```

---

## 📋 Was passiert beim ersten Start?

### Beim ersten Aufruf von `start.bat`:

1. ✅ Prüft ob `backend\.env` existiert
2. ❌ Wenn NICHT: Erstellt automatisch `.env` mit:
   - Permanentem SECRET_KEY (64 Zeichen)
   - Permanentem ENCRYPTION_KEY (44 Zeichen)
   - Datenbank-Konfiguration
   - Leere API Key Felder (optional)
3. ✅ Startet Backend mit der `.env`
4. ✅ Startet Frontend
5. ✅ Öffnet Browser

### Beim zweiten und allen weiteren Starts:

1. ✅ Findet bestehende `.env`
2. ✅ Verwendet permanente Keys
3. ✅ Kein "AUTO-FIX" mehr
4. ✅ Alle JWT Tokens bleiben gültig

---

## 🔑 API Keys hinzufügen (optional)

### Warum API Keys?

Ohne API Keys funktioniert das System, aber AI-Features (Chat mit OpenAI/Anthropic) sind nicht verfügbar.

### So fügen Sie Keys hinzu:

1. **Öffnen Sie:** `backend\.env`
2. **Finden Sie:**
   ```
   OPENAI_API_KEY=
   ANTHROPIC_API_KEY=
   ```
3. **Fügen Sie Ihre Keys ein:**
   ```
   OPENAI_API_KEY=sk-proj-ihr-echter-key-hier
   ANTHROPIC_API_KEY=sk-ant-ihr-echter-key-hier
   ```
4. **Speichern**
5. **Backend neu starten** (Fenster schließen und `start.bat` erneut)

### Wo bekomme ich API Keys?

- **OpenAI:** https://platform.openai.com/api-keys
- **Anthropic:** https://console.anthropic.com/
- **Perplexity:** https://www.perplexity.ai/settings/api

---

## 🛠️ Verfügbare BAT-Dateien

| Datei | Beschreibung | Wann verwenden? |
|-------|-------------|-----------------|
| `start.bat` | Startet Backend + Frontend | **Täglich** - Hauptstart |
| `setup-env.bat` | Erstellt nur .env Datei | Nur bei .env Problemen |
| `install.bat` | Installiert Dependencies | Einmalig / nach Updates |
| `reset-db.bat` | Löscht Datenbank | Bei DB-Problemen |

---

## ❓ Häufige Probleme

### Problem: "AUTO-FIX: .env file not found"

**Lösung:**
```cmd
# Führe aus:
setup-env.bat

# ODER:
start.bat
# (erstellt .env automatisch)
```

---

### Problem: "JWT validation failed"

**Grund:** SECRET_KEY hat sich geändert (alter Token im Browser)

**Lösung:**
1. Browser-Cache leeren:
   - F12 → Application → Clear storage
   - Strg+Shift+R
2. Neu einloggen

Dies passiert nur EINMAL nach .env Erstellung.

---

### Problem: "Chat antwortet nicht"

**Grund:** Keine API Keys konfiguriert

**Lösung:**
1. Öffne: `backend\.env`
2. Füge API Keys ein (siehe oben)
3. Backend neu starten

---

### Problem: Backend startet nicht

**Prüfen Sie:**
```cmd
# 1. MongoDB läuft?
# 2. Port 8001 frei?
netstat -ano | findstr :8001

# 3. .env existiert?
dir backend\.env

# 4. Python installiert?
python --version
```

---

## 🔒 Sicherheit

### Was ist SECRET_KEY?

- System-weiter Key für JWT Token Signierung
- Wird EINMAL generiert (64 Zeichen)
- Ändert sich NIE
- Wenn geändert → alle User müssen neu einloggen

### Was ist ENCRYPTION_KEY?

- Verschlüsselt API Keys in Datenbank
- Wird EINMAL generiert (44 Zeichen)
- Ändert sich NIE
- Wenn geändert → gespeicherte API Keys unleserlich

### User-spezifische API Keys

Jeder User kann eigene OpenAI/Anthropic Keys speichern:
- Werden verschlüsselt in MongoDB gespeichert
- Sind permanent pro User
- Sind isoliert (User A sieht nicht Keys von User B)

---

## 📊 System-Status prüfen

### Nach Start sollten Sie sehen:

**Backend:**
```
INFO:     Uvicorn running on http://0.0.0.0:8001
INFO:     Application startup complete.
```

**Keine Errors wie:**
- ❌ "AUTO-FIX: .env file not found"
- ❌ "SECRET_KEY automatically generated"

### Browser:

1. Öffnet automatisch: http://localhost:3000
2. Login: `admin` / `admin123`
3. Sollte funktionieren (kein JWT Error)

---

## 🎯 Zusammenfassung

### Beim ersten Start:
```
start.bat
  ↓
Prüft .env
  ↓
Nicht gefunden? → Erstellt automatisch
  ↓
Backend startet mit permanenten Keys
  ↓
✅ System läuft
```

### Ab dem zweiten Start:
```
start.bat
  ↓
.env gefunden
  ↓
Verwendet bestehende Keys
  ↓
✅ Tokens bleiben gültig
✅ Kein Neu-Login nötig
```

---

## 💡 Tipps

1. **Erste Installation:**
   ```cmd
   install.bat          # Dependencies installieren
   start.bat            # .env wird automatisch erstellt + System startet
   ```

2. **Tägliche Nutzung:**
   ```cmd
   start.bat            # Einfach starten
   ```

3. **Nach Git Pull:**
   ```cmd
   install.bat          # Falls neue Dependencies
   start.bat            # .env bleibt erhalten
   ```

4. **Bei Problemen:**
   ```cmd
   setup-env.bat        # .env neu erstellen
   reset-db.bat         # Datenbank zurücksetzen (wenn nötig)
   start.bat            # Neu starten
   ```

---

## ✅ Checkliste für Production

- [x] .env existiert mit permanenten Keys
- [x] SECRET_KEY ist 64 Zeichen
- [x] ENCRYPTION_KEY ist 44 Zeichen
- [ ] API Keys hinzugefügt (optional)
- [ ] MongoDB läuft
- [ ] Backend startet ohne "AUTO-FIX"
- [ ] Frontend erreichbar
- [ ] Login funktioniert
- [ ] Keine JWT Errors

---

## 🆘 Support

Bei Problemen:

1. Prüfen Sie diese Anleitung
2. Lesen Sie Error Messages im Terminal
3. Prüfen Sie `backend\.env` existiert
4. Versuchen Sie `setup-env.bat`

---

**Viel Erfolg mit Xionimus AI! 🚀**
