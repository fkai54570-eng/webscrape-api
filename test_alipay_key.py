# -*- coding: utf-8 -*-
from alipay.aop.api.AlipayClientConfig import AlipayClientConfig
from alipay.aop.api.DefaultAlipayClient import DefaultAlipayClient
from alipay.aop.api.request.AlipayTradePagePayRequest import AlipayTradePagePayRequest

# 使用 PKCS#8 格式的私钥
private_key = """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCiZGxwHfWPqLdI
pvU2odviWLkEUgK5mMAmKosQOovCIe2fWdUY+GqbprmybAxAEO7eXWVgJGlCZsMs
TFvzY7hnmc7pRHLR5YHWQsIAhOyss+cE/30UeSnsV9b/L126iqNuyP0Ih/FkK1uZ
GuGr95j7RVu7zPUUQcY+Vv0JJJ1LufL7fjjEJF11ZN9JevRtnfy3KShrhz9rI1UC
od+jHDB8hdpoFvgxLfI6YSB5UTDczY+VPJhaRFRrnOkgy7Bp3jgF9Rec4qjc4TqU
paPcj8xDWUAd251azcr3iF9gjNT8Zsd3NtJYFUApUFenD3sJREG+fR9YfQiUon/e
QJM0p137AgMBAAECggEACngxY/EQ7QtSXB693gdrzUxgpHfdF4LsY6MhuaqGN1fh
bmdn2hpGu6fXsdPn3kfsZO2q8YEN2dGvCslJf4f4Ul8tYqCesaWVGO+cFLuwWCbc
SAtotv8wxfBlbg8egQsbI+aIjOcNMW+rxVOUWEMeqJewi4tyAxvsE6AFsQ2cdOgU
nYjhaOUMDPQM9+CuOguyrtyUGZFiXjqJsHcpMbJjkI4grPee946GO6qrraQ5Kamd
F3zFDku6aBprj5OVgiBCleDpan0Z8aYm03EOTH1i0yuBm58nyw0LvjeeSBJ1iSA5
vbRZcjrchmnBj9Ot/Re4KkEv9JZn61kCWhoTeJWKsQKBgQDUBllievQO36ONmX62
SPRV8M0zOegybtqiqKn99tTu82mqH8Eew2tfs0OQHjNkVKkSt/mo8V/ngwTZ3X/z
RzCbCB8gsmL1dzQo6hmt4lsOUfIf/QwJH23QroVjeciSg7I5FK8X847Mi0jPmDpX
YzvYDozEgpgOpCc00YX7TXd69wKBgQDEEspO/hROXekLv348YOR/6mTLQeoi5MTi
cligTmQRffTHnZosXTa4yL0x0YNSRTrJhv3IU3HetGOV9tYIpZBqL3n17ze4IEiu
TQdoflt2ofBMzHL8exBEcS81NoeGYWGFbAZpBepOBgHQO38Eb1Oi7uTB7EQkj3V+
rUNtykkQHQKBgDfM8/lXIqRHd2Ps4cxXpvZ3SYoR02pyglgMy7BrJd89cLG1ab4O
8FNfeoiTajMdlOG4SZyM6hCkCsLL6MC+G6yxln+kcybnGHMsKVX6HLzIFFEW5/P+
sYgaZkCn7IGi52TebLaBAzQR9DeueKxHEZjrO2D8fchcq3TbL8fTu35BAoGANBrq
OGO88bZzH/Qbj+AP2Q5pCrrRhcRVrffFJZSvcxaN3h47wl5jFGgEHyEWTN6o6LU+
6+WA9TXq4QdfiZy17AIB3yFbJUsvBWLi/RnXJIeUXFRYmk/52rZZXULIcSWfzN0Q
NwijY2ilQrkM4BjVmQ7zK7WlxjF5f9h7esmu8OECgYAbZ3b0SfogXJI2MvprfsPR
61jVzkBWFKz4kmozKPBYYKcG4EJORz5hzgXppvN9uAj6zQS7uhXmat8+EqSZxhhW
vRdGttMDKZ/fe3uzjZc8WQzULn59tzUuUiBmlBhDT1SX+K4Jod59WLvOeU/CZzdC
IiWODYn7mPk09FNQzZi4Cw==
-----END PRIVATE KEY-----"""

# 公钥
public_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAomRscB31j6i3SKb1NqHb
4li5BFICuZjAJiqLEDqLwiHtn1nVGPhqm6a5smwMQBDu3l1lYCRpQmbDLExb82O4
Z5nO6URy0eWB1kLCAITsrLPnBP99FHkp7FfW/y9duoqjbsj9CIfxZCtbmRrhq/eY
+0Vbu8z1FEHGPlb9CSSdS7ny+344xCRddWTfSXr0bZ38tykoa4c/ayNVAqHfoxww
fIXaaBb4MS3yOmEgeVEw3M2PlTyYWkRUa5zpIMuwad44BfUXnOKo3OE6lKWj3I/M
Q1lAHdudWs3K94hfYIzU/GbHdzbSWBVAKVBXpw97CURBvn0fWH0IlKJ/3kCTNKdd
+wIDAQAB
-----END PUBLIC KEY-----"""

alipay_client_config = AlipayClientConfig()
alipay_client_config.server_url = 'https://openapi-sandbox.dl.alipaydev.com/gateway.do'
alipay_client_config.app_id = '9021000162659359'
alipay_client_config.app_private_key = private_key
alipay_client_config.alipay_public_key = public_key
alipay_client_config.sign_type = 'RSA2'

print('Creating client with PKCS#8 key...')
try:
    client = DefaultAlipayClient(alipay_client_config)
    print('Client created successfully!')
    
    request = AlipayTradePagePayRequest()
    request.biz_content = {
        "out_trade_no": "TEST123456",
        "product_code": "FAST_INSTANT_TRADE_PAY",
        "total_amount": "0.01",
        "subject": "Test Payment",
        "timeout_express": "30m",
    }
    
    print('Executing request...')
    response = client.execute(request)
    print(f'Response: {response}')
except Exception as e:
    print(f'Failed: {e}')
    import traceback
    traceback.print_exc()
