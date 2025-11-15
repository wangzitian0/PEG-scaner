"""
数据模型定义
"""

from dataclasses import dataclass, asdict
from typing import Optional
from datetime import datetime


@dataclass
class StockData:
    """股票数据模型"""
    
    ticker: str
    date: str  # ISO format: 2025-11-14
    
    # 价格数据
    price: float
    market_cap: Optional[float] = None
    
    # 财务数据
    ttm_profit: float = 0.0  # TTM净利润
    ttm_revenue: Optional[float] = None
    shares_outstanding: Optional[float] = None
    
    # 增长数据
    growth_rate: float = 0.0  # YoY增长率
    
    # 估值数据
    pe: float = 0.0
    peg: float = 0.0
    
    # 元数据
    currency: str = 'USD'
    data_source: str = 'yfinance'
    confidence: str = 'HIGH'  # HIGH/MEDIUM/LOW
    error_message: Optional[str] = None
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)
    
    def to_table_row(self) -> dict:
        """转换为表格行"""
        from core.format_utils import format_profit, format_ticker_name
        
        return {
            '公司名称': format_ticker_name(self.ticker),
            '净利润': format_profit(self.ttm_profit, self.currency),
            '利润增速': f"{self.growth_rate:.1%}" if self.growth_rate else 'N/A',
            'TTM PE': f"{self.pe:.1f}" if self.pe else 'N/A',
            'PEG': f"{self.peg:.2f}" if self.peg else 'N/A'
        }
    
    @property
    def is_valid(self) -> bool:
        """检查数据是否有效"""
        return (
            self.price > 0 and
            self.ttm_profit != 0 and
            0 < self.pe < 300 and
            -5 < self.peg < 10 and
            -1 < self.growth_rate < 5
        )


@dataclass
class ETFHolding:
    """ETF持仓数据"""
    
    ticker: str
    name: str
    weight: float = 0.0  # 百分比
    shares: Optional[int] = None
    market_value: Optional[float] = None


@dataclass
class BacktestResult:
    """回测结果"""
    
    ticker: str
    start_date: str
    end_date: str
    
    # 策略参数
    buy_threshold: float
    sell_threshold: float
    
    # 绩效指标
    initial_value: float
    final_value: float
    total_return: float
    annual_return: float
    max_drawdown: float
    sharpe_ratio: float
    
    # 交易统计
    num_trades: int
    num_wins: int
    win_rate: float
    
    # 详细数据
    trades: list
    monthly_values: list
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return asdict(self)

