# stock_fundamental - 基本面数据

**Schema**: 股票基本面数据（PE, PEG, 利润、增长率等）

**用途**: PEG分析、股票估值

---

## 📋 Schema 定义

参见：`core/schemas/stock_schema.py::StockFundamentalSchema`

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| ticker | str | 股票代码 |
| date | str | 数据日期 (YYYY-MM-DD) |
| price | float | 当前价格 |
| pe | float | 市盈率 (TTM) |
| peg | float | PEG比率 |
| net_income | float | 净利润 (USD或HKD) |
| growth_rate | float | 增长率 (小数，如0.155表示15.5%) |
| market_cap | float | 市值 |
| source | str | 数据来源 |
| confidence | str | 置信度 (HIGH/MEDIUM/LOW) |

---

## 📁 文件命名

格式: `stock_fundamental-{name}-{source}-{date}.csv`

示例:
- `stock_fundamental-mag7-yfinance-20251115.csv`
- `stock_fundamental-mag7-alphavantage-20251115.csv`
- `stock_fundamental-mag7-aggregated-20251115.csv`

---

## 📊 数据示例

```csv
ticker,date,price,pe,peg,net_income,growth_rate,market_cap,source,confidence
MSFT,2025-11-15,510.18,36.1,2.33,104900000000,0.155,3800000000000,yfinance,HIGH
AAPL,2025-11-15,225.50,35.9,1.84,112000000000,0.195,3500000000000,yfinance,HIGH
```

---

## 🔄 数据来源

### yfinance
- 原始数据源1
- 自动获取
- 可能有缺失

### alphavantage
- 原始数据源2
- 备用验证
- API限制

### aggregated ⭐
- 加工后的置信数据
- 经过多源交叉验证
- 包含置信度评分
- 优先使用

---

**上级文档**: [返回data目录](../README.md)
