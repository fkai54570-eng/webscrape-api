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
    
    def _convert_to_pkcs8(self, private_key: str) -> str:
        """将PKCS#1格式的RSA私钥转换为PKCS#8格式"""
        if not private_key or "-----BEGIN" not in private_key:
            return private_key
        
        # 如果已经是PKCS#8格式，直接返回
        if "-----BEGIN PRIVATE KEY-----" in private_key:
            return private_key
        
        # 否则转换为PKCS#8格式
        try:
            from cryptography.hazmat.primitives import serialization
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.backends import default_backend
            import base64
            
            # 提取Base64内容
            lines = private_key.strip().split('\n')
            content_lines = [l for l in lines if not l.startswith('-----')]
            b64_content = ''.join(content_lines)
            
            # 解码DER
            der_content = base64.b64decode(b64_content + '=' * (4 - len(b64_content) % 4))
            
            # 使用cryptography加载PKCS#1格式
            private_key_obj = serialization.load_der_private_key(
                der_content,
                password=None,
                backend=default_backend()
            )
            
            # 导出为PKCS#8格式
            pkcs8_pem = private_key_obj.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            print(f"[Alipay] 私钥已从PKCS#1转换为PKCS#8格式")
            return pkcs8_pem.decode('utf-8')
            
        except Exception as e:
            print(f"[Alipay] 密钥转换失败，使用原始格式: {e}")
            return private_key
    
    @property
    def client(self) -> DefaultAlipayClient:
        """延迟初始化客户端"""
        if self._client is None:
            print(f"[Alipay] 初始化客户端...")
            print(f"[Alipay] app_id: {settings.alipay_app_id}")
            print(f"[Alipay] gateway: {'沙箱' if settings.alipay_sandbox else '正式'}")
            
            # 获取处理后的密钥
            private_key = settings.get_alipay_private_key()
            public_key = settings.get_alipay_public_key()
            
            print(f"[Alipay] private_key length: {len(private_key)}")
            print(f"[Alipay] public_key length: {len(public_key)}")
            
            # 转换私钥格式为PKCS#8（SDK需要的格式）
            private_key = self._convert_to_pkcs8(private_key)
            
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
