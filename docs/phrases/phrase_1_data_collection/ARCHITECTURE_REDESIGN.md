# Phase 1 架构重新设计

**日期**: 2025-11-16  
**问题**: 当前架构混淆了数据层和计算层

---

## 🚨 当前问题

### 错误的设计

```python
# 当前：所有东西混在一起
stock_fundamental:
  - ticker
  - date (每次运行都变)
  - price (每天变) ❌
  - pe (每天变) ❌
  - peg (每天变) ❌
  - net_income (季度变)
  - growth_rate (季度变)
```

**问题**:
1. 混合了不同变化频率的数据
2. 无法复用财务数据
3. 无法独立更新价格
4. PEG计算耦合在数据获取中

---

## ✅ 正确的架构

### 分层设计

```
数据层（Data Layer）
├── stock_financial/     变化频率: 季度
│   └── ticker, quarter, net_income, growth_rate, report_date
│
├── stock_daily/         变化频率: 每天
│   └── ticker, date, open, high, low, close, volume
│
└── etf_portfolio/       变化频率: 月度/季度
    └── etf_ticker, component_ticker, weight, date

计算层（Computation Layer）
└── peg_result/          变化频率: 按需
    └── ticker, date, price, pe, peg, data_source, confidence
```

---

## 📋 新的Schema设计

### 1. stock_financial（财务数据）

**变化频率**: 季度  
**文件命名**: `stock_financial-{name}-{source}-{quarter}.csv`

```csv
ticker,quarter,net_income,revenue,growth_rate,report_date,source
AAPL,2024Q3,22956000000,,0.195,2024-08-01,yfinance
MSFT,2024Q3,,,0.155,2024-07-30,yfinance
```

**特点**:
- 一个季度只需获取一次
- 可以累积历史数据
- 独立于价格数据

---

### 2. stock_daily（每日价格）

**变化频率**: 每天  
**文件命名**: `stock_daily-{name}-{source}-{date}.csv`

```csv
ticker,date,open,high,low,close,volume,market_cap,source
AAPL,2025-11-16,271.05,275.96,269.60,272.41,47399300,,yfinance
MSFT,2025-11-16,498.23,511.60,497.44,510.18,28491700,,yfinance
```

**特点**:
- 每天更新
- 可以用于历史回测
- 独立于财务数据

---

### 3. peg_result（PEG计算结果）

**变化频率**: 按需（组合上面两个）  
**文件命名**: `peg_result-{name}-{source}-{date}.csv`

```csv
ticker,calc_date,price,pe,peg,quarter_used,confidence,data_source
AAPL,2025-11-16,272.41,35.94,1.84,2024Q3,HIGH,yfinance
MSFT,2025-11-16,510.18,36.14,2.33,2024Q3,HIGH,yfinance
```

**特点**:
- 由 PEG引擎 计算生成
- 引用具体的季度财务数据
- 可追溯数据来源

---

## 🏗️ 新的模块设计

### 数据获取模块

```python
# data_collection/fetch_financial.py
def fetch_financial_data(ticker, quarter):
    """获取季度财务数据"""
    return {
        'net_income': ...,
        'growth_rate': ...,
        'report_date': ...,
    }

# data_collection/fetch_daily.py
def fetch_daily_price(ticker, date):
    """获取每日价格"""
    return {
        'open': ..., 'close': ..., 
        'volume': ...,
    }
```

### PEG计算引擎

```python
# core/peg_engine.py
class PEGEngine:
    def calculate_peg(self, ticker, date):
        """
        计算PEG
        
        流程:
        1. 加载最新财务数据 (stock_financial)
        2. 加载指定日期价格 (stock_daily)
        3. 计算 PE = price / (net_income / shares)
        4. 计算 PEG = PE / (growth_rate * 100)
        5. 返回结果 + 数据溯源信息
        """
        financial = load_financial(ticker)
        price_data = load_daily(ticker, date)
        
        pe = calculate_pe(price_data, financial)
        peg = pe / (financial.growth_rate * 100)
        
        return PEGResult(
            ticker=ticker,
            date=date,
            pe=pe,
            peg=peg,
            quarter_used=financial.quarter,
            confidence=validate(pe, peg)
        )
```

---

## 🎯 优势

### 1. 数据复用
```
季度财务数据（2024Q3）
  ↓
可以用于计算90天的PEG
  - 2024-08-01: PEG with Q3 data
  - 2024-08-02: PEG with Q3 data
  - ...
  - 2024-10-31: PEG with Q3 data
```

### 2. 灵活更新
```
价格变化 → 只更新 stock_daily
财报发布 → 只更新 stock_financial
需要PEG → 运行 PEG引擎
```

### 3. 便于回测
```
历史回测:
  for date in date_range:
      financial = get_financial(ticker, quarter_of(date))
      price = get_price(ticker, date)
      peg = peg_engine.calculate(financial, price)
```

### 4. 易于扩展
```
新增指标（如PE-TTM）:
  - 只需修改 PEG引擎
  - 不需要重新获取数据

新增数据源:
  - 只需实现对应的 fetch_* 函数
  - PEG引擎逻辑不变
```

---

## 📝 实施计划

### Step 1: 重新设计Schema (1小时)
- [ ] 定义 `stock_financial` schema
- [ ] 定义 `stock_daily` schema  
- [ ] 定义 `peg_result` schema
- [ ] 更新 `core/schemas/`

### Step 2: 拆分数据获取 (2小时)
- [ ] 创建 `fetch_financial.py`
- [ ] 创建 `fetch_daily.py`
- [ ] 修改现有代码

### Step 3: 实现PEG引擎 (2小时)
- [ ] 创建 `core/peg_engine.py`
- [ ] 实现 `calculate_peg()`
- [ ] 实现数据加载逻辑

### Step 4: 重新生成数据 (30分钟)
- [ ] 运行财务数据获取
- [ ] 运行价格数据获取
- [ ] 运行PEG计算引擎

### Step 5: 更新文档 (30分钟)
- [ ] 更新README
- [ ] 更新Schema文档
- [ ] 更新使用指南

**总计**: ~6小时

---

## 🤔 是否现在重构？

### 选项A: 立即重构 ⭐⭐⭐⭐⭐
- 优点: 架构正确，便于后续开发
- 缺点: 需要6小时
- 建议: Phase 1还未完全完成，现在重构最合适

### 选项B: Phase 2再重构
- 优点: 先完成Phase 1
- 缺点: 技术债累积，回测时会遇到更多问题
- 建议: 不推荐

### 选项C: 保持现状
- 优点: 省时间
- 缺点: 架构错误会持续带来问题
- 建议: 不推荐

---

## 💡 我的建议

**立即重构（选项A）** ⭐⭐⭐⭐⭐

**理由**:
1. Phase 1刚完成，代码量还小
2. 正确的架构对Phase 2（回测）至关重要
3. 回测需要历史价格+历史财务数据的组合
4. 现在不改，以后会更痛苦

**重构后的Phase 1产物**:
```
x-data/
├── stock_financial/
│   └── stock_financial-mag7-yfinance-2024Q3.csv
├── stock_daily/
│   └── stock_daily-mag7-yfinance-20251116.csv
└── peg_result/
    └── peg_result-mag7-20251116.csv  (由引擎生成)
```

你同意立即重构吗？

