#!/usr/bin/env python3
"""直接测试 Finnhub API"""

import requests

# 你的 API key
api_key = "cpvd55hr01qr32bh6r2gcpvd55hr01qr32bh6r30"
print(f"API Key: {api_key}")

# 测试1: 获取 MSFT 报价
print("\n" + "="*50)
print("测试: MSFT 报价")
print("="*50)

url = f"https://finnhub.io/api/v1/quote?symbol=MSFT&token={api_key}"
response = requests.get(url)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    print("✅ API key 有效！")
else:
    print("❌ API key 无效或有问题")

