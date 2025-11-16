#!/usr/bin/env python3
"""测试修复后的normalize_ticker"""

import sys
sys.path.insert(0, '.')

from core.format_utils import normalize_ticker

test_cases = [
    ("00700.HK", "0700.HK"),  # 腾讯
    ("03690.HK", "3690.HK"),  # 美团
    ("09999.HK", "9999.HK"),  # 网易
    ("01810.HK", "1810.HK"),  # 小米
    ("09988.HK", "9988.HK"),  # 阿里
    ("MSFT.US", "MSFT"),      # 微软
]

print("测试 normalize_ticker 修复:")
print("="*60)

all_pass = True
for input_ticker, expected in test_cases:
    result = normalize_ticker(input_ticker)
    status = "✅" if result == expected else "❌"
    if result != expected:
        all_pass = False
    print(f"{status} {input_ticker:12s} → {result:12s} (预期: {expected})")

print("="*60)
if all_pass:
    print("✅ 全部测试通过")
else:
    print("❌ 有测试失败")

