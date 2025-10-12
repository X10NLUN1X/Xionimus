#!/usr/bin/env python3
import sys
sys.path.insert(0, 'backend')

from app.database import get_db
from app.models import APIKey

db = next(get_db())
keys = db.query(APIKey).all()

print("\nAPI Keys in Database:")
print("="*50)
for key in keys:
    masked = key.key[:8] + "..." if key.key else "NONE"
    print(f"{key.provider}: {masked}")
print("="*50)
