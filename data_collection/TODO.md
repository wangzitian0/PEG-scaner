# 数据采集模块 TODO

## 模块概述

负责从多个免费数据源获取股票实时数据，计算PEG指标，并提供数据验证与容错机制。

---

## 开发任务

### Phase 1: 核心数据源集成 🔌

#### 1.1 yfinance数据源（主数据源）
- [ ] **基础数据获取**
  ```python
  # fetch_yfinance.py
  
  import yfinance as yf
  
  def fetch_stock_data(ticker: str) -> StockData:
      """
      获取股票基础数据
      
      Returns:
          StockData(
              ticker, price, market_cap,
              pe_ratio, eps, net_income,
              revenue, shares_outstanding
          )
      """
      stock = yf.Ticker(ticker)
      
      # 价格数据
      price = stock.info['currentPrice']
      
      # 财务数据
      financials = stock.financials
      income_stmt = stock.income_stmt
      
      # TTM净利润（最近4季度）
      quarterly_income = stock.quarterly_income_stmt
      ttm_profit = quarterly_income.loc['Net Income'].iloc[:4].sum()
      
      # 去年同期TTM利润
      ttm_profit_last_year = quarterly_income.loc['Net Income'].iloc[4:8].sum()
      
      # 增长率
      growth_rate = (ttm_profit - ttm_profit_last_year) / ttm_profit_last_year
      
      # PE和PEG
      pe = stock.info['trailingPE']
      peg = pe / (growth_rate * 100)
      
      return StockData(
          ticker=ticker,
          price=price,
          ttm_profit=ttm_profit,
          growth_rate=growth_rate,
          pe=pe,
          peg=peg
      )
  ```

- [ ] **港股数据支持**
  - 后缀处理：`00700.HK`
  - 货币转换（HKD → USD）
  - 特殊字段映射

- [ ] **异常处理**
  - 网络超时重试（3次）
  - 数据缺失标记
  - 日志记录

#### 1.2 Alpha Vantage数据源（备用）
- [ ] **API封装**
  ```python
  # fetch_alpha_vantage.py
  
  import requests
  from dotenv import load_dotenv
  import os
  
  load_dotenv()
  API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
  
  def fetch_from_alpha_vantage(ticker: str) -> StockData:
      """
      从Alpha Vantage获取数据
      
      API Endpoints:
      - GLOBAL_QUOTE: 实时价格
      - INCOME_STATEMENT: 财务报表
      - EARNINGS: 盈利数据
      """
      base_url = 'https://www.alphavantage.co/query'
      
      # 1. 获取价格
      params = {
          'function': 'GLOBAL_QUOTE',
          'symbol': ticker,
          'apikey': API_KEY
      }
      response = requests.get(base_url, params=params)
      price_data = response.json()['Global Quote']
      price = float(price_data['05. price'])
      
      # 2. 获取财务数据
      params['function'] = 'INCOME_STATEMENT'
      response = requests.get(base_url, params=params)
      financials = response.json()['annualReports']
      
      # 提取最近财报
      latest = financials[0]
      net_income = float(latest['netIncome'])
      
      # ... 后续计算逻辑
      
      return StockData(...)
  ```

- [ ] **API限流处理**
  - 免费版：5次/分钟，500次/天
  - 使用队列缓冲请求
  - 自动等待间隔

- [ ] **数据格式转换**
  - 统一为StockData格式
  - 字段映射表

#### 1.3 数据验证与选择
- [ ] **双源验证**
  ```python
  # data_validator.py
  
  def validate_and_select(data_yf: StockData, data_av: StockData) -> StockData:
      """
      验证并选择数据
      
      规则：
      1. 两源数据偏差<5%：使用yfinance（更新快）
      2. 偏差>5%：标记为WARNING，使用平均值
      3. 单源失败：使用另一源，标记置信度为MEDIUM
      """
      if not data_yf:
          return data_av, Confidence.MEDIUM
      if not data_av:
          return data_yf, Confidence.MEDIUM
      
      # 计算PE偏差
      pe_diff = abs(data_yf.pe - data_av.pe) / data_av.pe
      
      if pe_diff < 0.05:
          return data_yf, Confidence.HIGH
      else:
          logger.warning(f"PE偏差过大: {data_yf.ticker} - yf:{data_yf.pe}, av:{data_av.pe}")
          # 使用平均值
          averaged_data = average_stock_data(data_yf, data_av)
          return averaged_data, Confidence.LOW
  ```

- [ ] **数据质量检查**
  - PE范围：0 < PE < 300
  - PEG范围：-5 < PEG < 10
  - 利润非零
  - 增长率：-100% < g < 500%

---

### Phase 2: ETF成分股获取 📋

#### 2.1 ETF Holdings爬取
- [ ] **VGT成分股获取**
  ```python
  # fetch_etf_holdings.py
  
  def fetch_vgt_holdings() -> List[str]:
      """
      获取VGT（Vanguard Information Technology ETF）成分股
      
      数据源：
      1. Vanguard官网（需爬虫）
      2. etfdb.com API
      3. yfinance（可能不完整）
      
      Returns:
          ['AAPL', 'MSFT', 'NVDA', ...]  # 约330只
      """
      # 方法1: etfdb.com（推荐）
      url = 'https://etfdb.com/etf/VGT/#holdings'
      response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
      soup = BeautifulSoup(response.text, 'html.parser')
      
      # 解析持仓表格
      table = soup.find('table', {'class': 'table'})
      tickers = []
      for row in table.find_all('tr')[1:]:  # 跳过表头
          ticker = row.find_all('td')[1].text.strip()
          tickers.append(ticker)
      
      return tickers
  ```

- [ ] **KWEB成分股获取**
  - 数据源：KraneShares官网 / etfdb.com
  - 约50只中国互联网股票
  - 包含ADR（BABA）和港股（00700.HK）

- [ ] **SPY成分股获取**
  - 数据源：slickcharts.com / wikipedia
  - 标普500成分股列表
  - 定期更新（季度调仓）

#### 2.2 持仓权重处理
- [ ] **权重数据获取**
  ```python
  @dataclass
  class Holding:
      ticker: str
      name: str
      weight: float  # 百分比
      shares: int
      market_value: float
  
  def fetch_weighted_holdings(etf_ticker: str) -> List[Holding]:
      """获取ETF带权重的持仓"""
      ...
  ```

- [ ] **成分股更新机制**
  - 本地缓存成分股列表（JSON）
  - 每周检查更新
  - 记录变更历史

---

### Phase 3: 批量数据采集 🚀

#### 3.1 当前PEG表格生成
- [ ] **美股+港股七姐妹**
  ```python
  # fetch_current_peg.py
  
  MAG7_US = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA']
  HK_TECH = ['00700.HK', '09988.HK', '03690.HK', '01810.HK', 
             '09618.HK', '01211.HK', '09999.HK']
  
  def fetch_mag7_peg():
      results = []
      for ticker in MAG7_US + HK_TECH:
          try:
              data = fetch_stock_data(ticker)
              results.append({
                  '公司名称': get_company_name(ticker),
                  '净利润': format_profit(data.ttm_profit),
                  '利润增速': f"{data.growth_rate:.1%}",
                  'TTM PE': f"{data.pe:.1f}",
                  'PEG': f"{data.peg:.2f}"
              })
          except Exception as e:
              logger.error(f"获取{ticker}数据失败: {e}")
              results.append({'公司名称': ticker, 'Error': str(e)})
      
      # 保存为CSV
      df = pd.DataFrame(results)
      df.to_csv('results/mag7_peg_2025-11-14.csv', index=False)
      
      # 生成Markdown表格
      md_table = df.to_markdown(index=False)
      with open('results/mag7_peg_2025-11-14.md', 'w') as f:
          f.write(md_table)
      
      return results
  ```

- [ ] **公司名称映射**
  ```python
  COMPANY_NAMES = {
      'AAPL': '苹果<AAPL.US>',
      'MSFT': '微软<MSFT.US>',
      '00700.HK': '腾讯<00700.HK>',
      ...
  }
  ```

#### 3.2 VGT+KWEB完整列表
- [ ] **合并去重**
  ```python
  def fetch_vgt_kweb_combined():
      vgt_holdings = fetch_vgt_holdings()
      kweb_holdings = fetch_kweb_holdings()
      
      # 合并并去重（BABA和09988.HK是同一公司）
      all_tickers = list(set(vgt_holdings + kweb_holdings))
      
      logger.info(f"VGT: {len(vgt_holdings)}只, KWEB: {len(kweb_holdings)}只")
      logger.info(f"合并后: {len(all_tickers)}只")
      
      return all_tickers
  ```

- [ ] **批量PEG计算**
  ```python
  from concurrent.futures import ThreadPoolExecutor
  
  def calculate_peg_batch(tickers: List[str]) -> pd.DataFrame:
      """并行计算多只股票的PEG"""
      with ThreadPoolExecutor(max_workers=10) as executor:
          results = executor.map(fetch_stock_data, tickers)
      
      data = [r for r in results if r is not None]
      df = pd.DataFrame([asdict(d) for d in data])
      return df
  ```

#### 3.3 低PEG筛选
- [ ] **筛选逻辑**
  ```python
  # screen_low_peg.py
  
  def screen_low_peg(min_profit_usd=10_000_000, top_n=15):
      """
      筛选最低PEG股票
      
      Args:
          min_profit_usd: 最低利润门槛（美元）
          top_n: 返回前N只
      
      Returns:
          DataFrame with columns: [ticker, name, profit, growth, pe, peg]
      """
      # 1. 获取全部股票
      all_tickers = fetch_vgt_kweb_combined()
      
      # 2. 批量计算PEG
      df = calculate_peg_batch(all_tickers)
      
      # 3. 过滤条件
      df_filtered = df[
          (df['ttm_profit'] > min_profit_usd) &  # 利润筛选
          (df['peg'] > 0) &                      # PEG正值
          (df['peg'] < 5) &                      # 排除极端值
          (df['growth_rate'] > 0)                # 正增长
      ]
      
      # 4. 排序并取前N
      df_sorted = df_filtered.sort_values('peg').head(top_n)
      
      # 5. 格式化输出
      df_sorted['公司名称'] = df_sorted['ticker'].map(format_ticker_name)
      df_sorted['净利润'] = df_sorted['ttm_profit'].apply(format_profit)
      df_sorted['利润增速'] = df_sorted['growth_rate'].apply(lambda x: f"{x:.1%}")
      df_sorted['TTM PE'] = df_sorted['pe'].apply(lambda x: f"{x:.1f}")
      df_sorted['PEG'] = df_sorted['peg'].apply(lambda x: f"{x:.2f}")
      
      # 6. 保存结果
      output = df_sorted[['公司名称', '净利润', '利润增速', 'TTM PE', 'PEG']]
      output.to_csv('results/low_peg_top15.csv', index=False)
      
      return output
  ```

---

### Phase 4: 数据缓存与管理 💾

#### 4.1 缓存系统
- [ ] **本地缓存设计**
  ```python
  # cache_manager.py
  
  CACHE_DIR = 'data_collection/cache'
  CACHE_EXPIRY = 24 * 3600  # 24小时
  
  def get_cached_data(ticker: str, date: str = 'latest') -> Optional[StockData]:
      """
      从缓存读取数据
      
      Cache structure:
      cache/
        ├── MSFT_2025-11-14.json
        ├── 00700.HK_2025-11-14.json
        └── ...
      """
      cache_file = f"{CACHE_DIR}/{ticker}_{date}.json"
      
      if not os.path.exists(cache_file):
          return None
      
      # 检查过期
      file_time = os.path.getmtime(cache_file)
      if time.time() - file_time > CACHE_EXPIRY:
          return None
      
      with open(cache_file, 'r') as f:
          data_dict = json.load(f)
      
      return StockData(**data_dict)
  
  def save_to_cache(ticker: str, data: StockData):
      """保存到缓存"""
      date = datetime.now().strftime('%Y-%m-%d')
      cache_file = f"{CACHE_DIR}/{ticker}_{date}.json"
      
      os.makedirs(CACHE_DIR, exist_ok=True)
      with open(cache_file, 'w') as f:
          json.dump(asdict(data), f, indent=2)
  ```

- [ ] **缓存清理策略**
  - 保留最近7天数据
  - 定期清理过期文件
  - 缓存大小限制（1GB）

#### 4.2 数据更新机制
- [ ] **增量更新**
  - 检查本地缓存时间戳
  - 仅更新过期/缺失数据
  - 批量更新时显示进度条

- [ ] **定时任务**
  ```python
  # scheduler.py
  
  import schedule
  import time
  
  def daily_update_job():
      """每日更新任务"""
      logger.info("开始每日数据更新...")
      
      # 更新ETF成分股列表
      update_etf_holdings()
      
      # 更新七姐妹PEG
      fetch_mag7_peg()
      
      # 更新低PEG筛选
      screen_low_peg()
      
      logger.info("数据更新完成!")
  
  # 每天早上8点执行
  schedule.every().day.at("08:00").do(daily_update_job)
  
  while True:
      schedule.run_pending()
      time.sleep(60)
  ```

---

## 数据结构设计

### StockData类
```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class StockData:
    ticker: str
    date: str  # ISO format: 2025-11-14
    
    # 价格数据
    price: float
    market_cap: float
    
    # 财务数据
    ttm_profit: float  # TTM净利润
    ttm_revenue: float
    shares_outstanding: float
    
    # 增长数据
    growth_rate: float  # YoY增长率
    
    # 估值数据
    pe: float
    peg: float
    
    # 元数据
    currency: str = 'USD'
    data_source: str = 'yfinance'
    confidence: str = 'HIGH'  # HIGH/MEDIUM/LOW
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    def to_table_row(self) -> dict:
        """转换为表格行"""
        return {
            '公司名称': format_ticker_name(self.ticker),
            '净利润': format_profit(self.ttm_profit),
            '利润增速': f"{self.growth_rate:.1%}",
            'TTM PE': f"{self.pe:.1f}",
            'PEG': f"{self.peg:.2f}"
        }
```

### 输出格式

#### CSV格式
```csv
ticker,name,profit,growth_rate,pe,peg,date,confidence
MSFT,微软<MSFT.US>,88100000000,0.218,35.2,1.61,2025-11-14,HIGH
AMZN,亚马逊<AMZN.US>,48300000000,2.26,42.8,0.19,2025-11-14,HIGH
00700.HK,腾讯<00700.HK>,179400000000,0.362,21.5,0.59,2025-11-14,HIGH
```

#### Markdown格式
```markdown
| 公司名称 | 净利润 | 利润增速 | TTM PE | PEG |
|---------|--------|---------|--------|-----|
| 微软<MSFT.US> | $88.1B | 21.8% | 35.2 | **1.61** |
| 亚马逊<AMZN.US> | $48.3B | 226% | 42.8 | **0.19** |
| 腾讯<00700.HK> | ¥179.4B | 36.2% | 21.5 | **0.59** |
```

---

## 技术挑战与方案

### 挑战1: 港股数据获取
**问题**：港股代码格式特殊（00700.HK），部分API不支持  
**方案**：
- yfinance支持港股（使用.HK后缀）
- 货币转换：HKD × 0.128 = USD
- 备用：使用ADR代码（TCEHY代替00700.HK）

### 挑战2: 数据源限流
**问题**：免费API有访问频率限制  
**方案**：
- yfinance：无官方限制，但建议<2000次/小时
- Alpha Vantage：5次/分，添加请求队列
- 实现指数退避重试

### 挑战3: TTM数据计算
**问题**：季报数据不完整或延迟发布  
**方案**：
- 优先使用yfinance的quarterly_financials
- 缺失时用年报/半年报估算：`Q_missing = Annual / 4`
- 标记数据置信度

### 挑战4: 数据一致性
**问题**：不同数据源结果偏差  
**方案**：
- 建立验证规则（偏差阈值5%）
- 自动标记异常数据
- 人工复核机制

---

## 辅助工具

### format_utils.py
```python
def format_profit(profit: float, currency='USD') -> str:
    """格式化利润显示"""
    if abs(profit) >= 1e9:
        return f"${profit/1e9:.1f}B" if currency == 'USD' else f"¥{profit/1e9:.1f}B"
    elif abs(profit) >= 1e6:
        return f"${profit/1e6:.1f}M" if currency == 'USD' else f"¥{profit/1e6:.1f}M"
    else:
        return f"${profit:,.0f}"

def format_ticker_name(ticker: str) -> str:
    """格式化股票代码为显示名称"""
    name_map = {
        'MSFT': '微软<MSFT.US>',
        'AMZN': '亚马逊<AMZN.US>',
        '00700.HK': '腾讯<00700.HK>',
        # ... 更多映射
    }
    return name_map.get(ticker, ticker)

def get_company_name(ticker: str) -> str:
    """获取公司全称"""
    stock = yf.Ticker(ticker)
    return stock.info.get('longName', ticker)
```

---

## 测试计划

### 单元测试
```python
# test_data_collection.py

def test_fetch_stock_data():
    """测试数据获取"""
    data = fetch_stock_data('MSFT')
    
    assert data.ticker == 'MSFT'
    assert data.price > 0
    assert 0 < data.pe < 300
    assert data.peg is not None

def test_cache_system():
    """测试缓存机制"""
    ticker = 'AAPL'
    
    # 第一次获取（应该调用API）
    data1 = fetch_stock_data(ticker)
    
    # 第二次获取（应该从缓存读取）
    data2 = fetch_stock_data(ticker)
    
    assert data1.peg == data2.peg
    assert get_cached_data(ticker) is not None

def test_data_validation():
    """测试数据验证"""
    # 构造异常数据
    bad_data = StockData(
        ticker='TEST',
        pe=-10,  # 异常PE
        peg=100,  # 异常PEG
        ...
    )
    
    assert not validate_stock_data(bad_data)
```

### 集成测试
- [ ] 完整流程测试（获取→验证→缓存→输出）
- [ ] 多数据源容错测试
- [ ] ETF成分股更新测试

---

## 里程碑

- [ ] **M1 (Week 1)**：完成yfinance数据源和美股七姐妹PEG
- [ ] **M2 (Week 2)**：完成港股支持和双数据源验证
- [ ] **M3 (Week 3)**：完成ETF成分股获取和低PEG筛选
- [ ] **M4 (Week 4)**：完成缓存系统和定时更新

---

## 环境变量配置

### .env文件
```bash
# Alpha Vantage API Key（可选）
ALPHA_VANTAGE_API_KEY=your_api_key_here

# 数据源选择
PRIMARY_DATA_SOURCE=yfinance
FALLBACK_DATA_SOURCE=alpha_vantage

# 缓存配置
CACHE_ENABLED=true
CACHE_EXPIRY_HOURS=24
CACHE_DIR=./cache

# 日志级别
LOG_LEVEL=INFO
```

---

## 参考资料

1. [yfinance Documentation](https://github.com/ranaroussi/yfinance)
2. [Alpha Vantage API Docs](https://www.alphavantage.co/documentation/)
3. [ETFdb.com](https://etfdb.com/)
4. [Pandas DataFrame to Markdown](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_markdown.html)

---

**最后更新**：2025-11-15  
**负责人**：Data Engineering Team

