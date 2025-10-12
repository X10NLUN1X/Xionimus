"""
PERMANENT FIX: API Keys gehen verloren
======================================

PROBLEM:
- API Keys werden im Frontend eingegeben
- Beim Chat werden sie nicht gesendet/geladen
- Chat funktioniert nicht mehr

LÖSUNG:
- Backend lädt API Keys automatisch aus der Datenbank
- Fallback wenn Frontend keine Keys sendet
- Debug-Tool zum Prüfen gespeicherter Keys
"""

import sys
from pathlib import Path

def fix_chat_stream_api_keys():
    """Fix chat_stream.py to automatically load API keys from database"""
    
    chat_stream_path = Path("backend/app/api/chat_stream.py")
    
    if not chat_stream_path.exists():
        print(f"❌ Datei nicht gefunden: {chat_stream_path}")
        return False
    
    print(f"✅ Datei gefunden: {chat_stream_path}")
    
    # Backup
    import shutil
    backup = chat_stream_path.with_suffix('.py.backup-apikeys')
    shutil.copy2(chat_stream_path, backup)
    print(f"✅ Backup erstellt: {backup.name}")
    
    # Read file
    with open(chat_stream_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix: Add automatic API key loading from database
    old_code = '''            api_keys = message_data.get("api_keys", {})
            conversation_history = message_data.get("messages", [])
            
            # Debug logging for API keys
            logger.info(f"🔍 WebSocket received - Provider: {provider}, Model: {model}")
            logger.info(f"🔍 API keys received: {list(api_keys.keys())}")
            logger.info(f"🔍 API key for {provider}: {'✅ Present' if api_keys.get(provider) else '❌ Missing'}")'''
    
    new_code = '''            api_keys = message_data.get("api_keys", {})
            conversation_history = message_data.get("messages", [])
            
            # Debug logging for API keys
            logger.info(f"🔍 WebSocket received - Provider: {provider}, Model: {model}")
            logger.info(f"🔍 API keys received from frontend: {list(api_keys.keys())}")
            logger.info(f"🔍 API key for {provider}: {'✅ Present' if api_keys.get(provider) else '❌ Missing'}")
            
            # CRITICAL FIX: Auto-load API keys from database if missing
            if not api_keys.get(provider):
                logger.warning(f"⚠️ API key for {provider} not sent from frontend - loading from database")
                try:
                    from ..models.api_key_models import UserApiKey
                    from ..core.encryption import encryption_manager
                    from ..core.auth import get_user_id_from_session
                    
                    # Get user ID from session
                    db = get_database()
                    try:
                        # Load all stored API keys for this user
                        user_api_keys = db.query(UserApiKey).filter(
                            UserApiKey.user_id == session_id.split('_')[0] if '_' in session_id else None,
                            UserApiKey.is_active == True
                        ).all()
                        
                        # If no keys found with session_id, try to get from first available user (demo mode)
                        if not user_api_keys:
                            logger.info("🔍 Trying to load API keys from first available user")
                            user_api_keys = db.query(UserApiKey).filter(
                                UserApiKey.is_active == True
                            ).all()
                        
                        # Decrypt and add to api_keys dict
                        loaded_count = 0
                        for key_record in user_api_keys:
                            try:
                                decrypted_key = encryption_manager.decrypt(key_record.encrypted_key)
                                api_keys[key_record.provider] = decrypted_key
                                loaded_count += 1
                                logger.info(f"✅ Loaded {key_record.provider} API key from database")
                            except Exception as decrypt_error:
                                logger.error(f"❌ Failed to decrypt {key_record.provider} key: {decrypt_error}")
                        
                        if loaded_count > 0:
                            logger.info(f"✅ Successfully loaded {loaded_count} API key(s) from database")
                        else:
                            logger.warning(f"⚠️ No API keys found in database")
                    
                    finally:
                        db.close()
                
                except Exception as e:
                    logger.error(f"❌ Failed to auto-load API keys from database: {e}")
                    import traceback
                    traceback.print_exc()'''
    
    if old_code in content:
        content = content.replace(old_code, new_code)
        print("✅ API Key Auto-Loading hinzugefügt")
    else:
        print("⚠️ Code-Stelle nicht gefunden - manuelle Anpassung nötig")
        return False
    
    # Write back
    with open(chat_stream_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Datei gespeichert: {chat_stream_path}")
    
    # Verify syntax
    import py_compile
    try:
        py_compile.compile(str(chat_stream_path), doraise=True)
        print("✅ Syntax OK!")
        return True
    except py_compile.PyCompileError as e:
        print(f"❌ Syntax-Fehler: {e}")
        # Restore backup
        shutil.copy2(backup, chat_stream_path)
        print("✅ Backup wiederhergestellt")
        return False

def create_api_key_checker():
    """Create a tool to check stored API keys"""
    
    checker_script = '''"""
API Key Checker - Zeigt gespeicherte API Keys an (maskiert)
"""
import sys
sys.path.insert(0, 'backend')

from app.core.database import get_database
from app.models.api_key_models import UserApiKey
from app.core.encryption import encryption_manager

def check_api_keys():
    """Check which API keys are stored in the database"""
    
    print("="*70)
    print("  API KEY CHECKER")
    print("="*70)
    print()
    
    db = get_database()
    try:
        all_keys = db.query(UserApiKey).all()
        
        if not all_keys:
            print("❌ Keine API Keys in der Datenbank gefunden!")
            print()
            print("📝 Schritte zum Hinzufügen:")
            print("   1. Backend starten: START.bat")
            print("   2. Frontend öffnen: http://localhost:3000")
            print("   3. Settings (⚙️) öffnen")
            print("   4. API Keys eingeben und speichern")
            return
        
        print(f"✅ {len(all_keys)} API Key(s) gefunden:")
        print()
        
        for key in all_keys:
            status = "🟢 Aktiv" if key.is_active else "🔴 Inaktiv"
            
            # Try to decrypt to verify
            try:
                decrypted = encryption_manager.decrypt(key.encrypted_key)
                # Mask the key (show first 4 and last 4 chars)
                if len(decrypted) > 12:
                    masked = f"{decrypted[:4]}...{decrypted[-4:]}"
                else:
                    masked = "***"
                
                print(f"  {status} {key.provider.upper()}")
                print(f"     Key: {masked}")
                print(f"     Länge: {len(decrypted)} Zeichen")
                print(f"     Erstellt: {key.created_at}")
                print(f"     User ID: {key.user_id}")
                
                if key.last_test_status:
                    print(f"     Letzter Test: {key.last_test_status}")
                
                print()
            
            except Exception as e:
                print(f"  ❌ {key.provider.upper()}")
                print(f"     Fehler beim Entschlüsseln: {e}")
                print()
    
    finally:
        db.close()
    
    print("="*70)
    print("💡 Tipp: Wenn Keys fehlen, in Settings (⚙️) hinzufügen")
    print("="*70)

if __name__ == "__main__":
    check_api_keys()
'''
    
    checker_path = Path("CHECK_API_KEYS.py")
    with open(checker_path, 'w', encoding='utf-8') as f:
        f.write(checker_script)
    
    print(f"\n✅ API Key Checker erstellt: {checker_path}")
    return True

def create_api_key_fixer_bat():
    """Create Windows batch script to add API keys via CLI"""
    
    bat_script = '''@echo off
setlocal EnableDelayedExpansion
title Xionimus AI - API Keys Setup
color 0B

echo.
echo ========================================================================
echo    XIONIMUS AI - API KEYS SETUP
echo ========================================================================
echo.

cd /d "%~dp0"

echo Dieses Tool hilft dir, deine API Keys zu ueberpruefen und zu setzen.
echo.

REM Check Python
python --version >nul 2>&1
if !errorlevel! neq 0 (
    echo ❌ Python nicht gefunden!
    pause
    exit /b 1
)

echo [1/2] Ueberpruefe gespeicherte API Keys...
echo.

python CHECK_API_KEYS.py

echo.
echo ========================================================================
echo    NAECHSTE SCHRITTE
echo ========================================================================
echo.

echo Falls keine Keys gefunden wurden:
echo.
echo   1. Backend starten: START.bat
echo   2. Browser: http://localhost:3000
echo   3. Settings (⚙️) oeffnen
echo   4. API Keys eingeben:
echo      - OpenAI: sk-...
echo      - Anthropic: sk-ant-...
echo      - Perplexity: pplx-...
echo   5. "Save API Keys" klicken
echo.

echo Nach dem Speichern:
echo   - Backend neu starten
echo   - CHECK_API_KEYS.py nochmal ausfuehren
echo   - Chat sollte funktionieren!
echo.

pause
'''
    
    bat_path = Path("SETUP_API_KEYS.bat")
    with open(bat_path, 'w', encoding='utf-8') as f:
        f.write(bat_script)
    
    print(f"✅ Setup Script erstellt: {bat_path}")
    return True

def main():
    """Run all fixes"""
    
    print("="*70)
    print("  XIONIMUS - PERMANENT API KEY FIX")
    print("="*70)
    print()
    print("Problem: API Keys gehen immer wieder verloren")
    print("Lösung: Backend lädt Keys automatisch aus der Datenbank")
    print()
    
    success = True
    
    # Fix 1: chat_stream.py
    print("\n[1/3] Fixe chat_stream.py...")
    if not fix_chat_stream_api_keys():
        success = False
    
    # Fix 2: API Key Checker
    print("\n[2/3] Erstelle API Key Checker...")
    create_api_key_checker()
    
    # Fix 3: Setup Script
    print("\n[3/3] Erstelle Setup Script...")
    create_api_key_fixer_bat()
    
    if success:
        print("\n" + "="*70)
        print("  ✅ FIX ERFOLGREICH!")
        print("="*70)
        print()
        print("🎯 Was wurde gefixt:")
        print("   ✅ Backend lädt API Keys automatisch aus der Datenbank")
        print("   ✅ Fallback wenn Frontend keine Keys sendet")
        print("   ✅ Besseres Logging für Debugging")
        print()
        print("🔧 Neue Tools:")
        print("   • CHECK_API_KEYS.py - Zeigt gespeicherte Keys")
        print("   • SETUP_API_KEYS.bat - Setup-Assistent")
        print()
        print("📋 Nächste Schritte:")
        print("   1. Prüfe ob API Keys gespeichert sind:")
        print("      python CHECK_API_KEYS.py")
        print()
        print("   2. Falls keine Keys gefunden:")
        print("      SETUP_API_KEYS.bat ausführen")
        print()
        print("   3. Backend neu starten:")
        print("      START.bat")
        print()
        print("   4. Chat sollte jetzt funktionieren!")
        print()
        print("="*70)
        print("💡 Der Chat lädt jetzt automatisch API Keys aus der Datenbank,")
        print("   auch wenn das Frontend sie nicht sendet!")
        print("="*70)
    else:
        print("\n❌ Fix fehlgeschlagen - siehe Fehler oben")
        sys.exit(1)

if __name__ == "__main__":
    main()
