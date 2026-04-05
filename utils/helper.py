"""工具函数"""
import time
import hashlib
from typing import Optional
from functools import wraps

def measure_time(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = await func(*args, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
        if isinstance(result, dict):
            result["_elapsed_ms"] = elapsed_ms
        return result
    return wrapper

def generate_cache_key(url: str, selector: Optional[str] = None) -> str:
    content = f"{url}:{selector or ''}"
    return hashlib.md5(content.encode()).hexdigest()

def normalize_url(url: str) -> str:
    url = url.strip()
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    return url

def truncate_text(text: str, max_length: int = 10000) -> str:
    if len(text) > max_length:
        return text[:max_length] + "...[truncated]"
    return text
