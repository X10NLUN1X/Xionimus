# 🚀 Xionimus AI - Schnellstart

## ✅ EINE DATEI FÜR ALLES

Alles wurde vereinfacht! Sie brauchen nur EINE Datei:

```cmd
START.bat
```

Das war's! Diese Datei macht ALLES:
- ✅ Prüft Python & Node.js
- ✅ Erstellt .env automatisch (mit permanenten Keys)
- ✅ Installiert alle Dependencies
- ✅ Startet Backend & Frontend
- ✅ Öffnet Browser

---

## 🎯 SCHNELLSTART (30 Sekunden)

### 1. Doppelklick auf START.bat

Das System:
- Erstellt .env mit permanenten SECRET_KEY und ENCRYPTION_KEY
- Installiert alle benötigten Packages
- Startet Backend (Port 8001)
- Startet Frontend (Port 3000)
- Öffnet Browser automatisch

### 2. Im Browser (beim ersten Mal)

**WICHTIG - Nur beim ersten Start:**

1. **Browser-Cache leeren:**
   - F12 drücken
   - Application → Clear storage
   - "Clear site data" klicken
   - ODER: Strg+Shift+R

2. **Einloggen:**
   - Username: `admin`
   - Password: `admin123`

3. **Fertig!** ✅

---

## 🔑 API Keys hinzufügen (optional)

**Warum?** Ohne API Keys läuft das System, aber Chat (OpenAI/Anthropic) funktioniert nicht.

**Wie:**

1. Starten Sie die Anwendung mit START.bat
2. Melden Sie sich an (admin / admin123)
3. Gehen Sie zu **Einstellungen** oder **Profil**
4. Geben Sie Ihre API Keys in der Benutzeroberfläche ein:
   - OpenAI API Key
   - Anthropic API Key
   - Perplexity API Key (optional)
5. Die Keys werden verschlüsselt in der Datenbank gespeichert

**Keys besorgen:**
- OpenAI: https://platform.openai.com/api-keys
- Anthropic: https://console.anthropic.com/
- Perplexity: https://www.perplexity.ai/settings/api

**Hinweis:** Keys werden sicher mit Fernet-Verschlüsselung gespeichert und sind pro Benutzer individuell.

---

## 📁 Dateien-Übersicht

| Datei | Zweck | Wann nutzen? |
|-------|-------|--------------|
| **START.bat** | **Alles-in-einem Start** | **IMMER** |
| INSTALL.bat | Nur Dependencies | Wird automatisch aufgerufen |
| backend\.env | Konfiguration | Automatisch erstellt |
| README-DEUTSCH.md | Diese Anleitung | Zum Nachlesen |

**Alle anderen .bat Dateien sind veraltet und können ignoriert werden.**

---

## ❓ Probleme lösen

### Problem: "Python nicht gefunden"
**Lösung:** Python 3.10+ installieren von https://www.python.org/downloads/

### Problem: "Node.js nicht gefunden"
**Lösung:** Node.js installieren von https://nodejs.org/

### Problem: "Port bereits verwendet"
**Lösung:** 
- Schließen Sie andere Instanzen
- Oder: Im Task Manager nach Python/Node suchen und beenden

### Problem: "JWT validation failed"
**Lösung:** Browser-Cache leeren (nur beim ersten Start)
- F12 → Application → Clear storage
- Neu einloggen

### Problem: "Chat antwortet nicht"
**Lösung:** API Keys in der Benutzeroberfläche hinzufügen (Einstellungen → API Keys)

---

## 🎉 Das ist alles!

**Tägliche Nutzung:**
1. Doppelklick START.bat
2. Warten bis Browser öffnet
3. Arbeiten!

**Kein manuelles Setup mehr nötig!**

---

## 🔒 Sicherheit

### Was ist SECRET_KEY?
- System-weiter JWT Token Signierungsschlüssel
- Wird EINMAL generiert (permanent)
- Ist identisch für alle User
- Ändert sich NIE

### Was ist ENCRYPTION_KEY?
- Verschlüsselt API Keys in Datenbank
- Wird EINMAL generiert (permanent)
- Ändert sich NIE

### User API Keys
- Jeder User kann eigene OpenAI/Anthropic Keys speichern
- Werden verschlüsselt in MongoDB gespeichert
- Sind permanent pro User

**Alle Keys sind automatisch konfiguriert - nichts zu tun!**

---

## 💡 Tipps

1. **Erste Installation:** Einfach START.bat ausführen
2. **Nach Updates:** Einfach START.bat ausführen
3. **API Keys ändern:** In der Anwendung unter Einstellungen → API Keys
4. **System zurücksetzen:** backend\.env löschen, START.bat neu ausführen

---

**Viel Erfolg mit Xionimus AI! 🚀**