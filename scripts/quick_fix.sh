#!/bin/bash
# =============================================================================
# Xionimus Genesis - Quick Fix Script
# =============================================================================
# Behebt die kritischsten Probleme automatisch
# Verwendung: bash quick_fix.sh

set -e  # Exit on error

echo "🔧 Xionimus Genesis - Quick Fix Script"
echo "======================================"
echo ""

# =============================================================================
# 1. .env Datei erstellen
# =============================================================================
echo "📝 [1/5] Checking .env file..."
if [ ! -f /app/backend/.env ]; then
  echo "   Creating .env from template..."
  cp /app/backend/.env.example /app/backend/.env
  
  # Generate SECRET_KEY
  if command -v openssl &> /dev/null; then
    SECRET_KEY=$(openssl rand -hex 32)
    echo "SECRET_KEY=$SECRET_KEY" >> /app/backend/.env
    echo "   ✅ .env created with SECRET_KEY"
  else
    echo "   ⚠️  openssl not found - please set SECRET_KEY manually"
  fi
else
  echo "   ✅ .env already exists"
fi

# =============================================================================
# 2. Dead Code entfernen
# =============================================================================
echo ""
echo "🗑️  [2/5] Removing dead code..."
if [ -f /app/frontend/src/App_old.tsx ]; then
  rm -f /app/frontend/src/App_old.tsx
  echo "   ✅ Removed App_old.tsx"
else
  echo "   ℹ️  App_old.tsx already removed"
fi

# =============================================================================
# 3. Trailing Slash Fix für API Endpoint
# =============================================================================
echo ""
echo "🔧 [3/5] Fixing 307 redirect issue..."
if grep -q "'/api/chat'" /app/frontend/src/contexts/AppContext.tsx; then
  sed -i "s|'/api/chat'|'/api/chat/'|g" /app/frontend/src/contexts/AppContext.tsx
  echo "   ✅ Fixed trailing slash in API endpoint"
else
  echo "   ℹ️  Already fixed or not found"
fi

# =============================================================================
# 4. Dependencies Check
# =============================================================================
echo ""
echo "📦 [4/5] Checking dependencies..."
if [ -d /app/backend/venv ]; then
  cd /app/backend
  source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null
  pip list --outdated > /tmp/outdated_pip.txt 2>&1
  echo "   ✅ Python dependency report: /tmp/outdated_pip.txt"
else
  echo "   ⚠️  Backend venv not found"
fi

if [ -d /app/frontend/node_modules ]; then
  cd /app/frontend
  yarn outdated > /tmp/outdated_yarn.txt 2>&1 || true
  echo "   ✅ Node dependency report: /tmp/outdated_yarn.txt"
else
  echo "   ⚠️  Frontend node_modules not found"
fi

# =============================================================================
# 5. Backup Creation
# =============================================================================
echo ""
echo "💾 [5/5] Creating backup..."
BACKUP_DIR="/tmp/xionimus_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
if [ -f /app/backend/.env ]; then
  cp /app/backend/.env "$BACKUP_DIR/.env"
fi
if [ -f ~/.xionimus_ai/xionimus.db ]; then
  cp ~/.xionimus_ai/xionimus.db "$BACKUP_DIR/xionimus.db"
fi
echo "   ✅ Backup created: $BACKUP_DIR"

# =============================================================================
# Summary
# =============================================================================
echo ""
echo "✅ Quick fixes complete!"
echo ""
echo "📋 Summary:"
echo "   1. .env configuration"
echo "   2. Dead code removed"
echo "   3. API endpoint fixed"
echo "   4. Dependencies checked"
echo "   5. Backup created"
echo ""
echo "📝 Next Steps:"
echo "   - Review: /app/COMPREHENSIVE_AUDIT_REPORT.md"
echo "   - Check outdated deps: /tmp/outdated_*.txt"
echo "   - Restart services: sudo supervisorctl restart all"
echo ""
echo "⚠️  For critical issues, see audit report Phase 1"
