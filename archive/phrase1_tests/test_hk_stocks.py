#!/usr/bin/env python3
"""
测试失败的3只港股
"""
import yfinance as yf

print("="*60)
print("测试失败的港股 ticker")
print("="*60)

# 测试不同的ticker格式
test_cases = [
    ("腾讯", ["00700.HK", "0700.HK", "700.HK", "TCEHY"]),
    ("美团", ["03690.HK", "3690.HK", "MPNGY"]),
    ("网易", ["09999.HK", "9999.HK", "NTES"]),
]

for name, tickers in test_cases:
    print(f"\n{name}:")
    print("-" * 60)
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # 检查是否有数据
            if info and 'currentPrice' in info:
                price = info.get('currentPrice', 'N/A')
                pe = info.get('trailingPE', 'N/A')
                print(f"  ✅ {ticker:12s} price={price}, PE={pe}")
            else:
                print(f"  ❌ {ticker:12s} info为空或无currentPrice")
        except Exception as e:
            print(f"  ❌ {ticker:12s} 错误: {e}")

print("\n" + "="*60)
print("测试财务数据")
print("="*60)

for name, tickers in test_cases:
    ticker = tickers[0]  # 使用第一个格式
    print(f"\n{name} ({ticker}):")
    try:
        stock = yf.Ticker(ticker)
        
        # 测试获取财务数据
        financials = stock.financials
        if not financials.empty:
            print(f"  ✅ 有财务数据: {financials.shape}")
            if 'Net Income' in financials.index:
                print(f"  ✅ 有净利润数据")
            else:
                print(f"  ⚠️  没有 'Net Income'，可用: {list(financials.index)[:5]}")
        else:
            print(f"  ❌ 财务数据为空")
            
    except Exception as e:
        print(f"  ❌ 错误: {e}")

