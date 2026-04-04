"""缓存服务"""
import sqlite3
import os
import json
from typing import Optional, Any
from datetime import datetime, timedelta

from config import settings


DB_PATH = settings.cache_db_path


def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


async def init_cache_db():
    """初始化缓存数据库"""
    os.makedirs("data", exist_ok=True)
    
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cache (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP
        )
    """)
    
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_cache_expires 
        ON cache(expires_at)
    """)
    
    conn.commit()
    conn.close()
    
    await cleanup_expired_cache()


async def get_cached(key: str) -> Optional[dict]:
    """获取缓存"""
    if not settings.cache_enabled:
        return None
    
    conn = get_db()
    cursor = conn.execute(
        """
        SELECT value, expires_at FROM cache 
        WHERE key = ? AND (expires_at IS NULL OR expires_at > ?)
        """,
        (key, datetime.utcnow().isoformat()),
    )
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
    
    try:
        return json.loads(row["value"])
    except json.JSONDecodeError:
        return None


async def set_cached(key: str, value: dict, ttl: int = None) -> None:
    """设置缓存"""
    if not settings.cache_enabled:
        return
    
    ttl = ttl or settings.cache_ttl
    expires_at = datetime.utcnow() + timedelta(seconds=ttl)
    
    conn = get_db()
    conn.execute(
        """
        INSERT OR REPLACE INTO cache (key, value, created_at, expires_at)
        VALUES (?, ?, ?, ?)
        """,
        (key, json.dumps(value), datetime.utcnow().isoformat(), expires_at.isoformat()),
    )
    conn.commit()
    conn.close()


async def delete_cached(key: str) -> None:
    """删除缓存"""
    conn = get_db()
    conn.execute("DELETE FROM cache WHERE key = ?", (key,))
    conn.commit()
    conn.close()


async def cleanup_expired_cache() -> int:
    """清理过期缓存"""
    conn = get_db()
    cursor = conn.execute(
        "DELETE FROM cache WHERE expires_at < ?",
        (datetime.utcnow().isoformat(),),
    )
    deleted = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted


async def get_cache_stats() -> dict:
    """获取缓存统计"""
    conn = get_db()
    
    total = conn.execute("SELECT COUNT(*) as count FROM cache").fetchone()["count"]
    
    valid = conn.execute(
        """
        SELECT COUNT(*) as count FROM cache 
        WHERE expires_at IS NULL OR expires_at > ?
        """,
        (datetime.utcnow().isoformat(),),
    ).fetchone()["count"]
    
    expired = total - valid
    
    conn.close()
    
    return {"total": total, "valid": valid, "expired": expired}
