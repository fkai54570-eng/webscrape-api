"""支付相关路由"""
import time
import hashlib
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from config import settings
from services.alipay import alipay_service
from services.cache import set_cached, get_cached


router = APIRouter()


# 套餐定价（元）
TIER_PRICES = {
    "basic": 9.9,    # Basic 套餐
    "pro": 29.9,     # Pro 套餐
    "enterprise": 99.9,  # 企业套餐
}

TIER_NAMES = {
    "basic": "Basic 套餐 (5000次/天)",
    "pro": "Pro 套餐 (25000次/天)",
    "enterprise": "企业套餐 (无限制)",
}


class CreateOrderRequest(BaseModel):
    """创建订单请求"""
    tier: str  # basic, pro, enterprise
    api_key: Optional[str] = None  # 用户的API Key（可选，测试时可不填）


class OrderResponse(BaseModel):
    """订单响应"""
    success: bool
    out_trade_no: str
    pay_url: Optional[str] = None
    app_pay_params: Optional[dict] = None
    qr_code: Optional[str] = None
    amount: float
    tier: str
    message: Optional[str] = None


@router.post("/pay/create-order", response_model=OrderResponse)
async def create_order(request: CreateOrderRequest):
    """
    创建支付订单
    
    返回支付链接或APP支付参数
    """
    print(f"[Pay] 收到创建订单请求: tier={request.tier}")
    
    # 验证套餐
    tier = request.tier.lower()
    if tier not in TIER_PRICES:
        print(f"[Pay] 无效的套餐类型: {tier}")
        raise HTTPException(status_code=400, detail="无效的套餐类型")
    
    print(f"[Pay] 套餐验证通过: {tier}, 价格: {TIER_PRICES[tier]}")
    
    # 验证API Key（确保用户存在）- 可选，不提供也能创建订单用于测试
    if request.api_key:
        from services.auth import verify_api_key
        key_info = await verify_api_key(request.api_key)
        if not key_info:
            raise HTTPException(status_code=401, detail="无效的API Key")
    
    # 生成订单
    out_trade_no = alipay_service.generate_out_trade_no()
    amount = TIER_PRICES[tier]
    subject = TIER_NAMES[tier]
    
    # 临时存储订单信息（30分钟有效）
    order_key = f"order:{out_trade_no}"
    order_data = {
        "out_trade_no": out_trade_no,
        "tier": tier,
        "api_key": request.api_key,
        "amount": amount,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }
    await set_cached(order_key, order_data, ttl=1800)
    
    try:
        print(f"[Pay] 生成订单号: {out_trade_no}")
        
        # 创建电脑网站支付链接
        pay_url = alipay_service.create_trade_page_url(
            out_trade_no=out_trade_no,
            total_amount=amount,
            subject=f"WebScrape API - {subject}",
            body=f"购买{subject}",
            timeout_express="30m",
        )
        
        print(f"[Pay] 支付链接创建成功: {pay_url}")
        
        return OrderResponse(
            success=True,
            out_trade_no=out_trade_no,
            pay_url=pay_url,
            amount=amount,
            tier=tier,
            message="请在浏览器打开支付链接完成付款",
        )
        
    except Exception as e:
        import traceback
        print(f"[Pay] 创建订单失败: {e}")
        print(f"[Pay] 详细错误: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"创建订单失败: {str(e)}")


@router.get("/pay/query/{out_trade_no}")
async def query_order(out_trade_no: str):
    """
    查询订单状态
    """
    try:
        result = alipay_service.query_trade(out_trade_no)
        
        trade_status = result.get("trade_status")
        status_map = {
            "WAIT_BUYER_PAY": "等待支付",
            "TRADE_CLOSED": "交易关闭",
            "TRADE_SUCCESS": "支付成功",
            "TRADE_FINISHED": "交易完成",
        }
        
        return {
            "success": True,
            "out_trade_no": out_trade_no,
            "trade_status": trade_status,
            "status_text": status_map.get(trade_status, trade_status),
            "response": result,
        }
        
    except Exception as e:
        return {
            "success": False,
            "out_trade_no": out_trade_no,
            "error": str(e),
        }


@router.post("/pay/notify")
async def pay_notify(request: Request):
    """
    支付宝异步回调通知
    
    注意：这个接口需要公网可访问
    """
    # 获取回调数据
    form_data = await request.form()
    data = dict(form_data)
    
    # 记录原始数据（调试用）
    print(f"[PayNotify] 收到回调: {data}")
    
    # 验证签名
    if not alipay_service.verify_notification(data):
        print("[PayNotify] 签名验证失败")
        return "fail"
    
    out_trade_no = data.get("out_trade_no")
    trade_status = data.get("trade_status")
    
    # 查询订单信息
    order_key = f"order:{out_trade_no}"
    order_data = await get_cached(order_key)
    
    if not order_data:
        print(f"[PayNotify] 订单不存在: {out_trade_no}")
        return "fail"
    
    if trade_status == "TRADE_SUCCESS":
        # 支付成功，更新套餐
        tier = order_data.get("tier")
        api_key = order_data.get("api_key")
        
        # 更新用户的套餐
        from services.auth import update_api_key_tier
        await update_api_key_tier(api_key, tier)
        
        # 更新订单状态
        order_data["status"] = "paid"
        order_data["paid_at"] = datetime.now().isoformat()
        order_data["trade_no"] = data.get("trade_no")
        await set_cached(order_key, order_data, ttl=86400 * 7)  # 保存7天
        
        print(f"[PayNotify] 支付成功: {out_trade_no}, 套餐: {tier}, API Key: {api_key}")
        
        return "success"
    
    return "success"


@router.get("/pay/packages")
async def get_packages():
    """
    获取套餐列表
    """
    return {
        "success": True,
        "packages": [
            {
                "tier": "basic",
                "name": "Basic 套餐",
                "price": TIER_PRICES["basic"],
                "daily_limit": 5000,
                "features": ["5000次/天", "基础支持", "1个月有效期"],
            },
            {
                "tier": "pro",
                "name": "Pro 套餐",
                "price": TIER_PRICES["pro"],
                "daily_limit": 25000,
                "features": ["25000次/天", "优先支持", "1个月有效期", "缓存加速"],
            },
            {
                "tier": "enterprise",
                "name": "企业套餐",
                "price": TIER_PRICES["enterprise"],
                "daily_limit": -1,  # 无限制
                "features": ["无限制", "专属支持", "1个月有效期", "缓存加速", "自定义配置"],
            },
        ],
        "currency": "CNY",
    }
