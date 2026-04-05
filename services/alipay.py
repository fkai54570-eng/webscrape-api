"""支付宝支付服务 - 新版SDK"""
import json
import time
import uuid
from typing import Optional
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest
from alipay.aop.api.request.AlipayTradeQueryRequest import AlipayTradeQueryRequest

from config import settings


# 沙箱网关
SANDBOX_GATEWAY = "https://openapi-sandbox.dl.alipaydev.com/gateway.do"
PRODUCTION_GATEWAY = "https://openapi.alipay.com/gateway.do"


class AlipayService:
    """支付宝支付服务"""
    
    _client: Optional[DefaultAlipayClient] = None
    
    def __init__(self):
        pass  # 延迟初始化
    
    def _normalize_key(self, key: str, key_type: str = "private") -> str:
        """标准化密钥格式 - 保持原始格式"""
        if not key:
            return key
        
        # 如果是PEM格式，直接返回（SDK内部会处理）
        if "-----BEGIN" in key:
            print(f"[Alipay] {key_type} key 是PEM格式，直接使用")
            return key
        
        # 如果是纯Base64（可能带换行的\n转义），也直接返回
        print(f"[Alipay] {key_type} key 长度: {len(key)}")
        return key
    
    @property
    def client(self) -> DefaultAlipayClient:
        """延迟初始化客户端"""
        if self._client is None:
            print(f"[Alipay] 初始化客户端...")
            print(f"[Alipay] app_id: {settings.alipay_app_id}")
            print(f"[Alipay] gateway: {'沙箱' if settings.alipay_sandbox else '正式'}")
            
            # 获取处理后的密钥（自动处理 PEM 格式）
            private_key = settings.get_alipay_private_key()
            public_key = settings.get_alipay_public_key()
            
            # 标准化格式
            private_key = self._normalize_key(private_key, "private")
            public_key = self._normalize_key(public_key, "public")
            
            print(f"[Alipay] final private_key length: {len(private_key)}")
            print(f"[Alipay] final private_key sample: {private_key[:30]}...{private_key[-30:]}")
            print(f"[Alipay] final public_key length: {len(public_key)}")
            
            self._client = self._init_client(private_key, public_key)
            print(f"[Alipay] 客户端初始化完成")
        return self._client
    
    def _init_client(self, private_key: str, public_key: str) -> DefaultAlipayClient:
        """初始化支付宝客户端"""
        alipay_client_config = AlipayClientConfig()
        
        # 设置网关
        gateway = SANDBOX_GATEWAY if settings.alipay_sandbox else PRODUCTION_GATEWAY
        alipay_client_config.server_url = gateway
        
        # 设置应用配置
        alipay_client_config.app_id = settings.alipay_app_id
        alipay_client_config.app_private_key = private_key
        alipay_client_config.alipay_public_key = public_key
        alipay_client_config.sign_type = "RSA2"
        
        return DefaultAlipayClient(alipay_client_config)
    
    def create_trade_page_url(
        self,
        out_trade_no: str,
        total_amount: float,
        subject: str,
        body: str = "",
        timeout_express: str = "30m",
    ) -> str:
        """
        创建电脑网站支付链接
        
        Args:
            out_trade_no: 商户订单号
            total_amount: 订单金额（元）
            subject: 订单标题
            body: 订单描述
            timeout_express: 支付超时时间
        
        Returns:
            支付跳转URL
        """
        print(f"[Alipay] 创建支付链接: {out_trade_no}, 金额: {total_amount}")
        
        # 创建请求对象
        request = AlipayTradePagePayRequest()
        request.biz_content = {
            "out_trade_no": out_trade_no,
            "product_code": "FAST_INSTANT_TRADE_PAY",
            "total_amount": str(total_amount),
            "subject": subject,
            "body": body,
            "timeout_express": timeout_express,
        }
        request.notify_url = settings.alipay_notify_url
        print(f"[Alipay] notify_url: {settings.alipay_notify_url}")
        
        # 执行请求
        print("[Alipay] 执行请求...")
        response = self.client.execute(request)
        print(f"[Alipay] 响应: {response}")
        
        # 处理响应
        if response and response.get("alipay_trade_page_pay_response"):
            pay_url = response.get("alipay_trade_page_pay_response").get("pay_url")
            print(f"[Alipay] 支付链接: {pay_url}")
            return pay_url
        
        raise Exception(f"创建支付链接失败: {response}")
    
    def query_trade(self, out_trade_no: str) -> dict:
        """
        查询交易状态
        
        Args:
            out_trade_no: 商户订单号
        
        Returns:
            交易状态信息
        """
        request = AlipayTradeQueryRequest()
        request.biz_content = json.dumps({"out_trade_no": out_trade_no})
        
        response = self.client.execute(request)
        return response
    
    def verify_notification(self, data: dict) -> bool:
        """
        验证回调通知签名
        
        Args:
            data: 回调数据字典
        
        Returns:
            验证是否通过
        """
        # 新版SDK的验签方式
        return self.client.verify(data, None)
    
    @staticmethod
    def generate_out_trade_no() -> str:
        """生成商户订单号"""
        return f"WS{int(time.time() * 1000)}{uuid.uuid4().hex[:6].upper()}"


# 单例
alipay_service = AlipayService()
