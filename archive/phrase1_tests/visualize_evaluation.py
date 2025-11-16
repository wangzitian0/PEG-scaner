#!/usr/bin/env python3
"""可视化数据源评估结果"""

import pandas as pd
import sys

# 读取最新的评估结果
csv_file = sys.argv[1] if len(sys.argv) > 1 else 'x-data/data_source_evaluation_20251116_153413.csv'
df = pd.read_csv(csv_file)

print("="*100)
print("数据源质量评估矩阵")
print("="*100)
print()

# 按市场和数据源分组
for market in ['美股', '港股']:
    if market == '美股':
        stocks = df[df['ticker'].str.contains(r'^[A-Z]+$')]
    else:
        stocks = df[df['ticker'].str.contains(r'\.HK$')]
    
    if stocks.empty:
        continue
    
    print(f"\n{'='*100}")
    print(f"{market} 市场")
    print("="*100)
    
    for source in stocks['source'].unique():
        source_data = stocks[stocks['source'] == source]
        
        print(f"\n[{source}]")
        print("-"*100)
        
        # 表头
        print(f"{'股票':<15} {'价格':^6} {'PE':^6} {'财报':^6} {'净利润':^6} {'增长率':^6} {'置信度':^10}")
        print("-"*100)
        
        for _, row in source_data.iterrows():
            name = row['name']
            ticker = row['ticker']
            price = row.get('price', '❌')
            pe = row.get('pe', '❌')
            financials = row.get('financials', '❌')
            net_income = row.get('net_income', '❌')
            growth = row.get('growth', '❌')
            confidence = row.get('confidence', 'N/A')
            
            print(f"{name:<15} {price:^6} {pe:^6} {financials:^6} {net_income:^6} {growth:^6} {confidence:^10}")

print("\n" + "="*100)
print("图例")
print("="*100)
print("✅ - 可用")
print("❌ - 不可用")
print("🔒 - 需付费/权限")
print("⚠️  - 不确定")
print()
print("置信度:")
print("  HIGH - 4+项可用")
print("  MEDIUM - 2-3项可用")
print("  LOW - 0-1项可用")
print("  BLOCKED - API被阻止")
print("  FAILED - 测试失败")

