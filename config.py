"""配置管理"""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    
    # 基础配置
    app_name: str = "WebScrape API"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API 配置
    api_key_header: str = "X-API-Key"
    master_api_key: str = "sk_demo_key_please_change_in_production"
    
    # 抓取配置
    default_timeout: int = 30
    max_timeout: int = 60
    max_retries: int = 3
    user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    
    # 缓存配置
    cache_enabled: bool = True
    cache_ttl: int = 3600  # 1小时
    cache_db_path: str = "data/cache.db"
    
    # 配额配置
    free_tier_limit: int = 100
    basic_tier_limit: int = 5000
    pro_tier_limit: int = 25000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# 单例
settings = Settings()

# 确保数据目录存在
os.makedirs("data", exist_ok=True)
