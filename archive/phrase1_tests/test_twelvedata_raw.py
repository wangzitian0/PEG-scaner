#!/usr/bin/env python3
"""直接测试 Twelve Data API"""

import os
from twelvedata import TDClient

# 获取 API key
api_key = "2b28a043331f418980ba353b6936f397"
print(f"API Key: {api_key}")

# 初始化客户端
td = TDClient(apikey=api_key)
print("✅ TDClient 初始化成功")

# 测试1: 美股 - MSFT
print("\n" + "="*50)
print("测试1: MSFT (美股)")
print("="*50)
try:
    ts = td.time_series(
        symbol="MSFT",
        interval="1day",
        outputsize=1
    )
    data = ts.as_json()
    print(f"✅ 成功获取 MSFT 数据:")
    print(f"   {data}")
except Exception as e:
    print(f"❌ 失败: {e}")

# 测试2: 港股 - 腾讯
print("\n" + "="*50)
print("测试2: 0700.HK (腾讯)")
print("="*50)
for symbol in ["0700.HK", "700.HK", "0700:HKEX", "TCH:US"]:
    print(f"\n尝试格式: {symbol}")
    try:
        ts = td.time_series(
            symbol=symbol,
            interval="1day",
            outputsize=1
        )
        data = ts.as_json()
        print(f"✅ 成功: {data}")
        break
    except Exception as e:
        print(f"❌ 失败: {e}")

# 测试3: 获取统计数据
print("\n" + "="*50)
print("测试3: MSFT 统计数据")
print("="*50)
try:
    stats = td.get_statistics(symbol="MSFT")
    print(f"✅ 成功获取 MSFT 统计数据:")
    print(f"   Status Code: {stats.status_code}")
    data = stats.as_json()
    print(f"   Data: {data}")
except Exception as e:
    print(f"❌ 失败: {e}")

