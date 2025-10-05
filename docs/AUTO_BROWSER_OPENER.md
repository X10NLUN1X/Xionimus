# Auto Browser Opener - Dokumentation

## ✅ Implementiert

Der Auto Browser Opener öffnet automatisch Xionimus AI im Browser nach Backend-Start.

### Dateien
- `/app/scripts/auto_browser_opener.py` - Hauptscript
- `/etc/supervisor/conf.d/auto_browser.conf` - Supervisor-Konfiguration

### Funktionsweise

1. **Wartet auf Services**
   - Backend Health-Check: `http://localhost:8001/api/health`
   - Frontend Erreichbarkeit: `http://localhost:3000`
   - Max. Wartezeit: 120 Sekunden

2. **Öffnet Browser**
   - Verwendet Python `webbrowser` Modul
   - Öffnet Frontend-URL automatisch

3. **Supervisor Integration**
   - Startet automatisch mit anderen Services
   - Beendet sich nach erfolgreicher Ausführung
   - Priority: 999 (startet als letztes)

### Logs

```bash
# Status prüfen
sudo supervisorctl status auto_browser

# Logs anzeigen
tail -f /var/log/supervisor/auto_browser.out.log
tail -f /var/log/supervisor/auto_browser.err.log
```

### Einschränkungen

**Cloud/Container-Umgebung:**
- Browser kann nicht physisch geöffnet werden
- Script läuft erfolgreich durch, aber kein Browser öffnet sich
- In diesen Umgebungen: Nutzer muss manuell URL öffnen

**Lokale Entwicklung:**
- ✅ Funktioniert perfekt
- Browser öffnet sich automatisch

### URL

Nach Start erreichbar unter:
```
http://localhost:3000
```

### Alternative für Cloud

Für Cloud-Deployments empfehlen wir:
1. URL-Anzeige im Terminal beim Start
2. QR-Code-Generierung
3. Email-Benachrichtigung mit Link

Diese Features können bei Bedarf hinzugefügt werden.
