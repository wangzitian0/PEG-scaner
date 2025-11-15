# Core 模块

核心代码模块，包含数据模型、Schema定义、工具函数。

---

## 📁 目录结构

```
core/
├── __init__.py
├── README.md              # 本文件
├── models.py              # 数据模型（StockData, ETFHolding, BacktestResult）
├── format_utils.py        # 格式化工具（小写公司名等）
├── data_persistence.py    # 数据持久化工具（Pipeline追踪）
└── schemas/               # Schema定义（SSOT）
    ├── __init__.py
    ├── stock_schema.py    # Pydantic数据模型
    └── validation_rules.py # 验证规则（95%测试覆盖）
```

**符合原则**：1个目录 + 4个文件

---

## 🎯 核心原则

### SSOT (Single Source of Truth)
所有Schema定义统一在 `schemas/` 目录：
- `stock_schema.py` - 数据结构定义
- `validation_rules.py` - 验证规则定义

### 数据验证
**原则**：宁可为空，不要使用错的数据

验证规则（95%测试覆盖）：
- PE范围：[0, 300]
- PEG范围：[-5, 10]
- 增长率：[-100%, 500%]
- 价格最低：$0.01

---

## 📝 模块说明

### models.py - 数据模型

基础数据类定义：

```python
from core.models import StockData, ETFHolding, BacktestResult

# 股票数据
data = StockData(
    ticker='MSFT',
    price=510.18,
    pe=36.14,
    peg=2.33,
    ...
)
```

**包含**：
- `StockData` - 股票数据模型
- `ETFHolding` - ETF持仓模型
- `BacktestResult` - 回测结果模型

---

### format_utils.py - 格式化工具

格式化显示工具（遵循小写格式）：

```python
from core.format_utils import format_ticker_name, format_profit

# 格式化公司名（小写）
format_ticker_name('MSFT')  # 返回：'微软<msft.us>'

# 格式化利润
format_profit(88_100_000_000)  # 返回：'$88.1B'
```

**功能**：
- 公司名格式化（小写：`微软<msft.us>`）
- 利润格式化（$88.1B, ¥179.4B）
- 增长率格式化（21.8%）
- 股票代码标准化

---

### data_persistence.py - 数据持久化

Pipeline追踪工具（遵循数据持久化原则）：

```python
from core.data_persistence import get_persistence_manager

pm = get_persistence_manager()

# 创建pipeline
pipeline = pm.create_pipeline('MSFT')

# 追踪每个步骤
pm.add_step(pipeline, 'fetch_yfinance', 'success', duration_ms=1234)
pm.add_step(pipeline, 'cross_validation', 'success', 
            metadata={'consistency': 0.98})

# 保存日志
pm.save_pipeline_log(pipeline)
```

**功能**：
- Pipeline追踪
- 中间数据保存（raw, processed）
- 自动清理
- 历史查询

---

### schemas/ - Schema定义

#### stock_schema.py - Pydantic数据模型

严格的数据验证：

```python
from core.schemas import StockDataSchema

# 自动验证
schema = StockDataSchema(
    ticker='MSFT',
    price=100.0,
    pe=350.0,  # 触发验证错误
    ...
)
# 抛出: ValueError("PE异常过高 (>350)")
```

#### validation_rules.py - 验证规则

验证规则集（95%测试覆盖）：

```python
from core.schemas import ValidationRules

# 验证PE
valid, msg = ValidationRules.validate_pe(20.0, 'MSFT')
# 返回: (True, None)

# 自动拒绝异常数据
should_reject, reason = ValidationRules.should_reject_data(
    pe=-10.0, peg=1.5, growth_rate=0.3, price=100.0
)
# 返回: (True, "PE无效: PE为负 (-10.00)")
```

---

## 🧪 测试

```bash
# 运行core模块测试
uv run pytest tests/test_validation_rules.py tests/test_format_utils.py -v

# 结果
✅ 38/38 tests passed
✅ 95% coverage (validation_rules.py)
```

---

## 📚 相关文档

- [数据模型详解](../docs/README.md#数据模型)
- [验证规则说明](../docs/README.md#数据验证)
- [Schema设计原则](../agent.md#SSOT原则)

---

**上级文档**：[返回项目README](../README.md)

