# Data 目录说明

**上级文档**：[返回项目README](../README.md)

---

## 📂 数据组织原则

遵循 agent.md (30-31) 要求：

> **Line 30**: 本质相同但是不同来源的数据(你加工之后的置信数据也可以认为是一个source)应当遵循 schema 且请放到一个文件夹  
> **Line 31**: 命名规则为 `schema-name-source-date.csv`

### 核心原则

1. **按 Schema 组织**（不是按处理阶段）
2. **统一命名规范**：`{schema}-{name}-{source}-{date}.csv`
3. **多源数据共存**：同一schema下可有多个source
4. **Schema 即文档**：core/schemas/ 定义数据结构

---

## 📁 目录结构

```
data/
├── stock_daily/          # Schema: 日度行情数据
├── stock_fundamental/    # Schema: 基本面数据 (PE, PEG, 利润等)
├── etf_portfolio/        # Schema: ETF持仓数据
├── backtest_result/      # Schema: 回测结果
├── analysis_result/      # Schema: 分析结果
└── cache/                # 临时缓存 (不遵循schema命名规范)
```

---

## 📋 命名规范

### 格式

```
{schema}-{name}-{source}-{date}.csv
```

### 组成部分

| 部分 | 说明 | 示例 |
|------|------|------|
| **schema** | 数据类型/表结构 | stock_daily, stock_fundamental, etf_portfolio |
| **name** | 数据集名称 | mag7, sp500, vgt, tsla |
| **source** | 数据来源 | yfinance, alphavantage, aggregated, backtest |
| **date** | 日期/日期范围 | 20251115 或 20240101_20251115 |

### 示例文件名

```
stock_daily-tsla-yfinance-20000101_20251115.csv
stock_fundamental-mag7-yfinance-20251115.csv
stock_fundamental-mag7-alphavantage-20251115.csv
stock_fundamental-mag7-aggregated-20251115.csv
etf_portfolio-vgt-yfinance-20240101_20251114.csv
backtest_result-tsla-strategy1-20000101_20251115.csv
```

---

## 📊 Schema 详细说明

### 1. stock_daily/ - 日度行情

**用途**：历史价格数据（OHLCV）

**Schema 定义**：参见 `core/schemas/stock_schema.py::StockDailySchema`

**字段**：
- `date` - 日期
- `ticker` - 股票代码
- `open` - 开盘价
- `high` - 最高价
- `low` - 最低价
- `close` - 收盘价
- `volume` - 成交量
- `adj_close` - 复权价

**文件示例**：
```csv
date,ticker,open,high,low,close,volume,adj_close
2025-11-15,TSLA,350.12,355.80,348.90,354.25,125680000,354.25
2025-11-14,TSLA,345.60,351.20,344.80,349.90,132450000,349.90
```

**多源示例**：
```
stock_daily/
├── stock_daily-tsla-yfinance-20000101_20251115.csv
├── stock_daily-mag7-yfinance-20251101_20251115.csv
└── README.md
```

---

### 2. stock_fundamental/ - 基本面数据

**用途**：PEG分析、估值

**Schema 定义**：参见 `core/schemas/stock_schema.py::StockFundamentalSchema`

**字段**：
- `ticker` - 股票代码
- `date` - 数据日期
- `price` - 当前价格
- `pe` - 市盈率
- `peg` - PEG比率
- `net_income` - 净利润
- `growth_rate` - 增长率
- `market_cap` - 市值
- `source` - 数据来源
- `confidence` - 置信度 (HIGH/MEDIUM/LOW)

**文件示例**：
```csv
ticker,date,price,pe,peg,net_income,growth_rate,market_cap,source,confidence
MSFT,2025-11-15,510.18,36.1,2.33,104900000000,0.155,3800000000000,yfinance,HIGH
AAPL,2025-11-15,225.50,35.9,1.84,112000000000,0.195,3500000000000,yfinance,HIGH
```

**多源示例**：
```
stock_fundamental/
├── stock_fundamental-mag7-yfinance-20251115.csv       # 来源1
├── stock_fundamental-mag7-alphavantage-20251115.csv   # 来源2
├── stock_fundamental-mag7-aggregated-20251115.csv     # 加工后的置信数据
└── README.md
```

**加工后的置信数据** (`aggregated` source):
- 综合2+个数据源
- 经过交叉验证
- 包含置信度评分
- 可视为一个新的"source"

---

### 3. etf_portfolio/ - ETF持仓

**用途**：ETF成分股分析

**Schema 定义**：参见 `core/schemas/stock_schema.py::ETFPortfolioSchema`

**字段**：
- `etf_ticker` - ETF代码
- `date` - 数据日期
- `holding_ticker` - 持仓股票代码
- `weight` - 权重
- `shares` - 持股数
- `market_value` - 市值
- `source` - 数据来源

**文件示例**：
```csv
etf_ticker,date,holding_ticker,weight,shares,market_value,source
VGT,2024-01-01,AAPL,21.5,125000000,23500000000,yfinance
VGT,2024-01-01,MSFT,19.8,95000000,21800000000,yfinance
```

**多源示例**：
```
etf_portfolio/
├── etf_portfolio-vgt-yfinance-20240101_20251114.csv
├── etf_portfolio-kweb-yfinance-20240101_20251114.csv
└── README.md
```

---

### 4. backtest_result/ - 回测结果

**用途**：策略回测记录

**Schema 定义**：参见 `core/schemas/stock_schema.py::BacktestResultSchema`

**字段**：
- `ticker` - 股票代码
- `date` - 交易日期
- `strategy` - 策略名称
- `signal` - 交易信号 (BUY/SELL/HOLD)
- `position` - 持仓数量
- `price` - 成交价格
- `pnl` - 损益
- `cumulative_return` - 累计收益率

**文件示例**：
```csv
ticker,date,strategy,signal,position,price,pnl,cumulative_return
TSLA,2025-01-15,peg_strategy,BUY,100,250.50,0,0
TSLA,2025-02-15,peg_strategy,HOLD,100,265.30,1480,0.0591
TSLA,2025-03-15,peg_strategy,SELL,0,270.80,2030,0.0811
```

**多源示例**：
```
backtest_result/
├── backtest_result-tsla-peg_strategy-20000101_20251115.csv
├── backtest_result-mag7-peg_strategy-20000101_20251115.csv
└── README.md
```

---

### 5. analysis_result/ - 分析结果

**用途**：各种分析输出

**Schema**: 根据分析类型不同而不同

**文件示例**：
```
analysis_result/
├── analysis_result-peg_ranking-mag7-20251115.csv      # PEG排名
├── analysis_result-low_peg_top15-vgt_kweb-20251115.csv # 低PEG筛选
├── analysis_result-strategy_comparison-all-20251115.csv # 策略对比
└── README.md
```

---

## 🔄 数据流程

### 1. 原始数据获取
```
yfinance API → stock_fundamental-mag7-yfinance-20251115.csv
alphavantage API → stock_fundamental-mag7-alphavantage-20251115.csv
```

### 2. 数据加工（交叉验证）
```
多个source → data_aggregator.py → stock_fundamental-mag7-aggregated-20251115.csv
```

`aggregated` source 是经过:
- 多源对比
- 异常值过滤
- 置信度评分
- 数据融合

### 3. 分析使用
```
stock_fundamental-mag7-aggregated-20251115.csv → 分析脚本 → analysis_result-xxx.csv
```

---

### 6. cache/ - 临时缓存 ⚠️

**用途**：临时缓存API响应数据

**特殊说明**：
- ⚠️ **不遵循** `schema-name-source-date.csv` 命名规范
- 缓存是临时性质的，仅用于减少API调用
- 文件格式：`{ticker}.json`
- 自动过期：24小时（可配置）

**管理**：
- 由 `data_collection/cache_manager.py` 自动管理
- 过期数据自动失效
- 手动清理：`rm data/cache/*`

**为什么不遵循schema规范？**
- 缓存是临时的、易失的
- Schema规范用于持久化数据
- 缓存文件命名优先考虑简洁性和性能

---

## 📝 最佳实践

### 1. 数据获取

```python
# 保存原始数据（每个source一个文件）
save_to_csv(
    data=yfinance_data,
    path="data/stock_fundamental",
    schema="stock_fundamental",
    name="mag7",
    source="yfinance",
    date="20251115"
)
# 生成: stock_fundamental-mag7-yfinance-20251115.csv
```

### 2. 数据加工

```python
# 加载多个source
yf_data = load_csv("data/stock_fundamental/stock_fundamental-mag7-yfinance-20251115.csv")
av_data = load_csv("data/stock_fundamental/stock_fundamental-mag7-alphavantage-20251115.csv")

# 交叉验证
aggregated = cross_validate(yf_data, av_data)

# 保存加工后数据（source=aggregated）
save_to_csv(
    data=aggregated,
    schema="stock_fundamental",
    name="mag7",
    source="aggregated",  # 加工后的置信数据
    date="20251115"
)
```

### 3. 数据读取

```python
# 读取特定source
df = load_csv_by_pattern(
    schema="stock_fundamental",
    name="mag7",
    source="aggregated",
    date="20251115"
)

# 读取所有source（用于对比）
all_sources = load_all_sources(
    schema="stock_fundamental",
    name="mag7",
    date="20251115"
)
# 返回: {"yfinance": df1, "alphavantage": df2, "aggregated": df3}
```

---

## 🔍 数据查找

### 按模式查找

```bash
# 找所有 mag7 的基本面数据
ls data/stock_fundamental/stock_fundamental-mag7-*.csv

# 找特定日期的数据
ls data/*/stock_*-*-*-20251115.csv

# 找所有 aggregated 数据
ls data/*/stock_*-*-aggregated-*.csv
```

### 数据校验

```bash
# 对比同一数据的不同source
diff \
  data/stock_fundamental/stock_fundamental-mag7-yfinance-20251115.csv \
  data/stock_fundamental/stock_fundamental-mag7-alphavantage-20251115.csv
```

---

## 📚 相关文档

- [Schema 定义](../core/schemas/stock_schema.py) - 数据结构定义
- [数据采集](../data_collection/README.md) - 如何获取数据
- [IO工具](../core/data_io.py) - 读写工具函数

---

## ⚠️ 注意事项

1. **严格遵循命名规范**
   - 4个部分缺一不可
   - 使用 `-` 分隔
   - 日期格式：YYYYMMDD

2. **Schema 一致性**
   - 同一schema下的所有文件必须有相同的列
   - 列名、数据类型必须符合Schema定义

3. **Source 标识**
   - 原始数据用实际来源（yfinance, alphavantage）
   - 加工数据用 aggregated
   - 回测结果用策略名

4. **日期范围**
   - 单日数据：20251115
   - 范围数据：20240101_20251115
   - 使用 `_` 连接起止日期

---

**上级文档**：[返回项目README](../README.md)
