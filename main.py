"""FastAPI 应用入口"""
import time
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse

from config import settings
from routers import scrape, auth, pay
from models import HealthResponse


# 应用启动时间
START_TIME = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    print(f"🚀 {settings.app_name} v{settings.app_version} 启动中...")

    # 初始化数据库
    from services.cache import init_cache_db
    from services.auth import init_auth_db
    await init_cache_db()
    await init_auth_db()

    yield

    # 关闭时
    print(f"👋 {settings.app_name} 关闭中...")


# 创建应用
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="简单易用的网页数据抓取 API 服务",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(scrape.router, prefix="/api", tags=["抓取"])
app.include_router(auth.router, prefix="/api", tags=["认证"])
app.include_router(pay.router, prefix="/api", tags=["支付"])


@app.get("/", response_class=HTMLResponse)
async def index():
    """前端页面"""
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    if os.path.exists(html_path):
        with open(html_path, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return HTMLResponse("<h1>WebScrape API</h1><p>前端页面未找到</p>")


@app.post("/api/web/scrape")
async def web_scrape(request: Request):
    """网页端抓取接口（免费，有限额）"""
    body = await request.json()
    url = body.get("url", "").strip()
    extract_type = body.get("extract_type", "full")
    selector = body.get("selector", "").strip()

    if not url:
        return JSONResponse(status_code=400, content={"success": False, "error": "请输入URL"})

    # 基于IP的简单限额
    from services.cache import get_cached, set_cached
    client_ip = request.client.host if request.client else "unknown"
    usage_key = f"web_usage:{client_ip}"
    usage = await get_cached(usage_key)
    if usage and usage.get("count", 0) >= 50:
        return JSONResponse(status_code=429, content={"success": False, "error": "今日免费次数已用完(50次/天)", "code": "RATE_LIMIT"})

    try:
        if selector:
            result = await scrape_url(url=url, selector=selector if selector else None, output_format="json")
        elif extract_type == "article":
            result = await extract_content(url=url, extract_type="article")
        elif extract_type == "links":
            result = await extract_content(url=url, extract_type="links")
        elif extract_type == "images":
            result = await extract_content(url=url, extract_type="images")
        else:
            result = await scrape_url(url=url, output_format="json")

        # 记录使用次数
        current_count = usage.get("count", 0) if usage else 0
        await set_cached(usage_key, {"count": current_count + 1}, ttl=86400)

        result["success"] = True
        remaining = 50 - current_count - 1
        result["remaining"] = remaining
        return JSONResponse(content=result)

    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": f"抓取失败: {str(e)}"})


@app.get("/api/health", response_model=HealthResponse)
async def health():
    """健康检查"""
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        uptime_seconds=time.time() - START_TIME,
    )


# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal Server Error",
            "error_code": "INTERNAL_ERROR",
            "detail": str(exc) if settings.debug else None,
        },
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
