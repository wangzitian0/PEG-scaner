# PEG-scaner 项目进度

**项目状态**: 🚀 Phrase 1 完成，Phrase 2 准备中  
**最后更新**: 2025-11-15

---

## 📊 项目概览

**PEG-scaner** 是一个基于PEG指标的科技股估值和策略回测工具。

### 核心功能
1. ✅ **数据采集** - 多源获取股票财务数据和实时价格
2. ✅ **PEG计算** - 自动计算美股+港股科技公司的PEG比率
3. 🔄 **策略回测** - 基于PEG阈值的买卖策略回测（开发中）
4. 📊 **结果展示** - 生成符合schema的CSV数据文件

---

## 🎯 Phrase 进度

### ✅ Phrase 1: 数据采集模块 (100% 完成)

**完成时间**: 2025-11-15  
**状态**: ✅ 已完成，可投入生产

#### 核心交付物
- ✅ 10个Python模块（数据获取、验证、格式化）
- ✅ 2个数据源（yfinance + Alpha Vantage）
- ✅ 55个测试用例（全部通过）
- ✅ Schema-based数据组织
- ✅ 数据质量验证和置信度评分

#### 实际数据产物
- ✅ `x-data/stock_fundamental/stock_fundamental-mag7-yfinance-20251115.csv`
- ✅ 11/14只股票成功获取PEG数据
- ✅ 数据质量：HIGH confidence

#### 文档
- [Phrase 1 详细状态](phrases/phrase_1_data_collection/STATUS.md)
- [完成度检查表](phrases/phrase_1_data_collection/CHECKLIST.md)
- [实现计划](phrases/phrase_1_data_collection/PLAN.md)
- [总结报告](phrases/phrase_1_data_collection/SUMMARY.md)
- [第三数据源规划](phrases/phrase_1_data_collection/THIRD_DATA_SOURCE.md)

---

### 🔄 Phrase 2: 策略回测模块 (准备中)

**状态**: 📝 计划阶段

#### 目标
- [ ] 获取历史月度数据（2000-2025）
- [ ] 计算历史PEG值
- [ ] 实现PEG策略回测引擎
- [ ] 参数优化和敏感性分析
- [ ] 生成回测报告

#### 回测标的
- 个股：腾讯、微软、亚马逊
- ETF：SP500、VGT、KWEB

#### 文档
- [Phrase 2 计划](phrases/phrase_2_backtest/PLAN.md)

---

### 🔮 Phrase 3: 策略计算与筛选 (未开始)

**状态**: ⏭️ 待启动

#### 目标
- [ ] 获取VGT+KWEB完整成分股列表
- [ ] 批量计算所有成分股PEG
- [ ] 筛选：利润>$10M，PEG最低15家
- [ ] 生成投资组合建议

---

## 📈 关键指标

| 指标 | 数值 | 目标 | 状态 |
|------|------|------|------|
| **测试覆盖率** | 39% | 50%+ | 🟡 |
| **测试通过率** | 100% (55/55) | 100% | ✅ |
| **数据源数量** | 2个 | 3个 | 🟡 |
| **代码模块** | 10个 | - | ✅ |
| **文档完整性** | 100% | 100% | ✅ |
| **Agent.md合规** | 90%+ | 100% | 🟢 |

---

## 🏗️ 技术栈

### 核心技术
- **语言**: Python 3.14
- **包管理**: uv
- **数据源**: yfinance, Alpha Vantage
- **测试**: pytest (55个测试)
- **Schema**: Pydantic
- **数据格式**: CSV (schema-name-source-date)

### 数据组织
```
x-data/
├── stock_fundamental/    # 基本面数据（PE, PEG, 增长率）
├── stock_daily/          # 日度行情
├── etf_portfolio/        # ETF持仓
├── backtest_result/      # 回测结果
└── analysis_result/      # 分析结果
```

---

## 📚 文档结构

### 项目文档
- **[本文档]** - One-page 宏观进度（你在这里）
- [PEG理论文档](PEG_THEORY.md) - PEG原理、数学推导、案例分析

### Phrase文档
- [Phrase 1: 数据采集](phrases/phrase_1_data_collection/)
  - STATUS.md - 完成状态报告
  - SUMMARY.md - 总结
  - CHECKLIST.md - 检查清单
  - PLAN.md - 实现计划
  - append_prompt.md - 提示词追溯
  - THIRD_DATA_SOURCE.md - 第三数据源规划
  
- [Phrase 2: 策略回测](phrases/phrase_2_backtest/)
  - PLAN.md - 回测计划

### 历史文档（归档）
- [归档文档](phrases/archived/) - 开发历程、重构记录等

---

## 🚀 快速开始

### 安装依赖
```bash
# 安装uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装项目依赖
cd PEG-scaner
uv sync
```

### 运行数据采集（Phrase 1）
```bash
# 获取当前PEG数据（美股+港股七姐妹）
uv run python data_collection/fetch_current_peg_new.py

# 查看结果
cat x-data/stock_fundamental/stock_fundamental-mag7-yfinance-*.csv
```

### 运行测试
```bash
# 运行所有测试
uv run pytest tests/ -v

# 运行数据质量测试
uv run pytest tests/test_data_quality.py -v
```

---

## 🎯 下一步计划

### 短期（Phrase 2）
1. ✅ 完成Phrase 1数据采集模块
2. 🔄 设计回测引擎架构
3. 📝 实现历史数据获取
4. 📝 开发PEG策略回测

### 中期（Phrase 3）
1. 获取VGT+KWEB成分股
2. 批量PEG计算
3. 低PEG筛选工具

### 长期
1. 添加第三数据源（Phase 1.5）
2. 提升测试覆盖率至50%+
3. Web界面展示
4. 实时数据更新

---

## 📊 数据产物示例

### Phrase 1 最新数据 (2025-11-15)

**PEG最低Top 5**:
1. 🥇 京东 (09618.HK): PEG=0.13, PE=9.38
2. 🥈 比亚迪 (01211.HK): PEG=0.26, PE=8.79
3. 🥉 阿里巴巴 (09988.HK): PEG=0.32, PE=20.20
4. 亚马逊 (AMZN): PEG=0.35, PE=32.80
5. 谷歌 (GOOGL): PEG=0.36, PE=12.94

**数据质量**: HIGH confidence  
**数据来源**: yfinance

---

## 📖 相关资源

### 代码模块
- [data_collection/](../data_collection/) - 数据采集模块
- [core/](../core/) - 核心功能（Schema, 验证, IO）
- [tests/](../tests/) - 测试套件
- [backtest/](../backtest/) - 回测模块（Phrase 2）

### 数据
- [x-data/](../x-data/) - 所有程序生成的数据
- [x-log/](../x-log/) - 日志
- [x-coverage/](../x-coverage/) - 测试覆盖率报告

### 配置
- [agent.md](../agent.md) - 项目核心指令和设计原则
- [config.yaml](../config.yaml) - 运行配置
- [pyproject.toml](../pyproject.toml) - 项目依赖

---

## 🤝 贡献指南

本项目遵循严格的工程准则（详见[agent.md](../agent.md)）：

1. **数据质量优先** - 宁可为空，不要使用错的数据
2. **多源验证** - 至少2个数据源一致才采用
3. **Schema规范** - 所有数据遵循schema组织
4. **测试驱动** - 每次改代码都要跑测试
5. **文档同步** - 改动要更新相关README

---

## 📝 变更日志

### 2025-11-15
- ✅ Phrase 1 数据采集模块完成（100%）
- ✅ 实现2源数据验证（yfinance + Alpha Vantage）
- ✅ 完成55个测试用例
- ✅ 建立Schema-based数据组织
- ✅ 生成首批PEG数据（11只股票）
- ✅ 文档规范化和目录重组

---

**上级文档**: [返回项目根目录](../README.md)

