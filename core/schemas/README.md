# Schemas - 数据模式定义

**上级文档**: [返回core目录](../README.md)

---

## 📋 用途

定义项目中所有数据结构的Schema，确保数据一致性和可验证性（agent.md Line 26）

---

## 📁 文件说明

### stock_schema.py

定义核心数据模式：

#### 1. StockDataSchema
股票基本面数据模式

**字段**：
- `ticker`: str - 股票代码
- `date`: str - 数据日期
- `price`: float - 当前价格
- `pe`: float - 市盈率 (TTM)
- `peg`: float - PEG比率
- `net_income`: float - 净利润
- `growth_rate`: float - 增长率
- `market_cap`: Optional[float] - 市值
- `source`: str - 数据来源
- `confidence`: str - 置信度 (HIGH/MEDIUM/LOW)

**用途**: x-data/stock_fundamental/

#### 2. ETFHoldingSchema
ETF持仓数据模式

**字段**：
- `etf_ticker`: str - ETF代码
- `date`: str - 持仓日期
- `holding_ticker`: str - 持仓股票代码
- `weight`: float - 权重
- `shares`: float - 持股数
- `market_value`: float - 市值
- `source`: str - 数据来源

**用途**: x-data/etf_portfolio/

#### 3. BacktestResultSchema
回测结果数据模式

**字段**：
- `ticker`: str - 股票代码
- `date`: str - 交易日期
- `strategy`: str - 策略名称
- `signal`: str - 交易信号 (BUY/SELL/HOLD)
- `position`: float - 持仓数量
- `price`: float - 成交价格
- `pnl`: float - 损益
- `cumulative_return`: float - 累计收益率

**用途**: x-data/backtest_result/

---

### validation_rules.py

数据验证规则类

**核心类**: `ValidationRules`

**验证方法**：
- `validate_pe()` - 验证PE范围
- `validate_peg()` - 验证PEG范围
- `validate_growth_rate()` - 验证增长率
- `validate_price()` - 验证价格
- `validate_profit()` - 验证利润
- `validate_cross_source_deviation()` - 验证多源数据偏差

**原则** (agent.md Line 29):
- 宁可为空，不要使用错的数据
- 严格验证，拒绝异常值

---

## 🎯 设计原则

### 1. SSOT（Single Source of Truth）
- Schema定义是数据结构的唯一权威来源
- 所有数据文件必须符合对应Schema
- agent.md Line 36

### 2. 数据验证
- 所有数据必须经过ValidationRules验证
- 失败数据立即拒绝
- agent.md Line 29

### 3. 多源一致性
- 同一数据至少2个数据源相同才采用
- 通过ValidationRules.validate_cross_source_deviation()实现
- agent.md Line 28

---

## 🔄 使用示例

### 创建Schema实例

```python
from core.schemas.stock_schema import StockDataSchema

data = StockDataSchema(
    ticker="AAPL",
    date="2025-11-15",
    price=272.41,
    pe=35.94,
    peg=1.84,
    net_income=112000000000,
    growth_rate=0.195,
    source="yfinance",
    confidence="HIGH"
)
```

### 验证数据

```python
from core.schemas.validation_rules import ValidationRules

# 验证PE
is_valid, message = ValidationRules.validate_pe("AAPL", 35.94)
if not is_valid:
    print(f"PE验证失败: {message}")

# 验证PEG
is_valid, message = ValidationRules.validate_peg("AAPL", 1.84)
```

### 多源对比

```python
# 对比两个数据源的PE值
deviation = abs(pe1 - pe2) / min(pe1, pe2)
is_valid, msg = ValidationRules.validate_cross_source_deviation(
    ticker="AAPL",
    field="pe",
    value1=35.9,
    value2=36.1,
    threshold=0.05  # 5%
)
```

---

## 📊 Schema与数据文件对应

| Schema | 数据目录 | 文件命名示例 |
|--------|----------|--------------|
| StockDataSchema | x-data/stock_fundamental/ | stock_fundamental-mag7-yfinance-20251115.csv |
| ETFHoldingSchema | x-data/etf_portfolio/ | etf_portfolio-vgt-yfinance-20240101_20251114.csv |
| BacktestResultSchema | x-data/backtest_result/ | backtest_result-tsla-peg_strategy-20000101_20251115.csv |

---

## ✅ 测试覆盖

- `tests/test_validation_rules.py` - 23个测试
- `tests/test_data_quality.py` - 9个数据质量测试
- 覆盖率: 71-95%

---

**上级文档**: [返回core目录](../README.md)

