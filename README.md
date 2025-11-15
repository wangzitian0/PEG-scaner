# PEG Scanner - 科技股估值分析系统

> **PEG（Price/Earnings to Growth）是科技公司最重要的估值指标**

基于双数据源交叉验证的PEG指标分析工具，支持美股和港股。

## ⚡ 快速开始

```bash
# 安装依赖
uv sync

# 获取七姐妹PEG数据
uv run python data_collection/fetch_current_peg.py

# 查看结果
cat data/results/mag7_peg_*.md
```

## 📊 核心功能

- ✅ **双数据源验证**：yfinance + Alpha Vantage交叉验证
- ✅ **严格数据质量**：宁可为空，不要使用错的数据
- ✅ **智能置信度**：HIGH/MEDIUM/LOW三级评估
- ✅ **自动缓存**：24小时本地缓存加速
- ✅ **完整测试**：47个测试用例，48%覆盖率

## 🎯 最新数据（2025-11-15）

**最具投资价值（PEG < 0.4）**：
1. 京东<09618.hk> - **PEG 0.13** 🏆
2. 比亚迪<01211.hk> - **PEG 0.26**
3. 阿里巴巴<09988.hk> - **PEG 0.32**

完整分析请查看 [`data/results/`](data/results/)

## 📁 项目结构（SSOT原则）

```
PEG-scaner/
├── 📚 docs/                  # 所有文档（Single Source）
│   ├── README.md             # 完整文档
│   ├── QUICKSTART.md         # 快速入门
│   ├── REQUIREMENTS.md       # 原始需求
│   └── ITERATION_SUMMARY.md  # 开发历程
│
├── 💾 data/                  # 所有数据（持久化）
│   ├── raw/                  # 原始数据
│   ├── processed/            # 处理后数据
│   ├── cache/                # 缓存数据
│   ├── results/              # 最终结果
│   └── logs/                 # 处理日志
│
├── 🧠 core/                  # 核心代码
│   ├── schemas/              # 数据Schema（SSOT）
│   ├── models.py
│   └── format_utils.py
│
├── 📡 data_collection/       # 数据采集
│   ├── fetch_yfinance.py
│   ├── fetch_alpha_vantage.py
│   └── data_aggregator.py    # 双源验证
│
├── 📈 backtest/              # 回测引擎（Phase 2）
└── 🧪 tests/                 # 测试套件
```

## 🚀 使用指南

### 基础使用

```bash
# 获取单只股票PEG
uv run python -c "
from data_collection.fetch_yfinance import fetch_stock_data
data = fetch_stock_data('MSFT')
print(f'PEG: {data.peg:.2f}')
"

# 运行测试
uv run pytest tests/ -v

# 查看覆盖率
uv run pytest tests/ --cov --cov-report=html
open htmlcov/index.html
```

### 数据持久化

所有数据处理中间过程都会持久化到 `data/` 目录：

```bash
data/
├── raw/           # API原始响应（调试用）
├── processed/     # 清洗后数据
├── cache/         # 24小时缓存
├── results/       # 最终输出
└── logs/          # 处理日志（每步都记录）
```

## 📖 详细文档

- [完整文档](docs/README.md) - PEG原理、数学推导、案例分析
- [快速入门](docs/QUICKSTART.md) - 环境配置、使用示例
- [开发历程](docs/ITERATION_SUMMARY.md) - 三次迭代详解
- [系统设计](agent.md) - 架构设计、模块说明

## 🧪 测试状态

```
✅ 46/46 tests passed
✅ 48% code coverage
✅ 100% SSOT compliance
✅ 100% data persistence
```

## 🎓 技术栈

- **Python 3.14** + **uv**（依赖管理）
- **yfinance** + **Alpha Vantage**（数据源）
- **Pydantic**（Schema验证）
- **pytest**（测试框架）

## 📝 设计原则

### 1. SSOT (Single Source of Truth)
- 所有文档集中在 `docs/`
- 配置统一在 `config.yaml`
- Schema定义在 `core/schemas/`

### 2. 数据持久化
- 中间过程全部保存到 `data/`
- 每步操作都有日志
- 便于调试和追溯

### 3. 数据质量优先
- 宁可为空，不要使用错的数据
- 双数据源交叉验证
- 严格的验证规则

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

**快速链接**：
[完整文档](docs/README.md) |
[快速开始](docs/QUICKSTART.md) |
[系统设计](agent.md) |
[测试报告](htmlcov/index.html)

