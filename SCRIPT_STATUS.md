# XIONIMUS AI - Korrigierte Skript-Struktur

## ✅ KORREKTE VERWENDUNG

### 1. Installation (einmalig)
```bash
WINDOWS_INSTALL.bat
```
- **Einzige** Installationsdatei
- Installiert Backend + Frontend Dependencies
- Erstellt alle Konfigurationsdateien
- Startet automatisch beide Services nach Installation

### 2. Start (nach Installation)
```bash
START_BACKEND.bat    # Nur Backend
START_FRONTEND.bat   # Nur Frontend  
START_ALL.bat        # Beide Services
```
- **Nur Start-Funktionalität**
- Keine Installationsschritte mehr
- Prüft Installation vor Start

## 📁 Bereinigte Skript-Übersicht

| Skript | Zweck | Status |
|--------|-------|--------|
| `WINDOWS_INSTALL.bat` | **Komplette Installation** | ✅ Zentral |
| `START_BACKEND.bat` | Backend starten | ✅ Bereinigt |
| `START_FRONTEND.bat` | Frontend starten | ✅ Bereinigt |
| `START_ALL.bat` | Beide Services starten | ✅ Bereinigt |
| `QUICK_FIX_AIOHTTP.bat` | Reparatur-Installation | ✅ Behalten |
| `MINIMAL_INSTALL.bat` | Minimale Installation | ✅ Behalten |

## 🔧 Durchgeführte Korrekturen

### Entfernte Dateien
- ❌ `install.bat` (überflüssig)
- ❌ `INSTALLATION_GUIDE.md` (überflüssig)

### Bereinigte Skripte
- ✅ `START_BACKEND.bat`: Nur noch Backend-Start
- ✅ `START_FRONTEND.bat`: Nur noch Frontend-Start
- ✅ `START_ALL.bat`: Verweist auf WINDOWS_INSTALL.bat

### Erweiterte WINDOWS_INSTALL.bat
- ✅ Zusätzliche Backend .env Parameter (DEBUG, HOST, PORT)
- ✅ Bleibt die zentrale Installationsdatei

## 🎯 Workflow

1. **Neue Installation:** `WINDOWS_INSTALL.bat` ausführen
2. **Services starten:** `START_ALL.bat` oder einzeln
3. **Bei Problemen:** `QUICK_FIX_AIOHTTP.bat` oder `MINIMAL_INSTALL.bat`

## ⚠️ Wichtige Erkenntnisse

Die ursprüngliche `WINDOWS_INSTALL.bat` war bereits vollständig und funktional. Das Problem war, dass zusätzliche Installationsskripte erstellt wurden, die die Start-Skripte verunreinigt haben. Die Lösung war, zu der ursprünglichen Struktur zurückzukehren und nur die Start-Skripte zu bereinigen.