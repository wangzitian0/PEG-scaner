# 严格验证要求

**用户要求**: 2025-11-15

---

## ❌ 当前问题

### 1. 文件太多
```
x-data/stock_fundamental/
├── stock_fundamental-mag7-yfinance-20251115.csv           ← 需要
├── stock_fundamental-mag7-finnhub-20251115.csv            ← 需要
├── stock_fundamental-mag7-aggregated-20251115.csv         ← 需要
├── stock_fundamental-mag7-yfinance_single-20251115.csv    ← 旧文件，删除
└── stock_fundamental-mag7-yfinance_multi-20251115.csv     ← 旧文件，删除
```

### 2. 验证逻辑不对

**当前逻辑**:
```python
if yf_data and fh_data:
    if data_consistent(yf, fh):
        return aggregated  # ✅ 双源一致
    else:
        # 不一致，使用investpy仲裁
        
if yf_data or fh_data:
    # ❌ 单源也返回（confidence=MEDIUM）
    return single_source
```

**问题**: 单源数据也返回了（4条港股）

**用户要求**:
```python
# 必须至少2/3数据源一致，才返回
if len(valid_sources) >= 2:
    if at_least_two_consistent(sources):
        return aggregated  # ✅
    else:
        return None  # ❌ 拒绝
else:
    return None  # ❌ 单源拒绝
```

---

## 🎯 用户的真实要求

### 原则
1. **三个数据源都要尝试获取**
2. **至少2个数据源一致，才算可信**
3. **单源数据 = 不可信 = 拒绝**

### 验证标准

```
3源都成功 + 至少2源一致 → ✅ aggregated (HIGH)
2源成功 + 2源一致       → ✅ aggregated (MEDIUM)
1源成功                → ❌ 拒绝
3源都成功 + 3源都不一致  → ❌ 拒绝
```

---

## �� 需要修复

### 1. 清理旧文件
```bash
rm x-data/stock_fundamental/stock_fundamental-mag7-yfinance_single-20251115.csv
rm x-data/stock_fundamental/stock_fundamental-mag7-yfinance_multi-20251115.csv
```

### 2. 解决数据源失败问题

**Finnhub港股问题**:
- 问题: 403错误
- 原因: 免费tier不支持港股
- 解决: ？需要付费或放弃港股

**Investpy问题**:
- 问题: 403错误
- 原因: 反爬虫机制
- 解决: 优化反爬虫策略

### 3. 重新实现验证逻辑

```python
def validate_with_strict_rule(ticker):
    # 1. 尝试所有三个源
    yf_data = fetch_yf(ticker)
    fh_data = fetch_fh(ticker)
    inv_data = fetch_inv(ticker)
    
    # 2. 收集成功的源
    valid_sources = [d for d in [yf_data, fh_data, inv_data] if d]
    
    # 3. 严格验证：至少2源
    if len(valid_sources) < 2:
        logger.warning(f"{ticker}: 只有{len(valid_sources)}个源，拒绝")
        return None
    
    # 4. 至少2源一致
    if not at_least_two_consistent(valid_sources):
        logger.warning(f"{ticker}: 数据源不一致，拒绝")
        return None
    
    # 5. 返回aggregated
    return aggregate(valid_sources)
```

---

## 📊 预期结果

### 理想情况
```
美股:
- yfinance: ✅
- finnhub: ✅
- investpy: ✅（如果能解决403）
→ 3源验证 → aggregated (7条)

港股:
- yfinance: ✅
- finnhub: ❌ (403)
- investpy: ✅（如果能解决403）
→ 2源验证 → aggregated (4-7条)
```

### 现实情况（如果investpy持续403）
```
美股:
- yfinance: ✅
- finnhub: ✅
- investpy: ❌
→ 2源验证 → aggregated (7条)

港股:
- yfinance: ✅
- finnhub: ❌
- investpy: ❌
→ 1源 → ❌ 拒绝（0条）
```

**结论**: 可能只有7条美股数据！

---

## 🤔 关键问题

**如果investpy和finnhub都无法获取港股数据，该怎么办？**

选项1: 接受只有美股数据（7条）
选项2: 放宽港股要求（yfinance单源也接受）
选项3: 寻找其他港股数据源

需要用户决策！
