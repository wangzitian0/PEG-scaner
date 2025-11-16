#!/usr/bin/env python3
"""测试新的 Finnhub token"""

import requests

# 新的 API key
api_key = "d4c7ifpr01qudf6h1e4gd4c7ifpr01qudf6h1e50"
print(f"测试 Finnhub API Key: {api_key}")

# 测试美股
print("\n" + "="*60)
print("测试1: MSFT (美股)")
print("="*60)

url = f"https://finnhub.io/api/v1/quote?symbol=MSFT&token={api_key}"
response = requests.get(url)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    data = response.json()
    print(f"✅ 成功！价格: {data.get('c')}")
else:
    print("❌ 失败")
    exit(1)

# 测试港股
print("\n" + "="*60)
print("测试2: 0700.HK (腾讯)")
print("="*60)

url = f"https://finnhub.io/api/v1/quote?symbol=0700.HK&token={api_key}"
response = requests.get(url)

print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")

if response.status_code == 200:
    data = response.json()
    if data.get('c', 0) > 0:
        print(f"✅ 港股成功！价格: {data.get('c')}")
    else:
        print("⚠️ 返回200但数据为空（免费tier可能不支持港股）")
else:
    print("❌ 失败")

# 测试基本面数据
print("\n" + "="*60)
print("测试3: MSFT 基本面数据")
print("="*60)

url = f"https://finnhub.io/api/v1/stock/metric?symbol=MSFT&metric=all&token={api_key}"
response = requests.get(url)

print(f"Status Code: {response.status_code}")
print(f"Response (前500字符): {response.text[:500]}")

if response.status_code == 200:
    data = response.json()
    if 'metric' in data:
        print(f"✅ 基本面数据成功！")
        metric = data['metric']
        print(f"   PE TTM: {metric.get('peBasicExclExtraTTM')}")
        print(f"   Price: {metric.get('52WeekHigh')}")
    else:
        print("⚠️ 返回200但没有metric数据")
else:
    print("❌ 失败")

