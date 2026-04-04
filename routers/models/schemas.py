"""Pydantic 数据模型"""
from typing import Optional, Dict, List, Any, Literal
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from datetime import datetime


# ============ 请求模型 ============

class ScrapeRequest(BaseModel):
    """基础抓取请求"""
    url: str = Field(..., description="要抓取的URL")
    selector: Optional[str] = Field(None, description="CSS选择器，多个用逗号分隔")
    format: Literal["json", "text", "markdown"] = Field("json", description="输出格式")
    timeout: int = Field(30, ge=5, le=60, description="超时秒数")


class ExtractRequest(BaseModel):
    """智能提取请求"""
    model_config = ConfigDict(populate_by_name=True)
    
    url: str = Field(..., description="要抓取的URL")
    extract_type: Literal["article", "product", "links", "images"] = Field(
        ..., description="提取类型"
    )
    custom_schema: Optional[Dict[str, str]] = Field(
        None, 
        alias="schema",
        description="自定义提取规则"
    )


# ============ 响应模型 ============

class Metadata(BaseModel):
    """响应元数据"""
    url: str
    status_code: int
    response_time_ms: float
    credits_used: int = 1
    cached: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ScrapeResponse(BaseModel):
    """抓取响应"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    text: Optional[str] = None
    metadata: Metadata
    error: Optional[str] = None


class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    error: str
    error_code: str
    detail: Optional[str] = None


class HealthResponse(BaseModel):
    """健康检查响应"""
    status: str = "ok"
    version: str
    uptime_seconds: float


# ============ 认证模型 ============

class APIKeyInfo(BaseModel):
    """API Key 信息"""
    key: str
    tier: str = "free"
    usage: int = 0
    limit: int = 100
    created_at: datetime = Field(default_factory=datetime.utcnow)
