#!/usr/bin/env python3
"""
测试 akshare 的各种港股接口
参考: https://akshare.akfamily.xyz/data/stock/stock.html
"""

import akshare as ak
import pandas as pd

print("="*60)
print("测试1: stock_hk_spot_em() - 港股实时行情")
print("="*60)
try:
    df = ak.stock_hk_spot_em()
    print(f"✅ 成功获取 {len(df)} 只港股")
    print(f"列名: {df.columns.tolist()}")
    
    # 查找腾讯
    tencent = df[df['代码'] == '00700']
    if not tencent.empty:
        print(f"\n腾讯 (00700):")
        print(tencent.to_dict('records')[0])
    else:
        print("\n❌ 未找到腾讯")
except Exception as e:
    print(f"❌ 失败: {e}")

print("\n" + "="*60)
print("测试2: stock_hk_daily(symbol='00700') - 腾讯历史数据")
print("="*60)
try:
    df = ak.stock_hk_daily(symbol="00700", adjust="qfq")
    print(f"✅ 成功获取 {len(df)} 天数据")
    print(f"列名: {df.columns.tolist()}")
    print(f"最新数据:")
    print(df.tail(1).to_dict('records')[0])
except Exception as e:
    print(f"❌ 失败: {e}")

print("\n" + "="*60)
print("测试3: stock_individual_info_em(symbol='00700') - 公司信息")
print("="*60)
try:
    info = ak.stock_individual_info_em(symbol="00700")
    print(f"✅ 成功获取公司信息")
    print(info)
except Exception as e:
    print(f"❌ 失败: {e}")

print("\n" + "="*60)
print("测试4: 检查是否有 PE 等估值数据")
print("="*60)
try:
    df = ak.stock_hk_spot_em()
    tencent = df[df['代码'] == '00700']
    if not tencent.empty:
        row = tencent.iloc[0]
        print("可用字段:")
        for col in df.columns:
            val = row[col]
            print(f"  {col}: {val}")
except Exception as e:
    print(f"❌ 失败: {e}")

