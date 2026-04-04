"""FastAPI 应用入口"""
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import settings
from routers import scrape, auth
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


@app.get("/", response_class=JSONResponse)
async def root():
    """根路径"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/api/health",
    }


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
