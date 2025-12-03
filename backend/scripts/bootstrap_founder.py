#!/usr/bin/env python3
"""Bootstrap Founder Admin Account"""
import asyncio
import sys
import os
sys.path.insert(0, '/app/backend')

from server import db, hash_password
from datetime import datetime, timezone

async def bootstrap_founder():
    email = os.environ.get("FOUNDER_EMAIL", "founder@gitpusher.ai")
    password = os.environ.get("FOUNDER_PASSWORD", "FounderAdmin2024!")
    
    existing = await db.users.find_one({"email": email})
    if existing:
        print(f"✅ Founder admin already exists: {email}")
        result = await db.users.update_one(
            {"email": email},
            {"$set": {"role": "FOUNDER_ADMIN", "is_admin": True}}
        )
        print(f"✅ Role updated to FOUNDER_ADMIN: {result.modified_count} doc(s)")
        return
    
    user_id = f"founder-{int(datetime.now(timezone.utc).timestamp())}"
    await db.users.insert_one({
        "_id": user_id,
        "email": email,
        "password": hash_password(password),
        "display_name": "Founder",
        "role": "FOUNDER_ADMIN",
        "is_admin": True,
        "credits": 999999,
        "plan": "business",
        "created_at": datetime.now(timezone.utc).isoformat()
    })
    
    print(f"✅ Founder admin created: {email}")
    print(f"   Role: FOUNDER_ADMIN")
    print(f"   Password: {password}")

if __name__ == "__main__":
    asyncio.run(bootstrap_founder())
