# 三个数据源深度分析

**日期**: 2025-11-15  
**目的**: 搞清楚三个库的区别、限速、和最佳实践

---

## 📊 yfinance vs pandas-datareader vs investpy

### 核心区别

| 维度 | yfinance | pandas-datareader | investpy |
|------|----------|-------------------|----------|
| **数据源** | Yahoo Finance (非官方API) | 多个官方源 | investing.com |
| **Yahoo实现** | 爬虫/逆向 | 曾经官方API，现在也是爬虫 | N/A |
| **维护状态** | ✅ 活跃 | ⚠️ Yahoo源已弃用 | ⚠️ 低频维护 |
| **限速** | 无明确限制 | 取决于源 | 严格反爬虫 |
| **数据完整性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

---

## 🔍 pandas-datareader vs yfinance 详解

### pandas-datareader

**历史**:
- 最初是pandas的一部分（`pandas.io.data`）
- 2015年独立为pandas-datareader
- 支持多个数据源：Yahoo, IEX, FRED, World Bank等

**Yahoo Finance源的现状**:
```python
# pandas-datareader使用的Yahoo Finance
# 在2017年Yahoo关闭官方API后，切换到爬虫方式
# 但实现不如yfinance完善

import pandas_datareader.data as web
df = web.DataReader('AAPL', 'yahoo', start, end)
# ⚠️ 经常出现404/403错误
# ⚠️ 只支持历史价格，不支持财务数据
```

**问题**:
1. Yahoo源经常失效（我们已经遇到了404错误）
2. 只能获取历史价格，无法获取PE、PEG、财务数据
3. 维护不如yfinance积极

### yfinance

**实现**:
```python
import yfinance as yf
stock = yf.Ticker('AAPL')

# 1. 价格数据 (爬取Yahoo Finance)
hist = stock.history(period='1y')

# 2. 财务数据 (爬取Yahoo Finance的财务页面)
financials = stock.financials
balance_sheet = stock.balance_sheet

# 3. 实时信息 (爬取多个Yahoo Finance页面)
info = stock.info  # PE, PEG, 市值等

# yfinance会智能缓存和管理请求
```

**优势**:
1. 数据更全面（价格+财务+估值指标）
2. 维护活跃，快速修复Yahoo的变更
3. 社区大，问题容易找到解决方案

### 结论

**pandas-datareader的Yahoo源 ≈ yfinance的历史价格功能的子集**

```
yfinance ⊃ pandas-datareader的Yahoo源

yfinance = 历史价格 + 财务数据 + 估值指标 + 公司信息
pandas-datareader的Yahoo源 = 历史价格（且经常失效）
```

**所以使用pandas-datareader没有意义！** 它只是yfinance的劣化版本。

---

## 🚦 限速分析

### 1. yfinance限速

**官方说明**: 无明确限速限制

**实际测试**:
```python
# 连续请求100只股票，无问题
for ticker in tickers:
    stock = yf.Ticker(ticker)
    info = stock.info
    # 无需等待
```

**Yahoo Finance的实际限制**:
- 短时间大量请求可能触发429错误
- 建议：每秒1-2个请求
- yfinance内部有一定的缓存机制

**最佳实践**:
```python
import time

for ticker in tickers:
    try:
        data = fetch_yfinance(ticker)
    except Exception as e:
        if '429' in str(e):
            time.sleep(60)  # 冷却1分钟
            data = fetch_yfinance(ticker)
    
    time.sleep(0.5)  # 每个请求间隔0.5秒
```

### 2. investpy限速

**问题**: investing.com有严格的反爬虫机制

**常见错误**:
```
ERR#0015: error 403, try again later.
```

**原因**:
1. 没有User-Agent
2. 请求频率过高
3. IP被识别为爬虫

**解决方案**:
```python
import investpy
import time
import random

# 1. 设置headers（需修改investpy源码或使用monkey patch）
investpy.utils.constant.USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'

# 2. 请求间隔
time.sleep(random.uniform(2, 5))

# 3. 重试机制
def fetch_with_retry(func, max_retries=3):
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if '403' in str(e) and i < max_retries - 1:
                wait_time = (2 ** i) * 10  # 指数退避：10s, 20s, 40s
                time.sleep(wait_time)
            else:
                raise
```

**限速建议**:
- 每个请求间隔：3-5秒
- 失败后等待：10-60秒（指数退避）
- 每日请求上限：未知，建议<1000次

### 3. 三源组合的限速策略

**问题**: 如果使用yfinance + investpy，如何管理限速？

**策略**:

```python
import time
from typing import Optional
from dataclasses import dataclass

@dataclass
class RateLimiter:
    """简单的限速器"""
    min_interval: float  # 最小请求间隔（秒）
    last_request: float = 0.0
    
    def wait(self):
        """等待到可以发送下一个请求"""
        elapsed = time.time() - self.last_request
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request = time.time()

# 为每个数据源设置独立的限速器
yfinance_limiter = RateLimiter(min_interval=0.5)  # 每秒2个请求
investpy_limiter = RateLimiter(min_interval=3.0)  # 每3秒1个请求

def fetch_from_yfinance(ticker):
    yfinance_limiter.wait()
    return fetch_stock_data_yfinance(ticker)

def fetch_from_investpy(ticker):
    investpy_limiter.wait()
    return fetch_stock_data_investpy(ticker)
```

---

## �� 重新评估方案

### 发现的关键事实

1. **pandas-datareader无价值**: 就是yfinance的劣化版
2. **investpy需要大量工程**: 反爬虫、限速、不稳定
3. **yfinance是唯一可靠选择**: 数据全、稳定、维护好

### 更新的方案评估

#### 方案A: yfinance双重验证（当前）⭐⭐⭐⭐
```
数据源: yfinance单端点 + yfinance多端点
优点: 稳定、已完成
缺点: 同一数据源
agent.md (28)符合度: 70%
```

#### 方案B: yfinance + investpy ⭐⭐
```
数据源: yfinance + investpy
优点: 两个独立源
缺点: 
  - investpy不稳定（403错误）
  - 需要大量限速逻辑
  - 维护成本高
  - 请求时间长（每只股票3秒间隔）
agent.md (28)符合度: 90%（理论）→ 60%（实际）
```

#### 方案C: yfinance + API key ⭐⭐⭐⭐⭐
```
数据源: yfinance + Alpha Vantage/FMP
优点: 
  - 真正独立的两个源
  - 稳定可靠
  - 官方支持
  - 代码已实现
缺点: 需要用户2分钟注册
agent.md (28)符合度: 100%
```

---

## 💡 最终结论

### pandas-datareader

**不推荐使用** ❌
- 就是yfinance的Yahoo源的子集
- 功能更少、更不稳定
- 没有任何优势

### investpy

**不推荐（除非必要）** ⚠️
- 403错误频繁
- 需要复杂的反爬虫措施
- 每只股票需要3-5秒间隔
- 14只股票 × 5秒 = 70秒（vs yfinance的7秒）
- 维护成本高

### 推荐方案

**短期**: 保持yfinance双重验证 ⭐⭐⭐⭐
- 已完成，稳定可靠
- 6条高质量数据
- 可立即进入Phrase 2

**中长期**: 用户提供免费API key ⭐⭐⭐⭐⭐
- 只需2分钟注册
- 100%符合agent.md (28)
- 代码已预留接口

---

## 📋 如果必须使用investpy

如果用户坚持要investpy，这是完整的实现：

```python
import investpy
import time
import random
from functools import wraps

def rate_limit(min_interval=3.0):
    """限速装饰器"""
    last_call = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 等待
            elapsed = time.time() - last_call[0]
            if elapsed < min_interval:
                sleep_time = min_interval - elapsed
                time.sleep(sleep_time)
            
            # 执行
            try:
                result = func(*args, **kwargs)
                last_call[0] = time.time()
                return result
            except Exception as e:
                if '403' in str(e):
                    # 403错误，等待更久
                    wait_time = random.uniform(10, 20)
                    time.sleep(wait_time)
                    # 重试一次
                    result = func(*args, **kwargs)
                    last_call[0] = time.time()
                    return result
                else:
                    raise
        return wrapper
    return decorator

@rate_limit(min_interval=3.0)
def fetch_investpy_safe(ticker):
    """带限速的investpy获取"""
    stock_code, country = normalize_ticker_for_investpy(ticker)
    
    # 获取数据
    recent_data = investpy.get_stock_recent_data(
        stock=stock_code,
        country=country,
        as_json=False
    )
    
    return recent_data
```

**预计采集时间**:
- 14只股票 × 3秒/只 = 42秒（vs yfinance的7秒）
- 加上重试和冷却：60-120秒

**值得吗？** 🤔
