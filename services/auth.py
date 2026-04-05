"""API Key 认证服务"""
import sqlite3
import os
from typing import Optional
from datetime import datetime
import secrets
from models import APIKeyInfo
from config import settings

DB_PATH = "data/auth.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

async def init_auth_db():
    os.makedirs("data", exist_ok=True)
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS api_keys (key TEXT PRIMARY KEY, tier TEXT NOT NULL DEFAULT 'free', usage INTEGER DEFAULT 0, "limit" INTEGER DEFAULT 100, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, last_used_at TIMESTAMP)""")
    conn.commit()
    conn.close()

async def verify_api_key(api_key: str) -> Optional[APIKeyInfo]:
    conn = get_db()
    cursor = conn.execute("SELECT * FROM api_keys WHERE key = ?", (api_key,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    if row["usage"] >= row["limit"]:
        conn.close()
        return None
    conn.execute("UPDATE api_keys SET usage = usage + 1, last_used_at = ? WHERE key = ?", (datetime.utcnow().isoformat(), api_key))
    conn.commit()
    conn.close()
    return APIKeyInfo(key=row["key"], tier=row["tier"], usage=row["usage"] + 1, limit=row["limit"], created_at=datetime.fromisoformat(row["created_at"]))

async def create_api_key(tier: str = "free") -> APIKeyInfo:
    key = f"sk_live_{secrets.token_hex(24)}"
    limits = {"free": settings.free_tier_limit, "basic": settings.basic_tier_limit, "pro": settings.pro_tier_limit}
    limit = limits.get(tier, settings.free_tier_limit)
    conn = get_db()
    conn.execute("INSERT INTO api_keys (key, tier, usage, \"limit\", created_at) VALUES (?, ?, 0, ?, ?)", (key, tier, limit, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()
    return APIKeyInfo(key=key, tier=tier, usage=0, limit=limit)

async def get_key_info(api_key: str) -> Optional[APIKeyInfo]:
    conn = get_db()
    cursor = conn.execute("SELECT * FROM api_keys WHERE key = ?", (api_key,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return APIKeyInfo(key=row["key"], tier=row["tier"], usage=row["usage"], limit=row["limit"], created_at=datetime.fromisoformat(row["created_at"]))


async def update_api_key_tier(api_key: str, tier: str) -> bool:
    """
    更新API Key的套餐等级
    
    Args:
        api_key: API Key
        tier: 套餐类型 (basic, pro, enterprise)
    
    Returns:
        是否更新成功
    """
    limits = {
        "free": settings.free_tier_limit,
        "basic": settings.basic_tier_limit,
        "pro": settings.pro_tier_limit,
        "enterprise": 999999999,  # 企业版无限制
    }
    new_limit = limits.get(tier, settings.free_tier_limit)
    
    conn = get_db()
    try:
        conn.execute(
            "UPDATE api_keys SET tier = ?, \"limit\" = ? WHERE key = ?",
            (tier, new_limit, api_key)
        )
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        conn.close()
        print(f"[Auth] 更新套餐失败: {e}")
        return False
