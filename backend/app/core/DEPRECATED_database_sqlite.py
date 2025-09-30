# ⚠️ DEPRECATED: This file is no longer used
# All database operations have been migrated to database.py (SQLAlchemy ORM)
# This file is kept for reference only and will be removed in a future version

"""
DEPRECATION NOTICE
==================
This module (database_sqlite.py) has been replaced by database.py

Migration completed on: 2025-09-30
Reason: Consolidation of database implementations
New approach: SQLAlchemy ORM only (database.py)

If you see imports of this file, please replace with:
    from app.core.database import get_database

Do NOT use get_sqlite_db() anymore!
"""

import warnings

warnings.warn(
    "database_sqlite.py is deprecated. Use database.py instead.",
    DeprecationWarning,
    stacklevel=2
)

# Keep original code for reference (but mark as deprecated)
# ... (original code remains unchanged)
