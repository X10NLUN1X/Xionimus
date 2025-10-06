#!/usr/bin/env python3
"""
Database Index Initialization Script

Erstellt/prüft Indizes für optimale Query-Performance in SQLite.
Idempotent - kann mehrfach ausgeführt werden ohne Schaden.
"""

import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine, Index, inspect, text
from sqlalchemy.orm import sessionmaker
from app.core.database import engine, Base
from app.models.user_models import User, UploadedFile
from app.models.session_models import Session, Message
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)


class IndexManager:
    """Verwaltet Datenbank-Indizes"""
    
    def __init__(self, db_engine):
        self.engine = db_engine
        self.inspector = inspect(db_engine)
    
    def get_existing_indexes(self, table_name: str) -> set:
        """Gibt existierende Indizes für eine Tabelle zurück"""
        try:
            indexes = self.inspector.get_indexes(table_name)
            return {idx['name'] for idx in indexes}
        except Exception as e:
            logger.warning(f"Konnte Indizes für {table_name} nicht abrufen: {e}")
            return set()
    
    def create_index_if_not_exists(self, index_name: str, table_name: str, columns: list) -> bool:
        """
        Erstellt Index falls er nicht existiert
        
        Returns:
            True wenn Index erstellt wurde, False wenn bereits existiert
        """
        existing_indexes = self.get_existing_indexes(table_name)
        
        if index_name in existing_indexes:
            logger.info(f"   ✓ Index '{index_name}' existiert bereits")
            return False
        
        try:
            # Erstelle Index
            columns_str = ", ".join(columns)
            sql = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({columns_str})"
            
            with self.engine.connect() as conn:
                conn.execute(text(sql))
                conn.commit()
            
            logger.info(f"   ✅ Index '{index_name}' erstellt: {table_name}({columns_str})")
            return True
        except Exception as e:
            logger.error(f"   ❌ Fehler beim Erstellen von Index '{index_name}': {e}")
            return False
    
    def analyze_table(self, table_name: str):
        """Führt ANALYZE aus für bessere Query-Planung"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text(f"ANALYZE {table_name}"))
                conn.commit()
            logger.info(f"   ✅ ANALYZE ausgeführt für {table_name}")
        except Exception as e:
            logger.warning(f"   ⚠️  ANALYZE fehlgeschlagen für {table_name}: {e}")


def init_indexes():
    """Initialisiert alle empfohlenen Indizes"""
    
    print("\n" + "="*70)
    print("🔧 DATENBANK-INDEX INITIALISIERUNG")
    print("="*70 + "\n")
    
    manager = IndexManager(engine)
    
    # Track statistics
    created_count = 0
    existing_count = 0
    
    # ========================================================================
    # USERS TABLE
    # ========================================================================
    print("📊 Users Table")
    print("-" * 70)
    
    # Email & Username sind bereits indexed in Model (unique=True, index=True)
    existing_count += 2
    logger.info("   ✓ Index 'ix_users_email' existiert bereits (Model-definiert)")
    logger.info("   ✓ Index 'ix_users_username' existiert bereits (Model-definiert)")
    
    # Zusätzliche Indizes für häufige Queries
    if manager.create_index_if_not_exists(
        "idx_users_role", "users", ["role"]
    ):
        created_count += 1
    else:
        existing_count += 1
    
    if manager.create_index_if_not_exists(
        "idx_users_is_active", "users", ["is_active"]
    ):
        created_count += 1
    else:
        existing_count += 1
    
    if manager.create_index_if_not_exists(
        "idx_users_github_username", "users", ["github_username"]
    ):
        created_count += 1
    else:
        existing_count += 1
    
    if manager.create_index_if_not_exists(
        "idx_users_last_login", "users", ["last_login"]
    ):
        created_count += 1
    else:
        existing_count += 1
    
    # ========================================================================
    # SESSIONS TABLE
    # ========================================================================
    print("\n📊 Sessions Table")
    print("-" * 70)
    
    if manager.create_index_if_not_exists(
        "idx_sessions_user_id", "sessions", ["user_id"]
    ):
        created_count += 1
    else:
        existing_count += 1
    
    if manager.create_index_if_not_exists(
        "idx_sessions_workspace_id", "sessions", ["workspace_id"]
    ):
        created_count += 1
    else:
        existing_count += 1
    
    if manager.create_index_if_not_exists(
        "idx_sessions_created_at", "sessions", ["created_at"]
    ):
        created_count += 1
    else:
        existing_count += 1
    
    if manager.create_index_if_not_exists(
        "idx_sessions_updated_at", "sessions", ["updated_at"]
    ):
        created_count += 1
    else:
        existing_count += 1
    
    # Composite Index für häufige User-Session Queries
    if manager.create_index_if_not_exists(
        "idx_sessions_user_updated", "sessions", ["user_id", "updated_at"]
    ):
        created_count += 1
    else:
        existing_count += 1
    
    # ========================================================================
    # MESSAGES TABLE
    # ========================================================================
    print("\n📊 Messages Table")
    print("-" * 70)
    
    if manager.create_index_if_not_exists(
        "idx_messages_session_id", "messages", ["session_id"]
    ):
        created_count += 1
    else:
        existing_count += 1
    
    if manager.create_index_if_not_exists(
        "idx_messages_timestamp", "messages", ["timestamp"]
    ):
        created_count += 1
    else:
        existing_count += 1
    
    if manager.create_index_if_not_exists(
        "idx_messages_role", "messages", ["role"]
    ):
        created_count += 1
    else:
        existing_count += 1
    
    if manager.create_index_if_not_exists(
        "idx_messages_parent_id", "messages", ["parent_message_id"]
    ):
        created_count += 1
    else:
        existing_count += 1
    
    # Composite Index für Chat-Historie Queries
    if manager.create_index_if_not_exists(
        "idx_messages_session_timestamp", "messages", ["session_id", "timestamp"]
    ):
        created_count += 1
    else:
        existing_count += 1
    
    # ========================================================================
    # UPLOADED_FILES TABLE
    # ========================================================================
    print("\n📊 Uploaded Files Table")
    print("-" * 70)
    
    if manager.create_index_if_not_exists(
        "idx_uploaded_files_user_id", "uploaded_files", ["user_id"]
    ):
        created_count += 1
    else:
        existing_count += 1
    
    if manager.create_index_if_not_exists(
        "idx_uploaded_files_uploaded_at", "uploaded_files", ["uploaded_at"]
    ):
        created_count += 1
    else:
        existing_count += 1
    
    if manager.create_index_if_not_exists(
        "idx_uploaded_files_mime_type", "uploaded_files", ["mime_type"]
    ):
        created_count += 1
    else:
        existing_count += 1
    
    # Composite Index für User File Queries
    if manager.create_index_if_not_exists(
        "idx_uploaded_files_user_uploaded", "uploaded_files", ["user_id", "uploaded_at"]
    ):
        created_count += 1
    else:
        existing_count += 1
    
    # ========================================================================
    # ANALYZE TABLES
    # ========================================================================
    print("\n📊 Optimiere Query-Planung")
    print("-" * 70)
    
    for table in ["users", "sessions", "messages", "uploaded_files"]:
        manager.analyze_table(table)
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    print("\n" + "="*70)
    print("📊 INDEX INITIALISIERUNG ABGESCHLOSSEN")
    print("="*70)
    print(f"✅ Neue Indizes erstellt:     {created_count}")
    print(f"✓  Existierende Indizes:      {existing_count}")
    print(f"📈 Gesamt-Indizes:            {created_count + existing_count}")
    print("="*70 + "\n")
    
    # ========================================================================
    # RECOMMENDATIONS
    # ========================================================================
    print("💡 EMPFEHLUNGEN")
    print("-" * 70)
    print("1. Führe dieses Script nach größeren Schema-Änderungen aus")
    print("2. Bei Performance-Problemen: EXPLAIN QUERY PLAN überprüfen")
    print("3. Regelmäßig VACUUM ausführen (SQLite Optimization)")
    print("4. Bei sehr großen Datenmenken: Archivierungs-Strategie erwägen")
    print("="*70 + "\n")
    
    return created_count


def show_index_status():
    """Zeigt aktuelle Index-Status für alle Tabellen"""
    print("\n" + "="*70)
    print("📊 AKTUELLER INDEX-STATUS")
    print("="*70 + "\n")
    
    manager = IndexManager(engine)
    
    for table_name in ["users", "sessions", "messages", "uploaded_files"]:
        print(f"📋 {table_name.upper()}")
        print("-" * 70)
        
        try:
            indexes = manager.inspector.get_indexes(table_name)
            if indexes:
                for idx in indexes:
                    cols = ", ".join(idx['column_names'])
                    unique = " (UNIQUE)" if idx.get('unique') else ""
                    print(f"   ✓ {idx['name']}: {cols}{unique}")
            else:
                print("   ⚠️  Keine expliziten Indizes")
        except Exception as e:
            print(f"   ❌ Fehler: {e}")
        
        print()
    
    print("="*70 + "\n")


def vacuum_database():
    """Führt VACUUM aus für SQLite Optimization"""
    print("\n" + "="*70)
    print("🧹 DATENBANK OPTIMIZATION (VACUUM)")
    print("="*70 + "\n")
    
    try:
        with engine.connect() as conn:
            # Close all other connections first
            conn.execute(text("PRAGMA optimize"))
            conn.commit()
            
            logger.info("✅ PRAGMA optimize ausgeführt")
            
            # VACUUM (kann nicht in Transaction laufen)
            conn.execute(text("VACUUM"))
            logger.info("✅ VACUUM ausgeführt - Datenbankdatei optimiert")
            
    except Exception as e:
        logger.error(f"❌ VACUUM fehlgeschlagen: {e}")
    
    print("="*70 + "\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Datenbank Index Management")
    parser.add_argument("--status", action="store_true", help="Zeige Index-Status")
    parser.add_argument("--vacuum", action="store_true", help="Führe VACUUM aus")
    parser.add_argument("--all", action="store_true", help="Führe alles aus (init + vacuum)")
    
    args = parser.parse_args()
    
    try:
        if args.status:
            show_index_status()
        elif args.vacuum:
            vacuum_database()
        elif args.all:
            init_indexes()
            vacuum_database()
            show_index_status()
        else:
            # Default: Nur Indizes initialisieren
            init_indexes()
        
        print("✅ Erfolgreich abgeschlossen\n")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
