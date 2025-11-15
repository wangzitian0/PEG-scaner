# PEG Scanner

> **科技股估值分析系统** - 基于双数据源交叉验证的PEG指标分析工具

[![Tests](https://img.shields.io/badge/tests-46%2F46%20passed-success)]() 
[![Coverage](https://img.shields.io/badge/coverage-42%25-yellow)]()
[![Python](https://img.shields.io/badge/python-3.14-blue)]()

---

## 📖 文档索引

### 核心文档
- **[完整文档](docs/README.md)** - PEG原理、数学推导、案例分析
- **[系统设计](agent.md)** - 架构设计、模块说明、开发原则

### 使用指南
- **[快速开始](docs/QUICKSTART.md)** - 5分钟快速上手
- **[数据管理](data/README.md)** - 数据目录说明、Pipeline追踪
- **[数据采集](data_collection/README.md)** - 数据源使用、API说明
- **[回测引擎](backtest/README.md)** - 回测工具使用（Phase 2）

### 开发文档
- **[开发历程](docs/ITERATION_SUMMARY.md)** - 三次迭代详解
- **[重构说明](docs/REFACTORING.md)** - 项目重构记录
- **[重构总结](docs/REFACTORING_SUMMARY.md)** - 重构成果汇总
- **[合规性总结](docs/COMPLIANCE_SUMMARY.md)** - agent.md合规检查
- **[Phase管理](docs/phases/)** - 分阶段计划和总结
  - [Phase 1: Data Collection](docs/phases/phase_1_data_collection/) - ✅ 完成
  - [Phase 2: Backtest](docs/phases/phase_2_backtest/) - 📝 计划中

---

## ⚡ 快速开始

```bash
# 1. 安装依赖
uv sync

# 2. 获取七姐妹PEG数据
uv run python data_collection/fetch_current_peg.py

# 3. 查看结果
cat data/results/mag7_peg_*.md

# 4. 运行测试
uv run pytest tests/ -v
```

---

## 📁 项目结构

```
PEG-scaner/
├── 📄 README.md          本文件（索引）
├── 📄 agent.md           系统设计文档
├── 📄 config.yaml        配置文件
├── 📄 pyproject.toml     依赖定义
│
├── 📚 docs/              完整文档
├── 💾 data/              所有数据（5级持久化）
├── 🧠 core/              核心代码
├── 📡 data_collection/   数据采集
├── 📈 backtest/          回测引擎
└── 🧪 tests/             测试套件
```

**符合人类阅读习惯**：6个目录 + 4个文件

---

## 🎯 核心功能

✅ **双数据源验证** - yfinance + Alpha Vantage交叉验证  
✅ **严格数据质量** - 宁可为空，不要使用错的数据  
✅ **智能置信度** - HIGH/MEDIUM/LOW三级评估  
✅ **完整测试** - 46个测试用例，42%覆盖率  
✅ **数据持久化** - 5级数据存储，Pipeline追踪  

---

## 📊 最新数据（2025-11-15）

| 公司 | 利润 | 增速 | PE | PEG | 评级 |
|------|------|------|-----|-----|------|
| 京东<09618.hk> | ¥32.2B | 71.1% | 9.4 | **0.13** | 🏆 极度低估 |
| 比亚迪<01211.hk> | ¥42.1B | 34.0% | 8.8 | **0.26** | 🥈 低估 |
| 阿里巴巴<09988.hk> | ¥146.4B | 62.6% | 20.2 | **0.32** | 🥉 低估 |

完整数据请查看 [`data/results/`](data/results/)

---

## 🏗️ 设计原则

遵循 [agent.md](agent.md) 中定义的核心原则：

1. **SSOT (Single Source of Truth)** - 本质相同的东西放一起
2. **数据持久化** - 中间过程全部保存，便于调试
3. **数据质量优先** - 宁可为空，不要使用错的数据
4. **严格目录管理** - 6-7个目录 + 3-4个文件
5. **README索引** - 每层README是内容索引

---

## 🧪 测试状态

```bash
pytest tests/ -v

Result: ✅ 46/46 passed (1 skipped)
Coverage: 42%
```

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

**快速导航**：
[📖 完整文档](docs/README.md) | 
[🚀 快速开始](docs/QUICKSTART.md) | 
[🏗️ 系统设计](agent.md) | 
[💾 数据管理](data/README.md)
