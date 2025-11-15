# 回测模块 TODO

## 模块概述

实现基于PEG指标的历史回测系统，验证策略有效性。

---

## 开发任务

### Phase 1: 基础框架 🔨

#### 1.1 数据获取层
- [ ] **历史价格数据获取**
  - 实现 `fetch_historical_prices(ticker, start_date, end_date)`
  - 支持美股（MSFT, AMZN）和港股（00700.HK）
  - 月度开盘价数据
  - 数据源：yfinance
  
- [ ] **历史财务数据获取**
  - 季度财报EPS数据
  - 季度净利润数据
  - 数据对齐与插值处理
  
- [ ] **数据缓存机制**
  - 本地CSV缓存历史数据
  - 增量更新（仅获取缺失日期）
  - 缓存路径：`backtest/cache/{ticker}_history.csv`

#### 1.2 PEG计算引擎
- [ ] **历史PEG计算**
  ```python
  def calculate_historical_peg(ticker, date):
      """
      计算指定日期的PEG值
      
      Logic:
      1. 获取当月开盘价
      2. 获取最近4季度净利润（TTM）
      3. 计算同比增长率（vs 去年同期TTM）
      4. 计算PE = Price / (TTM_Profit / Shares)
      5. 计算PEG = PE / (Growth% * 100)
      
      Returns:
          PEGData(date, price, eps, growth, pe, peg)
      """
  ```

- [ ] **数据质量检查**
  - 处理缺失值：前向填充/线性插值
  - 异常值检测：PEG > 10 或 < 0 标记
  - 负增长处理：PEG设为NaN，跳过交易

#### 1.3 回测引擎核心
- [ ] **Portfolio类设计**
  ```python
  class Portfolio:
      def __init__(self, initial_cash=100000):
          self.cash = initial_cash
          self.positions = {}  # {ticker: shares}
          self.history = []    # 每月净值记录
      
      def buy(self, ticker, price, date):
          """全仓买入"""
          shares = self.cash / price * 0.999  # 0.1% 交易成本
          self.positions[ticker] = shares
          self.cash = 0
          self.log_trade('BUY', ticker, shares, price, date)
      
      def sell(self, ticker, price, date):
          """全仓卖出"""
          shares = self.positions.pop(ticker)
          self.cash = shares * price * 0.999
          self.log_trade('SELL', ticker, shares, price, date)
      
      def get_value(self, current_prices):
          """计算当前净值"""
          holdings_value = sum(
              self.positions.get(t, 0) * current_prices[t]
              for t in self.positions
          )
          return self.cash + holdings_value
  ```

- [ ] **回测主循环**
  ```python
  def run_backtest(ticker, buy_threshold=0.8, sell_threshold=1.5):
      portfolio = Portfolio(initial_cash=100000)
      peg_history = calculate_all_peg(ticker, '2000-01', '2025-11')
      
      for month_data in peg_history:
          peg = month_data.peg
          price = month_data.price
          
          # 交易逻辑
          if peg < buy_threshold and not portfolio.has_position(ticker):
              portfolio.buy(ticker, price, month_data.date)
          
          elif peg > sell_threshold and portfolio.has_position(ticker):
              portfolio.sell(ticker, price, month_data.date)
          
          # 记录月度净值
          portfolio.record_value(month_data.date, {ticker: price})
      
      return BacktestResult(portfolio)
  ```

---

### Phase 2: 绩效分析 📊

#### 2.1 核心指标计算
- [ ] **年化收益率**
  ```python
  def calculate_annual_return(portfolio):
      years = (end_date - start_date).days / 365.25
      total_return = portfolio.final_value / portfolio.initial_cash
      annual_return = (total_return ** (1 / years)) - 1
      return annual_return
  ```

- [ ] **最大回撤**
  ```python
  def calculate_max_drawdown(value_history):
      peak = value_history[0]
      max_dd = 0
      for value in value_history:
          if value > peak:
              peak = value
          dd = (peak - value) / peak
          max_dd = max(max_dd, dd)
      return max_dd
  ```

- [ ] **夏普比率**
  ```python
  def calculate_sharpe_ratio(returns, risk_free_rate=0.02):
      excess_returns = returns - risk_free_rate / 12  # 月度化
      return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(12)
  ```

- [ ] **交易统计**
  - 总交易次数
  - 盈利次数/亏损次数
  - 胜率 = 盈利次数 / 总次数
  - 平均持仓天数

#### 2.2 报告生成
- [ ] **Markdown报告**
  - 策略参数总结
  - 核心绩效指标表格
  - 交易记录表（日期、动作、价格、PEG）
  - 净值曲线图（使用matplotlib生成PNG）

- [ ] **CSV数据导出**
  - `{ticker}_backtest_trades.csv`：交易记录
  - `{ticker}_backtest_monthly_value.csv`：月度净值
  - `{ticker}_backtest_peg_history.csv`：历史PEG数据

---

### Phase 3: 批量回测 🚀

#### 3.1 多标的回测
- [ ] **批量运行脚本**
  ```python
  # run_batch_backtest.py
  
  TICKERS = ['MSFT', 'AMZN', '00700.HK', 'SPY', 'VGT', 'KWEB']
  
  results = {}
  for ticker in TICKERS:
      print(f"回测 {ticker}...")
      result = run_backtest(ticker)
      results[ticker] = result
  
  # 生成对比报告
  generate_comparison_report(results)
  ```

- [ ] **对比报告生成**
  - 所有标的绩效对比表（Markdown）
  - 横向对比：年化收益、最大回撤、夏普
  - 最佳/最差标的分析

#### 3.2 参数优化
- [ ] **网格搜索**
  ```python
  # optimize_params.py
  
  buy_thresholds = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
  sell_thresholds = [1.2, 1.5, 1.8, 2.0, 2.5]
  
  best_sharpe = -999
  best_params = None
  
  for buy in buy_thresholds:
      for sell in sell_thresholds:
          if sell <= buy:
              continue
          
          result = run_backtest('MSFT', buy, sell)
          sharpe = result.sharpe_ratio
          
          if sharpe > best_sharpe:
              best_sharpe = sharpe
              best_params = (buy, sell)
  
  print(f"最佳参数: 买入PEG<{best_params[0]}, 卖出PEG>{best_params[1]}")
  ```

- [ ] **防止过拟合**
  - 训练集（2000-2018）+ 验证集（2019-2025）
  - 参数在训练集优化，验证集测试
  - Walk-forward分析

---

### Phase 4: 可视化增强 📈

#### 4.1 图表生成
- [ ] **净值曲线**
  ```python
  import matplotlib.pyplot as plt
  
  def plot_value_curve(backtest_result, benchmark=None):
      plt.figure(figsize=(12, 6))
      plt.plot(result.dates, result.values, label='策略净值', linewidth=2)
      
      if benchmark:
          plt.plot(benchmark.dates, benchmark.values, 
                   label='基准（买入持有）', linestyle='--')
      
      plt.xlabel('日期')
      plt.ylabel('净值')
      plt.title(f'{ticker} PEG策略回测净值曲线')
      plt.legend()
      plt.grid(True, alpha=0.3)
      plt.savefig(f'backtest/results/{ticker}_value_curve.png')
  ```

- [ ] **PEG历史走势**
  - X轴：时间
  - Y轴：PEG值
  - 标注买入/卖出点
  - 水平线：买入阈值、卖出阈值

- [ ] **回撤曲线**
  - 可视化最大回撤发生时间
  - 回撤恢复时间分析

---

## 数据结构设计

### 输入数据格式

#### historical_prices.csv
```csv
date,open,high,low,close,volume
2000-01-01,100.5,102.3,99.8,101.2,10000000
2000-02-01,101.0,105.0,100.5,104.5,12000000
```

#### historical_financials.csv
```csv
date,revenue,net_income,eps,shares_outstanding
2000-Q1,1000000000,100000000,1.25,80000000
2000-Q2,1100000000,120000000,1.50,80000000
```

### 中间数据格式

#### peg_history.csv
```csv
date,price,ttm_profit,ttm_growth_rate,pe,peg
2000-01,100.5,400000000,0.25,20.0,0.80
2000-02,104.5,420000000,0.28,21.0,0.75
```

### 输出数据格式

#### backtest_result.csv
```csv
date,action,price,peg,shares,cash,total_value
2000-01,BUY,100.5,0.75,995.02,0,100000
2000-02,HOLD,104.5,0.78,995.02,0,104000
2001-05,SELL,150.2,1.55,0,149328,149328
```

---

## 关键技术挑战

### 挑战1: 港股数据质量
**问题**：港股历史财务数据不完整  
**方案**：
1. 多数据源验证（yfinance + efinancial）
2. 季报缺失时使用年报/半年报估算
3. 标记数据置信度（high/medium/low）

### 挑战2: 前复权处理
**问题**：股票分拆/分红影响价格连续性  
**方案**：
- 使用yfinance的adjusted close价格
- 财务数据同步调整（股本变化）

### 挑战3: 增长率计算
**问题**：利润波动导致增长率失真  
**方案**：
- 使用TTM平滑短期波动
- 计算3年CAGR作为备用指标
- 负增长时跳过交易信号

### 挑战4: 回测偏差
**问题**：未来信息泄漏、存活偏差  
**方案**：
- 使用月初开盘价（避免看到当月数据）
- 财务数据使用发布日期（延迟45天）
- 包含已退市公司数据

---

## 测试计划

### 单元测试
```python
# test_backtest.py

def test_peg_calculation():
    """测试PEG计算准确性"""
    price = 100
    eps = 5
    growth = 0.20
    
    pe = price / eps  # 20
    peg = pe / (growth * 100)  # 1.0
    
    assert abs(peg - 1.0) < 0.01

def test_portfolio_buy():
    """测试买入逻辑"""
    portfolio = Portfolio(initial_cash=100000)
    portfolio.buy('MSFT', price=100, date='2020-01-01')
    
    assert portfolio.cash < 100  # 扣除交易成本
    assert portfolio.positions['MSFT'] > 0
    assert portfolio.has_position('MSFT')

def test_max_drawdown():
    """测试回撤计算"""
    values = [100, 120, 110, 90, 95, 130]
    mdd = calculate_max_drawdown(values)
    
    # 从120跌到90，回撤25%
    assert abs(mdd - 0.25) < 0.01
```

### 集成测试
- [ ] 完整回测流程测试（小数据集）
- [ ] 数据获取容错测试
- [ ] 结果输出格式验证

---

## 性能优化

### 计算优化
- [ ] 使用pandas向量化计算替代循环
- [ ] 缓存中间结果（TTM利润）
- [ ] 并行处理多标的回测

### 内存优化
- [ ] 分块读取大文件
- [ ] 及时释放无用数据
- [ ] 使用生成器处理月度迭代

---

## 里程碑

- [ ] **M1 (Week 1)**：完成单标的基础回测（MSFT）
- [ ] **M2 (Week 2)**：完成绩效分析和报告生成
- [ ] **M3 (Week 3)**：完成批量回测和参数优化
- [ ] **M4 (Week 4)**：完成可视化和文档完善

---

## 依赖项

```toml
[dependencies]
pandas = ">=2.2.0"
numpy = ">=1.26.0"
yfinance = ">=0.2.38"
matplotlib = ">=3.8.0"
```

---

## 参考资料

1. [Quantopian Lecture Series - Backtesting](https://www.quantopian.com/lectures)
2. [Python for Finance (2nd Edition)](https://www.oreilly.com/library/view/python-for-finance/9781492024323/)
3. [Backtrader Documentation](https://www.backtrader.com/docu/)

---

**最后更新**：2025-11-15  
**负责人**：Backend Team

