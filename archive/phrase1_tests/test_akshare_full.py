#!/usr/bin/env python3
"""
全面测试 akshare 港股接口
"""

import akshare as ak
import time

test_stocks = [
    ("00700", "腾讯"),
    ("09988", "阿里巴巴"),
    ("03690", "美团"),
]

print("="*70)
print("测试 akshare 各种港股接口")
print("="*70)

for symbol, name in test_stocks:
    print(f"\n{'='*70}")
    print(f"{name} ({symbol})")
    print("="*70)
    
    # 1. 历史价格（最稳定）
    print(f"\n[1] stock_hk_daily('{symbol}') - 历史价格")
    try:
        df = ak.stock_hk_daily(symbol=symbol, adjust="qfq")
        if not df.empty:
            latest = df.iloc[-1]
            print(f"✅ 成功: price={latest['close']}, date={latest['date']}")
        else:
            print(f"⚠️ 数据为空")
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 2. A+H股对比（可能有估值数据）
    print(f"\n[2] stock_a_lg_indicator(stock='{symbol}') - 估值指标")
    try:
        df = ak.stock_a_lg_indicator(stock=symbol)
        print(f"✅ 成功")
        print(df.tail(1))
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    # 3. 港股通持股（可能有市值数据）
    print(f"\n[3] stock_hk_ggt_components_em() - 港股通成分股")
    try:
        df = ak.stock_hk_ggt_components_em()
        stock_data = df[df['代码'] == symbol]
        if not stock_data.empty:
            print(f"✅ 成功")
            print(stock_data.iloc[0])
        else:
            print(f"⚠️ 未找到该股票")
    except Exception as e:
        print(f"❌ 失败: {e}")
    
    time.sleep(1)  # 避免限速

print("\n" + "="*70)
print("结论")
print("="*70)
print("akshare 对港股的支持有限，但可以获取历史价格数据")
print("估值数据（PE/PEG）可能需要其他渠道")

