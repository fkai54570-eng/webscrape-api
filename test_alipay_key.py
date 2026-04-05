# -*- coding: utf-8 -*-
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest

# 使用新生成的测试密钥
test_private_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQC1vyY8ZLiReCvKwuVDr5b30PoLku/4A5iJxVTr2Mdg1LyCihlIDC8FBAIP26LU2P/k1TTqLKe3MVz3DlPJ1FL8h/EDvCKSkP23MPuJ3ZhU/pB3HveVssUs9ijd2/XnWaO1fvmOWomIfRFC4IxPDDDj7KItQeT+Ze0hhrsUasOIz18r84yLUj02NewEy/moTUaKKucyBOXT7kdP/Iyx3Bz1avtlvQpXG8CkiHb+6Y+jw6lrBTmQEnKOnRM4hHfeZRtsfpCZWgQ0a+gdua4+2poB1C5akBHBmfuExwh/g6Vvm4ACe7fgKRHb/2wCwr6y54OP/DKPNIemg8slIjBDLPkBAgMBAAECggEAHMSIY1fYBSKd3+bQjlGtVkWMRqe39yxuiSQkiH5UNMYHnqwIS2iuSp9zShpMYF+Gxaxfx09RLsSQAAUTCyfiCNnlst8lI8jyd/w3XH+oXI+8wzYyH05gOnkuR8vI1RlRuelCzB8VlPai9FCBtQNre7BZjUtYWVI94igm1Zj+oVlZGGG0RDzpCJ9CUwn1aW6Cvqd0oMmleKbJtPj+ORptBgYmaBGPSpNa8UTLceAkI7o+1GUHFejrtVliazYnXran89Pr/of7ycMg49sg7yHcUjM5FGbECvD+c7faiyzzP1FSXIjVFs+UdWvTgFHh3eXN+PDexe8uayUifi5vUO1ZdwKBgQDsNqQFZjRKe0NvUeJ6mJBMjGeXvhD+fZoIJQ6jRA6URYI9w7aIltCFkYjX4RPe9vWkIMTsZh1xy91iUQAveyeqW8qEKG5rsDn7i+hZyn0Zc12t5Xb51THo/vzFpRFSV8HA4XTzdqjkcAcQ9z8slYQgBWvcQ9ye8TL3bi+p+RdbNwKBgQDE+IYWgKHI/HX2PowNpJMhUwijEbn6NXBb2YkVfVWLiemkqlrsHHOEgFeR0rZDEdpPHJNCBfBfdPkS3+0mqwdH9sgqcE3LiFr4/tiHXyjKYUnKSq4Nh19wBflKnSiDh62t25bfd+JKpAtibrk0UXFcJOGCzm96+wr4xgo3PGiZhwKBgAPvlSQR4+Up0KHWN3PbfuwHmuJIZHgZF6vzEh9eTu/hiJ4G2M/F04umNSWDtpUMgGNPuHhH602uG+47c0lXP/3ysZkqI0zgDtdGKYT1fsghx/nRzP20s7QyK3wPmA5LMAtKtmwoGgBUbYm21PKlOyJddMKiztZHJpZA28J1SBJZAoGAS0dMP9djfaP3FWhsMF6gmJDacTA6KsU3rvLhsGPZSN4pfHRbEXgCMja2wRWN8O4myCt8oDQS3PigpLUONsQQoVFQyN9o7Aut8RG9AWe9+DLcd8K46JS/RdoSn5CWxkYZe6O78qYnxy0Q6Mq2X6dssrGpuktZUeAWHmPZzah5tYsCgYAQVmGxA9Pq68WZzdQooSisCSchIisoIiRAullfkn8X2EGa97NiKfEwQJ2tktbkna9AJHfV4/HFXqyvKao+D3yS7p/kdP2UcsAaTVXtOuId2H5Fo/2SqKqd36vQ2u0/aHQRxpjv8OdGY2K1cCwdiMWVujq6Kk6X+PxXbW5YURKDrQ==
-----END RSA PRIVATE KEY-----"""

test_public_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAtb8mPGS4kXgrysLlQ6+W99D6C5Lv+AOYicVU69jHYNS8gooZSAwvBQQCD9ui1Nj/5NU06iyntzFc9w5TydRS/IfxA7wikpD9tzD7id2YVP6Qdx73lbLFLPYo3dv151mjtX75jlqJiH0RQuCMTwww4+yiLUHk/mXtIYa7FGrDiM9fK/OMi1I9NjXsBMv5qE1GiirnMgTl0+5HT/yMsdwc9Wr7Zb0KVxvApIh2/umPo8OpawU5kBJyjp0TOIR33mUbbH6QmVoENGvoHbmuPtqaAdQuWpARwZn7hMcIf4Olb5uAAnu34CkR2/9sAsK+sueDj/wyjzSHpoPLJSIwQyz5AQIDAQAB
-----END PUBLIC KEY-----"""

alipay_client_config = AlipayClientConfig()
alipay_client_config.server_url = 'https://openapi-sandbox.dl.alipaydev.com/gateway.do'
alipay_client_config.app_id = '9021000162659359'
alipay_client_config.app_private_key = test_private_key
alipay_client_config.alipay_public_key = test_public_key
alipay_client_config.sign_type = 'RSA2'

print('Starting client initialization...')
client = DefaultAlipayClient(alipay_client_config)
print('Client initialized successfully!')

# Test creating a payment request
print('Creating payment request...')
request = AlipayTradePagePayRequest()
request.biz_content = {
    "out_trade_no": "TEST123456",
    "product_code": "FAST_INSTANT_TRADE_PAY",
    "total_amount": "0.01",
    "subject": "Test Payment",
    "timeout_express": "30m",
}
request.notify_url = ''

try:
    response = client.execute(request)
    print(f'Response: {response}')
except Exception as e:
    print(f'Request failed: {e}')
    import traceback
    traceback.print_exc()
