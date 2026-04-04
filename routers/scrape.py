"""抓取相关路由"""
import time
from fastapi import APIRouter, HTTPException, Header, Depends
from typing import Optional

from models import ScrapeRequest, ExtractRequest, ScrapeResponse, Metadata
from services.scraper import scrape_url, extract_content
from services.cache import get_cached, set_cached
from services.auth import verify_api_key
from config import settings
from utils import generate_cache_key, measure_time


router = APIRouter()


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_endpoint(
    request: ScrapeRequest,
    api_key: str = Header(..., alias=settings.api_key_header),
):
    """
    基础抓取端点
    """
    # 验证 API Key
    key_info = await verify_api_key(api_key)
    if not key_info:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key",
        )
    
    # 检查缓存
    cache_key = generate_cache_key(request.url, request.selector)
    cached_result = await get_cached(cache_key)
    
    if cached_result:
        return ScrapeResponse(
            success=True,
            data=cached_result.get("data"),
            text=cached_result.get("text"),
            metadata=Metadata(
                url=request.url,
                status_code=cached_result.get("status_code", 200),
                response_time_ms=0,
                credits_used=0,
                cached=True,
            ),
        )
    
    # 执行抓取
    start_time = time.perf_counter()
    
    try:
        result = await scrape_url(
            url=request.url,
            selector=request.selector,
            output_format=request.format,
            timeout=request.timeout,
        )
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        # 缓存结果
        await set_cached(cache_key, result, ttl=settings.cache_ttl)
        
        return ScrapeResponse(
            success=True,
            data=result.get("data"),
            text=result.get("text"),
            metadata=Metadata(
                url=request.url,
                status_code=result.get("status_code", 200),
                response_time_ms=elapsed_ms,
                credits_used=1,
                cached=False,
            ),
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Scraping failed: {str(e)}",
        )


@router.post("/extract", response_model=ScrapeResponse)
async def extract_endpoint(
    request: ExtractRequest,
    api_key: str = Header(..., alias=settings.api_key_header),
):
    """
    智能提取端点
    """
    # 验证 API Key
    key_info = await verify_api_key(api_key)
    if not key_info:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key",
        )
    
    # 执行智能提取
    start_time = time.perf_counter()
    
    try:
        result = await extract_content(
            url=request.url,
            extract_type=request.extract_type,
            custom_schema=request.custom_schema,
        )
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        
        return ScrapeResponse(
            success=True,
            data=result.get("data"),
            text=result.get("text"),
            metadata=Metadata(
                url=request.url,
                status_code=result.get("status_code", 200),
                response_time_ms=elapsed_ms,
                credits_used=1,
                cached=False,
            ),
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Extraction failed: {str(e)}",
        )
