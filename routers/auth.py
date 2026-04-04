"""认证相关路由"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from models import APIKeyInfo
from services.auth import verify_api_key, create_api_key, get_key_info
from config import settings


router = APIRouter()


class CreateKeyRequest(BaseModel):
    """创建 API Key 请求"""
    tier: str = "free"
    master_key: str


class KeyResponse(BaseModel):
    """Key 响应"""
    success: bool
    api_key: str
    tier: str
    limit: int


@router.post("/keys", response_model=KeyResponse)
async def create_key(request: CreateKeyRequest):
    """
    创建新的 API Key（需要 Master Key）
    """
    if request.master_key != settings.master_api_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid master key",
        )
    
    key_info = await create_api_key(tier=request.tier)
    
    return KeyResponse(
        success=True,
        api_key=key_info.key,
        tier=key_info.tier,
        limit=key_info.limit,
    )


@router.get("/keys/info")
async def key_info(api_key: str):
    """
    查询 API Key 信息
    """
    info = await get_key_info(api_key)
    
    if not info:
        raise HTTPException(
            status_code=404,
            detail="API Key not found",
        )
    
    return {
        "success": True,
        "tier": info.tier,
        "usage": info.usage,
        "limit": info.limit,
        "remaining": max(0, info.limit - info.usage),
    }
