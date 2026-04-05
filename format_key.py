"""工具：格式化支付宝私钥用于环境变量

用法：
1. 把你的私钥内容保存到这个文件同目录的 private_key.pem
2. 运行本脚本
3. 复制输出的单行私钥到 Render 环境变量
"""

import os

# 读取原始私钥
pem_path = os.path.join(os.path.dirname(__file__), "private_key.pem")
if os.path.exists(pem_path):
    with open(pem_path, 'r') as f:
        original = f.read()
    
    # 转成单行（把换行符替换成\n）
    formatted = original.replace("\n", "\\n").replace("\r", "")
    
    print("=" * 60)
    print("格式化后的私钥（复制下面全部内容）：")
    print("=" * 60)
    print(formatted)
    print("=" * 60)
    print(f"\n长度：{len(formatted)} 字符")
else:
    print(f"找不到 {pem_path}")
    print("请把 private_key.pem 放到这个文件同目录")
