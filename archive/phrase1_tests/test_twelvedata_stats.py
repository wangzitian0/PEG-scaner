#!/usr/bin/env python3
"""测试 Twelve Data 统计数据的正确用法"""

from twelvedata import TDClient

api_key = "2b28a043331f418980ba353b6936f397"
td = TDClient(apikey=api_key)

print("="*60)
print("测试 Twelve Data 统计数据")
print("="*60)

test_symbols = ["MSFT", "AAPL", "GOOGL"]

for symbol in test_symbols:
    print(f"\n{'='*60}")
    print(f"{symbol}")
    print("="*60)
    
    # 1. 价格数据
    print(f"\n[1] 价格数据")
    try:
        ts = td.time_series(symbol=symbol, interval="1day", outputsize=1)
        data = ts.as_json()
        if data and 'values' in data:
            price = float(data['values'][0]['close'])
            print(f"✅ price={price}")
        else:
            print(f"❌ 没有价格数据")
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 2. 统计数据（正确用法）
    print(f"\n[2] 统计数据 (get_statistics)")
    try:
        stats = td.get_statistics(symbol=symbol)
        # 直接调用 as_json()，不要访问 status_code
        data = stats.as_json()
        
        if data and 'statistics' in data:
            statistics = data['statistics']
            valuations = statistics.get('valuations', {})
            
            print(f"✅ 统计数据成功:")
            print(f"   TrailingPE: {valuations.get('TrailingPE')}")
            print(f"   ForwardPE: {valuations.get('ForwardPE')}")
            print(f"   PegRatio: {valuations.get('PegRatio')}")
            print(f"   MarketCap: {valuations.get('MarketCapitalization')}")
        else:
            print(f"⚠️ 没有统计数据")
            print(f"   返回数据: {data}")
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*60)
print("结论")
print("="*60)

