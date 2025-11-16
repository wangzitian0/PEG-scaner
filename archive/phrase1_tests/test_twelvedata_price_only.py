#!/usr/bin/env python3
"""只测试 Twelve Data 价格数据"""

from twelvedata import TDClient
import time

api_key = "2b28a043331f418980ba353b6936f397"
td = TDClient(apikey=api_key)

print("测试 Twelve Data 价格数据")
print("="*60)

test_symbols = ["MSFT", "AAPL"]

for symbol in test_symbols:
    print(f"\n{symbol}:")
    try:
        ts = td.time_series(
            symbol=symbol,
            interval="1day",
            outputsize=1
        )
        data = ts.as_json()
        print(f"返回数据: {data}")
        
        if isinstance(data, tuple) and len(data) > 0:
            price_data = data[0]
            print(f"✅ price={price_data.get('close')}")
        elif isinstance(data, dict) and 'values' in data:
            price_data = data['values'][0]
            print(f"✅ price={price_data.get('close')}")
        else:
            print(f"❌ 数据格式不对")
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    time.sleep(1)

