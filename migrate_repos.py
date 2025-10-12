import os
import sys
from pathlib import Path
import shutil

def migrate_existing_repos():
    '''Migrate repos from /app to backend/workspace/github_imports'''
    
    old_workspace = Path("/app")
    new_workspace = Path(__file__).parent / "backend" / "workspace" / "github_imports"
    
    if not old_workspace.exists():
        print("Keine alten Repos gefunden in /app")
        return
    
    # Create anonymous user directory for migration
    anonymous_dir = new_workspace / "anonymous"
    anonymous_dir.mkdir(parents=True, exist_ok=True)
    
    migrated = 0
    for item in old_workspace.iterdir():
        if item.is_dir() and not item.name.startswith('.'):
            target = anonymous_dir / item.name
            
            if target.exists():
                print(f"⚠️  Überspringe {item.name} (existiert bereits)")
                continue
            
            try:
                shutil.move(str(item), str(target))
                print(f"✅ Migriert: {item.name}")
                migrated += 1
            except Exception as e:
                print(f"❌ Fehler bei {item.name}: {e}")
    
    print(f"\n✅ Migration abgeschlossen: {migrated} Repositories migriert")
    print(f"Neue Location: {anonymous_dir}")

if __name__ == "__main__":
    migrate_existing_repos()
