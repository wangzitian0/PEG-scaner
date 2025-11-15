# 回测模块

**上级文档**：[返回项目README](../README.md)

> **Status**: Phase 2 (待开发)

---

## 简介

本模块实现基于PEG指标的股票交易策略回测系统，用于验证策略的历史表现。

## 核心功能

- ✅ 历史数据获取与处理
- ✅ PEG指标计算
- ✅ 交易信号生成
- ✅ 投资组合管理
- ✅ 绩效评估与报告

## 使用方法

### 单票回测

```bash
# 使用默认参数回测微软
uv run python -m backtest.run_single_backtest --ticker MSFT

# 自定义参数
uv run python -m backtest.run_single_backtest \
    --ticker MSFT \
    --buy-threshold 0.7 \
    --sell-threshold 1.8 \
    --start-date 2010-01-01
```

### 批量回测

```bash
# 回测多只股票
uv run python -m backtest.run_batch_backtest

# 指定股票列表
uv run python -m backtest.run_batch_backtest \
    --tickers MSFT,AMZN,00700.HK
```

### 参数优化

```bash
# 网格搜索最优参数
uv run python -m backtest.optimize_params --ticker MSFT
```

## 目录结构

```
backtest/
├── __init__.py
├── README.md
├── TODO.md              # 开发任务列表
├── cache/               # 历史数据缓存
├── results/             # 回测结果输出
├── run_single_backtest.py   # 单票回测脚本
├── run_batch_backtest.py    # 批量回测脚本
├── optimize_params.py       # 参数优化脚本
├── portfolio.py            # 投资组合管理
├── metrics.py              # 绩效指标计算
└── visualize.py            # 结果可视化
```

## 输出示例

### 回测报告（Markdown）

```markdown
# MSFT 回测报告

## 策略参数
- 买入阈值: PEG < 0.8
- 卖出阈值: PEG > 1.5
- 回测期间: 2000-01-01 至 2025-11-14

## 绩效指标
| 指标 | 数值 |
|------|------|
| 年化收益率 | 15.2% |
| 最大回撤 | -32.5% |
| 夏普比率 | 1.18 |
| 交易次数 | 23 |
| 胜率 | 65.2% |
```

### 交易记录（CSV）

```csv
date,action,price,peg,shares,cash,total_value
2001-03-01,BUY,25.30,0.75,3950.59,0,100000
2003-08-01,SELL,27.45,1.52,0,108428,108428
...
```

## 开发进度

详见 [TODO.md](TODO.md)

---

**最后更新**: 2025-11-15

